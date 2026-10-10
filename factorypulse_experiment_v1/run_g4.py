"""G4 scenario paired study; research only. Uses the same base schedule for C0H, C1 and C2."""
import argparse,hashlib,json,platform,statistics,sys,time
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
from fjsp import parse_fjsp,greedy,validate_schedule,makespan
from dynamic import disruption_state,generate_events,cp_sat_full,validate_after
from g4_baselines import minimal_repair,g4_metrics
from g4_static import cp_sat_no_event

def main():
 p=argparse.ArgumentParser();p.add_argument('--data',default='data/mk01.txt');p.add_argument('--out',default='results/g4_36.json');p.add_argument('--time-limit',type=float,default=10);p.add_argument('--limit',type=int,default=0);args=p.parse_args()
 if args.time_limit<=0: p.error('--time-limit must be positive')
 data=Path(args.data);inst=parse_fjsp(data);c0h=greedy(inst)
 if validate_schedule(inst,c0h):raise RuntimeError('invalid C0H')
 c0o_rec,c0o=cp_sat_no_event(inst,time_limit=args.time_limit)
 if not c0o or c0o_rec['validation_errors']:raise RuntimeError('C0O missing or invalid: '+str(c0o_rec))
 rows=[]
 for i,ev in enumerate(generate_events(inst,c0h)):
  if args.limit and i>=args.limit:break
  state=disruption_state(inst,c0h,ev['time'],ev['machine'],ev['duration'])
  t=time.perf_counter();c1=minimal_repair(state);c1_elapsed=time.perf_counter()-t
  e1=validate_after(state,c1)
  if e1:raise RuntimeError(f'C1 invalid case {i}: {e1}')
  c2_rec,c2=cp_sat_full(state,time_limit=args.time_limit,seed=11,workers=1)
  valid_c2=c2 is not None and not validate_after(state,c2) and not c2_rec.get('validation_errors')
  metrics=g4_metrics(c0h,c0o,c1,c2) if valid_c2 else None
  rows.append({'case_id':i,'event':ev,'state_counts':dict(Counter(state['states'].values())),
    'C1':{'makespan':makespan(c1),'elapsed_s':c1_elapsed,'valid':True,'validation_errors':e1},
    'C2':{**c2_rec,'valid':valid_c2},'metrics':metrics,
    'changes':{'moved_machine':sum(1 for r in c2 if (r['job'],r['op']) not in state['fixed'] and r['machine'] != state['baseline'][r['job'],r['op']]['machine']) if c2 else None,
               'changed_start_vs_C1':sum(1 for a,b in zip(sorted(c1,key=lambda r:(r['job'],r['op'])),sorted(c2,key=lambda r:(r['job'],r['op']))) if a['start']!=b['start']) if c2 else None}})
 out={'scope':'G4 synthetic machine downtime on public FJSP only; not DENSO or cross-department evidence',
     'data_sha256':hashlib.sha256(data.read_bytes()).hexdigest(),'python':platform.python_version(),
     'time_limit_s':args.time_limit,'C0H':{'makespan':makespan(c0h),'valid':True},'C0O':c0o_rec,'cases':rows,
     'summary':{'cases':len(rows),'affected_plan_cases':sum(r['event']['affects_plan'] for r in rows),
       'C2_valid_cases':sum(r['C2']['valid'] for r in rows),'C2_status_counts':dict(Counter(r['C2']['status'] for r in rows)),
       'positive_event_loss_cases':sum(r['metrics'] is not None and r['metrics']['L_event']>0 for r in rows),
       'no_positive_event_loss_cases':sum(r['metrics'] is not None and r['metrics']['L_event']<=0 for r in rows)}}
 Path(args.out).parent.mkdir(parents=True,exist_ok=True);Path(args.out).write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
 print(json.dumps(out['summary'],indent=2))
 if len(rows)!=36 and not args.limit:raise SystemExit('Expected 36 cases for mk01, found '+str(len(rows)))
 if any(not r['C2']['valid'] for r in rows):raise SystemExit('C2 missing/invalid; raw artifact preserved')
if __name__=='__main__':main()
