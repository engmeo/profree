import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ai_swarm.fleet_stress import audit_history, run
from ai_swarm.robust_evidence import _topk, evaluate

class StressChecks(unittest.TestCase):
    def test_stress_many_scenarios(self):
        report=run(seed_count=30,ticks=25)
        self.assertEqual(report['invariant_violations'],0)
        self.assertEqual(report['cases'],30)
    def test_detect_vertex_collision(self):
        frames=[[('a',(0,0)),('b',(1,0))],[('a',(1,0)),('b',(1,0))]]
        self.assertTrue(any(v[1]=='vertex collision' for v in audit_history(frames,set())))
    def test_detect_edge_swap(self):
        frames=[[('a',(0,0)),('b',(1,0))],[('a',(1,0)),('b',(0,0))]]
        self.assertTrue(any(v[1]=='edge swap' for v in audit_history(frames,set())))
    def test_detect_obstacle(self):
        self.assertTrue(any(v[1]=='blocked cell occupancy' for v in audit_history([[('a',(0,0))]],{(0,0)})))
    def test_k_budget(self):
        got=_topk([1,0,1,0],[.8,.9,.7,.2],2)
        self.assertEqual(got['true_positives'],1)
        self.assertEqual(got['false_alarms'],1)
        self.assertEqual(got['missed'],1)
    def test_reject_insufficient_instances(self):
        with self.assertRaises(ValueError):evaluate({'records':[]})
if __name__=='__main__': unittest.main()
