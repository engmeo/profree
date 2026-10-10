"""UCI 198 Steel Plates Faults: preserve source labels; synthetic scheduling mapping.

UCI labels describe steel defects, NOT FJSP jobs or DENSO lot outcomes.
"""
import hashlib, io, zipfile
from pathlib import Path
from urllib.request import urlopen
LABELS=['Pastry','Z_Scratch','K_Scratch','Stains','Dirtiness','Bumps','Other_Faults']
URL='https://archive.ics.uci.edu/static/public/198/steel+plates+faults.zip'

def parse_faults_nna(content):
    labels=[]
    for rowno,line in enumerate(content.splitlines(),1):
        fields=line.strip().replace(',',' ').split()
        if not fields:continue
        if len(fields)!=34:raise ValueError(f'bad Steel Plates row {rowno}: {len(fields)} columns')
        try:flags=[float(v) for v in fields[-7:]]
        except ValueError as exc:raise ValueError(f'bad label fields row {rowno}') from exc
        marked=[LABELS[i] for i,v in enumerate(flags) if v==1]
        if len(marked)!=1 or any(v not in (0,1) for v in flags):raise ValueError(f'bad one-hot labels row {rowno}')
        labels.append(marked[0])
    if not labels:raise ValueError('empty QA data')
    return labels

def read_archive(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        candidates=[x for x in z.namelist() if x.lower().endswith('faults.nna')]
        if len(candidates)!=1:raise ValueError('expected exactly one Faults.NNA')
        labels=parse_faults_nna(z.read(candidates[0]).decode('utf8'))
    return labels

def fetch_archive(destination,timeout=30):
    target=Path(destination);target.parent.mkdir(parents=True,exist_ok=True)
    with urlopen(URL,timeout=timeout) as r:data=r.read()
    labels=read_archive(data)
    target.write_bytes(data)
    return {'sha256':hashlib.sha256(data).hexdigest(),'records':len(labels),'source_url':URL}

def qa_from_labels(labels,instance,base,seed=17,source_sha256=None):
    if not labels:raise ValueError('labels missing')
    j=seed%len(instance['jobs']);label=labels[seed%len(labels)]
    # Simulation policy is independent from actual UCI annotations.
    m=sorted(instance['jobs'][j][-1])[0]
    prev=max(s['end'] for s in base if s['job']==j)
    policy={'Pastry':(3,4),'Z_Scratch':(4,6),'K_Scratch':(4,6),
            'Stains':(2,3),'Dirtiness':(2,3),'Bumps':(3,5),'Other_Faults':(4,6)}
    wait,rework=policy[label]
    return {'defects':[dict(job=j,machine=m,duration=rework,hold_until=prev+wait,
                    label=label,source='UCI_198_REAL_LABEL_SIMULATED_POLICY')],
            'label_source_sha256':source_sha256,'label_index':seed%len(labels)}
