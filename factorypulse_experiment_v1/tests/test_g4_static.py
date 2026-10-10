import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from fjsp import parse_fjsp,greedy,validate_schedule,makespan
from g4_static import cp_sat_no_event
class StaticCPTests(unittest.TestCase):
 def test_static_optimum_when_ortools_available(self):
  try:import ortools
  except ImportError:self.skipTest('ortools unavailable locally; CI installs dependency');return
  inst=parse_fjsp(ROOT/'data/mk01.txt')
  r,s=cp_sat_no_event(inst,time_limit=10)
  self.assertIn(r['status'],('OPTIMAL','FEASIBLE'))
  self.assertEqual([],validate_schedule(inst,s))
  self.assertLessEqual(makespan(s),makespan(greedy(inst)))
if __name__=='__main__':unittest.main()
