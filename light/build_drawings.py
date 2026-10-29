"""MagPress L1: A3 drawing set (SVG pages -> set.html -> PDF via cad/render.js) and DXF cutting profiles.

Run:  python light/build_drawings.py <outdir> <model outdir>
<model outdir> is where light/build_models.py wrote assembly/projections.json, assembly/summary.json and the renders
(render_*.png from light/render.js). Missing renders or projections leave those views out.
"""
import base64
import csv
import json
import math
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'cad'))
import l1 as G                                                     # noqa: E402
from draft import (Sheet, View, DXF, draw_plan_features, draw_section, solid_minus_thru, feats_dxf, rrect, L, A, C,  # noqa: E402
                   fmt, MAJOR, esc)

OUT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(HERE, 'drawings')
MOD = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.join(HERE, 'models_out')
Sheet.PROJECT, Sheet.REV, Sheet.DATE = G.PROJECT, G.REV, G.DATE
SHEETS, DXFS = [], {}
SCALES = (1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 10.0)


def new(no, title, **kw):
    sh = Sheet(no, title, **kw)
    SHEETS.append(sh)
    return sh


def sc_label(s):
    if s >= 1:
        return '1:%s' % fmt(s)
    return '%s:1' % fmt(1 / s)


def extent(segs):
    xs, ys = [], []
    for g in segs:
        if g[0] == 'L':
            xs += [g[1], g[3]]; ys += [g[2], g[4]]
        elif g[0] == 'C':
            xs += [g[1] - g[3], g[1] + g[3]]; ys += [g[2] - g[3], g[2] + g[3]]
        elif g[0] == 'A':
            cx, cy, r, a0, a1 = g[1:]
            n = 24
            for k in range(n + 1):
                a = math.radians(a0 + (a1 - a0) * k / n)
                xs.append(cx + r * math.cos(a)); ys.append(cy + r * math.sin(a))
    return min(xs), max(xs), min(ys), max(ys)


def pick_scale(w, h, maxw, maxh):
    for s in SCALES:
        if w / s <= maxw and h / s <= maxh:
            return s
    return SCALES[-1]


def feature_table(sh, x, y, rows, title='FEATURES (positions from the part origin, mm)'):
    sh.text(x, y - 2, title, 3.0, weight='bold')
    cols = [('KEY', 12, 'middle'), ('POSITION', 52, 'start'), ('FEATURE', 130, 'start')]
    return sh.table(x, y, cols, rows, size=2.45, rh=4.5)


def img(sh, x, y, w, h, path):
    if not os.path.exists(path):
        sh.rect(x, y, w, h, 'thin')
        sh.text(x + w / 2, y + h / 2, '(render not available)', 3, 'middle')
        return
    try:
        from PIL import Image, ImageChops
        import io
        im = Image.open(path).convert('RGB')
        bb = ImageChops.difference(im, Image.new('RGB', im.size, (255, 255, 255))).getbbox()
        if bb:
            m = 12
            im = im.crop((max(0, bb[0] - m), max(0, bb[1] - m), min(im.width, bb[2] + m), min(im.height, bb[3] + m)))
        buf = io.BytesIO()
        im.save(buf, 'PNG')
        b = base64.b64encode(buf.getvalue()).decode()
    except ImportError:
        b = base64.b64encode(open(path, 'rb').read()).decode()
    sh.add('<image x="%.2f" y="%.2f" width="%.2f" height="%.2f" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,%s"/>'
           % (x, y, w, h, b))


# =====================================================================================
# part sheets
# =====================================================================================
def dxf_for(p, extra=()):
    dx = DXF()
    dx.segs(p['outline'])
    feats_dxf(dx, p['feats'])
    for segs, layer in extra:
        dx.segs(segs, layer)
    x0, x1, y0, y1 = extent(p['outline'])
    dx.text(x0, y0 - 8, 3.5, '%s %s  t=%s  qty %s  (%s)' % (p['id'], p['name'], fmt(p['T']), p['qty'], G.REV))
    DXFS['%s_%s.dxf' % (p['id'], p['name'].lower().replace(' + ', '-and-').replace(' ', '-').replace('/', '-').replace('(', '').replace(')', ''))] = dx


