"""Minimal 2D drafting library: A3 sheets as SVG (mm units), ISO-style lines,
dimensions, sections, hole tables, title block; plus an R12 DXF writer."""
import math, html

FONT = "DejaVu Sans, Liberation Sans, Arial, sans-serif"
MINOR = {'M4': 3.3, 'M5': 4.2, 'M6': 5.0, 'M8': 6.8, 'M10': 8.5, 'M12': 10.2, 'M16': 14.5, 'M16x1.5': 14.5, 'M6x0.75': 5.2, 'M10x1': 9.0}
MAJOR = {'M4': 4, 'M5': 5, 'M6': 6, 'M8': 8, 'M10': 10, 'M12': 12, 'M16': 16, 'M16x1.5': 16, 'M6x0.75': 6, 'M10x1': 10}


def fmt(v):
    v = round(float(v), 3)
    if abs(v) < 1e-9:
        v = 0.0
    return ('%.3f' % v).rstrip('0').rstrip('.')


def esc(t):
    return html.escape(str(t), quote=True)


# ---------------- geometry segments (part coordinates, u right, w up) -------------
def L(x1, y1, x2, y2): return ('L', x1, y1, x2, y2)
def A(cx, cy, r, a0, a1): return ('A', cx, cy, r, a0, a1)   # CCW a0 -> a1 (deg)
def C(cx, cy, r): return ('C', cx, cy, r)


def rrect(cx, cy, w, h, r):
    hw, hh = w / 2.0, h / 2.0
    r = min(r, hw, hh)
    if r <= 1e-6:
        return [L(cx - hw, cy - hh, cx + hw, cy - hh), L(cx + hw, cy - hh, cx + hw, cy + hh),
                L(cx + hw, cy + hh, cx - hw, cy + hh), L(cx - hw, cy + hh, cx - hw, cy - hh)]
    return [L(cx - hw + r, cy - hh, cx + hw - r, cy - hh), A(cx + hw - r, cy - hh + r, r, 270, 360),
            L(cx + hw, cy - hh + r, cx + hw, cy + hh - r), A(cx + hw - r, cy + hh - r, r, 0, 90),
            L(cx + hw - r, cy + hh, cx - hw + r, cy + hh), A(cx - hw + r, cy + hh - r, r, 90, 180),
            L(cx - hw, cy + hh - r, cx - hw, cy - hh + r), A(cx - hw + r, cy - hh + r, r, 180, 270)]


def polyline(pts, close=True):
    s = [L(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]) for i in range(len(pts) - 1)]
    if close:
        s.append(L(pts[-1][0], pts[-1][1], pts[0][0], pts[0][1]))
    return s


