import unittest, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ai_swarm.fleet_safety_lab import Agent, step, simulate, demonstration

class GridInvariants(unittest.TestCase):
 def test_no_same_cell_20_robots(self):
  agents=[Agent(str(i),(i%10,i//10),(i%10,6+i//10)) for i in range(20)]
  r=simulate(agents,ticks=80)
  for snapshot in r['history']:
   p=[q for _,q in snapshot];self.assertEqual(len(p),len(set(p)))
 def test_head_on_swap_prevented(self):
  robots=[Agent('a',(0,0),(1,0)),Agent('b',(1,0),(0,0))]
  next_,_=step(robots,width=2,height=1)
  self.assertEqual([a.pos for a in next_],[(0,0),(1,0)])
  self.assertEqual(simulate(robots,ticks=2)['status'],'STALLED_REQUIRES_REPLAN')
 def test_failure_never_moves(self):
  a=Agent('broken',(1,1),(8,7),healthy=False)
  r=simulate([a,Agent('ok',(2,1),(3,1))],ticks=10)
  self.assertTrue(all(dict(s)['broken']==(1,1) for s in r['history']))
 def test_blocked_cell_not_entered(self):
  a=[Agent('one',(0,0),(3,0))]
  r=simulate(a,ticks=5,blocked={(1,0)})
  self.assertTrue(all(dict(s)['one']!=(1,0) for s in r['history']))
 def test_20_agent_demo(self):
  r=demonstration();self.assertEqual(r['robots'],20)
  self.assertIn(r['status'],('FINISHED','STALLED_REQUIRES_REPLAN','TIME_LIMIT'))
 def test_invalid_start_rejected(self):
  with self.assertRaises(ValueError):step([Agent('a',(1,1),(2,2)),Agent('b',(1,1),(3,3))])
if __name__=='__main__':unittest.main()
