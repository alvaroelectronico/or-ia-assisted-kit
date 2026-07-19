"""Systematic experiment harness (phase P9) — PROBLEM-AGNOSTIC TEMPLATE.

Fill every <PLACEHOLDER> and delete this banner. This is the reusable scaffold
of a P9 experiment runner: it runs one or more METHODS over a deterministic
benchmark of instances, verifies every solution with the P3 checker (a hard
COMPLIANCE GATE), and persists each run TWICE (dual persistence) plus a
per-battery human log — all with reproducibility stamps.

Key patterns this template encodes (keep them; they are the point):
  * DUAL PERSISTENCE   — one rich JSON per run (full solution + config + stamps)
                         AND one appended row in a flat CSV ledger for analysis.
  * COMPLIANCE GATE    — every solution is run through the P3 checker; a
                         non-compliant solution is recorded infeasible and NEVER
                         counts as a result / never gets a gap.
  * CACHED BASELINE    — the exact/reference method (e.g. MILP) is the baseline;
                         cache it and pair heuristics against it. Don't re-run it
                         while iterating on a heuristic (refresh if it changes).
  * GAP CONVENTION     — gap = (baseline_obj - method_obj) / baseline_obj, fixed
                         once. Sign meaning depends on the objective direction:
                         for a MINIMISATION, gap > 0 means the method BEATS the
                         baseline objective. ALWAYS cross-read the absolute Δ too,
                         because the relative gap is unstable when baseline ≈ 0.
  * REPRODUCIBILITY    — per run stamp: seed (in the stem/config), full config,
                         objective, status, runtime, feasibility + violations,
                         timestamp, git commit (+dirty), host, library versions.

Naming: instances are keyed by a deterministic `stem` (seed-first, so a partial
battery still gives an early cross-size read). Experiments are keyed by a unique
`label` that drives filenames, CSV rows and baseline pairing.

Run:  python -m <package>.experiments [inst_filter] [exp_filter]
      python <package>/experiments.py            # runs the default battery
"""

from __future__ import annotations

import csv
import json
import os
import platform
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Allow running the file directly (not only as a module).
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# <PLACEHOLDER: imports> — the P2 generator, the P6 model / P8 heuristic(s) to
# register as methods, and the P3 checker used as the compliance gate.
from <PACKAGE> import <MODEL_MODULE>            # e.g. the MILP implementation (P6)
from <PACKAGE>.instance_generator import generate_instance  # P2 generator
from <PACKAGE>.solution_checker import <CHECKER>            # P3 checker class

# Outputs layout. Keep `solutions/` + `logs/` split; typically git-ignore the
# per-run JSON and battery logs and KEEP the CSV ledger under version control.
_OUT = Path(__file__).resolve().parent / "outputs"
_SOLUTIONS = _OUT / "solutions"
_LOGS = _OUT / "logs"
_LEDGER = _SOLUTIONS / "results.csv"
_CSV_COLUMNS = [
    "timestamp", "instance", "label", "method", "status", "objective",
    "runtime_s", "feasible", "violations", "git", "config",
]


# ---------------------------------------------------------------------
# Benchmark: deterministic (stem -> instance) grid from the P2 generator.
# Seed-first naming so a partial battery still gives an early cross-size read.
# Keep it SMALL enough that the exact/reference method solves to optimality (it
# is the baseline); grow it as heuristics land and LOG WHAT YOU DROP.
# ---------------------------------------------------------------------
def build_benchmark() -> list[tuple[str, dict]]:
    bench = []
    for seed in (<SEEDS>):                       # e.g. (1, 2, 3)
        for (<SIZE_A>, <SIZE_B>) in [<SIZE_GRID>]:  # e.g. [(2, 4), (3, 5)]
            stem = f"<STEM_PATTERN>"             # e.g. f"c{a}_s{b}_seed{seed}"
            inst = generate_instance(
                # <PLACEHOLDER: generator kwargs> — sizes/ranges as params, seed last.
                seed=seed,
            )
            bench.append((stem, inst))
    return bench


