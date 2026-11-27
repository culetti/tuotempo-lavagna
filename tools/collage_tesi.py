"""Scene 2.4 photo stop: the 2007 «Voice Message» frame + a polaroid sticker of the real portrait of the
master's-thesis author (no AI on the face), with a marker-drawn graduation cap and a rolled diploma.
Output: assets/memo2007-voice-tesi.png (the original frame stays in assets/memo2007-voice.png).
Run: python3 tools/collage_tesi.py"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFilter
P=Path(__file__).resolve().parent.parent
SRC=Path('/workspace/tuotempo-materiali/ritratto-tesi-voce.jpg')
S=4                                   # frame 320x240 -> 1280x960
base=Image.open(P/'assets/memo2007-voice.png').convert('RGB').resize((320*S,240*S),Image.LANCZOS)
# --- polaroid with the real photo
face=ImageOps.exif_transpose(Image.open(SRC)).convert('RGB').crop((190,250,770,975))      # hair..shoulders, 580x725
PW,PH=232,290;face=face.resize((PW,PH),Image.LANCZOS)
B,BB=16,58                                                                                 # white border, thicker bottom
pol=Image.new('RGBA',(PW+2*B,PH+B+BB),(255,255,255,255));pol.paste(face,(B,B))
# --- marker drawings, drawn at 3x on a transparent layer then reduced (smooth marker edges)
K=3;W,H=pol.size;top=110                                                                    # headroom above the polaroid for the cap
lay=Image.new('RGBA',(W*K,(H+top)*K),(0,0,0,0));d=ImageDraw.Draw(lay)
def pt(x,y):return (x*K,(y+top)*K)
ink=(20,20,20,255);lw=4*K
# graduation cap sitting on the hair (head top ~ x 120..215, y ~50 in polaroid coords)
cx,cy=B+round(272*PW/580),B+round(62*PH/725)+8
board=[pt(cx-100,cy-34),pt(cx+6,cy-70),pt(cx+106,cy-36),pt(cx-2,cy+2)]
d.polygon(board,fill=ink)
d.line(board+[board[0]],fill=ink,width=lw,joint='curve')
d.polygon([pt(cx-56,cy-14),pt(cx+56,cy-14),pt(cx+50,cy+26),pt(cx-48,cy+26)],fill=ink)      # skull cap
d.line([pt(cx+4,cy-34),pt(cx+82,cy-24),pt(cx+86,cy+26)],fill=(214,170,40,255),width=3*K)     # gold tassel cord
d.polygon([pt(cx+78,cy+24),pt(cx+94,cy+24),pt(cx+98,cy+54),pt(cx+74,cy+54)],fill=(214,170,40,255))
d.ellipse([pt(cx-2,cy-40),pt(cx+10,cy-28)],fill=(214,170,40,255))
# rolled diploma with a red ribbon, bottom-right corner of the polaroid
dx,dy=W-118,H-64
d.rounded_rectangle([pt(dx,dy),pt(dx+112,dy+30)],radius=15*K,fill=(255,253,240,255),outline=ink,width=lw)
d.ellipse([pt(dx+92,dy),pt(dx+122,dy+30)],fill=(255,253,240,255),outline=ink,width=lw)
d.ellipse([pt(dx+101,dy+9),pt(dx+113,dy+21)],outline=ink,width=2*K)
d.line([pt(dx+50,dy-2),pt(dx+50,dy+32)],fill=(189,40,43,255),width=6*K)
d.line([pt(dx+50,dy+30),pt(dx+38,dy+52)],fill=(189,40,43,255),width=5*K)
d.line([pt(dx+50,dy+30),pt(dx+64,dy+50)],fill=(189,40,43,255),width=5*K)
# two little marker sparkles
for (x,y) in [(B+40,B+40),(W-34,B+70)]:
  for a,b in [((x-12,y),(x+12,y)),((x,y-12),(x,y+12))]:d.line([pt(*a),pt(*b)],fill=ink,width=3*K)
lay=lay.resize((W,H+top),Image.LANCZOS)
sticker=Image.new('RGBA',(W,H+top),(0,0,0,0));sticker.paste(pol,(0,top));sticker.alpha_composite(lay)
sticker=sticker.rotate(4,resample=Image.BICUBIC,expand=True)
# soft shadow under the polaroid
sh=Image.new('RGBA',sticker.size,(0,0,0,0));m=sticker.split()[3].point(lambda v:90 if v>0 else 0)
sh.putalpha(m.filter(ImageFilter.GaussianBlur(10)))
out=base.convert('RGBA');X,Y=505,228
out.alpha_composite(sh,(X+8,Y+12));out.alpha_composite(sticker,(X,Y))
out.convert('RGB').save(P/'assets/memo2007-voice-tesi.png',optimize=True)
print('ok',out.size,'sticker box',(X,Y,X+sticker.size[0],Y+sticker.size[1]))
