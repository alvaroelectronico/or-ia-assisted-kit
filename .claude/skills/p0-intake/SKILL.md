---
name: p0-intake
description: >
  Phase P0 of the combinatorial-problem methodology — Intake & scoping. Use at
  the very start of a new problem, when you have a raw problem description and
  must scope it before formalizing. Captures the raw statement, runs clarifying
  questions, and produces a scoped brief. Follows docs/methodology/README.md.
---

# P0 — Intake & scoping

Turn a raw, possibly vague problem description into a scoped brief ready for
formalization (P1). Read `docs/methodology/README.md` first for the two-layer
principle and the phase list.

## Inputs
- The user's raw problem description (prose, docs, or conversation).

## Steps
1. Capture the raw problem statement verbatim (do not paraphrase away detail).
2. Identify: what system/process, what "solve" means here, and the single
   headline metric to optimize.
3. Ask 2–5 clarifying questions covering the gaps that would block P1:
   objective/metric, the decisions to make, hard constraints, which inputs are
   available, problem scale, and any distinct operating regimes/variants.
4. Record the answers and write a short **scoped brief** (context + resolved
   questions + explicit out-of-scope notes) in the problem's docs folder
   (e.g. `docs/<problem>/`).

## Done when
- The raw statement and clarifications are captured, and the brief has enough to
  fill P1's Decision / Requirements / Objective / Input without further guesswork.

## Governance
- Invoke `methodology-curator` to record P0 status and any scoping decisions in
  `docs/methodology/registry.md`.

## Next
- P1 formalization (`p1-formalize`).
