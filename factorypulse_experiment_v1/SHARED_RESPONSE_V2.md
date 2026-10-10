# FactoryPulse Research Extension V2 — B3 + BOM + QA

## Status and evidence boundary

Research **implementation**, not factory deployment. This overlay adds ONE CP-SAT model and ONE offline independent auditor for seven *predefined* event types on the public FJSP `mk01` input. G3/G4 originals are deliberately unchanged.

**Before merging:** local Python syntax compilation passed. Full local suite: 46 tests, 44 passed, 2 skipped because OR-Tools is not installed here. **CP-SAT benchmark results are NOT yet verified in this working environment**; GitHub Actions is configured to execute those and retain the raw artifacts. A green workflow and its case-level evidence are required before marking experimental validation DONE.

### Provenance

- FJSP: original public Brandimarte `mk01` already bundled in project; remains unchanged.
- QA defect *labels*: optional UCI [Steel Plates Faults, ID 198](https://archive.ics.uci.edu/dataset/198/steel+plates+faults) (CC BY 4.0; Buscema, Terzi and Tastle 2010). Workflow downloads the UCI archive and parses the seven original one-hot labels. Raw source bytes are SHA-256 identified in the case record. **These labels have no measured relationship to Brandimarte jobs.** Assigning a label to a job, hold length, rework duration and machine is synthetic policy.
- Materials: two synthetic materials, seeded BOM (seed 17), synthetic starting inventory and simulated delivery at t+10. No claim of measured BOM/warehouse observations.
- DENSO: no private line data, no field performance, no measured ROI. All units are abstract benchmark time units.

### Shared production state

C1/C2/B3 share: one immutable completed/running-work snapshot, one outage interval (only when scenario names machine failure), one FJSP machine/precedence model, identical BOM with inbound deliveries and QA rework appended to a job as an actual operation. C1 is conservative same-machine, same-machine-order/no-advancement response; C2 minimizes makespan; B3 minimizes `1000*makespan + 200*reassignment_count + 1*absolute_start_shift` with frozen work respected. These weights are hardcoded/pre-registered before experiment. **Machine-order inversion count is recorded as a result, not directly penalized by B3**. Thus B3 is NOT a claim of Pareto/global superiority to every baseline.

Seven cases: `machine`, `material`, `qa`, `machine_material`, `machine_qa`, `material_qa`, `all`. Every case solves C1/C2/B3 with the exact same state. Seed 11, one worker, configurable 10 seconds per solve; `OPTIMAL`, `FEASIBLE`, `UNKNOWN`, `INFEASIBLE` all preserved and counted. Cases that timeout are not silently discarded.

### Reproduction (Linux CI; local Python 3.11 + OR-Tools)

```bash
cd factorypulse_experiment_v1
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python fetch_qa_public.py --out data/steel_plates_faults_uci198.zip
python run_response_v2.py --data data/mk01.txt --out results/shared_response_v2.json --timeout 10 --qa-data data/steel_plates_faults_uci198.zip
python audit_response_v2.py --raw results/shared_response_v2.json --data data/mk01.txt
```

Offline synthetic-label fallback (not equivalent to public-label test):

```bash
python run_response_v2.py --data data/mk01.txt --out results/shared_response_v2_synthetic.json --timeout 10
python audit_response_v2.py --raw results/shared_response_v2_synthetic.json --data data/mk01.txt
```

Case-level complete schedules and solver statuses: `results/shared_response_v2.json`; flat per-arm records: `results/shared_response_v2.csv`. CI workflow at repo root `.github/workflows/factorypulse-response-v2.yml`. Independent auditor uses the original job and event data; recomputes feasibility, stock ledgers, QA hold and all aggregate changes from schedules, not stored validation flags.

### What remains outside experimental scope

- Original G4 36-event benchmark is not re-run with B3 in this phase; seven predeclared combination cases are a smoke/pilot comparison, insufficient to claim statistical generalization.
- Real-world QA hold/rework policy, scrap/rework yield, actual BOM, costs and DENSO benefits require industrial data or a field trial.
- No classifier is trained: **public fault labels drive predefined QA events, not predictions**, and there is no ground-truth linkage between defect type and repair duration.
- No demonstrated 'minimum editing' proof for C1. C1 is conservative policy with min-makespan scheduling under same machine and order; not a global optimal minimal-edit theorem.
