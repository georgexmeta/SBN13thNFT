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
    gr.addColorStop(0, 'rgba(70,70,70,.35)'); gr.addColorStop(.75, 'rgba(110,110,110,.1)'); gr.addColorStop(.9, 'rgba(170,170,170,.25)'); gr.addColorStop(1, 'rgba(128,128,128,0)');
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
  for (let i = 0; i < 6000; i++) { const v = rnd() < .5 ? 60 : 200; g.fillStyle = `rgba(${v},${v},${v},.18)`; g.fillRect(rnd() * S, rnd() * S, 1.5, 1.5); }
  return tex(c, 3.5, false);
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
  const [c, g] = canvas(256); g.fillStyle = base; g.fillRect(0, 0, 256, 256);
  g.strokeStyle = 'rgba(255,255,255,.85)'; g.fillStyle = 'rgba(255,255,255,.85)'; g.lineWidth = 3;
  for (let i = 0; i < 9; i++) { const x = (i % 3) * 86 + 30 + rnd() * 20, y = Math.floor(i / 3) * 86 + 30 + rnd() * 20, a = rnd() * 6;
    g.save(); g.translate(x, y); g.rotate(a); g.beginPath(); g.ellipse(0, 0, 16, 9, 0, 0, 7); g.stroke();
    g.beginPath(); g.arc(14, -4, 7, 0, 5); g.stroke(); g.beginPath(); g.arc(0, 0, 3, 0, 7); g.fill(); g.restore(); }
  for (let i = 0; i < 40; i++) { g.beginPath(); g.arc(rnd() * 256, rnd() * 256, 2, 0, 7); g.fill(); }
  return c;
}

function clay(color, o = {}) {
  return new THREE.MeshStandardMaterial({ color: o.map ? '#ffffff' : color, roughness: o.rough ?? .78, metalness: o.metal ?? 0,
    map: o.map || null, bumpMap: o.noBump ? null : BUMP, bumpScale: (o.bump ?? 1.2) * 3.2, roughnessMap: o.noBump ? null : BUMP, side: o.side ?? THREE.FrontSide,
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
  return clay(SKIN);
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
const cam = new THREE.PerspectiveCamera(26, 1, .1, 100); cam.position.set(0, .2, 12.5); cam.lookAt(0, -.2, 0);
const dark = ['Midnight', 'Full Moon', 'Blood Red'].includes(A['Background']);
scene.add(new THREE.HemisphereLight(0xfff4e8, 0x6a4a36, dark ? .8 : 1.0));
const key = new THREE.DirectionalLight(0xfff0de, 2.1); key.position.set(-3, 5, 8); key.castShadow = true;
key.shadow.mapSize.set(2048, 2048); key.shadow.radius = 10; key.shadow.bias = -.0015; key.shadow.normalBias = .03;
Object.assign(key.shadow.camera, { left: -6, right: 6, top: 6, bottom: -6, near: 1, far: 30 }); scene.add(key);
const fill = new THREE.DirectionalLight(0xdfe8ff, .8); fill.position.set(5, -1, 7); scene.add(fill);
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
    metalness: bgName === 'Gold' ? .5 : 0, bumpMap: pressedClay(), bumpScale: 9 }), scene, [0, 0, -6]);
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
const head = new THREE.Group(); head.position.set(.15, .22, 0); head.rotation.set(.03, .62, 0); head.scale.setScalar(1.6); scene.add(head);
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
const TUMORS = SHAPE === 'Tumor Cluster' ? [dir(-.5, .7, -.4), dir(.3, .85, -.3), dir(-.8, .2, -.3), dir(.1, .5, -.85)].map(d => [d, .24 + rnd() * .08, .2 + rnd() * .04]) : [];
const CHEEK = [-.42 + rnd() * .1, -.22, .07 + .06 * SW];    // swollen near cheek (George's reference)
function headPoint(n) {
  let best = 0;
  const faceW = THREE.MathUtils.smoothstep(n.z, .25, .65);           // keep the face smooth
  let sum = 0;
  for (const [d, a, w] of LOBES) sum += Math.exp(a * (1 - faceW * .85) * Math.exp(-(1 - n.dot(d)) / (w * w)) / .045);
  best = .045 * Math.log(sum / LOBES.length * 1.0 + 1e-9) + .045 * Math.log(LOBES.length) * .55;
  let r = 1 + Math.max(0, best);
  if (n.z > 0) {
    r += .06 * Math.exp(-((n.y - .25) ** 2) / .006) * THREE.MathUtils.smoothstep(n.z, .5, .8);           // brow ridge
    r += CHEEK[2] * Math.exp(-((n.x - CHEEK[0]) ** 2 + (n.y - CHEEK[1]) ** 2) / .03);                   // swollen cheek
    r += .07 * Math.exp(-(n.x ** 2 / .04 + (n.y + .7) ** 2 / .02));                                    // chin
    for (const ex of [-.33, .33]) r -= .05 * Math.exp(-((n.x - ex) ** 2 + (n.y - .1) ** 2) / .012);     // eye sockets
  }
  for (const [d, h, w] of TUMORS) { const t = Math.exp(-(1 - n.dot(d)) / (w * w)); r += h * t * t * (3 - 2 * t); }
  if (SHAPE === 'Split Skull') r -= .13 * Math.exp(-(n.x ** 2) / .003) * THREE.MathUtils.smoothstep(n.y, .2, .5) * (n.z < .55 ? 1 : 0);
  let x = n.x * r * .92, y = n.y * r, z = n.z * r;
  if (SHAPE === 'Cone Head' && y > 0) { const k = y * y; y *= 1 + .55 * k; x *= 1 - .3 * k; z *= 1 - .3 * k; }
  if (SHAPE === 'Flat Top' && y > .82) y = .82 + (y - .82) * .25;
  if (y < -.15) { const t = -.15 - y; x *= 1 - t * .45; if (z < 0) z *= 1 - t * .6; }
  if (MASKED) { if (z > .62) z = .62 + (z - .62) * .15; }
  else if (z > 0) z *= .9;
  return V(x, y, z);
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
  const ear = group(); ear.position.set(-.86, -.05, -.02); ear.rotation.set(0, -Math.PI / 2 + .25, .1); ear.scale.setScalar(1.4); head.add(ear);
  const kind = A['Ear'];
  mesh(sph(.2, 40, 30), SKINMAT, ear, null, null, [.8, 1.25, .35]);
  const rimE = mesh(new THREE.TorusGeometry(.17, .065, 18, 50, Math.PI * (kind === 'Torn' ? 1.15 : 1.55)), SKINMAT, ear, [0, 0, .03], [0, 0, Math.PI * .55], [.85, 1.2, 1]);
  mesh(sph(.06, 16, 12), skinShade(.45), ear, [-.02, -.02, .05], null, [1, 1, .4]);
  if (kind === 'Cauliflower') for (const [x, y] of [[.12, .12], [.15, -.02], [.06, .2], [.0, .1], [.1, -.12]]) mesh(sph(.06), SKINMAT, ear, [x, y, .07]);
  if (kind === 'Torn') { mesh(sph(.05), clay('#7a1212', { rough: .4 }), ear, [.1, .16, .06], null, [1, .5, .5]); }
  if (kind === 'Gauged') {
    mesh(new THREE.TorusGeometry(.085, .045, 18, 40), SKINMAT, ear, [-.02, -.3, .03], null, [1, 1.15, 1]);
    mesh(new THREE.TorusGeometry(.075, .028, 18, 48), clay('#151515', { rough: .3, bump: .2 }), ear, [-.02, -.3, .035]);
    mesh(new THREE.TorusGeometry(.052, .008, 10, 40), clay('#c9ccd0', { metal: .8, rough: .25, bump: .1 }), ear, [-.02, -.3, .06]);
  } else mesh(sph(.075), SKINMAT, ear, [-.02, -.22, .03]);
}
buildEar();

