"""Lavagna 6 · Back on course (2022-2026): see tools/boardlate.py. Text in tools/board6_text.json, voice tools/board6_tts.py.
Story source: voice message of 26/11/2026 (wiki raw handover) + meeting 24/11 + master §7."""
import sys;from pathlib import Path;sys.path.insert(0,str(Path(__file__).resolve().parent))
from boardlate import build
import json
# Module carousel at the end of 6.5 (Lele 27/11): cards and years from tools/carousel.json (years: Nicolò's readme and timeline;
# Marketplace 2018–19 and Noa Notes 2024 from the master «filo dei prodotti», not on the timeline).
CAROUSEL=json.load(open(Path(__file__).resolve().parent/'carousel.json'))
for it in CAROUSEL['items']:
 if it['name']=='Agenda':it['tall']=True
CAROUSEL.update({'title':'Twenty years of modules','color':'#cc1f63','note':'Module cards from the Tuotempo 20 graphics (marketing, 2026) · the data inside the cards is invented'})
CARD='Module cards from the Tuotempo 20 graphics (marketing, 2026); the data inside the cards is invented'
build({'n':6,'x0':22160,'title':'Di nuovo in rotta','tag':'Back on course','years':'2022–2026','color':'#cc1f63',
 'accent':lambda r,g,b:(r>g+60)&(b>g+30)&(r>140),
 'scenes':[('l6-rotta','A new course'),('l6-utile','In the black'),('l6-voce','Voice or chat?'),('l6-scommesse','Two bets'),('l6-ventanni','Twenty years')],
 'notes':{'l6-rotta':[(650,525,'LARGE ACCOUNTS')],'l6-voce':[(1075,297,'MAKE'),(1119,369,'BUY')],'l6-ventanni':[(869,590,'20 YEARS')]},
 'photos':{
  'l6-voce':{'src':'assets/l6-cards-voice-chat.jpg','caption':'Voice Assistant and Chat Assistant · module cards','kind':'doc','disclosure':CARD},
  'l6-scommesse':{'src':'assets/l6-cards-marketplace-noa.jpg','caption':'Marketplace and Noa Notes · module cards','kind':'doc','disclosure':CARD},
  'l6-ventanni':{'carousel':CAROUSEL,'src':'assets/l6-griglia.jpg','caption':'Twenty years of modules · from the Agenda to Claim Hub','kind':'doc','disclosure':'The full grid of the Tuotempo 20 graphics (marketing, 2026); the data inside the cards is invented'},
 },
 'circle':(1075,519,110,100),
 'sectnotes':{
  'l6-rotta':'M. (vocale 26/11): riunione a Barcellona fra settembre e novembre 2022, scelta dei large accounts; poi richiesta di tagliare i costi (denaro più caro); a Natale 2022 il terzo piano con un collega (non nominato). Formulazione prudente: «Late 2022». Nessun nome (M. = «a new guide»), nessuna cifra (cifre fuori).',
  'l6-utile':'M.: revisione dei processi, personalizzazioni e API a pagamento, aumenti di prezzo (percentuali fuori dalla voce); profittabilità a giugno 2023; nuovo grande cliente Connect in Italia (nome oscurato); allentamento delle misure più dure all’inizio del 2024. Temi delicati del periodo fuori dalla voce. Formulazioni prudenti: «by the summer of 2023», «a big new Connect client signed in Italy» (cliente non nominato, nessun anno), «soon the hardest measures of the plan could be lifted» (misure non nominate). ATTESA CLAUDE: dubbio 7.',
  'l6-voce':'M.: nel 2023 riunioni lunghe fra Gianfranco, Donatello e M.; Donatello «il Voice ha i giorni contati, il futuro è la chat», Gianfranco «non ci sono risorse», M. «servono prodotti nuovi»; make or buy → in house. Formulazione prudente: nessun anno in voce (riunioni 2023 per M., schede Voice e Chat Assistant 2025) e «Years after that first robot call» invece di «fourteen years». ATTESA CLAUDE: dubbio 6. Stop: schede 14 e 15 della grafica Tuotempo 20.',
  'l6-scommesse':'M.: nel 2025 due scommesse, Marketplace (base del successo 2026) e Noa Notes (prodotto per il medico, non ha attecchito nel mercato Enterprise di Spagna e Italia, ma grande impegno di tutti). Formulazione prudente: «Then came two bets» (nessun anno: scheda Noa Notes 2024, vendita 2025; Marketplace 2018/2019 per N.). ATTESA CLAUDE: dubbio 8. Stop: schede Marketplace e Noa Notes.',
  'l6-ventanni':'Chiusura proposta da M.: successo di Voice e Chat AI e crescita dei profili Marketplace in Spagna e Italia nel 2026; Claim Hub (Lele 24/11) nella griglia. «twenty years ago» invece di un anno (regola: nascita «tra il 2005 e il 2006»). Stop: carosello dei moduli (schede di Nicolò in ordine cronologico, anno a pennarello; richiesta di Lele 27/11), poi la griglia_bento della grafica Tuotempo 20. Anni: readme e timeline di Nicolò; Marketplace «2018–19» e Noa Notes 2024 dal master (non sono sulla timeline). ATTESA CLAUDE: anni di Voice/Chat (2023 per M., 2025 sulle schede), Noa Notes (2024 o 2025), Marketplace (2018/19 o 2025).'},
 'unknowns':['Lavagna 6 · disegni generati con l’AI (stile delle lavagne 1–4); stop solo su schede e griglia della grafica Tuotempo 20 (dati inventati, dichiarato).','Lavagna 6 · fatti in attesa di Claude: nome e primato del grande cliente Connect in Italia, anni di Voice/Chat e Noa Notes, secondo vocale di M. del 26/11 (Log 27/11).']})
