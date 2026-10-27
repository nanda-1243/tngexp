"""Die-set drawings (MP-2xx), general arrangement (MP-001) and cover (MP-000). Rev B: universal die outers."""
import math
from draft import *
import parts as P
from parts import new, SIZES, SIZE_LABEL, SHOWN, GEN, DXFS

DIE_NOTES = ['Tabulated drawing: one part per die size. Shown to scale for size 6590 (65 × 90 magnet). X = long side, along the die table.',
             'Mark each part on a side face: drawing no., size code and A/B where applicable (e.g. "MP-207 6590 A").']
UNI_NOTES = ['Rev B universal part: identical for all four die sizes (5050, 6363, 5380, 6590). X = along the die table.',
             'Mark each part on a side face with its drawing no. (and A/B where applicable).']

# Rev B universal die geometry (same for every size)
UX, UZ = 126.0, 100.0                       # outside of body, upper frame and lower frames
RX, RZ = 54.0, 41.5                         # frame-retention shoulder screws (±RX, ±RZ)
SPR_A = [(RX, 0), (-RX, 0), (0, RZ), (0, -RZ)]                                               # upper frame and pickup springs
SPR_B = [(sx * RX, sz * 16.25) for sx in (-1, 1) for sz in (-1, 1)] + [(sx * 22.5, sz * RZ) for sx in (-1, 1) for sz in (-1, 1)]
FX = 12.5                                    # plug / pedestal fixing: M5 at (±FX, ±FX), Ø5 dowels at (±FX, 0)
SHOE = (150.0, 120.0)
DOWEL = {'A': [(-40, -30), (40, -30)], 'B': [(-30, 30), (30, 30)]}
THUMB = [(70, 55), (-70, -55)]

DIE_MAT = 'A2 / 1.2363 tool steel; 7075-T6 for the prototype set; PM cold-work steel for high volume'
DIE_FIN = 'Harden 58–60 HRC, temper ×2; wire-EDM + 2 skim cuts, then re-temper; forming edges Ra 0.2; thin dense chrome'


def fixings(side, kind):
    """plug / pedestal fixing pattern. kind 'part' = tapped holes in the plug or pedestal; 'plate' = clearance in body or shoe."""
    f = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            if kind == 'part':
                f.append(feat(sx * FX, sz * FX, 'tap', m='M5', depth=10, side=side))
            else:
                f.append(feat(sx * FX, sz * FX, 'hole', d=5.5, thru=True, cb=(9.5, 5.5), cbside=side))
        if kind == 'part':
            f.append(feat(sx * FX, 0, 'hole', d=5, depth=8, side=side))
        else:
            f.append(feat(sx * FX, 0, 'hole', d=5, thru=True))
    return f


def corners(px, pz):
    return [(sx * px, sz * pz) for sx in (-1, 1) for sz in (-1, 1)]


# ---------------- part definitions ----------------
def body(X=None, Z=None):
    f = [feat(0, 0, 'tap', m='M10', thru=True)] + fixings('top', 'plate')
    f += [feat(x, z, 'tap', m='M5', thru=True) for (x, z) in corners(RX, RZ)]
    f += [feat(x, z, 'hole', d=10.5, depth=6, side='bot') for (x, z) in SPR_A]
    f.append(feat(0, 20, 'hole', d=4, depth=6, side='top'))
    return rrect(0, 0, UX, UZ, 6), 10, f


def plug(X, Z):
    return rrect(0, 0, X + 0.3, Z + 0.3, 4.15), 14.5, fixings('top', 'part')


def upframe(X, Z):
    f = [feat(0, 0, 'rr', w=X + 0.35, h=Z + 0.35, r=4.2, thru=True)]
    f += [feat(x, z, 'hole', d=6.1, thru=True, cb=(10.5, 10), cbside='bot') for (x, z) in corners(RX, RZ)]
    f += [feat(x, z, 'hole', d=10.5, depth=10, side='top') for (x, z) in SPR_A]
    return rrect(0, 0, UX, UZ, 3), 14, f


def shoe(which):
    f = [feat(x, z, 'hole', d=8, depth=8, side='bot') for (x, z) in DOWEL[which]]
    f += [feat(x, z, 'hole', d=5.5, thru=True) for (x, z) in THUMB]
    f += [feat(x, z, 'tap', m='M5', thru=True) for (x, z) in corners(RX, RZ)]
    f += fixings('bot', 'plate')
    f += [feat(x, z, 'hole', d=10.5, depth=6, side='top') for (x, z) in (SPR_A if which == 'A' else SPR_B)]
    return rrect(0, 0, SHOE[0], SHOE[1], 3), 10, f


