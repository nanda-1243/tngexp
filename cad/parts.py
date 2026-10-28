"""MagPress M4 Rev B part drawings. Coordinates: x right, y up, z toward the operator (front).
Plan views: u = x, w = -z (front at the bottom of the view) unless stated."""
import math
from draft import *


SIZES = [('5050', 50.0, 50.0), ('6363', 63.5, 63.5), ('5380', 80.0, 53.0), ('6590', 90.0, 65.0)]   # code, X (along table), Z
SIZE_LABEL = {'5050': '50 × 50', '6363': '63.5 × 63.5', '5380': '53 × 80', '6590': '65 × 90'}
SHOWN = ('6590', 90.0, 65.0)
GEN = ['General tolerances ISO 2768-mK; fits per ISO 286; threads ISO metric 6H/6g.',
       'Break all sharp edges 0.3 × 45° unless stated. Remove all burrs.']
PAP = 'PTFE-composite plain bushing (DU / PAP type)'

SHEETS = []
DXFS = {}


def new(no, title, **kw):
    sh = Sheet(no, title, **kw)
    SHEETS.append(sh)
    return sh


def hole_table(sh, x, y, rows, title='HOLE TABLE', zname='Z'):
    sh.text(x, y - 1.5, title, 3.0, weight='bold')
    cols = [('HOLE', 14, 'middle'), ('X', 18, 'end'), (zname, 18, 'end'), ('DESCRIPTION', 120, 'start')]
    return sh.table(x, y, cols, [[r[0], fmt(r[1]), fmt(r[2]), r[3]] for r in rows], size=2.6, rh=4.4)


def lead_to(v, u, w, tx, ty, text, r=0, size=2.8):
    x, y = v.P(u, w)
    a = math.atan2(ty - y, tx - x)
    v.leader(u, w, tx - x, ty - y, text, size=size, on_circle_r=r if r else None, ang=a if r else None)


def axes_glyph(v, u, w, xlab='X', zlab='Z', down=True):
    x, y = v.P(u, w)
    v.sh.line(x, y, x + 10, y, 'vis'); v.sh.arrow(x + 10, y, 0); v.sh.text(x + 11.5, y + 1, xlab, 2.6)
    v.sh.line(x, y, x, y + (10 if down else -10), 'vis'); v.sh.arrow(x, y + (10 if down else -10), math.pi / 2 if down else -math.pi / 2)
    v.sh.text(x + 1.5, y + (13 if down else -12), zlab, 2.6)
    v.sh.circle(x, y, 1.2, 'vis')


# =====================================================================================
# MP-101 BASE PLATE (Rev B: 15 mm S355, bench-mount holes, pilot clearance, QPQ slide area)
# =====================================================================================
def base_outline():
    return [L(-50, -340, 50, -340), A(50, -320, 20, 270, 360), L(70, -320, 70, -140), A(80, -140, 10, 90, 180),
            L(80, -130, 220, -130), A(220, -120, 10, 270, 360), L(230, -120, 230, 120), A(220, 120, 10, 0, 90),
            L(220, 130, -220, 130), A(-220, 120, 10, 90, 180), L(-230, 120, -230, -120), A(-220, -120, 10, 180, 270),
            L(-220, -130, -80, -130), A(-80, -140, 10, 0, 90), L(-70, -140, -70, -320), A(-50, -320, 20, 180, 270)]


RAIL_F = [-215, -160, -100, -40, 40, 100, 160, 215]
RAIL_B = [-215, -160, -110, -92, -40, 40, 92, 110, 160, 215]


def base_feats():
    f = [feat(0, -105, 'hole', d=20, thru=True, cb=(33, 8.5), cbside='bot', label='C1'),
         feat(0, 105, 'hole', d=20, thru=True, cb=(33, 8.5), cbside='bot', label='C2')]
    n = 1
    for x in RAIL_F:
        f.append(feat(x, 82, 'tap', m='M5', thru=True, label='R%d' % n)); n += 1
    for x in RAIL_B:
        f.append(feat(x, -82, 'tap', m='M5', thru=True, label='R%d' % n, ldy=-1.6 if x not in (-92, 92) else 4)); n += 1
    n = 1
    for (x, z) in [(-200, -110), (200, -110), (-200, 110), (200, 110), (-40, 300), (40, 300)]:
        f.append(feat(x, z, 'hole', d=9, thru=True, label='M%d' % n)); n += 1
    f.append(feat(-80, 45, 'spot', d=4, depth=1.5, label='D1'))
    f.append(feat(80, 45, 'spot', d=4, depth=1.5, label='D2'))
    f.append(feat(0, -65, 'hole', d=12, depth=8, side='top', label='PL'))
    return f


def mp101():
    sh = new('MP-101', 'BASE PLATE', scale='1:2.5', qty='1',
             material='S355J2 steel plate 20 mm, profile cut, faced to 15.0',
             finish='Slide area: QPQ nitrocarburize (prototype: black oxide + oil). Rest: black powder coat, bores masked',
             notes=['Rev B: 15 mm S355 (was 12 S235). At the 16 kN design load: 112 MPa, 0.26 mm (Rev A: 175 MPa, 0.51 mm). 0.08 mm at a normal 5 kN stroke.',
                    'Face both sides to 15.0 ±0.1. Flatness 0.05 over the slide area X ±230 × Z ±75, Ra 1.6.',
                    'C1/C2 Ø20 H7 at 210.00 ±0.01: same datum and program as crown MP-108 and ram MP-109. CBORE Ø33 × 8.5 from the BOTTOM (Rev C.1, was 4.5): the M10 × 16 DIN 7984 clamp screw and Ø32 × 2.5 washer sit flush with the underside.',
                    'M1–M6: Ø9 THRU bench-mounting holes (M8). Underside: five 3 mm adhesive rubber pads Ø24 at (±200, ±80) and (0, 300).',
                    'PL: Ø12 × 8 deep clearance for the station pilot MP-120. D1/D2: Ø4 × 90° spots, 1.5 deep (table detents).',
                    'Hole positions from datum O (midpoint of C1–C2). X to the right; Z toward the front (tongue).'] + GEN)
    v = View(sh, 125, 80, 2.5)
    v.segs(base_outline())
    fs = base_feats()
    draw_plan_features(v, fs)
    v.cl_h(-240, 240, 0); v.cl_v(140, -350, 0)
    axes_glyph(v, 0, 0)
    v.text(0, 0, 'O', 3.0, 'start', dx=-5, dy=-1.8, weight='bold')
    v.hdim(-230, 120, 230, 120, 152)
    v.hdim(-70, -330, 70, -330, -362)
    v.vdim(130, -220, -130, -220, -252)
    v.vdim(130, -220, -340, -60, -270)
    v.vdim(-130, 70, -340, 70, 100)
    v.vdim(105, 0, -105, 0, -45, text='210 ±0.01')
    v.leader(220, 120, 8, -10, '4× R10', on_circle_r=0)
    v.leader(64.14, -334.14, 10, 6, '2× R20')
    v.leader(80, -140, 22, 4, '2× R10 fillet', on_circle_r=0)
    v.leader(0, -105, -26, -18, 'C1, C2: Ø20 H7 THRU\nCBORE Ø33 × 8.5 FROM BOTTOM', on_circle_r=10)
    v.text(-150, -320, 'PLAN (TOP FACE)', 3.4, weight='bold')
    rows = []
    for f in fs:
        lb = f['label']
        if lb.startswith('C'): d = 'Ø20 H7 THRU; CBORE Ø33 × 8.5 BOTTOM'
        elif lb.startswith('R'): d = 'M5 THRU (rail screws)'
        elif lb.startswith('M'): d = 'Ø9 THRU (bench mounting, M8)'
        elif lb == 'PL': d = 'Ø12 × 8 deep (pilot clearance, Rev E)'
        else: d = 'Ø4 × 90° spot, 1.5 deep (detent)'
        rows.append((lb, f['x'], f['z'], d))
    hole_table(sh, 238, 18, rows)
    vd = View(sh, 300, 208, 1.0)
    T = 15
    draw_section(vd, [(-35, 35)], T, [feat(0, 0, 'hole', d=20, thru=True, cb=(33, 8.5), cbside='bot')], 0, y0=0)
    vd.cl_v(-4, T + 4, 0)
    vd.hdim(-10, T, 10, T, T + 7, text='Ø20 H7')
    vd.hdim(-16.5, 0, 16.5, 0, -6, text='Ø33')
    vd.vdim(0, 35, T, 35, 43, text='15')
    vd.vdim(0, -16.5, 8.5, -16.5, -44, text='8.5')
    vd.text(0, 0, 'DETAIL SECTION THROUGH C1/C2  (1:1)', 3.0, dy=10, weight='bold')
    dx = DXF(); dx.segs(base_outline()); feats_dxf(dx, fs); DXFS['MP-101_base_plate.dxf'] = dx


