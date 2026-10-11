"""P2 independent artifact audit; does not re-run solver, never labels UNKNOWN infeasible."""
import argparse,json,sys
from pathlib import Path
STATES={'OPTIMAL','FEASIBLE','INFEASIBLE','UNKNOWN','MODEL_INVALID','ERROR'}
GOOD={'OPTIMAL','FEASIBLE'}
EXPECTED={'remove_material_shortage','remove_qa_hold','remove_machine_failure','remove_all_three'}

def audit(rows):
    issues=[];keys=set()
    for idx,r in enumerate(rows):
        key=(r.get('seed'),r.get('scenario'))
        if key in keys:issues.append(f'{idx}: duplicate case')
        keys.add(key)
        primary=r['primary'];status=primary['status']
        if status not in STATES:issues.append(f'{idx}: unknown status {status}')
        alts=r.get('relaxation_experiments',{})
        if set(alts)!=EXPECTED:issues.append(f'{idx}: missing/extra relaxation')
        for name,res in alts.items():
            if res['status'] not in STATES:issues.append(f'{idx}: bad relaxed status {name}')
        proven=sorted(k for k,v in alts.items() if status=='INFEASIBLE' and v['status'] in GOOD)
        if proven!=sorted(r.get('relaxations_restoring_feasibility',[])):
            issues.append(f'{idx}: mismatch proven restoring relaxations')
        diagnosis=('EXPERIMENTAL_RELAXATION_RESTORES_FEASIBILITY' if proven else
                   'UNDETERMINED' if status=='INFEASIBLE' else 'NO_INFEASIBILITY_TO_EXPLAIN')
        if r.get('diagnosis')!=diagnosis:issues.append(f'{idx}: unsupported diagnosis')
        if status=='UNKNOWN' and proven:issues.append(f'{idx}: UNKNOWN incorrectly claimed infeasible')
    return issues
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--json',required=True);a=p.parse_args()
    rows=json.loads(Path(a.json).read_text('utf8'));errors=audit(rows)
    print('STRESS_AUDIT_'+('FAIL' if errors else 'PASS'),len(rows),'cases',len(errors),'errors')
    for e in errors:print('ERROR',e)
    sys.exit(bool(errors))