# ---------------------------------------------------------------------
# Method registry: name -> callable(instance, config) -> (solution_dict, status).
# The solution_dict MUST match the P3 solution schema. Register the reference
# method (baseline) and each heuristic. New methods (P8) just add a key here.
# ---------------------------------------------------------------------
def _solve_baseline(instance: dict, config: dict):
    # <PLACEHOLDER> — call the exact/reference solver (e.g. the P6 MILP). Return
    # (solution_dict, status). Read tuning knobs (time limit, gap, ...) from config.
    sol = <MODEL_MODULE>.solve_instance(
        instance,
        time_limit=config.get("time_limit", <DEFAULT_TIME_LIMIT>),
        # <PLACEHOLDER: other knobs, e.g. mip_gap>
    )
    status = sol.pop("_solver_status", "unknown")
    return sol, status


# Example heuristic method (from P8):
# def _solve_heuristic_ig(instance: dict, config: dict):
#     sol = <heuristic>(instance, iterations=config["iterations"], seed=config["seed"])
#     return sol, "heuristic"

METHODS = {
    "<BASELINE_METHOD>": _solve_baseline,   # e.g. "milp"
    # "heuristic:ig": _solve_heuristic_ig,
}


# ---------------------------------------------------------------------
# Experiment specs: one dict per named configuration. Compose configs by
# dict-splat from shared bases so tuning stays DRY. The `label` is UNIQUE and
# drives filenames, CSV rows and baseline pairing. The baseline experiment's
# label must equal `baseline_label` in compare().
# ---------------------------------------------------------------------
_BASE = {<SHARED_CONFIG_DEFAULTS>}           # e.g. {"time_limit": 60, "mip_gap": 0.0}
EXPERIMENTS = [
    {"label": "<BASELINE_LABEL>", "method": "<BASELINE_METHOD>", "config": {**_BASE}},
    # --- P8 heuristics register here, e.g. ---
    # {"label": "ig_v1", "method": "heuristic:ig",
    #  "config": {**_BASE, "iterations": 200, "seed": 1}},
]


# ---------------------------------------------------------------------
# Reproducibility stamps (git commit + environment). Keep as-is; problem-agnostic.
# ---------------------------------------------------------------------
def _git_commit() -> str:
    try:
        h = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
        dirty = subprocess.check_output(
            ["git", "status", "--porcelain"], text=True, stderr=subprocess.DEVNULL
        )
        return h + ("+dirty" if dirty.strip() else "")
    except Exception:
        return "unknown"


def _env() -> dict:
    import importlib.metadata as md

    def ver(pkg):
        try:
            return md.version(pkg)
        except Exception:
            return "n/a"

    return {
        "python": platform.python_version(), "host": socket.gethostname(),
        "platform": platform.platform(),
        # <PLACEHOLDER: stamp the solver / key libraries your methods depend on>
        # e.g. "pyomo": ver("Pyomo"), "gurobipy": ver("gurobipy"),
    }


# ---------------------------------------------------------------------
# One run: solve -> COMPLIANCE GATE (P3 checker) -> persist (JSON + CSV row).
# A failed run must NEVER abort the battery: catch, record status="error".
# ---------------------------------------------------------------------
def run_one(stem: str, instance: dict, exp: dict, git: str, env: dict) -> dict:
    label, method, config = exp["label"], exp["method"], exp["config"]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    t0 = time.perf_counter()
    solution, error = None, None
    try:
        solution, status = METHODS[method](instance, config)
        runtime = time.perf_counter() - t0
        checks = <CHECKER>(instance, solution).check()   # compliance gate (empty ⇒ feasible)
        feasible = (checks == {})
        objective = solution.get("objective") if feasible else None
        violations = sorted(checks.keys())
    except Exception as e:  # noqa: BLE001 - a failed run must not abort the battery
        runtime = time.perf_counter() - t0
        status, feasible, objective, violations = "error", False, None, []
        error = f"{type(e).__name__}: {e}"

    record = {
        "instance": stem, "label": label, "method": method, "config": config,
        "status": status, "objective": objective, "runtime_s": round(runtime, 3),
        "feasible": feasible, "violations": violations, "error": error,
        "timestamp": ts, "git": git, "env": env,
    }

    # DUAL PERSISTENCE — (1) rich per-run JSON with the full solution.
    _SOLUTIONS.mkdir(parents=True, exist_ok=True)
    with open(_SOLUTIONS / f"{stem}__{label}__{ts}.json", "w", encoding="utf-8") as fh:
        json.dump({**record, "solution": solution}, fh, indent=2)

    # DUAL PERSISTENCE — (2) one appended row in the flat CSV ledger.
    new = not _LEDGER.exists()
    with open(_LEDGER, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=_CSV_COLUMNS)
        if new:
            w.writeheader()
        w.writerow({
            "timestamp": ts, "instance": stem, "label": label, "method": method,
            "status": status, "objective": objective, "runtime_s": round(runtime, 3),
            "feasible": feasible, "violations": ";".join(violations),
            "git": git, "config": json.dumps(config),
        })
    return record