def hull(points):
    pts = sorted(set((round(p[0], 6), round(p[1], 6)) for p in points))
    def cross(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def circle_pts(cx, cy, r, step=1.0):
    return [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in [i * step for i in range(int(360 / step))]]


# ---------------- DXF (R12, entities only) -----------------------------------------
class DXF:
    def __init__(self):
        self.ents = []

    def segs(self, segs, layer='OUTLINE', ox=0.0, oy=0.0):
        for g in segs:
            if g[0] == 'L':
                self.ents.append(('LINE', layer, g[1] + ox, g[2] + oy, g[3] + ox, g[4] + oy))
            elif g[0] == 'C':
                self.ents.append(('CIRCLE', layer, g[1] + ox, g[2] + oy, g[3]))
            elif g[0] == 'A':
                self.ents.append(('ARC', layer, g[1] + ox, g[2] + oy, g[3], g[4] % 360, g[5] % 360 if g[5] % 360 else 360))

    def text(self, x, y, h, t, layer='NOTES'):
        self.ents.append(('TEXT', layer, x, y, h, t))

    def dumps(self):
        o = ['0', 'SECTION', '2', 'HEADER', '9', '$INSUNITS', '70', '4', '0', 'ENDSEC',
             '0', 'SECTION', '2', 'ENTITIES']
        for e in self.ents:
            k = e[0]
            if k == 'LINE':
                o += ['0', 'LINE', '8', e[1], '10', fmt(e[2]), '20', fmt(e[3]), '30', '0', '11', fmt(e[4]), '21', fmt(e[5]), '31', '0']
            elif k == 'CIRCLE':
                o += ['0', 'CIRCLE', '8', e[1], '10', fmt(e[2]), '20', fmt(e[3]), '30', '0', '40', fmt(e[4])]
            elif k == 'ARC':
                o += ['0', 'ARC', '8', e[1], '10', fmt(e[2]), '20', fmt(e[3]), '30', '0', '40', fmt(e[4]), '50', fmt(e[5]), '51', fmt(e[6])]
            elif k == 'TEXT':
                o += ['0', 'TEXT', '8', e[1], '10', fmt(e[2]), '20', fmt(e[3]), '30', '0', '40', fmt(e[4]), '1', str(e[5])]
        o += ['0', 'ENDSEC', '0', 'EOF']
        return '\n'.join(o) + '\n'


# ---------------- sheet ---------------------------------------------------------------
STYLE = """
.vis{stroke:#000;stroke-width:.5;fill:none;stroke-linecap:round;stroke-linejoin:round}
.thick{stroke:#000;stroke-width:.7;fill:none}
.thin{stroke:#000;stroke-width:.25;fill:none}
.hid{stroke:#000;stroke-width:.3;fill:none;stroke-dasharray:2.4 1.2}
.ctr{stroke:#000;stroke-width:.18;fill:none;stroke-dasharray:7 1.2 1.2 1.2}
.ph{stroke:#000;stroke-width:.25;fill:none;stroke-dasharray:8 1.2 1.2 1.2 1.2 1.2}
.dim{stroke:#000;stroke-width:.18;fill:none}
.arr{fill:#000;stroke:none}
.sec{fill:url(#hatch);stroke:#000;stroke-width:.5}
.ko{fill:#fff;stroke:none}
.cut{stroke:#000;stroke-width:.7;fill:none;stroke-dasharray:9 1.5 1.5 1.5}
.box{stroke:#000;stroke-width:.35;fill:none}
.fillw{fill:#fff;stroke:#000;stroke-width:.35}
.solidbk{fill:#000}
text{font-family:%s;fill:#000}
""" % FONT


class Sheet:
    W, H = 420.0, 297.0

    def __init__(self, no, title, scale='1:1', material='', finish='', qty='', notes=(), sub=''):
        self.no, self.title, self.scale, self.material, self.finish, self.qty = no, title, scale, material, finish, qty
        self.notes = list(notes)
        self.sub = sub
        self.el = []
        self.extra_defs = []
        self.index = 0
        self.total = 0

    def add(self, s): self.el.append(s)

    def line(self, x1, y1, x2, y2, c='vis'):
        self.add('<line x1="%.3f" y1="%.3f" x2="%.3f" y2="%.3f" class="%s"/>' % (x1, y1, x2, y2, c))

    def rect(self, x, y, w, h, c='vis'):
        self.add('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" class="%s"/>' % (x, y, w, h, c))

    def circle(self, x, y, r, c='vis'):
        self.add('<circle cx="%.3f" cy="%.3f" r="%.3f" class="%s"/>' % (x, y, r, c))

    def path(self, d, c='vis'):
        self.add('<path d="%s" class="%s"/>' % (d, c))

    def polygon(self, pts, c='vis'):
        self.add('<polygon points="%s" class="%s"/>' % (' '.join('%.3f,%.3f' % p for p in pts), c))

    def text(self, x, y, t, size=3.2, anchor='start', rot=0, weight='normal', italic=False):
        tr = ' transform="rotate(%.2f %.3f %.3f)"' % (rot, x, y) if rot else ''
        st = ' font-style="italic"' if italic else ''
        self.add('<text x="%.3f" y="%.3f" font-size="%.2f" text-anchor="%s" font-weight="%s"%s%s>%s</text>' % (x, y, size, anchor, weight, st, tr, esc(t)))

    def arrow(self, x, y, ang):
        Lh, Wh = 2.8, 0.6
        bx, by = x - Lh * math.cos(ang), y - Lh * math.sin(ang)
        px, py = -math.sin(ang) * Wh, math.cos(ang) * Wh
        self.add('<path d="M%.3f %.3f L%.3f %.3f L%.3f %.3f Z" class="arr"/>' % (x, y, bx + px, by + py, bx - px, by - py))

    def wrap(self, t, width_mm, size):
        cw = size * 0.55
        n = max(10, int(width_mm / cw))
        out, cur = [], ''
        for w in t.split(' '):
            if len(cur) + len(w) + 1 > n and cur:
                out.append(cur)
                cur = w
            else:
                cur = (cur + ' ' + w).strip()
        if cur:
            out.append(cur)
        return out

    def table(self, x, y, cols, rows, size=2.8, rh=5.0, head=True, bold_first_col=False):
        """cols: list of (title, width, align). rows: list of lists of strings."""
        tw = sum(c[1] for c in cols)
        n = len(rows) + (1 if head else 0)
        self.rect(x, y, tw, n * rh, 'box')
        yy = y
        if head:
            self.rect(x, y, tw, rh, 'box')
            cx = x
            for (t, w, al) in cols:
                self.text(cx + (w / 2 if al == 'middle' else 1.2 if al == 'start' else w - 1.2), yy + rh - 1.5, t, size * 0.92, al, weight='bold')
                cx += w
            yy += rh
        for r in rows:
            self.line(x, yy, x + tw, yy, 'thin')
            cx = x
            for i, ((t, w, al), val) in enumerate(zip(cols, r)):
                self.text(cx + (w / 2 if al == 'middle' else 1.2 if al == 'start' else w - 1.2), yy + rh - 1.5, val, size, al,
                          weight='bold' if (bold_first_col and i == 0) else 'normal')
                cx += w
            yy += rh
        cx = x
        for (t, w, al) in cols[:-1]:
            cx += w
            self.line(cx, y, cx, y + n * rh, 'thin')
        return y + n * rh

    # ---- frame, title block, notes ----
    def frame(self):
        self.rect(10, 10, 400, 277, 'thick')
        # centring marks
        for x, y, x2, y2 in [(210, 5, 210, 10), (210, 287, 210, 292), (5, 148.5, 10, 148.5), (410, 148.5, 415, 148.5)]:
            self.line(x, y, x2, y2, 'vis')

    def title_block(self):
        x0, y0 = 230.0, 231.0
        self.rect(x0, y0, 180, 56, 'thick')
        def cell(x, y, w, h, label, val, size=3.2, weight='normal'):
            self.rect(x, y, w, h, 'box')
            self.text(x + 1.2, y + 2.6, label, 1.9)
            if val != '':
                self.text(x + 1.5, y + h - 1.6, val, size, weight=weight)
        cell(x0, y0, 110, 8, 'PROJECT', 'MagPress M4 · manual photo-magnet press', 3.0)
        cell(x0 + 110, y0, 30, 8, 'REVISION', 'D', 3.2, 'bold')
        cell(x0 + 140, y0, 40, 8, 'SHEET', '%d / %d' % (self.index, self.total), 3.2)
        self.rect(x0, y0 + 8, 180, 14, 'box')
        self.text(x0 + 1.2, y0 + 10.6, 'TITLE', 1.9)
        t = self.title
        sz = 6.0 if len(t) < 34 else 4.8
        self.text(x0 + 2, y0 + 19.5, t, sz, weight='bold')
        if self.sub:
            self.text(x0 + 178, y0 + 12, self.sub, 2.6, 'end')
        cell(x0, y0 + 22, 62, 10, 'DRAWING NO.', self.no, 4.2, 'bold')
        cell(x0 + 62, y0 + 22, 38, 10, 'QTY', self.qty, 3.2)
        cell(x0 + 100, y0 + 22, 30, 10, 'SCALE', self.scale, 3.2)
        cell(x0 + 130, y0 + 22, 50, 10, 'UNITS', 'mm', 3.2)
        cell(x0, y0 + 32, 180, 8, 'MATERIAL', self.material, 2.9)
        cell(x0, y0 + 40, 180, 8, 'HEAT TREATMENT / FINISH', self.finish, 2.9)
        cell(x0, y0 + 48, 62, 8, 'GENERAL TOLERANCES', 'ISO 2768-mK', 3.0)
        # projection symbol: first angle
        self.rect(x0 + 62, y0 + 48, 30, 8, 'box')
        px, py = x0 + 66, y0 + 52
        self.polygon([(px, py - 2.6), (px + 9, py - 1.5), (px + 9, py + 1.5), (px, py + 2.6)], 'vis')
        self.line(px - 1, py, px + 10, py, 'ctr')
        self.circle(px + 16, py, 2.6, 'vis')
        self.circle(px + 16, py, 1.5, 'vis')
        self.line(px + 12.5, py, px + 19.5, py, 'ctr')
        self.text(x0 + 89.5, y0 + 55, '1st', 1.9, 'end')
        cell(x0 + 92, y0 + 48, 30, 8, 'DATE', '2026-10-27', 2.6)
        cell(x0 + 122, y0 + 48, 29, 8, 'DRAWN', '', 2.6)
        cell(x0 + 151, y0 + 48, 29, 8, 'CHECKED', '', 2.6)

    def notes_box(self):
        x0, y0, w, h = 10.0, 231.0, 218.0, 56.0
        self.rect(x0, y0, w, h, 'box')
        self.text(x0 + 2, y0 + 5, 'NOTES', 3.0, weight='bold')
        y = y0 + 9.6
        size = 2.55
        for i, n in enumerate(self.notes, 1):
            lines = self.wrap(n, w - 10, size)
            for j, ln in enumerate(lines):
                if y > y0 + h - 1.5:
                    break
                self.text(x0 + 2, y, ('%d.' % i) if j == 0 else '', size)
                self.text(x0 + 6.5, y, ln, size)
                y += size * 1.42

    def svg(self):
        self.frame()
        self.title_block()
        if self.notes:
            self.notes_box()
        defs = ('<defs><pattern id="hatch" patternUnits="userSpaceOnUse" width="1.8" height="1.8" patternTransform="rotate(45)">'
                '<rect width="1.8" height="1.8" fill="#fff"/><line x1="0" y1="0" x2="0" y2="1.8" stroke="#000" stroke-width="0.16"/></pattern>'
                '<pattern id="hatch2" patternUnits="userSpaceOnUse" width="1.8" height="1.8" patternTransform="rotate(-45)">'
                '<rect width="1.8" height="1.8" fill="#fff"/><line x1="0" y1="0" x2="0" y2="1.8" stroke="#000" stroke-width="0.16"/></pattern>'
                + ''.join(self.extra_defs) + '</defs>')
        return ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="420mm" height="297mm" viewBox="0 0 420 297">'
                '<style>%s</style>%s<rect width="420" height="297" fill="#fff"/>%s</svg>') % (STYLE, defs, ''.join(self.el))


