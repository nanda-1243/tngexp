/* MagPress magnet studio: shared core (sizes, geometry, drawing helpers, style registry, cell renderer).

   Units are mm. Every style draws on a CanvasRenderingContext2D that is already scaled so 1 unit = 1 mm,
   with the origin at the centre of the magnet face and y pointing down. The context is clipped to the
   paper cut outline, so a style may draw into the 6 mm bleed (it folds over the edge) but nothing outside it.

   A style is registered with MS.register({ id, cat, name, draw(ctx, g, p, h, o) }):
     cat  'frame' | 'pattern' | 'signature' | 'date' | 'brand' | 'caption' | 'preset'
     g    geometry of the magnet (MS.geom): shape, W, H, r, cut and safe sizes
     p    colours and shared settings: { ink, accent, paper, seed, logo }
     h    the helpers below (MS.h)
     o    marks only (signature, date, brand, caption): { text, date, pos, color, size }
   Presets have no draw(); they carry set: { frame, pattern, photo, colors, signature, date, brand, caption }.
*/
(function(){
  'use strict';
  const SIZES = [
    {id:'s50', label:'50 × 50',     shape:'rect',  W:50,   H:50},
    {id:'s63', label:'63.5 × 63.5', shape:'rect',  W:63.5, H:63.5},
    {id:'r53', label:'53 × 80',     shape:'rect',  W:53,   H:80},
    {id:'r65', label:'65 × 90',     shape:'rect',  W:65,   H:90},
    {id:'c44', label:'Ø44',         shape:'round', W:44,   H:44},
    {id:'c50', label:'Ø50',         shape:'round', W:50,   H:50},
    {id:'c56', label:'Ø56',         shape:'round', W:56,   H:56},
    {id:'c58', label:'Ø58',         shape:'round', W:58,   H:58}];
  // square and rectangular magnets have sharp corners (R1 at the face, like commercial photo magnets) and square-cut paper
  const BLEED = 6, SAFE_IN = 3, R_FACE = 1, R_CUT = 0;
  const POS = ['tl', 'tc', 'tr', 'ml', 'mc', 'mr', 'bl', 'bc', 'br', 'arc-top', 'arc-bottom'];

  // geometry of one magnet; rectangles are portrait unless landscape is set
  function geom(size, landscape){
    let W = size.W, H = size.H;
    if(size.shape === 'rect' && W !== H && !!landscape === (W < H)){ const t = W; W = H; H = t; }
    const round = size.shape === 'round';
    return { id: size.id, label: size.label, shape: size.shape, round, W, H,
      r: round ? W / 2 : R_FACE,                       // face corner radius (round: the radius)
      bleed: BLEED, cutW: W + 2 * BLEED, cutH: H + 2 * BLEED, cutR: round ? W / 2 + BLEED : R_CUT,
      safeW: W - 2 * SAFE_IN, safeH: H - 2 * SAFE_IN, safeR: round ? W / 2 - SAFE_IN : 0,
      min: Math.min(W, H), max: Math.max(W, H), k: Math.min(W, H) / 63.5 };   // k: size factor, 1 at 63.5
  }

  // ---------- paths ----------
  function shapePath(w, hh, r, round, path){
    const P = path || new Path2D();
    if(round){ P.moveTo(w / 2, 0); P.arc(0, 0, w / 2, 0, Math.PI * 2); P.closePath(); return P; }
    r = Math.max(0, Math.min(r, w / 2, hh / 2)); const x = -w / 2, y = -hh / 2;
    P.moveTo(x + r, y); P.arcTo(x + w, y, x + w, y + hh, r); P.arcTo(x + w, y + hh, x, y + hh, r);
    P.arcTo(x, y + hh, x, y, r); P.arcTo(x, y, x + w, y, r); P.closePath(); return P;
  }
  // face outline offset inward by `inset` mm (negative = outward, into the bleed)
  const face = (g, inset) => { inset = inset || 0; return shapePath(g.W - 2 * inset, g.H - 2 * inset, g.round ? 0 : Math.max(0, g.r - inset), g.round); };
  const safe = g => shapePath(g.safeW, g.safeH, g.round ? 0 : g.safeR, g.round);
  const cut = g => shapePath(g.cutW, g.cutH, g.cutR, g.round);

  // points spaced about `step` mm apart along the face outline offset inward by `inset`:
  // fn(x, y, tangentAngle, i, n). The outline runs clockwise on screen from the top centre.
  function alongEdge(g, inset, step, fn){
    const w = g.W - 2 * inset, hh = g.H - 2 * inset;
    if(g.round){ const R = w / 2, n = Math.max(3, Math.round(2 * Math.PI * R / step));
      for(let i = 0; i < n; i++){ const a = -Math.PI / 2 + 2 * Math.PI * i / n; fn(R * Math.cos(a), R * Math.sin(a), a + Math.PI / 2, i, n); } return n; }
    const r = Math.max(0, Math.min(g.r - inset, w / 2, hh / 2)), sx = w / 2 - r, sy = hh / 2 - r, q = Math.PI * r / 2;
    const segs = [['L', -0, -hh / 2, 1, 0, sx], ['A', sx, -sy, -Math.PI / 2], ['L', w / 2, -sy, 0, 1, 2 * sy], ['A', sx, sy, 0],
                  ['L', sx, hh / 2, -1, 0, 2 * sx], ['A', -sx, sy, Math.PI / 2], ['L', -w / 2, sy, 0, -1, 2 * sy], ['A', -sx, -sy, Math.PI], ['L', -sx, -hh / 2, 1, 0, sx]];
    const lens = segs.map(s => s[0] === 'L' ? s[5] : q), total = lens.reduce((a, b) => a + b, 0), n = Math.max(4, Math.round(total / step));
    for(let i = 0; i < n; i++){
      let d = total * i / n, j = 0; while(j < segs.length - 1 && d > lens[j]){ d -= lens[j]; j++; }
      const s = segs[j];
      if(s[0] === 'L') fn(s[1] + s[3] * d, s[2] + s[4] * d, Math.atan2(s[4], s[3]), i, n);
      else { const a = s[3] + (r ? d / r : 0); fn(s[1] + r * Math.cos(a), s[2] + r * Math.sin(a), a + Math.PI / 2, i, n); }
    }
    return n;
  }

  // centre of a bw × bh box placed at `pos` inside the safe area, `pad` mm further in
  function placeBox(g, pos, bw, bh, pad){
    pad = pad || 0; pos = pos === 'arc-top' ? 'tc' : pos === 'arc-bottom' ? 'bc' : (pos || 'mc');
    const cx = pos[1] === 'l' ? -1 : pos[1] === 'r' ? 1 : 0, cy = pos[0] === 't' ? -1 : pos[0] === 'b' ? 1 : 0;
    if(!g.round) return { x: cx * Math.max(0, g.safeW / 2 - pad - bw / 2), y: cy * Math.max(0, g.safeH / 2 - pad - bh / 2) };
    const R = g.safeR - pad, n = Math.hypot(cx, cy); if(!n) return { x: 0, y: 0 };
    const dx = cx / n, dy = cy / n, fits = t => { const x = t * dx, y = t * dy;
      return Math.hypot(Math.abs(x) + bw / 2, Math.abs(y) + bh / 2) <= R; };
    let lo = 0, hi = R; if(!fits(0)) return { x: 0, y: 0 };
    for(let i = 0; i < 40; i++){ const m = (lo + hi) / 2; if(fits(m)) lo = m; else hi = m; }
    return { x: lo * dx, y: lo * dy };
  }

  // ---------- text ----------
  const font = (size, family, weight, style) => (style || 'normal') + ' ' + (weight || 400) + ' ' + Math.max(0.1, size).toFixed(2) + 'px "' + family + '", sans-serif';
  // largest size ≤ size (down to min) at which text fits maxW; sets ctx.font and returns the size
  function fit(ctx, text, maxW, size, family, weight, style, min, spacing){
    min = min || size * 0.35; let s = size;
    const width = z => { ctx.font = font(z, family, weight, style); return ctx.measureText(text).width + (spacing || 0) * z * Math.max(0, text.length - 1); };
    while(s > min && width(s) > maxW) s *= 0.95;
    ctx.font = font(s, family, weight, style); return s;
  }
  // text along a circle of radius R (the text's middle line), centred on angle `at` (radians, canvas angles:
  // -π/2 is the top, π/2 the bottom). Top text reads clockwise, bottom text reads left to right, both upright.
  function arcText(ctx, text, R, at, o){
    o = o || {}; const size = o.size || 3, sp = (o.spacing || 0) * size;
    ctx.save(); ctx.font = font(size, o.family || 'Montserrat', o.weight, o.style); ctx.fillStyle = o.color || '#000';
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    const chars = Array.from(text), ws = chars.map(c => ctx.measureText(c).width + sp), span = (ws.reduce((a, b) => a + b, 0) - sp) / R;
    const bottom = o.side ? o.side === 'bottom' : Math.sin(at) > 0.01;
    let a = bottom ? at + span / 2 : at - span / 2;
    chars.forEach((c, i) => { const da = (ws[i] - (i === chars.length - 1 ? sp : 0)) / R, m = bottom ? a - da / 2 : a + da / 2;
      ctx.save(); ctx.translate(R * Math.cos(m), R * Math.sin(m)); ctx.rotate(bottom ? m - Math.PI / 2 : m + Math.PI / 2);
      if(o.stroke){ ctx.lineWidth = o.stroke; ctx.strokeStyle = o.strokeColor || '#fff'; ctx.lineJoin = 'round'; ctx.strokeText(c, 0, 0); }
      ctx.fillText(c, 0, 0); ctx.restore(); a = bottom ? a - ws[i] / R : a + ws[i] / R; });
    ctx.restore(); return span;
  }

  // ---------- colour, random, shapes ----------
  const hex = c => { c = c.replace('#', ''); if(c.length === 3) c = c.split('').map(x => x + x).join(''); return [0, 2, 4].map(i => parseInt(c.substr(i, 2), 16)); };
  const rgba = (c, a) => { const [r, gg, b] = hex(c); return 'rgba(' + r + ',' + gg + ',' + b + ',' + a + ')'; };
  const mix = (c1, c2, t) => { const a = hex(c1), b = hex(c2); return '#' + a.map((v, i) => Math.round(v + (b[i] - v) * t).toString(16).padStart(2, '0')).join(''); };
  const lum = c => { const v = hex(c).map(x => { x /= 255; return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); }); return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]; };
  const contrast = c => lum(c) > 0.4 ? '#111111' : '#ffffff';
  function rng(seed){ let t = (seed >>> 0) || 1; return () => { t += 0x6D2B79F5; let r = Math.imul(t ^ t >>> 15, 1 | t); r ^= r + Math.imul(r ^ r >>> 7, 61 | r); return ((r ^ r >>> 14) >>> 0) / 4294967296; }; }
  function star(path, x, y, R, n, inner){ n = n || 5; inner = inner || 0.45; for(let i = 0; i < 2 * n; i++){ const a = -Math.PI / 2 + Math.PI * i / n, rr = i % 2 ? R * inner : R; i ? path.lineTo(x + rr * Math.cos(a), y + rr * Math.sin(a)) : path.moveTo(x + rr * Math.cos(a), y + rr * Math.sin(a)); } path.closePath(); return path; }
  // canvas shadows ignore the transform, so give them in mm: shadow(ctx, blur, colour, dx, dy); shadow(ctx) clears it
  function shadow(ctx, blur, color, dx, dy){ const m = ctx.getTransform(), k = Math.hypot(m.a, m.b);
    ctx.shadowColor = blur || dx || dy ? (color || 'rgba(0,0,0,.4)') : 'transparent'; ctx.shadowBlur = (blur || 0) * k; ctx.shadowOffsetX = (dx || 0) * k; ctx.shadowOffsetY = (dy || 0) * k; }
  function heart(path, x, y, s){ path.moveTo(x, y + 0.35 * s); path.bezierCurveTo(x - 0.6 * s, y - 0.05 * s, x - 0.35 * s, y - 0.55 * s, x, y - 0.22 * s);
    path.bezierCurveTo(x + 0.35 * s, y - 0.55 * s, x + 0.6 * s, y - 0.05 * s, x, y + 0.35 * s); path.closePath(); return path; }

  // ---------- fonts ----------
  const FONTS = ['Great Vibes', 'Dancing Script', 'Allura', 'Sacramento', 'Pacifico', 'Caveat', 'Satisfy', 'Parisienne',
    'Playfair Display', 'Cormorant Garamond', 'Cinzel', 'Montserrat', 'Bebas Neue', 'Fredoka', 'Quicksand',
    'Special Elite', 'Courier Prime', 'Share Tech Mono', 'Lobster', 'Abril Fatface'];
  const FONT_CSS = 'https://fonts.googleapis.com/css2?family=Great+Vibes&family=Dancing+Script:wght@400;700&family=Allura&family=Sacramento&family=Pacifico'
    + '&family=Caveat:wght@400;700&family=Satisfy&family=Parisienne&family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Cormorant+Garamond:ital,wght@0,500;0,700;1,500'
    + '&family=Cinzel:wght@400;700&family=Montserrat:wght@400;600;800&family=Bebas+Neue&family=Fredoka:wght@400;600&family=Quicksand:wght@500;700'
    + '&family=Special+Elite&family=Courier+Prime:wght@400;700&family=Share+Tech+Mono&family=Lobster&family=Abril+Fatface&display=swap';
  // adds the Google Fonts stylesheet (once), waits for it, then for every family; offline it falls back to system fonts
  function loadFonts(timeoutMs){
    let l = document.querySelector('link[data-ms-fonts]');
    if(!l){ l = document.createElement('link'); l.rel = 'stylesheet'; l.href = FONT_CSS; l.dataset.msFonts = '1';
      l._ready = new Promise(r => { l.onload = r; l.onerror = r; }); document.head.appendChild(l); }
    const sheet = l._ready || Promise.resolve();
    const all = sheet.then(() => Promise.all(FONTS.flatMap(f => ['400', '700'].map(w => document.fonts.load(w + ' 16px "' + f + '"').catch(() => null)))));
    return Promise.race([all, new Promise(r => setTimeout(r, timeoutMs || 8000))]);
  }

  // ---------- registry ----------
  const CATS = ['frame', 'pattern', 'signature', 'date', 'brand', 'caption', 'preset'];
  const styles = {}, errors = [];
  function register(def){
    if(!def || !def.id || !CATS.includes(def.cat)) throw new Error('bad style ' + (def && def.id));
    if(def.cat !== 'preset' && typeof def.draw !== 'function') throw new Error('style ' + def.id + ' has no draw()');
    styles[def.id] = def; return def;
  }
  const list = cat => Object.values(styles).filter(s => s.cat === cat);

  // a stand-in photo (sunset over the sea) for previews
  let SAMPLE = null;
  function samplePhoto(){
    if(SAMPLE) return SAMPLE;
    const c = document.createElement('canvas'); c.width = c.height = 600; const x = c.getContext('2d');
    const sky = x.createLinearGradient(0, 0, 0, 380); sky.addColorStop(0, '#2b2d6e'); sky.addColorStop(.45, '#c0466f'); sky.addColorStop(.8, '#f39a4c'); sky.addColorStop(1, '#ffd27a');
    x.fillStyle = sky; x.fillRect(0, 0, 600, 390); x.fillStyle = '#fff1c4'; x.beginPath(); x.arc(350, 300, 60, 0, 7); x.fill();
    x.fillStyle = '#5b2a52'; x.beginPath(); x.moveTo(0, 350); x.lineTo(110, 245); x.lineTo(200, 325); x.lineTo(290, 220); x.lineTo(420, 350); x.lineTo(500, 270); x.lineTo(600, 340); x.lineTo(600, 400); x.lineTo(0, 400); x.fill();
    const sea = x.createLinearGradient(0, 390, 0, 600); sea.addColorStop(0, '#e0794f'); sea.addColorStop(1, '#1d2a55'); x.fillStyle = sea; x.fillRect(0, 390, 600, 210);
    x.strokeStyle = 'rgba(255,230,170,.7)'; x.lineWidth = 3; for(let i = 0; i < 10; i++){ const y = 405 + i * 18; x.beginPath(); x.moveTo(280 + i * 5, y); x.lineTo(420 - i * 5, y); x.stroke(); }
    return (SAMPLE = c);
  }

  // ---------- one magnet ----------
  // s: { photo:{img, zoom, dx, dy, rot}|null, pattern, frame, marks:[{cat, style, text, date, pos, color, size}], colors:{ink, accent, paper}, seed, logo, guides, cutLine }
  function guarded(ctx, id, fn){ ctx.save(); try{ fn(); }catch(e){ errors.push(id + ': ' + e.message); } ctx.restore(); }
  function drawPhoto(ctx, g, ph){
    const img = ph.img, iw = img.naturalWidth || img.width, ih = img.naturalHeight || img.height, rot = ((ph.rot || 0) % 360 + 360) % 360, side = rot % 180 !== 0;
    const w = side ? ih : iw, hh = side ? iw : ih, k = Math.max(g.cutW / w, g.cutH / hh) * (ph.zoom || 1);
    ctx.translate(ph.dx || 0, ph.dy || 0); ctx.rotate(rot * Math.PI / 180); ctx.drawImage(img, -iw * k / 2, -ih * k / 2, iw * k, ih * k);
  }
  function renderCell(ctx, g, s){
    const c = Object.assign({ ink: '#1f1f1f', accent: '#c2410c', paper: '#ffffff' }, s.colors || {});
    const p = { ink: c.ink, accent: c.accent, paper: c.paper, seed: s.seed || 7, logo: s.logo || null };
    const H = MS.h, CUT = cut(g);
    ctx.save(); ctx.clip(CUT); ctx.fillStyle = p.paper; ctx.fill(CUT);
    if(s.pattern && styles[s.pattern]) guarded(ctx, s.pattern, () => styles[s.pattern].draw(ctx, g, p, H));
    if(s.photo && s.photo.img) guarded(ctx, 'photo', () => drawPhoto(ctx, g, s.photo));
    if(s.frame && styles[s.frame]) guarded(ctx, s.frame, () => styles[s.frame].draw(ctx, g, p, H));
    (s.marks || []).forEach(m => { const st = styles[m.style]; if(!st || !(m.text || m.cat === 'brand' && p.logo || m.cat === 'date')) return;
      guarded(ctx, m.style, () => st.draw(ctx, g, p, H, { text: m.text || '', date: m.date || new Date(), pos: m.pos || st.pos || 'bc', color: m.color || p.ink, size: m.size || 1 })); });
    ctx.restore();
    if(s.guides){ ctx.save(); ctx.lineWidth = 0.25; ctx.strokeStyle = 'rgba(30,110,220,.9)'; ctx.setLineDash([1.2, 0.8]); ctx.stroke(face(g));
      ctx.strokeStyle = 'rgba(220,40,120,.85)'; ctx.setLineDash([0.4, 0.6]); ctx.stroke(safe(g)); ctx.restore(); }
    if(s.cutLine){ ctx.save(); ctx.lineWidth = 0.2; ctx.strokeStyle = '#555'; ctx.stroke(CUT); ctx.restore(); }
  }

  window.MS = { SIZES, POS, BLEED, SAFE_IN, geom, register, list, styles, errors, renderCell, samplePhoto, loadFonts, FONTS, FONT_CSS,
    h: { face, safe, cut, shapePath, alongEdge, placeBox, font, fit, arcText, rgba, mix, lum, contrast, rng, star, heart, shadow, FONTS } };
})();
