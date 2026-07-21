---
name: paper-litreview
description: >
  Phase P11 (optional — Scientific paper) — bibliographic / related-work review.
  Builds docs/<problem>/paper/related_work.tex + references.bib: the paper's
  scholarly positioning against the literature, organised by theme, with a gap
  statement. Usage: `/paper-litreview [focus]`. Dispatches to the
  `paper-bibreviewer` subagent.
arguments: focus
context: fork
agent: paper-bibreviewer
---

Build the related-work review and bibliography for the scientific paper.

Optional focus from the user: **$focus**

Follow your agent system prompt:
1. Read the case artifacts (`docs/<problem>/problem_description.tex`,
   `milp_formulation.tex`, `heuristic.tex`, `report.tex`) to state the contribution.
2. Reuse the P7 method-review digests (`docs/<problem>/theory/`) and any PDFs the
   user already dropped under `docs/<problem>/paper/sources/`; if a web search tool
   is available, locate canonical references per theme.
3. Write `docs/<problem>/paper/candidate_references.md` — the candidate list with a
   **URL + access flag** per entry (the "to-fetch" list for paywalled papers the
   user drops into `sources/`), plus `related_work.tex` (thematic groups +
   citations + gap paragraph) and `references.bib`.
4. Return: themes, key references, one-sentence gap, and the candidates still
   pending fetch. Re-run after the user adds PDFs to `sources/` to fold them in.

Never invent citations — every `\cite` key resolves in `references.bib`; mark
unverifiable sources `% TODO verify`. If a focus is given (a sub-topic or target
venue), bias the thematic emphasis toward it.
