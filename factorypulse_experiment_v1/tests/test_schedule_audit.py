import copy, hashlib, json, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'src'))
from fjsp import parse_fjsp,greedy,makespan
from dynamic import disruption_state
from g4_baselines import minimal_repair
from audit_schedules import audit

class ScheduleArtifactTests(unittest.TestCase):
 def setUp(self):
  self.path=ROOT/'data/mk01.txt';self.inst=parse_fjsp(self.path);self.base=greedy(self.inst)
  op=next(r for r in self.base if r['end']-r['start']>1)
  self.ev={'time':op['start']+1,'machine':op['machine'],'duration':5}
  self.c1=minimal_repair(disruption_state(self.inst,self.base,self.ev['time'],self.ev['machine'],self.ev['duration']))
  self.rec={'origin':'heuristic','case_id':0,'event':self.ev,'status':'NO_SOLUTION',
   'solver':{'status':'UNKNOWN'},'C0_schedule':self.base,'C0_makespan':makespan(self.base),
   'C1_schedule':self.c1,'C1_makespan':makespan(self.c1)}
  self.run={'instance':'mk01.txt','source_sha256':hashlib.sha256(self.path.read_bytes()).hexdigest(),'arms':[self.rec]}
 def check(self):
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)/'raw.json';out.write_text(json.dumps(self.run))
   return audit(out,self.path)
 def test_valid_c1_unknown_c2(self):self.assertEqual(self.check(),[])
 def test_missing_c1_rejected(self):
  del self.rec['C1_schedule'];self.assertTrue(any('missing C1' in x for x in self.check()))
 def test_changed_fixed_rejected(self):
  s=disruption_state(self.inst,self.base,self.ev['time'],self.ev['machine'],self.ev['duration'])
  k=next(iter(s['fixed']))
  for r in self.c1:
   if (r['job'],r['op'])==k:r['start']+=1;break
  self.assertTrue(self.check())
 def test_wrong_input_hash(self):
  self.run['source_sha256']='0'*64;self.assertTrue(any('SHA-256' in x for x in self.check()))
 def test_fake_complete_rejected(self):
  self.rec['status']='COMPLETE';self.rec['solver']['status']='OPTIMAL';self.assertTrue(any('missing C2' in x for x in self.check()))

if __name__=='__main__':unittest.main()
