/* MagPress magnet studio: frame / outline styles (cat 'frame').

   Written against web/studio/core.js: units are mm, origin at the face centre, y down, the context is
   already clipped to the paper cut outline. Every style scales its line widths and features with g.k
   and works on rectangles (portrait and landscape) and rounds. Colours come from p.accent / p.ink /
   p.paper (paper = the border / white colour); randomness only through h.rng(p.seed).
*/
(function(){
  'use strict';
  const PI = Math.PI, TAU = 2 * PI, OUT = 9;   // OUT: an outline this far outside the face covers the whole bleed
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const reg = (id, name, draw) => MS.register({ id: 'frame.' + id, cat: 'frame', name, draw });

  // ---------- colour ----------
  const hexRGB = c => { c = String(c || '#000').replace('#', ''); if(c.length === 3) c = c.split('').map(x => x + x).join('');
    return [0, 2, 4].map(i => parseInt(c.substr(i, 2), 16) || 0); };
  const toHex = a => '#' + a.map(v => clamp(Math.round(v), 0, 255).toString(16).padStart(2, '0')).join('');
  function rgb2hsl(c){ let [r, g, b] = c.map(v => v / 255); const mx = Math.max(r, g, b), mn = Math.min(r, g, b), l = (mx + mn) / 2; let hh = 0, s = 0;
    if(mx !== mn){ const d = mx - mn; s = l > 0.5 ? d / (2 - mx - mn) : d / (mx + mn);
      hh = (mx === r ? (g - b) / d + (g < b ? 6 : 0) : mx === g ? (b - r) / d + 2 : (r - g) / d + 4) / 6; }
    return [hh * 360, s, l]; }
  function hsl2hex(hh, s, l){ hh = ((hh % 360) + 360) % 360 / 30; const a = s * Math.min(l, 1 - l);
    const f = n => { const q = (n + hh) % 12; return 255 * (l - a * Math.max(-1, Math.min(q - 3, 9 - q, 1))); };
    return toHex([f(0), f(8), f(4)]); }
  // the accent turned round the colour wheel by `deg`, kept in a printable saturation / lightness range
  const turn = (c, deg, l, s) => { const [hh, ss, ll] = rgb2hsl(hexRGB(c)); return hsl2hex(hh + deg, s == null ? clamp(ss, 0.4, 0.85) : s, l == null ? clamp(ll, 0.38, 0.62) : l); };
  // a dark colour for vignettes / film: the ink when it is dark, else near-black
  const darkOf = (p, h) => h.lum(p.ink) < 0.12 ? h.mix(p.ink, '#000000', 0.35) : '#121212';

  // ---------- paths ----------
  // outline `d` mm in from the face (negative = out into the bleed); rect corner radius rr (default: concentric with the face)
  const ol = (g, h, d, rr) => h.shapePath(g.W - 2 * d, g.H - 2 * d, g.round ? 0 : Math.max(0, rr == null ? g.r - d : rr), g.round);
  const big = (g, h) => ol(g, h, -OUT);
  // several outlines in one path, for 'evenodd' bands and clips
  const eo = (...ps) => { const P = new Path2D(); ps.forEach(q => P.addPath(q)); return P; };
  const M = (x, y, rot, sx, sy) => { let m = new DOMMatrix().translate(x, y); if(rot) m = m.rotate(rot * 180 / PI); if(sx != null) m = m.scale(sx, sy == null ? sx : sy); return m; };
  const rrect = (h, cx, cy, w, hh, r) => { const P = new Path2D(); P.addPath(h.shapePath(w, hh, r, false), M(cx, cy)); return P; };
  const poly = (pts, P) => { P = P || new Path2D(); pts.forEach((q, i) => i ? P.lineTo(q[0], q[1]) : P.moveTo(q[0], q[1])); P.closePath(); return P; };
  const rotQ = (x, y, s) => s === 0 ? [x, y] : s === 1 ? [-y, x] : s === 2 ? [-x, -y] : [y, -x];

  // Points round the outline `d` in (rect corner radius rr), clockwise. Rect: a point at the middle of every
  // corner and each side divided evenly between them, so the four corners match; round: n a multiple of
  // o.mult (4), starting at o.start (top). fn(x, y, tangentAngle, i, n, isCorner, side, j). o.offset 0.5 = between.
  function walk(g, d, rr, step, fn, o){
    o = o || {}; const off = o.offset || 0, even = !!o.even;
    if(g.round){ const R = g.W / 2 - d, m = o.mult || 4, n = m * Math.max(1, Math.round(TAU * R / step / m)), a0 = o.start == null ? -PI / 2 : o.start;
      for(let i = 0; i < n; i++){ const a = a0 + TAU * (i + off) / n; fn(R * Math.cos(a), R * Math.sin(a), a + PI / 2, i, n, !off && i % (n / m) === 0, Math.floor(i * m / n), i % (n / m)); }
      return n; }
    const A = g.W / 2 - d, B = g.H / 2 - d; rr = clamp(rr == null ? g.r - d : rr, 0, Math.min(A, B));
    const q8 = PI * rr / 4, sides = []; let total = 0, i = 0;
    for(let s = 0; s < 4; s++){ const L = s % 2 ? B : A, D = s % 2 ? A : B, st = 2 * (L - rr), len = st + 2 * q8;
      const n = even ? 2 * Math.max(1, Math.round(len / step / 2)) : Math.max(1, Math.round(len / step)); sides.push({ L, D, st, len, n }); total += n; }
    sides.forEach((S, s) => { for(let j = 0; j < S.n; j++){ const t = S.len * (j + off) / S.n; let x, y, a;
      if(t < q8 && rr > 0){ const th = -3 * PI / 4 + t / rr; x = -S.L + rr + rr * Math.cos(th); y = -S.D + rr + rr * Math.sin(th); a = th + PI / 2; }
      else if(t <= q8 + S.st){ x = -S.L + rr + (t - q8); y = -S.D; a = t === 0 ? -PI / 4 : 0; }
      else { const th = -PI / 2 + (t - q8 - S.st) / rr; x = S.L - rr + rr * Math.cos(th); y = -S.D + rr + rr * Math.sin(th); a = th + PI / 2; }
      const q = rotQ(x, y, s); fn(q[0], q[1], a + s * PI / 2, i++, total, !off && j === 0, s, j); } });
    return total;
  }
  // inward unit normal for a tangent angle (clockwise walk, y down)
  const inN = a => [-Math.sin(a), Math.cos(a)];

  // smooth periodic noise on [0, 1): Catmull-Rom through n random values in -1…1
  function loopNoise(rand, n){ const v = []; for(let i = 0; i < n; i++) v.push(rand() * 2 - 1);
    return t => { t = ((t % 1) + 1) % 1 * n; const i = Math.floor(t), f = t - i, p0 = v[(i - 1 + n) % n], p1 = v[i % n], p2 = v[(i + 1) % n], p3 = v[(i + 2) % n];
      return 0.5 * (2 * p1 + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f + (-p0 + 3 * p1 - 3 * p2 + p3) * f * f * f); }; }
  // points of the outline `d` in, every `step` mm: [{x, y, a, t}]
  function ptsOf(g, d, rr, step){ const out = []; walk(g, d, rr, step, (x, y, a, i, n) => out.push({ x, y, a, t: i / n })); return out; }
  // a closed path through those points pushed inward by disp(pt, i) mm
  function displaced(pts, disp){ const P = new Path2D();
    pts.forEach((q, i) => { const o = disp(q, i), nx = -Math.sin(q.a) * o, ny = Math.cos(q.a) * o; i ? P.lineTo(q.x + nx, q.y + ny) : P.moveTo(q.x + nx, q.y + ny); });
    P.closePath(); return P; }

  // cubic Bézier chain [x0,y0, c1x,c1y, c2x,c2y, x1,y1, …] mapped through map(x, y) → [X, Y], appended as a polyline
  function chain(P, c, map, close, seg){ seg = seg || 10; let q = map(c[0], c[1]); P.moveTo(q[0], q[1]);
    for(let i = 2; i + 5 < c.length; i += 6){ const x0 = c[i - 2], y0 = c[i - 1];
      for(let j = 1; j <= seg; j++){ const t = j / seg, u = 1 - t, A = u * u * u, B = 3 * u * u * t, C = 3 * u * t * t, D = t * t * t;
        q = map(A * x0 + B * c[i] + C * c[i + 2] + D * c[i + 4], A * y0 + B * c[i + 1] + C * c[i + 3] + D * c[i + 5]); P.lineTo(q[0], q[1]); } }
    if(close) P.closePath(); }
  // a leaf / petal as a Bézier chain, base (bx,by) to tip (tx,ty), width w, `bulge` moves the widest point
  function leafC(bx, by, tx, ty, w, bulge){ const dx = tx - bx, dy = ty - by, L = Math.hypot(dx, dy) || 1, ux = dx / L, uy = dy / L, nx = -uy * w / 2, ny = ux * w / 2, b = bulge == null ? 0.35 : bulge;
    const P = (s, n) => [bx + dx * s + nx * n, by + dy * s + ny * n];
    return [bx, by, ...P(b - 0.15, 1.15), ...P(b + 0.45, 0.95), tx, ty, ...P(b + 0.45, -0.95), ...P(b - 0.15, -1.15), bx, by]; }
  // leaf straight into a Path2D: base (x, y), direction ang, length L, width w
  function leaf(P, x, y, ang, L, w){ const c = Math.cos(ang), s = Math.sin(ang), T = (u, v) => [x + u * c - v * s, y + u * s + v * c];
    let q = T(0, 0); P.moveTo(q[0], q[1]);
    const a = T(L * 0.25, -w * 0.62), b = T(L * 0.68, -w * 0.55), t = T(L, 0), e = T(L * 0.68, w * 0.55), f = T(L * 0.25, w * 0.62);
    P.bezierCurveTo(a[0], a[1], b[0], b[1], t[0], t[1]); P.bezierCurveTo(e[0], e[1], f[0], f[1], q[0], q[1]); P.closePath(); }
  // the shadow trick: only the (blurred) shadow of `path` lands on the canvas, the shape itself is drawn far outside the clip
  function shadowOnly(ctx, h, g, path, blur, color, rule){ const off = g.W + g.H + 60;
    ctx.save(); h.shadow(ctx, blur, color, -off, 0); ctx.translate(off, 0); ctx.fillStyle = '#000'; ctx.fill(path, rule || 'nonzero'); ctx.restore(); }
  // inner shadow just inside `win`, as if the border around it stood proud of the photo
  function innerShadow(ctx, h, g, win, blur, color, dy){ ctx.save(); ctx.clip(win); h.shadow(ctx, blur, color, 0, dy || 0);
    ctx.fillStyle = '#000'; ctx.fill(eo(big(g, h), win), 'evenodd'); ctx.restore(); }

  // ======================================================================= styles

  // ---- keyline: a thin paper line 2 mm in
  reg('keyline', 'Keyline', (ctx, g, p, h) => {
    const k = g.k; h.shadow(ctx, 0.5 * k, 'rgba(0,0,0,.35)', 0, 0.08 * k);
    ctx.lineWidth = 0.28 + 0.14 * k; ctx.strokeStyle = p.paper; ctx.stroke(ol(g, h, 2));
  });

  // ---- double: a thick-and-thin pair of paper rules
  reg('double', 'Double line', (ctx, g, p, h) => {
    const k = g.k, d1 = 1.6 + 0.2 * k, d2 = d1 + 1.3 * k; h.shadow(ctx, 0.5 * k, 'rgba(0,0,0,.35)', 0, 0.08 * k);
    ctx.strokeStyle = p.paper; ctx.lineWidth = 0.55 * k; ctx.stroke(ol(g, h, d1));
    ctx.lineWidth = 0.25 + 0.05 * k; ctx.stroke(ol(g, h, d2, Math.max(0.6, g.r - d2)));
  });

  // ---- matte: paper border with a bevelled, softly shadowed rounded window
  reg('matte', 'Matte border', (ctx, g, p, h) => {
    const k = g.k, m = 2.9 + 0.8 * k, rr = 2.4 * k, win = ol(g, h, m, rr);
    innerShadow(ctx, h, g, win, 1.3 * k, 'rgba(0,0,0,.42)', 0.3 * k);
    ctx.fillStyle = p.paper; ctx.fill(eo(big(g, h), win), 'evenodd');
    ctx.lineWidth = 0.45 * k; ctx.strokeStyle = h.mix(p.paper, '#000000', 0.1); ctx.stroke(ol(g, h, m - 0.22 * k, rr + 0.22 * k));
  });

  // ---- polaroid: paper border, much deeper at the bottom for a caption
  reg('polaroid', 'Polaroid', (ctx, g, p, h) => {
    const k = g.k, sd = 2.9 + 0.8 * k; let win;
    if(g.round){ const R = g.W / 2, Rw = R - sd, c = R * 0.4, al = Math.asin(c / Rw);
      win = new Path2D(); win.arc(0, 0, Rw, al, PI - al, true); win.closePath(); }
    else { const bot = Math.max(2.7 * sd, 0.19 * g.H), w = g.W - 2 * sd, hh = g.H - sd - bot;
      win = rrect(h, 0, -g.H / 2 + sd + hh / 2, w, hh, 0.5 * k); }
    innerShadow(ctx, h, g, win, 1.1 * k, 'rgba(0,0,0,.38)', 0.25 * k);
    ctx.fillStyle = p.paper; ctx.fill(eo(big(g, h), win), 'evenodd');
    ctx.lineWidth = 0.18 * k; ctx.strokeStyle = h.mix(p.paper, '#000000', 0.16); ctx.stroke(win);
  });

  // ---- inner-rounded: paper outside a generously rounded window rimmed with an accent line
  reg('inner-rounded', 'Rounded window', (ctx, g, p, h) => {
    const k = g.k, m = 2.6 + 0.6 * k, win = ol(g, h, m, 6.5 * k);
    ctx.fillStyle = p.paper; ctx.fill(eo(big(g, h), win), 'evenodd');
    ctx.lineWidth = 0.75 * k; ctx.strokeStyle = p.accent; ctx.stroke(win);
  });

  // ---- stitch: running stitches in paper-coloured thread
  reg('stitch', 'Stitched', (ctx, g, p, h) => {
    const k = g.k, d = 2.4 * k, step = 2.3 * k, len = 1.35 * k, P = new Path2D();
    walk(g, d, Math.max(1.6, g.r + 0.8 - d), step, (x, y, a) => { const c = Math.cos(a) * len / 2, s = Math.sin(a) * len / 2; P.moveTo(x - c, y - s); P.lineTo(x + c, y + s); });
    ctx.lineCap = 'round'; h.shadow(ctx, 0.45 * k, 'rgba(0,0,0,.55)', 0.08 * k, 0.14 * k);
    ctx.lineWidth = 0.5 * k; ctx.strokeStyle = p.paper; ctx.stroke(P);
  });

  // ---- filmstrip: dark bands with sprocket holes on the long sides (round: a dark ring with holes)
  reg('filmstrip', 'Film strip', (ctx, g, p, h) => {
    const k = g.k, dark = darkOf(p, h), bw = 5.3 * k, hc = 2.6 * k, hw = 1.75 * k, hl = 1.25 * k, pitch = 3.1 * k, hr = 0.28 * k, holes = new Path2D();
    let win;
    if(g.round){ win = ol(g, h, bw);
      walk(g, hc, 0, pitch, (x, y, a) => holes.addPath(h.shapePath(hl, hw, hr, false), M(x, y, a))); }
    else { const vert = g.H >= g.W, ws = vert ? bw : 2.3 * k, hs = vert ? 2.3 * k : bw, Lh = vert ? g.H : g.W;
      win = rrect(h, 0, 0, g.W - 2 * ws, g.H - 2 * hs, 0.8 * k);
      const n = Math.floor((Lh - 3.6 * k - hl) / pitch) + 1, s0 = -(n - 1) * pitch / 2;
      for(let i = 0; i < n; i++) for(const sg of [-1, 1]){ const u = s0 + i * pitch;
        holes.addPath(vert ? rrect(h, sg * (g.W / 2 - hc), u, hw, hl, hr) : rrect(h, u, sg * (g.H / 2 - hc), hl, hw, hr)); } }
    ctx.fillStyle = dark; ctx.fill(eo(big(g, h), win), 'evenodd');
    ctx.lineWidth = 0.2 * k; ctx.strokeStyle = 'rgba(255,255,255,.12)'; ctx.stroke(win);
    ctx.fillStyle = p.paper; ctx.fill(holes);
  });

  // ---- stamp: perforated postage-stamp edge on an accent backing, thin line round the picture
  reg('stamp', 'Postage stamp', (ctx, g, p, h) => {
    const k = g.k, e = 1.9 * k, ph = 0.78 * k, pitch = 2.35 * k, wi = e + 3.0 * k, cs = [];
    walk(g, e, 0, pitch, (x, y) => cs.push([x, y]));
    const S = new Path2D(), n = cs.length;
    cs.forEach((c, i) => { const pv = cs[(i - 1 + n) % n], nx = cs[(i + 1) % n];
      const a0 = Math.atan2(c[1] - pv[1], c[0] - pv[0]) + PI, sw = ((a0 - Math.atan2(nx[1] - c[1], nx[0] - c[0])) % TAU + TAU) % TAU;
      S.arc(c[0], c[1], ph, a0, a0 - sw, true); });
    S.closePath();
    const win = ol(g, h, wi, 0.4 * k);
    ctx.fillStyle = p.accent; ctx.fill(eo(big(g, h), S), 'evenodd');
    ctx.save(); h.shadow(ctx, 0.9 * k, 'rgba(0,0,0,.35)', 0.12 * k, 0.22 * k); ctx.fillStyle = p.paper; ctx.fill(eo(S, win), 'evenodd'); ctx.restore();
    ctx.lineWidth = 0.28 * k; ctx.strokeStyle = p.accent; ctx.stroke(ol(g, h, wi - 0.8 * k, 0.8 * k));
  });

  // ---- ornate: filigree corners on a fine line (round: a ring with four flourishes)
  // corner motif in corner units: the frame line's corner at 0,0, +x along the top edge, +y down the side
  const ORN_MAIN = [2.3, 2.3, 2.9, 1.25, 4.4, 0.85, 6.1, 1.1, 7.9, 1.4, 9.3, 2.2, 10.9, 1.7, 12.5, 1.2, 13.5, 2.4, 12.7, 3.25, 11.9, 4.0, 10.6, 3.5, 10.9, 2.65];
  const ORN_INNER = [2.3, 2.3, 3.7, 4.2, 6.1, 4.6, 7.4, 3.6, 8.2, 3.0, 7.7, 2.2, 7.0, 2.6];
  function ornCorner(S, F, map){
    for(const sw of [false, true]){ const m = sw ? (x, y) => map(y, x) : map;
      chain(S, ORN_MAIN, m); chain(S, ORN_INNER, m);
      chain(F, leafC(5.4, 1.2, 3.7, -0.15, 0.9, 0.4), m, true);
      chain(F, leafC(9.4, 2.15, 9.6, 4.6, 1.1, 0.35), m, true); }
    chain(F, leafC(2.0, 2.0, 6.6, 6.6, 1.5, 0.3), map, true);
    let q = map(1.0, 1.0); F.moveTo(q[0] + 0.01, q[1]); F.arc(q[0], q[1], 0.01, 0, TAU);
  }
  reg('ornate', 'Ornate corners', (ctx, g, p, h) => {
    const k = g.k, o = 2.0 * k, s = 0.95 * k, lw = 0.32 * k, S = new Path2D(), F = new Path2D(), D = new Path2D();
    const dot = (q, r) => { D.moveTo(q[0] + r, q[1]); D.arc(q[0], q[1], r, 0, TAU); };
    if(g.round){ const Rl = g.W / 2 - o;
      S.addPath(ol(g, h, o)); S.addPath(ol(g, h, o + 0.75 * k));
      for(let q = 0; q < 4; q++){ const a0 = -PI / 2 + q * PI / 2;
        for(const sg of [1, -1]){ const map = (u, v) => { const an = a0 + sg * (u - 2.3) * s / Rl, R = Rl - (v + 0.35) * s; return [R * Math.cos(an), R * Math.sin(an)]; };
          chain(S, ORN_MAIN, map); chain(S, ORN_INNER, map); chain(F, leafC(9.4, 2.15, 9.6, 4.6, 1.1, 0.35), map, true); }
        const mp = (u, v) => { const an = a0 + u * s / Rl, R = Rl - v * s; return [R * Math.cos(an), R * Math.sin(an)]; };
        chain(F, leafC(0, 1.6, 0, 6.6, 1.6, 0.3), mp, true); dot(mp(0, 0.2), 0.75 * s); }
    } else {
      S.addPath(ol(g, h, o, Math.max(0.5, g.r - o)));
      const ax = g.W / 2 - o, ay = g.H / 2 - o;
      for(const [sx, sy] of [[1, 1], [-1, 1], [1, -1], [-1, -1]]){
        const map = (x, y) => [-sx * ax + sx * x * s, -sy * ay + sy * y * s];
        ornCorner(S, F, map); dot(map(1.05, 1.05), 0.7 * s); dot(map(14.6, 1.0), 0.4 * s); dot(map(1.0, 14.6), 0.4 * s); }
    }
    ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.strokeStyle = h.rgba(p.paper, 0.85); ctx.fillStyle = h.rgba(p.paper, 0.85); ctx.lineWidth = lw + 0.7 * k;
    ctx.stroke(S); ctx.stroke(F); ctx.stroke(D); ctx.fill(F); ctx.fill(D);
    ctx.strokeStyle = p.accent; ctx.fillStyle = p.accent; ctx.lineWidth = lw; ctx.stroke(S); ctx.fill(F); ctx.fill(D);
  });

  // ---- vignette: soft darkened edges
  reg('vignette', 'Vignette', (ctx, g, p, h) => {
    const k = g.k, dark = h.lum(p.ink) < 0.3 ? h.mix(p.ink, '#000000', 0.5) : '#000000';
    shadowOnly(ctx, h, g, eo(big(g, h), ol(g, h, 1.0 * k, g.round ? 0 : 10 * k)), 7.5 * k, h.rgba(dark, 0.7), 'evenodd');
  });

  // ---- ring: thick accent band at the edge with a thin paper pinstripe inside it
  reg('ring', 'Ring band', (ctx, g, p, h) => {
    const k = g.k, bw = 3.7 * k, R0 = g.r + 1.6 * k;
    ctx.fillStyle = p.accent; ctx.fill(eo(big(g, h), ol(g, h, bw, R0 - bw)), 'evenodd');
    const d = bw - 0.95 * k; ctx.lineWidth = 0.42 * k; ctx.strokeStyle = p.paper; ctx.stroke(ol(g, h, d, R0 - d));
  });

  // ---- gradient-edge: accent fading inward from the edge
  reg('gradient-edge', 'Gradient edge', (ctx, g, p, h) => {
    const k = g.k, D = 9 * k, f = t => Math.pow(1 - clamp(t, 0, 1), 1.7);
    if(g.round){ const R = g.W / 2, gr = ctx.createRadialGradient(0, 0, R - D, 0, 0, R);
      for(let i = 0; i <= 12; i++){ const t = i / 12; gr.addColorStop(t, h.rgba(p.accent, f(1 - t))); }
      ctx.fillStyle = h.rgba(p.accent, 1); ctx.fill(eo(big(g, h), ol(g, h, 0)), 'evenodd'); ctx.fillStyle = gr; ctx.fill(ol(g, h, 0)); return; }
    const N = 56, rr = d => g.r + 0.8 * d;
    ctx.fillStyle = p.accent; ctx.fill(eo(big(g, h), ol(g, h, 0)), 'evenodd');
    for(let i = 0; i < N; i++){ const d0 = D * i / N, d1 = D * (i + 1) / N;
      ctx.fillStyle = h.rgba(p.accent, f((i + 0.5) / N)); ctx.fill(eo(ol(g, h, d0, rr(d0)), ol(g, h, d1, rr(d1))), 'evenodd'); }
  });

  // ---- hearts: small hearts all round, big and small in turn
  reg('hearts', 'Hearts', (ctx, g, p, h) => {
    const k = g.k, d = 2.75 * k, big2 = new Path2D(), sm = new Path2D();
    walk(g, d, Math.max(0, g.r + 2 * k - d), 3.3 * k, (x, y, a, i, n, c, s, j) => { if(j % 2) h.heart(sm, x, y + 0.05 * k, 2.0 * k); else h.heart(big2, x, y + 0.05 * k, 2.85 * k); }, { even: true });
    ctx.lineJoin = 'round'; ctx.strokeStyle = p.paper; ctx.lineWidth = 0.55 * k;
    h.shadow(ctx, 0.5 * k, 'rgba(0,0,0,.35)', 0, 0.12 * k); ctx.stroke(big2); ctx.stroke(sm); h.shadow(ctx);
    ctx.fillStyle = p.accent; ctx.fill(big2); ctx.fillStyle = h.mix(p.accent, p.paper, 0.35); ctx.fill(sm);
  });

  // ---- dots: a string of glossy beads
  reg('dots', 'Bead border', (ctx, g, p, h) => {
    const k = g.k, d = 2.3 * k, r = 0.98 * k, hi = h.mix(p.accent, '#ffffff', 0.6), lo = h.mix(p.accent, '#000000', 0.35), all = new Path2D(), pts = [];
    walk(g, d, Math.max(0, g.r + 1.5 * k - d), 2.25 * k, (x, y) => { pts.push([x, y]); all.moveTo(x + r, y); all.arc(x, y, r, 0, TAU); });
    ctx.save(); h.shadow(ctx, 0.6 * k, 'rgba(0,0,0,.45)', 0.1 * k, 0.2 * k); ctx.fillStyle = p.accent; ctx.fill(all); ctx.restore();
    for(const [x, y] of pts){ const gr = ctx.createRadialGradient(x - 0.35 * r, y - 0.4 * r, 0.05 * r, x, y, r);
      gr.addColorStop(0, hi); gr.addColorStop(0.45, p.accent); gr.addColorStop(1, lo); ctx.fillStyle = gr; ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill(); }
  });

  // ---- rope: a twisted rope laid inside a slim paper margin
  reg('rope', 'Rope', (ctx, g, p, h) => {
    const k = g.k, d = 2.5 * k, w = 2.5 * k, rr = Math.max(w * 0.9, g.r + 1.4 * k - d), th = 0.95, pitch = 1.25 * k;
    const outer = ol(g, h, d - w / 2, rr + w / 2), inner = ol(g, h, d + w / 2, Math.max(0, rr - w / 2)), band = eo(outer, inner);
    ctx.fillStyle = p.paper; ctx.fill(eo(big(g, h), outer), 'evenodd');
    ctx.save(); h.shadow(ctx, 0.6 * k, 'rgba(0,0,0,.45)', 0.1 * k, 0.2 * k); ctx.fillStyle = h.mix(p.accent, '#000000', 0.45); ctx.fill(band, 'evenodd'); ctx.restore();
    ctx.save(); ctx.clip(band, 'evenodd');
    const body = new Path2D(), lite = new Path2D(), rx = 0.62 * w / Math.sin(th), ry = 0.4 * pitch * Math.sin(th);
    walk(g, d, rr, pitch, (x, y, a) => { const r = a + th, c = Math.cos(r), s = Math.sin(r);
      body.moveTo(x + rx * c, y + rx * s); body.ellipse(x, y, rx, ry, r, 0, TAU);
      const n = inN(a), lx = x - n[0] * 0.12 * w - c * 0.1 * w, ly = y - n[1] * 0.12 * w - s * 0.1 * w;
      lite.moveTo(lx + rx * 0.55 * c, ly + rx * 0.55 * s); lite.ellipse(lx, ly, rx * 0.55, ry * 0.35, r, 0, TAU); });
    ctx.fillStyle = p.accent; ctx.fill(body); ctx.fillStyle = h.rgba(h.mix(p.accent, '#ffffff', 0.55), 0.8); ctx.fill(lite);
    ctx.restore();
  });

  // ---- neon: a glowing accent tube
  reg('neon', 'Neon glow', (ctx, g, p, h) => {
    const k = g.k, d = 3.1 * k, tube = ol(g, h, d, g.round ? 0 : 3.4 * k);
    shadowOnly(ctx, h, g, eo(big(g, h), ol(g, h, d - 1.2 * k, g.round ? 0 : 6 * k)), 6 * k, 'rgba(0,0,0,.55)', 'evenodd');
    ctx.strokeStyle = h.rgba(p.accent, 0.14); ctx.lineWidth = 3.4 * k; ctx.stroke(tube);
    ctx.strokeStyle = h.rgba(p.accent, 0.22); ctx.lineWidth = 2.1 * k; ctx.stroke(tube);
    ctx.strokeStyle = p.accent; ctx.lineWidth = 1.0 * k; h.shadow(ctx, 3.2 * k, p.accent); ctx.stroke(tube);
    h.shadow(ctx); ctx.lineWidth = 0.42 * k; ctx.strokeStyle = h.mix(p.accent, '#ffffff', 0.7); ctx.stroke(tube);
  });

  // ---- brush: rough hand-painted border in the paper colour, dry-brush bristle streaks on its inner edge
  reg('brush', 'Brush stroke', (ctx, g, p, h) => {
    const k = g.k, rand = h.rng(p.seed * 7 + 11), d0 = 2.5 * k, rr = g.round ? 0 : g.r + 2.5 * k - d0, st = 0.35;
    const n1 = loopNoise(rand, 7), n2 = loopNoise(rand, 23), n3 = loopNoise(rand, 64);
    const pts = ptsOf(g, d0, rr, st), N = pts.length, base = q => (n1(q.t) * 0.9 + n2(q.t) * 0.4 + n3(q.t) * 0.12) * k;
    ctx.fillStyle = p.paper; ctx.fill(eo(big(g, h), displaced(pts, base)), 'evenodd');
    ctx.strokeStyle = p.paper; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    for(let pass = 0; pass < 6; pass++){ let i = Math.floor(rand() * N), done = 0;
      while(done < N){ const len = Math.floor((2 + rand() * 9) * (1 - pass * 0.12) / st), gap = Math.floor((0.4 + rand() * (1.2 + pass * 2.4)) / st);
        const o0 = (0.15 + pass * 0.36 + rand() * 0.3) * k, o1 = o0 + (rand() - 0.6) * 0.6 * k;
        ctx.lineWidth = (0.62 - pass * 0.07) * k * (0.65 + rand() * 0.5); ctx.beginPath();
        for(let j = 0; j <= len && done + j < N; j++){ const q = pts[(i + j) % N], f = j / Math.max(1, len), o = base(q) + o0 + (o1 - o0) * f;
          const x = q.x - Math.sin(q.a) * o, y = q.y + Math.cos(q.a) * o; j ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }
        ctx.stroke(); i = (i + len + gap) % N; done += len + gap; } }
  });

  // ---- torn: torn-paper border in the paper colour, lifted off the photo with a soft shadow
  reg('torn', 'Torn paper', (ctx, g, p, h) => {
    const k = g.k, rand = h.rng(p.seed * 13 + 5), d0 = 3.6 * k, rr = g.round ? 0 : g.r + 2.5 * k - d0;
    const n1 = loopNoise(rand, 6), n2 = loopNoise(rand, 19), pts = ptsOf(g, d0, rr, 0.42 * k), jit = pts.map(() => rand()), fib = pts.map(() => rand());
    const base = (q, i) => (n1(q.t) * 1.0 + n2(q.t) * 0.45) * k + (jit[i] - 0.5) * 0.5 * k;
    const edge = displaced(pts, base), fringe = displaced(pts, (q, i) => base(q, i) + (0.25 + fib[i] * 0.45) * k);
    ctx.save(); h.shadow(ctx, 1.3 * k, 'rgba(0,0,0,.42)', 0.1 * k, 0.3 * k); ctx.fillStyle = h.rgba(h.mix(p.paper, '#ffffff', 0.5), 0.92); ctx.fill(eo(big(g, h), fringe), 'evenodd'); ctx.restore();
    ctx.fillStyle = p.paper; ctx.fill(eo(big(g, h), edge), 'evenodd');
    ctx.lineWidth = 0.12 * k; ctx.strokeStyle = h.rgba(h.mix(p.paper, '#000000', 0.25), 0.5); ctx.stroke(edge);
  });

  // ---- confetti: scattered in the edge zone, centre kept clear
  reg('confetti', 'Confetti', (ctx, g, p, h) => {
    const k = g.k, rand = h.rng(p.seed * 31 + 3), pts = ptsOf(g, 0, null, 0.5), N = pts.length, per = N * 0.5;
    const cols = [p.accent, turn(p.accent, 55, 0.6), turn(p.accent, 200, 0.55), turn(p.accent, -70, 0.66), p.paper, turn(p.accent, 130, 0.7)];
    const target = Math.round(per / (2.15 * k)), placed = [];
    for(let tries = 0; tries < target * 12 && placed.length < target; tries++){
      const q = pts[Math.floor(rand() * N)], dep = (-0.4 + 8.0 * Math.pow(rand(), 1.5)) * k, n = inN(q.a), x = q.x + n[0] * dep, y = q.y + n[1] * dep;
      const s = (0.9 + rand() * 0.7) * k * (1 - Math.max(0, dep) / (20 * k));
      if(placed.some(o => Math.hypot(o.x - x, o.y - y) < (o.s + s) * 0.95)) continue;
      placed.push({ x, y, s, type: Math.floor(rand() * 5), rot: rand() * TAU, col: cols[Math.floor(rand() * cols.length)] }); }
    h.shadow(ctx, 0.35 * k, 'rgba(0,0,0,.35)', 0.06 * k, 0.12 * k);
    for(const c of placed){ ctx.save(); ctx.translate(c.x, c.y); ctx.rotate(c.rot); ctx.fillStyle = c.col; ctx.strokeStyle = c.col; const s = c.s;
      if(c.type === 0) ctx.fillRect(-s * 0.9, -s * 0.32, s * 1.8, s * 0.64);
      else if(c.type === 1){ ctx.beginPath(); ctx.arc(0, 0, s * 0.55, 0, TAU); ctx.fill(); }
      else if(c.type === 2){ ctx.beginPath(); ctx.moveTo(0, -s * 0.7); ctx.lineTo(s * 0.62, s * 0.4); ctx.lineTo(-s * 0.62, s * 0.4); ctx.closePath(); ctx.fill(); }
      else if(c.type === 3){ ctx.lineWidth = s * 0.32; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(-s, 0);
        ctx.bezierCurveTo(-s * 0.5, -s * 0.8, 0, s * 0.8, s * 0.5, 0); ctx.bezierCurveTo(s * 0.7, -s * 0.3, s * 0.9, -s * 0.3, s, -s * 0.1); ctx.stroke(); }
      else { const st = new Path2D(); h.star(st, 0, 0, s * 0.72, 5, 0.48); ctx.fill(st); }
      ctx.restore(); }
  });

  // ---- sunburst: photo in a central window, two-tone rays round it
  reg('sunburst', 'Sunburst', (ctx, g, p, h) => {
    const k = g.k, m = (g.round ? 7.2 : 6.6) * k, rr = 5.5 * k, win = ol(g, h, m, rr), ring = ol(g, h, m - 1.1 * k, rr + 1.1 * k);
    ctx.save(); ctx.clip(eo(big(g, h), ring), 'evenodd');
    ctx.fillStyle = p.accent; ctx.fill(big(g, h));
    const n = 40, Rr = g.W + g.H, rays = new Path2D();
    for(let i = 0; i < n; i += 2){ const a0 = -PI / 2 + TAU * (i - 0.5) / n, a1 = a0 + TAU / n; rays.moveTo(0, 0); rays.lineTo(Rr * Math.cos(a0), Rr * Math.sin(a0)); rays.lineTo(Rr * Math.cos(a1), Rr * Math.sin(a1)); rays.closePath(); }
    ctx.fillStyle = h.mix(p.accent, p.paper, 0.3); ctx.fill(rays);
    const r0 = g.min / 2 - m, gr = ctx.createRadialGradient(0, 0, r0, 0, 0, Math.hypot(g.W, g.H) / 2 + 2);
    gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(1, 'rgba(0,0,0,.28)'); ctx.fillStyle = gr; ctx.fill(big(g, h));
    ctx.restore();
    ctx.save(); h.shadow(ctx, 1.0 * k, 'rgba(0,0,0,.4)', 0, 0.2 * k); ctx.fillStyle = p.paper; ctx.fill(eo(ring, win), 'evenodd'); ctx.restore();
  });

  // ---- washi: translucent patterned tape over the corners (round: two strips at the top)
  function tape(ctx, h, p, k, x, y, ang, L, Wd, tone, rand){
    const tw = 0.42 * k, nt = Math.max(5, Math.round(Wd / (0.85 * k))), pts = [];
    for(let i = 0; i <= nt; i++) pts.push([L / 2 - (i % 2 ? tw : 0) - rand() * 0.15 * k, -Wd / 2 + Wd * i / nt]);
    for(let i = 0; i <= nt; i++) pts.push([-L / 2 + (i % 2 ? tw : 0) + rand() * 0.15 * k, Wd / 2 - Wd * i / nt]);
    const T = poly(pts);
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang);
    ctx.save(); h.shadow(ctx, 0.7 * k, 'rgba(0,0,0,.28)', 0.1 * k, 0.25 * k); ctx.fillStyle = h.rgba(h.mix(tone, p.paper, 0.55), 0.8); ctx.fill(T); ctx.restore();
    ctx.save(); ctx.clip(T); ctx.strokeStyle = h.rgba(tone, 0.62); ctx.lineWidth = 0.75 * k; const sp = 1.9 * k; ctx.beginPath();
    for(let u = -L / 2 - Wd; u < L / 2 + Wd; u += sp){ ctx.moveTo(u, -Wd / 2 - 1); ctx.lineTo(u + Wd + 2, Wd / 2 + 1); } ctx.stroke();
    ctx.fillStyle = 'rgba(255,255,255,.18)'; ctx.fillRect(-L / 2, -Wd / 2, L, Wd * 0.22);
    ctx.restore(); ctx.restore();
  }
  reg('washi', 'Washi tape', (ctx, g, p, h) => {
    const k = g.k, rand = h.rng(p.seed * 17 + 9), Wd = 6.6 * k, L = 19 * k, tones = [p.accent, turn(p.accent, 150, 0.5)];
    if(g.round){ const R = g.W / 2;
      [-3 * PI / 4, -PI / 4].forEach((a, i) => { const j = (rand() - 0.5) * 0.25, rc = R - 2.4 * k, aa = a + j * 0.3;
        tape(ctx, h, p, k, rc * Math.cos(aa), rc * Math.sin(aa), aa + PI / 2 + j, L, Wd, tones[i % 2], rand); });
      return; }
    [[-1, -1], [1, -1], [1, 1], [-1, 1]].forEach(([sx, sy], i) => { const c = (3.3 + (rand() - 0.5) * 0.6) * k, j = (rand() - 0.5) * 0.22;
      tape(ctx, h, p, k, sx * (g.W / 2 - c), sy * (g.H / 2 - c), Math.atan2(sy, sx) + PI / 2 + j, L, Wd, tones[i % 2], rand); });
  });

  // ---- wreath: leafy laurel wreath (round); leafy garlands at two corners (rect)
  function leafSet(p, h){ return [h.mix(p.accent, '#000000', 0.25), p.accent, h.mix(p.accent, p.paper, 0.25)]; }
  function drawLeaves(ctx, h, p, k, leaves, berries){
    const cols = leafSet(p, h), Ps = cols.map(() => new Path2D()), ribs = new Path2D();
    leaves.forEach((l, i) => { leaf(Ps[l.c == null ? i % 3 : l.c], l.x, l.y, l.a, l.L, l.w);
      ribs.moveTo(l.x, l.y); ribs.lineTo(l.x + Math.cos(l.a) * l.L * 0.8, l.y + Math.sin(l.a) * l.L * 0.8); });
    const all = eo(...Ps); ctx.save(); h.shadow(ctx, 0.5 * k, 'rgba(0,0,0,.45)', 0.08 * k, 0.15 * k); ctx.fillStyle = cols[0]; ctx.fill(all); ctx.restore();
    Ps.forEach((P, i) => { ctx.fillStyle = cols[i]; ctx.fill(P); });
    ctx.lineWidth = 0.12 * k; ctx.strokeStyle = h.rgba(h.mix(p.accent, p.paper, 0.6), 0.75); ctx.stroke(ribs);
    if(berries && berries.length){ const B = new Path2D(); berries.forEach(([x, y, r]) => { B.moveTo(x + r, y); B.arc(x, y, r, 0, TAU); });
      ctx.lineWidth = 0.25 * k; ctx.strokeStyle = 'rgba(0,0,0,.22)'; ctx.stroke(B); ctx.fillStyle = p.paper; ctx.fill(B);
      ctx.fillStyle = h.rgba(p.accent, 0.35); ctx.fill(B); }
  }
  reg('wreath', 'Leaf wreath', (ctx, g, p, h) => {
    const k = g.k, leaves = [], berries = [], stem = new Path2D(), lw = 0.4 * k;
    if(g.round){ const Rb = g.W / 2 - 3.5 * k;
      for(const sg of [1, -1]){ const a0 = PI / 2 - sg * 0.14, a1 = -PI / 2 + sg * 0.36, A = t => a0 + (sg > 0 ? -1 : 1) * Math.abs(a1 - a0) * t;
        const pts = []; for(let i = 0; i <= 40; i++){ const a = A(i / 40); pts.push([Rb * Math.cos(a), Rb * Math.sin(a)]); }
        stem.moveTo(pts[0][0], pts[0][1]); pts.forEach(q => stem.lineTo(q[0], q[1]));
        const m = Math.round(Rb * Math.abs(a1 - a0) / (2.3 * k));
        for(let i = 0; i < m; i++){ const t = (i + 0.4) / m, a = A(t), x = Rb * Math.cos(a), y = Rb * Math.sin(a), dir = a - sg * PI / 2, L = (3.4 - 1.2 * t) * k, w = L * 0.42;
          leaves.push({ x, y, a: dir - sg * 0.6, L, w }, { x, y, a: dir + sg * 0.55, L: L * 0.85, w: w * 0.9 });
          if(i % 3 === 1){ const n = 0.9 * k; berries.push([x + Math.cos(a) * n, y + Math.sin(a) * n, 0.45 * k]); } }
        const at = A(1.02); leaves.push({ x: Rb * Math.cos(A(1)), y: Rb * Math.sin(A(1)), a: at - sg * PI / 2, L: 2.2 * k, w: 0.95 * k, c: 1 }); }
    } else {
      const d = 3.3 * k, rc = 5 * k, arm = Math.min(0.46 * g.min, 25 * k);
      for(const [sx, sy] of [[-1, -1], [1, 1]]){ const ox = sx * g.W / 2, oy = sy * g.H / 2, T = (x, y) => [ox - sx * x, oy - sy * y];
        // the stem in corner units: top arm, corner arc, side arm
        const pathPts = []; for(let i = 20; i >= 0; i--) pathPts.push([d + rc + (arm - rc - d) * i / 20, d]);
        for(let i = 1; i < 12; i++){ const th = -PI / 2 - PI / 2 * i / 12; pathPts.push([d + rc + rc * Math.cos(th), d + rc + rc * Math.sin(th)]); }
        for(let i = 0; i <= 20; i++) pathPts.push([d, d + rc + (arm - rc - d) * i / 20]);
        const P2 = pathPts.map(q => T(q[0], q[1])); stem.moveTo(P2[0][0], P2[0][1]); P2.forEach(q => stem.lineTo(q[0], q[1]));
        const lens = [0]; for(let i = 1; i < P2.length; i++) lens.push(lens[i - 1] + Math.hypot(P2[i][0] - P2[i - 1][0], P2[i][1] - P2[i - 1][1]));
        const tot = lens[lens.length - 1], mid = tot / 2, at = s => { let i = 1; while(i < lens.length - 1 && lens[i] < s) i++; const f = (s - lens[i - 1]) / (lens[i] - lens[i - 1] || 1);
          return [P2[i - 1][0] + (P2[i][0] - P2[i - 1][0]) * f, P2[i - 1][1] + (P2[i][1] - P2[i - 1][1]) * f, Math.atan2(P2[i][1] - P2[i - 1][1], P2[i][0] - P2[i - 1][0])]; };
        const m = Math.round(mid / (2.5 * k));
        for(const dirS of [-1, 1]) for(let i = 0; i < m; i++){ const t = (i + 0.7) / m, s = mid + dirS * t * mid * 0.97, q = at(s), dir = q[2] + (dirS < 0 ? PI : 0), L = (4.1 - 1.4 * t) * k, w = L * 0.42;
          leaves.push({ x: q[0], y: q[1], a: dir - 0.6, L, w }, { x: q[0], y: q[1], a: dir + 0.6, L: L * 0.85, w: w * 0.9 });
          if(i % 3 === 2) berries.push([q[0], q[1], 0.5 * k]); }
        const c = at(mid); berries.push([c[0] + sx * 0.3 * k, c[1] + sy * 0.3 * k, 0.95 * k]); }
    }
    ctx.lineCap = 'round'; ctx.lineWidth = lw; ctx.strokeStyle = h.mix(p.accent, '#000000', 0.35); ctx.stroke(stem);
    drawLeaves(ctx, h, p, k, leaves, berries);
  });

  // ---- geo: Memphis-style geometric shapes in the corners
  function geoShape(ctx, h, e, k, cols){
    ctx.save(); ctx.translate(e.x, e.y); ctx.rotate(e.r || 0); const s = e.s * k * GS, c = cols[e.c];
    ctx.fillStyle = c; ctx.strokeStyle = c; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.lineWidth = 0.7 * k;
    if(e.t === 'disc'){ ctx.beginPath(); ctx.arc(0, 0, s, 0, TAU); ctx.fill(); }
    else if(e.t === 'ring'){ ctx.beginPath(); ctx.arc(0, 0, s, 0, TAU); ctx.stroke(); }
    else if(e.t === 'half'){ ctx.beginPath(); ctx.arc(0, 0, s, PI, TAU); ctx.closePath(); ctx.fill(); }
    else if(e.t === 'tri'){ ctx.beginPath(); ctx.moveTo(0, -s); ctx.lineTo(s * 0.87, s * 0.5); ctx.lineTo(-s * 0.87, s * 0.5); ctx.closePath(); ctx.fill(); }
    else if(e.t === 'trio'){ ctx.beginPath(); ctx.moveTo(0, -s); ctx.lineTo(s * 0.87, s * 0.5); ctx.lineTo(-s * 0.87, s * 0.5); ctx.closePath(); ctx.stroke(); }
    else if(e.t === 'dots'){ const P = new Path2D(), sp = 1.55 * k, dr = 0.42 * k; for(let i = 0; i < 3; i++) for(let j = 0; j < 3; j++){ const x = (i - 1) * sp, y = (j - 1) * sp; P.moveTo(x + dr, y); P.arc(x, y, dr, 0, TAU); } ctx.fill(P); }
    else if(e.t === 'zig'){ ctx.beginPath(); for(let i = 0; i <= 6; i++){ const x = -s + 2 * s * i / 6, y = i % 2 ? -0.7 * k : 0.7 * k; i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); } ctx.stroke(); }
    else if(e.t === 'squig'){ ctx.beginPath(); for(let i = 0; i <= 24; i++){ const x = -s + 2 * s * i / 24, y = Math.sin(i / 24 * TAU * 1.5) * 0.75 * k; i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); } ctx.stroke(); }
    else if(e.t === 'plus'){ ctx.beginPath(); ctx.moveTo(-s, 0); ctx.lineTo(s, 0); ctx.moveTo(0, -s); ctx.lineTo(0, s); ctx.lineWidth = 0.75 * k; ctx.stroke(); }
    else if(e.t === 'stripe'){ ctx.beginPath(); for(let i = 0; i < 4; i++){ const y = (i - 1.5) * 1.0 * k; ctx.moveTo(-s, y); ctx.lineTo(s, y); } ctx.lineWidth = 0.48 * k; ctx.stroke(); }
    ctx.restore();
  }
  const GS = 1.3;   // cluster scale
  // two clusters in corner units (corner at 0,0, +x along the edge, +y inward)
  const GEO_A = [{ t: 'disc', x: 4.6, y: 4.4, s: 2.3, c: 0 }, { t: 'dots', x: 10.2, y: 3.0, s: 1, c: 2 }, { t: 'zig', x: 3.0, y: 11.2, s: 2.4, r: PI / 2, c: 1 },
    { t: 'trio', x: 8.6, y: 8.0, s: 1.35, r: 0.4, c: 2 }, { t: 'squig', x: 16.5, y: 2.3, s: 2.6, c: 3 }];
  const GEO_B = [{ t: 'half', x: 4.8, y: 3.0, s: 2.6, r: PI, c: 1 }, { t: 'tri', x: 3.3, y: 9.0, s: 1.7, r: -0.3, c: 0 }, { t: 'ring', x: 9.6, y: 6.0, s: 1.3, c: 2 },
    { t: 'stripe', x: 11.8, y: 2.6, s: 1.8, r: 0.5, c: 3 }, { t: 'plus', x: 3.0, y: 15.0, s: 0.9, c: 2 }];
  reg('geo', 'Memphis geo', (ctx, g, p, h) => {
    const k = g.k, cols = [p.accent, turn(p.accent, 165, 0.66), p.paper, turn(p.accent, 50, 0.55)];
    h.shadow(ctx, 0.35 * k, 'rgba(0,0,0,.35)', 0.06 * k, 0.12 * k);
    if(g.round){ const R = g.W / 2;
      [-3 * PI / 4, -PI / 4, PI / 4, 3 * PI / 4].forEach((a0, q) => { (q % 2 ? GEO_B : GEO_A).forEach(e => {
        const u = (e.x - 7) * k * 1.15, v = (e.y + 0.6) * k * 0.95, an = a0 + u / R, rr = R - v - 1.4 * k;
        geoShape(ctx, h, { t: e.t, x: rr * Math.cos(an), y: rr * Math.sin(an), s: e.s * 0.85, r: (e.r || 0) + an + PI / 2, c: e.c }, k, cols); }); });
      return; }
    [[-1, -1, 0], [1, -1, 1], [1, 1, 2], [-1, 1, 3]].forEach(([sx, sy, q]) => {
      (q % 2 ? GEO_B : GEO_A).forEach(e => { const ex = e.x * k * GS, ey = e.y * k * GS, rot = q * PI / 2;
        const [x, y] = rotQ(ex, ey, q), ox = sx * g.W / 2, oy = sy * g.H / 2;
        // rotQ turns the TL cluster about the origin; shift it to this corner
        geoShape(ctx, h, { t: e.t, x: ox + x, y: oy + y, s: e.s, r: (e.r || 0) + rot, c: e.c }, k, cols); }); });
  });

  // ---- gold-foil: metallic gold double border
  function goldGrad(ctx, g){ const gr = ctx.createLinearGradient(-g.W / 2, -g.H / 2, g.W / 2, g.H / 2);
    [[0, '#7a5518'], [0.1, '#c9993a'], [0.2, '#fbeaa5'], [0.29, '#d4a645'], [0.42, '#8d6420'], [0.53, '#d8b052'], [0.62, '#fff4c4'], [0.7, '#cf9f3e'], [0.84, '#8f661f'], [1, '#e2bd5c']]
      .forEach(s => gr.addColorStop(s[0], s[1])); return gr; }
  reg('gold-foil', 'Gold foil', (ctx, g, p, h) => {
    const k = g.k, gold = goldGrad(ctx, g), R0 = g.r + 1.2 * k, b1 = 2.1 * k, b2 = 2.95 * k, b3 = 3.45 * k, r = d => Math.max(0.4, R0 - d);
    const outer = eo(big(g, h), ol(g, h, b1, r(b1))), inner = eo(ol(g, h, b2, r(b2)), ol(g, h, b3, r(b3)));
    for(const [w, a] of [[1.6, 0.1], [1.0, 0.14], [0.55, 0.18]]){ ctx.lineWidth = w * k; ctx.strokeStyle = 'rgba(0,0,0,' + a + ')'; ctx.stroke(ol(g, h, b1, r(b1))); ctx.stroke(ol(g, h, b3, r(b3))); }
    ctx.fillStyle = gold; ctx.fill(outer, 'evenodd'); ctx.fill(inner, 'evenodd');
    ctx.lineWidth = 0.14 * k; ctx.strokeStyle = 'rgba(255,248,214,.75)'; ctx.stroke(ol(g, h, b2, r(b2))); ctx.stroke(ol(g, h, b1 - 0.5 * k, r(b1 - 0.5 * k)));
    ctx.strokeStyle = 'rgba(70,45,8,.55)'; ctx.stroke(ol(g, h, b1, r(b1))); ctx.stroke(ol(g, h, b3, r(b3)));
  });
})();
