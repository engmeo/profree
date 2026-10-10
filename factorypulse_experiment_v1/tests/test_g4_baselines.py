import sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from fjsp import parse_fjsp,greedy,makespan
from dynamic import disruption_state,validate_after,generate_events
from g4_baselines import minimal_repair,g4_metrics

class MinimalRepairTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.inst=parse_fjsp(ROOT/'data/mk01.txt')
  cls.base=greedy(cls.inst)
 def test_all_36_cases_valid_and_deterministic(self):
  for ev in generate_events(self.inst,self.base):
   with self.subTest(ev=ev):
    state=disruption_state(self.inst,self.base,ev['time'],ev['machine'],ev['duration'])
    a=minimal_repair(state)
    self.assertEqual(a,minimal_repair(state))
    self.assertEqual([],validate_after(state,a))
    original=state['baseline']
    for row in a:
     k=(row['job'],row['op'])
     self.assertEqual(row['machine'],original[k]['machine'])
     if k in state['fixed']:
      self.assertEqual(row,state['fixed'][k])
     else:
      self.assertGreaterEqual(row['start'],max(state['time'],original[k]['start']))
    for m in range(self.inst['machines']):
     def ordered(rows):
      return [(r['job'],r['op']) for r in sorted(rows,key=lambda r:(r['start'],r['end'],r['job'],r['op'])) if r['machine']==m]
     self.assertEqual(ordered(state['baseline'].values()),ordered(a))
 def test_failed_running_restarts_and_unaffected_fixed(self):
  op=next(x for x in self.base if x['end']-x['start']>1)
  state=disruption_state(self.inst,self.base,op['start']+1,op['machine'],5)
  plan={ (r['job'],r['op']):r for r in minimal_repair(state)}
  k=(op['job'],op['op'])
  self.assertEqual(state['states'][k],'RUNNING_FAILED')
  self.assertGreaterEqual(plan[k]['start'],state['time']+5)
  for k,row in state['fixed'].items():self.assertEqual(row,plan[k])
 def test_metrics_undefined_when_no_loss(self):
  a=[dict(end=10)]; b=[dict(end=8)]
  x=g4_metrics(a,b,a,b)
  self.assertIsNone(x['R_recovery_pct'])
  self.assertEqual(x['G_global'],2)
 def test_positive_loss_and_over_100_percent_not_clamped(self):
  a=[dict(end=10)];b=[dict(end=8)];c=[dict(end=15)];d=[dict(end=7)]
  x=g4_metrics(a,b,c,d)
  self.assertEqual(x['L_event'],5)
  self.assertEqual(x['G_response'],8)
  self.assertEqual(x['R_recovery_pct'],160)

if __name__=='__main__':unittest.main()
