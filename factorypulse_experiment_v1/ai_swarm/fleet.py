"""Deterministic heterogeneous fleet disruption simulator (proposal, not WareTwin port).

Robots have capabilities, payload, battery and health. Broken robot is removed,
blocked cells are avoided, and a second eligible AMR is reassigned via A*.
The output is a production-material delivery ETA, not a CP-SAT result.
"""
from dataclasses import dataclass
import heapq, json

@dataclass(frozen=True)
class Robot:
    id:str
    kind:str
    capabilities:frozenset
    payload_kg:int
    battery:int
    pos:tuple
    healthy:bool=True

@dataclass(frozen=True)
class Delivery:
    id:str
    material:str
    kg:int
    capability:str
    pickup:tuple
    station:tuple
    required_by:int


def shortest_path(start,finish,blocked,width=12,height=8):
    if start in blocked or finish in blocked:return None
    q=[(abs(start[0]-finish[0])+abs(start[1]-finish[1]),0,start)]
    dist={start:0};prev={};seen=set()
    while q:
        _,g,u=heapq.heappop(q)
        if u in seen:continue
        seen.add(u)
        if u==finish:
            path=[u]
            while u in prev:u=prev[u];path.append(u)
            return list(reversed(path))
        for v in ((u[0]+1,u[1]),(u[0]-1,u[1]),(u[0],u[1]+1),(u[0],u[1]-1)):
            if not (0<=v[0]<width and 0<=v[1]<height) or v in blocked:continue
            ng=g+1
            if ng<dist.get(v,10**9):dist[v]=ng;prev[v]=u;heapq.heappush(q,(ng+abs(v[0]-finish[0])+abs(v[1]-finish[1]),ng,v))
    return None


def assign(robots,task,blocked=frozenset(),now=0):
    ranked=[]
    for robot in robots:
        if not robot.healthy or task.capability not in robot.capabilities or task.kg>robot.payload_kg:continue
        a=shortest_path(robot.pos,task.pickup,blocked)
        b=shortest_path(task.pickup,task.station,blocked)
        if a is None or b is None:continue
        steps=len(a)+len(b)-2
        if robot.battery<steps*2+15:continue # deterministic reserve; not battery physics
        ranked.append((steps,-robot.battery,robot.id,robot,a,b))
    if not ranked:return {'status':'BLOCKED_NO_ELIGIBLE_ROBOT','task_id':task.id,'eta':None,'robot':None}
    steps,_,_,robot,a,b=min(ranked)
    return {'status':'ASSIGNED','task_id':task.id,'eta':now+steps,'robot':robot.id,
            'path_to_pickup':a,'path_to_station':b,'battery_after':robot.battery-2*steps,
            'late_by':max(0,now+steps-task.required_by)}


def scenario():
    robots=[Robot(f'AMR-{i:02d}','light-AMR',frozenset({'parts'}),30,85,(1+i%3,1+i//3)) for i in range(1,13)]
    robots += [Robot(f'TUG-{i:02d}','heavy-tug',frozenset({'parts','heavy'}),200,90,(1+i,6)) for i in range(1,5)]
    robots += [Robot(f'SERVICE-{i:02d}','service',frozenset({'inspection'}),5,80,(8,i+1)) for i in range(1,5)]
    task=Delivery('DELIVERY-7','MAT_A',18,'parts',(1,1),(10,5),15)
    baseline=assign(robots,task)
    failed=robots[0]
    # Realistically, the broken robot blocks its cell. Only the other robots may replan.
    updated=[r if r.id!=failed.id else Robot(r.id,r.kind,r.capabilities,r.payload_kg,r.battery,r.pos,False) for r in robots]
    recovery=assign(updated,task,frozenset({failed.pos}),now=4)
    return {'schema':'FactoryPulse-fleet-demo-v1','scenario':'AMR failure -> materials ETA',
            'robot_count':len(robots),'heterogeneous_types':sorted(set(r.kind for r in robots)),
            'failed_robot':failed.id,'baseline':baseline,'recovery':recovery,
            'material_gate':{'material':task.material,'station':'assembly-1',
                 'earliest_arrival_after_failure':recovery['eta'],
                 'earliest_production_start':recovery['eta'],
                 'note':'Bridge field for future CP-SAT integration; NOT yet fed to solve_shared'},
            'limits':['Single-job A*; no multi-robot collision reservation or deadlock guarantees',
                      'No robot control, no real sensor data, no WareTwin engine imported']}

if __name__=='__main__': print(json.dumps(scenario(),indent=2))
