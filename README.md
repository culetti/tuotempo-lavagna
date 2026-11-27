# TuoTempo · Lavagna 1 — Le origini



## Link
- Tutte le lavagne (2005–2026): https://culetti.github.io/tuotempo-lavagna/
- Lavagna 1 · Le origini (2005–2007): https://culetti.github.io/tuotempo-lavagna/?lavagna=1
- Lavagna 2 · Le architetture artigianali (In casa · 2007–2011): https://culetti.github.io/tuotempo-lavagna/?lavagna=2
- Lavagna 3 · L’espansione e gli schiaffi (All’estero · 2009–2015): https://culetti.github.io/tuotempo-lavagna/?lavagna=3
- Lavagna 4 · Verso Docplanner (2016–2019): https://culetti.github.io/tuotempo-lavagna/?lavagna=4
- Lavagna 5 · La corsa (The race · 2019–2022): https://culetti.github.io/tuotempo-lavagna/?lavagna=5
- Lavagna 6 · Di nuovo in rotta (Back on course · 2022–2026): https://culetti.github.io/tuotempo-lavagna/?lavagna=6

Con `?lavagna=N` (oppure `#lavagnaN`, valido anche per il file `index.html` aperto in locale) la schermata iniziale mostra gli anni di quella lavagna, il player parte direttamente da lì e si ferma sulla sua chiusura (cerchio e anni), senza passare alla lavagna successiva né fare lo zoom finale su tutte. Senza parametro il player è quello completo. Si combina con `speed`, per esempio `?lavagna=3&speed=2`.

## Struttura a file per lavagna (dal 18/11/2026)
Il vecchio `scenes.json` unico è diviso per lavagna, così per correggere una lavagna si apre solo il suo file:

- `boards/common.json`: dati comuni (mano, dimensioni, finale legacy) e `boardOrder`, l'ordine delle lavagne.
- `boards/lavagnaN.json` (N = 1…6): la lavagna (titolo, anni, colore, regione, cerchio finale), le `sections` con cue EN/IT, tempi, audio, stop (`photo`) e note, le `labels` e gli `unknowns`. **Le correzioni di testo si fanno qui.**
- `boards/lavagnaN.art.json`: i disegni della lavagna (immagine, posizione, percorsi del pennarello). File grosso, di solito non si tocca.
- `build.py` legge i file nell'ordine di `boardOrder` (`tools/boardfiles.py`, `load_all`) e produce come prima un solo `index.html` autonomo.

Script per lavagna in `tools/`: `boardN_text.json` (testi EN/IT), `boardN_tts.py` (voce edge-tts dal file comune `tools/voice.py`: en-US-EmmaMultilingualNeural +0%, WordBoundary), `boardN_build.py` (disegni → percorsi, cue allineati alla voce, scrive `boards/lavagnaN*.json`; **riscrive da zero** i due file della lavagna, quindi le modifiche a mano vanno ripetute: per una prova `BOARDS_OUT=/tmp/x python3 tools/boardN_build.py`). Nella Lavagna 3, la maschera di Pulcinella sullo speaker della demo Sanitas (richiesta di Lele, 19/11/2026) nasce da `tools/l3_mask.py`: parte da `from-gen/l3-sanitas.orig.jpg` + `from-gen/pulcinella-mask.jpg` (cartella locale, non pubblicata), scrive `from-gen/l3-sanitas.jpg` e un percorso extra del pennarello (`from-gen/l3-sanitas.extra-path.json`) che `board3_build.py` inserisce, così la maschera sopravvive a ogni rigenerazione. La Lavagna 1 non ha uno script di generazione: si modifica direttamente `boards/lavagna1.json`. `tools/split_scenes.py` è lo script una tantum che ha fatto la divisione.

Per aggiungere una lavagna: creare `boards/lavagnaN.json` e `.art.json` e aggiungere l'id a `boardOrder`. Alla fine dell'ultima lavagna il player fa uno zoom indietro su tutte le lavagne e resta fermo.

## Aprire e presentare
Aprire **index.html** in Chrome, Edge o Safari. È un file autonomo: include scene, immagini, mano e font; non servono rete, installazioni, server o accesso a Drive. Formato di disegno 1920×1080, rapporto 16:9 con bande esterne quando necessario.

