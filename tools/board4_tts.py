import asyncio,json,re,sys
from pathlib import Path
import edge_tts
P=Path(__file__).resolve().parent.parent
T=json.load(open(P/'tools/board4_text.json'))
norm=lambda s:re.sub(r'[^0-9a-z]','',s.lower())
async def one(sec):
    text=' '.join(c[0] for c in sec['cues'])
    c=edge_tts.Communicate(text,"en-GB-SoniaNeural",rate="+8%",boundary="WordBoundary")
    words=[];mp3=P/'audio'/f"{sec['id']}-en.mp3"
    with open(mp3,'wb') as f:
        async for ch in c.stream():
            if ch['type']=='audio':f.write(ch['data'])
            elif ch['type']=='WordBoundary':words.append({'offset':ch['offset'],'duration':ch['duration'],'text':ch['text']})
    json.dump({'voice':'en-GB-SoniaNeural','rate':'+8%','boundary':'WordBoundary','text':text,'words':words},open(P/'audio'/f"{sec['id']}-en.words.json",'w'),indent=1)
    return words
async def main():
    out={}
    for sec in T:
        out[sec['id']]=await one(sec)
    json.dump(out,open('/tmp/b4words.json','w'))
asyncio.run(main())
