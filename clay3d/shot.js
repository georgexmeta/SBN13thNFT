const { chromium } = require('playwright');
(async () => {
  const [q, out] = [process.argv[2] || '', process.argv[3] || 'bust.png'];
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1000, height: 1000 } });
  p.on('console', m => console.log('console:', m.text())); p.on('pageerror', e => console.log('err:', e.message));
  await p.goto('http://localhost:8765/bust.html' + q);
  await p.waitForFunction('window.done === true', null, { timeout: 120000 });
  await p.screenshot({ path: out }); await b.close();
})();
