"""Recompute the stroke path of Lavagna 1 drawings after an asset edit.
Usage: python3 tools/l1_repath.py key [key...]   (--check key: compare only)
Ink = gray<180 or red (same rule used when the L1 assets were cleaned)."""
import json,sys,cv2,numpy as np
from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parent.parent;F=P/'boards'/'lavagna1.art.json'
def path_for(src):
 a=np.asarray(Image.open(P/src).convert('RGB')).astype(int);r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
 red=(r>g+35)&(r>b+30);gray=0.299*r+0.587*g+0.114*b;ink=(gray<180)|red
 cs,_=cv2.findContours(ink.astype('uint8')*255,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
 cs=sorted(cs,key=lambda c:(cv2.boundingRect(c)[0]//170,cv2.boundingRect(c)[1]));out=[]
 for c in cs:
  if cv2.arcLength(c,False)<14:continue
  pts=cv2.approxPolyDP(c,1.3,True).reshape(-1,2).tolist()
  if len(pts)<2:continue
  out+=pts+[pts[0],None]
 return out
if __name__=='__main__':
 art=json.loads(F.read_text());check='--check' in sys.argv
 for k in [a for a in sys.argv[1:] if not a.startswith('--')]:
  p=path_for(art[k]['src'])
  if check: print(k,'identical' if p==art[k]['path'] else f'differs ({len(p)} vs {len(art[k]["path"])})')
  else: art[k]['path']=p;print(k,len(p))
 if not check:
  tmp={k:{**v,'path':f'@@{k}@@'} for k,v in art.items()};txt=json.dumps(tmp,indent=2)
  for k,v in art.items(): txt=txt.replace(f'"@@{k}@@"',json.dumps(v['path'],separators=(',',':')))
  F.write_text(txt+('\n' if F.read_text().endswith('\n') else ''))
