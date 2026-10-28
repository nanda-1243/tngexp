"""Die-set drawings (MP-2xx), general arrangement (MP-001) and cover (MP-000).
Rev C: one universal die per press (body, carriers, station bases, springs) + a hardened size kit per magnet size."""
import math
from draft import *
import parts as P
from parts import new, SIZES, SIZE_LABEL, SHOWN, GEN, DXFS

KIT_NOTES = ['Size kit part: one per magnet size, tabulated below. Shown to scale for size 6590 (65 × 90). X = long side, along the die table.',
             'Laser-mark on a side face: drawing no., size code and U / A / B where applicable (e.g. "MP-207 6590 A").']
UNI_NOTES = ['Universal die part: one per press, the same for every magnet size. X = along the die table, +Z = front.',
             'Laser-mark the drawing number on a side face.']

# ---- Rev C universal die geometry ----
CX, CZ = 144.0, 116.0                     # carriers and upper die body, outside
RX_, RZ_ = 106.0, 81.0                    # size rings, outside (ground -0.01/-0.02)
PKX, PKZ = 106.02, 81.02                  # carrier pocket for the rings (+0.01/0)
LDX, LDZ = 96.0, 72.0                     # ledge opening under the lower rings
RET = [(sx * 62.5, sz * 49.25) for sx in (-1, 1) for sz in (-1, 1)]          # carrier shoulder screws
SPR_LOW = [(62.5, 0), (-62.5, 0), (0, 49.25), (0, -49.25)]                     # lower springs, A and B
SPR_UP = [(sx * 30, sz * 49.25) for sx in (-1, 1) for sz in (-1, 1)] + [(sx * 62.5, sz * 25) for sx in (-1, 1) for sz in (-1, 1)]
# Rev E: key pins 1 mm into the pocket wall (240° of grip, not 180°); B keys at Z ±30 so ring A turned over can't enter carrier B
KEY = {'A': [(54.01, -20), (-54.01, 20)], 'B': [(54.01, 30), (-54.01, -30)], 'U': [(0, 41.51), (0, -41.51)]}
KEY_OFF = 1.0                              # key pin centre outside the ring edge
BASE = (150.0, 120.0)
BASE_FIX = [(sx * 35, sz * 35) for sx in (-1, 1) for sz in (-1, 1)]
BASE_DOWEL = [(45, 0), (-45, 0)]
PLUG_DOWEL = [(20, -10), (-20, -10)]
# Rev E: the plug pin runs along X from the body's LEFT end face (the front column blocked the Rev D pin along Z). Axis at
# Z = +7, 4 above the body bottom; the studs sit 6.8 either side of it, so the pin runs tangent to their grooves.
PIN_Z = 7.0
PIN_X0, PIN_X1 = -72.0, -7.0               # blind bore from the left end face to X -7 (clear of the M10 shank thread)
STUD = (-18, PIN_Z + 6.8)
# Rev D: round size kits and the inner plug pattern they hang on (the stud sits on the other side of the same detent pin)
ROUND = [('D44', 44.0), ('D50', 50.0), ('D56', 56.0), ('D58', 58.0)]
ROUND_LABEL = {cd: 'Ø' + fmt(d) for (cd, d) in ROUND}
SHOWN_R = ('D58', 58.0)
PLUG_DOWEL_R = [(12, -12), (-12, -12)]
STUD_R = (-13, PIN_Z - 6.8)
# Rev E magnet: sharp corners (R1 at the face, like commercial photo magnets), double flat fold on the back, photo 6.0 past the face
FACE_R = 1.0
BLEED = 6.0                                # Rev E: photo and film 6 a side over the face; they end with the tin inside the double fold
TIN_BLANK = 12.0                           # Rev E: flat tin blank X + 12 (6 a side), corners clipped on the photo's 45° line
RELIEF_D = 1.2                             # corner reliefs in the upper ring and ring B: room for the paper folded at the corner

KIT_MAT = 'A2 / 1.2363 tool steel; 7075-T6 for the prototype kit; PM cold-work steel for high volume'
KIT_FIN = 'Harden 58–60 HRC, temper ×2; wire-EDM + 2 skim cuts, then re-temper; forming edges Ra 0.2; thin dense chrome'
CAR_MAT = '42CrMo4 (1.7225) plate, QT 28–32 HRC'
CAR_FIN = 'Black oxide; pocket walls ground or wire-EDM, Ra 0.8'


def rr_notched(w, h, r, notches, rn=2.1, off=KEY_OFF):
    """rounded rectangle centred at 0 with circular notches (radius rn, centre `off` outside the edge) cut into the edges.
    notches: list of ('R'|'L'|'T'|'B', position along the edge) in plan coordinates (u, w)."""
    hw, hh = w / 2.0, h / 2.0
    e = math.sqrt(rn * rn - off * off)
    phi, psi = math.degrees(math.atan2(e, off)), math.degrees(math.atan2(off, e))
    segs = []
    def edge(side, a, b, fixed):
        cuts = sorted(p for (s, p) in notches if s == side)
        pos = a
        for c in cuts:
            if side in ('R', 'L'):
                segs.append(L(fixed, pos, fixed, c - e))
                segs.append(A(fixed + off, c, rn, 180 - phi, 180 + phi) if side == 'R' else A(fixed - off, c, rn, 360 - phi, 360 + phi))
            else:
                segs.append(L(pos, fixed, c - e, fixed))
                segs.append(A(c, fixed + off, rn, 180 + psi, 360 - psi) if side == 'T' else A(c, fixed - off, rn, psi, 180 - psi))
            pos = c + e
        if side in ('R', 'L'):
            segs.append(L(fixed, pos, fixed, b))
        else:
            segs.append(L(pos, fixed, b, fixed))
    edge('B', -hw + r, hw - r, -hh); segs.append(A(hw - r, -hh + r, r, 270, 360))
    edge('R', -hh + r, hh - r, hw); segs.append(A(hw - r, hh - r, r, 0, 90))
    edge('T', -hw + r, hw - r, hh); segs.append(A(-hw + r, hh - r, r, 90, 180))
    edge('L', -hh + r, hh - r, -hw); segs.append(A(-hw + r, -hh + r, r, 180, 270))
    return segs


def key_notches(which):
    """key slots of a ring (plan coordinates: u = x, w = -z)."""
    out = []
    for (x, z) in KEY[which]:
        if which == 'U':
            out.append(('T' if -z > 0 else 'B', x))
        else:
            out.append(('R' if x > 0 else 'L', -z))
    return out


# ---------------- part definitions ----------------
BODY_T, BODY_CB = 20, 10                   # Rev E: 20 thick (was 10), Ø54 × 10 counterbore on top for the holder and shims


def body(X=None, Z=None):
    f = [feat(0, 0, 'hole', d=54, depth=BODY_CB, side='top', label='H'),
         feat(49.5, 0, 'rr', w=45, h=10, r=0.5, depth=BODY_CB, side='top', label='W'),
         feat(0, 0, 'tap', m='M10', thru=True, label='S'), feat(0, 0, 'hole', d=12, depth=BODY_CB + 6, side='top', label='S')]
    f += [feat(x, z, 'hole', d=5, depth=6, side='bot', label='D') for (x, z) in PLUG_DOWEL]
    f.append(feat(STUD[0], STUD[1], 'hole', d=10.5, depth=8, side='bot', label='K'))
    f += [feat(x, z, 'hole', d=5, depth=6, side='bot', label='D2') for (x, z) in PLUG_DOWEL_R]
    f.append(feat(STUD_R[0], STUD_R[1], 'hole', d=10.5, depth=8, side='bot', label='K2'))
    f += [feat(x, z, 'tap', m='M5', thru=True, label='R') for (x, z) in RET]
    f += [feat(x, z, 'hole', d=13, depth=18, side='bot') for (x, z) in SPR_UP]          # Rev E: D12.5 x 44 red springs
    f.append(feat(0, 20, 'hole', d=4, depth=BODY_CB + 6, side='top', label='O'))
    return rrect(0, 0, CX, CZ, 6), BODY_T, f


def corner_reliefs(cx, cz):
    return [feat(sx * cx / 2, sz * cz / 2, 'hole', d=RELIEF_D, thru=True, label='Y') for sx in (-1, 1) for sz in (-1, 1)]


def upcarrier(X=None, Z=None):
    f = [feat(0, 0, 'rr', w=PKX, h=PKZ, r=6, thru=True)]
    f += [feat(x, z, 'hole', d=6.1, thru=True, cb=(10.5, 10), cbside='bot') for (x, z) in RET]
    f += [feat(x, z, 'hole', d=13, depth=12, side='top') for (x, z) in SPR_UP]
    f += [feat(x, z, 'hole', d=4, thru=True) for (x, z) in KEY['U']]
    return rrect(0, 0, CX, CZ, 3), 14, f


def lowcarrier(which):
    f = [feat(0, 0, 'rr', w=PKX, h=PKZ, r=6, depth=15, side='top'), feat(0, 0, 'rr', w=LDX, h=LDZ, r=6, thru=True)]
    f += [feat(x, z, 'hole', d=6.1, thru=True, cb=(10.5, 14), cbside='top') for (x, z) in RET]
    f += [feat(x, z, 'hole', d=10.5, depth=15, side='bot') for (x, z) in SPR_LOW]
    f += [feat(x, z, 'hole', d=4, depth=15, side='top') for (x, z) in KEY[which]]
    return rrect(0, 0, CX, CZ, 3), 18, f


def stbase():
    f = [feat(0, 0, 'hole', d=12, depth=8, side='top', label='C'), feat(0, 20, 'hole', d=4, depth=6, side='top', label='Q')]
    f += [feat(x, z, 'hole', d=10.5, depth=7, side='top') for (x, z) in SPR_LOW]
    f += [feat(x, z, 'tap', m='M5', thru=True) for (x, z) in RET]
    f += [feat(x, z, 'tap', m='M5', thru=True) for (x, z) in BASE_FIX]          # Rev E: tapped through (M5 x 20 from below)
    f += [feat(x, z, 'hole', d=6, depth=6, side='bot') for (x, z) in BASE_DOWEL]
    return rrect(0, 0, BASE[0], BASE[1], 3), 10, f


def plug(X, Z):
    f = [feat(STUD[0], STUD[1], 'tap', m='M6', depth=10, side='top')]
    f += [feat(x, z, 'hole', d=5, depth=8, side='top') for (x, z) in PLUG_DOWEL]
    return rrect(0, 0, X + 0.3, Z + 0.3, FACE_R + 0.15), 14.5, f


