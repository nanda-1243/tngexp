"""MagPress L1: 3D models of every part (STEP + STL), the placed assembly (STEP, GLB), an interference check through the
stroke at both stations, masses, and 2D projections of the assembly for the GA drawings.

Run:  python light/build_models.py <outdir>      (needs cadquery and trimesh)

Simplifications: threads at the nominal diameter, no cosmetic edge breaks, bought parts as plain shapes at catalogue size.
Pose names: 'A' / 'B' = station under the ram; theta = crank angle (10.5 deg on the handle stop, 70 deg handle up).
"""
import csv
import json
import math
import os
import sys

import cadquery as cq
from cadquery.occ_impl.exporters.assembly import exportAssembly
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir
from OCP.BRepLib import BRepLib
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from OCP.BRepTools import BRepTools_WireExplorer
from OCP.TopAbs import TopAbs_REVERSED
from OCP.TopoDS import TopoDS

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(HERE, 'out')
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'models'))
import l1 as G                 # noqa: E402
import build_models as BM      # noqa: E402  (helpers of the M4 model builder)

V, E = BM.V, BM.E
cyl, cone, box, tube, prism = BM.cyl, BM.cone, BM.box, BM.tube, BM.prism
STEEL, ALU, BRONZE = 7.85e-6, 2.70e-6, 8.8e-6      # kg / mm^3


# =====================================================================================
# part solids (each in its own frame)
# =====================================================================================
def edge_holes(T, holes):
    """holes into the bottom edge (w = 0) of a profile part: [(u, d, depth[, t])], at t (default: centred in the thickness)."""
    return [cq.Solid.makeCylinder(h[1] / 2.0, h[2] + E, V(h[0], -E, h[3] if len(h) > 3 else T / 2.0), V(0, 1, 0)) for h in holes]


def rr_loft(sections):
    """loft through rounded squares [(z, w, r)]."""
    wires = [BM.wire(G.rrect(0, 0, w, w, r), z) for (z, w, r) in sections]
    return cq.Solid.makeLoft(wires, ruled=len(wires) == 2)


def try_fillet(s, sel, r):
    try:
        out = cq.Workplane('XY').add(s).edges(sel).fillet(r).val()
        return out if out.isValid() else s
    except Exception:
        return s


def solid_for(p):
    pid = p['id']
    if p['kind'] == 'turned':
        segs = [(BM.NOM[d] if isinstance(d, str) else d, l) for (d, l) in p['segs']]
        return BM.stepped(segs)
    if p['kind'] == 'pin':
        s = cyl(p['d'], p['L'], z0=-p['L'] / 2.0)
        for z in ((-p['groove'], p['groove']) if p['groove'] else ()):
            s = s.cut(tube(p['d'] + 2, p['d'] - 0.8, 1.1, z0=z - 0.55))
        return s
    if p['kind'] == 'tube':
        return tube(p['od'], p['bore'], p['L'])
    s = BM.plate(p['outline'], p['T'], p['feats'])
    if pid == 'L-107':
        s = BM.cut_all(s, edge_holes(p['T'], [(-16, 8, 16), (16, 8, 16), (-6, 6, 10), (6, 6, 10)]))
    elif pid == 'L-108':
        c = G.CLEVIS
        s = s.cut(cq.Solid.makeBox(c['L'] + 10, 100, c['slot'], V(-c['L'] / 2 - 5, c['base'], (c['W'] - c['slot']) / 2.0)))
        s = BM.cut_all(s, edge_holes(p['T'], [(-8, 8, 10), (8, 8, 10), (0, 6, 8, c['W'] / 2 - 12), (0, 6, 8, c['W'] / 2 + 12)]))
    elif pid == 'L-202':
        s = try_fillet(s, '>Z', G.PED_EDGE)
    elif pid == 'L-205':
        tt = G.CUP_T + G.NOSE
        step = box(G.ST + 10, G.ST + 10, G.NOSE + E, z0=G.CUP_T).cut(
            rr_loft([(G.CUP_T, G.NOSE_BASE, G.CUP_R + 1.4), (tt + E, G.NOSE_TOP - 0.02, G.CUP_R + 0.6)]))
        s = s.cut(step).clean()
        ta = math.tan(math.radians(G.CUP_ALPHA))
        s = s.cut(rr_loft([(-E, G.CUP_BOT - 2 * E * ta, G.CUP_R), (tt + E, G.NOSE_IN + 2 * E * ta, G.CUP_R)])).clean()
        s = BM.cut_all(s, [cone(5.5, 10.4 + 2 * E, 2.45 + E, sx * 45, sy * 45, G.CUP_T - 2.45) for sx in (-1, 1) for sy in (-1, 1)])
    elif pid == 'L-207':
        secs = []
        for k in range(9):
            h = G.MOUTH_R * k / 8.0
            off = G.MOUTH_R - math.sqrt(max(0.0, G.MOUTH_R ** 2 - (G.MOUTH_R - h) ** 2))
            secs.append((h if k else -E, G.BORE + 2 * off, G.BORE_R + off))
        s = s.cut(rr_loft(secs)).clean()
        z = 3.2
        tools = [cq.Solid.makeCylinder(2.0, 25, V(30, 12, z), V(1, 0, 0)), cq.Solid.makeCylinder(2.0, 25, V(-30, -12, z), V(-1, 0, 0)),
                 cq.Solid.makeCylinder(2.0, 25, V(-12, 30, z), V(0, 1, 0)), cq.Solid.makeCylinder(2.0, 25, V(12, -30, z), V(0, -1, 0))]
        s = BM.cut_all(s, tools)
    elif pid == 'L-208':
        s = try_fillet(s, '<Z', G.PLUG_EDGE)
    return s


