"""Independent record validation for bounded CP-SAT baseline results."""
def solver_gap(status, objective, bound):
    if status not in ('OPTIMAL','FEASIBLE') or objective is None or bound is None:
        return None
    if objective < bound-1e-6:
        raise ValueError('minimization objective below solver lower bound')
    return max(0.0,(objective-bound)/max(1.0,abs(objective)))

def classify_solver_status(record):
    st=record.get('status')
    if st in ('OPTIMAL','FEASIBLE') and record.get('validation_errors') == [] and record.get('makespan') is not None:
        return 'VALID_SOLUTION'
    if st in ('OPTIMAL','FEASIBLE'):return 'INVALID_SOLUTION'
    if st in ('INFEASIBLE','UNKNOWN','MODEL_INVALID'):return st
    if st == 'EXECUTION_ERROR':return 'EXECUTION_ERROR'
    return 'UNRECOGNIZED_STATUS'
