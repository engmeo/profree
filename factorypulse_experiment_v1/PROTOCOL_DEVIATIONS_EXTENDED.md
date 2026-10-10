# G4 Extended deviations from G4 original

- Prior G4 baseline code left unchanged, preserving evidence of run `38027115954`.
- Added **optimized-origin** pairing rather than reusing the heuristic origin in both arms. This is origin-state sensitivity and not field causal identification.
- Event set is pinned to heuristic schedule (time fractions .25/.50/.75; machine/duration loops), and same event triple is replayed on optimized origin. Each arm recomputes overlaps.
- Prefix 6 events on mk02/mk03 is a deterministic sample of convenience; not representative of all disruptions.
- 10-second CP-SAT bound including model build; OPTIMAL/FEASIBLE/UNKNOWN/INFEASIBLE remain distinct. Missing static optimum is never imputed as 40 or 0 on other instances.
- PyPI / internet unavailable in local container, preventing running OR-Tools and downloading larger instances here; CI result pending.
- Material shortages, QA lot quarantine, plant ERP/MES integration, financial savings, B3 not evaluated.
