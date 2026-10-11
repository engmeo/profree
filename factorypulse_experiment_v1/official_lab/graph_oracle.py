"""P1 oracle independent of traced_graph()/BFS; regenerates expected exact multiset of edges from FJSP state.
Only asserts modeled dependencies, never observational causality.
"""
from collections import Counter,defaultdict

def edge_signature(e):
    import json
    return (e['from'],e['to'],e['rule'],json.dumps(e['evidence'],sort_keys=True,separators=(',',':')))

def reference_edges(instance,plan,material,qa):
    edges=[]
    ops={(r['job'],r['op']):r for r in plan}
    n_jobs=len(instance['jobs'])
    for (j,o),r in sorted(ops.items()):
        node=f'op:{j}:{o}'
        edges.append({'from':f"machine:{r['machine']}",'to':node,'rule':'uses_machine','evidence':{'machine':r['machine']}})
        if o:
            edges.append({'from':f'op:{j}:{o-1}','to':node,'rule':'job_precedence','evidence':{'job':j}})
        for m,n in material.get('bom',{}).get(f'{j}:{o}',{}).items():
            edges.append({'from':f'material:{m}','to':node,'rule':'bom_requirement','evidence':{'quantity':n}})
    by_machine=defaultdict(list)
    for r in plan:by_machine[r['machine']].append(r)
    for machine,rows in by_machine.items():
        seq=sorted(rows,key=lambda r:(r['start'],r['end']))
        for a,b in zip(seq,seq[1:]):
            edges.append({'from':f"op:{a['job']}:{a['op']}",'to':f"op:{b['job']}:{b['op']}",
                          'rule':'machine_sequence','evidence':{'machine':machine,'previous_end':a['end'],'next_start':b['start']}})
    for j in range(n_jobs):
        edges.append({'from':f'op:{j}:{len(instance["jobs"][j])-1}','to':f'order:{j}',
                     'rule':'completion_to_order','evidence':{'job':j}})
    for d in qa.get('defects',[]):
        j=d['job'];edges.append({'from':f'qa:{j}','to':f'op:{j}:{len(instance["jobs"][j])}',
                                 'rule':'qa_rework_hold','evidence':d})
    return edges

def audit_graph_oracle(instance,plan,material,qa,graph):
    problems=[]
    expected=Counter(map(edge_signature,reference_edges(instance,plan,material,qa)))
    actual=Counter(map(edge_signature,graph['edges']))
    if expected!=actual:
        problems.append('exact model dependency edge multiset mismatch; missing='+str(sum((expected-actual).values()))+
                        ' extra='+str(sum((actual-expected).values())))
    # Strict endpoint and node type validation.
    for edge in graph['edges']:
        if edge['from'] not in graph['nodes'] or edge['to'] not in graph['nodes']:
            problems.append('unknown endpoint: '+str(edge));break
    return problems