def density(p):
    m = p['material']
    if 'aluminium' in m:
        return ALU
    return STEEL


# ---------------- bought parts ----------------
def shoulder10(L):
    """ISO 7379 D10 / M8: underside of the head at z = 0, head up."""
    s = cyl(16, 10).fuse(cyl(10, L, z0=-L)).fuse(cyl(8, 13, z0=-L - 13))
    return BM.cut_all(s, [BM.hexagon(5, 5 + E, 5)])


def shoulder6(L, thread=7.5):
    """ISO 7379 D6 / M5, thread shortened to 7.5 (ring A is 8 thick): underside of the head at z = 0, head up."""
    s = cyl(10, 4.5).fuse(cyl(6, L, z0=-L)).fuse(cyl(5, thread, z0=-L - thread))
    return BM.cut_all(s, [BM.hexagon(3, 2.5 + E, 4.5 - 2.5)])


def die_spring(od, length):
    turns = max(3, int(length / (od * 0.32)))
    return BM.helix_spring(od, od * 0.18, length, turns)


def ball_plunger_m10():
    return cyl(10, 19).fuse(cq.Solid.makeSphere(3.0, V(0, 0, 0))).translate((0, 0, 0))


def ball_plunger_m4():
    return cyl(4, 12, z0=0.4).fuse(cq.Solid.makeSphere(1.25, V(0, 0, 1.25)))


def knob32():
    return cyl(8, 8, z0=-8).fuse(cq.Solid.makeSphere(16, V(0, 0, 14))).cut(box(40, 40, 10, 0, 0, -10))


BOUGHT_SOLIDS = {
    'B-01': lambda: tube(28, 20, 25),
    'B-02n': lambda: BM.nut(18, 10, 12), 'B-02w': lambda: tube(24, 13, 2.5),
    'B-03': lambda: tube(G.COLLAR['D'], G.COLLAR['d'], G.COLLAR['b']),
    'B-05': lambda: BM.retaining_ring(15.2, 24, 1.0),
    'B-06a': lambda: BM.cap_screw(8, 35, 13, 8, 6), 'B-06b': lambda: BM.cap_screw(8, 25, 13, 8, 6),
    'B-07': lambda: BM.cap_screw(8, 30, 13, 8, 6),
    'B-08b': lambda: BM.hex_screw(8, 45, 13, 5.3), 'B-08n': lambda: BM.nut(13, 6.5, 8), 'B-08a': lambda: BM.hex_screw(8, 35, 13, 5.3),
    'B-09': lambda: BM.dowel(6, 16), 'B-10a': lambda: BM.dowel(5, 12), 'B-10b': lambda: BM.dowel(5, 10), 'B-11': lambda: BM.dowel(10, 16),
    'B-12': ball_plunger_m10, 'B-13': knob32,
    'B-14': lambda: BM.cap_screw(4, 10, 7, 4, 3), 'B-15': lambda: BM.cap_screw(6, 12, 10, 6, 5),
    'B-16': lambda: BM.cap_screw(5, 16, 8.5, 5, 4), 'B-17': lambda: shoulder6(G.SH_RA),
    'B-19': lambda: BM.csk_screw(5, 12, 10.4, 3), 'B-20': lambda: shoulder10(G.SH_UR),
    'B-22': lambda: BM.cap_screw(6, 55, 10, 6, 5), 'B-23': ball_plunger_m4,
    'B-24': lambda: box(40, 36, 120),
}

