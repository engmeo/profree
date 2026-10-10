"""Summarize paired dynamic B1/B2 experimental results without discarding failures.

Run from factorypulse_experiment_v1 root; uses standard library only.
"""
import argparse
import csv
import json
import statistics
from pathlib import Path

FIELDS = ['case_id', 'time', 'machine', 'duration', 'affects_plan',
          'B1_valid', 'B1_makespan', 'B1_wall_s', 'B2_status',
          'B2_valid', 'B2_makespan', 'B2_elapsed_s', 'B2_solver_wall_s',
          'B2_best_bound', 'B2_errors', 'B2_minus_B1']


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', default='results/b1_b2_36.json')
    p.add_argument('--csv', default='results/b1_b2_36_pairs.csv')
    p.add_argument('--summary', default='results/b1_b2_36_summary.json')
    a = p.parse_args()
    raw = json.loads(Path(a.input).read_text(encoding='utf-8'))
    cases = raw.get('cases', [])
    if not cases:
        raise RuntimeError('no cases; refusing misleading empty summary')
    rows = []
    for row in cases:
        b1 = row['B1']
        b2 = row.get('B2', {})
        errors = b2.get('validation_errors')
        b2_has_solution = b2.get('status') in ('OPTIMAL', 'FEASIBLE') and b2.get('makespan') is not None
        b2_valid = b2_has_solution and isinstance(errors, list) and len(errors) == 0
        ev = row['event']
        rows.append(dict(case_id=row['case_id'], time=ev['time'], machine=ev['machine'], duration=ev['duration'],
                         affects_plan=ev['affects_plan'], B1_valid=b1.get('valid'), B1_makespan=b1.get('makespan'),
                         B1_wall_s=b1.get('wall_s'), B2_status=b2.get('status', 'NOT_EXECUTED'),
                         B2_valid=b2_valid, B2_makespan=b2.get('makespan'),
                         B2_elapsed_s=b2.get('elapsed_s'), B2_solver_wall_s=b2.get('solver_wall_s'),
                         B2_best_bound=b2.get('best_bound'), B2_errors=json.dumps(errors, ensure_ascii=False),
                         B2_minus_B1=b2['makespan'] - b1['makespan'] if b2_valid and b1.get('valid') else None))
    Path(a.csv).parent.mkdir(parents=True, exist_ok=True)
    with Path(a.csv).open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    paired = [r for r in rows if r['B1_valid'] and r['B2_valid']]
    status_counts = {}
    for r in rows:
        status_counts[r['B2_status']] = status_counts.get(r['B2_status'], 0) + 1
    summary = {
        'scope': 'Synthetic disruption on public mk01 FJSP; not real DENSO data',
        'sample_size': len(rows), 'affected_plan_cases': sum(bool(r['affects_plan']) for r in rows),
        'b1_valid_cases': sum(bool(r['B1_valid']) for r in rows),
        'b2_valid_cases': sum(bool(r['B2_valid']) for r in rows),
        'b2_status_counts': status_counts, 'paired_valid_cases': len(paired),
        'b2_better_makespan': sum(r['B2_minus_B1'] < 0 for r in paired),
        'b2_equal_makespan': sum(r['B2_minus_B1'] == 0 for r in paired),
        'b2_worse_makespan': sum(r['B2_minus_B1'] > 0 for r in paired),
        'median_b1_makespan_paired': statistics.median([r['B1_makespan'] for r in paired]) if paired else None,
        'median_b2_makespan_paired': statistics.median([r['B2_makespan'] for r in paired]) if paired else None,
        'median_b2_elapsed_s': statistics.median([r['B2_elapsed_s'] for r in paired]) if paired else None,
        'notes': ['B2 objective is makespan only, not cash cost or factory OEE.',
                  'This is a B1-vs-B2 baseline, not evidence that FactoryPulse B3 outperforms B2.',
                  'Elapsed seconds depend on GitHub runner and must not be interpreted as plant response time.',
                  'B2 OPTIMAL is a proof within the implemented model and given scenario, not a proof of industrial validity.']
    }
    Path(a.summary).write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if any(not r['B1_valid'] for r in rows) or any(not r['B2_valid'] for r in rows):
        raise SystemExit('Some B1/B2 schedules not independently validated; inspect pair CSV and raw JSON')

if __name__ == '__main__':
    main()
