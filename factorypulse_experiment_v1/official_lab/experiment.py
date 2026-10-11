"""Official FJSP experiment: local vs C1/C2/B3, trace graph, stress search.
All input is public Brandimarte or explicitly seeded SYNTHETIC policies.
"""
import argparse,hashlib,json,sys,os,time
from pathlib import Path
from random import Random
from collections import defaultdict,deque
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT))
from fjsp import parse_fjsp,greedy,makespan
from response_v2 import solve_shared,audit_shared
from run_response_matrix import scenario as matrix_scenario,WEIGHTS
from graph_oracle import audit_graph_oracle

GOOD={'OPTIMAL','FEASIBLE'}
METHODS=('LOCAL','C1','C2','B3-B')

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def digest(x):return hashlib.sha256(canonical(x)).hexdigest()
def job_finishes(plan):
    return {j:max(x['end'] for x in plan if x['job']==j) for j in {s['job'] for s in plan}}
def kpi(plan,due,priority,focus):
    end=job_finishes(plan)
    return {'focus_completion':end[focus], 'makespan':makespan(plan),
            'weighted_tardiness':sum(priority[str(j)]*max(0,end[j]-due[str(j)]) for j in end),
            'job_completions':end,'lateness':{j:max(0,end[j]-due[str(j)]) for j in end}}

def traced_graph(inst,plan,state,material,qa):
    """Documented constraints and their adjacency; NOT inferred real-world causation."""
    nodes={};edges=[]
    rows=sorted(plan,key=lambda s:(s['start'],s['job'],s['op']))
    key=lambda x:f"op:{x['job']}:{x['op']}"
    for s in rows:
        n=key(s);nodes[n]={'type':'operation',**s}
        mn=f"machine:{s['machine']}";nodes.setdefault(mn,{'type':'machine','machine':s['machine']})
        edges.append({'from':mn,'to':n,'rule':'uses_machine','evidence':{'machine':s['machine']}})
        if s['op']>0:
            edges.append({'from':f"op:{s['job']}:{s['op']-1}",'to':n,'rule':'job_precedence','evidence':{'job':s['job']}})
        for mat,qty in material.get('bom',{}).get(f"{s['job']}:{s['op']}",{}).items():
            name=f'material:{mat}';nodes.setdefault(name,{'type':'material','name':mat})
            edges.append({'from':name,'to':n,'rule':'bom_requirement','evidence':{'quantity':qty}})
    per=defaultdict(list)
    for s in rows:per[s['machine']].append(s)
    for machine,arr in per.items():
        for a,b in zip(sorted(arr,key=lambda x:(x['start'],x['end'])),sorted(arr,key=lambda x:(x['start'],x['end']))[1:]):
            edges.append({'from':key(a),'to':key(b),'rule':'machine_sequence','evidence':{'machine':machine,'previous_end':a['end'],'next_start':b['start']}})
    for job in range(len(inst['jobs'])):
        jn=f'order:{job}';nodes[jn]={'type':'order','job':job}
        prev={'job':job,'op':len(inst['jobs'][job])-1}
        edges.append({'from':key(prev),'to':jn,'rule':'completion_to_order','evidence':{'job':job}})
    for defect in qa.get('defects',[]):
        n=f"qa:{defect['job']}";nodes[n]={'type':'qa_hold','hold_until':defect['hold_until']}
        edges.append({'from':n,'to':f"op:{defect['job']}:{len(inst['jobs'][defect['job']])}",'rule':'qa_rework_hold','evidence':defect})
    # Graph encodes explicit constraints; a path is NOT a measured causal effect.
    return {'nodes':nodes,'edges':edges,'interpretation':'Dependencies, not experimentally identified causation'}

def reachable_bfs(graph,source):
    adj=defaultdict(list)
    for x in graph['edges']:adj[x['from']].append(x['to'])
    seen={source};q=deque([source])
    while q:
        for n in adj[q.popleft()]:
            if n not in seen:seen.add(n);q.append(n)
    return sorted(seen-{source})

def reachable_reference(graph,source):
    """Independent transitive-closure fixed-point formulation for graph audit."""
    visited={source}
    for _ in range(len(graph['nodes'])):
        nxt=visited|{e['to'] for e in graph['edges'] if e['from'] in visited}
        if nxt==visited:break
        visited=nxt
    return sorted(visited-{source})

def check_graph(graph):
    errors=[]
    for e in graph['edges']:
        if e['from'] not in graph['nodes'] or e['to'] not in graph['nodes']:errors.append('missing node in edge')
        if not e.get('evidence') or not e.get('rule'):errors.append('edge missing evidence/rule')
    if errors:return errors
    for n in graph['nodes']:
        if reachable_bfs(graph,n)!=reachable_reference(graph,n):errors.append('reachability reference mismatch: '+n)
    return errors

