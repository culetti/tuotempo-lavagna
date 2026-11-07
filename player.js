/* POC v2 extended: same canvas world + masked reveal, explicit cancellable playback. */
'use strict';
const DATA=JSON.parse(document.getElementById('scene-data').textContent);
const $=id=>document.getElementById(id),ctx=$('cv').getContext('2d');
const W=1920,H=1080,RED='#bd282b';
let lang='en',runToken=0,waiter=null,currentCue=null,currentSection=null,phase='loading',hand=null,audio=null,finalProgress=0;
let nameGag=null;let cam={cx:900,cy:480,w:2000},objects={},handImage=null,startAt=0;
const speed=Math.max(.02,Math.min(20,Number(new URLSearchParams(location.search).get('speed'))||1));
const ease=t=>t<.5?2*t*t:1-Math.pow(-2*t+2,2)/2;
class Cancelled extends Error{}
function loadImage(src){return new Promise((res,rej)=>{const im=new Image();im.onload=()=>res(im);im.onerror=()=>rej(new Error('Immagine non caricabile: '+src.slice(0,80)));im.src=src;});}
function setPhase(p){phase=p;document.body.dataset.phase=p;updateStatus();}
function updateStatus(){const names={loading:'Caricamento…',ready:'Pronto · EN',camera:'',drawing:'',hold:'',photo:'In pausa',name:'Il nome',final:'',ended:'Lavagna completa · R per ricominciare'};$('status').textContent=names[phase]??'';if(currentCue&&['drawing','hold'].includes(phase))$('status').textContent=lang.toUpperCase()+(audio?' · voce':' · senza voce');}
function subtitle(cue=currentCue){showSubtitleAt(cue, cue===currentCue?subProgress:0);}
let subProgress=0;
function splitSubtitle(text, maxLen=72){
 const raw=String(text||'').replace(/\s+/g,' ').trim();
 if(!raw)return [''];
 if(raw.length<=maxLen)return [raw];
 const chunks=[];
 let remaining=raw;
 const minCut=Math.max(20, Math.floor(maxLen*0.38));
 while(remaining.length>maxLen){
  const slice=remaining.slice(0, maxLen+1);
  let cut=-1;
  const re=/[.!?;:]["”')\]]?(?=\s|$)|,\s*| — | – | - /g;
  let m,last=-1;
  while((m=re.exec(slice))){
   const end=m.index+m[0].length;
   if(end<=maxLen && m.index>=minCut) last=end;
  }
  if(last>0) cut=last;
  else{
   const space=slice.lastIndexOf(' ', maxLen);
   cut=space>=minCut?space:maxLen;
  }
  chunks.push(remaining.slice(0,cut).trim());
  remaining=remaining.slice(cut).trim();
 }
 if(remaining) chunks.push(remaining);
 for(let i=chunks.length-1;i>0;i--){
  if(chunks[i].length<16 && chunks[i-1].length+1+chunks[i].length<=maxLen+24){
   chunks[i-1]+=' '+chunks[i];
   chunks.splice(i,1);
  }
 }
 return chunks.length?chunks:[''];
}
function showSubtitleAt(cue, t){
 currentCue=cue;
 subProgress=Math.min(1, Math.max(0, Number(t)||0));
 const el=$('sub');
 if(!cue){el.textContent='';el.classList.remove('on');updateStatus();return;}
 const chunks=splitSubtitle(cue[lang]||'');
 const weights=chunks.map(c=>Math.max(10,c.length));
 const total=weights.reduce((a,b)=>a+b,0)||1;
 let acc=0, idx=chunks.length-1;
 const p=Math.min(0.999, subProgress)*total;
 for(let i=0;i<chunks.length;i++){acc+=weights[i];if(p<acc){idx=i;break;}}
 const next=chunks[idx]||'';
 if(el.textContent!==next) el.textContent=next;
 el.classList.toggle('on',!!next);
 updateStatus();
}
function cueProgress(cue, t, sectionAudio){
 if(cue&&cue.start!=null&&cue.end!=null&&sectionAudio&&Number.isFinite(sectionAudio.currentTime)){
  return (sectionAudio.currentTime-cue.start)/Math.max(0.05, cue.end-cue.start);
 }
 return t;
}
function check(token){if(token!==runToken)throw new Cancelled();}
function tween(ms,fn,token){return new Promise((resolve,reject)=>{const t0=performance.now();function tick(now){if(token!==runToken)return reject(new Cancelled());const t=Math.min(1,(now-t0)/(ms/speed));fn(t);render();if(t<1)requestAnimationFrame(tick);else resolve();}requestAnimationFrame(tick);});}
async function moveCamera(target,token,ms=560){setPhase('camera');const from={...cam};await tween(ms,t=>{const e=ease(t);for(const k of ['cx','cy','w'])cam[k]=from[k]+(target[k]-from[k])*e;},token);}
function cameraFor(o){const height=o.h*o.scale;const width=Math.max(o.width*1.14,height*1.7778*1.28);return {cx:o.x+o.width/2,cy:o.y+height/2+height*.055,w:width};}
function render(){ctx.setTransform(1,0,0,1,0,0);ctx.fillStyle='#fff';ctx.fillRect(0,0,W,H);const z=W/cam.w;ctx.setTransform(z,0,0,z,W/2-cam.cx*z,H/2-cam.cy*z);
 // Each group is part of the same permanent whiteboard, never a slide replacement.
 for(const o of Object.values(objects)){if(!o.shown)continue;if(o.dirty){const c=o.comp.getContext('2d');c.globalCompositeOperation='copy';c.drawImage(o.mask,0,0);c.globalCompositeOperation='source-in';c.drawImage(o.image,0,0);o.dirty=false;}ctx.drawImage(o.comp,o.x,o.y,o.width,o.h*o.scale);}
 ctx.fillStyle=RED;ctx.font='54px Hand';
 const labels=[['origins','1 · Bologna → Valencia',90,105],['football','2 · L’idea del calcetto',2130,105],['remote','3 · Nati da remoto',2130,1400],['dentist','4 · Client number one',110,1400]];
 for(const [id,text,x,y] of labels){if(DATA.sections.find(s=>s.id===id).art.some(a=>objects[a].shown))ctx.fillText(text,x,y);}
 if(finalProgress>0){const p=DATA.final.tooth;ctx.strokeStyle=RED;ctx.lineWidth=8;ctx.lineCap='round';ctx.beginPath();ctx.ellipse(p.x,p.y,p.rx,p.ry,-.13,-Math.PI/2,-Math.PI/2+Math.PI*2*Math.min(1,finalProgress*1.6));ctx.stroke();if(finalProgress>.65){ctx.font='72px Hand';ctx.fillStyle=RED;const text=DATA.final.years;ctx.fillText(text.slice(0,Math.ceil((finalProgress-.65)/.35*text.length)),1800,2480);}}
 if(nameGag?.frame.label){const f=nameGag.frame;ctx.save();ctx.globalAlpha=f.alpha;ctx.translate(nameGag.cx,nameGag.cy+22+f.offset);ctx.font='64px Hand';ctx.fillStyle='#333';ctx.textAlign='center';ctx.fillText(f.label,0,0);if(f.cut>0){const w=ctx.measureText(f.label).width;ctx.strokeStyle=RED;ctx.lineWidth=4;ctx.beginPath();ctx.moveTo(-w/2-6,-18);ctx.lineTo(-w/2-6+(w+12)*f.cut,-15);ctx.stroke();}ctx.restore();}
 if(hand&&handImage){ctx.save();ctx.translate(hand.x,hand.y);ctx.rotate(DATA.hand.rotation);const hs=DATA.hand.width/handImage.width/(Math.max(1,z*.48));ctx.drawImage(handImage,-DATA.hand.tip[0]*hs,-DATA.hand.tip[1]*hs,handImage.width*hs,handImage.height*hs);ctx.restore();}
}
function prepareSegments(o){const segs=[];let prev=null,total=0;for(const p of o.path){if(p===null){prev=null;continue;}if(prev){const len=Math.hypot(p[0]-prev[0],p[1]-prev[1]);if(len){segs.push({a:prev,b:p,len,start:total});total+=len;}}prev=p;}o.segments=segs;o.total=total;o.drawn=0;o.si=0;}
function revealTo(o,progress){o.shown=true;const m=o.mask.getContext('2d');m.strokeStyle='#000';m.lineWidth=o.radius*2.1;m.lineCap='round';m.lineJoin='round';const target=o.total*progress;let point=null;
 while(o.si<o.segments.length){const s=o.segments[o.si];if(s.start>target)break;const f=Math.min(1,(target-s.start)/s.len);const p=[s.a[0]+(s.b[0]-s.a[0])*f,s.a[1]+(s.b[1]-s.a[1])*f];m.beginPath();m.moveTo(...s.a);m.lineTo(...p);m.stroke();point=p;if(f>=1)o.si++;else break;}
 if(progress>=1){m.fillStyle='#000';m.fillRect(0,0,o.w,o.h);}o.progress=progress;o.dirty=true;if(point)hand={x:o.x+point[0]*o.scale,y:o.y+point[1]*o.scale};
}
function clearAudio(){if(audio){audio.pause();audio.currentTime=0;audio=null;}}
async function startAudio(section,token){if(!section.audio)return null;const a=new Audio(section.audio);a.playbackRate=speed;audio=a;try{await a.play();check(token);return a;}catch(e){if(e instanceof Cancelled)throw e;clearAudio();$('status').textContent='Audio non disponibile · sottotitoli attivi';return null;}}
function waitForNext(token){check(token);return new Promise((resolve,reject)=>{waiter={token,resolve,reject};});}
async function showPhoto(section,token){check(token);clearAudio();subtitle(null);hand=null;render();const ph=section.photo;$('pol').className='pol '+ph.kind;$('photoContent').replaceChildren();
 if(ph.src){const img=document.createElement('img');img.src=ph.src;img.alt=ph.caption;$('photoContent').append(img);}else{const box=document.createElement('div');box.className='missing';const strong=document.createElement('strong');strong.textContent=ph.display;const span=document.createElement('span');span.textContent=ph.disclosure;box.append(strong,span);$('photoContent').append(box);}
 $('caption').textContent=ph.caption;$('disclosure').textContent=ph.disclosure||'';$('photo').classList.add('on');setPhase('photo');
 if(ph.intro){const introCue={en:ph.intro.en,it:ph.intro.it};showSubtitleAt(introCue,0);if(ph.introAudio){const a=new Audio(ph.introAudio);a.playbackRate=speed;audio=a;try{await a.play();check(token);}catch(e){if(e instanceof Cancelled)throw e;clearAudio();}if(audio&&Number.isFinite(audio.duration)){const left=Math.max(0,(audio.duration-audio.currentTime)*1000);if(left>80)await tween(left,t=>{const p=audio&&Number.isFinite(audio.duration)&&audio.duration>0?audio.currentTime/audio.duration:t;showSubtitleAt(introCue,p);},token);}clearAudio();}}
 await waitForNext(token);check(token);$('photo').classList.remove('on');subtitle(null);
}
// Pure time-based filter: remembered alternatives, not a claimed historical order.
function nameFilterFrame(section,seconds){
 const stop=section.cues[section.cues.length-1].start;
 const index=section.cues.findIndex(c=>seconds<c.end),cueIndex=index<0?section.cues.length-1:index;
 if(seconds>=stop)return {cueIndex,label:null,offset:0,alpha:0,cut:0,final:Math.min(1,(seconds-stop)/section.nameSequence.finalReveal)};
 const period=section.nameSequence.interval,step=Math.floor(Math.max(0,seconds)/period),p=(Math.max(0,seconds)%period)/period;
 const names=section.candidateNames;
 return {cueIndex,label:names[step%names.length],offset:(.5-p)*34,alpha:Math.min(1,p/.12,(1-p)/.12),cut:Math.min(1,Math.max(0,(p-.65)/.25)),final:0};
}
async function nameStop(section,token){subtitle(null);const o=objects.name;
 // Focus the actual lettering (the source image includes a wide blank margin).
 const points=o.path.filter(Boolean),xs=points.map(p=>p[0]),ys=points.map(p=>p[1]);
 const cx=o.x+(Math.min(...xs)+Math.max(...xs))/2*o.scale,cy=o.y+(Math.min(...ys)+Math.max(...ys))/2*o.scale;
 await moveCamera({cx,cy,w:900},token);
 nameGag={cx,cy,frame:nameFilterFrame(section,0)};
 subtitle(section.cues[0]);setPhase('drawing');const a=await startAudio(section,token);
 const total=(a&&Number.isFinite(a.duration)&&a.duration>0?a.duration:section.audioDuration)*1000;
 await tween(total,t=>{const seconds=a&&Number.isFinite(a.duration)?a.currentTime:t*total/1000;
  nameGag.frame=nameFilterFrame(section,seconds);
  const cue=section.cues[nameGag.frame.cueIndex];const local=cue&&cue.start!=null&&cue.end!=null?(seconds-cue.start)/Math.max(0.05,cue.end-cue.start):0;showSubtitleAt(cue, local);
  if(nameGag.frame.final>0)revealTo(o,nameGag.frame.final);
 },token);
 revealTo(o,1);hand=null;nameGag=null;render();clearAudio();subtitle(null);setPhase('name');await waitForNext(token);check(token);subtitle(null);}
async function playSection(section,token){currentSection=section;$('chapter').textContent='';
 if(section.id==='name'){await nameStop(section,token);return;}
 // All subtitle timings are editable. Optional cue.start/end override proportional local audio timing.
 let activeArt=null,sectionAudio=null;const totalTime=section.cues.reduce((s,c)=>s+c.duration,0);let durationFactor=1;
 const totals={};for(const c of section.cues)totals[c.art]=(totals[c.art]||0)+c.duration;
 const played={};
 if(section.cues.length){sectionAudio=await startAudio(section,token);if(sectionAudio&&Number.isFinite(sectionAudio.duration)&&sectionAudio.duration>0)durationFactor=sectionAudio.duration/totalTime;}
 for(let i=0;i<section.cues.length;i++){check(token);const cue=section.cues[i],o=objects[cue.art];
  if(activeArt!==cue.art){subtitle(null);await moveCamera(cameraFor(o),token);activeArt=cue.art;}
  check(token);showSubtitleAt(cue,0);setPhase('drawing');const from=o.progress||0;played[cue.art]=(played[cue.art]||0)+cue.duration;const target=Math.min(1,played[cue.art]/totals[cue.art]);
  let duration=(cue.start!=null&&cue.end!=null)?(cue.end-cue.start)*1000:cue.duration*durationFactor*1000;
  if(sectionAudio&&Number.isFinite(sectionAudio.currentTime)&&cue.end!=null)duration=Math.max(160,(cue.end-sectionAudio.currentTime)*1000);
  const revealSpan=Math.max(0,target-from);
  const drawMs=revealSpan>0.002?duration:(sectionAudio?0:Math.min(duration,Math.max(200,1850)));
  const followSub=t=>{showSubtitleAt(cue, cueProgress(cue,t,sectionAudio));};
  if(drawMs)await tween(drawMs,t=>{revealTo(o,from+revealSpan*t);followSub(t);},token);
  else {revealTo(o,target);render();if(sectionAudio&&duration>30)await tween(duration,followSub,token);}
  const nextSame=i+1<section.cues.length&&section.cues[i+1].art===cue.art;
  if(!nextSame){hand=null;render();}
 }
 // Keep images not referenced by a subtitle visible only if explicitly in section.art.
 for(const key of section.art){if(!objects[key].shown){await moveCamera(cameraFor(objects[key]),token);await tween(850,t=>revealTo(objects[key],t),token);}}
 if(sectionAudio&&Number.isFinite(sectionAudio.duration)){
  const left=Math.max(0,(sectionAudio.duration-sectionAudio.currentTime)*1000);
  if(left>80)await tween(left,()=>{},token);
 }
 await showPhoto(section,token);
}
async function finale(token){subtitle(null);$('chapter').textContent='';await moveCamera({cx:DATA.board.width/2,cy:DATA.board.height/2,w:Math.max(DATA.board.width+220,(DATA.board.height+180)*16/9)},token,1100);setPhase('final');await tween(1300,t=>{finalProgress=t;const p=DATA.final.tooth;if(t<.65){const a=-Math.PI/2+t/.65*Math.PI*2;hand={x:p.x+Math.cos(a)*p.rx,y:p.y+Math.sin(a)*p.ry};}else hand={x:1800+(t-.65)/.35*340,y:2460};},token);hand=null;render();setPhase('ended');$('progress').style.width='100%';}
function cancel(){runToken++;if(waiter){waiter.reject(new Cancelled());waiter=null;}clearAudio();hand=null;}
async function run(){cancel();const token=runToken;startAt=performance.now();currentCue=null;currentSection=null;finalProgress=0;for(const o of Object.values(objects)){o.mask.getContext('2d').clearRect(0,0,o.w,o.h);o.shown=false;o.dirty=true;o.progress=0;o.si=0;}
 $('photo').classList.remove('on');nameGag=null;$('start').style.display='none';$('frame').classList.add('clean');$('progress').style.width='0';cam={cx:900,cy:480,w:2000};render();
 try{for(let i=0;i<DATA.sections.length;i++){check(token);await playSection(DATA.sections[i],token);$('progress').style.width=((i+1)/DATA.sections.length*95)+'%';}await finale(token);}catch(e){if(!(e instanceof Cancelled))showError(e);}
}
function next(){if(phase==='loading')return;if(phase==='ready'){run();return;}if(waiter){const w=waiter;waiter=null;if(w.token===runToken){setPhase('camera');w.resolve();}}}
function toggleLanguage(){lang=lang==='en'?'it':'en';subtitle();$('langBtn').textContent=lang.toUpperCase()+' · cambia lingua';}
function showError(e){console.error(e);cancel();$('error').style.display='block';$('error').textContent='Impossibile aprire la lavagna: '+e.message;setPhase('error');}
async function init(){try{const entries=await Promise.all(Object.entries(DATA.art).map(async([key,a])=>{const image=await loadImage(a.src),mask=document.createElement('canvas'),comp=document.createElement('canvas');mask.width=comp.width=a.w;mask.height=comp.height=a.h;const o={...a,image,mask,comp,scale:a.width/a.w,dirty:true,shown:false,progress:0};prepareSegments(o);return [key,o];}));objects=Object.fromEntries(entries);handImage=await loadImage(DATA.hand.src);await document.fonts.ready;$('loading').style.display='none';setPhase('ready');render();}catch(e){showError(e);}}
$('frame').addEventListener('click',e=>{if(!e.target.closest('#toolbar'))next();});
$('nextBtn').onclick=next;$('resetBtn').onclick=()=>{if(phase!=='loading')run();};$('langBtn').onclick=toggleLanguage;
function fullscreen(){if(document.fullscreenElement){if(document.exitFullscreen)document.exitFullscreen().catch(()=>{});}else if($('frame').requestFullscreen)$('frame').requestFullscreen().catch(()=>{});}
$('fullBtn').onclick=fullscreen;$('hideBtn').onclick=()=>$('frame').classList.toggle('clean');
document.addEventListener('keydown',e=>{if(e.repeat||e.altKey||e.ctrlKey||e.metaKey||['INPUT','TEXTAREA','SELECT'].includes(e.target.tagName))return;const k=e.key.toLowerCase();if(e.code==='Space'||e.key==='ArrowRight'){e.preventDefault();next();}else if(k==='r'){e.preventDefault();if(phase!=='loading')run();}else if(k==='i')toggleLanguage();else if(k==='f')fullscreen();else if(k==='h')$('frame').classList.toggle('clean');});
// Read-only diagnostics for local verification; no network, telemetry or external API.
window.Whiteboard={getState:()=>({waiting:!!waiter,phase,lang,section:currentSection?.id,cue:currentCue?.en,token:runToken,shown:Object.keys(objects).filter(k=>objects[k].shown),cam:{...cam},nameFilter:nameGag?{...nameGag.frame}:null,finalProgress}),next,restart:run,toggleLanguage};
init();