def pick_ped(X, Z):
    return rrect(0, 0, X - 0.5, Z - 0.5, 3.75), 21.8, fixings('bot', 'part')


def crimp_ped(X, Z):
    return rrect(0, 0, X - 4.5, Z - 4.5, 2.5), 17, fixings('bot', 'part')


def lowframe(X, Z, which):
    if which == 'A':
        f = [feat(0, 0, 'rr', w=X + 0.6, h=Z + 0.6, r=4.3, thru=True), feat(0, 0, 'rr', w=X + 12.5, h=Z + 12.5, r=6.25, depth=0.6, side='top')]
    else:
        f = [feat(0, 0, 'rr', w=X + 0.45, h=Z + 0.45, r=4.2, thru=True)]
    f += [feat(x, z, 'hole', d=6.1, thru=True, cb=(10.5, 14), cbside='top') for (x, z) in corners(RX, RZ)]
    f += [feat(x, z, 'hole', d=10.5, depth=14, side='bot') for (x, z) in (SPR_A if which == 'A' else SPR_B)]
    return rrect(0, 0, UX, UZ, 3), 18, f


# ---------------- common plan + sections ----------------
def plan_and_sections(sh, outline, T, fs, callouts, sec_b=None, oy=82):
    v = View(sh, 100, oy, 1.0)
    v.segs(outline)
    draw_plan_features(v, fs)
    xs = [p for g in outline if g[0] == 'L' for p in (g[1], g[3])]
    hx = max(xs)
    v.cl_h(-hx - 5, hx + 5, 0); v.cl_v(UZ / 2 + 5, -UZ / 2 - 5, 0)
    sh.text(15, 18, 'PLAN (TOP) — front at bottom', 3.2, weight='bold')
    for c in callouts:
        kind = c[0]
        if kind == 'h':
            _, u1, u2, w, wd, t = c; v.hdim(u1, w, u2, w, wd, text=t)
        elif kind == 'v':
            _, w1, w2, u, ud, t = c; v.vdim(w1, u, w2, u, ud, text=t)
        elif kind == 'l':
            _, u, w, dx_, dy_, t, r = c; v.leader(u, w, dx_, dy_, t, on_circle_r=r)
    v.section_mark(-hx - 7, 0, hx + 7, 0, 'A', flip=True)
    vs = View(sh, 100, 175, 1.0)
    draw_section(vs, solid_minus_thru((-hx, hx), fs, 0), T, fs, 0, y0=0)
    vs.vdim(0, hx, T, hx, hx + 9, text=fmt(T))
    vs.text(0, 0, 'SECTION A–A', 3.2, dy=9, weight='bold')
    vb = None
    if sec_b is not None:
        zc, label = sec_b
        v.section_mark(-hx - 7, -zc, hx + 7, -zc, 'B', flip=False)
        vb = View(sh, 100, 209, 1.0)
        draw_section(vb, solid_minus_thru((-hx, hx), fs, zc), T, fs, zc, y0=0)
        vb.text(0, 0, 'SECTION B–B (' + label + ')', 3.2, dy=9, weight='bold')
    return v, vs, vb


def uni_dims(T_label=True):
    """dimension callouts for the universal 126 × 100 outline and the retention / spring pattern."""
    return [('h', -UX / 2, UX / 2, UZ / 2, UZ / 2 + 9, fmt(UX)),
            ('v', UZ / 2, -UZ / 2, UX / 2, UX / 2 + 16, fmt(UZ)),
            ('h', -RX, RX, -RZ, -UZ / 2 - 9, fmt(2 * RX)),
            ('v', RZ, -RZ, -RX, -UX / 2 - 16, fmt(2 * RZ))]


def feature_table(sh, x, y, rows, title='FEATURES (positions from the part centre, +Z = front)'):
    sh.text(x, y - 2, title, 3.0, weight='bold')
    cols = [('KEY', 12, 'middle'), ('POSITIONS (X, Z)', 54, 'start'), ('FEATURE', 120, 'start')]
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


FIX_ROWS_PART = lambda side: [['F', '(±12.5, ±12.5)', 'M5 × 10 deep from the %s (4×)' % side],
                              ['G', '(±12.5, 0)', 'Ø5 H7 × 8 deep from the %s (dowels Ø5 m6)' % side]]
