// SBN13th claymation PFP renderer.
// Builds one sculpted plasticine bust from a token's traits (window.PFP = {attrs, seed})
// and renders it. Every trait from generator/generate.py has a clay version here.
import * as THREE from './node_modules/three/build/three.module.js';

const PAL = await (await fetch('./palette.json')).json();
const TOKEN = window.PFP || { attrs: {}, seed: 7 };
const A = Object.assign({
  'Background': 'Rust', 'Skin Tone': 'Pink Flesh', 'Head Shape': 'Swollen Dome', 'Swelling': 'Lumpy', 'Ear': 'Normal',
  'Eyes': 'Droopy Mismatch', 'Brows': 'Bushy', 'Nose': 'Bulbous', 'Mouth': 'Crooked Grin', 'Hair': 'Bald',
  'Hair Color': 'Ginger', 'Clothing': 'Red Flannel', 'Skin Detail': 'None', 'Weapon': 'Machete', 'Bandana': 'None', 'Mask': 'None',
}, TOKEN.attrs);
let s = (TOKEN.seed % 2147483646) + 1;
const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
const pick = arr => arr[Math.floor(rnd() * arr.length)];
const shade = (hex, k) => '#' + new THREE.Color(hex).multiplyScalar(k).getHexString();

const SKIN = PAL.skins[A['Skin Tone']] || '#e9b49a';
const HAIR = PAL.hair[A['Hair Color']] || '#c8622c';
const BG = PAL.backgrounds[A['Background']] || '#c96b3c';
const MASKED = A['Mask'] && A['Mask'] !== 'None';
const MSTYLE = { 'Zipper Leather Mask': 'zip', 'Clown Mask': 'clown', 'Iron Plate Mask': 'iron', 'Gas Mask': 'gas', 'Sack Hood': 'sack', 'Long Nose Mask': 'nose', 'Killer Clown Mask': 'clown', 'Burlap Pig Mask': 'pig', 'Patchwork Mask': 'patch' }[A['Mask']];
const FULLFACE = ['zip', 'clown', 'sack', 'nose', 'pig', 'patch'].includes(MSTYLE);
const BANDANA = !MASKED && A['Bandana'] && A['Bandana'] !== 'None';
const GLOW = { 'Glowing Red': '#ff3a1a', 'Glowing Green': '#7dff3a' }[A['Eyes']];

// ------------------------------------------------------------------ textures
function canvas(S) { const c = document.createElement('canvas'); c.width = c.height = S; return [c, c.getContext('2d')]; }
function tex(c, rep = 1, srgb = true) {
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rep, rep);
  if (srgb) t.colorSpace = THREE.SRGBColorSpace; return t;
}
const BUMP = (() => {             // hand-worked plasticine: thumb dents, tool smears, fingerprints, pitting
  const S = 1024, [c, g] = canvas(S); g.fillStyle = '#808080'; g.fillRect(0, 0, S, S);
  for (let i = 0; i < 70; i++) {   // shallow thumb dents
    const x = rnd() * S, y = rnd() * S, r = 25 + rnd() * 45, gr = g.createRadialGradient(x, y, 0, x, y, r);
    gr.addColorStop(0, 'rgba(60,60,60,.5)'); gr.addColorStop(.75, 'rgba(110,110,110,.1)'); gr.addColorStop(.9, 'rgba(170,170,170,.25)'); gr.addColorStop(1, 'rgba(128,128,128,0)');
    g.fillStyle = gr; g.beginPath(); g.ellipse(x, y, r, r * .8, rnd() * 3, 0, 7); g.fill();
  }
  for (let i = 0; i < 160; i++) {  // modelling-tool smears: short bundles of parallel strokes
    const x = rnd() * S, y = rnd() * S, a = rnd() * 6.28, L = 20 + rnd() * 50;
    for (let k = 0; k < 4; k++) { const o = (k - 1.5) * 3, v = k % 2 ? 95 : 165;
      g.strokeStyle = `rgba(${v},${v},${v},.22)`; g.lineWidth = 1.5 + rnd() * 1.5; g.beginPath();
      g.moveTo(x - Math.sin(a) * o, y + Math.cos(a) * o); g.quadraticCurveTo(x + Math.cos(a) * L * .5 - Math.sin(a) * (o + 4), y + Math.sin(a) * L * .5 + Math.cos(a) * (o + 4), x + Math.cos(a) * L - Math.sin(a) * o, y + Math.sin(a) * L + Math.cos(a) * o); g.stroke(); }
  }
  g.lineWidth = 1.1;
  for (let i = 0; i < 40; i++) {   // fingerprints
    const x = rnd() * S, y = rnd() * S, a = rnd() * 6;
    for (let k = 0; k < 10; k++) { g.strokeStyle = `rgba(${k % 2 ? 90 : 160},${k % 2 ? 90 : 160},${k % 2 ? 90 : 160},.18)`; g.beginPath(); g.ellipse(x, y, 4 + k * 2.6, 3 + k * 1.9, a, 0, 6.3); g.stroke(); }
  }
  // the "peak clay" look: dense fingerprint whorls and wavy smoothing ridges pressed into every surface
  for (let i = 0; i < 260; i++) {
    const x = rnd() * S, y = rnd() * S, a = rnd() * 6, n = 6 + rnd() * 10 | 0, sx = 3 + rnd() * 1.5, sy = sx * (.6 + rnd() * .3);
    g.lineWidth = 1.5;
    for (let k = 1; k <= n; k++) { const v = k % 2 ? 92 : 168; g.strokeStyle = `rgba(${v},${v},${v},.28)`; g.beginPath(); g.ellipse(x, y, k * sx, k * sy, a, rnd() * .6, 5.4 + rnd() * .8); g.stroke(); }
  }
  for (let i = 0; i < 140; i++) {
    let x = rnd() * S, y = rnd() * S; const a = rnd() * 6.28, L = 60 + rnd() * 120, w = 3 + rnd() * 2;
    for (let k = 0; k < 6; k++) { const v = k % 2 ? 100 : 160; g.strokeStyle = `rgba(${v},${v},${v},.2)`; g.lineWidth = 1.3; g.beginPath();
      for (let t = 0; t <= 1.001; t += .1) { const px = x + Math.cos(a) * L * t - Math.sin(a) * (k * w + Math.sin(t * 6 + i) * 4), py = y + Math.sin(a) * L * t + Math.cos(a) * (k * w + Math.sin(t * 6 + i) * 4); t ? g.lineTo(px, py) : g.moveTo(px, py); }
      g.stroke(); }
  }
  for (let i = 0; i < 6000; i++) { const v = rnd() < .5 ? 60 : 200; g.fillStyle = `rgba(${v},${v},${v},.18)`; g.fillRect(rnd() * S, rnd() * S, 1.5, 1.5); }
  return tex(c, 1.8, false);
})();
function pressedClay() {
  const [c, g] = canvas(1024); g.fillStyle = '#808080'; g.fillRect(0, 0, 1024, 1024);
  for (let i = 0; i < 45; i++) {
    const x = rnd() * 1024, y = rnd() * 1024, r = 30 + rnd() * 70;
    const gr = g.createRadialGradient(x, y, 0, x, y, r); gr.addColorStop(0, 'rgba(50,50,50,.28)'); gr.addColorStop(1, 'rgba(50,50,50,0)');
    g.fillStyle = gr; g.beginPath(); g.ellipse(x, y, r, r * .75, rnd() * 3, 0, 7); g.fill();
    g.strokeStyle = 'rgba(40,40,40,.07)'; g.lineWidth = 1.4;
    for (let k = 2; k < 10; k++) { g.beginPath(); g.ellipse(x, y, k * r / 11, k * r / 15, .4, 0, 7); g.stroke(); }
  }
  g.strokeStyle = 'rgba(30,30,30,.35)'; g.lineWidth = 1.2;
  for (let i = 0; i < 22; i++) { let x = rnd() * 1024, y = rnd() * 1024; g.beginPath(); g.moveTo(x, y);
    for (let k = 0; k < 4; k++) { x += rnd() * 40 - 20; y += rnd() * 30; g.lineTo(x, y); } g.stroke(); }
  for (let i = 0; i < 160; i++) {          // fine swirling finger-smoothing ridges over the whole sheet
    const x = rnd() * 1024, y = rnd() * 1024, a = rnd() * 6, n = 8 + rnd() * 10 | 0, sx = 5 + rnd() * 4;
    g.lineWidth = 1.6;
    for (let k = 1; k <= n; k++) { g.strokeStyle = k % 2 ? 'rgba(40,40,40,.14)' : 'rgba(210,210,210,.14)'; g.beginPath(); g.ellipse(x, y, k * sx, k * sx * .7, a, rnd(), 4 + rnd() * 2); g.stroke(); }
  }
  return tex(c, 2, false);
}
function plaid(base) {
  const [c, g] = canvas(256), dark = '#1d1414';
  g.fillStyle = base; g.fillRect(0, 0, 256, 256);
  g.globalAlpha = .5; g.fillStyle = dark; g.fillRect(0, 96, 256, 64); g.fillRect(96, 0, 64, 256);
  g.globalAlpha = .25; g.fillRect(0, 16, 256, 18); g.fillRect(16, 0, 18, 256);
  g.globalAlpha = .45; g.fillStyle = '#e9d8ac'; g.fillRect(0, 126, 256, 4); g.fillRect(126, 0, 4, 256);
  g.globalAlpha = 1; return c;
}
function fabric(base, kind) {     // plain cloth with grime; denim twill; canvas weave
  const [c, g] = canvas(256); g.fillStyle = base; g.fillRect(0, 0, 256, 256);
  if (kind === 'denim') { g.strokeStyle = 'rgba(255,255,255,.12)'; g.lineWidth = 1; for (let i = -256; i < 256; i += 4) { g.beginPath(); g.moveTo(i, 0); g.lineTo(i + 256, 256); g.stroke(); } }
  if (kind === 'canvas') { g.fillStyle = 'rgba(0,0,0,.08)'; for (let i = 0; i < 256; i += 3) g.fillRect(0, i, 256, 1); }
  for (let i = 0; i < 14; i++) { g.fillStyle = `rgba(60,42,22,${.03 + rnd() * .06})`; g.beginPath(); g.ellipse(rnd() * 256, rnd() * 256, 6 + rnd() * 20, 4 + rnd() * 10, rnd() * 3, 0, 7); g.fill(); }
  return c;
}
function torn(c) {          // ragged holes showing skin through the cloth
  const g = c.getContext('2d');
  for (let i = 0; i < 3; i++) { const x = 30 + rnd() * 196, y = 30 + rnd() * 196, r = 10 + rnd() * 12; g.beginPath();
    for (let k = 0; k <= 12; k++) { const a = k / 12 * 6.28, rr = r * (.6 + rnd() * .6); k ? g.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr * .8) : g.moveTo(x + rr, y); }
    g.closePath(); g.fillStyle = SKIN; g.fill(); g.strokeStyle = 'rgba(40,25,20,.7)'; g.lineWidth = 3; g.stroke(); }
  return c;
}
function stained(base) {          // stained/bloodied cloth
  const c = fabric(base, ''); const g = c.getContext('2d');
  for (let i = 0; i < 6; i++) { g.fillStyle = rnd() < .6 ? 'rgba(170,130,40,.18)' : 'rgba(120,14,14,.35)'; g.beginPath(); g.ellipse(rnd() * 256, rnd() * 256, 8 + rnd() * 24, 6 + rnd() * 18, rnd() * 3, 0, 7); g.fill(); }
  return c;
}
function paisley(base) {
  const W = 1024, H = 512, c = document.createElement('canvas'); c.width = W; c.height = H; const g = c.getContext('2d');
  g.fillStyle = base; g.fillRect(0, 0, W, H);
  const ink = 'rgba(245,242,232,.92)'; g.strokeStyle = ink; g.fillStyle = ink; g.lineCap = 'round';
  const tear = (x, y, s, a) => {                    // one paisley teardrop with a curled tail and inner rings
    g.save(); g.translate(x, y); g.rotate(a); g.scale(s, s);
    const drop = () => { g.beginPath(); g.moveTo(0, 22); g.bezierCurveTo(-26, 18, -24, -16, 2, -18); g.bezierCurveTo(20, -20, 26, -6, 18, -26); g.bezierCurveTo(34, -10, 26, 22, 0, 22); };
    g.lineWidth = 3.2; drop(); g.stroke();
    g.save(); g.scale(.62, .62); g.translate(-2, 4); g.lineWidth = 3; drop(); g.stroke(); g.restore();
    g.beginPath(); g.arc(-1, 6, 4, 0, 7); g.fill();
    for (let k = 0; k < 9; k++) { const t = k / 9 * Math.PI * 1.6 + 1.6; g.beginPath(); g.arc(Math.cos(t) * 30, 4 + Math.sin(t) * 28, 1.8, 0, 7); g.fill(); }
    g.restore();
  };
  for (let y = 70; y < H - 40; y += 110) for (let x = 90 + (y / 110 % 2) * 60; x < W - 60; x += 135) tear(x + (rnd() - .5) * 20, y + (rnd() - .5) * 16, .95 + rnd() * .3, rnd() * 6.3);
  for (let i = 0; i < 26; i++) {                     // small four-petal flowers
    const x = 40 + rnd() * (W - 80), y = 30 + rnd() * (H - 60); g.lineWidth = 2.2;
    for (let k = 0; k < 4; k++) { g.beginPath(); g.ellipse(x + Math.cos(k * 1.57) * 6, y + Math.sin(k * 1.57) * 6, 5, 3, k * 1.57, 0, 7); g.stroke(); }
  }
  for (let i = 0; i < 260; i++) { g.beginPath(); g.arc(rnd() * W, rnd() * H, .9 + rnd() * 1.6, 0, 7); g.fill(); }
  for (const x of [22, W - 22]) {                   // border bands along the folded edges
    g.lineWidth = 3; g.beginPath(); g.moveTo(x - 14, 0); g.lineTo(x - 14, H); g.moveTo(x + 14, 0); g.lineTo(x + 14, H); g.stroke();
    for (let y = 8; y < H; y += 16) { g.beginPath(); g.arc(x, y, 3.2, 0, 7); g.fill(); }
  }
  g.lineWidth = 3; g.beginPath(); g.moveTo(0, 14); g.lineTo(W, 14); g.stroke();
  for (let x = 8; x < W; x += 16) { g.beginPath(); g.arc(x, 28, 2.4, 0, 7); g.fill(); }
  return c;
}

function clay(color, o = {}) {
  return new THREE.MeshStandardMaterial({ color: o.map ? '#ffffff' : color, roughness: Math.max(o.rough ?? .95, o.metal || o.rough < .5 ? 0 : .9), metalness: o.metal ?? 0,
    map: o.map || null, bumpMap: o.noBump ? null : BUMP, bumpScale: (o.bump ?? 1.2) * 7.5, roughnessMap: null, side: o.side ?? THREE.FrontSide,
    emissive: o.emissive || '#000000', emissiveIntensity: o.ei ?? 0, emissiveMap: o.emissiveMap || null,
    transparent: !!o.alpha, alphaMap: o.alpha || null, alphaTest: o.alpha ? .5 : 0 });
}
function skinMat() {
  const t = A['Skin Tone'];
  if (t === 'Gilded') return clay(SKIN, { metal: .75, rough: .3, bump: .8 });
  if (t === 'Radioactive') return clay(SKIN, { emissive: '#5cff2a', ei: .18 });
  if (t === 'Charred') {
    const [c, g] = canvas(512); g.fillStyle = '#000'; g.fillRect(0, 0, 512, 512); g.strokeStyle = '#ff7a1a'; g.lineWidth = 3;
    for (let i = 0; i < 30; i++) { let x = rnd() * 512, y = rnd() * 512; g.beginPath(); g.moveTo(x, y); for (let k = 0; k < 5; k++) { x += rnd() * 50 - 25; y += rnd() * 50 - 25; g.lineTo(x, y); } g.stroke(); }
    return clay(SKIN, { emissive: '#ff7a1a', ei: 1.4, emissiveMap: tex(c, 1), rough: .9 });
  }
  return clay('#fff', { map: tex(mottle(SKIN), 1) });
}
// age spots, flushed blotches and pitting painted into the skin colour
function mottle(base) {
  const S = 1024, [c, g] = canvas(S); g.fillStyle = base; g.fillRect(0, 0, S, S);
  const blob = (col, n, r0, r1) => { for (let i = 0; i < n; i++) { const x = rnd() * S, y = rnd() * S, r = r0 + rnd() * (r1 - r0), gr = g.createRadialGradient(x, y, 0, x, y, r);
    gr.addColorStop(0, col); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = gr; g.beginPath(); g.ellipse(x, y, r, r * (.6 + rnd() * .4), rnd() * 3, 0, 7); g.fill(); } };
  blob('rgba(200,70,70,.12)', 34, 40, 110);       // flushed patches
  blob('rgba(110,70,45,.2)', 55, 4, 14);         // age spots
  blob('rgba(90,55,40,.3)', 30, 2, 5);           // freckles and moles
  blob('rgba(255,240,225,.12)', 30, 30, 90);      // pale patches
  for (let i = 0; i < 400; i++) { g.fillStyle = 'rgba(80,40,30,.18)'; g.beginPath(); g.arc(rnd() * S, rnd() * S, .8 + rnd() * 1.6, 0, 7); g.fill(); }   // pores and pits
  return c;
}
const SKINMAT = skinMat();
const skinShade = k => clay(shade(SKIN, k));

// ------------------------------------------------------------------ renderer, camera, lights, backdrop
const W = 1000;
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setSize(W, W); renderer.setPixelRatio(window.PIXEL_RATIO || 2);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene(); scene.background = new THREE.Color(BG);
const cam = new THREE.PerspectiveCamera(window.FOV || 34, 1, .1, 100); cam.position.set(0, -.4, 12.5); cam.lookAt(0, -1.0, 0);
const dark = ['Midnight', 'Full Moon', 'Blood Red'].includes(A['Background']);
scene.add(new THREE.HemisphereLight(0xfff6ee, 0x8a7060, dark ? 1.0 : 1.45));
const key = new THREE.DirectionalLight(0xfff2e4, 1.7); key.position.set(-2, 3.5, 9); key.castShadow = true;
key.shadow.mapSize.set(2048, 2048); key.shadow.radius = 18; key.shadow.bias = -.0015; key.shadow.normalBias = .03;
Object.assign(key.shadow.camera, { left: -6, right: 6, top: 6, bottom: -6, near: 1, far: 30 }); scene.add(key);
const fill = new THREE.DirectionalLight(0xeef0ff, 1.0); fill.position.set(5, 0, 8); scene.add(fill);
const rim = new THREE.DirectionalLight(dark ? 0xbfd0ff : 0xffe4c0, dark ? 1.8 : 1.2); rim.position.set(5, 4, -6); scene.add(rim);

function add(m, parent = scene) { m.castShadow = m.receiveShadow = true; parent.add(m); return m; }
function mesh(geo, mat, parent, pos, rot, scl) {
  const m = add(new THREE.Mesh(geo, mat), parent);
  if (pos) m.position.set(...pos); if (rot) m.rotation.set(...rot); if (scl) (typeof scl === 'number' ? m.scale.setScalar(scl) : m.scale.set(...scl));
  return m;
}
function tube(pts, r, mat, parent, closed = false, seg) {
  return add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts, closed), seg || Math.max(32, pts.length * 4), r, 12, closed), mat), parent);
}
const V = (x, y, z) => new THREE.Vector3(x, y, z);
// flat band of leather/cloth along a path, facing the viewer (+z), with stitched edges
function ribbon(pts, w, col, parent, t = .03) {
  const c = new THREE.CatmullRomCurve3(pts), N = 80, pos = [], idx = [];
  for (let i = 0; i <= N; i++) { const p = c.getPoint(i / N), T = c.getTangent(i / N), B = T.clone().cross(V(0, 0, 1)).normalize();
    for (const [b, z] of [[-1, 0], [-1, t], [1, t], [1, 0]]) { const q = p.clone().addScaledVector(B, b * w / 2); q.z += z; pos.push(q.x, q.y, q.z); } }
  for (let i = 0; i < N; i++) for (let k = 0; k < 3; k++) { const a = i * 4 + k; idx.push(a, a + 4, a + 1, a + 1, a + 4, a + 5); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
  const m = add(new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: col, roughness: .7, side: THREE.DoubleSide, bumpMap: null })), parent);
  return m;
}
const sph = (r, a = 32, b = 24) => new THREE.SphereGeometry(r, a, b);

