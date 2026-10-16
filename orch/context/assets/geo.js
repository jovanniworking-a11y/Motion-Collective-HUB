const FLOOR = "__FLOOR__";
const G = __GEOM__;
const S = 0.875 * 0.0254, CX = 455, CY = 295, H = 2.74;        // metres per plan px (0.875 in/px, from bed + door sizes), plan centre, 9 ft ceilings
const wx = px => (px - CX) * S, wz = py => (py - CY) * S;

const stage = document.getElementById('stage');
const renderer = new THREE.WebGLRenderer({antialias:true, preserveDrawingBuffer:true});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.outputEncoding = THREE.sRGBEncoding;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
stage.appendChild(renderer.domElement);
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, 1, .05, 400);
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true; controls.maxPolarAngle = Math.PI * .495; controls.minDistance = .3; controls.maxDistance = 40;

const M = {
  wall: new THREE.MeshStandardMaterial({color:0xEDEAE4, roughness:.92}),
  cap:  new THREE.MeshStandardMaterial({color:0x121114, roughness:1}),
  glass:new THREE.MeshStandardMaterial({color:0x9FC3DA, roughness:.05, metalness:.1, transparent:true, opacity:.2, depthWrite:false}),
  frame:new THREE.MeshStandardMaterial({color:0xE8E8E6, roughness:.6}),
  ceil: new THREE.MeshStandardMaterial({color:0xF2F1EE, roughness:.95}),
  granite:new THREE.MeshStandardMaterial({color:0x3A3633, roughness:.35}),
  cherry:new THREE.MeshStandardMaterial({color:0x6A2E1F, roughness:.55}),
  steel:new THREE.MeshStandardMaterial({color:0xBFC2C4, roughness:.3, metalness:.6}),
  black:new THREE.MeshStandardMaterial({color:0x151518, roughness:.45}),
  sofa: new THREE.MeshStandardMaterial({color:0x2B2421, roughness:.5}),          // leather-style
  duvet:new THREE.MeshStandardMaterial({color:0xE7E1D8, roughness:.9}),
  duvet2:new THREE.MeshStandardMaterial({color:0x5A5F66, roughness:.9}),
  wood: new THREE.MeshStandardMaterial({color:0x5C3A28, roughness:.7}),
  rail: new THREE.MeshStandardMaterial({color:0x222326, roughness:.5, metalness:.4}),
  cdj:  new THREE.MeshStandardMaterial({color:0x1E1E22, roughness:.5, emissive:0x6FC8FF, emissiveIntensity:0}),
  djbody:new THREE.MeshStandardMaterial({color:0xA878FF, roughness:.7, emissive:0x3A1C6A, emissiveIntensity:.4}),
  screen:new THREE.MeshStandardMaterial({color:0x0B0C10, roughness:.2}),
};
const box = (w,h,d,mat,x,y,z,parent=scene) => { const m = new THREE.Mesh(new THREE.BoxGeometry(w,h,d), mat); m.position.set(x,y,z); m.castShadow = m.receiveShadow = true; parent.add(m); return m; };
const prect = (x0,y0,x1,y1,h0,h1,mat,parent=scene) => box((x1-x0)*S,h1-h0,(y1-y0)*S,mat,wx((x0+x1)/2),(h0+h1)/2,wz((y0+y1)/2),parent);
// wall slab along a plan segment
function seg(x0,y0,x1,y1,t,h0,h1,mat,parent=scene){
  const L = Math.hypot(x1-x0,y1-y0)*S; const m = box(L,h1-h0,t*S,mat,wx((x0+x1)/2),(h0+h1)/2,wz((y0+y1)/2),parent);
  m.rotation.y = -Math.atan2(y1-y0,x1-x0); return m; }
// extruded polygon (counters, closets, island, sofa)
function poly(pts,h0,h1,mat,parent=scene){
  const sh = new THREE.Shape(pts.map(([x,y])=>new THREE.Vector2(wx(x),-wz(y))));
  const g = new THREE.ExtrudeGeometry(sh,{depth:h1-h0,bevelEnabled:false}); g.rotateX(-Math.PI/2); g.translate(0,h0,0);
  const m = new THREE.Mesh(g,mat); m.castShadow = m.receiveShadow = true; parent.add(m); return m; }

/* floor (plan texture) */
const floorTex = new THREE.TextureLoader().load(FLOOR, t => { t.encoding = THREE.sRGBEncoding; t.anisotropy = renderer.capabilities.getMaxAnisotropy(); });
const floor = new THREE.Mesh(new THREE.PlaneGeometry(927*S, 615*S), new THREE.MeshStandardMaterial({map:floorTex, transparent:true, alphaTest:.5, roughness:.7}));
floor.rotation.x = -Math.PI/2; floor.position.set(wx(463.5), 0, wz(307.5)); floor.receiveShadow = true; scene.add(floor);