# =====================================================================================
# MP-102 GUIDE RAIL, MP-103 KEEPER, MP-104 STOP BLOCK, MP-106 STOP PIN (unchanged in Rev B)
# =====================================================================================
def mp102():
    sh = new('MP-102', 'GUIDE RAIL', scale='1:2', qty='2 (1 × -F, 1 × -B)',
             material='C45 bright flat 16 × 14, ground to 14 × 12.05',
             finish='Black oxide; ground faces oiled',
             notes=['Height 12.05 ±0.01: equal to die table MP-105 thickness + 0.05 running clearance. Grind both rails together.',
                    'Ground faces: top, bottom and inner face (faces the die table). Inner face straight within 0.02 over 460.',
                    'Variant -F: front rail, 8 holes. Variant -B: back rail, 10 holes (includes stop-block screws).',
                    'Holes Ø5.5 THRU on the rail centreline; hole X positions measured from the rail centre.'] + GEN)
    for (var, xs, oy) in [('-F (front)', RAIL_F, 60), ('-B (back)', RAIL_B, 150)]:
        v = View(sh, 150, oy, 2.0)
        v.rect(-230, -7, 230, 7)
        for x in xs:
            v.circle(x, 0, 2.75); v.cmark(x, 0, 2.75)
        v.cl_h(-236, 236, 0)
        v.text(-230, 7, 'MP-102%s  TOP VIEW' % var.split()[0], 3.2, 'start', dy=-9, weight='bold')
        v.hdim(-230, -7, 230, -7, -24)
        v.vdim(7, 230, -7, 230, 238, text='14')
        vf = View(sh, 150, oy + 30, 2.0)
        vf.rect(-230, 0, 230, 12.05)
        for x in xs:
            vf.line(x - 2.75, 0, x - 2.75, 12.05, 'hid'); vf.line(x + 2.75, 0, x + 2.75, 12.05, 'hid')
        vf.vdim(0, 230, 12.05, 230, 238, text='12.05 ±0.01')
        sh.text(300, oy - 6, 'Hole X positions (from rail centre), all Ø5.5 THRU:', 2.8, weight='bold')
        sh.text(300, oy, ', '.join(fmt(x) for x in xs), 2.8)
    for (tag, xs) in (('F_guide_rail_front', RAIL_F), ('B_guide_rail_back', RAIL_B)):
        dx = DXF(); dx.segs(rrect(0, 0, 460, 14, 0)); [dx.segs([C(x, 0, 2.75)], 'HOLES') for x in xs]; DXFS['MP-102-%s.dxf' % tag] = dx


def mp103():
    sh = new('MP-103', 'KEEPER STRIP (GIB)', scale='1:2', qty='2 (1 × -F, 1 × -B)',
             material='C45 bright flat 20 × 4', finish='Black oxide',
             notes=['Sits on top of the guide rail and overlaps the die table edge by 5 mm (inner edge).',
                    'Countersunk holes: Ø5.5 THRU, 90° countersink to Ø11.5 (M5 ISO 10642, head Ø11.2), from top; heads 0.15 below the surface. Rev E: Ø10.4 left the heads 0.4 proud. Screws M5 × 30 (Rev E, was × 20) for full thread in the base.',
                    'Variant -B: four plain Ø5.5 holes at X ±92 and ±110 for the stop-block screws (no countersink).',
                    'Hole line 12.0 from the inner edge. Hole X positions measured from the strip centre.'] + GEN)
    for (var, csk, plain, oy) in [('-F (front)', RAIL_F, [], 60), ('-B (back)', [-215, -160, -40, 40, 160, 215], [-110, -92, 92, 110], 150)]:
        v = View(sh, 150, oy, 2.0)
        v.rect(-230, -10, 230, 10)
        for x in csk:
            v.circle(x, -2, 2.75); v.circle(x, -2, 5.2); v.cmark(x, -2, 5.2)
        for x in plain:
            v.circle(x, -2, 2.75); v.cmark(x, -2, 2.75)
        v.text(-230, 10, 'MP-103%s  TOP VIEW  (inner edge at bottom)' % var.split()[0], 3.2, 'start', dy=-9, weight='bold')
        v.hdim(-230, -10, 230, -10, -26)
        v.vdim(10, 230, -10, 230, 238, text='20')
        v.vdim(-2, -230, -10, -230, -240, text='12')
        vf = View(sh, 150, oy + 32, 2.0)
        vf.rect(-230, 0, 230, 4)
        vf.vdim(0, 230, 4, 230, 238, text='4')
        sh.text(300, oy - 6, 'Countersunk (M5 ISO 10642):', 2.8, weight='bold')
        sh.text(300, oy, ', '.join(fmt(x) for x in csk), 2.8)
        if plain:
            sh.text(300, oy + 6, 'Plain Ø5.5 THRU:', 2.8, weight='bold')
            sh.text(300, oy + 12, ', '.join(fmt(x) for x in plain), 2.8)


def mp104():
    sh = new('MP-104', 'STATION STOP BLOCK', scale='2:1', qty='2',
             material='C45 bright 30 × 16 flat', finish='Black oxide',
             notes=['Bolted through keeper MP-103-B and rail MP-102-B into the base with 2 × M5 × 35 ISO 4762 + threadlocker.',
                    'Stop screw: M6 × 0.75 × 40 hex screw + thin lock nut (bought). Coarse stop only: the pilot MP-120 sets the exact station position. Rev E: set each stop 0.3 PAST its station, so the pilot always pulls the table back, never forward against the stop.',
                    'The 7 mm overhang (Z 20–27) sits above the die table; the table stop pin MP-106 hits the screw tip.',
                    'Z measured from the back face (the face over the keeper).'] + GEN)
    v = View(sh, 90, 50, 0.5)
    v.rect(-15, 0, 15, -27)
    for x in (-9, 9):
        v.circle(x, -8, 2.75); v.circle(x, -8, 4.75); v.cmark(x, -8, 4.75)
    v.line(-15, -22 - 2.6, 15, -22 - 2.6, 'hid'); v.line(-15, -22 + 2.6, 15, -22 + 2.6, 'hid'); v.cl_h(-18, 18, -22)
    v.text(0, 0, 'TOP VIEW', 3.2, dy=-14, weight='bold')
    v.hdim(-15, 0, 15, 0, 9)
    v.hdim(-9, -8, 9, -8, -40, text='18')
    v.vdim(0, -15, -27, -15, -24, text='27')
    v.vdim(0, 15, -8, 15, 22, text='8')
    v.vdim(0, 15, -22, 15, 30, text='22')
    v.leader(9, -8, 18, -16, '2× Ø5.5 THRU\nCBORE Ø9.5 × 5.5', on_circle_r=4.75)
    vf = View(sh, 90, 150, 0.5)
    vf.rect(-15, 0, 15, 16)
    for x in (-9, 9):
        vf.line(x - 2.75, 0, x - 2.75, 10.5, 'hid'); vf.line(x + 2.75, 0, x + 2.75, 10.5, 'hid')
        vf.line(x - 4.75, 10.5, x - 4.75, 16, 'hid'); vf.line(x + 4.75, 10.5, x + 4.75, 16, 'hid'); vf.line(x - 4.75, 10.5, x + 4.75, 10.5, 'hid')
    vf.line(-15, 8 - 2.6, 15, 8 - 2.6, 'hid'); vf.line(-15, 8 + 2.6, 15, 8 + 2.6, 'hid'); vf.cl_h(-18, 18, 8)
    vf.text(0, 0, 'FRONT VIEW (from the die table side)', 3.2, dy=14, weight='bold')
    vf.vdim(0, -15, 16, -15, -24, text='16')
    vf.vdim(0, 15, 8, 15, 22, text='8')
    vs = View(sh, 230, 150, 0.5)
    vs.rect(0, 0, 27, 16)
    vs.circle(22, 8, MINOR['M6x0.75'] / 2); vs.thread_arc(22, 8, 3.0); vs.cmark(22, 8, 3)
    vs.text(13.5, 0, 'SIDE VIEW', 3.2, dy=14, weight='bold')
    vs.hdim(0, 16, 27, 16, 25)
    vs.leader(22, 8, 20, -22, 'M6 × 0.75 THRU (along X)', on_circle_r=3)
    vs.hdim(0, 0, 22, 0, -9, text='22')


