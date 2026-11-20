"""Lavagna 3 (2009-2016): process generated art, align cues, write boards/lavagna3*.json.
Does not touch prepare_assets.py.
WARNING: regenerates boards/lavagna3.json and boards/lavagna3.art.json from scratch (art paths, cues, notes),
overwriting hand edits made later in those files. For text fixes edit boards/lavagna3.json directly.
Dry run: BOARDS_OUT=/tmp/x python3 tools/board3_build.py"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,cv2,json,re,subprocess
P=Path(__file__).resolve().parent.parent;A=P/'assets'
GREEN='#2a8a4a';GRGB=np.array([42,138,74])
X0=8840
font=ImageFont.truetype(str(A/'PatrickHand-Regular.ttf'),46)
def fit_note(dr,im,x,y,t,font,anchor,m=10):
 # keep the whole lettering (ascenders, accents, descenders of g j p q y) inside the image, with a margin
 l,tp,r,b=dr.textbbox((x,y),t,font=font,anchor=anchor);w,h=im.size
 dx=max(0,m-l)-max(0,r-(w-m));dy=max(0,m-tp)-max(0,b-(h-m));return x+dx,y+dy
def process(key,notes=()):
 im=Image.open(P/'from-gen'/f'{key}.jpg').convert('RGB');dr=ImageDraw.Draw(im)
 for (x,y,t) in notes: dr.text(fit_note(dr,im,x,y,t,font,'mt'),t,font=font,fill=GREEN,anchor='mt')
 a=np.asarray(im).copy().astype(int);r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
 green=(g>r+35)&(g>b+20)
 gray=(0.299*r+0.587*g+0.114*b);ink=(gray<170)|green
 out=a.copy();out[~ink]=255;out[green]=GRGB
 Image.fromarray(out.astype('uint8')).save(A/f'{key}.png')
 contours,_=cv2.findContours(ink.astype('uint8')*255,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
 contours=sorted(contours,key=lambda c:(cv2.boundingRect(c)[0]//170,cv2.boundingRect(c)[1]))
 extra=P/'from-gen'/f'{key}.extra-path.json'  # e.g. scribble over the Pulcinella mask (tools/l3_mask.py)
 extra=json.load(open(extra)) if extra.exists() else None
 ekey=(min(p[0] for p in extra if p)//170,min(p[1] for p in extra if p)) if extra else None
 paths=[]
 for c in contours:
  if cv2.arcLength(c,False)<14:continue
  if extra and (cv2.boundingRect(c)[0]//170,cv2.boundingRect(c)[1])>ekey:paths+=extra;extra=None  # drawn in its place, column by column
  pts=cv2.approxPolyDP(c,1.3,True).reshape(-1,2).tolist()
  if len(pts)<2:continue
  paths+=pts+[pts[0],None]
 if extra:paths+=extra
 w,h=im.size
 return {'src':f'assets/{key}.png','w':w,'h':h,'path':paths,'radius':8}
W=1100;cols=[X0+150,X0+1450,X0+2750];rows=[380,1400]
layout=[('l3-spagna',0,0,'1 · La Spagna'),('l3-abudhabi',1,0,'2 · Abu Dhabi'),('l3-cravatte',2,0,'3 · Le cravatte nel deserto'),
        ('l3-sanitas',0,1,'4 · Il teatro napoletano'),('l3-firma',1,1,'5 · La firma da multinazionale'),('l3-consegne',2,1,'6 · Il passaggio di consegne')]
notes={'l3-firma':[(150,560,'Bologna'),(487,560,'Barcellona'),(781,560,'Lione'),(1087,560,'Abu Dhabi')]}
art={};labels=[]
for key,c,rw,label in layout:
 a=process(key,notes.get(key,()));a.update({'x':cols[c],'y':rows[rw],'width':W});art[key]=a
 labels.append({'section':key,'text':label,'x':cols[c]-10,'y':rows[rw]-70})
T=json.load(open(P/'tools/board3_text.json'))
norm=lambda s:re.sub(r'[^0-9a-z]','',s.lower())
dur=lambda f:float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(f)]).decode())
photos={
 'l3-spagna':{'src':'assets/l3-mail-acuerdos.png','caption':'“Acuerdos” · September 24, 2009','kind':'doc','disclosure':'Original email text, re-typeset; sender hidden'},
 'l3-abudhabi':{'src':'assets/l3-mail-lastnotice.png','caption':'“Last Notice” · March 21, 2010','kind':'doc','disclosure':'Original email text, re-typeset; sender and recipients hidden, amounts left out'},
 'l3-cravatte':{'src':'assets/deserto-2008-12.jpg','caption':'In the desert · December 2008','kind':'original','disclosure':'Original photo'},
 'l3-sanitas':{'src':'assets/l3-sanitas-slides.png','caption':'tuOtempO_Sanitas_Performance.ppt · July 20, 2011','kind':'doc','disclosure':'Two original slides: the same search, 70 seconds without the cache, 5 with it'},
 'l3-firma':{'src':'assets/l3-mail-firma.png','caption':'The signature · September 9, 2014','kind':'doc','disclosure':'Original email, re-typeset; name and contact details hidden'},
}
titles={'l3-spagna':'La Spagna','l3-abudhabi':'Abu Dhabi','l3-cravatte':'Le cravatte nel deserto','l3-sanitas':'Il teatro napoletano','l3-firma':'La firma da multinazionale','l3-consegne':'Il passaggio di consegne'}
sectnotes={
 'l3-spagna':'Master §3 “Come nasce la Spagna” e §6 momento 9. Telefonata delle 18:30 (RICORDO, data incerta: 2009 o poco prima); mail “Acuerdos” 24/09/2009 (CERTO): accordo di distribuzione con i partner Infomed per Tarragona, Lleida, Huesca e Andorra, circa 60 cliniche dentali. Nessun nome del collaboratore in voce. Stop: mail ricomposta dal testo originale (Gmail di Lele).',
 'l3-abudhabi':'Master §3 “Abu Dhabi: le date dalle mail” e §6 momento 10. L’ex collega di Cezanne diventato direttore sanitario (CERTO, Lele 11/11), nessun nome in voce. Mail 21/03/2010 “Automatic Suspension of Service on April 1st – Last Notice” (CERTO); scadenza poi spostata al 1° agosto (a braccio). Importi omessi. La foto di Don nel deserto (EXIF 12/12/2008) è lo stop del momento successivo.',
 'l3-cravatte':'Master §3 (giacca e cravatta nel deserto: RICORDO; c’erano Lele e Don: CERTO, Lele 11/11; inizio ad Abu Dhabi a dicembre 2008) e §6 momento 11. In voce “one winter” invece di “one January”, per non stonare con la foto di dicembre. Stop: foto vera di Don nel deserto, EXIF 12/12/2008 (album Google Foto), confermata Abu Dhabi da Lele (Sync 18/11); didascalia prudente senza luogo.',
 'l3-sanitas':'Master §3 “Sanitas” e §6 momento 12. Il trucco del terminale col timer è RICORDO; la ppt del 20/07/2011 (allegato “tuOtempO_Sanita_Perfromance.ppt”, mail di Don) mostra 70 secondi senza cache e 5 con cache. Stop: due slide originali.',
 'l3-firma':'Master §3 (firme “BOLOGNA | BARCELONA | LYON | ABU DHABI” 2014–2018; a Lione e a Barcellona di fatto una persona; Bologna = la sala di via Ugo Bassi) e §6 momento 13. Stop: mail del 09/09/2014 con la firma, nome e recapiti coperti.',
 'l3-consegne':'Master §3 “Verso il 2016” e §6 momento 15: casella attivata il 22–23/09/2015, firma “Customer Services Director”. Mostrato solo come passaggio di consegne, senza dire che era uscito e rientrato (deciso da Lele 18/11). Le tre demo di Milano (momento 14) vanno nella Lavagna 4.',
}
sections=[]
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
 sections.append({'id':sid,'board':'lavagna3','title':titles[sid],'art':[sid],'narration':{'en':' '.join(c[0] for c in sec['cues']),'it':' '.join(c[1] for c in sec['cues'])},'cues':cues,'audio':f'audio/{sid}-en.mp3','photo':photos.get(sid),'notes':sectnotes[sid],'incomplete':False})
cs=art['l3-consegne'];sc=cs['width']/cs['w']
board={'id':'lavagna3','title':'L’espansione e gli schiaffi','tag':'All’estero','years':'2009–2015','color':GREEN,'sections':[s['id'] for s in sections],'region':{'x':X0,'y':0,'w':4040,'h':2540},'final':{'circle':{'x':round(cs['x']+575*sc),'y':round(cs['y']+340*sc),'rx':120,'ry':120},'yearsAt':[X0+1760,2300]}}
unk=['Lavagna 3 · cravatte nel deserto: stop sulla foto vera di Don nel deserto (12/12/2008); nella foto non c’è la cravatta: le cravatte restano nel disegno e nel racconto.',
     'Lavagna 3 · passaggio di consegne: nessun reperto; disegno della staffetta.',
     'Lavagna 3 · Spagna: la data della telefonata delle 18:30 è incerta (2009 o poco prima); in voce “2009” per l’arrivo della Spagna, datato dalla mail Acuerdos.']
import sys;sys.path.insert(0,str(P/'tools'))
from boardfiles import write_board
# Lavagna 3 runs in parallel with Lavagna 2 (2009–2011): a small sign at its start, no change to the voice.
labels.append({'section':labels[0]['section'],'text':'intanto, all’estero…','x':labels[0]['x'],'y':labels[0]['y']-95,'small':True})
write_board('lavagna3',board,sections,labels,unk,art)
print('sections',len(sections),'art',len(art),'voice',round(sum(c['duration'] for x in sections for c in x['cues']),1))
