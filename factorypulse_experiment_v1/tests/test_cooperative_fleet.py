import sys, unittest, random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ai_swarm.cooperative_fleet import plan
from ai_swarm.fleet_safety_lab import Agent
from ai_swarm.fleet_stress import audit_history

class CooperativeFleetTests(unittest.TestCase):
    def test_single_robot_detour(self):
        r=plan([Agent('a',(0,0),(2,0))],width=3,height=3,blocked={(1,0)})
        self.assertEqual(r['status'],'FINISHED');self.assertEqual(dict(r['history'][-1])['a'],(2,0))
        self.assertFalse(audit_history(r['history'],{(1,0)},3,3))
    def test_failed_robot_immobile(self):
        r=plan([Agent('broken',(1,1),(1,2),healthy=False),Agent('ok',(0,1),(2,1))],width=3,height=3)
        self.assertEqual(r['status'],'FINISHED')
        self.assertTrue(all(dict(h)['broken']==(1,1) for h in r['history']))
    def test_conflict_never_reported_as_success(self):
        robots=[Agent('a',(0,0),(1,0)),Agent('b',(1,0),(0,0))]
        r=plan(robots,width=2,height=1,horizon=8)
        self.assertEqual(r['status'],'UNSOLVED_REQUIRES_REPLAN')
    def test_independent_history_audit(self):
        rng=random.Random(42)
        for seed in range(20):
            cells=[(x,y) for x in range(8) for y in range(6)];rng.shuffle(cells)
            a=[Agent(str(i),cells[i],cells[12+i],healthy=(i!=0)) for i in range(10)]
            r=plan(a,width=8,height=6,horizon=90)
            if r['status']=='FINISHED':
                self.assertFalse(audit_history(r['history'],set(),8,6))
                self.assertEqual(r['completed_healthy'],r['healthy_count'])
if __name__=='__main__':unittest.main()
