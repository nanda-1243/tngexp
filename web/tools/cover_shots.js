// Renders the two reference images used on drawing MP-000 from the 3D model.
// Usage: node web/tools/cover_shots.js web/magpress-m4.html <outdir>   then: python3 web/tools/crop_covers.py <outdir> cad
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
(async () => {
  const page_ = path.resolve(process.argv[2] || 'web/magpress-m4.html');
  const out = path.resolve(process.argv[3] || 'out');
  fs.mkdirSync(out, { recursive: true });
  const tmp = path.join(__dirname, '_page.html');
  fs.writeFileSync(tmp, '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>' + fs.readFileSync(page_, 'utf8') + '</body></html>');
  const browser = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1500, height: 1400 }, deviceScaleFactor: 2 });
  await page.goto('file://' + tmp); await page.waitForTimeout(5000);
  await page.click('#resetCycle');
  await page.addStyleTag({ content: '.views,#caption,#tip{display:none!important} .bench{grid-template-columns:1fr!important} .rail{display:none!important} #stage{height:1150px!important;width:620px!important}' });
  await page.waitForTimeout(800);
  const stage = await page.$('#stage');
  await page.mouse.move(1450, 5);
  await page.evaluate(() => window.MP.camTo([1408, 1050, 1684], [0, 220, 60])); await page.waitForTimeout(1200);
  await stage.screenshot({ path: path.join(out, 'cover_assembled.png') });
  await page.$eval('#explode', e => { e.value = 70; e.dispatchEvent(new Event('input')); });
  await page.evaluate(() => window.MP.camTo([1650, 1420, 1960], [0, 400, 60])); await page.mouse.move(1450, 5); await page.waitForTimeout(1200);
  await stage.screenshot({ path: path.join(out, 'cover_exploded.png') });
  await browser.close(); fs.unlinkSync(tmp);
})();
