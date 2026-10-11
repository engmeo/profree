# FactoryPulse — Digital Factory 2D demonstration

## What is implemented

Interactive four-stage visualization of **ERP / WMS / MES / TMS** plus QA release gate. Three scenarios share exactly the existing `src/worlds.mjs` fixtures and `src/core.mjs` `evaluate`, `eligible`, and `decide` functions. User can play/pause/scrub simulation, select scenario, select alternative action, revoke approvals, mark data stale, inspect ETA and export JSON evidence. All numeric outcomes are computed by the engine, not hard-coded in the visual layer.

**Scope:** This is a synthetic 2D presentation of already existing rule-based production-flow simulation, **not** an integrated real DENSO factory, not a learned predictive maintenance model, not true Neo4j, not a discrete-event telemetry stream. Animation time is a storytelling cursor; it is not the scheduler's real physical timestamp and must never be conflated with solver results. Four stages use synthetic linked operational attributes, not live ERP/WMS/MES/TMS connectors. `QA` is the stage-gate inside the process.

## Run (from repo root)

```powershell
py -m http.server 8000
```

Open http://localhost:8000/digital_factory.html — use a local HTTP server because module imports don't reliably work from `file:///` URLs.

## Test

```bash
npm test
```

## Suggested video capture

1. Start machine scenario. Click **Chạy mô phỏng**. Show machine STOPPED and affected dependency nodes.
2. Read order-level ETA and late minutes.
3. Select repair or reroute; show how the engine recomputes ETA and score.
4. Uncheck authorized backup; show disallowed action. Uncheck fresh data; show VERIFY.
5. Switch to material and quality scenarios and repeat. Capture JSON export.

## Files to add (no existing files overwritten)

- `digital_factory.html` at repo root
- `src/digital_factory.css`
- `src/digital_factory.mjs`
- `tests/digital_factory.test.mjs`
- `DIGITAL_FACTORY_README.md`

The existing G3, G4, B3, QA and materials research is not changed or merged with this separate illustrative web demo.