FIX_ROWS_PLATE = lambda side: [['F', '(±12.5, ±12.5)', 'Ø5.5 THRU, CBORE Ø9.5 × 5.5 from the %s (M5 × 20 ISO 4762)' % side],
                               ['G', '(±12.5, 0)', 'Ø5 H7 THRU (dowels Ø5 m6 × 20)']]
RET = '(±54, ±41.5)'
SPA = '(±54, 0), (0, ±41.5)'
SPB = '(±54, ±16.25), (±22.5, ±41.5)'


# ---------------- tabulated die sheet ----------------
def die_sheet(no, title, fn, letters, notes, qty, callouts, feat_rows, extra=None, sec_b=None, dxfname=None,
              material=DIE_MAT, finish=DIE_FIN):
    sh = new(no, title, scale='1:1 (size 6590)', qty=qty, material=material, finish=finish, notes=DIE_NOTES + notes + GEN)
    code, X, Z = SHOWN
    outline, T, fs = fn(X, Z)
    v, vs, vb = plan_and_sections(sh, outline, T, fs, callouts, sec_b)
    if extra:
        extra(sh, v, vs)
    yy = size_table(sh, 212, 24, letters)
    if feat_rows:
        feature_table(sh, 212, yy + 6, feat_rows)
    if dxfname:
        for (cd, x, z) in SIZES:
            o, T_, f_ = fn(x, z)
            dx = DXF(); dx.segs(o); feats_dxf(dx, f_)
            DXFS['%s_%s_%s.dxf' % (no, dxfname, cd)] = dx
    return sh


def mp201():
    sh = new('MP-201', 'UPPER DIE BODY (UNIVERSAL)', scale='1:1', qty='4 (1 per set)',
             material='1.2312 (P20+S) prehardened 28–32 HRC, or C45 QT', finish='Black oxide',
             notes=UNI_NOTES + ['Rev B: one body for every size (was X + 32 × Z + 32). Only the plug MP-203 and frame MP-204 change with size.',
                                'Top face (die seat against holder/shims) and bottom face parallel 0.01, flat 0.01.',
                                'Upper frame springs: 4 × ISO 10243 Ø10 × 25 blue. Cavity 22 at rest (12 % preload), 16.5 at full travel (34 %). Replace every 250 000 strokes.',
                                'Orientation pin hole Ø4 H7 × 6 deep in the top face, 20 from centre toward the FRONT; press in Ø4 m6 × 10.'] + GEN)
    outline, T, fs = body()
    v, vs, vb = plan_and_sections(sh, outline, T, fs,
                                  uni_dims() + [('h', -FX, FX, -FX, -UZ / 2 - 17, '25'), ('v', FX, -FX, FX, UX / 2 + 26, '25'),
                                                ('l', 0, 0, 92, 10, 'M10 THRU (shank)', 4.25),
                                                ('l', 0, -20, 75, 40, 'Ø4 H7 × 6 (top)\n20 from centre, FRONT', 2)],
                                  sec_b=(RZ, 'Z = ±41.5'))
    rows = [['S', 'centre', 'M10 THRU (shank MP-202)']] + FIX_ROWS_PLATE('TOP') + \
           [['R', RET, 'M5 THRU (frame shoulder screws ISO 7379 Ø6 × 10)'],
            ['P', SPA, 'Ø10.5 × 6 deep from the BOTTOM (spring pockets)'],
            ['O', '(0, +20)', 'Ø4 H7 × 6 deep from the TOP (orientation pin)']]
    feature_table(sh, 212, 26, rows)
    dx = DXF(); dx.segs(outline); feats_dxf(dx, fs); DXFS['MP-201_upper_body_universal.dxf'] = dx


def mp202():
    sh = new('MP-202', 'UPPER DIE SHANK', scale='4:1', qty='1 per die set (4)',
             material='42CrMo4 Ø20 bar, QT 28–32 HRC', finish='Black oxide',
             notes=['Screw into the die body MP-201 (M10 THRU) with Loctite 243 until the Ø16 face seats; face square to axis 0.01.',
                    'V-groove takes the cone-point lock screw in the die holder MP-111 (groove centre 6.5 from the seating face).',
                    'Top end chamfer 1 × 45° (lead-in).'] + GEN)
    v, pos, Ltot = P.turned(sh, 130, 110, 0.25, [{'l': 9, 'd': 10, 'thread': 'M10'}, {'l': 15, 'd': 16}])
    gx = 9 + 6.5
    for s in (1, -1):
        v.line(gx - 1.5, s * 8, gx, s * 6.5); v.line(gx, s * 6.5, gx + 1.5, s * 8)
    v.hdim(0, -5, 9, -5, -14, text='9')
    v.hdim(9, -8, 24, -8, -14, text='15')
    v.hdim(9, 8, gx, 6.5, 14, text='6.5')
    v.vdim(-8, 21, 8, 21, 21, text='Ø16 g6')
    v.leader(4, 5, -6, -14, 'M10 – 6g')
    v.leader(gx, -6.5, 10, 16, '90° V-groove, 1.5 deep')
    v.text(12, 0, 'SIDE VIEW', 3.4, dy=56, weight='bold')


