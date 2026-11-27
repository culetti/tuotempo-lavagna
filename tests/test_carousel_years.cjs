// Every carousel year must be whole inside the frame, with a margin, at 1920×1080 and 1280×720: one frame per card.
const {chromium}=require('/workspace/tuotempo-lavagna1/tools/node_modules/playwright');
const URL=process.env.URL||'file:///workspace/tuotempo-lavagna1/index.html',OUT=process.env.OUT||'/workspace/previews/carosello-anni/';
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});let fails=0;const ok=(c,m)=>{console.log((c?'OK  ':'FAIL')+' '+m);if(!c)fails++;};
for(const [W,H] of [[1920,1080],[1280,720]]){const p=await b.newPage({viewport:{width:W,height:H}});
 await p.goto(URL+'?lavagna=6');await p.waitForFunction(()=>window.Whiteboard&&Whiteboard.getState().phase==='ready',null,{timeout:120000});
 await p.mouse.click(W/2,H*.4);await p.waitForTimeout(800);const tot=(await p.evaluate(()=>Whiteboard.getState())).total;
 await p.evaluate(t=>Whiteboard.seekTo(t),tot-0.1);await p.waitForFunction(()=>Whiteboard.getState().phase==='carousel',null,{timeout:15000});await p.mouse.move(2,2);
 const n=await p.evaluate(()=>document.querySelectorAll('#carousel .cyear').length);
 for(let i=0;i<n;i++){await p.evaluate(i=>{car.ms=i*1600+900;},i);await p.waitForTimeout(160);
  const r=await p.evaluate(i=>{const y=document.querySelectorAll('#carousel .cyear')[i],c=document.querySelectorAll('#carousel .ccard')[i];const rg=document.createRange();rg.selectNodeContents(y);const t=rg.getBoundingClientRect(),cb=c.getBoundingClientRect();
   return {year:y.textContent,op:+getComputedStyle(y).opacity,clip:y.style.clipPath,L:t.left,R:t.right,T:t.top,B:t.bottom,cardR:cb.right,cardL:cb.left,fs:parseFloat(y.style.fontSize)};},i);
  await p.keyboard.press('Space');await p.waitForTimeout(120);// freeze this frame
  const shot=`${OUT}${W}x${H}-${String(i+1).padStart(2,'0')}-${r.year}.png`;await p.screenshot({path:shot});
  // same frame with the year's clip-path removed: the marker ink must be identical (nothing cut by the writing clip)
  const ref='/tmp/cy-ref.png';await p.evaluate(i=>{const y=document.querySelectorAll('#carousel .cyear')[i];y.dataset.c=y.style.clipPath;y.style.clipPath='none';},i);await p.screenshot({path:ref});
  await p.evaluate(i=>{const y=document.querySelectorAll('#carousel .cyear')[i];y.style.clipPath=y.dataset.c;},i);
  const cnt=async f=>p.evaluate(async([src,W,H])=>{const im=new Image();im.src=src;await im.decode();const cv=document.createElement('canvas');cv.width=W;cv.height=H;const g=cv.getContext('2d');g.drawImage(im,0,0);const d=g.getImageData(0,0,W,H).data;let k=0;for(let j=0;j<d.length;j+=4)if(d[j]>150&&d[j+1]<110&&d[j+2]<160&&(j/4)%W>W*.4)k++;return k;},['data:image/png;base64,'+require('fs').readFileSync(f).toString('base64'),W,H]);
  const kc=await cnt(shot),kr=await cnt(ref);await p.keyboard.press('Space');
  // pixel check: no year-coloured ink in the rightmost 3% of the frame, rows of the year
  const ink=await p.evaluate(async([src,T,B,W,H])=>{const im=new Image();im.src=src;await im.decode();const cv=document.createElement('canvas');cv.width=W;cv.height=H;const g=cv.getContext('2d');g.drawImage(im,0,0);
    const x0=Math.floor(W*.97),y0=Math.max(0,Math.floor(T)),y1=Math.min(H,Math.ceil(B));const d=g.getImageData(x0,y0,W-x0,Math.max(1,y1-y0)).data;let k=0;for(let j=0;j<d.length;j+=4)if(d[j]>150&&d[j+1]<110&&d[j+2]<160)k++;
    let maxX=0;const d2=g.getImageData(0,y0,W,Math.max(1,y1-y0)).data;for(let j=0;j<d2.length;j+=4){if(d2[j]>150&&d2[j+1]<110&&d2[j+2]<160){const x=(j/4)%W;if(x>maxX)maxX=x;}}return {k,maxX};},
    ['data:image/png;base64,'+require('fs').readFileSync(shot).toString('base64'),r.T,r.B,W,H]);
  const margin=W-r.R;ok(r.op>0.95&&margin>=W*.03&&ink.k===0&&ink.maxX<W*.97&&r.L>r.cardR&&kc===kr&&kc>500,`${W}x${H} #${i+1} ${r.year}: ink ${kc}/${kr} (clipped/unclipped), text ${r.L.toFixed(0)}–${r.R.toFixed(0)} (right margin ${margin.toFixed(0)}px), ink up to x=${ink.maxX}, font ${r.fs.toFixed(0)}px, card ${r.cardL.toFixed(0)}–${r.cardR.toFixed(0)}`);}
 await p.close();}
console.log(fails?'FAILS '+fails:'ALL OK');await b.close();process.exit(fails?1:0);})();
