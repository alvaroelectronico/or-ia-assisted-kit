"""TEMPLATE (methodology asset A-P6-tpl) — P6 MILP implementation.

Purpose
-------
A solver-agnostic Pyomo scaffold that turns the P5 MILP FORMULATION
(`docs/<problem>/milp_formulation.tex`) into runnable code, solves generated
instances, extracts the result into the P3 SOLUTION schema, and self-verifies
it with the P3 checker.

How to use
----------
Copy this file into the problem's code package (e.g.
`<problem>_model/milp_model.py`), rename, and fill every `<PLACEHOLDER>`.
Delete guidance comments once instantiated. The result must:
  * build a model whose sets / params / variables are NAMED EXACTLY as in the
    formulation `.tex` (parameters UPPERCASE, variables lowercase, sets
    calligraphic in the math → plain names here) so code and math stay in
    one-to-one correspondence and are reviewable side by side;
  * read an instance produced by the P2 generator (schema `schemas/instance.json`);
  * emit a solution in the shape of the P3 `schemas/solution.json`;
  * pass the P3 checker (all `[RQxx]`) on the emitted solution.

Design contract (keep all of it)
--------------------------------
  * Solver chosen via `pyo.SolverFactory(<SOLVER>)` — swapping the backend
    (HiGHS / CBC / Gurobi / CPLEX) must not touch the model build. Record the
    chosen stack as a methodology decision.
  * `build_model(instance, ...)` returns a `ConcreteModel` and NOTHING ELSE
    (no solve) so the model can be inspected, reused, or exported (`.lp`/`.mps`).
  * Preprocessing (deriving index sets, bounds, horizons, candidate entities
    from raw instance data) lives in one helper and is stashed on the model
    (`m._prep`) so `solve_instance` can extract without recomputing.
  * Determinism: given the same instance and solver seed the run is reproducible.

Dependencies
------------
    pip install pyomo            # modeling layer
    # plus a solver backend, e.g. one of:
    #   highspy            (open source; SolverFactory("appsi_highs"))
    #   gurobipy           (commercial; SolverFactory("gurobi_direct"), no CLI needed)
"""

from __future__ import annotations

import math
from collections import defaultdict

import pyomo.environ as pyo

# The P3 checker, to self-verify every emitted solution.
from <problem>_model.solution_checker import <Checker>


# ---------------------------------------------------------------------
# Instance preprocessing: derive index sets, bounds/horizons, lookups.
# Everything the model and the extractor need is computed ONCE here.
# ---------------------------------------------------------------------
def _prepare(instance: dict) -> dict:
    # --- pull raw entities / config out of the instance dict ---------------
    <entity_by_id> = {e["id"]: e for e in instance["<ENTITY_SET>"]}
    cfg = instance["config"]
    <CAP_PARAM> = cfg["<cap_param>"]          # e.g. resource count / capacity

    # --- aggregate sparse demand into a dense lookup ----------------------
    demand = defaultdict(int)
    for d in instance["demand"]:
        demand[(d["<index_ref>"], d["<entity_ref>"])] += d["<quantity>"]

    # --- derive index sets / candidate decision objects -------------------
    # Build only the (index, entity) pairs that actually appear (sparsity),
    # and any DERIVED objects the formulation quantifies over (e.g. candidate
    # boxes/vehicles/slots). Bound their count so the model stays finite;
    # choose a bound that PROVABLY admits a feasible solution, plus slack.
    <derived_objects> = []
    # <... construct derived objects with a feasibility-safe count ...>

    # --- horizon / big-M bounds -------------------------------------------
    # If the formulation indexes over an ordered horizon set K (steps, calls,
    # periods), size it here from a safe upper bound. Keep UMAX/BIG_M explicit.
    <HORIZON> = <safe_upper_bound_expression>
    <BIG_M> = <tight_big_m_expression>

    return dict(
        <entity_by_id>=<entity_by_id>, demand=demand, <CAP_PARAM>=<CAP_PARAM>,
        <derived_objects>=<derived_objects>, <HORIZON>=<HORIZON>, <BIG_M>=<BIG_M>,
        # ... every lookup solve_instance / build_model will need ...
    )


