import unittest,sys,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from fjsp import parse_fjsp,validate_schedule,greedy
P=Path(__file__).resolve().parents[1]/'data/mk01.txt'
class TestValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.i=parse_fjsp(P);cls.s=greedy(cls.i)
    def test_valid(self):self.assertEqual(validate_schedule(self.i,self.s),[])
    def test_missing(self):self.assertTrue(validate_schedule(self.i,self.s[:-1]))
    def test_duplicate(self):self.assertTrue(validate_schedule(self.i,self.s+[self.s[0]]))
    def test_invalid_machine(self):
        a=copy.deepcopy(self.s);a[0]['machine']=99
        self.assertTrue(any('ineligible' in x for x in validate_schedule(self.i,a)))
    def test_invalid_duration(self):
        a=copy.deepcopy(self.s);a[0]['end']+=1
        self.assertTrue(any('duration' in x for x in validate_schedule(self.i,a)))
    def test_negative_start(self):
        a=copy.deepcopy(self.s);a[0]['start']=-1
        self.assertTrue(any('duration/start' in x for x in validate_schedule(self.i,a)))
    def test_overlap(self):
        a=copy.deepcopy(self.s);a[1]['machine']=a[0]['machine'];a[1]['start']=a[0]['start'];a[1]['end']=a[1]['start']+self.i['jobs'][a[1]['job']][a[1]['op']].get(a[1]['machine'],1)
        self.assertTrue(validate_schedule(self.i,a))
    def test_precedence(self):
        a=copy.deepcopy(self.s); k=next(k for k,v in enumerate(a) if v['job']==0 and v['op']==1)
        a[k]['start']=0;a[k]['end']=self.i['jobs'][0][1][a[k]['machine']]
        self.assertTrue(any('precedence' in x for x in validate_schedule(self.i,a)))
    def test_downtime(self):
        s=self.s[0]; self.assertTrue(any('downtime' in x for x in validate_schedule(self.i,self.s,[(s['machine'],s['start'],s['end'])])))
    def test_frozen(self):
        a=copy.deepcopy(self.s);fixed={(a[0]['job'],a[0]['op']):dict(a[0])};a[0]['start']+=1
        self.assertTrue(any('frozen' in x for x in validate_schedule(self.i,a,fixed=fixed)))
    def test_greedy_downtime(self):
        s=greedy(self.i,[(0,0,15)])
        self.assertEqual(validate_schedule(self.i,s,[(0,0,15)]),[])
if __name__=='__main__':unittest.main()
