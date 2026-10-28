"""MagPress M4 Rev E: 3D models of every part, made and bought, as STEP, STL and OBJ, plus a placed assembly.

Run:  python models/build_models.py [outdir]      (needs cadquery and trimesh; outdir defaults to models/)

Geometry comes from the drawing source in cad/ (outlines and feature lists), so the models match the drawings.
Simplifications: no threads (threaded holes and studs are shown at the nominal thread diameter), no cosmetic
chamfers or edge breaks, bought parts are plain shapes at the catalogue size.

Frames
  Assembly: X along the die table, +Y toward the back (the front of the press is -Y), Z up from the bench. mm.
            Pose: handle up, station B under the ram, size kit 6363 fitted.
  Part files: each part in its own frame, ready to print (plates flat, turned parts standing on one end).
"""
import csv
import math
import os
import sys

import cadquery as cq
from cadquery.occ_impl.exporters.assembly import exportAssembly

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'cad'))
import draft as DR      # noqa: E402
import parts as P       # noqa: E402
import parts2 as P2     # noqa: E402

OUT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else HERE
NOM = DR.MAJOR                      # threaded holes are modelled at the nominal diameter
KIT_SHOWN = '6363'
ASSY_TOL = (0.1, 0.35)              # tessellation for the assembly OBJ / GLB (part files use 0.05 mm)
E = 0.02                            # over-cut so cutting tools pass cleanly through faces


# =====================================================================================
# geometry helpers
# =====================================================================================
def V(x, y, z=0.0):
    return cq.Vector(x, y, z)


def edges_from_segs(segs, z=0.0):
    out = []
    for s in segs:
        if s[0] == 'L':
            _, x1, y1, x2, y2 = s
            if abs(x1 - x2) + abs(y1 - y2) > 1e-9:
                out.append(cq.Edge.makeLine(V(x1, y1, z), V(x2, y2, z)))
        elif s[0] == 'A':
            _, cx, cy, r, a0, a1 = s
            p = [V(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)), z) for a in (a0, (a0 + a1) / 2.0, a1)]
            out.append(cq.Edge.makeThreePointArc(*p))
        elif s[0] == 'C':
            _, cx, cy, r = s
            out.append(cq.Edge.makeCircle(r, V(cx, cy, z)))
    return out


def wire(segs, z=0.0):
    return cq.Wire.assembleEdges(edges_from_segs(segs, z))


def prism(segs, T, z0=0.0):
    return cq.Workplane('XY').add(wire(segs)).toPending().extrude(T).val().translate((0, 0, z0))


def poly_prism(pts, T, z0=0.0):
    return cq.Workplane('XY').polyline(pts).close().extrude(T).val().translate((0, 0, z0))


def rr(w, h, r, T, x=0.0, y=0.0, z0=0.0):
    return prism(DR.rrect(x, y, w, h, r), T, z0)


def box(lx, ly, lz, x=0.0, y=0.0, z0=0.0):
    """box centred on (x, y), from z0 up."""
    return cq.Solid.makeBox(lx, ly, lz, V(x - lx / 2.0, y - ly / 2.0, z0))


def cyl(d, h, x=0.0, y=0.0, z0=0.0, axis=(0, 0, 1)):
    return cq.Solid.makeCylinder(d / 2.0, h, V(x, y, z0), V(*axis))


def cone(d0, d1, h, x=0.0, y=0.0, z0=0.0, axis=(0, 0, 1)):
    return cq.Solid.makeCone(d0 / 2.0, d1 / 2.0, h, V(x, y, z0), V(*axis))


def tube(od, id_, h, z0=0.0):
    return cyl(od, h, z0=z0).cut(cyl(id_, h + 2 * E, z0=z0 - E))


def revolve(pts):
    """solid of revolution about Z from a closed half-profile [(r, z), ...]."""
    return cq.Workplane('XZ').polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0)).val()


def stepped(segs):
    """turned part from [(diameter, length), ...] stacked up from z = 0."""
    pts, z = [(0, 0)], 0.0
    for d, l in segs:
        pts += [(d / 2.0, z), (d / 2.0, z + l)]
        z += l
    pts.append((0, z))
    return revolve(pts)


def hexagon(af, h, z0=0.0):
    return cq.Workplane('XY').polygon(6, af / math.cos(math.radians(30))).extrude(h).val().translate((0, 0, z0))


def cut_all(s, tools):
    tools = [t for t in tools if t is not None]
    return s.cut(*tools).clean() if tools else s


def feat_tools(T, feats):
    """cutting tools for a feature list from cad/ (plan x, z; part frame X = x, Y = -z, Z up from the bottom face)."""
    tools = []
    for f in feats:
        x, y, k = f['x'], -f['z'], f['kind']
        thru = f.get('thru', False)
        side = f.get('side', 'top')
        if k in ('hole', 'tap'):
            d = f['d'] if k == 'hole' else NOM[f['m']]
            if thru:
                tools.append(cyl(d, T + 2 * E, x, y, -E))
            else:
                dep = f['depth']
                tools.append(cyl(d, dep + E, x, y, T - dep) if side == 'top' else cyl(d, dep + E, x, y, -E))
            if f.get('cb'):
                D, cd = f['cb']
                cside = f.get('cbside', side if not thru else 'top')
                tools.append(cyl(D, cd + E, x, y, T - cd) if cside == 'top' else cyl(D, cd + E, x, y, -E))
            if f.get('csk'):
                D = f['csk']
                dep = (D - d) / 2.0
                if side == 'top':
                    tools.append(cone(d, D + 2 * E, dep + E, x, y, T - dep))
                else:
                    tools.append(cone(D + 2 * E, d, dep + E, x, y, -E))
        elif k == 'spot':
            d, dep = f['d'], f['depth']
            tools.append(cone(max(d - 2 * dep, 0.4), d + 2 * E, dep + E, x, y, T - dep))
        elif k == 'rr':
            w, h, r = f['w'], f['h'], f['r']
            if thru:
                tools.append(rr(w, h, r, T + 2 * E, x, y, -E))
            else:
                dep = f['depth']
                tools.append(rr(w, h, r, dep + E, x, y, T - dep) if side == 'top' else rr(w, h, r, dep + E, x, y, -E))
    return tools


def plate(segs, T, feats, extra=()):
    return cut_all(prism(segs, T), feat_tools(T, feats) + list(extra))


def helix_spring(od, wire_d, length, turns):
    """coil spring standing on z = 0, height `length` (as installed)."""
    rm = (od - wire_d) / 2.0
    h = length - wire_d
    path = cq.Wire.makeHelix(h / turns, h, rm)
    prof = cq.Wire.makeCircle(wire_d / 2.0, V(rm, 0, 0), V(0, 1, 0))
    return cq.Solid.sweep(prof, [], path, isFrenet=True).translate((0, 0, wire_d / 2.0))


