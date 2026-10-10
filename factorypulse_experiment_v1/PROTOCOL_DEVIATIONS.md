# Protocol deviations & implementation notes

- **2026-10-10.** G2/G3 implementation before any B3/holdout evaluation. `run_experiment.py` enumerates all 3 × 6 × 2 = 36 machine downtime cases for mk01; it records which outages overlap the original schedule instead of quietly filtering those cases. The original v1.0 protocol called for unimpacted cases to be reported separately; they remain in the raw file for audit, and should be excluded from *affected-case* comparisons using the recorded flag, not dropped retroactively.
- B1 wall time is measured around the greedy repair function; B2 CP-SAT wrapper reports elapsed model-construction + solve and a separate solver wall time. Future benchmarking must also include common validation overhead consistently before B1–B2 conclusions are drawn.
- The original `validate_schedule` is independent of CP-SAT but `greedy_repair` calls `validate_after` defensively. The standalone test suite includes intentional mutated schedules. This does not prove complete bug freedom.
- **No B2 result available**: OR-Tools unavailable in this environment; package installation failed due DNS/network blocking. No synthetic B2 numbers.
- **No holdout touched** and no B3 implemented.
