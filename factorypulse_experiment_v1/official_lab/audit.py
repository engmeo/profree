"""P0/P1/P2 offline evidence audit independent of optimizer itself."""
import json,argparse,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from experiment import digest,traced_graph,check_graph,job_finishes,kpi
from fjsp import parse_fjsp,greedy
from run_response_matrix import scenario
from response_v2 import audit_shared,scenario_state
from graph_oracle import audit_graph_oracle
from fjsp import validate_schedule

def audit(doc,data):
    errors=[]
    parsed={Path(p).stem:parse_fjsp(p) for p in data}
    for i,r in enumerate(doc['records']):
        instance=parsed.get(r['instance'])
        if not instance:errors.append(f'{i} missing instance');continue
        inp=r['input']
        if digest(inp)!=r['input_sha256']:errors.append(f'{i} bad input hash')
        base=inp['base'];event=inp['event']
        original_errors=validate_schedule(instance,base)
        if original_errors:errors.append(f'{i} invalid original schedule {original_errors}')
        st=scenario_state(instance,base,event['time'],event['machine'],event['duration'],event['has_failure'])
        for method,arm in r['arms'].items():
            info=arm['info'];plan=arm['schedule']
            if info['status'] in ('OPTIMAL','FEASIBLE'):
                if plan is None:errors.append(f'{i} {method} no schedule');continue
                violations=audit_shared(st,base,plan,inp['material'],inp['qa'])
                if violations:errors.append(f'{i} {method} invalid {violations}')
                fresh=kpi(plan,inp['due'],inp['priority'],inp['focus'])
                if json.loads(json.dumps(fresh)) != arm['kpi']:errors.append(f'{i} {method} KPI mismatch')
                fresh_g=traced_graph(instance,plan,st,inp['material'],inp['qa'])
                if fresh_g!=arm['graph'] or check_graph(fresh_g):errors.append(f'{i} {method} graph invalid')
                for violation in audit_graph_oracle(instance,plan,inp['material'],inp['qa'],arm['graph']):
                    errors.append(f'{i} {method} P1 oracle {violation}')
            elif plan is not None:errors.append(f'{i} {method} unexpected plan')
        loc=r['arms']['LOCAL']['kpi'];c2=r['arms']['C2']['kpi']
        expected=bool(loc and c2 and loc['focus_completion']<c2['focus_completion'] and loc['weighted_tardiness']>c2['weighted_tardiness'])
        if r['counterexample']!=expected:errors.append(f'{i} forged counterexample flag')
    if any(r.get('counterexample') and (r['arms']['LOCAL']['info']['status'] not in ('OPTIMAL','FEASIBLE') or r['arms']['C2']['info']['status'] not in ('OPTIMAL','FEASIBLE')) for r in doc['records']):
        errors.append('counterexample without two feasible valid schedules')
    if len(doc['records'])!=doc['summary']['evaluated']:errors.append('count mismatch')
    if sum(r['counterexample'] for r in doc['records'])!=doc['summary']['counterexamples']:errors.append('counterexample count mismatch')
    return errors
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--json',required=True);p.add_argument('--data',nargs='+',required=True);a=p.parse_args()
    errors=audit(json.loads(Path(a.json).read_text('utf8')),a.data)
    print('OFFICIAL_AUDIT_PASS' if not errors else 'OFFICIAL_AUDIT_FAIL',len(errors),'errors')
    for e in errors[:20]:print('ERROR:',e)
    sys.exit(bool(errors))
