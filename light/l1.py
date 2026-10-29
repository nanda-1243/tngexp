"""MagPress L1: light photo-magnet press, one die set for 63.5 x 63.5 square magnets with the market edge.

Single source for the drawings (light/build_drawings.py), the 3D models (light/build_models.py) and the calculations
(light/calcs.py). Everything is in mm.

Assembly frame: X along the die table (left to right as the operator sees it), +Y toward the back (the operator stands at
-Y), Z up from the bench. The two columns stand at X = 0, Y = +-80; the ram moves along Z at X = Y = 0.
Plate parts: plan (u, w) = assembly (X, Y), thickness up from the bottom face. Feature lists use cad/draft.py `feat`
(x, z) with z = -Y (the front is +z there), so `F(x, y, ...)` below takes the assembly Y.
Profile parts (lever, links, cheeks, lug) are cut from plate and stand in the X-Z plane: their (u, w) is (X, Z) and the
plate thickness runs along Y.

ASSUMED MATERIAL (to confirm with a pre-cut set from the chosen seller): tin 71.5 x 71.5 x 0.23, photo and film
79 x 79 octagons, acrylic card 60.5 x 60.5 x 3.0, magnet sheet 57 x 57 x 1.0. Parts that change if these change are
marked with MAT in their notes.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'cad'))
from draft import feat, rrect, L, A, C   # noqa: E402

REV, DATE = 'L1-A', '2026-10-29'
PROJECT = 'MagPress L1 · light photo-magnet press'

# ------------------------------------------------------------------------------------------------------------------
# magnet and material (ASSUMED until a seller's set is measured)
# ------------------------------------------------------------------------------------------------------------------
FACE = 63.5            # finished face, square
T_TIN, T_PHOTO, T_FILM = 0.23, 0.12, 0.075
T_STACK = T_TIN + T_PHOTO + T_FILM          # 0.425
TIN = 71.5             # flat tin blank, square, corners clipped 45 deg (4.0 a side past the face)
PHOTO = 79.0           # photo and film, octagon (corners clipped)
ACR, T_ACR = 60.5, 3.0  # acrylic back card
MAG, T_MAG = 57.0, 1.0  # magnet sheet (self-adhesive, stuck centred on the card before pressing)
FINISHED_T = T_STACK + T_ACR + T_MAG        # 4.425

# ------------------------------------------------------------------------------------------------------------------
# die set (63.5 x 63.5)
# ------------------------------------------------------------------------------------------------------------------
PED = 62.65            # pedestal: face - 2 x (stack 0.425); R0.5 corners, top edge R0.3
PED_R, PED_EDGE = 0.5, 0.3
RA_OPEN, RA_OPEN_R = 70.0, 1.0      # ring A opening (tin ledge 0.75 a side under a 71.5 blank)
RA_TIN, RA_TIN_R = 72.0, 1.0        # tin pocket
RA_PHOTO, RA_PHOTO_R = 79.5, 3.0    # photo / film pocket
RA_STEP1, RA_STEP2 = 0.25, 0.50     # pocket floors below the ring A top (photo, tin)
RA_EDGE = 0.5                       # radius on the opening's top edge (the ledge the tin slides off)
BORE, BORE_R = 63.85, 1.2           # upper ring bore
MOUTH_R = 2.5                       # upper ring mouth radius (bottom edge of the bore)
PLUG, PLUG_R, PLUG_EDGE = 63.4, 1.0, 0.2   # inside the face (63.5) so it passes inside the cup ring's nose
RECESS = 7.1                        # plug face above the upper ring bottom, ring at rest: the whole 4 mm wall ends up in the
                                    # straight bore above the R2.5 mouth, so it comes out of stroke 1 straight (no flare)
CUP_TOP, CUP_R, CUP_ALPHA = 63.6, 1.0, 18.0   # cup ring opening at the top, corner radius, taper from vertical (deg)
CUP_T = FINISHED_T                  # cup ring below its landing face = finished magnet thickness (MAT)
CUP_BOT = CUP_TOP - 2 * CUP_T * math.tan(math.radians(CUP_ALPHA))
# Nose: a 1 mm raised square ring round the opening that fills the upper ring's R2.5 mouth when the ring lands, so the
# shell wall stays held from outside as it passes from the bore into the taper (a flat rim let the flared wall end land
# on it and buckle, verify/stroke2L.py). Inner face = the taper carried up; flat top; outer chamfer clear of the mouth.
NOSE = 1.0
NOSE_IN = CUP_TOP + 2 * NOSE * math.tan(math.radians(CUP_ALPHA))      # opening at the nose top, 64.25
NOSE_TOP = FACE + 2 * 0.613                                           # outer edge of the nose's top flat, 64.73
NOSE_BASE = FACE + 2 * 1.453                                          # foot of the outer chamfer on the landing face, 66.41

# ------------------------------------------------------------------------------------------------------------------
# heights (Z) at the bottom of the stroke (handle on its stop)
# ------------------------------------------------------------------------------------------------------------------
BASE_T = 12.0
TABLE_T = 10.0
Z_TABLE = BASE_T + TABLE_T          # 22.0, table top
Z_FACE = 58.1                       # magnet face top at the end of both strokes = plug face
# station A
BB_T = 21.0                         # base block (the ring A shoulder screws travel in it)
RA_T = 8.0                          # ring A
RA_TRAVEL = RECESS + 1.4             # 8.5: pedestal top 1.325 below the tin at rest, tin pocket 0.5 deep, less the stack
Z_BB = Z_TABLE + BB_T               # 37.4
Z_RA_REST = Z_BB + RA_TRAVEL        # ring A bottom at rest 43.4 (top 51.4)
PED_H = Z_FACE - T_STACK - Z_BB     # 12.175
# station B
RIS_T = Z_FACE - CUP_T - Z_TABLE    # 23.575
# upper die
UR_T = 14.0                         # upper ring
UR_GAP = 8.5                        # gap between upper ring and die body, ring at rest (> the 7.1 retraction)
DB_T = 54.0                         # die body (long upper springs)
PLUG_H, SHIM = 15.0, 0.4            # plug and nominal shim pack
PLUG_DROP = PLUG_H + SHIM           # plug face below the die body
assert abs((UR_T + UR_GAP - RECESS) - PLUG_DROP) < 1e-9
Z_DB = Z_FACE + PLUG_DROP           # die body bottom at the stop, 65.4
RAM_T = 25.0
Z_RAM = Z_DB + DB_T                 # ram bottom at the stop, 100.4
LUG_PIN = 26.0                      # pin B above the ram top
Z_B = Z_RAM + RAM_T + LUG_PIN       # 151.4

# ------------------------------------------------------------------------------------------------------------------
# toggle: the lever is a fork of two plates (Y +-8..16) on two stub pins O held in the cheeks; the crank O->A is part of
# the lever plates; ONE central link (Y +-7.5) from pin A to pin B in the ram clevis. theta = crank angle from straight down.
# ------------------------------------------------------------------------------------------------------------------
R_CRANK, L_LINK = 18.0, 55.0
Z_O = 251.1
HEAD_T = 30.0
O_ABOVE_HEAD = 20.0
Z_HEAD = Z_O - O_ABOVE_HEAD - HEAD_T     # head bottom 174.0
COL_Y = 80.0
THETA_UP = 70.0                          # handle up (ram up, on the up-stop collars)
HANDLE_OFF = 77.0                        # handle direction = crank direction + 77 deg
GRIP_C = 400.0                           # grip centre from O along the handle
LEVER_LEN = 460.0                        # O to the rounded end of the handle bar
LEVER_W, LEVER_T = 30.0, 8.0            # each of the two lever plates
LEVER_Y = (8.0, 16.0)                    # lever plates between |Y| 8 and 16; the link (15 thick) runs between them
PIN_D = 16.0                             # pins O (stubs), A, B
LINK_T, LINK_R = 15.0, 14.0


def drop(theta_deg):
    """O to B (vertical) at crank angle theta."""
    t = math.radians(theta_deg)
    return R_CRANK * math.cos(t) + math.sqrt(L_LINK ** 2 - (R_CRANK * math.sin(t)) ** 2)


def dB_dtheta(theta_deg):
    t = math.radians(theta_deg)
    s = math.sqrt(L_LINK ** 2 - (R_CRANK * math.sin(t)) ** 2)
    return R_CRANK * math.sin(t) * (1 + R_CRANK * math.cos(t) / s)       # mm of ram per rad of crank


def theta_for_drop(d):
    lo, hi = 0.0, 90.0
    for _ in range(80):
        m = (lo + hi) / 2
        if drop(m) > d:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


THETA_STOP = theta_for_drop(Z_O - Z_B)   # crank angle on the handle stop (about 10.5 deg)
STROKE = drop(THETA_STOP) - drop(THETA_UP)
Z_RAM_UP = Z_RAM + STROKE                # ram bottom with the handle up


def handle_angle(theta):
    return theta - 90.0 + HANDLE_OFF


_h = math.radians(handle_angle(THETA_STOP))
STOP_X = 38.0                             # handle stop screws in the head, under the lever plates (Y +-12)
STOP_Z = Z_O + (STOP_X + 4.0) * math.tan(_h) - (LEVER_W / 2) / math.cos(_h)   # lever lower edge over the M8 tip, on the stop


# ------------------------------------------------------------------------------------------------------------------
# springs
# ------------------------------------------------------------------------------------------------------------------
# upper ring: 4 x ISO 10243 red (heavy load) D20 x 76, rate about 62 N/mm (scaled from 37.3 N/mm for D20 x 127)
UP_SPR = dict(d=20.0, L0=76.0, k=62.3, n=4, pocket_ring=8.0, pocket_body=48.0)
UP_SPR['inst'] = UP_SPR['pocket_ring'] + UR_GAP + UP_SPR['pocket_body']          # 43.0
UP_SPR['pre'] = UP_SPR['L0'] - UP_SPR['inst']                                     # 8.0
# ring A: 4 x ISO 10243 green (light load) D10 x 38, rate about 6.6 N/mm; pockets right through the base block
RA_SPR = dict(d=10.0, L0=38.0, k=6.6, n=4, pocket_ring=5.6, pocket_body=BB_T)
RA_SPR['inst'] = RA_SPR['pocket_ring'] + RA_TRAVEL + RA_SPR['pocket_body']        # 22.0
RA_SPR['pre'] = RA_SPR['L0'] - RA_SPR['inst']                                     # 3.0
# return springs on the columns: wire 3.6, mean D 24.6, 8 active coils, L0 80 (k = G d^4 / 8 D^3 n = 13.9 N/mm)
RET_SPR = dict(id=21.0, od=28.2, wire=3.6, L0=80.0, k=13.9, n_act=8)
COLLAR = dict(d=20.0, D=32.0, b=14.0)                      # DIN 705 A 20
SH_RA, SH_UR = 16.0, 40.0                                  # shoulder lengths: ring A (ISO 7379 D6), upper ring (D10)
Z_SEAT = round(Z_RAM_UP - 70.5, 1)                         # top of the spring seat collars (70.5 installed, handle up)
Z_UPSTOP = Z_RAM_UP + RAM_T                                # underside of the up-stop collars = ram top, handle up

# ------------------------------------------------------------------------------------------------------------------
# table and stations
# ------------------------------------------------------------------------------------------------------------------
TABLE_L, TABLE_W = 330.0, 99.6
ST_X = 75.0                     # stations at table x = -75 (A) and +75 (B); the table slides +-75
ST = 110.0                      # station blocks, square
RAIL_W, RAIL_H, RAIL_L = 12.0, 9.0, 360.0
RAIL_IN = TABLE_W / 2 + 0.05    # rail inner faces (set on assembly to 0.05 a side)
RAIL_Y = RAIL_IN + RAIL_W / 2
BASE_L, BASE_W = 360.0, 220.0
DETENT = (0.0, -37.0)           # ball plunger in the table (table x, y); dimples in the base at X = +-75
STOP_Y = -15.0                  # stop pin in the base / slot under the table
SLOT_HALF = ST_X + 5.25 + 0.25  # slot end centres +-(75 + 0.25): the pin stops the table 0.25 past the detent


def F(x, y, kind, **kw):
    """feature at assembly-plan (x, y)."""
    return feat(x, -y, kind, **kw)


def P(x, y, kind, **kw):
    """feature on a profile part at (u, w) of its own outline."""
    return feat(x, -y, kind, **kw)


def sq(w, r=0.0, cx=0.0, cy=0.0):
    return rrect(cx, cy, w, w, r)


# ------------------------------------------------------------------------------------------------------------------
# outlines of profile parts
# ------------------------------------------------------------------------------------------------------------------
def lever_outline():
    """lever in its own frame: O at the origin, crank straight down to A (0, -R), handle bar along HANDLE_OFF - 90."""
    rh, ra, R, hw = 16.0, LINK_R, R_CRANK, LEVER_W / 2
    a = math.radians(HANDLE_OFF - 90.0)
    d = (math.cos(a), math.sin(a))
    n = (-math.sin(a), math.cos(a))                 # left normal of the bar (up)
    # external tangents between hub (0,0,rh) and lobe (0,-R,ra): m.p = rh, m.(0,-R) = rh - ra
    my = -(rh - ra) / R
    mx = math.sqrt(1 - my * my)
    t_hub_r, t_lobe_r = (rh * mx, rh * my), (ra * mx, -R + ra * my)
    t_hub_l, t_lobe_l = (-rh * mx, rh * my), (-ra * mx, -R + ra * my)
    # upper bar edge meets the hub circle
    tt = math.sqrt(rh * rh - hw * hw)
    p1 = (hw * n[0] + tt * d[0], hw * n[1] + tt * d[1])
    # lower bar edge meets the right tangent line m.p = rh
    q0 = (-hw * n[0], -hw * n[1])
    t = (rh - (mx * q0[0] + my * q0[1])) / (mx * d[0] + my * d[1])
    q = (q0[0] + t * d[0], q0[1] + t * d[1])
    e = (LEVER_LEN * d[0], LEVER_LEN * d[1])
    e_bot = (e[0] - hw * n[0], e[1] - hw * n[1])
    e_top = (e[0] + hw * n[0], e[1] + hw * n[1])
    ang = lambda p, c=(0.0, 0.0): math.degrees(math.atan2(p[1] - c[1], p[0] - c[0]))
    nd = math.degrees(math.atan2(n[1], n[0]))
    a_tl, a_tr = ang(t_lobe_l, (0, -R)), ang(t_lobe_r, (0, -R))
    segs = [L(*t_hub_l, *t_lobe_l),
            A(0, -R, ra, a_tl % 360, (a_tr % 360) if (a_tr % 360) > (a_tl % 360) else a_tr % 360 + 360),
            L(*t_lobe_r, *q), L(*q, *e_bot),
            A(e[0], e[1], hw, (nd + 180) % 360, (nd + 180) % 360 + 180),
            L(*e_top, *p1),
            A(0, 0, rh, ang(p1) % 360, ang(t_hub_l) % 360)]
    return segs


def link_outline():
    r = LINK_R
    return [L(0, -r, L_LINK, -r), A(L_LINK, 0, r, 270, 450), L(L_LINK, r, 0, r), A(0, 0, r, 90, 270)]


CHEEK = dict(L=50.0, H=34.0, T=18.0, pin=O_ABOVE_HEAD, r=14.0)
CHEEK_Y = (18.5, 36.5)          # inner and outer faces of the cheeks (|Y|): clear of pin A's ends (+-18) as it swings
CHEEK_SCREW_Y = 27.5            # head screws and dowels on the cheeks' centre line (|Y|), outside the head window


def cheek_outline():
    c = CHEEK
    hl, H, r, p = c['L'] / 2, c['H'], c['r'], c['pin']
    return [L(-hl, 0, hl, 0), L(hl, 0, hl, p), A(hl - r, p, r, 0, 90), L(hl - r, p + r, -hl + r, p + r), A(-hl + r, p, r, 90, 180),
            L(-hl, p, -hl, 0)]


CLEVIS = dict(L=30.0, W=32.0, base=11.0, slot=16.0, pin=LUG_PIN, r=15.0)


def clevis_outline():
    """ram clevis, side profile (X, Z); 32 thick along Y with a 16 wide slot from Z 11 up."""
    g = CLEVIS
    h, p, r = g['L'] / 2, g['pin'], g['r']
    return [L(-h, 0, h, 0), L(h, 0, h, p), A(0, p, r, 0, 180), L(-h, p, -h, 0)]


GRIP_SPACER = dict(L=110.0, W=LEVER_W, T=2 * LEVER_Y[0], u0=GRIP_C - 55.0)
SPACER_U = (70.0, 100.0)        # spacer tubes between the lever plates, along the handle from O
GRIP_BOLT_U = (GRIP_C - 35.0, GRIP_C + 35.0)


# ------------------------------------------------------------------------------------------------------------------
# part list
# ------------------------------------------------------------------------------------------------------------------
GEN = ['General tolerances ISO 2768-mK unless stated. Break sharp edges 0.3 x 45 deg, except the forming edges (stated).',
       'Light design L1, one size (63.5 x 63.5). Material sizes are ASSUMED until a seller\'s pre-cut set is measured: parts '
       'marked MAT may change by a few tenths of a mm before manufacture.']
S275 = 'S275 (IS 2062 E250/E350) steel plate'
AL = '6061-T6 aluminium plate'
D2 = 'D2 / 1.2379 tool steel (prototype: 1.2312 P20 prehardened 30 HRC)'
HARD = 'Harden and temper 58-60 HRC (D2); prototype in P20: no heat treatment'

PARTS = []


def part(**kw):
    kw.setdefault('feats', [])
    kw.setdefault('notes', [])
    kw.setdefault('dxf', True)
    kw.setdefault('kind', 'plate')
    PARTS.append(kw)
    return kw


# ---------------- frame ----------------
part(id='L-101', name='BASE PLATE', qty=1, group='frame', material=S275 + ' 12', finish='Black powder coat; slide area '
     'X +-170 x Y +-50 left bare, ground or surface-finished Ra 1.6, oiled',
     T=BASE_T, outline=rrect(0, 0, BASE_L, BASE_W, 10),
     feats=[F(0, -COL_Y, 'tap', m='M12', thru=True, label='C1'), F(0, COL_Y, 'tap', m='M12', thru=True, label='C2')] +
           [F(x, s * RAIL_Y, 'tap', m='M4', depth=10, side='top', label='R') for s in (-1, 1) for x in (-150, -50, 50, 150)] +
           [F(0, STOP_Y, 'hole', d=10, depth=10.5, side='top', label='S'),
            F(-ST_X, DETENT[1], 'spot', d=5, depth=1.5, label='D1'), F(ST_X, DETENT[1], 'spot', d=5, depth=1.5, label='D2')] +
           [F(sx * 165, sy * 95, 'hole', d=9, thru=True, label='M') for sx in (-1, 1) for sy in (-1, 1)],
     rows=[['C', '(0, +-80)', 'M12 THRU, square to the top face within 0.05 over 12 (columns L-104)'],
           ['R', '(+-50, +-150; Y +-%s)' % ('%.2f' % RAIL_Y), 'M4 x 10 (rails L-102), 8 off'],
           ['S', '(0, %g)' % STOP_Y, 'D10 H7 x 10.5 deep (stop pin D10 m6 x 16, 5.5 proud)'],
           ['D', '(+-75, %g)' % DETENT[1], 'Dimple: 90 deg spot drill to D5 (detent ball of the table)'],
           ['M', '(+-165, +-95)', 'D9 THRU (bench bolts M8)']],
     notes=['Top face flat within 0.1 over the table slide area.'])

part(id='L-102', name='TABLE RAIL', qty=2, group='frame', material='Bright mild steel flat 12 x 9 (EN8 / C45 bright bar)',
     finish='Black oxide or zinc; inner face oiled', T=RAIL_H, outline=rrect(0, 0, RAIL_L, RAIL_W, 0),
     feats=[F(x, 0, 'hole', d=4.5, thru=True, cb=(8.0, 4.5), label='') for x in (-150, -50, 50, 150)],
     rows=[['-', '(+-50, +-150; 0)', 'D4.5 THRU, c\'bore D8 x 4.5 from the top (M4 x 10 cap screws)']],
     notes=['Inner faces straight within 0.05 over the length. Set on assembly with the table between them: 0.05 a side, then tighten.'])

part(id='L-103', name='SLIDING TABLE', qty=1, group='frame', material=AL + ' 10', finish='Hard anodise (or clear anodise)',
     T=TABLE_T, outline=rrect(0, 0, TABLE_L, TABLE_W, 5),
     feats=[F(sx * ST_X + dx, dy, 'hole', d=6.6, thru=True, cb=(11.0, 6.5), cbside='bot', side='bot', label='K')
            for sx in (-1, 1) for dx in (-45, 45) for dy in (-30, 30)] +
           [F(sx * ST_X - 20, 45, 'hole', d=6, thru=True, label='P') for sx in (-1, 1)] +
           [F(sx * ST_X + 20, -45, 'hole', d=6, thru=True, label='P') for sx in (-1, 1)] +
           [F(0, STOP_Y, 'rr', w=2 * SLOT_HALF, h=10.5, r=5.25, depth=6.0, side='bot', label='SL'),
            F(DETENT[0], DETENT[1], 'tap', m='M10', thru=True, label='BP'),
            F(-150, 0, 'tap', m='M8', thru=True, label='KN'), F(150, 0, 'tap', m='M8', thru=True, label='KN')],
     rows=[['K', 'station x +-75 +-45, y +-30', 'D6.6 THRU, c\'bore D11 x 6.5 from the BOTTOM (M6 x 12, stations), 8 off'],
           ['P', '(-95, +45) (-55, -45) (55, +45) (95, -45)', 'D6 H7 THRU (dowels D6 m6 x 16 into the station blocks)'],
           ['SL', 'y %g, x +-%.2f' % (STOP_Y, SLOT_HALF), 'Slot 10.5 wide x 6 deep in the BOTTOM face, ends R5.25 (stop pin)'],
           ['BP', '(0, %g)' % DETENT[1], 'M10 THRU (ball plunger M10, ball 1.5 below the bottom face)'],
           ['KN', '(+-150, 0)', 'M8 THRU (DIN 319 knob D32)']],
     notes=['Station A at x = -75, station B at x = +75. Bottom face flat within 0.05 (it slides on the base plate).',
            'Pattern K/P is the same at both stations and matches L-201 and L-204.'])

part(id='L-104', name='COLUMN', qty=2, group='frame', kind='turned', dxf=False,
     material='CK45 / C45 induction-hardened hard-chrome bar D20 h6', finish='Hard chrome (as bought); threads turned after cutting',
     segs=[('M12', 12.0), (20.0, Z_HEAD - BASE_T), ('M12', 45.0)],
     notes=['Shoulders square to the axis within 0.02; the head (L-105) seats on the top shoulder.',
            'Length between shoulders %.1f sets the head height: tolerance +-0.05, both columns matched within 0.02.' % (Z_HEAD - BASE_T)])

HEAD_SLOT = dict(x0=-18.0, x1=30.0, hy=19.0)
HEAD_W = 90.0
part(id='L-105', name='HEAD', qty=1, group='frame', material=S275 + ' 30', finish='Black powder coat, holes masked',
     T=HEAD_T, outline=rrect(0, 0, HEAD_W, 200, 6),
     feats=[F(0, -COL_Y, 'hole', d=12.5, thru=True, label='C1'), F(0, COL_Y, 'hole', d=12.5, thru=True, label='C2'),
            F((HEAD_SLOT['x0'] + HEAD_SLOT['x1']) / 2, 0, 'rr', w=HEAD_SLOT['x1'] - HEAD_SLOT['x0'], h=2 * HEAD_SLOT['hy'], r=5,
              thru=True, label='SL')] +
           [F(sx * 16, sy * CHEEK_SCREW_Y, 'hole', d=9, thru=True, cb=(14.0, 8.5), cbside='bot', label='K') for sx in (-1, 1) for sy in (-1, 1)] +
           [F(sx * 6, sy * CHEEK_SCREW_Y, 'hole', d=6, depth=8, side='top', label='P') for sx in (-1, 1) for sy in (-1, 1)] +
           [F(STOP_X, sy * 12, 'tap', m='M8', thru=True, label='ST') for sy in (-1, 1)],
     rows=[['C', '(0, +-80)', 'D12.5 THRU (column threads); the head sits on the column shoulders'],
           ['SL', 'x %g ... +%g, y +-%g' % (HEAD_SLOT['x0'], HEAD_SLOT['x1'], HEAD_SLOT['hy']),
            'Window THRU, corners R5 (lever crank, link, pin A and the clevis pass through)'],
           ['K', '(+-16, +-%g)' % CHEEK_SCREW_Y, 'D9 THRU, c\'bore D14 x 8.5 from the BOTTOM (M8 x 35 cap screws into the cheeks)'],
           ['P', '(+-6, +-%g)' % CHEEK_SCREW_Y, 'D6 H7 x 8 from the TOP (cheek dowels D6 m6 x 16)'],
           ['ST', '(%g, +-12)' % STOP_X, 'M8 THRU (handle stops under the two lever plates: hex bolt M8 x 45 from below, jam nut under the head)']],
     notes=['Top face flat within 0.05 under the cheeks. Holes C at 160.00 +-0.05 and on the same line as K/P.',
            'At the 15 kN abuse load: about 95 MPa in the section through the window (S275: 275 MPa yield).'])

part(id='L-106', name='RAM', qty=1, group='frame', material=S275 + ' 25', finish='Black oxide; bores masked',
     T=RAM_T, outline=rrect(0, 0, 60, 200, 5),
     feats=[F(0, -COL_Y, 'hole', d=28, thru=True, label='B1'), F(0, COL_Y, 'hole', d=28, thru=True, label='B2')] +
           [F(sx * 18, sy * 38, 'hole', d=9, thru=True, cb=(14.0, 8.5), label='K') for sx in (-1, 1) for sy in (-1, 1)] +
           [F(0, sy * 22, 'hole', d=6, depth=8, side='bot', label='P') for sy in (-1, 1)] +
           [F(sx * 8, 0, 'hole', d=9, thru=True, cb=(14.0, 8.5), cbside='bot', side='bot', label='L') for sx in (-1, 1)] +
           [F(0, sy * 12, 'hole', d=6, depth=8, side='top', label='PL') for sy in (-1, 1)],
     rows=[['B', '(0, +-80)', 'D28 H7 THRU (bronze bushes D20 x D28 x 25, pressed in, ream D20 H7 after pressing)'],
           ['K', '(+-18, +-38)', 'D9 THRU, c\'bore D14 x 8.5 from the TOP (M8 x 30 into the die body)'],
           ['P', '(0, +-22)', 'D6 H7 x 8 from the BOTTOM (die body dowels)'],
           ['L', '(+-8, 0)', 'D9 THRU, c\'bore D14 x 8.5 from the BOTTOM (M8 x 25 into the clevis)'],
           ['PL', '(0, +-12)', 'D6 H7 x 8 from the TOP (clevis dowels)']],
     notes=['Bores B: centres 160.00 +-0.03, square to the faces within 0.02 (they guide the ram on the columns).',
            'Top and bottom faces parallel within 0.03.'])

part(id='L-107', name='PIVOT CHEEK', qty=2, group='frame', material=S275 + ' 20, faced to 18 (or C45)', finish='Black oxide',
     T=CHEEK['T'], outline=cheek_outline(),
     feats=[P(0, CHEEK['pin'], 'hole', d=PIN_D, thru=True, label='O')],
     rows=[['O', '(0, %g)' % CHEEK['pin'], 'D16 N7 THRU: stub pin O (L-111) pressed in; both cheeks bored as a pair'],
           ['K', 'bottom edge, x +-16', 'M8 x 16 deep into the bottom edge, on its centre line'],
           ['P', 'bottom edge, x +-6', 'D6 H7 x 10 deep into the bottom edge, on its centre line (dowels)']],
     notes=['Profile cut (laser / plasma), then mill the bottom edge flat and square to the bore.',
            'Bore O and the bottom-edge holes with the two cheeks clamped as a mirrored pair.'],
     profile='XZ')

part(id='L-108', name='RAM CLEVIS', qty=1, group='frame', material='C45 / EN8 block 35 x 35 x 45', finish='Black oxide',
     T=CLEVIS['W'], outline=clevis_outline(), feats=[P(0, CLEVIS['pin'], 'hole', d=PIN_D, thru=True, label='B')],
     rows=[['B', '(0, %g)' % CLEVIS['pin'], 'D16 N7 THRU (pin B pressed in), across the slot'],
           ['SL', 'centre', 'Slot %g wide (Y), from Z %g to the top, through in X (the link runs in it)' % (CLEVIS['slot'], CLEVIS['base'])],
           ['K', 'bottom face, x +-8, y 0', 'M8 x 10 deep from the bottom (2 off)'],
           ['P', 'bottom face, x 0, y +-12', 'D6 H7 x 8 deep from the bottom (2 dowels)']],
     edge_extra=[L(-CLEVIS['slot'] / 2, CLEVIS['base'], -CLEVIS['slot'] / 2, CLEVIS['pin'] + CLEVIS['r']), L(CLEVIS['slot'] / 2, CLEVIS['base'], CLEVIS['slot'] / 2, CLEVIS['pin'] + CLEVIS['r']),
                 L(-CLEVIS['slot'] / 2, CLEVIS['base'], CLEVIS['slot'] / 2, CLEVIS['base'])],
     notes=['Shown: side profile (X-Z). Thickness 32 along Y = two 8 mm legs either side of the 16 mm slot.',
            'Bottom face flat and square to the pin bore within 0.03.'], profile='XZ')

part(id='L-109', name='LEVER PLATE', qty=2, group='frame', material=S275 + ' 8', finish='Black powder coat; grip end bare',
     T=LEVER_T, outline=lever_outline(),
     feats=[P(0, 0, 'hole', d=PIN_D, thru=True, label='O'), P(0, -R_CRANK, 'hole', d=PIN_D, thru=True, label='A')] +
           [P(u * math.cos(math.radians(HANDLE_OFF - 90)), u * math.sin(math.radians(HANDLE_OFF - 90)), 'hole', d=8.5, thru=True, label='S')
            for u in SPACER_U + GRIP_BOLT_U],
     rows=[['O', '(0, 0)', 'D16 H8 THRU (turns on the stub pin O)'],
           ['A', '(0, -18)', 'D16 N7 THRU (pin A pressed in), centres 18.00 +-0.03 from O'],
           ['S', 'bar axis: 70, 100, %g, %g' % GRIP_BOLT_U, 'D8.5 THRU (M8 bolts through the spacers), distances from O']],
     notes=['Two plates, a mirrored pair: profile cut together, ream O and A with the plates clamped as a pair.',
            'Handle bar 30 wide at %g deg to the crank line; grip centre %g from O.' % (HANDLE_OFF, GRIP_C)], profile='XZ')

part(id='L-110', name='TOGGLE LINK', qty=1, group='frame', material='S355 (IS 2062 E350) plate 16, faced to 15', finish='Black oxide',
     T=LINK_T, outline=link_outline(),
     feats=[P(0, 0, 'hole', d=PIN_D, thru=True, label='B'), P(L_LINK, 0, 'hole', d=PIN_D, thru=True, label='A')],
     rows=[['A, B', '(55, 0), (0, 0)', 'D16 H8 THRU, centres 55.00 +-0.03']],
     notes=['Ends R14. Runs between the two lever plates (pin A) and in the clevis slot (pin B).'], profile='XZ')

PIN_O_L = CHEEK_Y[1] - LEVER_Y[0] - 0.5              # 28: from Y +-8.5 (inside the lever plate) to the cheek's outer face
PIN_AB_L = 2 * LEVER_Y[1]                            # 32: pressed into the lever plates / clevis legs, flush with their outer faces
part(id='L-111', name='PIN O (STUB)', qty=2, group='frame', kind='pin', dxf=False, d=PIN_D, L=PIN_O_L, groove=None,
     material='EN8 / C45 bright bar (or EN19 for longer life)', finish='Ground D16 m6; chamfer 1 x 45 both ends',
     notes=['Pressed into the cheek (D16 N7) flush with its outer face; the lever plate turns on the inner 7.5 mm, a 2.5 mm '
            'gap between plate and cheek. Grease.'])
part(id='L-112', name='PIN A / PIN B', qty=2, group='frame', kind='pin', dxf=False, d=PIN_D, L=PIN_AB_L, groove=None,
     material='EN8 / C45 bright bar (or EN19)', finish='Ground D16 m6; chamfer 1 x 45 both ends',
     notes=['Pressed into the lever plates (pin A) or the clevis legs (pin B), flush both sides; the link turns on it (link bores H8). '
            'No rings: a ring on pin A would hit the stub pins O as the crank turns. Grease the link bores.'])
part(id='L-113', name='LEVER SPACER TUBE', qty=2, group='frame', kind='tube', dxf=False, od=22.0, bore=8.5, L=2 * LEVER_Y[0],
     material='EN8 / mild steel round bar D22', finish='Zinc or black oxide', notes=['Length 16.00 +0.05/0: sets the gap between the lever plates.'])
part(id='L-114', name='GRIP SPACER', qty=1, group='frame', material=S275 + ' 16', finish='Black powder coat',
     T=GRIP_SPACER['T'], outline=rrect(0, 0, GRIP_SPACER['L'], GRIP_SPACER['W'], 5),
     feats=[F(-35, 0, 'hole', d=8.5, thru=True, label='S'), F(35, 0, 'hole', d=8.5, thru=True, label='S')],
     rows=[['S', '(+-35, 0)', 'D8.5 THRU (M8 x 35 bolts through both lever plates)']],
     notes=['Fills the grip end of the lever (32 x 30 with the plates); fit the slip-on grip over it.'])

# ---------------- die set: station A ----------------
part(id='L-201', name='STATION A BASE BLOCK', qty=1, group='die', material=AL + ' 16, faced to %g' % BB_T, finish='Clear anodise',
     T=BB_T, outline=sq(ST, 3),
     feats=[F(x, y, 'hole', d=10.5, thru=True, label='SP') for (x, y) in ((45, 0), (-45, 0), (0, 45), (0, -45))] +
           [F(sx * 45, sy * 45, 'hole', d=6.1, thru=True, cb=(11.0, BB_T - (SH_RA - RA_TRAVEL)), cbside='bot', side='bot', label='SS')
            for sx in (-1, 1) for sy in (-1, 1)] +
           [F(sx * 20, sy * 20, 'hole', d=5.5, thru=True, cb=(9.5, 5.5), cbside='bot', side='bot', label='PS')
            for sx in (-1, 1) for sy in (-1, 1)] +
           [F(sx * 24, 0, 'hole', d=5, depth=6, side='top', label='PD') for sx in (-1, 1)] +
           [F(sx * 45, sy * 30, 'tap', m='M6', depth=10, side='bot', label='K') for sx in (-1, 1) for sy in (-1, 1)] +
           [F(-20, 45, 'hole', d=6, depth=8, side='bot', label='P'), F(20, -45, 'hole', d=6, depth=8, side='bot', label='P')],
     rows=[['SP', '(+-45, 0), (0, +-45)', 'D10.5 THRU (ring A springs ISO 10243 green D10 x 38; they seat on the table)'],
           ['SS', '(+-45, +-45)', 'D6.1 THRU (shoulder guide), c\'bore D11 x %g from the BOTTOM (ISO 7379 D6 x 16 / M5)' % (BB_T - (SH_RA - RA_TRAVEL))],
           ['PS', '(+-20, +-20)', 'D5.5 THRU, c\'bore D9.5 x 5.5 from the BOTTOM (M5 x 16 into the pedestal)'],
           ['PD', '(+-24, 0)', 'D5 H7 x 6 from the TOP (pedestal dowels D5 m6 x 12)'],
           ['K', '(+-45, +-30)', 'M6 x 10 from the BOTTOM (table screws)'],
           ['P', '(-20, +45), (20, -45)', 'D6 H7 x 8 from the BOTTOM (table dowels)']],
     notes=['Top face (ring A stop) parallel to the bottom within 0.02; thickness %g +-0.02 (sets the stroke-1 depth).' % BB_T])

part(id='L-202', name='PEDESTAL', qty=1, group='die', material=D2, finish=HARD + '; top face and edge polished Ra 0.2',
     T=PED_H, outline=sq(PED, PED_R),
     feats=[F(sx * 20, sy * 20, 'tap', m='M5', depth=10, side='bot', label='T') for sx in (-1, 1) for sy in (-1, 1)] +
           [F(sx * 24, 0, 'hole', d=5, depth=6, side='bot', label='D') for sx in (-1, 1)],
     rows=[['T', '(+-20, +-20)', 'M5 x 10 from the BOTTOM'], ['D', '(+-24, 0)', 'D5 H7 x 6 from the BOTTOM (dowels)'],
           ['-', 'top edge', 'R%g all round the top edge (the tin folds over it); corners R%g in plan' % (PED_EDGE, PED_R)]],
     notes=['MAT: %g = face 63.5 - 2 x stack %.3f (tin 0.23 + photo 0.12 + film 0.075).' % (PED, T_STACK),
            'Height %.3f +-0.01 (sets the face level with the cup ring top).' % PED_H,
            'Wire-EDM the outline after hardening (or grind); sides square to the top within 0.01.'])

part(id='L-203', name='RING A (BLANK HOLDER)', qty=1, group='die', material=D2, finish=HARD + '; opening edge polished',
     T=RA_T, outline=sq(ST, 3),
     feats=[F(0, 0, 'rr', w=RA_OPEN, h=RA_OPEN, r=RA_OPEN_R, thru=True, label='OP'),
            F(0, 0, 'rr', w=RA_PHOTO, h=RA_PHOTO, r=RA_PHOTO_R, depth=RA_STEP1, side='top', label='PH'),
            F(0, 0, 'rr', w=RA_TIN, h=RA_TIN, r=RA_TIN_R, depth=RA_STEP2, side='top', label='TN')] +
           [F(sx * 45, sy * 45, 'tap', m='M5', thru=True, label='SS') for sx in (-1, 1) for sy in (-1, 1)] +
           [F(x, y, 'hole', d=10.5, depth=RA_SPR['pocket_ring'], side='bot', label='SP') for (x, y) in ((45, 0), (-45, 0), (0, 45), (0, -45))],
     rows=[['OP', 'centre', '%g x %g THRU, corners R%g; top edge R%g (tin ledge)' % (RA_OPEN, RA_OPEN, RA_OPEN_R, RA_EDGE)],
           ['TN', 'centre', 'Tin pocket %g x %g x %g deep from the top, corners R%g' % (RA_TIN, RA_TIN, RA_STEP2, RA_TIN_R)],
           ['PH', 'centre', 'Photo / film pocket %g x %g x %g deep from the top, corners R%g' % (RA_PHOTO, RA_PHOTO, RA_STEP1, RA_PHOTO_R)],
           ['SS', '(+-45, +-45)', 'M5 THRU (shoulder screws from below)'],
           ['SP', '(+-45, 0), (0, +-45)', 'D10.5 x 4 from the BOTTOM (spring seats)']],
     notes=['MAT: pockets follow the tin and photo sizes (tin %g, photo %g); opening = tin - 1.5 (0.75 ledge a side).' % (TIN, PHOTO),
            'Wire-EDM the opening after hardening; mill the pockets before hardening and finish to depth after.'])

# ---------------- die set: station B ----------------
part(id='L-204', name='STATION B RISER', qty=1, group='die', material=AL + ' 25, faced to %.3f' % RIS_T, finish='Hard anodise (the magnet sits on the top face)',
     T=RIS_T, outline=sq(ST, 3),
     feats=[F(sx * 45, sy * 30, 'tap', m='M6', depth=12, side='bot', label='K') for sx in (-1, 1) for sy in (-1, 1)] +
           [F(-20, 45, 'hole', d=6, depth=8, side='bot', label='P'), F(20, -45, 'hole', d=6, depth=8, side='bot', label='P')] +
           [F(sx * 45, sy * 45, 'tap', m='M5', depth=10, side='top', label='T') for sx in (-1, 1) for sy in (-1, 1)] +
           [F(sx * 45, 0, 'hole', d=5, depth=6, side='top', label='D') for sx in (-1, 1)],
     rows=[['K', '(+-45, +-30)', 'M6 x 12 from the BOTTOM (table screws)'], ['P', '(-20, +45), (20, -45)', 'D6 H7 x 8 from the BOTTOM'],
           ['T', '(+-45, +-45)', 'M5 x 10 from the TOP (cup ring screws)'], ['D', '(+-45, 0)', 'D5 H7 x 6 from the TOP (cup ring dowels)']],
     notes=['MAT: thickness %.3f +-0.02 = face level 50.0 - cup ring %.3f - table top 22. Top face flat within 0.01.' % (RIS_T, CUP_T),
            'Aluminium so the magnet sheet does not stick to the floor.'])

part(id='L-205', name='CUP RING (TAPER + NOSE)', qty=1, group='die', material=D2, finish=HARD + '; taper and nose polished Ra 0.2',
     T=CUP_T + NOSE, outline=sq(ST, 3),
     feats=[F(0, 0, 'rr', w=CUP_TOP, h=CUP_TOP, r=CUP_R, thru=True, label='TP')] +
           [F(sx * 45, sy * 45, 'hole', d=5.5, thru=True, csk=10.4, label='S') for sx in (-1, 1) for sy in (-1, 1)] +
           [F(sx * 45, 0, 'hole', d=5, thru=True, label='D') for sx in (-1, 1)],
     rows=[['TP', 'centre', 'Opening THRU, 18 deg taper: %.2f square at the nose top, %g at the landing face, %.2f at the bottom; corners R%g'
            % (NOSE_IN, CUP_TOP, CUP_BOT, CUP_R)],
           ['N', 'round TP', 'Nose %g high above the landing face: flat top to %.2f square, chamfer down to %.2f square (see detail)' % (NOSE, NOSE_TOP, NOSE_BASE)],
           ['LF', 'outside N', 'Landing face (the upper ring lands here): %g below the nose top, %.3f above the bottom face' % (NOSE, CUP_T)],
           ['S', '(+-45, +-45)', 'D5.5 THRU, 90 deg csk D10.4 from the landing face (M5 x 12 csk)'], ['D', '(+-45, 0)', 'D5 H7 THRU (dowels D5 m6 x 10)']],
     notes=['MAT: landing face %.3f above the bottom = finished magnet (stack %.3f + acrylic %g + magnet %g); grind the bottom and the landing face.'
            % (CUP_T, T_STACK, T_ACR, T_MAG),
            'Mill the landing face 1.0 down round the nose and the nose chamfer before hardening; taper THRU by 4-axis wire-EDM after hardening. '
            'The nose fills the upper ring\'s mouth (0.05 clear) so the shell wall stays supported; the taper turns the flap in onto the card.'])

# ---------------- die set: upper die ----------------
part(id='L-206', name='UPPER DIE BODY', qty=1, group='die', material=AL + ' 40, faced to %g' % DB_T, finish='Clear anodise',
     T=DB_T, outline=sq(ST, 3),
     feats=[F(sx * 42, sy * 42, 'hole', d=21, depth=UP_SPR['pocket_body'], side='bot', label='SP') for sx in (-1, 1) for sy in (-1, 1)] +
           [F(x, y, 'hole', d=10.5, thru=True, cb=(17.0, DB_T - (SH_UR - UR_GAP)), label='SS') for (x, y) in ((45, 0), (-45, 0), (0, 45), (0, -45))] +
           [F(sx * 22, sy * 22, 'hole', d=6.6, thru=True, cb=(11.0, 6.5), label='PS') for sx in (-1, 1) for sy in (-1, 1)] +
           [F(sx * 22, 0, 'hole', d=6, depth=8, side='bot', label='PD') for sx in (-1, 1)] +
           [F(sx * 18, sy * 38, 'tap', m='M8', depth=16, side='top', label='K') for sx in (-1, 1) for sy in (-1, 1)] +
           [F(0, sy * 22, 'hole', d=6, depth=8, side='top', label='P') for sy in (-1, 1)],
     rows=[['SP', '(+-42, +-42)', 'D21 x %g from the BOTTOM (upper springs ISO 10243 red D20 x 76)' % UP_SPR['pocket_body']],
           ['SS', '(+-45, 0), (0, +-45)', 'D10.5 THRU, c\'bore D17 x %g from the TOP (ISO 7379 D10 x 40 / M8)' % (DB_T - (SH_UR - UR_GAP))],
           ['PS', '(+-22, +-22)', 'D6.6 THRU, c\'bore D11 x 6.5 from the TOP (M6 x 55 into the plug)'],
           ['PD', '(+-22, 0)', 'D6 H7 x 8 from the BOTTOM (plug dowels D6 m6 x 16)'],
           ['K', '(+-18, +-38)', 'M8 x 16 from the TOP (ram screws)'], ['P', '(0, +-22)', 'D6 H7 x 8 from the TOP (ram dowels)']],
     notes=['Faces parallel within 0.02. The shoulder screws guide the upper ring: holes SS square to the faces within 0.02.'])

part(id='L-207', name='UPPER RING', qty=1, group='die', material=D2, finish=HARD + '; bore and mouth polished Ra 0.2',
     T=UR_T, outline=sq(ST, 3),
     feats=[F(0, 0, 'rr', w=BORE, h=BORE, r=BORE_R, thru=True, label='BR')] +
           [F(sx * 42, sy * 42, 'hole', d=21, depth=UP_SPR['pocket_ring'], side='top', label='SP') for sx in (-1, 1) for sy in (-1, 1)] +
           [F(x, y, 'tap', m='M8', thru=True, label='SS') for (x, y) in ((45, 0), (-45, 0), (0, 45), (0, -45))],
     rows=[['BR', 'centre', 'Bore %g x %g THRU, corners R%g; bottom edge R%g (mouth)' % (BORE, BORE, BORE_R, MOUTH_R)],
           ['SP', '(+-42, +-42)', 'D21 x 8 from the TOP (spring seats)'], ['SS', '(+-45, 0), (0, +-45)', 'M8 THRU (shoulder screws)'],
           ['BP', 'side faces, 3.2 up', 'M4 THRU to the bore, 4 off: +X face y +12, -X face y -12, +Y face x -12, -Y face x +12'],
           ['', '', '(ball plungers M4 set 0.4 proud in the bore, locked by an M4 set screw behind)']],
     notes=['MAT: bore = face 63.5 + 2 x 0.175 (the shell wall stands inside it); mouth R2.5 lets the flat tin slide in without being drawn.',
            'Wire-EDM the bore after hardening; grind the mouth radius blend. Drill and tap BP before hardening.'])

part(id='L-208', name='PLUG', qty=1, group='die', material=D2, finish=HARD + '; face lapped Ra 0.1 (it presses the film side)',
     T=PLUG_H, outline=sq(PLUG, PLUG_R),
     feats=[F(sx * 22, sy * 22, 'tap', m='M6', depth=12, side='top', label='T') for sx in (-1, 1) for sy in (-1, 1)] +
           [F(sx * 22, 0, 'hole', d=6, depth=8, side='top', label='D') for sx in (-1, 1)],
     rows=[['T', '(+-22, +-22)', 'M6 x 12 from the TOP'], ['D', '(+-22, 0)', 'D6 H7 x 8 from the TOP (dowels)'],
           ['-', 'bottom edge', 'R%g all round' % PLUG_EDGE]],
     notes=['%g: 0.05 a side inside the magnet face, so it passes inside the cup ring\'s nose; 0.225 a side clear of the upper ring '
            'bore (the ring is guided by its shoulder screws). Outline +-0.02 after hardening.' % PLUG])

part(id='L-209', name='PLUG SHIM', qty='2 x 0.1, 1 x 0.2', group='die', material='Stainless shim stock 0.1 / 0.2 (AISI 301 / 304)',
     finish='Deburr; flat', T=0.2, outline=sq(PLUG, PLUG_R),
     feats=[F(sx * 22, sy * 22, 'hole', d=6.6, thru=True, label='S') for sx in (-1, 1) for sy in (-1, 1)] +
           [F(sx * 22, 0, 'hole', d=6.1, thru=True, label='D') for sx in (-1, 1)],
     rows=[['S', '(+-22, +-22)', 'D6.6 THRU'], ['D', '(+-22, 0)', 'D6.1 THRU']],
     notes=['Nominal pack 0.4 between plug and die body: add or remove to set the plug face level with the cup ring top (station B) '
            'at the bottom of the stroke.'])

# ------------------------------------------------------------------------------------------------------------------
# bought parts (for the BOM)
# ------------------------------------------------------------------------------------------------------------------
BOUGHT = [
    ('B-01', 'Bronze plain bush D20 x D28 x 25 (or sintered bronze, oil-impregnated)', 2, 'Ram on the columns'),
    ('B-02', 'Hex nut M12 + washer M12', '2 + 2', 'Columns over the head'),
    ('B-03', 'Shaft collar DIN 705 A 20 (D32 x 14) with set screw', 4, '2 return-spring seats at Z %g, 2 up-stops at Z %.1f' % (Z_SEAT - 14, Z_UPSTOP)),
    ('B-04', 'Compression spring ID 21, wire 3.6, L0 80, 8 active coils, about 14 N/mm', 2, 'Ram return, on the columns'),
    ('B-06', 'Cap screw ISO 4762 M8 x 35 / M8 x 25', '4 + 2', 'Head to cheeks; ram to clevis'),
    ('B-07', 'Cap screw ISO 4762 M8 x 30', 4, 'Ram to die body'),
    ('B-08', 'Hex bolt M8 x 45 + hex nut M8', 2, 'Handle stops in the head (one under each lever plate), jam nuts underneath'),
    ('B-08a', 'Hex bolt M8 x 35 + nyloc nut M8', 4, 'Lever plates through the spacer tubes and the grip spacer'),
    ('B-09', 'Dowel pin ISO 8734 D6 m6 x 16', 15, 'Head/cheeks 4, ram/clevis 2, ram/die body 2, die body/plug 2, table/stations 4, +1 spare'),
    ('B-10', 'Dowel pin ISO 8734 D5 m6 x 12 / x 10', '2 + 2', 'Pedestal; cup ring'),
    ('B-11', 'Dowel pin ISO 8734 D10 m6 x 16', 1, 'Table stop pin in the base'),
    ('B-12', 'Ball plunger M10 (spring, ball D6, end force 30-60 N)', 1, 'Table detent'),
    ('B-13', 'Knob DIN 319 D32 M8', 2, 'Table'),
    ('B-14', 'Cap screw ISO 4762 M4 x 10', 8, 'Rails'),
    ('B-15', 'Cap screw ISO 4762 M6 x 12', 8, 'Stations to table'),
    ('B-16', 'Cap screw ISO 4762 M5 x 16', 4, 'Pedestal'),
    ('B-17', 'Shoulder screw ISO 7379 D6 x 16, M5 (thread cut to 7.5)', 4, 'Ring A'),
    ('B-18', 'Die spring ISO 10243 green D10 x 38', 4, 'Ring A'),
    ('B-19', 'Countersunk screw ISO 10642 M5 x 12', 4, 'Cup ring'),
    ('B-20', 'Shoulder screw ISO 7379 D10 x 40, M8', 4, 'Upper ring'),
    ('B-21', 'Die spring ISO 10243 red D20 x 76', 4, 'Upper ring'),
    ('B-22', 'Cap screw ISO 4762 M6 x 55', 4, 'Plug through the die body and shims'),
    ('B-23', 'Ball plunger M4 x 12 + set screw M4 x 6', '4 + 4', 'Upper ring: hold the shell between strokes'),
    ('B-24', 'Handle grip: rubber sleeve over the 32 x 30 grip end (or cloth tape)', 1, 'Lever'),
    ('B-25', 'Rubber feet / bench bolts M8', 4, 'Base'),
]


def part_by(pid):
    return next(p for p in PARTS if p['id'] == pid)