# ---------------- view with part->paper transform --------------------------------------
class View:
    def __init__(self, sh, ox, oy, scale, label=None, lx=None, ly=None):
        self.sh, self.ox, self.oy = sh, ox, oy
        self.k = 1.0 / scale
        if label:
            sh.text(lx, ly, label, 3.4, 'middle', weight='bold')

    def P(self, u, w):
        return self.ox + u * self.k, self.oy - w * self.k

    def segs(self, segs, c='vis'):
        for g in segs:
            if g[0] == 'L':
                x1, y1 = self.P(g[1], g[2]); x2, y2 = self.P(g[3], g[4])
                self.sh.line(x1, y1, x2, y2, c)
            elif g[0] == 'C':
                x, y = self.P(g[1], g[2]); self.sh.circle(x, y, g[3] * self.k, c)
            elif g[0] == 'A':
                cx, cy, r, a0, a1 = g[1:]
                x0, y0 = self.P(cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0)))
                x1, y1 = self.P(cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1)))
                span = (a1 - a0) % 360
                if abs(span) < 1e-9:
                    span = 360
                R = r * self.k
                self.sh.path('M%.3f %.3f A%.3f %.3f 0 %d 0 %.3f %.3f' % (x0, y0, R, R, 1 if span > 180 else 0, x1, y1), c)

    def line(self, u0, w0, u1, w1, c='vis'):
        x0, y0 = self.P(u0, w0); x1, y1 = self.P(u1, w1); self.sh.line(x0, y0, x1, y1, c)

    def rect(self, u0, w0, u1, w1, c='vis'):
        x0, y0 = self.P(min(u0, u1), max(w0, w1))
        self.sh.rect(x0, y0, abs(u1 - u0) * self.k, abs(w1 - w0) * self.k, c)

    def poly(self, pts, c='vis'):
        self.sh.polygon([self.P(*p) for p in pts], c)

    def circle(self, u, w, r, c='vis'):
        x, y = self.P(u, w); self.sh.circle(x, y, r * self.k, c)

    def thread_arc(self, u, w, r):
        x, y = self.P(u, w); R = r * self.k
        self.sh.path('M%.3f %.3f A%.3f %.3f 0 1 0 %.3f %.3f' % (x + R, y, R, R, x, y - R), 'thin')

    def cmark(self, u, w, r, ext=1.8):
        x, y = self.P(u, w); e = r * self.k + ext
        self.sh.line(x - e, y, x + e, y, 'ctr'); self.sh.line(x, y - e, x, y + e, 'ctr')

    def cl_h(self, u0, u1, w):
        self.line(u0, w, u1, w, 'ctr')

    def cl_v(self, w0, w1, u):
        self.line(u, w0, u, w1, 'ctr')

    def text(self, u, w, t, size=3.0, anchor='middle', dx=0, dy=0, rot=0, weight='normal'):
        x, y = self.P(u, w); self.sh.text(x + dx, y + dy, t, size, anchor, rot, weight)

    # ---- dimensions ----
    def hdim(self, u1, w1, u2, w2, wd, text=None, size=3.0, prefix='', suffix=''):
        sh = self.sh
        x1, y1 = self.P(u1, w1); x2, y2 = self.P(u2, w2); _, yd = self.P(0, wd)
        for (x, y) in ((x1, y1), (x2, y2)):
            sgn = 1 if yd > y else -1
            if abs(yd - y) > 1.2:
                sh.line(x, y + sgn * 1.0, x, yd + sgn * 1.5, 'dim')
        if x2 < x1:
            x1, x2 = x2, x1
        t = prefix + (text if text is not None else fmt(abs(u2 - u1))) + suffix
        span = x2 - x1
        tw = len(t) * size * 0.56
        if span >= 7.5:
            sh.line(x1, yd, x2, yd, 'dim'); sh.arrow(x1, yd, math.pi); sh.arrow(x2, yd, 0)
        else:
            sh.line(x1 - 5, yd, x2 + 5, yd, 'dim'); sh.arrow(x1, yd, 0); sh.arrow(x2, yd, math.pi)
        if tw + 4 < span:
            sh.text((x1 + x2) / 2, yd - 1.0, t, size, 'middle')
        else:
            sh.text(x2 + (6 if span < 7.5 else 1.5), yd - 1.0, t, size, 'start')

    def vdim(self, w1, u1, w2, u2, ud, text=None, size=3.0, prefix='', suffix=''):
        sh = self.sh
        x1, y1 = self.P(u1, w1); x2, y2 = self.P(u2, w2); xd, _ = self.P(ud, 0)
        for (x, y) in ((x1, y1), (x2, y2)):
            sgn = 1 if xd > x else -1
            if abs(xd - x) > 1.2:
                sh.line(x + sgn * 1.0, y, xd + sgn * 1.5, y, 'dim')
        if y2 < y1:
            y1, y2 = y2, y1
        t = prefix + (text if text is not None else fmt(abs(w2 - w1))) + suffix
        span = y2 - y1
        tw = len(t) * size * 0.56
        if span >= 7.5:
            sh.line(xd, y1, xd, y2, 'dim'); sh.arrow(xd, y1, -math.pi / 2); sh.arrow(xd, y2, math.pi / 2)
        else:
            sh.line(xd, y1 - 5, xd, y2 + 5, 'dim'); sh.arrow(xd, y1, math.pi / 2); sh.arrow(xd, y2, -math.pi / 2)
        if tw + 4 < span:
            sh.text(xd - 1.0, (y1 + y2) / 2, t, size, 'middle', rot=-90)
        else:
            sh.text(xd - 1.0, y1 - (6 if span < 7.5 else 1.5), t, size, 'start', rot=-90)

    def adim(self, u0, w0, r, a0, a1, text, size=3.0):
        """angular dimension: arc of radius r (paper mm) about part point."""
        x, y = self.P(u0, w0)
        p0 = (x + r * math.cos(math.radians(-a0)), y + r * math.sin(math.radians(-a0)))
        p1 = (x + r * math.cos(math.radians(-a1)), y + r * math.sin(math.radians(-a1)))
        large = 1 if (a1 - a0) % 360 > 180 else 0
        self.sh.path('M%.3f %.3f A%.3f %.3f 0 %d 0 %.3f %.3f' % (p0[0], p0[1], r, r, large, p1[0], p1[1]), 'dim')
        self.sh.arrow(p0[0], p0[1], math.radians(-a0) + math.pi / 2)
        self.sh.arrow(p1[0], p1[1], math.radians(-a1) - math.pi / 2)
        am = math.radians(-(a0 + a1) / 2)
        self.sh.text(x + (r + 2.5) * math.cos(am), y + (r + 2.5) * math.sin(am) + 1, text, size, 'middle')

    def leader(self, u, w, dx, dy, text, size=2.8, on_circle_r=None, ang=None):
        """Leader from a part point (optionally from circle edge) to text at paper offset (dx,dy)."""
        x, y = self.P(u, w)
        if on_circle_r is not None:
            a = math.atan2(dy, dx) if ang is None else ang
            x, y = x + on_circle_r * self.k * math.cos(a), y + on_circle_r * self.k * math.sin(a)
            tx, ty = self.P(u, w)[0] + dx, self.P(u, w)[1] + dy
        else:
            tx, ty = x + dx, y + dy
        self.sh.line(x, y, tx, ty, 'dim')
        self.sh.arrow(x, y, math.atan2(y - ty, x - tx))
        lines = text.split('\n')
        right = dx >= 0
        tw = max(len(l) for l in lines) * size * 0.56
        sx = tx + (tw + 1.5 if right else -(tw + 1.5))
        self.sh.line(tx, ty, sx, ty, 'dim')
        for i, ln in enumerate(lines):
            self.sh.text(tx + (1.0 if right else -1.0), ty - 0.9 + i * size * 1.3, ln, size, 'start' if right else 'end')

    def label(self, u, w, t, dx=2.0, dy=-2.0, size=2.3):
        x, y = self.P(u, w); self.sh.text(x + dx, y + dy, t, size, 'start')

    def section_mark(self, u0, w0, u1, w1, name, flip=False):
        """cutting plane line with arrows (arrows show viewing direction)."""
        x0, y0 = self.P(u0, w0); x1, y1 = self.P(u1, w1)
        self.sh.line(x0, y0, x1, y1, 'cut')
        ang = math.atan2(y1 - y0, x1 - x0)
        nx, ny = -math.sin(ang), math.cos(ang)
        if flip:
            nx, ny = -nx, -ny
        for (x, y) in ((x0, y0), (x1, y1)):
            self.sh.line(x, y, x + nx * 6, y + ny * 6, 'thick')
            self.sh.arrow(x + nx * 6, y + ny * 6, math.atan2(ny, nx))
            self.sh.text(x + nx * 9 + (2 if x == x1 else -2) * math.cos(ang), y + ny * 9 + 1.2, name, 3.8, 'middle', weight='bold')


