from pathlib import Path
import json,base64,mimetypes
P=Path(__file__).parent

def uri(path):
 p=P/path;mime=mimetypes.guess_type(p)[0] or 'application/octet-stream'
 return 'data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode()
d=json.loads((P/'scenes.json').read_text())
for art in d['art'].values():art['src']=uri(art['src'])
d['hand']['src']=uri(d['hand']['src'])
for s in d['sections']:
 if s['photo'] and s['photo']['src']:s['photo']['src']=uri(s['photo']['src'])
 if s['photo'] and s['photo'].get('introAudio') and not str(s['photo']['introAudio']).startswith(('data:','http')):s['photo']['introAudio']=uri(s['photo']['introAudio'])
 if s['audio'] and not s['audio'].startswith(('data:','http')):s['audio']=uri(s['audio'])
text=(P/'player.template.html').read_text().replace('__DATA__',json.dumps(d,ensure_ascii=False).replace('</','<\\/')).replace('__PLAYER__',(P/'player.js').read_text()).replace('__HAND_FONT__',uri('assets/PatrickHand-Regular.ttf')).replace('__TITLE_FONT__',uri('assets/Caveat-VariableFont_wght.ttf'))
(P/'index.html').write_text(text,encoding='utf8')
print('Built index.html:',round(len(text)/1024),'KB; fully offline, file:// compatible')
