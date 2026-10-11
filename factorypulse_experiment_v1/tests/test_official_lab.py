import unittest,sys,tempfile,json,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'official_lab'),str(ROOT),str(ROOT/'src')]
from patch_official_solver import patch
from experiment import kpi,traced_graph,check_graph,reachable_bfs,reachable_reference,digest
class OfficialTests(unittest.TestCase):
    def test_patch_idempotent(self):
        from pathlib import Path
        actual=(ROOT/'src'/'response_v2.py').read_text('utf-8')
        modified=patch(actual)
        self.assertEqual(patch(modified),modified)
        self.assertIn("mode=='LOCAL'",modified)
    def test_patch_refuses_unknown_version(self):
        with self.assertRaises(ValueError):patch('unrecognized')
    def test_kpi_local_backfire(self):
        local=[dict(job=0,op=0,machine=0,start=0,end=3),dict(job=1,op=0,machine=0,start=3,end=15)]
        global_=[dict(job=1,op=0,machine=0,start=0,end=10),dict(job=0,op=0,machine=0,start=10,end=15)]
        due={'0':12,'1':10};weights={'0':1,'1':8}
        a=kpi(local,due,weights,0);b=kpi(global_,due,weights,0)
        self.assertLess(a['focus_completion'],b['focus_completion'])
        self.assertGreater(a['weighted_tardiness'],b['weighted_tardiness'])
    def test_graph_evidence_and_reference(self):
        inst={'machines':1,'jobs':[[{0:2},{0:3}]]}
        plan=[dict(job=0,op=0,machine=0,start=0,end=2),dict(job=0,op=1,machine=0,start=2,end=5)]
        g=traced_graph(inst,plan,{}, {'bom':{'0:0':{'MAT_A':2}}},{'defects':[]})
        self.assertEqual(check_graph(g),[])
        self.assertEqual(reachable_bfs(g,'op:0:0'),reachable_reference(g,'op:0:0'))
    def test_graph_detects_tamper(self):
        inst={'machines':1,'jobs':[[{0:2}]]};p=[dict(job=0,op=0,machine=0,start=0,end=2)]
        g=traced_graph(inst,p,{}, {'bom':{}},{'defects':[]});g['edges'][0]['to']='missing'
        self.assertTrue(check_graph(g))
    def test_digest_stable_roundtrip(self):
        item={'due':{'0':12,'11':4},'base':[{'job':0,'op':1}]}
        self.assertEqual(digest(item),digest(json.loads(json.dumps(item))))
    def test_real_solver_if_installed(self):
        try:import ortools
        except ImportError:self.skipTest('OR-Tools not installed locally; GitHub CI installs it')
        import inspect
        from response_v2 import solve_shared
        self.assertIn('local_focus_job',inspect.signature(solve_shared).parameters)
if __name__=='__main__':unittest.main()
