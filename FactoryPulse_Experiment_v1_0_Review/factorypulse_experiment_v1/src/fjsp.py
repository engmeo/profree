"""Strict FJSP parser and separate schedule validator (no solver dependencies)."""
from pathlib import Path
from collections import defaultdict
import json


def parse_fjsp(path):
    rows=[list(map(int, line.split())) for line in Path(path).read_text().splitlines() if line.strip()]
    if len(rows[0])!=2: raise ValueError('invalid header')
    n_jobs,n_machines=rows[0]
    if len(rows)!=n_jobs+1: raise ValueError('incorrect job row count')
    if n_jobs<1 or n_machines<1: raise ValueError('nonpositive dimensions')
    jobs=[]
    for j,row in enumerate(rows[1:]):
        k=0
        nops=row[k];k+=1
        if nops<1: raise ValueError(f'job {j} has no operations')
        ops=[]
        for o in range(nops):
            if k>=len(row):raise ValueError('truncated operation header')
            nopt=row[k];k+=1
            if nopt<1 or k+2*nopt>len(row):raise ValueError('invalid options count')
            choices={}
            for _ in range(nopt):
                m,d=row[k:k+2];k+=2
                if not 0<=m<n_machines or d<=0 or m in choices:raise ValueError('invalid or repeated machine option')
                choices[m]=d
            ops.append(choices)
        if k!=len(row):raise ValueError(f'job {j} has extra tokens')
        jobs.append(ops)
    return {'machines':n_machines,'jobs':jobs}


def validate_schedule(instance,schedule,downtimes=(),fixed=None):
    """Return list of violations. Half-open intervals [start,end), zero-based j/o/m."""
    errors=[]; jobs=instance['jobs']; expected={(j,o) for j,ops in enumerate(jobs) for o in range(len(ops))}
    seen=set(); intervals=defaultdict(list); per_job=defaultdict(dict)
    for idx,s in enumerate(schedule):
        try:
            j,o,m,t0,t1=(s[k] for k in ('job','op','machine','start','end'))
        except (KeyError,TypeError): errors.append(f'malformed row {idx}');continue
        if not all(isinstance(v,int) and not isinstance(v,bool) for v in (j,o,m,t0,t1)):
            errors.append(f'non-integer field {idx}');continue
        key=(j,o)
        if key in seen:errors.append(f'duplicate operation {key}')
        seen.add(key)
        if key not in expected:errors.append(f'unknown operation {key}');continue
        if m not in jobs[j][o]: errors.append(f'ineligible machine {key}:{m}');continue
        if t0<0 or t1-t0 != jobs[j][o][m]:errors.append(f'duration/start violation {key}')
        intervals[m].append((t0,t1,key));per_job[j][o]=(t0,t1)
        for dm,ds,de in downtimes:
            if m==dm and t0<de and ds<t1:errors.append(f'downtime overlap {key}')
    missing=expected-seen
    if missing:errors.append(f'missing operations: {sorted(missing)}')
    for j,ops in enumerate(jobs):
        for o in range(1,len(ops)):
            if o in per_job[j] and o-1 in per_job[j] and per_job[j][o][0]<per_job[j][o-1][1]:
                errors.append(f'precedence violation {(j,o)}')
    for m,ivs in intervals.items():
        ordered=sorted(ivs)
        for (_,e,a),(s,_,b) in zip(ordered,ordered[1:]):
            if s<e:errors.append(f'machine overlap {m}: {a} vs {b}')
    if fixed:
        bykey={(s['job'],s['op']):s for s in schedule if isinstance(s,dict) and 'job' in s and 'op' in s}
        for key,original in fixed.items():
            if key not in bykey or any(bykey[key].get(field)!=original[field] for field in ('machine','start','end')):
                errors.append(f'frozen operation altered: {key}')
    return errors


def greedy(instance,downtimes=()):
    """Deterministic earliest-completion list scheduling; benchmark, not SOP."""
    jobs=instance['jobs']; current=[0]*len(jobs); ready=[0]*len(jobs); avail=[0]*instance['machines']; out=[]
    while any(current[j]<len(jobs[j]) for j in range(len(jobs))):
        proposals=[]
        for j,ops in enumerate(jobs):
            if current[j]>=len(ops):continue
            o=current[j]
            for m,d in ops[o].items():
                start=max(ready[j],avail[m]);end=start+d
                for dm,ds,de in sorted(downtimes,key=lambda x:x[1]):
                    if m==dm and start<de and ds<end:
                        start=de;end=start+d
                proposals.append((end,start,j,o,m))
        end,start,j,o,m=min(proposals)
        out.append({'job':j,'op':o,'machine':m,'start':start,'end':end})
        ready[j]=end;avail[m]=end;current[j]+=1
    return out


def makespan(schedule):return max(s['end'] for s in schedule)
