# FactoryPulse AI / AMR — Verified evidence and limits

## Context

This document distinguishes a **simulation/software acceptance** from a **physical robotic safety assessment**. The latter requires hardware, actual control stack, risk assessment and site approval; no number of Python unit tests can establish physical-plant safety.

## What has actually run

- Existing core CP-SAT and official resilience experiments are unmodified by this overlay.
- GitHub CI `FactoryPulse Fleet Material CP-SAT Integration` on branch `feature/amr-cpsat-integration`, commit `fc587ca`: PASS (https://github.com/engmeo/profree/actions/runs/38196780909). The merged main run also succeeded: https://github.com/engmeo/profree/actions/runs/38197041259.
- B1-B2 and G4 on merged main `4932606` also PASS. The research AI CI has succeeded on earlier branch / merged revisions; inspect newest Actions if reviewing later.
- New `fleet_safety_lab.py` and `test_fleet_safety_lab.py`: **6/6 local Python standard-library tests PASS**. Newly authored GitHub workflow requires a push to run in CI; do not cite CI PASS for this module until then.

## Risk classifier: actual limits, not marketing

Training example: baseline schedule and pre-decision machine / QA / material / due-date fields. Label: valid paired LOCAL vs C2 comparison where LOCAL focal job ends earlier but raises global weighted tardiness. Invalid/nonpaired runs are excluded, not counted as negatives.

The reference artifact in `evidence/ai_risk_exploratory_reference.json` was previously derived from 54 cases across mk01/02/03, with 46 paired valid and 16 positives, and is **a reference copy, not a freshly generated CI artifact**. Leave-one-instance-out pooled scores: Dummy PR-AUC 0.3323, Logistic 0.4603 (10/16 positive cases missed), Random Forest 0.2596 (14/16 missed). These cannot support autonomous decisions. Small-sample exploratory model only; thresholds not tuned/deployed. No DENSO observations.

Reproduce from current CI workflow `factorypulse-ai-swarm-research.yml`; inspect uploaded artifact, input manifest/hashes, and the `risk.py` implementation. Model training is research-only.

## Integration boundary

`ai_swarm/integration.py` uses synthetic fleet ETA -> material ledger -> production `solve_shared` CP-SAT -> independent `audit_shared`; it is a controlled one-delivery experiment. The job-shop input is deliberately tiny and data are synthetic. It does **not** prove 20 simultaneous mobile agents can safely feed production in realistic conditions.

## Fleet safety boundary

New bounded test introduces conservative discrete-grid synchronous movement. 20 simulated agents occupy distinct cells. Assertions reject duplicate initial positions, collisions, invalid obstacle occupancy and head-on swapping. Failure stops robot movement. The simulator returns `STALLED_REQUIRES_REPLAN` when progress is impossible, rather than claiming deadlock resolved. This is not continuous-time geometry, true A* multi-agent route planning, collision avoidance at speed, localization, braking, fail-safe controls, human detection, physical validation, or certification.

**Do not connect this algorithm to physical robots.** Required before hardware: site-specific hazard identification, safety PLC/interlocks, vendor-certified AMR controllers, pedestrian zones, E-stop, fail-safe communications, localization tests, speed/stop distance tests, interoperability tests, and signed acceptance by qualified engineering personnel under applicable local standards.

## Acceptance matrix

| Item | Status | Proof |
|---|---|---|
| Official CP-SAT experiment and audits | CI passed on previous and merged main | GitHub Actions official workflows |
| AMR ETA -> material -> CP-SAT -> audit, one task | CI passed | Main integration workflow |
| AI risk baseline/model on holdout instances | Exploratory results | `risk.py` + referenced JSON + CI artifacts |
| Bounded-grid multi-agent no same-cell occupancy | Local 6/6 tests | `test_fleet_safety_lab.py` |
| General collision-free 20 AMR with traffic/deadlock recovery | NOT VERIFIED | Needs real multi-agent planner and continuous safety simulation |
| Physical factory robot safety or DENSO ROI | NOT VERIFIED | Requires onsite systems, data and qualified acceptance |

**Pitch-safe statement:** FactoryPulse has verified the trace from one simulated AMR disruption to a material arrival constraint and audited CP-SAT rescheduling. Risk ML and multi-robot coordination remain experimental. Physical safety and performance have not been demonstrated.