def mp203():
    X, Z = SHOWN[1], SHOWN[2]
    def extra(sh, v, vs):
        vd = View(sh, 345, 195, 0.2)
        pts = [(-6, 0), (-6, 6), (0, 6), (0, 1.0), (-0.3, 0.5), (-1.0, 0.25), (-1.5, 0.5), (-1.8, 0)]
        vd.poly(pts, 'sec')
        vd.text(-3, 0, 'DETAIL Y (5:1) working edge', 3.0, dy=12, weight='bold')
        vd.leader(-1.0, 0.25, -30, -8, 'concave lip R1, 1.5 wide × 0.5 deep\nall round the bottom face')
    die_sheet('MP-203', 'UPPER DIE PLUG', plug,
              [('A', 'X + 0.30  (plug length, ±0.01)', lambda x, z: x + 0.30), ('B', 'Z + 0.30  (plug width, ±0.01)', lambda x, z: z + 0.30)],
              ['Profile A × B with R4.15 corners: wire-EDM after hardening, ±0.01. Sliding fit in the upper frame opening (frame = plug + 0.05).',
               'Bottom (working) face flat 0.01, Ra 0.2, with lip per Detail Y. Fixing pattern 25 × 25 is the same for every size (Rev B).',
               'Height 14.5 ±0.01: sets the 5.5 mm recess between plug face and frame face.'],
              '1 per die set (4)',
              [('h', -(X + 0.3) / 2, (X + 0.3) / 2, (Z + 0.3) / 2, (Z + 0.3) / 2 + 9, 'A'),
               ('v', (Z + 0.3) / 2, -(Z + 0.3) / 2, (X + 0.3) / 2, (X + 0.3) / 2 + 18, 'B'),
               ('h', -FX, FX, -FX, -(Z + 0.3) / 2 - 9, '25'),
               ('v', FX, -FX, -FX, -(X + 0.3) / 2 - 18, '25'),
               ('l', (X + 0.3) / 2 - 2, (Z + 0.3) / 2 - 2, 26, -14, 'R4.15 (4×)', 0)],
              FIX_ROWS_PART('TOP'), extra=extra, dxfname='upper_plug')


def mp204():
    X, Z = SHOWN[1], SHOWN[2]
    def extra(sh, v, vs):
        for sx in (-1, 1):
            for sz in (-1, 1):
                u = sx * X / 4
                w0, w1 = sz * (Z + 0.35) / 2, sz * UZ / 2
                v.line(u - 2, w0, u - 2, w1, 'hid'); v.line(u + 2, w0, u + 2, w1, 'hid')
                v.cl_v(w0, w1, u)
        v.leader(X / 4, -UZ / 2, 30, 18, '4× M4 THRU, radial (spring plungers)\n3.5 from the BOTTOM face, at X = ±E/2')
        vd = View(sh, 345, 190, 0.2)
        pts = [(-8, 0), (-8, 8), (0, 8), (0, 1.65), (-0.6, 0)]
        vd.poly(pts, 'sec')
        vd.rect(-8, 3.5 - 2, 0, 3.5 + 2, 'ko'); vd.line(-8, 1.5, 0, 1.5); vd.line(-8, 5.5, 0, 5.5); vd.cl_h(-9, 1, 3.5)
        vd.text(-4, 0, 'DETAIL P (5:1) bottom inner edge', 3.0, dy=18, weight='bold')
        vd.text(1.5, 4, 'opening', 2.6, 'start')
        vd.leader(-0.3, 0.8, -30, 10, 'lead-in 0.6 × 20° all round, polished')
        vd.leader(-4, 5.5, -16, -10, 'M4 plunger hole, centre 3.5')
    die_sheet('MP-204', 'UPPER DIE FRAME', upframe,
              [('C', 'X + 0.35  (opening, +0.01/0)', lambda x, z: x + 0.35), ('D', 'Z + 0.35  (opening, +0.01/0)', lambda x, z: z + 0.35),
               ('E', 'X / 2  (pitch of the plungers in X)', lambda x, z: x / 2)],
              ['Rev B: outside 126 × 100 for every size. Opening C × D, R4.2, THRU: wire-EDM after hardening, lap Ra 0.2.',
               'Rev B: bottom inner edge lead-in 0.6 × 20° (Detail P), and 4 nylon-tip spring plungers M4 (protrude 0.2–0.3 into the opening) so the wrapped shell cannot drop out.',
               'Retention: 4 × Ø6.1 THRU, CBORE Ø10.5 × 10 from the BOTTOM. Spring pockets 4 × Ø10.5 × 10 from the TOP. Faces parallel 0.01.'],
              '1 per die set (4)',
              uni_dims() + [('h', -(X + .35) / 2, (X + .35) / 2, 0, -UZ / 2 - 17, 'C'),
                            ('v', (Z + .35) / 2, -(Z + .35) / 2, 0, -UX / 2 - 24, 'D')],
              [['R', RET, 'Ø6.1 THRU, CBORE Ø10.5 × 10 from the BOTTOM'], ['P', SPA, 'Ø10.5 × 10 deep from the TOP (spring pockets)'],
               ['N', '(±E/2, ±(D/2 … 50))', 'M4 radial THRU from the long sides, 3.5 above the bottom face']],
              extra=extra, sec_b=(RZ, 'Z = ±41.5'), dxfname='upper_frame')


