"""Compare old greedy simulator and prioritized time-expanded planner on matched seeds."""
import argparse, json, random
from pathlib import Path
from .cooperative_fleet import plan
from .fleet_safety_lab import Agent
from .fleet_stress import audit_history

def run(seeds=100,horizon=100):
    successes=0; unsolved=[]; failures=[]; completed=0; total=0
    for seed in range(seeds):
        rng=random.Random(seed);cells=[(x,y) for x in range(12) for y in range(8)];rng.shuffle(cells)
        blocked=set(cells[:8]);starts=cells[8:28];goals=cells[28:48]
        agents=[Agent(f'R{i:02d}',starts[i],goals[i],('amr','tug','inspection')[i%3],i!=seed%20) for i in range(20)]
        r=plan(agents,blocked=blocked,horizon=horizon)
        total+=19
        if r['status']=='FINISHED':
            successes+=1;completed+=r['completed_healthy']
            issues=audit_history(r['history'],blocked)
            if issues:failures.append({'seed':seed,'issues':issues[:5]})
            if any(dict(h)[f'R{seed%20:02d}']!=starts[seed%20] for h in r['history']):failures.append({'seed':seed,'issues':['failed moved']})
        else:unsolved.append(seed)
    report={'cases':seeds,'robots_per_case':20,'complete_scenarios':successes,
     'completion_rate':successes/seeds,'completed_healthy_in_successful_scenarios':completed,
     'total_healthy_across_all_scenarios':total,'unsolved_seed_examples':unsolved[:20],
     'independent_audit_failed_scenarios':len(failures),'audit_examples':failures[:5],
     'limitations':['Prioritized planning is incomplete and may fail on solvable cases','Failures are reported as unsolved, never hidden','Discrete point robots only; no physical safety guarantee']}
    if failures:raise AssertionError(report)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seeds',type=int,default=100);p.add_argument('--out');a=p.parse_args()
    result=run(a.seeds)
    if a.out:Path(a.out).write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
