"""Prespecified paired robustness experiment; additive to frozen G3/G4/v2."""
import argparse,csv,hashlib,json,platform,sys,time,traceback
from pathlib import Path
from random import Random
sys.path.insert(0,str(Path(__file__).parent/'src'))
from fjsp import parse_fjsp,greedy,makespan
from response_v2 import scenario_state,build_material_spec,solve_shared,audit_shared
from qa_public import read_archive,qa_from_labels

SEEDS=(42,123,456,789,2026)
SCENARIOS=('machine','material','qa','machine_material','machine_qa','material_qa','all')
# Fixed before evaluation; weights apply to RAW integer objective terms.
WEIGHTS={'B3-M':(100000,10,1),'B3-B':(1000,200,1),'B3-S':(100,1000,10)}
MODES=('C1','C2','B3-M','B3-B','B3-S')
SCHEMA='FactoryPulse-response-matrix-1.0'

def sha(data):return hashlib.sha256(data).hexdigest()
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf8')
def scenario(inst,base,seed,kind,qa_bytes=None):
    rng=Random(seed*1000003+SCENARIOS.index(kind)*9176)
    # Do not change public job processing/machine alternatives.
    t=max(1,makespan(base)//3+rng.randint(-2,2))
    machine=rng.randrange(inst['machines'])
    failure='machine' in kind or kind=='all'
    event={'time':t,'machine':machine,'duration':rng.randint(3,7) if failure else 1,'has_failure':failure}
    state=scenario_state(inst,base,t,machine,event['duration'],has_failure=failure)
    shortage='material' in kind or kind=='all'
    material=build_material_spec(inst,seed=seed,mode='shortage' if shortage else 'none')
    # Past consumption cannot be undone. Supply shortages occur strictly after snapshot.
    if shortage:
        for mat in material['initial']:
            consumed=sum(material['bom'][f"{s['job']}:{s['op']}"].get(mat,0) for s in base if s['start']<t)
            total=sum(v.get(mat,0) for v in material['bom'].values())
            residual=max(0,total-consumed)
            material['initial'][mat]=consumed+min(1,residual)
            for d in material['deliveries']:
                if d['material']==mat:
                    d['time']=t+rng.randint(8,12)
                    d['quantity']=max(0,residual-1)
            material['deliveries']=[d for d in material['deliveries'] if d['quantity']>0]
    has_qa='qa' in kind or kind=='all'
    if has_qa and qa_bytes:
        qa=qa_from_labels(read_archive(qa_bytes),inst,base,seed,sha(qa_bytes))
    elif has_qa:
        j=rng.randrange(len(inst['jobs']))
        last_end=max(x['end'] for x in base if x['job']==j)
        qa={'defects':[{'job':j,'machine':min(inst['jobs'][j][-1]),'duration':rng.randint(2,5),'hold_until':last_end+rng.randint(4,8),'source':'SYNTHETIC_POLICY'}]}
    else:qa={'defects':[]}
    return state,event,material,qa

def execute(data_paths,output_dir,qa_data=None,timeout=2.0,seeds=SEEDS,scenarios=SCENARIOS):
    output=Path(output_dir);output.mkdir(parents=True,exist_ok=True)
    qb=Path(qa_data).read_bytes() if qa_data else None
    manifest={'schema':SCHEMA,'protocol_revision':'1.0 frozen','git_sha':'PROVIDED_BY_CI_ENV',
              'instances':{},'qa_archive_sha256':sha(qb) if qb else None,
              'qa_provenance':'UCI_198_REAL_LABELS_SYNTHETIC_MAPPING' if qb else 'SYNTHETIC_QA_FLAGS',
              'seeds':list(seeds),'scenario_types':list(scenarios),'methods':list(MODES),
              'weights':{k:list(v) for k,v in WEIGHTS.items()},'timeout_seconds_per_arm':timeout,
              'environment':{'python':sys.version,'platform':platform.platform()},
              'status_definition':'OPTIMAL/FEASIBLE valid schedule; INFEASIBLE proven for the encoded model only; UNKNOWN not proven impossible',
              'all_results_are_synthetic_simulation':True}
    import os
    manifest['git_sha']=os.environ.get('GITHUB_SHA','LOCAL_UNCOMMITTED')
    records=[];start=time.perf_counter()
    for path in data_paths:
        p=Path(path);raw=p.read_bytes();inst=parse_fjsp(p);base=greedy(inst)
        manifest['instances'][p.stem]={'file':p.name,'sha256':sha(raw),'jobs':len(inst['jobs']),'machines':inst['machines']}
        for seed in seeds:
            for kind in scenarios:
                state,event,mat,qa=scenario(inst,base,seed,kind,qb)
                inputs={'instance':p.stem,'seed':seed,'scenario':kind,'event':event,'material':mat,'qa':qa,'origin_schedule':base}
                rec={'input':inputs,'input_sha256':sha(canonical(inputs)),'arms':{}}
                for mode in MODES:
                    weights=WEIGHTS.get(mode,WEIGHTS['B3-B'])
                    try:
                        info,plan=solve_shared(state,base,material=mat,qa=qa,
                            mode=mode if mode in ('C1','C2') else 'B3',weights=weights,
                            timeout=timeout,seed=seed)
                        if plan is not None:
                            violations=audit_shared(state,base,plan,mat,qa)
                            if violations:raise AssertionError('; '.join(violations))
                        info['declared_mode']=mode
                        rec['arms'][mode]={'info':info,'schedule':plan,'error':None}
                    except Exception as ex:
                        rec['arms'][mode]={'info':{'status':'ERROR','declared_mode':mode},'schedule':None,
                                          'error':type(ex).__name__+': '+str(ex)}
                records.append(rec)
        print('FINISHED INSTANCE',p.stem, 'records',len(records),flush=True)
    document={'schema':SCHEMA,'manifest':manifest,'records':records}
    json_path=output/'response_matrix.json';json_path.write_text(json.dumps(document,indent=2,ensure_ascii=False),encoding='utf8')
    cols=('instance','seed','scenario','input_sha256','method','status','makespan','reassigned','start_shift','order_inversions','wall_s','elapsed_s','error')
    rows=[]
    for rec in records:
        inp=rec['input']
        for mode,arm in rec['arms'].items():
            info=arm['info'];change=info.get('changes') or {}
            rows.append({'instance':inp['instance'],'seed':inp['seed'],'scenario':inp['scenario'],
                         'input_sha256':rec['input_sha256'],'method':mode,'status':info.get('status'),
                         'makespan':info.get('makespan'),'reassigned':change.get('reassigned'),
                         'start_shift':change.get('start_shift'),'order_inversions':change.get('machine_order_inversions'),
                         'wall_s':info.get('wall_s'),'elapsed_s':info.get('elapsed_s'),'error':arm['error']})
    with (output/'response_matrix.csv').open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
    manifest['output_json_sha256']=sha(json_path.read_bytes())
    manifest['output_csv_sha256']=sha((output/'response_matrix.csv').read_bytes())
    # Separate manifests avoid a cyclic digest dependency.
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    summary={'expected_cases':len(data_paths)*len(seeds)*len(scenarios),'actual_cases':len(records),
             'expected_arms':len(data_paths)*len(seeds)*len(scenarios)*len(MODES),'actual_arms':len(rows),
             'elapsed_s':time.perf_counter()-start,'status_counts':{},'comparisons':{}}
    for method in MODES:
        subset=[x for x in rows if x['method']==method]
        summary['status_counts'][method]={status:sum(x['status']==status for x in subset) for status in sorted(set(x['status'] for x in subset))}
    for method in WEIGHTS:
        for baseline in ('C1','C2'):
            for metric,direction in (('makespan','min'),('reassigned','min'),('start_shift','min'),('order_inversions','min')):
                for group_field,group_values in (('overall',['ALL']),('instance',[Path(p).stem for p in data_paths]),('scenario',list(scenarios))):
                    for group in group_values:
                        wins=ties=losses=excluded=0;deltas=[]
                        for rec in records:
                            inp=rec['input']
                            if group_field=='instance' and inp['instance']!=group:continue
                            if group_field=='scenario' and inp['scenario']!=group:continue
                            x=rec['arms'][baseline]['info'];y=rec['arms'][method]['info']
                            if x.get('status') not in ('OPTIMAL','FEASIBLE') or y.get('status') not in ('OPTIMAL','FEASIBLE'):
                                excluded+=1;continue
                            if metric=='makespan':a=x['makespan'];b=y['makespan']
                            else:
                                key={'reassigned':'reassigned','start_shift':'start_shift','order_inversions':'machine_order_inversions'}[metric]
                                a=x['changes'][key];b=y['changes'][key]
                            deltas.append(b-a)
                            if b<a:wins+=1
                            elif b>a:losses+=1
                            else:ties+=1
                        k=f'{method}_vs_{baseline}/{metric}/{group_field}/{group}'
                        summary['comparisons'][k]={'win':wins,'tie':ties,'loss':losses,'excluded':excluded,
                            'paired_feasible':len(deltas),'mean_delta_B3_minus_baseline':sum(deltas)/len(deltas) if deltas else None,
                            'median_delta_B3_minus_baseline':sorted(deltas)[len(deltas)//2] if deltas else None}
    (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
    print('OUTPUT',output,'CASES',len(records),'ARMS',len(rows));return document

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',nargs='+',default=['data/mk01.txt','data/mk02.txt','data/mk03.txt'])
    p.add_argument('--out-dir',default='results/response_matrix');p.add_argument('--qa-data')
    p.add_argument('--timeout',type=float,default=2.0)
    p.add_argument('--seeds',nargs='+',type=int,default=list(SEEDS));p.add_argument('--scenarios',nargs='+',choices=SCENARIOS,default=list(SCENARIOS))
    a=p.parse_args();execute(a.data,a.out_dir,a.qa_data,a.timeout,a.seeds,a.scenarios)
