# FactoryPulse Official Resilience Lab (P0–P3)

> **Experimental prototype, not a DENSO pilot.** Brandimarte FJSP scheduling data is public; materials, QA policies, priorities, due dates and disruption events are synthetic. No claimed industrial ROI.

## What is different from the prior Resilience Lab?

The previous `resilience_lab/` used an independent two-order JavaScript model. This package adds `factorypulse_experiment_v1/official_lab/` and runs **LOCAL/C1/C2/B3** using the actual CP-SAT constraint model in `src/response_v2.py`. Its LOCAL objective prioritizes completion of a predeclared job, with makespan as tie-break, while retaining the *same* machine, frozen work, material, QA and downtime constraints as C2/B3. The original G3/G4 and 525-arm experiments are not overwritten.

This package adds one narrowly scoped mode to `solve_shared`: `LOCAL` with `local_focus_job`. It is **not** a claim that a real factory department behaves in exactly this way. It tests the *model-defined local-first policy*.

- **P0**: paired LOCAL/C1/C2/B3 schedules; precommitted KPI test: `LOCAL.focus_completion < C2.focus_completion` **and** `LOCAL.weighted_tardiness > C2.weighted_tardiness`. Results are labelled negative if no case matches. Every arm, including `UNKNOWN`/`INFEASIBLE`/`ERROR`, stays in the artifact.
- **P1**: trace of explicit job precedence, resource order, BOM demand, QA release and order completion. Each graph edge carries a rule and evidence. BFS is cross-checked against a separate fixed-point transitive closure. Paths represent **dependency** and are not automatically causal effects.
- **P2**: multi-scenario stress experiments and *controlled relaxation* of machine, material and QA constraints. Only `INFEASIBLE` proves infeasibility of the encoded model. A relaxation that restores feasibility gives a sufficient intervention, **not** a minimal unsat core.
- **P3**: an interactive **Three.js/WebGL** industrial scene, robot arms, conveyors, procedural CNC enclosures, real CP-SAT results from a loopback HTTP server, live graph rule summary, JSON export. **Not photorealistic or validated against factory machines.** Needs internet for Three.js CDN.

## Put files into repo, safely

Copy **contents of `REPO_OVERLAY/`** into `C:\Users\tuant\profree`. Everything is additive **except** the explicit patch to `factorypulse_experiment_v1/src/response_v2.py` in step below. Do not copy any top-level sibling folder and do not delete `factorypulse_experiment_v1/src` or `tests`.

```powershell
cd C:\Users\tuant\profree
# Patch the official CP-SAT solver IN PLACE, with an automatic .bak backup.
py factorypulse_experiment_v1\official_lab\patch_official_solver.py
# Verify only expected changes
 git diff -- factorypulse_experiment_v1/src/response_v2.py
```

This patch is idempotent and **rejects an unexpected version**. If it reports `source version mismatch`, stop; do not force the edit.

## Requirements and tests

```powershell
cd C:\Users\tuant\profree
py -m pip install -r factorypulse_experiment_v1\requirements.txt
cd factorypulse_experiment_v1
py -m unittest discover -s tests -v
py official_lab\experiment.py --data data\mk01.txt --out results\official_lab --seeds 42 123 --limit 24 --timeout 3
py official_lab\audit.py --json results\official_lab\results.json --data data\mk01.txt
py official_lab\stress.py --data data\mk01.txt --out results\official_lab\stress.json --timeout 3
```

Expected evidence: `results/official_lab/results.json`, `manifest.json`, `summary.json`, `sha256.txt`, `stress.json`. Do not report an observed counterexample unless `summary.json` has `counterexamples > 0` and offline audit passes.

**Larger trial:** fetch `mk02`/`mk03` with existing `fetch_public_instances.py` then pass all 3 `--data` paths to the runner. Run time grows with `--limit` × 4 solver arms × `--timeout`; use CI for larger tests.

## Interactive 3D with official solver

From `factorypulse_experiment_v1`:

```powershell
py official_lab\server.py --port 8765
```

Open `http://127.0.0.1:8765/` in Chrome/Edge. **Do not** use plain `py -m http.server`; that cannot call Python CP-SAT. The `POST /api/run` endpoint is loopback-only, runs four methods for the same generated scenario and returns full schedules and graphs. Change seed/scenario/focal job and run again. The 3D geometry represents a *generic simulated* factory, not DENSO equipment. The machine state overlay depends on the selected event, and KPI/graphs are returned by Python, not hardcoded.

## GitHub Actions

Push `.github/workflows/factorypulse-official-resilience-lab.yml` together with the patched Python file and the new lab. The workflow runs real OR-Tools, asserts graph + schedule validity and uploads artifacts even on failure. **A green workflow is still not proof that a particular counterexample was found**; check summary and schedules.

```powershell
git add .github/workflows/factorypulse-official-resilience-lab.yml
git add factorypulse_experiment_v1/official_lab factorypulse_experiment_v1/tests/test_official_lab.py
git add factorypulse_experiment_v1/src/response_v2.py factorypulse_experiment_v1/OFFICIAL_RESILIENCE_LAB_README.md
git diff --cached --check
git diff --cached --name-only
```

Commit/push only after reviewing the diff. Do not use `git add .` while inspecting the research overlay.

## Evidence boundaries

1. **Official solver integration**: code uses the same constraint construction function; check via CI execution.
2. **Causal reasoning**: graph follows encoded constraints; causal claims require separate intervention/ground truth.
3. **Stress results**: perturbations are synthetic and bounded. Some runs can return UNKNOWN due to timeouts, NOT INFEASIBLE.
4. **3D**: WebGL real geometry and animation with no imported physical CAD model. Procedural rendering cannot be marketed as industrial photorealism.
5. **DENSO**: no factory data, ERP/MES integration or measured savings.
