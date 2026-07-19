---
name: p5-formulate-milp
description: >
  Phase P5 of the combinatorial-problem methodology — MILP formulation
  (mathematical model only, no code). Use after P4, to write the exact model:
  sets, parameters, variables, constraints, objective, in LaTeX. Applies
  templates/milp-formulation.template.tex. Follows docs/methodology/README.md.
---

# P5 — MILP formulation

Write the mathematical MILP model. Formulation only — the executable model is P6.

## Inputs
- The P2 data model (sets and parameters) and the P1 problem statement.

## Template
- `docs/methodology/templates/milp-formulation.template.tex` (asset A-P5-tpl),
  fleets style with constraint groups **interleaved** with their explanations.

## Naming convention (hard rule)
Parameters are **always UPPERCASE** (multi-letter allowed, e.g. `V^{BOX}`,
`DUR^{MAX}`); decision variables are **always lowercase**; sets are calligraphic.
This lets a reader tell data from decisions at a glance. Disambiguate colliding
parameters with sub/superscripts — never by lowercasing a parameter.

## Steps
1. Copy the template into `docs/<problem>/milp_formulation.tex`.
2. State modeling assumptions explicitly up front (any approximation of the real
   dynamics), then fill **Notation** (Sets / Parameters / Binary / Integer
   variable tables) and **Model** (objective block + one interleaved constraint
   group per family, each followed by its explanation, then the domains block).
3. Flag every bilinear/nonlinear term that will need linearization, and add a
   "Notes and open modeling choices" section. Where useful, reference the `[RQxx]`
   a constraint enforces (traceability).
4. Wire into `main.tex` and compile.

## Optional agent
- For a hard/ambiguous model, spawn a panel that drafts alternative formulations
  and pick the best (a `milp-modeler` agent), rather than committing to one.

## Done when
- The formulation compiles, follows the template style (interleaved groups), and
  every symbol is defined; assumptions and open choices are explicit.

## Governance
- Invoke `methodology-curator` to record P5 and reconcile with A-P5-tpl.
- Run `methodology-auditor` before P6.

## Next
- P6 MILP implementation (`p6-implement-milp`).
