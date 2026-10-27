// Saves the forming-section stages and the finished-magnet views of the build-pack page as PNGs.
// node web/tools/forming_stills.js web/magpress-m4.html docs/forming
const { chromium } = require('playwright');
const path = require('path');
let p;
(async () => {
  const [page, out] = process.argv.slice(2);
  const shot = async (sel, file) => { await p.evaluate(sel => document.querySelector(sel).scrollIntoView({ block: 'center' }), sel); await p.waitForTimeout(300); const bb = await p.locator(sel).boundingBox(); await p.screenshot({ path: path.join(out, file), clip: bb, timeout: 120000 }); };
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader'] });
  p = await b.newPage({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 2, colorScheme: 'light' });
  await p.goto('file://' + path.resolve(page)); await p.waitForTimeout(6000);
  await p.locator('#mgStage').scrollIntoViewIfNeeded(); await p.waitForTimeout(1500);
  for (const v of ['face', 'back', 'edge']) {
    await p.evaluate(v => window.MPmag.view(v), v); await p.waitForTimeout(1500);
    await shot('#mgStage', 'magnet_' + v + '.png');
  }
  const n = await p.evaluate(() => window.MPfold.stages);
  for (let i = 0; i < n; i++) {
    await p.evaluate(i => window.MPfold.at(i), i); await p.waitForTimeout(120);
    await shot('#foldSvg', 'stage' + String(i + 1).padStart(2, '0') + '.png');
  }
  const info = await p.evaluate(() => ({ list: window.MPfold.list, thick: window.MPfold.thick }));
  const md = ['# How the MagPress M4 forms a magnet', '',
    'Stills from section 02 of the build pack (`web/magpress-m4.html`), where they are animated. The section runs through one edge of the dies at true size, about 25 times enlarged.',
    'The dimensions come from the die drawings MP-203 to MP-209. Remake these images with `node web/tools/forming_stills.js web/magpress-m4.html docs/forming`.', '',
    '## The finished magnet', '',
    'Photo and film wrapped round the R1 edge, the tinplate skirt rolled under the back plate, ' + info.thick.toFixed(1) + ' mm thick (size 63.5 × 63.5 shown).', '',
    '| Front | Back | Edge, cut open |', '|---|---|---|', '| ![Front](magnet_face.png) | ![Back](magnet_back.png) | ![Edge, cut open](magnet_edge.png) |', '',
    '## Stroke by stroke', ''];
  info.list.forEach((g, i) => { const f = 'stage' + String(i + 1).padStart(2, '0') + '.png'; md.push('### ' + (i + 1) + '. ' + g.t, '', '![' + g.t + '](' + f + ')', '', g.x, ''); });
  md.push('## At the corners', '', 'At a corner the photo and film shrink from an arc at 10 mm radius (6 mm out from the R4 face corner) to the 4 mm arc of the skirt. The excess, about 60%, gathers into fine pleats on the skirt and inside the rolled edge. If the corners wrinkle onto the face, the paper is too thick: use 90–120 g/m² paper.', '');
  require('fs').writeFileSync(path.join(out, 'README.md'), md.join('\n'));
  await b.close();
})();
