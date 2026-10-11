"""Offline validation using the existing independently implemented official audit.

Validation extends to exact scenario coverage and comparative classification.
"""
import argparse,csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'src'),str(Path(__file__).resolve().parent)]
from audit import audit
from expanded_matrix import SCHEMA,SEEDS,KINDS,summarize
from experiment import digest,GOOD

def check(out,paths):
    out=Path(out);doc=json.loads((out/'results.json').read_text(encoding='utf8'))
    errs=[]
    if doc.get('schema')!=SCHEMA:errs.append('schema mismatch')
    inst_names={Path(p).stem for p in paths}
    if set(doc['manifest']['seeds'])!=set(SEEDS) or set(doc['manifest']['scenario_types'])!=set(KINDS):errs.append('unexpected design')
    for p in paths:
        from hashlib import sha256
        if doc['manifest']['files'].get(Path(p).name)!=sha256(Path(p).read_bytes()).hexdigest():errs.append('source hash changed '+p)
    # Official auditor checks every arm's schedule, graph, KPI and backfire flag.
    proxy={'records':doc['records'],'summary':{'evaluated':len(doc['records']),
         'counterexamples':sum(r['counterexample'] for r in doc['records'])}}
    errs+=audit(proxy,paths)
    expected={(n,s,k,f) for n in inst_names for s in SEEDS for k in KINDS for f in (0,9)} if False else None
    from fjsp import parse_fjsp
    expected={(Path(p).stem,s,k,f) for p in paths for s in SEEDS for k in KINDS for f in {0,len(parse_fjsp(p)['jobs'])-1}}
    actual=[(r['instance'],r['input']['seed'],r['input']['kind'],r['input']['focus']) for r in doc['records']]
    if len(actual)!=len(set(actual)) or set(actual)!=expected:errs.append('coverage mismatch / duplicate')
    rows,summary=summarize(doc['records'])
    if summary!=doc['summary']['by_instance']:errs.append('summary mismatch')
    with (out/'paired_comparisons.csv').open(encoding='utf8',newline='') as f:csvrows=list(csv.DictReader(f))
    if len(rows)!=len(csvrows):errs.append('CSV row count mismatch')
    for i,(a,b) in enumerate(zip(rows,csvrows)):
        for key,val in a.items():
            if str(val if val is not None else '')!=b[key]:errs.append(f'CSV mismatch row {i} column {key}')
    return errs
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--out',required=True);a.add_argument('--data',nargs='+',required=True);p=a.parse_args()
    errs=check(p.out,p.data)
    print('EXPANDED_AUDIT_PASS 0 errors' if not errs else f'EXPANDED_AUDIT_FAIL {len(errs)} errors')
    for e in errs[:25]:print('ERROR',e)
    sys.exit(bool(errs))
