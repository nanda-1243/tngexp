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
  await p.click('#sizeSeg button[data-size="c58"]'); await p.waitForTimeout(800);   // Rev D round kit
  for (const v of ['face', 'back', 'edge']) {
    await p.evaluate(v => window.MPmag.view(v), v); await p.waitForTimeout(1500);
    await shot('#mgStage', 'round_' + v + '.png');
  }
  await p.click('#sizeSeg button[data-size="s63"]'); await p.waitForTimeout(800);
  const n = await p.evaluate(() => window.MPfold.stages);
  for (let i = 0; i < n; i++) {
    await p.evaluate(i => window.MPfold.at(i), i); await p.waitForTimeout(120);
    await shot('#foldSvg', 'stage' + String(i + 1).padStart(2, '0') + '.png');
  }
  const info = await p.evaluate(() => ({ list: window.MPfold.list, thick: window.MPfold.thick, border: window.MPfold.border }));
  const md = ['# How the MagPress M4 forms a magnet', '',
    'Stills from section 02 of the build pack (`web/magpress-m4.html`), where they are animated. The section runs through one edge of the dies at true size, about 25 times enlarged.',
    'The dimensions come from the die drawings MP-203 to MP-209 (square and rectangular kits); the round kits (MP-223 to MP-229) roll the edge instead, see the end. Remake these images with `node web/tools/forming_stills.js web/magpress-m4.html docs/forming`.', '',
    '## The finished magnet', '',
    'Rev E: sharp corners, photo and film wrapped round the edge, the edge folded twice, flat, under the back plate (a flattened version of the Rev D rolled edge, with the cut edge of the tin hidden inside), ' + info.thick.toFixed(1) + ' mm thick, with a ' + (info.border - 0.7).toFixed(1) + ' mm flat border of the photo on the back, mitred at the corners (size 63.5 × 63.5 shown). Print a date, a name or a brand on that border with the Magnet Studio (`web/magnet-studio.html`).', '',
    '| Front | Back | Edge, cut open |', '|---|---|---|', '| ![Front](magnet_face.png) | ![Back](magnet_back.png) | ![Edge, cut open](magnet_edge.png) |', '',
    '## Stroke by stroke', ''];
  info.list.forEach((g, i) => { const f = 'stage' + String(i + 1).padStart(2, '0') + '.png'; md.push('### ' + (i + 1) + '. ' + g.t, '', '![' + g.t + '](' + f + ')', '', g.x, ''); });
  md.push('## At the corners', '', 'The tin blank, the photo and the film are all cut 6 mm over the face, with their corners clipped at 45° on the line |x| + |y| = W/2 + H/2 + 1.7. Folded down the side, along the back and back on themselves, the edges at a corner meet in a diagonal mitre on the back. Where the side walls meet, about two layers overlap in a small gusset; the upper ring and ring B have a Ø1.2 relief in each corner to make room for it. If the corners tear or wrinkle onto the face, the paper is too thick: use 90–120 g/m² paper.', '');
  md.push('## Round magnets (Rev D rolled edge)', '', 'Round kits keep the Rev D design: a drawn round cup, and a roll channel in the anvil that rolls the edge under the back plate with the photo and film inside the roll. A round edge cannot be folded flat without wrinkling, so nothing of the print shows on the back. Size Ø58 shown: photo cut Ø70.', '',
    '| Front | Back | Edge, cut open |', '|---|---|---|', '| ![Round magnet, front](round_face.png) | ![Round magnet, back](round_back.png) | ![Round magnet, edge cut open](round_edge.png) |', '');
  require('fs').writeFileSync(path.join(out, 'README.md'), md.join('\n'));
  await b.close();
})();