def mp106():
    sh = new('MP-106', 'DIE TABLE STOP PIN', scale='4:1', qty='1',
             material='C45 Ø8 bright bar', finish='Harden 45–50 HRC; black oxide',
             notes=['Screwed into the die table (MP-105, hole S) with Loctite 243.', 'Contact face Ø6 must be square to the axis within 0.05.'] + GEN)
    v = View(sh, 120, 110, 0.25)
    v.rect(0, -3, 16, 3); v.rect(-6, -2, 0, 2)
    v.line(-6, -1.65, 0, -1.65, 'thin'); v.line(-6, 1.65, 0, 1.65, 'thin')
    v.cl_h(-9, 19, 0)
    v.hdim(0, 3, 16, 3, 8)
    v.hdim(-6, 2, 0, 2, 8, text='6')
    v.vdim(-3, 8, 3, 8, 21, text='Ø6')
    v.leader(-3, -2, -8, 12, 'M4 × 6')
    v.text(5, -3, 'SIDE VIEW', 3.2, dy=24, weight='bold')


# =====================================================================================
# MP-105 DIE TABLE (Rev B: pilot holes, shoe pattern for 142 × 120 shoes)
# =====================================================================================
def table_feats():
    f = []
    n = 1
    for cx in (-80, 80):
        for (x, z) in ((-35, -35), (35, -35), (-35, 35), (35, 35)):
            f.append(feat(cx + x, z, 'hole', d=5.5, thru=True, csk=11.5, side='bot', label='F%d' % n)); n += 1
    n = 1
    for cx in (-80, 80):
        for x in (-45, 45):
            f.append(feat(cx + x, 0, 'hole', d=6, thru=True, label='G%d' % n, ldy=4)); n += 1
    f += [feat(0, -66, 'tap', m='M4', depth=8, label='S'), feat(0, 45, 'tap', m='M6', thru=True, label='BP'),
          feat(-80, -65, 'hole', d=10, thru=True, label='PA', ldy=4), feat(80, -65, 'hole', d=10, thru=True, label='PB', ldy=4),
          feat(-163, 0, 'tap', m='M5', depth=8, label='K1'), feat(163, 0, 'tap', m='M5', depth=8, label='K2')]
    return f


def mp105():
    sh = new('MP-105', 'DIE TABLE (SLIDE)', scale='1:2', qty='1',
             material='EN AW-6061-T6 plate 15 mm, faced to 12.00',
             finish='Hard anodise 25 µm, gold, PTFE-sealed',
             notes=['Thickness 12.00 ±0.01 and flat within 0.03 after anodising. Guide rails MP-102 are 12.05.',
                    'PA/PB Ø10 H8 THRU take the station pilot MP-120 (Rev E: Ø10, was Ø8), ±0.02 to the base dowel holes G. The station bases MP-205 are fixed for good (F, G).',
                    'F1–F8: Ø5.5 THRU, 90° countersink Ø11.5 from the BOTTOM (M5 × 20 ISO 10642, 0.15 below flush). G1–G4: Ø6 H7 THRU, drilled and reamed in place with the station base aligned (base dowels).',
                    'S: M4 × 8 (stop pin MP-106). BP: M6 THRU (ball plunger). K1/K2: M5 × 8 in the top face (Ø14 push knobs; Rev C.1, the Rev C Ø24 end-face knobs reached below the table into the base).',
                    'Hole positions from the table centre. Station centres at X = −80 (A) and +80 (B), Z = 0.',
                    'Long edges: 0.5 × 45° chamfer only (they run against the rails).'] + GEN)
    v = View(sh, 115, 65, 2.0)
    v.segs(rrect(0, 0, 340, 150, 0))
    fs = table_feats()
    draw_plan_features(v, fs)
    v.cl_h(-175, 175, 0); v.cl_v(80, -80, 0)
    for x in (-80, 80):
        v.cl_v(70, -70, x); v.text(x, 0, 'STATION ' + ('A' if x < 0 else 'B'), 2.6, dy=-2)
    axes_glyph(v, 0, 0)
    v.hdim(-170, 75, 170, 75, 95)
    v.vdim(75, -170, -75, -170, -190)
    v.hdim(-80, 75, 80, 75, 85, text='160')
    v.text(0, -75, 'PLAN', 3.4, dy=12, weight='bold')
    rows = []
    for f in fs:
        lb = f['label']
        if lb.startswith('F'): d = 'Ø5.5 THRU, CSK Ø11.5 × 90° BOTTOM (base screw)'
        elif lb.startswith('G'): d = 'Ø6 H7 × 10 deep (base dowel)'
        elif lb == 'S': d = 'M4 × 8 deep (stop pin MP-106)'
        elif lb == 'BP': d = 'M6 THRU (ball plunger)'
        elif lb.startswith('K'): d = 'M5 × 8 deep (push knob Ø14, top face)'
        else: d = 'Ø10 H8 THRU (station pilot), ±0.02'
        rows.append((lb, f['x'], f['z'], d))
    hole_table(sh, 238, 18, rows)
    v.section_mark(-178, 65, 178, 65, 'A', flip=False)
    vs = View(sh, 115, 185, 2.0)
    draw_section(vs, solid_minus_thru((-170, 170), fs, -65), 12, fs, -65, y0=0)
    vs.vdim(0, 170, 12, 170, 182, text='12 ±0.01')
    vs.text(0, 0, 'SECTION A–A (through the pilot holes)', 3.4, dy=12, weight='bold')
    dx = DXF(); dx.segs(rrect(0, 0, 340, 150, 0)); feats_dxf(dx, fs); DXFS['MP-105_die_table.dxf'] = dx


# =====================================================================================
# Turned parts
# =====================================================================================
def turned(sh, ox, oy, scale, segs):
    v = View(sh, ox, oy, scale)
    x = 0.0
    pos = []
    for s in segs:
        r = s['d'] / 2.0
        v.line(x, r, x + s['l'], r); v.line(x, -r, x + s['l'], -r)
        if s.get('thread'):
            mr = MINOR[s['thread']] / 2.0
            v.line(x, mr, x + s['l'], mr, 'thin'); v.line(x, -mr, x + s['l'], -mr, 'thin')
        pos.append((x, x + s['l'], r))
        x += s['l']
    for i, (a, b, r) in enumerate(pos):
        rp = pos[i - 1][2] if i > 0 else 0
        v.line(a, -max(r, rp), a, max(r, rp))
    v.line(x, -pos[-1][2], x, pos[-1][2])
    v.cl_h(-5, x + 5, 0)
    return v, pos, x


