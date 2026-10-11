"""Idempotent conservative patch: add LOCAL as objective in EXISTING CP-SAT solver."""
from pathlib import Path
import argparse

def patch(content):
    changes = [
        ("def solve_shared(state, original, *, material=None, qa=None, mode='B3', weights=(1000,200,1), timeout=10, seed=11):",
         "def solve_shared(state, original, *, material=None, qa=None, mode='B3', weights=(1000,200,1), timeout=10, seed=11, local_focus_job=None):"),
        ("if mode not in ('B3','C2','C1'):raise ValueError('unknown solver mode')",
         "if mode not in ('B3','C2','C1','LOCAL'):raise ValueError('unknown solver mode')\n    if mode=='LOCAL' and (not isinstance(local_focus_job,int) or not 0<=local_focus_job<len(state['instance']['jobs'])):raise ValueError('invalid local focus job')"),
        ("if mode=='C2':model.Minimize(max_end)",
         "if mode=='LOCAL':\n        # Lexicographic: minimize completion of focal job first; whole-shop makespan second.\n        # Same feasible set as C2/B3, with all machine/material/QA/immutable constraints.\n        model.Minimize((upper+1)*ends[local_focus_job,len(jobs[local_focus_job])-1]+max_end)\n    elif mode=='C2':model.Minimize(max_end)"),
    ]
    for old,new in changes:
        if new in content:continue
        if content.count(old)!=1:raise ValueError('source version mismatch: '+old[:70])
        content=content.replace(old,new,1)
    return content

def main():
    p=argparse.ArgumentParser();p.add_argument('--path',default=None);p.add_argument('--check',action='store_true');a=p.parse_args()
    source=Path(a.path) if a.path else Path(__file__).resolve().parents[1]/'src'/'response_v2.py'
    text=source.read_text('utf-8');new=patch(text)
    if a.check:
        print('PATCH_REQUIRED' if text!=new else 'PATCH_APPLIED');return
    if new!=text:
        (source.with_suffix('.py.pre_official_lab.bak')).write_text(text,encoding='utf-8')
        source.write_text(new,encoding='utf-8')
    print('OFFICIAL_LOCAL_MODE_READY', source)
if __name__=='__main__':main()
