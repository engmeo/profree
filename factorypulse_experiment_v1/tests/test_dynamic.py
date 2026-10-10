import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from fjsp import parse_fjsp,greedy
from dynamic import disruption_state,validate_after,greedy_repair,generate_events

class DynamicTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.inst=parse_fjsp(ROOT/'data/mk01.txt');cls.base=greedy(cls.inst)
  # Event at first genuinely running interval rather than assuming a specific hardcoded machine.
  cls.op=next(x for x in cls.base if x['end']-x['start']>1)
  cls.t=cls.op['start']+1
  cls.state=disruption_state(cls.inst,cls.base,cls.t,cls.op['machine'],5)
 def test_valid_repair(self):self.assertEqual(validate_after(self.state,greedy_repair(self.state)),[])
 def test_nonstarted_cannot_time_travel(self):
  p=greedy_repair(self.state);r=next(r for r in p if self.state['states'][r['job'],r['op']]=='NOT_STARTED')
  r['start']=self.t-1
  self.assertTrue(any('before event' in e for e in validate_after(self.state,p)))
 def test_finished_immutable(self):
  fixed=next(iter(self.state['fixed'].values()),None)
  if fixed is None:self.skipTest('no finished job at this t')
  p=greedy_repair(self.state);r=next(x for x in p if (x['job'],x['op'])==(fixed['job'],fixed['op']));r['start']+=1
  self.assertTrue(any('frozen' in e for e in validate_after(self.state,p)))
 def test_running_failed_is_restarted(self):
  k=(self.op['job'],self.op['op']);self.assertEqual(self.state['states'][k],'RUNNING_FAILED')
  p=greedy_repair(self.state);r=next(x for x in p if (x['job'],x['op'])==k)
  self.assertGreaterEqual(r['start'],self.t)
 def test_running_other_immutable(self):
  for k,kind in self.state['states'].items():
   if kind=='RUNNING_UNAFFECTED':
    p=greedy_repair(self.state);r=next(x for x in p if (x['job'],x['op'])==k);r['machine']=-1
    self.assertTrue(validate_after(self.state,p));return
  self.skipTest('no other running operation')
 def test_generator_deterministic(self):
  a=list(generate_events(self.inst,self.base));self.assertEqual(a,list(generate_events(self.inst,self.base)));self.assertEqual(len(a),36)
 def test_wrong_event(self):
  with self.assertRaises(ValueError):disruption_state(self.inst,self.base,-1,0,5)
 def test_downtime_reject(self):
  p=greedy_repair(self.state);r=next(x for x in p if self.state['states'][x['job'],x['op']]=='RUNNING_FAILED');r['machine']=self.op['machine'];r['start']=self.t;r['end']=self.t+self.inst['jobs'][r['job']][r['op']][r['machine']]
  self.assertTrue(validate_after(self.state,p))
if __name__=='__main__':unittest.main()