// backdrop: a sheet of pressed plasticine, plus 1/1 scenery
{
  const bgName = A['Background'];
  const wall = mesh(new THREE.PlaneGeometry(40, 40), new THREE.MeshStandardMaterial({ color: BG, roughness: bgName === 'Gold' ? .45 : 1,
    metalness: bgName === 'Gold' ? .5 : 0, bumpMap: pressedClay(), bumpScale: 14 }), scene, [0, 0, -6]);
  wall.castShadow = false;
  const Z = -5.85;
  if (bgName === 'Full Moon') {
    const moon = mesh(sph(1.4, 48, 32), clay('#efe6c4', { rough: .9 }), scene, [2.6, 2.5, Z], null, [1, 1, .25]);
    for (let i = 0; i < 6; i++) mesh(sph(.12 + rnd() * .18), clay('#d6cb9f'), scene, [2.6 + (rnd() - .5) * 1.8, 2.5 + (rnd() - .5) * 1.8, Z + .33], null, [1, 1, .3]);
    moon.castShadow = false;
  }
  if (bgName === 'Cornfield') {
    for (let i = 0; i < 26; i++) {
      const x = -5 + i * .4 + (rnd() - .5) * .2, h = 2.4 + rnd() * 1.2;
      mesh(new THREE.CylinderGeometry(.05, .07, h, 10), clay('#8a7a3a'), scene, [x, -3 + h / 2, Z + .3]);
      for (let k = 0; k < 3; k++) {
        const leaf = mesh(new THREE.CapsuleGeometry(.04, .6, 4, 8), clay('#a08a40'), scene, [x + (k % 2 ? .25 : -.25), -2.6 + k * .7 + rnd() * .3, Z + .32], [0, 0, k % 2 ? -1 : 1]);
        leaf.scale.set(1.6, 1, .4);
      }
      if (rnd() < .5) mesh(new THREE.CapsuleGeometry(.09, .3, 6, 10), clay('#e3b440'), scene, [x + .12, -1.2 + rnd() * .8, Z + .4], [0, 0, -.4]);
    }
  }
  if (bgName === 'Blood Drip' || bgName === 'Toxic Slime') {
    const col = bgName === 'Blood Drip' ? '#8e1010' : '#5ee82a';
    const m = clay(col, { rough: .25, bump: .2, emissive: bgName === 'Toxic Slime' ? '#3aff00' : '#000', ei: .15 });
    mesh(new THREE.BoxGeometry(14, .5, .2), m, scene, [0, 3.4, Z + .1]);
    for (let i = 0; i < 18; i++) { const x = -5 + i * .6 + rnd() * .3, L = .4 + rnd() * 1.4;
      mesh(new THREE.CapsuleGeometry(.09, L, 6, 12), m, scene, [x, 3.2 - L / 2, Z + .15]);
      mesh(sph(.13), m, scene, [x, 3.15 - L, Z + .18]); }
  }
  if (bgName === 'Blood Splatter') {        // wet blood flung at the wall: splats, flecks and runs dripping down
    const wet = clay('#8a0c0c', { rough: .22, bump: .25 }), dark = clay('#5e0606', { rough: .3, bump: .3 });
    const splat = (x, y, R) => {
      const m = rnd() < .3 ? dark : wet;
      mesh(sph(R, 28, 18), m, scene, [x, y, Z], null, [1 + rnd() * .4, .8 + rnd() * .4, .12]);
      for (let i = 0, n = 6 + rnd() * 8; i < n; i++) {                  // lobes and flung flecks
        const a = rnd() * Math.PI * 2, d = R * (.7 + rnd() * 1.6), r = R * (d > R * 1.4 ? .08 + rnd() * .12 : .3 + rnd() * .3);
        mesh(sph(r, 14, 10), m, scene, [x + Math.cos(a) * d, y + Math.sin(a) * d, Z + .02], null, [1, 1, .2]);
        if (d < R * 1.3 && rnd() < .4) tube([V(x + Math.cos(a) * R * .5, y + Math.sin(a) * R * .5, Z + .03), V(x + Math.cos(a) * d * 1.5, y + Math.sin(a) * d * 1.5, Z + .03)], r * .35, m, scene);
      }
      for (let i = 0, n = 1 + rnd() * 3; i < n; i++) {                  // runs dripping down the wall
        const dx = (rnd() - .5) * R * 1.4, L = .6 + rnd() * 2.2, w = .05 + rnd() * .05, x0 = x + dx, y0 = y - R * .4;
        tube([V(x0, y0, Z + .02), V(x0 + (rnd() - .5) * .08, y0 - L * .5, Z + .02), V(x0 + (rnd() - .5) * .1, y0 - L, Z + .02)], w, m, scene);
        mesh(sph(w * 1.9, 14, 10), m, scene, [x0, y0 - L - w, Z + .03], null, [1, 1.25, .45]);
      }
    };
    for (const [x, y, R] of [[-3.6, 2.6, .55], [3.4, 2.9, .45], [-4.2, -.2, .4], [3.9, .6, .5], [.4, 3.6, .35], [-1.8, 3.4, .3], [2.0, 1.9, .25]])
      splat(x + (rnd() - .5) * .8, y + (rnd() - .5) * .6, R * (.8 + rnd() * .5));
    for (let i = 0; i < 40; i++) mesh(sph(.025 + rnd() * .05, 10, 8), wet, scene, [(rnd() - .5) * 10, -1 + rnd() * 5, Z + .02], null, [1, 1, .25]);
  }
  if (bgName === 'Midnight') for (let i = 0; i < 14; i++) mesh(sph(.04 + rnd() * .04), clay('#fff7cf', { emissive: '#fff7cf', ei: .5 }), scene, [(rnd() - .5) * 10, rnd() * 3.5, Z + .1]);
}

// ------------------------------------------------------------------ head: lobed swollen skull with a face
const HEAD_Y = .08, BODY_Y = -1.75;
const head = new THREE.Group(); head.position.set(.33, HEAD_Y, 0); head.rotation.set(.03, .4, 0); head.scale.setScalar(1.45); scene.add(head);
const SW = { Mild: .6, Lumpy: 1, Grotesque: 1.45 }[A['Swelling']] * (A['Hair'] === 'Backwards Cap' ? .6 : 1);
const SHAPE = A['Head Shape'];
const dir = (x, y, z) => V(x, y, z).normalize();
const LOBES = [[dir(-.25, .55, -.8), .30, .42], [dir(.25, .95, -.15), .2, .36], [dir(-.85, .35, -.35), .2, .34],
  [dir(.7, .5, -.5), .22, .34], [dir(0, .15, -1), .24, .38], [dir(-.4, .9, .25), .14, .3], [dir(.45, .8, .35), .12, .28],
  [dir(-.6, -.05, -.75), .16, .3], [dir(.75, .05, -.6), .14, .3], [dir(-.1, .75, -.55), .2, .32]];
for (const l of LOBES) { l[1] *= SW * (.75 + rnd() * .5); l[0].add(V(rnd() - .5, rnd() - .5, rnd() - .5).multiplyScalar(.2)).normalize(); }
if (SHAPE === 'Brow Bulge') LOBES.push([dir(0, .5, .85), .28, .3]);
if (SHAPE === 'Lopsided') LOBES.push([dir(-.75, .45, -.45), .48, .42]);
// tumors are sculpted into the skull as swollen mounds (no separate balls)
const TUMORS = SHAPE === 'Tumor Cluster' ? [dir(-.5, .7, -.4), dir(.3, .85, -.3), dir(-.8, .2, -.3), dir(.1, .5, -.85)].map(d => [d, .16 + rnd() * .06, .2 + rnd() * .04]) : [];
const CHEEK = [-.42 + rnd() * .1, -.22, .07 + .06 * SW];    // swollen near cheek (George's reference)
const HX = 1.0, HY = 1.3;   // tall dome: George's silhouette
// broad flat-ish crown, long jaw, the back of the skull bulging behind the ear
const stretchY = y => y > 0 ? y * 1.2 : y * 1.45;
const stretchX = (x, y) => x * HX * (1 + .1 * Math.max(0, y)) * (x < 0 ? 1.07 : 1);
const BACKLOBE = V(-.75, .55, -.35).normalize();
function headPoint(n) {
  let best = 0;
  const faceW = THREE.MathUtils.smoothstep(n.z, .25, .65);           // keep the face smooth
  let sum = 0;
  for (const [d, a, w] of LOBES) sum += Math.exp(a * (1 - faceW * .6) * Math.exp(-(1 - n.dot(d)) / (w * w)) / .045);
  best = .045 * Math.log(sum / LOBES.length * 1.0 + 1e-9) + .045 * Math.log(LOBES.length) * .55;
  let r = 1 + Math.max(0, best);
  if (n.z > 0) {
    r += .06 * Math.exp(-((n.y - .25) ** 2) / .006) * THREE.MathUtils.smoothstep(n.z, .5, .8);           // brow ridge
    r += CHEEK[2] * Math.exp(-((n.x - CHEEK[0]) ** 2 + (n.y - CHEEK[1]) ** 2) / .03);                   // swollen cheek
    r += .07 * Math.exp(-(n.x ** 2 / .04 + (n.y + .7) ** 2 / .02));                                    // chin
    r += .07 * Math.exp(-((n.x - .6) ** 2 + (n.y + .28) ** 2) / .03);                                  // far cheek bulge (silhouette)
    r += .1 * Math.exp(-((n.x - .3) ** 2 / .08 + (n.y + .62) ** 2 / .05));                            // heavy lower jaw
    r += .09 * Math.exp(-((n.x - .3) ** 2 / .05 + (n.y + .85) ** 2 / .03));                           // jutting chin
    {
      const ny = n.y, nx = n.x - .01;
      // nose bridge sculpted out of the face: a ridge from between the brows widening into the nose
      const along = THREE.MathUtils.smoothstep(ny, -.22, .12) * (1 - THREE.MathUtils.smoothstep(ny, .12, .2));
      r += (.05 + .07 * (1 - THREE.MathUtils.smoothstep(ny, -.2, .1))) * along * Math.exp(-(nx * nx) / (.004 + .006 * (1 - THREE.MathUtils.smoothstep(ny, -.2, .1))));
      // cheekbones and the soft muzzle round the mouth
      for (const sx of [-1, 1]) r += .045 * Math.exp(-((n.x - sx * .4) ** 2 / .02 + (ny + .08) ** 2 / .012));
      r += .055 * Math.exp(-(nx * nx / .06 + (ny + .48) ** 2 / .03));
      // nasolabial folds: creases from the nose wings round the muzzle
      for (const sx of [-1, 1]) { const cx = sx * (.2 + (-.2 - ny) * .35); if (ny < -.15 && ny > -.62) r -= .025 * Math.exp(-((n.x - cx) ** 2) / .0012) * Math.sin(Math.PI * (-.15 - ny) / .47); }
      // carved wrinkles: forehead furrows, crow's feet, lines bracketing the mouth
      if (ny > .3 && ny < .66) r -= .014 * Math.pow(Math.max(0, Math.sin((ny - .3) * 52 + nx * 3)), 8) * Math.exp(-(nx * nx) / .12);
      for (const sx of [-1, 1]) { const dx = n.x - sx * .5; if (Math.abs(dx) < .08 && ny > -.05 && ny < .22) r -= .008 * Math.pow(Math.max(0, Math.sin(ny * 70 + dx * 10)), 8) * (1 - Math.abs(dx) / .08); }
      for (const sx of [-1, 1]) { const cx = sx * .27; if (ny < -.6 && ny > -.85) r -= .015 * Math.exp(-((n.x - cx - sx * (-.6 - ny) * .1) ** 2) / .0008); }
      // under-eye hollows
      for (const ex of [-.33, .33]) r -= .02 * Math.exp(-((n.x - ex) ** 2 / .012 + (ny + .1) ** 2 / .003));
    }
  }
  {
    const b = n.dot(BACKLOBE); if (b > 0) r += .1 * Math.exp(-(1 - b) / .1);                         // full back-top of the skull
    for (const ex of [-.33, .33]) r -= .05 * Math.exp(-((n.x - ex) ** 2 + (n.y - .1) ** 2) / .012);     // eye sockets
  }
  for (const [d, h, w] of TUMORS) { const t = Math.exp(-(1 - n.dot(d)) / (w * w)); r += h * t * t * (3 - 2 * t); }
  if (SHAPE === 'Split Skull') r -= .13 * Math.exp(-(n.x ** 2) / .003) * THREE.MathUtils.smoothstep(n.y, .2, .5) * (n.z < .55 ? 1 : 0);
  let x = n.x * r * .92, y = n.y * r, z = n.z * r;
  if (SHAPE === 'Cone Head' && y > 0) { const k = y * y; y *= 1 + .55 * k; x *= 1 - .3 * k; z *= 1 - .3 * k; }
  if (SHAPE === 'Flat Top' && y > .82) y = .82 + (y - .82) * .25;
  if (y < -.15) { const t = -.15 - y; x *= 1 - t * .45; if (z < 0) z *= 1 - t * .6; }
  if (z > 0) z *= .9;
  return V(stretchX(x, y), stretchY(y), z);
}
const HEADGEO = (() => {
  const g = new THREE.SphereGeometry(1, 200, 150), p = g.attributes.position, n = V(0, 0, 0);
  for (let i = 0; i < p.count; i++) { n.fromBufferAttribute(p, i).normalize(); p.setXYZ(i, ...headPoint(n).toArray()); }
  g.computeVertexNormals(); return g;
})();
const HEADMESH = mesh(HEADGEO, SKINMAT, head); head.updateMatrixWorld(true);
const PROBE = new THREE.Mesh(HEADGEO); PROBE.updateMatrixWorld(true);
const ray = new THREE.Raycaster();
// a point on the face: cast straight back from in front of the head
function onFace(x, y, extra = []) {
  x = stretchX(x, y); y = stretchY(y);
  ray.set(V(x, y, 3), V(0, 0, -1)); const h = ray.intersectObjects([PROBE, ...extra], true)[0];
  return h ? { p: h.point.clone(), n: h.face.normal.clone().transformDirection(h.object.matrixWorld) } : { p: V(x, y, .6), n: V(0, 0, 1) };
}
// a point on the skull along a direction from the centre
function onSkull(d) {
  d = d.clone().normalize(); ray.set(d.clone().multiplyScalar(4), d.clone().negate()); const h = ray.intersectObject(PROBE)[0];
  return h ? { p: h.point.clone(), n: h.face.normal.clone() } : { p: d, n: d };
}
const ZAX = V(0, 0, 1);
function placed(obj, at, lift = 0, parent = head) {
  obj.position.copy(at.p).addScaledVector(at.n, lift); obj.quaternion.setFromUnitVectors(ZAX, at.n); parent.add(obj); return obj;
}
function group() { return new THREE.Group(); }

// tumors and split-skull staples

if (SHAPE === 'Split Skull') for (const t of [.35, .55, .75]) {
  const at = onSkull(dir(0, Math.cos(t * 1.4), -Math.sin(t * 1.4)));
  const st = placed(group(), at, .01);
  tube([V(-.09, 0, -.02), V(-.09, 0, .02), V(.09, 0, .02), V(.09, 0, -.02)], .013, clay('#b8bcc0', { metal: .8, rough: .3, bump: .1 }), st);
}

// ------------------------------------------------------------------ ears
function buildEar() {
  if (MSTYLE === 'sack') return;
  const ear = group(); ear.position.set(-.86 * HX - .03, -.41, -.08); ear.rotation.set(0, -Math.PI / 2 + .5, .1); ear.scale.setScalar(1.4); head.add(ear);
  const kind = A['Ear'];
  mesh(sph(.2, 40, 30), SKINMAT, ear, null, null, [.8, 1.25, .35]);
  const rimE = mesh(new THREE.TorusGeometry(.17, .065, 18, 50, Math.PI * (kind === 'Torn' ? 1.15 : 1.55)), SKINMAT, ear, [0, 0, .03], [0, 0, Math.PI * .55], [.85, 1.2, 1]);
  mesh(sph(.06, 16, 12), skinShade(.45), ear, [-.02, -.02, .05], null, [1, 1, .4]);
  // antihelix ridge with its upper fork, tragus flap, and a shadowed bowl leading into the canal
  tube([V(.06, -.13, .06), V(.1, -.02, .07), V(.08, .1, .07), V(.0, .15, .06)], .028, SKINMAT, ear);
  tube([V(.09, .05, .07), V(-.02, .07, .065)], .02, SKINMAT, ear);
  mesh(sph(.045, 16, 12), SKINMAT, ear, [-.12, -.06, .05], null, [.8, 1.1, .7]);
  mesh(sph(.1, 20, 14), skinShade(.62), ear, [-.01, -.03, .035], null, [.8, 1, .3]);
  if (kind === 'Normal' || kind === 'Cauliflower') mesh(sph(.11, 24, 18), SKINMAT, ear, [.0, -.27, .03], null, [1, 1.15, .7]);   // fat hanging lobe (silhouette)
  if (kind === 'Cauliflower') for (const [x, y] of [[.12, .12], [.15, -.02], [.06, .2], [.0, .1], [.1, -.12]]) mesh(sph(.06), SKINMAT, ear, [x, y, .07]);
  if (kind === 'Torn') { mesh(sph(.05), clay('#7a1212', { rough: .4 }), ear, [.1, .16, .06], null, [1, .5, .5]); }
  if (kind === 'Gauged') {
    mesh(new THREE.TorusGeometry(.085, .045, 18, 40), SKINMAT, ear, [-.02, -.3, .03], null, [1, 1.15, 1]);
    mesh(new THREE.TorusGeometry(.075, .028, 18, 48), clay('#151515', { rough: .3, bump: .2 }), ear, [-.02, -.3, .035]);
    mesh(new THREE.TorusGeometry(.052, .008, 10, 40), clay('#c9ccd0', { metal: .8, rough: .25, bump: .1 }), ear, [-.02, -.3, .06]);
  } else if (kind === 'Torn') mesh(sph(.075), SKINMAT, ear, [-.02, -.22, .03]);
}
buildEar();

// ------------------------------------------------------------------ face: eyes, brows, nose, mouth
const EYE_COLORS = { 'Swamp Green': '#6f8f4a', 'Ice Blue': '#8fb8de', 'Mud Brown': '#5a3f28', 'Hazel': '#8a7638', 'Steel Grey': '#9aa3a8',
  'Jaundice Yellow': '#d1a91c', 'Milky White': '#d8d4c8' };