RA_OPEN = 10.5                             # ring A opening X + 10.5 (Rev E verification fix)
UR_MOUTH = 1.5                             # upper ring mouth radius (was a 0.3 x 30 deg lead-in)
UR_N = 2.5                                 # M3 ball plungers, height above the upper ring's bottom face (was 1.8)


def ring(X, Z, which):
    """size rings: U (upper, 14 high), A (pickup, 15), B (crimp guide, 15)."""
    if which == 'U':
        f = [feat(0, 0, 'rr', w=X + 0.35, h=Z + 0.35, r=FACE_R + 0.2, thru=True)] + corner_reliefs(X + 0.35, Z + 0.35)
        T = 14
    elif which == 'A':
        # verification: an opening X + 0.6 trapped the flange on the recess floor and stroke 1 DREW it (15 N/mm); X + RA_OPEN
        # leaves a 0.5 ledge after an R0.5 edge: the flange slides off it and is wiped down (6-7 N/mm peak, 1-2 at the end)
        f = [feat(0, 0, 'rr', w=X + RA_OPEN, h=Z + RA_OPEN, r=0.5, thru=True),
             feat(0, 0, 'rr', w=X + 2 * BLEED + 0.5, h=Z + 2 * BLEED + 0.5, r=1.5, depth=0.6, side='top', label='G')]   # tin, photo and film
        T = 15
    else:
        f = [feat(0, 0, 'rr', w=X + 0.45, h=Z + 0.45, r=FACE_R + 0.2, thru=True)] + corner_reliefs(X + 0.45, Z + 0.45)
        T = 15
    return rr_notched(RX_, RZ_, 6, key_notches(which)), T, f


PED_H = 23.0                               # Rev E square kits: 1.2 higher, so stroke 1 draws the whole 6 mm flange into the upper ring


def pick_ped(X, Z):
    f = [feat(0, 0, 'tap', m='M5', depth=6, side='top'), feat(0, 0, 'hole', d=12, depth=8.5, side='bot'), feat(0, 20, 'hole', d=4, depth=6, side='bot')]
    return rrect(0, 0, X - 1.0, Z - 1.0, 0.5), PED_H, f


# Rev E double-fold anvil: block X + 0.43 slides in ring B (X + 0.45). Platform 17.0 (X - 6.6) under the back plate; floor 16.15
# round it (0.85 below: room for two layers of tin, photo and film); cove R0.7 rising to the block edge at 16.85, flush with ring
# B's bore. The skirt runs down the bore, the cove turns it inward along the floor, the platform wall turns it up and back outward
# under the back plate: a flat two-layer hem, the photo outside (a 2.8 mm border on the back), the cut edge of the tin inside.
ANV = dict(block=0.43, r=FACE_R + 0.2, top=16.85, platform=17.0, floor=16.15, cove=0.7, plat_in=6.6)


def anvil(X, Z):
    f = [feat(0, 0, 'tap', m='M5', depth=6, side='top'), feat(0, 0, 'hole', d=12, depth=8.5, side='bot'), feat(0, 20, 'hole', d=4, depth=6, side='bot')]
    return rrect(0, 0, X + ANV['block'], Z + ANV['block'], ANV['r']), ANV['top'], f


# ---------------- common plan + sections ----------------
def plan_and_sections(sh, outline, T, fs, callouts, sec_b=None, oy=82, sec_oy=(175, 209), extent=None, title_y=18):
    v = View(sh, 100, oy, 1.0)
    v.segs(outline)
    draw_plan_features(v, fs)
    xs = [p for g in outline if g[0] == 'L' for p in (g[1], g[3])] + [g[1] + k * g[3] for g in outline if g[0] == 'C' for k in (-1, 1)]
    ys = [p for g in outline if g[0] == 'L' for p in (g[2], g[4])] + [g[2] + k * g[3] for g in outline if g[0] == 'C' for k in (-1, 1)]
    hx = extent or max(xs)
    hz = max(ys)
    v.cl_h(-hx - 5, hx + 5, 0); v.cl_v(hz + 5, -hz - 5, 0)
    sh.text(15, title_y, 'PLAN (TOP) — front at bottom', 3.2, weight='bold')
    for c in callouts:
        kind = c[0]
        if kind == 'h':
            _, u1, u2, w, wd, t = c; v.hdim(u1, w, u2, w, wd, text=t)
        elif kind == 'v':
            _, w1, w2, u, ud, t = c; v.vdim(w1, u, w2, u, ud, text=t)
        elif kind == 'l':
            _, u, w, dx_, dy_, t, r = c; v.leader(u, w, dx_, dy_, t, on_circle_r=r)
    v.section_mark(-hx - 7, 0, hx + 7, 0, 'A', flip=True)
    vs = View(sh, 100, sec_oy[0], 1.0)
    draw_section(vs, solid_minus_thru((-hx, hx), fs, 0), T, fs, 0, y0=0)
    vs.vdim(0, hx, T, hx, hx + 9, text=fmt(T))
    vs.text(0, 0, 'SECTION A–A', 3.2, dy=8.5, weight='bold')
    vb = None
    if sec_b is not None:
        zc, label = sec_b
        v.section_mark(-hx - 7, -zc, hx + 7, -zc, 'B', flip=False)
        vb = View(sh, 100, sec_oy[1], 1.0)
        draw_section(vb, solid_minus_thru((-hx, hx), fs, zc), T, fs, zc, y0=0)
        vb.text(0, 0, 'SECTION B–B (' + label + ')', 3.2, dy=8.5, weight='bold')
    return v, vs, vb


def outer_dims(w, h, off=9, voff=16, top=True):
    return [('h', -w / 2, w / 2, h / 2 if top else -h / 2, (h / 2 + off) if top else -(h / 2 + off), fmt(w)),
            ('v', h / 2, -h / 2, w / 2, w / 2 + voff, fmt(h))]


def feature_table(sh, x, y, rows, title='FEATURES (positions from the part centre, +Z = front)'):
    sh.text(x, y - 2, title, 3.0, weight='bold')
    cols = [('KEY', 12, 'middle'), ('POSITIONS (X, Z)', 56, 'start'), ('FEATURE', 120, 'start')]
    return sh.table(x, y, cols, rows, size=2.5, rh=4.6)


def size_table(sh, x, y, letters):
    cw = 17.0
    cols = [('SIZE', 24, 'middle'), ('X', 13, 'end'), ('Z', 13, 'end')] + [(l[0], cw, 'end') for l in letters]
    rows = [[cd, fmt(X), fmt(Z)] + [fmt(l[2](X, Z)) for l in letters] for (cd, X, Z) in SIZES]
    sh.text(x, y - 2, 'DIMENSION TABLE (mm)', 3.0, weight='bold')
    yend = sh.table(x, y, cols, rows, size=2.7, rh=5.2, bold_first_col=True)
    yy = yend + 5
    sh.text(x, yy, 'Size code = magnet face: 5050 = 50 × 50, 6363 = 63.5 × 63.5, 5380 = 53 × 80, 6590 = 65 × 90.', 2.4)
    yy += 4.5
    for l in letters:
        sh.text(x, yy, '%s = %s' % (l[0], l[1]), 2.6)
        yy += 4.0
    return yy


def uni_sheet(no, title, outline, T, fs, callouts, rows, notes, qty, material=CAR_MAT, finish=CAR_FIN, sec_b=None, dxfname=None,
              extra=None, scale='1:1'):
    sh = new(no, title, scale=scale, qty=qty, material=material, finish=finish, notes=UNI_NOTES + notes + GEN)
    v, vs, vb = plan_and_sections(sh, outline, T, fs, callouts, sec_b, oy=88, sec_oy=(184, 214), title_y=15)
    if extra:
        extra(sh, v, vs, vb)
    feature_table(sh, 212, 26, rows)
    if dxfname:
        dx = DXF(); dx.segs(outline); feats_dxf(dx, fs); DXFS['%s_%s.dxf' % (no, dxfname)] = dx
    return sh


def kit_sheet(no, title, fn, letters, notes, callouts, feat_rows, extra=None, sec_b=None, dxfname=None, qty='1 per size kit (4)',
              material=KIT_MAT, finish=KIT_FIN):
    sh = new(no, title, scale='1:1 (size 6590)', qty=qty, material=material, finish=finish, notes=KIT_NOTES + notes + GEN)
    code, X, Z = SHOWN
    outline, T, fs = fn(X, Z)
    v, vs, vb = plan_and_sections(sh, outline, T, fs, callouts, sec_b)
    if extra:
        extra(sh, v, vs, vb)
    yy = size_table(sh, 212, 24, letters)
    if feat_rows:
        feature_table(sh, 212, yy + 6, feat_rows)
    if dxfname:
        for (cd, x, z) in SIZES:
            o, T_, f_ = fn(x, z)
            dx = DXF(); dx.segs(o); feats_dxf(dx, f_)
            DXFS['%s_%s_%s.dxf' % (no, dxfname, cd)] = dx
    return sh


RET_T = '(±62.5, ±49.25)'
SPL_T = '(±62.5, 0), (0, ±49.25)'
SPU_T = '(±30, ±49.25), (±62.5, ±25)'