def plate_sheet(p, details=None, section=True, extra_dxf=(), dims=None):
    x0, x1, y0, y1 = extent(p['outline'])
    w, h = x1 - x0, y1 - y0
    profile = p.get('profile') == 'XZ'
    T = p['T']
    s = pick_scale(w, h, 170.0, 118.0 if section else 175.0)
    sh = new(p['id'], p['name'], scale=sc_label(s), qty=str(p['qty']), material=p['material'], finish=p['finish'],
             notes=p['notes'] + G.GEN)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    ox, oy = 112 - cx / s, 22 + 8 + (y1 / s)
    v = View(sh, ox, oy, s)
    sh.text(16, 18, ('PROFILE (side view, as cut)' if profile else 'PLAN (top) - +Y (back of the press) up'), 3.2, weight='bold')
    v.segs(p['outline'])
    draw_plan_features(v, p['feats'])
    v.cl_h(x0 - 4, x1 + 4, 0 if y0 < 0 < y1 else cy)
    v.cl_v(y1 + 4, y0 - 4, 0 if x0 < 0 < x1 else cx)
    v.hdim(x0, y1, x1, y1, y1 + 8 * s, text=fmt(w))
    v.vdim(y1, x1, y0, x1, x1 + 10 * s, text=fmt(h))
    for d in (dims or []):
        kind = d[0]
        if kind == 'h':
            _, u1, u2, ww, wd, t = d; v.hdim(u1, ww, u2, ww, wd, text=t)
        elif kind == 'v':
            _, w1, w2, uu, ud, t = d; v.vdim(w1, uu, w2, uu, ud, text=t)
        elif kind == 'l':
            _, uu, ww, dx_, dy_, t = d; v.leader(uu, ww, dx_, dy_, t)
    ybot = oy + (-y0) / s
    if section and T >= 1.0 and not profile:
        cut = 0.0 if y0 < 0 < y1 else cy
        v.section_mark(x0 - 6, cut, x1 + 6, cut, 'A', flip=True)
        sy = ybot + 22 + T / s
        vs = View(sh, ox, sy, s)
        draw_section(vs, solid_minus_thru((x0, x1), p['feats'], -cut), T, p['feats'], -cut, y0=0)
        vs.vdim(0, x1, T, x1, x1 + 10 * s, text=fmt(T))
        vs.text(cx, 0, 'SECTION A-A', 3.2, dy=8.5, weight='bold')
        ybot = sy + 12
    elif profile:
        ex = ox + x1 / s + 30
        if ex + T / s / 2 < 205:                      # edge view to the right of the profile
            vx = View(sh, ex, oy, s)
            vx.rect(-T / 2, y0, T / 2, y1)
            if p.get('edge_extra'):
                vx.segs(p['edge_extra'])
            vx.hdim(-T / 2, y0, T / 2, y0, y0 - 8 * s, text=fmt(T))
            sh.text(ex, oy - y1 / s - 4, 'EDGE VIEW', 2.8, 'middle', weight='bold')
        else:                                         # no room: a strip below
            vx = View(sh, ox, ybot + 16 + T / s / 2, s)
            vx.rect(x0, -T / 2, x1, T / 2)
            vx.vdim(-T / 2, x1, T / 2, x1, x1 + 8 * s, text=fmt(T))
            sh.text(16, ybot + 10, 'EDGE VIEW', 2.8, weight='bold')
            ybot += 22 + T / s
    if details:
        details(sh, ybot)
    yt = feature_table(sh, 212, 24, p['rows'])
    if p.get('dxf', True):
        dxf_for(p, extra_dxf)
        sh.text(212, yt + 6, 'DXF: %s profile (layer OUTLINE), holes (HOLES / TAP_DRILL / COUNTERBORE / POCKET).' % p['id'], 2.5)
    if p.get('mass'):
        sh.text(212, yt + 10.5, 'Mass about %.2f kg each.' % p['mass'], 2.5)
    return sh


def edge_detail(sh, x, y, k, title, segs_list, dims=(), u0=0.0, h=30.0):
    """detail view at scale k:1: part point (u0, 0) at paper (x, y); segs in part mm (u right, w up); title h mm above."""
    v = View(sh, x - u0 * k, y, 1.0 / k)
    sh.text(x, y - h, title, 3.0, 'start', weight='bold')
    for segs, c in segs_list:
        v.segs(segs, c)
    for d in dims:
        if d[0] == 'h':
            _, u1, u2, w, wd, t = d; v.hdim(u1, w, u2, w, wd, text=t, size=2.6)
        elif d[0] == 'v':
            _, w1, w2, u, ud, t = d; v.vdim(w1, u, w2, u, ud, text=t, size=2.6)
        elif d[0] == 'l':
            _, u, w, dx, dy, t = d; v.leader(u, w, dx, dy, t, size=2.5)
        elif d[0] == 'a':
            _, u, w, r, a0, a1, t = d; v.adim(u, w, r, a0, a1, t, size=2.6)
    return v


def arcseg(cx, cy, r, a0, a1):
    return A(cx, cy, r, a0, a1)


def det_ring_a(sh, ybot):
    # half section through the opening edge (u = distance from the centre, w = height above the ring bottom), 5:1
    t = G.RA_T
    o, tn, ph = G.RA_OPEN / 2, G.RA_TIN / 2, G.RA_PHOTO / 2
    r = G.RA_EDGE
    segs = [L(o, 0, o, t - G.RA_STEP2 - r), A(o + r, t - G.RA_STEP2 - r, r, 90, 180), L(o + r, t - G.RA_STEP2, tn, t - G.RA_STEP2),
            L(tn, t - G.RA_STEP2, tn, t - G.RA_STEP1), L(tn, t - G.RA_STEP1, ph, t - G.RA_STEP1), L(ph, t - G.RA_STEP1, ph, t),
            L(ph, t, ph + 4, t), L(o, 0, ph + 4, 0)]
    v = edge_detail(sh, 262, 205, 5, 'DETAIL: opening edge and pockets, half section (5:1)', [(segs, 'vis')],
                    [('h', o, tn, t - G.RA_STEP2, t + 2.2, fmt((G.RA_TIN - G.RA_OPEN) / 2)),
                     ('v', t, t - G.RA_STEP1, ph + 4, ph + 5.5, fmt(G.RA_STEP1)), ('v', t, t - G.RA_STEP2, ph + 4, ph + 7.5, fmt(G.RA_STEP2)),
                     ('l', o + r * 0.3, t - G.RA_STEP2 - r * 0.3, -14, -14, 'R%s (tin ledge edge)' % fmt(r))], u0=o, h=60)
    v.text(o, 1.0, 'opening %s / 2 ' % fmt(G.RA_OPEN), 2.4, 'end')