# =====================================================================================
# placement
# =====================================================================================
COLORS = {'frame': (0.20, 0.22, 0.25), 'lever': (0.08, 0.08, 0.09), 'alu': (0.78, 0.80, 0.83), 'die': (0.55, 0.58, 0.62),
          'chrome': (0.85, 0.86, 0.88), 'bronze': (0.72, 0.53, 0.25), 'screw': (0.12, 0.12, 0.13), 'spring_r': (0.80, 0.15, 0.15),
          'spring_g': (0.20, 0.60, 0.25), 'spring': (0.70, 0.70, 0.72), 'grip': (0.75, 0.08, 0.10), 'knob': (0.10, 0.10, 0.10),
          'shim': (0.80, 0.70, 0.40)}
PCOL = {'L-101': 'frame', 'L-102': 'frame', 'L-103': 'alu', 'L-104': 'chrome', 'L-105': 'frame', 'L-106': 'frame', 'L-107': 'frame',
        'L-108': 'frame', 'L-109': 'lever', 'L-110': 'frame', 'L-111': 'chrome', 'L-112': 'chrome', 'L-201': 'alu', 'L-202': 'die',
        'L-203': 'die', 'L-204': 'alu', 'L-205': 'die', 'L-206': 'alu', 'L-207': 'die', 'L-208': 'die', 'L-209': 'shim'}


def mv(s, x, y, z):
    return s.translate(V(x, y, z))


def rot(s, axis, deg, c=(0, 0, 0)):
    return s.rotate(V(*c), V(c[0] + axis[0], c[1] + axis[1], c[2] + axis[2]), deg) if deg else s


def profile_place(s, T, yc, x, z, ang=0.0):
    """profile part (u, w, t) -> X-Z plane, thickness centred on Y = yc, rotated CCW (front view) by ang about its origin."""
    s = rot(s, (1, 0, 0), 90)                     # (u, w, t) -> (u, -t, w)
    s = s.translate(V(0, T / 2.0, 0))
    s = rot(s, (0, 1, 0), -ang)
    return mv(s, x, yc, z)


def flip(s):
    return rot(s, (1, 0, 0), 180)


class Pose:
    def __init__(self, station, theta, table=None):
        self.station, self.theta = station, theta
        self.tx = table if table is not None else (G.ST_X if station == 'A' else -G.ST_X)     # table centre X
        self.zb = G.Z_O - G.drop(theta)                       # pin B
        self.ram = self.zb - G.LUG_PIN - G.RAM_T              # ram bottom
        self.db = self.ram - G.DB_T                           # die body bottom
        free = self.db - G.UR_GAP - G.UR_T                    # upper ring bottom, springs extended
        xa, xb = self.tx - G.ST_X, self.tx + G.ST_X           # stations A, B
        ra_top = G.Z_RA_REST + G.RA_T
        if abs(xa) < 1e-6 and free < ra_top:
            ra_top = max(free, G.Z_BB + G.RA_T)
        self.ra_top = ra_top
        floor = -1e9
        if abs(xa) < 1e-6:
            floor = G.Z_BB + G.RA_T
        if abs(xb) < 1e-6:
            floor = G.Z_FACE
        self.ur = max(free, floor)                            # upper ring bottom
        self.retract = self.ur - free
        self.xa, self.xb = xa, xb
        self.a = (G.R_CRANK * math.sin(math.radians(theta)), G.Z_O - G.R_CRANK * math.cos(math.radians(theta)))