def tapped_end(v, xend, m, thread_depth, inward=1):
    mn, mj = MINOR[m] / 2, MAJOR[m] / 2
    drill = thread_depth + MAJOR[m] * 0.4
    e1 = xend + inward * thread_depth; e2 = xend + inward * drill
    v.line(xend, mn, e2, mn, 'hid'); v.line(xend, -mn, e2, -mn, 'hid')
    v.line(xend, mj, e1, mj, 'hid'); v.line(xend, -mj, e1, -mj, 'hid')
    v.line(e1, -mj, e1, mj, 'hid')
    tip = e2 + inward * mn * 0.6
    v.line(e2, mn, tip, 0, 'hid'); v.line(e2, -mn, tip, 0, 'hid')


def mp107():
    sh = new('MP-107', 'COLUMN', scale='1:1', qty='2',
             material='100Cr6 (52100 / GCr15) Ø30 bar',
             finish='Ø25 section: induction harden 58–62 HRC, hard chrome 8–12 µm, ground to h6, Ra 0.2',
             notes=['Ø25 h6 length 158.00 ±0.02; the two columns matched within 0.01 (sets crown parallelism).',
                    'Bottom spigot Ø20 p6 × 6.2 in the 6.5 bore below the base counterbore: the clamp washer bears on the base, not on the spigot end (Rev E, was 6.5). Clamp from below: M10 × 16 DIN 7984 + hardened washer Ø32 × 2.5, 40 N·m; head flush with the base underside.',
                    'Ø20 h6 top section 24.5 long passes through the 25 crown (Ø20 H7), so the nut clamps the crown, not the column (Rev E, was 25). Nut M16 × 1.5 + Nord-Lock washer on top, 100 N·m; thread 20 long (was 16).',
                    'Rev E: no tapped hole in the top end (it left a 2 mm wall under the nut thread). The handle stop is on a post on the crown, MP-121.',
                    'Shoulders square to the axis within 0.01. Run-out of all diameters 0.01 to the Ø25 axis.',
                    'Chamfers: ends 1 × 45°; steps 0.5 × 45°. Thread undercut DIN 76-A at the M16 thread end.'] + GEN)
    segs = [{'l': 6.2, 'd': 20}, {'l': 158, 'd': 25}, {'l': 24.5, 'd': 20}, {'l': 20, 'd': 16, 'thread': 'M16x1.5'}]
    v, pos, Ltot = turned(sh, 95, 90, 1.0, segs)
    tapped_end(v, 0, 'M10', 15, +1)
    v.vdim(-10, 3.25, 10, 3.25, 3.25, text='Ø20 p6')
    v.vdim(-12.5, 80, 12.5, 80, 80, text='Ø25 h6')
    v.vdim(-10, 177, 10, 177, 177, text='Ø20 h6')
    v.leader(197, 8, 12, -16, 'M16 × 1.5 – 6g')
    v.hdim(0, -10, 6.2, -10, -22, text='6.2')
    v.hdim(6.2, -12.5, 164.2, -12.5, -22, text='158 ±0.02')
    v.hdim(164.2, -10, 188.7, -10, -22, text='24.5')
    v.hdim(188.7, -8, 208.7, -8, -22, text='20')
    v.hdim(0, -10, 208.7, -8, -32, text='208.7')
    v.leader(4, 0, -14, 22, 'M10 × 15 deep\n(drill Ø8.5 × 19)')
    v.text(100, 0, 'SIDE VIEW', 3.4, dy=48, weight='bold')


def pin_sheet(no, title, Ltot, faces, qty, d=12.0, gd=11.5, ring='DIN 471 – 12'):
    sh = new(no, title, scale='2:1', qty=qty,
             material='100Cr6 (GCr15) bar, or hardened ground dowel stock Ø%s g6' % fmt(d),
             finish='Harden 58–62 HRC, grind Ø%s g6, Ra 0.4. Runs in PTFE-composite bushings: no grease' % fmt(d),
             notes=['Retaining-ring grooves for %s: groove Ø%s h12, width 1.1 H13, both ends.' % (ring, fmt(gd)),
                    'Ends 0.5 × 45° chamfer. Groove inner edge at %s from the pin centre (bearing faces at ±%s).' % (fmt(faces + 0.1), fmt(faces))] + GEN)
    h = Ltot / 2.0
    g0 = faces + 0.1
    segs = [{'l': h - g0 - 1.1, 'd': d}, {'l': 1.1, 'd': gd}, {'l': 2 * g0, 'd': d}, {'l': 1.1, 'd': gd}, {'l': h - g0 - 1.1, 'd': d}]
    v, pos, L_ = turned(sh, 210 - Ltot, 100, 0.5, segs)
    v.hdim(0, -d / 2, Ltot, -d / 2, -d / 2 - 10, text=fmt(Ltot))
    v.hdim(pos[1][1], -d / 2, pos[3][0], -d / 2, -d / 2 - 4, text=fmt(2 * g0))
    v.vdim(-d / 2, Ltot / 2, d / 2, Ltot / 2, Ltot / 2, text='Ø%s g6' % fmt(d))
    v.leader(pos[1][0] + 0.55, gd / 2, -6, -14, '2× groove Ø%s × 1.1' % fmt(gd))
    v.text(Ltot / 2, 0, 'SIDE VIEW', 3.4, dy=48, weight='bold')


def mp116(): pin_sheet('MP-116', 'PIN A / PIN B (TOGGLE)', 39, 17.5, '2')   # Rev E: 39 (was 40): pin A's ends cleared the cheeks by 0
def mp117(): pin_sheet('MP-117', 'PIN O (HANDLE PIVOT)', 78, 36.0, '1', d=16.0, gd=15.2, ring='DIN 471 – 16')


def mp121():
    sh = new('MP-121', 'HANDLE-STOP POST', scale='2:1', qty='1',
             material='C45 Ø20 bar (or 17 a/f hex)', finish='Black oxide',
             notes=['Rev E: replaces the handle stop in the front column top (its tapped hole weakened the column nut thread).',
                    'Screws into the crown MP-108, hole T (M10 × 15, Z +62) with Loctite 243, 25 N·m on the 17 a/f flats.',
                    'Top: M10 × 1 × 12 thread for the adjustable stop (M10 × 1 × 12 set screw with nylon patch + urethane cap Ø16 × 4). Set the screw so the lever rests 3° above horizontal: cap top ≈ 220.5 above the bench (screw ≈ 1.5 proud).'] + GEN)
    v, pos, Ltot = turned(sh, 110, 110, 0.5, [{'l': 12, 'd': 10, 'thread': 'M10'}, {'l': 14, 'd': 20}])
    tapped_end(v, Ltot, 'M10x1', 12, -1)
    v.hdim(0, -5, 12, -5, -14, text='12')
    v.hdim(12, -10, 26, -10, -16, text='14')
    v.vdim(-10, 32, 10, 32, 32, text='Ø20, flats 17 a/f')
    v.leader(6, 5, -6, -14, 'M10 – 6g')
    v.leader(22, 0, 12, 24, 'M10 × 1 × 12 deep (stop screw)')
    v.text(13, 0, 'SIDE VIEW', 3.4, dy=34, weight='bold')


def mp118():
    sh = new('MP-118', 'RETURN ROD', scale='1:1', qty='2',
             material='C45 Ø12 bright bar', finish='Zinc plate 8 µm',
             notes=['Bottom thread screws into the ram MP-109 (M10 × 15) with Loctite 243.',
                    'Return spring: music wire Ø3.5 (EN 10270-1 DH), OD 31.5, free length 128, ≈ 16.4 active coils, ends closed and ground, shot-peened.',
                    'Rate ≈ 4.25 N/mm. Installed 109.5 at handle-up (≈ 80 N); 70.6 at handle-down (≈ 245 N, τ ≈ 480 MPa). Solid length ≤ 64.5.',
                    'Top: Ø32 × 3 washer and M10 nylock nut. The two springs together must lift the handle from the fully-down position.',
                    'Rev E: two flats 8 a/f, 6 long, just above the bottom thread (to tighten the rod). A POM guide sleeve Ø24 × Ø10.5 × 60 (BUY-49) on each rod centres the spring and stops it buckling.'] + GEN)
    v, pos, Ltot = turned(sh, 110, 110, 1.0, [{'l': 15, 'd': 10, 'thread': 'M10'}, {'l': 131, 'd': 10}, {'l': 30, 'd': 10, 'thread': 'M10'}])
    v.hdim(0, -5, 15, -5, -16, text='15')
    v.hdim(146, -5, 176, -5, -16, text='30')
    v.hdim(0, -5, 176, -5, -26, text='176')
    v.vdim(-5, 80, 5, 80, 80, text='Ø10 h9')
    v.leader(8, 5, -6, -14, 'M10 – 6g')
    v.leader(160, 5, 6, -14, 'M10 – 6g')
    v.text(88, 0, 'SIDE VIEW', 3.4, dy=34, weight='bold')


