"""Narration voice for every board (one place): tools/board1_tts.py … board4_tts.py import it.
Changed on 19/11/2026 from en-GB-SoniaNeural +8% to en-US-EmmaMultilingualNeural +0% (Lele: sample 03).
SAY() only changes what the voice is given; subtitles and word timings keep the written text (UNSAY)."""
import re
VOICE="en-US-EmmaMultilingualNeural"
RATE="+0%"
# written -> spoken (only what the voice is given). Gef is pronounced like 'Jeff'.
SPOKEN={'Gef':'Jeff','Ugo':'Oogo','Farini':'Fareeni'}  # checked with a speech-to-text pass: Emma says 'Yugo' and 'Fa-RAI-ni' otherwise
def SAY(t):
    for w,s in SPOKEN.items():t=re.sub(r'\b'+re.escape(w)+r'\b',s,t)
    return t
def UNSAY(t):
    for w,s in SPOKEN.items():t=re.sub(r'\b'+re.escape(s)+r'\b',w,t)
    return t
