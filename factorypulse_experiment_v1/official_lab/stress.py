"""P2: bounded model-level stress test and controlled relaxation, NOT unsat proof beyond CP-SAT status."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from fjsp import parse_fjsp,greedy
from response_v2 import solve_shared,audit_shared,scenario_state
from run_response_matrix import scenario

def diagnose(inst,base,seed,kind,timeout=3,qa_bytes=None):
    state,event,mat,qa=scenario(inst,base,seed,kind,qa_bytes)
    def solve(m,q,s):
        info,plan=solve_shared(s,base,material=m,qa=q,mode='C2',timeout=timeout,seed=seed)
        if plan is not None:
            errs=audit_shared(s,base,plan,m,q)
            if errs:raise AssertionError(errs)
        return {'status':info['status'],'makespan':info.get('makespan'),'elapsed_s':info.get('elapsed_s')}
    primary=solve(mat,qa,state)
    none_mat={'initial':{m:sum(row.get(m,0) for row in mat['bom'].values()) for m in mat['initial']},'deliveries':[],'bom':mat['bom']}
    none_qa={'defects':[]}
    no_failure=scenario_state(inst,base,event['time'],event['machine'],event['duration'],has_failure=False)
    alternatives={
        'remove_material_shortage':solve(none_mat,qa,state),
        'remove_qa_hold':solve(mat,none_qa,state),
        'remove_machine_failure':solve(mat,qa,no_failure),
        'remove_all_three':solve(none_mat,none_qa,no_failure),
    }
    restored=[k for k,v in alternatives.items() if primary['status']=='INFEASIBLE' and v['status'] in ('OPTIMAL','FEASIBLE')]
    diagnosis=('EXPERIMENTAL_RELAXATION_RESTORES_FEASIBILITY' if restored else
               'UNDETERMINED' if primary['status']=='INFEASIBLE' else 'NO_INFEASIBILITY_TO_EXPLAIN')
    return {'event':event,'primary':primary,'relaxation_experiments':alternatives,
            'relaxations_restoring_feasibility':restored,'diagnosis':diagnosis,
            'warning':'Relaxation shows a sufficient change for feasibility, not a mathematically minimal unsat core.'}

def execute(path,out,seeds=(42,123),kinds=('machine_material','machine_qa','material_qa','all'),timeout=3,qa_bytes=None):
    inst=parse_fjsp(path);base=greedy(inst)
    res=[{'seed':seed,'scenario':kind,**diagnose(inst,base,seed,kind,timeout,qa_bytes)} for seed in seeds for kind in kinds]
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(res,indent=2),encoding='utf8')
    print('STRESS',len(res),'CASES',sum(r['primary']['status']=='INFEASIBLE' for r in res),'PROVEN_INFEASIBLE_FOR_ENCODED_MODEL')
    return res
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',default=str(ROOT/'data'/'mk01.txt'));p.add_argument('--out',default=str(ROOT/'results'/'official_lab'/'stress.json'));p.add_argument('--timeout',type=float,default=3);a=p.parse_args()
    execute(a.data,a.out,timeout=a.timeout)
