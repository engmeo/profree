"""Research extension: CP-SAT response with shared disruption/material/QA constraints.

All times and costs are simulated benchmark units; no DENSO data or claims.
"""
import copy
import time
from collections import defaultdict


def scenario_state(instance, base, t, machine, duration, has_failure=True):
    from dynamic import disruption_state
    state=disruption_state(instance,base,t,machine,duration)
    if not has_failure:
        for k,v in list(state['states'].items()):
            if v=='RUNNING_FAILED':
                state['states'][k]='RUNNING_UNAFFECTED'
                state['fixed'][k]=state['baseline'][k]
        state['downtime']=(t,t)
    return state


def event_model(instance, base, state, *, material=None, qa=None):
    """Build extension inputs. QA rework appends a new operation to a job;
    quality hold applies to the rework step after the original final operation.
    The baseline itself remains untouched for all original operations.
    """
    inst=copy.deepcopy(instance)
    reference=[dict(s) for s in base]
    release={}
    qa=qa or {}
    for e in qa.get('defects',[]):
        j=int(e['job']); m=int(e['machine']); d=int(e['duration']); hold=int(e['hold_until'])
        if not (0<=j<len(inst['jobs']) and 0<=m<inst['machines'] and d>0 and hold>=0):
            raise ValueError('invalid QA rework event')
        op=len(inst['jobs'][j]);inst['jobs'][j].append({m:d})
        release[j,op]=hold
        prev=max(s['end'] for s in reference if s['job']==j)
        start=max(prev,hold,state['time'])
        reference.append(dict(job=j,op=op,machine=m,start=start,end=start+d))
    # Baseline appended QA operations are not actual frozen work, even if the
    # synthetic reference places them before the disruption timestamp.
    return inst,reference,release