// ------------------------------------------------------------------ face: eyes, brows, nose, mouth
const IRIS = A['Skin Tone'] === 'Albino' ? '#d77a8a' : pick(['#6f8f6a', '#7d9bb8', '#8a7a52', '#5a4632', '#9aa3a8', '#4f7a8c']);
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
  return clay('#fff', { map: tex(c), rough: .22, bump: .12 });
}
const eyeballMat = scleraMat(A['Eyes'] === 'Pinprick' || A['Eyes'] === 'Popped Out' ? 1.6 : 1);
// iris: radial fibres, dark limbal ring, flecks and the pupil, painted onto a slightly domed disc
function irisTex(pupil) {
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
  g.fillStyle = '#060404'; g.beginPath(); g.arc(C, C, C * pupil, 0, 7); g.fill();                                     // pupil
  return tex(c);
}
const IRISTEX = {};
function irisDisc(r, pupil, h) {
  const geo = new THREE.RingGeometry(r * .001, r, 48, 10), p = geo.attributes.position;
  for (let i = 0; i < p.count; i++) { const d = Math.hypot(p.getX(i), p.getY(i)) / r; p.setZ(i, h * (1 - d * d)); }
  geo.computeVertexNormals();
  const key = pupil.toFixed(2), m = clay('#fff', { map: IRISTEX[key] ||= irisTex(pupil), rough: .35, bump: .08 });
  const o = new THREE.Mesh(geo, m); o.userData.rigid = true; return o;
}
const CORNEA = new THREE.MeshPhysicalMaterial({ color: '#ffffff', roughness: .04, metalness: 0, transparent: true, opacity: .18, clearcoat: 1, clearcoatRoughness: .03 });
// the eyeball itself: sclera, iris that turns with the gaze, wet cornea and a hot highlight
function eyeball(size, o = {}, parent) {
  const e = group(); parent.add(e);
  mesh(sph(size, 40, 30), GLOW ? clay(GLOW, { emissive: GLOW, ei: 2.5, rough: .3, noBump: true }) : (o.mat || eyeballMat), e).userData.rigid = true;   // no wobble: it would swallow the iris
  if (GLOW) { const l = new THREE.PointLight(GLOW, .5, 1.2); l.position.set(0, 0, size * 1.5); e.add(l); return e; }
  const look = o.look || [0, 0], ir = size * (o.iris ?? .52), gaze = group();
  gaze.rotation.set(-look[1] * .45 + Math.max(0, (o.lid ?? .35) - .2) * 1.1, look[0] * .45, 0); e.add(gaze);   // heavy lids push the gaze down so the iris peeks out
  const sz = Math.sqrt(size * size - ir * ir), disc = irisDisc(ir, o.pupil ?? .42, (size - sz) * 1.15 + size * .03); disc.position.z = sz - size * .005; gaze.add(disc);
  const cor = mesh(new THREE.SphereGeometry(size * 1.025, 32, 16, 0, Math.PI * 2, 0, Math.asin(ir / size) * 1.25), CORNEA, gaze, null, [Math.PI / 2, 0, 0]);
  cor.userData.rigid = true; cor.castShadow = false;
  mesh(sph(size * .085, 12, 8), clay('#fff', { emissive: '#fff', ei: 1.2, noBump: true }), gaze, [size * .2, size * .2, sz + size * .2]).castShadow = false;
  return e;
}
function eye(x, y, size, o = {}) {
  size *= 1.35; const at = onFace(x, y + (o.dy || 0)), e = placed(group(), at, 0);
  mesh(sph(size * 1.45, 32, 24), clay(shade(SKIN, o.socket ?? .6)), e, [0, 0, -size * .35], null, [1, .9, .3]);      // socket
  if (o.hollow || o.popped) {
    mesh(sph(size * 1.1), new THREE.MeshStandardMaterial({ color: o.popped ? '#3a0606' : '#050303', roughness: o.popped ? .35 : 1 }), e, [0, 0, -size * .1], null, [1, .9, .35]);
    if (o.popped) {      // raw red rim of the emptied socket
      mesh(new THREE.TorusGeometry(size * .98, size * .13, 12, 36), clay('#7e1c1c', { rough: .3, bump: .3 }), e, [0, 0, size * .02], null, [1, .9, .4]);
    }
    if (!o.popped) return e;
  } else eyeball(size, o, e).position.z = size * .05;
  if (!o.popped) {
    const lid = o.lid ?? .35;
    const lidG = new THREE.SphereGeometry(size * 1.12, 32, 16, 0, Math.PI * 2, 0, Math.PI * Math.max(.05, lid));
    mesh(lidG, SKINMAT, e, [0, 0, size * .05], [.35 + (o.tilt || 0), 0, o.roll || 0]);
  }
  mesh(new THREE.TorusGeometry(size * .95, size * .22, 12, 30, Math.PI * .9), SKINMAT, e, [0, -size * .25, size * .3], [0, 0, Math.PI * 1.05 + (o.roll || 0)], [1, .55, 1]);
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
function buildEyes() {
  if (MASKED) return;
  const k = A['Eyes'];
  if (k === 'Droopy Mismatch') { eye(-.33, .08, .13, { lid: .55, roll: .15 }); eye(.31, .04, .095, { lid: .35, dy: -.03 }); }
  else if (k === 'Lazy Eye') { eye(-.33, .08, .115, { lid: .4, look: [.6, .1] }); eye(.31, .08, .11, { lid: .35, look: [1, -.5] }); }
  else if (k === 'Sunken Socket') { eye(-.33, .08, .085, { lid: .3, socket: .38 }); eye(.31, .08, .08, { lid: .3, socket: .38 }); }
  else if (k === 'Swollen Shut') { eye(-.33, .08, .12, { lid: .98 }); eye(.31, .08, .1, { lid: .7 });
    for (const [x, sz] of [[-.33, .1], [.31, .08]]) placed(mesh(sph(sz, 24, 16), SKINMAT, group(), null, null, [1.4, .9, .7]), onFace(x, .15), .04); }
  else if (k === 'Pinprick') { eye(-.33, .08, .125, { lid: .15, iris: .32, pupil: .3 }); eye(.31, .08, .11, { lid: .18, iris: .32, pupil: .3 }); }
  else if (k === 'Popped Out') { eye(-.33, .08, .125, { popped: true }); poppedEye(-.33, .08, .125); eye(.31, .06, .105, { lid: .3, look: [.4, 0] }); }
  else if (k === 'Hollow Sockets') { eye(-.33, .08, .12, { hollow: true }); eye(.31, .08, .1, { hollow: true }); }
  else { eye(-.33, .08, .11, { lid: .3 }); eye(.31, .08, .1, { lid: .3 }); }   // glowing
}
buildEyes();

function buildBrows() {
  const k = A['Brows']; if (MASKED || k === 'None') return;
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
  const k = A['Nose'], at = onFace(.02, -.15), g = placed(group(), at, 0, NOSE); g.scale.setScalar(1.3);
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
  tube([bridge.p.clone().addScaledVector(bridge.n, -.02), at.p.clone().addScaledVector(at.n, .08)], .085, SKINMAT, NOSE);
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
  const tm = clay('#e9dcb0', { rough: .45, bump: .3 }), rot = clay('#9a7a3a', { rough: .6, bump: .3 });
  for (let i = 0; i < n; i++) {
    if (gaps.includes(i)) continue;
    const x = -w / 2 + (i + .5) * w / n, h = .05 + rnd() * .035;
    mesh(new THREE.CapsuleGeometry(.022, h, 4, 8), rnd() < .2 ? rot : tm, g, [x, y0 + up * (h / 2), .03 - Math.abs(x) * .25], [0, 0, (rnd() - .5) * .35], [1.2, 1, .8]);
  }
}
function buildMouth() {
  if (MASKED || BANDANA) return;
  const k = A['Mouth'], at = onFace(.02, -.5), g = placed(group(), at, 0); g.scale.setScalar(1.35);
  const cav = new THREE.MeshStandardMaterial({ color: '#2a0808', roughness: .9 }), lipM = clay(shade(SKIN, .75), { rough: .5 });
  const gum = clay('#b84a4a', { rough: .4 });
  const lip = (pts, r) => tube(pts.map(([x, y]) => V(x, y, .02 - Math.abs(x) * .25)), r, lipM, g);
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
  if (k === 'Burn Scar') for (let i = 0; i < 9; i++) { const at = MASKED || BANDANA ? onSkull(dir(-.8 + rnd() * .2, .1 + rnd() * .3, rnd() * .3)) : onSkull(dir(-.65 + rnd() * .25, -.1 + rnd() * .35, .55 + rnd() * .2));
    placed(mesh(sph(.06 + rnd() * .05, 20, 14), clay(i % 2 ? '#c46a6a' : '#e09a8a', { rough: .3, bump: 2 }), group(), null, null, [1, 1, .3]), at, 0); }
}
buildDetail();

// ------------------------------------------------------------------ hair
function buildHair() {
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
  const col = PAL.bandanas[A['Bandana']], cmap = tex(paisley(col), 2);
  const N = 40, M = 40, pos = [], uv = [], idx = [], LAST = [];
  head.updateMatrixWorld(true);
  // wrap the cloth round the face (angle phi about the vertical axis), point hanging onto the chest
  for (let j = 0; j <= M; j++) for (let i = 0; i <= N; i++) {
    const v = j / M, u = i / N * 2 - 1, phi = u * 1.95 * (1 - Math.pow(v, 1.15) * .96), y = -.02 - v * 1.3;
    const d = V(Math.sin(phi), 0, Math.cos(phi));
    ray.set(head.localToWorld(d.clone().multiplyScalar(3).setY(y)), d.clone().negate().transformDirection(head.matrixWorld));
    const h = y > -.82 ? ray.intersectObjects([HEADMESH, NOSE], true)[0] : null;
    let p;
    if (h) { p = head.worldToLocal(h.point.clone()).addScaledVector(d, .06); LAST[i] = p.clone(); }
    else if (LAST[i]) { p = LAST[i].clone(); p.y = y; p.addScaledVector(d, (LAST[i].y - y) * .22); }
    else { p = d.clone().multiplyScalar(.85).setY(y); }
    pos.push(p.x, p.y, p.z); uv.push(i / N, 1 - v);
  }
  for (let j = 0; j < M; j++) for (let i = 0; i < N; i++) { const a = j * (N + 1) + i, b = a + 1, c = a + N + 1, d = c + 1; idx.push(a, c, b, b, c, d); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx); g.computeVertexNormals();
  mesh(g, clay('#fff', { map: cmap, side: THREE.DoubleSide, bump: 1.5 }), head);
  NOSE.visible = false;   // the cloth is already shaped over it
  // knot at the back of the near side
  const kn = onSkull(dir(-.7, -.15, -.6)); const k = placed(group(), kn, .03);
  mesh(sph(.09), clay('#fff', { map: cmap }), k); mesh(new THREE.CapsuleGeometry(.05, .3, 6, 10), clay('#fff', { map: cmap }), k, [.05, -.2, .05], [0, 0, .4], [1.4, 1, .5]);
}

// ------------------------------------------------------------------ 1/1 goalie mask
if (MASKED) {
  const FIN = A['Mask'], MC = PAL.masks[FIN];
  const base = { chrome: '#cfd5da', gold: '#e2b84a' }[MC] || MC;
  const MW = .5, MH = .66, OUT = [];
  for (let i = 0; i < 160; i++) { const t = i / 160 * Math.PI * 2, x = Math.sin(t), y = Math.cos(t);
    const w = y > 0 ? 1 - .12 * y ** 4 : 1 - .42 * y * y; OUT.push([MW * .86 * x * w, MH * (y > 0 ? .92 : 1) * y]); }
  const HOLES = [[-.08, .5], [-.1, .38], [-.12, .26], [.08, .5], [.1, .38], [.12, .26], [-.25, .45], [-.32, .33], [-.36, .2], [.25, .45], [.32, .33], [.36, .2], [0, .2],
    [-.39, .02], [-.36, -.12], [-.29, -.2], [.39, .02], [.36, -.12], [.29, -.2], [-.22, -.33], [-.1, -.36], [.1, -.36], [.22, -.33], [-.15, -.46], [0, -.48], [.15, -.46], [-.07, -.58], [.07, -.58]];
  const EYES = [[-.17, .06, .1, .075], [.17, .06, .1, .075]];
  const shellZ = (u, v) => {
    let z = -1.05 * u * u - .55 * Math.max(0, v - .2) ** 2 - .8 * Math.max(0, -v - .15) ** 2;
    z += .2 * Math.exp(-(u * u / .006 + (v + .1) ** 2 / .026)) + .045 * Math.exp(-((v - .16) ** 2 / .003)) * Math.exp(-u * u / .15);
    for (const [eu, ev] of EYES) z -= .035 * Math.exp(-((u - eu) ** 2 + (v - ev) ** 2) / .007);
    return z + .035 * Math.exp(-(u * u / .03 + (v + .5) ** 2 / .004));
  };
  const S = 1024, MX = u => (u + MW) / (2 * MW) * S, MY = v => (1 - (v + MH) / (2 * MH)) * S;
  const path = g => { g.beginPath(); OUT.forEach(([u, v], i) => i ? g.lineTo(MX(u), MY(v)) : g.moveTo(MX(u), MY(v))); g.closePath(); };
  const CHUNK = [[-.43, -.05], [-.25, -.12], [-.3, -.25], [-.12, -.33], [-.2, -.5], [-.05, -.62], [-.5, -.7]];
  function alpha(holes) {
    const [c, g] = canvas(S); g.fillStyle = '#000'; g.fillRect(0, 0, S, S); g.fillStyle = '#fff'; path(g); g.fill();
    if (FIN === 'Broken Mask') { g.fillStyle = '#000'; g.beginPath(); CHUNK.forEach(([u, v], i) => i ? g.lineTo(MX(u), MY(v)) : g.moveTo(MX(u), MY(v))); g.fill(); }
    if (holes) { g.fillStyle = '#000';
      for (const [u, v] of HOLES) { g.beginPath(); g.ellipse(MX(u), MY(v), 17, 17, 0, 0, 7); g.fill(); }
      g.beginPath(); g.ellipse(MX(0), MY(-.235), 12, 7, 0, 0, 7); g.fill();
      for (const [u, v, rx, ry] of EYES) { g.beginPath(); g.ellipse(MX(u), MY(v), rx / (2 * MW) * S, ry / (2 * MH) * S, 0, 0, 7); g.fill(); }
      if (FIN === "Jack-o'-Lantern Mask") { g.beginPath(); const pts = [[-.25, -.3], [-.18, -.38], [-.11, -.31], [-.04, -.4], [.04, -.31], [.11, -.4], [.18, -.31], [.25, -.38], [.28, -.3], [.15, -.5], [-.15, -.5]];
        pts.forEach(([u, v], i) => i ? g.lineTo(MX(u), MY(v)) : g.moveTo(MX(u), MY(v))); g.fill(); } }
    return tex(c, 1, false);
  }
  function colour() {
    const [c, g] = canvas(S); g.fillStyle = base; g.fillRect(0, 0, S, S);
    const blot = (col, n, r0, r1, area) => { for (let i = 0; i < n; i++) { g.fillStyle = col; g.beginPath(); const [x0, y0, x1, y1] = area || [0, 0, S, S];
      g.ellipse(x0 + rnd() * (x1 - x0), y0 + rnd() * (y1 - y0), r0 + rnd() * r1, (r0 + rnd() * r1) * .6, rnd() * 3, 0, 7); g.fill(); } };
    const drip = (x, y, L, col, w = 16) => { g.fillStyle = col; g.beginPath(); g.roundRect(x - w / 2, y, w, L, w / 2); g.fill(); g.beginPath(); g.arc(x, y + L, w * .8, 0, 7); g.fill(); };
    if (MC !== 'chrome' && MC !== 'gold') blot('rgba(110,85,50,.06)', 60, 20, 50);
    const eyeDrips = col => { for (const [u, v] of EYES) drip(MX(u) + 6, MY(v) + 62, 110 + rnd() * 120, col); };
    if (FIN === 'Bloody Mask') { blot('rgba(130,12,12,.85)', 40, 6, 30); eyeDrips('#7d1010'); g.fillStyle = 'rgba(120,10,10,.85)';
      g.beginPath(); g.ellipse(MX(-.25), MY(-.3), 70, 55, 0, 0, 7); g.fill(); for (let f = 0; f < 4; f++) { g.beginPath(); g.roundRect(MX(-.33) + f * 34, MY(-.1), 22, 110, 11); g.fill(); } }
    if (FIN === 'Rusted Mask') { blot('rgba(138,74,34,.6)', 120, 4, 26); eyeDrips('#8a4a22'); }
    if (FIN === 'Muddy Mask') { g.fillStyle = 'rgba(94,68,48,.85)'; g.fillRect(0, MY(-.25), S, S); blot('rgba(94,68,48,.7)', 50, 10, 40); }
    if (FIN === 'Bone Mask' || FIN === 'Broken Mask') { g.strokeStyle = 'rgba(60,50,40,.8)'; g.lineWidth = 4; for (let i = 0; i < 5; i++) { let x = rnd() * S, y = rnd() * S * .7; g.beginPath(); g.moveTo(x, y); for (let k = 0; k < 5; k++) { x += rnd() * 80 - 40; y += 40 + rnd() * 40; g.lineTo(x, y); } g.stroke(); } }
    if (FIN === 'Lipstick Mask') { g.strokeStyle = '#c21f3a'; g.lineWidth = 34; g.lineCap = 'round'; g.beginPath(); g.moveTo(MX(-.25), MY(-.32)); g.quadraticCurveTo(MX(0), MY(-.5), MX(.25), MY(-.3)); g.stroke();
      g.fillStyle = 'rgba(232,106,138,.55)'; for (const u of [-.3, .3]) { g.beginPath(); g.ellipse(MX(u), MY(-.15), 60, 40, 0, 0, 7); g.fill(); } }
    if (FIN === 'Toxic Mask') { for (let i = 0; i < 6; i++) drip(MX(-.35 + i * .14), MY(.6), 80 + rnd() * 200, '#5ee82a', 22); eyeDrips('#5ee82a'); }
    if (FIN === 'Charred Mask') blot('rgba(0,0,0,.5)', 40, 10, 40);
    if (FIN === 'Gold Mask' || FIN === 'Chrome Mask') blot('rgba(255,255,255,.25)', 10, 10, 30);
    return tex(c, 1);
  }
  function emissive() {
    const [c, g] = canvas(S); g.fillStyle = '#000'; g.fillRect(0, 0, S, S);
    if (FIN === 'Charred Mask') { g.strokeStyle = '#ff7a1a'; g.lineWidth = 7; for (let i = 0; i < 8; i++) { let x = rnd() * S, y = rnd() * S; g.beginPath(); g.moveTo(x, y); for (let k = 0; k < 5; k++) { x += rnd() * 120 - 60; y += rnd() * 120 - 60; g.lineTo(x, y); } g.stroke(); } }
    if (FIN === 'Toxic Mask') { g.drawImage(colour().image, 0, 0); const d = g.getImageData(0, 0, S, S); for (let i = 0; i < d.data.length; i += 4) { const gr = d.data[i + 1] > 200 && d.data[i] < 140; d.data[i] = d.data[i + 2] = 0; d.data[i + 1] = gr ? 255 : 0; } g.putImageData(d, 0, 0); }
    return tex(c, 1);
  }
  const shellGeo = dz => { const g = new THREE.PlaneGeometry(2 * MW, 2 * MH, 160, 200), p = g.attributes.position;
    for (let i = 0; i < p.count; i++) p.setZ(i, shellZ(p.getX(i), p.getY(i)) + dz); g.computeVertexNormals(); return g; };
  const mask = group(); mask.position.set(0, -.04, .9); mask.scale.set(1.3, 1.2, 1.2); head.add(mask);
  const glowy = FIN === 'Charred Mask' || FIN === 'Toxic Mask';
  const mm = clay('#fff', { map: colour(), rough: MC === 'chrome' ? .15 : MC === 'gold' ? .28 : .6, metal: MC === 'chrome' ? 1 : MC === 'gold' ? .9 : 0,
    bump: .7, side: THREE.DoubleSide, alpha: alpha(true), emissive: glowy ? '#ffffff' : '#000', ei: glowy ? 1.2 : 0, emissiveMap: glowy ? emissive() : null });
  mesh(shellGeo(0), mm, mask);
  mesh(shellGeo(-.035), new THREE.MeshStandardMaterial({ color: '#140c0a', roughness: 1, side: THREE.DoubleSide, alphaMap: alpha(false), alphaTest: .5, transparent: true }), mask);
  tube(OUT.map(([u, v]) => V(u, v, shellZ(u, v) - .015)), .024, clay(base, { rough: .6, bump: .5, metal: MC === 'chrome' ? 1 : MC === 'gold' ? .9 : 0 }), mask, true);
  if (FIN === 'Broken Mask') {     // wound showing through the broken chunk
    mesh(sph(.2, 32, 24), clay('#8e1a1a', { rough: .35 }), mask, [-.3, -.4, -.05], null, [1, 1.4, .3]);
    mesh(sph(.12, 24, 16), SKINMAT, mask, [-.38, -.25, -.04], null, [1, 1, .3]);
  }
  if (FIN === 'Stitched Mask') for (const [u0, v0, u1, v1] of [[.05, .62, .12, .3], [-.42, -.2, -.05, -.4]]) for (let i = 0; i <= 4; i++) {
    const u = u0 + (u1 - u0) * i / 4, v = v0 + (v1 - v0) * i / 4; tube([V(u - .03, v - .03, shellZ(u, v) + .01), V(u + .03, v + .03, shellZ(u, v) + .01)], .008, clay('#202020'), mask);
    tube([V(u - .03, v + .03, shellZ(u, v) + .01), V(u + .03, v - .03, shellZ(u, v) + .01)], .008, clay('#202020'), mask); }
  if (FIN === 'Mossy Mask') for (let i = 0; i < 9; i++) { const u = (rnd() - .5) * .8, v = (rnd() - .5) * 1.1;
    if (Math.abs(v - .06) < .1 && Math.abs(Math.abs(u) - .17) < .12) continue; mesh(sph(.04 + rnd() * .05, 16, 12), clay(i % 2 ? '#4f7a2a' : '#79a83a', { bump: 3 }), mask, [u, v, shellZ(u, v) + .01], null, [1, 1, .5]); }
  if (FIN === 'Jack-o\'-Lantern Mask') { const l = new THREE.PointLight('#ffb340', 1.2, 1.5); l.position.set(0, -.35, -.05); mask.add(l);
    mesh(sph(.2, 24, 16), clay('#ffb340', { emissive: '#ff8a1a', ei: 2, noBump: true }), mask, [0, -.38, -.1], null, [1.3, .6, .2]);
    tube([V(-.05, .62, -.02), V(0, .72, .02), V(.06, .78, .05)], .03, clay('#5a7a2a'), mask); }
  // eyes behind the holes
  for (const [u, v] of EYES) {
    if (GLOW) { mesh(sph(.05, 24, 16), clay(GLOW, { emissive: GLOW, ei: 4, noBump: true }), mask, [u + .015, v - .005, shellZ(u, v) - .065]);
      const l = new THREE.PointLight(GLOW, .35, .5); l.position.set(u, v, shellZ(u, v) - .05); mask.add(l); }
    else if (A['Eyes'] !== 'Hollow Sockets') { mesh(sph(.055, 24, 16), eyeballMat, mask, [u, v, shellZ(u, v) - .08]); mesh(sph(.025, 16, 12), clay('#0d0a0a'), mask, [u + .015, v, shellZ(u, v) - .028]); }
  }
  // flesh grown over the near edge with a raw seam
  const near = OUT.filter(([u, v]) => u < -.2 && v > -.35 && v < .5).sort((a, b) => b[1] - a[1]);
  const flesh = near.map(([u, v]) => V(u - .012, v, shellZ(u, v) + .005));
  tube(flesh.map(p => p.clone().add(V(.03, 0, .004))), .016, clay('#6a0f0f', { rough: .35, bump: .3 }), mask);
  tube(flesh, .03, SKINMAT, mask);
  for (const [u, v] of [[-.43, .2], [.43, .2], [0, .6], [-.33, -.42], [.33, -.42]]) {
    mesh(new THREE.BoxGeometry(.1, .11, .025), clay('#1f1d1c', { rough: .85 }), mask, [u, v, shellZ(u, v) + .02], [0, -u * 1.6, 0]);
    mesh(new THREE.CylinderGeometry(.025, .025, .02, 24), clay('#c9ccd0', { metal: .8, rough: .3, bump: .1 }), mask, [u, v, shellZ(u, v) + .04], [Math.PI / 2, 0, 0]);
  }
  // black elastic straps traced on the skull
  function surfacePath(centre, normal, a0, a1, n = 120) {
    const N = normal.clone().normalize(), helper = Math.abs(N.y) > .9 ? V(1, 0, 0) : V(0, 1, 0);
    const e1 = helper.clone().cross(N).normalize(), e2 = N.clone().cross(e1).normalize(), out = [];
    for (let i = 0; i <= n; i++) { const t = a0 + (a1 - a0) * i / n, d = e1.clone().multiplyScalar(Math.cos(t)).add(e2.clone().multiplyScalar(Math.sin(t)));
      ray.set(centre.clone().add(d.clone().multiplyScalar(4)), d.clone().negate()); const h = ray.intersectObject(PROBE)[0]; if (h) out.push([h.point, h.face.normal.clone()]); }
    return out;
  }
  function strap(path, w = .07, t = .03) {
    const pos = [], idx = [], L = [], R = [];
    path.forEach(([p, nrm], i) => { const nx = path[Math.min(i + 1, path.length - 1)][0], pv = path[Math.max(i - 1, 0)][0];
      const T = nx.clone().sub(pv).normalize(), B = T.clone().cross(nrm).normalize(), b0 = p.clone().addScaledVector(nrm, -.004), top = p.clone().addScaledVector(nrm, t);
      for (const q of [b0.clone().addScaledVector(B, -w), top.clone().addScaledVector(B, -w), top.clone().addScaledVector(B, w), b0.clone().addScaledVector(B, w)]) pos.push(q.x, q.y, q.z);
      L.push(p.clone().addScaledVector(B, -w - .02)); R.push(p.clone().addScaledVector(B, w + .02)); });
    for (let i = 0; i < path.length - 1; i++) for (let k = 0; k < 3; k++) { const a = i * 4 + k, b = a + 1, c = a + 4, d = b + 4; idx.push(a, c, b, b, c, d); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
    mesh(g, clay('#1f1d1c', { rough: .85, side: THREE.DoubleSide }), head); tube(L, .028, SKINMAT, head); tube(R, .028, SKINMAT, head);
  }
  strap(surfacePath(V(0, .22, 0), V(0, 1, -.12), 0, Math.PI * 2, 200));
  strap(surfacePath(V(0, 0, 0), V(1, 0, 0), .35, Math.PI * .92), .06);
}

// ------------------------------------------------------------------ neck and clothing
mesh(new THREE.CylinderGeometry(.6, .7, 1.0, 40), SKINMAT, scene, [.05, -.7, -.05]);
const body = group(); body.position.set(0, -1.05, -.25); body.rotation.y = .35; scene.add(body);
const CL = A['Clothing'];
const KIND = PAL.flannels[CL] ? 'flannel' : PAL.hoodie[CL] ? 'hoodie' : PAL.trench[CL] ? 'trench' : PAL.tee[CL] ? 'tee'
  : { 'Denim Shirt': 'denim', 'Chore Coat': 'chore', 'Stained Undershirt': 'undershirt', 'Butcher Apron': 'apron' }[CL];
const CCOL = PAL.flannels[CL] || PAL.hoodie[CL] || PAL.trench[CL] || PAL.tee[CL] || PAL.other[CL] || '#555';
function clothMat(rep = 6) {
  const c = KIND === 'flannel' ? plaid(CCOL) : KIND === 'denim' ? fabric(CCOL, 'denim') : KIND === 'chore' ? fabric(CCOL, 'canvas')
    : KIND === 'undershirt' ? torn(stained(CCOL)) : KIND === 'apron' ? stained('#5a5a5e') : KIND === 'tee' ? torn(fabric(CCOL, '')) : fabric(CCOL, '');
  return clay('#fff', { map: tex(c, 1), bump: 1.4 });
}
const CM = clothMat();
CM.map.repeat.set(6, 3);
function torso() {
  const prof = new THREE.SplineCurve([[.6, .12], [.8, .04], [1.25, -.1], [1.7, -.4], [1.93, -.85], [2.0, -1.5], [2.0, -3]].map(([r, y]) => new THREE.Vector2(r, y))).getPoints(60);
  const t = mesh(new THREE.LatheGeometry([new THREE.Vector2(0, .12), ...prof], 160), CM, body); t.scale.set(1, 1, .62);
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
const steel = (o = {}) => clay(o.c || '#aeb3b8', { metal: .55, rough: .38, bump: .4, ...o });
function rustTex() {
  const [c, g] = canvas(512); g.fillStyle = '#7d736a'; g.fillRect(0, 0, 512, 512);
  for (let i = 0; i < 1400; i++) { g.fillStyle = rnd() < .5 ? `rgba(110,62,30,${.15 + rnd() * .3})` : `rgba(200,195,185,${.08 + rnd() * .15})`;
    g.beginPath(); g.ellipse(rnd() * 512, rnd() * 512, 1 + rnd() * 6, 1 + rnd() * 3, rnd() * 3, 0, 7); g.fill(); }
  g.fillStyle = 'rgba(225,222,215,.7)'; g.fillRect(0, 0, 512, 22); return tex(c);
}
function blade(shape, mat, parent, pos, rotY = -.3) {
  const g = new THREE.ExtrudeGeometry(shape, { depth: .02, bevelEnabled: true, bevelThickness: .025, bevelSize: .025, bevelSegments: 3, curveSegments: 20 });
  g.computeBoundingBox(); const bb = g.boundingBox, uv = g.attributes.uv, ps = g.attributes.position;
  for (let i = 0; i < uv.count; i++) uv.setXY(i, (ps.getY(i) - bb.min.y) / (bb.max.y - bb.min.y), (ps.getX(i) - bb.min.x) / (bb.max.x - bb.min.x));
  return mesh(g, mat, parent, pos, [0, rotY, 0]);
}
function shapeFrom(pts) { const sh = new THREE.Shape(); pts.forEach(([x, y], i) => i ? sh.lineTo(x, y) : sh.moveTo(x, y)); sh.closePath(); return sh; }
if (HELD) {
  const hand = group(); hand.position.set(.8, -2.1, 1.85); hand.rotation.set(0, -.15, -.42); scene.add(hand);
  const sleeveM = (() => { const m = clothMat(); m.map.repeat.set(3, 3); return m; })();
  mesh(new THREE.CylinderGeometry(.3, .33, .7, 30), SKINMAT, hand, [-.02, -.5, -.12], [0, 0, 3.01]);
  mesh(new THREE.CylinderGeometry(.46, .52, 2.4, 40), KIND === 'tee' || KIND === 'undershirt' ? SKINMAT : sleeveM, hand, [-.18, -1.95, -.2], [0, 0, 3.01]);
  mesh(sph(.42, 40, 30), SKINMAT, hand, [-.05, 0, 0], null, [1, 1, .75]);
  for (let i = 0; i < 4; i++) { const y = .27 - i * .175, z = .3 - Math.abs(i - 1.5) * .03;
    mesh(new THREE.CapsuleGeometry(.115, .3, 8, 20), SKINMAT, hand, [.08, y, z], [0, 0, Math.PI / 2]);
    mesh(sph(.07, 16, 12), SKINMAT, hand, [-.2, y + .02, z - .02]);
    mesh(sph(.06, 16, 12), clay(shade(SKIN, 1.1), { rough: .4 }), hand, [.3, y, z + .07], null, [.6, .75, .4]); }
  mesh(new THREE.CapsuleGeometry(.1, .26, 8, 20), SKINMAT, hand, [.1, .45, .2], [0, 0, Math.PI / 2 - .25]);
  const grip = (col, r = .12) => { mesh(new THREE.CylinderGeometry(r, r + .01, 1.0, 28), clay(col, { rough: .5, bump: .5 }), hand, [.05, .05, .1]); mesh(new THREE.CylinderGeometry(r + .03, r + .02, .16, 28), clay(col, { rough: .5 }), hand, [.05, .6, .1]); };
  if (WEAPON === 'Machete') { grip('#e8592e'); blade(shapeFrom([[-.17, 0], [.17, 0], [.2, 3.6], [-.14, 3.72]]), clay('#fff', { map: rustTex(), metal: .35, rough: .6, bump: .8 }), hand, [.05, .66, .09]); }
  if (WEAPON === 'Golden Machete') { grip('#1a1a1a'); blade(shapeFrom([[-.17, 0], [.17, 0], [.2, 3.6], [-.14, 3.72]]), clay('#e2b84a', { metal: 1, rough: .22, bump: .3 }), hand, [.05, .66, .09]);
    for (let i = 0; i < 4; i++) mesh(sph(.03, 8, 6), clay('#fff', { emissive: '#fff8d0', ei: 2 }), hand, [.05 + (rnd() - .5) * .2, 1 + rnd() * 2.4, .16]); }
  if (WEAPON === 'Hunting Knife') { grip('#5a3a22', .11); mesh(new THREE.BoxGeometry(.5, .07, .12), clay('#b08a3a', { metal: .8, rough: .3 }), hand, [.05, .7, .1]);
    blade(shapeFrom([[-.12, 0], [.13, 0], [.14, 1.0], [0, 1.55], [-.04, 1.25], [-.12, 1.1]]), steel(), hand, [.05, .72, .09]); }
  if (WEAPON === 'Butcher Knife') { grip('#4a2e1a', .11);
    const sh = shapeFrom([[-.14, 0], [.14, 0], [.14, .15], [.42, .2], [.42, 1.45], [-.14, 1.45]]); const hole = new THREE.Path(); hole.absarc(.25, 1.25, .07, 0, Math.PI * 2, true); sh.holes.push(hole);
    blade(sh, steel(), hand, [.0, .66, .09]); }
  if (WEAPON === 'Fish Hook') { grip('#4a2e1a', .11);
    const pts = [V(.05, .6, .1), V(.05, 1.6, .1), V(.05, 2.2, .1), V(.15, 2.5, .1), V(.45, 2.55, .1), V(.62, 2.3, .1), V(.6, 1.95, .1)];
    tube(pts, .06, steel({ c: '#9aa0a6' }), hand); mesh(new THREE.ConeGeometry(.08, .22, 12), steel({ c: '#9aa0a6' }), hand, [.62, 1.85, .1], [0, 0, Math.PI + .3]);
    mesh(sph(.06, 12, 8), clay('#7a1010', { rough: .3 }), hand, [.6, 2.0, .16]); }
}
if (SLUNG) {
  const back = group(); back.position.set(WEAPON === 'Pitchfork' ? -1.05 : -1.25, WEAPON === 'Pitchfork' ? -1.95 : -.9, -1.9); back.rotation.set(0, .35, WEAPON === 'Pitchfork' ? .26 : .32); scene.add(back);
  ribbon([V(-1.0, .2, 1.0), V(-.6, -.3, 1.35), V(0, -.9, 1.55), V(.7, -1.6, 1.5), V(1.1, -2.2, 1.4)], .13, '#3a2a1e', body);    // flat sling strap across the chest
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
    const sm = steel({ c: '#9a9fa4' }), orange = clay('#e8592e', { rough: .5 }), blk = clay('#262626', { rough: .6 });
    mesh(new THREE.CylinderGeometry(.075, .075, 5.0, 16), sm, back, [0, 0, 0]);
    const top = group(); top.position.set(0, 2.5, 0); top.rotation.z = -.55; back.add(top);              // bent neck
    mesh(new THREE.CylinderGeometry(.075, .075, .7, 16), sm, top, [0, .35, 0]);
    const hd = group(); hd.position.set(0, .75, 0); hd.rotation.set(.35, 0, .2); hd.scale.setScalar(1.45); top.add(hd);
    mesh(new THREE.CapsuleGeometry(.16, .28, 8, 16), orange, hd, [0, .1, 0]);                          // gearbox housing
    mesh(new THREE.CylinderGeometry(.2, .2, .14, 30), blk, hd, [0, -.2, 0]);                            // line spool
    mesh(new THREE.CylinderGeometry(.08, .08, .08, 20), orange, hd, [0, -.3, 0]);                       // bump knob
    mesh(new THREE.CylinderGeometry(.55, .55, .05, 36, 1, false, -Math.PI / 2, Math.PI), orange, hd, [0, -.08, -.1]);   // guard
    for (const a of [.2, 3.3]) tube([V(0, -.2, 0), V(Math.cos(a) * .5, -.21, Math.sin(a) * .5), V(Math.cos(a) * .75, -.25, Math.sin(a) * .7)], .013, clay('#c6e85a', { rough: .4 }), hd);
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
    const d = (vnoise(wp.x * 1.8, wp.y * 1.8, wp.z * 1.8) * .06 + vnoise(wp.x * 5, wp.y * 5, wp.z * 5) * .018) / sc;
    p.setXYZ(i, p.getX(i) + n.getX(i) * d, p.getY(i) + n.getY(i) * d, p.getZ(i) + n.getZ(i) * d);
  }
  p.needsUpdate = true; g.computeVertexNormals();
});

renderer.render(scene, cam);
window.done = true;
