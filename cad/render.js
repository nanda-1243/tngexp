const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
(async () => {
  const [,, outDir, pdfName, pngList] = process.argv;
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.join(outDir, 'set.html'));
  await page.pdf({ path: path.join(outDir, pdfName), width: '420mm', height: '297mm', printBackground: true });
  if (pngList) {
    const svgs = fs.readdirSync(path.join(outDir, 'svg')).sort();
    for (const n of pngList.split(',')) {
      const f = svgs[parseInt(n, 10) - 1]; if (!f) continue;
      const p2 = await browser.newPage({ viewport: { width: 1680, height: 1188 } });
      await p2.setContent('<html><body style="margin:0">' + fs.readFileSync(path.join(outDir, 'svg', f), 'utf8').replace('width="420mm" height="297mm"', 'width="1680" height="1188"') + '</body></html>');
      await p2.screenshot({ path: path.join(outDir, 'prev_' + n + '.png') });
      await p2.close();
    }
  }
  await browser.close();
})();
