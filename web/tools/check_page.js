// Smoke test for the build-pack page: loads it in Chromium (Playwright), runs the press cycle,
// and checks for console errors and horizontal overflow at phone width.
// Usage: node web/tools/check_page.js web/magpress-m4.html
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
(async () => {
  const page_ = path.resolve(process.argv[2] || 'web/magpress-m4.html');
  const tmp = path.join(__dirname, '_page.html');
  fs.writeFileSync(tmp, '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>' + fs.readFileSync(page_, 'utf8') + '</body></html>');
  const browser = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
  const errs = [];
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
  page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  page.on('pageerror', e => errs.push('pageerror: ' + e.message));
  await page.goto('file://' + tmp); await page.waitForTimeout(6000);
  const canvas = await page.$('#stage canvas') !== null;
  await page.click('#playCycle'); await page.waitForTimeout(18000);
  const cycleDone = !(await page.$eval('#playCycle', b => b.disabled));
  await page.$eval('#handle', e => { e.value = 3; e.dispatchEvent(new Event('input')); });
  const readout = await page.$eval('#poseRead', e => e.textContent);
  const phone = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await phone.goto('file://' + tmp); await phone.waitForTimeout(3000);
  const sw = await phone.evaluate(() => document.documentElement.scrollWidth);
  console.log(JSON.stringify({ canvas, cycleDone, readoutClosed: readout, phoneScrollWidth: sw, errors: errs }, null, 1));
  await browser.close(); fs.unlinkSync(tmp);
  process.exit(canvas && cycleDone && sw <= 390 && !errs.length ? 0 : 1);
})();
