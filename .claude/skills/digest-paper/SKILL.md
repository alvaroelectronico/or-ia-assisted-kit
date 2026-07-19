---
name: digest-paper
description: >
  Phase P7 (Method review & transfer) — digest ONE source (paper/chapter) into a structured
  transfer analysis under docs/<problem>/theory/digests/. Usage: `/digest-paper
  <source_path> [focus]`. Dispatches to the `theory-paper-digest` subagent.
arguments: source_path focus
context: fork
agent: theory-paper-digest
---

Digest the source at: **$source_path**

Optional focus from the user: **$focus**

Follow the workflow and template in your agent system prompt:

1. Read `docs/<problem>/problem_description.tex` first (the P1 formalization: Decision,
   Requirements `[RQxx]`, Objective, Input).
2. Read the source (chunk PDFs by pages: start with pages 1–5).
3. Check existing digests under `docs/<problem>/theory/digests/` to cross-reference and
   avoid repetition.
4. Write the digest to `docs/<problem>/theory/digests/<slug>.md`, where `<slug>` is the
   source basename without its extension.
5. Return a short summary: title, verdict (High/Medium/Low), and the single most
   transferable idea.

Tie the **What transfers** analysis to our problem's `[RQxx]` requirements, decisions
and objective. Do NOT read the solver/implementation code or unrelated repo areas —
only the source, the problem formalization, and existing digests. If the focus names a
specific angle (e.g. "construction heuristics", "a given requirement"), bias the
**What transfers** section toward it.
