"""No-disruption CP-SAT benchmark C0O; instance FJSP without factory data."""
from collections import defaultdict
import time
from fjsp import validate_schedule, makespan


def cp_sat_no_event(instance, time_limit=10, seed=11, workers=1):
    from ortools.sat.python import cp_model
    start_clock=time.perf_counter()
    model=cp_model.CpModel(); jobs=instance['jobs']
    horizon=sum(max(alts.values()) for job in jobs for alts in job)
    starts={}; ends={}; assignment={}; occupancy=defaultdict(list)
    for j,job in enumerate(jobs):
        for o,alts in enumerate(job):
            key=(j,o);s=model.NewIntVar(0,horizon,f's_{j}_{o}'); e=model.NewIntVar(0,horizon,f'e_{j}_{o}')
            starts[key]=s;ends[key]=e;assignment[key]={}
            for m,d in sorted(alts.items()):
                present=model.NewBoolVar(f'm_{j}_{o}_{m}')
                assignment[key][m]=present
                occupancy[m].append(model.NewOptionalIntervalVar(s,d,e,present,f'iv_{j}_{o}_{m}'))
            model.AddExactlyOne(list(assignment[key].values()))
            if o:model.Add(s>=ends[j,o-1])
    for intervals in occupancy.values():model.AddNoOverlap(intervals)
    cmax=model.NewIntVar(0,horizon,'makespan')
    model.AddMaxEquality(cmax,list(ends.values()));model.Minimize(cmax)
    solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=max(.01,time_limit-(time.perf_counter()-start_clock))
    solver.parameters.random_seed=seed;solver.parameters.num_search_workers=workers
    status=solver.Solve(model); elapsed=time.perf_counter()-start_clock
    rec={'status':solver.StatusName(status),'elapsed_s':elapsed,'solver_wall_s':solver.WallTime(),
         'best_bound':solver.BestObjectiveBound() if status in (cp_model.FEASIBLE,cp_model.OPTIMAL) else None}
    if status not in (cp_model.FEASIBLE,cp_model.OPTIMAL):return rec,None
    schedule=[]
    for (j,o),s in sorted(starts.items()):
        m=next(m for m,b in assignment[j,o].items() if solver.Value(b))
        schedule.append({'job':j,'op':o,'machine':m,'start':solver.Value(s),'end':solver.Value(ends[j,o])})
    rec['makespan']=makespan(schedule);rec['validation_errors']=validate_schedule(instance,schedule)
    return rec,schedule
