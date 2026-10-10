"""G4 Extended: paired, optimal-origin counterfactual, and capacity sensitivity.
Run from factorypulse_experiment_v1/. Raw results ALWAYS saved, even if cases fail.
Public FJSP with synthetic downtime; no DENSO factory data.
"""
import argparse,csv,hashlib,json,platform,statistics,sys,time,traceback
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
from fjsp import parse_fjsp,greedy,validate_schedule,makespan
from dynamic import cp_sat_full,disruption_state,generate_events,validate_after
from g4_static import cp_sat_no_event
from g4_baselines import minimal_repair
from g4_extended import validate_counterfactual,policy_change_counts,paired_metrics,independently_check_record
from g4_extended_static import solver_gap,classify_solver_status

FIELDS=['instance','origin','case_id','time','machine','duration','overlaps_original','status','C0_makespan','C1_makespan','C2_makespan','event_loss','response_gain','recovery_ratio','solver_status','solver_elapsed_s','solver_wall_s','solver_lower_bound','gap','validator_error_count','error']

def _arm(inst,origin,base,case_id,event,time_limit,seed):
    row={'origin':origin,'case_id':case_id,'event':event,'status':'ERROR','solver':{'status':'EXECUTION_ERROR'},'validator_errors':None}
    try:
        state=disruption_state(inst,base,event['time'],event['machine'],event['duration'])
        start=time.perf_counter();minimal=minimal_repair(state);t1=time.perf_counter()-start
        err1=validate_counterfactual(inst,base,event,minimal)
        row['C0_makespan']=makespan(base);row['C1_makespan']=makespan(minimal)
        row['C1']={'valid':err1==[],'validation_errors':err1,'elapsed_s':t1}
        if err1:raise AssertionError('C1 invalid '+str(err1))
        try:
            solver,optimized=cp_sat_full(state,time_limit=time_limit,seed=seed,workers=1)
        except Exception as ex:
            solver={'status':'EXECUTION_ERROR','error':type(ex).__name__+': '+str(ex)}
            optimized=None
        row['solver']=solver
        if optimized is None:
            row['status']='NO_SOLUTION';row['error']=solver.get('error') or solver.get('status')
            return row
        errors=validate_counterfactual(inst,base,event,optimized)
        row['validator_errors']=errors
        row['C2_makespan']=makespan(optimized)
        row['C2_changes']=policy_change_counts(base,optimized,state)
        row['metrics']=paired_metrics(row['C0_makespan'],row['C1_makespan'],row['C2_makespan'])
        row['gap']=solver_gap(solver.get('status'),solver.get('makespan'),solver.get('best_bound'))
        row['status']='COMPLETE' if not errors and classify_solver_status(solver)=='VALID_SOLUTION' else 'ERROR'
        if row['status']=='ERROR':row['error']='validator or solver-status mismatch'
    except Exception as ex:
        row['status']='ERROR';row['error']=type(ex).__name__+': '+str(ex)
    return row

def flatten(run,rec):
    ev=rec.get('event',{});metrics=rec.get('metrics',{});solver=rec.get('solver',{})
    return dict(instance=run['instance'],origin=rec.get('origin'),case_id=rec.get('case_id'),
        time=ev.get('time'),machine=ev.get('machine'),duration=ev.get('duration'),overlaps_original=ev.get('affects_plan'),
        status=rec.get('status'),C0_makespan=rec.get('C0_makespan'),C1_makespan=rec.get('C1_makespan'),
        C2_makespan=rec.get('C2_makespan'),event_loss=metrics.get('event_loss'),response_gain=metrics.get('response_gain'),
        recovery_ratio=metrics.get('recovery_ratio'),solver_status=solver.get('status'),solver_elapsed_s=solver.get('elapsed_s'),
        solver_wall_s=solver.get('solver_wall_s'),solver_lower_bound=solver.get('best_bound'),gap=rec.get('gap'),
        validator_error_count=len(rec['validator_errors']) if isinstance(rec.get('validator_errors'),list) else None,
        error=rec.get('error'))

