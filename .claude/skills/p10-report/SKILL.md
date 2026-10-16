---
name: p10-report
description: >
  Phase P10 of the combinatorial-problem methodology — Reporting & synthesis. Use
  last, to write the conclusions report (documenting the algorithm(s) and the
  experimental results) plus a methodology retrospective. Applies
  templates/report.template.tex. Follows docs/methodology/README.md.
---

# P10 — Reporting & synthesis

Document the algorithm(s) and the results, and close the loop on the methodology.

## Inputs
- The P9 experiment results (`<problem>_model/outputs/solutions/results.csv` + the
  battery log) and all prior artifacts (P4 visualizations, P5 formulation, P6/P8
  implementations, P7 synthesis).

## Template
- `docs/methodology/templates/report.template.tex`.

## Steps
1. Copy the template into `docs/<problem>/report.tex` and wire it into the LaTeX
   harness (`main.tex`); compile to verify.
2. **Document the algorithm(s)** — Methods section: the exact model (summarise the
   P5 formulation: sets/variables/objective) and each heuristic (P8: constructive
   + evaluator + metaheuristic loop). State they emit the same solution schema and
   pass the P3 checker.
3. **Document the results** — Experimental setup (benchmark table, harness,
   compliance gate, gap convention, reproducibility) and a Results table straight
   from the P9 ledger: per-instance objective + status + time for each method, and
   the gap. Then a Discussion: where the exact method proves optimality vs where
   it stalls; feasibility; and **honest caveats** (benchmark scale, noise floor,
   unclosed-MILP cases).
4. **Conclusions & recommendations** — which technique/config to use, at what
   cost/quality, and the next study.
5. **Methodology retrospective** — what worked (phases, templates, the checker as
   a compliance gate, the experiment harness, the method review) and what to
   improve for the next problem.

## Reusable asset
- Refresh `templates/report.template.tex` if the report's structure generalized.

## Done when
- The report compiles (if LaTeX), documents both the algorithm(s) and the P9
  results with honest caveats, and the retrospective is captured.

## Governance
- Invoke `methodology-curator` to record P10 and log retrospective items as
  decisions/improvements.
- Run a final `methodology-auditor` consistency pass over the whole methodology.
