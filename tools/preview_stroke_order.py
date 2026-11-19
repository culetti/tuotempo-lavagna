"""Previews for the stroke order (tools/stroke_order.py): for each drawing, frames at 25/50/75% of its pen path
with the old order (prima) and the new one (dopo), labelled with the number of objects half drawn at that moment,
and the number of objects left half drawn when each subtitle cue ends (new order, with the player's snapping)."""
import sys,math,json
sys.path.insert(0,'tools')
import numpy as np,cv2
from PIL import Image,ImageDraw
from boardfiles import load_all,P
from stroke_order import reorder,_polys
OUT='/workspace/previews/ordine-tratti/';SNAP=0.08
d=load_all()
def segs(path):
 out=[]
 for pl in _polys(path):
  for p,q in zip(pl,pl[1:]):out.append((tuple(p),tuple(q),math.hypot(q[0]-p[0],q[1]-p[1])))
 return out
def frame(a,path,frac,img):
 m=np.zeros((a['h'],a['w']),np.uint8);S=segs(path);L=sum(s[2] for s in S)*frac;acc=0;th=max(1,int(round(a['radius']*2.1)))
 for p,q,l in S:
  if acc>=L:break
  if acc+l>L:t=(L-acc)/l;q=(p[0]+(q[0]-p[0])*t,p[1]+(q[1]-p[1])*t)
  cv2.line(m,(int(p[0]),int(p[1])),(int(q[0]),int(q[1])),255,th,cv2.LINE_AA);acc+=l
 if frac>=1:m[:]=255
 return (img*(m[...,None]/255)+255*(1-m[...,None]/255)).astype(np.uint8)
def objmap(n):
 # segment -> object id, from the new path and its breaks
 S=segs(n['path']);T=sum(s[2] for s in S);acc=0;o=0;m={}
 for p,q,l in S:
  m[(p,q)]=m[(q,p)]=o;acc+=l
  while o<len(n['breaks'])-1 and acc/T>=n['breaks'][o]-1e-7:o+=1
 return m
def halfdrawn(path,frac,m):
 S=segs(path);L=sum(s[2] for s in S)*frac;acc=0;full={};dr={}
 for p,q,l in S:
  o=m.get((p,q),-1);full[o]=full.get(o,0)+l;dr[o]=dr.get(o,0)+max(0,min(l,L-acc));acc+=l
 return sum(1 for o in full if full[o]>0 and .02<dr[o]/full[o]<.98)
def snap(n,t,mn):
 if t>=.999:return 1
 best,dd=t,SNAP
 for b in n['breaks']:
  if b<mn-1e-6:continue
  if abs(b-t)<dd:dd=abs(b-t);best=b
 return max(mn,min(1,best))
report={}
for b in d['boards']:
 arts=[]
 for s in d['sections']:
  if s['id'] in b['sections']:
   for c in s['cues']:
    if c['art'] not in arts:arts.append(c['art'])
 rows=[];TW=300
 for k in arts:
  a=d['art'][k];n=reorder(a,P);m=objmap(n);img=np.asarray(Image.open(P/a['src']).convert('RGB')).astype(float);th=int(a['h']*TW/a['w']);cells=[];hd={}
  for tag,path in (('prima',a['path']),('dopo',n['path'])):
   row=[];hd[tag]=[]
   for f in (.25,.5,.75):
    h=halfdrawn(path,f,m);hd[tag].append(h)
    im=Image.fromarray(frame(a,path,f,img)).resize((TW,th));dr=ImageDraw.Draw(im)
    dr.rectangle([0,0,TW-1,th-1],outline=(200,200,200));dr.rectangle([0,0,TW-1,13],fill=(255,255,255))
    dr.text((4,2),f"{k} {tag} {int(f*100)}%  oggetti a meta: {h}",fill=(200,0,0) if h>1 else (0,120,0));row.append(im)
   cells.append(row)
  tot=sum(c['duration'] for s in d['sections'] for c in s['cues'] if c['art']==k);acc=0;prog=0;ce=[]
  for s in d['sections']:
   for c in s['cues']:
    if c['art']==k:acc+=c['duration'];prog=snap(n,acc/tot,prog);ce.append((round(prog,3),halfdrawn(n['path'],prog,m)))
  report[k]={'oggetti':len(n['breaks']),'a_meta_prima_25_50_75':hd['prima'],'a_meta_dopo_25_50_75':hd['dopo'],'fine_cue':ce};rows.append((k,cells))
 Hs=sum(r[1][0][0].size[1]*2+8 for r in rows);sheet=Image.new('RGB',(TW*3,Hs),'white');y=0
 for k,cells in rows:
  for row in cells:
   for j,im in enumerate(row):sheet.paste(im,(j*TW,y))
   y+=row[0].size[1]
  y+=8
 sheet.save(OUT+f"{b['id']}-prima-dopo.png")
json.dump(report,open(OUT+'report.json','w'),indent=1)
for k,v in report.items():print(k,v['oggetti'],'prima',v['a_meta_prima_25_50_75'],'dopo',v['a_meta_dopo_25_50_75'],'fine cue',[h for _,h in v['fine_cue']])