def aggregate(rows):
    out={'total':len(rows),'statuses':dict(Counter(r['status'] for r in rows)),
         'solver_statuses':dict(Counter(r['solver_status'] for r in rows)),
         'overlapping_original':sum(bool(r['overlaps_original']) for r in rows),
         'complete':sum(r['status']=='COMPLETE' for r in rows),
         'event_loss_positive':sum(r['event_loss'] is not None and r['event_loss']>0 for r in rows),
         'response_gain_positive':sum(r['response_gain'] is not None and r['response_gain']>0 for r in rows),
         'response_gain_negative':sum(r['response_gain'] is not None and r['response_gain']<0 for r in rows)}
    for k in ('C0_makespan','C1_makespan','C2_makespan','event_loss','response_gain','solver_elapsed_s','gap'):
        vals=[r[k] for r in rows if isinstance(r[k],(int,float)) and not isinstance(r[k],bool)]
        out[k+'_median']=statistics.median(vals) if vals else None
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--data',required=True);p.add_argument('--out-prefix',required=True)
    p.add_argument('--time-limit',type=float,default=10);p.add_argument('--seed',type=int,default=11)
    p.add_argument('--case-limit',type=int,default=0);p.add_argument('--static-limit',type=float,default=10)
    args=p.parse_args()
    if args.time_limit<=0 or args.static_limit<=0 or args.case_limit<0:p.error('invalid limit')
    path=Path(args.data);inst=parse_fjsp(path);heur=greedy(inst)
    if validate_schedule(inst,heur):raise RuntimeError('C0H invalid')
    try: static,opt=cp_sat_no_event(inst,time_limit=args.static_limit,seed=args.seed,workers=1)
    except Exception as e:static={'status':'EXECUTION_ERROR','error':repr(e)};opt=None
    static_valid=opt is not None and static.get('validation_errors') == [] and validate_schedule(inst,opt)==[]
    # Predeclared scenario CLOCK based on heuristic origin; identical t,m,d across both arms.
    events=list(generate_events(inst,heur))
    if args.case_limit:events=events[:args.case_limit]
    run={'instance':path.name,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
         'instance_structure':{'jobs':len(inst['jobs']),'machines':inst['machines'],
                'operations':sum(len(j) for j in inst['jobs'])},
         'seed':args.seed,'time_limit_s':args.time_limit,'static_limit_s':args.static_limit,
         'python':platform.python_version(),'platform':platform.platform(),
         'protocol':'G4 Extended v1, events generated from heuristic t/m/d and applied unchanged to both origin schedules',
         'C0H':{'makespan':makespan(heur),'valid':True},'C0O':{'record':static,'valid':static_valid},
         'C0_global_gain':makespan(heur)-makespan(opt) if static_valid else None,
         'arms':[],'warnings':[]}
    if not static_valid:run['warnings'].append('Optimized-origin arm unavailable: static CP-SAT not validated; retained as failure, not silently dropped')
    elif static.get('status')!='OPTIMAL':run['warnings'].append('C0O FEASIBLE only: cannot describe optimum as proven')
    for idx,ev in enumerate(events):
        for origin,base in [('heuristic',heur),('optimized',opt)]:
            e={**ev}
            if base is None:
                run['arms'].append({'origin':origin,'case_id':idx,'event':e,'status':'NO_SOLUTION','solver':{'status':'UNKNOWN'},'error':'C0O missing/invalid','validator_errors':None})
                continue
            e['affects_plan']=any(s['machine']==e['machine'] and s['end']>e['time'] and s['start']<e['time']+e['duration'] for s in base)
            run['arms'].append(_arm(inst,origin,base,idx,e,args.time_limit,args.seed))
    bad=[dict(origin=r['origin'],case_id=r['case_id'],issues=independently_check_record(r)) for r in run['arms'] if independently_check_record(r)]
    run['consistency_errors']=bad
    prefix=Path(args.out_prefix);prefix.parent.mkdir(parents=True,exist_ok=True)
    rows=[flatten(run,r) for r in run['arms']]
    stats={'scope':'public FJSP synthetic downtime, not DENSO; heuristic vs optimal-origin is a sensitivity comparison, not causal field evidence',
           'instance':run['instance'],'source_sha256':run['source_sha256'],'seed':args.seed,
           'static_status':static.get('status'),'static_valid':static_valid,
           'global_gain':run['C0_global_gain'],
           'heuristic_origin':aggregate([r for r in rows if r['origin']=='heuristic']),
           'optimized_origin':aggregate([r for r in rows if r['origin']=='optimized']),
           'consistency_errors':bad}
    Path(str(prefix)+'.json').write_text(json.dumps(run,indent=2,ensure_ascii=False),encoding='utf-8')
    with Path(str(prefix)+'.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
    Path(str(prefix)+'_summary.json').write_text(json.dumps(stats,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(stats,indent=2,ensure_ascii=False))
    # don't fail on solver unknown: scientifically valid outcome; fail on processing corruption
    if bad:raise SystemExit('integrity failure; inspect raw results')
if __name__=='__main__':main()
