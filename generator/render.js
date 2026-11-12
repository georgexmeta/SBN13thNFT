// Render every SVG in a folder to a 1000x1000 PNG next to it, plus a contact sheet.
// Usage: node generator/render.js output/samples
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const dir = process.argv[2];
  const files = fs.readdirSync(dir).filter(f => f.endsWith('.svg'))
    .sort((a, b) => parseInt(a) - parseInt(b));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1000, height: 1000 } });
  for (const f of files) {
    const svg = fs.readFileSync(path.join(dir, f), 'utf8');
    await page.setContent(`<html><body style="margin:0">${svg}</body></html>`);
    await page.screenshot({ path: path.join(dir, f.replace('.svg', '.png')), clip: { x: 0, y: 0, width: 1000, height: 1000 } });
  }
  // contact sheet: 3 per row at 500px
  const cols = 3, size = 500, rows = Math.ceil(files.length / cols);
  await page.setViewportSize({ width: cols * size, height: rows * size });
  const imgs = files.map(f => {
    const b64 = fs.readFileSync(path.join(dir, f.replace('.svg', '.png'))).toString('base64');
    return `<img src="data:image/png;base64,${b64}" width="${size}" height="${size}" style="display:block;float:left">`;
  }).join('');
  await page.setContent(`<html><body style="margin:0;width:${cols * size}px">${imgs}</body></html>`);
  await page.screenshot({ path: path.join(dir, 'contact-sheet.png'), fullPage: true });
  await browser.close();
  console.log(`rendered ${files.length} files in ${dir}`);
})();
