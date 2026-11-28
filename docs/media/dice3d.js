// Real 3D clay dice for the Peddler's table (George 2026-11-28).
// Physics runs ahead of time, then the faces are painted so the side that lands up shows the rolled number.
const THREE_URL='https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.min.js';
const CANNON_URL='https://cdn.jsdelivr.net/npm/cannon-es@0.20.0/dist/cannon-es.js';
let T,C,ready=null,renderer,scene,camera,mats,host,dice=[],raf=0,shadowPlane;
const S=0.36, HALF=S/2, FELT={x:3.05,z:0.58};

function claySkin(v){ // canvas texture: bone-coloured clay with pressed-in pips
  const n=256,cv=document.createElement('canvas');cv.width=cv.height=n;const g=cv.getContext('2d');
  g.fillStyle='#dccbab';g.fillRect(0,0,n,n);
  for(let i=0;i<2600;i++){const x=Math.random()*n,y=Math.random()*n,r=Math.random()*2.2+.4,l=Math.random()<.5;g.fillStyle=l?'rgba(255,246,225,.10)':'rgba(120,90,55,.10)';g.beginPath();g.arc(x,y,r,0,7);g.fill()}
  for(let i=0;i<14;i++){g.strokeStyle='rgba(110,80,50,.12)';g.lineWidth=1+Math.random()*1.5;g.beginPath();const x=Math.random()*n,y=Math.random()*n;g.moveTo(x,y);g.quadraticCurveTo(x+Math.random()*40-20,y+Math.random()*40-20,x+Math.random()*60-30,y+Math.random()*60-30);g.stroke()}
  const P={1:[4],2:[0,8],3:[0,4,8],4:[0,2,6,8],5:[0,2,4,6,8],6:[0,2,3,5,6,8]}[v];
  P.forEach(k=>{const cx=n*(.27+.23*(k%3))+Math.random()*6-3,cy=n*(.27+.23*Math.floor(k/3))+Math.random()*6-3,r=n*(v===1?.11:.075)*(0.94+Math.random()*.14);
    let gr=g.createRadialGradient(cx,cy-r*.15,r*.1,cx,cy,r*1.25);gr.addColorStop(0,'#1a0404');gr.addColorStop(.55,'#3a0b0a');gr.addColorStop(.78,'#6b2a1c');gr.addColorStop(.9,'rgba(255,238,205,.55)');gr.addColorStop(1,'rgba(255,238,205,0)');
    g.fillStyle=gr;g.beginPath();g.ellipse(cx,cy,r*1.25,r*1.2,Math.random()*3,0,7);g.fill()});
  const t=new T.CanvasTexture(cv);t.colorSpace=T.SRGBColorSpace;t.anisotropy=4;
  const b=document.createElement('canvas');b.width=b.height=n;const h=b.getContext('2d');h.fillStyle='#fff';h.fillRect(0,0,n,n); // bump: pips pressed in
  for(let i=0;i<1800;i++){h.fillStyle='rgba(0,0,0,'+(Math.random()*.08)+')';h.beginPath();h.arc(Math.random()*n,Math.random()*n,Math.random()*3+.5,0,7);h.fill()}
  P.forEach(k=>{const cx=n*(.27+.23*(k%3)),cy=n*(.27+.23*Math.floor(k/3)),r=n*(v===1?.12:.085);const gr=h.createRadialGradient(cx,cy,0,cx,cy,r);gr.addColorStop(0,'#000');gr.addColorStop(.7,'#333');gr.addColorStop(1,'#fff');h.fillStyle=gr;h.beginPath();h.arc(cx,cy,r,0,7);h.fill()});
  const bt=new T.CanvasTexture(b);
  return new T.MeshStandardMaterial({map:t,bumpMap:bt,bumpScale:2.2,roughness:.88,metalness:0,color:0xe2d6c4});
}
function roundedCube(size,r,seg){ // box whose corners are pushed out onto spheres: soft, hand-rolled clay edges
  const g=new T.BoxGeometry(size,size,size,seg,seg,seg),p=g.attributes.position,v=new T.Vector3(),inner=size/2-r;
  for(let i=0;i<p.count;i++){v.fromBufferAttribute(p,i);const c=new T.Vector3(Math.max(-inner,Math.min(inner,v.x)),Math.max(-inner,Math.min(inner,v.y)),Math.max(-inner,Math.min(inner,v.z)));
    const d=v.clone().sub(c);if(d.lengthSq()>1e-9){d.normalize().multiplyScalar(r);v.copy(c).add(d)}
    // a little hand-made wobble
    v.multiplyScalar(1+(Math.sin(v.x*41+v.y*17)+Math.cos(v.z*37-v.y*23))*.006);p.setXYZ(i,v.x,v.y,v.z)}
  g.computeVertexNormals();return g}

