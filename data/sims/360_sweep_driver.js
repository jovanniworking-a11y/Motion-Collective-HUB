setTimeout(()=>{ try{
const St=window.__studio, D=St.dbg, G=D.G(); const g=G.grid;
const Q=Math.PI/2, snap=r=>Math.round(r/Q)*Q;
const base=St.items.map(i=>Object.assign({},i));
const others=base.filter(i=>i.type!=='dj_rig'&&i.type!=='speaker');
const N=50, SCR=[1000,8919], REF=Array.from({length:12},(_,k)=>1000+k*7919);
const cx=c=>g.minx+((c%g.nx)+.5)*0.5, cz=c=>g.minz+(((c/g.nx)|0)+.5)*0.5;
const R=v=>Math.round(v*100)/100;
function evalLayout(its,seeds,d360){
  window.__D360=d360; const env=D.buildEnv(its);
  const egIn=env.egressFt*12, restIn=env.restPathFt*12;
  const rs=seeds.map(s=>D.simScore(its,N,s)); const mean=k=>rs.reduce((a,r)=>a+(r[k]||0),0)/rs.length;
  const snd=D.soundReport(its,env);
  const rig=its.find(i=>i.type==='dj_rig'); const f=[Math.sin(rig.rot),Math.cos(rig.rot)];
  let behind=0,total=0; for(let c=0;c<g.N;c++){ if(!env.dance[c])continue; total++; if((cx(c)-rig.x)*f[0]+(cz(c)-rig.z)*f[1]<-3.2) behind++; }
  const sc=rs.map(r=>r.score), m=sc.reduce((a,b)=>a+b,0)/sc.length, sd=Math.sqrt(sc.reduce((a,b)=>a+(b-m)**2,0)/Math.max(1,sc.length-1));
  return {score:R(m),ci:R(sc.length>1?2.2*sd/Math.sqrt(sc.length):0),jam:R(mean('jamMin')),cut:R(mean('cutMin')),trip:R(mean('avgTrip')),qPeak:R(mean('qPeak')),restWait:R(mean('restWait')),dancePeak:R(mean('dancePeak')),
    egIn:R(egIn),restIn:R(restIn),floorSqft:R(total*0.25),behindSqft:R(behind*0.25),soundSd:snd?R(snd.sd):null,djSpill:snd?R(snd.djSpill):null};
}
const rot=snap(Math.atan2(G.n[0],G.n[1]));
const P=(s,n)=>[Math.round((G.wallA[0]+G.u[0]*s+G.n[0]*n)*4)/4, Math.round((G.wallA[1]+G.u[1]*s+G.n[1]*n)*4)/4];
function rigAt(p,r,spk,s,n){
  const f=[Math.sin(r),Math.cos(r)], side=[f[1],-f[0]]; const out=[{id:-11,type:'dj_rig',x:p[0],z:p[1],rot:r}];
  if(spk==='beside'){ for(const k of [-1,1]) out.push({id:-12-(k>0),type:'speaker',x:Math.round((p[0]+side[0]*4.6*k+f[0]*1)*4)/4,z:Math.round((p[1]+side[1]*4.6*k+f[1]*1)*4)/4,rot:r}); }
  else { const a=P(1.25,1.5), b=P(G.wallLen-1.25,1.5); out.push({id:-12,type:'speaker',x:a[0],z:a[1],rot},{id:-13,type:'speaker',x:b[0],z:b[1],rot}); }
  return out;
}

const cands=[];
cands.push({fam:'A wall (current)',its:base,d360:false,spk:'current'});
function spkPair(p,r,spread,ahead,mode){ const f=[Math.sin(r),Math.cos(r)], side=[f[1],-f[0]]; const out=[];
  for(const k of [-1,1]){ const x=Math.round((p[0]+side[0]*spread*k+f[0]*ahead)*4)/4, z=Math.round((p[1]+side[1]*spread*k+f[1]*ahead)*4)/4;
    const rr= mode==='forward'? r : snap(Math.atan2(-side[0]*k,-side[1]*k)); out.push({id:-12-(k>0),type:'speaker',x,z,rot:rr}); } return out; }
for(let s=2;s<=G.wallLen-2+1e-6;s+=0.5) for(const n of [5.25,5.75,6.25,6.75,7.25,7.75]) for(const sp of [3.8,4.6,5.4]) for(const ahead of [0,1]) for(const mode of ['forward','inward']){
  const p=P(s,n); const rig=[{id:-11,type:'dj_rig',x:p[0],z:p[1],rot}].concat(spkPair(p,rot,sp,ahead,mode)); if(!D.rigValid(rig,others)) continue;
  cands.push({fam:'B pulled off wall',s,n,gapBehind:n-3,spk:mode+' '+sp+'ft'+(ahead?' +1':''),its:others.concat(rig),d360:true}); }
for(const c of cands){ window.__D360=c.d360; const env=D.buildEnv(c.its); c.eg=env.egressFt*12; c.rest=env.restPathFt*12; c.ok=c.eg>=36&&c.rest>=30; }
const okc=cands.filter(c=>c.ok&&c.fam!=='A wall (current)');
// screen survivors with 2 seeds, then refine best 5 by score and best 3 by sound
for(const c of okc){ c.r=evalLayout(c.its,SCR,true); }
const byScore=okc.slice().sort((a,b)=>a.r.score-b.r.score).slice(0,5);
const bySound=okc.filter(c=>c.r.soundSd!=null).sort((a,b)=>a.r.soundSd-b.r.soundSd).slice(0,3);
const pick=[cands[0],...new Set([...byScore,...bySound])];
for(const c of pick){ c.ref=evalLayout(c.its,REF,c.d360); }
// geometry for drawing
const shape=(it)=>{ const fp=D.CAT[it.type].fp||[]; const c=Math.cos(it.rot), s=Math.sin(it.rot); return fp.map(f=>({x:it.x+f.cx*c+f.cz*s, z:it.z-f.cx*s+f.cz*c, r:f.r, w:f.w, d:f.d, rot:it.rot})); };
const geo={ext:G.ext,balc:G.balc,rooms:G.rooms,fixed:G.fixed,island:G.island,entry:G.entry,rest:G.rest,wallA:G.wallA,wallB:G.wallB};
const draw=pick.map(c=>{ window.__D360=c.d360; const env=D.buildEnv(c.its); const dc=[]; for(let k=0;k<g.N;k++) if(env.dance[k]) dc.push([R(cx(k)),R(cz(k))]);
  return {its:c.its.filter(i=>!D.CAT[i.type].virtual).map(i=>({type:i.type,shapes:shape(i)})),dance:dc}; });
const out={tested:cands.length-1,passedPaths:okc.length,refined:pick.map((c,i)=>({fam:c.fam,s:c.s,n:c.n,gapBehind:c.gapBehind,spk:c.spk,...c.ref})),geo,draw};
console.log('RESULT '+JSON.stringify(out).replace(/"/g,"'"));
}catch(e){console.log('ERR '+e.message+' '+(e.stack||'').slice(0,300).replace(/"/g,"'"))} },1500);