/* walls: [x0,y0,x1,y1,kind]  w = wall, g = window, d = glass door */
const SILL = .5, HEAD = 2.3;
for (const [x0,y0,x1,y1,k,t0] of G.walls){
  const t = t0 || (k==='i' ? 5 : 8), mat = M.wall;
  if (k==='w' || k==='i'){ seg(x0,y0,x1,y1,t,0,H,mat); seg(x0,y0,x1,y1,t,H,H+.004,M.cap); continue; }
  const lo = k==='d' ? 0 : SILL;
  if (lo > 0) seg(x0,y0,x1,y1,t,0,lo,mat);
  seg(x0,y0,x1,y1,t,HEAD,H,mat); seg(x0,y0,x1,y1,t,H,H+.004,M.cap);
  const gl = seg(x0,y0,x1,y1,1.2,lo,HEAD,M.glass); gl.castShadow = false;
  const n = Math.max(1, Math.round(Math.hypot(x1-x0,y1-y0)*S/1.1));
  for (let i=0;i<=n;i++){ const px=x0+(x1-x0)*i/n, py=y0+(y1-y0)*i/n; const f = seg(px-(x1-x0)/Math.hypot(x1-x0,y1-y0)*1.5,py-(y1-y0)/Math.hypot(x1-x0,y1-y0)*1.5,px+(x1-x0)/Math.hypot(x1-x0,y1-y0)*1.5,py+(y1-y0)/Math.hypot(x1-x0,y1-y0)*1.5,t*.8,lo,HEAD,M.frame); }
}
// ceiling (faces down)
const ceilShape = new THREE.Shape(G.ext.map(([x,y])=>new THREE.Vector2(wx(x),-wz(y))));
const ceil = new THREE.Mesh(new THREE.ShapeGeometry(ceilShape), new THREE.MeshStandardMaterial({color:0xF2F1EE, roughness:.95, side:THREE.BackSide}));
ceil.rotation.x = -Math.PI/2; ceil.position.y = H; scene.add(ceil);
// balcony railing
{ const b = G.balc; const outer = [[b[0],b[3]],[b[3],b[2]]];   // the two outer edges? use all edges facing out
  for (const [p,q] of [[b[3],b[0]]]) {} }
seg(G.balc[0][0],G.balc[0][1],G.balc[3][0],G.balc[3][1],2,0,1.07,M.glass);
seg(G.balc[0][0],G.balc[0][1],G.balc[3][0],G.balc[3][1],2,1.04,1.08,M.rail);

/* fixed furniture */
for (const [k,p] of Object.entries(G.fixed)){
  if (k==='island'){ poly(p,0,.9,M.cherry); poly(p,.9,.94,M.granite); continue; }
  if (k==='fridge'){ poly(p,0,1.8,M.steel); continue; }
  if (k.startsWith('counter')){ poly(p,0,.9,M.cherry); poly(p,.9,.94,M.granite); continue; }
  poly(p,0,H,M.wall);   // pantry / coat closet
}
// upper cherry cabinets along the right wall + chamfer
prect(795,400,812,452,1.45,2.2,M.cherry);
// bedrooms: beds + desks + dressers (furnished: full bed, nightstand, dresser, desk + chair)
function bed(x0,y0,x1,y1,head,duv){ prect(x0,y0,x1,y1,0,.28,M.wood); prect(x0+2,y0+2,x1-2,y1-2,.28,.55,duv);
  const hb = {w:[x0-3,y0,x0+3,y1],e:[x1-3,y0,x1+3,y1],s:[x0,y1-3,x1,y1+3],n:[x0,y0-3,x1,y0+3]}[head]; prect(...hb,0,1.0,M.wood); }
for (const b of G.beds) bed(...b);
for (const r of G.desks) prect(...r,.72,.76,M.wood);
for (const r of G.dressers) prect(...r,0,.8,M.wood);

/* movable: leather-style sofa, coffee table, entertainment center */
const sofas = new THREE.Group(); scene.add(sofas);
poly(G.sofa,0,.44,M.sofa,sofas); poly(G.sofaBack,0,.82,M.sofa,sofas);
poly(G.coffee,0,.42,M.wood,sofas); poly(G.tv,0,.55,M.wood,sofas);

