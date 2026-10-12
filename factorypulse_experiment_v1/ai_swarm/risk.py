"""Leakage-conscious AI warning experiment for FactoryPulse.

Inputs come ONLY from before each decision: original base schedule and incident/
material/QA/due/priority policy; NEVER selected-arm schedule, solver status or KPI.
LOIO validation = leave-one-INSTANCE-out. Tiny original 54-case study is exploratory.
"""
from __future__ import annotations
import argparse, json, math, hashlib
from collections import Counter
from pathlib import Path
import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

FEATURES = ('machine_failure','event_time','event_duration','material_shortage','material_delay',
            'qa_holds','qa_latest_hold','n_jobs','focus_index_fraction', 'due_focus_margin',
            'focus_weight','priority_mean','base_makespan','base_total_duration',
            'base_utilization_proxy','focus_base_completion', 'base_weighted_tardiness')


def features(rec):
    p=rec['input']; base=p['base']; focus=int(p['focus']); ev=p.get('event',{})
    due=p['due']; priority=p['priority']; material=p.get('material',{});qa=p.get('qa',{})
    jobs={int(s['job']) for s in base};end={j:max(s['end'] for s in base if s['job']==j) for j in jobs}
    machine_ids={s['machine'] for s in base}
    maxend=max(end.values()); duration=sum(s['end']-s['start'] for s in base)
    # Parse only policy payload. Does not inspect output of LOCAL, C1, C2, B3.
    shortages=material.get('shortages',[])
    # Delivery policy includes scheduled future inbound lots.
    deliveries=material.get('deliveries',[])
    delayed_inbound=sum(1 for x in deliveries if isinstance(x,dict) and x.get('time',0)>ev.get('time',0))
    if isinstance(shortages,dict): shortages=list(shortages.values())
    arrivals=material.get('arrivals',{})
    if isinstance(arrivals,dict): arrvals=list(arrivals.values())
    else: arrvals=[]
    delays=[float(v) for v in arrvals if isinstance(v,(int,float))]
    defects=qa.get('defects',[])
    d={
      'machine_failure':float(bool(ev.get('has_failure'))),
      'event_time':float(ev.get('time',0)),
      'event_duration':float(ev.get('duration',0)),
      'material_shortage':float(len(shortages)+delayed_inbound),
      'material_delay':float(max(delays,default=0)),
      'qa_holds':float(len(defects)),
      'qa_latest_hold':float(max((x.get('hold_until',0) for x in defects),default=0)),
      'n_jobs':float(len(jobs)),
      'focus_index_fraction':focus/max(1,len(jobs)-1),
      'due_focus_margin':float(due[str(focus)]-end[focus]),
      'focus_weight':float(priority[str(focus)]),
      'priority_mean':float(sum(priority[str(j)] for j in jobs)/len(jobs)),
      'base_makespan':float(maxend),
      'base_total_duration':float(duration),
      'base_utilization_proxy':float(duration/max(1,maxend*len(machine_ids))),
      'focus_base_completion':float(end[focus]),
      'base_weighted_tardiness':float(sum(priority[str(j)]*max(0,end[j]-due[str(j)]) for j in jobs))
    }
    return [d[k] for k in FEATURES]


def label_of(rec):
    # EXCLUDED_NONPAIRED is not a negative training example.
    good={'OPTIMAL','FEASIBLE'}
    if rec['arms']['LOCAL']['info']['status'] not in good or rec['arms']['C2']['info']['status'] not in good:
        return None
    L=rec['arms']['LOCAL']['kpi']; C=rec['arms']['C2']['kpi']
    return int(L['focus_completion'] < C['focus_completion'] and
               L['weighted_tardiness'] > C['weighted_tardiness'])


def grouped_evaluation(doc):
    recs=doc['records']; valid=[r for r in recs if label_of(r) is not None]
    excluded=len(recs)-len(valid);instances=sorted({r['instance'] for r in valid})
    if len(instances)<2: raise ValueError('need at least two held-out instances')
    allfolds=[];allpred={name:[] for name in ('dummy','logistic','forest')};alltrue=[]
    for instance in instances:
        train=[r for r in valid if r['instance']!=instance];test=[r for r in valid if r['instance']==instance]
        y=np.array([label_of(r) for r in train],dtype=int); yt=np.array([label_of(r) for r in test],dtype=int)
        if len(set(y))<2: raise ValueError('training fold lacks both classes: '+instance)
        x=np.array([features(r) for r in train]);xt=np.array([features(r) for r in test])
        models={
          'dummy':DummyClassifier(strategy='prior'),
          'logistic':make_pipeline(StandardScaler(),LogisticRegression(class_weight='balanced',max_iter=1000,random_state=2026)),
          'forest':RandomForestClassifier(n_estimators=120,max_depth=4,min_samples_leaf=3,class_weight='balanced',random_state=2026,n_jobs=1)
        }
        metrics={}
        for name,model in models.items():
            model.fit(x,y);prob=model.predict_proba(xt)[:,1]
            pred=(prob>=0.5).astype(int)
            allpred[name].extend(prob.tolist())
            metrics[name]={ 'pr_auc':float(average_precision_score(yt,prob)) if yt.any() else None,
              'precision_at_0_5':float(precision_score(yt,pred,zero_division=0)),
              'recall_at_0_5':float(recall_score(yt,pred,zero_division=0)),
              'f1_at_0_5':float(f1_score(yt,pred,zero_division=0)),
              'false_negatives':int(((yt==1)&(pred==0)).sum()), 'n':len(yt)}
        alltrue.extend(yt.tolist())
        allfolds.append({'holdout_instance':instance,'train_size':len(train),'test_size':len(test),
                         'train_positive':int(y.sum()),'test_positive':int(yt.sum()),'metrics':metrics})
    yall=np.array(alltrue)
    pooled={}
    for name,probs in allpred.items():
        pr=np.array(probs);pred=(pr>=0.5).astype(int)
        pooled[name]={'pr_auc':float(average_precision_score(yall,pr)),
                      'precision':float(precision_score(yall,pred,zero_division=0)),
                      'recall':float(recall_score(yall,pred,zero_division=0)),
                      'f1':float(f1_score(yall,pred,zero_division=0)),
                      'false_negatives':int(((yall==1)&(pred==0)).sum()),
                      'confusion_matrix':confusion_matrix(yall,pred,labels=[0,1]).tolist()}
    return {'status':'EXPLORATORY_SMALL_SAMPLE','provenance':doc.get('manifest',{}),
       'validation':'leave-one-instance-out; feature extraction excludes arm output',
       'valid_pairs':len(valid),'excluded_nonpaired':excluded,
       'positive':sum(label_of(r) for r in valid),'features':list(FEATURES),
       'folds':allfolds,'pooled_out_of_instance':pooled,
       'limitations':['54 predeclared cases are insufficient to claim deployment-ready predictive AI',
       'synthetic targets are simulator-specific, not observed DENSO outcomes',
       'Do not deploy automated decisions; shadow-mode validation and broader data needed']}


def main():
    p=argparse.ArgumentParser();p.add_argument('--results',required=True);p.add_argument('--out',required=True)
    a=p.parse_args();doc=json.loads(Path(a.results).read_text(encoding='utf-8'))
    report=grouped_evaluation(doc)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print('AI_RISK_EXPLORATORY',json.dumps({k:report[k] for k in ('valid_pairs','excluded_nonpaired','positive')}))
    for name,val in report['pooled_out_of_instance'].items():print('MODEL',name,val)
if __name__=='__main__':main()