# ---------------- universal die ----------------
def mp201():
    outline, T, fs = body()
    def extra(sh, v, vs, vb):
        for dz_ in (-3, 3):
            v.line(PIN_X0, -(PIN_Z + dz_), PIN_X1, -(PIN_Z + dz_), 'hid')
        v.cl_h(PIN_X0 - 3, PIN_X1 + 2, -PIN_Z)
        v.leader(PIN_X1 - 4, -PIN_Z, 108, 58, 'L: Ø6 H8 from the LEFT end face to X −7, at Z +7,\n4 above the bottom face (detent pin, inserted from the left)')
    uni_sheet('MP-201', 'UPPER DIE BODY (UNIVERSAL)', outline, T, fs,
              outer_dims(CX, CZ, off=6) + [('h', -62.5, 62.5, -49.25, -CZ / 2 - 9, '125'), ('v', 49.25, -49.25, 62.5, CX / 2 + 26, '98.5'),
                                    ('l', 0, 0, 92, 10, 'S: Ø12 H7 × 6 + M10 THRU (shank)', 6)],
              [['H', 'centre', 'Ø54 × 10 from the TOP (room for the shim pack and the die holder MP-111)'],
               ['W', 'X +27 → +72', 'Slot 10 wide × 10 deep from the TOP, H to the +X end (key for the lock screw)'],
               ['S', 'centre', 'Ø12 H7 × 6 below the floor of H (shank spigot), then M10 THRU (shank MP-202)'],
               ['D', '(±20, −10)', 'Ø5 F7 × 6 from the BOTTOM (square-kit plug dowels; drop-in fit)'],
               ['K', '(−18, +13.8)', 'Ø10.5 × 8 from the BOTTOM (plug stud MP-212, square kits)'],
               ['D2', '(±12, −12)', 'Ø5 F7 × 6 from the BOTTOM (round-kit plug dowels; drop-in fit)'],
               ['K2', '(−13, +0.2)', 'Ø10.5 × 8 from the BOTTOM (round-kit plug stud)'],
               ['L', 'Z +7, X −72 → −7', 'Ø6 H8 along X from the LEFT end, 4 up; detent groove 0.4 deep, 4 from the end'],
               ['R', RET_T, 'M5 THRU (carrier shoulder screws ISO 7379 Ø6 × 10)'],
               ['P', SPU_T, 'Ø13 × 18 from the BOTTOM (8 upper springs ISO 10243 Ø12.5 × 44 red)'],
               ['O', '(0, +20)', 'Ø4 H7 × 6 below the floor of H (orientation pin Ø4 m6 × 12, 6 proud)']],
              ['The plug hangs on dowels D and the stud K, held by a Ø6 quick-release detent pin in hole L: no screws to change a size. Round kits use the inner pattern D2 + K2.',
               'Rev E: pin L runs along X from the left end face (Rev D ran it from the front face, where the front column blocked it). K and K2 sit 6.8 either side of its axis, so one pin holds either stud. D, D2 are F7: the plug dowels drop in by hand.',
               'Floor of H (seat against the holder through the shim pack) and bottom face parallel 0.01, flat 0.01. The shim pack sets the crimp depth once for all kits.',
               'Rev E: 20 thick (was 10) for longer, stronger upper springs: 8 × ISO 10243 Ø12.5 × 44 red in 36 mm cavities, 8 mm preload (≈ 1.57 kN total), ≈ 2.54 kN at full retraction (29%). They hold the upper ring while stroke 1 folds the flat tin blank (up to ≈ 1.7 kN). Replace every 100,000 strokes. Top face 2 mm below the ram.'],
              '1 per press', material='1.2312 (P20+S) prehardened 28–32 HRC', finish='Black oxide', sec_b=(49.25, 'Z = ±49.25'),
              dxfname='upper_body', extra=extra)


def mp202():
    sh = new('MP-202', 'UPPER DIE SHANK', scale='4:1', qty='1 per press',
             material='42CrMo4 Ø20 bar, QT 28–32 HRC', finish='Black oxide',
             notes=['Rev E: the Ø12 g6 spigot locates the die body (Ø12 H7); the M10 thread only clamps. Screw in with Loctite 243 until the Ø16 face seats; face square to axis 0.01.',
                    'V-groove takes the cone-point lock screw in the die holder MP-111 (groove centre 6.5 from the seating face).',
                    'Top end chamfer 1 × 45° (lead-in).'] + GEN)
    v, pos, Ltot = P.turned(sh, 130, 110, 0.25, [{'l': 4, 'd': 10, 'thread': 'M10'}, {'l': 6, 'd': 12}, {'l': 15, 'd': 16}])
    gx = 10 + 6.5
    for s in (1, -1):
        v.line(gx - 1.5, s * 8, gx, s * 6.5); v.line(gx, s * 6.5, gx + 1.5, s * 8)
    v.hdim(0, -5, 4, -5, -14, text='4')
    v.hdim(4, -6, 10, -6, -20, text='6')
    v.hdim(10, -8, 25, -8, -14, text='15')
    v.hdim(10, 8, gx, 6.5, 14, text='6.5')
    v.vdim(-8, 26, 8, 26, 26, text='Ø16 g6')
    v.leader(7, 6, -4, 16, 'Ø12 g6 spigot')
    v.leader(4, 5, -6, -14, 'M10 – 6g')
    v.leader(gx, -6.5, 10, 16, '90° V-groove, 1.5 deep')
    v.text(12, 0, 'SIDE VIEW', 3.4, dy=56, weight='bold')


def mp205():
    outline, T, fs = stbase()
    uni_sheet('MP-205', 'STATION BASE (UNIVERSAL)', outline, T, fs,
              outer_dims(BASE[0], BASE[1], off=6) + [('h', -35, 35, -35, -BASE[1] / 2 - 9, '70'), ('v', 35, -35, 35, BASE[0] / 2 + 26, '70')],
              [['C', 'centre', 'Ø12 F7 × 8 from the TOP (pedestal / anvil spigot; drop-in fit)'],
               ['Q', '(0, +20)', 'Ø4 F7 × 6 from the TOP (anti-rotation pin; drop-in fit)'],
               ['P', SPL_T, 'Ø10.5 × 7 from the TOP (4 lower springs)'],
               ['R', RET_T, 'M5 THRU (carrier shoulder screws ISO 7379 Ø6 × 12)'],
               ['F', '(±35, ±35)', 'M5 THRU (fixing to the die table, M5 × 20 ISO 10642 from below)'],
               ['G', '(±45, 0)', 'Ø6 H7 × 6 from the BOTTOM (dowels Ø6 m6 × 12 into the table)']],
              ['Both stations use this part; it stays fixed to the die table and is never removed for a size change.',
               'Rev E: align each base to its carrier pocket with a setting plug through the ring pocket, clamp, then drill and ream the dowels G in place through the table. Faces parallel 0.01, flat 0.01.'],
              '2 per press', material='C45 plate 12 mm, faced to 10', finish='Black oxide', dxfname='station_base')


def mp210():
    outline, T, fs = upcarrier()
    def extra(sh, v, vs, vb):
        for s in (-1, 1):
            for d_ in (-2.5, 2.5):
                v.line(s * CX / 2, d_, s * PKX / 2, d_, 'hid')
            v.cl_h(s * (CX / 2 + 3), s * (PKX / 2 - 3), 0)
        v.leader(CX / 2 - 6, 0, 14, 34, 'T: M5 THRU along X, 7 above the bottom face,\nboth ends (thumb screws, dog point, hold the ring)')
    uni_sheet('MP-210', 'UPPER CARRIER (UNIVERSAL)', outline, T, fs,
              outer_dims(CX, CZ, off=6) + [('h', -PKX / 2, PKX / 2, 0, -CZ / 2 - 9, fmt(PKX) + ' +0.01/0'),
                                    ('v', PKZ / 2, -PKZ / 2, PKX / 2, CX / 2 + 26, fmt(PKZ) + ' +0.01/0')],
              [['W', 'centre', 'Pocket 106.02 × 81.02 (+0.01/0), R6, THRU: holds the upper ring MP-204'],
               ['R', RET_T, 'Ø6.1 THRU, CBORE Ø10.5 × 10 from the BOTTOM'],
               ['P', SPU_T, 'Ø13 × 12 from the TOP (8 upper springs, Rev E: Ø12.5 × 44 red)'],
               ['K', '(0, ±41.51)', 'Ø4 H7 THRU, centre 1.0 into the pocket wall; press in Ø4 m6 × 14 flush (key pins, upper ring only)'],
               ['T', 'X ±72 → ±53, Z 0', 'M5 THRU along X, 7 above the bottom face (2 dog-point thumb screws, Ø3.5 × 3 dog)']],
              ['Rev C: spring-loaded sleeve that carries the upper size ring. Guided by the plug through the ring; floats on 4 shoulder screws.',
               'Faces parallel 0.01. Pocket walls square to the faces within 0.01.'],
              '1 per press', sec_b=(49.25, 'Z = ±49.25'), dxfname='upper_carrier', extra=extra)


def mp211():
    outline, T, fs = lowcarrier('A')
    _, _, fsb = lowcarrier('B')
    def extra(sh, v, vs, vb):
        for (x, z) in KEY['B']:
            v.circle(x, -z, 2, 'thin'); v.label(x, -z, 'KB', dx=1.6, dy=4)
        for (x, z) in KEY['A']:
            v.label(x, -z, 'KA', dx=1.6, dy=4)
    uni_sheet('MP-211', 'LOWER CARRIER A / B (UNIVERSAL)', outline, T, fs,
              outer_dims(CX, CZ, off=6) + [('h', -PKX / 2, PKX / 2, 0, -CZ / 2 - 9, fmt(PKX) + ' +0.01/0'),
                                    ('v', PKZ / 2, -PKZ / 2, PKX / 2, CX / 2 + 26, fmt(PKZ) + ' +0.01/0'),
                                    ('h', -LDX / 2, LDX / 2, -30, -CZ / 2 - 17, '96 (ledge)')],
              [['W', 'centre', 'Pocket 106.02 × 81.02 (+0.01/0), R6, 15 deep from the TOP (ring seat on a 3 mm ledge)'],
               ['V', 'centre', 'Ledge opening 96 × 72, R6, THRU'],
               ['R', RET_T, 'Ø6.1 THRU, CBORE Ø10.5 × 14 from the TOP (ISO 7379 Ø6 × 12 into the base)'],
               ['P', SPL_T, 'Ø10.5 × 15 from the BOTTOM (4 lower springs)'],
               ['KA', '(+54.01, −20), (−54.01, +20)', 'Variant A only: Ø4 H7 × 15, centre 1.0 into the pocket wall, Ø4 m6 × 14 pressed flush (key pins)'],
               ['KB', '(+54.01, +30), (−54.01, −30)', 'Variant B only: as KA at these positions']],
              ['Rev C: one carrier per station. Variant A (pickup, left station, green band) and variant B (crimp, right station, red band) differ only in the key pins.',
               'The keys stop a pickup ring going into the crimp station and the other way round. Faces parallel 0.01; ledge face flat 0.01.',
               'Lower springs: 4 × ISO 10243 Ø10 × 32 green per carrier in 30 mm cavities: 2 mm preload (≈ 75 N), ≈ 0.38 kN at the 8 mm stop (31%).'],
              'A + B per press', sec_b=(49.25, 'Z = ±49.25'), dxfname='lower_carrier_A', extra=extra)
    dx = DXF(); dx.segs(outline); feats_dxf(dx, fsb); DXFS['MP-211_lower_carrier_B.dxf'] = dx


