# FactoryPulse response robustness benchmark — registered protocol 1.0

**Registration point:** this document and `run_response_matrix.py` must be committed together **before** evaluating the matrix artifact. This is a preregistered simulation benchmark, **not a DENSO plant trial**. Do not edit the frozen G3/G4/v2 artifacts.

## Design

- Public immutable FJSP: `mk01`, `mk02`, `mk03`; `fetch_public_instances.py` verifies upstream git blob checksums for the two larger instances.
- Event generation seeds: **42, 123, 456, 789, 2026**. The seed is used for scenario realization, BOM quantities and solver initialization. Public instance content is never modified.
- Seven event types: `machine`, `material`, `qa`, `machine_material`, `machine_qa`, `material_qa`, `all`.
- For each `(instance, seed, event)`, **C1**, **C2**, **B3-M**, **B3-B**, **B3-S** share the identical original greedy plan, snapshot, material ledger, QA events and scenario SHA-256.
- **105 scenarios, 525 method arms**. Unsolved arms remain included and are reported as `INFEASIBLE`, `UNKNOWN` or `ERROR`; never omit them.
- CP-SAT per-arm wall-time limit **2 s**, **one worker**, solver random seed equal to scenario seed. The tool versions are resolved from `requirements.txt`; CI uses Python 3.11 and records versions in installation log.

## Fixed objective weights (raw units)

The order is `(makespan, machine reassignments, sum absolute start-time shifts)`:

| Variant | Weights |
|---|---|
| B3-M | (100000, 10, 1) |
| B3-B | (1000, 200, 1) |
| B3-S | (100, 1000, 10) |

These are *candidate sensitivity conditions*, not proof of lexicographic priority. Different term ranges can dominate weight names; interpret actual tradeoffs from outcomes. C1/C2 remain the incumbent policies, unchanged. The order-inversion metric is **reported**, not optimized directly.

## Data provenance

- Scheduling: Brandimarte public FJSP.
- QA classification labels: UCI Steel Plates Faults, downloaded by the existing `fetch_qa_public.py`; provenance stored with SHA-256 of downloaded archive. Conversion from defect labels to QA hold/rework is **synthetic policy**, not an observed repair timeline.
- BOM, initial inventory, replenishment time and machine downtime: deterministic **synthetic**, derived from seed. No manufacturing observations or DENSO data are claimed.

## Validity and interpretation

The independent validator replays the emitted full schedules, original job precedence, machine exclusion, frozen state, material ledger, QA hold/rework, makespan, reassignments, shift and order inversions; recomputes CSV consistency and source SHA. Its passing does not prove optimizer optimality, nor rule out all bugs shared with the data/model assumptions. `OPTIMAL` is conditional on the encoded model; `FEASIBLE` is a valid schedule with no certificate of optimality; `UNKNOWN` cannot be recoded as infeasible.

`diagnose_infeasible_matrix.py` reports provable **total** material deficits separately from other unknown causes. When supply suffices in aggregate, reason is `UNDETERMINED`, not falsely attributed to QA or machinery. Root-cause proof for these cases requires controlled model relaxation or solver unsat-core analysis not yet present. The two historically infeasible v2 cases are not automatically explained by this new matrix.

## Predeclared questions and success criteria

- Feasibility: status counts per arm / all assigned arms, with no silent exclusions.
- Paired makespan and schedule stability (`reassigned`, `start_shift`, `machine_order_inversions`) for each B3 variant vs C2 and C1.
- Timing: solver wall clock (`wall_s`) and full Python elapsed (`elapsed_s`) reported separately.
- Report per instance, scenario type, seed, and variant with wins/ties/losses and explicit denominator (paired **feasible** cases). Report non-solution count over **all** expected pairs.
- Do not promote any B3 variant as universally best based on a small sample or post-hoc weight tuning.

## Reproduction (from `factorypulse_experiment_v1`)

```bash
python -m pip install -r requirements.txt
python fetch_public_instances.py --names mk02 mk03
python fetch_qa_public.py --out data/steel_plates_faults_uci198.zip
python -m unittest discover -s tests -v
python run_response_matrix.py --data data/mk01.txt data/mk02.txt data/mk03.txt --qa-data data/steel_plates_faults_uci198.zip --out-dir results/response_matrix --timeout 2
python audit_response_matrix.py --dir results/response_matrix --data data/mk01.txt data/mk02.txt data/mk03.txt
python diagnose_infeasible_matrix.py --raw results/response_matrix/response_matrix.json --out results/response_matrix/diagnostics.json
```

Outputs: `response_matrix.json`, `response_matrix.csv`, `summary.json`, `manifest.json`, `diagnostics.json`, CI test/benchmark/audit logs. **The full 525-arm run has not been executed or confirmed at the time of authoring this patch.**
