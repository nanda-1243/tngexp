/* MagPress magnet studio: text marks — signatures, date stamps, brand marks and captions (written against core.js).

   Every mark is laid out at a nominal size from the glyphs' real ink box (measureText actualBoundingBox*), shrunk if it
   would not fit the room its position allows, and placed inside the safe area with h.placeBox. Text over a photo gets a
   soft contrasting halo (h.shadow); badges and bands carry their own backing. Round magnets: arc-top / arc-bottom set
   text along the face edge where a style suits it (the *.arc styles also follow the edge at the corner positions).
   o = { text, date, pos, color, size }; decorative parts use p.accent, text uses o.color. */
(function(){
  'use strict';
  const MS = window.MS; if(!MS) return;
  const PI = Math.PI, TAU = 2 * PI;
  const GRID = ['tl', 'tc', 'tr', 'ml', 'mc', 'mr', 'bl', 'bc', 'br'];
  const ANG = { tl: -0.75 * PI, tc: -0.5 * PI, tr: -0.25 * PI, bl: 0.75 * PI, bc: 0.5 * PI, br: 0.25 * PI };
  const MON = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  const DAY = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

  // ---------- small utilities ----------
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const scaleOf = o => clamp(+o.size || 1, 0.3, 2.5);
  const clean = t => String(t == null ? '' : t).replace(/\s+/g, ' ').trim();
  const gridPos = o => { const q = o.pos || 'bc'; return q === 'arc-top' ? 'tc' : q === 'arc-bottom' ? 'bc' : GRID.includes(q) ? q : 'bc'; };
  const isArc = (g, o) => g.round && (o.pos === 'arc-top' || o.pos === 'arc-bottom');
  const edgeCurve = (g, pos) => g.round && pos !== 'mc' && pos !== 'ml' && pos !== 'mr';   // *.arc styles on round
  const alignOf = pos => pos[1] === 'l' ? 'left' : pos[1] === 'r' ? 'right' : 'center';
  const dateOf = o => (o.date instanceof Date && !isNaN(o.date)) ? o.date : new Date();
  const fmtDate = d => d.getDate() + ' ' + MON[d.getMonth()].slice(0, 3) + ' ' + d.getFullYear();
  const hash = s => { let x = 2166136261; for(const ch of String(s)){ x ^= ch.codePointAt(0); x = Math.imul(x, 16777619); } return x >>> 0; };

  // ---------- colour ----------
  // any CSS colour → #rrggbb (fallback fb when missing or invalid)
  function hexOf(ctx, c, fb){
    if(typeof c !== 'string' || !c.trim()) return fb;
    c = c.trim(); if(/^#([0-9a-f]{3}|[0-9a-f]{6})$/i.test(c)) return c;
    const prev = ctx.fillStyle; ctx.fillStyle = '#010203'; ctx.fillStyle = c; const v = String(ctx.fillStyle); ctx.fillStyle = prev;
    if(/^#[0-9a-f]{6}$/i.test(v)) return v === '#010203' ? fb : v;
    const m = /rgba?\(([^)]+)\)/.exec(v);
    return m ? '#' + m[1].split(',').slice(0, 3).map(x => clamp(Math.round(parseFloat(x)), 0, 255).toString(16).padStart(2, '0')).join('') : fb;
  }
  const ratio = (h, a, b) => { const x = h.lum(a), y = h.lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const light = (h, c) => h.lum(c) > 0.3;
  // text colour on a backing: the user's colour if it reads (contrast ≥ min), else white or near-black
  function onBg(h, bg, c, min){ if(c && ratio(h, bg, c) >= (min || 4)) return c; return ratio(h, bg, '#ffffff') >= ratio(h, bg, '#161616') ? '#ffffff' : '#161616'; }
  // soft contrasting halo so text reads over a busy photo (dark under light text, light glow under dark text)
  function halo(ctx, h, g, c, amt){
    amt = amt == null ? 1 : amt;
    if(light(h, c)) h.shadow(ctx, 0.75 * g.k * amt, 'rgba(0,0,0,' + (0.55 * Math.min(1, amt)).toFixed(2) + ')', 0, 0.12 * g.k * amt);
    else h.shadow(ctx, 0.9 * g.k * amt, 'rgba(255,255,255,' + (0.85 * Math.min(1, amt)).toFixed(2) + ')', 0, 0);
  }

  // ---------- text ----------
  // one line in a CSS font, optionally letter-spaced (sp in mm, kerning kept); ink box + a drawer
  function line(ctx, text, font, sp){
    sp = sp || 0; ctx.font = font; ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
    const chars = Array.from(text), m = ctx.measureText(text);
    let xs = null, adv = m.width, l = m.actualBoundingBoxLeft || 0, r = m.actualBoundingBoxRight; if(r == null) r = m.width;
    if(sp && chars.length > 1){
      xs = []; let acc = ''; chars.forEach((c, i) => { xs.push(ctx.measureText(acc).width + i * sp); acc += c; });
      const last = ctx.measureText(chars[chars.length - 1]);
      adv = m.width + sp * (chars.length - 1); l = ctx.measureText(chars[0]).actualBoundingBoxLeft || 0;
      r = xs[xs.length - 1] + (last.actualBoundingBoxRight != null ? last.actualBoundingBoxRight : last.width);
    }
    const a = m.actualBoundingBoxAscent || 0, d = m.actualBoundingBoxDescent || 0;
    return { text, font, adv, l, r, w: Math.max(0, l + r), a, d, h: a + d,
      // ink box's left edge at x, baseline at y
      draw(c, x, y, stroke){ c.font = font; c.textAlign = 'left'; c.textBaseline = 'alphabetic'; const ox = x + l;
        const put = (s, px) => stroke ? c.strokeText(s, px, y) : c.fillText(s, px, y);
        if(!xs) put(text, ox); else chars.forEach((ch, i) => put(ch, ox + xs[i])); },
      // ink box centred on (x, y)
      at(c, x, y, stroke){ this.draw(c, x - this.w / 2, y - this.h / 2 + this.a, stroke); } };
  }
  // font size ≤ size at which text fits maxW (core fit, then an exact linear correction)
  function fitSize(ctx, h, text, maxW, size, fam, wt, st, spEm){
    let s = h.fit(ctx, text, maxW, size, fam, wt, st, size * 0.3, spEm);
    ctx.font = h.font(s, fam, wt, st);
    const w = ctx.measureText(text).width + (spEm || 0) * s * Math.max(0, Array.from(text).length - 1);
    if(w > maxW && w > 0) s *= maxW / w;
    return s;
  }
  function wrapLines(meas, words, maxW){
    const out = []; let cur = '';
    words.forEach(w => { const t = cur ? cur + ' ' + w : w; if(!cur || meas(t) <= maxW) cur = t; else { out.push(cur); cur = w; } });
    if(cur) out.push(cur); return out;
  }
  // narrowest (balanced) wrapping into ≤ n lines of ≤ maxW, or null
  function balance(meas, text, maxW, n){
    const words = text.split(' '); if(words.some(w => meas(w) > maxW)) return null;
    const first = wrapLines(meas, words, maxW); if(first.length > n) return null;
    let lo = 0, hi = maxW; for(let i = 0; i < 16; i++){ const mid = (lo + hi) / 2; if(wrapLines(meas, words, mid).length <= first.length) hi = mid; else lo = mid; }
    return wrapLines(meas, words, hi);
  }
  // biggest size (fewest lines first, unless that costs > 26 %) at which text wraps into ≤ maxLines lines of ≤ maxW
  function flow(ctx, h, text, maxW, size, fam, wt, st, maxLines, spEm){
    const meas = s => { const f = h.font(s, fam, wt, st); return t => { ctx.font = f; return ctx.measureText(t).width + (spEm || 0) * s * Math.max(0, Array.from(t).length - 1); }; };
    for(let n = 1; n <= maxLines; n++){
      const floor = n < maxLines ? 0.74 : 0.4;
      for(let s = size; s >= size * floor; s *= 0.95){ const ls = balance(meas(s), text, maxW, n); if(ls) return { size: s, lines: ls }; }
    }
    const s = size * 0.4, ls = wrapLines(meas(s), text.split(' '), maxW);
    if(ls.length > maxLines) ls.splice(maxLines - 1, ls.length, ls.slice(maxLines - 1).join(' '));
    return { size: s, lines: ls };
  }
  // stacked lines: draw(c, align, x, y) with (x, y) the block's top-left
  function block(ctx, lines, font, lead, sp){
    const Ls = lines.map(t => line(ctx, t, font, sp)), n = Ls.length;
    const w = Math.max(...Ls.map(L => L.w)), top = Ls[0].a, hh = top + lead * (n - 1) + Ls[n - 1].d;
    return { Ls, w, h: hh, top, draw(c, align, x, y){
      Ls.forEach((L, i) => L.draw(c, align === 'left' ? x : align === 'right' ? x + w - L.w : x + (w - L.w) / 2, y + top + lead * i)); } };
  }
  // small caps: capitals and digits at S, lower-case letters as capitals at k × S
  function smallCaps(ctx, h, text, S, fam, wt, spEm, k){
    const chars = Array.from(text), items = []; let w = 0;
    chars.forEach((ch, i) => { const sm = ch !== ch.toUpperCase(), f = h.font(sm ? S * (k || 0.8) : S, fam, wt), u = ch.toUpperCase();
      ctx.font = f; const gw = ctx.measureText(u).width, adv = gw + (i < chars.length - 1 ? spEm * S : 0); items.push({ ch: u, f, gw, adv }); w += adv; });
    ctx.font = h.font(S, fam, wt); const m = ctx.measureText('H');
    return { items, w, a: m.actualBoundingBoxAscent || 0.7 * S,
      draw(c, x, y){ c.textAlign = 'left'; c.textBaseline = 'alphabetic'; items.forEach(it => { c.font = it.f; c.fillText(it.ch, x, y); x += it.adv; }); } };
  }

  // ---------- placement ----------
  // the largest box a mark may take at pos (side: share of the width off-centre; tall: share of the height on a top/bottom row)
  function room(g, pos, side, tall){
    side = side || 0.64; tall = tall || 0.42;
    const c = pos[1] === 'c', m = pos[0] === 'm';
    if(!g.round) return { w: g.safeW * (c ? 1 : side), h: g.safeH * (m ? Math.min(0.9, 2 * tall) : tall) };
    const D = 2 * g.safeR;
    if(pos === 'mc') return { w: D * 0.88, h: D * Math.min(0.75, 1.5 * tall) };
    if(c) return { w: D * 0.76, h: D * tall * 0.62 };
    if(m) return { w: D * side * 0.6, h: D * tall * 0.75 };
    return { w: D * side * 0.62, h: D * tall * 0.55 };
  }
  // box = { w, h, draw(c) } drawn centred on the origin: scaled to fit lim and the safe area, placed at pos and drawn
  function put(ctx, g, h, pos, box, lim, pad){
    if(!(box.w > 0 && box.h > 0)) return null;
    pad = pad == null ? 0.45 * g.k : pad;
    let f = Math.min(1, lim.w / box.w, lim.h / box.h);
    if(g.round){ const R = g.safeR - pad, dd = Math.hypot(box.w * f / 2, box.h * f / 2); if(dd > R) f *= R / dd; }
    else f = Math.min(f, (g.safeW - 2 * pad) / box.w, (g.safeH - 2 * pad) / box.h);
    const at = h.placeBox(g, pos, box.w * f, box.h * f, pad);
    ctx.save(); ctx.translate(at.x, at.y); if(f !== 1) ctx.scale(f, f); box.draw(ctx); ctx.restore();
    return { x: at.x, y: at.y, f };
  }
  // rotated box size
  const rotBox = (w, hh, a) => { const c = Math.abs(Math.cos(a)), s = Math.abs(Math.sin(a)); return { w: w * c + hh * s, h: w * s + hh * c }; };

  // text along the edge of a round face centred on angle `at`; shrinks until the span ≤ maxSpan; keeps the ink inside safeR − pad
  function arcFit(ctx, h, g, text, at, o2){
    const pad = o2.pad == null ? 0.45 * g.k : o2.pad, bottom = Math.sin(at) > 0.01, chars = Array.from(text), spEm = o2.spacing || 0;
    let size = o2.size, R = 0, span = 0, a = 0, d = 0;
    for(let i = 0; i < 50; i++){
      ctx.font = h.font(size, o2.family, o2.weight, o2.style); ctx.textBaseline = 'middle'; ctx.textAlign = 'left';
      const m = ctx.measureText(text); a = m.actualBoundingBoxAscent || size * 0.4; d = m.actualBoundingBoxDescent || size * 0.3;
      R = g.safeR - pad - 0.1 - (bottom ? d : a);
      span = (chars.reduce((s, c) => s + ctx.measureText(c).width, 0) + spEm * size * (chars.length - 1)) / R;
      if(span <= o2.maxSpan) break; size *= 0.95;
    }
    ctx.textBaseline = 'alphabetic';
    return { size, R, span, a, d, bottom };
  }
  // arc text with an optional ornament (dot / star) at both ends
  function arcLine(ctx, g, h, text, pos, o2){
    const at = ANG[pos], corner = pos[1] !== 'c';
    const F = arcFit(ctx, h, g, text, at, Object.assign({}, o2, { maxSpan: (corner ? 1.1 : 2.3) * (o2.spanK || 1) }));
    ctx.save(); halo(ctx, h, g, o2.color, o2.haloAmt);
    h.arcText(ctx, text, F.R, at, { size: F.size, family: o2.family, weight: o2.weight, style: o2.style, spacing: o2.spacing, color: o2.color, side: F.bottom ? 'bottom' : 'top' });
    if(o2.orn){
      const rc = F.R + (F.bottom ? -1 : 1) * (F.a - F.d) / 2, ga = 0.85 * F.size / F.R, r0 = (o2.orn === 'star' ? 0.3 : 0.16) * F.size, P = new Path2D();
      [-1, 1].forEach(sg => { const a = at + sg * (F.span / 2 + ga), x = rc * Math.cos(a), y = rc * Math.sin(a);
        if(o2.orn === 'star') h.star(P, x, y, r0, 5, 0.45); else { P.moveTo(x + r0, y); P.arc(x, y, r0, 0, TAU); } });
      ctx.fillStyle = o2.ornColor || o2.color; ctx.fill(P);
    }
    ctx.restore(); return F;
  }
  // per-glyph arc text (for small caps); R is the baseline radius
  function arcItems(ctx, items, R, at, bottom){
    const span = items.reduce((s, it) => s + it.adv, 0) / R; let a = bottom ? at + span / 2 : at - span / 2;
    ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
    items.forEach(it => { const m = bottom ? a - it.gw / 2 / R : a + it.gw / 2 / R;
      ctx.save(); ctx.translate(R * Math.cos(m), R * Math.sin(m)); ctx.rotate(bottom ? m - PI / 2 : m + PI / 2); ctx.font = it.f; ctx.fillText(it.ch, 0, 0); ctx.restore();
      a = bottom ? a - it.adv / R : a + it.adv / R; });
    return span;
  }
  // one line of text on a band running right across the face at pos's row (band may run into the bleed; text stays safe)
  // mk(S) → { w, h, draw(c, xLeft, yCentre) }; opt: { S, padY (× S), fill, rules, flush }
  function bandMark(ctx, g, h, pos, mk, opt){
    const pad = 0.45 * g.k; let S = opt.S, it, at, bt;
    for(let i = 0; i < 45; i++){
      it = mk(S); bt = it.h + 2 * opt.padY * S; at = h.placeBox(g, pos, it.w, bt, pad);
      const ok = g.round ? Math.hypot(Math.abs(at.x) + it.w / 2, Math.abs(at.y) + bt / 2) <= g.safeR - pad + 1e-6 && (pos[0] === 'm' || Math.abs(at.y) > 0.3 * g.safeR)
                         : it.w <= g.safeW - 2 * pad + 1e-6 && bt <= g.safeH - 2 * pad + 1e-6;
      if(ok) break; S *= 0.94;
    }
    let y0 = at.y - bt / 2, y1 = at.y + bt / 2; const x0 = -g.cutW / 2 - 1, x1 = g.cutW / 2 + 1;
    if(opt.flush && pos[0] === 't') y0 = -g.cutH / 2 - 1;
    if(opt.flush && pos[0] === 'b') y1 = g.cutH / 2 + 1;
    ctx.save(); ctx.fillStyle = opt.fill; h.shadow(ctx, 1.1 * g.k, 'rgba(0,0,0,.3)', 0, 0.3 * g.k); ctx.fillRect(x0, y0, x1 - x0, y1 - y0); h.shadow(ctx);
    if(opt.rules){
      const e = 0.32 * opt.padY * S; ctx.strokeStyle = opt.rules; ctx.lineWidth = Math.max(0.1, 0.045 * S); ctx.beginPath();
      if(!(opt.flush && pos[0] === 't')){ ctx.moveTo(x0, at.y - bt / 2 + e); ctx.lineTo(x1, at.y - bt / 2 + e); }
      if(!(opt.flush && pos[0] === 'b')){ ctx.moveTo(x0, at.y + bt / 2 - e); ctx.lineTo(x1, at.y + bt / 2 - e); }
      ctx.stroke();
    }
    it.draw(ctx, at.x - it.w / 2, at.y); ctx.restore();
  }

  // ---------- drawing bits ----------
  // calligraphic stroke along a cubic Bézier P = [x0,y0, x1,y1, x2,y2, x3,y3] with width wmax × wfn(t)
  function swash(ctx, P, wmax, wfn){
    const N = 56, A = [], B = [];
    for(let i = 0; i <= N; i++){ const t = i / N, u = 1 - t;
      const x = u*u*u*P[0] + 3*u*u*t*P[2] + 3*u*t*t*P[4] + t*t*t*P[6], y = u*u*u*P[1] + 3*u*u*t*P[3] + 3*u*t*t*P[5] + t*t*t*P[7];
      const dx = 3*u*u*(P[2]-P[0]) + 6*u*t*(P[4]-P[2]) + 3*t*t*(P[6]-P[4]), dy = 3*u*u*(P[3]-P[1]) + 6*u*t*(P[5]-P[3]) + 3*t*t*(P[7]-P[5]);
      const n = Math.hypot(dx, dy) || 1, wd = wmax * Math.max(0, wfn(t)) / 2;
      A.push([x - dy / n * wd, y + dx / n * wd]); B.push([x + dy / n * wd, y - dx / n * wd]); }
    ctx.beginPath(); A.forEach((q, i) => i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]));
    for(let i = B.length - 1; i >= 0; i--) ctx.lineTo(B[i][0], B[i][1]); ctx.closePath(); ctx.fill();
  }
  function roundRect(c, x, y, w, hh, r){ r = Math.min(r, w / 2, hh / 2); c.beginPath(); c.moveTo(x + r, y); c.arcTo(x + w, y, x + w, y + hh, r);
    c.arcTo(x + w, y + hh, x, y + hh, r); c.arcTo(x, y + hh, x, y, r); c.arcTo(x, y, x + w, y, r); c.closePath(); }
  // points every ~step mm round a rounded rectangle centred on the origin
  function rrPoints(w, hh, r, step){
    const pts = [], sx = w / 2 - r, sy = hh / 2 - r;
    const seg = (x0, y0, x1, y1) => { const n = Math.max(1, Math.ceil(Math.hypot(x1 - x0, y1 - y0) / step)); for(let i = 0; i < n; i++) pts.push([x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n]); };
    const arc = (cx, cy, a0) => { const n = Math.max(2, Math.ceil(PI * r / 2 / step)); for(let i = 0; i < n; i++){ const a = a0 + PI / 2 * i / n; pts.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]); } };
    seg(-sx, -hh / 2, sx, -hh / 2); arc(sx, -sy, -PI / 2); seg(w / 2, -sy, w / 2, sy); arc(sx, sy, 0);
    seg(sx, hh / 2, -sx, hh / 2); arc(-sx, sy, PI / 2); seg(-w / 2, sy, -w / 2, -sy); arc(-sx, -sy, PI);
    return pts;
  }
  // draw fn into an offscreen layer (w × h mm, centred on the origin) at the current resolution, then composite it back
  function layer(ctx, w, hh, fn){
    const m = ctx.getTransform(), k = Math.min(Math.hypot(m.a, m.b), 2400 / Math.max(w, hh));
    if(typeof document === 'undefined' || !(k > 0)){ fn(ctx, false); return; }
    const cv = document.createElement('canvas'); cv.width = Math.max(1, Math.ceil(w * k)); cv.height = Math.max(1, Math.ceil(hh * k));
    const c = cv.getContext('2d'); c.setTransform(k, 0, 0, k, cv.width / 2, cv.height / 2);
    fn(c, true);
    ctx.drawImage(cv, -cv.width / k / 2, -cv.height / k / 2, cv.width / k, cv.height / k);
  }
  // worn-ink specks knocked out of a layer
  function distress(c, h, w, hh, seed, amount, unit){
    const r = h.rng(seed), n = Math.round(w * hh / (unit * unit) * amount);
    c.save(); c.globalCompositeOperation = 'destination-out';
    for(let i = 0; i < n; i++){ const x = (r() - 0.5) * w, y = (r() - 0.5) * hh, rr = unit * (0.12 + r() * r() * 0.8);
      c.globalAlpha = 0.3 + r() * 0.7; c.beginPath(); c.ellipse(x, y, rr, rr * (0.35 + r() * 0.65), r() * PI, 0, TAU); c.fill(); }
    c.globalAlpha = 0.18; c.lineWidth = unit * 0.25;
    for(let i = 0; i < n / 25; i++){ const x = (r() - 0.5) * w, y = (r() - 0.5) * hh, a = r() * PI; c.beginPath(); c.moveTo(x, y); c.lineTo(x + Math.cos(a) * unit * 6, y + Math.sin(a) * unit * 6); c.stroke(); }
    c.restore();
  }
  // initials: 'Anu & Ravi' → A & R, 'MagPress' → M P
  function initials(t, max){
    const toks = String(t).replace(/[&+]/g, ' & ').split(/\s+/).filter(Boolean), out = []; let amp = false;
    for(const w of toks){ if(/^(&|and|und|et|y)$/i.test(w)){ if(out.length) amp = true; continue; } const m = w.match(/[\p{L}\p{N}]/u); if(m) out.push(m[0].toUpperCase()); }
    if(out.length === 1){ const word = toks.find(w => /\p{L}/u.test(w)) || '', caps = Array.from(word).filter(ch => /\p{Lu}/u.test(ch));
      if(caps.length >= 2) return { chars: caps.slice(0, max), amp: false }; }
    return { chars: out.slice(0, max), amp: amp && out.length === 2 };
  }

  // =====================================================================================
  // SIGNATURES
  // =====================================================================================
  // a single line of script, sized, fitted and placed
  function scriptSig(id, name, fam, wt, base, extra){
    MS.register({ id, cat: 'signature', name, pos: extra.pos || 'br',
      draw(ctx, g, p, h, o){
        const t = clean(o.text); if(!t) return;
        const pos = gridPos(o), lim = room(g, pos, 0.66, 0.4), C = hexOf(ctx, o.color, '#ffffff');
        const S = fitSize(ctx, h, t, lim.w * (extra.wk || 0.97), base * g.k * scaleOf(o), fam, wt);
        const L = line(ctx, t, h.font(S, fam, wt));
        put(ctx, g, h, pos, extra.box(ctx, g, h, L, S, C), lim);
      } });
  }
  scriptSig('signature.script', 'Script (Great Vibes)', 'Great Vibes', 400, 9.5, {
    box: (ctx, g, h, L, S, C) => ({ w: L.w, h: L.h, draw(c){ c.fillStyle = C; halo(c, h, g, C); L.at(c, 0, 0); } }) });

  scriptSig('signature.flourish', 'Flourish (Allura + swash)', 'Allura', 400, 10, { wk: 0.9,
    box(ctx, g, h, L, S, C){
      const x0 = -L.w / 2, x1 = L.w / 2, dep = Math.max(0.3 * S, L.d + 0.08 * S);
      const P = [x0 + 0.04 * L.w, dep * 0.75, x0 + 0.34 * L.w, dep * 1.45, x1 - 0.12 * L.w, dep * 1.05, x1 + 0.16 * S, -0.06 * S];
      const wm = 0.075 * S, xs = [x0, x1, P[0], P[2], P[4], P[6]], ys = [-L.a, L.d, P[1], P[3], P[5], P[7]];
      const mnX = Math.min(...xs) - wm, mxX = Math.max(...xs) + wm, mnY = Math.min(...ys) - wm, mxY = Math.max(...ys) + wm;
      return { w: mxX - mnX, h: mxY - mnY, draw(c){
        c.translate(-(mnX + mxX) / 2, -(mnY + mxY) / 2); c.fillStyle = C; halo(c, h, g, C);
        L.draw(c, x0, 0); swash(c, P, wm, t => Math.pow(Math.sin(PI * t), 0.65) * (1 - 0.45 * t) + 0.04); } };
    } });

  scriptSig('signature.handwritten', 'Handwritten (Caveat)', 'Caveat', 700, 10.5, { pos: 'bl',
    box(ctx, g, h, L, S, C){ const a = -0.065, b = rotBox(L.w, L.h, a);
      return { w: b.w, h: b.h, draw(c){ c.rotate(a); c.fillStyle = C; halo(c, h, g, C, 1.1); L.at(c, 0, 0); } }; } });

  scriptSig('signature.marker', 'Marker (Pacifico)', 'Pacifico', 400, 7.6, {
    box(ctx, g, h, L, S, C){ const ox = 0.045 * S, oy = 0.06 * S, dark = light(h, C);
      return { w: L.w + ox, h: L.h + oy, draw(c){
        c.fillStyle = dark ? 'rgba(0,0,0,.42)' : 'rgba(255,255,255,.7)'; L.at(c, ox / 2, oy / 2);
        c.fillStyle = C; h.shadow(c, 0.35 * g.k, dark ? 'rgba(0,0,0,.3)' : 'rgba(255,255,255,.5)'); L.at(c, -ox / 2, -oy / 2); } }; } });

  scriptSig('signature.elegant', 'Elegant (Parisienne, dash)', 'Parisienne', 400, 8.6, { wk: 0.8,
    box(ctx, g, h, L, S, C){
      ctx.font = h.font(S, 'Parisienne'); const xh = ctx.measureText('x').actualBoundingBoxAscent || 0.3 * S;
      const dl = 0.95 * S, gap = 0.3 * S, W = dl + gap + L.w, top = Math.max(L.a, xh), bot = Math.max(L.d, 0.05 * S);
      return { w: W, h: top + bot, draw(c){
        const y0 = -(top + bot) / 2 + top, x0 = -W / 2; c.fillStyle = C; halo(c, h, g, C);
        const yd = y0 - xh * 0.55;
        swash(c, [x0, yd + 0.04 * S, x0 + dl * 0.35, yd, x0 + dl * 0.7, yd - 0.02 * S, x0 + dl, yd - 0.05 * S], 0.07 * S, t => Math.pow(Math.sin(PI * (0.08 + 0.84 * t)), 0.8) * (0.55 + 0.45 * t));
        L.draw(c, x0 + dl + gap, y0); } };
    } });

  MS.register({ id: 'signature.with-love', cat: 'signature', name: 'With love', pos: 'br',
    draw(ctx, g, p, h, o){
      let t = clean(o.text); if(!t) return;
      const pos = gridPos(o), lim = room(g, pos, 0.66, 0.45), C = hexOf(ctx, o.color, '#ffffff'), al = alignOf(pos);
      t = t.replace(/^with love,?\s*/i, '') || t;
      const S = fitSize(ctx, h, t, lim.w * 0.95, 8.2 * g.k * scaleOf(o), 'Dancing Script', 700);
      const N = line(ctx, t, h.font(S, 'Dancing Script', 700)), W1 = line(ctx, 'with love,', h.font(0.46 * S, 'Cormorant Garamond', 500, 'italic'));
      const hs = 0.3 * S, hg = 0.16 * S, w1 = W1.w + hg + hs * 0.9, ind = al === 'left' ? 0.35 * S : 0;
      const gap = 0.12 * S, b2 = W1.d + gap + N.a;           // baseline-to-baseline
      const W = Math.max(w1 + ind, N.w), top = Math.max(W1.a, hs * 0.5), H = top + b2 + N.d;
      put(ctx, g, h, pos, { w: W, h: H, draw(c){
        const y1 = -H / 2 + top, x = s => al === 'left' ? -W / 2 + (s === 1 ? ind : 0) : al === 'right' ? W / 2 - (s === 1 ? w1 : N.w) : -(s === 1 ? w1 : N.w) / 2;
        c.fillStyle = C; halo(c, h, g, C);
        W1.draw(c, x(1), y1);
        const hp = new Path2D(); h.heart(hp, x(1) + W1.w + hg + hs * 0.45, y1 - W1.a * 0.42, hs); c.fill(hp);
        N.draw(c, x(2), y1 + b2); } }, lim);
    } });

  MS.register({ id: 'signature.monogram', cat: 'signature', name: 'Monogram badge', pos: 'br',
    draw(ctx, g, p, h, o){
      const t = clean(o.text); if(!t) return; const ini = initials(t, 3); if(!ini.chars.length) return;
      const pos = gridPos(o), lim = room(g, pos, 0.5, 0.42), C = hexOf(ctx, o.color, '#ffffff'), D = 15 * g.k * scaleOf(o), r = D / 2;
      let ls = (ini.chars.length === 1 ? 0.52 : ini.chars.length === 2 ? 0.42 : 0.33) * D;
      const parts = () => { const out = []; ini.chars.forEach((ch, i) => {
        if(i && ini.amp) out.push({ L: line(ctx, '&', h.font(ls * 0.72, 'Playfair Display', 400, 'italic')), amp: true });
        out.push({ L: line(ctx, ch, h.font(ls, 'Cormorant Garamond', 700)) }); }); return out; };
      let P = parts(), gp = () => 0.06 * ls, tw = () => P.reduce((s, q) => s + q.L.w, 0) + gp() * (P.length - 1);
      if(tw() > 0.64 * D){ ls *= 0.64 * D / tw(); P = parts(); }
      const capA = Math.max(...P.filter(q => !q.amp).map(q => q.L.a));
      put(ctx, g, h, pos, { w: D, h: D, draw(c){
        c.fillStyle = light(h, C) ? 'rgba(0,0,0,.34)' : 'rgba(255,255,255,.62)'; h.shadow(c, 0.9 * g.k, 'rgba(0,0,0,.25)', 0, 0.2 * g.k);
        c.beginPath(); c.arc(0, 0, r, 0, TAU); c.fill(); h.shadow(c);
        c.strokeStyle = C; c.lineWidth = 0.032 * D; c.beginPath(); c.arc(0, 0, r - 0.05 * D, 0, TAU); c.stroke();
        c.lineWidth = 0.011 * D; c.beginPath(); c.arc(0, 0, r - 0.11 * D, 0, TAU); c.stroke();
        c.fillStyle = C; halo(c, h, g, C, 0.5); let x = -tw() / 2; const yb = capA / 2;
        P.forEach(q => { c.globalAlpha = q.amp ? 0.85 : 1; q.L.draw(c, x, yb); x += q.L.w + gp(); }); } }, lim);
    } });

  // =====================================================================================
  // DATES
  // =====================================================================================
  MS.register({ id: 'date.camera', cat: 'date', name: 'Camera date (LED)', pos: 'br',
    draw(ctx, g, p, h, o){
      const d = dateOf(o), p2 = n => (n < 10 ? ' ' : '') + n, pos = gridPos(o), lim = room(g, pos, 0.6, 0.3);
      const t = "'" + String(d.getFullYear() % 100).padStart(2, '0') + ' ' + p2(d.getMonth() + 1) + ' ' + p2(d.getDate());
      const user = hexOf(ctx, o.color, null), C = user && user.toLowerCase() !== hexOf(ctx, p.ink, '').toLowerCase() ? user : '#ff8a1e';
      const S = fitSize(ctx, h, t, lim.w, 3.9 * g.k * scaleOf(o), 'Share Tech Mono', 400, null, 0.05), L = line(ctx, t, h.font(S, 'Share Tech Mono'), 0.05 * S);
      put(ctx, g, h, pos, { w: L.w, h: L.h, draw(c){
        const glow = h.mix(C, '#ff3300', 0.3); c.fillStyle = C;
        h.shadow(c, 0.18 * S + 0.5 * g.k, h.rgba(glow, 0.9)); L.at(c, 0, 0);
        h.shadow(c, 0.08 * S, h.rgba(C, 0.9)); L.at(c, 0, 0);
        h.shadow(c); c.globalAlpha = 0.55; c.fillStyle = h.mix(C, '#fff3d0', 0.5); L.at(c, 0, 0); } }, lim, 0.7 * g.k);
    } });

  MS.register({ id: 'date.typewriter', cat: 'date', name: 'Typewriter label', pos: 'bl',
    draw(ctx, g, p, h, o){
      const d = dateOf(o), pos = gridPos(o), lim = room(g, pos, 0.7, 0.3), C = hexOf(ctx, o.color, '#262626');
      const t = clean(o.text) || String(d.getDate()).padStart(2, '0') + ' ' + MON[d.getMonth()].slice(0, 3).toUpperCase() + ' ' + d.getFullYear();
      const rnd = h.rng((p.seed || 7) + hash(t));
      const S = fitSize(ctx, h, t, lim.w * 0.8, 3.5 * g.k * scaleOf(o), 'Special Elite'), L = line(ctx, t, h.font(S, 'Special Elite'));
      const W = L.w + 1.5 * S, H = 1.75 * S, ang = -0.03 - rnd() * 0.025, b = rotBox(W, H, ang);
      const strip = light(h, C) ? 'rgba(24,24,24,.8)' : 'rgba(250,246,234,.95)';
      const ys = [], n = 7; for(let i = 0; i <= n; i++) ys.push([rnd(), rnd()]);
      put(ctx, g, h, pos, { w: b.w, h: b.h, draw(c){
        c.rotate(ang); c.fillStyle = strip; h.shadow(c, 0.6 * g.k, 'rgba(0,0,0,.35)', 0, 0.2 * g.k);
        c.beginPath(); c.moveTo(-W / 2, -H / 2);
        for(let i = 0; i <= n; i++) c.lineTo(W / 2 - ys[i][0] * 0.16 * S, -H / 2 + H * i / n);   // torn right end
        for(let i = n; i >= 0; i--) c.lineTo(-W / 2 + ys[i][1] * 0.16 * S, -H / 2 + H * i / n);  // torn left end
        c.closePath(); c.fill(); h.shadow(c);
        c.fillStyle = C; c.globalAlpha = 0.3; L.at(c, 0.02 * S, 0.015 * S); c.globalAlpha = 0.92; L.at(c, 0, 0); } }, lim);
    } });

  MS.register({ id: 'date.postmark', cat: 'date', name: 'Postmark', pos: 'tr',
    draw(ctx, g, p, h, o){
      const d = dateOf(o), pos = gridPos(o), C = hexOf(ctx, o.color, '#1f1f1f'), lim = room(g, pos, 0.8, 0.5), rnd = h.rng((p.seed || 7) + 101);
      const D = 17 * g.k * scaleOf(o), r = D / 2, lw = 0.04 * D, gap = 0.05 * D, wl = (g.round ? 0.5 : 0.85) * D;
      const dir = pos[1] === 'r' ? -1 : 1, W = D + gap + wl, H = D, cx = -dir * (W / 2 - r);
      const ang = -dir * (0.07 + rnd() * 0.05), b = rotBox(W, H, ang);
      const ring = (clean(o.text) && !/\d/.test(o.text) ? clean(o.text) : DAY[d.getDay()]).toUpperCase();
      put(ctx, g, h, pos, { w: b.w, h: b.h, draw(c){
        c.rotate(ang); halo(c, h, g, C, 0.8); c.globalAlpha = 0.92;
        layer(c, W + 0.6, H + 0.6, L => {
          L.fillStyle = L.strokeStyle = C; L.lineCap = 'round';
          const ri = 0.6 * r; L.lineWidth = lw; L.beginPath(); L.arc(cx, 0, r - lw / 2, 0, TAU); L.stroke();
          L.lineWidth = lw * 0.5; L.beginPath(); L.arc(cx, 0, ri, 0, TAU); L.stroke();
          L.save(); L.translate(cx, 0);
          const Rm = (r - lw + ri + lw * 0.25) / 2; let sz = 0.13 * D;
          for(let i = 0; i < 30; i++){ L.font = h.font(sz, 'Montserrat', 600); const w = Array.from(ring).reduce((s, ch) => s + L.measureText(ch).width + 0.14 * sz, 0); if(w / Rm <= 2.5) break; sz *= 0.94; }
          h.arcText(L, ring, Rm, -PI / 2, { size: sz, family: 'Montserrat', weight: 600, spacing: 0.14, color: C });
          const st = new Path2D(); [-0.42, 0, 0.42].forEach(da => h.star(st, Rm * Math.cos(PI / 2 + da), Rm * Math.sin(PI / 2 + da), 0.042 * D, 5, 0.45)); L.fill(st);
          const l1 = line(L, MON[d.getMonth()].slice(0, 3).toUpperCase(), h.font(0.12 * D, 'Montserrat', 600), 0.12 * 0.12 * D);
          const l2 = line(L, String(d.getDate()), h.font(0.27 * D, 'Montserrat', 800));
          const l3 = line(L, String(d.getFullYear()), h.font(0.12 * D, 'Montserrat', 600), 0.08 * 0.12 * D);
          const g1 = 0.045 * D, th = l1.h + l2.h + l3.h + 2 * g1, mw = Math.max(l1.w, l2.w, l3.w), s = Math.min(1, 1.5 * ri / mw, 1.55 * ri / th);
          L.scale(s, s); let y = -th / 2;
          [l1, l2, l3].forEach(q => { q.draw(L, -q.w / 2, y + q.a); y += q.h + g1; });
          L.restore();
          L.lineWidth = 0.028 * D;
          for(let i = 0; i < 5; i++){ const y0 = (i - 2) * 0.15 * D, xs = cx + dir * (Math.sqrt(Math.max(0, r * r - y0 * y0)) + gap), xe = cx + dir * (r + gap + wl) - dir * 0.03 * D;
            L.beginPath(); for(let j = 0; j <= 48; j++){ const x = xs + (xe - xs) * j / 48, yy = y0 + 0.04 * D * Math.sin((x - cx) / (0.3 * D) * TAU); j ? L.lineTo(x, yy) : L.moveTo(x, yy); } L.stroke(); }
          distress(L, h, W + 0.6, H + 0.6, (p.seed || 7) * 7 + 3, 0.2, 0.05 * D);
        });
      } }, lim);
    } });

  MS.register({ id: 'date.calendar', cat: 'date', name: 'Calendar tile', pos: 'tl',
    draw(ctx, g, p, h, o){
      const d = dateOf(o), pos = gridPos(o), lim = room(g, pos, 0.5, 0.45), A = hexOf(ctx, p.accent, '#c2410c'), body = '#fbfaf6';
      const s = scaleOf(o), Wt = 12.5 * g.k * s, Ht = 14.5 * g.k * s, ring = 0.08 * Ht, hdr = 0.3 * Ht;
      const ink = onBg(h, body, hexOf(ctx, o.color, '#1f1f1f'), 3), grey = h.mix(ink, body, 0.45), HT = onBg(h, A, '#ffffff', 3);
      const mfont = sz => h.font(sz, 'Montserrat', 800);
      let mt = MON[d.getMonth()].toUpperCase(), ms = fitSize(ctx, h, mt, 0.8 * Wt, 0.15 * Ht, 'Montserrat', 800, null, 0.08);
      if(ms < 0.115 * Ht){ mt = mt.slice(0, 3); ms = fitSize(ctx, h, mt, 0.8 * Wt, 0.15 * Ht, 'Montserrat', 800, null, 0.1); }
      const M = line(ctx, mt, mfont(ms), 0.09 * ms);
      const day = line(ctx, String(d.getDate()), h.font(fitSize(ctx, h, String(d.getDate()), 0.78 * Wt, 0.42 * Ht, 'Playfair Display', 700), 'Playfair Display', 700));
      const yr = line(ctx, String(d.getFullYear()), h.font(0.085 * Ht, 'Montserrat', 600), 0.15 * 0.085 * Ht);
      const wd = 0.075 * Ht >= 1.05 ? line(ctx, DAY[d.getDay()].toUpperCase(), h.font(fitSize(ctx, h, DAY[d.getDay()].toUpperCase(), 0.8 * Wt, 0.07 * Ht, 'Montserrat', 600, null, 0.12), 'Montserrat', 600), 0.12 * 0.07 * Ht) : null;
      put(ctx, g, h, pos, { w: Wt, h: Ht + ring, draw(c){
        c.translate(0, ring / 2); const x0 = -Wt / 2, y0 = -Ht / 2;
        h.shadow(c, 0.9 * g.k, 'rgba(0,0,0,.38)', 0, 0.3 * g.k); c.fillStyle = body; roundRect(c, x0, y0, Wt, Ht, 0.1 * Wt); c.fill(); h.shadow(c);
        c.save(); roundRect(c, x0, y0, Wt, Ht, 0.1 * Wt); c.clip(); c.fillStyle = A; c.fillRect(x0, y0, Wt, hdr);
        c.fillStyle = 'rgba(0,0,0,.12)'; c.fillRect(x0, y0 + hdr, Wt, 0.012 * Ht); c.restore();
        c.fillStyle = HT; M.at(c, 0, y0 + hdr * 0.58);
        [-1, 1].forEach(sg => { const x = sg * 0.26 * Wt;
          c.fillStyle = 'rgba(0,0,0,.45)'; c.beginPath(); c.ellipse(x, y0 + 0.075 * Ht, 0.05 * Wt, 0.03 * Ht, 0, 0, TAU); c.fill();
          c.fillStyle = '#3a3a3a'; roundRect(c, x - 0.035 * Wt, y0 - ring, 0.07 * Wt, ring + 0.075 * Ht, 0.035 * Wt); c.fill();
          c.fillStyle = 'rgba(255,255,255,.35)'; c.fillRect(x - 0.018 * Wt, y0 - ring + 0.02 * Ht, 0.012 * Wt, ring * 0.8); });
        const parts = [wd, day, yr].filter(Boolean), gp = 0.05 * Ht, tot = parts.reduce((s2, q) => s2 + q.h, 0) + gp * (parts.length - 1);
        let y = y0 + hdr + (Ht - hdr - tot) / 2;
        parts.forEach(q => { c.fillStyle = q === day ? ink : grey; q.draw(c, -q.w / 2, y + q.a); y += q.h + gp; });
      } }, lim);
    } });

  MS.register({ id: 'date.ribbon', cat: 'date', name: 'Folded ribbon', pos: 'bc',
    draw(ctx, g, p, h, o){
      const d = dateOf(o), pos = gridPos(o), lim = room(g, pos, 0.8, 0.3), A = hexOf(ctx, p.accent, '#c2410c');
      const T = onBg(h, A, hexOf(ctx, o.color, null), 4.5), t = (clean(o.text) || fmtDate(d)).toUpperCase();
      const S = fitSize(ctx, h, t, lim.w * 0.62, 3.1 * g.k * scaleOf(o), 'Montserrat', 600, null, 0.14), L = line(ctx, t, h.font(S, 'Montserrat', 600), 0.14 * S);
      const bw = L.w + 2 * S, bh = 2.05 * S, E = 1.5 * S, Dd = 0.5 * S, N = 0.5 * S;
      put(ctx, g, h, pos, { w: bw + 2 * E, h: bh + Dd, draw(c){
        c.translate(0, -Dd / 2); const bx = bw / 2, by0 = -bh / 2, by1 = bh / 2;
        h.shadow(c, 0.8 * g.k, 'rgba(0,0,0,.35)', 0, 0.25 * g.k);
        [-1, 1].forEach(sg => {
          c.fillStyle = h.mix(A, '#000000', 0.24); c.beginPath(); c.moveTo(sg * (bx - Dd), by0 + Dd); c.lineTo(sg * (bx + E), by0 + Dd);
          c.lineTo(sg * (bx + E - N), Dd); c.lineTo(sg * (bx + E), by1 + Dd); c.lineTo(sg * (bx - Dd), by1 + Dd); c.closePath(); c.fill();
          c.fillStyle = h.mix(A, '#000000', 0.5); c.beginPath(); c.moveTo(sg * bx, by1); c.lineTo(sg * (bx - Dd), by1); c.lineTo(sg * (bx - Dd), by1 + Dd); c.closePath(); c.fill(); });
        c.fillStyle = A; c.fillRect(-bx, by0, bw, bh); h.shadow(c);
        c.strokeStyle = h.rgba(T, 0.35); c.lineWidth = Math.max(0.08, 0.04 * S); c.beginPath();
        c.moveTo(-bx, by0 + 0.2 * S); c.lineTo(bx, by0 + 0.2 * S); c.moveTo(-bx, by1 - 0.2 * S); c.lineTo(bx, by1 - 0.2 * S); c.stroke();
        c.fillStyle = T; L.at(c, 0, 0); } }, lim);
    } });

  MS.register({ id: 'date.serif', cat: 'date', name: 'Serif italic', pos: 'bc',
    draw(ctx, g, p, h, o){
      const d = dateOf(o), pos = gridPos(o), lim = room(g, pos, 0.7, 0.3), C = hexOf(ctx, o.color, '#ffffff');
      const t = clean(o.text) || d.getDate() + ' ' + MON[d.getMonth()] + ' ' + d.getFullYear();
      const S = fitSize(ctx, h, t, lim.w, 4.8 * g.k * scaleOf(o), 'Playfair Display', 400, 'italic'), L = line(ctx, t, h.font(S, 'Playfair Display', 400, 'italic'));
      put(ctx, g, h, pos, { w: L.w, h: L.h, draw(c){ c.fillStyle = C; halo(c, h, g, C); L.at(c, 0, 0); } }, lim);
    } });

  MS.register({ id: 'date.arc', cat: 'date', name: 'Edge arc', pos: 'arc-bottom',
    draw(ctx, g, p, h, o){
      const d = dateOf(o), pos = gridPos(o), C = hexOf(ctx, o.color, '#ffffff'), t = (clean(o.text) || fmtDate(d)).toUpperCase(), S = 2.8 * g.k * scaleOf(o);
      if(edgeCurve(g, pos)){ arcLine(ctx, g, h, t, pos, { size: S, family: 'Montserrat', weight: 600, spacing: 0.32, color: C, orn: 'dot', spanK: 0.92 }); return; }
      const lim = room(g, pos, 0.75, 0.25), Sz = fitSize(ctx, h, t, lim.w * 0.8, S, 'Montserrat', 600, null, 0.32), L = line(ctx, t, h.font(Sz, 'Montserrat', 600), 0.32 * Sz);
      const gap = 0.9 * Sz, r0 = 0.16 * Sz, W = L.w + 2 * (gap + 2 * r0);
      put(ctx, g, h, pos, { w: W, h: L.h, draw(c){ c.fillStyle = C; halo(c, h, g, C); L.at(c, 0, 0);
        const yc = 0; c.beginPath(); [-1, 1].forEach(sg => { const x = sg * (W / 2 - r0); c.moveTo(x + r0, yc); c.arc(x, yc, r0, 0, TAU); }); c.fill(); } }, lim);
    } });

  MS.register({ id: 'date.minimal', cat: 'date', name: 'Minimal tracked', pos: 'bc',
    draw(ctx, g, p, h, o){
      const d = dateOf(o), pos = gridPos(o), lim = room(g, pos, 0.75, 0.25), C = hexOf(ctx, o.color, '#ffffff');
      const t = (clean(o.text) || fmtDate(d)).toUpperCase();
      const S = fitSize(ctx, h, t, lim.w, 2.7 * g.k * scaleOf(o), 'Montserrat', 600, null, 0.45), L = line(ctx, t, h.font(S, 'Montserrat', 600), 0.45 * S);
      put(ctx, g, h, pos, { w: L.w, h: L.h, draw(c){ c.fillStyle = C; halo(c, h, g, C, 0.9); L.at(c, 0, 0); } }, lim);
    } });

  // =====================================================================================
  // BRAND MARKS
  // =====================================================================================
  function wordmark(ctx, g, p, h, o){
    const t = clean(o.text).toUpperCase(); if(!t) return;
    const pos = gridPos(o), C = hexOf(ctx, o.color, '#ffffff'), S = 3.8 * g.k * scaleOf(o);
    if(isArc(g, o)){ arcLine(ctx, g, h, t, pos, { size: S, family: 'Montserrat', weight: 800, spacing: 0.24, color: C }); return; }
    const lim = room(g, pos, 0.7, 0.25), Sz = fitSize(ctx, h, t, lim.w, S, 'Montserrat', 800, null, 0.24), L = line(ctx, t, h.font(Sz, 'Montserrat', 800), 0.24 * Sz);
    put(ctx, g, h, pos, { w: L.w, h: L.h, draw(c){ c.fillStyle = C; halo(c, h, g, C, 0.9); L.at(c, 0, 0); } }, lim);
  }
  MS.register({ id: 'brand.wordmark', cat: 'brand', name: 'Wordmark', pos: 'bc', draw: wordmark });

  MS.register({ id: 'brand.pill', cat: 'brand', name: 'Pill badge', pos: 'br',
    draw(ctx, g, p, h, o){
      const t = clean(o.text).toUpperCase(); if(!t) return;
      const pos = gridPos(o), lim = room(g, pos, 0.7, 0.25), A = hexOf(ctx, p.accent, '#c2410c'), T = onBg(h, A, hexOf(ctx, o.color, '#ffffff'));
      const S = fitSize(ctx, h, t, lim.w * 0.78, 2.5 * g.k * scaleOf(o), 'Montserrat', 600, null, 0.16), L = line(ctx, t, h.font(S, 'Montserrat', 600), 0.16 * S);
      const ph = 2.3 * S, pw = L.w + 2.1 * S;
      put(ctx, g, h, pos, { w: pw, h: ph, draw(c){
        h.shadow(c, 0.8 * g.k, 'rgba(0,0,0,.35)', 0, 0.25 * g.k); c.fillStyle = A; roundRect(c, -pw / 2, -ph / 2, pw, ph, ph / 2); c.fill(); h.shadow(c);
        const e = 0.26 * S; c.strokeStyle = h.rgba(T, 0.45); c.lineWidth = Math.max(0.08, 0.04 * S); roundRect(c, -pw / 2 + e, -ph / 2 + e, pw - 2 * e, ph - 2 * e, ph / 2 - e); c.stroke();
        c.fillStyle = T; L.at(c, 0, 0); } }, lim);
    } });

  MS.register({ id: 'brand.seal', cat: 'brand', name: 'Seal emblem', pos: 'br',
    draw(ctx, g, p, h, o){
      const t = clean(o.text); if(!t) return;
      const pos = gridPos(o), lim = room(g, pos, 0.5, 0.42), A = hexOf(ctx, p.accent, '#c2410c'), T = onBg(h, A, hexOf(ctx, o.color, '#ffffff'));
      const D = 18 * g.k * scaleOf(o), r = D / 2, ri = 0.6 * r, Rm = (0.9 * r + ri) / 2, up = t.toUpperCase(), ini = initials(t, 3).chars.join('') || up[0];
      let sz = 0.125 * D;
      for(let i = 0; i < 30; i++){ ctx.font = h.font(sz, 'Cinzel', 700); const w = Array.from(up).reduce((s, ch) => s + ctx.measureText(ch).width + 0.2 * sz, 0); if(w / Rm <= 1.2 * PI) break; sz *= 0.94; }
      const I = line(ctx, ini, h.font(fitSize(ctx, h, ini, 1.45 * ri, (ini.length > 1 ? 0.3 : 0.4) * D, 'Playfair Display', 700), 'Playfair Display', 700));
      put(ctx, g, h, pos, { w: D, h: D, draw(c){
        h.shadow(c, 0.9 * g.k, 'rgba(0,0,0,.35)', 0, 0.3 * g.k); c.fillStyle = A; c.beginPath(); c.arc(0, 0, r, 0, TAU); c.fill(); h.shadow(c);
        c.strokeStyle = T; c.lineWidth = 0.022 * D; c.beginPath(); c.arc(0, 0, 0.93 * r, 0, TAU); c.stroke();
        c.lineWidth = 0.01 * D; c.beginPath(); c.arc(0, 0, ri, 0, TAU); c.stroke();
        c.setLineDash([0.012 * D, 0.02 * D]); c.beginPath(); c.arc(0, 0, 0.86 * r, 0, TAU); c.stroke(); c.setLineDash([]);
        h.arcText(c, up, Rm, -PI / 2, { size: sz, family: 'Cinzel', weight: 700, spacing: 0.2, color: T });
        const st = new Path2D(); [-0.36, 0, 0.36].forEach(da => h.star(st, Rm * Math.cos(PI / 2 + da), Rm * Math.sin(PI / 2 + da), (da ? 0.04 : 0.055) * D, 5, 0.45));
        c.fillStyle = T; c.fill(st); I.at(c, 0, 0); } }, lim);
    } });

  MS.register({ id: 'brand.monogram', cat: 'brand', name: 'Monogram square', pos: 'br',
    draw(ctx, g, p, h, o){
      const t = clean(o.text); if(!t) return; const ini = initials(t, 3).chars.join(''); if(!ini) return;
      const pos = gridPos(o), lim = room(g, pos, 0.4, 0.35), A = hexOf(ctx, p.accent, '#c2410c'), T = onBg(h, A, hexOf(ctx, o.color, '#ffffff'));
      const Q = 10.5 * g.k * scaleOf(o), L = line(ctx, ini, h.font(fitSize(ctx, h, ini, 0.66 * Q, (ini.length > 1 ? 0.42 : 0.55) * Q, 'Montserrat', 800, null, 0.02), 'Montserrat', 800), 0.02 * Q);
      put(ctx, g, h, pos, { w: Q, h: Q, draw(c){
        h.shadow(c, 0.9 * g.k, 'rgba(0,0,0,.35)', 0, 0.3 * g.k); c.fillStyle = A; roundRect(c, -Q / 2, -Q / 2, Q, Q, 0.22 * Q); c.fill(); h.shadow(c);
        const e = 0.075 * Q; c.strokeStyle = h.rgba(T, 0.5); c.lineWidth = 0.018 * Q; roundRect(c, -Q / 2 + e, -Q / 2 + e, Q - 2 * e, Q - 2 * e, 0.16 * Q); c.stroke();
        c.fillStyle = T; L.at(c, 0, 0); } }, lim);
    } });

  // corner tag (triangle folded over a corner) and sash (diagonal ribbon): text across a corner, or along an edge, or in the middle
  // where a tw × th text box sits across corner pos: centre, rotation, unit vector u to the corner, coordinate lam along u
  function cornerFit(g, pos, tw, th, m1){
    const sx = pos[1] === 'l' ? -1 : 1, sy = pos[0] === 't' ? -1 : 1, ux = sx / Math.SQRT2, uy = sy / Math.SQRT2, ang = sx * sy > 0 ? -PI / 4 : PI / 4;
    if(!g.round){ const t = tw / 2 + m1 + th / 2, cx = sx * g.safeW / 2 - t * ux, cy = sy * g.safeH / 2 - t * uy; return { cx, cy, ang, ux, uy, lam: cx * ux + cy * uy }; }
    const q = Math.pow(g.safeR, 2) - Math.pow(tw / 2 + m1, 2); if(q <= 0) return null;
    const lam = Math.sqrt(q) - th / 2; return { cx: lam * ux, cy: lam * uy, ang, ux, uy, lam };
  }
  function cornerMark(ctx, g, p, h, o, sash){
    const t = clean(o.text).toUpperCase(); if(!t) return;
    const pos = gridPos(o), k = g.k, A = hexOf(ctx, p.accent, '#c2410c'), T = onBg(h, A, hexOf(ctx, o.color, '#ffffff')), sp = sash ? 0.16 : 0.13;
    const mk = S => line(ctx, t, h.font(S, 'Montserrat', 800), sp * S), mf = sash ? 0.6 : 0.75, B = g.cutW + g.cutH, pad = 0.45 * k;
    let S = (sash ? 2.5 : 2.4) * k * scaleOf(o), L = mk(S);
    const text = (x, y, a) => { ctx.save(); ctx.translate(x, y); ctx.rotate(a); ctx.fillStyle = T; L.draw(ctx, -L.w / 2, (L.a - L.d) / 2); ctx.restore(); };
    const stitch = (draw) => { ctx.save(); ctx.strokeStyle = h.rgba(T, 0.6); ctx.lineWidth = Math.max(0.08, 0.05 * S); ctx.setLineDash([0.5 * S, 0.32 * S]); ctx.beginPath(); draw(); ctx.stroke(); ctx.restore(); };
    ctx.save();
    if(pos[0] !== 'm' && pos[1] !== 'c'){                  // ---- corner
      let F = null, th = 0;
      for(let i = 0; i < 45; i++){ L = mk(S); th = Math.max(L.h, 0.72 * S); F = cornerFit(g, pos, L.w, th, 0.7 + 0.25 * k);
        if(F){ const lh = F.lam - th / 2 - mf * th, reach = g.round ? g.W / 2 - lh : (g.W + g.H) / 2 - lh * Math.SQRT2;
          if(reach <= (g.round ? 0.62 * g.W / 2 : 0.52 * g.min)) break; }
        S *= 0.93; }
      if(!F){ ctx.restore(); return; }
      const ux = F.ux, uy = F.uy, vx = -uy, vy = ux, lo = F.lam - th / 2 - mf * th, hi = sash ? F.lam + th / 2 + mf * th : lo + B;
      const strip = (a, b2) => { ctx.beginPath(); ctx.moveTo(a * ux + B * vx, a * uy + B * vy); ctx.lineTo(a * ux - B * vx, a * uy - B * vy); ctx.lineTo(b2 * ux - B * vx, b2 * uy - B * vy); ctx.lineTo(b2 * ux + B * vx, b2 * uy + B * vy); ctx.closePath(); };
      h.shadow(ctx, 1.1 * k, 'rgba(0,0,0,.4)', -ux * 0.35 * k, -uy * 0.35 * k);
      if(sash){ ctx.fillStyle = A; strip(lo, hi); ctx.fill(); h.shadow(ctx);
        const e = 0.35 * mf * th; stitch(() => { [lo + e, hi - e].forEach(a => { ctx.moveTo(a * ux + B * vx, a * uy + B * vy); ctx.lineTo(a * ux - B * vx, a * uy - B * vy); }); }); }
      else { const gr = ctx.createLinearGradient(lo * ux, lo * uy, (lo + 1.4 * th) * ux, (lo + 1.4 * th) * uy);
        gr.addColorStop(0, h.mix(A, '#000000', 0.3)); gr.addColorStop(0.35, A); gr.addColorStop(1, A); ctx.fillStyle = gr; strip(lo, hi); ctx.fill(); h.shadow(ctx);
        ctx.strokeStyle = 'rgba(255,255,255,.35)'; ctx.lineWidth = Math.max(0.08, 0.04 * S); const a = lo + 0.18 * th;
        ctx.beginPath(); ctx.moveTo(a * ux + B * vx, a * uy + B * vy); ctx.lineTo(a * ux - B * vx, a * uy - B * vy); ctx.stroke(); }
      text(F.cx, F.cy, F.ang);
    } else if(pos !== 'mc'){                               // ---- edge: tab (corner tag) or straight band (sash)
      const vert = pos[0] === 'm', rot = { tc: 0, mr: PI / 2, bc: PI, ml: -PI / 2 }[pos], tr = vert ? rot : 0;
      let at, th = 0, along = 0, across = 0;
      for(let i = 0; i < 45; i++){ L = mk(S); th = Math.max(L.h, 0.72 * S); along = L.w + (sash ? 0 : 2 * 0.9 * S); across = th + 2 * mf * th;
        const bw = vert ? across : along, bh = vert ? along : across; at = h.placeBox(g, pos, bw, bh, pad);
        const ok = g.round ? Math.hypot(Math.abs(at.x) + bw / 2, Math.abs(at.y) + bh / 2) <= g.safeR - pad + 1e-6 : bw <= g.safeW - 2 * pad + 1e-6 && bh <= g.safeH - 2 * pad + 1e-6;
        if(ok) break; S *= 0.93; }
      ctx.save(); ctx.translate(at.x, at.y); ctx.rotate(rot); h.shadow(ctx, 1.1 * k, 'rgba(0,0,0,.4)', 0, 0.3 * k); ctx.fillStyle = A;
      if(sash){ ctx.fillRect(-B, -across / 2, 2 * B, across); h.shadow(ctx); const e = 0.35 * mf * th;
        stitch(() => { ctx.moveTo(-B, -across / 2 + e); ctx.lineTo(B, -across / 2 + e); ctx.moveTo(-B, across / 2 - e); ctx.lineTo(B, across / 2 - e); }); }
      else { const rr = 0.32 * across, x0 = -along / 2, x1 = along / 2, y1 = across / 2;
        ctx.beginPath(); ctx.moveTo(x0, -B); ctx.lineTo(x1, -B); ctx.arcTo(x1, y1, x0, y1, rr); ctx.arcTo(x0, y1, x0, -B, rr); ctx.closePath(); ctx.fill(); h.shadow(ctx);
        stitch(() => { const e = 0.3 * mf * th; ctx.moveTo(x0 + e, -B); ctx.lineTo(x0 + e, y1 - e - rr * 0.3); ctx.lineTo(x1 - e, y1 - e - rr * 0.3); ctx.lineTo(x1 - e, -B); }); }
      ctx.restore(); text(at.x, at.y, tr);
    } else if(sash){                                       // ---- middle: diagonal band through the centre
      let th = 0;
      for(let i = 0; i < 45; i++){ L = mk(S); th = Math.max(L.h, 0.72 * S);
        const ok = g.round ? Math.hypot(L.w / 2, th / 2) <= g.safeR - pad : (L.w + th) / (2 * Math.SQRT2) <= Math.min(g.safeW, g.safeH) / 2 - pad;
        if(ok) break; S *= 0.93; }
      const across = th + 2 * mf * th, e = 0.35 * mf * th;
      ctx.save(); ctx.rotate(-PI / 4); h.shadow(ctx, 1.1 * k, 'rgba(0,0,0,.4)', 0, 0.3 * k); ctx.fillStyle = A; ctx.fillRect(-B, -across / 2, 2 * B, across); h.shadow(ctx);
      stitch(() => { ctx.moveTo(-B, -across / 2 + e); ctx.lineTo(B, -across / 2 + e); ctx.moveTo(-B, across / 2 - e); ctx.lineTo(B, across / 2 - e); });
      ctx.restore(); text(0, 0, -PI / 4);
    } else {                                               // ---- middle: a free tag with a dog-eared corner
      const lim = room(g, pos, 1, 0.3); S = fitSize(ctx, h, t, lim.w * 0.75, S, 'Montserrat', 800, null, sp); L = mk(S);
      const th = Math.max(L.h, 0.72 * S), bh = th * 2.5, bw = L.w + 2.2 * S, e = 0.4 * bh, rr = 0.18 * bh;
      put(ctx, g, h, pos, { w: bw, h: bh, draw(c){
        c.beginPath(); c.moveTo(-bw / 2 + rr, -bh / 2); c.lineTo(bw / 2 - e, -bh / 2); c.lineTo(bw / 2, -bh / 2 + e); c.arcTo(bw / 2, bh / 2, -bw / 2, bh / 2, rr);
        c.arcTo(-bw / 2, bh / 2, -bw / 2, -bh / 2, rr); c.arcTo(-bw / 2, -bh / 2, bw / 2, -bh / 2, rr); c.closePath();
        h.shadow(c, 1 * k, 'rgba(0,0,0,.38)', 0, 0.3 * k); c.fillStyle = A; c.fill(); h.shadow(c);
        c.beginPath(); c.moveTo(bw / 2 - e, -bh / 2); c.lineTo(bw / 2 - e, -bh / 2 + e * 0.85); c.quadraticCurveTo(bw / 2 - e, -bh / 2 + e, bw / 2 - e * 0.85, -bh / 2 + e); c.lineTo(bw / 2, -bh / 2 + e); c.closePath();
        h.shadow(c, 0.5 * k, 'rgba(0,0,0,.35)', -0.15 * k, 0.15 * k); c.fillStyle = h.mix(A, '#ffffff', 0.32); c.fill(); h.shadow(c);
        c.fillStyle = T; L.at(c, -0.12 * e, 0); } }, lim);
    }
    ctx.restore();
  }
  MS.register({ id: 'brand.corner-tag', cat: 'brand', name: 'Corner tag', pos: 'tr', draw(ctx, g, p, h, o){ cornerMark(ctx, g, p, h, o, false); } });
  MS.register({ id: 'brand.sash', cat: 'brand', name: 'Corner sash', pos: 'tl', draw(ctx, g, p, h, o){ cornerMark(ctx, g, p, h, o, true); } });

  MS.register({ id: 'brand.copyright', cat: 'brand', name: 'Copyright line', pos: 'br',
    draw(ctx, g, p, h, o){
      let t = clean(o.text); if(!t) return; if(!/^(©|\(c\))/i.test(t)) t = '© ' + t;
      const pos = gridPos(o), C = hexOf(ctx, o.color, '#ffffff'), S = Math.max(1.5 * Math.min(1, scaleOf(o)), 2.1 * g.k * scaleOf(o));
      if(isArc(g, o)){ arcLine(ctx, g, h, t, pos, { size: S, family: 'Montserrat', weight: 600, spacing: 0.06, color: C, haloAmt: 0.8 }); return; }
      const lim = room(g, pos, 0.7, 0.2), Sz = fitSize(ctx, h, t, lim.w, S, 'Montserrat', 600, null, 0.06), L = line(ctx, t, h.font(Sz, 'Montserrat', 600), 0.06 * Sz);
      put(ctx, g, h, pos, { w: L.w, h: L.h, draw(c){ c.fillStyle = C; halo(c, h, g, C, 0.8); L.at(c, 0, 0); } }, lim);
    } });

  MS.register({ id: 'brand.stamp', cat: 'brand', name: 'Rubber stamp', pos: 'bl',
    draw(ctx, g, p, h, o){
      const t = clean(o.text).toUpperCase(); if(!t) return;
      const pos = gridPos(o), lim = room(g, pos, 0.7, 0.4), C = hexOf(ctx, o.color, '#ffffff'), seed = (p.seed || 7) * 31 + hash(t), rnd = h.rng(seed);
      const S = fitSize(ctx, h, t, lim.w * 0.62, 5 * g.k * scaleOf(o), 'Bebas Neue', 400, null, 0.08), L = line(ctx, t, h.font(S, 'Bebas Neue'), 0.08 * S);
      const st = 0.17 * S, gs = 0.32 * S, padX = 0.45 * S, bw = L.w + 2 * (gs + 2 * st + padX), bh = L.a + 1.05 * S, lw = 0.1 * S, ins = 0.24 * S;
      const ang = (rnd() < 0.5 ? -1 : 1) * (0.06 + rnd() * 0.05), W = bw + lw + 0.4, H = bh + lw + 0.4, b = rotBox(W, H, ang);
      put(ctx, g, h, pos, { w: b.w, h: b.h, draw(c){
        c.rotate(ang); halo(c, h, g, C, 0.7); c.globalAlpha = 0.9;
        layer(c, W, H, Lc => {
          Lc.strokeStyle = Lc.fillStyle = C; Lc.lineJoin = 'round';
          const rough = (w, hh, r, jit, lwd) => { const pts = rrPoints(w, hh, r, Math.max(0.2, S * 0.12)); Lc.lineWidth = lwd; Lc.beginPath();
            pts.forEach((q, i) => { const x = q[0] + (rnd() - 0.5) * jit, y = q[1] + (rnd() - 0.5) * jit; i ? Lc.lineTo(x, y) : Lc.moveTo(x, y); }); Lc.closePath(); Lc.stroke(); };
          rough(bw, bh, 0.14 * S, 0.05 * S, lw); rough(bw - 2 * ins, bh - 2 * ins, 0.08 * S, 0.03 * S, lw * 0.4);
          L.draw(Lc, -L.w / 2, L.a / 2);
          const sp = new Path2D(); [-1, 1].forEach(sg => h.star(sp, sg * (L.w / 2 + gs + st), -0.02 * S, st, 5, 0.45)); Lc.fill(sp);
          distress(Lc, h, W, H, seed, 0.3, 0.1 * S);
        });
      } }, lim);
    } });

  MS.register({ id: 'brand.arc', cat: 'brand', name: 'Small caps arc / band', pos: 'arc-top',
    draw(ctx, g, p, h, o){
      const t = clean(o.text); if(!t) return;
      const pos = gridPos(o), k = g.k, C = hexOf(ctx, o.color, '#ffffff'), S0 = 3 * k * scaleOf(o), fam = 'Montserrat', wt = 600, sp = 0.3;
      if(edgeCurve(g, pos)){
        const at = ANG[pos], bottom = Math.sin(at) > 0.01, pad = 0.45 * k, maxSpan = pos[1] === 'c' ? 2.1 : 1.0;
        let S = S0, sc, Rb;
        for(let i = 0; i < 45; i++){ sc = smallCaps(ctx, h, t, S, fam, wt, sp, 0.78); Rb = g.safeR - pad - 0.1 - (bottom ? 0.12 * S : sc.a); if(sc.w / Rb <= maxSpan) break; S *= 0.95; }
        ctx.save(); halo(ctx, h, g, C, 0.9); ctx.fillStyle = C;
        const span = arcItems(ctx, sc.items, Rb, at, bottom), rc = Rb + (bottom ? -1 : 1) * sc.a / 2, ga = 1.0 * S / Rb, P = new Path2D();
        [-1, 1].forEach(sg => { const a = at + sg * (span / 2 + ga); h.star(P, rc * Math.cos(a), rc * Math.sin(a), 0.3 * S, 5, 0.45); }); ctx.fill(P);
        ctx.restore(); return;
      }
      const A = hexOf(ctx, p.accent, '#c2410c'), T = onBg(h, A, C);
      bandMark(ctx, g, h, pos, S => { const sc = smallCaps(ctx, h, t, S, fam, wt, sp, 0.78);
        return { w: sc.w, h: sc.a, draw(c, x, yc){ c.fillStyle = T; sc.draw(c, x, yc + sc.a / 2); } }; },
        { S: S0 * 0.9, padY: 0.75, fill: h.rgba(A, 0.92), rules: h.rgba(T, 0.5), flush: true });
    } });

  MS.register({ id: 'brand.logo', cat: 'brand', name: 'Logo image', pos: 'br',
    draw(ctx, g, p, h, o){
      const img = p.logo, iw = img && (img.naturalWidth || img.width), ih = img && (img.naturalHeight || img.height);
      if(!(iw > 0 && ih > 0) || img.complete === false){ wordmark(ctx, g, p, h, o); return; }
      const pos = gridPos(o), lim = room(g, pos, 0.6, 0.35), M = 13 * g.k * scaleOf(o), sc = Math.min(1.8 * M / iw, M / ih), w = iw * sc, hh = ih * sc;
      put(ctx, g, h, pos, { w, h: hh, draw(c){ h.shadow(c, 0.6 * g.k, 'rgba(0,0,0,.3)', 0, 0.15 * g.k); c.drawImage(img, -w / 2, -hh / 2, w, hh); } }, lim);
    } });

  // =====================================================================================
  // CAPTIONS
  // =====================================================================================
  MS.register({ id: 'caption.title', cat: 'caption', name: 'Title (Abril Fatface)', pos: 'bc',
    draw(ctx, g, p, h, o){
      const t = clean(o.text); if(!t) return;
      const pos = gridPos(o), lim = room(g, pos, 0.8, 0.45), C = hexOf(ctx, o.color, '#ffffff'), al = alignOf(pos);
      const F = flow(ctx, h, t, lim.w * 0.98, 10.5 * g.k * scaleOf(o), 'Abril Fatface', 400, null, 2), S = F.size;
      const B = block(ctx, F.lines, h.font(S, 'Abril Fatface'), 1.05 * S), rt = Math.max(0.14, 0.04 * S), gap = 0.24 * S, rw = Math.min(B.w, Math.max(4 * g.k, 0.42 * B.w));
      const H = B.h + gap + rt;
      put(ctx, g, h, pos, { w: B.w, h: H, draw(c){
        c.fillStyle = C; halo(c, h, g, C); B.draw(c, al, -B.w / 2, -H / 2);
        const x = al === 'left' ? -B.w / 2 : al === 'right' ? B.w / 2 - rw : -rw / 2; c.fillRect(x, H / 2 - rt, rw, rt); } }, lim);
    } });

  MS.register({ id: 'caption.quote', cat: 'caption', name: 'Quote (italic)', pos: 'mc',
    draw(ctx, g, p, h, o){
      const t = clean(clean(o.text).replace(/^["“”'‘’«»„]+|["“”'‘’«»„]+$/g, '')); if(!t) return;
      const pos = gridPos(o), lim = room(g, pos, 0.75, 0.45), C = hexOf(ctx, o.color, '#ffffff'), al = alignOf(pos);
      const F = flow(ctx, h, t, lim.w * 0.95, 5 * g.k * scaleOf(o), 'Playfair Display', 400, 'italic', 3), S = F.size;
      const B = block(ctx, F.lines, h.font(S, 'Playfair Display', 400, 'italic'), 1.28 * S), Q = line(ctx, '“', h.font(3 * S, 'Playfair Display', 700));
      const gap = 0.12 * S, W = Math.max(B.w, Q.w), H = Q.h + gap + B.h;
      put(ctx, g, h, pos, { w: W, h: H, draw(c){
        c.fillStyle = C; halo(c, h, g, C);
        c.globalAlpha = 0.9; Q.draw(c, al === 'left' ? -W / 2 : al === 'right' ? W / 2 - Q.w : -Q.w / 2, -H / 2 + Q.a); c.globalAlpha = 1;
        B.draw(c, al, -B.w / 2, -H / 2 + Q.h + gap); } }, lim);
    } });

  MS.register({ id: 'caption.banner', cat: 'caption', name: 'Banner across', pos: 'bc',
    draw(ctx, g, p, h, o){
      const t = clean(o.text); if(!t) return;
      const pos = gridPos(o), A = hexOf(ctx, p.accent, '#c2410c'), T = onBg(h, A, hexOf(ctx, o.color, '#ffffff'));
      bandMark(ctx, g, h, pos, S => { const L = line(ctx, t, h.font(S, 'Cinzel', 700), 0.08 * S);
        return { w: L.w, h: L.h, draw(c, x, yc){ c.fillStyle = T; L.draw(c, x, yc - L.h / 2 + L.a); } }; },
        { S: 4.6 * g.k * scaleOf(o), padY: 0.62, fill: A, rules: h.rgba(T, 0.55) });
    } });

  MS.register({ id: 'caption.arc', cat: 'caption', name: 'Arc / top band', pos: 'arc-top',
    draw(ctx, g, p, h, o){
      const t = clean(o.text).toUpperCase(); if(!t) return;
      const pos = gridPos(o), C = hexOf(ctx, o.color, '#ffffff'), S = 5 * g.k * scaleOf(o);
      if(edgeCurve(g, pos)){ arcLine(ctx, g, h, t, pos, { size: S, family: 'Montserrat', weight: 800, spacing: 0.12, color: C, spanK: 1.1, haloAmt: 1.2 }); return; }
      bandMark(ctx, g, h, pos, Sz => { const L = line(ctx, t, h.font(Sz, 'Montserrat', 800), 0.12 * Sz);
        return { w: L.w, h: L.h, draw(c, x, yc){ c.fillStyle = C; L.draw(c, x, yc - L.h / 2 + L.a); } }; },
        { S: S * 0.85, padY: 0.5, fill: light(h, C) ? 'rgba(0,0,0,.4)' : 'rgba(255,255,255,.66)', flush: true });
    } });

  MS.register({ id: 'caption.bold', cat: 'caption', name: 'Bold block (Bebas Neue)', pos: 'bl',
    draw(ctx, g, p, h, o){
      const t = clean(o.text).toUpperCase(); if(!t) return;
      const pos = gridPos(o), lim = room(g, pos, 0.7, 0.5), C = hexOf(ctx, o.color, '#ffffff'), al = alignOf(pos);
      const maxW = Math.min(lim.w, (g.round ? 2 * g.safeR : g.safeW) * 0.62), F = flow(ctx, h, t, maxW, 9 * g.k * scaleOf(o), 'Bebas Neue', 400, null, 3, 0.02);
      const base = F.lines.map(s => line(ctx, s, h.font(F.size, 'Bebas Neue'), 0.02 * F.size)), bw = Math.max(...base.map(L => L.w));
      const Ls = base.map((L, i) => { const s = F.size * Math.min(1.5, bw / Math.max(0.01, L.w)); return line(ctx, F.lines[i], h.font(s, 'Bebas Neue'), 0.02 * s); });
      const gap = 0.14 * F.size, W = Math.max(...Ls.map(L => L.w)), H = Ls.reduce((s, L) => s + L.h, 0) + gap * (Ls.length - 1);
      put(ctx, g, h, pos, { w: W, h: H, draw(c){
        c.fillStyle = C; halo(c, h, g, C, 1.1); let y = -H / 2;
        Ls.forEach(L => { L.draw(c, al === 'left' ? -W / 2 : al === 'right' ? W / 2 - L.w : -L.w / 2, y + L.a); y += L.h + gap; }); } }, lim);
    } });

  MS.register({ id: 'caption.script', cat: 'caption', name: 'Script (Lobster)', pos: 'tc',
    draw(ctx, g, p, h, o){
      const t = clean(o.text); if(!t) return;
      const pos = gridPos(o), lim = room(g, pos, 0.75, 0.42), C = hexOf(ctx, o.color, '#ffffff'), al = alignOf(pos), dark = light(h, C);
      const F = flow(ctx, h, t, lim.w * 0.96, 8.6 * g.k * scaleOf(o), 'Lobster', 400, null, 2), S = F.size;
      const B = block(ctx, F.lines, h.font(S, 'Lobster'), 1.08 * S), ox = 0.05 * S, oy = 0.065 * S, W = B.w + ox, H = B.h + oy;
      put(ctx, g, h, pos, { w: W, h: H, draw(c){
        c.fillStyle = dark ? 'rgba(0,0,0,.45)' : 'rgba(255,255,255,.75)'; B.draw(c, al, -W / 2 + ox, -H / 2 + oy);
        c.fillStyle = C; h.shadow(c, 0.5 * g.k, dark ? 'rgba(0,0,0,.35)' : 'rgba(255,255,255,.5)'); B.draw(c, al, -W / 2, -H / 2); } }, lim);
    } });
})();
