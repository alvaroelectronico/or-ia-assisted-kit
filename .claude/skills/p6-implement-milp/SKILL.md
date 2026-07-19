---
name: p6-implement-milp
description: >
  Phase P6 of the combinatorial-problem methodology — MILP implementation. Use
  after P5, to build the executable model that realizes the formulation and runs
  on generated instances. Chooses the solver stack and linearizes as needed.
  Follows docs/methodology/README.md.
---

# P6 — MILP implementation

Turn the P5 formulation into runnable code.

## Inputs
- The P5 formulation (`docs/<problem>/milp_formulation.tex`).
- The P2 generator and schema, and the P3 solution schema (`<problem>_model/`).

## Steps
1. Choose the solver stack. For this project the decision is **Pyomo + Gurobi**
   (via `SolverFactory("gurobi_direct")`); Pyomo + HiGHS is the license-free
   fallback. Record the choice as a decision.
2. Implement the model in the problem's code package
   (`<problem>_model/milp_model.py`), reading instances from the generator's
   JSON. Keep the code's sets/params/vars named as in the formulation.
3. Linearize every bilinear term the formulation flagged (McCormick / indicator).
4. Solve small generated instances; assert feasibility, inspect the objective,
   and sanity-check against any known bound or a brute-force tiny case.

## Reusable asset
- The MILP-implementation template (`templates/milp-implementation.template.py`):
  a solver-agnostic Pyomo scaffold (build_model + solve_instance that extracts to
  the P3 solution schema and runs the P3 checker). Refresh it on changes.

## Done when
- The model solves sample instances; its solutions pass the **P3 solution
  checker** (all RQxx) and the objective matches the formulation's intent;
  results are reproducible from a seed.

## Governance
- Invoke `methodology-curator` to record P6 and refresh the implementation
  template. Use the built-in `verify` skill to exercise the model end-to-end.

## Next
- P7 method review & transfer (skills `digest-paper` + `synthesize-theory`).
