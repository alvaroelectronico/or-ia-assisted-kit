"""TEMPLATE (methodology asset A-P8-tpl) — P8 Heuristic design.

Purpose
-------
A problem-agnostic scaffold for a constructive + local-search / metaheuristic
solver, built from a P7 candidate approach. It has three parts:

  1. a CONSTRUCTIVE builder that respects the problem's requirements by
     construction (`construct(instance) -> decision_objects`);
  2. a deterministic OBJECTIVE EVALUATOR that turns a candidate ordering /
     assignment into a full P3-schema solution AND its score
     (`evaluate(instance, ..., decision) -> (calls_or_blocks, schedule, score)`);
  3. an ITERATED-GREEDY / local-search loop (destroy -> best-insertion ->
     accept) with multi-restart, wrapped by the phase entry point
     `solve_heuristic(instance, config) -> (solution, status)`.

The EVALUATOR is the reusable core. It is what P9 (experimentation) compares
against the exact/MILP baseline, so it MUST emit solutions in the P3 solution
schema (`schemas/solution.json`) that pass the P3 checker unchanged — a fast,
deterministic re-implementation of the objective, not an approximation.

How to use
----------
Copy this file into the problem's code package (e.g.
`<problem>_model/heuristics.py`), rename, and fill every `<PLACEHOLDER>`.
Delete guidance comments once instantiated. The result must:
  * produce solutions in the shape of the P3 `schemas/solution.json`;
  * pass the P3 checker (all `[RQxx]`) on every emitted solution;
  * be deterministic given `config["seed"]` (all randomness through one
    `random.Random(seed)`), so P9 runs are reproducible;
  * keep `solve_heuristic(instance, config) -> (solution, status)` as the sole
    entry point (same shape as the MILP `solve_instance`, so P9's METHODS
    registry can call either interchangeably).

Design contract (keep all of it)
--------------------------------
  * Feasibility by construction in `construct` — every hard requirement that can
    be enforced while building (grouping/separation rules, capacity limits,
    forbidden pairs) is enforced there, so the local search only reorders
    feasible pieces and can never break a requirement.
  * The evaluator is PURE and DETERMINISTIC: same (instance, decision) -> same
    (solution, score). No hidden global state, no RNG inside it.
  * Local search perturbs only a DEGREE OF FREEDOM that keeps feasibility
    (typically the entry/processing ORDER of the constructed objects), never the
    feasibility-critical content produced by `construct`.
  * Multi-restart: run the loop from several seeds, keep the best; this is the
    cheap variance reduction that turns a greedy into a metaheuristic.
"""

from __future__ import annotations

import os
import random
import sys
from collections import defaultdict

# Allow `python -m <problem>_model.heuristics` and direct execution.
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# The P3 checker, to self-verify every emitted solution (see _demo).
from <problem>_model.solution_checker import <Checker>


# ---------------------------------------------------------------------
# 1. CONSTRUCTIVE builder — respect the requirements BY CONSTRUCTION.
#    Group / partition the raw demand along whatever the requirements force
#    (e.g. one pass per <grouping key> so a separation rule [RQxx] holds),
#    then greedily fill capacity-limited decision objects, never violating a
#    forbidden-combination rule [RQxx]. Return the feasible building blocks the
#    evaluator and local search will (re)order.
# ---------------------------------------------------------------------
def construct(instance: dict) -> list[dict]:
    # --- pull raw entities / config / demand out of the instance ----------
    <entity_by_id> = {e["id"]: e for e in instance["<ENTITY_SET>"]}
    cfg = instance["config"]
    <CAP> = cfg["<capacity_param>"]                 # e.g. box volume / bin size

    demand: dict = defaultdict(dict)
    for d in instance["demand"]:
        demand[d["<owner_ref>"]][d["<entity_ref>"]] = (
            demand[d["<owner_ref>"]].get(d["<entity_ref>"], 0) + d["<quantity>"]
        )

    # Forbidden combinations expressed as a set of frozensets (order-free).
    forbidden = {frozenset(p) for p in instance.get("<forbidden_pairs>", [])}

    objects, n = [], 0
    for owner, dem in demand.items():
        cap = <per_owner_capacity_expression>       # e.g. fill% * CAP
        # One partition pass per grouping key that a separation rule forces,
        # so items from different groups NEVER share an object ([RQxx]).
        by_group: dict = defaultdict(list)
        for e in dem:
            by_group[<entity_by_id>[e]["<group_key>"]].append(e)

        for _, entities in by_group.items():
            # First-fit decreasing within capacity, skipping forbidden pairs.
            open_objs: list[dict] = []
            for e in sorted(entities, key=lambda x: -<size_of>(x)):
                size = <size_of>(e)
                for _ in range(dem[e]):
                    placed = False
                    for o in open_objs:
                        if (o["load"] + size <= cap + 1e-9 and
                                all(frozenset((e, e2)) not in forbidden
                                    for e2 in o["members"])):
                            o["contents"][e] = o["contents"].get(e, 0) + 1
                            o["load"] += size
                            o["members"].add(e)
                            placed = True
                            break
                    if not placed:
                        open_objs.append(
                            {"contents": {e: 1}, "load": size, "members": {e}}
                        )
            for o in open_objs:
                n += 1
                objects.append({"id": f"o{n}", "<owner_field>": owner,
                                "contents": dict(o["contents"])})
    return objects


