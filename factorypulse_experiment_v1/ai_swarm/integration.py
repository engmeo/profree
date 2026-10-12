"""Auditable one-task heterogeneous fleet -> material ledger -> CP-SAT pilot.

Synthetic time units only. This is NOT robot control or collision-safe multi-fleet routing.
Uses production's existing solve_shared and audit_shared unmodified.
"""
from __future__ import annotations

from copy import deepcopy

from .fleet import scenario
from .bridge import apply_fleet_arrival


def run_integrated_pilot(*, timeout: float = 8.0, seed: int = 11):
    """Run paired baseline and failed-AMR material arrivals against identical job-shop.

    A tiny controlled instance isolates the material-dependency mechanism. The
    fleet arrival is a future replenishment; initial stock of MAT_A is zero.
    Raise on solver failure; do not silently present infeasibility as recovery.
    """
    try:
        from fjsp import greedy
        from response_v2 import scenario_state, solve_shared, audit_shared, material_violations
    except ImportError as exc:
        raise RuntimeError('Run from factorypulse_experiment_v1 with PYTHONPATH=src; install ortools') from exc

    inst = {'machines': 2, 'jobs': [[{0: 4}, {1: 3}], [{1: 5}]]}
    original = greedy(inst)
    state = scenario_state(inst, original, t=0, machine=0, duration=0, has_failure=False)
    task_sim = scenario()
    if task_sim['baseline']['status'] != 'ASSIGNED' or task_sim['recovery']['status'] != 'ASSIGNED':
        raise AssertionError('fleet could not supply paired arrivals')
    if task_sim['failed_robot'] == task_sim['recovery']['robot']:
        raise AssertionError('failed robot was assigned again')

    raw = {'initial': {'MAT_A': 0, 'MAT_B': 1}, 'deliveries': [],
           'bom': {'0:0': {'MAT_A': 1}, '0:1': {}, '1:0': {'MAT_B': 1}}}
    normal_gate = deepcopy(task_sim)
    normal_gate['material_gate']['earliest_arrival_after_failure'] = task_sim['baseline']['eta']
    baseline_material = apply_fleet_arrival(raw, normal_gate, quantity=1)
    recovery_material = apply_fleet_arrival(raw, task_sim, quantity=1)

    arms = {}
    for label, material in [('BASELINE', baseline_material), ('AMR_FAILURE', recovery_material)]:
        info, schedule = solve_shared(state, original, material=material, qa={}, mode='C2', timeout=timeout, seed=seed)
        if info['status'] not in ('OPTIMAL', 'FEASIBLE') or schedule is None:
            raise AssertionError(f'{label}: CP-SAT did not return feasible schedule: {info}')
        errors = audit_shared(state, original, schedule, material, {})
        errors += material_violations(schedule, material)
        if errors:
            raise AssertionError(f'{label}: audit failed: {errors}')
        # Explicit material gate: every MAT_A consuming operation starts only after its arrival.
        arrival = next(d['time'] for d in material['deliveries'] if d['material'] == 'MAT_A')
        consumers = [op for op in schedule if material['bom'].get(f"{op['job']}:{op['op']}", {}).get('MAT_A', 0)]
        if not consumers or any(op['start'] < arrival for op in consumers):
            raise AssertionError(f'{label}: material availability was not propagated into schedule')
        arms[label] = {'solver_status': info['status'], 'material_eta': arrival,
                       'makespan': max(op['end'] for op in schedule), 'schedule': schedule,
                       'independent_audit_errors': errors}
    return {'schema': 'FactoryPulse-AMR-Production-CPSAT-pilot-v1',
            'provenance': 'SYNTHETIC; tiny controlled job-shop; no DENSO data',
            'failed_robot': task_sim['failed_robot'],
            'replacement_robot': task_sim['recovery']['robot'],
            'baseline_fleet_eta': task_sim['baseline']['eta'],
            'failure_fleet_eta': task_sim['recovery']['eta'],
            'arms': arms,
            'limitations': ['Single transport task only; no multi-robot collision/deadlock proof',
                           'No AI prediction or automated physical control validated',
                           'A controlled integration test, not evidence of industrial ROI']}


if __name__ == '__main__':
    import json
    print(json.dumps(run_integrated_pilot(), indent=2))
