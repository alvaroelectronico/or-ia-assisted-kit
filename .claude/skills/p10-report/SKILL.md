---
name: p10-report
description: >
  Phase P10 of the combinatorial-problem methodology — Reporting & synthesis. Use
  last, to write the conclusions report and a methodology retrospective. Follows
  docs/methodology/README.md.
---

# P10 — Reporting & synthesis

Synthesize the results and close the loop on the methodology.

## Inputs
- The P9 experiment results and all prior artifacts (including P4 visualizations
  and the P7 method-review synthesis).

## Steps
1. Write the **conclusions report**: the problem, the approaches tried
   (formulation + heuristic), the results across scenarios (with P4
   visualizations of representative solutions), and the recommendations (which
   technique/config, at what cost/quality).
2. Write a short **methodology retrospective**: which templates/skills worked,
   what was awkward, and what to improve for the next problem.

## Reusable asset
- Extract a report template on the first run.

## Done when
- The report is written (and compiles, if LaTeX) and the retrospective is
  captured.

## Governance
- Invoke `methodology-curator` to record P10 and log retrospective items as
  decisions/improvements.
- Run a final `methodology-auditor` consistency pass over the whole methodology.