def mp119():
    sh = new('MP-119', 'PIVOT SPACER', scale='4:1', qty='2',
             material='CuSn8 bronze tube Ø26 × Ø14, or bar', finish='None',
             notes=['Bore Ø16.2 for the Ø16 pin O. Fits between the handle lever and each pivot cheek.',
                    'Rev E: 9.75 (was 10): lever 20 + 2 spacers = 39.5 between cheeks 40 apart, so the lever has 0.2–0.6 end float.', 'Faces parallel within 0.02.'] + GEN)
    v = View(sh, 120, 110, 0.25)
    v.rect(0, -12, 9.75, -8.1, 'sec'); v.rect(0, 8.1, 9.75, 12, 'sec')
    v.line(0, -8.1, 9.75, -8.1); v.line(0, 8.1, 9.75, 8.1)
    v.cl_h(-3, 13, 0)
    v.hdim(0, 12, 9.75, 12, 17, text='9.75 −0.05/−0.10')
    v.vdim(-12, -3, 12, -3, -10, text='Ø24')
    v.vdim(-8.1, 13, 8.1, 13, 18, text='Ø16.2 H9')
    v.text(5, -12, 'SECTION', 3.4, dy=30, weight='bold')


def mp120():
    sh = new('MP-120', 'STATION PILOT', scale='2:1', qty='1',
             material='42CrMo4 Ø12 bar, QT 28–32 HRC', finish='Grind Ø10 g6, Ra 0.4; tip nitrided or hard chrome',
             notes=['Rev E: Ø10 in tough 42CrMo4 (was Ø8 hardened 100Cr6): if the table is held off station it bends, it does not snap. The Ø10 g6 body locates in the ram (Ø10 H7 × 4); the M6 thread only clamps.',
                    'Screwed into the ram underside (MP-109, hole PL) with Loctite 243 until the shoulder seats; tip 84 below the ram.',
                    'Enters the die table hole PA or PB 6 mm before the dies touch. If the table is more than about 2 mm off a station, the tip lands on the table and stops the stroke with the dies still 6 mm apart.',
                    'Within ±2 mm, the 30° tip pulls the table onto the exact station (±0.02).',
                    'Tip: 30° half-angle cone, 4 long, tip radius R0.5, polished.'] + GEN)
    v, pos, Ltot = turned(sh, 110, 110, 0.5, [{'l': 10, 'd': 6, 'thread': 'M6'}, {'l': 84, 'd': 10}])
    v.line(94, 5, 98, 1.7); v.line(94, -5, 98, -1.7); v.line(98, -1.7, 98, 1.7)
    v.hdim(0, -3, 10, -3, -12, text='10')
    v.hdim(10, -5, 14, -5, -20, text='4 in ram')
    v.hdim(14, -5, 98, -1.7, -12, text='84')
    v.hdim(94, 5, 98, 1.7, 10, text='4')
    v.vdim(-5, 50, 5, 50, 50, text='Ø10 g6')
    v.leader(6, 3, -6, -14, 'M6 – 6g')
    v.leader(96, -3.35, 8, 14, '30° cone, tip R0.5')
    v.text(48, 0, 'SIDE VIEW', 3.4, dy=34, weight='bold')


# =====================================================================================
# MP-108 CROWN, MP-109 RAM (plan views: u = z (front to the right), w = x)
# =====================================================================================
def zx(feats):
    out = []
    for f in feats:
        g = dict(f); g['x'], g['z'] = f['z'], -f['x']
        if f['kind'] == 'rr':
            g['w'], g['h'] = f['h'], f['w']
        out.append(g)
    return out


def crown_feats():
    f = [feat(0, -105, 'hole', d=20, thru=True, label='C1'), feat(0, 105, 'hole', d=20, thru=True, label='C2'),
         feat(0, 13, 'rr', w=38, h=66, r=5, thru=True, label='SLOT'),
         feat(30, 60, 'hole', d=11, thru=True, label='R1'), feat(-30, -60, 'hole', d=11, thru=True, label='R2'),
         feat(0, 62, 'tap', m='M10', depth=15, side='top', label='T')]
    n = 1
    for x in (-28, 28):
        for z in (-17, 17):
            f.append(feat(x, z, 'hole', d=9, thru=True, cb=(14, 8.5), cbside='bot', label='K%d' % n)); n += 1
    f.append(feat(-28, 0, 'hole', d=6, depth=8, side='top', label='P1')); f.append(feat(28, 0, 'hole', d=6, depth=8, side='top', label='P2'))
    f += [feat(-19.5, 0, 'rr', w=3, h=14, r=1.5, depth=5, side='bot', label='N1'), feat(19.5, 0, 'rr', w=3, h=14, r=1.5, depth=5, side='bot', label='N2'),
          feat(-19.5, 17.5, 'rr', w=3, h=39, r=1.5, depth=13, side='top', label='N3'), feat(19.5, 17.5, 'rr', w=3, h=39, r=1.5, depth=13, side='top', label='N4')]
    return f