def build_material_spec(instance, seed=17, mode='none'):
    """Synthetic BOM/inbound supply, fully reproducible, not real observations."""
    if mode not in ('none','shortage'):raise ValueError('invalid material mode')
    from random import Random
    rng=Random(seed)
    bom={}
    for j,ops in enumerate(instance['jobs']):
        for o,_ in enumerate(ops):bom[j,o]={'MAT_A' if j%2==0 else 'MAT_B':rng.randint(1,2)}
    total={mat:sum(v.get(mat,0) for v in bom.values()) for mat in ('MAT_A','MAT_B')}
    if mode=='none':initial=dict(total); deliveries=[]
    else:
        initial={mat: max(0,total[mat]//3) for mat in total}
        deliveries=[{'material':mat,'time':20,'quantity':total[mat]-initial[mat]} for mat in sorted(total)]
    return {'initial':initial,'deliveries':deliveries,
            'bom':{f'{j}:{o}':demands for (j,o),demands in bom.items()},'source':'SYNTHETIC_SEEDED','seed':seed}


def material_violations(schedule, material):
    """Independent event-ledger audit: deliveries at time t precede starts at t."""
    if not material:return []
    errors=[]; events=defaultdict(list); stock=defaultdict(int)
    for name,qty in material.get('initial',{}).items():
        if not isinstance(qty,int) or qty<0:errors.append(f'invalid initial inventory {name}')
        stock[name]=qty
    for d in material.get('deliveries',[]):
        if d['quantity']<=0 or d['time']<0:errors.append('invalid delivery')
        events[d['time']].append((0,d['material'],d['quantity'],'delivery'))
    bom=material.get('bom',{})
    for s in schedule:
        for name,qty in bom.get(f"{s['job']}:{s['op']}",{}).items():
            if not isinstance(qty,int) or qty<=0:errors.append('invalid BOM demand')
            events[s['start']].append((1,name,-qty,f"{s['job']}:{s['op']}"))
    for t in sorted(events):
        for _,mat,qty,who in sorted(events[t]):
            stock[mat]+=qty
            if stock[mat]<0:errors.append(f'material negative {mat} at t={t} caused by {who}: {stock[mat]}')
    return errors


def qa_violations(schedule, qa, instance):
    errors=[];lookup={(s['job'],s['op']):s for s in schedule}
    for defect in (qa or {}).get('defects',[]):
        j=defect['job'];o=len(instance['jobs'][j]);s=lookup.get((j,o))
        if not s:errors.append(f'QA missing rework job {j} op {o}');continue
        if s['start']<defect['hold_until']:errors.append(f'QA hold violated job {j}')
        if s['machine']!=defect['machine'] or s['end']-s['start']!=defect['duration']:
            errors.append(f'QA rework resource/duration violated job {j}')
    return errors


def schedule_changes(original, result):
    baseline={(s['job'],s['op']):s for s in original}
    rows=[s for s in result if (s['job'],s['op']) in baseline]
    swapped=sum(s['machine']!=baseline[s['job'],s['op']]['machine'] for s in rows)
    drift=sum(abs(s['start']-baseline[s['job'],s['op']]['start']) for s in rows)
    inversions=0
    for i,a in enumerate(rows):
        for b in rows[i+1:]:
            x=baseline[a['job'],a['op']];y=baseline[b['job'],b['op']]
            if a['machine']==b['machine'] and x['machine']==y['machine']==a['machine']:
                if (x['start']<y['start'] and a['start']>b['start']) or (x['start']>y['start'] and a['start']<b['start']):inversions+=1
    return dict(reassigned=swapped,start_shift=drift,machine_order_inversions=inversions)


def solve_shared(state, original, *, material=None, qa=None, mode='B3', weights=(1000,200,1), timeout=10, seed=11, local_focus_job=None):
    """One solver for B3/C2 on identical instance, snapshot, materials and QA.
    B3 objective: alpha*makespan + beta*#machine reassignments + gamma*sum(abs(start-original_start)).
    Machine-order inversions are *reported*, not in objective.
    """
    from ortools.sat.python import cp_model
    from fjsp import validate_schedule, makespan
    from dynamic import validate_after
    if mode not in ('B3','C2','C1','LOCAL'):raise ValueError('unknown solver mode')
    if mode=='LOCAL' and (not isinstance(local_focus_job,int) or not 0<=local_focus_job<len(state['instance']['jobs'])):raise ValueError('invalid local focus job')
    if len(weights)!=3 or any(not isinstance(w,int) or w<0 for w in weights) or weights[0]==0:
        raise ValueError('bad B3 weights')
    started=time.perf_counter();inst,reference,qa_releases=event_model(state['instance'],original,state,qa=qa)
    # original frozen operations remain immutable, QA steps are always future operations.
    model=cp_model.CpModel();jobs=inst['jobs'];upper=max([state['downtime'][1]]+[s['end'] for s in reference])+sum(max(x.values()) for ops in jobs for x in ops)+100
    intervals=defaultdict(list);starts={};ends={};select={};swaps=[];drifts=[]
    for j,ops in enumerate(jobs):
        for o,alternatives in enumerate(ops):
            k=j,o
            if k in state['fixed']:
                row=state['fixed'][k];s=model.NewConstant(row['start']);e=model.NewConstant(row['end'])
                select[k]={row['machine']:model.NewConstant(1)}
                intervals[row['machine']].append(model.NewIntervalVar(s,row['end']-row['start'],e,f'fixed_{j}_{o}'))
            else:
                lo=max(state['time'],qa_releases.get(k,0));s=model.NewIntVar(lo,upper,f's_{j}_{o}');e=model.NewIntVar(lo,upper,f'e_{j}_{o}')
                choices={}
                for m,d in alternatives.items():
                    b=model.NewBoolVar(f'x_{j}_{o}_{m}');choices[m]=b
                    intervals[m].append(model.NewOptionalIntervalVar(s,d,e,b,f'iv_{j}_{o}_{m}'))
                model.AddExactlyOne(list(choices.values()));select[k]=choices
                base=state['baseline'].get(k)
                if base and mode=='C1':
                    model.Add(s>=base['start'])
                    model.Add(choices[base['machine']]==1)
                if base and mode in ('B3','C1'):
                    base_m=base['machine']
                    if base_m in choices:swaps.append(1-choices[base_m])
                    else:swaps.append(1)
                    delta=model.NewIntVar(0,upper+base['start'],f'delta_{j}_{o}')
                    model.AddAbsEquality(delta,s-base['start']);drifts.append(delta)
            starts[k]=s;ends[k]=e
    for j,ops in enumerate(jobs):
        for o in range(1,len(ops)):model.Add(starts[j,o]>=ends[j,o-1])
    if mode=='C1':
        original_by_machine=defaultdict(list)
        for row in original:original_by_machine[row['machine']].append(row)
        for rows in original_by_machine.values():
            rows.sort(key=lambda x:(x['start'],x['end'],x['job'],x['op']))
            for a,b in zip(rows,rows[1:]):
                model.Add(starts[b['job'],b['op']]>=ends[a['job'],a['op']])
    for m in range(inst['machines']):
        if m==state['machine']:
            ds,de=state['downtime'];intervals[m].append(model.NewIntervalVar(ds,de-ds,de,'downtime'))
        model.AddNoOverlap(intervals[m])
    if material:
        stock=material['initial'];deliveries=material['deliveries'];bom=material['bom']
        materials=set(stock)|{d['material'] for d in deliveries}
        for name in materials:
            changes_times=[model.NewConstant(0)];changes_qty=[stock.get(name,0)];maxinv=stock.get(name,0)
            for d in deliveries:
                if d['material']==name:
                    changes_times.append(model.NewConstant(d['time']));changes_qty.append(d['quantity']);maxinv+=d['quantity']
            for (j,o),s in starts.items():
                demand=bom.get(f'{j}:{o}',{}).get(name,0)
                if demand:changes_times.append(s);changes_qty.append(-demand)
            model.AddReservoirConstraint(changes_times,changes_qty,0,maxinv)
    max_end=model.NewIntVar(0,upper,'makespan');model.AddMaxEquality(max_end,list(ends.values()))
    if mode=='LOCAL':
        # Lexicographic: minimize completion of focal job first; whole-shop makespan second.
        # Same feasible set as C2/B3, with all machine/material/QA/immutable constraints.
        model.Minimize((upper+1)*ends[local_focus_job,len(jobs[local_focus_job])-1]+max_end)
    elif mode=='C2':model.Minimize(max_end)
    elif mode=='C1':
        model.Minimize((upper*len(starts)+1)*max_end+sum(drifts))
    else:
        a,b,c=weights;model.Minimize(a*max_end+b*sum(swaps)+c*sum(drifts))
    solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=timeout;solver.parameters.random_seed=seed;solver.parameters.num_search_workers=1
    status=solver.Solve(model);info=dict(status=solver.StatusName(status),wall_s=solver.WallTime(),elapsed_s=time.perf_counter()-started,mode=mode,weights=list(weights))
    if status not in (cp_model.OPTIMAL,cp_model.FEASIBLE):return info,None
    result=[]
    for (j,o),s in sorted(starts.items()):
        machine=next(m for m,b in select[j,o].items() if solver.Value(b))
        result.append(dict(job=j,op=o,machine=machine,start=solver.Value(s),end=solver.Value(ends[j,o])))
    info['makespan']=makespan(result);info['changes']=schedule_changes(original,result)
    info['errors']=validate_schedule(inst,result,downtimes=[(state['machine'],*state['downtime'])],fixed=state['fixed'])+material_violations(result,material)+qa_violations(result,qa,state['instance'])
    if info['errors']:raise AssertionError(info['errors'])
    return info,result


def audit_shared(state, original, plan, material=None, qa=None):
    from fjsp import validate_schedule
    inst,_,_=event_model(state['instance'],original,state,qa=qa)
    return (validate_schedule(inst,plan,downtimes=[(state['machine'],*state['downtime'])],fixed=state['fixed'])
            +material_violations(plan,material)+qa_violations(plan,qa,state['instance']))