def det_upper_ring(sh, ybot):
    t, b, m = G.UR_T, G.BORE / 2, G.MOUTH_R
    segs = [L(b, t, b, m), A(b + m, m, m, 180, 270), L(b + m, 0, b + 9, 0), L(b, t, b + 9, t)]
    hole = [L(b, 3.2 - 2, b + 9, 3.2 - 2), L(b, 3.2 + 2, b + 9, 3.2 + 2)]
    edge_detail(sh, 262, 212, 4, 'DETAIL: bore mouth, half section (4:1)', [(segs, 'vis'), (hole, 'hid')],
                [('l', b + m * (1 - math.cos(math.radians(45))), m * (1 - math.sin(math.radians(45))), 18, 8, 'R%s mouth, polished' % fmt(m)),
                 ('v', 0, 3.2, b + 9, b + 11, '3.2'), ('l', b + 6, 3.2 + 2, 14, -10, 'M4 ball plunger')], u0=b, h=62)


def det_cup(sh, ybot):
    t = G.CUP_T
    top, bot = G.CUP_TOP / 2, G.CUP_BOT / 2
    ni, nt, nb, hn = G.NOSE_IN / 2, G.NOSE_TOP / 2, G.NOSE_BASE / 2, G.NOSE
    segs = [L(bot, 0, ni, t + hn), L(ni, t + hn, nt, t + hn), L(nt, t + hn, nb, t), L(nb, t, top + 8, t), L(bot, 0, top + 8, 0)]
    b2, m = G.BORE / 2, G.MOUTH_R
    ring = [L(b2, t + 6, b2, t + m), A(b2 + m, t + m, m, 180, 270), L(b2 + m, t, top + 8, t)]
    mag = [L(G.MAG / 2 - 2, 0, G.MAG / 2, 0), L(G.MAG / 2, 0, G.MAG / 2, G.T_MAG), L(G.MAG / 2, G.T_MAG, G.ACR / 2, G.T_MAG),
           L(G.ACR / 2, G.T_MAG, G.ACR / 2, G.T_MAG + G.T_ACR), L(G.ACR / 2, G.T_MAG + G.T_ACR, G.ACR / 2 - 3, G.T_MAG + G.T_ACR)]
    edge_detail(sh, 245, 205, 5, 'DETAIL: taper and nose, half section; upper ring landed (phantom) (5:1)',
                [(segs, 'vis'), (mag, 'ph'), (ring, 'ph')],
                [('a', bot, 0, 20, 90 - G.CUP_ALPHA, 90, '%s°' % fmt(G.CUP_ALPHA)), ('v', 0, t, top + 8, top + 10, fmt(round(t, 3))),
                 ('v', t, t + hn, top + 8, top + 13, fmt(hn)), ('l', nt, t + hn, 6, -22, 'nose top flat %.2f wide' % (nt - ni)),
                 ('l', (nt + nb) / 2, t + hn / 2, 16, -6, 'chamfer to %.2f sq.' % G.NOSE_BASE)], u0=G.MAG / 2 - 2, h=66)


def det_edge_r(r, label):
    def f(sh, ybot):
        segs = [L(0, 0, 6 - r, 0), A(6 - r, -r, r, 0, 90), L(6, -r, 6, -6)]
        edge_detail(sh, 262, 150, 10, 'DETAIL: %s (10:1)' % label, [(segs, 'vis')],
                    [('l', 6 - r + r * math.cos(math.radians(45)), -r + r * math.sin(math.radians(45)), 16, -8, 'R%s' % fmt(r))], h=12)
    return f


def turned_sheet(p):
    sh = new(p['id'], p['name'], scale='1:1' if p['kind'] != 'turned' else '1:2', qty=str(p['qty']), material=p['material'],
             finish=p['finish'], notes=p['notes'] + G.GEN)
    if p['kind'] == 'turned':
        s = 2.0
        v = View(sh, 30, 120, s)
        z = 0.0
        for d, l in p['segs']:
            dd = MAJOR[d] if isinstance(d, str) else d
            v.rect(z, -dd / 2, z + l, dd / 2)
            if isinstance(d, str):
                v.line(z, -dd / 2 + 0.9, z + l, -dd / 2 + 0.9, 'thin'); v.line(z, dd / 2 - 0.9, z + l, dd / 2 - 0.9, 'thin')
            v.hdim(z, dd / 2, z + l, dd / 2, 22, text=fmt(l))
            v.text(z + l / 2, -dd / 2, ('%s' % d) if isinstance(d, str) else 'D%s h6' % fmt(d), 2.8, dy=5)
            z += l
        v.cl_h(-4, z + 4, 0)
        v.hdim(0, -12, z, -12, -34, text=fmt(z))
        sh.text(16, 18, 'SIDE VIEW (axis horizontal)', 3.2, weight='bold')
    else:
        s = 0.5
        v = View(sh, 60, 100, s)
        if p['kind'] == 'pin':
            Lp, d = p['L'], p['d']
            v.rect(-Lp / 2, -d / 2, Lp / 2, d / 2)
            if p.get('groove'):
                for z in (-p['groove'], p['groove']):
                    v.line(z - 0.55, -d / 2 + 0.4, z - 0.55, d / 2 - 0.4, 'thin'); v.line(z + 0.55, -d / 2 + 0.4, z + 0.55, d / 2 - 0.4, 'thin')
                v.hdim(-p['groove'], d / 2, p['groove'], d / 2, d / 2 + 6, text=fmt(2 * p['groove']) + ' (groove centres, 1.1 wide, D15.2)')
            v.hdim(-Lp / 2, -d / 2, Lp / 2, -d / 2, -d / 2 - 6, text=fmt(Lp))
            v.vdim(-d / 2, -Lp / 2, d / 2, -Lp / 2, -Lp / 2 - 6, text='D%s' % fmt(d))
            v.cl_h(-Lp / 2 - 3, Lp / 2 + 3, 0)
        else:
            Lp, od, bo = p['L'], p['od'], p['bore']
            v.rect(-Lp / 2, -od / 2, Lp / 2, od / 2)
            v.line(-Lp / 2, -bo / 2, Lp / 2, -bo / 2, 'hid'); v.line(-Lp / 2, bo / 2, Lp / 2, bo / 2, 'hid')
            v.hdim(-Lp / 2, -od / 2, Lp / 2, -od / 2, -od / 2 - 6, text=fmt(Lp))
            v.vdim(-od / 2, -Lp / 2, od / 2, -Lp / 2, -Lp / 2 - 6, text='D%s' % fmt(od))
            v.leader(0, bo / 2, 20, -14, 'bore D%s' % fmt(bo))
            v.cl_h(-Lp / 2 - 3, Lp / 2 + 3, 0)
        sh.text(16, 18, 'SIDE VIEW (2:1)', 3.2, weight='bold')
    if p.get('mass'):
        sh.text(212, 30, 'Mass about %.3f kg each.' % p['mass'], 2.8)
    return sh


