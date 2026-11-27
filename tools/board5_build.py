"""Lavagna 5 · The race (2019-2022): see tools/boardlate.py. Text in tools/board5_text.json, voice tools/board5_tts.py.
Story source: Donatello's notes 2019-2022 (Gemini notes of a Meet, 27/11/2026) + master §7; proposal docs/proposta-nuove-sequenze.md."""
import sys;from pathlib import Path;sys.path.insert(0,str(Path(__file__).resolve().parent))
from boardlate import build
CARD='Module card from the Tuotempo 20 graphics (marketing, 2026); the data inside the card is invented'
build({'n':5,'x0':17720,'title':'La corsa','tag':'The race','years':'2019–2022','color':'#e06a16',
 'accent':lambda r,g,b:(r>g+50)&(g>b+30)&(r>150),
 'scenes':[('l5-manager','A manager from Turkey'),('l5-trasloco','Leaving via Ugo Bassi'),('l5-razzo','Hypergrowth'),('l5-vienna','The last flight from Vienna'),('l5-pandemia','The world stops')],
 'photos':{
  'l5-manager':{'src':'assets/l5-mail-preliminary.png','caption':'“Let’s make sure TuoTempo accelerates” · Docplanner email · November 27, 2018','kind':'doc','disclosure':'Original text of an email in the “Preliminary agreement” thread, re-typeset; sender hidden'},
  'l5-pandemia':{'src':'assets/l5-card-video.jpg','caption':'Video consultation · module card','kind':'small','disclosure':CARD},
 },
 'circle':(1150,330,150,130),
 'sectnotes':{
  'l5-manager':'Don (note Gemini 27/11) e master §7 momenti 21–22. Il manager è C. (decisione di Lele 27/11: in voce «a manager from Turkey», nessun nome). Formulazione prudente: «2019» (non «fine gennaio»: la mail «Preliminary agreement» del 15/01/2019 è già di C.) e «In spring, the deal was done» (Don dice aprile, le mail «JOIN 13 MAY» 2019). ATTESA CLAUDE: dubbio 1 del Log 27/11. Stop: risposta del 27/11/2018 nel thread «Preliminary agreement» (Gmail di Lele, sola lettura), testo originale ricomposto, mittente coperto, nessuna cifra.',
  'l5-trasloco':'Don (note Gemini 27/11, 00:14:21): via Ugo Bassi non basta più, settembre–ottobre 2019 trasloco in via Garibaldi; «un integratore in più? perché non tre o cinque»; regola: nessun collo di bottiglia. Formulazione prudente: «Later that year» (mese non in voce). ATTESA CLAUDE: dubbio 9 (data esatta, civico, foto; video Google Foto del 02/09/2019 «nuovo ufficio» da verificare). Nessuno stop finché non c’è una foto sicura.',
  'l5-razzo':'Don (00:02:54–00:05:48): l’hyperscaling 2019–2021, filiali in America Latina (Brasile, Cile), leadership in Italia e Spagna, la «navicella» non pronta. Formulazione prudente: «the team grew several times over» (Don «quasi 200», M. 24/11 «da 20 a 100»); niente anni precisi, niente fatturato (cifre fuori dalla voce). ATTESA CLAUDE: dubbi 2 e 3.',
  'l5-vienna':'Don (00:09:50): di ritorno dalla Polonia, scalo a Vienna, presi dalla strategia perdono l’ultimo volo e dormono in aeroporto. In voce «two of them», nessun nome e nessun anno. ATTESA CLAUDE: dubbio 4 (anno; il compagno di Don è C.?).',
  'l5-pandemia':'Pandemia 2020 (certo); videoconsulenza: scheda «Videoconsultation 2020» di N.. Formulazione prudente: «and Tuotempo added video consultations» (nessun nesso causale dichiarato). Ridimensionamento detto come «find the right size» (Don 00:05:48–00:06:54), senza uscite. ATTESA CLAUDE: dubbio 5. Stop: scheda modulo 11 della grafica Tuotempo 20 (marketing).'},
 'unknowns':['Lavagna 5 · disegni generati con l’AI (stile delle lavagne 1–4), nessuna foto reale della corsa 2019–2022.','Lavagna 5 · via Garibaldi: manca una foto sicura del nuovo ufficio (candidato: video Google Foto 02/09/2019 «nuovo ufficio»).','Lavagna 5 · fatti in attesa di Claude: data di chiusura, chi guidava, dimensioni della squadra, anno di Vienna, videoconsulenza e pandemia (Log 27/11).']})