def assemble(solids, pose):
    """[(name, pid, shape, colour key)] for a pose."""
    S, out = solids, []

    def add(name, pid, s, col):
        out.append((name, pid, s, col))

    # ---- frame ----
    add('L-101', 'L-101', S['L-101'], 'frame')
    for i, sy in enumerate((-1, 1), 1):
        add('L-102_%d' % i, 'L-102', mv(S['L-102'], 0, sy * G.RAIL_Y, G.BASE_T), 'frame')
        for j, x in enumerate((-150, -50, 50, 150), 1):
            add('B-14_%d%d' % (i, j), 'B-14', mv(S['B-14'], x, sy * G.RAIL_Y, G.BASE_T + 4.5), 'screw')
    add('B-11', 'B-11', mv(S['B-11'], 0, G.STOP_Y, G.BASE_T - 10.5), 'chrome')
    for i, sy in enumerate((-1, 1), 1):
        add('L-104_%d' % i, 'L-104', mv(S['L-104'], 0, sy * G.COL_Y, 0), 'chrome')
        add('B-03s_%d' % i, 'B-03', mv(S['B-03'], 0, sy * G.COL_Y, G.Z_SEAT - G.COLLAR['b']), 'frame')
        add('B-03u_%d' % i, 'B-03', mv(S['B-03'], 0, sy * G.COL_Y, G.Z_UPSTOP), 'frame')
        add('B-04_%d' % i, 'B-04', mv(BM.helix_spring(G.RET_SPR['od'], G.RET_SPR['wire'], pose.ram - G.Z_SEAT, 10), 0, sy * G.COL_Y, G.Z_SEAT), 'spring')
        add('B-02w_%d' % i, 'B-02w', mv(S['B-02w'], 0, sy * G.COL_Y, G.Z_HEAD + G.HEAD_T), 'chrome')
        add('B-02n_%d' % i, 'B-02n', mv(S['B-02n'], 0, sy * G.COL_Y, G.Z_HEAD + G.HEAD_T + 2.5), 'screw')
        add('B-01_%d' % i, 'B-01', mv(S['B-01'], 0, sy * G.COL_Y, pose.ram), 'bronze')
    add('L-105', 'L-105', mv(S['L-105'], 0, 0, G.Z_HEAD), 'frame')
    ht = G.Z_HEAD + G.HEAD_T
    for i, sy in enumerate((-1, 1), 1):
        yc = sy * G.CHEEK_SCREW_Y
        add('L-107_%d' % i, 'L-107', profile_place(S['L-107'], G.CHEEK['T'], yc, 0, ht), 'frame')
        for j, x in enumerate((-16, 16), 1):
            add('B-06a_%d%d' % (i, j), 'B-06a', mv(flip(S['B-06a']), x, yc, G.Z_HEAD + 8.5), 'screw')
        for j, x in enumerate((-6, 6), 1):
            add('B-09h_%d%d' % (i, j), 'B-09', mv(S['B-09'], x, yc, ht - 8), 'chrome')
    stop_z = G.STOP_Z                                         # handle-stop contact (lever plate lower edge, theta on the stop)
    for j, sy in enumerate((-1, 1), 1):
        add('B-08b_%d' % j, 'B-08b', mv(flip(S['B-08b']), G.STOP_X, sy * 12, stop_z - 45), 'screw')
        add('B-08n_%d' % j, 'B-08n', mv(S['B-08n'], G.STOP_X, sy * 12, G.Z_HEAD - 6.5), 'screw')
    # ---- moving: ram group ----
    rt = pose.ram + G.RAM_T
    add('L-106', 'L-106', mv(S['L-106'], 0, 0, pose.ram), 'frame')
    add('L-108', 'L-108', profile_place(S['L-108'], G.CLEVIS['W'], 0, 0, rt), 'frame')
    for j, x in enumerate((-8, 8), 1):
        add('B-06b_%d' % j, 'B-06b', mv(flip(S['B-06b']), x, 0, pose.ram + 8.5), 'screw')
    for j, y in enumerate((-12, 12), 1):
        add('B-09l_%d' % j, 'B-09', mv(S['B-09'], 0, y, rt - 8), 'chrome')
    for j, (x, y) in enumerate([(sx * 18, sy * 38) for sx in (-1, 1) for sy in (-1, 1)], 1):
        add('B-07_%d' % j, 'B-07', mv(S['B-07'], x, y, rt - 8.5), 'screw')
    for j, y in enumerate((-22, 22), 1):
        add('B-09r_%d' % j, 'B-09', mv(S['B-09'], 0, y, pose.ram - 8), 'chrome')
    # ---- upper die ----
    add('L-206', 'L-206', mv(S['L-206'], 0, 0, pose.db), 'alu')
    add('L-209', 'L-209', mv(S['L-209x2'], 0, 0, pose.db - G.SHIM), 'shim')
    add('L-208', 'L-208', mv(S['L-208'], 0, 0, pose.db - G.PLUG_DROP), 'die')
    for j, (x, y) in enumerate([(sx * 22, sy * 22) for sx in (-1, 1) for sy in (-1, 1)], 1):
        add('B-22_%d' % j, 'B-22', mv(S['B-22'], x, y, pose.ram - 6.5), 'screw')
    for j, x in enumerate((-22, 22), 1):
        add('B-09p_%d' % j, 'B-09', mv(S['B-09'], x, 0, pose.db - G.PLUG_DROP + G.PLUG_H - 8), 'chrome')
    add('L-207', 'L-207', mv(S['L-207'], 0, 0, pose.ur), 'die')
    urt = pose.ur + G.UR_T
    for j, (x, y) in enumerate([(45, 0), (-45, 0), (0, 45), (0, -45)], 1):
        add('B-20_%d' % j, 'B-20', mv(S['B-20'], x, y, urt + G.SH_UR), 'screw')
    for j, (x, y) in enumerate([(sx * 42, sy * 42) for sx in (-1, 1) for sy in (-1, 1)], 1):
        add('B-21_%d' % j, 'B-21', mv(die_spring(20, pose.db + G.UP_SPR['pocket_body'] - (urt - 8)), x, y, urt - 8), 'spring_r')
    for j, (x, y, d) in enumerate([(31.925, 12, (1, 0, 0)), (-31.925, -12, (-1, 0, 0)), (-12, 31.925, (0, 1, 0)), (12, -31.925, (0, -1, 0))], 1):
        b = S['B-23'].translate(V(0, 0, -0.4))           # ball 0.4 proud of the bore wall
        b = b.rotate(V(0, 0, 0), V(0, 1, 0), 90) if d[0] else b.rotate(V(0, 0, 0), V(1, 0, 0), -90)
        if d[0] < 0 or d[1] < 0:
            b = b.rotate(V(0, 0, 0), V(0, 0, 1), 180)
        add('B-23_%d' % j, 'B-23', mv(b, x, y, pose.ur + 3.2), 'screw')
    # ---- toggle ----
    zo, (ax, az) = G.Z_O, pose.a
    hdeg = G.handle_angle(pose.theta)
    ha = math.radians(hdeg)
    alongh = lambda u: (u * math.cos(ha), zo + u * math.sin(ha))
    for i, sy in enumerate((-1, 1), 1):
        add('L-109_%d' % i, 'L-109', profile_place(S['L-109'], G.LEVER_T, sy * sum(G.LEVER_Y) / 2, 0, zo, pose.theta), 'lever')
        add('L-111_%d' % i, 'L-111', mv(rot(S['L-111'], (1, 0, 0), 90), 0, sy * (G.LEVER_Y[0] + 0.5 + G.PIN_O_L / 2), zo), 'chrome')
    for j, u in enumerate(G.SPACER_U, 1):
        x, z = alongh(u)
        add('L-113_%d' % j, 'L-113', mv(rot(S['L-113'], (1, 0, 0), 90), x, G.LEVER_Y[0], z), 'chrome')
    gx, gz = alongh(G.GRIP_C)
    add('L-114', 'L-114', profile_place(S['L-114'], G.GRIP_SPACER['T'], 0, gx, gz, hdeg), 'lever')
    for j, u in enumerate(G.SPACER_U + G.GRIP_BOLT_U, 1):
        x, z = alongh(u)
        add('B-08a_%d' % j, 'B-08a', mv(rot(S['B-08a'], (1, 0, 0), -90), x, G.LEVER_Y[1], z), 'screw')
    g = rot(S['B-24'].translate(V(0, 0, -60)), (0, 1, 0), 90 - hdeg)
    add('B-24', 'B-24', mv(g, gx, 0, gz), 'grip')
    phi = math.degrees(math.atan2(az - pose.zb, ax - 0.0))
    add('L-110', 'L-110', profile_place(S['L-110'], G.LINK_T, 0, 0, pose.zb, phi), 'frame')
    pin = lambda s: rot(s, (1, 0, 0), 90)
    add('L-112_A', 'L-112', mv(pin(S['L-112']), ax, 0, az), 'chrome')
    add('L-112_B', 'L-112', mv(pin(S['L-112']), 0, 0, pose.zb), 'chrome')
    # ---- table and stations ----
    tx = pose.tx
    add('L-103', 'L-103', mv(S['L-103'], tx, 0, G.BASE_T), 'alu')
    add('B-12', 'B-12', mv(S['B-12'], tx + G.DETENT[0], G.DETENT[1], G.BASE_T + 2.6), 'screw')
    for j, x in enumerate((-150, 150), 1):
        add('B-13_%d' % j, 'B-13', mv(S['B-13'], tx + x, 0, G.Z_TABLE), 'knob')
    for st, xs in (('A', pose.xa), ('B', pose.xb)):
        for j, (x, y) in enumerate([(sx * 45, sy * 30) for sx in (-1, 1) for sy in (-1, 1)], 1):
            add('B-15%s_%d' % (st, j), 'B-15', mv(flip(S['B-15']), xs + x, y, G.BASE_T + 6.5), 'screw')
        for j, (x, y) in enumerate([(-20, 45), (20, -45)], 1):
            add('B-09t%s_%d' % (st, j), 'B-09', mv(S['B-09'], xs + x, y, G.BASE_T), 'chrome')
    xa = pose.xa
    add('L-201', 'L-201', mv(S['L-201'], xa, 0, G.Z_TABLE), 'alu')
    add('L-202', 'L-202', mv(S['L-202'], xa, 0, G.Z_BB), 'die')
    add('L-203', 'L-203', mv(S['L-203'], xa, 0, pose.ra_top - G.RA_T), 'die')
    dra = (G.Z_RA_REST + G.RA_T) - pose.ra_top
    for j, (x, y) in enumerate([(sx * 45, sy * 45) for sx in (-1, 1) for sy in (-1, 1)], 1):
        add('B-17_%d' % j, 'B-17', mv(flip(S['B-17']), xa + x, y, G.Z_RA_REST - G.SH_RA - dra), 'screw')
    for j, (x, y) in enumerate([(45, 0), (-45, 0), (0, 45), (0, -45)], 1):
        z0 = G.Z_BB - G.RA_SPR['pocket_body']
        add('B-18_%d' % j, 'B-18', mv(die_spring(10, pose.ra_top - G.RA_T + G.RA_SPR['pocket_ring'] - z0), xa + x, y, z0), 'spring_g')
    for j, (x, y) in enumerate([(sx * 20, sy * 20) for sx in (-1, 1) for sy in (-1, 1)], 1):
        add('B-16_%d' % j, 'B-16', mv(flip(S['B-16']), xa + x, y, G.Z_TABLE + 5.5), 'screw')
    for j, x in enumerate((-24, 24), 1):
        add('B-10a_%d' % j, 'B-10a', mv(S['B-10a'], xa + x, 0, G.Z_BB - 6), 'chrome')
    xb = pose.xb
    add('L-204', 'L-204', mv(S['L-204'], xb, 0, G.Z_TABLE), 'alu')
    add('L-205', 'L-205', mv(S['L-205'], xb, 0, G.Z_FACE - G.CUP_T), 'die')
    for j, (x, y) in enumerate([(sx * 45, sy * 45) for sx in (-1, 1) for sy in (-1, 1)], 1):
        add('B-19_%d' % j, 'B-19', mv(S['B-19'], xb + x, y, G.Z_FACE), 'screw')
    for j, x in enumerate((-45, 45), 1):
        add('B-10b_%d' % j, 'B-10b', mv(S['B-10b'], xb + x, 0, G.Z_FACE - 10), 'chrome')
    return out


