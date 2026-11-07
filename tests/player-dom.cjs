// Isolated DOM + native raster Canvas tests. No browser process, profile or CDP.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {JSDOM,VirtualConsole}=require('../tools/node_modules/jsdom');
const {createCanvas,Image,GlobalFonts}=require('../tools/node_modules/@napi-rs/canvas');
const P=path.resolve(__dirname,'..');
GlobalFonts.registerFromPath(path.join(P,'assets/PatrickHand-Regular.ttf'),'Hand');
const errors=[];const virtualConsole=new VirtualConsole();virtualConsole.on('jsdomError',e=>errors.push(e.message));virtualConsole.on('error',e=>errors.push(String(e)));
let now=0;
const dom=new JSDOM(fs.readFileSync(path.join(P,'index.html'),'utf8'),{url:'file://'+P+'/index.html?speed=20',runScripts:'dangerously',pretendToBeVisual:true,virtualConsole,beforeParse(w){
 w.Image=Image;w.document.fonts={ready:Promise.resolve()};w.performance.now=()=>now;w.requestAnimationFrame=cb=>setTimeout(()=>{now+=75;cb(now)},1);
 const proto=w.HTMLCanvasElement.prototype;proto.getContext=function(){if(!this._native)this._native=createCanvas(this.width||300,this.height||150);if(!this._proxy){const c=this._native.getContext('2d');this._proxy=new Proxy(c,{get(t,k){if(k==='drawImage')return (im,...args)=>t.drawImage(im._native||im,...args);const v=t[k];return typeof v==='function'?v.bind(t):v;},set(t,k,v){t[k]=v;return true;}});}return this._proxy;};
}});
const w=dom.window;const state=()=>w.Whiteboard?.getState();
async function until(fn,label){const end=Date.now()+25000;while(Date.now()<end){if(fn())return;await new Promise(r=>setTimeout(r,5));}throw Error('Timeout '+label+' '+JSON.stringify(state())+' '+errors.join(';'));}
function key(k,code=k){w.document.dispatchEvent(new w.KeyboardEvent('keydown',{key:k,code,bubbles:true}));}
function snapshot(name){fs.writeFileSync(path.join(P,'tests',name+'.png'),w.document.getElementById('cv')._native.toBuffer('image/png'));}
(async()=>{
 await until(()=>state()?.phase==='ready','ready');assert.equal(state().lang,'en');console.log('PASS offline data and image preload');
 key(' ','Space');await until(()=>state().phase==='drawing','drawing');const en=w.document.getElementById('sub').textContent;assert.ok(en.startsWith('Once upon'));key('i');assert.equal(state().lang,'it');assert.ok(w.document.getElementById('sub').textContent.startsWith("C'era una volta"));snapshot('reveal-with-hand');console.log('PASS live EN/IT subtitle switching');
 const old=state().token;key('r');assert.ok(state().token>old);await until(()=>state().phase==='photo','first photo after reset');assert.equal(state().section,'origins');assert.equal(w.document.querySelector('#photo img').alt,'Bologna · Alma Mater');
 const at=state().token;await new Promise(r=>setTimeout(r,30));assert.equal(state().phase,'photo');assert.equal(state().token,at);console.log('PASS reset while drawing and indefinite manual photo pause');
 key('r');await until(()=>state().phase==='photo','reset photo');assert.equal(state().section,'origins');console.log('PASS reset while photo paused');
 const stops=[];
 for(let i=0;i<5;i++){
  await until(()=>['photo','name'].includes(state().phase)&&state().waiting,'stop '+i);stops.push(state().section);
  if(state().section==='remote'){assert.ok(w.document.querySelector('#photo img'));assert.match(w.document.getElementById('caption').textContent,/2007/);assert.match(w.document.getElementById('disclosure').textContent,/Flash/);}
  if(state().section==='name'){snapshot('name-stop');assert.match(w.document.getElementById('sub').textContent,/SPACE|SPAZIO/);}
  if(state().section==='dentist')assert.match(w.document.getElementById('disclosure').textContent,/ricostruzione/);
  key(' ','Space');await until(()=>!['photo','name'].includes(state().phase),'advance '+i);
 }
 await until(()=>state().phase==='ended','finale');assert.deepEqual(stops,['origins','football','remote','name','dentist']);assert.equal(state().shown.length,10);assert.equal(state().finalProgress,1);snapshot('final-board');console.log('PASS all four stops + 3 bis, missing-archive warning, reconstruction labels and final zoom');
 const real=errors.filter(e=>!/HTMLMediaElement/.test(e));assert.equal(real.length,0,real.join('\n'));console.log('PASS no DOM/runtime errors');
 fs.writeFileSync(path.join(P,'tests/results.json'),JSON.stringify({engine:'jsdom + @napi-rs/canvas (NOT browser)',stops,errors,finalState:state()},null,2));w.close();
})().catch(e=>{console.error(e);w.close();process.exitCode=1;});
