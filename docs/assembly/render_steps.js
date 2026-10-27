// Renders the assembly-manual step images from the assembly GLB.
// node docs/assembly/render_steps.js <assembly.glb> <steps.json> <outdir>
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const [glb, spec, out] = process.argv.slice(2);
const page_html = fs.readFileSync(path.join(__dirname, 'viewer.html'));

(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });
  page.on('pageerror', e => console.log('page error:', e.message));
  await page.route('http://manual.local/**', r => {
    const u = r.request().url();
    if (u.endsWith('.glb')) r.fulfill({ body: fs.readFileSync(glb), contentType: 'model/gltf-binary' });
    else r.fulfill({ body: page_html, contentType: 'text/html' });
  });
  await page.goto('http://manual.local/index.html');
  await page.waitForFunction(() => window.ready === true, null, { timeout: 180000 });
  for (const s of JSON.parse(fs.readFileSync(spec))) {
    await page.evaluate(st => window.renderStep(st), s);
    await page.locator('#stage').screenshot({ path: path.join(out, s.img) });
    console.log('rendered', s.img);
  }
  await browser.close();
})();
