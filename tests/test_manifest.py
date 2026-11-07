import json,pathlib,unittest
P=pathlib.Path(__file__).resolve().parents[1]
class ManifestTests(unittest.TestCase):
 def test_manifest_exists(self): self.assertTrue((P/'scenes.json').exists(),'Manca il manifesto delle scene completo')
 def test_four_sections_and_name(self):
  if not (P/'scenes.json').exists(): self.skipTest('Manifesto assente')
  d=json.loads((P/'scenes.json').read_text());self.assertEqual([s['id'] for s in d['sections']],['origins','football','remote','name','dentist'])
  for s in d['sections']:
   if s['id']=='name':self.assertTrue(s['narration']['en']);self.assertTrue(s['audio']);continue
   self.assertTrue(s['photo']);self.assertTrue(s['cues']);self.assertEqual(' '.join(c['en'] for c in s['cues']),s['narration']['en'])
   self.assertNotIn('Fabio',s['narration']['en']);self.assertNotIn('Flacco',s['narration']['en'])
   for c in s['cues']:self.assertTrue(c['it']);self.assertGreater(c['duration'],0)
 def test_assets(self):
  if not (P/'scenes.json').exists():self.skipTest('Manifesto assente')
  d=json.loads((P/'scenes.json').read_text())
  for a in d['art'].values():self.assertTrue((P/a['src']).is_file());self.assertGreater(len(a['path']),0)
  self.assertTrue((P/'assets/hand.png').exists())
 def test_tooth_is_in_dentist_crop(self):
  from PIL import Image
  import numpy as np
  a=np.array(Image.open(P/"assets/dentist.png"));h,w=a.shape[:2];r=a[:int(h*.35),int(w*.4):int(w*.65)].astype(int);red=(r[:,:,0]>r[:,:,1]+35)&(r[:,:,0]>r[:,:,2]+30);self.assertGreater(red.sum(),300,"Il ritaglio del dentista deve contenere il dente rosso in alto")
 def test_offline_build(self):
  self.assertTrue((P/'index.html').exists(),'Manca il player offline')
  if (P/'index.html').exists():
   h=(P/'index.html').read_text();self.assertNotIn('fonts.googleapis',h);self.assertIn('data:image/png;base64,',h);self.assertNotIn('__DATA__',h)
if __name__=='__main__':unittest.main()
