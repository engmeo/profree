"""Disruption-state transformation, independent validator and dynamic dispatch.
All times are dimensionless benchmark units. No factory connectivity.
"""
from collections import defaultdict
from fjsp import validate_schedule, makespan

FIELDS=('machine','start','end')
def key(row):return (row['job'],row['op'])

def disruption_state(instance, base, t, failed_machine, duration):
    if t < 0 or duration <= 0 or not 0 <= failed_machine < instance['machines']:
        raise ValueError('bad disruption')
    if validate_schedule(instance,base):raise ValueError('invalid original schedule')
    original={key(s):dict(s) for s in base}
    fixed={}; states={}
    for k,s in original.items():
        if s['end'] <= t:
            states[k]='FINISHED';fixed[k]=s
        elif s['start'] < t < s['end']:
            if s['machine']==failed_machine:
                states[k]='RUNNING_FAILED' # restart from zero after t
            else:
                states[k]='RUNNING_UNAFFECTED';fixed[k]=s
        else:
            states[k]='NOT_STARTED'
    return dict(instance=instance,baseline=original,time=t,machine=failed_machine,
                downtime=(t,t+duration),fixed=fixed,states=states)

def validate_after(state,schedule):
    errors=validate_schedule(state['instance'],schedule,
           downtimes=[(state['machine'],*state['downtime'])],fixed=state['fixed'])
    got={key(s):s for s in schedule if all(k in s for k in ('job','op','start','end','machine'))}
    for k,status in state['states'].items():
        if status in ('NOT_STARTED','RUNNING_FAILED') and k in got:
            if got[k]['start'] < state['time']:
                errors.append(f'unscheduled/restarted operation before event: {k}')
        if status=='RUNNING_FAILED' and k in got:
            # Its previous execution is intentionally discarded, no overlap record is accepted.
            if got[k] == state['baseline'][k]:errors.append(f'failed running operation not restarted: {k}')
    return errors

def _adjust(start, duration, machine, state):
    ds,de=state['downtime']
    if machine==state['machine'] and start < de and ds < start+duration:
        return de
    return start

def greedy_repair(state):
    """Dynamic B1, not an incremental optimal solver. Fixed ongoing work is immutable."""
    instance=state['instance'];jobs=instance['jobs']
    fixed=state['fixed'];plan={k:dict(row) for k,row in fixed.items()}
    on_machine=defaultdict(list)
    for s in fixed.values():on_machine[s['machine']].append((s['start'],s['end']))
    remaining={(j,o) for j,ops in enumerate(jobs) for o in range(len(ops))}-set(fixed)
    while remaining:
        proposals=[]
        for j,o in sorted(remaining):
            if o>0 and (j,o-1) not in plan:continue
            earliest=max(state['time'],plan[(j,o-1)]['end'] if o else 0)
            for m,d in sorted(jobs[j][o].items()):
                start=earliest
                for _ in range(len(on_machine[m])+3):
                    ns=_adjust(start,d,m,state)
                    for a,b in sorted(on_machine[m]):
                        if ns < b and a < ns+d:ns=max(ns,b)
                    if ns==start:break
                    start=ns
                else:raise RuntimeError('unable to find machine slot')
                proposals.append((start+d,start,j,o,m))
        if not proposals:raise RuntimeError('precedence deadlock')
        end,start,j,o,m=min(proposals)
        plan[j,o]=dict(job=j,op=o,machine=m,start=start,end=end)
        on_machine[m].append((start,end));remaining.remove((j,o))
    result=[plan[k] for k in sorted(plan)]
    errs=validate_after(state,result)
    if errs:raise AssertionError(f'B1 invalid: {errs}')
    return result

def generate_events(instance,base, fractions=(.25,.50,.75),durations=(5,15)):
    """Deterministic predeclared enumeration: sort t,m,d; include indirect future overlaps."""
    horizon=makespan(base)
    for frac in fractions:
        t=int(horizon*frac)
        for machine in range(instance['machines']):
            for duration in durations:
                active=any(s['machine']==machine and s['end']>t and s['start']<t+duration for s in base)
                yield dict(time=t,machine=machine,duration=duration,affects_plan=active)

def cp_sat_full(state,time_limit=10,seed=11,workers=1):
    """B2 global CP-SAT; requires ortools installed. Includes model build time externally."""
    from ortools.sat.python import cp_model
    import time
    t0=time.perf_counter();inst=state['instance'];jobs=inst['jobs'];model=cp_model.CpModel()
    fixed=state['fixed'];ds,de=state['downtime'];end_upper= max([de]+[s['end'] for s in fixed.values()])+sum(max(x.values()) for ops in jobs for x in ops)+1
    by_machine=defaultdict(list); starts={};ends={}; choices={}
    for j,ops in enumerate(jobs):
        for o,alts in enumerate(ops):
            k=(j,o)
            if k in fixed:
                r=fixed[k];s=model.NewConstant(r['start']);e=model.NewConstant(r['end'])
                iv=model.NewIntervalVar(s,r['end']-r['start'],e,f'fixed_{j}_{o}')
                by_machine[r['machine']].append(iv);starts[k]=s;ends[k]=e
                choices[k]={r['machine']:model.NewConstant(1)}
                continue
            s=model.NewIntVar(state['time'],end_upper,f's{j}_{o}')
            e=model.NewIntVar(state['time'],end_upper,f'e{j}_{o}')
            bs=[]; choices[k]={}
            for m,d in alts.items():
                b=model.NewBoolVar(f'x{j}_{o}_{m}');bs.append(b);choices[k][m]=b
                iv=model.NewOptionalIntervalVar(s,d,e,b,f'iv{j}_{o}_{m}')
                by_machine[m].append(iv)
            model.AddExactlyOne(bs);starts[k]=s;ends[k]=e
    for j,ops in enumerate(jobs):
        for o in range(1,len(ops)):model.Add(starts[j,o]>=ends[j,o-1])
    for m in range(inst['machines']):
        if m==state['machine']:
            by_machine[m].append(model.NewIntervalVar(ds,de-ds,de,f'downtime_{m}'))
        model.AddNoOverlap(by_machine[m])
    cmax=model.NewIntVar(0,end_upper,'makespan')
    model.AddMaxEquality(cmax,list(ends.values()));model.Minimize(cmax)
    solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=max(0.01,time_limit-(time.perf_counter()-t0));solver.parameters.random_seed=seed;solver.parameters.num_search_workers=workers
    status=solver.Solve(model);whole=time.perf_counter()-t0;name=solver.StatusName(status)
    record=dict(status=name,elapsed_s=whole,solver_wall_s=solver.WallTime(),best_bound=solver.BestObjectiveBound() if status in (cp_model.OPTIMAL,cp_model.FEASIBLE) else None)
    if status not in (cp_model.OPTIMAL,cp_model.FEASIBLE):return record,None
    rows=[]
    for (j,o),s in starts.items():
        m=next(m for m,b in choices[j,o].items() if solver.Value(b))
        rows.append(dict(job=j,op=o,machine=m,start=solver.Value(s),end=solver.Value(ends[j,o])))
    rows.sort(key=key);record['makespan']=makespan(rows);record['validation_errors']=validate_after(state,rows)
    return record,rows
