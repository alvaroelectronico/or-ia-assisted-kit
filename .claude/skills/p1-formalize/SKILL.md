---
name: p1-formalize
description: >
  Phase P1 of the combinatorial-problem methodology — Formalization. Use after
  P0, to turn the scoped brief into an explicit formal spec: a problem
  description with Decision / Requirements / Objective / Input information.
  Applies templates/problem-description.template.tex. Follows
  docs/methodology/README.md.
---

# P1 — Formalization

Produce a rigorous, technique-agnostic problem description.

## Inputs
- The P0 scoped brief.

## Template
- `docs/methodology/templates/problem-description.template.tex` (asset A-P1-tpl).

## Steps
1. Copy the template into the problem's docs folder as
   `docs/<problem>/problem_description.tex`.
2. Fill **Part 1 — Problem presentation**: overview, setup, how the cost/metric
   arises, **Key assumptions** (consolidate ALL modeling assumptions here — what
   is not tracked, what is assumed infinite/instant/feasible), and operating
   regime/variant if any.
3. Fill **Part 2 — Problem statement**: Decision, Requirements, Objective, Input
   information (+ scenario evaluation if relevant).
4. Wire it into a small `main.tex` + `compile.py` harness under `docs/<problem>/`
   (a two-pass `pdflatex` build that cleans aux files) and compile to verify it
   builds.

## Done when
- `problem_description.tex` compiles; all four statement sections are filled;
  every assumption lives under Key assumptions; no leftover `<PLACEHOLDER>`.

## Governance
- Invoke `methodology-curator` to record P1 and reconcile the instance with the
  template (extract/update A-P1-tpl if the skeleton needed generalizing).
- Run `methodology-auditor` before moving on.

## Next
- P2 data model & instances (`p2-data-model`).