def mp205():
    sh = new('MP-205', 'LOWER DIE SHOE A / B (UNIVERSAL)', scale='1:2 / 1:1', qty='A + B per set',
             material='C45 plate 12 mm (blank 155 × 125), faced to 10; or 6061-T6', finish='Black oxide; paint front edge band: A green, B red',
             notes=UNI_NOTES + ['Rev B: 150 × 120, the same for every size. A and B differ only in the table dowels (DA / DB) and the spring pockets (SA / SB).',
                                'Table dowels Ø8 m6 × 16 pressed into DA / DB from the BOTTOM, 8 protruding. A and B use different pitches so they cannot be swapped.',
                                'Thumb screws: M5 × 16 knurled, head Ø12 max (larger heads foul the frame corner or the stop block).',
                                'Lower springs: ISO 10243 Ø10 × 32 (A: 4 × green; B: 8 × red). Cavity 28 at rest (12.5 %), 20 at full travel (37.5 %). Replace every 250 000 strokes.'] + GEN)
    for i, which in enumerate(('A', 'B')):
        o, T, fs = shoe(which)
        v = View(sh, 62 + i * 112, 80, 2.0)
        v.segs(o)
        draw_plan_features(v, fs)
        v.cl_h(-80, 80, 0); v.cl_v(64, -64, 0)
        sh.text(v.P(-75, 0)[0], 128, 'SHOE %s — PLAN (TOP)' % which, 3.2, weight='bold')
        v.hdim(-75, -60, 75, -60, -72, text='150')
        v.vdim(60, -75, -60, -75, -86, text='120')
        dw = DOWEL[which]
        if which == 'A':
            v.hdim(dw[0][0], 30, dw[1][0], 30, 72, text='80')
            v.vdim(0, 0, 30, 40, 82, text='30')
        else:
            v.hdim(dw[0][0], -30, dw[1][0], -30, -82, text='60')
            v.vdim(-30, 30, 0, 30, 82, text='30')
    sh.text(20, 136, 'DA (shoe A): Ø8 H7 × 8 BOTTOM at (±40, −30) = back.  DB (shoe B): at (±30, +30) = front.', 2.8)
    o, T, fs = shoe('A')
    va = View(sh, 105, 160, 1.0)
    draw_section(va, solid_minus_thru((-75, 75), fs, 0), T, fs, 0, y0=0)
    va.vdim(0, 75, 10, 75, 83, text='10')
    va.text(0, 0, 'SECTION A–A, SHOE A, through Z = 0 (1:1)', 3.2, dy=9, weight='bold')
    ob, Tb, fsb = shoe('B')
    vb = View(sh, 105, 196, 1.0)
    draw_section(vb, solid_minus_thru((-75, 75), fsb, 16.25), Tb, fsb, 16.25, y0=0)
    vb.text(0, 0, 'SECTION, SHOE B, through Z = +16.25 (1:1)', 3.2, dy=9, weight='bold')
    rows = [['R', RET, 'M5 THRU (frame shoulder screws)', 'A, B'],
            ['F', '(±12.5, ±12.5)', 'Ø5.5 THRU, CBORE Ø9.5 × 5.5 BOTTOM', 'A, B'],
            ['G', '(±12.5, 0)', 'Ø5 H7 THRU (pedestal dowels)', 'A, B'],
            ['T', '(70, 55), (−70, −55)', 'Ø5.5 THRU (thumb screws)', 'A, B'],
            ['DA', '(±40, −30)', 'Ø8 H7 × 8 BOTTOM (table dowels)', 'A'],
            ['DB', '(±30, +30)', 'Ø8 H7 × 8 BOTTOM (table dowels)', 'B'],
            ['SA', SPA, 'Ø10.5 × 6 TOP (4 spring pockets)', 'A'],
            ['SB', SPB, 'Ø10.5 × 6 TOP (8 spring pockets)', 'B']]
    sh.text(236, 22, 'FEATURES (from the shoe centre, +Z = front)', 3.0, weight='bold')
    sh.table(236, 24, [('KEY', 11, 'middle'), ('POSITIONS (X, Z)', 50, 'start'), ('FEATURE', 92, 'start'), ('SHOE', 13, 'middle')], rows, size=2.5, rh=4.8)
    for which in ('A', 'B'):
        o, T, fs = shoe(which)
        dx = DXF(); dx.segs(o); feats_dxf(dx, fs); DXFS['MP-205_shoe_%s_universal.dxf' % which] = dx


