"""G4 P1a: conservative, deterministic minimal-delay repair (C1).

Preserves machine assignment and the order of non-frozen operations from the
original schedule. All times are half-open discrete FJSP benchmark units.
This is a policy counterfactual, not literal inaction by factory staff.
"""
from collections import defaultdict
from dynamic import key, validate_after, _adjust
from fjsp import validate_schedule, makespan


def minimal_repair(state):
    """Construct C1 with immutable fixed work, no reassignment/reordering.

    Among operations whose job predecessor and machine predecessor have been
    planned, choose by (earliest feasible start, baseline start, machine,
    job, operation). The explicit tie-break avoids dependence on dict order.
    Re-execute running operations on the failed machine from zero at/after t.
    """
    inst = state['instance']
    original = state['baseline']
    fixed = state['fixed']
    plan = {k: dict(v) for k, v in fixed.items()}
    machine_order = defaultdict(list)
    for k, row in original.items():
        machine_order[row['machine']].append(k)
    for machine in machine_order:
        machine_order[machine].sort(key=lambda k: (original[k]['start'],original[k]['end'],k))
    predecessors = {}
    for machine, seq in machine_order.items():
        for prev, nxt in zip(seq, seq[1:]):
            predecessors[nxt] = prev
    pending = set(original) - set(fixed)
    while pending:
        options=[]
        for j,o in sorted(pending):
            k=(j,o)
            machine_pred=predecessors.get(k)
            job_pred=(j,o-1) if o else None
            if machine_pred is not None and machine_pred not in plan:
                continue
            if job_pred is not None and job_pred not in plan:
                continue
            row=original[k];m=row['machine'];d=inst['jobs'][j][o][m]
            start=max(state['time'],row['start'],
                      plan[machine_pred]['end'] if machine_pred is not None else 0,
                      plan[job_pred]['end'] if job_pred is not None else 0)
            start=_adjust(start,d,m,state)
            # Protect the frozen in-progress work on each machine. The
            # original machine order guarantees its preceding relationship.
            if any(m==f['machine'] and start<f['end'] and f['start']<start+d
                   for f in fixed.values()):
                start=max(f['end'] for f in fixed.values() if f['machine']==m and
                          start<f['end'] and f['start']<start+d)
                start=_adjust(start,d,m,state)
            options.append((start,row['start'],m,j,o,d))
        if not options:
            raise RuntimeError('minimal repair deadlock: inconsistent precedence / machine order')
        start,_,m,j,o,d=min(options)
        plan[j,o]=dict(job=j,op=o,machine=m,start=start,end=start+d)
        pending.remove((j,o))
    result=[plan[k] for k in sorted(plan)]
    errors=validate_after(state,result)
    if errors:
        raise AssertionError(f'minimal repair invalid: {errors}')
    return result


def g4_metrics(c0h, c0o, c1, c2):
    """Metrics only; caller must validate all plans against proper scenarios."""
    baseline=makespan(c0h)
    event_loss=makespan(c1)-baseline
    gain=makespan(c1)-makespan(c2)
    return {'C0H':baseline,'C0O':makespan(c0o),'C1':makespan(c1),'C2':makespan(c2),
            'L_event':event_loss,'G_response':gain,
            'R_recovery_pct':100*gain/event_loss if event_loss>0 else None,
            'G_global':baseline-makespan(c0o)}