/* party: decks mid-floor, tops on stands, sub under the table */
const party = new THREE.Group(); scene.add(party);
const D = G.deck;
prect(D[0],D[1],D[2],D[3],.9,.95,M.black,party);
for (const [dx,dy] of [[D[0]+2,D[1]+2],[D[2]-5,D[1]+2],[D[0]+2,D[3]-5],[D[2]-5,D[3]-5]]) prect(dx,dy,dx+3,dy+3,0,.9,M.black,party);
prect(D[0]+4,D[1]+6,D[2]-4,D[3]-6,.1,.55,M.black,party);
const players = []; const L = D[3]-D[1];
for (const [a,b] of [[.12,.34],[.39,.61],[.66,.88]]) players.push(prect(D[0]+6,D[1]+L*a,D[2]-6,D[1]+L*b,.95,1.03,M.cdj,party));
for (const [x,y] of G.tops){ prect(x-8,y-8,x+8,y+8,0,1.25,M.black,party); prect(x-10,y-10,x+10,y+10,1.25,1.85,M.black,party); }
function person(x,z,mat,parent,h=1.72){ const g = new THREE.Group(); g.position.set(x,0,z);
  const b = new THREE.Mesh(new THREE.CapsuleGeometry(.19,h-.62,4,10), mat); b.position.y = (h-.25)/2+.02; b.castShadow = true; g.add(b);
  const hd = new THREE.Mesh(new THREE.SphereGeometry(.11,14,10), mat); hd.position.y = h-.13; hd.castShadow = true; g.add(hd); parent.add(g); return g; }
for (const [x,y] of G.djs) person(wx(x),wz(y),M.djbody,party);
const DC = [(D[0]+D[2])/2,(D[1]+D[3])/2];
const deckGlow = new THREE.PointLight(0x9EC8FF, 0, 3.2, 2); deckGlow.position.set(wx(DC[0]), 1.6, wz(DC[1])); party.add(deckGlow);
const fan = new THREE.Group(); scene.add(fan);

/* crowd + clear floor */
const crowd = new THREE.Group(); scene.add(crowd);
const inPoly = (x,y,p) => { let c=false; for (let i=0,j=p.length-1;i<p.length;j=i++){ const [xi,yi]=p[i],[xj,yj]=p[j];
  if ((yi>y)!==(yj>y) && x < (xj-xi)*(y-yi)/(yj-yi)+xi) c=!c; } return c; };
const ROOMS = Object.values(G.rooms), FIX = Object.values(G.fixed);
function blocked(x,y){
  if (!inPoly(x,y,G.ext) || ROOMS.some(p=>inPoly(x,y,p)) || FIX.some(p=>inPoly(x,y,p))) return true;
  if (ui.sofas && [G.sofa,G.sofaBack,G.coffee,G.tv].some(p=>inPoly(x,y,p))) return true;
  if (ui.decks && inPoly(x,y,G.djzone)) return true;
  return false; }
function clearFloor(){ let n=0; const st=3; for (let x=92;x<816;x+=st) for (let y=45;y<546;y+=st) if (!blocked(x,y)) n++;
  const m2 = n*(st*S)**2; return {m2, sqft:m2*10.7639}; }
let rng = 7; const rnd = () => (rng = (rng*16807) % 2147483647) / 2147483647;
function buildCrowd(cap){
  crowd.clear(); if (!ui.crowd) return; rng = 7;
  const cell = Math.sqrt(7/10.7639)/S, cand = [];
  for (let x=92+cell/2;x<816;x+=cell) for (let y=45+cell/2;y<546;y+=cell){
    const jx = x+(rnd()-.5)*cell*.5, jy = y+(rnd()-.5)*cell*.5; if (!blocked(jx,jy)) cand.push([jx,jy]); }
  cand.sort((a,b)=>Math.hypot(a[0]-DC[0],a[1]-DC[1])-Math.hypot(b[0]-DC[0],b[1]-DC[1]));
  const tone = [0x2A2530,0x3A3140,0x232830,0x40333A,0x2E2E36];
  cand.slice(0,cap).forEach(([x,y],i)=>{ const g = person(wx(x),wz(y),new THREE.MeshStandardMaterial({color:tone[i%5],roughness:.85}),crowd,1.58+rnd()*.3);
    g.rotation.y = Math.atan2(wx(DC[0])-wx(x), wz(DC[1])-wz(y)); });
}

