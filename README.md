# FactoryPulse â€” Traceable Incident Decision Support (D3)

**DENSO Factory Hacks 2026 Â· D3 Â· Data Utilization**

A lightweight, rule-based **synthetic experimental prototype** connecting order priorities/deadlines (ERP / Logic) with component stock (WMS), machine/processing state (MES / Manufacturing), quality-release approval (QA), and shipping ETA (TMS). Three incident families: machine downtime, shortage, quality hold.

**Critical disclosure:** No real DENSO data was supplied. All operational timings, intervention permissions, manual response times, order quantities, costs and savings are hypothetical. This is **NOT** a trained AI, a root-cause discovery system, a certified digital twin, a true SOP benchmark, nor demonstrated positive ROI at DENSO.

## Run immediately

```bash
# Python 3, modern browser, Node.js 18+ for reproducible tests
python3 -m http.server 8000
# open http://localhost:8000
npm test
npm run benchmark
```

No external runtime packages, model downloads, GPU or network APIs. CSS can fall back to system fonts when offline.

## Main demonstration

1. Select machine downtime, material shortage or QA hold.
2. Compare the same deterministic incident with two **identical optimization policies**. One has to retrieve cross-department data via a manual lookup delay; the other gets the integrated data at a feed-lag delay.
3. Adjust manual lookup and feed delay. Make the manual lookup faster to see **FactoryPulse lose**.
4. Change to stale data; the integrated policy refuses automatic recommendation and flags **VERIFY**.
5. Change to restricted approval/capacity; a backup or substitute cannot be selected when unauthorized or infeasible.
6. Inspect order ETA, decision time, model loss, and export the current trial JSON.

## Benchmark result (synthetic, hand-authored)

`npm run benchmark` executes **24 stress cases** (8 each for 3 incident types) and writes `evidence/trials.csv`, `evidence/trials.json`, `evidence/summary.json`.

- **5 cases** integrated policy lower modeled loss
- **14 cases** tie
- **2 cases** manual policy lower modeled loss
- **3 cases** integrated feed refused recommendation due to stale input (`VERIFY`)
- **0 invalid actions selected** under modeled hard constraints

Do **not** quote the above as measured DENSO factory performance or a statistically representative success rate. The benchmark uses team-authored worlds and an evaluator that shares the declared model with the policy; it is neither an independent empirical gold standard nor a realistic manual-SOP timing study. In fact, average integrated loss **exceeds** average manual loss across all 24 cases in this toy experiment because stale feeds are penalized. This adverse result is disclosed, not hidden.

## What is controlled (and what isn't)

- Same complete physical world, permissible actions, safety constraints and decision rule for both policies.
- Manipulated factor: *when reliable cross-department information becomes available*.
- Only **known injected events** are traced; the demo does not infer unknown root causes.
- Order lateness is calculated **once** at shipping ETA, not repeatedly at each dependency edge.
- Quality/re-routing authorization and resource limits are enforced before action ranking.
- A stale integrated feed outputs `VERIFY` and leaves the line unchanged until an operator intervenes (recovery workflow not yet implemented).
- Scenario families are hand-specified, not representative field samples. No independent simulator validation or measured operator times.

## Why pursue D3 at all?

The official [2026 D3 challenge](https://densohackathon.vn/theme) requests **production-chain data linkage**, **impact/cause propagation** and **department-specific recommendations** over at least three scenarios. We demonstrate a constrained subset: event-to-order dependency tracing, order-level impact estimates and department-specific *advisory* outputs. Causal diagnosis and operational ROI remain future hypotheses.

DENSO Manufacturing Vietnam has also publicly described a **Future Command Room** with consolidated factory data ([JMA, June 2026](https://imd.jma.or.jp/management/report/activity_report41.html)). We do not claim their current systems lack our capabilities. The pilot question is whether a constrained, auditable response-decision layer can add useful performance atop their current workflows.

## Proposed 12-week pilot â€” contingent, not promised results

| Weeks | Work | Gate |
|---|---|---|
| 1â€“2 | Select one cell, data owner, MES/ERP/WMS keys and approval rules | Stop if no meaningful linkage can be established |
| 3â€“5 | Replay historical incidents with observed outcomes and expert review | Stop if timestamps / data quality not adequate |
| 6â€“9 | Shadow-mode decision comparison with **actual** SOP data and uncertainty estimates | Stop if decisions unsafe or no demonstrated value |
| 10â€“12 | Optional controlled human-approved pilot, cost analysis and cross-line feasibility | Deploy only if quality, value and governance gates pass |

Metrics to collect: time-to-safe-decision, operator confirmation rate, eligible-action rate, missing data rate, order ETA error, manual effort, action cost, incident frequency and realized cost impact. **ROI cannot be computed credibly before these observations.**

## Repo organization

- `src/worlds.mjs`: clearly disclosed synthetic data and possible actions.
- `src/core.mjs`: queue/stock/QA-constrained schedule, decision policies, safety checks.
- `src/app.mjs`, `src/style.css`, `index.html`: interactive demo.
- `tests/core.test.mjs`: 17 automated verification tests.
- `scripts/benchmark.mjs`: auditable paired stress cases.
- `evidence/`: full trials and summary; includes negative outcomes.
- `docs/`: red-team, method and submission outline.

**License:** MIT. The official DENSO theme and template remain the organizers' intellectual property.


## AI / fleet research evidence and scope

FactoryPulse has a separate **experimental** AI risk study (not a deployment-ready trained AI controller), a synthetic heterogeneous fleet prototype, and a verified one-delivery AMR-material-CP-SAT integration test. Bounded 20-agent discrete-grid invariant checks are not evidence of physical AMR safety. [Evidence, reproduction and scope](factorypulse_experiment_v1/AI_SWARM_EVIDENCE_AND_LIMITS.md).