def mp108():
    sh = new('MP-108', 'CROWN', scale='1:1', qty='1',
             material='C45 flat 120 × 30, faced to 25', finish='Black oxide',
             notes=['C1/C2 Ø20 H7 at 210.00 ±0.01: same datum and program as base MP-101 and ram MP-109.',
                    'Rev E: 120 wide (was 80). At the cheek-bolt line the slot, bolt holes and reliefs left the 80 crown at 373–426 MPa at 16 kN; 120 wide takes it to about 120 MPa and carries the whole return-spring seat.',
                    'T: M10 × 15 from the TOP at Z +62 for the handle-stop post MP-121 (Rev E: the stop moved off the column top).',
                    'K1–K4: Ø9 THRU, CBORE Ø14 × 8.5 from the BOTTOM (M8 × 30 ISO 4762 + Nord-Lock into the cheeks MP-112).',
                    'P1/P2: Ø6 H7 × 8 from the top (cheek dowels). Slot 38 × 66, R5, THRU (links pass through).',
                    'Rev C.1: reliefs in the slot walls, all to X ±21, R1.5. N1/N2 from the BOTTOM, Z −7 to +7, 5 deep: ends of pin B, handle up. N3/N4 from the TOP, Z −2 to +37, 13 deep: ends of pin A, handle down. 212 MPa at 16 kN at the centre section.',
                    'Top and bottom faces parallel 0.02, flat 0.02. Plan drawn with the front of the press to the right.'] + GEN)
    fs = crown_feats()
    fz = zx(fs)
    v = View(sh, 150, 75, 1.0)
    v.segs(rrect(0, 0, 250, 120, 0))
    draw_plan_features(v, fz)
    v.cl_h(-130, 130, 0)
    sh.text(292, 124, 'PLAN (TOP)  — FRONT →', 3.4, 'start', weight='bold')
    v.hdim(-125, 60, 125, 60, 72)
    v.vdim(60, 125, -60, 125, 135)
    v.hdim(-105, 0, 105, 0, -68, text='210 ±0.01')
    lead_to(v, 62, 0, 290, 18, 'T: M10 × 15 (top), handle-stop post', r=5)
    v.hdim(-20, -19, 46, -19, -56, text='66')
    v.hdim(0, 0, 13, 0, -62, text='13')
    v.vdim(19, -20, -19, -20, -32, text='38')
    v.hdim(-17, 28, 17, 28, 46, text='34')
    v.vdim(28, -17, -28, -17, -40, text='56')
    v.hdim(0, -30, 60, -30, -68, text='60')
    v.vdim(30, 60, 0, 60, 75, text='30')
    lead_to(v, 105, 0, 290, 92, '2× Ø20 H7 THRU', r=10)
    lead_to(v, 60, 30, 290, 30, '2× Ø11 THRU', r=5.5)
    lead_to(v, 17, -28, 290, 106, '4× Ø9 THRU\nCBORE Ø14 × 8.5 BOTTOM', r=4.5)
    lead_to(v, 0, 28, 290, 44, '2× Ø6 H7 × 8 (top)', r=3)
    lead_to(v, 0, -21, 290, 66, 'N1, N2: RELIEF TO X ±21, Z ±7, 5 DEEP\nFROM BOTTOM, R1.5 (pin B ends)')
    lead_to(v, 30, -21, 290, 78, 'N3, N4: RELIEF TO X ±21, Z −2 TO +37,\n13 DEEP FROM TOP, R1.5 (pin A ends)')
    v.section_mark(-132, 0, 132, 0, 'A', flip=True)
    vs = View(sh, 150, 175, 1.0)
    draw_section(vs, solid_minus_thru((-125, 125), fz, 0), 25, fz, 0, y0=0)
    vs.vdim(0, 125, 25, 125, 135, text='25')
    vs.text(0, 0, 'SECTION A–A', 3.4, dy=10, weight='bold')
    vs2 = View(sh, 150, 217, 1.0)
    draw_section(vs2, solid_minus_thru((-125, 125), fz, -28), 25, fz, -28, y0=0)
    v.section_mark(-132, 28, 132, 28, 'B', flip=False)
    vs2.text(0, 0, 'SECTION B–B (X = +28)', 3.4, dy=10, weight='bold')
    vs2.vdim(0, -17, 8.5, -17, -40, text='8.5')
    dx = DXF(); dx.segs(rrect(0, 0, 250, 120, 0)); feats_dxf(dx, fz); DXFS['MP-108_crown.dxf'] = dx


def ram_feats():
    f = [feat(0, -105, 'hole', d=32, thru=True, label='B1'), feat(0, 105, 'hole', d=32, thru=True, label='B2'),
         feat(0, 0, 'hole', d=24, depth=4.2, side='bot', label='H'),
         feat(0, 0, 'rr', w=20.02, h=32.02, r=2, depth=2, side='top'),
         feat(-14.5, 0, 'rr', w=9, h=15, r=2, depth=3, side='top', label='L1'), feat(14.5, 0, 'rr', w=9, h=15, r=2, depth=3, side='top', label='L2')]
    n = 1
    for a in (45, 135, 225, 315):
        f.append(feat(20 * math.cos(math.radians(a)), 20 * math.sin(math.radians(a)), 'tap', m='M5', depth=10, side='bot', label='S%d' % n)); n += 1
    f += [feat(0, -12, 'tap', m='M5', depth=10, side='top', label='V1'), feat(0, 12, 'tap', m='M5', depth=10, side='top', label='V2'),
          feat(30, 60, 'tap', m='M10', depth=15, side='top', label='R1'), feat(-30, -60, 'tap', m='M10', depth=15, side='top', label='R2'),
          feat(-30, 60, 'tap', m='M6', depth=10, side='top', label='U1'), feat(30, -60, 'tap', m='M6', depth=10, side='top', label='U2'),
          feat(0, -65, 'tap', m='M6', depth=14, side='bot', label='PL'), feat(0, -65, 'hole', d=10, depth=4, side='bot', label='PL')]
    return f


def mp109():
    sh = new('MP-109', 'RAM', scale='1:1', qty='1',
             material='C45 flat 90 × 35, faced to 80 × 30', finish='Black oxide',
             notes=['Rev B: width 80 (was 70) to carry the return rods at X = ±30 with full thread walls.',
                    'B1/B2 Ø32 H7 at 210.00 ±0.01 for flanged self-lubricating bronze bushings ID 25 / OD 32 / L 33; same program as MP-101/MP-108.',
                    'Top: clevis pocket 20.02 × 32.02 × 2.0 (R2) with V1/V2 M5 × 10; R1/R2 M10 × 15 (return rods); U1/U2 M6 × 10 (urethane bumpers).',
                    'Bottom: H Ø24 H7 × 4.2 (die-holder spigot); S1–S4 M5 × 10 on PCD 40 at 45°; PL Ø10 H7 × 4 + M6 × 14 for the station pilot MP-120 (Rev E: the pilot locates on its Ø10 body, not its thread).',
                    'V1/V2: M5 thread 10 deep BELOW the pocket floor (Rev E: the section showed 8; the M5 × 25 clevis screws need 8.5).',
                    'Rev E: after pressing in the bushings, ream the BACK bushing (B2) to Ø25.15: one column guides the ram, the other only stops it turning, so the columns bowing 0.05 under load cannot pinch it.',
                    'Rev C.1: L1/L2 link-clearance pockets on the top, X ±10 to ±19, 15 long, 3 deep, R2, open into the clevis pocket. The R12 link ends dip 2 mm below the ram top.',
                    'Top and bottom faces parallel 0.02. Plan drawn with the front of the press to the right; hidden features are on the bottom.'] + GEN)
    fs = ram_feats()
    fz = zx(fs)
    v = View(sh, 150, 72, 1.0)
    v.segs(rrect(0, 0, 250, 80, 0))
    draw_plan_features(v, fz)
    v.cl_h(-130, 130, 0)
    sh.text(292, 124, 'PLAN (TOP)  — FRONT →', 3.4, 'start', weight='bold')
    v.hdim(-125, 40, 125, 40, 50)
    v.vdim(40, 125, -40, 125, 135)
    v.hdim(-105, 0, 105, 0, -50, text='210 ±0.01')
    v.hdim(-12, -10, 12, -10, -44, text='24')
    v.hdim(-60, 30, 60, 30, 45, text='120')
    v.vdim(30, -60, -30, -60, -80, text='60')
    v.hdim(-65, 0, 0, 0, -58, text='65')
    lead_to(v, 105, 0, 290, 30, '2× Ø32 H7 THRU', r=16)
    lead_to(v, 60, 30, 290, 44, 'R1, R2: M10 × 15 (top)', r=5)
    lead_to(v, 60, -30, 290, 58, 'U1, U2: M6 × 10 (top)', r=3)
    lead_to(v, 16, 10, 290, 72, 'POCKET 32.02 × 20.02 × 2 DEEP, R2 (top)\nV1, V2: M5 × 10 in pocket floor')
    lead_to(v, 14.14, -14.14, 290, 94, 'S1–S4: M5 × 10 BOTTOM, PCD 40\nH: Ø24 H7 × 4.2 BOTTOM', r=2.5)
    lead_to(v, -65, 0, 290, 110, 'PL: M6 × 12 BOTTOM (station pilot)', r=3)
    lead_to(v, 0, 17, 290, 82, 'L1, L2: POCKET 15 × 9 × 3 DEEP, R2 (top)\nX ±10 to ±19, open to the clevis pocket')
    v.section_mark(-132, 0, 132, 0, 'A', flip=True)
    vs = View(sh, 150, 168, 1.0)
    draw_section(vs, solid_minus_thru((-125, 125), fz, 0), 30, fz, 0, y0=0)
    vs.vdim(0, 125, 30, 125, 135, text='30')
    vs.text(0, 0, 'SECTION A–A', 3.4, dy=10, weight='bold')
    v.section_mark(-132, 30, 132, 30, 'B', flip=False)
    vs2 = View(sh, 150, 214, 1.0)
    draw_section(vs2, solid_minus_thru((-125, 125), fz, -30), 30, fz, -30, y0=0)
    vs2.text(0, 0, 'SECTION B–B (X = +30)', 3.4, dy=10, weight='bold')
    dx = DXF(); dx.segs(rrect(0, 0, 250, 80, 0)); feats_dxf(dx, fz); DXFS['MP-109_ram.dxf'] = dx


