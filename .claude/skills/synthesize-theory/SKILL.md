---
name: synthesize-theory
description: >
  Phase P7 (Method review & transfer) — synthesize all digests under docs/<problem>/theory/digests/
  into docs/<problem>/theory/synthesis.md, with convergent themes, distinct angles and
  2–4 concrete candidate approaches. Usage: `/synthesize-theory [focus]`. Dispatches to
  the `theory-synthesize` subagent.
arguments: focus
context: fork
agent: theory-synthesize
---

Produce the method-review synthesis for the current problem.

Optional focus from the user: **$focus**

Follow the workflow in your agent system prompt:

1. Glob and read every file under `docs/<problem>/theory/digests/*.md`.
2. Read `docs/<problem>/problem_description.tex` (Decision, Requirements `[RQxx]`,
   Objective, Input).
3. Do NOT read the original sources (already digested) or the solver code.
4. Write the synthesis to `docs/<problem>/theory/synthesis.md` using the template in the
   agent prompt. Sort the "Digests considered" table by verdict (High → Medium → Low).
5. Return a short summary: the 2–4 candidate names (one line each) and your single
   highest-confidence recommendation.

Each candidate must say which phase it targets — the MILP formulation and/or the
heuristic design phase. If a focus is given (e.g. "GRASP-heavy", "matheuristic"), bias the
candidates you put forward, but list any high-verdict transfers you'd be cutting under
**Open questions** so the human can override.