def run_case(instance,origin,seed,kind,focus,qa_bytes=None,timeout=3,duration_extra=0):
    state,event,material,qa=matrix_scenario(instance,origin,seed,kind,qa_bytes)
    if duration_extra and event['has_failure']:
        from response_v2 import scenario_state
        event['duration']+=duration_extra
        state=scenario_state(instance,origin,event['time'],event['machine'],event['duration'],has_failure=True)
    # KPI preferences are precommitted via seed + public original schedule; equal input for all methods.
    base_end=job_finishes(origin);rng=Random(seed*1009+focus*17)
    due={str(j):base_end[j]+rng.randint(-3,5) for j in base_end}
    priority={str(j):(8 if j!=focus and j%3==0 else 2 if j!=focus else 1) for j in base_end}
    payload={'seed':seed,'kind':kind,'focus':focus,'event':event,'material':material,'qa':qa,'due':due,'priority':priority,'base':origin}
    arms={}
    for method in METHODS:
        actual='B3' if method=='B3-B' else method
        try:
            info,plan=solve_shared(state,origin,material=material,qa=qa,mode=actual,
                local_focus_job=focus if actual=='LOCAL' else None,weights=WEIGHTS['B3-B'],timeout=timeout,seed=seed)
            errors=audit_shared(state,origin,plan,material,qa) if plan is not None else []
            if errors:raise AssertionError('; '.join(errors))
            graph=traced_graph(instance,plan,state,material,qa) if plan is not None else None
            if graph:
                violations=check_graph(graph)+audit_graph_oracle(instance,plan,material,qa,graph)
                if violations:raise AssertionError(str(violations))
            arms[method]={'info':info,'schedule':plan,'kpi':kpi(plan,due,priority,focus) if plan else None,'graph':graph}
        except Exception as ex:
            arms[method]={'info':{'status':'ERROR','error':repr(ex)},'schedule':None,'kpi':None,'graph':None}
    loc=arms['LOCAL']['kpi'];global_=arms['C2']['kpi']
    is_backfire=bool(loc and global_ and loc['focus_completion']<global_['focus_completion'] and loc['weighted_tardiness']>global_['weighted_tardiness'])
    return {'input':payload,'input_sha256':digest(payload),'arms':arms,'counterexample':is_backfire}

def execute(instances,out,seeds=(42,123,456,789,2026),kinds=('machine','material','qa','machine_material','machine_qa','material_qa','all'),timeout=3,limit=180,qa_data=None):
    output=Path(out);output.mkdir(parents=True,exist_ok=True)
    qa_bytes=Path(qa_data).read_bytes() if qa_data else None
    manifest={'source':'official response_v2.py CP-SAT via solve_shared','counterexample_rules':'LOCAL.focus_completion < C2.focus_completion AND LOCAL.weighted_tardiness > C2.weighted_tardiness',
              'instance_files':{Path(p).name:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in instances},
              'qa_sha256':hashlib.sha256(qa_bytes).hexdigest() if qa_bytes else None,'seeds':list(seeds),'scenarios':list(kinds),
              'timeout_seconds':timeout,'limit':limit,'git_sha':os.getenv('GITHUB_SHA','LOCAL'),
              'data_notice':'FJSP public, BOM and QA mappings synthesized, not DENSO data','weights_B3_B':list(WEIGHTS['B3-B'])}
    records=[]; started=time.monotonic()
    for f in instances:
        inst=parse_fjsp(f);base=greedy(inst)
        for seed in seeds:
            for kind in kinds:
                for focus in range(len(inst['jobs'])):
                    if len(records)>=limit:break
                    r=run_case(inst,base,seed,kind,focus,qa_bytes,timeout)
                    r['instance']=Path(f).stem;records.append(r)
                if len(records)>=limit:break
            if len(records)>=limit:break
        if len(records)>=limit:break
    summary={'evaluated':len(records),'counterexamples':sum(x['counterexample'] for x in records),
             'no_counterexample_found':not any(x['counterexample'] for x in records),
             'status_counts':{m:{s:sum(r['arms'][m]['info']['status']==s for r in records) for s in ['OPTIMAL','FEASIBLE','INFEASIBLE','UNKNOWN','ERROR']} for m in METHODS},
             'elapsed_s':round(time.monotonic()-started,2)}
    doc={'schema':'FactoryPulse-official-resilience-lab-v1','manifest':manifest,'summary':summary,'records':records}
    (output/'results.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf8')
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
    # Human-review-ready factual facts. The JSON retains complete paired schedules.
    matches=[]
    for index,case in enumerate(records):
        if not case['counterexample']:continue
        local=case['arms']['LOCAL']['kpi'];c2=case['arms']['C2']['kpi']
        matches.append({'record_index':index,'instance':case['instance'],'input_sha256':case['input_sha256'],
          'seed':case['input']['seed'],'event_type':case['input']['kind'],'focus_job':case['input']['focus'],
          'focus_completion_gain':c2['focus_completion']-local['focus_completion'],
          'additional_weighted_tardiness':local['weighted_tardiness']-c2['weighted_tardiness'],
          'LOCAL':local,'C2':c2,'interpretation':'Counterexample under synthetic deadlines and priority weights, not real plant harm.'})
    (output/'counterexamples.json').write_text(json.dumps(matches,indent=2),encoding='utf8')
    (output/'sha256.txt').write_text(hashlib.sha256((output/'results.json').read_bytes()).hexdigest()+'  results.json\n')
    print('OFFICIAL_LAB',json.dumps(summary));return doc

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',nargs='+',default=[str(ROOT/'data'/'mk01.txt')]);p.add_argument('--out',default=str(ROOT/'results'/'official_lab'))
    p.add_argument('--qa-data');p.add_argument('--timeout',type=float,default=3);p.add_argument('--limit',type=int,default=180)
    p.add_argument('--seeds',nargs='+',type=int,default=[42,123,456,789,2026]);a=p.parse_args()
    execute(a.data,a.out,seeds=a.seeds,timeout=a.timeout,limit=a.limit,qa_data=a.qa_data)