# ---------------- size kit ----------------
def mp203():
    X, Z = SHOWN[1], SHOWN[2]
    def extra(sh, v, vs, vb):
        vd = View(sh, 345, 195, 0.2)
        pts = [(-6, 0), (-6, 6), (0, 6), (0, 1.0), (-0.3, 0.5), (-1.0, 0.25), (-1.5, 0.5), (-1.8, 0)]
        vd.poly(pts, 'sec')
        vd.text(-3, 0, 'DETAIL Y (5:1) working edge', 3.0, dy=12, weight='bold')
        vd.leader(-1.0, 0.25, -30, -8, 'concave lip R1, 1.5 wide × 0.5 deep\nall round the bottom face')
    kit_sheet('MP-203', 'PLUG (SIZE KIT)', plug,
              [('A', 'X + 0.30  (plug length, ±0.01)', lambda x, z: x + 0.30), ('B', 'Z + 0.30  (plug width, ±0.01)', lambda x, z: z + 0.30)],
              ['No screws. Two Ø5 × 14 dowels pressed in (5.5 protruding), one cylindrical and one diamond, locate it in the body; stud MP-212 in the M6 hole takes the detent pin.',
               'Profile A × B, R1.15 (Rev E: sharp-cornered magnets): wire-EDM after hardening, ±0.01. Sliding fit in the upper ring (ring = plug + 0.05).',
               'Bottom (working) face flat 0.01, Ra 0.2, lip per Detail Y. Height 14.5 ±0.01 sets the 5.5 recess in the ring.'],
              [('h', -(X + 0.3) / 2, (X + 0.3) / 2, (Z + 0.3) / 2, (Z + 0.3) / 2 + 9, 'A'),
               ('v', (Z + 0.3) / 2, -(Z + 0.3) / 2, (X + 0.3) / 2, (X + 0.3) / 2 + 18, 'B'),
               ('l', (X + 0.3) / 2 - 0.4, (Z + 0.3) / 2 - 0.4, 26, -14, 'R1.15 (4×)', 0)],
              [['S', '(−18, +13.8)', 'M6 × 10 from the TOP (stud MP-212, Loctite 243)'],
               ['D', '(±20, −10)', 'Ø5 H7 × 8 from the TOP (dowels Ø5 m6 × 14: +X cylindrical, −X diamond)']],
              extra=extra, dxfname='plug')


def mp204():
    X, Z = SHOWN[1], SHOWN[2]
    def extra(sh, v, vs, vb):
        for sx in (-1, 1):
            for sz in (-1, 1):
                u = sx * X / 4
                w0, w1 = sz * (Z + 0.35) / 2, sz * RZ_ / 2
                v.line(u - 2, w0, u - 2, w1, 'hid'); v.line(u + 2, w0, u + 2, w1, 'hid')
                v.cl_v(w0, w1, u)
            v.poly([(sx * RX_ / 2, -3), (sx * (RX_ / 2 - 3), 0), (sx * RX_ / 2, 3)], 'hid')
        v.leader(X / 4, -RZ_ / 2, 30, 28, 'N: 4× M3 radial (ball plungers)\n%g above the BOTTOM face, at X = ±E/2' % UR_N)
        v.leader(RX_ / 2, 0, 30, 45, 'M: Ø3.6 × 3.5 hole, both X ends, 7 above\nthe bottom face (dog-point thumb screws)')
        v.leader((X + 0.35) / 2, (Z + 0.35) / 2, 22, 16, 'Y: corner relief Ø1.2 THRU on each corner of\nthe opening (paper folded at the corner)', 0.6)
        vd = View(sh, 345, 190, 0.2)
        m, n = UR_MOUTH, UR_N
        pts = [(-8, 0), (-8, 8), (0, 8)] + [(-m + m * math.cos(math.radians(a)), m - m * math.sin(math.radians(a))) for a in range(0, 91, 10)]
        vd.poly(pts, 'sec')
        vd.rect(-8, n - 1.5, 0, n + 1.5, 'ko'); vd.line(-8, n - 1.5, 0, n - 1.5); vd.line(-8, n + 1.5, 0, n + 1.5); vd.cl_h(-9, 1, n)
        vd.text(-4, 0, 'DETAIL P (5:1) bottom inner edge', 3.0, dy=18, weight='bold')
        vd.text(1.5, 4, 'opening', 2.6, 'start')
        vd.leader(-m * 0.29, m * 0.29, -30, 10, 'mouth R%g all round, polished Ra 0.2' % m)
        vd.leader(-4, n + 1.5, -16, -10, 'M3 plunger hole, centre %g' % n)
    kit_sheet('MP-204', 'UPPER RING (SIZE KIT)', lambda x, z: ring(x, z, 'U'),
              [('C', 'X + 0.35  (opening, +0.01/0)', lambda x, z: x + 0.35), ('D', 'Z + 0.35  (opening, +0.01/0)', lambda x, z: z + 0.35),
               ('E', 'X / 2  (pitch of the plungers in X)', lambda x, z: x / 2)],
              ['Outside 106 × 81 (−0.01/−0.02) for every size: fits the upper carrier MP-210 pocket. Key slots K (R2.1, centre 1.0 outside the face) take the carrier pins.',
               'Opening C × D, R1.2, with corner reliefs Y, THRU: wire-EDM after hardening, lap Ra 0.2. Bottom inner edge R1.5 (Detail P): the die edge the flat tin blank folds over in stroke 1 (verification: the 0.3 × 30° lead-in drew the flange at 15 N/mm; R1.5 with ring A\'s narrow ledge wipes it at 6–7 N/mm, below the 1.57 kN spring preload for every kit). Polish it.',
               'Held by 2 dog-point thumb screws in holes M (Rev E: dog points take the load in shear; cone points brinelled their dimples). Four M3 ball plungers N at 2.5, set 0.4–0.5 proud of the opening (screw in, check with a feeler gauge, lock): the folded wall springs back to 0.2–0.3 inside the bore, so the balls, not friction, hold the shell while the table slides.'],
              outer_dims(RX_, RZ_) + [('h', -(X + .35) / 2, (X + .35) / 2, 0, -RZ_ / 2 - 17, 'C'),
                                      ('v', (Z + .35) / 2, -(Z + .35) / 2, 0, -RX_ / 2 - 24, 'D')],
              [['K', '(0, ±41.5)', 'Key slot R2.1, centre 1.0 outside the face, full height, on both long faces'],
               ['M', '(±53, 0)', 'Ø3.6 × 3.5 deep, 7 above the bottom face (dog-point thumb screws)'],
               ['N', '(±E/2, long faces)', 'M3 radial THRU, 2.5 above the bottom face (ball plungers, 0.4–0.5 proud)'],
               ['Y', 'opening corners', 'Ø1.2 THRU on each corner of the opening (corner relief)']],
              extra=extra, sec_b=(20, 'Z = ±20'), dxfname='upper_ring')


def mp206():
    X, Z = SHOWN[1], SHOWN[2]
    kit_sheet('MP-206', 'PICKUP PEDESTAL (SIZE KIT)', pick_ped,
              [('A', 'X − 1.0  (±0.01)', lambda x, z: x - 1.0), ('B', 'Z − 1.0  (±0.01)', lambda x, z: z - 1.0)],
              ['Rev E: the flat tin blank, photo and film lie in ring A\'s recess, 2.4 above it. In stroke 1 ring A drops and the pedestal folds the blank\'s edges down into the upper ring (0.68 a side for 0.4 of tin, photo and film). Top face flat 0.01, Ra 0.2; top edge R0.8, the inside radius of the fold. Height 23.0 ±0.02 (Rev E, was 21.8): the whole 6 mm flange is drawn into the upper ring.',
               'Rev C: drop-in. Press a Ø12 m6 × 15 dowel into C (7 protruding) and a Ø4 m6 × 10 pin into Q (4 protruding). Lift out with the M5 T-handle puller in hole H.'],
              [('h', -(X - 1) / 2, (X - 1) / 2, (Z - 1) / 2, (Z - 1) / 2 + 9, 'A'),
               ('v', (Z - 1) / 2, -(Z - 1) / 2, (X - 1) / 2, (X - 1) / 2 + 18, 'B'),
               ('l', (X - 1) / 2 - 0.2, (Z - 1) / 2 - 0.2, 24, -12, 'R0.5 (4×)', 0)],
              [['H', 'centre', 'M5 × 6 from the TOP (puller)'], ['C', 'centre', 'Ø12 H7 × 8.5 from the BOTTOM (spigot dowel)'],
               ['Q', '(0, +20)', 'Ø4 H7 × 6 from the BOTTOM (anti-rotation pin)']],
              dxfname='pickup_pedestal')


def mp207():
    X, Z = SHOWN[1], SHOWN[2]
    kit_sheet('MP-207', 'PICKUP RING A (SIZE KIT)', lambda x, z: ring(x, z, 'A'),
              [('C', 'X + 10.5  (opening)', lambda x, z: x + RA_OPEN), ('D', 'Z + 10.5  (opening)', lambda x, z: z + RA_OPEN),
               ('G', 'X + 12.5  (recess, 0.6 deep)', lambda x, z: x + 2 * BLEED + 0.5), ('H', 'Z + 12.5  (recess)', lambda x, z: z + 2 * BLEED + 0.5)],
              ['Outside 106 × 81 (−0.01/−0.02) for every size: drops into the lower carrier A pocket. Key slots KA fit only carrier A.',
               'Opening C × D, R0.5, THRU, wire-EDM; top inner edge R0.5, polished. Recess G × H, R1.5, 0.6 deep, Ra 0.8: it centres the flat tin blank, the photo and the film, all cut X + 12 (never over X + 12.4) with the corners clipped at 45°, 0.4 thick together.',
               'The blank rests on a 1.0 ledge (0.5 flat + the R0.5 edge). Verification fix: with the old X + 0.6 opening the flange was trapped on the recess floor and stroke 1 drew it into the upper ring (15 N/mm, more than the springs hold); now it slides off the ledge and is wiped down.',
               'Lift out by hand through the opening once the pedestal is out. Faces parallel 0.01.'],
              outer_dims(RX_, RZ_) + [('h', -(X + RA_OPEN) / 2, (X + RA_OPEN) / 2, 0, -RZ_ / 2 - 17, 'C'),
                                      ('v', (Z + RA_OPEN) / 2, -(Z + RA_OPEN) / 2, 0, -RX_ / 2 - 24, 'D'),
                                      ('l', (X + 12.5) / 2, -20, 30, 34, 'recess G × H, R1.5, 0.6 deep', 0)],
              [['KA', '(+54, −20), (−54, +20)', 'Key slot R2.1, centre 1.0 outside the face, full height, on the short faces']],
              dxfname='pickup_ring')