function init(dz){
  host=dz;
  renderer=new T.WebGLRenderer({alpha:true,antialias:true});renderer.setPixelRatio(Math.min(2,devicePixelRatio||1));
  renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=.95;
  const cv=renderer.domElement;cv.className='dice3d';host.appendChild(cv);
  scene=new T.Scene();
  camera=new T.PerspectiveCamera(39.9,16/9,.1,60);camera.position.set(0,3.386,8.685);camera.lookAt(0,1.903,0);
  scene.add(new T.HemisphereLight(0xffe2b8,0x2a1608,.55));
  const lamp=new T.SpotLight(0xffc98a,95,14,.75,.6,1.6);lamp.position.set(-.1,5.2,-.4);lamp.target.position.set(0,0,.2);lamp.castShadow=true;lamp.shadow.mapSize.set(1024,1024);lamp.shadow.bias=-.0006;lamp.shadow.radius=4;scene.add(lamp,lamp.target);
  const fill=new T.DirectionalLight(0xff9a5a,.35);fill.position.set(4,2,4);scene.add(fill); // candle glow from the right
  shadowPlane=new T.Mesh(new T.PlaneGeometry(8,2.4),new T.ShadowMaterial({opacity:.55}));shadowPlane.rotation.x=-Math.PI/2;shadowPlane.receiveShadow=true;scene.add(shadowPlane);
  mats={};for(let v=1;v<=6;v++)mats[v]=claySkin(v);
  const geo=roundedCube(S,S*.2,6);
  for(let k=0;k<2;k++){const m=new T.Mesh(geo,[mats[1],mats[1],mats[1],mats[1],mats[1],mats[1]]);m.castShadow=true;m.visible=false;scene.add(m);dice.push(m)}
  const fit=()=>{const w=host.clientWidth,h=host.clientHeight;if(!w||!h)return;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();draw()};
  new ResizeObserver(fit).observe(host);fit();
}
function draw(){renderer&&renderer.render(scene,camera)}

// local face normals in BoxGeometry material order (+x,-x,+y,-y,+z,-z)
const N=[[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]], OPP=[1,0,3,2,5,4];
function upFace(q){let best=0,by=-9;N.forEach((n,i)=>{const v=new C.Vec3(n[0],n[1],n[2]);const w=q.vmult(v);if(w.y>by){by=w.y;best=i}});return best}
function paint(mesh,up,val){ // val on the up face, 7-val underneath, the other two pairs around the sides
  const rest=[1,2,3,4,5,6].filter(x=>x!==val&&x!==7-val),p1=Math.min(...rest),p2=rest.filter(x=>x!==p1&&x!==7-p1)[0];
  const arr=new Array(6);arr[up]=mats[val];arr[OPP[up]]=mats[7-val];
  [0,1,2].filter(ax=>ax!==(up>>1)).forEach((ax,j)=>{const q=j?p2:p1;arr[ax*2]=mats[q];arr[ax*2+1]=mats[7-q]});mesh.material=arr}

