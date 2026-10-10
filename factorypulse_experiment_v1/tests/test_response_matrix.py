import json,tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from run_response_matrix import SEEDS,SCENARIOS,MODES,WEIGHTS,canonical,sha,scenario
from diagnose_infeasible_matrix import diagnose
from src.fjsp import parse_fjsp,greedy

ROOT=Path(__file__).resolve().parents[1]
class MatrixTests(unittest.TestCase):
    def test_protocol_frozen(self):
        self.assertEqual(len(SEEDS),5);self.assertEqual(len(SCENARIOS),7)
        self.assertEqual(len(MODES),5);self.assertEqual(len(WEIGHTS),3)
    def test_seed_reproducible(self):
        inst=parse_fjsp(ROOT/'data/mk01.txt');base=greedy(inst)
        for kind in SCENARIOS:
            a=scenario(inst,base,42,kind);b=scenario(inst,base,42,kind)
            self.assertEqual(sha(canonical(a[1:])),sha(canonical(b[1:])))
    def test_seed_changes_some_events(self):
        inst=parse_fjsp(ROOT/'data/mk01.txt');base=greedy(inst)
        x=scenario(inst,base,42,'machine')[1]
        y=scenario(inst,base,123,'machine')[1]
        self.assertNotEqual(x,y)
    def test_no_change_original(self):
        inst=parse_fjsp(ROOT/'data/mk01.txt');base=greedy(inst)
        before=sha(canonical(inst))
        scenario(inst,base,2026,'all')
        self.assertEqual(before,sha(canonical(inst)))
    def test_deficit_diagnosis(self):
        r={'input':{'instance':'mk01','seed':42,'scenario':'material','material':{'initial':{'A':0},'deliveries':[], 'bom':{'0:0':{'A':2}}},'qa':{'defects':[]},'event':{}},'input_sha256':'test', 'arms':{'C1':{'info':{'status':'INFEASIBLE','elapsed_s':.1}}}}
        self.assertEqual(diagnose(r,'C1')['total_inventory_deficit'],{'A':2})
if __name__=='__main__':unittest.main()
