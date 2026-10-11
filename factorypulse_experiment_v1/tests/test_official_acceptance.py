import unittest,sys,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'official_lab'),str(ROOT/'src')]
from graph_oracle import audit_graph_oracle
from experiment import traced_graph
from stress_audit import audit as stress_audit

class OfficialAcceptance(unittest.TestCase):
    def setUp(self):
        self.instance={'machines':2,'jobs':[[{0:2},{1:3}],[{0:4}]]}
        self.plan=[dict(job=0,op=0,machine=0,start=0,end=2),dict(job=0,op=1,machine=1,start=2,end=5),dict(job=1,op=0,machine=0,start=2,end=6)]
        self.material={'bom':{'0:0':{'X':1},'0:1':{'Y':1}}}
        self.qa={'defects':[]}
        self.graph=traced_graph(self.instance,self.plan,{},self.material,self.qa)
    def test_exact_edges_match_independent_oracle(self):
        self.assertEqual([],audit_graph_oracle(self.instance,self.plan,self.material,self.qa,self.graph))
    def test_missing_edge_detected(self):
        altered=copy.deepcopy(self.graph);altered['edges'].pop()
        self.assertTrue(audit_graph_oracle(self.instance,self.plan,self.material,self.qa,altered))
    def test_wrong_rule_detected(self):
        altered=copy.deepcopy(self.graph);altered['edges'][0]['rule']='unsupported'
        self.assertTrue(audit_graph_oracle(self.instance,self.plan,self.material,self.qa,altered))
    def test_wrong_bom_detected(self):
        altered=copy.deepcopy(self.graph);altered['edges'][2]['evidence']['quantity']=200
        self.assertTrue(audit_graph_oracle(self.instance,self.plan,self.material,self.qa,altered))
    def test_stress_audit_status_correct(self):
        case=dict(seed=42,scenario='all',primary={'status':'INFEASIBLE'},
                  relaxation_experiments={k:{'status':'OPTIMAL'} for k in ('remove_material_shortage','remove_qa_hold','remove_machine_failure','remove_all_three')},
                  relaxations_restoring_feasibility=['remove_material_shortage','remove_qa_hold','remove_machine_failure','remove_all_three'],
                  diagnosis='EXPERIMENTAL_RELAXATION_RESTORES_FEASIBILITY')
        self.assertEqual([],stress_audit([case]))
        case['primary']['status']='UNKNOWN'
        self.assertTrue(stress_audit([case]))
if __name__=='__main__':unittest.main()