# =====================================================================================
# assembly sheets
# =====================================================================================
def draw_proj(sh, pr, ox, oy, s, hidden=False):
    v = View(sh, ox, oy, s)
    for line in pr.get('vis', []):
        if len(line) > 1:
            sh.add('<polyline points="%s" class="thin" style="stroke-width:.22"/>' % ' '.join('%.2f,%.2f' % v.P(x, y) for x, y in line))
    if hidden:
        for line in pr.get('hid', []):
            if len(line) > 1:
                sh.add('<polyline points="%s" class="hid" style="stroke-width:.15"/>' % ' '.join('%.2f,%.2f' % v.P(x, y) for x, y in line))
    return v


def bom_rows(summary):
    rows = []
    for p in G.PARTS:
        m = summary.get('masses', {}).get(p['id']) if summary else None
        rows.append([p['id'], p['name'], str(p['qty']), p['material'].split(' (')[0][:44], ('%.2f' % m) if m else ''])
    return rows


def sheet_cover(listing, summary):
    sh = new('L-000', 'COVER AND SHEET LIST', scale='-', qty='-', material='-', finish='-',
             notes=['MagPress L1: a light, hand-lever photo-magnet press for one size, 63.5 x 63.5 (2.5 inch square) with the market edge: '
                    'the flat tin is folded once (sharp crease, flap angled back onto the acrylic card) and the photo and film wrap round it.',
                    'Two stations on a sliding table: A folds the flat tin with the photo and film into a shell (stroke 1); B presses the '
                    'shell onto the acrylic card and magnet sheet and turns the flap in (stroke 2). One magnet = 2 strokes.',
                    'ASSUMED material (to confirm with a seller\'s pre-cut set before manufacture): tin 71.5 x 71.5 x 0.23, photo and film '
                    '79 x 79 octagons, acrylic card 60.5 x 60.5 x 3.0, magnet sheet 57 x 57 x 1.0. Parts marked MAT follow these sizes.',
                    'DXF files: one per cut part, 1:1 mm, layers OUTLINE / HOLES / TAP_DRILL / COUNTERBORE / POCKET. No part is bent: all are '
                    'flat profiles (laser, plasma or wire-EDM) plus machining; columns and pins are turned.',
                    '3D: STEP of every part and of the assembly come with this set.'])
    sh.text(16, 20, 'MagPress L1', 9, weight='bold')
    sh.text(16, 28, 'Light photo-magnet press, 63.5 x 63.5 (2.5 inch square), market edge', 4)
    img(sh, 14, 34, 98, 128, os.path.join(MOD, 'render_assembled.png'))
    img(sh, 112, 34, 98, 128, os.path.join(MOD, 'render_exploded.png'))
    y = 170
    data = [['Footprint', '360 x 220 mm (base), height about %d mm with the handle up' % round(G.Z_O + G.LEVER_LEN * math.sin(math.radians(G.handle_angle(G.THETA_UP))) + 15)],
            ['Mass', 'about %.0f kg' % summary['mass_total'] if summary else ''],
            ['Stroke', '%.1f mm (handle %.0f deg up to %.1f deg down)' % (G.STROKE, G.handle_angle(G.THETA_UP), G.handle_angle(G.THETA_STOP))],
            ['Force at the die', 'about 2 kN fold (stroke 1), 3-5 kN with the upper springs (stroke 2); frame checked at 15 kN'],
            ['Magnet', '63.5 x 63.5, finished about %.1f thick' % G.FINISHED_T]]
    sh.table(16, y, [('', 34, 'start'), ('', 160, 'start')], data, size=2.7, rh=5.2, head=False, bold_first_col=True)
    sh.text(212, 22, 'SHEET LIST', 3.4, weight='bold')
    sh.table(212, 26, [('SHEET', 16, 'middle'), ('DRAWING', 22, 'start'), ('TITLE', 112, 'start'), ('QTY', 22, 'start')], listing,
             size=2.45, rh=4.25)
    return sh