# ---------------- plate parts: plan view + sections from a feature list ----------------
def feat(x, z, kind, **kw):
    d = {'x': x, 'z': z, 'kind': kind}
    d.update(kw)
    return d


def draw_plan_features(v, feats, flipz=True):
    """plan view: u = x, w = -z (front at bottom) when flipz."""
    for f in feats:
        u, w = f['x'], (-f['z'] if flipz else f['z'])
        k = f['kind']
        side = f.get('side', 'top')
        thru = f.get('thru', False)
        vis = 'vis' if (side == 'top' or thru) else 'hid'
        if k == 'hole':
            v.circle(u, w, f['d'] / 2, vis)
            if f.get('cb'):
                v.circle(u, w, f['cb'][0] / 2, 'vis' if side == 'top' else 'hid')
            if f.get('csk'):
                v.circle(u, w, f['csk'] / 2, 'vis' if side == 'top' else 'hid')
            v.cmark(u, w, max(f['d'], f.get('cb', (0,))[0] if f.get('cb') else 0) / 2)
        elif k == 'tap':
            M = f['m']
            if side == 'top' or thru:
                v.circle(u, w, MINOR[M] / 2, 'vis'); v.thread_arc(u, w, MAJOR[M] / 2)
            else:
                v.circle(u, w, MINOR[M] / 2, 'hid')
            v.cmark(u, w, MAJOR[M] / 2)
        elif k == 'spot':
            v.circle(u, w, f['d'] / 2, 'vis'); v.cmark(u, w, f['d'] / 2)
        elif k == 'rr':
            v.segs(rrect(u, w, f['w'], f['h'], f['r']), vis)
        if f.get('label'):
            v.label(u, w, f['label'], dx=f.get('ldx', 1.6), dy=f.get('ldy', -1.6))


