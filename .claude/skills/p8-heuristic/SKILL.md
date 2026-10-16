---
name: p8-heuristic
description: >
  Phase P8 of the combinatorial-problem methodology — Heuristic design. Use after
  P7 (method review), to design and implement a heuristic (constructive + local
  search / metaheuristic) — ideally a candidate from the P7 synthesis — to be
  compared against the MILP. Follows docs/methodology/README.md.
---

# P8 — Heuristic design

Design a heuristic that exploits the problem's cost lever, and implement it.

## Inputs
- The P1 problem statement (objective and the cost lever it identifies).
- The **P7 method-review synthesis** (`docs/<problem>/theory/synthesis.md`) — pick a
  candidate approach from it as the starting blueprint.
- The P2 generator/schema, the P3 solution schema, and the P6 instance interface.

## Steps
1. Choose a candidate from the P7 synthesis (or justify a different design). Design a
   **constructive** heuristic that builds a feasible solution greedily along the cost
   lever, then a **local search / metaheuristic** to improve it.
2. Implement it in the problem's code package (`<problem>_model/heuristics.py`),
   consuming the same instances and producing the same solution shape as the
   MILP implementation.
3. Run it on sample instances; confirm feasibility with the P3 checker and record
   objective + time.
4. **Document the algorithm in detail.** Write a dedicated `docs/<problem>/heuristic.tex`
   (\input into the LaTeX harness) describing HOW it works — not just a summary:
   per-stage **pseudocode**, the **objective/evaluator**, **complexity**, a
   **parameter table** with defaults, **design rationale**, a **worked micro-example**,
   and **limitations**. The P10 report only summarises; this is the full description.

## Optional agent
- Spawn a design panel that proposes several heuristic strategies from different
  angles and judges them, then implement the winner (grafting good ideas from
  runners-up).

## Reusable asset
- Start from `docs/methodology/templates/heuristic-design.template.py`
  (constructive builder + deterministic evaluator + iterated-greedy/local-search
  loop) and `templates/algorithm-doc.template.tex` for `heuristic.tex`; refresh
  them if the design generalizes.

## Done when
- The heuristic returns solutions that pass the **P3 solution checker** on all
  sample instances, with recorded objective and runtime; and a **detailed
  algorithm description** (pseudocode, complexity, parameters, rationale, worked
  example) exists in `docs/<problem>/heuristic.tex`.

## Governance
- Invoke `methodology-curator` to record P8 and extract the template.

## Next
- P9 experimentation & comparison (`p9-experiments`).