def mp206():
    X, Z = SHOWN[1], SHOWN[2]
    die_sheet('MP-206', 'PICKUP PEDESTAL (DIE A)', pick_ped,
              [('A', 'X − 0.5  (±0.01)', lambda x, z: x - 0.5), ('B', 'Z − 0.5  (±0.01)', lambda x, z: z - 0.5)],
              ['The tinplate shell sits face-up over this pedestal. Top face flat 0.01, Ra 0.2; top edge R0.3.',
               'Height 21.8 ±0.02. Fixing pattern 25 × 25 is the same for every size (Rev B).'],
              '1 per die set (4)',
              [('h', -(X - .5) / 2, (X - .5) / 2, (Z - .5) / 2, (Z - .5) / 2 + 9, 'A'),
               ('v', (Z - .5) / 2, -(Z - .5) / 2, (X - .5) / 2, (X - .5) / 2 + 18, 'B'),
               ('h', -FX, FX, -FX, -(Z - .5) / 2 - 9, '25'),
               ('v', FX, -FX, -FX, -(X - .5) / 2 - 18, '25'),
               ('l', (X - .5) / 2 - 1.5, (Z - .5) / 2 - 1.5, 24, -12, 'R3.75 (4×)', 0)],
              FIX_ROWS_PART('BOTTOM'), dxfname='pickup_pedestal')


def mp207():
    X, Z = SHOWN[1], SHOWN[2]
    die_sheet('MP-207', 'PICKUP FRAME (DIE A)', lambda x, z: lowframe(x, z, 'A'),
              [('C', 'X + 0.6  (opening)', lambda x, z: x + 0.6), ('D', 'Z + 0.6  (opening)', lambda x, z: z + 0.6),
               ('G', 'X + 12.5  (film recess, 0.6 deep)', lambda x, z: x + 12.5), ('H', 'Z + 12.5  (film recess)', lambda x, z: z + 12.5)],
              ['Rev B: outside 126 × 100 for every size. Opening C × D, R4.3, THRU, wire-EDM; top inner edge R0.5. Film recess G × H, R6.25, 0.6 deep, Ra 0.8.',
               'Retention: 4 × Ø6.1 THRU, CBORE Ø10.5 × 14 from the TOP (ISO 7379 Ø6 × 12 into the shoe). Spring pockets 4 × Ø10.5 × 14 from the BOTTOM.',
               'Frame travel 8: it bottoms on the shoe.'],
              '1 per die set (4)',
              uni_dims() + [('h', -(X + .6) / 2, (X + .6) / 2, 0, -UZ / 2 - 17, 'C'),
                            ('v', (Z + .6) / 2, -(Z + .6) / 2, 0, -UX / 2 - 24, 'D'),
                            ('l', (X + 12.5) / 2, -20, 30, 34, 'film recess G × H, R6.25, 0.6 deep', 0)],
              [['R', RET, 'Ø6.1 THRU, CBORE Ø10.5 × 14 from the TOP'], ['P', SPA, 'Ø10.5 × 14 deep from the BOTTOM (spring pockets)']],
              sec_b=(RZ, 'Z = ±41.5'), dxfname='pickup_frame')


