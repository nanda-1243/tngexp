/* MagPress magnet studio: background patterns.

   Each pattern fills the whole paper (face + 6 mm bleed) behind the photo or the text marks. Colours come from
   the user's pickers: p.paper is the ground (already filled by the renderer), p.accent the motif colour and p.ink
   a secondary tone; tints are mixed toward the paper so text drawn on top stays legible. Lattices are anchored on
   the face centre so they sit symmetrically on round magnets; randomness is seeded (h.rng(p.seed)).
*/
(function(){
  'use strict';
  const TAU = Math.PI * 2, D = Math.PI / 180;

  // ---------- local colour helpers (hex in, hex out) ----------
  const hex = c => { c = String(c || '#000').replace('#', ''); if(c.length === 3) c = c.split('').map(x => x + x).join(''); return [0, 2, 4].map(i => parseInt(c.substr(i, 2), 16) / 255); };
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  function toHsl(c){
    const [r, g, b] = hex(c), mx = Math.max(r, g, b), mn = Math.min(r, g, b), l = (mx + mn) / 2, d = mx - mn;
    if(!d) return [0, 0, l];
    const s = d / (1 - Math.abs(2 * l - 1));
    let hh = mx === r ? ((g - b) / d) % 6 : mx === g ? (b - r) / d + 2 : (r - g) / d + 4;
    return [(hh * 60 + 360) % 360, s, l];
  }
  function fromHsl(hh, s, l){
    hh = ((hh % 360) + 360) % 360; s = clamp(s, 0, 1); l = clamp(l, 0, 1);
    const c = (1 - Math.abs(2 * l - 1)) * s, x = c * (1 - Math.abs((hh / 60) % 2 - 1)), m = l - c / 2;
    const [r, g, b] = hh < 60 ? [c, x, 0] : hh < 120 ? [x, c, 0] : hh < 180 ? [0, c, x] : hh < 240 ? [0, x, c] : hh < 300 ? [x, 0, c] : [c, 0, x];
    return '#' + [r, g, b].map(v => Math.round((v + m) * 255).toString(16).padStart(2, '0')).join('');
  }
  // the accent turned round the colour wheel by `deg`; grey accents get a little colour so the shift shows
  function shift(c, deg, sMul, lAdd){
    const [hh, s, l] = toHsl(c);
    return fromHsl(hh + deg, Math.max(s, deg ? 0.35 : 0) * (sMul == null ? 1 : sMul), l + (lAdd || 0));
  }
  // half-sizes of the cut paper and the radius that covers it from the centre
  const ext = g => ({ X: g.cutW / 2, Y: g.cutH / 2, R: Math.hypot(g.cutW, g.cutH) / 2 + 1 });
  // half-drop lattice anchored on the centre: fn(x, y, i, j) for every point covering the paper (+ margin)
  function halfDrop(g, sx, sy, margin, fn){
    const { X, Y } = ext(g), nj = Math.ceil((Y + margin) / sy), ni = Math.ceil((X + margin) / sx) + 1;
    for(let j = -nj; j <= nj; j++){ const off = (j & 1) ? sx / 2 : 0;
      for(let i = -ni; i <= ni; i++){ const x = i * sx + off; if(Math.abs(x) <= X + margin) fn(x, j * sy, i, j); } }
  }
  // tints mix a colour toward the paper; on a dark paper a weak tint turns muddy, so it is pushed further
  const dark = (p, h) => h.lum(p.paper) < 0.18;
  const tc = (p, h, c, t) => h.mix(p.paper, c, dark(p, h) ? Math.min(0.88, t * 1.5) : t);
  const tint = (p, h, t) => tc(p, h, p.accent, t);
  function ellipse(path, x, y, rx, ry, rot){ path.moveTo(x + rx * Math.cos(rot), y + rx * Math.sin(rot)); path.ellipse(x, y, rx, ry, rot, 0, TAU); return path; }
  function circle(path, x, y, r){ path.moveTo(x + r, y); path.arc(x, y, r, 0, TAU); return path; }

  const reg = (id, name, draw) => MS.register({ id: 'pattern.' + id, cat: 'pattern', name, draw });

  // ---------- polka dots ----------
  reg('dots', 'Polka dots', (ctx, g, p, h) => {
    const k = g.k, s = 7.4 * k, r = 1.45 * k, P = new Path2D();
    halfDrop(g, s, s / 2, s, (x, y) => circle(P, x, y, r));
    ctx.fillStyle = tint(p, h, 0.42); ctx.fill(P);
  });

  // ---------- diagonal stripes ----------
  reg('stripes', 'Diagonal stripes', (ctx, g, p, h) => {
    const k = g.k, { R } = ext(g), w = 2.7 * k, per = 6.2 * k, n = Math.ceil(R / per) + 1;
    ctx.rotate(-45 * D);
    const broad = new Path2D(), thin = new Path2D();
    for(let i = -n; i <= n; i++){ const x = i * per; broad.rect(x - w / 2, -R, w, 2 * R); thin.rect(x + per / 2 - 0.22 * k, -R, 0.44 * k, 2 * R); }
    ctx.fillStyle = tint(p, h, 0.26); ctx.fill(broad);
    ctx.fillStyle = tint(p, h, 0.4); ctx.fill(thin);
  });

  // ---------- gingham ----------
  reg('gingham', 'Gingham', (ctx, g, p, h) => {
    const k = g.k, { X, Y } = ext(g), b = 3.3 * k, per = 2 * b, ni = Math.ceil(X / per) + 1, nj = Math.ceil(Y / per) + 1;
    const light = tint(p, h, 0.2), deep = tint(p, h, 0.42), V = new Path2D(), Hz = new Path2D(), X2 = new Path2D();
    for(let i = -ni; i <= ni; i++) V.rect(i * per - b / 2, -Y, b, 2 * Y);
    for(let j = -nj; j <= nj; j++) Hz.rect(-X, j * per - b / 2, 2 * X, b);
    for(let i = -ni; i <= ni; i++) for(let j = -nj; j <= nj; j++) X2.rect(i * per - b / 2, j * per - b / 2, b, b);
    ctx.fillStyle = light; ctx.fill(V); ctx.fill(Hz); ctx.fillStyle = deep; ctx.fill(X2);
    // a faint woven thread line through the light bands
    ctx.strokeStyle = h.rgba(p.paper, 0.35); ctx.lineWidth = 0.12 * k; const T = new Path2D();
    for(let i = -ni; i <= ni; i++) for(const d of [-b / 4, b / 4]){ T.moveTo(i * per + d, -Y); T.lineTo(i * per + d, Y); }
    for(let j = -nj; j <= nj; j++) for(const d of [-b / 4, b / 4]){ T.moveTo(-X, j * per + d); T.lineTo(X, j * per + d); }
    ctx.stroke(T);
  });

  // ---------- chevron ----------
  reg('chevron', 'Chevron', (ctx, g, p, h) => {
    const k = g.k, { X, Y } = ext(g), w = 5.2 * k, A = 3 * k, per = 7.6 * k, t = per * 0.42;
    const ni = Math.ceil(X / w) + 2, nj = Math.ceil(Y / per) + 2, P = new Path2D();
    const z = i => (i & 1) ? A / 2 : -A / 2;              // peak at x = 0
    for(let j = -nj; j <= nj; j++){ const c = j * per;
      P.moveTo(-ni * w, c + z(-ni) - t / 2);
      for(let i = -ni + 1; i <= ni; i++) P.lineTo(i * w, c + z(i) - t / 2);
      for(let i = ni; i >= -ni; i--) P.lineTo(i * w, c + z(i) + t / 2);
      P.closePath(); }
    ctx.fillStyle = tint(p, h, 0.32); ctx.fill(P);
  });

  // ---------- stars ----------
  reg('stars', 'Stars', (ctx, g, p, h) => {
    const k = g.k, s = 9.6 * k, rnd = h.rng(p.seed), S = new Path2D(), T = new Path2D();
    halfDrop(g, s, s / 2, s, (x, y) => {
      const R = 2 * k * (0.85 + rnd() * 0.3), a = (rnd() - 0.5) * 26 * D;
      const one = h.star(new Path2D(), 0, 0, R, 5, 0.46), m = new DOMMatrix().translate(x, y).rotate(a / D);
      S.addPath(one, m);
      // a little four-point sparkle in the gap to the right
      const sx = x + s / 2, sr = 0.75 * k * (0.8 + rnd() * 0.4); h.star(T, sx, y, sr, 4, 0.32);
    });
    ctx.fillStyle = tint(p, h, 0.48); ctx.fill(S);
    ctx.fillStyle = tint(p, h, 0.3); ctx.fill(T);
  });

  // ---------- hearts ----------
  reg('hearts', 'Hearts', (ctx, g, p, h) => {
    const k = g.k, s = 8.4 * k, A = new Path2D(), B = new Path2D(), d = new Path2D();
    halfDrop(g, s, s / 2, s, (x, y, i, j) => {
      const one = h.heart(new Path2D(), 0, 0, 4 * k), m = new DOMMatrix().translate(x, y).rotate(((i + j) & 1) ? -12 : 12);
      ((j & 3) < 2 ? A : B).addPath(one, m);
      circle(d, x + s / 2, y, 0.42 * k);
    });
    ctx.fillStyle = tint(p, h, 0.45); ctx.fill(A);
    ctx.fillStyle = tc(p, h, shift(p.accent, -18, 0.9, 0.06), 0.36); ctx.fill(B);
    ctx.fillStyle = tint(p, h, 0.25); ctx.fill(d);
  });

  // ---------- confetti ----------
  reg('confetti', 'Confetti', (ctx, g, p, h) => {
    const k = g.k, { X, Y } = ext(g), rnd = h.rng(p.seed), cell = 5.6 * k;
    const pal = [p.accent, shift(p.accent, 45, 1, 0.05), shift(p.accent, 160, 0.85), shift(p.accent, -70, 0.9), shift(p.accent, 100, 0.8)]
      .map(c => tc(p, h, c, 0.68));
    const ni = Math.ceil(X / cell), nj = Math.ceil(Y / cell);
    ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    for(let j = -nj; j <= nj; j++) for(let i = -ni; i <= ni; i++){
      if(rnd() < 0.12) continue;
      const x = (i + (rnd() - 0.5) * 0.8) * cell, y = (j + (rnd() - 0.5) * 0.8) * cell, a = rnd() * Math.PI, kind = rnd(), col = pal[Math.floor(rnd() * pal.length)];
      ctx.save(); ctx.translate(x, y); ctx.rotate(a); ctx.fillStyle = col; ctx.strokeStyle = col;
      if(kind < 0.4){ const L = (1.9 + rnd() * 1.1) * k; ctx.fillRect(-L / 2, -0.45 * k, L, 0.9 * k); }
      else if(kind < 0.65){ ctx.beginPath(); ctx.arc(0, 0, (0.55 + rnd() * 0.35) * k, 0, TAU); ctx.fill(); }
      else if(kind < 0.82){ const r = 1.05 * k; ctx.beginPath(); ctx.moveTo(0, -r); ctx.lineTo(r * 0.87, r * 0.5); ctx.lineTo(-r * 0.87, r * 0.5); ctx.closePath(); ctx.fill(); }
      else { ctx.lineWidth = 0.42 * k; ctx.beginPath(); const L = 3.2 * k;
        for(let q = 0; q <= 12; q++){ const u = q / 12, px = -L / 2 + u * L, py = Math.sin(u * TAU * 1.25) * 0.55 * k; q ? ctx.lineTo(px, py) : ctx.moveTo(px, py); }
        ctx.stroke(); }
      ctx.restore();
    }
  });

  // ---------- waves ----------
  reg('waves', 'Waves', (ctx, g, p, h) => {
    const k = g.k, { X, Y } = ext(g), sp = 4.6 * k, A = 1.25 * k, L = 11.5 * k, n = Math.ceil(Y / sp) + 2;
    const wave = (P, y0, back) => { const N = Math.ceil(2 * X / (0.5 * k));
      for(let q = 0; q <= N; q++){ const u = back ? 1 - q / N : q / N, x = -X + u * 2 * X, y = y0 + A * Math.cos(TAU * x / L);
        (q || back) ? P.lineTo(x, y) : P.moveTo(x, y); } };
    const band = new Path2D(), line = new Path2D(), line2 = new Path2D();
    for(let j = -n; j <= n; j++){ const y = j * sp;
      if(!(j & 1)){ wave(band, y - sp / 2, false); wave(band, y + sp / 2, true); band.closePath(); }
      const Pl = (j & 1) ? line2 : line; wave(Pl, y, false); }
    ctx.fillStyle = tint(p, h, 0.1); ctx.fill(band);
    ctx.lineWidth = 0.75 * k; ctx.lineCap = 'round'; ctx.strokeStyle = tint(p, h, 0.42); ctx.stroke(line);
    ctx.lineWidth = 0.45 * k; ctx.strokeStyle = tint(p, h, 0.28); ctx.stroke(line2);
  });

  // ---------- sunburst ----------
  reg('sunburst', 'Sunburst', (ctx, g, p, h) => {
    const { R } = ext(g), N = 28, w = TAU / N, P = new Path2D();
    for(let i = 0; i < N; i += 2){ const a = -Math.PI / 2 - w / 2 + i * w; P.moveTo(0, 0); P.arc(0, 0, R, a, a + w); P.closePath(); }
    const dk = dark(p, h), bg = ctx.createRadialGradient(0, 0, 0, 0, 0, R);
    bg.addColorStop(0, p.paper); bg.addColorStop(1, dk ? h.mix(p.paper, '#000000', 0.25) : h.mix(p.paper, p.accent, 0.14));
    ctx.fillStyle = bg; ctx.fillRect(-R, -R, 2 * R, 2 * R);
    // dark paper: tonal rays (lighter paper) and a warm accent glow; light paper: accent rays and a paper glow
    ctx.fillStyle = dk ? h.rgba('#ffffff', 0.07) : h.rgba(p.accent, 0.16); ctx.fill(P);
    const glow = ctx.createRadialGradient(0, 0, 0, 0, 0, g.min * (dk ? 0.5 : 0.42)), gc = dk ? p.accent : p.paper;
    glow.addColorStop(0, h.rgba(gc, dk ? 0.3 : 0.85)); glow.addColorStop(0.55, h.rgba(gc, dk ? 0.1 : 0.35)); glow.addColorStop(1, h.rgba(gc, 0));
    ctx.fillStyle = glow; ctx.fillRect(-R, -R, 2 * R, 2 * R);
  });

  // ---------- soft two-tone gradient ----------
  reg('gradient', 'Soft gradient', (ctx, g, p, h) => {
    const { X, Y, R } = ext(g), dk = dark(p, h);
    // light paper: accent tint into a warmer/cooler neighbour; dark paper: the paper's own hue, deep into lighter
    const a = dk ? h.mix(p.paper, '#000000', 0.2) : h.mix(p.paper, p.accent, 0.14);
    const b = dk ? shift(p.paper, -28, 1.1, 0.14) : h.mix(p.paper, h.mix(p.accent, shift(p.accent, -30, 1, 0.08), 0.6), 0.5);
    const lg = ctx.createLinearGradient(-X, -Y, X, Y); lg.addColorStop(0, a); lg.addColorStop(0.5, h.mix(a, b, 0.42)); lg.addColorStop(1, b);
    ctx.fillStyle = lg; ctx.fillRect(-X, -Y, 2 * X, 2 * Y);
    const glow = ctx.createRadialGradient(-X * 0.45, -Y * 0.5, 0, -X * 0.45, -Y * 0.5, R * 0.9);
    glow.addColorStop(0, h.rgba(dk ? '#ffffff' : p.paper, dk ? 0.08 : 0.55)); glow.addColorStop(1, h.rgba(dk ? '#ffffff' : p.paper, 0));
    ctx.fillStyle = glow; ctx.fillRect(-X, -Y, 2 * X, 2 * Y);
  });

  // ---------- terrazzo ----------
  reg('terrazzo', 'Terrazzo', (ctx, g, p, h) => {
    const k = g.k, { X, Y } = ext(g), rnd = h.rng(p.seed), cell = 6.4 * k;
    const pal = [tc(p, h, p.accent, 0.62), tc(p, h, shift(p.accent, 35, 0.9, 0.08), 0.55), h.mix(p.paper, p.ink, 0.4),
      tc(p, h, shift(p.accent, 180, 0.55), 0.48), tc(p, h, p.accent, 0.32)];
    const chip = (x, y, r) => { const n = 5 + Math.floor(rnd() * 3), a0 = rnd() * TAU; ctx.beginPath();
      for(let q = 0; q < n; q++){ const a = a0 + q * TAU / n + (rnd() - 0.5) * 0.6, rr = r * (0.6 + rnd() * 0.45); q ? ctx.lineTo(x + rr * Math.cos(a), y + rr * Math.sin(a)) : ctx.moveTo(x + rr * Math.cos(a), y + rr * Math.sin(a)); }
      ctx.closePath(); ctx.fill(); };
    const ni = Math.ceil(X / cell) + 1, nj = Math.ceil(Y / cell) + 1;
    for(let j = -nj; j <= nj; j++) for(let i = -ni; i <= ni; i++){
      const x = (i + (rnd() - 0.5) * 0.7) * cell, y = (j + (rnd() - 0.5) * 0.7) * cell;
      ctx.fillStyle = pal[Math.floor(rnd() * pal.length)]; chip(x, y, (rnd() < 0.3 ? 2.1 : 1.3) * k);
      for(let q = 0; q < 3; q++){ ctx.fillStyle = pal[Math.floor(rnd() * pal.length)];
        chip(x + (rnd() - 0.5) * cell, y + (rnd() - 0.5) * cell, (0.3 + rnd() * 0.35) * k); }
    }
  });

  // ---------- graph paper ----------
  reg('grid', 'Graph paper', (ctx, g, p, h) => {
    const k = g.k, { X, Y } = ext(g), m = 2.5 * k, ni = Math.ceil(X / m), nj = Math.ceil(Y / m);
    const minor = new Path2D(), major = new Path2D();
    for(let i = -ni; i <= ni; i++){ const P = i % 4 ? minor : major; P.moveTo(i * m, -Y); P.lineTo(i * m, Y); }
    for(let j = -nj; j <= nj; j++){ const P = j % 4 ? minor : major; P.moveTo(-X, j * m); P.lineTo(X, j * m); }
    ctx.lineWidth = 0.11 * k; ctx.strokeStyle = tint(p, h, 0.3); ctx.stroke(minor);
    ctx.lineWidth = 0.24 * k; ctx.strokeStyle = tint(p, h, 0.48); ctx.stroke(major);
  });

  // ---------- simple flowers ----------
  reg('floral', 'Flowers', (ctx, g, p, h) => {
    const k = g.k, s = 11.5 * k, rnd = h.rng(p.seed);
    const petalA = tint(p, h, 0.5), petalB = tc(p, h, shift(p.accent, 28, 0.9, 0.08), 0.48);
    const leaf = tc(p, h, shift(p.accent, 115, 0.55, -0.05), 0.42), heart = tc(p, h, shift(p.accent, 45, 1, 0.1), 0.85);
    const leafPath = (x, y, a, L) => { const P = new Path2D(), c = Math.cos(a), sn = Math.sin(a), q = (u, v) => [x + u * c - v * sn, y + u * sn + v * c];
      P.moveTo(...q(0, 0)); P.quadraticCurveTo(...q(L / 2, L * 0.42), ...q(L, 0)); P.quadraticCurveTo(...q(L / 2, -L * 0.42), ...q(0, 0)); return P; };
    const flowers = [];
    halfDrop(g, s, s / 2, s, (x, y, i, j) => flowers.push({ x, y, big: !(j & 1), a: rnd() * TAU, z: 0.85 + rnd() * 0.3, la: rnd() * TAU }));
    ctx.fillStyle = leaf;
    flowers.forEach(f => { const r = (f.big ? 2.6 : 1.8) * k * f.z;
      ctx.fill(leafPath(f.x + Math.cos(f.la) * r * 0.7, f.y + Math.sin(f.la) * r * 0.7, f.la, r * 1.5));
      ctx.fill(leafPath(f.x + Math.cos(f.la + 2.2) * r * 0.7, f.y + Math.sin(f.la + 2.2) * r * 0.7, f.la + 2.2, r * 1.15)); });
    flowers.forEach(f => { const r = (f.big ? 2.6 : 1.8) * k * f.z, P = new Path2D(), n = f.big ? 5 : 6;
      for(let q = 0; q < n; q++){ const a = f.a + q * TAU / n; ellipse(P, f.x + Math.cos(a) * r * 0.55, f.y + Math.sin(a) * r * 0.55, r * 0.55, r * 0.36, a); }
      ctx.fillStyle = f.big ? petalA : petalB; ctx.fill(P);
      ctx.fillStyle = f.big ? heart : p.paper; ctx.beginPath(); ctx.arc(f.x, f.y, r * 0.26, 0, TAU); ctx.fill(); });
    // seed dots between the flowers
    const d = new Path2D(); halfDrop(g, s, s / 2, s, (x, y) => { circle(d, x + s / 2, y, 0.38 * k); circle(d, x + s / 2 + 0.95 * k, y - 0.7 * k, 0.26 * k); });
    ctx.fillStyle = tint(p, h, 0.3); ctx.fill(d);
  });

  // ---------- bokeh ----------
  reg('bokeh', 'Bokeh lights', (ctx, g, p, h) => {
    const k = g.k, { X, Y } = ext(g), rnd = h.rng(p.seed), dk = dark(p, h);
    const wash = ctx.createLinearGradient(0, -Y, 0, Y);
    wash.addColorStop(0, h.mix(p.paper, p.accent, dk ? 0.05 : 0.1)); wash.addColorStop(1, h.mix(p.paper, shift(p.accent, -30), dk ? 0.22 : 0.3));
    ctx.fillStyle = wash; ctx.fillRect(-X, -Y, 2 * X, 2 * Y);
    const cols = dk ? [p.accent, shift(p.accent, 30, 1, 0.12), '#fff3d6', shift(p.accent, -35, 1, 0.1)] : [p.accent, shift(p.accent, 30), shift(p.accent, -35), '#ffffff'];
    const n = Math.round(2 * X * 2 * Y / (38 * k * k)), discs = [];
    for(let i = 0; i < n; i++){ const big = rnd(); discs.push({ x: (rnd() * 2 - 1) * X, y: (rnd() * 2 - 1) * Y, r: (0.9 + big * big * 5.2) * k, c: cols[Math.floor(rnd() * cols.length)], a: 0.1 + rnd() * 0.17 }); }
    discs.sort((a, b) => b.r - a.r);
    if(dk) ctx.globalCompositeOperation = 'screen';
    discs.forEach(d => { const soft = Math.min(0.45, 0.12 + d.r / (14 * k)), a = d.c === '#ffffff' ? d.a * 1.6 : d.a;
      const gr = ctx.createRadialGradient(d.x, d.y, 0, d.x, d.y, d.r);
      gr.addColorStop(0, h.rgba(d.c, a * 0.55)); gr.addColorStop(1 - soft, h.rgba(d.c, a * 0.8)); gr.addColorStop(1 - soft * 0.35, h.rgba(d.c, a)); gr.addColorStop(1, h.rgba(d.c, 0));
      ctx.fillStyle = gr; ctx.beginPath(); ctx.arc(d.x, d.y, d.r, 0, TAU); ctx.fill(); });
  });

  // ---------- rangoli mandala (extra) ----------
  reg('mandala', 'Rangoli mandala', (ctx, g, p, h) => {
    const { R } = ext(g), u = g.min / 2, k = g.k;
    const line = tint(p, h, 0.5), fillA = tint(p, h, 0.16), fillB = tc(p, h, shift(p.accent, 40, 1, 0.08), 0.3), dotC = tint(p, h, 0.55);
    ctx.lineWidth = 0.3 * k; ctx.strokeStyle = line; ctx.lineJoin = 'round';
    const ring = (r) => { ctx.beginPath(); ctx.arc(0, 0, r, 0, TAU); ctx.stroke(); };
    const dots = (r, n, rr, off) => { const P = new Path2D(); for(let i = 0; i < n; i++){ const a = (i + (off || 0)) * TAU / n - Math.PI / 2; circle(P, r * Math.cos(a), r * Math.sin(a), rr); } ctx.fillStyle = dotC; ctx.fill(P); };
    // pointed petals between radii r0 and r1, n of them, half-width angle w
    const petals = (r0, r1, n, w, fill, off) => { const P = new Path2D();
      for(let i = 0; i < n; i++){ const a = (i + (off || 0)) * TAU / n - Math.PI / 2, rm = r0 + (r1 - r0) * 0.45;
        const pt = (rr, da) => [rr * Math.cos(a + da), rr * Math.sin(a + da)];
        P.moveTo(...pt(r0, 0)); P.quadraticCurveTo(...pt(rm, -w * 2.1), ...pt(r1, 0)); P.quadraticCurveTo(...pt(rm, w * 2.1), ...pt(r0, 0)); P.closePath(); }
      ctx.fillStyle = fill; ctx.fill(P); ctx.stroke(P); };
    // arches (scallops) whose feet sit on radius r0 and crowns reach r1
    const arches = (r0, r1, n, fill) => { const P = new Path2D(), w = TAU / n;
      for(let i = 0; i < n; i++){ const a = i * w - Math.PI / 2, b = a + w, m = a + w / 2;
        P.moveTo(r0 * Math.cos(a), r0 * Math.sin(a));
        P.bezierCurveTo(r1 * Math.cos(a), r1 * Math.sin(a), r1 * Math.cos(b), r1 * Math.sin(b), r0 * Math.cos(b), r0 * Math.sin(b));
        P.arc(0, 0, r0, b, a, true); P.closePath(); void m; }
      ctx.fillStyle = fill; ctx.fill(P); ctx.stroke(P); };
    // outer field (corners of rectangles, bleed): faint rays and rings so the motif carries on to the edge
    ctx.save(); ctx.strokeStyle = tint(p, h, 0.2); ctx.lineWidth = 0.2 * k;
    for(let r = u * 0.98; r < R; r += 3.2 * k) ring(r);
    ctx.restore();
    arches(u * 0.78, u * 0.94, 28, fillA);
    dots(u * 0.745, 56, 0.3 * k);
    ring(u * 0.715);
    petals(u * 0.49, u * 0.7, 16, 0.07, fillB);
    petals(u * 0.52, u * 0.665, 16, 0.045, fillA, 0.5);
    ring(u * 0.49);
    dots(u * 0.44, 32, 0.34 * k, 0.5);
    arches(u * 0.29, u * 0.4, 12, fillA);
    petals(u * 0.11, u * 0.29, 8, 0.16, fillB);
    petals(u * 0.11, u * 0.24, 8, 0.1, fillA, 0.5);
    ring(u * 0.11);
    dots(u * 0.065, 8, 0.3 * k);
    ctx.fillStyle = tint(p, h, 0.4); ctx.beginPath(); ctx.arc(0, 0, 0.9 * k, 0, TAU); ctx.fill();
  });

  // ---------- balloons (extra) ----------
  reg('balloons', 'Balloons', (ctx, g, p, h) => {
    const k = g.k, sx = 12.5 * k, sy = 9 * k, rnd = h.rng(p.seed);
    const pal = [p.accent, shift(p.accent, 50, 1, 0.06), shift(p.accent, 170, 0.8), shift(p.accent, -60, 0.9), shift(p.accent, 110, 0.75)].map(c => tc(p, h, c, 0.6));
    const str = h.mix(p.paper, p.ink, 0.3), list = [];
    halfDrop(g, sx, sy, sx, (x, y, i, j) => list.push({ x: x + (rnd() - 0.5) * 2 * k, y: y + (rnd() - 0.5) * 2 * k, c: pal[((i % 5) + 5 + 2 * j + 50) % 5], z: 0.85 + rnd() * 0.3, t: (rnd() - 0.5) * 16 }));
    ctx.lineCap = 'round';
    list.forEach(b => { const rx = 2.3 * k * b.z, ry = 2.85 * k * b.z;
      ctx.save(); ctx.translate(b.x, b.y); ctx.rotate(b.t * D);
      ctx.strokeStyle = str; ctx.lineWidth = 0.2 * k; ctx.beginPath(); ctx.moveTo(0, ry + 0.5 * k);
      ctx.bezierCurveTo(1.1 * k, ry + 2 * k, -1.1 * k, ry + 3.4 * k, 0.3 * k, ry + 5 * k); ctx.stroke();
      ctx.fillStyle = b.c; ctx.beginPath(); ctx.ellipse(0, 0, rx, ry, 0, 0, TAU); ctx.fill();
      ctx.beginPath(); ctx.moveTo(0, ry - 0.2 * k); ctx.lineTo(0.55 * k, ry + 0.6 * k); ctx.lineTo(-0.55 * k, ry + 0.6 * k); ctx.closePath(); ctx.fill();
      ctx.fillStyle = h.rgba('#ffffff', 0.45); ctx.beginPath(); ctx.ellipse(-rx * 0.4, -ry * 0.42, rx * 0.2, ry * 0.3, -0.5, 0, TAU); ctx.fill();
      ctx.restore(); });
  });

  // ---------- paw prints (extra) ----------
  reg('paws', 'Paw prints', (ctx, g, p, h) => {
    const k = g.k, s = 11 * k, P = new Path2D(), Hs = new Path2D();
    const paw = (x, y, a, z) => { const m = new DOMMatrix().translate(x, y).rotate(a).scale(z), one = new Path2D();
      one.moveTo(0, 1.6 * k);
      one.bezierCurveTo(-1.7 * k, 1.75 * k, -2 * k, 0.4 * k, -1.05 * k, -0.15 * k); one.bezierCurveTo(-0.4 * k, -0.55 * k, 0.4 * k, -0.55 * k, 1.05 * k, -0.15 * k);
      one.bezierCurveTo(2 * k, 0.4 * k, 1.7 * k, 1.75 * k, 0, 1.6 * k); one.closePath();
      [[-1.75, -1.15, 0.5, 0.66, -0.35], [-0.65, -2.1, 0.52, 0.7, -0.12], [0.65, -2.1, 0.52, 0.7, 0.12], [1.75, -1.15, 0.5, 0.66, 0.35]]
        .forEach(t => ellipse(one, t[0] * k, t[1] * k, t[2] * k, t[3] * k, t[4]));
      P.addPath(one, m); };
    halfDrop(g, s, s / 2, s, (x, y, i, j) => { paw(x, y, ((i + j) & 1) ? -22 : 18, 1.05);
      h.heart(Hs, x + s / 2, y, 1.7 * k); });
    ctx.fillStyle = tint(p, h, 0.38); ctx.fill(P);
    ctx.fillStyle = tint(p, h, 0.22); ctx.fill(Hs);
  });

  // ---------- marble (extra) ----------
  reg('marble', 'Marble', (ctx, g, p, h) => {
    const k = g.k, { X, Y, R } = ext(g), rnd = h.rng(p.seed), dk = dark(p, h);
    const vc = dk ? h.mix(p.paper, '#ffffff', 0.6) : h.mix(p.paper, p.ink, 0.62);
    // veins run along one diagonal; each is a smooth meander (sum of sines) across that direction
    const ang = -0.55 + (rnd() - 0.5) * 0.3, ux = Math.cos(ang), uy = Math.sin(ang), nx = -uy, ny = ux;
    const meander = amp => { const w = [0, 1, 2, 3].map(i => ({ f: (0.05 + rnd() * 0.04) * Math.pow(2.2, i) / k, ph: rnd() * TAU, a: amp * Math.pow(0.38, i) * (0.7 + rnd() * 0.6) }));
      return t => w.reduce((sum, q) => sum + q.a * Math.sin(q.f * t + q.ph), 0); };
    const vein = (off, t0, t1, amp, dx, dy, ex, ey) => { const m = meander(amp), P = new Path2D(); let i = 0;
      for(let t = t0; t <= t1; t += 0.5 * k, i++){ const o = off + m(t), x = (dx || 0) + ux * t + nx * o + (ex || 0) * t, y = (dy || 0) + uy * t + ny * o + (ey || 0) * t; i ? P.lineTo(x, y) : P.moveTo(x, y); }
      return { P, at: t => [ux * t + nx * (off + m(t)), uy * t + ny * (off + m(t))] }; };
    ctx.lineJoin = 'round'; ctx.lineCap = 'round';
    const span = R + 4 * k, offs = [-0.62, 0.02, 0.58].map(f => (f + (rnd() - 0.5) * 0.18) * Math.min(X, Y) * 1.3);
    const mains = offs.map(o => vein(o, -span, span, 7 * k));
    // soft clouding along the veins
    mains.forEach(v => [[16, 0.03], [8, 0.04], [3.2, 0.05]].forEach(([w, a]) => { ctx.strokeStyle = h.rgba(vc, a); ctx.lineWidth = w * k; ctx.stroke(v.P); }));
    // the veins: a soft body and a fine core, with thin satellites and a branch or two
    mains.forEach((v, n) => {
      ctx.strokeStyle = h.rgba(vc, 0.22); ctx.lineWidth = 0.7 * k; ctx.stroke(v.P);
      ctx.strokeStyle = h.rgba(vc, 0.6); ctx.lineWidth = (n === 1 ? 0.22 : 0.16) * k; ctx.stroke(v.P);
      for(let q = 0; q < 2; q++){ const t0 = -span + rnd() * span, sat = vein(offs[n] + (rnd() - 0.5) * 5 * k, t0, t0 + span * (0.5 + rnd() * 0.6), 6 * k);
        ctx.strokeStyle = h.rgba(vc, 0.35); ctx.lineWidth = 0.1 * k; ctx.stroke(sat.P); }
      const tb = (rnd() - 0.5) * span, [bx, by] = v.at(tb), turn = (rnd() < 0.5 ? -1 : 1) * (0.5 + rnd() * 0.4);
      const br = vein(0, 0, span * 0.45, 3 * k, bx, by, Math.cos(ang + turn) - ux, Math.sin(ang + turn) - uy);
      ctx.strokeStyle = h.rgba(vc, 0.4); ctx.lineWidth = 0.12 * k; ctx.stroke(br.P);
    });
    // one thin accent (gold) vein beside the middle one
    const gold = vein(offs[1] + 2.4 * k, -span, span, 7.5 * k);
    ctx.strokeStyle = h.rgba(p.accent, 0.75); ctx.lineWidth = 0.26 * k; ctx.stroke(gold.P);
  });
})();
