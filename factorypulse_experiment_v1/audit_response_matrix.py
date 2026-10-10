"""Replay schedules, inputs and CSV/manifest without invoking the optimizer."""
import argparse,csv,hashlib,json,sys
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'src'))
from fjsp import parse_fjsp,validate_schedule,makespan
from response_v2 import scenario_state,audit_shared,schedule_changes
from run_response_matrix import SCHEMA,MODES,SEEDS,SCENARIOS,WEIGHTS,canonical,sha

def audit(folder,data_paths,require_full=True):
    folder=Path(folder);err=[];raw=(folder/'response_matrix.json').read_bytes();doc=json.loads(raw)
    manifest=json.loads((folder/'manifest.json').read_text(encoding='utf8'))
    if doc.get('schema')!=SCHEMA or manifest.get('schema')!=SCHEMA:err.append('schema mismatch')
    if manifest.get('output_json_sha256')!=sha(raw):err.append('JSON digest mismatch')
    if manifest.get('output_csv_sha256')!=sha((folder/'response_matrix.csv').read_bytes()):err.append('CSV digest mismatch')
    files={Path(p).stem:Path(p) for p in data_paths};instances={}
    for name,p in files.items():
        if name not in manifest['instances'] or sha(p.read_bytes())!=manifest['instances'][name]['sha256']:
            err.append(f'instance {name}: checksum mismatch');continue
        instances[name]=parse_fjsp(p)
    seeds=manifest['seeds'];scenarios=manifest['scenario_types'];methods=manifest['methods']
    if methods!=list(MODES) or manifest['weights']!={k:list(v) for k,v in WEIGHTS.items()}:err.append('frozen methods/weights mismatch')
    if require_full and (seeds!=list(SEEDS) or scenarios!=list(SCENARIOS) or set(files)!={'mk01','mk02','mk03'}):err.append('incomplete registered matrix')
    expected={(name,seed,kind) for name in files for seed in seeds for kind in scenarios}
    observed=set();rows=[];status_counts={mode:Counter() for mode in methods}
    for rec in doc.get('records',[]):
        inp=rec['input'];key=(inp['instance'],inp['seed'],inp['scenario']);tag=f'{key}'
        if key in observed:err.append(f'{tag}: duplicated case')
        observed.add(key)
        if sha(canonical(inp))!=rec['input_sha256']:err.append(f'{tag}: input hash mismatch')
        inst=instances.get(inp['instance']);base=inp['origin_schedule']
        if inst is None:err.append(f'{tag}: missing verified instance');continue
        base_errors=validate_schedule(inst,base)
        if base_errors:err.append(f'{tag}: invalid initial schedule {base_errors}');continue
        ev=inp['event']
        state=scenario_state(inst,base,ev['time'],ev['machine'],ev['duration'],ev['has_failure'])
        if set(rec.get('arms',{}))!=set(methods):err.append(f'{tag}: methods incomplete')
        for mode in methods:
            arm=rec.get('arms',{}).get(mode)
            if arm is None:continue
            info=arm['info'];status=info['status'];plan=arm.get('schedule');status_counts[mode][status]+=1
            if status in ('OPTIMAL','FEASIBLE'):
                if plan is None:err.append(f'{tag} {mode}: no plan for successful status')
            elif plan is not None:err.append(f'{tag} {mode}: non-solution with plan')
            if plan is not None:
                checks=audit_shared(state,base,plan,inp['material'],inp['qa'])
                err.extend(f'{tag} {mode}: {x}' for x in checks)
                if makespan(plan)!=info.get('makespan'):err.append(f'{tag} {mode}: makespan mismatch')
                if schedule_changes(base,plan)!=info.get('changes'):err.append(f'{tag} {mode}: change metric mismatch')
            changes=info.get('changes') or {}
            rows.append({'instance':inp['instance'],'seed':str(inp['seed']),'scenario':inp['scenario'],
                'input_sha256':rec['input_sha256'],'method':mode,'status':status,
                'makespan':str(info.get('makespan') if info.get('makespan') is not None else ''),
                'reassigned':str(changes.get('reassigned') if changes.get('reassigned') is not None else ''),
                'start_shift':str(changes.get('start_shift') if changes.get('start_shift') is not None else ''),
                'order_inversions':str(changes.get('machine_order_inversions') if changes.get('machine_order_inversions') is not None else ''),
                'wall_s':str(info.get('wall_s') if info.get('wall_s') is not None else ''),
                'elapsed_s':str(info.get('elapsed_s') if info.get('elapsed_s') is not None else ''),
                'error':arm['error'] or ''})
    if observed!=expected:err.append(f'coverage mismatch missing={sorted(expected-observed)[:8]} extra={sorted(observed-expected)[:8]}')
    with (folder/'response_matrix.csv').open(encoding='utf8',newline='') as f:actual=list(csv.DictReader(f))
    if rows!=actual:err.append('CSV rows differ from independently reconstructed JSON')
    summary=json.loads((folder/'summary.json').read_text(encoding='utf8'))
    if summary['actual_cases']!=len(doc['records']) or summary['actual_arms']!=len(rows):err.append('summary counts mismatch')
    for mode,counts in status_counts.items():
        if summary['status_counts'].get(mode)!={k:v for k,v in counts.items()}:err.append(f'{mode}: summary statuses mismatch')
    return err

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dir',default='results/response_matrix');p.add_argument('--data',nargs='+',default=['data/mk01.txt','data/mk02.txt','data/mk03.txt']);p.add_argument('--allow-subset',action='store_true')
    a=p.parse_args();errors=audit(a.dir,a.data,not a.allow_subset)
    if errors:
        print('\n'.join('FAIL '+s for s in errors));raise SystemExit(1)
    print('INDEPENDENT RESPONSE MATRIX AUDIT PASS',a.dir)