# =====================================================================================
# placement: rotations about axes through the origin (degrees, applied in order), then a move
# =====================================================================================
def Tr(*ops, at=(0, 0, 0)):
    def f(s):
        for ax, deg in ops:
            if deg:
                s = s.rotate(V(0, 0, 0), V(*{'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1)}[ax]), deg)
        return s.translate(V(*at))
    return f


def at(x, y, z):
    return Tr(at=(x, y, z))


UP, DOWN = (), (('x', 180),)
ALONG_X = (('y', 90),)          # part +Z -> world +X
ALONG_MX = (('y', -90),)        # part +Z -> world -X
TO_FRONT = (('x', 90),)         # part +Z -> world -Y (front)
TO_BACK = (('x', -90),)         # part +Z -> world +Y
SIDE_PLATE = (('x', 90), ('z', -90))   # profile (u, w, t) -> (-Y, +Z, -X): side profiles in the Y-Z plane


# =====================================================================================
# press geometry (Rev C)
# =====================================================================================
OY = 234.5                      # pivot O
SX = -80.0                      # die table offset: station B (table x = +80) under the ram
STA, STB = -80.0 + SX, 80.0 + SX
A_U, A_W = 40 * math.sin(math.radians(5)), -40 * math.cos(math.radians(5))   # crank pin A in lever coordinates
B_Z = 174.0                     # pin B, handle up (clevis bore 12 above the ram pocket floor)


def lever_pt(u, w, psi):
    c, s = math.cos(math.radians(psi)), math.sin(math.radians(psi))
    return -(u * c - w * s), OY + u * s + w * c          # (Y, Z)


def solve_psi():
    lo, hi = 60.0, 70.0
    for _ in range(60):
        m = (lo + hi) / 2
        y, z = lever_pt(A_U, A_W, m)
        if math.hypot(y, z - B_Z) > 60.0:
            hi = m
        else:
            lo = m
    return (lo + hi) / 2


PSI = solve_psi()
A_Y, A_Z = lever_pt(A_U, A_W, PSI)
LINK_ANG = math.degrees(math.atan2(A_Z - B_Z, -A_Y))
Y_REST = P2.lever_rest_height(3.0, 62.0)   # Rev E: lever underside over the handle-stop post (crown, Z +62) at the 3 deg stop


# =====================================================================================
# part registry
# =====================================================================================
COL = {'oxide': (0.20, 0.21, 0.23), 'steel': (0.66, 0.68, 0.71), 'chrome': (0.86, 0.88, 0.91), 'bronze': (0.74, 0.52, 0.26),
       'gold': (0.86, 0.69, 0.32), 'carrier': (0.30, 0.32, 0.36), 'die': (0.56, 0.60, 0.65), 'base': (0.14, 0.15, 0.17),
       'red': (0.80, 0.10, 0.10), 'ure': (0.92, 0.62, 0.12), 'rubber': (0.08, 0.08, 0.08), 'blue': (0.18, 0.36, 0.82),
       'green': (0.18, 0.62, 0.30), 'wire': (0.62, 0.63, 0.67), 'knob': (0.07, 0.07, 0.07), 'ptfe': (0.58, 0.47, 0.36),
       'zinc': (0.78, 0.79, 0.74), 'stain': (0.80, 0.81, 0.82)}

PARTS = []


def part(pid, name, src, group, shape, color, places, qty_note='', spec=''):
    PARTS.append(dict(id=pid, name=name, src=src, group=group, shape=shape, color=COL[color], places=places, qty_note=qty_note, spec=spec))


# =====================================================================================
# MADE PARTS: frame
# =====================================================================================
def mp101():
    return plate(P.base_outline(), 15, P.base_feats())


def mp102(xs):
    s = box(460, 14, 12.05)
    return cut_all(s, [cyl(5.5, 12.05 + 2 * E, x, 0, -E) for x in xs])


def mp103(csk, plain, yh):
    s = box(460, 20, 4)
    tools = []
    for x in csk:
        tools += [cyl(5.5, 4 + 2 * E, x, yh, -E), cone(5.5, 11.5 + 2 * E, 3.0 + E, x, yh, 4 - 3.0)]
    tools += [cyl(5.5, 4 + 2 * E, x, yh, -E) for x in plain]
    return cut_all(s, tools)


def mp104():
    s = box(30, 27, 16)
    tools = []
    for x in (-9, 9):
        tools += [cyl(5.5, 16 + 2 * E, x, 5.5, -E), cyl(9.5, 5.5 + E, x, 5.5, 16 - 5.5)]
    tools.append(cyl(6, 30 + 2 * E, -15 - E, -8.5, 8, axis=(1, 0, 0)))
    return cut_all(s, tools)


def mp105():
    return plate(DR.rrect(0, 0, 340, 150, 0), 12, P.table_feats())


def mp106():
    return stepped([(4, 6), (6, 16)])


def mp107():
    s = stepped([(20, 6.2), (25, 158), (20, 24.5), (16, 20)])
    return cut_all(s, [cyl(10, 15 + E, z0=-E)])


def mp108():
    return plate(DR.rrect(0, 0, 120, 250, 0), 25, P.crown_feats())


def mp121():
    """handle-stop post: M10 stud into the crown (z < 0), Ø20 body, M10 x 1 x 12 hole in the top"""
    s = cyl(10, 12, z0=-12).fuse(cyl(20, 14))
    return cut_all(s, [cyl(10, 12 + E, z0=14 - 12)])


def mp109():
    fs = []
    for f in P.ram_feats():
        g = dict(f)
        if g.get('label') in ('V1', 'V2'):
            g['depth'] = 12                      # M5 x 10 measured from the 2 mm pocket floor
        fs.append(g)
    return plate(DR.rrect(0, 0, 80, 250, 0), 30, fs)


# =====================================================================================
# MADE PARTS: drive
# =====================================================================================
def mp110():
    s = cq.Workplane('XY').box(20, 32, 22, centered=(True, True, False)).edges('|Z').chamfer(2.5).val()
    tools = [cyl(14, 20 + 2 * E, -10 - E, 0, 12, axis=(1, 0, 0))]
    for y in (-12, 12):
        tools += [cyl(5.5, 22 + 2 * E, 0, y, -E), cyl(9.5, 5.5 + E, 0, y, 22 - 5.5)]
    return cut_all(s, tools)


def mp111():
    s = stepped([(50, 11), (24, 4)])
    tools = [cyl(16, 15 + 2 * E, z0=-E), cyl(4, 8 + E, 0, -20, -E), cyl(5, 25 - 7.5, 7.5, 0, 7.0, axis=(1, 0, 0))]
    for a in (45, 135, 225, 315):
        x, y = 20 * math.cos(math.radians(a)), 20 * math.sin(math.radians(a))
        tools += [cyl(5.5, 11 + 2 * E, x, y, -E), cyl(9, 3.8 + E, x, y, -E)]
    return cut_all(s, tools)


def mp112():
    segs = [DR.L(-25, 0, 25, 0), DR.L(25, 0, 25, 40), DR.A(15, 40, 10, 0, 90), DR.L(15, 50, -15, 50), DR.A(-15, 40, 10, 90, 180), DR.L(-25, 40, -25, 0)]
    s = prism(segs, 16, -8)
    tools = [cyl(18, 16 + 2 * E, 0, 33.5, -8 - E)]
    tools += [cyl(8, 16 + E, u, -E, 0, axis=(0, 1, 0)) for u in (-17, 17)]
    tools.append(cyl(6, 8 + E, 0, -E, 0, axis=(0, 1, 0)))
    return cut_all(s, tools)


def mp113():
    prof, (Az, Ay) = P.lever_profile()
    s = poly_prism(prof, 20, -10)
    try:
        sel = cq.selectors.BoxSelector((262, -30, -11), (395, 30, 11))
        s = cq.Workplane('XY').add(s).edges(sel).edges('not |Z').fillet(6).val()
    except Exception as e:                                    # keep the square grip zone if the fillet fails
        print('  lever grip fillet skipped:', e)
    return cut_all(s, [cyl(18, 20 + 2 * E, 0, 0, -10 - E), cyl(14, 20 + 2 * E, Az, Ay, -10 - E)])


def mp114():
    segs = [DR.L(0, -12, 60, -12), DR.A(60, 0, 12, 270, 450), DR.L(60, 12, 0, 12), DR.A(0, 0, 12, 90, 270)]
    s = prism(segs, 7, -3.5)
    return cut_all(s, [cyl(14, 7 + 2 * E, x, 0, -3.5 - E) for x in (0, 60)])


def pin(L, d, gd, faces):
    s = cyl(d, L)
    tools = []
    for zc in (L / 2 - faces - 0.1 - 1.1, L / 2 + faces + 0.1):
        tools.append(tube(d + 1, gd, 1.1, z0=zc))
    return cut_all(s, tools)


def mp118():
    return cyl(10, 176)


def mp119():
    return tube(24, 16.2, 9.75)


def mp120():
    return revolve([(0, 0), (1.7, 0), (5, 5.7), (5, 88), (3, 88), (3, 98), (0, 98)])


# =====================================================================================
# MADE PARTS: universal die and size kits (feature lists from cad/parts2.py)
# =====================================================================================
def mp201():
    o, T, fs = P2.body()
    return plate(o, T, fs, [cyl(6, P2.PIN_X1 - P2.PIN_X0 + E, P2.PIN_X0 - E, -P2.PIN_Z, 4, axis=(1, 0, 0))])


def mp202():
    s = stepped([(10, 4), (12, 6), (16, 15)])
    groove = revolve([(6.5, 16.5), (8 + E, 16.5 - 1.5 - E), (8 + E, 16.5 + 1.5 + E)])
    return cut_all(s, [groove])


def mp205():
    o, T, fs = P2.stbase()
    return plate(o, T, fs)


def mp210():
    o, T, fs = P2.upcarrier()
    extra = [cyl(5, 72 - 53 + 2 * E, sx * (53 - E), 0, 7, axis=(sx, 0, 0)) for sx in (-1, 1)]
    return plate(o, T, fs, extra)


def mp211(which):
    o, T, fs = P2.lowcarrier(which)
    return plate(o, T, fs)


def mp212():
    s = stepped([(6, 8), (10, 7.5)])
    torus = revolve([(6.9 + 3.1 * math.cos(math.radians(a)), 12 + 3.1 * math.sin(math.radians(a))) for a in range(0, 360, 10)])
    return cut_all(s, [torus])


def mp203(X, Z):
    o, T, fs = P2.plug(X, Z)
    return plate(o, T, fs)


def mouth(cx, cz, r, m):
    """cutter for a radius m on the bottom inner edge of an opening cx x cz (corner radius r): a frame m x m round the edge
    less the quarter torus left by a circle swept along the opening offset by m."""
    w, h, rp = cx + 2 * m, cz + 2 * m, r + m
    path = wire(DR.rrect(0, 0, w, h, rp), m)
    start = V(-w / 2 + rp, -h / 2, m)
    tor = cq.Solid.sweep(cq.Wire.makeCircle(m, start, V(1, 0, 0)), [], path, transitionMode='round')
    return rr(w, h, rp, m - E, z0=-E).cut(tor)


def mp204(X, Z):
    o, T, fs = P2.ring(X, Z, 'U')
    extra = [mouth(X + 0.35, Z + 0.35, P2.FACE_R + 0.2, P2.UR_MOUTH)]                # verification fix: R1.5 mouth
    for x in (-X / 4, X / 4):
        extra.append(cyl(3, 81 + 2, x, -40.5 - 1, P2.UR_N, axis=(0, 1, 0)))        # N: M3 radial, both long faces
    for sx in (-1, 1):
        extra.append(cyl(3.6, 3.5 + E, sx * (53 + E), 0, 7, axis=(-sx, 0, 0)))    # M: dog-point holes
    return plate(o, T, fs, extra)


def mp206(X, Z):
    o, T, fs = P2.pick_ped(X, Z)
    return plate(o, T, fs)


def mp207(X, Z):
    o, T, fs = P2.ring(X, Z, 'A')
    return plate(o, T, fs)


def mp208(X, Z):
    """Rev E double-fold anvil: block to the edge top, floor round the platform (wall at its edge), cove R0.7 at the edge (cad/parts2.ANV)"""
    o, T, fs = P2.anvil(X, Z)
    a = P2.ANV
    bw, bz, ci = X + a['block'], Z + a['block'], 2 * a['cove']
    s = rr(bw, bz, a['r'], a['top'])
    top = rr(bw - ci, bz - ci, 0.5, a['top'] - a['floor'] + E).translate(V(0, 0, a['floor']))
    path = wire(DR.rrect(0, 0, bw - ci, bz - ci, 0.5), a['top'])
    start = V(-(bw - ci) / 2 + 0.5, -(bz - ci) / 2, a['top'])
    cove = cq.Solid.sweep(cq.Wire.makeCircle(a['cove'], start, V(1, 0, 0)), [], path, transitionMode='round')
    plat = rr(X - a['plat_in'], Z - a['plat_in'], 0.5, a['platform'] - a['floor']).translate(V(0, 0, a['floor']))
    s = s.cut(top).cut(cove).fuse(plat).clean()
    return cut_all(s, feat_tools(T, fs))


def mp209(X, Z):
    o, T, fs = P2.ring(X, Z, 'B')
    cx, cz, r = X + 0.45, Z + 0.45, P2.FACE_R + 0.2
    lead = cq.Solid.makeLoft([wire(DR.rrect(0, 0, cx, cz, r), 15 - 1.2), wire(DR.rrect(0, 0, cx + 1.38, cz + 1.38, r + 0.69), 15 + E)], True)
    return plate(o, T, fs, [lead])


# =====================================================================================
# BOUGHT PARTS (catalogue shapes)
# =====================================================================================
# ---------------- Rev D: round size kits (turned plug, pedestal and anvil; round bores in the 106 x 81 rings) ----------------
def mp223(D):
    o, T, fs = P2.plug_r(D)
    return plate(o, T, fs)


def mp224(D):
    o, T, fs = P2.ring_r(D, 'U')
    extra = [cyl(3, 81 + 2, x, -40.5 - 1, 1.8, axis=(0, 1, 0)) for x in (-D / 4, D / 4)]
    extra += [cyl(3.6, 3.5 + E, sx * (53 + E), 0, 7, axis=(-sx, 0, 0)) for sx in (-1, 1)]
    return plate(o, T, fs, extra)


def mp226(D):
    o, T, fs = P2.pick_ped_r(D)
    return plate(o, T, fs)


def mp227(D):
    o, T, fs = P2.ring_r(D, 'A')
    return plate(o, T, fs)


def mp228(D):
    """round kits keep the Rev D roll channel (a round edge cannot be folded flat)"""
    o, T, fs = P2.anvil_r(D)
    s = cyl(D + 0.3, 16)
    plat = cq.Solid.makeLoft([cq.Wire.makeCircle((D - 4.0) / 2, V(0, 0, 16), V(0, 0, 1)), cq.Wire.makeCircle((D - 4.5) / 2, V(0, 0, 17), V(0, 0, 1))], True)
    s = s.fuse(plat).clean()
    return cut_all(s.cut(cq.Solid.makeTorus((D - 2.0) / 2, 1.0, V(0, 0, 16), V(0, 0, 1))), feat_tools(T, fs))


def mp229(D):
    o, T, fs = P2.ring_r(D, 'B')
    c = D + 0.45
    return plate(o, T, fs, [cone(c, c + 1.38 + 2 * E, 1.2 + E, 0, 0, 15 - 1.2)])


def cap_screw(d, L, hd, hh, socket):
    """ISO 4762 style: underside of the head at z = 0, head up, shank down."""
    s = cyl(hd, hh).fuse(cyl(d, L, z0=-L))
    return cut_all(s, [hexagon(socket, hh * 0.55 + E, hh - hh * 0.55)])


def csk_screw(d, L, hd, socket):
    """ISO 10642: top of the head at z = 0, length includes the head."""
    hh = (hd - d) / 2.0
    s = cone(d, hd, hh, z0=-hh).fuse(cyl(d, L - hh, z0=-L))
    return cut_all(s, [hexagon(socket, d * 0.6 + E, -d * 0.6)])


def hex_screw(d, L, af, hh):
    return hexagon(af, hh).fuse(cyl(d, L, z0=-L))


def nut(af, h, d):
    return cut_all(hexagon(af, h), [cyl(d, h + 2 * E, z0=-E)])


def set_screw(d, L, cone_point=True, socket=None):
    s = cyl(d, L - d / 2.0, z0=d / 2.0).fuse(cone(d * 0.25, d, d / 2.0)) if cone_point else cyl(d, L)
    return cut_all(s, [hexagon(socket, d * 0.6 + E, L - d * 0.6)]) if socket else s


def shoulder_screw(L):
    """ISO 7379, shoulder Ø6: underside of the head at z = 0, head up."""
    s = cyl(10, 4.5).fuse(cyl(6, L, z0=-L)).fuse(cyl(5, 9.5, z0=-L - 9.5))
    return cut_all(s, [hexagon(3, 2.5 + E, 4.5 - 2.5)])


def retaining_ring(id_, od, t):
    r = tube(od, id_, t)
    return r.cut(box(4, od, t + 2 * E, 0, -od / 4, -E))


def bushing(id_, od, L, flange=None):
    s = tube(od, id_, L)
    if flange:
        fd, ft = flange
        s = s.fuse(tube(fd, id_, ft, z0=L)).clean()
    return s


def dowel(d, L):
    return cyl(d, L)


def detent_pin():
    """Rev E quick-release detent pin Ø6, usable length 64: tip at z = 0, collar and ring handle beyond z = 64."""
    return cyl(6, 64).fuse(cyl(12, 4, z0=64)).fuse(tube(22, 16, 3, z0=68))


def plunger():
    """M3 ball plunger: ball centre at z = 0."""
    return cyl(3, 6).fuse(cq.Solid.makeSphere(0.75, V(0, 0, 0)))


def thumb_screw():
    """dog-point thumb screw: Ø3.5 x 3 dog, M5 x 19, knurled head."""
    head = cut_all(cyl(12, 6, z0=22), [cyl(1.6, 6 + 2 * E, 6 * math.cos(math.radians(a)), 6 * math.sin(math.radians(a)), 22 - E) for a in range(0, 360, 30)])
    return cyl(3.4, 3).fuse(cyl(5, 19, z0=3)).fuse(head)


def bumper():
    return cyl(6, 10, z0=-10).fuse(cyl(16, 12))


def knob():
    k = cq.Workplane('XY').circle(7).extrude(18).edges('>Z').fillet(3).val()
    return k.fuse(cyl(5, 8, z0=-8))


def grip():
    g = tube(32, 24, 120)
    return cq.Workplane('XY').add(g).edges('%CIRCLE').edges(cq.selectors.RadiusNthSelector(1)).fillet(3).val()


def puller():
    return cyl(8, 50, -25, 0, 0, axis=(1, 0, 0)).fuse(cyl(5, 40, z0=-40)).fuse(cyl(10, 8, z0=-4))


def shim_pack():
    return cut_all(cyl(40, 1), [cyl(16.5, 1 + 2 * E, z0=-E), cyl(4.2, 1 + 2 * E, 0, -20, -E)])


def ball_plunger():
    return cut_all(cyl(6, 11.5), [box(1, 6, 1.5 + E, 0, 0, 10)]).fuse(cq.Solid.makeSphere(1.5, V(0, 0, 0)))


def adj_stop_screw():
    return set_screw(10, 12, cone_point=False, socket=5)


# =====================================================================================
# the parts list with placements (assembly frame)
# =====================================================================================
def build():
    # ---------------- frame ----------------
    part('MP-101', 'Base plate', 'make', 'Frame', mp101(), 'base', [at(0, 0, 3)])
    part('MP-102-F', 'Guide rail, front', 'make', 'Frame', mp102(P.RAIL_F), 'oxide', [at(0, -82, 18)])
    part('MP-102-B', 'Guide rail, back', 'make', 'Frame', mp102(P.RAIL_B), 'oxide', [at(0, 82, 18)])
    part('MP-103-F', 'Keeper strip, front', 'make', 'Frame', mp103(P.RAIL_F, [], -2), 'oxide', [at(0, -80, 30.05)])
    part('MP-103-B', 'Keeper strip, back', 'make', 'Frame', mp103([-215, -160, -40, 40, 160, 215], [-110, -92, 92, 110], 2), 'oxide', [at(0, 80, 30.05)])
    part('MP-104', 'Station stop block', 'make', 'Frame', mp104(), 'oxide', [at(-101, 76.5, 34.05), at(101, 76.5, 34.05)])
    part('MP-105', 'Die table (slide)', 'make', 'Die table', mp105(), 'gold', [at(SX, 0, 18)])
    part('MP-106', 'Die table stop pin', 'make', 'Die table', mp106(), 'oxide', [at(SX, 66, 24)])
    part('MP-107', 'Column', 'make', 'Frame', mp107(), 'chrome', [at(0, -105, 11.8), at(0, 105, 11.8)])
    part('MP-108', 'Crown', 'make', 'Frame', mp108(), 'oxide', [at(0, 0, 176)])
    part('MP-109', 'Ram', 'make', 'Press drive', mp109(), 'oxide', [at(0, 0, 134)])
    part('MP-110', 'Clevis', 'make', 'Press drive', mp110(), 'oxide', [at(0, 0, 162)])
    part('MP-111', 'Die holder', 'make', 'Press drive', mp111(), 'oxide', [at(0, 0, 123)])
    part('MP-112', 'Pivot cheek', 'make', 'Press drive', mp112(), 'oxide', [Tr(*SIDE_PLATE, at=(x, 0, 201)) for x in (-28, 28)])
    lever_pose = SIDE_PLATE + (('x', -PSI),)
    part('MP-113', 'Handle lever (one piece)', 'make', 'Press drive', mp113(), 'oxide', [Tr(*lever_pose, at=(0, 0, OY))])
    link_pose = SIDE_PLATE + (('x', -LINK_ANG),)
    part('MP-114', 'Toggle link', 'make', 'Press drive', mp114(), 'oxide', [Tr(*link_pose, at=(x, 0, B_Z)) for x in (-14, 14)])
    part('MP-116', 'Pin A / pin B (toggle)', 'make', 'Press drive', pin(39, 12, 11.5, 17.5), 'steel',
         [Tr(*ALONG_X, at=(-19.5, A_Y, A_Z)), Tr(*ALONG_X, at=(-19.5, 0, B_Z))])
    part('MP-117', 'Pin O (handle pivot)', 'make', 'Press drive', pin(78, 16, 15.2, 36), 'steel', [Tr(*ALONG_X, at=(-39, 0, OY))])
    part('MP-118', 'Return rod', 'make', 'Press drive', mp118(), 'zinc', [at(30, -60, 149), at(-30, 60, 149)])
    part('MP-119', 'Pivot spacer', 'make', 'Press drive', mp119(), 'bronze', [Tr(*ALONG_X, at=(10.1, 0, OY)), Tr(*ALONG_X, at=(-19.85, 0, OY))])
    part('MP-120', 'Station pilot', 'make', 'Press drive', mp120(), 'chrome', [at(0, 65, 50)])
    part('MP-121', 'Handle-stop post', 'make', 'Frame', mp121(), 'oxide', [at(0, -62, 201)])

    # ---------------- universal die ----------------
    part('MP-201', 'Upper die body (universal)', 'make', 'Universal die', mp201(), 'carrier', [at(0, 0, 112)])
    part('MP-202', 'Upper die shank (universal)', 'make', 'Universal die', mp202(), 'oxide', [at(0, 0, 113)])
    part('MP-205', 'Station base (universal)', 'make', 'Universal die', mp205(), 'oxide', [at(STA, 0, 30), at(STB, 0, 30)])
    part('MP-210', 'Upper carrier (universal)', 'make', 'Universal die', mp210(), 'carrier', [at(0, 0, 92)])
    part('MP-211-A', 'Lower carrier A (universal, pickup)', 'make', 'Universal die', mp211('A'), 'carrier', [at(STA, 0, 48)])
    part('MP-211-B', 'Lower carrier B (universal, crimp)', 'make', 'Universal die', mp211('B'), 'carrier', [at(STB, 0, 48)])
    part('MP-212', 'Plug stud (size kit, same for every size)', 'make', 'Size kit', mp212(), 'oxide', [at(P2.STUD[0], -P2.STUD[1], 104)])

    # ---------------- size kits (all four; kit 6363 is placed in the assembly) ----------------
    for code, X, Z in P.SIZES:
        shown = code == KIT_SHOWN
        pl = (lambda *p: list(p)) if shown else (lambda *p: [])
        lab = P.SIZE_LABEL[code]
        part('MP-203-%s' % code, 'Plug, kit %s' % lab, 'make', 'Size kit', mp203(X, Z), 'die', pl(at(0, 0, 97.5)))
        part('MP-204-%s' % code, 'Upper ring, kit %s' % lab, 'make', 'Size kit', mp204(X, Z), 'die', pl(at(0, 0, 92)))
        part('MP-206-%s' % code, 'Pickup pedestal, kit %s' % lab, 'make', 'Size kit', mp206(X, Z), 'die', pl(at(STA, 0, 40)))
        part('MP-207-%s' % code, 'Pickup ring A, kit %s' % lab, 'make', 'Size kit', mp207(X, Z), 'die', pl(at(STA, 0, 51)))
        part('MP-208-%s' % code, 'Crimp anvil, kit %s' % lab, 'make', 'Size kit', mp208(X, Z), 'die', pl(at(STB, 0, 40)))
        part('MP-209-%s' % code, 'Crimp ring B, kit %s' % lab, 'make', 'Size kit', mp209(X, Z), 'die', pl(at(STB, 0, 51)))

    for code, Dm in P2.ROUND:
        lab = P2.ROUND_LABEL[code]
        part('MP-223-%s' % code, 'Plug, round kit %s' % lab, 'make', 'Size kit', mp223(Dm), 'die', [])
        part('MP-224-%s' % code, 'Upper ring, round kit %s' % lab, 'make', 'Size kit', mp224(Dm), 'die', [])
        part('MP-226-%s' % code, 'Pickup pedestal, round kit %s' % lab, 'make', 'Size kit', mp226(Dm), 'die', [])
        part('MP-227-%s' % code, 'Pickup ring A, round kit %s' % lab, 'make', 'Size kit', mp227(Dm), 'die', [])
        part('MP-228-%s' % code, 'Crimp anvil, round kit %s' % lab, 'make', 'Size kit', mp228(Dm), 'die', [])
        part('MP-229-%s' % code, 'Crimp ring B, round kit %s' % lab, 'make', 'Size kit', mp229(Dm), 'die', [])

    # ---------------- bought parts: frame and drive ----------------
    part('BUY-01', 'Rubber pad Ø24 × 3', 'buy', 'Frame', cyl(24, 3), 'rubber',
         [at(x, y, 0) for (x, y) in ((-200, -80), (200, -80), (-200, 80), (200, 80), (-60, -300), (60, -300))], spec='NBR, adhesive; 6 per press (Rev E: two under the tongue)')
    rail_pts = [(x, -82) for x in P.RAIL_F] + [(x, 82) for x in (-215, -160, -40, 40, 160, 215)]
    part('BUY-02', 'Countersunk screw M5 × 30 ISO 10642', 'buy', 'Frame', csk_screw(5, 30, 11.2, 3), 'oxide', [at(x, y, 33.9) for (x, y) in rail_pts])
    part('BUY-03', 'Cap screw M5 × 35 ISO 4762 (stop blocks)', 'buy', 'Frame', cap_screw(5, 35, 8.5, 5, 4), 'oxide',
         [at(x, 82, 44.55) for x in (-110, -92, 92, 110)])
    stop_nut_x = 116.0
    part('BUY-04', 'Stop screw M6 × 0.75 × 40 hex', 'buy', 'Frame', hex_screw(6, 40, 10, 4), 'steel',
         [Tr(*ALONG_X, at=(83 + 40, 68, 42.05)), Tr(*ALONG_MX, at=(-83 - 40, 68, 42.05))])
    part('BUY-05', 'Thin lock nut M6 × 0.75', 'buy', 'Frame', nut(10, 3.2, 6), 'steel',
         [Tr(*ALONG_X, at=(stop_nut_x, 68, 42.05)), Tr(*ALONG_MX, at=(-stop_nut_x, 68, 42.05))])
    part('BUY-06', 'Column clamp screw M10 × 16 DIN 7984 (low head)', 'buy', 'Frame', cap_screw(10, 16, 16, 6, 7), 'oxide',
         [Tr(*DOWN, at=(0, y, 9)) for y in (-105, 105)])
    part('BUY-07', 'Column clamp washer Ø32 × 2.5, hardened', 'buy', 'Frame', tube(32, 10.5, 2.5), 'oxide', [at(0, y, 9) for y in (-105, 105)])
    part('BUY-08', 'Nord-Lock washer M16', 'buy', 'Frame', tube(25.4, 17, 3.4), 'steel', [at(0, y, 201) for y in (-105, 105)])
    part('BUY-09', 'Column nut M16 × 1.5', 'buy', 'Frame', nut(24, 13, 16), 'steel', [at(0, y, 204.4) for y in (-105, 105)])
    part('BUY-10', 'Handle stop screw M10 × 1 × 12, nylon patch (set screw)', 'buy', 'Frame', adj_stop_screw(), 'steel', [at(0, -62, Y_REST - 4 - 12)])
    part('BUY-12', 'Handle stop cap, urethane Ø16 × 4', 'buy', 'Frame', cyl(16, 4), 'ure', [at(0, -62, Y_REST - 4)])
    part('BUY-13', 'Flanged bronze bushing 25 × 32 × 33 (ram)', 'buy', 'Press drive', bushing(25, 32, 30, (40, 3)), 'bronze',
         [at(0, y, 134) for y in (-105, 105)], spec='self-lubricating, graphite plugs')
    part('BUY-14', 'PTFE-composite bushing 16 × 18 × 15 (cheeks)', 'buy', 'Press drive', bushing(16, 18, 15), 'ptfe',
         [Tr(*ALONG_X, at=(20.5, 0, OY)), Tr(*ALONG_X, at=(-35.5, 0, OY))])
    part('BUY-15', 'PTFE-composite bushing 16 × 18 × 20 (lever O)', 'buy', 'Press drive', bushing(16, 18, 20), 'ptfe', [Tr(*ALONG_X, at=(-10, 0, OY))])
    part('BUY-16', 'PTFE-composite bushing 12 × 14 × 20 (lever A, clevis)', 'buy', 'Press drive', bushing(12, 14, 20), 'ptfe',
         [Tr(*ALONG_X, at=(-10, A_Y, A_Z)), Tr(*ALONG_X, at=(-10, 0, B_Z))])
    part('BUY-17', 'PTFE-composite bushing 12 × 14 × 6 (links)', 'buy', 'Press drive', bushing(12, 14, 6), 'ptfe',
         [Tr(*ALONG_X, at=(x0, y, z)) for x0 in (11.5, -17.5) for (y, z) in ((A_Y, A_Z), (0, B_Z))])
    part('BUY-18', 'Retaining ring DIN 471-12', 'buy', 'Press drive', retaining_ring(11.5, 16.5, 1), 'oxide',
         [Tr(*ALONG_X, at=(x0, y, z)) for x0 in (17.6, -18.6) for (y, z) in ((A_Y, A_Z), (0, B_Z))])
    part('BUY-19', 'Retaining ring DIN 471-16', 'buy', 'Press drive', retaining_ring(15.2, 21.5, 1), 'oxide',
         [Tr(*ALONG_X, at=(x0, 0, OY)) for x0 in (36.1, -37.1)])
    part('BUY-20', 'Return spring Ø3.5 wire, OD 31.5 (shown installed, 109.5)', 'buy', 'Press drive', helix_spring(31.5, 3.5, 109.5, 18.4), 'wire',
         [at(30, -60, 201), at(-30, 60, 201)], spec='music wire, free length 128, about 16.4 active coils')
    part('BUY-21', 'Washer Ø32 × 3 (return rod)', 'buy', 'Press drive', tube(32, 10.5, 3), 'zinc', [at(30, -60, 310.5), at(-30, 60, 310.5)])
    part('BUY-49', 'Spring guide sleeve POM Ø24 × Ø10.5 × 60 (return rod)', 'buy', 'Press drive', tube(24, 10.5, 60), 'ptfe',
         [at(30, -60, 201), at(-30, 60, 201)], spec='Rev E: centres the return spring on its rod and stops it buckling')
    part('BUY-22', 'Nylock nut M10', 'buy', 'Press drive', nut(17, 10, 10), 'zinc', [at(30, -60, 313.5), at(-30, 60, 313.5)])
    part('BUY-23', 'Urethane bumper Ø16 × 12, M6 stud', 'buy', 'Press drive', bumper(), 'ure', [at(-30, -60, 164), at(30, 60, 164)])
    part('BUY-24', 'Cap screw M8 × 30 ISO 4762 (cheeks)', 'buy', 'Press drive', cap_screw(8, 30, 13, 8, 6), 'oxide',
         [Tr(*DOWN, at=(x, y, 182)) for x in (-28, 28) for y in (-17, 17)])
    part('BUY-25', 'Nord-Lock washer M8', 'buy', 'Press drive', tube(13.5, 8.7, 2.5), 'steel',
         [at(x, y, 182) for x in (-28, 28) for y in (-17, 17)])
    part('BUY-26', 'Dowel pin Ø6 × 16 (cheeks)', 'buy', 'Press drive', dowel(6, 16), 'steel', [at(x, 0, 193) for x in (-28, 28)])
    part('BUY-27', 'Cap screw M5 × 25 ISO 4762 (clevis)', 'buy', 'Press drive', cap_screw(5, 25, 8.5, 5, 4), 'oxide',
         [at(0, y, 178.5) for y in (-12, 12)])
    part('BUY-28', 'Low-head cap screw M5 × 16 DIN 7984 (die holder)', 'buy', 'Press drive', cap_screw(5, 16, 8.5, 3.5, 3), 'oxide',
         [Tr(*DOWN, at=(20 * math.cos(math.radians(a)), 20 * math.sin(math.radians(a)), 126.8)) for a in (45, 135, 225, 315)])
    part('BUY-29', 'Lock screw M5 × 10 ISO 4027, cone point (die holder)', 'buy', 'Press drive', set_screw(5, 10, socket=2.5), 'oxide',
         [Tr(*ALONG_X, at=(7.0, 0, 130.0))])
    part('BUY-30', 'Grip, red TPR Ø32 × 120', 'buy', 'Press drive', grip(), 'red', [grip_place()])

    # ---------------- bought parts: die table ----------------
    part('BUY-31', 'Spring ball plunger M6', 'buy', 'Die table', ball_plunger(), 'stain', [at(SX, -45, 18.5)])
    part('BUY-32', 'Push knob, phenolic Ø14 × 18, M5', 'buy', 'Die table', knob(), 'knob', [at(SX + 163, 0, 30), at(SX - 163, 0, 30)])

    # ---------------- bought parts: universal die ----------------
    spl = [(x, -z) for (x, z) in P2.SPR_LOW]
    spu = [(x, -z) for (x, z) in P2.SPR_UP]
    ret = [(x, -z) for (x, z) in P2.RET]
    part('BUY-33', 'Die spring ISO 10243 Ø10 × 32 green (light), shown installed 30', 'buy', 'Universal die',
         helix_spring(9.8, 1.6, 30, 6), 'green', [at(cx + x, y, 33) for cx in (STA, STB) for (x, y) in spl])
    part('BUY-34', 'Die spring ISO 10243 Ø12.5 × 44 red (heavy), shown installed 36', 'buy', 'Universal die',
         helix_spring(12.2, 2.2, 36, 7.5), 'red', [at(x, y, 94) for (x, y) in spu], spec='Rev E: 8 mm preload, 1.57 kN total; holds the upper ring while stroke 1 folds the flat tin blank')
    part('BUY-35', 'Shoulder screw ISO 7379 Ø6 × 10 (upper carrier)', 'buy', 'Universal die', shoulder_screw(10), 'oxide',
         [Tr(*DOWN, at=(x, y, 102)) for (x, y) in ret])
    part('BUY-36', 'Shoulder screw ISO 7379 Ø6 × 12 (lower carriers)', 'buy', 'Universal die', shoulder_screw(12), 'oxide',
         [at(cx + x, y, 52) for cx in (STA, STB) for (x, y) in ret])
    keys = [(STA + x, -z, 52) for (x, z) in P2.KEY['A']] + [(STB + x, -z, 52) for (x, z) in P2.KEY['B']] + [(x, -z, 92) for (x, z) in P2.KEY['U']]
    part('BUY-37', 'Key pin Ø4 × 14', 'buy', 'Universal die', dowel(4, 14), 'steel', [at(*k) for k in keys])
    part('BUY-38', 'Thumb screw M5, knurled, dog point Ø3.5 × 3 (upper ring)', 'buy', 'Universal die', thumb_screw(), 'knob',
         [Tr(*ALONG_X, at=(50.0, 0, 99)), Tr(*ALONG_MX, at=(-50.0, 0, 99))])
    part('BUY-39', 'Quick-release detent pin Ø6, usable length 64, ring handle', 'buy', 'Universal die', detent_pin(), 'stain',
         [Tr(*ALONG_MX, at=(P2.PIN_X1 - 1, -P2.PIN_Z, 116))])
    part('BUY-40', 'Countersunk screw M5 × 20 ISO 10642 (station bases)', 'buy', 'Universal die', csk_screw(5, 20, 11.2, 3), 'oxide',
         [Tr(*DOWN, at=(cx + x, -z, 18.15)) for cx in (STA, STB) for (x, z) in P2.BASE_FIX])
    part('BUY-41', 'Dowel pin Ø6 × 12 (station bases)', 'buy', 'Universal die', dowel(6, 12), 'steel',
         [at(cx + x, -z, 24) for cx in (STA, STB) for (x, z) in P2.BASE_DOWEL])
    part('BUY-42', 'Orientation pin Ø4 × 12', 'buy', 'Universal die', dowel(4, 12), 'steel', [at(0, -20, 116)])
    part('BUY-43', 'Depth shim pack Ø40 × 1', 'buy', 'Universal die', shim_pack(), 'stain', [at(0, 0, 122)], spec='stainless 0.1 / 0.2 / 0.5, shown as 1.0')
    part('BUY-44', 'Puller, M5 T-handle (loose tool)', 'buy', 'Universal die', puller(), 'knob', [])

    # ---------------- bought parts: size kit ----------------
    part('BUY-45', 'Ball plunger M3 (upper ring)', 'buy', 'Size kit', plunger(), 'stain',
         [Tr(*(TO_BACK if sy > 0 else TO_FRONT), at=(x, sy * (31.925 + 0.75 - 0.45), 92 + P2.UR_N)) for x in (-63.5 / 4, 63.5 / 4) for sy in (-1, 1)],
         spec='4 per kit; set the ball 0.4-0.5 proud of the opening, 2.5 above the ring bottom')
    part('BUY-46', 'Dowel pin Ø5 × 14 (plug)', 'buy', 'Size kit', dowel(5, 14), 'steel', [at(x, -z, 104) for (x, z) in P2.PLUG_DOWEL])
    part('BUY-47', 'Dowel pin Ø12 × 15 (pedestal and anvil spigot)', 'buy', 'Size kit', dowel(12, 15), 'steel', [at(STA, 0, 33), at(STB, 0, 33)])
    part('BUY-48', 'Pin Ø4 × 10 (pedestal and anvil anti-rotation)', 'buy', 'Size kit', dowel(4, 10), 'steel', [at(STA, -20, 36), at(STB, -20, 36)])


def grip_place():
    """grip centred 320 from O along the handle, axis along the handle."""
    u = P.GRIP_C - 60
    y, z = lever_pt(u, 0, PSI)
    return Tr(('x', 90 - PSI), at=(0, y, z))


def overlaps(placed, skip):
    """pairs of placed parts [(name, pid, shape)] that overlap by more than 1 mm^3."""
    boxes = [(n, s, s.BoundingBox()) for (n, pid, s) in placed]
    hits = []
    for i in range(len(boxes)):
        n1, s1, b1 = boxes[i]
        for j in range(i + 1, len(boxes)):
            n2, s2, b2 = boxes[j]
            if b1.xmax < b2.xmin or b2.xmax < b1.xmin or b1.ymax < b2.ymin or b2.ymax < b1.ymin or b1.zmax < b2.zmin or b2.zmax < b1.zmin:
                continue
            if skip(n1, n2):
                continue
            v = s1.intersect(s2).Volume()
            if v > 1.0:
                hits.append((n1, n2, v))
    return hits


POSES = (50.0, 35.0, 20.0, 10.0, 3.0)          # handle angles checked besides the placed (open) pose; 3 deg = on the stop
RAM_MOVES = {'MP-109', 'BUY-13', 'MP-110', 'BUY-27', 'MP-111', 'BUY-28', 'BUY-29', 'MP-120', 'MP-118', 'BUY-23', 'BUY-21', 'BUY-22',
             'MP-201', 'MP-202', 'MP-210', 'BUY-34', 'BUY-35', 'BUY-38', 'BUY-39', 'BUY-42', 'BUY-43', 'MP-212', 'BUY-46', 'BUY-45',
             'MP-203-' + KIT_SHOWN, 'MP-204-' + KIT_SHOWN, 'BUY-16_2', 'MP-116_2', 'BUY-17_2', 'BUY-17_4', 'BUY-18_2', 'BUY-18_4',
             'BUY-37_5', 'BUY-37_6'}
LEVER_MOVES = {'MP-113', 'BUY-15', 'BUY-30', 'BUY-16_1', 'MP-116_1', 'BUY-17_1', 'BUY-17_3', 'BUY-18_1', 'BUY-18_3'}


def pose(inst, psi):
    """the placed assembly at handle angle psi: ram group lowered, lever turned about O, links re-placed. Returns (parts, ram drop)."""
    a_y, a_z = lever_pt(A_U, A_W, psi)
    b_z = a_z - math.sqrt(60.0 ** 2 - a_y ** 2)
    out = []
    link_local = next(p['shape'] for p in PARTS if p['id'] == 'MP-114')
    ang = math.degrees(math.atan2(a_z - b_z, -a_y))
    for n, pid, s, c in inst:
        if n in RAM_MOVES or pid in RAM_MOVES:
            s = s.translate(V(0, 0, b_z - B_Z))
        elif n in LEVER_MOVES or pid in LEVER_MOVES:
            s = s.translate(V(0, 0, -OY)).rotate(V(0, 0, 0), V(1, 0, 0), PSI - psi).translate(V(0, 0, OY))
        elif pid == 'MP-114':
            x = -14 if n.endswith('_1') else 14
            s = Tr(*(SIDE_PLATE + (('x', -ang),)), at=(x, 0, b_z))(link_local)
        out.append((n, pid, s))
    return out, B_Z - b_z


# =====================================================================================
# export
# =====================================================================================
def slug(s):
    out = ''.join(c.lower() if c.isascii() and c.isalnum() else '-' for c in s.replace('Ø', 'd').replace('×', 'x'))
    while '--' in out:
        out = out.replace('--', '-')
    return out.strip('-')


def write_obj(path, items, mtl=None, tol=(0.05, 0.2)):
    """items: [(name, shape, rgb)]. One OBJ object per item."""
    vo = 1
    with open(path, 'w') as f:
        f.write('# MagPress M4 Rev C, units mm\n')
        if mtl:
            f.write('mtllib %s\n' % os.path.basename(mtl))
        mats = {}
        for name, shape, rgb in items:
            vs, tris = shape.tessellate(*tol)
            f.write('o %s\n' % name)
            if mtl:
                key = 'm_%02x%02x%02x' % tuple(int(c * 255) for c in rgb)
                mats[key] = rgb
                f.write('usemtl %s\n' % key)
            for v in vs:
                f.write('v %.4f %.4f %.4f\n' % (v.x, v.y, v.z))
            for a, b, c in tris:
                f.write('f %d %d %d\n' % (a + vo, b + vo, c + vo))
            vo += len(vs)
    if mtl:
        with open(mtl, 'w') as f:
            for k, (r, g, b) in sorted(mats.items()):
                f.write('newmtl %s\nKd %.3f %.3f %.3f\nKa 0 0 0\nKs 0.2 0.2 0.2\nNs 40\n\n' % (k, r, g, b))


def main():
    for d in ('step', 'stl', 'obj', 'assembly'):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    print('handle angle %.3f deg, pin A (Y %.3f, Z %.3f), link %.3f deg, handle-stop rest %.2f' % (PSI, A_Y, A_Z, LINK_ANG, Y_REST))
    build()
    rows, inst = [], []
    for p in PARTS:
        s = p['shape']
        if not s.isValid():
            s = s.fix()
            print('  fixed shape', p['id'])
        base = '%s_%s' % (p['id'], slug(p['name']))
        cq.exporters.export(s, os.path.join(OUT, 'step', base + '.step'))
        cq.exporters.export(s, os.path.join(OUT, 'stl', base + '.stl'), tolerance=0.05, angularTolerance=0.2)
        write_obj(os.path.join(OUT, 'obj', base + '.obj'), [(p['id'], s, p['color'])])
        bb = s.BoundingBox()
        rows.append([p['id'], p['name'], p['src'], p['group'], len(p['places']), '%.1f × %.1f × %.1f' % (bb.xlen, bb.ylen, bb.zlen),
                     '%.0f' % s.Volume(), base, p['spec']])
        for n, f in enumerate(p['places'], 1):
            inst.append(('%s_%d' % (p['id'], n), p['id'], f(s), p['color']))
        print('  %-10s %-55s x%d' % (p['id'], p['name'][:55], len(p['places'])))
    with open(os.path.join(OUT, 'parts.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['id', 'name', 'make_or_buy', 'group', 'qty_in_assembly', 'size_xyz_mm', 'volume_mm3', 'file_base', 'note'])
        w.writerows(rows)

    assy = cq.Assembly(name='MagPress-M4_RevC')
    for name, pid, s, rgb in inst:
        assy.add(s, name=name, color=cq.Color(rgb[0], rgb[1], rgb[2], 1.0))
    exportAssembly(assy, os.path.join(OUT, 'assembly', 'MagPress-M4_assembly.step'))
    write_obj(os.path.join(OUT, 'assembly', 'MagPress-M4_assembly.obj'), [(n, s, c) for (n, _, s, c) in inst],
              mtl=os.path.join(OUT, 'assembly', 'MagPress-M4_assembly.mtl'), tol=ASSY_TOL)
    try:
        import trimesh
        sc = trimesh.Scene()
        for name, pid, s, rgb in inst:
            vs, tris = s.tessellate(*ASSY_TOL)
            m = trimesh.Trimesh([(v.x, v.z, -v.y) for v in vs], tris, process=False)    # glTF is Y-up
            m.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
                name=pid, baseColorFactor=[int(c * 255) for c in rgb] + [255], metallicFactor=0.3, roughnessFactor=0.55))
            sc.add_geometry(m, node_name=name, geom_name=name)
        with open(os.path.join(OUT, 'assembly', 'MagPress-M4_assembly.glb'), 'wb') as f:
            f.write(trimesh.exchange.gltf.export_glb(sc, include_normals=True))
    except ImportError:
        print('trimesh not installed: GLB skipped')

    # ---------------- interference checks: handle up (as placed) and handle down ----------------
    groups = {p['id']: p['group'] for p in PARTS}
    open_pose = [(n, pid, s) for (n, pid, s, c) in inst]
    hits_open, below = overlaps(open_pose, skip=lambda a, b: False), []
    for n, pid, s in open_pose:
        z = s.BoundingBox().zmin
        if z < -0.1:
            below.append((n, z))
    die = lambda n: groups[n.rsplit('_', 1)[0]] in ('Universal die', 'Size kit')
    skip = lambda a, b: (die(a) and die(b)) or 'BUY-20' in (a.rsplit('_', 1)[0], b.rsplit('_', 1)[0])
    moving = []
    for psi in POSES:
        placed, drop = pose(inst, psi)
        moving.append((psi, drop, overlaps(placed, skip)))
    hits_closed = [h for (_, _, hs) in moving for h in hs]
    # Rev D: a round kit (with its own dowels, stud and plungers) fitted instead of kit 6363, handle up
    rk, Dm = 'D58', dict(P2.ROUND)['D58']
    shapes = {p['id']: p['shape'] for p in PARTS}
    sq = {'%s-%s' % (m, KIT_SHOWN) for m in ('MP-203', 'MP-204', 'MP-206', 'MP-207', 'MP-208', 'MP-209')} | {'BUY-45', 'BUY-46', 'BUY-48', 'MP-212'}
    rnd = [(n, pid, s) for (n, pid, s) in open_pose if pid not in sq]
    def fit(pid, f, k=1):
        rnd.append(('%s_r%d' % (pid, k), pid, f(shapes[pid])))
    for m, place in (('MP-223', at(0, 0, 97.5)), ('MP-224', at(0, 0, 92)), ('MP-226', at(STA, 0, 40)), ('MP-227', at(STA, 0, 51)),
                     ('MP-228', at(STB, 0, 40)), ('MP-229', at(STB, 0, 51))):
        fit('%s-%s' % (m, rk), place)
    for k, (x, z) in enumerate(P2.PLUG_DOWEL_R, 1):
        fit('BUY-46', at(x, -z, 104), k)
    fit('MP-212', at(P2.STUD_R[0], -P2.STUD_R[1], 104))
    yb, k = math.sqrt(((Dm + 0.35) / 2) ** 2 - (Dm / 4) ** 2), 0
    for x in (-Dm / 4, Dm / 4):
        for sy in (-1, 1):
            k += 1
            fit('BUY-45', Tr(*(TO_BACK if sy > 0 else TO_FRONT), at=(x, sy * (yb + 0.75 - 0.25), 93.8)), k)
    hits_round = overlaps(rnd, skip=lambda a, b: False)
    with open(os.path.join(OUT, 'assembly', 'interference.txt'), 'w') as f:
        f.write('Interference check, MagPress M4 Rev E assembly (station B under the ram, kit %s)\n' % KIT_SHOWN)
        f.write('%d placed parts. Overlaps above 1 mm^3 (touching faces and press fits at the same nominal size are not overlaps).\n' % len(inst))
        f.write('Through the stroke, die parts against die parts are not checked: the spring-loaded rings telescope by design. '
                'Return springs are not checked (they compress).\n')
        for title, hits in [('Handle up, %.1f deg (as placed in the assembly files)' % PSI, hits_open)] + \
                [('Handle at %.0f deg%s (ram %.1f mm down)' % (psi, ', on the stop' if psi == POSES[-1] else '', drop), hs) for (psi, drop, hs) in moving] + \
                [('Round kit %s fitted instead of kit %s, with its dowels on the inner pattern D2, stud in K2 and plungers, handle up' % (rk, KIT_SHOWN), hits_round)]:
            f.write('\n%s:\n' % title)
            for a_, b_, v in sorted(hits, key=lambda h: -h[2]):
                f.write('  %-14s x %-14s %10.1f mm^3\n' % (a_, b_, v))
            if not hits:
                f.write('  none\n')
        f.write('\nParts reaching below the bench (Z < 0):\n')
        for n, z in below:
            f.write('  %-14s lowest point Z = %.2f\n' % (n, z))
        if not below:
            f.write('  none\n')
    print('%d part files, %d placed instances, overlaps: %d handle up, %d through the stroke, %d with round kit %s; %d below the bench'
          % (len(PARTS), len(inst), len(hits_open), len(hits_closed), len(hits_round), rk, len(below)))


if __name__ == '__main__':
    main()
