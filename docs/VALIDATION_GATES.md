# FactoryPulse: defensible evidence, limits and deployment gates

## What the software test can establish

- **AI:** supervised research classifiers trained on synthetic LOCAL-versus-C2 labels; held-out *instance* predictions only. PR-AUC, Brier, model-seed variation, alert-budget precision/recall, plus an exploratory instance-cluster bootstrap. These are **diagnostics**; three clusters do not establish external validity.
- **Simulation fleet:** bounded 12 x 8 grid, 20 agents per seed, randomized obstacles/goals, failed agent remains immobile, vertex and edge-swap invariants audited independently for 100 seeds. Report explicitly counts `STALLED_REQUIRES_REPLAN`; safety invariants do **not** imply progress or liveness.
- **Integration:** separate existing test traces *one* AMR delay through the material ledger into CP-SAT and validates the schedule; it is not a synchronized multi-robot factory controller.
- **KPI:** comparing synthetic arms can establish outcomes only **under the declared toy schedule/objective and simulated disturbances**, not a real factory reduction in cost, labor, time or emissions.

## Gates for any real-world claim (outside this repository's current evidence)

| Claim | Required external evidence | Status |
|---|---|---|
| AI dependable in operations | Anonymized historical production incidents; temporal/site holdout; label provenance by operators; pre-registered precision/recall alert budget; calibrated probabilities; monitoring and human override | NOT VERIFIED |
| AMRs safe among people and equipment | Certified controllers and protective systems, hazard analysis, site speed/separation measurements, emergency stop, communications-loss handling, pedestrian tests, qualified safety acceptance | NOT VERIFIED |
| 20 AMRs finish tasks without deadlock | Validated continuous-time multi-agent simulation and traffic control, conflict-free dispatch, adversarial workload/traffic studies, real hardware testing | NOT VERIFIED |
| Measured productivity or ROI at DENSO | Real ERP/MES/WMS timestamps, baseline SOP, prospective controlled/shadow comparison, business cost ledger, uncertainty intervals, independent sign-off | NOT VERIFIED |
| Root cause established | Process expert review, causal identification strategy or intervention evidence; graph path alone is *association/dependency* | NOT VERIFIED |

## Reproduction

On Ubuntu GitHub Actions, run `FactoryPulse Robust Evidence and Fleet Stress`. Review `factorypulse-robust-research-evidence` artifact for `risk_robust.json` (rows, fold/seed metrics and warnings) and `fleet_stress.json` (status counts and collision violations). Never describe this workflow as third-party safety certification.

## Research interpretation

High PR-AUC relative to a dummy classifier is **not** proof of acceptable false-negative cost. Declaring a threshold after looking at holdout outcomes is leakage. This evaluation reports preselected top-k budgets and does not deploy automated actions. Instance-level bootstrap based on only 3 clusters must not be treated as a reliable tight confidence interval. Any later enlargement of the dataset must document independently sourced instances and stable incident policy definitions.
