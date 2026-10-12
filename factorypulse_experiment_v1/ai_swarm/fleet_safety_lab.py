"""Bounded, deterministic grid reservation laboratory, NOT a physical AMR controller.

No simultaneous same-cell occupancy; no head-on edge swaps. Conservative empty-cell
moves only. A stalled state is explicitly reported rather than silently 'resolved'.
"""
from dataclasses import dataclass
from collections import Counter

@dataclass(frozen=True)
class Agent:
    name: str
    pos: tuple[int, int]
    goal: tuple[int, int]
    kind: str = 'light'
    healthy: bool = True


def step(agents, *, width=12, height=8, blocked=frozenset()):
    """One synchronous tick. Replanning is greedy Manhattan; not collision-free A*."""
    if len({a.pos for a in agents}) != len(agents):
        raise ValueError('initial position collision')
    occupied = {a.pos for a in agents}
    destinations = set()
    updated = []
    moved = 0
    for a in agents:
        target = a.pos
        if a.healthy and a.pos != a.goal:
            x,y = a.pos
            candidates = ((x+1,y),(x-1,y),(x,y+1),(x,y-1))
            ranked = sorted(candidates, key=lambda p:(abs(p[0]-a.goal[0])+abs(p[1]-a.goal[1]),p))
            for p in ranked:
                if not (0<=p[0]<width and 0<=p[1]<height): continue
                if p in blocked or p in occupied or p in destinations: continue
                if abs(p[0]-a.goal[0])+abs(p[1]-a.goal[1]) >= abs(x-a.goal[0])+abs(y-a.goal[1]): continue
                target = p
                break
        destinations.add(target)
        updated.append(Agent(a.name,target,a.goal,a.kind,a.healthy))
        moved += target != a.pos
    assert len({a.pos for a in updated}) == len(updated)
    # Every moving robot goes to a cell that was empty at the START of the tick;
    # therefore a reverse edge swap is impossible by construction.
    assert not any(n.pos in occupied for old,n in zip(agents,updated) if old.pos!=n.pos)
    return updated,moved


def simulate(agents, *, ticks=100, blocked=frozenset()):
    if ticks < 0: raise ValueError('negative time horizon')
    history = [[(a.name,a.pos) for a in agents]]
    for tick in range(ticks):
        agents,moved=step(agents,blocked=blocked)
        history.append([(a.name,a.pos) for a in agents])
        if all(a.pos==a.goal or not a.healthy for a in agents):
            return {'status':'FINISHED','ticks':tick+1,'history':history}
        if not moved:
            return {'status':'STALLED_REQUIRES_REPLAN','ticks':tick+1,'history':history}
    return {'status':'TIME_LIMIT','ticks':ticks,'history':history}


def demonstration():
    agents = [Agent(f'AMR-{i:02d}',(i%10,i//10),(i%10,6+i//10),
                    ('light','tug','service')[i%3], i != 7) for i in range(20)]
    result=simulate(agents,ticks=40,blocked=frozenset({(7,2)}))
    result.pop('history')
    result.update({'robots':20,'failed_robot':'AMR-07',
                   'safety_scope':'Discrete grid cell occupancy only; NOT validated for physical robots',
                   'unsupported':['continuous geometry','braking distance','localization drift','people safety','real multi-AMR throughput','guaranteed deadlock resolution']})
    return result