def sheet_ga(proj, summary):
    sh = new('L-001', 'GENERAL ARRANGEMENT', scale='1:4', qty='1', material='see parts list', finish='-',
             notes=['Handle up, station A (fold) under the ram. Pull the handle down to the stop for each stroke; slide the table '
                    'between the two click positions (ball detent) to change station.',
                    'Heights at the bottom of the stroke: table top Z %g, magnet face %g, plug face %g. Pivot O at Z %g.' % (G.Z_TABLE, G.Z_FACE, G.Z_FACE, G.Z_O),
                    'Bolt the base to a bench (4 x M8) or fit rubber feet. Grease the pins, the columns and the table slide.',
                    'Interference check (3D): no clashes through the stroke at either station or while the table slides (springs excluded).'])
    s = 4.0
    if proj:
        sh.text(16, 18, 'FRONT VIEW', 3.2, weight='bold')
        v = draw_proj(sh, proj['front_up'], 70, 196, s)
        v.hdim(-180, 0, 180, 0, -14, text='360')
        sh.text(158, 18, 'SIDE VIEW (from the right)', 3.2, weight='bold')
        v2 = draw_proj(sh, proj['side_up'], 178, 196, s)
        v2.hdim(-110, 0, 110, 0, -14, text='220')
        ztop = max(y for ln in proj['front_up']['vis'] for (x, y) in ln)
        v.vdim(0, -180, ztop, -180, -205, text='%d' % round(ztop))
        v.vdim(0, 180, G.Z_HEAD + G.HEAD_T, 180, 200, text='%g' % (G.Z_HEAD + G.HEAD_T))
    sh.text(212, 22, 'PARTS LIST - MADE', 3.2, weight='bold')
    y = sh.table(212, 26, [('PART', 14, 'start'), ('NAME', 52, 'start'), ('QTY', 18, 'start'), ('MATERIAL', 92, 'start'), ('KG', 12, 'end')],
                 bom_rows(summary), size=2.3, rh=3.9)
    sh.text(212, y + 6, 'PARTS LIST - BOUGHT', 3.2, weight='bold')
    sh.table(212, y + 10, [('ITEM', 12, 'start'), ('DESCRIPTION', 98, 'start'), ('QTY', 14, 'start'), ('WHERE', 64, 'start')],
             [[b[0], b[1][:80], str(b[2]), b[3][:52]] for b in G.BOUGHT], size=2.15, rh=3.55)
    return sh


def poly_path(loops, v):
    d = ''
    for lp in loops:
        if len(lp) < 3:
            continue
        pts = [v.P(x, y) for x, y in lp]
        d += 'M%.2f %.2f ' % pts[0] + ' '.join('L%.2f %.2f' % p for p in pts[1:]) + ' Z '
    return d


def sheet_sections(proj):
    sh = new('L-002', 'DIE SECTIONS AT THE BOTTOM OF THE STROKE', scale='1:1', qty='-', material='-', finish='-',
             notes=['Sections on the press centre plane (Y = 0), handle on its stop, material shown black. Left: station A, stroke 1 (the '
                    'flat tin, photo and film folded over the pedestal into the upper ring). Right: station B, stroke 2 (the shell pushed '
                    'into the taper cup onto the acrylic card and magnet; the upper ring retracted %.1f mm).' % G.RECESS,
                    'Both strokes end with the plug face at Z %g: the handle stop sets it (two stop bolts; 1 deg = 0.08 mm); the plug '
                    'shims set station B against station A.' % G.Z_FACE,
                    'Stroke 1: ring A (4 light springs) carries the blank down %g mm round the fixed pedestal; the upper ring (4 heavy ' % G.RA_TRAVEL +
                    'springs, %.1f kN preload) holds the edge, so the flat tin folds up the ring bore. Ball plungers keep the shell in the '
                    'upper ring when the ram goes up.' % (G.UP_SPR['n'] * G.UP_SPR['k'] * G.UP_SPR['pre'] / 1000),
                    'Stroke 2: the upper ring lands on the cup ring, its mouth over the cup ring\'s nose; the plug pushes the shell down %g mm and the 18 deg taper turns the ' % G.RECESS +
                    'tin flap in onto the back corner of the acrylic card.'])
    s = 1.0
    h, T = G.FACE / 2, G.T_STACK
    zf, zdb, zr = G.Z_FACE, G.Z_DB, G.Z_RAM
    za = zf - G.RECESS
    common = [('L-206', 40, zdb + G.DB_T / 2, zdb + G.DB_T / 2), ('L-103', 50, 17, 17), ('L-101', 50, 6, 6),
              ('L-106', 25, zr + 12, zr + 12), ('L-108', 10, zr + G.RAM_T + 20, zr + G.RAM_T + 22)]
    labels = {'A': common + [('L-208', 20, zf + 8, zf + 16), ('L-207', 50, za + 7, za + 9), ('L-203', 50, za - 4, za - 3),
                             ('L-202', 20, zf - 4, zf - 2.5), ('L-201', 50, G.Z_TABLE + G.BB_T / 2, G.Z_TABLE + G.BB_T / 2)],
              'B': common + [('L-208', 20, zf + 8, zf + 16), ('L-207', 50, zf + 7, zf + 8), ('L-205', 50, zf - 2, zf - 1),
                             ('L-204', 30, G.Z_TABLE + G.RIS_T / 2, G.Z_TABLE + G.RIS_T / 2)]}
    for k, (st, ox) in enumerate((('A', 82), ('B', 236))):
        pr = proj.get('sec_%s' % st) if proj else None
        sh.text(ox, 17, 'STATION %s - STROKE %d' % (st, k + 1), 3.4, 'middle', weight='bold')
        if not pr:
            continue
        v = View(sh, ox, 226, s)
        d = ''.join(poly_path(f, v) for f in pr['faces'])
        sh.add('<path d="%s" fill="url(#hatch)" fill-rule="evenodd" stroke="#000" stroke-width=".25"/>' % d)
        for line in pr['vis']:
            if len(line) > 1:
                sh.add('<polyline points="%s" class="thin" style="stroke-width:.2"/>' % ' '.join('%.2f,%.2f' % v.P(x, y) for x, y in line))
        if st == 'A':
            zt, ped = G.Z_FACE, G.PED / 2
            z0 = G.Z_BB + G.RA_T + 0.2
            v.poly([(-h, z0), (-h, zt), (h, zt), (h, z0), (ped, z0), (ped, zt - T), (-ped, zt - T), (-ped, z0)], 'solidbk')
        else:
            zt = G.Z_FACE
            zb = zt - G.CUP_T
            a = math.radians(G.CUP_ALPHA)
            v.rect(-G.MAG / 2, zb, G.MAG / 2, zb + G.T_MAG, 'fillw')
            v.rect(-G.ACR / 2, zb + G.T_MAG, G.ACR / 2, zb + G.T_MAG + G.T_ACR, 'fillw')
            xo = h - G.CUP_T * math.tan(a)
            xi = h - T * (math.tan(a) + 1 / math.cos(a))
            v.poly([(-xo + T / math.cos(a), zb), (-xo, zb), (-h, zt), (h, zt), (xo, zb), (xo - T / math.cos(a), zb), (xi, zt - T),
                    (-xi, zt - T)], 'solidbk')
        for (lab, u, w, wt) in labels[st]:
            v.leader(u, w, 64 - u if st == 'B' else 66 - u, w - wt, lab, size=2.6)
        v.vdim(G.Z_TABLE, -62, G.Z_FACE, -62, -70, text='%g' % (G.Z_FACE - G.Z_TABLE))
    sh.text(330, 72, 'KEY', 3.2, weight='bold')
    key = [['L-101', 'base plate'], ['L-103', 'sliding table'], ['L-106', 'ram'], ['L-108', 'ram clevis'], ['L-201', 'station A base block'],
           ['L-202', 'pedestal'], ['L-203', 'ring A (blank holder)'], ['L-204', 'station B riser'], ['L-205', 'cup ring (18 deg taper)'],
           ['L-206', 'upper die body'], ['L-207', 'upper ring'], ['L-208', 'plug'], ['black', 'tin + photo + film'],
           ['white', 'acrylic card, magnet sheet']]
    sh.table(330, 76, [('PART', 16, 'start'), ('NAME', 58, 'start')], key, size=2.5, rh=4.4)
    return sh


