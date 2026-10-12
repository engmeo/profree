# FactoryPulse — Cooperative MAPF research evidence

## Problem addressed

The previous grid demonstrator greedily reduced Manhattan distance, never letting a robot take a temporary detour. The independently audited 100-seed stress study reported **100/100 `STALLED_REQUIRES_REPLAN`**. Collision avoidance alone was insufficient for task progress.

## Proposed isolated experimental module

`ai_swarm/cooperative_fleet.py` implements prioritized **space-time A\*** with explicit wait moves, cell and edge reservations, persistent goal occupancy, immobile failed robots, and up to 64 deterministic priority-order retries. It does **not** replace the current original fleet simulator, and its output is not automatically fed into production `solve_shared`. No plant deployment is claimed.

## Fixed-seed local reference

On 100 deterministic scenarios, 20 agents/case (19 healthy + one disabled), 12×8 grid, eight cells blocked, 100-tick planning horizon:

| Outcome | Old greedy lab | Cooperative priority retry |
|---|---:|---:|
| Fully completed scenarios | 0/100 | **95/100** |
| Incomplete / stalled scenarios | 100/100 | **5/100** |
| Audited safety violations in returned completed schedules | 0 | **0** |

The five unsolved seeds: `4, 38, 45, 56, 67`. These are **not automatically evidence of physical deadlocks**. Prioritized planners are incomplete: a different ordering or a complete MAPF algorithm might solve those instances. The objective is **complete mission progress without collisions**, not just movement at one tick.

Reproduce with:

```bash
cd factorypulse_experiment_v1
python -m unittest discover -s tests -p test_cooperative_fleet.py -v
python -m ai_swarm.cooperative_stress --seeds 100 --out results/cooperative_mapf/stress.json
```

## CI acceptance criteria

- 100 fixed seeds and 20 robots/case; at least 90% mission completion.
- Zero independently audited vertex collisions, edge swaps, illegal jumps or obstacle occupancy in **completed** schedules.
- Immobile failure remains immobile for the full trajectory.
- Unsolved instances must be reported as unsolved; never claim universal deadlock resolution.
- A separate workload, randomized maps/goal correlations and more difficult bottlenecks should be used for external validation; passing the same fixed seeds is not generalization.

## Not established

Physical AMR collision safety, real-time replanning under sensor delays, dynamic traffic, human safety, battery management, hardware control, real DENSO ROI, universal MAPF completeness/optimality and integrated 20-robot CP-SAT material delivery are **not validated**. This remains a discrete-grid scheduling research prototype.
