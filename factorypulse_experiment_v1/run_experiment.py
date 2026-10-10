"""Reproducible dynamic baseline runner. Run from project root."""
import argparse,sys,json,time,hashlib,platform,statistics
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'src'))
from fjsp import parse_fjsp,greedy,makespan
from dynamic import disruption_state,validate_after,greedy_repair,generate_events,cp_sat_full

def main():
 p=argparse.ArgumentParser();p.add_argument('--data',default='data/mk01.txt');p.add_argument('--out',default='results/dynamic_baselines.json');p.add_argument('--with-cpsat',action='store_true');p.add_argument('--limit',type=int,default=0);args=p.parse_args()
 raw=Path(args.data).read_bytes();inst=parse_fjsp(args.data);base=greedy(inst);rows=[]
 for i,event in enumerate(generate_events(inst,base)):
  if args.limit and i>=args.limit:break
  state=disruption_state(inst,base,event['time'],event['machine'],event['duration'])
  started=time.perf_counter();b1=greedy_repair(state);elapsed=time.perf_counter()-started
  result={'case_id':i,'event':event,'B1':{'makespan':makespan(b1),'valid':not validate_after(state,b1),'wall_s':elapsed,'errors':validate_after(state,b1)}}
  if args.with_cpsat:
   record,plan=cp_sat_full(state,time_limit=10,seed=11,workers=1);result['B2']=record
  rows.append(result)
 output={'scope':'synthetic machine downtime applied to public mk01 FJSP instance; not DENSO data','data_sha256':hashlib.sha256(raw).hexdigest(),'python':platform.python_version(),'platform':platform.platform(),'base_makespan':makespan(base),'cp_sat_executed':args.with_cpsat,'cases':rows,'summary':{'cases':len(rows),'affected_plan_cases':sum(bool(r['event']['affects_plan']) for r in rows),'B1_valid_cases':sum(r['B1']['valid'] for r in rows),'B1_makespan_min':min(r['B1']['makespan'] for r in rows),'B1_makespan_max':max(r['B1']['makespan'] for r in rows),'B1_makespan_median':statistics.median(r['B1']['makespan'] for r in rows)}}
 Path(args.out).parent.mkdir(parents=True,exist_ok=True);Path(args.out).write_text(json.dumps(output,ensure_ascii=False,indent=2));print(json.dumps(output['summary'],indent=2))
if __name__=='__main__':main()
