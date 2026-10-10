import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from fjsp import parse_fjsp,greedy
from response_v2 import material_violations,qa_violations,build_material_spec,schedule_changes,scenario_state,audit_shared
class Tests(unittest.TestCase):
    def setUp(self):
        self.inst=parse_fjsp(ROOT/'data/mk01.txt');self.base=greedy(self.inst)
    def test_deterministic_bom(self):
        self.assertEqual(build_material_spec(self.inst,42,'shortage'),build_material_spec(self.inst,42,'shortage'))
    def test_inventory_negative_detected(self):
        spec={'initial':{'A':0},'deliveries':[],'bom':{'0:0':{'A':1}}}
        self.assertTrue(material_violations([dict(job=0,op=0,start=2)],spec))
    def test_delivery_at_same_time_is_available(self):
        spec={'initial':{'A':0},'deliveries':[{'material':'A','time':2,'quantity':1}],'bom':{'0:0':{'A':1}}}
        self.assertFalse(material_violations([dict(job=0,op=0,start=2)],spec))
    def test_qa_missing_rework(self):
        qa={'defects':[dict(job=0,machine=0,duration=4,hold_until=50)]}
        self.assertTrue(qa_violations(self.base,qa,self.inst))
    def test_no_machine_failure_keeps_running(self):
        state=scenario_state(self.inst,self.base,8,0,5,False)
        for k,st in state['states'].items():
            if st=='RUNNING_UNAFFECTED':self.assertIn(k,state['fixed'])
    def test_changes_zero_original(self):
        changes=schedule_changes(self.base,self.base)
        self.assertEqual(changes,dict(reassigned=0,start_shift=0,machine_order_inversions=0))
    def test_shared_baseline_valid_unconstrained(self):
        state=scenario_state(self.inst,self.base,1,0,5,False)
        self.assertEqual(audit_shared(state,self.base,self.base,build_material_spec(self.inst,17,'none'),{'defects':[]}),[])
    def test_solver_modes_if_ortools_present(self):
        try:import ortools
        except ImportError:self.skipTest('ortools unavailable locally')
        from response_v2 import solve_shared
        state=scenario_state(self.inst,self.base,3,0,5,False)
        mat=build_material_spec(self.inst,17,'none')
        for mode in ('C1','C2','B3'):
            info,result=solve_shared(state,self.base,material=mat,qa={'defects':[]},mode=mode,timeout=5)
            self.assertIsNotNone(result,info)
            self.assertEqual(audit_shared(state,self.base,result,mat,{'defects':[]}),[])
if __name__=='__main__':unittest.main()

class TestPublicLabels(unittest.TestCase):
    def test_one_hot_label_parser(self):
        from qa_public import parse_faults_nna
        self.assertEqual(parse_faults_nna(' '.join(['1']*27+['0','1','0','0','0','0','0'])),['Z_Scratch'])
    def test_bad_one_hot_rejected(self):
        from qa_public import parse_faults_nna
        with self.assertRaises(ValueError):parse_faults_nna(' '.join(['1']*34))
    def test_mapping_preserves_label_provenance(self):
        from qa_public import qa_from_labels
        inst=parse_fjsp(ROOT/'data/mk01.txt');base=greedy(inst)
        q=qa_from_labels(['Bumps'],inst,base,0,'ab'*32)
        self.assertEqual(q['defects'][0]['label'],'Bumps')
        self.assertEqual(q['defects'][0]['source'],'UCI_198_REAL_LABEL_SIMULATED_POLICY')