def sheet_edge():
    sh = new('L-003', 'MAGNET EDGE AND MATERIAL (ASSUMED)', scale='10:1', qty='-', material='-', finish='-',
             notes=['The finished edge (market construction): tin folded once with a sharp crease at the face, flap angled back 18 deg and '
                    'bearing on the back corner of the acrylic card; photo and film wrap round the crease and are tucked back between the '
                    'flap and the card.',
                    'Sizes shown are ASSUMED. Measure one pre-cut set from the chosen seller (ruler accuracy) and send: tin L x W x t; '
                    'photo / film L x W and corner clip; acrylic L x W x t; magnet L x W x t. Parts marked MAT are then adjusted.',
                    'Stroke 2 forming is checked in 2D (plane strain, verify/stroke2L.py); the paper tuck is not modelled. Prove it on the '
                    'first die set with real material before ordering spares.'])
    s = 0.1
    h = G.FACE / 2
    v = View(sh, 30 - (h - 10) / s, 140, s)
    T = G.T_STACK
    # stack, half section: u = distance from the centre (shown from 22 to the edge), w = height above the magnet back
    acr0, acr1 = G.T_MAG, G.T_MAG + G.T_ACR
    v.rect(h - 10, 0, G.MAG / 2, G.T_MAG, 'vis'); v.text(h - 7.5, 0.35, 'magnet %s' % fmt(G.T_MAG), 2.4)
    v.rect(h - 10, acr0, G.ACR / 2, acr1, 'vis'); v.text(h - 7.5, acr0 + 1.2, 'acrylic card %s' % fmt(G.T_ACR), 2.4)
    top = acr1 + T
    a = math.radians(G.CUP_ALPHA)
    xc = h
    v.poly([(h - 10, top), (xc, top), (xc - top * math.tan(a), 0.0), (xc - top * math.tan(a) - T / math.cos(a), 0.0),
            (xc - T * (math.tan(a) + 1 / math.cos(a)), top - T), (h - 10, top - T)], 'sec')
    v.text(h - 5, top + 0.4, 'tin + photo + film %s (photo and film wrap round the crease)' % fmt(T), 2.4)
    v.vdim(0, xc + 0.3, top, xc + 0.3, xc + 1.2, text='%s' % fmt(round(G.FINISHED_T, 3)))
    v.hdim(G.ACR / 2, acr0, xc, top, -1.0, text='%s' % fmt(round(xc - G.ACR / 2, 2)))
    v.adim(xc, top, 25, 270 - G.CUP_ALPHA, 270, '%s°' % fmt(G.CUP_ALPHA))
    v.leader(xc, top, 20, -14, 'sharp crease (face edge)')
    v.leader(G.ACR / 2, acr0, 24, 22, 'flap bears on the card\'s back corner')
    rows = [['Tin sheet (flat)', '%s x %s x %s, corners clipped 45 deg' % (fmt(G.TIN), fmt(G.TIN), fmt(G.T_TIN)), 'seller pre-cut'],
            ['Photo', '%s x %s octagon, paper about %s' % (fmt(G.PHOTO), fmt(G.PHOTO), fmt(G.T_PHOTO)), 'own print'],
            ['Film', '%s x %s octagon, about %s' % (fmt(G.PHOTO), fmt(G.PHOTO), fmt(G.T_FILM)), 'seller pre-cut'],
            ['Acrylic card', '%s x %s x %s' % (fmt(G.ACR), fmt(G.ACR), fmt(G.T_ACR)), 'seller pre-cut'],
            ['Magnet sheet', '%s x %s x %s, self-adhesive, stuck centred on the card first' % (fmt(G.MAG), fmt(G.MAG), fmt(G.T_MAG)), 'seller pre-cut'],
            ['Finished magnet', '%s x %s face, about %s thick' % (fmt(G.FACE), fmt(G.FACE), fmt(round(G.FINISHED_T, 2))), '']]
    sh.text(212, 22, 'MATERIAL PER MAGNET (ASSUMED - TO CONFIRM)', 3.2, weight='bold')
    y = sh.table(212, 26, [('ITEM', 30, 'start'), ('SIZE (mm)', 120, 'start'), ('SOURCE', 40, 'start')], rows, size=2.5, rh=4.6)
    sh.text(212, y + 8, 'PARTS THAT CHANGE WITH THE MATERIAL (MAT)', 3.2, weight='bold')
    mat = [['L-202 pedestal', 'face - 2 x (tin + photo + film)'], ['L-203 ring A', 'pockets = tin and photo sizes, opening = tin - 1.5'],
           ['L-205 cup ring', 'landing face height = finished magnet; taper; nose'], ['L-204 riser', 'thickness = 28 - cup ring'],
           ['L-207 upper ring', 'bore = face + 0.35'], ['L-208 plug', 'face - 0.1']]
    sh.table(212, y + 12, [('PART', 40, 'start'), ('DEPENDS ON', 150, 'start')], mat, size=2.5, rh=4.6)
    return sh


