// The promo clip (scene 2.1 stop, assets/memo2007-agenda-clip.mp4) must be heard ONLY in its own stop:
// during the first seconds of scene 1.1 no clip media may be playing or audible — on first start, after R,
// after ←/→ jumps out of the clip, and when opening a Share link. Also: it still plays with sound in its stop.
const {chromium}=require('/workspace/tuotempo-lavagna1/tools/node_modules/playwright');
const URL=process.env.URL||'file:///workspace/tuotempo-lavagna1/index.html';
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
let fails=0;const ok=(c,m)=>{console.log((c?'OK  ':'FAIL')+' '+m);if(!c)fails++;};const errs=[];
const hook=()=>{window.__clipLog=[];window.__media=[];const isClip=m=>/^data:video|\.mp4/.test(m.currentSrc||m.src||'');
 const watch=m=>{__media.push(m);['play','playing','timeupdate','volumechange'].forEach(ev=>m.addEventListener(ev,()=>{if(!isClip(m))return;const st=window.Whiteboard?Whiteboard.getState():{};
  __clipLog.push({ev,t:+m.currentTime.toFixed(2),paused:m.paused,audible:!m.paused&&!m.muted&&m.volume>0,section:st.section,phase:st.phase,now:performance.now()|0});}));};
 const oc=document.createElement.bind(document);document.createElement=function(t,...a){const e=oc(t,...a);if(/^(video|audio)$/i.test(t))watch(e);return e;};
 const OA=window.Audio;window.Audio=function(s){const a=new OA(s);watch(a);return a;};window.Audio.prototype=OA.prototype;};
const open=async h=>{const p=await b.newPage({viewport:{width:1920,height:1080}});p.on('pageerror',e=>errs.push(e.message));await p.addInitScript(hook);await p.goto(URL+(h||''));
 await p.waitForFunction(()=>window.Whiteboard&&Whiteboard.getState().phase==='ready',null,{timeout:120000});await p.waitForTimeout(300);return p;};
// samples every 100 ms for ms: any clip element playing / audible / advancing, plus 'playing' events in the window
const silent=async(p,ms,label)=>{await p.evaluate(()=>{window.__mark=__clipLog.length;});const bad=[];let secs=new Set();
 for(let t=0;t<ms;t+=100){const s=await p.evaluate(()=>({sec:Whiteboard.getState().section,m:__media.filter(m=>/^data:video|\.mp4/.test(m.currentSrc||m.src||'')).map(m=>({paused:m.paused,muted:m.muted,vol:m.volume,t:m.currentTime}))}));
  secs.add(s.sec);for(const m of s.m)if(!m.paused||m.t>0.05)bad.push({at:t,...m});await p.waitForTimeout(100);}
 const ev=await p.evaluate(()=>__clipLog.slice(__mark).filter(e=>e.ev!=='volumechange'&&(e.ev==='playing'||!e.paused)));
 ok(bad.length===0&&ev.length===0,`${label}: no clip playing/audible in ${ms/1000}s of ${[...secs].join(',')}`+(bad.length||ev.length?' '+JSON.stringify({bad:bad.slice(0,3),ev:ev.slice(0,3)}):''));
 return [...secs];};
const goClip=async p=>{const t=await p.evaluate(()=>{const x=FLAT.find(f=>f.sec.id==='l2-clients');return x.start+x.dur-0.05;});await p.evaluate(t=>Whiteboard.seekTo(t),t);
 await p.waitForFunction(()=>Whiteboard.getState().phase==='photo',null,{timeout:20000});await p.waitForTimeout(3200);
 return p.evaluate(()=>{const v=document.querySelector('#photoContent video');return v?{playing:!v.paused,audible:!v.paused&&!v.muted&&v.volume>0,t:v.currentTime}:null;});};
const first=await open();const id11=await first.evaluate(()=>FLAT[0].sec.id);
// 1) first start
await first.mouse.click(960,400);let secs=await silent(first,5000,'first start');ok(secs.every(s=>s===id11),'sampled inside scene 1.1 ('+id11+')');
// 2) the clip in its stop plays with sound
let c=await goClip(first);ok(c&&c.playing&&c.audible&&c.t>0.5,'clip plays with sound in its stop '+JSON.stringify(c));
// 3) R while the clip plays → back to 1.1, silent
await first.keyboard.press('r');await silent(first,5000,'after R');
// 4) → out of the clip, then ← twice back toward the start
c=await goClip(first);await first.keyboard.press('ArrowRight');await silent(first,3000,'after → (out of the clip)');
c=await goClip(first);await first.keyboard.press('ArrowLeft');await silent(first,2500,'after ← (scene restart)');
await first.evaluate(()=>Whiteboard.seekTo(0.5));await first.waitForTimeout(300);await silent(first,4000,'after seek back to 1.1');
await first.close();
// 5) Share links: to 1.1 and to the scene right after the clip
for(const h of ['#s=1.1&t=00:00','#t=00:02']){const p=await open(h);await p.mouse.click(960,400);await silent(p,5000,'share link '+h);await p.close();}
{const p=await open();const link=await p.evaluate(()=>{const x=FLAT.findIndex(f=>f.sec.id==='l2-clients');return '#s='+sceneNo(FLAT[x+1])+'&t=00:00';});await p.close();
 const q=await open(link.replace('&t=00:00',''));await q.mouse.click(960,400);await silent(q,4000,'share link '+link.replace('&t=00:00','')+' (after the clip)');await q.close();}
ok(errs.length===0,'no page errors '+JSON.stringify(errs));console.log(fails?'FAILS '+fails:'ALL OK');await b.close();process.exit(fails?1:0);})();