def anvil_section(w):
    """Section A-A of the Rev E anvil: w = block width (X + 0.43 or D + 0.43). Returns the outline points."""
    a, hx = ANV, w / 2.0
    hp = hx - (a['block'] + a['plat_in']) / 2.0
    cx, cz, r = hx - a['cove'], a['top'], a['cove']
    cove = [(cx + r * math.cos(math.radians(-t)), cz + r * math.sin(math.radians(-t))) for t in range(0, 91, 10)]
    right = [(hx, 0)] + cove + [(hp, a['floor']), (hp, a['platform'])]
    return [(-x, y) for (x, y) in reversed(right)] + right


def anvil_detail(sh, title):
    """Detail R (10:1): the cove and floor at the right edge, x from the shell line X/2, z from the floor."""
    a = ANV
    vd = View(sh, 330, 168, 0.1)
    e = a['block'] / 2
    w, hp = -(a['block'] + a['plat_in']) / 2 + e, a['platform'] - a['floor']        # wall x from the shell line, platform height
    vd.segs([L(w - 0.9, hp, w, hp), L(w, hp, w, 0),
             L(w, 0, e - a['cove'], 0), A(e - a['cove'], a['cove'], a['cove'], 270, 360), L(e, a['cove'], e, -1.6)])
    vd.line(e + 0.01, a['cove'], e + 0.01, 2.6, 'hid')
    vd.text(-1.7, -1.6, title, 2.8, dy=11, weight='bold')
    vd.leader(e - 0.2, 0.2, 6, 14, 'cove R0.7, tangent to the\nring B bore (X/2 + 0.225)')
    vd.leader(-1.6, 0, -8, -16, 'floor, 0.85 below the platform: the edge runs\nin here, turns up at the wall and folds back')
    vd.leader(w, hp / 2, -14, 8, 'wall X/2 − 3.3: the second fold')
    vd.leader(w - 0.6, hp, -12, 18, 'platform X − 6.6 (back plate)')


def mp208():
    X, Z = SHOWN[1], SHOWN[2]
    a = ANV
    sh = new('MP-208', 'CRIMP ANVIL (SIZE KIT)', scale='1:1 / 10:1', qty='1 per size kit (4)', material=KIT_MAT, finish=KIT_FIN,
             notes=KIT_NOTES + ['Rev E: double flat fold, as on commercial square magnets. The skirt runs down the ring B bore; the cove (Detail R) turns it inward along the floor; the wall at the platform edge turns it up and back outward under the back plate. The edge ends in two flat layers with the photo outside: a 2.8 mm printed border on the back, the cut edge of the tin hidden inside.',
                                'Block A × B (X + 0.43) slides in the crimp ring (X + 0.45). Platform E × F (X − 6.6) carries the back plate; the floor is 0.85 below it, room for the two layers.',
                                'Profile is a start value: prove it on the prototype kit, then cut tool steel. Polish the cove and floor Ra 0.2.',
                                'Drop-in: Ø12 m6 × 15 dowel in C (7 protruding), Ø4 m6 × 10 pin in Q. Lift out with the M5 puller in hole H.'] + GEN)
    o, T, fs = anvil(X, Z)
    bw, bz, pw, pz = X + a['block'], Z + a['block'], X - a['plat_in'], Z - a['plat_in']
    v = View(sh, 100, 82, 1.0)
    v.segs(o)
    v.segs(rrect(0, 0, pw, pz, 0.5))
    v.segs(rrect(0, 0, bw - 2 * a['cove'], bz - 2 * a['cove'], 0.5), 'thin')
    draw_plan_features(v, fs)
    v.cl_h(-X / 2 - 8, X / 2 + 8, 0); v.cl_v(Z / 2 + 8, -Z / 2 - 8, 0)
    sh.text(15, 18, 'PLAN (TOP) — front at bottom', 3.2, weight='bold')
    v.hdim(-bw / 2, bz / 2, bw / 2, bz / 2, bz / 2 + 9, text='A')
    v.vdim(bz / 2, bw / 2, -bz / 2, bw / 2, bw / 2 + 18, text='B')
    v.hdim(-pw / 2, -pz / 2, pw / 2, -pz / 2, -bz / 2 - 9, text='E')
    v.vdim(pz / 2, -pw / 2, -pz / 2, -pw / 2, -bw / 2 - 18, text='F')
    v.leader(bw / 2 - 0.3, -bz / 2 + 4, 24, 26, 'cove, floor and wall all round (Detail R)')
    v.section_mark(-X / 2 - 12, 0, X / 2 + 12, 0, 'A', flip=True)
    vs = View(sh, 100, 175, 1.0)
    vs.poly(anvil_section(bw), 'sec')
    vs.rect(-6, 0, 6, 8.5, 'ko'); vs.line(-6, 0, -6, 8.5, 'hid'); vs.line(6, 0, 6, 8.5, 'hid'); vs.line(-6, 8.5, 6, 8.5, 'hid')
    vs.vdim(0, bw / 2, a['top'], bw / 2, bw / 2 + 9, text=fmt(a['top']))
    vs.vdim(0, -bw / 2, a['platform'], -pw / 2, -bw / 2 - 9, text=fmt(a['platform']))
    vs.text(0, 0, 'SECTION A–A', 3.2, dy=8.5, weight='bold')
    anvil_detail(sh, 'DETAIL R (10:1) cove, floor and wall — X/2 = shell line')
    yy = size_table(sh, 212, 24, [('A', 'X + 0.43  (block, ±0.01)', lambda x, z: x + a['block']), ('B', 'Z + 0.43  (block, ±0.01)', lambda x, z: z + a['block']),
                                  ('E', 'X − 6.6  (platform)', lambda x, z: x - a['plat_in']), ('F', 'Z − 6.6  (platform)', lambda x, z: z - a['plat_in'])])
    feature_table(sh, 212, yy + 6, [['H', 'centre', 'M5 × 6 from the TOP (puller)'], ['C', 'centre', 'Ø12 H7 × 8.5 from the BOTTOM (spigot dowel)'],
                                    ['Q', '(0, +20)', 'Ø4 H7 × 6 from the BOTTOM (anti-rotation pin)']])
    for (cd, x, z) in SIZES:
        o_, T_, f_ = anvil(x, z)
        dx = DXF(); dx.segs(o_); dx.segs(rrect(0, 0, x - a['plat_in'], z - a['plat_in'], 0.5), 'POCKET'); feats_dxf(dx, f_)
        DXFS['MP-208_crimp_anvil_%s.dxf' % cd] = dx


def mp209():
    X, Z = SHOWN[1], SHOWN[2]
    def extra(sh, v, vs, vb):
        for s in (-1, 1):
            u = s * (X + 0.45) / 2
            vs.line(u, 15 - 1.2, u + s * 0.69, 15)
        vs.leader((X + 0.45) / 2 + 0.4, 14.6, 18, -10, '1.2 × 30° lead-in, all round, polished Ra 0.2')
    kit_sheet('MP-209', 'CRIMP RING B (SIZE KIT)', lambda x, z: ring(x, z, 'B'),
              [('C', 'X + 0.45  (opening, +0.01/0)', lambda x, z: x + 0.45), ('D', 'Z + 0.45  (opening, +0.01/0)', lambda x, z: z + 0.45)],
              ['Outside 106 × 81 (−0.01/−0.02) for every size: drops into the lower carrier B pocket. Key slots KB fit only carrier B.',
               'Opening C × D, R1.2, with corner reliefs Y (Ø1.2 THRU on each corner), wire-EDM, lap Ra 0.2. Top lead-in 1.2 × 30°. The bore guides the skirt down onto the anvil cove; the anvil block slides in it (X + 0.43 in X + 0.45).',
               'A drop of silicone release on the lead-in stops laser-printed film slipping. No EDM recast on the forming edges (2 skim cuts + re-temper).'],
              outer_dims(RX_, RZ_) + [('h', -(X + .45) / 2, (X + .45) / 2, 0, -RZ_ / 2 - 17, 'C'),
                                      ('v', (Z + .45) / 2, -(Z + .45) / 2, 0, -RX_ / 2 - 24, 'D')],
              [['KB', '(+54, +30), (−54, −30)', 'Key slot R2.1, centre 1.0 outside the face, full height, on the short faces (Rev E: Z ±30, so ring A turned over cannot enter carrier B)'],
               ['Y', 'opening corners', 'Ø1.2 THRU on each corner of the opening (corner relief)']],
              extra=extra, dxfname='crimp_ring')


def mp212():
    sh = new('MP-212', 'PLUG STUD (SIZE KIT)', scale='4:1', qty='1 per kit (8: 4 square, 4 round)',
             material='C45 Ø12 bar, QT 28–32 HRC', finish='Black oxide',
             notes=['Screwed into the plug MP-203 (M6) with Loctite 243 until the shoulder seats. It only holds the plug up: the dowels locate it.',
                    'The Ø6 detent pin in the body runs tangent to the groove (Rev E: along X); any rotation of the stud works. Two flats 8 a/f on the Ø10 for a spanner.',
                    'Groove: R3.1 centred 4.0 above the shoulder, root Ø7.6. Top end chamfer 0.5 × 45°.'] + GEN)
    v, pos, Ltot = P.turned(sh, 140, 110, 0.25, [{'l': 8, 'd': 6, 'thread': 'M6'}, {'l': 7.5, 'd': 10}])
    gx = 8 + 4.0
    v.segs([A(gx, 6.9, 3.1, 217.8, 322.2), A(gx, -6.9, 3.1, 37.8, 142.2)])
    v.hdim(0, -3, 8, -3, -14, text='8')
    v.hdim(8, -5, 15.5, -5, -14, text='7.5')
    v.hdim(8, 5, gx, 5, 14, text='4')
    v.vdim(-5, 18.5, 5, 18.5, 18.5, text='Ø10 h9')
    v.leader(4, 3, -6, -14, 'M6 – 6g')
    v.leader(gx, -4.9, 10, 16, 'groove R3.1, root Ø7.6')
    v.text(8, 0, 'SIDE VIEW', 3.4, dy=68, weight='bold')


# =====================================================================================
# Rev D: round size kits (MP-223 to MP-229). Same heights and fits as the square kits; turned and bored.
# =====================================================================================
KIT_NOTES_R = ['Rev D round size-kit part: one per round size, tabulated below. Shown to scale for size D58 (Ø58).',
               'Laser-mark on a side face: drawing no., size code and U / A / B where applicable (e.g. "MP-227 D58 A").']