def mp208():
    X, Z = SHOWN[1], SHOWN[2]
    die_sheet('MP-208', 'CRIMP PEDESTAL (DIE B)', crimp_ped,
              [('A', 'X − 4.5  (±0.02)', lambda x, z: x - 4.5), ('B', 'Z − 4.5  (±0.02)', lambda x, z: z - 4.5)],
              ['Smaller than the back plate (X − 1.4) so the shell edge can roll under the back. Top face flat 0.01, Ra 0.2; top edge R0.5.',
               'Height 17.0 ±0.02. Fixing pattern 25 × 25 is the same for every size (Rev B).'],
              '1 per die set (4)',
              [('h', -(X - 4.5) / 2, (X - 4.5) / 2, (Z - 4.5) / 2, (Z - 4.5) / 2 + 9, 'A'),
               ('v', (Z - 4.5) / 2, -(Z - 4.5) / 2, (X - 4.5) / 2, (X - 4.5) / 2 + 18, 'B'),
               ('h', -FX, FX, -FX, -(Z - 4.5) / 2 - 9, '25'),
               ('v', FX, -FX, -FX, -(X - 4.5) / 2 - 18, '25'),
               ('l', (X - 4.5) / 2 - 1, (Z - 4.5) / 2 - 1, 24, -12, 'R2.5 (4×)', 0)],
              FIX_ROWS_PART('BOTTOM'), dxfname='crimp_pedestal')


def mp209():
    X, Z = SHOWN[1], SHOWN[2]
    def extra(sh, v, vs):
        for s in (-1, 1):
            u = s * (X + 0.45) / 2
            vs.line(u, 18 - 1.2, u + s * 0.69, 18)
        vs.leader((X + 0.45) / 2 + 0.4, 17.6, 18, -10, '1.2 × 30° lead-in, all round, polished Ra 0.2')
    die_sheet('MP-209', 'CRIMP FRAME (DIE B)', lambda x, z: lowframe(x, z, 'B'),
              [('C', 'X + 0.45  (opening, +0.01/0)', lambda x, z: x + 0.45), ('D', 'Z + 0.45  (opening, +0.01/0)', lambda x, z: z + 0.45)],
              ['Rev B: outside 126 × 100 for every size. Opening C × D, R4.2, THRU, wire-EDM, lap Ra 0.2. Top lead-in 1.2 × 30°: folds the film under the shell edge.',
               'Retention as MP-207. Spring pockets 8 × Ø10.5 × 14 from the BOTTOM. A drop of silicone release on the lead-in stops laser-printed film slipping.',
               'Rev B: forming edge must have no EDM recast layer (2 skim cuts + re-temper): recast is where crimp frames crack.'],
              '1 per die set (4)',
              uni_dims() + [('h', -(X + .45) / 2, (X + .45) / 2, 0, -UZ / 2 - 17, 'C'),
                            ('v', (Z + .45) / 2, -(Z + .45) / 2, 0, -UX / 2 - 24, 'D'),
                            ('v', 16.25, -16.25, RX, UX / 2 + 24, '32.5'),
                            ('h', -22.5, 22.5, RZ, UZ / 2 + 17, '45')],
              [['R', RET, 'Ø6.1 THRU, CBORE Ø10.5 × 14 from the TOP'], ['P', SPB, 'Ø10.5 × 14 deep from the BOTTOM (8 spring pockets)']],
              extra=extra, sec_b=(RZ, 'Z = ±41.5'), dxfname='crimp_frame')


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
        for t in [k / 20.0 for k in range(21)]:
            u, w = u0 + (u1 - u0) * t, w0 + (w1 - w0) * t
            zz, yy = u * c - w * s, 234.5 + u * s + w * c
            if abs(zz - z) < 6 and w < 0:
                best = yy if best is None else min(best, yy)
    return best


