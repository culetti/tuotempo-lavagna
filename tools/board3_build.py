"""Lavagna 3 (2009-2016): process generated art, align cues, insert into scenes.json.
Rebuilds from tools/scenes.board12.json (Lavagne 1+2) each run. Does not touch prepare_assets.py."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,cv2,json,re,subprocess
P=Path(__file__).resolve().parent.parent;A=P/'assets'
GREEN='#2a8a4a';GRGB=np.array([42,138,74])
X0=8840
font=ImageFont.truetype(str(A/'PatrickHand-Regular.ttf'),46)
def process(key,notes=()):
 im=Image.open(P/'from-gen'/f'{key}.jpg').convert('RGB');dr=ImageDraw.Draw(im)
 for (x,y,t) in notes: dr.text((x,y),t,font=font,fill=GREEN,anchor='mt')
 a=np.asarray(im).copy().astype(int);r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
 green=(g>r+35)&(g>b+20)
 gray=(0.299*r+0.587*g+0.114*b);ink=(gray<170)|green
 out=a.copy();out[~ink]=255;out[green]=GRGB
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
 'l3-spagna':{'src':'assets/l3-mail-acuerdos.png','caption':'«Acuerdos» · 24 settembre 2009','kind':'doc','disclosure':'Testo originale della mail, ricomposto; mittente coperto'},
 'l3-abudhabi':{'src':'assets/l3-mail-lastnotice.png','caption':'«Last Notice» · 21 marzo 2010','kind':'doc','disclosure':'Testo originale della mail, ricomposto; mittente e destinatari coperti, importi omessi'},
 'l3-sanitas':{'src':'assets/l3-sanitas-slides.png','caption':'tuOtempO_Sanitas_Performance.ppt · 20 luglio 2011','kind':'doc','disclosure':'Due slide originali: la stessa ricerca, 70 secondi senza cache, 5 con la cache'},
 'l3-firma':{'src':'assets/l3-mail-firma.png','caption':'La firma · 9 settembre 2014','kind':'doc','disclosure':'Mail originale, ricomposta; nome e recapiti coperti'},
}
titles={'l3-spagna':'La Spagna','l3-abudhabi':'Abu Dhabi','l3-cravatte':'Le cravatte nel deserto','l3-sanitas':'Il teatro napoletano','l3-firma':'La firma da multinazionale','l3-consegne':'Il passaggio di consegne'}
sectnotes={
 'l3-spagna':'Master §3 “Come nasce la Spagna” e §6 momento 9. Telefonata delle 18:30 (RICORDO, data incerta: 2009 o poco prima); mail “Acuerdos” 24/09/2009 (CERTO): accordo di distribuzione con i partner Infomed per Tarragona, Lleida, Huesca e Andorra, circa 60 cliniche dentali. Nessun nome del collaboratore in voce. Stop: mail ricomposta dal testo originale (Gmail di Lele).',
 'l3-abudhabi':'Master §3 “Abu Dhabi: le date dalle mail” e §6 momento 10. L’ex collega di Cezanne diventato direttore sanitario (CERTO, Lele 11/11), nessun nome in voce. Mail 21/03/2010 “Automatic Suspension of Service on April 1st – Last Notice” (CERTO); scadenza poi spostata al 1° agosto (a braccio). Importi omessi. La foto di Don nel deserto (EXIF 12/12/2008) non è confermata come Abu Dhabi: non usata.',
 'l3-cravatte':'Master §3 (giacca e cravatta nel deserto a gennaio: RICORDO; c’erano Lele e Don: CERTO, Lele 11/11) e §6 momento 11. Anno non noto. Disegno in attesa di una foto di Abu Dhabi da Don.',
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
base_text=(P/'tools/scenes.board12.json').read_text();base=json.loads(base_text)
boards=base['boards']+[{'id':'lavagna3','title':'L’espansione e gli schiaffi','years':'2009–2016','color':GREEN,'sections':[s['id'] for s in sections],'region':{'x':X0,'y':0,'w':4040,'h':2540},'final':{'circle':{'x':round(cs['x']+575*sc),'y':round(cs['y']+340*sc),'rx':120,'ry':120},'yearsAt':[X0+1760,2300]}}]
labels=base['labels']+labels
unk=['Lavagna 3 · cravatte nel deserto: disegno provvisorio; manca una foto confermata di Abu Dhabi (quella di Don nel deserto, EXIF 12/12/2008, non è confermata).',
     'Lavagna 3 · passaggio di consegne: nessun reperto; disegno della staffetta.',
     'Lavagna 3 · Spagna: la data della telefonata delle 18:30 è incerta (2009 o poco prima); in voce “2009” per l’arrivo della Spagna, datato dalla mail Acuerdos.']
s=base_text
dump=lambda o,ind:('\n'+' '*ind).join(json.dumps(o,ensure_ascii=False,indent=2).split('\n'))
def artdump(a):
 head={k:v for k,v in a.items() if k!='path'}
 return dump(head,4)[:-1].rstrip()+',\n      "path": '+json.dumps(a['path'],separators=(',',':'))+'\n    }'
anchor='\n  },\n  "sections": [';assert s.count(anchor)==1
s=s.replace(anchor,''.join(',\n    "%s": %s'%(k,artdump(v)) for k,v in art.items())+anchor)
anchor='\n  ],\n  "final": {';assert s.count(anchor)==1
s=s.replace(anchor,''.join(',\n    '+dump(x,4) for x in sections)+anchor)
i=s.index('\n  "boards": ');j=s.index('\n  "unknowns": [')
s=s[:i]+'\n  "boards": '+dump(boards,2)+',\n  "labels": '+dump(labels,2)+','+s[j:]
i=s.rstrip().rfind('\n  ]')
s=s[:i]+''.join(',\n    '+json.dumps(u,ensure_ascii=False) for u in unk)+s[i:]
d=json.loads(s);(P/'scenes.json').write_text(s,encoding='utf8')
print('sections',len(d['sections']),'art',len(d['art']),'boards',[b['id'] for b in d['boards']],'voice',round(sum(c['duration'] for x in sections for c in x['cues']),1))