KIT_FIN_R = 'Turn/bore +0.2; harden 58–60 HRC, temper ×2; grind, hone bores Ra 0.2; thin dense chrome'


def circ(d):
    return [C(0, 0, d / 2.0)]


def plug_r(D):
    f = [feat(STUD_R[0], STUD_R[1], 'tap', m='M6', depth=10, side='top')]
    f += [feat(x, z, 'hole', d=5, depth=8, side='top') for (x, z) in PLUG_DOWEL_R]
    return circ(D + 0.3), 14.5, f


def ring_r(D, which):
    if which == 'U':
        f, T = [feat(0, 0, 'hole', d=D + 0.35, thru=True)], 14
    elif which == 'A':
        f, T = [feat(0, 0, 'hole', d=D + 0.6, thru=True), feat(0, 0, 'hole', d=D + 2 * BLEED + 0.5, depth=0.6, side='top')], 15
    else:
        f, T = [feat(0, 0, 'hole', d=D + 0.45, thru=True)], 15
    return rr_notched(RX_, RZ_, 6, key_notches(which)), T, f


def pick_ped_r(D):
    return circ(D - 1.0), 21.8, [feat(0, 0, 'tap', m='M5', depth=6, side='top'), feat(0, 0, 'hole', d=12, depth=8.5, side='bot')]


def anvil_r(D):
    # Rev E keeps the Rev D roll channel for round kits: a round edge cannot be folded flat without wrinkling
    return circ(D + 0.3), 17, [feat(0, 0, 'tap', m='M5', depth=6, side='top'), feat(0, 0, 'hole', d=12, depth=8.5, side='bot')]


def size_table_r(sh, x, y, letters):
    cols = [('SIZE', 24, 'middle'), ('Ø', 15, 'end')] + [(l[0], 17.0, 'end') for l in letters]
    rows = [[cd, fmt(D)] + [fmt(l[2](D)) for l in letters] for (cd, D) in ROUND]
    sh.text(x, y - 2, 'DIMENSION TABLE (mm)', 3.0, weight='bold')
    yend = sh.table(x, y, cols, rows, size=2.7, rh=5.2, bold_first_col=True)
    yy = yend + 5
    sh.text(x, yy, 'Size code = magnet face diameter: D44 = Ø44, D50 = Ø50, D56 = Ø56, D58 = Ø58.', 2.4)
    yy += 4.5
    for l in letters:
        sh.text(x, yy, '%s = %s' % (l[0], l[1]), 2.6)
        yy += 4.0
    return yy


def round_sheet(no, title, fn, letters, notes, callouts, feat_rows, extra=None, sec_b=None, dxfname=None, qty='1 per round kit (4)'):
    sh = new(no, title, scale='1:1 (size D58)', qty=qty, material=KIT_MAT, finish=KIT_FIN_R, notes=KIT_NOTES_R + notes + GEN)
    code, D = SHOWN_R
    outline, T, fs = fn(D)
    v, vs, vb = plan_and_sections(sh, outline, T, fs, callouts, sec_b)
    if extra:
        extra(sh, v, vs, vb)
    yy = size_table_r(sh, 212, 24, letters)
    if feat_rows:
        feature_table(sh, 212, yy + 6, feat_rows)
    if dxfname:
        for (cd, d) in ROUND:
            o, T_, f_ = fn(d)
            dx = DXF(); dx.segs(o); feats_dxf(dx, f_)
            DXFS['%s_%s_%s.dxf' % (no, dxfname, cd)] = dx
    return sh


def dia(D, extra_w=9, label='A'):
    R = D / 2.0
    return [('h', -R, R, 0, R + extra_w, label)]


def mp223():
    D = SHOWN_R[1]
    def extra(sh, v, vs, vb):
        vd = View(sh, 345, 195, 0.2)
        pts = [(-6, 0), (-6, 6), (0, 6), (0, 1.0), (-0.3, 0.5), (-1.0, 0.25), (-1.5, 0.5), (-1.8, 0)]
        vd.poly(pts, 'sec')
        vd.text(-3, 0, 'DETAIL Y (5:1) working edge, as MP-203', 3.0, dy=12, weight='bold')
        vd.leader(-1.0, 0.25, -30, -8, 'concave lip R1, 1.5 wide × 0.5 deep\nall round the bottom face')
    round_sheet('MP-223', 'PLUG, ROUND (SIZE KIT)', plug_r,
                [('A', 'D + 0.30  (plug diameter, ±0.01)', lambda d: d + 0.30)],
                ['Turned part. Two Ø5 × 14 dowels pressed in (5.5 protruding; +X cylindrical, −X diamond) locate it on the INNER pattern D2 of the die body MP-201; stud MP-212 in the M6 hole sits in K2 and takes the same detent pin as the square kits.',
                 'Diameter A: grind after hardening, ±0.01. Sliding fit in the upper ring (ring = plug + 0.05).',
                 'Bottom (working) face flat 0.01, Ra 0.2, lip per Detail Y. Height 14.5 ±0.01 sets the 5.5 recess in the ring. No DXF: turned.'],
                [('h', -(D + 0.3) / 2, (D + 0.3) / 2, 0, (D + 0.3) / 2 + 9, 'ØA')],
                [['S', '(−13, +0.2)', 'M6 × 10 from the TOP (stud MP-212, Loctite 243)'],
                 ['D', '(±12, −12)', 'Ø5 H7 × 8 from the TOP (dowels Ø5 × 14: +X cylindrical, −X diamond)']], extra=extra)


def mp224():
    D = SHOWN_R[1]
    def extra(sh, v, vs, vb):
        for sx in (-1, 1):
            for sz in (-1, 1):
                u = sx * D / 4
                w0 = sz * math.sqrt(((D + 0.35) / 2) ** 2 - u * u)
                w1 = sz * RZ_ / 2
                v.line(u - 2, w0, u - 2, w1, 'hid'); v.line(u + 2, w0, u + 2, w1, 'hid'); v.cl_v(w0, w1, u)
            v.poly([(sx * RX_ / 2, -3), (sx * (RX_ / 2 - 3), 0), (sx * RX_ / 2, 3)], 'hid')
        v.leader(D / 4, -RZ_ / 2, 30, 28, 'N: 4× M3 THRU from the long faces\n1.8 above the BOTTOM face, at X = ±E')
        v.leader(RX_ / 2, 0, 30, 45, 'M: Ø3.6 × 3.5 hole, both X ends, 7 above\nthe bottom face (dog-point thumb screws)')
        vd = View(sh, 345, 190, 0.2)
        vd.poly([(-8, 0), (-8, 8), (0, 8), (0, 0.52), (-0.3, 0)], 'sec')
        vd.text(-4, 0, 'DETAIL P (5:1) bottom inner edge', 3.0, dy=18, weight='bold')
        vd.leader(-0.15, 0.3, -30, 10, 'lead-in 0.3 × 30° all round, polished')
    round_sheet('MP-224', 'UPPER RING, ROUND (SIZE KIT)', lambda d: ring_r(d, 'U'),
                [('C', 'D + 0.35  (bore, +0.01/0)', lambda d: d + 0.35), ('E', 'D / 4  (plunger offset in X)', lambda d: d / 4)],
                ['Outside 106 × 81 (−0.01/−0.02) for every size: fits the upper carrier MP-210 pocket. Key slots K (R2.1, centre 1.0 outside the face) take the carrier pins.',
                 'Bore C: bore and hone after hardening, Ra 0.2. Bottom inner lead-in 0.3 × 30° (Detail P). Deburr the plunger breakouts in the bore.',
                 'Held by 2 dog-point thumb screws in holes M. Four M3 ball plungers N stand 0.2–0.3 into the bore at 1.8 above the bottom face.'],
                [('h', -RX_ / 2, RX_ / 2, RZ_ / 2, RZ_ / 2 + 9, fmt(RX_)), ('v', RZ_ / 2, -RZ_ / 2, RX_ / 2, RX_ / 2 + 16, fmt(RZ_)),
                 ('h', -(D + .35) / 2, (D + .35) / 2, 0, -RZ_ / 2 - 17, 'ØC')],
                [['K', '(0, ±41.5)', 'Key slot R2.1, centre 1.0 outside the face, full height, on both long faces'],
                 ['M', '(±53, 0)', 'Ø3.6 × 3.5 deep, 7 above the bottom face (dog-point thumb screws)'],
                 ['N', '(±E, long faces)', 'M3 THRU to the bore, 1.8 above the bottom face (ball plungers)']],
                extra=extra, sec_b=(20, 'Z = ±20'), dxfname='upper_ring_round')


def mp226():
    D = SHOWN_R[1]
    round_sheet('MP-226', 'PICKUP PEDESTAL, ROUND (SIZE KIT)', pick_ped_r,
                [('A', 'D − 1.0  (±0.01)', lambda d: d - 1.0)],
                ['The tinplate shell sits face-up over it with 0.3 clearance a side (Rev E: was D − 0.5). Top face flat 0.01, Ra 0.2; top edge R0.3. Height 21.8 ±0.02.',
                 'Turned part. Press a Ø12 m6 × 15 dowel into C (7 protruding). No anti-rotation pin: a round pedestal can turn. Lift out with the M5 T-handle puller in hole H. No DXF: turned.'],
                [('h', -(D - 1) / 2, (D - 1) / 2, 0, (D - 1) / 2 + 9, 'ØA')],
                [['H', 'centre', 'M5 × 6 from the TOP (puller)'], ['C', 'centre', 'Ø12 H7 × 8.5 from the BOTTOM (spigot dowel)']])


def mp227():
    D = SHOWN_R[1]
    round_sheet('MP-227', 'PICKUP RING A, ROUND (SIZE KIT)', lambda d: ring_r(d, 'A'),
                [('C', 'D + 0.6  (bore)', lambda d: d + 0.6), ('G', 'D + 9.5  (film recess, 0.6 deep)', lambda d: d + 2 * BLEED + 0.5)],
                ['Outside 106 × 81 (−0.01/−0.02) for every size: drops into the lower carrier A pocket. Key slots KA fit only carrier A.',
                 'Bore C THRU, top inner edge R0.5. Film recess ØG, 0.6 deep, Ra 0.8: it centres the photo and film.',
                 'Lift out by hand through the bore once the pedestal is out. Faces parallel 0.01.'],
                [('h', -RX_ / 2, RX_ / 2, RZ_ / 2, RZ_ / 2 + 9, fmt(RX_)), ('v', RZ_ / 2, -RZ_ / 2, RX_ / 2, RX_ / 2 + 16, fmt(RZ_)),
                 ('h', -(D + .6) / 2, (D + .6) / 2, 0, -RZ_ / 2 - 17, 'ØC')],
                [['KA', '(+54, −20), (−54, +20)', 'Key slot R2.1, centre 1.0 outside the face, full height, on the short faces']],
                dxfname='pickup_ring_round')


