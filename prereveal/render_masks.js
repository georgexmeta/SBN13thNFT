const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => { const dir = process.argv[2]; const b = await chromium.launch();
 const p = await b.newPage({ viewport: { width: 1080, height: 1080 } });
 for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.svg'))) {
  await p.setContent(`<html><body style="margin:0;background:transparent">${fs.readFileSync(path.join(dir,f),'utf8')}</body></html>`);
  await p.screenshot({ path: path.join(dir, f.replace('.svg','.png')), omitBackground: true, clip:{x:0,y:0,width:1080,height:1080} }); }
 await b.close(); })();
