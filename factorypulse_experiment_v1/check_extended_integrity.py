"""Independent cross-check raw records vs CSV and summary, no dependency on solver."""
import argparse,csv,json,math
from pathlib import Path
from collections import Counter

def verify(prefix):
 prefix=Path(prefix)
 raw=json.loads(Path(str(prefix)+'.json').read_text(encoding='utf-8'))
 summ=json.loads(Path(str(prefix)+'_summary.json').read_text(encoding='utf-8'))
 with Path(str(prefix)+'.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
 arms=raw['arms'];errs=[]
 if len(rows)!=len(arms):errs.append('row count disagrees')
 for i,(rec,cr) in enumerate(zip(arms,rows)):
  if str(rec['case_id'])!=cr['case_id'] or rec['origin']!=cr['origin'] or rec['status']!=cr['status']:
   errs.append(f'row identity mismatch {i}')
  if rec['status']=='COMPLETE':
   if rec.get('validator_errors')!=[]:errs.append(f'validator invalid {i}')
   metrics=rec['metrics']
   for key in ('event_loss','response_gain'):
    if not math.isclose(float(cr[key]),float(metrics[key]),abs_tol=1e-8):errs.append(f'metric mismatch {key}:{i}')
   if metrics['event_loss']<=0 and cr['recovery_ratio']!='':errs.append(f'ratio should be null:{i}')
 for origin,label in [('heuristic','heuristic_origin'),('optimized','optimized_origin')]:
  cur=[r for r in arms if r['origin']==origin]
  expected=Counter(r['status'] for r in cur)
  if dict(expected)!=summ[label]['statuses']:errs.append(f'status summary mismatch {origin}')
  if len(cur)!=summ[label]['total']:errs.append(f'total mismatch {origin}')
 if raw['source_sha256']!=summ['source_sha256']:errs.append('input hash mismatch')
 return errs
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);a=p.parse_args()
 errors=verify(a.prefix)
 if errors:raise SystemExit('INTEGRITY FAILED: '+str(errors))
 print('INTEGRITY OK',a.prefix)
