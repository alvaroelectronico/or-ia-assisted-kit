---
name: paper-write
description: >
  Phase P11 (optional — Scientific paper) — draft the manuscript in scientific-
  journal style, ADAPTING to a target journal's structure, tone and citation
  conventions. Assembles docs/<problem>/paper/paper.tex from the case artifacts +
  the P11 related-work + bibliography. Usage: `/paper-write [target-journal-or-style]`.
  Dispatches to the `paper-writer` subagent.
arguments: style_target
context: fork
agent: paper-writer
---

Draft the scientific paper.

Style target from the user (journal name, author-guide URL, or example papers):
**$style_target**

Follow your agent system prompt:
1. Establish the target style — infer section structure, tone, length norms and
   citation format from the given journal / author guide / example papers under
   `docs/<problem>/paper/style/`. If none is given, use a neutral `article` class
   and state the assumption.
2. Apply the paper skeleton `docs/methodology/templates/paper.template.tex`; draft
   each section from the case artifacts (P0–P10): abstract, intro (+ contribution
   bullets), related work (`\input` the P11 `related_work.tex`), problem statement,
   methods (exact + heuristic — summarise, cite the detailed docs), experiments &
   results (tables/gaps from `report.tex` / the P9 ledger), discussion,
   conclusions, references (`references.bib`).
3. Write `docs/<problem>/paper/paper.tex` (compiles); return the chosen style, the
   section list, and any TODO placeholders.

No invented numbers or citations: results trace to the report/ledger; citations
resolve in `references.bib`. Carry over the report's honest caveats. Adapt to the
target journal; when unsure, follow the template and note the assumption.
