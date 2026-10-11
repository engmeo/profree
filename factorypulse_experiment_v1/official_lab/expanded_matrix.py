"""Additive predeclared cross-instance LOCAL/C1/C2/B3 comparison.

Never tunes cases after observing results. All event/material/QA data remain synthetic.
"""
import argparse, csv, hashlib, json, os, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT), str(Path(__file__).resolve().parent)]
from fjsp import parse_fjsp, greedy, validate_schedule
GOOD={"OPTIMAL","FEASIBLE"}
METHODS=("LOCAL","C1","C2","B3-B")

SEEDS = (42, 123, 456)
KINDS = ('machine', 'material', 'qa')
# Fixed selection of first and last job; deliberately independent of outcomes.
SCHEMA = 'FactoryPulse-expanded-predeclared-v1'


def summarize(records):
    rows=[]
    for r in records:
        l=r['arms']['LOCAL']; c=r['arms']['C2']
        stl=l['info']['status']; stc=c['info']['status']
        row={'instance':r['instance'],'seed':r['input']['seed'],'scenario':r['input']['kind'],
             'focus':r['input']['focus'],'input_sha256':r['input_sha256'],
             'LOCAL_status':stl,'C2_status':stc,'C1_status':r['arms']['C1']['info']['status'],
             'B3_B_status':r['arms']['B3-B']['info']['status'],
             'classification':'EXCLUDED_NONPAIRED','global_comparison_LOCAL_vs_C2':'EXCLUDED','focus_completion_delta_LOCAL_minus_C2':None,
             'weighted_tardiness_delta_LOCAL_minus_C2':None}
        if stl in GOOD and stc in GOOD:
            k1=l['kpi']; k2=c['kpi']; dc=k1['focus_completion']-k2['focus_completion'];dt=k1['weighted_tardiness']-k2['weighted_tardiness']
            row.update(focus_completion_delta_LOCAL_minus_C2=dc,weighted_tardiness_delta_LOCAL_minus_C2=dt,global_comparison_LOCAL_vs_C2=('WIN' if dt<0 else 'TIE' if dt==0 else 'LOSS'))
            # Tradeoff outcome specifically tests whether LOCAL gains focus completion.
            row['classification']=('BACKFIRE' if dc<0 and dt>0 else
               'LOCAL_FOCUS_GAIN_WITHOUT_GLOBAL_HARM' if dc<0 and dt<=0 else
               'NO_LOCAL_FOCUS_GAIN')
        rows.append(row)
    by_inst={}
    for instance in sorted({x['instance'] for x in rows}):
        sub=[x for x in rows if x['instance']==instance]
        by_inst[instance]={'total':len(sub),'paired_valid':sum(x['classification']!='EXCLUDED_NONPAIRED' for x in sub),
            'backfire':sum(x['classification']=='BACKFIRE' for x in sub),
            'focus_gain_without_global_harm':sum(x['classification']=='LOCAL_FOCUS_GAIN_WITHOUT_GLOBAL_HARM' for x in sub),
            'no_focus_gain':sum(x['classification']=='NO_LOCAL_FOCUS_GAIN' for x in sub),
            'excluded_nonpaired':sum(x['classification']=='EXCLUDED_NONPAIRED' for x in sub),
            'global_local_wins':sum(x['global_comparison_LOCAL_vs_C2']=='WIN' for x in sub),
            'global_local_ties':sum(x['global_comparison_LOCAL_vs_C2']=='TIE' for x in sub),
            'global_local_losses':sum(x['global_comparison_LOCAL_vs_C2']=='LOSS' for x in sub)}
    return rows,by_inst


def execute(paths, out, timeout=2.0, seeds=SEEDS, kinds=KINDS):
    from experiment import run_case
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    records=[];manifest={'schema':SCHEMA,'git_sha':os.environ.get('GITHUB_SHA','LOCAL'),
        'seeds':list(seeds),'scenario_types':list(kinds),'focus_selection':'first-and-last-job',
        'seconds_per_solver_arm':timeout,'methods':list(METHODS),
        'data_provenance':'Public Brandimarte FJSP; synthetic seeded machine/material/QA policies; not DENSO data',
        'files':{str(Path(p).name):hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths}}
    t0=time.monotonic()
    for p in paths:
        inst=parse_fjsp(p);base=greedy(inst)
        assert not validate_schedule(inst,base)
        for seed in seeds:
            for kind in kinds:
                for focus in sorted({0,len(inst['jobs'])-1}):
                    case=run_case(inst,base,seed,kind,focus,timeout=timeout)
                    case['instance']=Path(p).stem
                    records.append(case)
        print('FINISHED',Path(p).stem,len(records),flush=True)
    rows,by_inst=summarize(records)
    doc={'schema':SCHEMA,'manifest':manifest,'records':records,
         'summary':{'evaluated':len(records),'by_instance':by_inst,'elapsed_seconds':round(time.monotonic()-t0,2)}}
    (out/'results.json').write_text(json.dumps(doc,indent=2,ensure_ascii=False),encoding='utf-8')
    (out/'summary.json').write_text(json.dumps(doc['summary'],indent=2),encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    with (out/'paired_comparisons.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print('EXPANDED_MATRIX',json.dumps(doc['summary']))
    return doc

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--data',nargs='+',required=True)
    p.add_argument('--out',required=True)
    p.add_argument('--timeout',type=float,default=2)
    args=p.parse_args()
    execute(args.data,args.out,args.timeout)