def mp228():
    D = SHOWN_R[1]
    sh = new('MP-228', 'CRIMP ANVIL, ROUND (SIZE KIT)', scale='1:1 / 10:1', qty='1 per round kit (4)', material=KIT_MAT, finish=KIT_FIN_R,
             notes=KIT_NOTES_R + ['Rev D, kept in Rev E: turned. The R1.0 roll channel runs round the full circle (Detail R): it rolls the shell edge inward under the back plate. Round kits do not get the Rev E double flat fold: a round edge cannot be folded flat without wrinkling.',
                                  'Block D + 0.3 slides in the crimp ring (D + 0.45) and guides it. Platform (D − 4.5) carries the back plate.',
                                  'Channel profile is a start value: prove it on the 7075 prototype kit. Polish the channel Ra 0.2. Drop-in: Ø12 m6 × 15 dowel in C (7 protruding); no anti-rotation pin.'] + GEN)
    o, T, fs = anvil_r(D)
    v = View(sh, 100, 82, 1.0)
    v.segs(o)
    v.segs(circ(D - 4.5))
    v.segs(circ(D), 'thin'); v.segs(circ(D - 4.0), 'thin')
    draw_plan_features(v, fs)
    v.cl_h(-D / 2 - 8, D / 2 + 8, 0); v.cl_v(D / 2 + 8, -D / 2 - 8, 0)
    sh.text(15, 18, 'PLAN (TOP)', 3.2, weight='bold')
    v.hdim(-(D + .3) / 2, 0, (D + .3) / 2, 0, (D + .3) / 2 + 9, text='ØA')
    v.hdim(-(D - 4.5) / 2, 0, (D - 4.5) / 2, 0, -(D + .3) / 2 - 9, text='ØE')
    v.leader((D - 2) / 2 * 0.7071, (D - 2) / 2 * 0.7071, 26, -20, 'roll channel all round (Detail R)')
    v.section_mark(-D / 2 - 12, 0, D / 2 + 12, 0, 'A', flip=True)
    vs = View(sh, 100, 175, 1.0)
    hx, hp = (D + 0.3) / 2, (D - 4.5) / 2
    chan = [(D / 2 - 1.0 + math.cos(math.radians(t)), 16 - math.sin(math.radians(t))) for t in range(0, 181, 15)]
    prof = [(-hx, 0), (hx, 0), (hx, 16)] + chan + [(hp, 17), (-hp, 17)] + [(-x, y) for (x, y) in reversed(chan)] + [(-hx, 16)]
    vs.poly(prof, 'sec')
    vs.rect(-6, 0, 6, 8.5, 'ko'); vs.line(-6, 0, -6, 8.5, 'hid'); vs.line(6, 0, 6, 8.5, 'hid'); vs.line(-6, 8.5, 6, 8.5, 'hid')
    vs.vdim(0, hx, 16, hx, hx + 9, text='16')
    vs.vdim(0, -hx, 17, -hx, -hx - 9, text='17')
    vs.text(0, 0, 'SECTION A–A', 3.2, dy=8.5, weight='bold')
    vd = View(sh, 330, 168, 0.1)
    vd.segs([L(-3.5, -4, 0.15, -4), L(0.15, -4, 0.15, 0), L(0.15, 0, 0.0, 0), A(-1.0, 0, 1.0, 180, 360), L(-2.0, 0, -2.25, 1.0), L(-2.25, 1.0, -3.5, 1.0)])
    vd.text(-1.75, -4, 'DETAIL R (10:1) roll channel (round kits only)', 2.8, dy=11, weight='bold')
    vd.leader(-1.0, -1.0, -18, 10, 'R1.0, centre 1.0 inside the shell line D/2,\nlevel with the rim (1.0 below the platform)')
    yy = size_table_r(sh, 212, 24, [('A', 'D + 0.3  (block, ±0.01)', lambda d: d + 0.3), ('E', 'D − 4.5  (platform)', lambda d: d - 4.5)])
    feature_table(sh, 212, yy + 6, [['H', 'centre', 'M5 × 6 from the TOP (puller)'], ['C', 'centre', 'Ø12 H7 × 8.5 from the BOTTOM (spigot dowel)']])


def mp229():
    D = SHOWN_R[1]
    def extra(sh, v, vs, vb):
        for sx in (-1, 1):
            u = sx * (D + 0.45) / 2
            vs.line(u, 15 - 1.2, u + sx * 0.69, 15)
        vs.leader((D + 0.45) / 2 + 0.4, 14.6, 18, -10, '1.2 × 30° lead-in, all round, polished Ra 0.2')
    round_sheet('MP-229', 'CRIMP RING B, ROUND (SIZE KIT)', lambda d: ring_r(d, 'B'),
                [('C', 'D + 0.45  (bore, +0.01/0)', lambda d: d + 0.45)],
                ['Outside 106 × 81 (−0.01/−0.02) for every size: drops into the lower carrier B pocket. Key slots KB fit only carrier B.',
                 'Bore C THRU, honed Ra 0.2. Top lead-in 1.2 × 30° folds the film under the shell edge and guides the shell onto the anvil\'s roll channel (round kits keep the Rev D rolled edge).'],
                [('h', -RX_ / 2, RX_ / 2, RZ_ / 2, RZ_ / 2 + 9, fmt(RX_)), ('v', RZ_ / 2, -RZ_ / 2, RX_ / 2, RX_ / 2 + 16, fmt(RZ_)),
                 ('h', -(D + .45) / 2, (D + .45) / 2, 0, -RZ_ / 2 - 17, 'ØC')],
                [['KB', '(+54, +30), (−54, −30)', 'Key slot R2.1, centre 1.0 outside the face, full height, on the short faces']],
                extra=extra, dxfname='crimp_ring_round')


# =====================================================================================
# MP-001 GENERAL ARRANGEMENT
# =====================================================================================
def lever_rest_height(psi=3.0, z=105.0):
    """y of the lever underside above the front column (z) at handle angle psi."""
    prof, _ = P.lever_profile()
    c, s = math.cos(math.radians(psi)), math.sin(math.radians(psi))
    best = None
    for i in range(len(prof)):
        (u0, w0), (u1, w1) = prof[i], prof[(i + 1) % len(prof)]
        n = max(20, int(math.hypot(u1 - u0, w1 - w0) / 0.1))
        for t in [k / float(n) for k in range(n + 1)]:
            u, w = u0 + (u1 - u0) * t, w0 + (w1 - w0) * t
            zz, yy = u * c - w * s, 234.5 + u * s + w * c
            if abs(zz - z) < 8 and w < 0:
                best = yy if best is None else min(best, yy)
    return best