function simulate(){
  const w=new C.World({gravity:new C.Vec3(0,-9.8*1.6,0)});w.allowSleep=true;
  const felt=new C.Material('felt'),die=new C.Material('die');
  w.addContactMaterial(new C.ContactMaterial(felt,die,{friction:.32,restitution:.32}));
  w.addContactMaterial(new C.ContactMaterial(die,die,{friction:.2,restitution:.4}));
  const ground=new C.Body({mass:0,material:felt,shape:new C.Plane()});ground.quaternion.setFromEuler(-Math.PI/2,0,0);w.addBody(ground);
  // padded rails all round the felt
  [[0,-FELT.z-.15,FELT.x+.2,.15],[0,FELT.z+.15,FELT.x+.2,.15],[-FELT.x-.15,0,.15,FELT.z+.3],[FELT.x+.15,0,.15,FELT.z+.3]].forEach(([x,z,hx,hz])=>{const b=new C.Body({mass:0,material:felt,shape:new C.Box(new C.Vec3(hx,1,hz))});b.position.set(x,1,z);w.addBody(b)});
  const B=[0,1].map(k=>{const b=new C.Body({mass:1,material:die,shape:new C.Box(new C.Vec3(HALF*.97,HALF*.97,HALF*.97)),linearDamping:.08,angularDamping:.12,sleepSpeedLimit:.12,sleepTimeLimit:.3});
    b.position.set(1.05+k*.22,1.75-k*.12,.05+k*.12);
    b.quaternion.setFromEuler(Math.random()*6.3,Math.random()*6.3,Math.random()*6.3);
    b.velocity.set(-(2.7+Math.random()*1.1),1.0+Math.random()*.8,.25+Math.random()*.6);
    b.angularVelocity.set((Math.random()-.5)*28,(Math.random()-.5)*18,(Math.random()-.5)*28);w.addBody(b);return b});
  const F=[];const dt=1/60;
  for(let i=0;i<60*5;i++){w.step(dt);F.push(B.map(b=>[b.position.x,b.position.y,b.position.z,b.quaternion.x,b.quaternion.y,b.quaternion.z,b.quaternion.w]));
    if(i>40&&B.every(b=>b.sleepState===C.Body.SLEEPING))break}
  // judge the result: each die must be flat (one face clearly up) and on the felt
  // score the result: flat on a face, in front of the Peddler's hands, not buried in a corner
  let pen=0;B.forEach(b=>{const u=b.quaternion.vmult(new C.Vec3(...N[upFace(b.quaternion)]));pen+=(1-u.y)*40;
    const x=b.position.x,z=b.position.z;pen+=Math.max(0,-1.05-x)+Math.max(0,x-.9)+Math.max(0,-.05-z)*3+Math.max(0,z-.45)});
  return {F,ok:pen<.02,pen,up:B.map(b=>upFace(b.quaternion))};
}

export async function load(dz){
  if(!ready) ready=(async()=>{[T,C]=await Promise.all([import(THREE_URL),import(CANNON_URL)]);init(dz)})();
  return ready;
}
export function clear(){cancelAnimationFrame(raf);dice.forEach(d=>d.visible=false);draw()}
// throws a and b; onLand fires when both are still. Returns false if 3D isn't available.
export function toss(a,b,onLand,speed=1){
  if(!renderer) return false;
  cancelAnimationFrame(raf);
  let r=null;for(let t=0;t<40;t++){const q=simulate();if(!r||q.pen<r.pen)r=q;if(q.ok)break}
  paint(dice[0],r.up[0],a);paint(dice[1],r.up[1],b);
  dice.forEach(d=>d.visible=true);
  const F=r.F,t0=performance.now();let landed=false;
  const step=now=>{const i=Math.max(0,Math.min(F.length-1,Math.floor((now-t0)/1000*60*speed)));
    F[i].forEach((s,k)=>{dice[k].position.set(s[0],s[1],s[2]);dice[k].quaternion.set(s[3],s[4],s[5],s[6])});draw();
    if(i<F.length-1) raf=requestAnimationFrame(step); else if(!landed){landed=true;onLand&&onLand()}};
  raf=requestAnimationFrame(step);return true;
}
