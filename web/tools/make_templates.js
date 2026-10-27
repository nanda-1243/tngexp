// Blank print templates (PDF, A4 and Letter) and one-magnet design guides (SVG) for every size, from the magnet studio.
// node web/tools/make_templates.js print-templates
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
(async () => {
  const out = path.resolve(process.argv[2] || 'print-templates');
  const src = path.resolve(__dirname, '..', 'magnet-studio.html'), tmp = path.resolve(__dirname, '..', '_templates.html');
  fs.writeFileSync(tmp, '<!doctype html><html><head><meta charset="utf-8"></head><body>' + fs.readFileSync(src, 'utf8') + '</body></html>');
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + tmp); await p.waitForFunction(() => window.MSApp && window.jspdf);
  const jobs = await p.evaluate(() => MS.SIZES.flatMap(z => (z.shape === 'rect' && z.W !== z.H ? [false, true] : [false]).map(land => ({ id: z.id, land }))));
  const rows = [];
  for (const dir of ['A4', 'Letter', 'svg']) fs.mkdirSync(path.join(out, dir), { recursive: true });
  for (const j of jobs) {
    const r = await p.evaluate(async ({ id, land }) => {
      const res = { files: {} };
      for (const paper of ['A4', 'Letter']) {
        MSApp.setSize(id, land, paper); const L = MSApp.layout(), d = await MSApp.buildPDF(true);
        const bytes = new Uint8Array(d.output('arraybuffer')); let s = ''; for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
        res.files[paper] = btoa(s); res[paper] = L.n; res.g = L.g;
      }
      res.svg = MSApp.guideSVG(); return res;
    }, j);
    const g = r.g, base = (g.round ? 'D' + g.W : Math.min(g.W, g.H) + 'x' + Math.max(g.W, g.H)).replace(/\./g, '_') + (j.land ? '_landscape' : g.W !== g.H && !g.round ? '_portrait' : '');
    for (const paper of ['A4', 'Letter']) fs.writeFileSync(path.join(out, paper, 'template_' + base + '_' + paper + '.pdf'), Buffer.from(r.files[paper], 'base64'));
    fs.writeFileSync(path.join(out, 'svg', 'guide_' + base + '.svg'), r.svg);
    rows.push({ base, g, A4: r.A4, Letter: r.Letter, land: j.land });
  }
  const pair = (g, w, h) => g.round ? 'Ø' + w : w + ' × ' + h;
  const md = ['# Print templates for the MagPress M4', '',
    'Blank sheets and design guides for every magnet size, made by the Magnet Studio ([`web/magnet-studio.html`](../web/magnet-studio.html)).',
    'The studio itself lays your photos out on these sheets for you; use these files when you design in another app (Canva, Inkscape, Photoshop, Word).', '',
    '- **Grey line:** cut line (the paper size). Let the photo fill the whole cut area: the outer 6 mm folds over the rim.',
    '- **Blue dashed line:** the edge of the magnet face.',
    '- **Pink dotted line:** keep faces and text inside it (3 mm in from the face edge).',
    '- **Print at 100 % ("Actual size"), never "Fit to page".** The bar at the foot of each sheet must measure 50 mm.',
    '- Paper: 90–120 g/m² matte inkjet paper. Cut round sizes with a circle punch; the others with a trimmer and a 6 mm corner rounder.', '',
    '| Size | Face (mm) | Paper cut (mm) | Keep text inside (mm) | Per A4 | Per Letter | Files |', '|---|---|---|---|---|---|---|'];
  for (const r of rows) {
    const g = r.g, name = (g.round ? g.label : g.label + (g.W !== g.H ? (r.land ? ' landscape' : ' portrait') : ''));
    md.push('| ' + name + ' | ' + pair(g, g.W, g.H) + ' | ' + pair(g, g.cutW, g.cutH) + (g.round ? '' : ', R6 corners') + ' | ' + pair(g, g.safeW, g.safeH) + ' | ' + r.A4 + ' | ' + r.Letter
      + ' | [A4](A4/template_' + r.base + '_A4.pdf) · [Letter](Letter/template_' + r.base + '_Letter.pdf) · [SVG](svg/guide_' + r.base + '.svg) |');
  }
  md.push('', 'Remake these files with `node web/tools/make_templates.js print-templates`.', '');
  fs.writeFileSync(path.join(out, 'README.md'), md.join('\n'));
  console.log(JSON.stringify(rows.map(r => [r.base, r.A4, r.Letter])));
  await b.close(); fs.unlinkSync(tmp);
})();