# =====================================================================================
# 2D projection (hidden-line removal) for the GA drawings
# =====================================================================================
def project(shapes, normal, xdir, tol=0.15):
    comp = cq.Compound.makeCompound(shapes)
    hlr = HLRBRep_Algo()
    hlr.Add(comp.wrapped)
    hlr.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*normal), gp_Dir(*xdir))))
    hlr.Update()
    hlr.Hide()
    h = HLRBRep_HLRToShape(hlr)
    res = {}
    for key, getters in (('vis', (h.VCompound, h.OutLineVCompound)), ('hid', (h.HCompound,))):
        lines = []
        for g in getters:
            c = g()
            if c.IsNull():
                continue
            BRepLib.BuildCurves3d_s(c, 1e-4)
            for e in cq.Shape(c).Edges():
                cu = e._geomAdaptor()
                pts = GCPnts_QuasiUniformDeflection(cu, tol, cu.FirstParameter(), cu.LastParameter())
                if pts.IsDone() and pts.NbPoints() > 1:
                    lines.append([(round(pts.Value(i + 1).X(), 3), round(pts.Value(i + 1).Y(), 3)) for i in range(pts.NbPoints())])
        res[key] = lines
    return res


def section_faces(shapes, y0=0.0, tol=0.1):
    """faces cut by the plane Y = y0, as closed polylines in (X, Z)."""
    plane = cq.Face.makePlane(2000, 2000, V(0, y0, 0), V(0, 1, 0))
    out = []
    for s in shapes:
        try:
            cut = s.intersect(plane)
        except Exception:
            continue
        for f in cut.Faces():
            loops = []
            for w in [f.outerWire()] + f.innerWires():
                pts = []
                ex = BRepTools_WireExplorer(TopoDS.Wire_s(w.wrapped))
                while ex.More():
                    e = cq.Edge(ex.Current())
                    cu = e._geomAdaptor()
                    gp = GCPnts_QuasiUniformDeflection(cu, tol, cu.FirstParameter(), cu.LastParameter())
                    seg = [(round(gp.Value(i + 1).X(), 3), round(gp.Value(i + 1).Z(), 3)) for i in range(gp.NbPoints())]
                    if ex.Orientation() == TopAbs_REVERSED:
                        seg = seg[::-1]
                    pts += seg
                    ex.Next()
                loops.append(pts)
            out.append(loops)
    return out


