"""Lavagna 2 (2007-2012): process generated art, align cues from WordBoundary, write boards/lavagna2*.json.
Own script (does not touch prepare_assets.py).
WARNING: regenerates boards/lavagna2.json and boards/lavagna2.art.json from scratch (art paths, cues, notes),
overwriting hand edits made later in those files. For text fixes edit boards/lavagna2.json directly.
Dry run: BOARDS_OUT=/tmp/x python3 tools/board2_build.py"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,cv2,json,re
P=Path(__file__).resolve().parent.parent;A=P/'assets'
BLUE='#1f5fbf'
X0=4400
font=ImageFont.truetype(str(A/'PatrickHand-Regular.ttf'),46)
def fit_note(dr,im,x,y,t,font,anchor,m=10):
 # keep the whole lettering (ascenders, accents, descenders of g j p q y) inside the image, with a margin
 l,tp,r,b=dr.textbbox((x,y),t,font=font,anchor=anchor);w,h=im.size
 dx=max(0,m-l)-max(0,r-(w-m));dy=max(0,m-tp)-max(0,b-(h-m));return x+dx,y+dy
def process(key,notes=()):
 im=Image.open(P/'from-gen'/f'{key}.jpg').convert('RGB')
 dr=ImageDraw.Draw(im)
 for (x,y,t) in notes: dr.text(fit_note(dr,im,x,y,t,font,'la'),t,font=font,fill=BLUE)
 a=np.asarray(im).copy().astype(int)
 r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
 blue=(b>r+40)&(b>g+15)
 gray=(0.299*r+0.587*g+0.114*b)
 ink=(gray<170)|blue
 out=a.copy();out[~ink]=255
 # snap accent pixels to clean marker blue, keep dark ink
 out[blue]=out[blue]*0+np.array([31,95,191])
 out=out.astype('uint8');Image.fromarray(out).save(A/f'{key}.png')
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
W=880
cols=[X0+120,X0+1090,X0+2060,X0+3030];rows=[380,1330]
layout=[('l2-clients',0,0,'1 · The first clients'),('l2-troiano',1,0,'2 · The sincro'),('l2-salotto',2,0,'3 · The living room in via Ugo Bassi'),('l2-voce',3,0,'4 · The voice'),
        ('l2-cloud',0,1,'5 · From server to cloud'),('l2-serverino',1,1,'6 · The little SMS server'),('l2-machu',2,1,'7 · Machu Picchu'),('l2-indip',3,1,'8 · Independent')]
notes={'l2-cloud':[(90,610,'Rome'),(870,640,'Dublin')],'l2-salotto':[(40,660,'Bologna · via Ugo Bassi')]}
art={};labels=[]
for key,c,rw,label in layout:
 a=process(key,notes.get(key,()));a.update({'x':cols[c],'y':rows[rw],'width':W});art[key]=a
 labels.append({'section':key,'text':label,'x':cols[c]-10,'y':rows[rw]-70})
# cues from WordBoundary
T=json.load(open(P/'tools/board2_text.json'))
norm=lambda s:re.sub(r'[^0-9a-z]','',s.lower())
def dur(f):
 import subprocess;return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(f)]).decode())
# Photo captions are always in English (Lele, 20/11), whatever the subtitle language.
memo='Original frame from the promotional video “tuOtempO Memo” (YouTube, 20/07/2007)'
photos={
 'l2-clients':{'src':'assets/memo2007-agenda.png','caption':'The calendar · Thursday, June 14, 2007','kind':'screen','disclosure':'Original frame, then a clip (1:16–1:27.6) from the promotional video “tuOtempO Memo” (YouTube, 20/07/2007)','video':'assets/memo2007-agenda-clip.mp4','videoDelay':1.5},
 'l2-troiano':{'src':'assets/memo2007-sincro.png','caption':'tuOtempO SINCRO · 2007','kind':'screen','disclosure':memo+'; syncing with the practice software was already announced'},
 'l2-machu':{'src':'assets/machu-picchu-2011-04-07.jpg','caption':'Machu Picchu · April 7, 2011','kind':'original','disclosure':'Original photo'},
 'l2-voce':{'src':'assets/memo2007-voice.png','caption':'“Voice Message” · the 2007 promise','kind':'screen','disclosure':memo+'; the voice message only arrived in 2009'},
}
titles={'l2-clients':'The first clients','l2-troiano':'The sincro','l2-salotto':'The living room in via Ugo Bassi','l2-voce':'The voice','l2-cloud':'From server to cloud','l2-serverino':'The little SMS server','l2-machu':'Machu Picchu','l2-indip':'Independent'}
sectnotes={
 'l2-clients':'Master §3 (primi clienti nelle mail 2007: studio dentistico, Clinica Tiro de Pichón, K-Sport, Hedoniste Day Spa, Japanese Beauty Center…; primo memo automatico agosto 2007) e §6 momento 1. Il gancio di §6 cita parrucchiere e tiro a volo: non trovati nell’elenco del master, quindi in voce solo tipologie verificate. Stop: fotogramma reale del video 2007.',
 'l2-troiano':'Master §3 marzo 2008 (integrazione Orisdent con Elite Computer, il “troiano”, in voce chiamato «il sincro» (il troiano si racconta a braccio dal vivo): Don “non era un malware, non esistevano le API”) e §6 momento 2. Nessun nome di gestionale in voce. Mail Orisdent 2008 e manuale tuOtempO_help_ita non trovati nella Gmail personale (ricerca 18/11): stop sul fotogramma SINCRO del video 2007.',
 'l2-salotto':'Master §3 (marzo 2009 via Ugo Bassi 11) e §6 momento 3 (sala della casa dei genitori di Don, fino a 8 persone). Disegno in attesa di una foto della sala o del palazzo (chiedere a Don).',
 'l2-voce':'Master §3 (voce nel 2009 con Voxeo, tesi su VoiceXML) e Reperto video 2007: nel 2007 la voce era una promessa (Lele 18/11). “Fra i primi” è RICORDO di Lele. Stop: fotogramma reale “Voice Message” del video 2007.',
 'l2-cloud':'Master §3 Hosting (server di produzione spento il 07/07/2009, AWS Dublino da settembre 2009, unico hosting da febbraio 2010) e §6 momento 5. Il down di 24 ore con Don a Manfredonia resta a braccio. Stop sul disegno (a braccio).',
 'l2-serverino':'Master §3 (macchinetta degli SMS in via Ugo Bassi, modem GSM, SIM dall’estero, SIM greca; “Serverino Down” 20/07/2011, generale saltato alle due di notte) e §6 momento 6. Nessun nome in voce (chi è salito a riaccenderla resta a braccio). Disegno in attesa di una foto del serverino.',
 'l2-machu':'Master §3 (“Due cadute di Amazon nel 2011”) e §6 momento 7. Licenza scenica decisa da Lele (Sync 18/11, [COWORK]): il fulmine di Dublino (in realtà 7/8/2011) raccontato insieme alla giornata di Lele a Machu Picchu (7/4/2011: corsa giù da Huayna Picchu, internet café di Aguas Calientes, 9 ore per spostare Tuotempo su un’altra zona, poi riparte tutto da solo sulla zona di prima). In voce solo “primavera 2011”, nessuna data del fulmine. Stop: foto vera IMG_0814 del 7/4/2011 (Drive Materiali, machu_picchu_2011-04-07_IMG_0814.jpg). Nessun ritaglio di giornale usato.',
 'l2-indip':'Master §3 “L’indipendenza” (niente round, family & friends) e §6 momento 8. La storia dei 20.000 € resta a braccio; nessuna cifra in voce. Stop sul disegno, poi chiusura della lavagna.',
}
sections=[]
for sec in T:
 sid=sec['id'];words=json.load(open(P/'audio'/f'{sid}-en.words.json'))['words']
 total=dur(P/'audio'/f'{sid}-en.mp3');cues=[];wi=0
 for k,(en,it) in enumerate(sec['cues']):
  need=norm(en);got='';first=None;last=None
  while wi<len(words) and len(got)<len(need):
   w=words[wi];first=first if first is not None else w;got+=norm(w['text']);last=w;wi+=1
  assert got==need,(sid,en,got,need)
  start=round(first['offset']/1e7,6)
  end=round(total,6) if k==len(sec['cues'])-1 else round((last['offset']+last['duration'])/1e7,6)
  cues.append({'en':en,'it':it,'art':sid,'start':start,'end':end,'duration':round(end-start,6)})
 assert wi==len(words),sid
 sections.append({'id':sid,'board':'lavagna2','title':titles[sid],'art':[sid],'narration':{'en':' '.join(c[0] for c in sec['cues']),'it':' '.join(c[1] for c in sec['cues'])},'cues':cues,'audio':f'audio/{sid}-en.mp3','photo':photos.get(sid),'notes':sectnotes[sid],'incomplete':False})
ind=art['l2-indip'];sc=ind['width']/ind['w']
boards=[{'id':'lavagna1','title':'Le origini','years':'2005–2007','color':'#bd282b','sections':['origins','football','remote','name','dentist'],'region':{'x':0,'y':0,'w':4040,'h':2540},'final':{'circle':{'x':1040,'y':1600,'rx':110,'ry':145},'yearsAt':[1800,2480]}},
        {'id':'lavagna2','title':'Le architetture artigianali','tag':'At home','years':'2007–2011','color':BLUE,'sections':[s['id'] for s in sections],'region':{'x':X0,'y':0,'w':4040,'h':2540},'final':{'circle':{'x':round(ind['x']+525*sc),'y':round(ind['y']+205*sc),'rx':95,'ry':95},'yearsAt':[X0+1760,2150]}}]
labels1=[{'section':'origins','text':'1 · Bologna → Valencia','x':90,'y':105},{'section':'football','text':'2 · The five-a-side idea','x':2130,'y':105},{'section':'remote','text':'3 · Born remote','x':2130,'y':1400},{'section':'dentist','text':'4 · Client number one','x':110,'y':1400}]
unk=['Lavagna 2 · via Ugo Bassi: disegno provvisorio; sostituibile con una foto vera della sala o del palazzo (da Don).',
     'Lavagna 2 · serverino degli SMS: disegno provvisorio; sostituibile con una foto vera del PC/modem o della salita estiva per riaccenderlo.',
     'Lavagna 2 · Machu Picchu: stop sulla foto vera IMG_0814 (7/4/2011); il disegno resta sulla lavagna. Racconto per licenza scenica (fulmine di Dublino + Machu Picchu), deciso da Lele.',
     'Lavagna 2 · sincro: mail “Integrazione Orisdent” (marzo 2008) e manuale tuOtempO_help_ita (luglio 2008) non trovati nella Gmail personale; stop sul fotogramma SINCRO del video 2007.',
     'Lavagna 2 · primi clienti: il gancio §6 cita parrucchiere e tiro a volo, non presenti nell’elenco clienti 2007 del master (Clinica Tiro de Pichón è una clinica): in voce solo dentista, centro sportivo, day spa, centro estetico.']
import sys;sys.path.insert(0,str(P/'tools'))
from boardfiles import write_board
write_board('lavagna2',boards[1],sections,labels,unk,art)
d={'sections':sections,'art':art}
print('sections',len(sections),'art',len(art),'audio total',round(sum(c['duration'] for x in sections for c in x['cues']),1))
for x in sections: print(x['id'],[(c['start'],c['end']) for c in x['cues']])