# =====================================================================================
# MP-110 CLEVIS, MP-111 DIE HOLDER, MP-112 CHEEK, MP-113 LEVER, MP-114 LINK
# =====================================================================================
def mp110():
    sh = new('MP-110', 'CLEVIS', scale='2:1', qty='1',
             material='C45 flat 25 × 35', finish='Black oxide',
             notes=['Sits 2 mm deep in the ram pocket; 2 × M5 × 25 ISO 4762 + threadlocker.',
                    'Rev B: bore Ø14 H7 with a %s 12 × 14 × 20 pressed in; pin B Ø12 runs dry.' % PAP,
                    'Bore axis parallel to the bottom face within 0.02 and square to the long sides within 0.02.',
                    'Vertical edges chamfer 2.5 × 45° to clear the R2 pocket corners.'] + GEN)
    v = View(sh, 100, 120, 0.5)
    v.segs(rrect(0, 11, 32, 22, 0))
    v.circle(0, 12, 7); v.circle(0, 12, 6, 'thin'); v.cmark(0, 12, 7)
    for z in (-12, 12):
        v.line(z - 2.75, 0, z - 2.75, 16.5, 'hid'); v.line(z + 2.75, 0, z + 2.75, 16.5, 'hid')
        v.line(z - 4.75, 16.5, z - 4.75, 22, 'hid'); v.line(z + 4.75, 16.5, z + 4.75, 22, 'hid'); v.line(z - 4.75, 16.5, z + 4.75, 16.5, 'hid')
    v.text(0, 0, 'FRONT VIEW (pin axis = X)', 3.2, dy=26, weight='bold')
    v.hdim(-16, 22, 16, 22, 32)
    v.vdim(0, -16, 22, -16, -26)
    v.vdim(0, 16, 12, 16, 24, text='12')
    v.hdim(-12, 0, 12, 0, -9, text='24')
    v.leader(0, 12, 22, -20, 'Ø14 H7 THRU\n+ bushing 12 × 14 × 20', on_circle_r=7, ang=-0.8)
    vt = View(sh, 260, 120, 0.5)
    vt.segs(rrect(0, 0, 32, 20, 0))
    for z in (-12, 12):
        vt.circle(z, 0, 2.75); vt.circle(z, 0, 4.75); vt.cmark(z, 0, 4.75)
    vt.text(0, 10, 'TOP VIEW', 3.2, dy=-14, weight='bold')
    vt.vdim(10, 16, -10, 16, 26, text='20')
    vt.leader(12, 0, 16, -20, '2× Ø5.5 THRU\nCBORE Ø9.5 × 5.5', on_circle_r=4.75)


def mp111():
    sh = new('MP-111', 'DIE HOLDER', scale='2:1', qty='1',
             material='42CrMo4 Ø55 bar, QT 28–32 HRC', finish='Black oxide',
             notes=['Spigot Ø24 h6 locates in the ram (Ø24 H7). 4 × M5 × 16 DIN 7984 low-head screws from below + threadlocker.',
                    'Bore Ø16 H7 takes the upper-die shank MP-202. Bottom face (die seat) square to the bore within 0.01, flat 0.01.',
                    'Lock screw: M5 × 10 ISO 4027 cone-point set screw with nylon patch; seats in the shank V-groove. Rev E: 7.0 above the die seat (was 5.5), above the groove centre for any shim pack, so it always pulls the shank up. Check at every die change.',
                    'Orientation hole Ø4 H8 × 8 deep in the bottom face at 20 mm radius, on the Z axis toward the FRONT (Rev E: was 6; with the Ø4 × 12 pin it engages 5–6 mm whatever the shim pack).'] + GEN)
    v = View(sh, 110, 120, 0.5)
    v.rect(-25, 0, -12, 11, 'sec'); v.rect(12, 0, 25, 11, 'sec'); v.rect(-12, 11, -8, 15, 'sec'); v.rect(8, 11, 12, 15, 'sec')
    v.rect(-8, 0, 8, 15, 'ko')
    v.line(-8, 0, -8, 15); v.line(8, 0, 8, 15)
    v.line(-25, 0, -8, 0); v.line(8, 0, 25, 0)
    v.line(8, 7.0 - 2.5, 25, 7.0 - 2.5, 'thin'); v.line(8, 7.0 + 2.5, 25, 7.0 + 2.5, 'thin')
    v.cl_v(-4, 19, 0)
    v.text(0, 0, 'SECTION THROUGH X AXIS', 3.2, dy=26, weight='bold')
    v.hdim(-25, 11, 25, 11, 24, text='Ø50')
    v.hdim(-12, 15, 12, 15, 19, text='Ø24 h6')
    v.hdim(-8, 0, 8, 0, -7, text='Ø16 H7')
    v.vdim(0, -25, 11, -25, -32, text='11')
    v.vdim(11, -12, 15, -12, -32, text='4')
    v.vdim(0, 25, 7.0, 25, 32, text='7')
    v.leader(20, 7.0, 18, -18, 'M5 radial (lock screw)')
    vb = View(sh, 280, 120, 0.5)
    vb.circle(0, 0, 25); vb.circle(0, 0, 8); vb.cmark(0, 0, 25)
    for a in (45, 135, 225, 315):
        u, w = 20 * math.cos(math.radians(a)), 20 * math.sin(math.radians(a))
        vb.circle(u, w, 2.75); vb.circle(u, w, 4.5); vb.cmark(u, w, 4.5)
    vb.circle(0, -20, 2); vb.cmark(0, -20, 2)
    vb.text(0, -25, 'BOTTOM VIEW (front at bottom)', 3.2, dy=14, weight='bold')
    vb.leader(14.14, 14.14, 20, -18, '4× Ø5.5 THRU, PCD 40\nCBORE Ø9 × 3.8 (bottom)', on_circle_r=4.5)
    vb.leader(0, -20, -26, 14, 'Ø4 H8 × 6', on_circle_r=2)


def mp112():
    sh = new('MP-112', 'PIVOT CHEEK', scale='2:1', qty='2',
             material='C45 flat 20 × 55', finish='Black oxide',
             notes=['Rev B: pivot bore Ø18 H7 for a %s 16 × 18 × 15 (pin O is now Ø16). Line-ream both cheeks together after fitting to the crown.' % PAP,
                    'Fixed to the crown with 2 × M8 × 30 ISO 4762 + Nord-Lock washers from below + 1 × Ø6 × 16 dowel. Carries the full toggle reaction (16 kN design).',
                    'Bottom face flat 0.02, square to the sides.'] + GEN)
    v = View(sh, 95, 145, 0.5)
    s = [L(-25, 0, 25, 0), L(25, 0, 25, 40), A(15, 40, 10, 0, 90), L(15, 50, -15, 50), A(-15, 40, 10, 90, 180), L(-25, 40, -25, 0)]
    v.segs(s)
    v.circle(0, 33.5, 9); v.circle(0, 33.5, 8, 'thin'); v.cmark(0, 33.5, 9)
    for z in (-17, 17):
        v.line(z - 3.4, 0, z - 3.4, 18.7, 'hid'); v.line(z + 3.4, 0, z + 3.4, 18.7, 'hid')
    v.line(-3, 0, -3, 8, 'hid'); v.line(3, 0, 3, 8, 'hid'); v.line(-3, 8, 3, 8, 'hid')
    v.text(0, 0, 'SIDE VIEW (Z horizontal)', 3.2, dy=14, weight='bold')
    v.hdim(-25, 50, 25, 50, 57)
    v.vdim(0, -25, 50, -25, -35)
    v.vdim(0, 25, 33.5, 25, 35, text='33.5')
    v.hdim(-17, 0, 17, 0, -10, text='34')
    v.leader(0, 33.5, 22, -22, 'Ø18 H7 THRU\n+ bushing 16 × 18 × 15', on_circle_r=9, ang=-0.7)
    v.leader(-22.07, 47.07, -18, -4, '2× R10')
    vb = View(sh, 270, 145, 0.5)
    vb.segs(rrect(0, 0, 50, 16, 0))
    for z in (-17, 17):
        vb.circle(z, 0, MINOR['M8'] / 2); vb.thread_arc(z, 0, 4); vb.cmark(z, 0, 4)
    vb.circle(0, 0, 3); vb.cmark(0, 0, 3)
    vb.text(0, -8, 'BOTTOM VIEW', 3.2, dy=14, weight='bold')
    vb.vdim(8, 25, -8, 25, 35, text='16')
    vb.leader(17, 0, 14, -20, '2× M8 × 16 deep', on_circle_r=4)
    vb.leader(0, 0, -14, -22, 'Ø6 H7 × 8 deep', on_circle_r=3)
    dx = DXF(); dx.segs(s); dx.segs([C(0, 33.5, 9)], 'HOLES'); DXFS['MP-112_pivot_cheek.dxf'] = dx