# ---------------------------------------------------------------------
# Comparison: FIXED gap convention vs the cached baseline, per instance.
# gap = (baseline_obj - method_obj) / baseline_obj. Only computed when BOTH the
# baseline and the method are feasible (compliance gate first). Always report the
# absolute Δ alongside the gap when consuming these rows (see the protocol doc).
# ---------------------------------------------------------------------
def compare(records: list[dict], baseline_label: str = "<BASELINE_LABEL>") -> list[dict]:
    by_inst: dict[str, dict[str, dict]] = {}
    for r in records:
        by_inst.setdefault(r["instance"], {})[r["label"]] = r
    rows = []
    for inst, byl in sorted(by_inst.items()):
        base = byl.get(baseline_label)
        for label, r in sorted(byl.items()):
            gap = None
            if (base and base.get("feasible") and r.get("feasible")
                    and base.get("objective")):
                gap = (base["objective"] - r["objective"]) / base["objective"]
            rows.append({
                "instance": inst, "label": label, "objective": r.get("objective"),
                "feasible": r.get("feasible"), "runtime_s": r.get("runtime_s"),
                "gap_vs_baseline": None if gap is None else round(gap, 4),
            })
    return rows


# ---------------------------------------------------------------------
# Battery log (git + env header + summary table + gap table). Problem-agnostic.
# ---------------------------------------------------------------------
def _write_battery_log(records: list[dict], git: str, env: dict) -> Path:
    _LOGS.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = _LOGS / f"battery_{ts}.log"
    lines = [
        f"# Battery {ts}", f"git: {git}", f"env: {json.dumps(env)}",
        f"runs: {len(records)}", "",
        f"{'instance':16} {'label':16} {'status':12} {'obj':>6} {'time_s':>8} {'feasible':>8} violations",
        "-" * 82,
    ]
    for r in sorted(records, key=lambda x: (x["instance"], x["label"])):
        lines.append(
            f"{r['instance']:16} {r['label']:16} {r['status']:12} "
            f"{str(r['objective']):>6} {r['runtime_s']:>8} {str(r['feasible']):>8} "
            f"{','.join(r['violations']) or '-'}"
        )
    lines += ["", "# gap vs baseline (sign per objective direction; see protocol)"]
    for row in compare(records):
        lines.append(
            f"{row['instance']:16} {row['label']:16} obj={str(row['objective']):>6} "
            f"gap={row['gap_vs_baseline']}"
        )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# ---------------------------------------------------------------------
# Battery driver + CLI. inst_filter = comma-separated substrings on the stem;
# exp_filter = comma-separated exact labels. Empty ⇒ everything.
# ---------------------------------------------------------------------
def run_battery(inst_filter: str = "", exp_filter: str = "") -> list[dict]:
    git, env = _git_commit(), _env()
    bench = [(s, i) for (s, i) in build_benchmark()
             if not inst_filter or any(f in s for f in inst_filter.split(","))]
    exps = [e for e in EXPERIMENTS
            if not exp_filter or e["label"] in exp_filter.split(",")]
    records = []
    for stem, inst in bench:
        for exp in exps:
            print(f"[run] {stem} × {exp['label']} ...", flush=True)
            rec = run_one(stem, inst, exp, git, env)
            print(f"      status={rec['status']} obj={rec['objective']} "
                  f"feasible={rec['feasible']} {rec['runtime_s']}s")
            records.append(rec)
    log = _write_battery_log(records, git, env)
    print(f"[battery] {len(records)} runs; ledger={_LEDGER}; log={log}")
    return records


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    inst_filter = argv[0] if len(argv) > 0 else ""
    exp_filter = argv[1] if len(argv) > 1 else ""
    run_battery(inst_filter, exp_filter)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
