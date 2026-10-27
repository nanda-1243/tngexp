// Contact sheets of magnet-studio styles, plus an error check of every style at every size.
// node web/tools/studio_gallery.js --cat frame --out /tmp/frames [--nophoto] [--per 6] web/studio/frames.js [more style files]
// Writes <out>_01.png, <out>_02.png … (each style on 63.5 × 63.5, 53 × 80 and Ø58, cut line and face/safe guides shown)
// and prints a JSON report: styles drawn, errors (style: message) from all 8 sizes, portrait and landscape.
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
(async () => {
  const a = process.argv.slice(2), opt = { cat: null, out: 'gallery', per: 6, photo: true, files: [] };
  for (let i = 0; i < a.length; i++) {
    if (a[i] === '--cat') opt.cat = a[++i]; else if (a[i] === '--out') opt.out = a[++i];
    else if (a[i] === '--per') opt.per = +a[++i]; else if (a[i] === '--nophoto') opt.photo = false; else opt.files.push(path.resolve(a[i]));
  }
  const core = path.resolve(__dirname, '..', 'studio', 'core.js');
  const scripts = [core, ...opt.files].map(f => '<script src="file://' + f + '"></script>').join('');
  const tmp = path.join(require('os').tmpdir(), 'ms_gallery_' + process.pid + '.html');
  fs.writeFileSync(tmp, '<!doctype html><html><head><meta charset="utf-8"></head><body style="margin:0;background:#fff">' + scripts + '</body></html>');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1600, height: 1000 } });
  const pageErr = []; p.on('pageerror', e => pageErr.push(e.message)); p.on('console', m => { if (m.type() === 'error') pageErr.push(m.text()); });
  await p.goto('file://' + tmp); await p.evaluate(() => MS.loadFonts(8000));
  const res = await p.evaluate(({ cat, per, photo }) => {
    const ids = Object.values(MS.styles).filter(s => !cat || s.cat === cat).map(s => s.id);
    const sample = { signature: 'Anu & Ravi', date: '27 Oct 2026', brand: 'MagPress', caption: 'Summer 2026' };
    const stateFor = (st) => {
      const s = { photo: photo ? { img: MS.samplePhoto(), zoom: 1 } : null, colors: { ink: '#1f1f1f', accent: '#c2410c', paper: '#ffffff' }, marks: [], seed: 7, guides: true, cutLine: true };
      if (st.cat === 'frame') s.frame = st.id; else if (st.cat === 'pattern') { s.pattern = st.id; s.photo = null; }
      else if (st.cat === 'preset') { const t = st.set || {}; s.frame = t.frame; s.pattern = t.pattern; if (t.photo === false) s.photo = null; if (t.colors) s.colors = Object.assign(s.colors, t.colors);
        ['signature', 'date', 'brand', 'caption'].forEach(k => { if (t[k]) s.marks.push({ cat: k, style: t[k].style, pos: t[k].pos, color: t[k].color, size: t[k].size, text: t[k].text || sample[k] }); }); }
      else s.marks.push({ cat: st.cat, style: st.id, pos: st.pos, text: sample[st.cat], color: st.cat === 'date' ? null : '#ffffff' });
      return s;
    };
    // error check: every style at every size and orientation
    MS.errors.length = 0;
    const scratch = document.createElement('canvas'); scratch.width = scratch.height = 300; const sc = scratch.getContext('2d');
    for (const id of ids) for (const z of MS.SIZES) for (const land of [false, true]) {
      const g = MS.geom(z, land), st = MS.styles[id], s = stateFor(st);
      for (const pos of (st.cat === 'frame' || st.cat === 'pattern' || st.cat === 'preset') ? [null] : MS.POS) {
        if (pos) s.marks[0].pos = pos;
        sc.setTransform(2, 0, 0, 2, 150, 150); try { MS.renderCell(sc, g, s); } catch (e) { MS.errors.push(id + ' (' + z.id + '): ' + e.message); }
      }
    }
    // contact sheets
    const K = 4, cols = [MS.geom(MS.SIZES[1]), MS.geom(MS.SIZES[2]), MS.geom(MS.SIZES[7])], cellW = 110 * K, rowH = 118 * K, labelH = 26;
    const pages = [];
    for (let s0 = 0; s0 < ids.length; s0 += per) {
      const chunk = ids.slice(s0, s0 + per), cv = document.createElement('canvas'), perRow = 2;
      cv.width = perRow * cols.length * cellW; cv.height = Math.ceil(chunk.length / perRow) * (rowH + labelH);
      const c = cv.getContext('2d'); c.fillStyle = '#eef0f2'; c.fillRect(0, 0, cv.width, cv.height);
      chunk.forEach((id, n) => {
        const ox = (n % perRow) * cols.length * cellW, oy = Math.floor(n / perRow) * (rowH + labelH), st = MS.styles[id];
        c.fillStyle = '#222'; c.font = '600 18px sans-serif'; c.fillText(id + '  ·  ' + (st.name || ''), ox + 10, oy + 19);
        cols.forEach((g, j) => { c.setTransform(K, 0, 0, K, ox + j * cellW + cellW / 2, oy + labelH + rowH / 2); MS.renderCell(c, g, stateFor(st)); c.setTransform(1, 0, 0, 1, 0, 0); });
      });
      pages.push(cv.toDataURL('image/png'));
    }
    return { ids, errors: MS.errors.slice(0, 80), nErrors: MS.errors.length, pages };
  }, { cat: opt.cat, per: opt.per, photo: opt.photo });
  res.pages.forEach((d, i) => fs.writeFileSync(opt.out + '_' + String(i + 1).padStart(2, '0') + '.png', Buffer.from(d.split(',')[1], 'base64')));
  console.log(JSON.stringify({ styles: res.ids.length, ids: res.ids, pages: res.pages.length, nErrors: res.nErrors, errors: res.errors, pageErrors: pageErr }, null, 1));
  await b.close(); fs.unlinkSync(tmp);
  process.exit(res.nErrors || pageErr.length ? 1 : 0);
})();