const EC = A['Eye Color'] || 'Mud Brown', MILKY = EC === 'Milky White';
const IRIS = A['Skin Tone'] === 'Albino' ? '#d77a8a' : EC === 'Mismatched' ? '#8fb8de' : (EYE_COLORS[EC] || '#5a3f28');   // near eye
const IRIS_FAR = A['Skin Tone'] === 'Albino' ? '#d77a8a' : EC === 'Mismatched' ? '#5a3f28' : IRIS;
// bloodshot sclera: veins in angular space converging on the front of the ball (sphere UV front = u .25, v .5)
function scleraMat(blood = 1) {
  const S = 512, [c, g] = canvas(S), P = (az, el) => [S * .25 + az * S / 360, S * .5 - el * S / 180];
  g.fillStyle = '#efe5cf'; g.fillRect(0, 0, S, S);
  const wash = g.createRadialGradient(...P(0, 0), S * .05, ...P(0, 0), S * .3);   // pink, sore rim
  wash.addColorStop(0, 'rgba(230,120,110,0)'); wash.addColorStop(1, `rgba(205,85,80,${.35 + .25 * blood})`);
  g.fillStyle = wash; g.fillRect(0, 0, S, S);
  g.lineCap = 'round';
  function vein(az, el, ang, len, w) {
    g.beginPath(); g.moveTo(...P(az, el)); g.lineWidth = w;
    g.strokeStyle = `rgba(${160 + rnd() * 40 | 0},${20 + rnd() * 25 | 0},${25 + rnd() * 20 | 0},${.75 + rnd() * .25})`;
    for (let k = 0; k < 6; k++) {
      ang += (rnd() - .5) * .7; az += Math.cos(ang) * len / 6; el += Math.sin(ang) * len / 6;
      if (Math.hypot(az, el) < 34) break; g.lineTo(...P(az, el));
      if (w > 1.6 && rnd() < .35) { g.stroke(); vein(az, el, ang + (rnd() < .5 ? .8 : -.8), len * .5, w * .6); g.beginPath(); g.moveTo(...P(az, el)); g.lineWidth = w; }
    }
    g.stroke();
  }
  const n = Math.round(14 + 16 * blood);
  for (let i = 0; i < n; i++) { const a = rnd() * Math.PI * 2, r = 75 + rnd() * 20;
    vein(Math.cos(a) * r, Math.sin(a) * r * .9, a + Math.PI + (rnd() - .5) * .5, 40 + rnd() * 25, 2.2 + rnd() * 2.2 * blood); }
  return clay('#fff', { map: tex(c), rough: .6, bump: .45 });   // moist clay, not glass
}
const eyeballMat = scleraMat(A['Eyes'] === 'Pinprick' || A['Eyes'] === 'Popped Out' ? 1.6 : 1);
// iris: radial fibres, dark limbal ring, flecks and the pupil, painted onto a slightly domed disc
function irisTex(pupil, IRIS) {
  const S = 256, [c, g] = canvas(S), C = S / 2;
  g.fillStyle = shade(IRIS, .45); g.fillRect(0, 0, S, S);
  const base = g.createRadialGradient(C, C, 0, C, C, C);
  base.addColorStop(0, shade(IRIS, 1.35)); base.addColorStop(.55, IRIS); base.addColorStop(.86, shade(IRIS, .7)); base.addColorStop(1, shade(IRIS, .3));
  g.fillStyle = base; g.beginPath(); g.arc(C, C, C, 0, 7); g.fill();
  for (let i = 0; i < 140; i++) { const a = rnd() * Math.PI * 2, r0 = C * pupil * (1 + rnd() * .3), r1 = C * (.7 + rnd() * .25);
    g.strokeStyle = rnd() < .5 ? shade(IRIS, 1.5) + '88' : shade(IRIS, .55) + '99'; g.lineWidth = 1 + rnd() * 2;
    g.beginPath(); g.moveTo(C + Math.cos(a) * r0, C + Math.sin(a) * r0); g.lineTo(C + Math.cos(a + (rnd() - .5) * .15) * r1, C + Math.sin(a + (rnd() - .5) * .15) * r1); g.stroke(); }
  for (let i = 0; i < 6; i++) { const a = rnd() * 7, r = C * (pupil + .1 + rnd() * .4); g.fillStyle = '#5a3a1a88'; g.beginPath(); g.arc(C + Math.cos(a) * r, C + Math.sin(a) * r, 3 + rnd() * 5, 0, 7); g.fill(); }
  g.strokeStyle = shade(IRIS, .25); g.lineWidth = S * .07; g.beginPath(); g.arc(C, C, C - S * .035, 0, 7); g.stroke();   // limbal ring
  g.fillStyle = shade(IRIS, .6); g.beginPath(); g.arc(C, C, C * pupil * 1.18, 0, 7); g.fill();                         // collarette
  g.fillStyle = MILKY ? '#6e6c66' : '#060404'; g.beginPath(); g.arc(C, C, C * pupil, 0, 7); g.fill();                // pupil
  if (MILKY) { const fog = g.createRadialGradient(C, C, 0, C, C, C); fog.addColorStop(0, 'rgba(240,238,230,.75)'); fog.addColorStop(1, 'rgba(225,222,212,.35)'); g.fillStyle = fog; g.fillRect(0, 0, S, S); }   // clouded, blind
  return tex(c);
}
const IRISTEX = {};
function irisDisc(r, pupil, h, col) {
  const geo = new THREE.RingGeometry(r * .001, r, 48, 10), p = geo.attributes.position;
  for (let i = 0; i < p.count; i++) { const d = Math.hypot(p.getX(i), p.getY(i)) / r; p.setZ(i, h * (1 - d * d)); }
  geo.computeVertexNormals();
  const key = pupil.toFixed(2) + col, m = clay('#fff', { map: IRISTEX[key] ||= irisTex(pupil, col), rough: .35, bump: .08 });
  const o = new THREE.Mesh(geo, m); o.userData.rigid = true; return o;
}
const CORNEA = new THREE.MeshPhysicalMaterial({ color: '#ffffff', roughness: .04, metalness: 0, transparent: true, opacity: .07, clearcoat: .5, clearcoatRoughness: .2 });
// the eyeball itself: sclera, iris that turns with the gaze, wet cornea and a hot highlight
function eyeball(size, o = {}, parent) {
  const e = group(); parent.add(e);
  mesh(sph(size, 40, 30), GLOW ? clay(GLOW, { emissive: GLOW, ei: 2.5, rough: .3, noBump: true }) : (o.mat || eyeballMat), e).userData.rigid = true;   // no wobble: it would swallow the iris
  if (GLOW) { const l = new THREE.PointLight(GLOW, .5, 1.2); l.position.set(0, 0, size * 1.5); e.add(l); return e; }
  const look = o.look || [0, 0], ir = size * (o.iris ?? .52), gaze = group();
  gaze.rotation.set(-look[1] * .45 + Math.max(0, (o.lid ?? .35) - .2) * 1.1, look[0] * .45, 0); e.add(gaze);   // heavy lids push the gaze down so the iris peeks out
  const sz = Math.sqrt(size * size - ir * ir), disc = irisDisc(ir, o.pupil ?? .42, (size - sz) * 1.15 + size * .03, o.col || IRIS); disc.position.z = sz - size * .005; gaze.add(disc);
  const cor = mesh(new THREE.SphereGeometry(size * 1.025, 32, 16, 0, Math.PI * 2, 0, Math.asin(ir / size) * 1.25), CORNEA, gaze, null, [Math.PI / 2, 0, 0]);
  cor.userData.rigid = true; cor.castShadow = false;
  mesh(sph(size * .085, 12, 8), clay('#fff', { emissive: '#fff', ei: 1.2, noBump: true }), gaze, [size * .2, size * .2, sz + size * .2]).castShadow = false;
  return e;
}
const LIDMAT = clay('#' + new THREE.Color(SKIN).lerp(new THREE.Color('#c84e50'), .55).getHexString(), { bump: 1 });
const RIMMAT = clay('#b23a3c', { rough: .6, bump: .4 });
function eye(x, y, size, o = {}) {
  o.col ??= x < 0 ? IRIS : IRIS_FAR;
  size *= 1.6; const at = onFace(x, y + (o.dy || 0)), e = placed(group(), at, 0);
  mesh(sph(size * 1.45, 32, 24), clay(shade(SKIN, o.socket ?? .6)), e, [0, 0, -size * .35], null, [1, .9, .3]);      // socket
  if (o.hollow || o.popped) {
    mesh(sph(size * 1.1), new THREE.MeshStandardMaterial({ color: o.popped ? '#3a0606' : '#050303', roughness: o.popped ? .35 : 1 }), e, [0, 0, -size * .1], null, [1, .9, .35]);
    if (o.popped) {      // raw red rim of the emptied socket
      mesh(new THREE.TorusGeometry(size * .98, size * .13, 12, 36), clay('#7e1c1c', { rough: .3, bump: .3 }), e, [0, 0, size * .02], null, [1, .9, .4]);
    }
    if (!o.popped) return e;
  } else eyeball(size * .92, o, e).position.z = -size * .28;        // sunk into the socket
  if (!o.popped) {
    const lid = Math.max(o.lid ?? .35, .42);   // heavy, drooping upper lids
    const lidG = new THREE.SphereGeometry(size * 1.02, 32, 16, 0, Math.PI * 2, 0, Math.PI * Math.max(.05, lid));
    mesh(lidG, LIDMAT, e, [0, 0, -size * .26], [.35 + (o.tilt || 0), 0, o.roll || 0]);
  }
  // swollen, inflamed lids all round: wet red rim, puffy upper lid, heavy lower bag (George's target head)
  const rot = [0, 0, o.roll || 0];
  if (!o.hollow) mesh(new THREE.TorusGeometry(size * .9, size * .12, 12, 40), RIMMAT, e, [0, 0, size * .12], rot, [1.12, .78, .6]);
  mesh(new THREE.TorusGeometry(size * .98, size * .42, 16, 36, Math.PI), LIDMAT, e, [0, size * .1, size * .02], rot, [1.15, .8, .75]);
  mesh(new THREE.TorusGeometry(size * .98, size * .38, 16, 36, Math.PI), LIDMAT, e, [0, -size * .12, size * .0], [0, 0, Math.PI + (o.roll || 0)], [1.12, .7, .75]);
  return e;
}
// popped out eye: the ball hangs out of its socket onto the cheek on a raw optic stalk
function poppedEye(x, y, size) {
  size *= 1.35;
  const s0 = onFace(x, y), hang = onFace(x - .05, y - .36);
  const start = s0.p.clone().addScaledVector(s0.n, -.02), end = hang.p.clone().addScaledVector(hang.n, size * 1.15);
  const stalk = new THREE.CatmullRomCurve3([start, start.clone().addScaledVector(s0.n, .07).add(V(0, -size * .3, 0)),
    start.clone().lerp(end, .6).addScaledVector(s0.n, .05), end.clone().add(V(0, size * .7, 0)).addScaledVector(hang.n, -size * .2), end]);
  const sm = clay('#b8333a', { rough: .3, bump: .4 });
  add(new THREE.Mesh(new THREE.TubeGeometry(stalk, 48, size * .2, 14), sm), head);
  add(new THREE.Mesh(new THREE.TubeGeometry(stalk, 48, size * .05, 8), clay('#6e2a6e', { rough: .4 })), head).position.set(size * .12, 0, size * .12);   // a purple vessel along it
  const ball = eyeball(size * 1.05, { look: [.15, .25], pupil: .55, mat: scleraMat(2) }, head);
  ball.position.copy(end); ball.quaternion.setFromUnitVectors(ZAX, hang.n.clone().add(V(0, .25, .35)).normalize());
  mesh(sph(size * .55, 20, 14), sm, ball, [0, 0, -size * .75]);                                           // nerve root on the back
  mesh(sph(size * .1, 12, 8), clay('#8a0c0c', { rough: .15, noBump: true }), head, hang.p.clone().addScaledVector(hang.n, .02).add(V(0, -.07, 0)).toArray());   // drip of blood
}
// a slash of scar tissue across an emptied socket
function socketScar(x, y, size) {
  const pts = [[-1.7, 1.6], [-.6, .55], [.6, -.55], [1.7, -1.7]].map(([a, b]) => { const at = onFace(x + a * size, y + b * size); return at.p.addScaledVector(at.n, .025); });
  tube(pts, size * .09, clay('#b4626a', { rough: .5, bump: .6 }), head);
  for (let i = 0; i < 4; i++) { const t = .15 + i * .23, p = pts[0].clone().lerp(pts[3], t), d = pts[3].clone().sub(pts[0]).normalize(), q = V(-d.y, d.x, 0).multiplyScalar(size * .45);
    tube([p.clone().sub(q), p.clone().add(q).addScaledVector(V(0, 0, 1), .01)], size * .05, clay('#2a1a14'), head); }      // crude stitches
}
// cybernetic replacement: a bolted steel housing with a glowing red lens
function cyborgEye(x, y, size) {
  size *= 1.35; const at = onFace(x, y), e = placed(group(), at, 0);
  const st = clay('#9aa1a7', { metal: .2, rough: .7, bump: 1 }), dk = clay('#2b2e33', { metal: .15, rough: .75, bump: .8 });
  mesh(sph(size * 1.5, 32, 24), clay(shade(SKIN, .55)), e, [0, 0, -size * .35], null, [1, .9, .3]);             // scarred socket
  mesh(new THREE.CylinderGeometry(size * 1.35, size * 1.5, size * .55, 40), st, e, [0, 0, size * .1], [Math.PI / 2, 0, 0]);   // housing
  mesh(new THREE.TorusGeometry(size * 1.38, size * .12, 12, 48), dk, e, [0, 0, size * .38]);
  mesh(new THREE.CylinderGeometry(size * .8, size * .9, size * .5, 32), dk, e, [0, 0, size * .55], [Math.PI / 2, 0, 0]);       // lens barrel
  mesh(sph(size * .55, 28, 20), clay('#ff2a1a', { emissive: '#ff2a1a', ei: 2.2, rough: .15, noBump: true }), e, [0, 0, size * .72], null, [1, 1, .55]);
  mesh(sph(size * .16, 12, 8), clay('#fff', { emissive: '#fff', ei: 1.5, noBump: true }), e, [size * .2, size * .2, size * 1.0]);
  const l = new THREE.PointLight('#ff3a1a', .6, 1.4); l.position.set(0, 0, size * 1.6); e.add(l);
  e.updateMatrixWorld(true);
  for (let i = 0; i < 6; i++) { const a = i / 6 * Math.PI * 2 + .3; mesh(new THREE.CylinderGeometry(size * .12, size * .12, size * .1, 6), clay('#cfd5da', { metal: .8, rough: .3, noBump: true }), e, [Math.cos(a) * size * 1.1, Math.sin(a) * size * 1.1, size * .4], [Math.PI / 2, 0, 0]); }
  for (const [dy, c] of [[.3, '#b8332e'], [-.1, '#2b2e33']]) {                                                      // wires into the temple
    const p0 = e.localToWorld(V(-size * 1.3, size * dy, size * .2)), p1 = onFace(x - .3, y + dy * .4 + .05);
    tube([head.worldToLocal(p0), p1.p.clone().addScaledVector(p1.n, .05).lerp(head.worldToLocal(p0), .5).addScaledVector(p1.n, .06), p1.p.clone().addScaledVector(p1.n, .01)], size * .07, clay(c, { rough: .4 }), head);
  }
}
function buildEyes() {
  const k = A['Eyes'];
  if (k === 'Droopy Mismatch') { eye(-.33, .08, .13, { lid: .55, roll: .15 }); eye(.31, .04, .095, { lid: .35, dy: -.03 }); }
  else if (k === 'Lazy Eye') { eye(-.33, .08, .115, { lid: .4, look: [.6, .1] }); eye(.31, .08, .11, { lid: .35, look: [1, -.5] }); }
  else if (k === 'Sunken Socket') { eye(-.33, .08, .085, { lid: .3, socket: .38 }); eye(.31, .08, .08, { lid: .3, socket: .38 }); }
  else if (k === 'Swollen Shut') { eye(-.33, .08, .12, { lid: .98 }); eye(.31, .08, .1, { lid: .7 });
    for (const [x, sz] of [[-.33, .1], [.31, .08]]) placed(mesh(sph(sz, 24, 16), SKINMAT, group(), null, null, [1.4, .9, .7]), onFace(x, .15), .04); }
  else if (k === 'Pinprick') { eye(-.33, .08, .125, { lid: .15, iris: .32, pupil: .3 }); eye(.31, .08, .11, { lid: .18, iris: .32, pupil: .3 }); }
  else if (k === 'Popped Out') { eye(-.33, .08, .125, { popped: true }); poppedEye(-.33, .08, .125); eye(.31, .06, .105, { lid: .3, look: [.4, 0] }); }
  else if (k === 'Cyborg Eye') { cyborgEye(-.33, .08, .12); eye(.31, .06, .105, { lid: .3 }); }
  else if (k === 'Missing Right Eye') { eye(-.33, .08, .12, { hollow: true }); socketScar(-.33, .08, .12); eye(.31, .06, .105, { lid: .32 }); }
  else if (k === 'Missing Left Eye') { eye(-.33, .08, .125, { lid: .38 }); eye(.31, .08, .1, { hollow: true }); socketScar(.31, .08, .1); }
  else if (k === 'Hollow Sockets') { eye(-.33, .08, .12, { hollow: true }); eye(.31, .08, .1, { hollow: true }); }
  else { eye(-.33, .08, .11, { lid: .3 }); eye(.31, .08, .1, { lid: .3 }); }   // glowing
}
buildEyes();

function foreheadRolls() {
  if (FULLFACE || A['Hair'] === 'Backwards Cap') return;
  const m = clay(shade(SKIN, .82), { bump: 1.4 });
  for (let i = 0; i < 4; i++) {
    const y = .4 + i * .075, w = .28 - i * .03 + rnd() * .05, pts = [];
    for (let k = 0; k <= 6; k++) { const x = -w + 2 * w * k / 6, at = onFace(x + .02, y + .02 * Math.sin(k * 1.3 + i) - .03 * (x * x / (w * w))); pts.push(at.p.addScaledVector(at.n, .008)); }
    tube(pts, .014 + rnd() * .006, m, head);
  }
}
foreheadRolls();
function buildBrows() {
  const k = A['Brows']; if (FULLFACE || k === 'None') return;
  const m = clay(A['Hair Color'] === 'Blood-Matted' ? HAIR : HAIR, { bump: 2.4 });
  for (const [x0, sgn] of [[-.33, -1], [.31, 1]]) {
    const pts = [-.16, -.05, .06, .16].map((dx, i) => { const a = onFace(x0 + dx, .3 + (i === 1 || i === 2 ? .035 : 0) + (sgn < 0 && i === 0 ? -.03 : 0)); return a.p.addScaledVector(a.n, .02); });
    if (k === 'Scarred' && sgn < 0) {
      tube(pts.slice(0, 2), .035, m, head); tube(pts.slice(2), .035, m, head);
      const s0 = onFace(x0 - .02, .42), s1 = onFace(x0 + .06, .14);
      tube([s0.p.addScaledVector(s0.n, .01), onFace(x0 + .02, .3).p.addScaledVector(V(0, 0, 1), .03), s1.p.addScaledVector(s1.n, .01)], .018, clay('#d98a8a', { rough: .5 }), head);
    } else tube(pts, .035, m, head).scale.set(1, 1, 1);
  }
}
buildBrows();

const NOSE = group(); head.add(NOSE);
function buildNose() {
  if (MASKED) return;
  const k = A['Nose'], at = onFace(.02, -.17), g = placed(group(), at, 0, NOSE); g.scale.setScalar(1.5);
  const nost = clay('#2a1414', { rough: .9 });
  const bridge = onFace(0, .02);
  if (k === 'Missing') {
    mesh(sph(.15, 32, 20), clay(shade(SKIN, .7), { rough: .5 }), g, [0, -.01, .0], null, [1, 1.15, .25]);
    mesh(sph(.12, 32, 20), new THREE.MeshStandardMaterial({ color: '#1a0a0a', roughness: 1 }), g, [0, -.01, .02], null, [.8, 1.05, .25]);
    mesh(new THREE.BoxGeometry(.025, .2, .04), clay(shade(SKIN, .6)), g, [0, -.02, .03]);
    mesh(new THREE.TorusGeometry(.13, .018, 10, 40), clay('#a0453a', { rough: .45 }), g, [0, -.01, .02], null, [1, 1.15, 1]);
    return;
  }
  // bridge running down from between the eyes
  if (k === 'Smashed Flat') {
    mesh(sph(.2, 32, 24), SKINMAT, g, [.03, 0, .06], [0, 0, .35], [1.15, .6, .5]);
    for (const x of [-.07, .09]) mesh(sph(.045), nost, g, [x, -.09, .11], null, [1.3, .6, .6]);
  } else if (k === 'Split Nostril') {
    mesh(sph(.12, 32, 24), SKINMAT, g, [-.06, 0, .12]); mesh(sph(.11, 32, 24), SKINMAT, g, [.07, -.01, .11]);
    mesh(new THREE.CapsuleGeometry(.02, .12, 6, 10), clay('#8e1a1a', { rough: .4 }), g, [0, -.02, .17]);
    for (const x of [-.08, .08]) mesh(sph(.04), nost, g, [x, -.09, .13]);
  } else {   // Bulbous
    mesh(sph(.17, 40, 30), SKINMAT, g, [0, -.02, .14], null, [1, .95, .95]);
    for (const x of [-.13, .13]) mesh(sph(.08), SKINMAT, g, [x, -.07, .09]);
    for (const x of [-.06, .06]) mesh(sph(.04), nost, g, [x, -.15, .14], null, [1.2, .7, .8]);
    mesh(sph(.03), clay('#c96b5a'), g, [.04, .04, .3]);   // shiny red tip
  }
}
buildNose();

function teeth(g, n, w, y0, gaps, up = 1) {
  const tm = clay('#e2cd6a', { rough: .9, bump: .9 }), rot = clay('#9a7a3a', { rough: .9, bump: .9 });
  for (let i = 0; i < n; i++) {
    if (gaps.includes(i)) continue;
    const x = -w / 2 + (i + .5) * w / n, h = .022 + rnd() * .02;   // short, chunky clay teeth
    mesh(new THREE.CapsuleGeometry(.03, h, 4, 8), rnd() < .2 ? rot : tm, g, [x, y0 + up * (h / 2), .03 - Math.abs(x) * .25], [0, 0, (rnd() - .5) * .35], [1.2, 1, .8]);
  }
}
function buildMouth() {
  if (MASKED || BANDANA) return;
  const k = A['Mouth'], at = onFace(.02, -.52), g = placed(group(), at, 0); g.scale.setScalar(1.65);
  const cav = new THREE.MeshStandardMaterial({ color: '#2a0808', roughness: .9 }), lipM = clay('#' + new THREE.Color(SKIN).lerp(new THREE.Color('#a8463e'), .3).multiplyScalar(.85).getHexString(), { rough: .55, bump: .8 });
  const gum = clay('#b84a4a', { rough: .4 });
  const lip = (pts, r) => {      // fat, rounded lips that taper into creased corners
    const curve = new THREE.CatmullRomCurve3(pts.map(([x, y]) => V(x, y, .02 - Math.abs(x) * .25)));
    const geo = new THREE.TubeGeometry(curve, 48, r * 1.05, 14, false), pp = geo.attributes.position, c = V(0, 0, 0), q = V(0, 0, 0);
    for (let i = 0; i <= 48; i++) { const t = i / 48, k = .35 + .65 * Math.sin(Math.PI * t); curve.getPointAt(t, c);
      for (let j = 0; j <= 14; j++) { const vi = i * 15 + j; q.fromBufferAttribute(pp, vi).sub(c).multiplyScalar(k).add(c); pp.setXYZ(vi, q.x, q.y, q.z); } }
    geo.computeVertexNormals(); const m = mesh(geo, lipM, g);
    for (const e of [pts[0], pts[pts.length - 1]]) mesh(sph(r * .9, 12, 8), SKINMAT, g, [e[0] * 1.04, e[1], .0 - Math.abs(e[0]) * .25], null, [1, 1.3, .6]);   // corner creases
    return m;
  };
  if (k === 'Slack Jaw') {
    mesh(sph(.16, 32, 24), cav, g, [0, -.05, -.02], null, [1.2, 1, .3]);
    mesh(sph(.08, 24, 16), clay('#c45a5a', { rough: .35 }), g, [.02, -.12, .02], null, [1.2, .6, .6]);
    teeth(g, 6, .26, -.18, [1, 4], 1);
    lip([[-.2, -.02], [-.1, .06], [.05, .07], [.2, .0]], .035); lip([[-.2, -.04], [-.1, -.2], [.06, -.22], [.2, -.06]], .045);
  } else if (k === 'Lipless') {
    mesh(sph(.16, 32, 24), cav, g, [0, -.01, -.02], null, [1.25, .55, .3]);
    mesh(new THREE.CapsuleGeometry(.03, .34, 6, 12), gum, g, [0, .07, .0], [0, 0, Math.PI / 2]);
    mesh(new THREE.CapsuleGeometry(.03, .32, 6, 12), gum, g, [0, -.1, .0], [0, 0, Math.PI / 2]);
    teeth(g, 9, .34, .04, [6], -1); teeth(g, 9, .32, -.07, [2], 1);
  } else if (k === 'Stitched Shut') {
    lip([[-.2, 0], [-.07, .03], [.08, .025], [.2, -.01]], .04); lip([[-.2, -.02], [-.07, -.06], [.08, -.06], [.2, -.03]], .045);
    for (let i = 0; i < 5; i++) { const x = -.14 + i * .07; tube([V(x - .025, .06, .05), V(x + .025, -.08, .05)], .009, clay('#1a1a1a'), g); tube([V(x + .025, .06, .05), V(x - .025, -.08, .05)], .009, clay('#1a1a1a'), g); }
  } else if (k === 'Snarl') {
    mesh(sph(.16, 32, 24), cav, g, [0, -.01, -.02], null, [1.2, .55, .3]);
    mesh(new THREE.CapsuleGeometry(.025, .2, 6, 12), gum, g, [-.06, .07, .0], [0, 0, Math.PI / 2 - .2]);
    teeth(g, 7, .3, .06, [2], -1); teeth(g, 7, .28, -.07, [5], 1);
    lip([[-.22, .0], [-.12, .13], [0, .1], [.2, .02]], .04); lip([[-.2, -.04], [-.05, -.12], [.1, -.11], [.2, -.03]], .045);
  } else {   // Crooked Grin
    g.rotation.z += .12;
    mesh(sph(.16, 32, 24), cav, g, [0, -.01, -.02], null, [1.25, .45, .3]);
    teeth(g, 8, .3, .05, [2, 5], -1); teeth(g, 7, .26, -.06, [3], 1);
    lip([[-.22, -.02], [-.1, .06], [.06, .07], [.22, .04]], .035); lip([[-.22, -.04], [-.08, -.1], [.08, -.1], [.22, .0]], .05);
  }
}
buildMouth();

// ------------------------------------------------------------------ skin details
function buildDetail() {
  if (FULLFACE) return;
  const k = A['Skin Detail'];
  if (k === 'Wart') { const at = MASKED || BANDANA ? onSkull(dir(-.7, .5, -.2)) : onFace(.25, -.25);
    const w = placed(mesh(sph(.05, 20, 14), clay(shade(SKIN, .8), { bump: 3 }), group()), at, .02);
    tube([V(0, 0, .04), V(.02, .02, .1)], .004, clay('#1a1a1a'), w); tube([V(.01, 0, .04), V(-.02, .03, .09)], .004, clay('#1a1a1a'), w); }
  if (k === 'Veins') for (let i = 0; i < 3; i++) {
    const pts = []; let d = dir(-.7 + rnd() * .3, .3 + rnd() * .3, -.1 + rnd() * .3);
    for (let j = 0; j < 7; j++) { const at = onSkull(d); pts.push(at.p.addScaledVector(at.n, .008)); d = d.clone().add(V(.04 + rnd() * .06, .06 + (rnd() - .5) * .1, (rnd() - .5) * .08)).normalize(); }
    tube(pts, .016, clay('#6b78b0', { rough: .5 }), head);
  }
  if (k === 'Boils') for (let i = 0; i < 5; i++) { const at = onSkull(dir(-.6 + rnd() * .9, .2 + rnd() * .6, -.3 + rnd() * .7)), r = .04 + rnd() * .04;
    const b = placed(mesh(sph(r, 20, 14), clay('#c0504a', { rough: .4 }), group()), at, 0); b.scale.z = .45;
    mesh(sph(r * .45, 12, 10), clay('#e8d36a', { rough: .3 }), b, [0, 0, r * .8]); }
  if (k === 'Stitches') {
    const pts = [], d0 = dir(-.5, .7, .1);
    for (let j = 0; j < 9; j++) { const at = onSkull(d0.clone().add(V(j * .08, -j * .05, -j * .06)).normalize()); pts.push(at); }
    tube(pts.map(a => a.p.clone().addScaledVector(a.n, .005)), .02, clay('#b85a5a', { rough: .5 }), head);
    for (let j = 1; j < 8; j += 2) { const a = pts[j], t = pts[j + 1].p.clone().sub(pts[j - 1].p).normalize(), b = t.clone().cross(a.n).normalize();
      tube([a.p.clone().addScaledVector(b, .06).addScaledVector(a.n, .01), a.p.clone().addScaledVector(a.n, .03), a.p.clone().addScaledVector(b, -.06).addScaledVector(a.n, .01)], .009, clay('#1a1a1a'), head); }
  }
  if (k === 'Rusty Nails') {   // bent, rusty nails and screws hammered unevenly into the skull, blood weeping round each
    const NM = clay('#fff', { map: rustTex(), metal: .15, rough: .75, bump: .8 }), BL = clay('#7a0b0b', { rough: .3 });
    for (let i = 0; i < 26; i++) { const d = dir(-.95 + rnd() * 1.9, -.1 + rnd() * 1.1, -.7 + rnd() * 1.2); if (d.z > .55 && d.y < .45) continue;   // keep the face clear
      const at2 = onSkull(d), L = .25 + rnd() * .35, g = placed(group(), at2, 0); g.rotation.x += (rnd() - .5) * .7; g.rotation.y += (rnd() - .5) * .7;
      mesh(new THREE.CylinderGeometry(.018, .022, L, 8), NM, g, [0, 0, L / 2 - .05], [Math.PI / 2, 0, 0]);
      if (rnd() < .3) { const b = mesh(new THREE.CylinderGeometry(.018, .018, .15, 8), NM, g, [.05, 0, L - .03], [0, 0, Math.PI / 2 - .4]); }   // bent over
      else mesh(new THREE.CylinderGeometry(.055, .055, .02, 14), NM, g, [0, 0, L - .05], [Math.PI / 2, 0, 0]);
      mesh(sph(.05, 10, 8), BL, g, [0, 0, .0], null, [1, 1, .3]);
      if (rnd() < .5) { const s2 = placed(group(), at2, 0); tube([V(0, 0, .01), V(0, -.12 - rnd() * .15, .01)], .016, BL, s2); } }
  }
  if (k === 'Burn Scar') for (let i = 0; i < 9; i++) { const at = MASKED || BANDANA ? onSkull(dir(-.8 + rnd() * .2, .1 + rnd() * .3, rnd() * .3)) : onSkull(dir(-.65 + rnd() * .25, -.1 + rnd() * .35, .55 + rnd() * .2));
    placed(mesh(sph(.06 + rnd() * .05, 20, 14), clay(i % 2 ? '#c46a6a' : '#e09a8a', { rough: .3, bump: 2 }), group(), null, null, [1, 1, .3]), at, 0); }
}
buildDetail();