/* labels */
const labels = new THREE.Group(); scene.add(labels);
function label(txt, px, py, big){
  const c = document.createElement('canvas'), g = c.getContext('2d'); const fs = big ? 64 : 44;
  g.font = `500 ${fs}px Jost, Futura, sans-serif`; const w = Math.ceil(g.measureText(txt).width) + 40;
  c.width = w; c.height = fs + 30; g.font = `500 ${fs}px Jost, Futura, sans-serif`;
  g.fillStyle = 'rgba(10,8,16,.72)'; g.beginPath(); g.roundRect ? g.roundRect(0,0,w,c.height,c.height/2) : g.rect(0,0,w,c.height); g.fill();
  g.fillStyle = big ? '#C8A8FF' : '#EDE6DA'; g.textBaseline = 'middle'; g.fillText(txt, 20, c.height/2+2);
  const t = new THREE.CanvasTexture(c); t.encoding = THREE.sRGBEncoding;
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({map:t, depthTest:false, transparent:true}));
  const hgt = big ? .5 : .36; sp.scale.set(hgt*w/c.height, hgt, 1); sp.position.set(wx(px), H+.5, wz(py)); sp.renderOrder = 10; labels.add(sp);
}
function drawLabels(){ labels.clear();
  for (const [t,x,y] of G.labels) label(t,x,y,false);
  label(ui.decks ? 'Decks' : 'Living', DC[0], DC[1], true); }

/* sky / city */
function skyline(night){
  const c = document.createElement('canvas'); c.width = 4096; c.height = 1024; const g = c.getContext('2d');
  const gr = g.createLinearGradient(0,0,0,1024);
  if (night){ gr.addColorStop(0,'#05040A'); gr.addColorStop(.62,'#16122A'); gr.addColorStop(1,'#241A2E'); }
  else { gr.addColorStop(0,'#8FB7DA'); gr.addColorStop(.62,'#D5E4EE'); gr.addColorStop(1,'#E7EEF0'); }
  g.fillStyle = gr; g.fillRect(0,0,4096,1024);
  let r = 11; const rr = () => (r = (r*16807)%2147483647)/2147483647;
  for (let x=0;x<4096;){ const w = 40+rr()*150, h = 80+rr()*rr()*300;
    g.fillStyle = night ? `rgb(${14+rr()*10},${12+rr()*8},${24+rr()*12})` : `rgb(${150+rr()*40},${160+rr()*36},${150+rr()*30})`;
    g.fillRect(x, 1024-h, w, h);
    for (let yy=1024-h+10; yy<1020; yy+=14) for (let xx=x+6; xx<x+w-8; xx+=11)
      if (rr() < (night ? .22 : .3)){ g.fillStyle = night ? (rr()<.7?'rgba(255,214,150,.85)':'rgba(170,200,255,.7)') : 'rgba(90,110,130,.35)'; g.fillRect(xx,yy,6,8); }
    x += w + rr()*30; }
  const t = new THREE.CanvasTexture(c); t.encoding = THREE.sRGBEncoding; t.wrapS = THREE.RepeatWrapping; return t;
}
const SKY = {day:skyline(false), night:skyline(true)};
const dome = new THREE.Mesh(new THREE.CylinderGeometry(70,70,50,64,1,true), new THREE.MeshBasicMaterial({map:SKY.day, side:THREE.BackSide}));
dome.position.y = 10; scene.add(dome);
const groundFar = new THREE.Mesh(new THREE.CircleGeometry(70,48), new THREE.MeshBasicMaterial({color:0x101018}));
groundFar.rotation.x = -Math.PI/2; groundFar.position.y = -.02; scene.add(groundFar);

/* lights */
const hemi = new THREE.HemisphereLight(0xEAF2FF, 0x6B5A48, .9); scene.add(hemi);
const sun = new THREE.DirectionalLight(0xFFF3E2, 1.6); sun.position.set(-10, 14, 6); sun.castShadow = true;
sun.shadow.mapSize.set(2048,2048); Object.assign(sun.shadow.camera, {left:-12,right:12,top:12,bottom:-12,near:1,far:60}); sun.shadow.bias = -.0005; scene.add(sun);
const amb = new THREE.AmbientLight(0xffffff, 0); scene.add(amb);
const cityGlow = new THREE.DirectionalLight(0x5B6CB8, 0); cityGlow.position.set(-20, 6, 0); scene.add(cityGlow);
const amberL = G.lightsA.map(([x,y])=>{ const l = new THREE.PointLight(0xFF9A3C, 0, 7, 1.6); l.position.set(wx(x),H-.25,wz(y)); scene.add(l); return l; });
const redL = G.lightsR.map(([x,y])=>{ const l = new THREE.PointLight(0xFF2A1A, 0, 7.5, 1.4); l.position.set(wx(x),H-.3,wz(y)); scene.add(l); return l; });
