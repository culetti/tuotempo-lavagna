"""One-off: split the old monolithic scenes.json into boards/*.json (kept for history)."""
import json,sys
from boardfiles import P,B,write_board,_dump
d=json.loads((P/'tools/scenes.legacy-before-split.json').read_text())
common={k:d[k] for k in ['version','title','years','sourceDoc','sourceRevision','board','hand','final']}
common['boardOrder']=[b['id'] for b in d['boards']]
(B/'common.json').write_text(json.dumps(common,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
used=set()
for b in d['boards']:
 secs=[s for s in d['sections'] if s['id'] in b['sections']]
 keys=[k for s in secs for k in s['art']];used|=set(keys)
 art={k:v for k,v in d['art'].items() if k in keys}
 labels=[l for l in d['labels'] if l['section'] in b['sections']]
 n=b['id'][-1]
 unk=[u for u in d['unknowns'] if (u.startswith(f'Lavagna {n} ') if n!='1' else not u.startswith('Lavagna '))]
 write_board(b['id'],b,secs,labels,unk,art)
assert used==set(d['art']),set(d['art'])-used
