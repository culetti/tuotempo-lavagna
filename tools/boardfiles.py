"""Shared helpers: read/write the per-board files in boards/.
boards/common.json        global data (hand, player settings, legacy L1 final)
boards/lavagnaN.json      board entry, sections (cues EN/IT, photos, notes), labels, unknowns  <- edit text here
boards/lavagnaN.art.json  drawings: image size/position + pen paths (big, rarely edited)"""
import json,os
from pathlib import Path
P=Path(__file__).resolve().parent.parent;B=P/'boards'
def _dump(o,ind):return ('\n'+' '*ind).join(json.dumps(o,ensure_ascii=False,indent=2).split('\n'))
def write_board(bid,board,sections,labels,unknowns,art):
 B=Path(os.environ.get('BOARDS_OUT',P/'boards'));B.mkdir(parents=True,exist_ok=True)
 t=('{\n  "board": '+_dump(board,2)+',\n  "sections": '+_dump(sections,2)+',\n  "labels": '+_dump(labels,2)+',\n  "unknowns": '+_dump(unknowns,2)+'\n}\n')
 json.loads(t);(B/f'{bid}.json').write_text(t,encoding='utf8')
 parts=[]
 for k,a in art.items():
  head={x:v for x,v in a.items() if x!='path'}
  parts.append('  '+json.dumps(k)+': '+_dump(head,2)[:-1].rstrip()+',\n    "path": '+json.dumps(a['path'],separators=(',',':'))+'\n  }')
 t='{\n'+',\n'.join(parts)+'\n}\n';json.loads(t);(B/f'{bid}.art.json').write_text(t,encoding='utf8')
def board_ids():
 return json.loads((B/'common.json').read_text())['boardOrder']
def load_all():
 """Assemble the single DATA object (same key order as the old scenes.json)."""
 c=json.loads((B/'common.json').read_text());d={k:c[k] for k in ['version','title','years','sourceDoc','sourceRevision','board','hand']}
 d['art']={};d['sections']=[];boards=[];labels=[];unk=[]
 for bid in c['boardOrder']:
  b=json.loads((B/f'{bid}.json').read_text());d['art'].update(json.loads((B/f'{bid}.art.json').read_text()))
  d['sections']+=b['sections'];boards.append(b['board']);labels+=b['labels'];unk+=b['unknowns']
 d['final']=c['final'];d['boards']=boards;d['labels']=labels;d['unknowns']=unk
 return d
