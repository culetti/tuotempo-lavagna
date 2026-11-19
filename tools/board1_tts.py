"""Lavagna 1 has no generator (made once by prepare_assets.py, never to be run again): this regenerates the voice of
the given sections straight from the cues in boards/lavagna1.json and re-times those cues with the WordBoundary
events, the same way tools/boardN_build.py does. Narration is rebuilt from the cues.
Usage: python3 tools/board1_tts.py football remote name"""
import asyncio,json,re,sys,subprocess
from pathlib import Path
import edge_tts
P=Path(__file__).resolve().parent.parent
SAY=lambda t:re.sub(r'\bGef\b','Jeff',t)    # Gef is pronounced like 'Jeff'
UNSAY=lambda t:re.sub(r'\bJeff\b','Gef',t)
norm=lambda s:re.sub(r'[^0-9a-z]','',s.lower())
dur=lambda f:float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(f)]).decode())
async def one(sec):
    text=' '.join(c['en'] for c in sec['cues']);spoken=SAY(text)
    c=edge_tts.Communicate(spoken,"en-GB-SoniaNeural",rate="+8%",boundary="WordBoundary")
    words=[];mp3=P/'audio'/f"{sec['id']}-en.mp3"
    with open(mp3,'wb') as f:
        async for ch in c.stream():
            if ch['type']=='audio':f.write(ch['data'])
            elif ch['type']=='WordBoundary':words.append({'offset':ch['offset'],'duration':ch['duration'],'text':UNSAY(ch['text'])})
    json.dump({'voice':'en-GB-SoniaNeural','rate':'+8%','boundary':'WordBoundary','text':text,'spoken':spoken,'words':words},open(P/'audio'/f"{sec['id']}-en.words.json",'w'),indent=1)
    total=dur(mp3);wi=0
    for k,cue in enumerate(sec['cues']):
        need=norm(cue['en']);got='';first=None
        while wi<len(words) and len(got)<len(need):
            w=words[wi];first=first or w;got+=norm(w['text']);last=w;wi+=1
        assert got==need,(sec['id'],cue['en'],got,need)
        cue['start']=round(first['offset']/1e7,6)
        cue['end']=round(total,6) if k==len(sec['cues'])-1 else round((last['offset']+last['duration'])/1e7,6)
        cue['duration']=round(cue['end']-cue['start'],6)
    assert wi==len(words),sec['id']
    sec['narration']={'en':' '.join(c['en'] for c in sec['cues']),'it':' '.join(c['it'] for c in sec['cues'])}
    if 'audioDuration' in sec:sec['audioDuration']=round(total,3)
    print(sec['id'],round(total,2),'s')
async def main():
    f=P/'boards/lavagna1.json';d=json.load(open(f));only=set(sys.argv[1:])
    for sec in d['sections']:
        if sec['id'] in only:await one(sec)
    open(f,'w').write(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
asyncio.run(main())
