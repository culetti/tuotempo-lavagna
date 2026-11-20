"""Lavagna 4 (2016-2019): process generated art, align cues, write boards/lavagna4*.json.
Does not touch prepare_assets.py.
WARNING: regenerates boards/lavagna4.json and boards/lavagna4.art.json from scratch (art paths, cues, notes),
overwriting hand edits made later in those files. For text fixes edit boards/lavagna4.json directly.
Dry run: BOARDS_OUT=/tmp/x python3 tools/board4_build.py"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,cv2,json,re,subprocess
P=Path(__file__).resolve().parent.parent;A=P/'assets'
PURPLE='#7442b8';PRGB=np.array([116,66,184])
X0=13280
font=ImageFont.truetype(str(A/'PatrickHand-Regular.ttf'),46)
def fit_note(dr,im,x,y,t,font,anchor,m=10):
 # keep the whole lettering (ascenders, accents, descenders of g j p q y) inside the image, with a margin
 l,tp,r,b=dr.textbbox((x,y),t,font=font,anchor=anchor);w,h=im.size
 dx=max(0,m-l)-max(0,r-(w-m));dy=max(0,m-tp)-max(0,b-(h-m));return x+dx,y+dy
def process(key,notes=()):
 im=Image.open(P/'from-gen'/f'{key}.jpg').convert('RGB');dr=ImageDraw.Draw(im)
 for (x,y,t) in notes: dr.text(fit_note(dr,im,x,y,t,font,'mt'),t,font=font,fill=PURPLE,anchor='mt')
 a=np.asarray(im).copy().astype(int);r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
 green=(r>g+30)&(b>g+30)
 gray=(0.299*r+0.587*g+0.114*b);ink=(gray<170)|green
 out=a.copy();out[~ink]=255;out[green]=PRGB
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
W=1100;cols=[X0+150,X0+1450,X0+2750];rows=[380,1400];bcols=[X0+800,X0+2100]
layout=[('l4-milano',cols[0],rows[0],'1 · Tre demo a Milano'),('l4-pretendenti',cols[1],rows[0],'2 · Due pretendenti alla porta'),('l4-scelta',cols[2],rows[0],'3 · La scelta'),
        ('l4-ciacco',bcols[0],rows[1],'4 · La cena da Ciacco'),('l4-si',bcols[1],rows[1],'5 · Il sì')]
art={};labels=[]
for key,x,y,label in layout:
 a=process(key);a.update({'x':x,'y':y,'width':W});art[key]=a
 labels.append({'section':key,'text':label,'x':x-10,'y':y-70})
T=json.load(open(P/'tools/board4_text.json'))
norm=lambda s:re.sub(r'[^0-9a-z]','',s.lower())
dur=lambda f:float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(f)]).decode())
photos={
 'l4-milano':{'src':'assets/l4-mail-ieo.png','caption':'“analisi per attivazione tuOtempO” (activation analysis) · June 15, 2016','kind':'doc','disclosure':'Original text of the IEO email, re-typeset; sender hidden'},
}
titles={'l4-milano':'Tre demo a Milano','l4-pretendenti':'Due pretendenti alla porta','l4-scelta':'La scelta','l4-ciacco':'La cena da Ciacco','l4-si':'Il sì'}
sectnotes={
 'l4-milano':'Master §3 (registrazione 11/11, RICORDO dei tre) e §6 momenti 14/16: San Raffaele, Multimedica, IEO in un giorno; giacca e cravatta, uno col giubbotto di pelle; Don racconta prodotto e visione. Anno ricostruito 2016 dalle mail (CERTO): giugno 2016 IEO “analisi per attivazione tuOtempO”, settembre 2016 Multimedica, dicembre 2016 app di test IEO. Stop: mail di IEO del 15/06/2016 (Gmail di Lele, sola lettura), mittente coperto. La macchina (Mercedes Classe B o Yaris) non è nominata. Voce corretta il 19/11 ([COWORK]): San Raffaele arriva solo nel 2018 (Gruppo San Donato), quindi “two of them were customers, and the third followed”.',
 'l4-pretendenti':'Master §3 “Il finale” e §6 momento 17. Autunno 2018: term sheet del fondo 23/09–01/10/2018, Docplanner dal 15/10/2018 (CERTO). Il fondo resta anonimo; niente cifre (regola dell’11/11).',
 'l4-scelta':'Master §3 “Perché Docplanner” e §6 momento 18 (RICORDO, registrazione 11/11): Don torna dal fondo, il fondo capisce che i fondatori non vogliono ripartire con round ed espansione USA. Lasciato fuori l’aspetto personale.',
 'l4-ciacco':'Master §3 “La cena decisiva” e §6 momento 19 (RICORDO): trattoria Ciacco, via Farini, Bologna; Gef (Gianfranco) arriva dalla Spagna col trolley; affinità su strumenti e lavoro distribuito. Persone di Docplanner non nominate; la richiesta della quota resta fuori. Data: con ogni probabilità la sera del 17/10/2018 (visita di Mariusz e dei due cofondatori a Bologna, [COWORK] 18/11); in voce “one evening in October 2018”.',
 'l4-si':'Master §3 e §6 momento 20: assemblea 27/11/2018, nuova proposta approvata 30/01/2019, due diligence chiusa ad aprile 2019, “JOIN 13 MAY” 2019 (CERTO). Breve e positivo, nessuna cifra; passa la parola al racconto di Gef (Gianfranco).',
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
 sections.append({'id':sid,'board':'lavagna4','title':titles[sid],'art':[sid],'narration':{'en':' '.join(c[0] for c in sec['cues']),'it':' '.join(c[1] for c in sec['cues'])},'cues':cues,'audio':f'audio/{sid}-en.mp3','photo':photos.get(sid),'notes':sectnotes[sid],'incomplete':False})
cs=art['l4-si'];sc=cs['width']/cs['w']
board={'id':'lavagna4','title':'Verso Docplanner','years':'2016–2019','color':PURPLE,'sections':[s['id'] for s in sections],'region':{'x':X0,'y':0,'w':4040,'h':2540},'final':{'circle':{'x':round(cs['x']+590*sc),'y':round(cs['y']+470*sc),'rx':150,'ry':120},'yearsAt':[X0+3250,2300]}}
unk=['Lavagna 4 · tre demo a Milano: disegno provvisorio; nessuna foto della giornata (auto, ospedali); stop sulla mail IEO del 15/06/2016.',
     'Lavagna 4 · cena da Ciacco: disegno provvisorio; sostituibile con una foto della trattoria Ciacco (via Farini) o della cena (probabilmente 17/10/2018).',
     'Lavagna 4 · due pretendenti e la scelta: nessun reperto mostrabile senza cifre; disegni della porta e del bivio.',
     'Lavagna 4 · il sì: nessun reperto; possibile stop futuro sulla mail “DOCPLANNER › JOIN › 13 MAY” se ritagliata senza dati sensibili.']
import sys;sys.path.insert(0,str(P/'tools'))
from boardfiles import write_board
write_board('lavagna4',board,sections,labels,unk,art)
print('sections',len(sections),'art',len(art),'voice',round(sum(c['duration'] for x in sections for c in x['cues']),1))
