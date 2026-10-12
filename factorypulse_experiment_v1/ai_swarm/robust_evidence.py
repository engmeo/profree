"""Additional out-of-instance research evaluation; never a production decision gate.

A pre-registered top-k budget is evaluated on all held-out predictions.
No model selection or operating threshold is fitted on held-out labels.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path
import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from .risk import features, label_of

MODELS = ('dummy', 'logistic', 'forest')

def _model(name, seed):
    if name == 'dummy': return DummyClassifier(strategy='prior')
    if name == 'logistic': return make_pipeline(StandardScaler(), LogisticRegression(class_weight='balanced', max_iter=2000, random_state=seed))
    if name == 'forest': return RandomForestClassifier(n_estimators=120, max_depth=4, min_samples_leaf=3, class_weight='balanced', random_state=seed, n_jobs=1)
    raise ValueError(name)

def _topk(y, p, k):
    assert len(y) == len(p)
    order=sorted(range(len(y)),key=lambda i:(-float(p[i]),i))
    k=min(k,len(y));tp=sum(int(y[i]) for i in order[:k]); positives=sum(y)
    return {'budget':k,'true_positives':int(tp),'precision':float(tp/k) if k else None,
            'recall':float(tp/positives) if positives else None,
            'false_alarms':int(k-tp),'missed':int(positives-tp)}

def evaluate(document, seeds=(11,23,47,71,101), budgets=(3,5,10)):
    valid=[r for r in document['records'] if label_of(r) is not None]
    instances=sorted({r['instance'] for r in valid})
    if len(instances)<3: raise ValueError('at least three distinct instances required')
    rows=[]
    for seed in seeds:
        for holdout in instances:
            train=[r for r in valid if r['instance']!=holdout]
            test=[r for r in valid if r['instance']==holdout]
            y=np.asarray([label_of(r) for r in train],dtype=int)
            yt=np.asarray([label_of(r) for r in test],dtype=int)
            if len(set(y.tolist()))<2:raise ValueError('training fold only one class: '+holdout)
            X=np.asarray([features(r) for r in train]);Xt=np.asarray([features(r) for r in test])
            for name in MODELS:
                clf=_model(name,seed);clf.fit(X,y)
                probabilities=clf.predict_proba(Xt)[:,list(clf.classes_).index(1)]
                for idx,(record,truth,probability) in enumerate(zip(test,yt,probabilities)):
                    rows.append({'seed':int(seed),'holdout':holdout,'case_index_in_holdout':idx,
                                 'model':name,'label':int(truth),'probability':float(probability)})
    summary={}
    for name in MODELS:
        per_seed=[]
        for seed in seeds:
            group=[r for r in rows if r['model']==name and r['seed']==seed]
            yy=[r['label'] for r in group];pp=[r['probability'] for r in group]
            per_seed.append({'seed':int(seed),'pr_auc':float(average_precision_score(yy,pp)),
                             'brier':float(brier_score_loss(yy,pp)),
                             'budgets':{str(k):_topk(yy,pp,k) for k in budgets}})
        vals=[r['pr_auc'] for r in per_seed]
        summary[name]={'pr_auc_mean':float(np.mean(vals)),
                       'pr_auc_std_sample':float(np.std(vals,ddof=1)) if len(vals)>1 else None,
                       'per_seed':per_seed}
    # Transparent group uncertainty; bootstrap instances, never individual correlated records.
    # Only 3 clusters -> intervals are very unstable and are NOT confidence of generalization.
    bootstrap={}
    rng=np.random.default_rng(20261012)
    for name in MODELS:
        group=[r for r in rows if r['model']==name and r['seed']==seeds[0]]
        by_instance={inst:[r for r in group if r['holdout']==inst] for inst in instances}
        ap=[]
        for _ in range(500):
            sample=[r for inst in rng.choice(instances,len(instances),replace=True) for r in by_instance[inst]]
            if len(set(r['label'] for r in sample))<2:continue
            ap.append(float(average_precision_score([r['label'] for r in sample],[r['probability'] for r in sample])))
        bootstrap[name]={'resamples_with_both_classes':len(ap),
                         'exploratory_cluster_bootstrap_2_5_97_5_percentiles':list(map(float,np.percentile(ap,[2.5,97.5]))) if ap else None}
    return {'schema':'factorypulse-robust-risk-v1','data_source':'synthetic simulator outputs only',
            'positive_label':'LOCAL focus completion < C2 and LOCAL global weighted tardiness > C2',
            'observations':len(valid),'excluded':len(document['records'])-len(valid),
            'class_counts':dict(Counter(str(label_of(r)) for r in valid)),
            'distinct_instances':instances,'seed_values':list(seeds),'alert_budgets':list(budgets),
            'method':'Leave-one-instance-out; held-out labels used only for scoring. Top-k no threshold tuning.',
            'model_summary':summary,'cluster_bootstrap_seed':int(seeds[0]),
            'cluster_bootstrap_exploratory':bootstrap,'predictions':rows,
            'limitations':['3 clusters cannot validate industrial generalization or yield trustworthy tight confidence intervals',
                           'Changing seed is not new independently collected production data',
                           'Synthetic labels are not real incidents',
                           'Never use this output to authorize an automated factory action']}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--results',required=True);parser.add_argument('--out',required=True)
    args=parser.parse_args()
    report=evaluate(json.loads(Path(args.results).read_text(encoding='utf-8')))
    path=Path(args.out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print('ROBUST_EVIDENCE',json.dumps({k:report[k] for k in ('observations','excluded','class_counts','distinct_instances')}))
    for name,result in report['model_summary'].items():print(name,'AP mean',result['pr_auc_mean'],'std',result['pr_auc_std_sample'])

if __name__=='__main__':main()