# ---------------------------------------------------------------------
# Pyomo model build — mirrors <problem>/milp_formulation.tex section by section.
# Keep symbol names identical to the formulation.
# ---------------------------------------------------------------------
def build_model(instance: dict, <horizon>: int | None = None) -> pyo.ConcreteModel:
    p = _prepare(instance)
    demand = p["demand"]
    HORIZON = <horizon> or p["<HORIZON>"]

    m = pyo.ConcreteModel()
    m._prep = p  # stash preprocessing for the extractor

    # --- sets (calligraphic in the .tex) ----------------------------------
    m.<SET_A> = pyo.Set(initialize=<...>)             # e.g. m.B
    m.<SET_B> = pyo.Set(initialize=<...>)             # e.g. m.S
    m.K = pyo.RangeSet(1, HORIZON)                    # ordered horizon, if any
    # Multi-dimensional index sets restricted to the pairs that exist:
    m.<SET_AB> = pyo.Set(dimen=2, initialize=<sparse_pairs>)

    # --- variables (lowercase in the .tex) --------------------------------
    # One Var per formulation symbol; match domains (Binary / NonNegativeIntegers
    # / NonNegativeReals) to the variable-domain block of the formulation.
    m.<var1> = pyo.Var(m.<SET_AB>, domain=pyo.NonNegativeIntegers)   # e.g. x[b,s]
    m.<var2> = pyo.Var(m.<SET_A>, domain=pyo.Binary)                 # e.g. y[b]
    # ... one per symbol: g, w, h, n, delta, ...

    # --- objective (single expression from the formulation) ---------------
    m.obj = pyo.Objective(
        expr=<objective_expression>, sense=pyo.minimize   # or pyo.maximize
    )

    # --- constraints: ONE Pyomo Constraint per constraint family in the .tex.
    # Name each after its \label{eq:...} so reviewers can cross-check 1:1.
    def <family1>_rule(m, *idx):
        return <linear_relation>
    m.<family1> = pyo.Constraint(<index_set>, rule=<family1>_rule)

    # For families that only apply to a filtered index (skip the rest):
    def <family2>_rule(m, *idx):
        if not <applies>:
            return pyo.Constraint.Skip
        return <linear_relation>
    m.<family2> = pyo.Constraint(<index_set>, rule=<family2>_rule)

    # Symmetry-breaking / valid inequalities are legitimate additions here even
    # if absent from the pure formulation; note them as implementation choices.

    return m


# ---------------------------------------------------------------------
# Solve + extract to the P3 solution.json shape.
# ---------------------------------------------------------------------
def solve_instance(
    instance: dict,
    <horizon>: int | None = None,
    solver: str = "<SOLVER>",          # e.g. "appsi_highs" or "gurobi_direct"
    time_limit: float = 60,
    mip_gap: float = 0.0,
    tee: bool = False,
) -> dict:
    m = build_model(instance, <horizon>=<horizon>)
    opt = pyo.SolverFactory(solver)
    # Option KEYS are solver-specific; map the two portable knobs per backend.
    opt.options["<TIME_LIMIT_OPT>"] = time_limit   # e.g. "TimeLimit" / "time_limit"
    opt.options["<MIP_GAP_OPT>"] = mip_gap         # e.g. "MIPGap"    / "mip_rel_gap"
    res = opt.solve(m, tee=tee)

    p = m._prep

    def iv(var) -> int:  # rounded integer value of a variable
        return int(round(pyo.value(var)))

    # --- extract each realized-decision block of the solution schema -------
    # Read ONLY the decision variables; recompute nothing the checker recomputes.
    # Emit exactly the keys the P3 solution schema declares.
    <block1> = []
    # <... walk the relevant variables, append schema-shaped dicts ...>

    return {
        "<solution_block_1>": <block1>,
        # ... one key per solution-schema decision block ...
        "objective": <objective_value_from_solution>,
        "_solver_status": str(res.solver.termination_condition),
    }


# ---------------------------------------------------------------------
# Demo: generate a tiny instance, solve, verify with the P3 checker.
# Run with:  python -m <problem>_model.<module>
# ---------------------------------------------------------------------
def _demo() -> int:
    from <problem>_model.instance_generator import generate_instance

    instance = generate_instance(<small_args>, seed=<seed>)
    sol = solve_instance(instance, time_limit=60, tee=False)
    print("solver:", sol.pop("_solver_status"), "| objective:", sol["objective"])

    checks = <Checker>(instance, sol).check()
    print("checker:", checks if checks else "{}  (feasible — all RQ pass)")
    ok = (checks == {})   # empty dict from the P3 checker == feasible
    print("P6 DEMO", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(_demo())