def interval_at(f, c, axis):
    """intersection of a feature with a cutting line. axis='x' means cut along x at z=c (returns x-interval)."""
    k = f['kind']
    if axis == 'x':
        along, across = f['x'], f['z']
    else:
        along, across = f['z'], f['x']
    def circ(rad):
        dd = abs(across - c)
        if dd >= rad: return None
        h = math.sqrt(rad * rad - dd * dd); return (along - h, along + h)
    if k == 'hole':
        out = {'main': circ(f['d'] / 2)}
        if f.get('cb'): out['cb'] = circ(f['cb'][0] / 2)
        if f.get('csk'): out['csk'] = circ(f['csk'] / 2)
        return out if out['main'] else None
    if k == 'tap':
        a = circ(MAJOR[f['m']] / 2)
        if not a: return None
        return {'major': a, 'minor': circ(MINOR[f['m']] / 2) or a}
    if k == 'spot':
        a = circ(f['d'] / 2)
        return {'main': a} if a else None
    if k == 'rr':
        if axis == 'x':
            w, h = f['w'], f['h']
        else:
            w, h = f['h'], f['w']
        r = f['r']; dd = abs(across - c)
        if dd >= h / 2: return None
        if dd <= h / 2 - r:
            hw = w / 2
        else:
            e = dd - (h / 2 - r)
            hw = w / 2 - r + math.sqrt(max(0.0, r * r - e * e))
        return {'main': (along - hw, along + hw)}
    return None


