"""Common build step: draw every object of a drawing completely before moving to the next one.

The generators trace ink contours and used to sort them in 170 px columns, so the hand drew part of
an object, moved on to the start of others and came back later. Here the pen path (polylines
separated by None) is regrouped into objects:
  * ink (grey + accent colour) is dilated by GAP px; each connected blob is an object (a figure,
    a word, a sign...);
  * a blob that is a whole scene (it spans a large part of the drawing, e.g. buildings standing on
    one ground line) is split into compact parts: its strokes are cut into short pieces and grouped
    with k-means on position, keeping accent-coloured ink separate from grey ink, so e.g. the purple
    car is one object and each building is another;
  * objects go left to right (the board's reading order), each object's strokes are chained
    nearest-first; text-like objects (wide and short) strictly left to right, so every word is
    written completely before the next.
It adds art['breaks'] = fraction of pen length at the end of each object, used by the player to end
a subtitle cue on a finished object. Applied in build.py, so the board files keep the generator's raw
order and any regenerated board gets the same treatment at the next build."""
import math
from pathlib import Path
import numpy as np,cv2
from PIL import Image
GAP=11      # px in the drawing: strokes closer than this belong to the same blob
PART=300    # px: target size of one part when a scene-sized blob is split
PIECE=24    # points per piece when cutting strokes of a scene-sized blob

def _polys(path):
 out,cur=[],[]
 for p in path:
  if p is None:
   if cur:out.append(cur);cur=[]
  else:cur.append(p)
 if cur:out.append(cur)
 return out

def _plen(pl):return sum(math.hypot(q[0]-p[0],q[1]-p[1]) for p,q in zip(pl,pl[1:]))

def _length(path):return sum(_plen(pl) for pl in _polys(path))

def _chain(polys,idx):
 left=set(idx);cur=min(left,key=lambda i:polys[i][0][0]+polys[i][0][1]);seq=[cur];left.remove(cur)
 while left:
  ex,ey=polys[cur][-1];cur=min(left,key=lambda i:min((polys[i][0][0]-ex)**2+(polys[i][0][1]-ey)**2,(polys[i][-1][0]-ex)**2+(polys[i][-1][1]-ey)**2))
  # open pieces may be drawn backwards when their end is the closer one
  if (polys[cur][-1][0]-ex)**2+(polys[cur][-1][1]-ey)**2<(polys[cur][0][0]-ex)**2+(polys[cur][0][1]-ey)**2 and polys[cur][0]!=polys[cur][-1]:polys[cur]=polys[cur][::-1]
  seq.append(cur);left.remove(cur)
 return seq

def reorder(art,root):
 polys=_polys(art['path'])
 if len(polys)<2:return art
 im=np.asarray(Image.open(Path(root)/art['src']).convert('RGB')).astype(int)
 if im.shape[1]!=art['w'] or im.shape[0]!=art['h']:return art
 H,W=im.shape[:2]
 gray=.299*im[...,0]+.587*im[...,1]+.114*im[...,2];sat=np.max(im,2)-np.min(im,2)
 accent=cv2.dilate((sat>60).astype(np.uint8),np.ones((5,5),np.uint8))
 ink=((gray<200)|(sat>60)).astype(np.uint8)
 n,lab,st,cen=cv2.connectedComponentsWithStats(cv2.dilate(ink,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(GAP,GAP))),connectivity=8)
 at=lambda x,y,m:m[min(H-1,max(0,int(y))),min(W-1,max(0,int(x)))]
 groups={}
 for i,pl in enumerate(polys):
  votes={}
  for x,y in pl:
   l=at(x,y,lab)
   if l:votes[l]=votes.get(l,0)+1
  if votes:g=max(votes,key=votes.get)
  else:
   cx=sum(p[0] for p in pl)/len(pl);cy=sum(p[1] for p in pl)/len(pl)
   g=min(range(1,n),key=lambda k:(cen[k][0]-cx)**2+(cen[k][1]-cy)**2) if n>1 else 0
  groups.setdefault(g,[]).append(i)
 objects=[]  # (polylines, text_like)
 for g,idx in groups.items():
  x,y,w,h=(st[g][:4] if g else (0,0,W,H))
  if w>0.35*W or h>0.55*H:   # a whole scene: split into compact parts
   pieces=[]
   for i in idx:
    pl=polys[i]
    for j in range(0,len(pl)-1,PIECE):pieces.append(pl[j:j+PIECE+1])
   pieces=[p for p in pieces if len(p)>1] or [polys[i] for i in idx]
   feat=np.array([[sum(p[0] for p in pc)/len(pc),sum(p[1] for p in pc)/len(pc),
                   2000.0*(sum(at(px,py,accent) for px,py in pc)*2>len(pc))] for pc in pieces],np.float32)
   k=int(max(2,min(16,round(w*h/(PART*PART)))));k=min(k,len(pieces))
   cv2.setRNGSeed(7)
   _,lbl,_=cv2.kmeans(feat,k,None,(cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER,60,0.5),4,cv2.KMEANS_PP_CENTERS)
   for c in range(k):
    sel=[pieces[i] for i in range(len(pieces)) if lbl[i][0]==c]
    if sel:objects.append((sel,False))
  else:
   objects.append(([polys[i] for i in idx],h<90 and w>1.6*h))
 objects.sort(key=lambda o:(min(p[0] for pl in o[0] for p in pl),min(p[1] for pl in o[0] for p in pl)))
 total=_length(art['path']) or 1
 new,breaks,done=[],[],0.0
 for pls,text in objects:
  pls=[list(p) for p in pls]
  order=sorted(range(len(pls)),key=lambda i:min(p[0] for p in pls[i])) if text else _chain(pls,range(len(pls)))
  for i in order:new+=pls[i]+[None];done+=_plen(pls[i])
  breaks.append(round(done/total,8))
 out=dict(art);out['path']=new;out['breaks']=breaks
 return out
