---
name: p3-solution-checker
description: >
  Phase P3 of the combinatorial-problem methodology — Solution model & checker.
  Use after P2, to define the solution schema and build a checker that verifies,
  for any candidate solution, that every tagged requirement (RQ01, RQ02, …) from
  the formalization holds, and recomputes the objective. Follows
  docs/methodology/README.md.
---

# P3 — Solution model & checker

Define what a solution looks like and build the verifier that any technique's
output (MILP, heuristic) must pass. This exists BEFORE the technique phases so
they can self-verify.

## Inputs
- The P1 problem statement, in particular the **requirements tagged `[RQxx]`**.
- The P2 data model and instance schema.

## Templates
- `docs/methodology/templates/solution-schema.template.json`
- `docs/methodology/templates/solution-checker.template.py`

## Recommended: reuse cornflow's built-in check mechanism
If the problem is built as a cornflow app (your `<problem>_model` package), do NOT
build a custom runner. `ExperimentCore.check()`
auto-discovers every method named `check_*`, runs each, and aggregates the
**non-empty** results into a dict keyed by the method name with `check_` stripped
(so an **empty dict means the solution is feasible**), validated against
`schema_checks` (`solution_checks.json`). Concretely:
- Implement **one method `check_rq01`, `check_rq02`, …** per requirement on the
  `Experiment` subclass; each returns a list of error entries (empty = pass).
- Define `solution.json` (solution schema) and `solution_checks.json` (schema of
  the aggregated check output).
- Implement `get_objective()` to recompute the objective from the solution.
- Calling `check()` then runs all requirement checks at once.

Generic fallback (non-cornflow context): a standalone
`<problem>_model/solution_checker.py` with one function per RQ plus an aggregator.

## Steps
1. **Solution schema**: define a candidate solution's structure in
   `<problem>_model/schemas/solution.json`.
2. **Requirement checks**: one `check_rqXX` per `[RQxx]` (traceability: every RQ
   maps to exactly one check), on the cornflow `Experiment` (or the fallback
   module).
3. **Checks schema**: `<problem>_model/schemas/solution_checks.json` for the
   aggregated output.
4. Test: build a valid and a deliberately invalid solution for a small generated
   instance; confirm `check()` is empty for the valid one and flags the right
   `rqXX` for the invalid one.

## Reusable asset
- Extract/refresh the solution-schema and solution-checker templates (cornflow
  `check_rq*` pattern + `solution_checks.json`).

## Done when
- Every requirement `RQxx` has a corresponding `check_rqXX`; `check()` is empty
  for a valid sample and flags an invalid one; `get_objective()` recomputes the
  objective.

## Governance
- Invoke `methodology-curator` to record P3 and extract the templates.
- This checker is reused by P6 (MILP implementation), P8 (heuristic) and P9
  (experimentation) to assert feasibility before comparing objectives.

## Next
- P4 solution visualization (`p4-visualize`).
