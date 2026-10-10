"""Non-solution triage: no false attribution of solver INFEASIBLE to a root cause."""
import argparse,json
from pathlib import Path
from collections import defaultdict

def diagnose(record,mode):
    inp=record['input'];arm=record['arms'][mode];info=arm['info'];mat=inp['material']
    total=defaultdict(int);initial=mat.get('initial',{});received=defaultdict(int)
    for demands in mat.get('bom',{}).values():
        for name,q in demands.items():total[name]+=q
    for d in mat.get('deliveries',[]):received[d['material']]+=d['quantity']
    shortages={k:q-initial.get(k,0)-received[k] for k,q in total.items() if q>initial.get(k,0)+received[k]}
    qa=inp['qa'].get('defects',[]);event=inp['event']
    return {'instance':inp['instance'],'seed':inp['seed'],'scenario':inp['scenario'],
        'method':mode,'solver_status':info['status'],'elapsed_seconds':info.get('elapsed_s'),
        'input_sha256':record['input_sha256'],'total_inventory_deficit':shortages,
        'qa_defect_count':len(qa),'qa_hold_until':[x['hold_until'] for x in qa],
        'machine_event':event,'assessment':(
         'PROVEN_GLOBAL_MATERIAL_SHORTAGE_FOR_THIS_MODEL' if shortages else
         'UNDETERMINED_NEEDS_RELAXATION_EXPERIMENT_OR_UNSAT_CORE'),
        'qualification':'A solver INFEASIBLE verdict applies to the encoded model; this diagnostic does not prove other causes.'}

def run(raw,out):
    doc=json.loads(Path(raw).read_text(encoding='utf8'));items=[]
    for rec in doc['records']:
        for mode,arm in rec['arms'].items():
            if arm['info']['status'] not in ('OPTIMAL','FEASIBLE'):
                items.append(diagnose(rec,mode))
    Path(out).write_text(json.dumps({'non_solution_arms':len(items),'cases':items},indent=2),encoding='utf8')
    return items
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--raw',required=True);p.add_argument('--out',required=True)
    a=p.parse_args();print('Non-solution arms:',len(run(a.raw,a.out)))
