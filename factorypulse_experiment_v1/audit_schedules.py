"""Independent replay validator for FULL G4 Extended schedule artifacts.
No solver dependency. Fails closed on absent plans; does not trust stored flags.
"""
import argparse, hashlib, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from src.fjsp import parse_fjsp,validate_schedule,makespan
from src.dynamic import disruption_state,validate_after
from src.g4_extended import policy_change_counts,paired_metrics


def audit(raw_path, instance_path):
    run=json.loads(Path(raw_path).read_text(encoding='utf-8'))
    raw_bytes=Path(instance_path).read_bytes()
    errors=[]
    if hashlib.sha256(raw_bytes).hexdigest()!=run.get('source_sha256'):
        errors.append('input SHA-256 mismatch; refusing replay')
        return errors
    inst=parse_fjsp(instance_path)
    for idx,rec in enumerate(run['arms']):
        label=f"{run['instance']} {rec.get('origin')} #{rec.get('case_id')}"
        base=rec.get('C0_schedule')
        if base is None:
            if rec.get('status')!='NO_SOLUTION':errors.append(f'{label}: missing C0 schedule')
            continue
        base_errors=validate_schedule(inst,base)
        if base_errors:errors.append(f'{label}: invalid C0: {base_errors}');continue
        event=rec.get('event') or {}
        try:state=disruption_state(inst,base,event['time'],event['machine'],event['duration'])
        except (KeyError,ValueError,TypeError) as ex:
            errors.append(f'{label}: invalid event: {ex}');continue
        if rec.get('C0_makespan') is not None and makespan(base)!=rec['C0_makespan']:
            errors.append(f'{label}: C0 makespan mismatch')
        c1=rec.get('C1_schedule')
        if c1 is None:
            errors.append(f'{label}: missing C1 schedule (cannot independently audit)');continue
        errs=validate_after(state,c1)
        if errs:errors.append(f'{label}: C1 violations: {errs}')
        if rec.get('C1_makespan')!=makespan(c1):errors.append(f'{label}: C1 makespan mismatch')
        # C1 policy requirement: preserved machines and baseline machine order,
        # with no planned future work shifted earlier than baseline.
        lookup={(r['job'],r['op']):r for r in c1}
        for prior in base:
            key=(prior['job'],prior['op']);actual=lookup.get(key)
            if actual is None:continue
            if actual['machine']!=prior['machine']:
                errors.append(f'{label}: C1 reassigned operation {key}')
            if actual['start']<prior['start']:
                errors.append(f'{label}: C1 moved operation earlier {key}')
        by_machine={}
        for x in base:by_machine.setdefault(x['machine'],[]).append(x)
        for machine,rs in by_machine.items():
            rs.sort(key=lambda r:(r['start'],r['end'],r['job'],r['op']))
            for prev,nxt in zip(rs,rs[1:]):
                a=lookup.get((prev['job'],prev['op']));b=lookup.get((nxt['job'],nxt['op']))
                if a and b and b['start']<a['end']:
                    errors.append(f'{label}: C1 machine-order inversion machine {machine}')
        c2=rec.get('C2_schedule')
        if rec.get('status')=='COMPLETE':
            if c2 is None:errors.append(f'{label}: missing C2 schedule');continue
            errs2=validate_after(state,c2)
            if errs2:errors.append(f'{label}: C2 violations: {errs2}')
            if makespan(c2)!=rec.get('C2_makespan'):
                errors.append(f'{label}: C2 makespan mismatch')
            if rec.get('solver',{}).get('status') not in ('OPTIMAL','FEASIBLE'):
                errors.append(f'{label}: complete with non-solution solver status')
            changes=policy_change_counts(base,c2,state)
            if changes!=rec.get('C2_changes'):errors.append(f'{label}: C2 change metrics mismatch')
            metrics=paired_metrics(makespan(base),makespan(c1),makespan(c2))
            if metrics!=rec.get('metrics'):errors.append(f'{label}: G4 metrics mismatch')
        elif c2 is not None:
            errs2=validate_after(state,c2)
            if errs2:errors.append(f'{label}: invalid C2 schedule in failed case: {errs2}')
    return errors

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--raw',required=True);p.add_argument('--data',required=True)
    a=p.parse_args();errors=audit(a.raw,a.data)
    if errors:
        for e in errors:print('FAIL:',e)
        raise SystemExit(1)
    print('INDEPENDENT SCHEDULE AUDIT OK:',a.raw)
