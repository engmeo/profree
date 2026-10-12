"""Research-only prioritized space-time A* for discrete grid AMR simulation.

Each robot is a point occupying one cell per integer tick; this is NOT a
physical robot safety controller. Robots that are unhealthy never move.
"""
from __future__ import annotations
from collections import defaultdict
from heapq import heappop, heappush
import random

from .fleet_safety_lab import Agent


def _neighbors(p, width, height, blocked):
    x, y = p
    for q in ((x,y),(x+1,y),(x-1,y),(x,y+1),(x,y-1)):
        if 0 <= q[0] < width and 0 <= q[1] < height and q not in blocked:
            yield q


def _path(start, goal, vertex, edges, stationary, width, height, blocked, horizon):
    """A*: vertex/edge reservations checked in both directions.

    Prior robots retain their goal forever. Future unplanned robots are
    conservatively treated as immobile obstacles until separately planned.
    """
    h=lambda p: abs(p[0]-goal[0])+abs(p[1]-goal[1])
    queue=[(h(start), 0, start)]
    parent={}; seen={(start,0)}
    while queue:
        _, t, pos=heappop(queue)
        if pos==goal and all(goal not in vertex.get(k,set()) for k in range(t,horizon+1)):
            route=[pos]
            while (pos,t) in parent:
                pos,t=parent[pos,t];route.append(pos)
            return route[::-1]
        if t>=horizon:continue
        for nxt in _neighbors(pos,width,height,blocked):
            if nxt in stationary or nxt in vertex.get(t+1,set()):continue
            if (nxt,pos) in edges.get(t,set()):continue
            node=(nxt,t+1)
            if node in seen:continue
            seen.add(node);parent[node]=(pos,t)
            heappush(queue,(t+1+h(nxt),t+1,nxt))
    return None


def _plan_once(agents, *, width=12, height=8, blocked=frozenset(), horizon=100, attempt=0):
    """Plan non-overlapping paths with wait actions and permanent goal reservations.

    Reports unsolved cases explicitly, rather than faking success.
    """
    agents=list(agents); blocked=set(blocked)
    if horizon<1:raise ValueError('positive horizon required')
    ids=[a.name for a in agents]; starts=[a.pos for a in agents]
    if len(ids)!=len(set(ids)) or len(starts)!=len(set(starts)):
        raise ValueError('duplicate robot identity or initial position')
    if any(not (0<=x<width and 0<=y<height) or (x,y) in blocked for x,y in starts):
        raise ValueError('invalid initial robot position')
    if any(a.goal in blocked or not(0<=a.goal[0]<width and 0<=a.goal[1]<height) for a in agents):
        raise ValueError('invalid robot goal')
    vertex=defaultdict(set);edges=defaultdict(set)
    routes={}; pending={a.name:a.pos for a in agents if a.healthy}
    frozen={a.pos for a in agents if not a.healthy}
    for a in agents:
        if not a.healthy:
            routes[a.name]=[a.pos]
            for t in range(horizon+1):vertex[t].add(a.pos)
    # Deterministic; shorter tasks first, with stable names.
    order=sorted((a for a in agents if a.healthy),key=lambda a:(abs(a.pos[0]-a.goal[0])+abs(a.pos[1]-a.goal[1]),a.name))
    if attempt == 1: order.reverse()
    elif attempt >= 2:
        rng=random.Random(7919*attempt)
        rng.shuffle(order)
    for a in order:
        pending.pop(a.name)
        # Positions of not-yet-planned robots stay forbidden for this route.
        # This prioritization is intentionally conservative; it can lose completeness.
        route=_path(a.pos,a.goal,vertex,edges,frozen|set(pending.values()),width,height,blocked,horizon)
        if route is None:
            return {'status':'UNSOLVED_REQUIRES_REPLAN','reason':'prioritized routing failed',
                    'failed_agent':a.name,'planned':len(routes),'total':len(agents)}
        routes[a.name]=route
        for t in range(horizon+1):
            p=route[min(t,len(route)-1)];vertex[t].add(p)
            if t<len(route)-1:edges[t].add((route[t],route[t+1]))
    finish=max(len(route)-1 for route in routes.values())
    history=[]
    for t in range(finish+1):
        history.append([(a.name,routes[a.name][min(t,len(routes[a.name])-1)]) for a in agents])
    return {'status':'FINISHED','ticks':finish,'history':history,
            'completed_healthy':sum(bool(a.healthy and routes[a.name][-1]==a.goal) for a in agents),
            'healthy_count':sum(a.healthy for a in agents)}


def plan(agents, *, width=12, height=8, blocked=frozenset(), horizon=100, attempts=64):
    """Try deterministic alternate priorities when initial prioritized plan fails."""
    if not isinstance(attempts,int) or attempts<1:raise ValueError('positive attempts required')
    last=None
    for trial in range(attempts):
        result=_plan_once(agents,width=width,height=height,blocked=blocked,horizon=horizon,attempt=trial)
        if result['status']=='FINISHED':
            result['priority_attempt']=trial+1
            return result
        last=result
    last['priority_attempts_exhausted']=attempts
    return last
