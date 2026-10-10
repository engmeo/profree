# G4 Extended experiment protocol — preregistered implementation, 2026-10-10

## Research question
How much improvement stems from choosing an optimized production schedule versus reacting to a downtime event? This is a **synthetic scheduling sensitivity analysis**, not causal evidence from DENSO production.

## Scenarios and methods
- Source: public Brandimarte FJSP mk01, mk02, mk03. `mk01` is in repository. mk02/mk03 are obtained from `SchedulingLab/fjsp-instances/brandimarte/` only after SHA-1 Git blob verification. SHA-256 of actual bytes is stored in outputs.
- Origin schedules: **H** = deterministic greedy (`C0H`); **O** = globally optimized baseline (`C0O`) if solved and independently validated. If O is `FEASIBLE` only, call it a *bounded incumbent*, not proven optimal. If absent, preserve `NO_SOLUTION` rows rather than deleting that arm.
- Within each origin, `C1` applies deterministic minimal-delay repair without changing machine assignment or baseline machine order, and `C2` solves CP-SAT rescheduling globally with immutable completed and unaffected-running work.
- Downtime event coordinates: generated from **heuristic** schedule at fractions `.25,.50,.75` and machine indices in ascending order, durations `5,15`. **Same `(t,m,d)`** is applied to H and O, but `affects_plan` is recalculated per-origin; do not assume both origins have identical state at `t`.
- Test sizes: mk01 all 36 events, mk02 and mk03 first 6 events each (deterministic prefix, explicitly chosen ex ante, not a representative random sample). Each event creates two origin arms.
- Fixed settings: seed 11, single solver worker, 10 s per CP-SAT solve including build, and 10 s for each no-event optimized origin. GitHub ubuntu-latest, Python 3.11, requirements.txt. Times from different invocations are observational and not plant-wide response times.
- Solver status: OPTIMAL means proved optimum for the model; FEASIBLE means feasible incumbent only; UNKNOWN means no usable solution proved/found; INFEASIBLE means model infeasible; MODEL_INVALID and EXECUTION_ERROR are recorded separately. A solver result is never accepted without an independent schedule validator.
- State convention: all times discrete/half-open. Finished operations frozen. In-progress work on other machines frozen. In-progress work on failed machine is discarded and restarted from zero. No job preemption, lot materials, QA, or delivery date modeling.

## Metrics and interpretation
For each origin independently: `L_event=M(C1)-M(C0)` and `G_response=M(C1)-M(C2)`. Recovery ratio is only defined if `L_event>0`. A gain may contain generic reoptimization. The H vs O baseline comparison specifically exposes that confounding; **not an additive causal decomposition**. Negative results/timeouts/invalid schedules remain visible. No claim B3 beats B2.

## Acceptance
Tests + all cases + cross JSON/CSV/summary audit; CI artifact only verified after actual GitHub Actions run. A green workflow is not proof of factory benefits. Scalability conclusions require examining solver statuses, feasibility and runtime per instance rather than cherry-picked medians.