# =====================================================================================
# main
# =====================================================================================
def main():
    for d in ('step', 'stl', 'assembly'):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    print('theta on the stop %.3f deg, stroke %.3f mm, pin O at %.1f, pin B %.2f (stop)' % (G.THETA_STOP, G.STROKE, G.Z_O, G.Z_B))
    S, rows = {}, []
    for p in G.PARTS:
        s = solid_for(p)
        if not s.isValid():
            s = s.fix()
        S[p['id']] = s
        m = s.Volume() * density(p)
        p['mass'] = m
        bb = s.BoundingBox()
        base = '%s_%s' % (p['id'], BM.slug(p['name']))
        cq.exporters.export(s, os.path.join(OUT, 'step', base + '.step'))
        cq.exporters.export(s, os.path.join(OUT, 'stl', base + '.stl'), tolerance=0.05, angularTolerance=0.2)
        rows.append([p['id'], p['name'], 'make', p['group'], p['qty'], '%.1f x %.1f x %.1f' % (bb.xlen, bb.ylen, bb.zlen), '%.3f' % m,
                     base + '.step', p['material']])
        print('  %-6s %-28s %7.3f kg' % (p['id'], p['name'], m))
    S['L-209x2'] = BM.plate(G.part_by('L-209')['outline'], G.SHIM, G.part_by('L-209')['feats'])
    for k, f in BOUGHT_SOLIDS.items():
        S[k] = f()
    for k in ('B-01', 'B-03', 'B-11', 'B-12', 'B-17', 'B-20', 'B-23'):
        cq.exporters.export(S[k], os.path.join(OUT, 'step', '%s_bought.step' % k))
    with open(os.path.join(OUT, 'parts.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['id', 'name', 'make_or_buy', 'group', 'qty', 'size_xyz_mm', 'mass_kg_each', 'step_file', 'material'])
        w.writerows(rows)
        for b in G.BOUGHT:
            w.writerow([b[0], b[1], 'buy', '', b[2], '', '', '', b[3]])

    # ---------------- assembly (station A under the ram, handle up) ----------------
    pose0 = Pose('A', G.THETA_UP)
    inst = assemble(S, pose0)
    assy = cq.Assembly(name='MagPress-L1')
    for name, pid, s, col in inst:
        c = COLORS[col]
        assy.add(s, name=name, color=cq.Color(c[0], c[1], c[2], 1.0))
    exportAssembly(assy, os.path.join(OUT, 'assembly', 'MagPress-L1_assembly.step'))
    mass_total = 0.0
    for name, pid, s, col in inst:
        if pid.startswith('L-'):
            mass_total += s.Volume() * density(G.part_by(pid))
        else:
            mass_total += s.Volume() * (BRONZE if pid == 'B-01' else STEEL if col != 'grip' and col != 'knob' else 1.2e-6)

    # ---------------- GLB (assembled and exploded) for the renders ----------------
    import trimesh
    EXPL = {'L-101': 0, 'L-102': 0, 'B-14': 0, 'B-11': 0, 'L-103': 40, 'B-12': 40, 'B-13': 40, 'B-15': 40, 'B-09t': 40,
            'L-201': 80, 'L-204': 80, 'B-16': 70, 'B-10a': 95, 'L-202': 110, 'B-17': 60, 'B-18': 120, 'L-203': 150,
            'L-205': 130, 'B-19': 160, 'B-10b': 150, 'L-208': 190, 'L-209': 200, 'B-09p': 205, 'L-207': 175, 'B-23': 175,
            'B-21': 225, 'L-206': 255, 'B-20': 330, 'B-22': 345, 'B-09r': 285, 'L-106': 300, 'B-01': 300, 'B-07': 380,
            'L-108': 340, 'B-06b': 290, 'B-09l': 330, 'L-110': 375, 'L-112': 375, 'B-05': 375, 'L-109': 430, 'B-24': 430,
            'L-111': 430, 'L-113': 430, 'L-114': 430, 'B-08a': 430, 'L-105': 480, 'L-107': 520, 'B-06a': 450, 'B-09h': 500, 'B-02': 520, 'B-02w': 515, 'B-02n': 530,
            'B-08b': 470, 'B-08n': 460, 'B-08a': 430, 'L-104': 0, 'B-03': 0, 'B-04': 0}

    def explode_z(name, pid):
        for k in (name.split('_')[0], pid, pid[:4]):
            if k in EXPL:
                return EXPL[k]
        return 0

    def glb(items, path, exploded=False):
        sc = trimesh.Scene()
        for name, pid, s, col in items:
            vs, tris = s.tessellate(0.1, 0.35)
            dz = explode_z(name, pid) if exploded else 0.0
            m = trimesh.Trimesh([(v.x, v.z + dz, -v.y) for v in vs], tris, process=False)
            c = COLORS[col]
            m.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
                name=col, baseColorFactor=[int(k * 255) for k in c] + [255], metallicFactor=0.25, roughnessFactor=0.55))
            sc.add_geometry(m, node_name=name, geom_name=name)
        with open(path, 'wb') as f:
            f.write(trimesh.exchange.gltf.export_glb(sc, include_normals=True))
    glb(inst, os.path.join(OUT, 'assembly', 'MagPress-L1_assembly.glb'))
    glb(inst, os.path.join(OUT, 'assembly', 'MagPress-L1_exploded.glb'), exploded=True)

    # ---------------- interference through the stroke ----------------
    springs = ('B-04', 'B-18', 'B-21')
    pairs = (('B-12', 'L-101'), ('B-24', 'L-109'), ('B-24', 'L-114'), ('B-24', 'B-08a'), ('B-23', 'L-208'))      # detent ball in its dimple; grip on the bar; spring balls on the plug
    skip = lambda a, b: any(a.startswith(k) or b.startswith(k) for k in springs) or \
        any((a.startswith(x) and b.startswith(y)) or (a.startswith(y) and b.startswith(x)) for x, y in pairs)
    report = []
    for st in ('A', 'B'):
        for th in (G.THETA_UP, 50.0, 35.0, 25.0, 18.0, G.THETA_STOP):
            pz = Pose(st, th)
            placed = [(n, pid, s) for (n, pid, s, c) in assemble(S, pz)]
            hits = BM.overlaps(placed, skip)
            report.append(('Station %s under the ram, crank %.1f deg (ram %.2f mm down, upper ring retracted %.2f, ring A down %.2f)'
                           % (st, th, Pose(st, G.THETA_UP).ram - pz.ram, pz.retract, G.Z_RA_REST + G.RA_T - pz.ra_top), hits))
            print('  station %s theta %5.1f: %d overlaps' % (st, th, len(hits)))
    for tx in (0.0, 37.5, -37.5):
        pz = Pose('A', G.THETA_UP, table=tx)
        hits = BM.overlaps([(n, pid, s) for (n, pid, s, c) in assemble(S, pz)], skip)
        report.append(('Handle up, table sliding (table centre at X %.1f)' % tx, hits))
        print('  table at %.1f: %d overlaps' % (tx, len(hits)))
    with open(os.path.join(OUT, 'assembly', 'interference.txt'), 'w') as f:
        f.write('Interference check, MagPress L1 (63.5 x 63.5). %d placed parts. Overlaps above 1 mm^3 listed; touching faces and '
                'fits at the same nominal size are not overlaps. Springs are not checked (they compress).\n' % len(inst))
        for title, hits in report:
            f.write('\n%s:\n' % title)
            for a_, b_, v in sorted(hits, key=lambda h: -h[2]):
                f.write('  %-14s x %-14s %10.1f mm^3\n' % (a_, b_, v))
            if not hits:
                f.write('  none\n')

    # ---------------- projections for the GA ----------------
    proj = {}
    pstop = Pose('A', G.THETA_STOP)
    shapes_up = [s for (n, pid, s, c) in inst]
    proj['front_up'] = project(shapes_up, (0, -1, 0), (1, 0, 0))
    proj['side_up'] = project(shapes_up, (1, 0, 0), (0, 1, 0))
    proj['top_up'] = project(shapes_up, (0, 0, 1), (1, 0, 0))
    for st in ('A', 'B'):
        pz = Pose(st, G.THETA_STOP)
        items = assemble(S, pz)
        clip = cq.Solid.makeBox(124, 400, 205, V(-62, -200, 0))
        half = cq.Solid.makeBox(124, 200, 205, V(-62, 0, 0))
        near, cut = [], []
        for (n, pid, s, c) in items:
            bb = s.BoundingBox()
            if bb.xmax < -62 or bb.xmin > 62 or bb.zmin > 205 or pid.startswith('B-04') or pid.startswith('B-13'):
                continue
            try:
                c1 = s.intersect(clip)
                if c1.Volume() > 1e-3:
                    near.append(c1)
                    c2 = c1.intersect(half)
                    if c2.Volume() > 1e-3:
                        cut.append(c2)
            except Exception:
                pass
        proj['sec_%s' % st] = project(cut, (0, -1, 0), (1, 0, 0))
        proj['sec_%s' % st]['faces'] = section_faces(near)
        proj['sec_%s' % st]['retract'] = pz.retract
    json.dump(proj, open(os.path.join(OUT, 'assembly', 'projections.json'), 'w'))
    summary = dict(mass_total=mass_total, n_inst=len(inst), masses={p['id']: p['mass'] for p in G.PARTS},
                   overlaps=sum(len(h) for _, h in report))
    json.dump(summary, open(os.path.join(OUT, 'assembly', 'summary.json'), 'w'), indent=1)
    print('assembly mass %.1f kg (%d placed parts); total overlaps %d' % (mass_total, len(inst), summary['overlaps']))


if __name__ == '__main__':
    main()