GRIP_C = 320.0


def lever_profile():
    """one-piece handle lever, local coords: u along the handle axis from pivot O, w perpendicular (crank side negative)."""
    Az, Ay = 40 * math.sin(math.radians(5)), -40 * math.cos(math.radians(5))
    wt = lambda u: 17 - 5.0 * (u - 40) / 220.0
    p_top, p_bot = (50.0, wt(50)), (50.0, -wt(50))
    hub = hull(circle_pts(0, 0, 18, 1.0) + circle_pts(Az, Ay, 12, 1.0) + [p_top, p_bot])
    hub = [(round(x, 6), round(y, 6)) for (x, y) in hub]
    it = hub.index((round(p_top[0], 6), round(p_top[1], 6))); ib = hub.index((round(p_bot[0], 6), round(p_bot[1], 6)))
    seq = []
    i = it
    while True:
        seq.append(hub[i])
        if i == ib:
            break
        i = (i + 1) % len(hub)
    arc = [(370 + 10 * math.cos(math.radians(a)), 10 * math.sin(math.radians(a))) for a in range(-90, 91, 6)]
    path = [(260, -12), (260, -10), (370, -10)] + arc[1:-1] + [(370, 10), (260, 10), (260, 12)]
    return seq + path, (Az, Ay)


def mp113():
    sh = new('MP-113', 'HANDLE LEVER (ONE PIECE)', scale='1:2', qty='1',
             material='C45 plate 25 mm, faced to 20', finish='Black oxide; grip zone edges R6',
             notes=['Rev B: replaces the Rev A hub + screwed bar (MP-115 deleted). The Rev A M12 thread reached ≈ 465 MPa at a 200 N push; this section sees ≈ 14 MPa (36 MPa at 500 N).',
                    'Profile from DXF (laser/waterjet + CNC, or wire EDM). Faces parallel 0.05.',
                    'O: Ø18 H7 for a %s 16 × 18 × 20. A: Ø14 H7 for a 12 × 14 × 20. Crank O→A = 40.00 ±0.02 at 85° ±0.1° to the handle axis.' % PAP,
                    'Grip zone (u 260–380): 20 × 20 with all four long edges R6; red TPR grip Ø32 / Ø24 × 120 pushed on with rubber adhesive. Grip centre 320 from O.',
                    'Handle stop: the lever underside rests on the adjustable stop screw on the front column at 3° above horizontal.'] + GEN)
    prof, (Az, Ay) = lever_profile()
    v = View(sh, 95, 105, 2.0)
    v.segs(polyline(prof))
    v.circle(0, 0, 9); v.circle(0, 0, 8, 'thin'); v.cmark(0, 0, 9)
    v.circle(Az, Ay, 7); v.circle(Az, Ay, 6, 'thin'); v.cmark(Az, Ay, 7)
    v.cl_h(-25, 390, 0)
    v.line(0, 0, Az * 1.4, Ay * 1.4, 'ctr')
    v.text(0, 0, 'O', 3.0, 'end', dx=-5, dy=-3, weight='bold'); v.text(Az, Ay, 'A', 3.0, 'start', dx=4.5, dy=1, weight='bold')
    sh.text(40, 22, 'PROFILE (handle axis horizontal)', 3.2, weight='bold')
    v.hdim(0, 18, 260, 12, 34, text='260')
    v.hdim(0, 18, 380, 10, 46, text='380')
    v.hdim(0, -14, GRIP_C, -10, -40, text='%s (grip centre)' % fmt(GRIP_C))
    v.vdim(12, 260, -12, 260, 250, text='24')
    v.vdim(10, 372, -10, 372, 392, text='20')
    v.vdim(16.77, 50, -16.77, 50, 66, text='33.5')
    v.leader(0, 0, -24, -26, 'Ø18 H7 THRU (O)', on_circle_r=9)
    v.leader(Az, Ay, -26, 20, 'Ø14 H7 THRU (A)\n40 ±0.02 from O at 85°', on_circle_r=7)
    v.leader(-12.7, 12.7, -12, -8, 'R18')
    v.leader(Az - 8.5, Ay - 8.5, -8, 12, 'R12')
    v.leader(380 - 7.07, -7.07, 10, 12, 'R10')
    ve = View(sh, 95, 190, 2.0)
    ve.rect(0, -10, 380, 10)
    ve.line(260, -10, 260, 10, 'thin')
    ve.cl_h(-10, 390, 0)
    sh.text(40, 176, 'EDGE VIEW (thickness)', 3.2, weight='bold')
    ve.vdim(-10, 380, 10, 380, 392, text='20')
    ve.leader(320, 10, 10, -10, 'grip zone: 4 edges R6')
    dx = DXF(); dx.segs(polyline(prof)); dx.segs([C(0, 0, 9), C(Az, Ay, 7)], 'HOLES'); DXFS['MP-113_handle_lever.dxf'] = dx


def mp114():
    sh = new('MP-114', 'TOGGLE LINK', scale='2:1', qty='2',
             material='C45 plate 8 mm, faced to 7', finish='Black oxide',
             notes=['Hole centres 60.00 ±0.02; make both links as a matched pair (within 0.01).',
                    'Rev B: bores Ø14 H7 with %s 12 × 14 × 6 pressed flush. Pins run dry.' % PAP,
                    'Faces parallel 0.02. Stamp the pair with matching numbers.'] + GEN)
    s = [L(0, -12, 60, -12), A(60, 0, 12, 270, 450), L(60, 12, 0, 12), A(0, 0, 12, 90, 270)]
    v = View(sh, 120, 110, 0.5)
    v.segs(s)
    for x in (0, 60):
        v.circle(x, 0, 7); v.circle(x, 0, 6, 'thin'); v.cmark(x, 0, 7)
    v.cl_h(-16, 76, 0)
    v.text(30, 12, 'PROFILE', 3.2, dy=-14, weight='bold')
    v.hdim(0, 0, 60, 0, -22, text='60 ±0.02')
    v.hdim(-12, 0, 72, 0, -30, text='84')
    v.vdim(12, 72, -12, 72, 82, text='24')
    v.leader(60, 0, 16, -22, '2× Ø14 H7 THRU\n+ bushing 12 × 14 × 6', on_circle_r=7)
    v.leader(-8.5, 8.5, -16, -10, '2× R12', on_circle_r=0)
    ve = View(sh, 330, 110, 0.5)
    ve.rect(-3.5, -12, 3.5, 12)
    ve.text(0, -12, 'EDGE VIEW', 3.2, dy=12, weight='bold')
    ve.hdim(-3.5, 12, 3.5, 12, 20, text='7')
    dx = DXF(); dx.segs(s); dx.segs([C(0, 0, 7), C(60, 0, 7)], 'HOLES'); DXFS['MP-114_toggle_link.dxf'] = dx
