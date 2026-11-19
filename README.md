# TuoTempo · Lavagna 1 — Le origini



## Link
- Tutte le lavagne (2005–2019): https://culetti.github.io/tuotempo-lavagna/
- Lavagna 1 · Le origini (2005–2007): https://culetti.github.io/tuotempo-lavagna/?lavagna=1
- Lavagna 2 · Le architetture artigianali (2007–2012): https://culetti.github.io/tuotempo-lavagna/?lavagna=2
- Lavagna 3 · L’espansione e gli schiaffi (2009–2016): https://culetti.github.io/tuotempo-lavagna/?lavagna=3
- Lavagna 4 · Verso Docplanner (2016–2019): https://culetti.github.io/tuotempo-lavagna/?lavagna=4

Con `?lavagna=N` (oppure `#lavagnaN`, valido anche per il file `index.html` aperto in locale) la schermata iniziale mostra gli anni di quella lavagna, il player parte direttamente da lì e si ferma sulla sua chiusura (cerchio e anni), senza passare alla lavagna successiva né fare lo zoom finale su tutte. Senza parametro il player è quello completo. Si combina con `speed`, per esempio `?lavagna=3&speed=2`.

## Struttura a file per lavagna (dal 18/11/2026)
Il vecchio `scenes.json` unico è diviso per lavagna, così per correggere una lavagna si apre solo il suo file:

- `boards/common.json`: dati comuni (mano, dimensioni, finale legacy) e `boardOrder`, l'ordine delle lavagne.
- `boards/lavagnaN.json` (N = 1…4): la lavagna (titolo, anni, colore, regione, cerchio finale), le `sections` con cue EN/IT, tempi, audio, stop (`photo`) e note, le `labels` e gli `unknowns`. **Le correzioni di testo si fanno qui.**
- `boards/lavagnaN.art.json`: i disegni della lavagna (immagine, posizione, percorsi del pennarello). File grosso, di solito non si tocca.
- `build.py` legge i file nell'ordine di `boardOrder` (`tools/boardfiles.py`, `load_all`) e produce come prima un solo `index.html` autonomo.

Script per lavagna in `tools/`: `boardN_text.json` (testi EN/IT), `boardN_tts.py` (voce edge-tts en-GB-SoniaNeural +8%, WordBoundary), `boardN_build.py` (disegni → percorsi, cue allineati alla voce, scrive `boards/lavagnaN*.json`; **riscrive da zero** i due file della lavagna, quindi le modifiche a mano vanno ripetute: per una prova `BOARDS_OUT=/tmp/x python3 tools/boardN_build.py`). Nella Lavagna 3, la maschera di Pulcinella sullo speaker della demo Sanitas (richiesta di Lele, 19/11/2026) nasce da `tools/l3_mask.py`: parte da `from-gen/l3-sanitas.orig.jpg` + `from-gen/pulcinella-mask.jpg` (cartella locale, non pubblicata), scrive `from-gen/l3-sanitas.jpg` e un percorso extra del pennarello (`from-gen/l3-sanitas.extra-path.json`) che `board3_build.py` inserisce, così la maschera sopravvive a ogni rigenerazione. La Lavagna 1 non ha uno script di generazione: si modifica direttamente `boards/lavagna1.json`. `tools/split_scenes.py` è lo script una tantum che ha fatto la divisione.

Per aggiungere una lavagna: creare `boards/lavagnaN.json` e `.art.json` e aggiungere l'id a `boardOrder`. Alla fine dell'ultima lavagna il player fa uno zoom indietro su tutte le lavagne e resta fermo.

## Aprire e presentare
Aprire **index.html** in Chrome, Edge o Safari. È un file autonomo: include scene, immagini, mano e font; non servono rete, installazioni, server o accesso a Drive. Formato di disegno 1920×1080, rapporto 16:9 con bande esterne quando necessario.

- **SPAZIO / clic**: avvia; dopo ogni foto riparte. Durante il disegno non salta per errore.
- **R**: ricomincia immediatamente anche durante una foto o un disegno.
- **I**: cambia EN/IT subito, senza ricominciare (la voce resta EN).
- **F** o pulsante: tutto schermo; ESC per uscire.
- **H**: nasconde/mostra i comandi e la barra di avanzamento. All'avvio vengono nascosti; ricompaiono puntando il mouse direttamente sulla fascia inferiore.
- **→** (o pulsante **Avanti ▸▸**): salta alla fine della scena in corso (allo stop foto/pausa se c'è); su uno stop passa alla scena successiva.
- **←** (o pulsante **◂◂ Indietro**): torna all'inizio della scena; se si è entro i primi 2 secondi, alla scena precedente.
- **+** / **=** e **−** / **_** (o pulsante **Velocità**): 1× → 2× → 4×. Voce (playbackRate), disegno, mano e camera accelerano insieme; quando non si è a 1× compare l'indicatore in alto a destra.
- **Barra di avanzamento** (in cima alla fascia comandi): clic o trascinamento per saltare in qualsiasi punto dell'intervento (con `?lavagna=N` solo di quella lavagna). Segmenti nel colore di ogni lavagna, tacche bianche sugli stop foto, nome della scena al passaggio del mouse. Dopo un salto voce, sottotitoli e disegno si riallineano (le scene precedenti compaiono già complete). Si vede solo insieme ai comandi (H o mouse sulla fascia bassa): in proiezione con i comandi nascosti non c'è.
- Limiti: la barra misura il tempo della voce (movimenti di camera e finali non contano); lo stop "Il nome" riparte sempre dall'inizio.
- Gli stop non scadono mai da soli. Il finale resta visibile finché non si preme R.

I quattro spezzoni hanno foto/stop; tra 3 e 4 è incluso uno stop breve **Il nome, inventato insieme**, senza voce inventata. Lo stop del sito 2006 è dichiaratamente **immagine d'archivio da inserire**, non un falso screenshot. Le due ricostruzioni AI sono etichettate sempre.

Durata automatica attuale: circa **3 minuti e 15 secondi**, più il tempo dei cinque stop scelto dai presentatori. Non viene imposta una durata alle parti a braccio; i 15 minuti sono il riferimento dell'intero intervento, non un conto alla rovescia di questa sola lavagna.

## Cosa manca prima della versione evento
1. **Voce narrante EN**: nessun TTS gratuito già funzionante presente sul box; non sono stati attivati servizi. I testi EN sono in `audio/narration-en.txt`.
2. **Screenshot autentico sito 2006**: da Donatello, sostituire il segnaposto.
3. **3 bis / il nome**: nel Doc mancano copione, alternative e dettagli quando/dove; noto solo che il nome fu inventato insieme. Non è stata inventata una storia.
4. Confronto finale con Lele della ricostruzione del dentista e prova sul browser/HDMI effettivo. Le somiglianze AI sono approssimative, non foto storiche.

La mano reale da Pakutaso è stata integrata con chroma key, non è più quella da fumetto. Il file fornito non mostra una mano particolarmente pelosa; non sono stati aggiunti peli artificiali. La punta è ancorata al tratto. Restano da approvare artisticamente questo aspetto e lo stile complessivo.

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
