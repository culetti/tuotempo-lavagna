"""Shared generator for Lavagne 5 and 6 (2019-2026): same pipeline as tools/board4_build.py
(generated marker drawing -> ink + accent colour -> pen paths; cues aligned to the Emma voice word timings),
parameterised by board. Used by tools/board5_build.py and tools/board6_build.py.
WARNING: regenerates boards/lavagnaN.json and boards/lavagnaN.art.json from scratch.
Dry run: BOARDS_OUT=/tmp/x python3 tools/board5_build.py"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,cv2,json,re,subprocess,sys
P=Path(__file__).resolve().parent.parent;A=P/'assets'
font=ImageFont.truetype(str(A/'PatrickHand-Regular.ttf'),46)
def fit_note(dr,im,x,y,t,font,anchor,m=10):
 # keep the whole lettering (ascenders, accents, descenders of g j p q y) inside the image, with a margin
 l,tp,r,b=dr.textbbox((x,y),t,font=font,anchor=anchor);w,h=im.size
 dx=max(0,m-l)-max(0,r-(w-m));dy=max(0,m-tp)-max(0,b-(h-m));return x+dx,y+dy
def process(key,color,accent,notes=()):
 rgb=tuple(int(color[i:i+2],16) for i in (1,3,5))
 im=Image.open(P/'from-gen'/f'{key}.jpg').convert('RGB');dr=ImageDraw.Draw(im)
 for (x,y,t) in notes: dr.text(fit_note(dr,im,x,y,t,font,'mt'),t,font=font,fill=rgb,anchor='mt')
 a=np.asarray(im).copy().astype(int);r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
 acc=accent(r,g,b)
 gray=(0.299*r+0.587*g+0.114*b);ink=(gray<170)|acc
 out=a.copy();out[~ink]=255;out[acc]=np.array(rgb)
 Image.fromarray(out.astype('uint8')).save(A/f'{key}.png')
 contours,_=cv2.findContours(ink.astype('uint8')*255,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
 contours=sorted(contours,key=lambda c:(cv2.boundingRect(c)[0]//170,cv2.boundingRect(c)[1]))
 paths=[]
 for c in contours:
  if cv2.arcLength(c,False)<14:continue
  pts=cv2.approxPolyDP(c,1.3,True).reshape(-1,2).tolist()
  if len(pts)<2:continue
  paths+=pts+[pts[0],None]
 w,h=im.size
 return {'src':f'assets/{key}.png','w':w,'h':h,'path':paths,'radius':8}
def build(cfg):
 n=cfg['n'];X0=cfg['x0'];W=1100;cols=[X0+150,X0+1450,X0+2750];rows=[380,1400];bcols=[X0+800,X0+2100]
 pos=[(cols[0],rows[0]),(cols[1],rows[0]),(cols[2],rows[0]),(bcols[0],rows[1]),(bcols[1],rows[1])]
 art={};labels=[]
 for i,(key,title) in enumerate(cfg['scenes']):
  x,y=pos[i];a=process(key,cfg['color'],cfg['accent'],cfg.get('notes',{}).get(key,()));a.update({'x':x,'y':y,'width':W});art[key]=a
  labels.append({'section':key,'text':f'{i+1} · {title}','x':x-10,'y':y-70})
 T=json.load(open(P/f'tools/board{n}_text.json'))
 norm=lambda s:re.sub(r'[^0-9a-z]','',s.lower())
 dur=lambda f:float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(f)]).decode())
 titles=dict(cfg['scenes']);sections=[]
 for sec in T:
  sid=sec['id'];words=json.load(open(P/'audio'/f'{sid}-en.words.json'))['words'];total=dur(P/'audio'/f'{sid}-en.mp3');cues=[];wi=0
  for k,(en,it) in enumerate(sec['cues']):
   need=norm(en);got='';first=None
   while wi<len(words) and len(got)<len(need):
    w=words[wi];first=first or w;got+=norm(w['text']);last=w;wi+=1
   assert got==need,(sid,en,got,need)
   start=round(first['offset']/1e7,6);end=round(total,6) if k==len(sec['cues'])-1 else round((last['offset']+last['duration'])/1e7,6)
   cues.append({'en':en,'it':it,'art':sid,'start':start,'end':end,'duration':round(end-start,6)})
  assert wi==len(words),sid
  sections.append({'id':sid,'board':f'lavagna{n}','title':titles[sid],'art':[sid],'narration':{'en':' '.join(c[0] for c in sec['cues']),'it':' '.join(c[1] for c in sec['cues'])},'cues':cues,'audio':f'audio/{sid}-en.mp3','photo':cfg['photos'].get(sid),'notes':cfg['sectnotes'][sid],'incomplete':False})
 last=cfg['scenes'][-1][0];cs=art[last];sc=cs['width']/cs['w'];cx,cy,rx,ry=cfg['circle']
 board={'id':f'lavagna{n}','title':cfg['title'],'tag':cfg['tag'],'years':cfg['years'],'color':cfg['color'],'sections':[s['id'] for s in sections],'region':{'x':X0,'y':0,'w':4040,'h':2540},'final':{'circle':{'x':round(cs['x']+cx*sc),'y':round(cs['y']+cy*sc),'rx':rx,'ry':ry},'yearsAt':[X0+3250,2300]}}
 sys.path.insert(0,str(P/'tools'))
 from boardfiles import write_board
 write_board(f'lavagna{n}',board,sections,labels,cfg['unknowns'],art)
 print('sections',len(sections),'art',len(art),'voice',round(sum(c['duration'] for x in sections for c in x['cues']),1))