# ---------------------------------------------------------------------
# 2. OBJECTIVE EVALUATOR (the reusable core, feeds P9).
#    Deterministically turn a DECISION (here: an ordering of the constructed
#    objects) into a full P3-schema solution plus its score. If the objective
#    is dynamic/sequential, this is a small discrete-event simulator; if static,
#    it is a direct cost computation. Either way it emits exactly the keys the
#    P3 solution schema declares and returns the score used by the search.
# ---------------------------------------------------------------------
def evaluate(instance: dict, objects_by_id: dict, order: list[str], <RES>: int):
    <entity_by_id> = {e["id"]: e for e in instance["<ENTITY_SET>"]}
    remaining = {o: dict(objects_by_id[o]["contents"]) for o in order}

    # --- initialise the sequential state (if any) -------------------------
    # e.g. bring the first <RES> objects "active"; track enter/leave events.
    schedule_events: dict = {}
    steps: list[dict] = []          # ordered P3 decision records (calls/moves)
    # <... state init ...>

    # --- greedy step loop: pick the locally-best action, apply it ---------
    # Replace with the problem's step logic; keep it deterministic.
    while <work_remains>:
        action = <choose_best_action(remaining, state)>
        if action is None:
            break
        steps.append(<schema_shaped_record(action)>)   # P3 solution vocabulary
        <apply action to `remaining` / state, record enter/leave events>

    schedule = [{"object": o, "enter": schedule_events[o]["enter"],
                 "leave": schedule_events[o]["leave"]} for o in order]
    score = <objective_from_steps>          # e.g. len(steps); must MINIMISE-align
    return steps, schedule, score


def _initial_order(objects: list[dict]) -> list[str]:
    """A decent constructive seed for the search (e.g. greedy nearest-neighbour
    by shared features, so similar objects start adjacent). Deterministic."""
    sig = {o["id"]: set(o["contents"]) for o in objects}
    ids = [o["id"] for o in objects]
    if not ids:
        return []
    order, rem = [ids[0]], set(ids[1:])
    while rem:
        last = sig[order[-1]]
        nxt = max(rem, key=lambda x: (len(sig[x] & last), x))  # tie-break stable
        order.append(nxt)
        rem.discard(nxt)
    return order


# ---------------------------------------------------------------------
# 3. ITERATED GREEDY / local search over the DEGREE OF FREEDOM (the order).
#    destroy k objects -> best-insertion reconstruct -> accept if not worse.
#    All randomness through the passed-in rng, so a fixed seed is reproducible.
# ---------------------------------------------------------------------
def iterated_greedy(instance, objects, <RES>, iterations=150, seed=0, destroy=2):
    rng = random.Random(seed)
    by_id = {o["id"]: o for o in objects}

    def ev(o):                                   # score-only shortcut
        return evaluate(instance, by_id, o, <RES>)[2]

    best = _initial_order(objects)
    best_obj = ev(best)
    for _ in range(iterations):
        cur = best[:]
        # --- DESTROY: remove k elements at random -------------------------
        removed = []
        k = min(destroy, max(0, len(cur) - 1))
        for _ in range(k):
            removed.append(cur.pop(rng.randrange(len(cur))))
        # --- RECONSTRUCT: greedy best-insertion of each removed element ----
        for r in removed:
            best_pos, best_o = 0, None
            for pos in range(len(cur) + 1):
                o = ev(cur[:pos] + [r] + cur[pos:])
                if best_o is None or o < best_o:   # < for a minimisation score
                    best_o, best_pos = o, pos
            cur.insert(best_pos, r)
        # --- ACCEPT: keep if not worse than the incumbent -----------------
        o = ev(cur)
        if o <= best_obj:
            best_obj, best = o, cur[:]
    return best, best_obj


# ---------------------------------------------------------------------
# Phase entry point — same (solution, status) shape as the MILP solver, so the
# P9 METHODS registry can call heuristic and exact methods interchangeably.
# ---------------------------------------------------------------------
def solve_heuristic(instance: dict, config: dict | None = None):
    """P8 entry point. Returns (solution matching schemas/solution.json, status)."""
    config = config or {}
    objects = construct(instance)
    by_id = {o["id"]: o for o in objects}
    <RES> = instance["config"]["<resource_param>"]

    # Multi-restart: keep the best over several seeds.
    best, best_obj = None, None
    for r in range(config.get("restarts", 4)):
        order, obj = iterated_greedy(
            instance, objects, <RES>,
            iterations=config.get("iterations", 150),
            seed=config.get("seed", 0) + r,
            destroy=config.get("destroy", 2),
        )
        if best_obj is None or obj < best_obj:
            best, best_obj = order, obj

    steps, schedule, objective = evaluate(instance, by_id, best, <RES>)
    objects_out = [
        {"id": o["id"], "<owner_field>": o["<owner_field>"],
         "contents": [{"<entity_ref>": e, "<quantity>": u}
                      for e, u in o["contents"].items()]}
        for o in objects
    ]
    solution = {
        "<objects_block>": objects_out,     # constructed decision objects
        "<steps_block>": steps,             # ordered sequential decisions
        "schedule": schedule,               # per-object timing, if applicable
        "objective": objective,
    }
    return solution, "heuristic_ok"


# ---------------------------------------------------------------------
# Demo: generate small instances, solve, verify each with the P3 checker.
# Run with:  python -m <problem>_model.heuristics
# ---------------------------------------------------------------------
def _demo() -> int:
    from <problem>_model.instance_generator import generate_instance

    print(f"{'instance':16} {'heur_obj':>8} {'feasible':>8}  violations")
    print("-" * 52)
    ok = True
    for seed in (1, 2, 3):
        for size in [<small_size_args>]:
            inst = generate_instance(**size, seed=seed)
            sol, _ = solve_heuristic(inst, {"seed": 1})
            checks = <Checker>(inst, sol).check()      # empty dict == feasible
            feasible = checks == {}
            ok = ok and feasible
            print(f"{<label(size, seed)>:16} {sol['objective']:>8} "
                  f"{str(feasible):>8}  {','.join(checks) or '-'}")
    print("SELF-TEST", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(_demo())
