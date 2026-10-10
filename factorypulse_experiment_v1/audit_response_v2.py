"""Independent replay from emitted JSON, no solver dependency."""
import argparse,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'src'))
from fjsp import parse_fjsp,makespan
from response_v2 import scenario_state
from response_v2 import audit_shared,schedule_changes

def audit(path,data):
    raw=json.loads(Path(path).read_text(encoding='utf8'))
    if hashlib.sha256(Path(data).read_bytes()).hexdigest()!=raw.get('source_sha256'):
        return ['input source checksum mismatch']
    instance=parse_fjsp(data);errors=[]
    if len(raw['cases'])!=7:errors.append('wrong number of scenarios')
    for case in raw['cases']:
        event=case['event'];state=scenario_state(instance,case['origin_schedule'],event['time'],event['machine'],event['duration'],has_failure=event['has_failure'])
        for mode in ('C1','C2','B3'):
            result=case['methods'].get(mode)
            if result is None:errors.append(f"case {case['id']}: missing {mode}");continue
            schedule=result['schedule'];info=result['info']
            if schedule is None:
                if info['status'] in ('OPTIMAL','FEASIBLE'):errors.append(f"case {case['id']} {mode}: claimed solved without schedule")
                continue
            errs=audit_shared(state,case['origin_schedule'],schedule,case['material'],case['qa'])
            errors.extend(f"case {case['id']} {mode}: {e}" for e in errs)
            if makespan(schedule)!=info.get('makespan'):errors.append(f"case {case['id']} {mode}: makespan mismatch")
            if schedule_changes(case['origin_schedule'],schedule)!=info.get('changes'):
                errors.append(f"case {case['id']} {mode}: changes mismatch")
    return errors
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--raw',required=True);p.add_argument('--data',required=True);args=p.parse_args()
    errs=audit(args.raw,args.data)
    if errs:
        print('\n'.join('FAIL '+e for e in errs));sys.exit(1)
    print('INDEPENDENT SHARED-STATE AUDIT PASS',args.raw)
