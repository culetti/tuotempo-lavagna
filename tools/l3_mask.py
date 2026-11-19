"""Lavagna 3, Il teatro napoletano: put a Pulcinella mask (commedia dell'arte) on the speaker's face.
Source of truth: from-gen/l3-sanitas.orig.jpg + from-gen/pulcinella-mask.jpg -> from-gen/l3-sanitas.jpg,
which tools/board3_build.py then turns into assets/l3-sanitas.png and its pen paths. Requested by Lele, 19/11/2026."""
from PIL import Image
import numpy as np,cv2
from pathlib import Path
P=Path(__file__).resolve().parent.parent;F=P/'from-gen'
base=Image.open(F/'l3-sanitas.orig.jpg').convert('L')
m=np.asarray(Image.open(F/'pulcinella-mask.jpg').convert('L'))
dark=(m<128).astype(np.uint8)
# silhouette = everything not reachable from the border through white (fills eye holes and white highlights)
white=(1-dark).copy();ff=white.copy()*255;h,w=ff.shape;msk=np.zeros((h+2,w+2),np.uint8);cv2.floodFill(ff,msk,(0,0),128)
sil=(ff!=128).astype(np.uint8)
ys,xs=np.where(sil);x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
mask_img=Image.fromarray(m[y0:y1+1,x0:x1+1]);sil_img=Image.fromarray(sil[y0:y1+1,x0:x1+1]*255)
S=0.10;W=round((x1-x0+1)*S);H=round((y1-y0+1)*S)
cx,top=440,103   # mask box centre x and top y in the 1280x720 source (face at x 414-472, eyes y~139)
mi=mask_img.resize((W,H),Image.LANCZOS);si=sil_img.resize((W,H),Image.LANCZOS)
out=base.copy();out.paste(mi,(cx-W//2,top),si)
# pupils in the eye holes so the face stays alive behind the mask
a=np.asarray(out).copy()
hole=(np.asarray(si)>200)&(np.asarray(mi)>200)
n,lab,st,cen=cv2.connectedComponentsWithStats(hole.astype(np.uint8))
for i in range(1,n):
 if 15<st[i,4]<400 and st[i,1]<H*0.6:
  px,py=int(cen[i][0])+cx-W//2,int(cen[i][1])+top;cv2.circle(a,(px,py),2,0,-1)
# keep the green accents of the original: work in RGB, mask pasted only where silhouette is
rgb=np.asarray(Image.open(F/'l3-sanitas.orig.jpg').convert('RGB')).copy()
reg=np.zeros(a.shape,bool);reg[top:top+H,cx-W//2:cx-W//2+W]=np.asarray(si)>20
for c in range(3):rgb[...,c][reg]=a[reg]
Image.fromarray(rgb).save(F/'l3-sanitas.jpg',quality=95)
print('mask',W,H,'at',cx-W//2,top)
# pen scribble over the solid black mask: the contour-only pen would leave its middle white while drawing.
# board3_build.py appends this path to l3-sanitas, so the mask is inked last, as if put on at the end.
import json
x0m,y0m=cx-W//2,top;pts=[]
for k,y in enumerate(range(y0m+4,y0m+H-2,9)):
 xs_=[x0m+2,x0m+W-2] if k%2==0 else [x0m+W-2,x0m+2]
 pts+=[[xs_[0],y],[xs_[1],y]]
json.dump(pts+[None],open(F/'l3-sanitas.extra-path.json','w'))