def mp001():
    sh = new('MP-001', 'GENERAL ARRANGEMENT & HEIGHTS', scale='1:3 / 1:5', qty='—',
             material='—', finish='—',
             notes=['Shown with the handle UP (open), die table at "B under ram", size kit 6363 in the universal die. Heights from the bench top.',
                    'Toggle: crank O→A 40, link A→B 60, grip centre 320 from O (Rev A 290). Handle 65° → 3° above horizontal. Force gain 6.6 at the start, 34.6 at the end of the stroke.',
                    'Ram stroke 38.9. Dies meet after 26.0; working travel 12.9. Pickup stroke stops at 35.5. Station pilot MP-120 enters the table at 20.0, before the dies meet.',
                    'Open stop: 2 urethane bumpers on the ram top. Closed stop: adjustable M10 × 1 screw + urethane cap in the post MP-121 on the crown (Rev E), set so the lever rests at 3°.',
                    'Rev B: one-piece lever (MP-115 deleted); pin O Ø16; dry bushings; return springs 80 / 245 N; station pilot; 15 mm base. Rev C: universal die + size kits (MP-201 to 212). Rev C.1: seven fit fixes from the 3D check (MP-101, 104, 105, 107, 108, 109). Rev D: round size kits Ø44 to Ø58 (MP-223 to 229), inner plug pattern on MP-201. Rev E: fixes from the independent review (see the cover).',
                    'Balloons = drawing numbers (MP-xxx). Pins MP-116 at A and B, MP-117 at O; spacers MP-119 on pin O; stop blocks MP-104 behind the table.'])
    v = View(sh, 150, 214, 3.0)
    def box(z0, z1, y0, y1, c='vis'): v.rect(z0, y0, z1, y1, c)
    X, Z = 63.5, 63.5
    for z in (-80, 80, 300): box(z - 12, z + 12, 0, 3)
    box(-130, 340, 3, 18)
    for s in (-1, 1):
        box(s * 75, s * 89, 18, 30.05); box(s * 70, s * 90, 30.05, 34.05)
    box(-75, 75, 18, 30)
    box(-60, 60, 30, 40)
    box(-CZ / 2, CZ / 2, 48, 66); box(-RZ_ / 2, RZ_ / 2, 51, 66, 'hid')
    box(-(Z - 4.5) / 2, (Z - 4.5) / 2, 40, 57, 'hid')
    box(-CZ / 2, CZ / 2, 92, 106); box(-RZ_ / 2, RZ_ / 2, 92, 106, 'hid')
    box(-(Z + 0.3) / 2, (Z + 0.3) / 2, 106, 112)
    box(-CZ / 2, CZ / 2, 112, 122); box(-CZ / 2, -27, 122, 132); box(27, CZ / 2, 122, 132)   # Rev E body 20 thick, holder counterbore
    box(-20, 20, 122, 123); box(-25, 25, 123, 134)
    box(-125, 125, 134, 164)
    v.poly([(-69, 134), (-69, 54), (-65, 50), (-61, 54), (-61, 134)], 'vis')
    for s in (-1, 1):
        box(s * 105 - 20, s * 105 + 20, 164, 167)
        box(s * 105 - 12.5, s * 105 + 12.5, 18, 134); box(s * 105 - 12.5, s * 105 + 12.5, 167, 176)
        box(s * 105 - 10, s * 105 + 10, 176, 201, 'hid')
        box(s * 105 - 8, s * 105 + 8, 201, 217); box(s * 105 - 12, s * 105 + 12, 203.5, 216.5)
    y_rest = lever_rest_height()
    box(105 - 5, 105 + 5, 217, y_rest - 4); box(105 - 8, 105 + 8, y_rest - 4, y_rest)
    box(-125, 125, 176, 201)
    box(-25, 25, 201, 251)
    box(-16, 16, 164, 184)
    for zc in (60, -60):
        box(zc - 8, zc + 8, 164, 176)
        box(zc - 5, zc + 5, 176, 324, 'thin')
        box(zc - 15.75, zc + 15.75, 201, 310.5, 'thin')
        for yy in [201 + k * 109.5 / 16 for k in range(16)]:
            v.line(zc - 15.75, yy, zc + 15.75, yy + 109.5 / 32, 'thin')
        box(zc - 16, zc + 16, 310.5, 313.5)
        box(zc - 8, zc + 8, 313.5, 321.5)
    O = (0, 234.5)
    prof, (Az, Ay) = P.lever_profile()
    def rot(pts, psi):
        c, s = math.cos(math.radians(psi)), math.sin(math.radians(psi))
        return [(u * c - w * s, 234.5 + u * s + w * c) for (u, w) in pts]
    grip = [(260, -16), (380, -16), (380, 16), (260, 16)]
    v.poly(rot(prof, 65), 'fillw'); v.poly(rot(grip, 65), 'fillw')
    v.segs(polyline(rot(prof, 3)), 'ph'); v.segs(polyline(rot(grip, 3)), 'ph')
    A_ = rot([(Az, Ay)], 65)[0]
    B_ = (0, 174.04)
    ang = math.atan2(A_[1] - B_[1], A_[0] - B_[0]); nx, ny = -math.sin(ang) * 12, math.cos(ang) * 12
    ex, ey = math.cos(ang) * 12, math.sin(ang) * 12
    v.poly([(B_[0] - ex + nx, B_[1] - ey + ny), (A_[0] + ex + nx, A_[1] + ey + ny), (A_[0] + ex - nx, A_[1] + ey - ny), (B_[0] - ex - nx, B_[1] - ey - ny)], 'fillw')
    for (p, t, r) in ((O, 'O', 8), (A_, 'A', 6), (B_, 'B', 6)):
        v.circle(p[0], p[1], r, 'vis'); v.cmark(p[0], p[1], r)
        v.text(p[0], p[1], t, 3.2, 'start', dx=3.5, dy=-2.5, weight='bold')
    v.cl_h(-10, 120, 234.5)
    v.adim(0, 234.5, 34, 0, 65, '65°')
    v.adim(0, 234.5, 52, 0, 3, '3°')
    gtop = max(y for (_, y) in rot(grip, 65))
    H = [(0, 'bench'), (3, 'base underside (3 mm pads)'), (18, 'base top'), (30, 'die table top'), (40, 'station base top'), (66, 'lower die top'),
         (92, 'upper die bottom'), (134, 'ram bottom'), (164, 'ram top'), (176, 'crown bottom'), (201, 'crown top'), (234.5, 'pivot O'),
         (324, 'return-rod top'), (round(gtop), 'grip top, handle up')]
    sh.text(16, 20, 'KEY HEIGHTS, handle up (mm from bench)', 2.8, weight='bold')
    sh.table(16, 22, [('HEIGHT', 18, 'end'), ('LEVEL', 46, 'start')], [[fmt(y), t] for (y, t) in reversed(H)], size=2.6, rh=4.4)
    v.text(385, 212, 'handle down (phantom)', 2.6, 'end')
    v.text(100, 0, 'SIDE ELEVATION (viewed from the left; front →)', 3.4, dy=10, weight='bold')
    left = [(-120, 12, 210, '101'), (-105, 80, 192, '107'), (-65, 100, 180, '120'), (-100, 149, 168, '109'), (-12, 175, 158, '110'),
            (-100, 188, 148, '108'), (-60, 262, 128, '118')]
    right = [(60, 24, 206, '105'), (55, 35, 196, '205'), (52, 57, 186, '211'), (52, 99, 176, '210'), (52, 117, 166, '201'), (22, 128, 156, '111'),
             (12, 189, 120, '114'), (20, 245, 106, '112'), (320 * math.cos(math.radians(65)), 234.5 + 320 * math.sin(math.radians(65)), 40, '113')]
    for col, bx in ((left, 88), (right, 240)):
        for (z, y, by, t) in col:
            x, yy = v.P(z, y)
            ex_ = bx + (5.5 if bx < x else -5.5)
            sh.line(x, yy, ex_, by, 'dim'); sh.circle(x, yy, 0.7, 'solidbk')
            sh.circle(bx, by, 5.5, 'fillw'); sh.text(bx, by + 1, t, 2.8, 'middle', weight='bold')
    # front elevation (1:5): x horizontal, y up; table with B under ram
    vf = View(sh, 350, 118, 5.0)
    def fb(x0, x1, y0, y1, c='vis'): vf.rect(x0, y0, x1, y1, c)
    fb(-230, 230, 3, 18)
    for x in (-200, 200): fb(x - 12, x + 12, 0, 3)
    fb(-250, 90, 18, 30)
    for cx in (-160, 0):
        fb(cx - 75, cx + 75, 30, 40); fb(cx - CX / 2, cx + CX / 2, 48, 66); fb(cx - RX_ / 2, cx + RX_ / 2, 51, 66, 'hid')
    fb(-CX / 2, CX / 2, 92, 106); fb(-CX / 2, CX / 2, 112, 122); fb(-CX / 2, -27, 122, 132); fb(27, CX / 2, 122, 132); fb(-25, 25, 123, 134)
    fb(-40, 40, 134, 164); fb(-40, 40, 176, 201)
    fb(-4, 4, 50, 134, 'hid')
    for s in (-1, 1):
        fb(s * 20, s * 36, 201, 251); fb(s * 86, s * 116, 34, 50)
        fb(s * 30 - 5, s * 30 + 5, 201, 324, 'thin'); fb(s * 30 - 15.75, s * 30 + 15.75, 201, 310.5, 'thin'); fb(s * 30 - 8, s * 30 + 8, 313.5, 321.5)
    fb(-12.5, 12.5, 18, 176); fb(-10, 10, 176, 201); fb(-8, 8, 201, 217)
    fb(-10, 10, 220, 300)
    vf.hdim(-230, 3, 230, 3, -18, text='460')
    vf.hdim(-160, 66, 0, 66, 80, text='160 (stations)')
    vf.hdim(-40, 164, 40, 164, 340, text='80 (ram)')
    vf.text(0, 0, 'FRONT ELEVATION 1:5 (handle cut off)', 3.2, dy=10, weight='bold')
    vf.text(-160, 51, 'A', 2.6); vf.text(-40, 51, 'B', 2.6)


# =====================================================================================
# MP-000 COVER
# =====================================================================================
def mp000(listing, img_b64=None, img2_b64=None):
    sh = Sheet('MP-000', 'DRAWING SET — COVER & LIST', scale='—', material='—', finish='—', qty='—',
               notes=['Units mm. First-angle projection (ISO 128-30); every view is also labelled by name.',
                      'General tolerances ISO 2768-mK unless stated. Fits ISO 286. Threads ISO metric coarse 6H/6g unless stated. Ra 3.2 unless stated.',
                      'Column bores in base MP-101, crown MP-108 and ram MP-109 at 210.00 ±0.01: same datum scheme and CNC program.',
                      'Universal parts (MP-201, 202, 205, 210, 211) are made once per press. Square and rectangular kit parts (MP-203, 204, 206 to 209, 212) are tabulated for 5050, 6363, 5380, 6590; Rev D round kit parts (MP-223, 224, 226 to 229, with stud MP-212) for D44, D50, D56, D58.',
                      'DXF profiles are supplied for cutting and wire-EDM. If a DXF and a drawing disagree, the drawing governs. Bought parts are in the build pack BOM.',
                      'Rev B: failure-mode review (lever, pin O, bushings, return springs, pilot, base, 16 kN). Rev C (2026-10-27): universal die + 6-part size kits changed by hand in about a minute; crimp anvil with roll channel; die springs re-rated to ISO 10243 limits. Rev C.1 (2026-10-27): fit fixes from the 3D interference check: ram link pockets (MP-109), crown reliefs for pins A and B (MP-108), push knobs on the table top (MP-105), flush column clamp (MP-101, MP-107), handle stop without jam nut, stop screw M6 × 0.75 × 40 (MP-104). Rev D (2026-10-27): four round size kits on the same universal die; MP-201 gains the inner plug pattern D2/K2. Rev E (2026-10-27), release: fixes from the independent review: sharp-cornered magnets from flat tin blanks folded in stroke 1, double flat fold (hem) with a printed border on the back (round kits keep the rolled edge); die body 20 thick with Ø12.5 × 44 red upper springs; detent pin along X; spigots; crown 120; stop post MP-121.',
                      'Prove the die fits on a 7075 aluminium set before cutting tool steel.'])
    P.SHEETS.insert(0, sh)
    sh.text(20, 30, 'MagPress M4', 12, weight='bold')
    sh.text(20, 40, 'Photo-magnet press · drawing set · Rev E (release)', 4.2)
    sh.text(20, 47, 'One universal die + size kits: 50 × 50, 63.5 × 63.5, 53 × 80, 65 × 90 mm', 3.2)
    sh.text(20, 52, 'Round kits (Rev D): Ø44, Ø50, Ø56, Ø58 mm', 3.2)
    cols = [('DRG NO.', 22, 'start'), ('TITLE', 70, 'start'), ('QTY', 36, 'start'), ('SHEET', 14, 'middle')]
    sh.text(20, 60, 'DRAWING LIST', 3.2, weight='bold')
    sh.table(20, 62, cols, listing, size=2.4, rh=4.1)
    if img_b64:
        sh.add('<image x="178" y="18" width="111" height="200" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,%s"/>' % img_b64)
        sh.rect(178, 18, 111, 200, 'box')
    if img2_b64:
        sh.add('<image x="293" y="18" width="111" height="200" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,%s"/>' % img2_b64)
        sh.rect(293, 18, 111, 200, 'box')
    if img_b64 or img2_b64:
        sh.text(180, 224, 'Reference renderings (Rev E): assembled, handle up (left); exploded (right). Not for measurement.', 2.6, italic=True)
    return sh