def sheet_assembly():
    sh = new('L-004', 'ASSEMBLY SEQUENCE AND USE', scale='-', qty='-', material='-', finish='-',
             notes=['Torques (8.8 screws, oiled): M4 3 Nm, M5 6 Nm, M6 10 Nm, M8 25 Nm, M12 column nuts 60 Nm. Thread-lock the shoulder '
                    'screws and the stop-bolt jam nuts.',
                    'Before the first magnet: run both stations slowly with no material and check with a 0.1 feeler that the upper ring '
                    'clears the pedestal all round (station A) and lands square on the cup ring (station B).'])
    img(sh, 14, 16, 98, 210, os.path.join(MOD, 'render_exploded.png'))
    img(sh, 114, 16, 94, 104, os.path.join(MOD, 'render_dies.png'))
    img(sh, 114, 122, 94, 104, os.path.join(MOD, 'render_assembled.png'))
    steps = [
        'FRAME: screw the two columns L-104 into the base L-101 (M12, shoulder tight). Slide on the seat collars (top at Z %g), the '
        'return springs, the ram L-106 with its pressed-in bushes, then the up-stop collars (underside at Z %.1f).' % (G.Z_SEAT, G.Z_UPSTOP),
        'HEAD: dowel and screw the two cheeks L-107 (stub pins L-111 pressed in) to the head L-105. Fit the head on the columns, '
        'washers and M12 nuts.',
        'TOGGLE: clevis L-108 on the ram (2 dowels, 2 x M8 from below). Link L-110 in the clevis with pin B. Lever plates L-109 on the '
        'stub pins with the link between them; press pin A through plates and link (pin B likewise through the clevis); spacer '
        'tubes L-113 and grip spacer L-114 with 4 x M8 bolts.',
        'TABLE: rails L-102 loosely on the base; stop pin in; table L-103 with ball plunger and knobs between the rails; push the '
        'rails to 0.05 a side and tighten.',
        'STATION A: pedestal L-202 to the base block L-201 (2 dowels, 4 x M5 from below); springs, ring A L-203 on 4 shoulder '
        'screws from below; block to the table at x = -75 (2 dowels, 4 x M6 from below).',
        'STATION B: cup ring L-205 on the riser L-204 (2 dowels, 4 x M5 countersunk); riser to the table at x = +75.',
        'UPPER DIE: plug L-208 with the 0.4 shim pack L-209 to the die body L-206 (2 dowels, 4 x M6). Springs, upper ring L-207 on '
        '4 shoulder screws, ball plungers set 0.4 proud. Die body to the ram (2 dowels, 4 x M8 from the top).',
        'SET: station A under the ram, handle down: adjust the two stop bolts until the plug just touches a blank stack on the '
        'pedestal. Station B: add or remove shims until a test magnet comes out with its face level with the cup ring top.',
        'USE: (1) station A out at the left: lay the tin in ring A\'s small pocket, photo face-up on it, film on top. (2) Slide to '
        'station A, pull the handle to the stop: the shell stays in the upper ring. (3) Station B out at the right: card with magnet, '
        'magnet down, into the cup. (4) Slide to station B, pull to the stop. (5) Slide back and lift the magnet out of the cup.']
    y = 70
    sh.text(212, y - 6, 'ASSEMBLY', 3.2, weight='bold')
    for i, t in enumerate(steps, 1):
        lines = sh.wrap(t, 188, 2.45)
        for j, ln in enumerate(lines):
            if y > 227:
                break
            sh.text(212, y, ('%d.' % i) if j == 0 else '', 2.45, weight='bold')
            sh.text(217, y, ln, 2.45)
            y += 3.4
        y += 0.8
    sh.text(212, 22, 'OPERATING CYCLE (one magnet = 2 strokes)', 3.2, weight='bold')
    cyc = [['1', 'Table right (station A under the ram)', 'load B: card + magnet into the cup'],
           ['2', 'Pull to the stop', 'stroke 1 at A: flat tin + photo + film folded into a shell'],
           ['3', 'Slide the table left (B under the ram)', 'load A: next tin, photo, film'],
           ['4', 'Pull to the stop', 'stroke 2 at B: shell pressed onto the card, flap turned in'],
           ['5', 'Slide right, lift the magnet out', 'repeat from 2']]
    sh.table(212, 26, [('#', 8, 'middle'), ('HANDLE / TABLE', 74, 'start'), ('WHAT HAPPENS', 110, 'start')], cyc, size=2.5, rh=4.8)
    return sh