def mp001():
    sh = new('MP-001', 'GENERAL ARRANGEMENT & HEIGHTS', scale='1:3 / 1:5', qty='—',
             material='—', finish='—',
             notes=['Shown with the handle UP (open), die table at "B under ram", die set 6363 (Rev B universal die outers 126 × 100). Heights from the bench top.',
                    'Toggle: crank O→A 40, link A→B 60, grip centre 320 from O (Rev A 290). Handle 65° → 3° above horizontal. Force gain 6.6 at the start, 34.6 at the end of the stroke.',
                    'Ram stroke 38.9. Dies meet after 26.0; working travel 12.9. Pickup stroke stops at 35.5. Station pilot MP-120 enters the table at 20.0, before the dies meet.',
                    'Open stop: 2 urethane bumpers on the ram top. Closed stop: adjustable M10 × 1 screw + urethane cap on the front column top, set so the lever rests at 3°.',
                    'Rev B: one-piece lever (MP-115 deleted); pin O Ø16; PTFE-composite bushings at O, A, B; return springs 60 N / 225 N; station pilot; 15 mm base on rubber pads.',
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
    box(-50, 50, 48, 66)
    box(-(Z - 4.5) / 2, (Z - 4.5) / 2, 40, 57, 'hid')
    box(-50, 50, 92, 106)
    box(-(Z + 0.3) / 2, (Z + 0.3) / 2, 106, 112)
    box(-50, 50, 112, 122)
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
    H = [(0, 'bench'), (3, 'base underside (3 mm pads)'), (18, 'base top'), (30, 'die table top'), (40, 'shoe top'), (66, 'lower die top'),
         (92, 'upper die bottom'), (134, 'ram bottom'), (164, 'ram top'), (176, 'crown bottom'), (201, 'crown top'), (234.5, 'pivot O'),
         (324, 'return-rod top'), (round(gtop), 'grip top, handle up')]
    sh.text(16, 20, 'KEY HEIGHTS, handle up (mm from bench)', 2.8, weight='bold')
    sh.table(16, 22, [('HEIGHT', 18, 'end'), ('LEVEL', 46, 'start')], [[fmt(y), t] for (y, t) in reversed(H)], size=2.6, rh=4.4)
    v.text(385, 212, 'handle down (phantom)', 2.6, 'end')
    v.text(100, 0, 'SIDE ELEVATION (viewed from the left; front →)', 3.4, dy=10, weight='bold')
    left = [(-120, 12, 210, '101'), (-105, 80, 192, '107'), (-65, 100, 180, '120'), (-100, 149, 168, '109'), (-12, 175, 158, '110'),
            (-100, 188, 148, '108'), (-60, 262, 128, '118')]
    right = [(60, 24, 206, '105'), (55, 35, 196, '205'), (45, 57, 186, '209'), (44, 99, 176, '204'), (44, 117, 166, '201'), (22, 128, 156, '111'),
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
        fb(cx - 75, cx + 75, 30, 40); fb(cx - UX / 2, cx + UX / 2, 48, 66)
    fb(-UX / 2, UX / 2, 92, 106); fb(-UX / 2, UX / 2, 112, 122); fb(-25, 25, 123, 134)
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
                      'Rev B die sets: bodies MP-201 and shoes MP-205 are common to all sizes. Plugs, upper frames, pedestals and lower frames are tabulated for 5050, 6363, 5380, 6590.',
                      'DXF profiles are supplied for cutting and wire-EDM. If a DXF and a drawing disagree, the drawing governs. Bought parts are in the build pack BOM.',
                      'Rev B (2026-10-27), failure-mode review: one-piece lever (MP-115 deleted), pin O Ø16 in PTFE-composite bushings, stronger return springs, station pilot MP-120 (new), universal die outers, A2 dies re-tempered after EDM, 15 mm base on pads, 16 kN design load.',
                      'Prove the die fits on a 7075 aluminium set before cutting tool steel.'])
    P.SHEETS.insert(0, sh)
    sh.text(20, 30, 'MagPress M4', 12, weight='bold')
    sh.text(20, 40, 'Manual photo fridge-magnet press · manufacturing drawing set · Rev B', 4.2)
    sh.text(20, 47, '4 swappable die sets: 50 × 50, 63.5 × 63.5, 53 × 80, 65 × 90 mm', 3.2)
    cols = [('DRG NO.', 22, 'start'), ('TITLE', 70, 'start'), ('QTY', 36, 'start'), ('SHEET', 14, 'middle')]
    sh.text(20, 58, 'DRAWING LIST', 3.2, weight='bold')
    sh.table(20, 60, cols, listing, size=2.5, rh=4.85)
    if img_b64:
        sh.add('<image x="178" y="18" width="111" height="200" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,%s"/>' % img_b64)
        sh.rect(178, 18, 111, 200, 'box')
    if img2_b64:
        sh.add('<image x="293" y="18" width="111" height="200" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,%s"/>' % img2_b64)
        sh.rect(293, 18, 111, 200, 'box')
    if img_b64 or img2_b64:
        sh.text(180, 224, 'Reference renderings (Rev B): assembled, handle up (left); exploded (right). Not for measurement.', 2.6, italic=True)
    return sh
