"""Multi-seed discrete-grid stress suite, not a physical robot safety case."""
from __future__ import annotations
import argparse
import json
import random
from collections import Counter
from pathlib import Path
from .fleet_safety_lab import Agent, simulate

def audit_history(history, blocked, width=12, height=8):
    failures=[]
    for t,frame in enumerate(history):
        ids=[n for n,_ in frame];positions=[tuple(p) for _,p in frame]
        if len(ids)!=len(set(ids)):failures.append((t,'duplicate identity'))
        if len(positions)!=len(set(positions)):failures.append((t,'vertex collision'))
        if any(not(0<=x<width and 0<=y<height) for x,y in positions):failures.append((t,'out of bounds'))
        if any(p in blocked for p in positions):failures.append((t,'blocked cell occupancy'))
        if t:
            past=dict(history[t-1]);now=dict(frame)
            for a in now:
                if a not in past:failures.append((t,'identity lost'));continue
                x,y=past[a];u,v=now[a]
                if abs(x-u)+abs(y-v)>1:failures.append((t,'nonlocal jump'))
            for i,a in enumerate(ids):
                for b in ids[i+1:]:
                    if now[a]==past[b] and now[b]==past[a] and now[a]!=now[b]:
                        failures.append((t,'edge swap'))
    return failures

def run(seed_count=100,ticks=45):
    if seed_count<1 or ticks<1:raise ValueError('positive seeds and ticks required')
    outcome=Counter();failure_cases=[];total_ticks=0
    for seed in range(seed_count):
        rng=random.Random(seed)
        cells=[(x,y) for x in range(12) for y in range(8)]
        rng.shuffle(cells)
        blocked=frozenset(cells[:8]); starts=cells[8:28];goals=cells[28:48]
        agents=[Agent(f'R{i:02d}',starts[i],goals[i],('amr','tug','inspection')[i%3],healthy=(i!=seed%20)) for i in range(20)]
        response=simulate(agents,ticks=ticks,blocked=blocked)
        issues=audit_history(response['history'],blocked)
        # independently ensure the known failed robot never moves
        robot=f'R{seed%20:02d}'
        initial=dict(response['history'][0])[robot]
        if any(dict(frame)[robot]!=initial for frame in response['history']):issues.append((0,'failed robot moved'))
        if issues: failure_cases.append({'seed':seed,'violations':issues[:20]})
        outcome[response['status']]+=1;total_ticks+=response['ticks']
    report={'schema':'factorypulse-bounded-grid-stress-v1','cases':seed_count,'agents_per_case':20,
            'invariant_violations':sum(bool(x['violations']) for x in failure_cases),
            'failed_examples':failure_cases[:10],'statuses':dict(outcome),
            'average_ticks':total_ticks/seed_count,
            'limitations':['Only discrete 12x8 grid; no motion dynamics, real sensors, speed or human safety',
                           'Stalled is a real limitation, not solved deadlock',
                           'Robot type labels do not model certified physical dynamics']}
    if failure_cases:raise AssertionError(report)
    return report

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--seeds',type=int,default=100)
    a=p.parse_args();report=run(seed_count=a.seeds)
    target=Path(a.out);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('FLEET_STRESS',json.dumps({k:report[k] for k in ('cases','agents_per_case','invariant_violations','statuses')}))

if __name__=='__main__':main()
