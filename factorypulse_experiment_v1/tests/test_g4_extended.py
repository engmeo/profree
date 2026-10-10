import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from fjsp import parse_fjsp,greedy,makespan
from dynamic import disruption_state,validate_after
from g4_baselines import minimal_repair
from g4_extended import validate_counterfactual,paired_metrics,independently_check_record
from g4_extended_static import solver_gap,classify_solver_status
class ExtendedTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.inst=parse_fjsp(ROOT/'data/mk01.txt');cls.base=greedy(cls.inst)
  op=next(x for x in cls.base if x['end']-x['start']>1)
  cls.event={'time':op['start']+1,'machine':op['machine'],'duration':5}
  cls.state=disruption_state(cls.inst,cls.base,**{'t':cls.event['time'],'failed_machine':cls.event['machine'],'duration':cls.event['duration']})
 def test_preserves_previously_completed_work(self):
  rows=minimal_repair(self.state)
  idx={(r['job'],r['op']):r for r in rows}
  for k,r in self.state['fixed'].items():self.assertEqual(idx[k],r)
 def test_independent_validator_checks_fixed(self):
  rows=minimal_repair(self.state)
  fixed=next(iter(self.state['fixed']),None)
  if fixed is None:self.skipTest('no frozen operation in selected event')
  r=next(x for x in rows if (x['job'],x['op'])==fixed);r['start']+=1
  self.assertTrue(validate_counterfactual(self.inst,self.base,self.event,rows))
 def test_downtime_and_precedence(self):
  rows=minimal_repair(self.state)
  self.assertEqual(validate_counterfactual(self.inst,self.base,self.event,rows),[])
 def test_undefined_ratio(self):
  self.assertIsNone(paired_metrics(5,5,4)['recovery_ratio'])
  self.assertIsNone(paired_metrics(5,4,4)['recovery_ratio'])
  self.assertEqual(paired_metrics(5,10,15)['response_gain'],-5)
 def test_gap(self):
  self.assertEqual(solver_gap('OPTIMAL',40,40),0)
  self.assertIsNone(solver_gap('UNKNOWN',None,None))
  self.assertAlmostEqual(solver_gap('FEASIBLE',60,40),1/3)
  with self.assertRaises(ValueError):solver_gap('FEASIBLE',30,40)
 def test_correct_semantics(self):
  self.assertEqual(classify_solver_status(dict(status='FEASIBLE',makespan=40,validation_errors=[])),'VALID_SOLUTION')
  self.assertEqual(classify_solver_status(dict(status='OPTIMAL',makespan=40,validation_errors=['overlap'])),'INVALID_SOLUTION')
  self.assertEqual(classify_solver_status(dict(status='UNKNOWN')),'UNKNOWN')
 def test_integrity(self):
  self.assertTrue(independently_check_record(dict(status='COMPLETE',solver={'status':'UNKNOWN'},C2_makespan=None,validator_errors=None)))
  self.assertEqual(independently_check_record(dict(status='COMPLETE',solver={'status':'FEASIBLE'},C2_makespan=50,validator_errors=[])),[])
if __name__=='__main__':unittest.main()
