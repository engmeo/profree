"""Run shared C1/C2/B3 on machine/material/QA event combinations."""
import argparse, csv, hashlib, json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'src'))
from fjsp import parse_fjsp,greedy,makespan
from response_v2 import scenario_state
from response_v2 import build_material_spec, solve_shared, audit_shared
from qa_public import read_archive,qa_from_labels

WEIGHTS=(1000,200,1) # predeclared; not post-hoc tuned

def qa_event(instance,base,seed):
    j=seed%len(instance['jobs']); last=instance['jobs'][j][-1];m=sorted(last)[0]
    last_end=max(x['end'] for x in base if x['job']==j)
    return {'defects':[{'job':j,'machine':m,'duration':4,'hold_until':last_end+6,'source':'SYNTHETIC_POLICY'}]}

def run(path, out, timeout=7, qa_data=None):
    inst=parse_fjsp(path);base=greedy(inst);cases=[]
    qa_bytes=Path(qa_data).read_bytes() if qa_data else None
    labels=read_archive(qa_bytes) if qa_bytes else None
    # pre-registered, paired designs, including combined disruptions.
    scenario_types=['machine','material','qa','machine_material','machine_qa','material_qa','all']
    for case_no,kind in enumerate(scenario_types):
        t=max(1,makespan(base)//3); machine=case_no%inst['machines'];duration=5 if 'machine' in kind or kind=='all' else 1
        state=scenario_state(inst,base,t,machine,duration,has_failure=('machine' in kind or kind=='all'))
        material=build_material_spec(inst,seed=17,mode='shortage') if 'material' in kind or kind=='all' else build_material_spec(inst,seed=17,mode='none')
        if material['deliveries']:
            # Guarantee feasibility of the already-executed immutable prefix.
            for mat in material['initial']:
                consumed=sum(material['bom'][f"{s['job']}:{s['op']}"].get(mat,0) for s in base if s['start']<t)
                remaining=sum(row.get(mat,0) for row in material['bom'].values())-consumed
                material['initial'][mat]=consumed+min(1,remaining)
                for d in material['deliveries']:
                    if d['material']==mat:
                        d['time']=t+10;d['quantity']=remaining-min(1,remaining)
        # No external dataset means QA flags are simulated, provenance never hidden.
        qa=(qa_from_labels(labels,inst,base,case_no,hashlib.sha256(qa_bytes).hexdigest()) if labels else qa_event(inst,base,case_no)) if 'qa' in kind or kind=='all' else {'defects':[]}
        record=dict(id=case_no,scenario=kind,event=dict(time=t,machine=machine,duration=duration,has_failure=('machine' in kind or kind=='all')),material=material,qa=qa,origin_schedule=base,methods={})
        for mode in ('C1','C2','B3'):
            info,plan=solve_shared(state,base,material=material,qa=qa,mode=mode,weights=WEIGHTS,timeout=timeout,seed=11)
            record['methods'][mode]=dict(info=info,schedule=plan)
            if plan is not None:
                checks=audit_shared(state,base,plan,material,qa)
                if checks:raise AssertionError(f'{kind} {mode}: {checks}')
        cases.append(record)
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    result=dict(schema='FactoryPulse-shared-response-v2',instance=Path(path).name,
                source_sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest(),
                synthetic_scenarios=True,qa_label_source=('UCI_198_REAL_LABELS' if labels else 'SYNTHETIC_FLAGS'),objective_weights=list(WEIGHTS),timeout_s=timeout,cases=cases)
    out.write_text(json.dumps(result,indent=2),encoding='utf-8')
    csvout=out.with_suffix('.csv');rows=[]
    for rec in cases:
        for mode,res in rec['methods'].items():
            i=res['info'];ch=i.get('changes',{})
            rows.append(dict(case=rec['id'],scenario=rec['scenario'],mode=mode,status=i['status'],makespan=i.get('makespan'),
                             runtime_seconds=round(i['elapsed_s'],6),reassigned=ch.get('reassigned'),start_shift=ch.get('start_shift'),
                             order_inversions=ch.get('machine_order_inversions'),independent_violations=len(i.get('errors',[]))))
    with csvout.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print('RESULT',out,'CSV',csvout,'cases',len(cases),'arms',len(rows))
    print('statuses', {mode:{status:sum(c['methods'][mode]['info']['status']==status for c in cases) for status in ('OPTIMAL','FEASIBLE','UNKNOWN','INFEASIBLE')} for mode in ('C1','C2','B3')})
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/mk01.txt');p.add_argument('--out',default='results/shared_response_v2.json');p.add_argument('--timeout',type=float,default=7);p.add_argument('--qa-data',default=None)
    a=p.parse_args();run(a.data,a.out,a.timeout,a.qa_data)