- **SPAZIO / clic sulla lavagna**: il primo avvia. Durante la riproduzione mettono in **pausa** tutto (voce, mano e tratti, timer, camera, spezzone video) e il successivo riprende esattamente da lì; in pausa compare un piccolo ❚❚ semitrasparente in alto a destra e i comandi restano visibili. Sugli stop delle foto in attesa continuano come prima; se sullo stop sta girando lo spezzone (o la sua attesa di 1,5 s) lo mettono in pausa/riprendono, e a spezzone finito proseguono. Pulsante ❚❚ Pausa / ▶ Riprendi nella barra.
- In pausa: ← → R e la barra di avanzamento saltano e **riprendono** la riproduzione; + − (velocità) e I (lingua) funzionano e la pausa resta. Test: `node /workspace/test_pause.cjs`.
- Scritte e disegni non si tagliano: le note scritte nei disegni generati (`fit_note` in `tools/board2/3/4_build.py`) stanno sempre dentro l'immagine con discendenti e accenti; nel player i disegni si sovrappongono in 'multiply', così la carta bianca di un disegno non copre l'inchiostro del vicino. Solo un disegno appoggiato in gran parte sopra un altro (>20%, Valencia sulla mappa) tiene la carta opaca.
- **R**: ricomincia immediatamente anche durante una foto o un disegno.
- **I**: cambia EN/IT subito, senza ricominciare (la voce resta EN).
- **F** o pulsante: tutto schermo; ESC per uscire.
- **Comandi e barra**: compaiono appena si muove il mouse (o si tocca lo schermo) e spariscono con una dissolvenza dopo 2 secondi di mouse fermo, insieme al cursore; restano visibili finché il mouse è sopra la fascia comandi o si trascina la barra. Con i comandi visibili il sottotitolo sale un poco per non sovrapporsi.
- **H**: cambia modalità comandi, con un breve avviso in alto: automatici (col mouse) → sempre visibili → sempre nascosti (per la proiezione: il mouse non li fa ricomparire) → automatici. Il pulsante «Nascondi comandi» li nasconde fissi; si riportano con H.
- **→** (o pulsante **Avanti ▸▸**): salta alla fine della scena in corso (allo stop foto/pausa se c'è); su uno stop passa alla scena successiva.
- **←** (o pulsante **◂◂ Indietro**): torna all'inizio della scena; se si è entro i primi 2 secondi, alla scena precedente.
- **+** / **=** e **−** / **_** (o pulsante **Velocità**): 1× → 2× → 4×. Voce (playbackRate), disegno, mano e camera accelerano insieme; quando non si è a 1× compare l'indicatore in alto a destra.
- **Barra di avanzamento** (in cima alla fascia comandi): clic o trascinamento per saltare in qualsiasi punto dell'intervento (con `?lavagna=N` solo di quella lavagna). Segmenti nel colore di ogni lavagna, tacche bianche sugli stop foto, nome della scena al passaggio del mouse. Dopo un salto voce, sottotitoli e disegno si riallineano (le scene precedenti compaiono già complete). Si vede solo insieme ai comandi (H o mouse sulla fascia bassa): in proiezione con i comandi nascosti non c'è.
- Limiti: la barra misura il tempo della voce (movimenti di camera e finali non contano); lo stop "Il nome" riparte sempre dall'inizio.
- Gli stop non scadono mai da soli. Il finale resta visibile finché non si preme R.

I quattro spezzoni hanno foto/stop; tra 3 e 4 è incluso uno stop breve **Il nome, inventato insieme**, senza voce inventata. Lo stop del sito 2006 è dichiaratamente **immagine d'archivio da inserire**, non un falso screenshot. Le due ricostruzioni AI sono etichettate sempre.

Durata automatica della sola Lavagna 1 nella prima versione: circa **3 minuti e 15 secondi** (voce attuale di tutte e sei le lavagne: vedi sotto), più il tempo dei cinque stop scelto dai presentatori. Non viene imposta una durata alle parti a braccio; i 15 minuti sono il riferimento dell'intero intervento, non un conto alla rovescia di questa sola lavagna.

## Cosa manca prima della versione evento
1. **Voce narrante EN**: nessun TTS gratuito già funzionante presente sul box; non sono stati attivati servizi. I testi EN sono in `audio/narration-en.txt`.
2. **Screenshot autentico sito 2006**: da Donatello, sostituire il segnaposto.
3. **3 bis / il nome**: nel Doc mancano copione, alternative e dettagli quando/dove; noto solo che il nome fu inventato insieme. Non è stata inventata una storia.
4. Confronto finale con Lele della ricostruzione del dentista e prova sul browser/HDMI effettivo. Le somiglianze AI sono approssimative, non foto storiche.

La mano reale da Pakutaso è stata integrata con chroma key, non è più quella da fumetto. Il file fornito non mostra una mano particolarmente pelosa; non sono stati aggiunti peli artificiali. La punta è ancorata al tratto. Restano da approvare artisticamente questo aspetto e lo stile complessivo.

## Voce: "Gef" e rigenerazione (dal 19/11/2026)
Nei testi (voce EN e sottotitoli EN/IT) Gianfranco è **Gef**. Gli script TTS passano a edge-tts "Jeff" (pronuncia corretta) ma tengono "Gef" nei sottotitoli e nei tempi parola per parola (`spoken` nei file `audio/*.words.json`). Lavagna 1 non ha un generatore: `python3 tools/board1_tts.py football remote name` rigenera la voce delle sezioni indicate e ritempra i loro sottotitoli direttamente in `boards/lavagna1.json`. Lavagne 2–6: `python3 tools/boardN_tts.py <sezioni>` e poi `python3 tools/boardN_build.py`. Le Lavagne 5 e 6 (27/11/2026) usano il generatore comune `tools/boardlate.py` (colore, maschera dell'accento, note, cerchio finale); `board5_build.py`/`board6_build.py` contengono solo la configurazione. Nelle note delle sezioni, «ATTESA CLAUDE: dubbio N» segna le formulazioni prudenti in attesa di conferma (dubbi elencati nel Log del wiki, 27/11/2026). Disegni generati con AI (indicato negli `unknowns`); stop foto solo su reperti veri: mail Docplanner del 27/11/2018 ricomposta con mittente oscurato, card dei moduli della grafica Tuotempo 20 (dati nelle card inventati, dichiarato in didascalia).

Sottotitoli (dal 20/11/2026, richiesta di Gef): testo bianco in grassetto (peso 600), carattere sans di sistema, circa 38 px su schermo 1920×1080 (scala con lo schermo), su una fascia scura semitrasparente (nero al 65%) con angoli arrotondati, centrati in basso, al massimo 2 righe. Quando compaiono i comandi i sottotitoli salgono sopra la barra. Durante gli stop foto i sottotitoli non compaiono.

## Voce Emma ed etichette degli anni (dal 19/11/2026)
- **Voce**: tutta la narrazione è **en-US-EmmaMultilingualNeural, velocità +0%** (scelta di Lele sul campione 03), impostata in un solo punto, `tools/voice.py`, usato da `board1_tts.py` … `board6_tts.py`. Le correzioni di pronuncia valgono solo per il testo dato alla voce (`SPOKEN` in `tools/voice.py`); sottotitoli e tempi tengono il testo scritto: Gef → "Jeff", Ugo → "Oogo" (Emma diceva "Yugo"), Farini → "Fareeni" (Emma diceva "Fa-rai-ni"). Controllo fatto con una trascrizione automatica (faster-whisper) della voce generata.
- Durate voce (27/11/2026): L1 2'27", L2 2'36", L3 1'47", L4 1'49", L5 1'40", L6 1'40", totale 11'58" (718 s).
- **Etichette**: le lavagne possono avere un `tag` oltre agli anni. Lavagna 2 «In casa · 2007–2011», Lavagna 3 «All’estero · 2009–2015» (2 e 3 sono storie parallele). L'etichetta compare nella schermata iniziale di `?lavagna=N`, nel cerchio finale della lavagna e nella linea del tempo finale. Lavagna 5 «The race · 2019–2022» (arancio), Lavagna 6 «Back on course · 2022–2026» (magenta). La linea del tempo finale è in anni (2005 → 2026): le lavagne che si sovrappongono stanno su tracce parallele (Lavagna 3 sotto la 2).
- **Cartello** «intanto, all’estero…» (etichetta `small` in `tools/board3_build.py`): la mano lo scrive all'inizio della Lavagna 3, prima della voce (circa 2,8 s, non conteggiati nella barra); la voce non cambia.

## Didascalie delle foto e video dell'agenda 2007 (dal 20/11/2026)
- Le didascalie delle foto (titolo e riga sotto) sono **sempre in inglese**, qualunque sia la lingua dei sottotitoli (Lele). Le foto ricostruite restano dichiarate: «AI reconstruction · …» (agenda di carta, dentista).
- Stop «The calendar · Thursday, June 14, 2007» (Lavagna 2, primi clienti): il fotogramma resta fermo 1,5 s (`photo.videoDelay`), poi nella stessa cornice parte uno spezzone del video promozionale originale «tuOtempO Memo» (https://www.youtube.com/watch?v=thgtysRhaWU, 20/07/2007), **da 1:16,0 a 1:27,6** (11,6 s, con dissolvenza audio finale, con l'audio inglese: "Select the available time slot and create the appointment…"). Finito lo spezzone resta l'ultimo fotogramma e lo stop aspetta Spazio/clic; Spazio, R, ←, → lo fermano. File: `assets/memo2007-agenda-clip.mp4` (H.264 baseline 320×240 + AAC 96k, 86 KB, incorporato in index.html, quindi funziona offline e su GitHub Pages).
- Rifare lo spezzone (27/11: accorciato a 11,6 s, 1:16,0–1:27,6, e chiuso con una dissolvenza audio di 1,8 s): misura `ffmpeg -ss 76.0 -t 11.6 -i memo2007.mp4 -af loudnorm=I=-18.5:TP=-1.5:LRA=11:print_format=json -f null -`, poi `ffmpeg -ss 76.0 -t 11.6 -i memo2007.mp4 -c:v libx264 -preset slow -crf 22 -pix_fmt yuv420p -profile:v baseline -level 3.0 -r 30 -af "loudnorm=I=-18.5:TP=-1.5:LRA=11:measured_I=…:measured_TP=…:measured_LRA=…:measured_thresh=…:offset=…:linear=true,aresample=44100,afade=t=in:st=0:d=0.15,afade=t=out:st=9.8:d=1.8" -c:a aac -b:a 96k -ac 2 -movflags +faststart assets/memo2007-agenda-clip.mp4` (`-ss` prima di `-i`, così i tempi delle dissolvenze partono da 0). Risultato: −18,6 LUFS integrati; il primo secondo ha livello pieno, poi da 9,8 s sfuma fino a zero a 11,6 s. Il vecchio file (13,6 s, taglio netto) è in `/workspace/tuotempo-materiali/backup/memo2007-agenda-clip-v2.mp4`.
- Audio dello spezzone: l'elemento video viene «sbloccato» al primo clic/tasto (play muto + pausa), così allo stop parte con l'audio anche se avviato da un timer; se il browser rifiuta comunque l'audio, lo spezzone parte muto e compare il pulsante «🔊 click for sound».

## Ordine dei tratti (dal 18/11/2026)
`build.py` passa ogni disegno per `tools/stroke_order.py`: la mano completa un oggetto prima di passare al successivo. Gli oggetti sono i blocchi d'inchiostro separati (figure, parole, cartelli); un blocco grande quanto una scena viene diviso in parti compatte, tenendo separato l'inchiostro colorato (es. l'auto viola). Oggetti da sinistra a destra, ogni parola scritta lettera per lettera da sinistra a destra. Le fini degli oggetti (`breaks`) servono al player per chiudere ogni sottotitolo su un oggetto finito (tolleranza ±8% del disegno). I file `boards/*.art.json` conservano l'ordine grezzo dei generatori: rigenerare una lavagna non perde la correzione. Anteprime: `python3 tools/preview_stroke_order.py` → `/workspace/previews/ordine-tratti/`.

## Correggere scene e aggiungere voce
La fonte modificabile sono i file in **boards/** (vedi sopra), non l'HTML generato; qui sotto «scenes.json» indica quei file. `sections` contiene testi, sottotitoli EN/IT, durate, assegnazioni ai disegni, foto e audio. `art` contiene asset e percorsi del pennarello. Il player non legge JSON esterni all'apertura per evitare i blocchi `file://` dei browser.

Dopo una modifica:

```sh
cd tuotempo-lavagna1
python3 build.py
```

Per una voce locale: salvare, ad esempio, `audio/01-origins.mp3` e impostare `sections[0].audio` a quel percorso. La build integra anche l'audio nel file autonomo. Nessun caricamento esterno.
- Le durate dei sottotitoli vengono scalate alla durata dell'audio se disponibile.
- L'audio viene fermato durante gli spostamenti di camera e gli stop.
- Per allineamento puntuale aggiungere `start` e `end` (secondi nella traccia) a ogni cue. Controllare poi ogni spezzone con il file voce reale.
- Nessuna voce di browser viene avviata automaticamente.

Per il sito storico: impostare la foto della sezione `remote`: `src: "assets/sito-2006.jpg"`, `kind: "original"`, `disclosure: ""`. Poi build.

Per sostituire la mano: mettere un PNG trasparente in `assets/hand.png` e adattare `hand.tip` (coordinate pixel della punta), `hand.rotation` (radianti) e `hand.width`. Se si parte da green screen, il codice di scontorno originale è in `prepare_assets.py` (dipende da Pillow, NumPy e OpenCV).

**Non rilanciare prepare_assets.py per modificare i testi**: serve a ricostruire gli asset originali e riscrive il manifesto dal Doc salvato in questa sessione. Per normali correzioni bastano `boards/lavagnaN.json` + `build.py`.

## File e provenienza
- `poc-v2/`: sorgenti originali conservati.
- `from-mac/`: file già copiati dal parent col permesso di Lele; nessun ulteriore accesso al Mac.
- `assets/`: immagini originali/preparate, atlante dei disegni generati, ricostruzioni AI e font offline.
- `docs/storyboard-lavagna1.txt`: snapshot Lavagna 1 del Google Doc `1dA9Ja1mzXY14iAMeijzxuCZBTltaXgKtXV0viZfAXMs` letto tramite connettore.
- `docs/ganci-presentatori.md`: ganci dal Doc, mai sovrapposti alle foto in proiezione.
- `tests/`: prove manifest e DOM/Canvas. `tests/final-board.png` e `reveal-with-hand.png` sono render del Canvas, **non screenshot di un browser**.

Foto mano: Pakutaso, © susi-paku, file `GREEN_magic_TP_V.jpg` fornito. Font Patrick Hand / Caveat disponibili sul box, licenze OFL incluse in assets. Foto università originale incorporata nella POC; altre due foto sono ricostruzioni AI.

## Verifica tecnica eseguita
Test Python: manifesto, quattro sezioni + nome, corrispondenza integrale voce EN, asset, build offline, ritaglio del dente. Test Node: caricamento immagini, switch EN/IT, reset durante disegno e foto, pause indefinite, ordine dei cinque stop, disclaimer e zoom finale, nessun errore runtime nel DOM simulato.

Non è stata effettuata una prova in un browser reale né sul proiettore: il relativo strumento non era disponibile. Fullscreen, CSS dei polaroid e sincronizzazione con audio reale richiedono quindi una prova sul portatile prima dell'evento.

## Inglese, numeri di scena, link a un momento (20/11)
- Tutto il testo visibile del player è in inglese (comandi, stati, avvisi H, schermata iniziale, etichette delle scene, cartello «meanwhile, abroad…», etichette delle lavagne «At home · 2007–2011» / «Abroad · 2009–2015», note nei disegni Rome, Dublin, Barcelona, Lyon). Restano in italiano solo i sottotitoli IT (tasto I) e i nomi propri (Bologna · via Ugo Bassi, via San Felice, Alma Mater Studiorum). Le note nei disegni passano per `fit_note`.
- Barra: tacche e numeri di scena «lavagna.scena» (2.3 = Lavagna 2, terza scena); al passaggio del mouse «Scene 2.3 · titolo · mm:ss». Stato: «Scene 2.3 · 04:12».
- «🔗 Share this moment» copia `https://culetti.github.io/tuotempo-lavagna/#s=2.3&t=04:12` (toast «Link copied»; senza appunti mostra il link selezionabile). Un link con `#t=MM:SS` (o solo `#s=2.3`) apre la lavagna disegnata fino a quella scena e aspetta il clic: «Starts at Scene 2.3 · 04:12 — click to play». Il tempo è quello della barra (secondi di voce). Test: `node /workspace/test_link.cjs`.