# =====================================================================================
def main():
    os.makedirs(os.path.join(OUT, 'svg'), exist_ok=True)
    summary = None
    sp = os.path.join(MOD, 'assembly', 'summary.json')
    if os.path.exists(sp):
        summary = json.load(open(sp))
        for p in G.PARTS:
            p['mass'] = summary['masses'].get(p['id'])
    proj = None
    pp = os.path.join(MOD, 'assembly', 'projections.json')
    if os.path.exists(pp):
        proj = json.load(open(pp))
    # placeholders for the front sheets (filled after the part sheets so the list is complete)
    cover_i = len(SHEETS)
    sheet_ga(proj, summary)
    sheet_sections(proj)
    sheet_edge()
    sheet_assembly()
    by = {p['id']: p for p in G.PARTS}
    for p in G.PARTS:
        pid = p['id']
        if p['kind'] in ('turned', 'pin', 'tube'):
            turned_sheet(p)
        elif pid == 'L-203':
            plate_sheet(p, details=det_ring_a)
        elif pid == 'L-207':
            plate_sheet(p, details=det_upper_ring)
        elif pid == 'L-205':
            plate_sheet(p, details=det_cup, extra_dxf=[(rrect(0, 0, G.CUP_BOT, G.CUP_BOT, G.CUP_R), 'TAPER_BOTTOM')])
        elif pid == 'L-202':
            plate_sheet(p, details=det_edge_r(G.PED_EDGE, 'pedestal top edge'))
        elif pid == 'L-208':
            plate_sheet(p, details=det_edge_r(G.PLUG_EDGE, 'plug face edge'))
        elif pid == 'L-209':
            plate_sheet(p, section=False)
        elif pid == 'L-109':
            plate_sheet(p, dims=[('l', -16, 0, -12, -10, 'R16 hub'), ('l', -12, -G.R_CRANK - 6, -12, 12, 'R14 crank lobe'),
                                 ('l', 200, -46, 10, 22, 'bar 30 wide, %g deg below the O-A normal; end R15 at %g from O' % (90 - G.HANDLE_OFF, G.LEVER_LEN))])
        else:
            plate_sheet(p)
    listing = [['1', 'L-000', 'COVER AND SHEET LIST', '-']] + \
              [[str(i + 2), s.no, s.title, s.qty] for i, s in enumerate(SHEETS)]
    cover = sheet_cover(listing, summary)
    SHEETS.remove(cover)
    SHEETS.insert(cover_i, cover)
    N = len(SHEETS)
    pages = []
    for i, sh in enumerate(SHEETS, 1):
        sh.index, sh.total = i, N
        svg = sh.svg()
        open(os.path.join(OUT, 'svg', '%02d_%s.svg' % (i, sh.no)), 'w').write(svg)
        pages.append(svg)
    html = ('<!doctype html><html><head><meta charset="utf-8"><style>@page{size:420mm 297mm;margin:0}'
            'html,body{margin:0;padding:0}.pg{width:420mm;height:297mm;page-break-after:always;overflow:hidden}'
            '.pg:last-child{page-break-after:auto}</style></head><body>' + ''.join('<div class="pg">%s</div>' % p for p in pages) + '</body></html>')
    open(os.path.join(OUT, 'set.html'), 'w').write(html)
    zp = os.path.join(OUT, 'MagPress-L1_DXF_%s.zip' % G.REV)
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('README.txt',
                   'MagPress L1 (%s) - DXF cutting profiles, R12, mm, 1:1. One file per cut part.\n'
                   'No part is bent: every file is a flat profile to cut (laser / plasma / waterjet for the frame plates; wire-EDM for the '
                   'hardened die openings) and then machine as the PDF drawing says.\n'
                   'Layers: OUTLINE (cut), HOLES (through holes, true size), TAP_DRILL (tap drill size - tap after cutting), COUNTERBORE '
                   '(machine to depth), POCKET (blind pocket outline), SPOT (dimple), TAPER_BOTTOM (cup ring: bottom of the 18 deg taper), '
                   'NOTES (part label).\n'
                   'Plate parts: plan view, +Y (back of the press) up. Profile parts (cheek, clevis, lever plate, link): side profile as cut.\n'
                   'Material sizes are ASSUMED (see sheet L-003): parts marked MAT may change by a few tenths before manufacture.\n'
                   'The PDF drawings govern.\n' % G.REV)
        for name, dx in sorted(DXFS.items()):
            z.writestr(name, dx.dumps())
    with open(os.path.join(OUT, 'MagPress-L1_BOM_%s.csv' % G.REV), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['item', 'name', 'qty', 'make / buy', 'material or spec', 'finish', 'mass kg each', 'dxf'])
        for p in G.PARTS:
            w.writerow([p['id'], p['name'], p['qty'], 'make', p['material'], p['finish'], ('%.3f' % p['mass']) if p.get('mass') else '',
                        'yes' if p.get('dxf', True) else 'no (turned)'])
        for b in G.BOUGHT:
            w.writerow([b[0], b[1], b[2], 'buy', '', '', '', b[3]])
    print(json.dumps({'sheets': N, 'dxf': len(DXFS)}))


if __name__ == '__main__':
    main()
