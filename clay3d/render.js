// Render clay PFPs with headless Chromium.
// Usage: node clay3d/render.js <outDir> <ids e.g. 1-1300 or 1,5,9> [--jobs 3] [--port 8766]
// Needs the repo root served over http (the script starts its own server).
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const [outDir, spec = '1-13'] = process.argv.slice(2);
const opt = k => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : null; };
const JOBS = +(opt('--jobs') || 3), PORT = +(opt('--port') || 8766), EXTRA = opt('--query') || '';
const ids = spec.split(',').flatMap(p => { const [a, b] = p.split('-').map(Number); return b ? Array.from({ length: b - a + 1 }, (_, i) => a + i) : [a]; });
const types = { '.js': 'text/javascript', '.json': 'application/json', '.html': 'text/html' };
const server = http.createServer((req, res) => {
  const f = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!f.startsWith(ROOT) || !fs.existsSync(f)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(res);
}).listen(PORT);
(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const queue = ids.filter(id => !fs.existsSync(path.join(outDir, `${id}.png`))); let done = 0; const t0 = Date.now();
  async function worker() {
    const page = await browser.newPage({ viewport: { width: 1000, height: 1000 } });
    page.on('console', m => { if (m.text().startsWith('err')) console.log(m.text()); });
    while (queue.length) {
      const id = queue.shift();
      try {
        await page.goto(`http://localhost:${PORT}/clay3d/index.html?id=${id}${EXTRA}`);
        await page.waitForFunction('window.done === true || window.failed', null, { timeout: 180000 });
        const failed = await page.evaluate('window.failed'); if (failed) throw new Error(failed);
        await page.screenshot({ path: path.join(outDir, `${id}.png`) });
        done++; if (done % 10 === 0 || queue.length === 0) console.log(`${done} rendered, ${((Date.now() - t0) / done / 1000).toFixed(1)}s each`);
      } catch (e) { console.log(`#${id} failed: ${e.message}`); }
    }
    await page.close();
  }
  await Promise.all(Array.from({ length: JOBS }, worker));
  await browser.close(); server.close();
})();