def draw_section(v, solid, T, feats, c, axis='x', y0=0.0, flip_u=False, hatch='sec'):
    """Section of a plate of thickness T (part y from y0 to y0+T) through line c.
    v: view where u = along-coordinate, w = y. solid: list of (u0,u1) intervals of material."""
    sh = v.sh
    k = v.k
    def U(a): return -a if flip_u else a
    for (a, b) in solid:
        v.rect(U(a), y0, U(b), y0 + T, hatch)
    knocks = []
    for f in feats:
        it = interval_at(f, c, axis)
        if not it:
            continue
        side = f.get('side', 'top')
        thru = f.get('thru', False)
        kind = f['kind']
        if kind in ('hole', 'spot', 'rr'):
            a, b = it['main']
            if kind == 'spot':
                depth = f.get('depth', 1.5)
            else:
                depth = T if thru else f.get('depth', T)
            if side == 'top':
                ya, yb = y0 + T - depth, y0 + T
            else:
                ya, yb = y0, y0 + depth
            knocks.append((a, b, ya, yb, side, thru or depth >= T))
            if f.get('cb') and it.get('cb'):
                ca, cb_ = it['cb']; cd = f['cb'][1]
                cside = f.get('cbside', side if not thru else 'top')
                if cside == 'top':
                    knocks.append((ca, cb_, y0 + T - cd, y0 + T, 'top', False))
                else:
                    knocks.append((ca, cb_, y0, y0 + cd, 'bot', False))
            if f.get('csk') and it.get('csk'):
                ca, cb_ = it['csk']; dep = (f['csk'] - f['d']) / 2.0
                knocks.append(('csk', ca, cb_, a, b, y0 + T, y0 + T - dep))
        elif kind == 'tap':
            ma, mb = it['major']; na, nb = it['minor']
            depth = T if thru else f.get('depth', T)
            if side == 'top':
                ya, yb = y0 + T - depth, y0 + T
                dya, dyb = y0 + T - min(T, depth + MAJOR[f['m']] * 0.5), y0 + T
            else:
                ya, yb = y0, y0 + depth
                dya, dyb = y0, y0 + min(T, depth + MAJOR[f['m']] * 0.5)
            knocks.append(('tap', na, nb, ma, mb, ya, yb, dya, dyb, thru or depth >= T, side))
    # knockouts
    for kn in knocks:
        if kn[0] == 'csk':
            _, ca, cb_, a, b, ytop, ybot = kn
            pts = [v.P(U(ca), ytop + 0.3), v.P(U(cb_), ytop + 0.3), v.P(U(b), ybot), v.P(U(a), ybot)]
            sh.polygon(pts, 'ko')
            v.line(U(ca), ytop, U(a), ybot); v.line(U(cb_), ytop, U(b), ybot)
        elif kn[0] == 'tap':
            _, na, nb, ma, mb, ya, yb, dya, dyb, full, side = kn
            x0, ytop = v.P(U(na), dyb); x1, ybot = v.P(U(nb), dya)
            sh.rect(min(x0, x1), ytop - (0.4 if side == 'top' or full else 0), abs(x1 - x0), (ybot - ytop) + (0.8 if full else 0.4), 'ko')
            v.line(U(na), dya, U(na), dyb); v.line(U(nb), dya, U(nb), dyb)
            v.line(U(ma), ya, U(ma), yb, 'thin'); v.line(U(mb), ya, U(mb), yb, 'thin')
            if not full:
                yend = dya if side == 'top' else dyb
                v.line(U(na), yend, U(nb), yend)
                v.line(U(ma), ya if side == 'top' else yb, U(mb), ya if side == 'top' else yb)
        else:
            a, b, ya, yb, side, full = kn
            x0, ytop = v.P(U(a), yb); x1, ybot = v.P(U(b), ya)
            ext_t = 0.4 if (side == 'top' or full) else 0
            ext_b = 0.4 if (side == 'bot' or full) else 0
            sh.rect(min(x0, x1), ytop - ext_t, abs(x1 - x0), (ybot - ytop) + ext_t + ext_b, 'ko')
            v.line(U(a), ya, U(a), yb); v.line(U(b), ya, U(b), yb)
            if not full:
                yy = ya if side == 'top' else yb
                v.line(U(a), yy, U(b), yy)
    # re-stroke outer top/bottom edges where material is
    return knocks