// ------------------------------------------------------------------ hair
function buildHair() {
  if (MSTYLE === 'sack') return;
  const k = A['Hair'], m = clay(HAIR, { rough: A['Hair Color'] === 'Blood-Matted' ? .35 : .7, bump: 2 });
  if (k === 'Patchy Tufts') for (let i = 0; i < 5; i++) {
    const at = onSkull(dir(-.7 + rnd() * 1.3, .55 + rnd() * .4, -.6 + rnd() * .8)), t = placed(group(), at, 0);
    for (let j = 0; j < 14; j++) { const h = .12 + rnd() * .16, a = rnd() * 6.28, lean = .3 + rnd() * .5, x0 = (rnd() - .5) * .1, y0 = (rnd() - .5) * .1;
      tube([V(x0, y0, -.01), V(x0 + Math.cos(a) * h * lean * .4, y0 + Math.sin(a) * h * lean * .4, h * .55), V(x0 + Math.cos(a) * h * lean, y0 + Math.sin(a) * h * lean - .02, h)], .011, m, t); }
  }
  if (k === 'Greasy Comb-over') for (let i = 0; i < 6; i++) {
    const pts = []; for (let j = 0; j <= 10; j++) { const t = j / 10;
      const at = onSkull(dir(-.95 + t * 1.6, .25 + Math.sin(t * Math.PI) * .7 + i * .03, .25 - i * .1 + t * .1)); pts.push(at.p.addScaledVector(at.n, .015)); }
    tube(pts, .028, clay(HAIR, { rough: .3, bump: .8 }), head).scale.set(1, 1, 1);
  }
  if (k === 'Backwards Cap') {
    const cap = pick(['#2f4f3a', '#7a2f2a', '#c9b27a', '#2a3550', '#3a3a3c']), cm = clay(cap, { bump: 1.8, rough: .85 });
    const AX = dir(0, .9, -.32), TMAX = 1.22, Q = new THREE.Quaternion().setFromUnitVectors(V(0, 1, 0), AX);
    const capR = d => {           // fabric over the skull: follows the lumps loosely, never into the creases
      let r = 0; const t1 = d.clone().cross(V(.3, .1, .9)).normalize(), t2 = d.clone().cross(t1).normalize();
      for (const [a, b] of [[0, 0], [.14, 0], [-.14, 0], [0, .14], [0, -.14]]) r = Math.max(r, headPoint(d.clone().addScaledVector(t1, a).addScaledVector(t2, b).normalize()).length());
      return r + .07;
    };
    const capPoint = (theta, phi, extra = 0) => { const d = V(Math.sin(theta) * Math.cos(phi), Math.cos(theta), Math.sin(theta) * Math.sin(phi)).applyQuaternion(Q);
      const hp = headPoint(d), dirP = hp.clone().normalize(); return dirP.multiplyScalar(capR(d) + extra + .05 * Math.cos(theta / TMAX * Math.PI / 2)); };
    // crown
    const NT = 36, NP = 96, pos = [], idx = [];
    for (let i = 0; i <= NT; i++) for (let j = 0; j <= NP; j++) { const p = capPoint(i / NT * TMAX, j / NP * Math.PI * 2); pos.push(p.x, p.y, p.z); }
    for (let i = 0; i < NT; i++) for (let j = 0; j < NP; j++) { const a = i * (NP + 1) + j, b = a + 1, c = a + NP + 1, d = c + 1; idx.push(a, b, c, b, d, c); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
    const uv = []; for (let i = 0; i <= NT; i++) for (let j = 0; j <= NP; j++) uv.push(j / NP * 3, i / NT); g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
    mesh(g, cm, head);
    // sweatband edge, six panel seams with stitching, eyelets, top button
    const dk = clay(shade(cap, .65), { bump: 1 });
    tube(Array.from({ length: 97 }, (_, j) => capPoint(TMAX, j / 96 * Math.PI * 2, .01)), .045, cm, head, true, 200);
    for (let k = 0; k < 6; k++) { const phi = k / 6 * Math.PI * 2 + Math.PI / 6;
      tube(Array.from({ length: 13 }, (_, i) => capPoint(i / 12 * TMAX, phi, .006)), .014, dk, head);
      const e = capPoint(.5, phi + .45, .0); mesh(new THREE.TorusGeometry(.03, .01, 8, 16), dk, head, e.toArray()).lookAt(e.clone().multiplyScalar(2)); }
    const top = capPoint(0, 0, .02); mesh(sph(.075, 20, 14), cm, head, top.toArray(), null, [1, .55, 1]).lookAt(top.clone().multiplyScalar(2));
    // brim sticking out over the back of the neck, curved like a worn visor
    const BP = [], BI = [], BU = [], NS = 24, NO = 8, back = Math.PI / 2 * -1 + Math.PI;   // phi of the back of the head
    const phiBack = Math.atan2(-1, 0);
    for (let i = 0; i <= NO; i++) for (let j = 0; j <= NS; j++) {
      const sx = j / NS * 2 - 1, phi = -Math.PI / 2 + sx * 1.0;  // around the back rim
      const base = capPoint(TMAX, phi, .02), out = V(base.x, 0, base.z).normalize();
      const t = i / NO, p = base.clone().addScaledVector(out, t * .72 * (1 - sx * sx * .5)).add(V(0, -t * .06 - sx * sx * t * .16, 0));
      BP.push(p.x, p.y, p.z); BU.push(j / NS, t);
    }
    for (let i = 0; i < NO; i++) for (let j = 0; j < NS; j++) { const a = i * (NS + 1) + j, b = a + 1, c = a + NS + 1, d = c + 1; BI.push(a, b, c, b, d, c); }
    const bg = new THREE.BufferGeometry(); bg.setAttribute('position', new THREE.Float32BufferAttribute(BP, 3)); bg.setAttribute('uv', new THREE.Float32BufferAttribute(BU, 2)); bg.setIndex(BI); bg.computeVertexNormals();
    mesh(bg, clay(shade(cap, .9), { bump: 1.5, side: THREE.DoubleSide }), head);
    const edge = []; for (let j = 0; j <= NS; j++) { const k = (NO * (NS + 1) + j) * 3; edge.push(V(BP[k], BP[k + 1], BP[k + 2])); }
    tube(edge, .03, clay(shade(cap, .9)), head);
    // the snapback opening sits over the forehead: skin showing through an arch, plastic strap across it
    const arch = []; for (let j = 0; j <= 16; j++) { const a = j / 16 * Math.PI; arch.push(capPoint(TMAX - Math.sin(a) * .32, Math.PI / 2 + Math.cos(a) * .3, .012)); }
    const ag = new THREE.Shape(); // skin patch made from the arch points projected onto the crown
    const patch = []; for (let j = 0; j <= 16; j++) for (let i = 0; i <= 4; i++) { const a = j / 16 * Math.PI; patch.push(capPoint(TMAX - Math.sin(a) * .32 * i / 4, Math.PI / 2 + Math.cos(a) * .3, .008)); }
    const PI2 = []; for (let j = 0; j < 16; j++) for (let i = 0; i < 4; i++) { const a = j * 5 + i, b = a + 1, c = a + 5, d = c + 1; PI2.push(a, b, c, b, d, c); }
    const pg = new THREE.BufferGeometry(); pg.setAttribute('position', new THREE.Float32BufferAttribute(patch.flatMap(p => p.toArray()), 3)); pg.setIndex(PI2); pg.computeVertexNormals();
    mesh(pg, clay(shade(SKIN, .8), { side: THREE.DoubleSide }), head);
    tube(arch, .022, cm, head);
    tube(Array.from({ length: 9 }, (_, j) => capPoint(TMAX - .06, Math.PI / 2 - .3 + j / 8 * .6, .03)), .028, clay('#1c1c1c', { rough: .4, bump: .4 }), head);
  }

}
buildHair();

// ------------------------------------------------------------------ bandana over nose and mouth
if (BANDANA) {
  // a folded triangle of soft cotton: pulled snug over the nose and mouth, the point draping down the chest,
  // corners knotted at the side of the neck (George's reference)
  const col = PAL.bandanas[A['Bandana']], cmap = tex(paisley(col), 1);
  const N = 56, M1 = 26, M2 = 24, pos = [], uv = [], idx = [], LAST = [];
  head.updateMatrixWorld(true);
  const RIGHT = V(1, 0, 0).transformDirection(head.matrixWorld).setY(0).normalize(), FWD = V(0, 0, 1).transformDirection(head.matrixWorld).setY(0).normalize();
  const PROF = [[.12, .6], [.04, .8], [-.1, 1.25], [-.4, 1.7], [-.85, 1.93], [-1.5, 2.0]];   // torso profile (body-local y, radius)
  const chestZ = yw => { const yb = yw - BODY_Y; let r = 2; for (let k = 1; k < PROF.length; k++) if (yb >= PROF[k][0]) { const [y0, r0] = PROF[k - 1], [y1, r1] = PROF[k]; r = r0 + (r1 - r0) * (yb - y0) / (y1 - y0); break; } return r * .62 - .25; };
  for (let j = 0; j <= M1; j++) for (let i = 0; i <= N; i++) {          // snug part, cast onto the face
    const v = j / M1, u = i / N * 2 - 1, phi = u * (1.9 - v * .25), y = -.02 - v * .8;
    const d = V(Math.sin(phi), 0, Math.cos(phi));
    ray.set(head.localToWorld(d.clone().multiplyScalar(3).setY(y)), d.clone().negate().transformDirection(head.matrixWorld));
    const h = ray.intersectObjects([HEADMESH, NOSE], true)[0];
    let p;
    if (h) p = head.worldToLocal(h.point.clone()).addScaledVector(d, .055 + .012 * Math.sin(v * 22 + u * 3));   // soft tension ripples
    else p = (LAST[i] ? LAST[i].clone().setY(y) : d.clone().multiplyScalar(.8).setY(y));
    LAST[i] = p.clone(); pos.push(p.x, p.y, p.z); uv.push(i / N, 1 - v * .45);
  }
  const top = head.localToWorld(LAST[N / 2].clone()), W0 = 1.15;
  const tip = V(top.x, top.y - 1.2, top.z).addScaledVector(RIGHT, .05).addScaledVector(FWD, -.3); tip.z = Math.max(tip.z, chestZ(tip.y) + .25);   // hangs nearly straight down off the chin
  for (let j = 1; j <= M2; j++) for (let i = 0; i <= N; i++) {          // the hanging point
    const t = j / M2, u = i / N * 2 - 1;
    const c = top.clone().addScaledVector(FWD, .1).lerp(tip, t);
    const f = c.addScaledVector(RIGHT, u * W0 * Math.pow(1 - t, .85) * (1 + .25 * Math.sin(t * Math.PI)));
    f.z = Math.max(f.z, chestZ(f.y) + .1 + .06 * (1 - Math.abs(u)));
    f.addScaledVector(FWD, (.035 * Math.sin(u * 7 + t * 2) + .01 * Math.sin(u * 17)) * Math.min(1, t * 3) * (1 - t * .6));   // pleats fanning to the point
    f.y -= .07 * Math.sin(Math.abs(u) * Math.PI) * t * (1 - t) * 4;     // the cloth sags between the corners
    const w = head.localToWorld(LAST[i].clone()), s0 = THREE.MathUtils.smoothstep(t, 0, .22);
    const p = head.worldToLocal(w.lerp(f, s0));
    pos.push(p.x, p.y, p.z); uv.push(i / N, .55 - t * .55);
  }
  const R = M1 + M2;
  for (let j = 0; j < R; j++) for (let i = 0; i < N; i++) { const a = j * (N + 1) + i, b = a + 1, c = a + N + 1, d = c + 1; idx.push(a, c, b, b, c, d); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx); g.computeVertexNormals();
  const BM = clay('#fff', { map: cmap, side: THREE.DoubleSide, bump: .9, rough: .95 }); BM.roughnessMap = null;   // matte cotton, no clay sheen
  mesh(g, BM, head).userData.rigid = true;
  NOSE.visible = false;   // the cloth is already shaped over it
  // knot at the side of the neck with two short tails
  const kn = onSkull(dir(-.8, -.62, -.25)); const k = placed(group(), kn, .05);
  const km = clay('#fff', { map: tex(paisley(col), 1), bump: 1.2, rough: .95 }); km.roughnessMap = null;
  mesh(sph(.15, 24, 16), km, k, null, null, [1.1, .9, .8]);
  mesh(new THREE.CapsuleGeometry(.07, .3, 6, 12), km, k, [-.12, -.18, .03], [0, 0, -.7], [1.5, 1, .45]);
  mesh(new THREE.CapsuleGeometry(.07, .24, 6, 12), km, k, [.05, -.22, .06], [0, 0, .35], [1.4, 1, .45]);
}

// ------------------------------------------------------------------ 1/1 goalie mask
// lower-face hockey mask: covers nose to chin, eyes stay visible above it, held on by rusty riveted leather straps
if (MASKED) {
  let at;
  // ---- extra mask styles (heavy-metal horror inspired, our own designs)
  const steel = (o = {}) => clay(o.c || '#aeb3b8', { metal: .12, rough: .78, bump: 1.1, ...o });
  function faceShell(FX0, FX1, FY0, FY1, off, blurR, bumpFn = () => 0, NX = 110, NY = 110) {
    const RAW = new Float32Array((NX + 1) * (NY + 1)), Z = new Float32Array(RAW.length);
    for (let j = 0; j <= NY; j++) for (let i = 0; i <= NX; i++) { const fx = FX0 + (FX1 - FX0) * i / NX, fy = FY1 - (FY1 - FY0) * j / NY;
      ray.set(V(stretchX(fx, fy), stretchY(fy), 3), V(0, 0, -1)); const h = ray.intersectObject(PROBE)[0]; RAW[j * (NX + 1) + i] = h ? h.point.z : -.3; }
    const blur = (src, r) => { const out = new Float32Array(src.length);
      for (let j = 0; j <= NY; j++) for (let i = 0; i <= NX; i++) { let s = 0, w = 0;
        for (let dj = -r; dj <= r; dj++) for (let di = -r; di <= r; di++) { const a = i + di, b = j + dj; if (a < 0 || b < 0 || a > NX || b > NY) continue; s += src[b * (NX + 1) + a]; w++; }
        out[j * (NX + 1) + i] = s / w; } return out; };
    let sm = blurR ? blur(RAW, blurR) : RAW.slice(); for (let k = 0; k < sm.length; k++) sm[k] = Math.max(sm[k], RAW[k]); if (blurR) sm = blur(sm, Math.ceil(blurR / 2));
    for (let j = 0; j <= NY; j++) for (let i = 0; i <= NX; i++) { const fx = FX0 + (FX1 - FX0) * i / NX, fy = FY1 - (FY1 - FY0) * j / NY, q = j * (NX + 1) + i;
      Z[q] = Math.max(sm[q], RAW[q] + .015) + off + bumpFn(fx, fy); }
    const look = (fx, fy) => { const u = THREE.MathUtils.clamp((fx - FX0) / (FX1 - FX0) * NX, 0, NX - 1e-4), v = THREE.MathUtils.clamp((FY1 - fy) / (FY1 - FY0) * NY, 0, NY - 1e-4);
      const i = Math.floor(u), j = Math.floor(v), a = u - i, b = v - j, z = (I, J) => Z[J * (NX + 1) + I];
      return V(stretchX(fx, fy), stretchY(fy), z(i, j) * (1 - a) * (1 - b) + z(i + 1, j) * a * (1 - b) + z(i, j + 1) * (1 - a) * b + z(i + 1, j + 1) * a * b); };
    const geo = dz => { const g = new THREE.PlaneGeometry(1, 1, NX, NY), p = g.attributes.position;
      for (let j = 0; j <= NY; j++) for (let i = 0; i <= NX; i++) { const fx = FX0 + (FX1 - FX0) * i / NX, fy = FY1 - (FY1 - FY0) * j / NY, q = j * (NX + 1) + i; p.setXYZ(q, stretchX(fx, fy), stretchY(fy), Z[q] + dz); }
      g.computeVertexNormals(); return g; };
    const S = 1024, MX = fx => (fx - FX0) / (FX1 - FX0) * S, MY = fy => (FY1 - fy) / (FY1 - FY0) * S, PX = S / (FX1 - FX0);
    return { at: look, geo, S, MX, MY, PX };
  }
  const EYEH = [[-.33, .08, .22, .17], [.31, .08, .2, .16]];
  const fullOutline = sh => { const o = []; for (let i = 0; i < 120; i++) { const t = i / 120 * Math.PI * 2, c = Math.cos(t), s = Math.sin(t);
    o.push([.8 * Math.sign(c) * Math.abs(c) ** .8 * (s < 0 ? 1 - .3 * s * s : 1), s > 0 ? -.08 + .9 * s : -.08 + .9 * s]); } return o; };
  function cutTex(sh, outline, cuts, extra) {   // alpha: white inside the outline, holes cut out
    const [c, g] = canvas(sh.S); g.fillStyle = '#000'; g.fillRect(0, 0, sh.S, sh.S); g.fillStyle = '#fff'; g.beginPath();
    outline.forEach(([u, v], i) => i ? g.lineTo(sh.MX(u), sh.MY(v)) : g.moveTo(sh.MX(u), sh.MY(v))); g.closePath(); g.fill();
    if (cuts) { g.fillStyle = '#000'; for (const [u, v, rx, ry] of cuts) { g.beginPath(); g.ellipse(sh.MX(u), sh.MY(v), rx * sh.PX, ry * sh.PX, 0, 0, 7); g.fill(); } if (extra) extra(g); }
    return tex(c, 1, false);
  }
  function paintTex(sh, base, fn) { const [c, g] = canvas(sh.S); g.fillStyle = base; g.fillRect(0, 0, sh.S, sh.S);
    for (let i = 0; i < 80; i++) { const x = rnd() * sh.S, y = rnd() * sh.S, r = 20 + rnd() * 80, gr = g.createRadialGradient(x, y, 0, x, y, r);
      gr.addColorStop(0, rnd() < .5 ? 'rgba(0,0,0,.12)' : 'rgba(255,255,255,.08)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = gr; g.fillRect(x - r, y - r, 2 * r, 2 * r); }
    fn && fn(g); return tex(c, 1); }
  function shellMeshes(sh, map, alphaT, alphaBack, o = {}) {
    const m = mesh(sh.geo(0), clay('#fff', { map, rough: o.rough ?? .85, metal: o.metal ?? 0, bump: o.bump ?? 1, side: THREE.DoubleSide, alpha: alphaT }), head); m.userData.rigid = true;
    const b = mesh(sh.geo(-.03), new THREE.MeshStandardMaterial({ color: o.inner || '#1a1310', roughness: 1, side: THREE.DoubleSide, alphaMap: alphaBack, alphaTest: .5, transparent: true }), head); b.userData.rigid = true;
    return m;
  }
  const rim = (sh, outline, r, mat, closed = true) => { const t = tube(outline.map(([u, v]) => sh.at(u, v).add(V(0, 0, -.014))), r, mat, head, closed); t.userData.rigid = true; return t; };
  const eyeRims = (sh, r, mat) => { for (const [u, v, rx, ry] of EYEH) { const pts = []; for (let i = 0; i < 40; i++) { const t = i / 40 * Math.PI * 2; pts.push([u + rx * Math.cos(t), v + ry * Math.sin(t)]); } rim(sh, pts, r, mat); } };
  const LOWER = []; { const top = fx => -.15 - .035 * Math.exp(-((Math.abs(fx) - .33) ** 2) / .02) + .27 * Math.exp(-(fx * fx) / .006) + .07 * THREE.MathUtils.smoothstep(Math.abs(fx), .5, .7);
    for (let i = 0; i <= 40; i++) { const fx = -.62 + 1.24 * i / 40; LOWER.push([fx, top(fx)]); }
    for (let i = 1; i < 40; i++) { const a = i / 40 * Math.PI, s = Math.sin(a); LOWER.push([.62 * Math.cos(a) * (1 - .22 * s * s), -.1 - .82 * Math.pow(s, .7)]); } }
  const noseBump = (h, len = .44) => (fx, fy) => { const k = THREE.MathUtils.clamp((.14 - fy) / len, 0, 1), wx = .045 + .085 * k, under = fy < .14 - len ? Math.exp(-(((fy - .14 + len) / .07) ** 2)) : 1;
    return h * Math.pow(k, 1.4) * under * Math.exp(-((fx - .01) ** 2) / (wx * wx)); };

  // burlap weave shared by the pig and patchwork masks
  const burlap = (sh, base = '#b39466') => paintTex(sh, base, g => {
    for (let y = 0; y < sh.S; y += 12) { g.fillStyle = 'rgba(55,35,18,.45)'; g.fillRect(0, y, sh.S, 4); }
    for (let x = 0; x < sh.S; x += 12) { g.fillStyle = 'rgba(55,35,18,.38)'; g.fillRect(x, 0, 4, sh.S); }
    for (let i = 0; i < 400; i++) { g.strokeStyle = `rgba(${rnd() < .5 ? '210,180,130' : '70,50,30'},.5)`; g.lineWidth = 1.5; g.beginPath(); const x = rnd() * sh.S, y = rnd() * sh.S; g.moveTo(x, y); g.lineTo(x + rnd() * 20 - 10, y + rnd() * 20 - 10); g.stroke(); }
    for (let i = 0; i < 7; i++) { const x = rnd() * sh.S, y = rnd() * sh.S, w = 60 + rnd() * 90, h = 50 + rnd() * 80; g.fillStyle = rnd() < .5 ? 'rgba(90,60,35,.45)' : 'rgba(200,170,120,.35)'; g.fillRect(x, y, w, h);   // sewn-on patches
      g.strokeStyle = 'rgba(40,25,15,.8)'; g.lineWidth = 3; g.setLineDash([8, 7]); g.strokeRect(x + 5, y + 5, w - 10, h - 10); g.setLineDash([]); }
    for (let i = 0; i < 4; i++) { const x = rnd() * sh.S, y = rnd() * sh.S * .7; g.fillStyle = 'rgba(110,14,14,.55)'; g.beginPath(); g.ellipse(x, y, 30 + rnd() * 30, 20, rnd() * 3, 0, 7); g.fill(); }
  });
  const fray = (sh, outline, n, mat) => { for (let i = 0; i < n; i++) { const [u, v] = outline[Math.floor(rnd() * outline.length)], p = sh.at(u, v), d = V(u, v + .1, 0).normalize();
    tube([p, p.clone().add(d.multiplyScalar(.03 + rnd() * .05)).add(V(0, -.04 - rnd() * .05, .01))], .006 + rnd() * .005, mat, head).userData.rigid = true; } };
  const topStrap = () => {     // leather strap with a buckle over the crown, ear to ear
    const pts = []; for (let i = 0; i <= 60; i++) { const a = -1.25 + 2.5 * i / 60, d = V(Math.sin(a), Math.cos(a), -.15).normalize(); ray.set(d.clone().multiplyScalar(4), d.clone().negate());
      const h = ray.intersectObject(PROBE)[0]; if (h) pts.push(h.point.clone().addScaledVector(h.face.normal, .025)); }
    const LM = clay('#6e4428', { rough: .9, bump: 1.6 }); const c = new THREE.CatmullRomCurve3(pts);
    { const geo = new THREE.TubeGeometry(c, 80, .075, 12, false); geo.scale(1, 1, 1); const m = mesh(geo, LM, head); m.scale.set(1, 1, 1); m.userData.rigid = true;
      const pp = geo.attributes.position, cp = V(0, 0, 0), q = V(0, 0, 0), n = V(0, 0, 0);   // flatten the tube into a strap lying on the skull
      for (let i = 0; i <= 80; i++) { c.getPointAt(i / 80, cp); n.copy(cp).normalize(); for (let j = 0; j <= 12; j++) { const vi = i * 13 + j; q.fromBufferAttribute(pp, vi).sub(cp); const k = q.dot(n); q.addScaledVector(n, -k * .7).add(cp); pp.setXYZ(vi, q.x, q.y, q.z); } } geo.computeVertexNormals(); }
    const b = c.getPointAt(.62), T = c.getTangentAt(.62), bk = group(); bk.position.copy(b); bk.lookAt(head.localToWorld(b.clone().add(T))); head.add(bk);
    const RM = clay('#8d8a84', { metal: .35, rough: .65 }); for (const [x, y, w, h] of [[0, -.1, .2, .025], [0, .1, .2, .025], [-.1, 0, .025, .2], [.1, 0, .025, .2]]) mesh(new THREE.BoxGeometry(w, h, .04), RM, bk, [x, y, .0]);
    mesh(new THREE.BoxGeometry(.18, .025, .025), RM, bk, [0, 0, .03], [0, 0, 0]).userData.rigid = true;
  };
  if (MSTYLE === 'pig') {          // stitched burlap pig face: snout, floppy ears, blocky grin
    const sh = faceShell(-.9, .9, -1.05, .95, .06, 3), OUTL = fullOutline();
    const PE = [[-.31, .1, .11, .1], [.3, .1, .1, .09]];
    const MOUTH = g => { g.beginPath(); g.moveTo(sh.MX(-.36), sh.MY(-.5)); g.quadraticCurveTo(sh.MX(0), sh.MY(-.72), sh.MX(.38), sh.MY(-.48)); g.quadraticCurveTo(sh.MX(0), sh.MY(-.95), sh.MX(-.36), sh.MY(-.5)); g.fill(); };
    shellMeshes(sh, burlap(sh), cutTex(sh, OUTL, PE, MOUTH), cutTex(sh, OUTL), { rough: 1, bump: 2.4, inner: '#1a0c0a' });
    const bm = clay('#a88a5c', { rough: 1, bump: 2.6 }); rim(sh, OUTL, .025, bm); fray(sh, OUTL, 70, clay('#c2a472', { bump: .5 }));
    for (const [u, v, rx, ry] of PE) { const pts = []; for (let i = 0; i < 30; i++) { const t = i / 30 * Math.PI * 2; pts.push([u + rx * Math.cos(t), v + ry * Math.sin(t)]); } rim(sh, pts, .022, clay('#5a3a24', { rough: 1, bump: 2 })); }
    const sn = sh.at(.03, -.3), sg = group(); sg.position.copy(sn); head.add(sg);
    const pink = clay('#c98f86', { rough: .8, bump: 1.4 }); mesh(new THREE.CylinderGeometry(.2, .23, .22, 30), pink, sg, [0, 0, .08], [Math.PI / 2, 0, 0], [1.15, 1, .85]).userData.rigid = true;
    for (const x of [-.07, .08]) mesh(sph(.05, 16, 12), clay('#3a1a16'), sg, [x, -.01, .19], null, [.8, 1.2, .5]).userData.rigid = true;
    const tm = clay('#c9ad78', { rough: 1, bump: 2 }); for (let i = 0; i < 8; i++) { const fx = -.27 + .54 * i / 7, fy = -.6 - .04 * (1 - (fx / .3) ** 2), p = sh.at(fx, fy); mesh(new THREE.BoxGeometry(.06, .08, .05), tm, head, [p.x, p.y + .03, p.z - .02], [0, 0, (rnd() - .5) * .3]).userData.rigid = true;
      const q = sh.at(fx * .8, fy - .12); mesh(new THREE.BoxGeometry(.055, .065, .05), tm, head, [q.x, q.y, q.z - .03], [0, 0, (rnd() - .5) * .3]).userData.rigid = true; }
    for (const sx of [-1, 1]) { const e = sh.at(sx * .62, .62), eg = group(); eg.position.copy(e); eg.rotation.set(-.5, sx * .5, sx * -.7); head.add(eg);
      const shp = new THREE.Shape(); shp.moveTo(-.2, 0); shp.quadraticCurveTo(-.15, .35, .05, .45); shp.quadraticCurveTo(.25, .3, .2, 0); shp.closePath();
      mesh(new THREE.ExtrudeGeometry(shp, { depth: .03, bevelEnabled: true, bevelThickness: .02, bevelSize: .02, bevelSegments: 2 }), clay('#b39466', { rough: 1, bump: 2.4 }), eg).userData.rigid = true;
      mesh(new THREE.ExtrudeGeometry(shp, { depth: .01, bevelEnabled: false }), clay('#c98f86', { rough: .9 }), eg, [0, .04, .045], null, [.65, .7, 1]).userData.rigid = true; }
    topStrap();
  }
  if (MSTYLE === 'patch') {        // burlap face patched with riveted scrap-metal plates, goggle eyes, wire-stitched mouth
    const sh = faceShell(-.9, .9, -1.05, .95, .06, 3, noseBump(.12, .38)), OUTL = fullOutline();
    const GE = [[-.31, .1, .13, .12], [.3, .1, .12, .11]];
    shellMeshes(sh, burlap(sh, '#a98d62'), cutTex(sh, OUTL, GE), cutTex(sh, OUTL), { rough: 1, bump: 2.4 });
    rim(sh, OUTL, .025, clay('#9a7e56', { rough: 1, bump: 2 }));
    const MT = paintTex(sh, '#7b7a76', g => { for (let i = 0; i < 260; i++) { g.fillStyle = `rgba(${115 + rnd() * 40 | 0},${55 + rnd() * 25 | 0},20,${.3 + rnd() * .5})`; g.beginPath(); g.arc(rnd() * sh.S, rnd() * sh.S, 3 + rnd() * 20, 0, 7); g.fill(); }
      g.fillStyle = 'rgba(220,220,210,.25)'; for (let i = 0; i < 30; i++) { g.fillRect(rnd() * sh.S, rnd() * sh.S, 40 + rnd() * 60, 3); } });
    const PLATES = [[[-.55, .85], [.1, .9], [.16, .45], [-.05, .3], [-.62, .4]], [[.2, .88], [.62, .7], [.72, .35], [.48, .22], [.18, .4]], [[.45, -.05], [.74, -.1], [.68, -.6], [.48, -.5]], [[-.8, -.1], [-.5, -.08], [-.46, -.4], [-.7, -.5]]];
    const pm = clay('#fff', { map: MT, metal: .35, rough: .62, bump: 1.4, side: THREE.DoubleSide });
    for (const P of PLATES) { const a = cutTex(sh, P, GE); const m = mesh(sh.geo(.025), pm.clone(), head); m.material.alphaMap = a; m.material.transparent = true; m.material.alphaTest = .5; m.userData.rigid = true;
      rim(sh, P.concat([P[0]]).map(([u, v]) => [u, v]), .014, clay('#5c5a56', { metal: .35, rough: .6 })).position.z += .035;
      for (const [u, v] of P) { const q = sh.at(u * .9 + .0, v * .92 + .02); mesh(sph(.025, 12, 8), clay('#9a9890', { metal: .4, rough: .5 }), head, [q.x, q.y, q.z + .05], null, [1, 1, .6]).userData.rigid = true; } }
    const GM = clay('#8f8d88', { metal: .45, rough: .5 });
    for (const [u, v, rx, ry] of GE) { const p = sh.at(u, v), g = group(); g.position.set(p.x, p.y, p.z + .04); head.add(g);
      mesh(new THREE.TorusGeometry(rx * 1.05, .04, 14, 40), GM, g, null, null, [1, ry / rx, 1]).userData.rigid = true;
      mesh(new THREE.TorusGeometry(rx * .82, .02, 10, 40), GM, g, [0, 0, .03], null, [1, ry / rx, 1]).userData.rigid = true;
      const lens = mesh(new THREE.CircleGeometry(rx * .8, 30), new THREE.MeshStandardMaterial({ color: '#b01818', roughness: .2, metalness: .1, transparent: true, opacity: .55 }), g, [0, 0, .02], null, [1, ry / rx, 1]); lens.userData.rigid = true;
      for (let i = 0; i < 6; i++) { const a = i / 6 * Math.PI * 2; mesh(sph(.018, 10, 8), GM, g, [Math.cos(a) * rx * 1.05, Math.sin(a) * ry * 1.05, .04]).userData.rigid = true; } }
    for (const [u, v] of [[-.55, .55], [.52, .5]]) { const p = sh.at(u, v); const g = group(); g.position.set(p.x, p.y, p.z + .05); head.add(g);     // small sensor ports
      mesh(new THREE.TorusGeometry(.06, .022, 10, 24), GM, g).userData.rigid = true; mesh(new THREE.CircleGeometry(.045, 20), clay('#2a0c0c'), g, [0, 0, .005]).userData.rigid = true; }
    const mp = []; for (let i = 0; i <= 24; i++) { const fx = -.4 + .8 * i / 24; mp.push(sh.at(fx, -.58 + .04 * (fx / .4) ** 2).add(V(0, 0, .01))); }
    tube(mp, .025, clay('#1a0e0a'), head).userData.rigid = true;
    const wire = clay('#a7a49c', { metal: .5, rough: .4 }); for (let i = 0; i < 12; i++) { const fx = -.37 + .74 * i / 11, a = sh.at(fx - .03, -.5 + .04 * (fx / .4) ** 2), b = sh.at(fx + .03, -.67 + .04 * (fx / .4) ** 2);
      tube([a.add(V(0, 0, .01)), a.clone().lerp(b, .5).add(V(0, 0, .04)), b.add(V(0, 0, .01))], .011, wire, head).userData.rigid = true; }
    const lace = clay('#c8642a', { rough: .8 }); for (let i = 0; i < 5; i++) { const a = sh.at(-.72, -.05 - i * .1), b = sh.at(-.6, -.1 - i * .1); tube([a.add(V(0, 0, .01)), b.add(V(0, 0, .01))], .014, lace, head).userData.rigid = true; }
    topStrap();
  }
  if (MSTYLE === 'zip') {          // stitched black leather face, zipped mouth, laced seams
    const sh = faceShell(-.9, .9, -1.05, .95, .05, 3, noseBump(.18, .4)), OUTL = fullOutline();
    const map = paintTex(sh, '#2a211d', g => { g.strokeStyle = 'rgba(120,100,85,.35)'; g.lineWidth = 3; for (let i = 0; i < 120; i++) { const x = rnd() * sh.S, y = rnd() * sh.S; g.beginPath(); g.moveTo(x, y); g.lineTo(x + rnd() * 30 - 15, y + rnd() * 30 - 15); g.stroke(); }
      g.fillStyle = 'rgba(120,12,12,.7)'; for (let i = 0; i < 4; i++) { const x = sh.MX(-.5 + rnd()), y = sh.MY(-.2 - rnd() * .5); g.beginPath(); g.roundRect(x, y, 8, 60 + rnd() * 120, 4); g.fill(); } });
    shellMeshes(sh, map, cutTex(sh, OUTL, EYEH.concat([[-.05, -.3, .022, .016], [.07, -.3, .022, .016]])), cutTex(sh, OUTL), { rough: .55, bump: 1.4 });
    rim(sh, OUTL, .02, clay('#1d1714', { rough: .6 })); eyeRims(sh, .022, clay('#1d1714', { rough: .6 }));
    const thread = clay('#c9b89a', { rough: .9, bump: .3 });
    for (const [x0, y0, x1, y1] of [[0, .9, .01, .2], [-.75, .2, -.48, .02], [.75, .2, .48, .02], [-.6, -.75, -.2, -.6], [.6, -.75, .2, -.6]]) for (let i = 0; i <= 8; i++) {
      const fx = x0 + (x1 - x0) * i / 8, fy = y0 + (y1 - y0) * i / 8, p = sh.at(fx, fy).add(V(0, 0, .006)), d = V(y1 - y0, -(x1 - x0), 0).normalize().multiplyScalar(.035);
      tube([p.clone().add(d), p.clone().sub(d)], .008, thread, head).userData.rigid = true; }
    // zipper across the mouth: tape, interlocking teeth and a pull tab
    const zm = steel({ c: '#a7a9a4' }); const zp = []; for (let i = 0; i <= 30; i++) { const fx = -.36 + .72 * i / 30; zp.push(sh.at(fx, -.58 + .06 * (fx / .36) ** 2).add(V(0, 0, .01))); }
    tube(zp, .03, clay('#151210', { rough: .7 }), head).userData.rigid = true;
    zp.forEach((p, i) => { const b = mesh(new THREE.BoxGeometry(.022, .045, .02), zm, head, [p.x, p.y + (i % 2 ? .015 : -.015), p.z + .025]); b.userData.rigid = true; });
    const sl = zp[22]; mesh(new THREE.BoxGeometry(.07, .08, .04), zm, head, [sl.x, sl.y, sl.z + .045]).userData.rigid = true;
    mesh(new THREE.BoxGeometry(.04, .14, .015), zm, head, [sl.x + .01, sl.y - .1, sl.z + .06], [.3, 0, .15]).userData.rigid = true;
  }
  if (MSTYLE === 'clown') {        // cracked white latex clown face, red bulb nose, painted grin
    const sh = faceShell(-.9, .9, -1.05, .95, .05, 3), OUTL = fullOutline();
    const MOUTH = g => { g.beginPath(); g.ellipse(sh.MX(.01), sh.MY(-.56), .3 * sh.PX, .06 * sh.PX, 0, 0, 7); g.fill(); };
    const map = paintTex(sh, '#ebe5d6', g => {
      g.fillStyle = '#16121a'; for (const [u, v, rx, ry] of EYEH) { g.beginPath(); g.moveTo(sh.MX(u), sh.MY(v + ry + .2)); g.lineTo(sh.MX(u + rx + .07), sh.MY(v)); g.lineTo(sh.MX(u), sh.MY(v - ry - .22)); g.lineTo(sh.MX(u - rx - .07), sh.MY(v)); g.closePath(); g.fill(); }
      g.fillStyle = '#b3141e'; g.beginPath(); g.moveTo(sh.MX(-.5), sh.MY(-.42)); g.quadraticCurveTo(sh.MX(0), sh.MY(-.95), sh.MX(.5), sh.MY(-.42)); g.quadraticCurveTo(sh.MX(0), sh.MY(-.68), sh.MX(-.5), sh.MY(-.42)); g.fill();
      g.strokeStyle = 'rgba(60,50,40,.7)'; g.lineWidth = 3; for (let i = 0; i < 10; i++) { let x = rnd() * sh.S, y = rnd() * sh.S; g.beginPath(); g.moveTo(x, y); for (let k = 0; k < 6; k++) { x += rnd() * 60 - 30; y += rnd() * 60 - 30; g.lineTo(x, y); } g.stroke(); }
      g.fillStyle = 'rgba(130,14,14,.8)'; for (let i = 0; i < 5; i++) { g.beginPath(); g.roundRect(sh.MX(-.4 + rnd() * .8), sh.MY(-.6), 9, 80 + rnd() * 140, 4); g.fill(); } });
    shellMeshes(sh, map, cutTex(sh, OUTL, EYEH, MOUTH), cutTex(sh, OUTL), { rough: .6, bump: .8 });
    rim(sh, OUTL, .02, clay('#ddd6c6', { rough: .7 }));
    const n = sh.at(.02, -.2); mesh(sph(.17, 40, 30), clay('#c8101c', { rough: .45, bump: .4 }), head, [n.x, n.y, n.z + .1]).userData.rigid = true;
    const tm = clay('#e6d58a', { rough: .85 }); for (let i = 0; i < 9; i++) { const fx = -.24 + .48 * i / 8, p = sh.at(fx, -.53); mesh(new THREE.BoxGeometry(.045, .06, .03), tm, head, [p.x, p.y, p.z - .02]).userData.rigid = true; }
    for (let i = 0; i < 10; i++) { const at2 = onSkull(dir(-.8 + 1.6 * rnd(), .55 + rnd() * .35, -.4 + rnd() * .6)); tube([at2.p, at2.p.clone().addScaledVector(at2.n, .35 + rnd() * .2).add(V(rnd() * .3 - .15, .1, 0))], .05, clay(i % 2 ? '#d1361e' : '#e0561e', { bump: 2 }), head); }
  }
  if (A['Mask'] === 'Killer Clown Mask') {   // crazed killer clown: slashed grin full of fangs, bloodshot paint, wild hair puffs
    const sh = faceShell(-.9, .9, -1.05, .95, .065, 3);
    const OUTL = []; for (let i = 0; i < 60; i++) { const t = i / 59, fx = -.62 + 1.24 * t; OUTL.push([fx, -.42 - .3 * Math.sin(Math.PI * t) + .08 * Math.cos(Math.PI * 2 * t)]); }
    for (let i = 59; i >= 0; i--) { const t = i / 59, fx = -.62 + 1.24 * t; OUTL.push([fx, -.42 - .08 * Math.sin(Math.PI * t)]); }
    const map = paintTex(sh, '#c8101c', g => { g.fillStyle = 'rgba(90,0,0,.6)'; for (let i = 0; i < 30; i++) { g.beginPath(); g.arc(rnd() * sh.S, rnd() * sh.S, 6 + rnd() * 20, 0, 7); g.fill(); } });
    const lip = mesh(sh.geo(.012), clay('#fff', { map, rough: .35, bump: .5, side: THREE.DoubleSide, alpha: cutTex(sh, OUTL, [[0, -.6, .5, .1]]) }), head); lip.userData.rigid = true;
    const fang = clay('#efe6c8', { rough: .5 }), FG = new THREE.ConeGeometry(.032, .12, 8);
    for (let i = 0; i < 13; i++) { const t = (i + .5) / 13, fx = -.56 + 1.12 * t, top = sh.at(fx, -.45 - .07 * Math.sin(Math.PI * t)), bot = sh.at(fx * .95, -.52 - .26 * Math.sin(Math.PI * t));
      mesh(FG, fang, head, [top.x, top.y - .05, top.z + .0], [Math.PI, 0, (rnd() - .5) * .3]).userData.rigid = true; mesh(FG, fang, head, [bot.x, bot.y + .05, bot.z - .01], [0, 0, (rnd() - .5) * .3]).userData.rigid = true; }
    const BL = clay('#7a0b0b', { rough: .3 }); for (let i = 0; i < 7; i++) { const fx = -.5 + rnd(), p = sh.at(fx, -.72 - rnd() * .1), L = .15 + rnd() * .35; tube([p.clone().add(V(0, 0, .02)), p.clone().add(V(0, -L, .03))], .025, BL, head); mesh(sph(.045, 12, 8), BL, head, [p.x, p.y - L - .02, p.z + .03]); }
    const HM = clay('#2fa83a', { bump: 2.4 }), HM2 = clay('#c8101c', { bump: 2.4 });
    for (const sx of [-1, 1]) for (let i = 0; i < 14; i++) { const at2 = onSkull(dir(sx * (.85 + rnd() * .2), .2 + rnd() * .5, -.4 + rnd() * .6)); mesh(sph(.16 + rnd() * .1, 16, 12), i % 3 ? HM : HM2, head, at2.p.clone().addScaledVector(at2.n, .12).toArray()); }
  }
  if (MSTYLE === 'nose') {         // grey latex face with a long, crooked, warty nose
    const sh = faceShell(-.9, .9, -1.05, .95, .05, 3), OUTL = fullOutline();
    const map = paintTex(sh, '#c9c2b4', g => { g.fillStyle = 'rgba(30,24,20,.85)'; g.beginPath(); g.ellipse(sh.MX(.02), sh.MY(-.58), .22 * sh.PX, .035 * sh.PX, .05, 0, 7); g.fill();
      for (const [u, v] of EYEH) { const gr = g.createRadialGradient(sh.MX(u), sh.MY(v), 30, sh.MX(u), sh.MY(v), 150); gr.addColorStop(0, 'rgba(40,30,30,.6)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = gr; g.fillRect(0, 0, sh.S, sh.S); } });
    shellMeshes(sh, map, cutTex(sh, OUTL, EYEH), cutTex(sh, OUTL), { rough: .7, bump: 1.1 });
    rim(sh, OUTL, .02, clay('#b9b2a4'));
    const base = sh.at(.02, -.08), nm = clay('#c9c2b4', { bump: 1.3 }); const pts = [base.clone().add(V(0, 0, -.05)), base.clone().add(V(.08, -.06, .35)), base.clone().add(V(.2, -.2, .7)), base.clone().add(V(.28, -.38, .95))];
    const c = new THREE.CatmullRomCurve3(pts), geo = new THREE.TubeGeometry(c, 40, 1, 16, false), pp = geo.attributes.position, cp = V(0, 0, 0), q = V(0, 0, 0);
    for (let i = 0; i <= 40; i++) { const t = i / 40, r = .13 * (1 - t) + .02; c.getPointAt(t, cp); for (let j = 0; j <= 16; j++) { const vi = i * 17 + j; q.fromBufferAttribute(pp, vi).sub(cp).normalize().multiplyScalar(r).add(cp); pp.setXYZ(vi, q.x, q.y, q.z); } }
    geo.computeVertexNormals(); mesh(geo, nm, head);
    for (const t of [.3, .55, .7]) { const p = c.getPointAt(t); mesh(sph(.03, 12, 8), nm, head, [p.x + .03, p.y + .05, p.z]); }
  }
  if (MSTYLE === 'iron') {         // riveted iron face plate with grille slots over the mouth
    const sh = faceShell(-.74, .74, -1.02, .16, .07, 6, noseBump(.3)), SLOTS = [];
    for (let i = 0; i < 7; i++) SLOTS.push([-.27 + i * .09, -.62]);
    const slots = g => { g.fillStyle = '#000'; for (const [u, v] of SLOTS) { g.beginPath(); g.roundRect(sh.MX(u) - .022 * sh.PX, sh.MY(v) - .14 * sh.PX, .044 * sh.PX, .28 * sh.PX, .02 * sh.PX); g.fill(); } };
    const map = paintTex(sh, '#6f6d68', g => { for (let i = 0; i < 160; i++) { g.fillStyle = `rgba(${120 + rnd() * 40 | 0},${55 + rnd() * 25 | 0},20,${.3 + rnd() * .5})`; g.beginPath(); g.arc(rnd() * sh.S, rnd() * sh.S, 3 + rnd() * 22, 0, 7); g.fill(); }
      g.fillStyle = 'rgba(110,10,10,.8)'; for (let i = 0; i < 4; i++) { g.beginPath(); g.roundRect(sh.MX(-.4 + rnd() * .8), sh.MY(-.75), 9, 60 + rnd() * 100, 4); g.fill(); } });
    shellMeshes(sh, map, cutTex(sh, LOWER, [[-.05, -.315, .02, .015], [.07, -.315, .02, .015]], slots), cutTex(sh, LOWER), { metal: .35, rough: .6, bump: 1.2 });
    const im = clay('#5d5b57', { metal: .35, rough: .6 }); rim(sh, LOWER, .028, im);
    for (let i = 0; i < LOWER.length; i += 6) { const [u, v] = LOWER[i], p = sh.at(u * .92, v * .95 + (v > -.2 ? -.03 : .02)); mesh(sph(.024, 12, 8), im, head, [p.x, p.y, p.z + .01], null, [1, 1, .6]).userData.rigid = true; }
    for (const fy of [-.45, -.8]) { const pts = []; for (let i = 0; i <= 12; i++) pts.push(sh.at(-.5 + i / 12, fy).add(V(0, 0, .015))); tube(pts, .02, im, head).userData.rigid = true; }
    at = sh.at;
  }
  if (MSTYLE === 'gas') {          // black rubber respirator with a filter canister
    const sh = faceShell(-.74, .74, -1.02, .16, .06, 6, noseBump(.22)), rub = clay('#25282a', { rough: .6, bump: .9 });
    shellMeshes(sh, paintTex(sh, '#2a2d2f'), cutTex(sh, LOWER), cutTex(sh, LOWER), { rough: .6, bump: .9 });
    rim(sh, LOWER, .03, rub);
    const p = sh.at(.03, -.58), can = group(); can.position.copy(p); can.rotation.set(Math.PI / 2 - .25, 0, 0); head.add(can);
    mesh(new THREE.CylinderGeometry(.2, .22, .12, 32), rub, can, [0, .03, 0]).userData.rigid = true;
    mesh(new THREE.CylinderGeometry(.24, .24, .26, 40), steel({ c: '#5a6b52' }), can, [0, .2, 0]).userData.rigid = true;
    for (const y of [.1, .2, .3]) mesh(new THREE.TorusGeometry(.245, .015, 8, 40), rub, can, [0, y, 0], [Math.PI / 2, 0, 0]).userData.rigid = true;
    mesh(new THREE.CylinderGeometry(.18, .18, .02, 32), clay('#151515'), can, [0, .34, 0]).userData.rigid = true;
    for (let i = 0; i < 7; i++) { const a = i / 7 * Math.PI * 2; mesh(new THREE.CylinderGeometry(.025, .025, .03, 10), clay('#050505'), can, [Math.cos(a) * .1, .345, Math.sin(a) * .1]).userData.rigid = true; }
    for (const sx of [-1, 1]) { const q = sh.at(sx * .32, -.35); mesh(new THREE.CylinderGeometry(.08, .09, .06, 24), rub, head, [q.x, q.y, q.z + .03], [Math.PI / 2, 0, 0]).userData.rigid = true; }
    const hs = [V(p.x + .1, p.y - .1, p.z + .1), V(p.x + .35, p.y - .6, p.z + .25), V(p.x + .55, p.y - 1.1, p.z + .1)]; const hose = tube(hs, .07, rub, head);
    for (let i = 1; i < 12; i++) { const c = new THREE.CatmullRomCurve3(hs), t = i / 12, q = c.getPointAt(t), T = c.getTangentAt(t); const r = mesh(new THREE.TorusGeometry(.075, .012, 6, 24), rub, head, [q.x, q.y, q.z]); r.quaternion.setFromUnitVectors(V(0, 0, 1), T); }
    at = sh.at;
  }
  if (MSTYLE === 'sack') {         // burlap sack hood pulled over the whole head, eye holes, stitched mouth, rope at the neck
    const g = HEADGEO.clone(), ps = g.attributes.position, idx = g.index.array, keep = [];
    const eyeP = EYEH.map(([u, v, rx, ry]) => [stretchX(u, v), stretchY(v), rx * 1.0, ry * 1.1]);
    const inHole = i => { const x = ps.getX(i), y = ps.getY(i), z = ps.getZ(i); return z > 0 && eyeP.some(([ex, ey, rx, ry]) => ((x - ex) / rx) ** 2 + ((y - ey) / ry) ** 2 < 1); };
    for (let k = 0; k < idx.length; k += 3) if (!(inHole(idx[k]) && inHole(idx[k + 1]) && inHole(idx[k + 2]))) keep.push(idx[k], idx[k + 1], idx[k + 2]);
    g.setIndex(keep); const pn = V(0, 0, 0);
    for (let i = 0; i < ps.count; i++) { pn.fromBufferAttribute(ps, i); const lift = .07 + .03 * Math.sin(pn.x * 9 + pn.y * 4) * Math.cos(pn.z * 7); pn.addScaledVector(pn.clone().normalize(), lift); if (pn.y < -.9) { const k = Math.min(1, (-.9 - pn.y) / .5); pn.x *= 1 - .3 * k; pn.z *= 1 - .3 * k; } ps.setXYZ(i, pn.x, pn.y, pn.z); }
    g.computeVertexNormals();
    const [c, cg] = canvas(1024); cg.fillStyle = '#a88a5c'; cg.fillRect(0, 0, 1024, 1024);
    for (let y = 0; y < 1024; y += 8) { cg.fillStyle = 'rgba(70,50,25,.35)'; cg.fillRect(0, y, 1024, 3); } for (let x = 0; x < 1024; x += 8) { cg.fillStyle = 'rgba(70,50,25,.25)'; cg.fillRect(x, 0, 3, 1024); }
    for (let i = 0; i < 60; i++) { const x = rnd() * 1024, y = rnd() * 1024, r = 20 + rnd() * 90, gr = cg.createRadialGradient(x, y, 0, x, y, r); gr.addColorStop(0, rnd() < .3 ? 'rgba(110,15,15,.5)' : 'rgba(60,40,20,.3)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); cg.fillStyle = gr; cg.fillRect(x - r, y - r, 2 * r, 2 * r); }
    const t = tex(c, 1); t.repeat.set(3, 2);
    const sack = mesh(g, clay('#fff', { map: t, rough: 1, bump: 2.2, side: THREE.DoubleSide }), head); sack.userData.rigid = true;
    const thread = clay('#2a1d12', { rough: .9 }); for (let i = 0; i <= 8; i++) { const a = onFace(-.3 + .6 * i / 8, -.55), p = a.p.clone().addScaledVector(a.n, .09);
      tube([p.clone().add(V(-.035, .05, 0)), p.clone().add(V(.035, -.05, 0))], .012, thread, head); tube([p.clone().add(V(-.035, -.05, 0)), p.clone().add(V(.035, .05, 0))], .012, thread, head); }
    const rope = []; for (let i = 0; i <= 60; i++) { const a = i / 60 * Math.PI * 2; rope.push(V(Math.cos(a) * .72 * HX, -1.32 + .04 * Math.sin(a * 3), Math.sin(a) * .62)); }
    tube(rope, .055, clay('#8a6a3a', { bump: 2.5 }), head, true);
    tube([V(-.6, -1.35, .3), V(-.7, -1.6, .45), V(-.65, -1.85, .5)], .05, clay('#8a6a3a', { bump: 2.5 }), head);
  }
  const FIN = A['Mask'], MC = PAL.masks[FIN] || '#e6dfc4', METAL = MC === 'chrome' || MC === 'gold';
  if (!MSTYLE) {
  const aged = c => '#' + new THREE.Color(c).lerp(new THREE.Color('#d0b866'), .62).getHexString();
  const base = METAL ? { chrome: '#c4cad0', gold: '#d9ae44' }[MC] : ['Charred Mask', 'Toxic Mask', "Jack-o'-Lantern Mask", 'Mossy Mask'].includes(FIN) ? MC : aged(MC);
  // face-space extents of the shell grid (fx, fy as used by onFace)
  const FX0 = -.74, FX1 = .74, FY0 = -1.02, FY1 = .16, NX = 110, NY = 100;
  const top = fx => -.15 - .035 * Math.exp(-((Math.abs(fx) - .33) ** 2) / .02) + .27 * Math.exp(-(fx * fx) / .006) + .07 * THREE.MathUtils.smoothstep(Math.abs(fx), .5, .7);
  const OUT = [];
  for (let i = 0; i <= 40; i++) { const fx = -.66 + 1.32 * i / 40; OUT.push([fx, top(fx)]); }
  for (let i = 1; i < 40; i++) { const a = i / 40 * Math.PI, s = Math.sin(a); OUT.push([.66 * Math.cos(a) * (1 - .22 * s * s), -.1 - .84 * Math.pow(s, .7)]); }
  // depth of the face under the shell, smoothed into one hard moulded surface
  const Z = new Float32Array((NX + 1) * (NY + 1)), RAW = new Float32Array(Z.length);
  for (let j = 0; j <= NY; j++) for (let i = 0; i <= NX; i++) {
    const fx = FX0 + (FX1 - FX0) * i / NX, fy = FY1 - (FY1 - FY0) * j / NY;
    ray.set(V(stretchX(fx, fy), stretchY(fy), 3), V(0, 0, -1)); const h = ray.intersectObject(PROBE)[0];
    RAW[j * (NX + 1) + i] = h ? h.point.z : -.3;
  }
  const blur = (src, r) => { const out = new Float32Array(src.length);
    for (let j = 0; j <= NY; j++) for (let i = 0; i <= NX; i++) { let s = 0, w = 0;
      for (let dj = -r; dj <= r; dj++) for (let di = -r; di <= r; di++) { const a = i + di, b = j + dj; if (a < 0 || b < 0 || a > NX || b > NY) continue; s += src[b * (NX + 1) + a]; w++; }
      out[j * (NX + 1) + i] = s / w; } return out; };
  let sm = blur(RAW, 6); for (let k = 0; k < Z.length; k++) sm[k] = Math.max(sm[k], RAW[k]); sm = blur(sm, 4);
  const bump = (fx, fy) => {      // moulded nose: rises from the bridge into a hooked beak
    const k = THREE.MathUtils.clamp((.14 - fy) / .44, 0, 1), wx = .045 + .085 * k;
    const under = fy < -.3 ? Math.exp(-(((fy + .3) / .07) ** 2)) : 1;
    return .44 * Math.pow(k, 1.4) * under * Math.exp(-((fx - .01) ** 2) / (wx * wx));
  };
  for (let j = 0; j <= NY; j++) for (let i = 0; i <= NX; i++) {
    const fx = FX0 + (FX1 - FX0) * i / NX, fy = FY1 - (FY1 - FY0) * j / NY, q = j * (NX + 1) + i;
    Z[q] = Math.max(sm[q], RAW[q] + .02) + .07 + bump(fx, fy) + .03 * Math.exp(-(fx * fx / .05 + (fy + .78) ** 2 / .01));   // chin ridge
  }
  at = (fx, fy) => {        // bilinear lookup of the shell
    const u = THREE.MathUtils.clamp((fx - FX0) / (FX1 - FX0) * NX, 0, NX - 1e-4), v = THREE.MathUtils.clamp((FY1 - fy) / (FY1 - FY0) * NY, 0, NY - 1e-4);
    const i = Math.floor(u), j = Math.floor(v), a = u - i, b = v - j, z = (I, J) => Z[J * (NX + 1) + I];
    return V(stretchX(fx, fy), stretchY(fy), z(i, j) * (1 - a) * (1 - b) + z(i + 1, j) * a * (1 - b) + z(i, j + 1) * (1 - a) * b + z(i + 1, j + 1) * a * b);
  };
  const shellGeo = dz => { const g = new THREE.PlaneGeometry(1, 1, NX, NY), p = g.attributes.position;
    for (let j = 0; j <= NY; j++) for (let i = 0; i <= NX; i++) { const fx = FX0 + (FX1 - FX0) * i / NX, fy = FY1 - (FY1 - FY0) * j / NY, q = j * (NX + 1) + i;
      p.setXYZ(q, stretchX(fx, fy), stretchY(fy), Z[q] + dz); }
    g.computeVertexNormals(); return g; };
  const S = 1024, MX = fx => (fx - FX0) / (FX1 - FX0) * S, MY = fy => (FY1 - fy) / (FY1 - FY0) * S, PX = S / (FX1 - FX0);
  const path = (g, pts) => { g.beginPath(); pts.forEach(([u, v], i) => i ? g.lineTo(MX(u), MY(v)) : g.moveTo(MX(u), MY(v))); g.closePath(); };
  const HOLES = [];
  for (const [fy, xs] of [[-.32, [-.5, -.36]], [-.46, [-.46, -.32]], [-.58, [-.38]], [-.3, [.32, .48]], [-.44, [.3, .46]], [-.58, [.38]],
    [-.67, [-.24, -.1, .06, .2]], [-.8, [-.13, .02, .16]]]) for (const fx of xs) HOLES.push([fx + (rnd() - .5) * .02, fy + (rnd() - .5) * .02]);
  const NOSTRILS = [[-.05, -.315], [.07, -.315]];
  const CHUNK = [[-.66, -.2], [-.42, -.24], [-.36, -.4], [-.48, -.5], [-.4, -.66], [-.6, -.62]];
  function alpha(holes) {
    const [c, g] = canvas(S); g.fillStyle = '#000'; g.fillRect(0, 0, S, S); g.fillStyle = '#fff'; path(g, OUT); g.fill();
    if (FIN === 'Broken Mask') { g.fillStyle = '#000'; path(g, CHUNK); g.fill(); }
    if (holes) { g.fillStyle = '#000';
      for (const [u, v] of HOLES) { g.beginPath(); g.ellipse(MX(u), MY(v), .02 * PX, .017 * PX, 0, 0, 7); g.fill(); }
      for (const [u, v] of NOSTRILS) { g.beginPath(); g.ellipse(MX(u), MY(v), .022 * PX, .016 * PX, 0, 0, 7); g.fill(); }
      if (FIN === "Jack-o'-Lantern Mask") { g.beginPath(); const pts = [[-.3, -.6], [-.2, -.7], [-.12, -.62], [-.04, -.72], [.04, -.62], [.12, -.72], [.2, -.62], [.3, -.7], [.32, -.62], [.16, -.84], [-.16, -.84]];
        pts.forEach(([u, v], i) => i ? g.lineTo(MX(u), MY(v)) : g.moveTo(MX(u), MY(v))); g.fill(); } }
    return tex(c, 1, false);
  }
  function colour() {
    const [c, g] = canvas(S); g.fillStyle = base; g.fillRect(0, 0, S, S);
    const blot = (col, n, r0, r1) => { for (let i = 0; i < n; i++) { const x = rnd() * S, y = rnd() * S, r = r0 + rnd() * r1, gr = g.createRadialGradient(x, y, 0, x, y, r);
      gr.addColorStop(0, col); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = gr; g.beginPath(); g.ellipse(x, y, r, r * .7, rnd() * 3, 0, 7); g.fill(); } };
    const drip = (x, y, L, col, w = 12) => { g.fillStyle = col; g.beginPath(); g.roundRect(x - w / 2, y, w, L, w / 2); g.fill(); g.beginPath(); g.arc(x, y + L, w * .75, 0, 7); g.fill(); };
    const smear = (x, y, col, n = 5) => { g.fillStyle = col; for (let i = 0; i < n; i++) { g.beginPath(); g.ellipse(x + (rnd() - .5) * 60, y + (rnd() - .5) * 40, 14 + rnd() * 30, 6 + rnd() * 14, rnd() * 3, 0, 7); g.fill(); }
      for (let i = 0; i < 3; i++) drip(x + (rnd() - .5) * 50, y, 40 + rnd() * 130, col, 6 + rnd() * 8); };
    if (!METAL) {   // yellowed, grimy plastic: dirt pooled round the holes and in the creases
      blot('rgba(150,120,40,.22)', 70, 30, 90); blot('rgba(90,70,30,.2)', 40, 8, 30); blot('rgba(255,250,220,.18)', 20, 30, 70);
      for (const [u, v] of HOLES) { g.strokeStyle = 'rgba(80,60,25,.45)'; g.lineWidth = 7; g.beginPath(); g.ellipse(MX(u), MY(v), .027 * PX, .023 * PX, 0, 0, 7); g.stroke(); }
    } else blot('rgba(255,255,255,.25)', 12, 10, 40);
    const BLOOD = 'rgba(128,14,14,.85)', bloodN = FIN === 'Bloody Mask' ? 16 : ['Chrome Mask', 'Gold Mask', 'Toxic Mask', "Jack-o'-Lantern Mask"].includes(FIN) ? 2 : 6;
    for (let i = 0; i < bloodN; i++) smear(MX((rnd() - .5) * 1.1), MY(-.05 - rnd() * .6), BLOOD, FIN === 'Bloody Mask' ? 7 : 3);
    for (let i = 0; i < bloodN * 6; i++) { g.fillStyle = 'rgba(120,10,10,.8)'; g.beginPath(); g.arc(rnd() * S, rnd() * S, 2 + rnd() * 6, 0, 7); g.fill(); }
    if (FIN === 'Bloody Mask') { g.fillStyle = BLOOD; g.beginPath(); g.ellipse(MX(.3), MY(-.5), 70, 120, .3, 0, 7); g.fill(); for (let i = 0; i < 6; i++) drip(MX(.18 + i * .05), MY(-.55), 80 + rnd() * 160, BLOOD, 12); }
    if (FIN === 'Rusted Mask') { blot('rgba(138,74,34,.7)', 130, 4, 26); for (let i = 0; i < 8; i++) drip(MX(-.5 + rnd()), MY(-.1 - rnd() * .3), 60 + rnd() * 140, 'rgba(120,60,24,.8)', 9); }
    if (FIN === 'Muddy Mask') { g.fillStyle = 'rgba(94,68,48,.85)'; g.fillRect(0, MY(-.6), S, S); blot('rgba(94,68,48,.8)', 60, 10, 40); for (let i = 0; i < 10; i++) drip(MX(-.6 + rnd() * 1.2), MY(-.6), 40 + rnd() * 100, 'rgba(94,68,48,.9)', 14); }
    if (FIN === 'Bone Mask' || FIN === 'Broken Mask') { g.strokeStyle = 'rgba(60,45,25,.85)'; g.lineWidth = 4; for (let i = 0; i < 6; i++) { let x = rnd() * S, y = rnd() * S * .5; g.beginPath(); g.moveTo(x, y); for (let k = 0; k < 6; k++) { x += rnd() * 80 - 40; y += 30 + rnd() * 40; g.lineTo(x, y); } g.stroke(); } }
    if (FIN === 'Lipstick Mask') { g.strokeStyle = '#c21f3a'; g.lineWidth = 30; g.lineCap = 'round'; g.beginPath(); g.moveTo(MX(-.24), MY(-.58)); g.quadraticCurveTo(MX(0), MY(-.74), MX(.24), MY(-.56)); g.stroke();
      g.fillStyle = 'rgba(232,106,138,.5)'; for (const u of [-.42, .42]) { g.beginPath(); g.ellipse(MX(u), MY(-.36), 60, 40, 0, 0, 7); g.fill(); } }
    if (FIN === 'Toxic Mask') for (let i = 0; i < 8; i++) drip(MX(-.55 + i * .15), MY(-.05 + rnd() * .1), 80 + rnd() * 220, '#5ee82a', 18);
    if (FIN === 'Charred Mask') blot('rgba(0,0,0,.55)', 50, 10, 40);
    if (FIN === 'Stitched Mask') { g.strokeStyle = 'rgba(70,40,30,.6)'; g.lineWidth = 6; g.beginPath(); g.moveTo(MX(-.3), MY(-.1)); g.lineTo(MX(.1), MY(-.75)); g.stroke(); }
    return tex(c, 1);
  }
  function emissive() {
    const [c, g] = canvas(S); g.fillStyle = '#000'; g.fillRect(0, 0, S, S);
    if (FIN === 'Charred Mask') { g.strokeStyle = '#ff7a1a'; g.lineWidth = 7; for (let i = 0; i < 9; i++) { let x = rnd() * S, y = rnd() * S; g.beginPath(); g.moveTo(x, y); for (let k = 0; k < 5; k++) { x += rnd() * 120 - 60; y += rnd() * 120 - 60; g.lineTo(x, y); } g.stroke(); } }
    if (FIN === 'Toxic Mask') { g.drawImage(colour().image, 0, 0); const d = g.getImageData(0, 0, S, S); for (let i = 0; i < d.data.length; i += 4) { const gr = d.data[i + 1] > 200 && d.data[i] < 140; d.data[i] = d.data[i + 2] = 0; d.data[i + 1] = gr ? 255 : 0; } g.putImageData(d, 0, 0); }
    return tex(c, 1);
  }
  const mask = group(); head.add(mask);
  const glowy = FIN === 'Charred Mask' || FIN === 'Toxic Mask';
  const mm = clay('#fff', { map: colour(), rough: MC === 'chrome' ? .3 : MC === 'gold' ? .38 : .75, metal: MC === 'chrome' ? .7 : MC === 'gold' ? .6 : 0,
    bump: .8, side: THREE.DoubleSide, alpha: alpha(true), emissive: glowy ? '#ffffff' : '#000', ei: glowy ? 1.2 : 0, emissiveMap: glowy ? emissive() : null });
  mesh(shellGeo(0), mm, mask).userData.rigid = true;
  const inner = mesh(shellGeo(-.035), new THREE.MeshStandardMaterial({ color: '#2a2016', roughness: 1, side: THREE.DoubleSide, alphaMap: alpha(false), alphaTest: .5, transparent: true }), mask);
  inner.userData.rigid = true;
  const edge = FIN === 'Broken Mask' ? OUT.filter(([u, v]) => !(u < -.36 && v < -.2 && v > -.66)) : OUT;
  tube(edge.map(([u, v]) => at(u, v).add(V(0, 0, -.017))), .022, clay(base, { rough: .75, bump: .5, metal: METAL ? .6 : 0 }), mask, FIN !== 'Broken Mask').userData.rigid = true;
  if (FIN === 'Broken Mask') {     // jagged break with the wound showing through
    tube(CHUNK.map(([u, v]) => at(u, v).add(V(0, 0, -.017))), .016, clay(base, { rough: .8 }), mask).userData.rigid = true;
    const w = at(-.5, -.42); mesh(sph(.13, 32, 24), clay('#8e1a1a', { rough: .5 }), mask, [w.x, w.y, w.z - .08], null, [1.2, 1.4, .4]);
  }
  if (FIN === 'Stitched Mask') for (let i = 0; i <= 6; i++) { const fx = -.3 + .4 * i / 6, fy = -.1 - .65 * i / 6, p = at(fx, fy).add(V(0, 0, .008));
    tube([p.clone().add(V(-.035, .02, 0)), p.clone().add(V(.035, -.02, 0))], .009, clay('#1f1a16'), mask); }
  if (FIN === 'Mossy Mask') for (let i = 0; i < 12; i++) { const fx = (rnd() - .5) * 1.1, fy = -.2 - rnd() * .65, p = at(fx, fy);
    mesh(sph(.035 + rnd() * .04, 16, 12), clay(i % 2 ? '#4f7a2a' : '#79a83a', { bump: 3 }), mask, [p.x, p.y, p.z + .005], null, [1, 1, .45]); }
  if (FIN === "Jack-o'-Lantern Mask") { const p = at(0, -.7), l = new THREE.PointLight('#ffb340', 1.2, 1.5); l.position.set(p.x, p.y, p.z - .1); mask.add(l);
    mesh(sph(.22, 24, 16), clay('#ffb340', { emissive: '#ff8a1a', ei: 2, noBump: true }), mask, [p.x, p.y, p.z - .1], null, [1.4, .6, .2]); }

  }
  if (!MSTYLE || MSTYLE === 'iron' || MSTYLE === 'gas') {
  // rusty leather straps riveted to the mask: one over the temple, one buckled under the ear round the jaw
  const LEATHER = (() => { const [c, g] = canvas(512); g.fillStyle = '#6e4428'; g.fillRect(0, 0, 512, 512);
    for (let i = 0; i < 90; i++) { const x = rnd() * 512, y = rnd() * 512, r = 6 + rnd() * 40, gr = g.createRadialGradient(x, y, 0, x, y, r);
      gr.addColorStop(0, rnd() < .5 ? 'rgba(150,80,30,.5)' : 'rgba(40,22,12,.5)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = gr; g.fillRect(x - r, y - r, 2 * r, 2 * r); }
    for (let i = 0; i < 60; i++) { g.strokeStyle = 'rgba(200,160,110,.25)'; g.lineWidth = 1 + rnd() * 2; g.beginPath(); const x = rnd() * 512, y = rnd() * 512; g.moveTo(x, y); g.lineTo(x + rnd() * 40 - 20, y + rnd() * 8 - 4); g.stroke(); }
    return clay('#fff', { map: tex(c, 1), rough: .9, bump: 1.6, side: THREE.DoubleSide }); })();
  const RUST = (() => { const [c, g] = canvas(256); g.fillStyle = '#8d8d88'; g.fillRect(0, 0, 256, 256);
    for (let i = 0; i < 70; i++) { g.fillStyle = `rgba(${120 + rnd() * 40 | 0},${55 + rnd() * 25 | 0},20,${.4 + rnd() * .5})`; g.beginPath(); g.arc(rnd() * 256, rnd() * 256, 3 + rnd() * 18, 0, 7); g.fill(); }
    return clay('#fff', { map: tex(c, 1), metal: .35, rough: .7, bump: 1.2 }); })();
  const along = (pts, n = 90) => { const c = new THREE.CatmullRomCurve3(pts), out = [];
    for (let i = 0; i <= n; i++) { const d = c.getPoint(i / n).normalize(); ray.set(d.clone().multiplyScalar(4), d.clone().negate()); const h = ray.intersectObject(PROBE)[0];
      if (h) out.push([h.point.clone().addScaledVector(h.face.normal, .012), h.face.normal.clone()]); }
    return out; };
  function band(path, w, t) {
    const pos = [], uv = [], idx = [];
    path.forEach(([p, nrm], i) => { const nx = path[Math.min(i + 1, path.length - 1)][0], pv = path[Math.max(i - 1, 0)][0];
      const T = nx.clone().sub(pv).normalize(), B = T.clone().cross(nrm).normalize(), top = p.clone().addScaledVector(nrm, t);
      for (const [q, k] of [[p.clone().addScaledVector(B, -w), 0], [top.clone().addScaledVector(B, -w), 0], [top.clone().addScaledVector(B, w), 1], [p.clone().addScaledVector(B, w), 1]]) { pos.push(q.x, q.y, q.z); uv.push(i / 20, k); } });
    for (let i = 0; i < path.length - 1; i++) for (let k = 0; k < 3; k++) { const a = i * 4 + k, b = a + 1, c = a + 4, d = b + 4; idx.push(a, c, b, b, c, d); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); g.setIndex(idx); g.computeVertexNormals();
    const m = mesh(g, LEATHER, head); m.userData.rigid = true; return m;
  }
  const rivet = (p, n, r = .022) => { const g = group(); placed(g, { p, n }, .0, head); mesh(sph(r, 16, 10), RUST, g, [0, 0, .012], null, [1, 1, .55]).userData.rigid = true; };
  const frame = (p, n, T, w, h, r = .014) => {  // square metal loop lying on the strap
    const g = group(); g.position.copy(p); const B = T.clone().cross(n).normalize(); g.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(T, B, n)); head.add(g);
    for (const [a, b] of [[[-w, -h], [w, -h]], [[w, -h], [w, h]], [[w, h], [-w, h]], [[-w, h], [-w, -h]]]) tube([V(a[0], a[1], .03), V(b[0], b[1], .03)], r, RUST, g).userData.rigid = true;
    return g;
  };
  for (const [fx, fy, dirs, w, buckle] of [
    [-.63, -.1, [V(-1, .14, -.05), V(-.75, .2, -.7), V(-.2, .22, -1)], .055, false],
    [-.62, -.5, [V(-1, -.4, -.1), V(-.75, -.38, -.7), V(-.2, -.35, -1)], .05, true]]) {
    const P = at(fx, fy), pts = along([P.clone(), ...dirs]);
    band(pts, w, .022);
    const [p0, n0] = pts[Math.min(5, pts.length - 1)], [p1] = pts[Math.min(6, pts.length - 1)], T0 = p1.clone().sub(p0).normalize();
    // riveted metal plate where the strap meets the mask
    const pl = new THREE.Mesh(new THREE.BoxGeometry(.24, w * 2.6, .02), RUST); pl.castShadow = true; pl.userData.rigid = true;
    pl.position.copy(P).add(V(-.03, 0, .02)); pl.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(T0, T0.clone().cross(V(0, 0, 1)).normalize().negate(), V(0, 0, 1))); head.add(pl);
    for (const s of [-1, 1]) rivet(P.clone().add(V(-.03 + s * .075, 0, .035)), V(0, 0, 1), .028);
    if (buckle) { const k = Math.floor(pts.length * .22), [bp, bn] = pts[k], T = pts[k + 1][0].clone().sub(pts[k - 1][0]).normalize();
      const g = frame(bp, bn, T, .085, w * 1.5, .018); tube([V(-.065, 0, .035), V(.04, 0, .05)], .011, RUST, g).userData.rigid = true;
      // loose tail end of the strap
      const tail = pts.slice(k - 8, k + 2).map(([p, n]) => [p.clone().addScaledVector(n, .028), n]); band(tail, w * .95, .018); }
    for (let i = 14; i < pts.length - 4; i += 18) rivet(pts[i][0].clone().addScaledVector(pts[i][1], .022), pts[i][1], .016);
  }
}
}
// ------------------------------------------------------------------ neck and clothing
{ // thick neck: flares into the trapezius, cords running down from behind the ears, a lump of Adam's apple
  const nk = group(); nk.position.set(.26, BODY_Y + .55, -.1); nk.rotation.y = .5; scene.add(nk);
  const prof = [[.86, -.8], [.8, -.5], [.74, -.1], [.73, .3], [.78, .8]].map(([r, y]) => new THREE.Vector2(r, y));
  mesh(new THREE.LatheGeometry(new THREE.SplineCurve(prof).getPoints(24), 60), SKINMAT, nk, null, null, [1, 1, .92]);
  for (const sx of [-1, 1]) tube([V(sx * .55, .75, -.25), V(sx * .45, .2, .35), V(sx * .22, -.6, .72)], .13, SKINMAT, nk);   // neck cords
  mesh(sph(.12, 20, 14), SKINMAT, nk, [0, .05, .72], null, [.9, 1.2, .7]);                                              // Adam's apple
}
const body = group(); body.position.set(.2, BODY_Y, -.25); body.rotation.y = .2; scene.add(body);
const CL = A['Clothing'];
const KIND = PAL.flannels[CL] ? 'flannel' : PAL.hoodie[CL] ? 'hoodie' : PAL.trench[CL] ? 'trench' : PAL.tee[CL] ? 'tee'
  : { 'Denim Shirt': 'denim', 'Chore Coat': 'chore', 'Stained Undershirt': 'undershirt', 'Butcher Apron': 'apron', 'Clown Suit': 'clown' }[CL];
const CCOL = PAL.flannels[CL] || PAL.hoodie[CL] || PAL.trench[CL] || PAL.tee[CL] || PAL.other[CL] || '#555';
function clownCloth() {   // baggy harlequin clown suit: red and cream halves, fat polka dots, dried blood
  const S = 1024, [c, g] = canvas(S); g.fillStyle = '#e8e0cc'; g.fillRect(0, 0, S, S); g.fillStyle = '#b8161e'; g.fillRect(0, 0, S / 2, S);
  for (let i = 0; i < 40; i++) { g.fillStyle = ['#1f5fb8', '#f0c020', '#2fa83a', '#e8e0cc'][i % 4]; g.beginPath(); g.arc(rnd() * S, rnd() * S, 22 + rnd() * 14, 0, 7); g.fill(); }
  for (let i = 0; i < 25; i++) { g.fillStyle = 'rgba(100,6,6,.8)'; g.beginPath(); g.ellipse(rnd() * S, rnd() * S, 20 + rnd() * 60, 12 + rnd() * 40, rnd() * 3, 0, 7); g.fill(); }
  for (let i = 0; i < 12; i++) { g.fillStyle = 'rgba(100,6,6,.85)'; g.beginPath(); g.roundRect(rnd() * S, rnd() * S, 10, 80 + rnd() * 160, 5); g.fill(); }
  return c;
}
function clothMat(rep = 6) {
  const c = KIND === 'clown' ? clownCloth() : KIND === 'flannel' ? plaid(CCOL) : KIND === 'denim' ? fabric(CCOL, 'denim') : KIND === 'chore' ? fabric(CCOL, 'canvas')
    : KIND === 'undershirt' ? torn(stained(CCOL)) : KIND === 'apron' ? stained('#5a5a5e') : KIND === 'tee' ? torn(fabric(CCOL, '')) : fabric(CCOL, '');
  return clay('#fff', { map: tex(c, 1), bump: 1.4 });
}
const CM = clothMat();
CM.map.repeat.set(6, 3);
function torso() {
  const prof = new THREE.SplineCurve([[.6, .12], [.8, .04], [1.25, -.1], [1.7, -.4], [1.93, -.85], [2.0, -1.5], [2.0, -3], [1.9, -5.5]].map(([r, y]) => new THREE.Vector2(r, y))).getPoints(60);
  const t = mesh(new THREE.LatheGeometry([new THREE.Vector2(0, .12), ...prof], 160), CM, body); t.scale.set(1.0, 1, .62);
}
const small = (() => { const m = clothMat(); m.map.repeat.set(2, 2); return m; })();
const frontZ = y => Math.sqrt(Math.max(0, 1.93 ** 2 - 0)) * .62;   // chest front ~1.2
function collarPoints(m, size = 1, lift = 0) {
  for (const sgn of [-1, 1]) {
    const sh = new THREE.Shape(); sh.moveTo(0, 0); sh.lineTo(.55 * size, .05); sh.quadraticCurveTo(.45 * size, -.3 * size, .22 * size, -.6 * size); sh.closePath();
    const c = mesh(new THREE.ExtrudeGeometry(sh, { depth: .03, bevelEnabled: true, bevelThickness: .04, bevelSize: .05, bevelSegments: 5, curveSegments: 12 }), m, body, [sgn * .1, .02 + lift, .5]);
    c.scale.set(sgn, 1, 1); c.rotation.set(-.35, sgn * .55, 0);
  }
}
function buttons(col = '#e9e1cf', n = 3, x = 0, metal = 0) { for (let i = 0; i < n; i++) mesh(sph(.055, 20, 14), clay(col, { rough: .4, metal, bump: .2 }), body, [x, -.75 - i * .55, 1.25 + i * .04]); }
function placket(m) { mesh(new THREE.BoxGeometry(.16, 2.2, .04), m, body, [0, -1.4, 1.22], [-.06, 0, 0]); }
function pocket(m, x = .85, y = -1.3, flap = false) {
  mesh(new THREE.BoxGeometry(.6, .62, .05, 4, 4, 1), m, body, [x, y, 1.08], [0, x > 0 ? .5 : -.5, 0]);
  if (flap) mesh(new THREE.BoxGeometry(.64, .16, .07), m, body, [x, y + .3, 1.1], [0, x > 0 ? .5 : -.5, 0]);
}
function undershirtV(col = '#2a2626') { mesh(sph(.55, 32, 16), clay(col), body, [0, -.1, .45], null, [1, .9, .5]); }
function holes(n) { for (let i = 0; i < n; i++) { const a = (rnd() - .5) * 1.6, y = -.8 - rnd() * 1.4, r = 1.95;
  const hp = V(Math.sin(a) * r, y, Math.cos(a) * r * .62);
  mesh(sph(.12 + rnd() * .08, 20, 14), SKINMAT, body, hp.toArray(), null, [1, 1.3, .3]).lookAt(hp.clone().multiplyScalar(2).add(body.position));
  mesh(new THREE.TorusGeometry(.15, .03, 8, 20), clay(shade(CCOL, .6)), body, hp.toArray()).lookAt(hp.clone().multiplyScalar(2)); } }
torso();
if (KIND === 'clown') {   // ruffled collar and pom-pom buttons
  const RF = [clay('#e8e0cc', { bump: 1.6 }), clay('#b8161e', { bump: 1.6 })];
  for (let i = 0; i < 26; i++) { const a = i / 26 * Math.PI * 2; mesh(sph(.32, 18, 12), RF[i % 2], body, [Math.cos(a) * 1.0, .05 + .06 * Math.sin(a * 4), Math.sin(a) * .72], [0, -a, 0], [.45, .42, 1]); }
  for (let i = 0; i < 26; i++) { const a = (i + .5) / 26 * Math.PI * 2; mesh(sph(.24, 16, 10), RF[(i + 1) % 2], body, [Math.cos(a) * .92, .22, Math.sin(a) * .66], [0, -a, 0], [.4, .35, .9]); }
  for (const [y, col] of [[-.75, '#f0c020'], [-1.45, '#1f5fb8'], [-2.15, '#2fa83a']]) { const pm = mesh(sph(.2, 20, 14), clay(col, { bump: 3 }), body, [0, y, 1.27]); mesh(sph(.08, 10, 8), clay('#7a0b0b', { rough: .3 }), body, [.1, y - .1, 1.4]); }
}
if (KIND === 'flannel') { undershirtV(); collarPoints(small); placket(small); buttons(); pocket(small, .85, -1.3, true); }
if (KIND === 'denim') { undershirtV(); collarPoints(small); placket(small); buttons('#c9ccd0', 3, 0, .8); pocket(small, .85, -1.3, true); pocket(small, -.85, -1.3, true); }
if (KIND === 'chore') { undershirtV('#3a2f28'); collarPoints(clay('#4a3324', { bump: 2.5 }), 1.15); placket(small); buttons('#3a3a3a', 3); pocket(small, .9, -2.1); pocket(small, -.9, -2.1); pocket(small, .85, -1.2); }
if (KIND === 'undershirt' || KIND === 'tee' || KIND === 'apron') {
  mesh(new THREE.TorusGeometry(.66, .07, 14, 60), small, body, [0, .08, .02], [Math.PI / 2, 0, 0], [1, .66, 1]);

}
if (KIND === 'apron') {
  const ap = clay('#fff', { map: tex(stained('#ddd6c2'), 1) });
  const prof = new THREE.SplineCurve([[.85, -.05], [1.3, -.12], [1.75, -.42], [1.98, -.85], [2.06, -1.5], [2.06, -3]].map(([r, y]) => new THREE.Vector2(r, y))).getPoints(40);
  mesh(new THREE.LatheGeometry(prof, 60, -.62, 1.24), ap, body, null, null, [1, 1, .64]);
  tube([V(-.45, -.1, .9), V(-.55, .25, .3), V(0, .4, -.4), V(.55, .25, .3), V(.45, -.1, .9)], .045, clay('#ddd6c2'), body);
}
if (KIND === 'hoodie') {
  const hm = small;
  mesh(new THREE.TorusGeometry(.78, .26, 20, 60), hm, body, [0, .1, -.15], [Math.PI / 2 - .25, 0, 0], [1.05, .85, 1]);      // hood rolled round the neck
  mesh(sph(.75, 40, 30), hm, body, [0, .45, -.75], null, [1.05, .9, .6]);                                                        // hood lying on the back
  for (const x of [-.2, .2]) { const str = tube([V(x, .02, .7), V(x * 1.1, -.4, 1.05), V(x * 1.2, -.9, 1.18)], .025, clay('#e8e4d8'), body); mesh(new THREE.CylinderGeometry(.03, .03, .1, 10), clay('#c9ccd0', { metal: .7 }), body, [x * 1.2, -.95, 1.18]); }
  mesh(new THREE.BoxGeometry(1.4, .7, .06), hm, body, [0, -2.3, 1.22], [-.05, 0, 0]);
}
if (KIND === 'trench') {
  undershirtV('#2a2626');
  const tm = small;
  mesh(new THREE.TorusGeometry(.8, .16, 16, 60, Math.PI * 1.3), tm, body, [0, .25, -.05], [Math.PI / 2 - .5, 0, Math.PI * 1.35], [1, .75, 1]);   // popped collar behind the neck
  collarPoints(tm, 1.6, -.12);
  mesh(new THREE.TorusGeometry(2.0, .09, 10, 80, Math.PI * .7), tm, body, [0, -2.6, 0], [Math.PI / 2, 0, Math.PI * .15], [1, .63, 1]);
  for (const sgn of [-1, 1]) for (let i = 0; i < 3; i++) mesh(sph(.06, 16, 12), clay('#2a2018', { rough: .4 }), body, [sgn * .35, -1.0 - i * .5, 1.18]);
  mesh(new THREE.BoxGeometry(.5, .1, .5), tm, body, [-1.35, -.25, .2], [0, 0, .35]);
}

// ------------------------------------------------------------------ weapons
const WEAPON = A['Weapon'];
const HELD = ['Machete', 'Golden Machete', 'Hunting Knife', 'Butcher Knife', 'Fish Hook'].includes(WEAPON);
const SLUNG = ['Pitchfork', 'Weed Whacker'].includes(WEAPON);
const steel = (o = {}) => clay(o.c || '#aeb3b8', { metal: .12, rough: .78, bump: 1.1, ...o });   // grey plasticine 'metal'
function rustTex(blood) {
  const [c, g] = canvas(512); g.fillStyle = '#7d736a'; g.fillRect(0, 0, 512, 512);
  for (let i = 0; i < 1400; i++) { g.fillStyle = rnd() < .5 ? `rgba(110,62,30,${.15 + rnd() * .3})` : `rgba(200,195,185,${.08 + rnd() * .15})`;
    g.beginPath(); g.ellipse(rnd() * 512, rnd() * 512, 1 + rnd() * 6, 1 + rnd() * 3, rnd() * 3, 0, 7); g.fill(); }
  g.fillStyle = 'rgba(225,222,215,.7)'; g.fillRect(0, 0, 512, 22);
  for (let i = 0; i < 700; i++) { g.fillStyle = `rgba(${100 + rnd() * 50 | 0},${45 + rnd() * 20 | 0},18,${.3 + rnd() * .4})`; g.beginPath(); g.arc(rnd() * 512, rnd() * 512, 2 + rnd() * 10, 0, 7); g.fill(); }   // heavy rust
  if (blood) { g.fillStyle = 'rgba(120,8,8,.92)'; for (let i = 0; i < 26; i++) { g.beginPath(); g.ellipse(300 + rnd() * 212, rnd() * 512, 14 + rnd() * 40, 10 + rnd() * 30, rnd() * 3, 0, 7); g.fill(); }
    for (let i = 0; i < 8; i++) { const x = 330 + rnd() * 170, y = rnd() * 300; g.beginPath(); g.roundRect(x - 60 - rnd() * 80, y, 70 + rnd() * 80, 9, 4); g.fill(); } }
  return tex(c);
}
function blade(shape, mat, parent, pos, rotY = -.3) {
  const g = new THREE.ExtrudeGeometry(shape, { depth: .02, bevelEnabled: true, bevelThickness: .025, bevelSize: .025, bevelSegments: 3, curveSegments: 20 });
  g.computeBoundingBox(); const bb = g.boundingBox, uv = g.attributes.uv, ps = g.attributes.position;
  for (let i = 0; i < uv.count; i++) uv.setXY(i, (ps.getY(i) - bb.min.y) / (bb.max.y - bb.min.y), (ps.getX(i) - bb.min.x) / (bb.max.x - bb.min.x));
  return mesh(g, mat, parent, pos, [0, rotY, 0]);
}
function shapeFrom(pts) { const sh = new THREE.Shape(); pts.forEach(([x, y], i) => i ? sh.lineTo(x, y) : sh.moveTo(x, y)); sh.closePath(); return sh; }
if (HELD) {
  const hand = group(); hand.position.set(.85, -3.25, 2.15); hand.rotation.set(0, .55, -.8); hand.scale.setScalar(1.2); hand.userData.fist = true; scene.add(hand); hand.updateMatrixWorld(true);   // fist at the lower chest, knuckles out, blade raised up and out
  const sleeveM = (() => { const m = clothMat(); m.map.repeat.set(3, 3); return m; })();
  mesh(new THREE.CylinderGeometry(.3, .33, .7, 30), SKINMAT, hand, [-.02, -.5, -.12], [0, 0, 3.01]);   // wrist
  // fist seen from the back: the back of the hand and the knuckle row face the viewer, fingers curl away behind the grip
  mesh(sph(.42, 40, 30), SKINMAT, hand, [-.1, 0, .05], null, [1, 1.02, .62]);                                       // back of the hand
  for (let i = 0; i < 4; i++) { const y = .27 - i * .175, zk = .26 - Math.abs(i - 1.5) * .035;
    mesh(sph(.1, 20, 14), SKINMAT, hand, [.22, y, zk], null, [1, .95, .9]);                                         // knuckle
    mesh(new THREE.CapsuleGeometry(.095, .22, 8, 16), SKINMAT, hand, [.33, y, zk - .2], [Math.PI / 2, 0, 0]);       // finger folding back
    mesh(new THREE.CapsuleGeometry(.085, .12, 8, 16), SKINMAT, hand, [.24, y, -.18], [0, 0, Math.PI / 2]);          // fingertip tucked behind the grip
    tube([V(-.42, y * .55, .2), V(-.1, y * .8, .28), V(.14, y, zk + .05)], .018, SKINMAT, hand);                    // tendon ridge
    for (const dz of [-.04, .04]) tube([V(.14, y + .07, zk + dz), V(.2, y + .085, zk + dz + .02)], .006, skinShade(.75), hand);   // knuckle creases
  }
  mesh(new THREE.CapsuleGeometry(.1, .26, 8, 20), SKINMAT, hand, [0, .44, .18], [0, 0, Math.PI / 2 - .3]);       // thumb resting over the top
  // blade rises out of the top of the fist
  const wg = group(); hand.add(wg); if (WEAPON === 'Machete' || WEAPON === 'Golden Machete') wg.scale.setScalar(.9);
  const grip = (col, r = .12) => { mesh(new THREE.CylinderGeometry(r, r + .01, 1.0, 28), clay(col, { rough: .5, bump: .5 }), wg, [.05, .05, .1]); mesh(new THREE.CylinderGeometry(r + .03, r + .02, .16, 28), clay(col, { rough: .5 }), wg, [.05, .6, .1]); };
  if (WEAPON === 'Machete') { grip('#5a3a22');   // rusty farm machete with a bellied tip, blood running off the edge
    const sh = new THREE.Shape(); sh.moveTo(-.2, 0); sh.lineTo(.2, 0); sh.quadraticCurveTo(.36, 2.2, .34, 3.1); sh.quadraticCurveTo(.3, 3.65, -.02, 3.95); sh.quadraticCurveTo(-.2, 3.4, -.2, 2.6); sh.closePath();
    blade(sh, clay('#fff', { map: rustTex(true), metal: .06, rough: .85, bump: 1.6 }), wg, [.05, .66, .09]);
    for (const y of [.25, .5]) mesh(new THREE.CylinderGeometry(.03, .03, .32, 10), clay('#b9a77a', { metal: .3, rough: .5 }), wg, [.05, y - .3, .1], [Math.PI / 2, 0, 0]);   // handle rivets
    wg.updateMatrixWorld(true); const BL = clay('#7a0b0b', { rough: .3, bump: .2 });
    for (const [x, y, L] of [[.36, 2.6, .5], [.37, 2.95, .8], [.33, 3.3, .35], [.3, 2.2, .25]]) { const p = wg.localToWorld(V(x + .05, y + .66, .1)), q = scene.worldToLocal(p.clone());
      tube([q, q.clone().add(V(.01, -L * .5, .02)), q.clone().add(V(.02, -L, .03))], .035, BL, scene); mesh(sph(.06, 14, 10), BL, scene, [q.x + .02, q.y - L - .03, q.z + .03], null, [1, 1.25, 1]); } }
  if (WEAPON === 'Golden Machete') { grip('#1a1a1a'); blade(shapeFrom([[-.17, 0], [.17, 0], [.2, 3.6], [-.14, 3.72]]), clay('#e2b84a', { metal: 1, rough: .22, bump: .3 }), wg, [.05, .66, .09]);
    for (let i = 0; i < 4; i++) mesh(sph(.03, 8, 6), clay('#fff', { emissive: '#fff8d0', ei: 2 }), wg, [.05 + (rnd() - .5) * .2, 1 + rnd() * 2.4, .16]); }
  if (WEAPON === 'Hunting Knife') { grip('#5a3a22', .11); mesh(new THREE.BoxGeometry(.5, .07, .12), clay('#b08a3a', { metal: .2, rough: .75 }), wg, [.05, .7, .1]);
    blade(shapeFrom([[-.12, 0], [.13, 0], [.14, 1.0], [0, 1.55], [-.04, 1.25], [-.12, 1.1]]), steel(), wg, [.05, .72, .09]); }
  if (WEAPON === 'Butcher Knife') { grip('#4a2e1a', .11);
    const sh = shapeFrom([[-.14, 0], [.14, 0], [.14, .15], [.42, .2], [.42, 1.45], [-.14, 1.45]]); const hole = new THREE.Path(); hole.absarc(.25, 1.25, .07, 0, Math.PI * 2, true); sh.holes.push(hole);
    blade(sh, steel(), wg, [.0, .66, .09]); }
  if (WEAPON === 'Fish Hook') { grip('#4a2e1a', .11);
    const pts = [V(.05, .6, .1), V(.05, 1.6, .1), V(.05, 2.2, .1), V(.15, 2.5, .1), V(.45, 2.55, .1), V(.62, 2.3, .1), V(.6, 1.95, .1)];
    tube(pts, .06, steel({ c: '#9aa0a6' }), wg); mesh(new THREE.ConeGeometry(.08, .22, 12), steel({ c: '#9aa0a6' }), wg, [.62, 1.85, .1], [0, 0, Math.PI + .3]);
    mesh(sph(.06, 12, 8), clay('#7a1010', { rough: .3 }), wg, [.6, 2.0, .16]); }
}
if (A['Back Weapon'] === 'Circus Mallet') {   // giant striped circus mallet slung behind the back, head above the near shoulder
  const bk = group(); bk.position.set(-1.25, -2.2, -1.7); bk.rotation.set(0, .3, .3); scene.add(bk);
  mesh(new THREE.CylinderGeometry(.11, .13, 5.2, 18), clay('#8a5a2e', { bump: 1.8 }), bk, [0, .2, 0]);
  const hd = group(); hd.position.set(0, 2.9, 0); hd.rotation.z = Math.PI / 2 + .1; bk.add(hd);
  const [c, g] = canvas(512); g.fillStyle = '#e8e0cc'; g.fillRect(0, 0, 512, 512); for (let i = 0; i < 8; i += 2) { g.fillStyle = '#b8161e'; g.fillRect(i * 64, 0, 64, 512); }
  for (let i = 0; i < 18; i++) { g.fillStyle = 'rgba(100,6,6,.85)'; g.beginPath(); g.ellipse(rnd() * 512, rnd() * 512, 15 + rnd() * 40, 10 + rnd() * 25, rnd() * 3, 0, 7); g.fill(); }
  const hm = clay('#fff', { map: tex(c, 1), bump: 1.4 });
  mesh(new THREE.CylinderGeometry(.6, .6, 1.5, 40), hm, hd);
  for (const y of [-.78, .78]) { mesh(new THREE.CylinderGeometry(.66, .66, .12, 40), clay('#f0c020', { bump: 1.4 }), hd, [0, y, 0]); mesh(sph(.6, 32, 16), hm, hd, [0, y * 1.02, 0], null, [1, .18, 1]); }
  ribbon([V(-1.0, .2, 1.0), V(-.6, -.3, 1.35), V(0, -.9, 1.55), V(.7, -1.6, 1.5), V(1.1, -2.2, 1.4)], .13, '#3a2a1e', body);
}
// arms: the near arm crosses the belly to the weapon fist, the far arm hangs with an open hand
{
  const bare = KIND === 'tee' || KIND === 'undershirt', SM = bare ? SKINMAT : (() => { const m = clothMat(); m.map.repeat.set(3, 3); return m; })();
  const arm = (pts, r0, r1) => { const c = new THREE.CatmullRomCurve3(pts), geo = new THREE.TubeGeometry(c, 60, 1, 24, false), pp = geo.attributes.position, cp = V(0, 0, 0), q = V(0, 0, 0);
    for (let i = 0; i <= 60; i++) { const t = i / 60, r = r0 + (r1 - r0) * t + .05 * Math.sin(t * 9); c.getPointAt(t, cp); for (let j = 0; j <= 24; j++) { const vi = i * 25 + j; q.fromBufferAttribute(pp, vi).sub(cp).normalize().multiplyScalar(r).add(cp); pp.setXYZ(vi, q.x, q.y, q.z); } }
    geo.computeVertexNormals(); return mesh(geo, SM, scene); };
  const cuff = (p, d, r) => { if (bare) return; const m = mesh(new THREE.TorusGeometry(r, .07, 10, 30), SM, scene, [p.x, p.y, p.z]); m.quaternion.setFromUnitVectors(V(0, 0, 1), d.clone().normalize()); };
  if (typeof HELD !== 'undefined' && HELD) {
    const hand = scene.children.find(o => o.userData.fist); const w = hand.localToWorld(V(-.02, -.75, -.12));
    const pts = [V(-1.4, -1.95, .2), V(-1.75, -3.1, .9), V(-.9, -3.85, 1.9), w];
    arm(pts, .46, .36); cuff(w.clone().lerp(pts[2], .08), w.clone().sub(pts[2]), .37);
  } else {
    const pts = [V(-1.4, -1.95, .2), V(-1.85, -3.2, .5), V(-1.8, -4.6, .9)]; arm(pts, .46, .38);
  }
  // far arm hanging down, open clay hand with curled fingers
  const fp = [V(2.05, -1.95, -.4), V(2.45, -3.1, -.1), V(2.45, -4.25, .45)]; arm(fp, .44, .36);
  const oh = group(); oh.position.set(2.47, -4.55, .6); oh.rotation.set(.2, -.5, .15); oh.scale.setScalar(1.15); scene.add(oh);
  cuff(V(2.46, -4.3, .5), V(0, -1, .3), .37);
  mesh(new THREE.CylinderGeometry(.28, .3, .4, 24), SKINMAT, oh, [0, .25, 0]);
  mesh(sph(.34, 32, 24), SKINMAT, oh, [0, -.15, 0], null, [1, 1.05, .5]);
  for (let i = 0; i < 4; i++) { const x = -.2 + i * .135, L = .2 + (i === 1 || i === 2 ? .06 : 0);
    const f = group(); f.position.set(x, -.45, .02); f.rotation.x = .5; oh.add(f);
    mesh(new THREE.CapsuleGeometry(.07, L, 6, 12), SKINMAT, f, [0, -L / 2, 0]);
    const f2 = group(); f2.position.set(0, -L, 0); f2.rotation.x = .7; f.add(f2); mesh(new THREE.CapsuleGeometry(.062, L * .7, 6, 12), SKINMAT, f2, [0, -L * .35, 0]);
    mesh(sph(.075, 12, 8), SKINMAT, oh, [x, -.42, .1], null, [1, .8, .8]); }   // knuckle bumps
  const th = group(); th.position.set(-.3, -.05, .08); th.rotation.set(.3, 0, -.9); oh.add(th); mesh(new THREE.CapsuleGeometry(.08, .28, 6, 12), SKINMAT, th, [0, -.15, 0]);
}
if (SLUNG) {
  const back = group(); back.position.set(WEAPON === 'Pitchfork' ? -1.05 : -1.25, WEAPON === 'Pitchfork' ? -1.95 : -.9, -1.9); back.rotation.set(0, .35, WEAPON === 'Pitchfork' ? .26 : .32); scene.add(back);
  if (WEAPON !== 'Weed Whacker') ribbon([V(-1.0, .2, 1.0), V(-.6, -.3, 1.35), V(0, -.9, 1.55), V(.7, -1.6, 1.5), V(1.1, -2.2, 1.4)], .13, '#3a2a1e', body);    // flat sling strap across the chest
  if (WEAPON === 'Pitchfork') {
    // bold farm fork: thick ash shaft, forged socket, chunky curved tines with sharp points
    const fs = steel({ c: '#5d6266' }), rust = clay('#7a3f1e', { rough: .8, bump: 1.4 });
    mesh(new THREE.CylinderGeometry(.11, .12, 6, 20), clay('#9a6434', { bump: 1.6 }), back, [0, -.1, 0]);
    for (const y of [-1.4, .2, 1.6]) mesh(new THREE.TorusGeometry(.115, .02, 8, 24), clay('#5a3a1e'), back, [0, y, 0], [Math.PI / 2, 0, 0]);   // grip wear rings
    mesh(new THREE.CylinderGeometry(.1, .14, .55, 18), fs, back, [0, 3.05, 0]);                     // socket
    tube([V(-.5, 3.55, .02), V(-.25, 3.36, 0), V(0, 3.32, 0), V(.25, 3.36, 0), V(.5, 3.55, .02)], .075, fs, back);   // curved crossbar
    for (let i = 0; i < 4; i++) {
      const x = -.5 + i * (1 / 3), x2 = x * 1.12, pts = [V(x, 3.45 - Math.abs(x) * .2 + .1, .02), V(x * 1.06, 4.0, .02), V(x2, 4.55, .12), V(x2, 4.8, .2)];
      tube(pts, .06, fs, back);
      const tip = mesh(new THREE.ConeGeometry(.06, .3, 14), fs, back, [x2, 4.93, .24]); tip.rotation.x = .35;
      if (i % 2) mesh(sph(.062, 12, 8), rust, back, [x * 1.04, 3.75, .03], null, [1.05, 1.4, .7]);   // rust blooms
    }
    mesh(sph(.09, 14, 10), rust, back, [.1, 3.35, .05], null, [1.6, .8, 1]);
  }
  if (WEAPON === 'Weed Whacker') {
    const RT = (() => { const [c, g] = canvas(512); g.fillStyle = '#8b8378'; g.fillRect(0, 0, 512, 512);
      for (let i = 0; i < 900; i++) { g.fillStyle = rnd() < .6 ? `rgba(${110 + rnd() * 40 | 0},${52 + rnd() * 20 | 0},22,${.3 + rnd() * .5})` : `rgba(50,40,30,${.2 + rnd() * .3})`; g.beginPath(); g.ellipse(rnd() * 512, rnd() * 512, 2 + rnd() * 14, 2 + rnd() * 8, rnd() * 3, 0, 7); g.fill(); }
      return tex(c, 1); })();
    const sm = clay('#fff', { map: RT, metal: .1, rough: .8, bump: 1.3 }), orange = clay('#fff', { map: RT, rough: .85, bump: 1.4 }), blk = clay('#2e2a26', { rough: .8 });
    // engine pack strapped to the back, peeking out behind the near shoulder
    const pk = group(); pk.position.set(-2.35, -2.9, -.5); pk.rotation.set(.1, .6, .15); pk.scale.setScalar(1.3); scene.add(pk);
    mesh(sph(.5, 32, 24), orange, pk, [0, 0, 0], null, [1, 1.1, .85]);                                     // engine shroud
    mesh(sph(.38, 28, 20), orange, pk, [.2, -.45, .05], null, [1.2, .7, 1]);                                 // fuel tank
    mesh(new THREE.BoxGeometry(.5, .14, .9), blk, pk, [0, -.75, -.1]);                                       // frame foot
    mesh(new THREE.CylinderGeometry(.12, .14, .35, 16), sm, pk, [.45, .25, .1], [0, 0, Math.PI / 2]);        // muffler
    mesh(new THREE.CylinderGeometry(.36, .36, .3, 30), sm, pk, [-.35, -.05, .35], [0, 0, Math.PI / 2]);          // recoil starter
    for (let i = 0; i < 7; i++) mesh(new THREE.BoxGeometry(.04, .5, .05), clay('#9a2a1e', { rough: .8 }), pk, [-.2 + i * .07, .2, .42]);   // cooling fins
    mesh(new THREE.CylinderGeometry(.13, .13, .14, 18), blk, pk, [.1, .62, 0]);                                  // fuel cap
    mesh(new THREE.CylinderGeometry(.08, .08, .3, 12), sm, pk, [-.62, -.25, .2], [0, 0, Math.PI / 2]);           // pull handle stub
    tube([V(-1.6, -1.9, -.6), V(-1.35, -1.0, -1.2), V(-1.25, -.4, -1.85)], .09, blk, scene);                        // drive hose up to the shaft
    // padded harness over the near shoulder, down the front of the chest
    ribbon([V(-1.15, -1.55, .85), V(-1.05, -2.0, 1.3), V(-1.0, -2.8, 1.45), V(-1.05, -3.8, 1.4), V(-1.1, -4.8, 1.3)], .4, '#7a5434', scene, .09);   // padded harness down the front
    tube([V(-1.15, -1.55, .85), V(-1.45, -1.45, .2), V(-1.75, -1.7, -.4), V(-2.0, -2.3, -.5)], .13, clay('#7a5434', { bump: 1.8 }), scene);   // over the shoulder to the pack
    for (let i = 0; i < 26; i++) { const p = V(-1.75 + rnd() * .9, -1.3 - rnd() * 1.6, 1.0 + rnd() * .6); mesh(new THREE.CapsuleGeometry(.012, .05 + rnd() * .05, 3, 6), clay(rnd() < .5 ? '#9ab35a' : '#c6c46a'), scene, [p.x, p.y, p.z], [rnd() * 3, rnd() * 3, rnd() * 3]); }   // grass clippings
    mesh(new THREE.CylinderGeometry(.075, .075, 5.0, 16), sm, back, [0, 0, 0]);
    const top = group(); top.position.set(0, 2.5, 0); top.rotation.z = -.55; back.add(top);              // bent neck
    mesh(new THREE.CylinderGeometry(.075, .075, .7, 16), sm, top, [0, .35, 0]);
    const hd = group(); hd.position.set(0, .75, 0); hd.rotation.set(.35, 0, .2); hd.scale.setScalar(1.45); top.add(hd);
    mesh(new THREE.CapsuleGeometry(.16, .28, 8, 16), orange, hd, [0, .1, 0]);                          // gearbox housing
    mesh(new THREE.CylinderGeometry(.2, .2, .14, 30), blk, hd, [0, -.2, 0]);                            // line spool
    mesh(new THREE.CylinderGeometry(.08, .08, .08, 20), orange, hd, [0, -.3, 0]);                       // bump knob
    mesh(new THREE.CylinderGeometry(.55, .55, .05, 36, 1, false, -Math.PI / 2, Math.PI), orange, hd, [0, -.08, -.1]);   // guard
    for (const a of [.2, 3.3]) tube([V(0, -.2, 0), V(Math.cos(a) * .5, -.15, Math.sin(a) * .5), V(Math.cos(a) * .8, -.05, Math.sin(a) * .6)], .015, clay('#c8201e', { rough: .5 }), hd);
    mesh(new THREE.TorusGeometry(.28, .045, 10, 30), blk, back, [0, .9, .15], [0, Math.PI / 2, 0]);       // D-handle
  }
}

// hand-made wobble: nudge every sculpted surface along its normals with low-frequency noise
function hsh(x, y, z) { const h = Math.sin(x * 127.1 + y * 311.7 + z * 74.7 + TOKEN.seed % 1000) * 43758.5453; return h - Math.floor(h); }
function vnoise(x, y, z) {
  const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z), f = t => t * t * (3 - 2 * t), u = f(x - xi), v = f(y - yi), w = f(z - zi); let r = 0;
  for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) for (let k = 0; k < 2; k++) r += hsh(xi + i, yi + j, zi + k) * (i ? u : 1 - u) * (j ? v : 1 - v) * (k ? w : 1 - w);
  return r - .5;
}
scene.updateMatrixWorld(true);
const seen = new Set(), wp = V(0, 0, 0), ws = V(0, 0, 0);
scene.traverse(o => {
  if (!o.isMesh || o === PROBE || o.userData.rigid || seen.has(o.geometry) || o.material.alphaMap || o.geometry.type === 'PlaneGeometry') return;
  const g = o.geometry, p = g.attributes.position, n = g.attributes.normal; if (!n || p.count < 150) return;
  seen.add(g); o.getWorldScale(ws); const sc = (ws.x + ws.y + ws.z) / 3; if (sc > 3) return;
  for (let i = 0; i < p.count; i++) {
    wp.fromBufferAttribute(p, i).applyMatrix4(o.matrixWorld);
    const d = (vnoise(wp.x * 1.8, wp.y * 1.8, wp.z * 1.8) * .09 + vnoise(wp.x * 5, wp.y * 5, wp.z * 5) * .03) / sc;   // hand-pressed lumpiness
    p.setXYZ(i, p.getX(i) + n.getX(i) * d, p.getY(i) + n.getY(i) * d, p.getZ(i) + n.getZ(i) * d);
  }
  p.needsUpdate = true; g.computeVertexNormals();
});

if (window.SILHOUETTE) {   // debug: flat black figure on green, to check the outline against the reference
  const blk = new THREE.MeshBasicMaterial({ color: '#000' }); scene.background = new THREE.Color('#55b848');
  scene.traverse(o => { if (o.isMesh) { if (o.position.z < -5 || o.geometry.type === 'PlaneGeometry') o.visible = false; else o.material = blk; } });
}
renderer.render(scene, cam);
window.done = true;
