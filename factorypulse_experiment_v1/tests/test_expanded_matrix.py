"""No solver required: prove reporting doesn't hide negative/unsolved cases."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'official_lab'))
from expanded_matrix import summarize

def arm(f,t,status='OPTIMAL'):
    return {'info':{'status':status},'kpi':{'focus_completion':f,'weighted_tardiness':t} if status=='OPTIMAL' else None}
def rec(local,c2,instance='mk01'):
    return {'instance':instance,'input':{'seed':42,'kind':'machine','focus':0},'input_sha256':'x','arms':{'LOCAL':local,'C2':c2,'C1':arm(0,0),'B3-B':arm(0,0)}}
class Accounting(unittest.TestCase):
    def test_win_loss_and_nonpaired_preserved(self):
        inp=[rec(arm(5,18),arm(8,11)),rec(arm(5,3),arm(8,11)),rec(arm(9,11),arm(8,11)),rec(arm(None,None,'INFEASIBLE'),arm(8,11))]
        rows,s=summarize(inp)
        self.assertEqual([r['classification'] for r in rows],['BACKFIRE','LOCAL_FOCUS_GAIN_WITHOUT_GLOBAL_HARM','NO_LOCAL_FOCUS_GAIN','EXCLUDED_NONPAIRED'])
        self.assertEqual(s['mk01']['total'],4)
        self.assertEqual(s['mk01']['paired_valid'],3)
        self.assertEqual(s['mk01']['excluded_nonpaired'],1)
if __name__=='__main__':unittest.main()
