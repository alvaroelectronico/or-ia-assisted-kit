<!--
PROBLEM-AGNOSTIC TEMPLATE — phase P9 experiment protocol (battery style).
Fill every <PLACEHOLDER>, delete the guidance comments and this banner.
This is the companion doc to the experiment-runner template: it states HOW the
battery is run and, crucially, HOW results are judged, so comparisons are fair
and reproducible rather than ad hoc. Lives at `docs/<problem>/experiments.md`.
-->

# Experiments — <PROBLEM NAME> (phase P9)

Protocol for running <METHODS: the exact/reference method and the heuristics>
**systematically** and comparing them. The harness is `<PACKAGE>/experiments.py`;
every run is logged (dual persistence: rich JSON + CSV ledger).

## How to run

```bash
python -m <PACKAGE>.experiments                 # full default battery
python -m <PACKAGE>.experiments <inst_substr>   # instance filter (substring on stem)
python -m <PACKAGE>.experiments "" <label>      # experiment filter (exact label)
```

## Benchmark

Deterministic `(stem → instance)` grid built from the P2 generator
(`instance_generator.generate_instance`, fixed seeds), seed-first so a partial
battery still gives an early cross-size read:

| stem | <SIZE DIM A> | <SIZE DIM B> | seed |
|------|--------------|--------------|------|
| `<stem_pattern>` | ... | ... | ... |

<!-- Keep the grid SMALL enough that the exact/reference method solves to
optimality — it is the baseline. Grow it (more sizes, more seeds) as heuristics
land, and LOG WHAT YOU DROP. -->

<!-- SIZE GUARD (document it explicitly). When the grid is grown into a scaling
study (many size types x K seeds), the exact/reference method stops being viable
past some size. Guard it OFF beyond a documented threshold (e.g. skip the exact
method when `<size proxy> > <THRESHOLD>`) so the battery stays tractable, and run
only the heuristics on the larger types. State the threshold and its rationale
here — a reader must know which types HAVE an exact baseline (and therefore a
gap) and which do not. Never let the guard silently drop the exact method. -->

## Methods

Registered in `experiments.py` (`METHODS`) and swept as `EXPERIMENTS`
(`{label, method, config}`, configs composed by dict-splat from shared bases):

- **`<BASELINE_LABEL>`** — the exact/reference method (e.g. the P6 MILP), the
  baseline everything is compared against.
- **heuristics (from P8)** — register as `METHODS["heuristic:<name>"]` and add an
  experiment row; each is paired against the cached baseline.

## Rules

- **Compliance gate.** Every solution is verified with the P3 checker
  (`<CHECKER>`, requirements `[RQ01]…[RQnn]`). A non-compliant solution is
  recorded infeasible and NEVER counts as a result (no objective, no gap).
- **Cached baseline.** The reference result is fixed reference data; don't re-run
  it while iterating on a heuristic — pair each heuristic run against the cached
  baseline by instance. If the reference model changes, refresh the cache.
- **Gap** `= (baseline_obj − method_obj) / baseline_obj`. Fix the sign meaning by
  the objective direction: for a **<MINIMISATION / MAXIMISATION>**, gap
  `<> 0` means the method BEATS the baseline objective. Always cross-read the
  **absolute Δ** (in <OBJECTIVE UNIT>) — the relative gap is unstable when the
  baseline is tiny.
- **Judging order.** (1) mean gap, (2) absolute Δ, (3) compliance. A heuristic
  only "wins" if it is checker-valid AND beats the baseline by more than the
  run-to-run noise.
- **Noise floor & honesty.** Report run-to-run variance for stochastic methods; a
  delta below it is noise, not an improvement. If the baseline is unconverged at
  scale, a heuristic "win" means "better feasible solution within the time
  limit", not proven superiority — say so.
- **Log what you drop.** If you cap the grid (time limits, subset of sizes/seeds),
  record exactly what was excluded and why — never silently truncate.
- **Aggregate reporting for a scaling study.** When the benchmark spans many size
  types (N size types x K seeds), report results **per type — mean $\pm$ sd over
  the K seeds** — NOT per individual instance (a per-instance table stops being
  readable at scale; keep it only for the small correctness benchmark). The
  means-per-type table carries: size descriptor, mean objective $\pm$ sd,
  **median AND max** runtime (median = robust central tendency, max = exposes
  worst-case variance — do not hide a spike behind the median), feasibility count
  (how many of K passed the P3 checker), and gap-vs-exact **only where the exact
  baseline exists** (dash where the size guard turned it off — see the Benchmark
  size-guard note). State explicitly which types have no exact baseline.

## Logs & outputs

- `<PACKAGE>/outputs/solutions/<stem>__<label>__<ts>.json` — one rich record per
  run (full solution + config + git/env stamps). *(typically gitignored)*
- `<PACKAGE>/outputs/solutions/results.csv` — the append-only ledger (flat
  metrics: objective, runtime, status, feasibility, violations, git, config).
  *(kept in git)*
- `<PACKAGE>/outputs/logs/battery_<ts>.log` — per-battery human log with the git
  commit, environment, summary table and gap table. *(typically gitignored)*

## Reproducibility

Each run stamps: seed (in the stem), full config, objective, status, runtime,
feasibility + violations, timestamp, git commit (`+dirty` if the working tree has
changes), host, and library versions (<KEY LIBS / SOLVER>). Requires
<RUNTIME DEPS> (see `<PACKAGE>/requirements.txt`; pin the solver to your license
major version if applicable).
