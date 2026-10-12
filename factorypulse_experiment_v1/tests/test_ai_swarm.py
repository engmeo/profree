import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ai_swarm.fleet import Robot,Delivery,shortest_path,assign,scenario
from ai_swarm.risk import features,label_of

class FleetTests(unittest.TestCase):
 def test_path_avoids_blocked(self):
  p=shortest_path((0,0),(3,0),{(1,0)})
  self.assertNotIn((1,0),p)
  self.assertEqual(p[-1],(3,0))
 def test_capability_and_fault(self):
  robots=[Robot('bad','AMR',frozenset({'parts'}),20,99,(0,0),False),Robot('weak','AMR',frozenset({'parts'}),5,99,(1,1)),Robot('good','tug',frozenset({'parts','heavy'}),200,90,(2,2))]
  task=Delivery('t','MAT',30,'heavy',(2,3),(4,3),12)
  self.assertEqual(assign(robots,task)['robot'],'good')
 def test_fault_propagates_eta(self):
  s=scenario()
  self.assertEqual(s['robot_count'],20)
  self.assertEqual(s['recovery']['status'],'ASSIGNED')
  self.assertEqual(s['material_gate']['earliest_production_start'],s['recovery']['eta'])
 def test_blocked(self):
  r=Robot('one','AMR',frozenset({'parts'}),20,100,(1,1))
  t=Delivery('t','MAT',10,'heavy',(1,2),(3,3),5)
  self.assertEqual(assign([r],t)['status'],'BLOCKED_NO_ELIGIBLE_ROBOT')

class RiskTests(unittest.TestCase):
 def test_unpaired_is_not_negative(self):
  self.assertIsNone(label_of({'arms':{'LOCAL':{'info':{'status':'INFEASIBLE'}},'C2':{'info':{'status':'OPTIMAL'}}}}))
 def test_label_predeclared(self):
  r={'arms':{'LOCAL':{'info':{'status':'OPTIMAL'},'kpi':{'focus_completion':10,'weighted_tardiness':20}},'C2':{'info':{'status':'OPTIMAL'},'kpi':{'focus_completion':13,'weighted_tardiness':14}}}}
  self.assertEqual(label_of(r),1)
 def test_output_arm_mutation_cannot_change_features(self):
  b=[{'job':0,'start':0,'end':5,'machine':0}]
  r={'input':{'base':b,'focus':0,'event':{'time':2,'duration':3,'has_failure':True},'due':{'0':8},'priority':{'0':1},'material':{'initial':{},'deliveries':[]},'qa':{'defects':[]}},'arms':{'LOCAL':{'kpi':{'weighted_tardiness':1}}}}
  before=features(r);r['arms']['LOCAL']['kpi']['weighted_tardiness']=9999
  self.assertEqual(before,features(r))
if __name__=='__main__':unittest.main()

class BridgeTests(unittest.TestCase):
 def test_material_inbound_gate(self):
  from ai_swarm.bridge import apply_fleet_arrival
  fleet=scenario();raw={'initial':{'MAT_A':0},'deliveries':[],'bom':{'0:0':{'MAT_A':2}}}
  out=apply_fleet_arrival(raw,fleet)
  self.assertEqual(out['deliveries'][0]['time'],fleet['recovery']['eta'])
  self.assertEqual(out['deliveries'][0]['quantity'],2)
  self.assertEqual(raw['deliveries'],[])
 def test_uncontrolled_existing_supply_is_rejected(self):
  from ai_swarm.bridge import apply_fleet_arrival
  raw={'initial':{'MAT_A':5},'deliveries':[],'bom':{'0:0':{'MAT_A':2}}}
  with self.assertRaises(ValueError):apply_fleet_arrival(raw,scenario())
