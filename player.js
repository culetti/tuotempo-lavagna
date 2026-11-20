/* POC v2 extended: same canvas world + masked reveal, explicit cancellable playback. */
'use strict';
const DATA=JSON.parse(document.getElementById('scene-data').textContent);
const $=id=>document.getElementById(id),ctx=$('cv').getContext('2d');
const W=1920,H=1080,RED='#bd282b';
let lang='en',runToken=0,waiter=null,currentCue=null,currentSection=null,phase='loading',hand=null,audio=null,finalProgress=0,finals={};
// Boards share one world; each has its own marker colour, region and closing mark.
const ALL_BOARDS=DATA.boards||[{id:'lavagna1',years:DATA.final.years,color:RED,sections:DATA.sections.map(s=>s.id),region:{x:0,y:0,w:DATA.board.width,h:DATA.board.height},final:{circle:DATA.final.tooth,yearsAt:[1800,2480]}}];
// Single-board link: ?lavagna=3 or #lavagna3 plays only that board and ends on its own closing.
const ONLY=(()=>{const m=(new URLSearchParams(location.search).get('lavagna')||'').match(/^\d+$/)||location.hash.match(/^#lavagna(\d+)$/i);const n=m&&Number(m[1]??m[0]);return n&&ALL_BOARDS[n-1]?ALL_BOARDS[n-1]:null;})();
const BOARDS=ONLY?[ONLY]:ALL_BOARDS;const PLAY_SECTIONS=BOARDS.reduce((n,b)=>n+b.sections.length,0);
const boardOf=id=>BOARDS.find(b=>b.sections.includes(id))||BOARDS[0];
let nameGag=null;let cam={cx:900,cy:480,w:2000},objects={},handImage=null,startAt=0;
let speed=Math.max(.02,Math.min(20,Number(new URLSearchParams(location.search).get('speed'))||1));
const ease=t=>t<.5?2*t*t:1-Math.pow(-2*t+2,2)/2;
class Cancelled extends Error{}
function loadImage(src){return new Promise((res,rej)=>{const im=new Image();im.onload=()=>res(im);im.onerror=()=>rej(new Error('Immagine non caricabile: '+src.slice(0,80)));im.src=src;});}
function setPhase(p){phase=p;document.body.dataset.phase=p;updateStatus();}
function updateStatus(){const names={loading:'Caricamento…',ready:'Pronto · EN',camera:'',drawing:'',hold:'',photo:'Stop · Spazio per continuare',pause:'Stop · Spazio per continuare',boardEnd:'Fine lavagna · Spazio per continuare',name:'Il nome',final:'',ended:'Lavagne complete · R per ricominciare'};$('status').textContent=names[phase]??'';if(currentCue&&['drawing','hold'].includes(phase))$('status').textContent=lang.toUpperCase()+(audio?' · voce':' · senza voce');}
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
function tween(ms,fn,token){return new Promise((resolve,reject)=>{let last=performance.now(),el=0;function tick(now){if(token!==runToken)return reject(new Cancelled());if(paused){last=now;requestAnimationFrame(tick);return;}el+=Math.max(0,now-last)*speed;last=now;const t=Math.min(1,el/ms);fn(t);render();if(t<1)requestAnimationFrame(tick);else resolve();}requestAnimationFrame(tick);});}
async function moveCamera(target,token,ms=560){setPhase('camera');const from={...cam};await tween(ms,t=>{const e=ease(t);for(const k of ['cx','cy','w'])cam[k]=from[k]+(target[k]-from[k])*e;},token);}
function cameraFor(o){const height=o.h*o.scale;const width=Math.max(o.width*1.14,height*1.7778*1.28);return {cx:o.x+o.width/2,cy:o.y+height/2+height*.055,w:width};}
function drawSheet(g,s){if(s.alpha<=0)return;ctx.save();ctx.globalAlpha=s.alpha;ctx.translate(g.cx+s.dx,g.cy);ctx.rotate(s.rot);ctx.fillStyle='#fffdf6';ctx.strokeStyle='#555';ctx.lineWidth=3;ctx.lineJoin='round';ctx.beginPath();ctx.moveTo(-g.sw/2,-g.sh/2);ctx.lineTo(g.sw/2+3,-g.sh/2+2);ctx.lineTo(g.sw/2,g.sh/2);ctx.lineTo(-g.sw/2-2,g.sh/2-2);ctx.closePath();ctx.fill();ctx.stroke();ctx.restore();}
function drawNameSheets(g){drawSheet(g,g.frame.oldSheet);drawSheet(g,g.frame.newSheet);}
let paperDone=false;
function markPaper(){const L=Object.values(objects);L.forEach((c,j)=>{c.paper=L.slice(0,j).some(a=>{const ix=Math.min(a.x+a.width,c.x+c.width)-Math.max(a.x,c.x),iy=Math.min(a.y+a.h*a.scale,c.y+c.h*c.scale)-Math.max(a.y,c.y);return ix>0&&iy>0&&ix*iy>.2*Math.min(a.width*a.h*a.scale,c.width*c.h*c.scale);});});paperDone=L.length>0;}
function render(){ctx.setTransform(1,0,0,1,0,0);ctx.fillStyle='#fff';ctx.fillRect(0,0,W,H);const z=W/cam.w;ctx.setTransform(z,0,0,z,W/2-cam.cx*z,H/2-cam.cy*z);
 // Each group is part of the same permanent whiteboard, never a slide replacement.
 // Drawings are composited with 'multiply': their white paper never cuts ink already on the board (descenders of g j p q y,
 // accents, lines of a neighbouring drawing); on the white board they look the same. Only a drawing laid largely on top of an
 // earlier one (>20% of the smaller, e.g. Valencia over the map) keeps its opaque paper, so the scene underneath does not show through.
 if(!paperDone)markPaper();
 if(nameGag)drawNameSheets(nameGag);
 for(const o of Object.values(objects)){if(!o.shown)continue;if(o.dirty){const c=o.comp.getContext('2d');c.globalCompositeOperation='copy';c.drawImage(o.mask,0,0);c.globalCompositeOperation='source-in';c.drawImage(o.image,0,0);o.dirty=false;}if(!o.paper)ctx.globalCompositeOperation='multiply';ctx.drawImage(o.comp,o.x,o.y,o.width,o.h*o.scale);ctx.globalCompositeOperation='source-over';}
 ctx.font='54px Hand';
 for(const l of (DATA.labels||[])){const sec=DATA.sections.find(s=>s.id===l.section);if(sec&&(l.small||sec.art.some(a=>objects[a]&&objects[a].shown))){ctx.fillStyle=boardOf(l.section).color;if(l.small){const w=l.write||0;if(w<=0)continue;ctx.font='italic 64px Hand';const tw=ctx.measureText(l.text).width;ctx.save();ctx.beginPath();ctx.rect(l.x-10,l.y-110,(tw+20)*w,180);ctx.clip();ctx.fillText(l.text,l.x,l.y);ctx.restore();}else{ctx.font='54px Hand';ctx.fillText(l.text,l.x,l.y);}}}
 ctx.font='54px Hand';
 for(const b of BOARDS){const fp=finals[b.id]||0;if(fp<=0)continue;const p=b.final.circle,col=b.color;ctx.strokeStyle=col;ctx.lineWidth=8;ctx.lineCap='round';ctx.beginPath();ctx.ellipse(p.x,p.y,p.rx,p.ry,-.13,-Math.PI/2,-Math.PI/2+Math.PI*2*Math.min(1,fp*1.6));ctx.stroke();if(fp>.65){ctx.font='72px Hand';ctx.fillStyle=col;const text=boardLabel(b);ctx.fillText(text.slice(0,Math.ceil((fp-.65)/.35*text.length)),b.final.yearsAt[0],b.final.yearsAt[1]);}}
 drawClosing();
 if(nameGag){const g=nameGag,f=g.frame,lh=Math.min(78,(g.sh-70)/f.list.length),top=g.cy-lh*(f.list.length-1)/2+20;g.hand=null;ctx.save();ctx.font='60px Hand';ctx.textAlign='left';
  if(f.oldSheet.alpha>0){ctx.save();ctx.globalAlpha=f.oldSheet.alpha;ctx.translate(g.cx+f.oldSheet.dx,g.cy);ctx.rotate(f.oldSheet.rot);ctx.translate(-g.cx,-g.cy);
   f.list.forEach((it,i)=>{if(it.write<=0)return;const y=top+i*lh,w=ctx.measureText(it.label).width,x=g.cx-w/2;ctx.save();ctx.beginPath();ctx.rect(x-10,y-Math.max(lh,75),(w+20)*it.write,Math.max(lh,75)+30);ctx.clip();ctx.fillStyle='#333';ctx.fillText(it.label,x,y);ctx.restore();
    if(it.cut>0){ctx.strokeStyle=RED;ctx.lineWidth=5;ctx.lineCap='round';ctx.beginPath();ctx.moveTo(x-12,y-18);ctx.lineTo(x-12+(w+24)*it.cut,y-15-3*it.cut);ctx.stroke();}
    if(f.handAt&&f.handAt.i===i&&f.oldSheet.dx===0)g.hand={x:x+w*f.handAt.p,y:f.handAt.kind==='cut'?y-16:y-8};});
   ctx.restore();}
  ctx.restore();}
 if(hand&&handImage){ctx.save();ctx.translate(hand.x,hand.y);ctx.rotate(DATA.hand.rotation);const hs=DATA.hand.width/handImage.width/(Math.max(1,z*.48));ctx.drawImage(handImage,-DATA.hand.tip[0]*hs,-DATA.hand.tip[1]*hs,handImage.width*hs,handImage.height*hs);ctx.restore();}
}
function prepareSegments(o){const segs=[];let prev=null,total=0;for(const p of o.path){if(p===null){prev=null;continue;}if(prev){const len=Math.hypot(p[0]-prev[0],p[1]-prev[1]);if(len){segs.push({a:prev,b:p,len,start:total});total+=len;}}prev=p;}o.segments=segs;o.total=total;o.drawn=0;o.si=0;}
function revealTo(o,progress){o.shown=true;const m=o.mask.getContext('2d');m.strokeStyle='#000';m.lineWidth=o.radius*2.1;m.lineCap='round';m.lineJoin='round';const target=o.total*progress;let point=null;
 while(o.si<o.segments.length){const s=o.segments[o.si];if(s.start>target)break;const f=Math.min(1,(target-s.start)/s.len);const p=[s.a[0]+(s.b[0]-s.a[0])*f,s.a[1]+(s.b[1]-s.a[1])*f];m.beginPath();m.moveTo(...s.a);m.lineTo(...p);m.stroke();point=p;if(f>=1)o.si++;else break;}
 if(progress>=1){m.fillStyle='#000';m.fillRect(0,0,o.w,o.h);}o.progress=progress;o.dirty=true;if(point)hand={x:o.x+point[0]*o.scale,y:o.y+point[1]*o.scale};
}
function clearAudio(){if(audio){audio.pause();audio.currentTime=0;audio=null;}stopPhotoVideo();}
// Photo stops with photo.video: the still is shown for photo.videoDelay seconds, then the clip plays in the same frame,
// with its own sound; at the end it stays on its last frame. R, ←, →, Space (leaving the stop) stop it.
let photoVideo=null,photoSeq=0;const clipEls={};
// Video elements for photo clips are created and "unlocked" (muted play + pause) on the first click/key of the user,
// so that later, when the stop is reached from a timer, they may play with sound (Safari/Chrome autoplay rules).
function clipEl(src){let v=clipEls[src];if(!v){v=document.createElement('video');v.src=src;v.playsInline=true;v.preload='auto';v.volume=1;clipEls[src]=v;}return v;}
function unlockClips(){for(const s of DATA.sections){const src=s.photo&&s.photo.video;if(!src)continue;const v=clipEl(src);if(v._unlocked)continue;v._unlocked=true;v.muted=true;const p=v.play();if(p&&p.then)p.then(()=>{v.pause();v.currentTime=0;v.muted=false;}).catch(()=>{v.muted=false;v._unlocked=false;});}}
['pointerdown','keydown','touchend'].forEach(ev=>document.addEventListener(ev,unlockClips,{capture:true}));
function stopPhotoVideo(){photoSeq++;clipPending=false;$('soundHint').classList.remove('on');if(photoVideo){try{photoVideo.pause();photoVideo.currentTime=0;}catch(e){}photoVideo=null;}}
// A pause that counts only frames actually shown (a frame blocked by decoding the photo counts at most 100 ms).
function holdFrames(ms,token){return new Promise((res,rej)=>{let el=0,last=null;const tick=now=>{if(token!==runToken)return rej(new Cancelled());if(paused){last=now;requestAnimationFrame(tick);return;}if(last!==null)el+=Math.min(100,Math.max(0,now-last))*speed;last=now;if(el>=ms)res();else requestAnimationFrame(tick);};requestAnimationFrame(tick);});}
async function playPhotoVideo(ph,token){const seq=++photoSeq;clipPending=true;try{await holdFrames((ph.videoDelay??1.5)*1000,token);}catch(e){return;}finally{if(seq===photoSeq)clipPending=false;}
 if(seq!==photoSeq||token!==runToken||!$('photo').classList.contains('on'))return;
 const v=clipEl(ph.video);v.pause();v.currentTime=0;v.muted=false;v.volume=1;v.playbackRate=speed;v.setAttribute('aria-label',ph.caption);photoVideo=v;
 const img=$('photoContent').querySelector('img');
 const show=()=>{if(photoVideo!==v)return;if(img&&img.isConnected)img.replaceWith(v);else if(!v.isConnected)$('photoContent').append(v);};
 v.addEventListener('playing',show,{once:true});
 try{await v.play();if(paused&&photoVideo===v)v.pause();}catch(e){if(photoVideo!==v)return;
  // Sound refused by the browser: play muted and offer «click for sound».
  try{v.muted=true;await v.play();if(paused&&photoVideo===v)v.pause();}catch(e2){if(photoVideo===v)photoVideo=null;return;}
  const h=$('soundHint');h.classList.add('on');h.onclick=ev=>{ev.stopPropagation();v.muted=false;v.play().catch(()=>{});h.classList.remove('on');};}}
async function startAudio(section,token,at=0){if(!section.audio)return null;const a=new Audio(section.audio);a.playbackRate=speed;audio=a;try{if(at>0){if(a.readyState<1)await new Promise(r=>a.addEventListener('loadedmetadata',r,{once:true}));check(token);a.currentTime=at;}await a.play();check(token);if(paused)a.pause();return a;}catch(e){if(e instanceof Cancelled)throw e;clearAudio();$('status').textContent='Audio non disponibile · sottotitoli attivi';return null;}}
function waitForNext(token){check(token);return new Promise((resolve,reject)=>{waiter={token,resolve,reject};});}
async function showPhoto(section,token){check(token);stage='stop';clearAudio();subtitle(null);hand=null;render();const ph=section.photo;
 if(!ph){setPhase('pause');await waitForNext(token);check(token);return;}$('pol').className='pol '+ph.kind;$('photoContent').replaceChildren();
 if(ph.src){const img=document.createElement('img');img.src=ph.src;img.alt=ph.caption;$('photoContent').append(img);}else{const box=document.createElement('div');box.className='missing';const strong=document.createElement('strong');strong.textContent=ph.display;const span=document.createElement('span');span.textContent=ph.disclosure;box.append(strong,span);$('photoContent').append(box);}
 $('caption').textContent=ph.caption;$('disclosure').textContent=ph.disclosure||'';$('photo').classList.add('on');setPhase('photo');if(ph.video)playPhotoVideo(ph,token);
 if(ph.intro){const introCue={en:ph.intro.en,it:ph.intro.it};showSubtitleAt(introCue,0);if(ph.introAudio){const a=new Audio(ph.introAudio);a.playbackRate=speed;audio=a;try{await a.play();check(token);if(paused)a.pause();}catch(e){if(e instanceof Cancelled)throw e;clearAudio();}if(audio&&Number.isFinite(audio.duration)){const left=Math.max(0,(audio.duration-audio.currentTime)*1000);if(left>80)await tween(left,t=>{const p=audio&&Number.isFinite(audio.duration)&&audio.duration>0?audio.currentTime/audio.duration:t;showSubtitleAt(introCue,p);},token);}clearAudio();}}
 await waitForNext(token);check(token);stopPhotoVideo();$('photo').classList.remove('on');subtitle(null);
}
// Pure time-based filter: remembered alternatives, not a claimed historical order.
function nameFilterFrame(section,seconds){
 // Hand writes the remembered names on a sheet, strikes them one by one, swaps the sheet, then TuoTempo is drawn on the new one.
 const cues=section.cues,stop=cues[cues.length-1].start,cutStart=cues.length>1?cues[1].start:stop*.6;
 const index=cues.findIndex(c=>seconds<c.end),cueIndex=index<0?cues.length-1:index;
 const names=section.candidateNames,n=names.length,clamp=v=>Math.min(1,Math.max(0,v));
 const writeStart=Math.min(.35,cutStart*.1),writeEach=Math.min(.5,(cutStart-writeStart-.15)/n);
 const swapDur=Math.min(.5,(stop-cutStart)*.25),cutEnd=stop-swapDur,cutEach=Math.min(.4,(cutEnd-cutStart-.1)/n);
 const list=names.map((label,i)=>({label,write:clamp((seconds-writeStart-i*writeEach)/(writeEach*.9)),cut:clamp((seconds-cutStart-i*cutEach)/(cutEach*.85))}));
 const swap=clamp((seconds-cutEnd)/swapDur),e=swap*swap*(3-2*swap);
 const final=seconds>=stop?Math.min(1,(seconds-stop)/section.nameSequence.finalReveal):0;
 let handAt=null;
 if(seconds<cutStart){const i=Math.min(n-1,Math.max(0,Math.floor((seconds-writeStart)/writeEach)));if(seconds>=writeStart&&list[i].write<1)handAt={kind:'write',i,p:list[i].write};}
 else if(seconds<cutEnd){const i=Math.min(n-1,Math.floor((seconds-cutStart)/cutEach));if(list[i].cut<1)handAt={kind:'cut',i,p:list[i].cut};}
 return {cueIndex,list,handAt,oldSheet:{dx:-e*1300,rot:-e*.35,alpha:1-e},newSheet:{dx:(1-e)*1300,rot:(1-e)*.3,alpha:swap>0?Math.min(1,swap*1.5):0},swap,final};
}
async function nameStop(section,token){subtitle(null);const o=objects.name;
 // Focus the actual lettering (the source image includes a wide blank margin).
 const points=o.path.filter(Boolean),xs=points.map(p=>p[0]),ys=points.map(p=>p[1]);
 const cx=o.x+(Math.min(...xs)+Math.max(...xs))/2*o.scale,cy=o.y+(Math.min(...ys)+Math.max(...ys))/2*o.scale;
 await moveCamera({cx,cy,w:900},token);
 const bw=(Math.max(...xs)-Math.min(...xs))*o.scale,bh=(Math.max(...ys)-Math.min(...ys))*o.scale;
 nameGag={cx,cy,sw:Math.max(520,bw+120),sh:Math.max(470,bh+140),frame:nameFilterFrame(section,0)};
 subtitle(section.cues[0]);setPhase('drawing');const a=await startAudio(section,token);
 const total=(a&&Number.isFinite(a.duration)&&a.duration>0?a.duration:section.audioDuration)*1000;
 await tween(total,t=>{const seconds=a&&Number.isFinite(a.duration)?a.currentTime:t*total/1000;
  nameGag.frame=nameFilterFrame(section,seconds);
  const cue=section.cues[nameGag.frame.cueIndex];const local=cue&&cue.start!=null&&cue.end!=null?(seconds-cue.start)/Math.max(0.05,cue.end-cue.start):0;showSubtitleAt(cue, local);
  if(nameGag.frame.final>0)revealTo(o,nameGag.frame.final);else hand=nameGag.hand||null;
 },token);
 revealTo(o,1);hand=null;render();clearAudio();subtitle(null);setPhase('name');await waitForNext(token);check(token);nameGag=null;subtitle(null);}
async function playSection(section,token,at=0){currentSection=section;stage='section';$('chapter').textContent='';
 if(section.id==='name'){await nameStop(section,token);return;}
 await writeSign(section,token,at);
 // All subtitle timings are editable. Optional cue.start/end override proportional local audio timing.
 let activeArt=null,sectionAudio=null;const totalTime=section.cues.reduce((s,c)=>s+c.duration,0);let durationFactor=1;
 const totals={};for(const c of section.cues)totals[c.art]=(totals[c.art]||0)+c.duration;
 const played={};
 if(section.cues.length){sectionAudio=await startAudio(section,token,at);if(sectionAudio&&Number.isFinite(sectionAudio.duration)&&sectionAudio.duration>0)durationFactor=sectionAudio.duration/totalTime;}
 for(let i=0;i<section.cues.length;i++){check(token);const cue=section.cues[i],o=objects[cue.art];
  if(at>0&&cue.end!=null&&cue.end<=at){played[cue.art]=(played[cue.art]||0)+cue.duration;revealTo(o,snapT(o,played[cue.art]/totals[cue.art],o.progress||0));hand=null;continue;}  // seek: cues already past
  if(activeArt!==cue.art){subtitle(null);await moveCamera(cameraFor(o),token);activeArt=cue.art;}
  check(token);showSubtitleAt(cue,0);setPhase('drawing');played[cue.art]=(played[cue.art]||0)+cue.duration;const target=snapT(o,played[cue.art]/totals[cue.art],o.progress||0);
  if(at>0&&cue.start!=null&&cue.end!=null&&cue.start<at){const f0=o.progress||0;revealTo(o,f0+(target-f0)*Math.min(1,(at-cue.start)/Math.max(.05,cue.end-cue.start)));hand=null;}  // seek: inside this cue
  const from=o.progress||0;
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
// Board label: "In casa · 2007–2011" (tag, when the board has one, then the years).
const boardLabel=b=>b.tag?b.tag+' · '+b.years:b.years;
// Closing shot: after the last board, zoom out over every board of the talk and draw one timeline under them all.
// The timeline is in years (2005 → 2019); boards whose years overlap (2 and 3) run on parallel tracks.
let closing=0;const TL_Y=2840,TRACK=560;
function timeline(){const xs=BOARDS.map(b=>b.region.x),x0=Math.min(...xs)+40,x1=Math.max(...BOARDS.map(b=>b.region.x+b.region.w))-40;
 const yr=b=>{const m=String(b.years).match(/(\d{4})\D+(\d{4})/);return m?[+m[1],+m[2]]:null;};const spans=BOARDS.map(yr);
 if(spans.some(x=>!x)){return BOARDS.map((b,i)=>({b,a:Math.max(x0,b.region.x),e:i<BOARDS.length-1?BOARDS[i+1].region.x:x1,y:TL_Y})).map(t=>({...t,x0,x1}));}
 const Y0=Math.min(...spans.map(x=>x[0])),Y1=Math.max(...spans.map(x=>x[1])),X=y=>x0+(y-Y0)/Math.max(1,Y1-Y0)*(x1-x0),ends=[];
 return BOARDS.map((b,i)=>{const [a,e]=spans[i];let k=ends.findIndex(v=>v<=a);if(k<0){k=ends.length;ends.push(e);}else ends[k]=e;return {b,a:X(a),e:X(e),y:TL_Y+k*TRACK,x0,x1};});}
function drawClosing(){if(closing<=0)return;const T=timeline(),x0=T[0].x0,x1=T[0].x1,tip=x0+(x1-x0)*closing;ctx.save();ctx.lineCap='round';ctx.lineJoin='round';ctx.textAlign='center';ctx.font='170px Hand';
 T.forEach(({b,a,e,y})=>{if(tip<=a)return;const end=Math.min(tip,e);ctx.strokeStyle=b.color;ctx.lineWidth=28;ctx.beginPath();ctx.moveTo(a,y);ctx.lineTo(end,y);ctx.stroke();ctx.beginPath();ctx.moveTo(a,y-90);ctx.lineTo(a,y+90);ctx.stroke();
  if(tip>=e){ctx.beginPath();ctx.moveTo(e,y-60);ctx.lineTo(e,y+60);ctx.stroke();}
  const mid=(a+e)/2;if(tip>mid){ctx.fillStyle=b.color;ctx.fillText(boardLabel(b),mid,y+250);}});
 if(closing>=1){const t=T[T.length-1];ctx.strokeStyle=t.b.color;ctx.lineWidth=28;ctx.beginPath();ctx.moveTo(t.e-120,t.y-90);ctx.lineTo(t.e,t.y);ctx.lineTo(t.e-120,t.y+90);ctx.stroke();}
 ctx.restore();}
async function closingShot(token){if(BOARDS.length<2)return;await tween(900,()=>{},token);const T=timeline(),x0=Math.min(...BOARDS.map(b=>b.region.x)),x1=Math.max(...BOARDS.map(b=>b.region.x+b.region.w)),y0=Math.min(...BOARDS.map(b=>b.region.y)),y1=Math.max(...T.map(t=>t.y))+420;await moveCamera({cx:(x0+x1)/2,cy:(y0+y1)/2,w:Math.max(x1-x0+360,(y1-y0+240)*16/9)},token,3200);setPhase('final');
 await tween(3600,t=>{closing=t;const tip=T[0].x0+(T[0].x1-T[0].x0)*t;let cur=T[0];for(const s of T)if(s.a<=tip)cur=s;hand={x:Math.min(tip,cur.e),y:cur.y};},token);hand=null;render();}
async function finale(board,token,last){stage='finale';subtitle(null);$('chapter').textContent='';const r=board.region;await moveCamera({cx:r.x+r.w/2,cy:r.y+r.h/2,w:Math.max(r.w+220,(r.h+180)*16/9)},token,1100);setPhase('final');const [yx,yy]=board.final.yearsAt;await tween(1300,t=>{finals[board.id]=t;finalProgress=t;const p=board.final.circle;if(t<.65){const a=-Math.PI/2+t/.65*Math.PI*2;hand={x:p.x+Math.cos(a)*p.rx,y:p.y+Math.sin(a)*p.ry};}else hand={x:yx+(t-.65)/.35*340,y:yy-20};},token);hand=null;render();if(last){await closingShot(token);setPhase('ended');$('progress').style.width='100%';}else{setPhase('boardEnd');await waitForNext(token);check(token);}}
function cancel(){runToken++;if(waiter){waiter.reject(new Cancelled());waiter=null;}clearAudio();hand=null;}
// Timeline of the talk (or of the single board): one segment per section, voice time only.
let stage='idle',curIdx=0;
const FLAT=[];BOARDS.forEach((b,bi)=>b.sections.forEach(id=>{const sec=DATA.sections.find(x=>x.id===id);if(sec)FLAT.push({sec,bi})}));
{let t=0;for(const f of FLAT){const c=f.sec.cues||[];const ends=c.map(x=>x.end).filter(x=>x!=null);f.dur=Math.max(1,ends.length?Math.max(...ends):(c.reduce((a,x)=>a+(x.duration||0),0)||f.sec.audioDuration||2));f.start=t;t+=f.dur;}}
const TOTAL=FLAT.reduce((a,f)=>a+f.dur,0);
// Cue targets end on a finished object (art.breaks from tools/stroke_order.py), never halfway through one.
function snapT(o,t,min=0){if(t>=.999||!o.breaks||!o.breaks.length)return Math.min(1,t);let best=t,d=SNAP;for(const b of o.breaks){if(b<min-1e-6)continue;const e=Math.abs(b-t);if(e<d){d=e;best=b;}}return Math.max(min,Math.min(1,best));}
const SNAP=0.08;  // a cue may draw up to 8% more or less of its drawing so it ends on a finished object
// A small hand-written sign (label.small) is written at the start of its section, before the voice: e.g. «intanto, all’estero…» on Lavagna 3.
const signOf=sec=>(DATA.labels||[]).find(l=>l.small&&l.section===sec.id);
async function writeSign(section,token,at){const l=signOf(section);if(!l)return;if(at>0||l.write>=1){l.write=1;return;}ctx.font='italic 64px Hand';const tw=ctx.measureText(l.text).width;
 await moveCamera({cx:l.x+tw/2,cy:l.y-20,w:1500},token,700);setPhase('drawing');await tween(1500,t=>{l.write=t;hand={x:l.x+tw*t,y:l.y-14};},token);hand=null;l.write=1;render();await tween(600,()=>{},token);}
function instantDone(sec){const l=signOf(sec);if(l)l.write=1;for(const c of sec.cues||[])if(objects[c.art])revealTo(objects[c.art],1);for(const k of sec.art||[])if(objects[k])revealTo(objects[k],1);hand=null;}
// opts.from = index in FLAT, opts.at = seconds into that section's voice, opts.stop = go straight to its photo/pause stop.
async function run(opts={}){cancel();setPaused(false);const token=runToken;startAt=performance.now();currentCue=null;currentSection=null;finalProgress=0;finals={};closing=0;for(const o of Object.values(objects)){o.mask.getContext('2d').clearRect(0,0,o.w,o.h);o.shown=false;o.dirty=true;o.progress=0;o.si=0;}for(const l of DATA.labels||[])if(l.small)l.write=0;
 const k=Math.max(0,Math.min(FLAT.length-1,opts.from||0)),kb=FLAT.length?FLAT[k].bi:0,at=opts.at>0.3?opts.at:0;curIdx=k;stage='section';
 $('photo').classList.remove('on');nameGag=null;subtitle(null);$('start').style.display='none';uiPoke(false);$('progress').style.width=(k/PLAY_SECTIONS*95)+'%';cam={cx:BOARDS[0].region.x+900,cy:480,w:2000};
 for(let i=0;i<k+(opts.stop?1:0);i++)instantDone(FLAT[i].sec);for(let bi=0;bi<kb;bi++)finals[BOARDS[bi].id]=1;
 if(k>0||at||opts.stop){const a0=objects[(FLAT[k].sec.cues[0]||{}).art||FLAT[k].sec.art[0]];if(a0)cam={...cameraFor(a0)};}
 render();
 try{let done=k;for(let bi=kb;bi<BOARDS.length;bi++){const b=BOARDS[bi],secs=b.sections.map(id=>DATA.sections.find(s=>s.id===id)).filter(Boolean);
  let j0=0;if(bi===kb)j0=Math.max(0,secs.indexOf(FLAT[k].sec));else if(secs.length){const first=objects[secs[0].art[0]];if(first)await moveCamera(cameraFor(first),token,1600);}
  for(let j=j0;j<secs.length;j++){const sec=secs[j];check(token);curIdx=FLAT.findIndex(f=>f.sec===sec);
   if(bi===kb&&j===j0&&opts.stop){currentSection=sec;await showPhoto(sec,token);}
   else await playSection(sec,token,bi===kb&&j===j0?at:0);
   done++;$('progress').style.width=(done/PLAY_SECTIONS*95)+'%';}
  await finale(b,token,bi===BOARDS.length-1);}}catch(e){if(!(e instanceof Cancelled))showError(e);}
}
// Position on the timeline (seconds of voice).
function position(){const f=FLAT[curIdx];if(!f)return 0;if(phase==='ended')return TOTAL;if(stage==='finale')return f.start+f.dur;if(stage==='stop'||['photo','pause','name'].includes(phase))return f.start+f.dur;
 if(audio&&currentSection===f.sec&&Number.isFinite(audio.currentTime))return f.start+Math.min(f.dur,audio.currentTime);return f.start;}
function seekTo(t){if(phase==='loading'||!FLAT.length)return;t=Math.max(0,Math.min(TOTAL,t));let k=FLAT.findIndex(f=>t<f.start+f.dur);if(k<0)k=FLAT.length-1;const f=FLAT[k],at=t-f.start;
 if(at>f.dur-0.35)run({from:k,stop:true});else run({from:k,at:f.sec.id==='name'?0:at});}
// → : at a stop, continue; while a scene plays, jump to that scene's stop (photo or pause). ← : start of this scene, or of the previous one.
function skipForward(){if(phase==='loading')return;if(phase==='ready'){run();return;}if(waiter){next();return;}if(stage==='section')run({from:curIdx,stop:true});}
function skipBack(){if(phase==='loading')return;if(phase==='ready'){run();return;}const f=FLAT[curIdx];if(!f)return;const into=position()-f.start;
 if(stage==='section'&&into>2)run({from:curIdx});else if(stage==='stop'||stage==='finale')run({from:curIdx});else run({from:Math.max(0,curIdx-1)});}
const SPEEDS=[1,2,4];
function setSpeed(v){speed=v;if(audio)audio.playbackRate=v;if(photoVideo)photoVideo.playbackRate=v;const b=$('speedBadge');if(b){b.textContent=v+'×';b.style.display=v===1?'none':'block';}const sb=$('speedBtn');if(sb)sb.textContent='Velocità '+v+'×';}
function speedStep(d){const i=SPEEDS.indexOf(speed);const n=i<0?(d>0?SPEEDS.find(x=>x>speed)||4:[...SPEEDS].reverse().find(x=>x<speed)||1):SPEEDS[Math.max(0,Math.min(SPEEDS.length-1,i+d))];setSpeed(n);}
// Controls (seek bar, buttons) and cursor: in 'auto' mode they appear as soon as the pointer moves and fade out
// after 2 s without movement (never while the pointer is over them or the bar is being dragged); the cursor hides with them.
// H cycles: auto → always shown → always hidden → auto. The "Nascondi comandi" button pins them hidden (H brings them back).
let uiMode='auto',uiTimer=null,uiOver=false,uiDrag=false;const UI_IDLE=2000;
const uiShow=on=>$('frame').classList.toggle('ui',on);
function uiPoke(show=true){clearTimeout(uiTimer);if(uiMode!=='auto'){uiShow(uiMode==='shown');return;}if(show)uiShow(true);
 uiTimer=setTimeout(()=>{if(paused||uiOver||uiDrag||$('start').style.display!=='none'){uiPoke(false);return;}uiShow(false);},show?UI_IDLE:600);}
function uiToast(t){const el=$('uiToast');el.textContent=t;el.classList.add('on');clearTimeout(el._t);el._t=setTimeout(()=>el.classList.remove('on'),1400);}
function uiSetMode(m){uiMode=m;$('hideBtn').textContent=m==='hidden'?'Mostra comandi':'Nascondi comandi';uiToast({auto:'Comandi automatici (col mouse)',shown:'Comandi sempre visibili',hidden:'Comandi nascosti · H per riaverli'}[m]);if(m==='auto')uiPoke(true);else{clearTimeout(uiTimer);uiShow(m==='shown');}}
function uiCycle(){uiSetMode({auto:'shown',shown:'hidden',hidden:'auto'}[uiMode]);}
function uiInit(){const tb=$('toolbar');let lx=-1,ly=-1;
 document.addEventListener('pointermove',e=>{if(Math.abs(e.clientX-lx)+Math.abs(e.clientY-ly)<2)return;lx=e.clientX;ly=e.clientY;uiPoke(true);});
 document.addEventListener('pointerdown',()=>uiPoke(true));
 tb.addEventListener('pointerenter',()=>{uiOver=true;uiPoke(true);});tb.addEventListener('pointerleave',()=>{uiOver=false;uiPoke(true);});
 $('seek').addEventListener('pointerdown',()=>{uiDrag=true;});document.addEventListener('pointerup',()=>{if(uiDrag){uiDrag=false;uiPoke(true);}});
 uiShow(true);}
// Seek bar: board colours, photo-stop marks, click or drag to jump.
function buildSeek(){const bar=$('seek');if(!bar)return;const tr=bar.querySelector('.track');
 BOARDS.forEach((b,bi)=>{const fs=FLAT.filter(f=>f.bi===bi);if(!fs.length)return;const a=fs[0].start,e=fs[fs.length-1].start+fs[fs.length-1].dur;const seg=document.createElement('i');seg.className='bseg';seg.style.left=(a/TOTAL*100)+'%';seg.style.width=((e-a)/TOTAL*100)+'%';seg.style.background=b.color;tr.append(seg);});
 FLAT.forEach(f=>{if(f.sec.photo){const m=document.createElement('i');m.className='stopmark';m.style.left=((f.start+f.dur)/TOTAL*100)+'%';m.title=f.sec.photo.caption||'';tr.append(m);}});
 let drag=false;const tAt=e=>{const r=tr.getBoundingClientRect();return Math.max(0,Math.min(1,(e.clientX-r.left)/r.width))*TOTAL;};
 const label=t=>{let k=FLAT.findIndex(f=>t<f.start+f.dur);if(k<0)k=FLAT.length-1;const f=FLAT[k];const lab=(DATA.labels||[]).find(l=>l.section===f.sec.id&&!l.small);return (BOARDS.length>1?'Lavagna '+(ALL_BOARDS.indexOf(BOARDS[f.bi])+1)+' · ':'')+(lab?lab.text.replace(/^\d+\s·\s/,''):f.sec.title||f.sec.id);};
 bar.addEventListener('pointerdown',e=>{if(phase==='loading')return;drag=true;bar.setPointerCapture(e.pointerId);bar.querySelector('.fill').style.width=(tAt(e)/TOTAL*100)+'%';e.preventDefault();});
 bar.addEventListener('pointermove',e=>{const t=tAt(e);bar.title=label(t);if(drag)bar.querySelector('.fill').style.width=(t/TOTAL*100)+'%';});
 bar.addEventListener('pointerup',e=>{if(!drag)return;drag=false;seekTo(tAt(e));});
 bar.addEventListener('pointercancel',()=>{drag=false;});
 setInterval(()=>{if(!drag&&phase!=='loading')bar.querySelector('.fill').style.width=((phase==='ready'?0:position())/TOTAL*100)+'%';},200);}
function next(){if(phase==='loading')return;if(phase==='ready'){run();return;}if(waiter){const w=waiter;waiter=null;setPaused(false);if(w.token===runToken){setPhase('camera');w.resolve();}}}
// Pause (click on the board or Space): freezes voice, hand/strokes, every timer, the camera and the photo clip; the same key resumes.
// On a photo stop that is waiting, Space/click still continue (unless its clip is still running: then they pause/resume the clip).
// ←/→/R/seek resume playback from the new point; + − and I work while paused and keep the pause.
let paused=false,clipPending=false;
const clipBusy=()=>clipPending||(photoVideo&&!photoVideo.ended);
function canPause(){if(['loading','ready','error','ended','boardEnd','name','pause'].includes(phase))return false;if(waiter)return !!clipBusy();return true;}
function setPaused(on){paused=on;document.body.dataset.paused=on?'1':'';$('frame').classList.toggle('paused',on);const b=$('playBtn');if(b){b.textContent=on?'▶ Riprendi':'❚❚ Pausa';b.title=(on?'Riprendi':'Pausa')+' · Spazio o clic sulla lavagna';}
 if(on){if(audio)audio.pause();if(photoVideo)photoVideo.pause();$('status').textContent='In pausa · Spazio per riprendere';uiPoke(true);}else{updateStatus();uiPoke(true);}}
function pause(){if(paused||!canPause())return false;setPaused(true);return true;}
function resume(){if(!paused)return false;setPaused(false);if(audio&&!audio.ended)audio.play().catch(()=>{});if(photoVideo&&!photoVideo.ended)photoVideo.play().catch(()=>{});return true;}
function togglePause(){if(paused)return resume();return pause();}
// Space / click on the board: start, resume, pause, or continue from a stop.
function press(){if(phase==='loading')return;if(paused){resume();return;}if(phase==='ready'){run();return;}if(waiter&&!clipBusy()){next();return;}if(!pause()&&waiter)next();}
function toggleLanguage(){lang=lang==='en'?'it':'en';subtitle();$('langBtn').textContent=lang.toUpperCase()+' · cambia lingua';}
function showError(e){console.error(e);cancel();$('error').style.display='block';$('error').textContent='Impossibile aprire la lavagna: '+e.message;setPhase('error');}
async function init(){if(ONLY){const t='TuoTempo · '+boardLabel(ONLY);document.title=t;const y=document.querySelector('#start p');if(y)y.textContent=boardLabel(ONLY);}try{const entries=await Promise.all(Object.entries(DATA.art).map(async([key,a])=>{const image=await loadImage(a.src),mask=document.createElement('canvas'),comp=document.createElement('canvas');mask.width=comp.width=a.w;mask.height=comp.height=a.h;const o={...a,image,mask,comp,scale:a.width/a.w,dirty:true,shown:false,progress:0};prepareSegments(o);return [key,o];}));objects=Object.fromEntries(entries);handImage=await loadImage(DATA.hand.src);await document.fonts.ready;$('loading').style.display='none';setPhase('ready');render();}catch(e){showError(e);}}
$('frame').addEventListener('click',e=>{if(!e.target.closest('#toolbar'))press();});
$('nextBtn').onclick=next;$('playBtn').onclick=()=>{if(phase==='ready')run();else togglePause();};$('resetBtn').onclick=()=>{if(phase!=='loading')run();};$('langBtn').onclick=toggleLanguage;
function fullscreen(){if(document.fullscreenElement){if(document.exitFullscreen)document.exitFullscreen().catch(()=>{});}else if($('frame').requestFullscreen)$('frame').requestFullscreen().catch(()=>{});}
$('fullBtn').onclick=fullscreen;$('backBtn').onclick=skipBack;$('fwdBtn').onclick=skipForward;$('speedBtn').onclick=()=>setSpeed(SPEEDS[(SPEEDS.indexOf(speed)+1)%SPEEDS.length]||1);buildSeek();setSpeed(speed);$('hideBtn').onclick=()=>uiSetMode(uiMode==='hidden'?'auto':'hidden');uiInit();
document.addEventListener('keydown',e=>{if(e.repeat||e.altKey||e.ctrlKey||e.metaKey||['INPUT','TEXTAREA','SELECT'].includes(e.target.tagName))return;const k=e.key.toLowerCase();if(e.code==='Space'){e.preventDefault();press();}else if(e.key==='ArrowRight'){e.preventDefault();skipForward();}else if(e.key==='ArrowLeft'){e.preventDefault();skipBack();}else if(e.key==='+'||e.key==='='){e.preventDefault();speedStep(1);}else if(e.key==='-'||e.key==='_'){e.preventDefault();speedStep(-1);}else if(k==='r'){e.preventDefault();if(phase!=='loading')run();}else if(k==='i')toggleLanguage();else if(k==='f')fullscreen();else if(k==='h')uiCycle();});
// Read-only diagnostics for local verification; no network, telemetry or external API.
window.Whiteboard={getState:()=>({waiting:!!waiter,phase,lang,section:currentSection?.id,cue:currentCue?.en,token:runToken,shown:Object.keys(objects).filter(k=>objects[k].shown),cam:{...cam},nameFilter:nameGag?{...nameGag.frame}:null,finalProgress,finals:{...finals},board:currentSection?boardOf(currentSection.id).id:null,speed,stage,curIdx,pos:position(),total:TOTAL,audioTime:audio?audio.currentTime:null,audioRate:audio?audio.playbackRate:null,paused,clipTime:photoVideo?photoVideo.currentTime:null,clipPaused:photoVideo?photoVideo.paused:null,progress:Object.fromEntries(Object.entries(objects).filter(([k,o])=>o.shown).map(([k,o])=>[k,o.progress]))}),next,press,pause,resume,restart:run,toggleLanguage,seekTo,skipForward,skipBack,setSpeed};
init();
