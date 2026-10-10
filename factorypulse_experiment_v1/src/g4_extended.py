"""Pre-registered counterfactual experiment: optimal-origin and heuristic-origin.

This is a policy comparison, not identification of a causal effect on real factories.
A disrupted running operation on the failed machine restarts from zero.
Other in-progress/finished operations are immutable; half-open integer times.
"""
from collections import Counter
from fjsp import makespan, validate_schedule
from dynamic import disruption_state, validate_after
from g4_baselines import minimal_repair


def validate_counterfactual(instance, original, event, repaired):
    """Validator recomputes disruption state, does NOT trust solver status or flags."""
    bad_original = validate_schedule(instance, original)
    if bad_original:
        return [f'original schedule invalid: {bad_original}']
    state = disruption_state(instance, original, event['time'], event['machine'], event['duration'])
    return validate_after(state, repaired)


def policy_change_counts(original, revised, state):
    before = {(r['job'], r['op']): r for r in original}
    after = {(r['job'], r['op']): r for r in revised}
    future = [k for k in before if k not in state['fixed']]
    return {'future_operations':len(future),
            'machine_changes':sum(after[k]['machine'] != before[k]['machine'] for k in future),
            'start_changes':sum(after[k]['start'] != before[k]['start'] for k in future),
            'finished':sum(s == 'FINISHED' for s in state['states'].values()),
            'running_unaffected':sum(s == 'RUNNING_UNAFFECTED' for s in state['states'].values()),
            'running_failed_restart':sum(s == 'RUNNING_FAILED' for s in state['states'].values()),
            'not_started':sum(s == 'NOT_STARTED' for s in state['states'].values())}


def paired_metrics(m0, m1, m2):
    loss=m1-m0; gain=m1-m2
    return {'M_initial':m0,'M_minimal_repair':m1,'M_reschedule':m2,
            'event_loss':loss,'response_gain':gain,
            'recovery_ratio':gain/loss if loss>0 else None,
            'ratio_undefined_reason':'nonpositive_event_loss' if loss<=0 else None,
            'note':'Gain includes global reoptimization and cannot be attributed solely to event-response.'}


def independently_check_record(rec):
    """Reject missing data, false validity assertions, malformed solver statuses."""
    errors=[]
    if rec.get('solver',{}).get('status') not in ('OPTIMAL','FEASIBLE','INFEASIBLE','UNKNOWN','MODEL_INVALID','EXECUTION_ERROR'):
        errors.append('unknown solver status')
    if rec.get('status') == 'COMPLETE':
        if rec.get('validator_errors') != []: errors.append('complete case has validator violations')
        if rec.get('C2_makespan') is None: errors.append('complete case missing C2')
    if rec.get('status') not in ('COMPLETE','NO_SOLUTION','ERROR'):
        errors.append('unknown case status')
    return errors