def solid_minus_thru(extent, feats, c, axis='x'):
    """subtract through features from an extent interval list (for sections)."""
    ivs = [list(extent)]
    for f in feats:
        if not (f.get('thru') or (f['kind'] == 'rr' and f.get('thru'))):
            continue
        it = interval_at(f, c, axis)
        if not it:
            continue
        a, b = it.get('main') or it.get('minor')
        new = []
        for (p, q) in ivs:
            if b <= p or a >= q:
                new.append([p, q])
            else:
                if a > p: new.append([p, a])
                if b < q: new.append([b, q])
        ivs = new
    return [tuple(i) for i in ivs]


def feats_dxf(dx, feats, flipz=True, layer='HOLES'):
    for f in feats:
        u, w = f['x'], (-f['z'] if flipz else f['z'])
        if f['kind'] == 'hole':
            dx.segs([C(u, w, f['d'] / 2)], layer)
            if f.get('cb'): dx.segs([C(u, w, f['cb'][0] / 2)], 'COUNTERBORE')
        elif f['kind'] == 'tap':
            dx.segs([C(u, w, MINOR[f['m']] / 2)], 'TAP_DRILL')
        elif f['kind'] == 'spot':
            dx.segs([C(u, w, f['d'] / 2)], 'SPOT')
        elif f['kind'] == 'rr':
            dx.segs(rrect(u, w, f['w'], f['h'], f['r']), 'POCKET' if not f.get('thru') else 'OUTLINE')
