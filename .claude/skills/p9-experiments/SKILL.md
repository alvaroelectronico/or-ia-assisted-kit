---
name: p9-experiments
description: >
  Phase P9 of the combinatorial-problem methodology — Experimentation &
  comparison. Use after P6/P8, to run each technique SYSTEMATICALLY over a
  benchmark, log every run, and compare exact vs heuristic. Follows
  docs/methodology/README.md.
---

# P9 — Experimentation & comparison

Run the techniques systematically and compare them fairly. Every run is logged;
nothing is measured ad hoc.

## Inputs
- The P6 MILP implementation and P8 heuristic (registered as methods).
- The P2 generator (for reproducible benchmark instances via seeds/scales).
- The P3 solution checker (the compliance gate).
- The P4 visualizer (optional, to picture representative solutions).

## Templates
- `docs/methodology/templates/experiment-runner.template.py` — the harness.
- `docs/methodology/templates/experiment-protocol.template.md` — the battery doc.

## The harness (systematic, logged)
Implement `<problem>_model/experiments.py` from the runner template:
1. **Benchmark** — a deterministic `(stem → instance)` grid from the P2 generator
   (seed-first naming), so a partial battery still gives an early cross-size read.
2. **Method registry** — `name → callable(instance, config) -> (solution, status)`;
   register the MILP and each heuristic. **Experiment = `{label, method, config}`**;
   compose configs by dict-splat from shared bases; unique labels drive filenames,
   CSV rows and pairing.
3. **Sweep** — instances × experiments (× seeds). CLI filters for subsets.
4. **Compliance gate** — every solution is verified with the P3 checker; a
   non-compliant solution never counts as a result (record it infeasible).
5. **Dual persistence** — per run: one rich JSON (`outputs/solutions/<stem>__<label>__<ts>.json`,
   full solution + config + stamps) AND one appended row in the ledger
   `outputs/solutions/results.csv` (flat metrics for analysis).
6. **Per-battery log** — `outputs/logs/battery_<ts>.log` with the git commit, the
   env, and a summary + gap table.
7. **Reproducibility stamps** — per run capture: seed (in the stem/config), full
   config, objective, status, runtime, feasibility+violations, timestamp, git
   commit (+dirty), host and library versions (pyomo/solver).

## Comparison (fixed conventions)
- **Cache the MILP baseline**: don't re-run it while iterating on a heuristic;
  pair each heuristic run against the cached baseline by `(instance)`. Declare the
  cache stale if the MILP changes.
- **Gap** `= (MILP_obj − method_obj) / MILP_obj` (>0 ⇒ method beats the MILP
  objective, for our minimisation). ALWAYS cross-read the **absolute Δ** too —
  the relative gap blows up when the baseline ≈ 0.
- **Noise floor & honesty**: report run-to-run variance; a delta below it is noise,
  not an improvement. If the MILP is unconverged at scale, a heuristic "win" means
  "better feasible solution within the time limit", not proven superiority. If you
  cap the grid (time limits, subset), `log` exactly what was dropped.

## Protocol doc
Write `docs/<problem>/experiments.md` from the protocol template: benchmark
composition, methods/configs, the cached-baseline rule, the judging procedure
(gap → absolute Δ → compliance), caveats/noise floor.

## Reusable asset
- Refresh the experiment-runner + protocol templates on changes.

## Done when
- A results table compares the techniques across the benchmark, with gaps + Δ
  reported, coverage/noise disclosed, and every reported solution passing the P3
  checker; each run is in the ledger and has a JSON record.

## Governance
- Invoke `methodology-curator` to record P9 and refresh the templates.

## Next
- P10 reporting & synthesis (`p10-report`).
