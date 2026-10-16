# Methodology Registry

Living record of the methodology **for this project**. Maintained by the
**`methodology-curator`** agent; audited by **`methodology-auditor`**. Humans may
read it freely but edits should go through the curator to keep it consistent.

> This is the **fresh registry that ships with the methodology kit**. §A lists the
> reusable assets bundled in the kit; §B and §C start empty — you fill them as you
> apply the phases to *your* problem.

Four sections: **Project binding** (what the generic placeholders mean in this
repo), **Assets** (the reusable layer), **Case-study status** (progress of your
problem), and **Decision log**.

---

## 0. Project binding

Fixed during P0 (`p0-intake`); the solver stack is fixed in P6. Skills, agents
and templates resolve `<problem>` and `<problem>_model` from this table.

| Key | Value | Notes |
|-----|-------|-------|
| Problem slug `<problem>` | `<problem>` | docs live in `docs/<problem>/`; P7/P11 outputs in `docs/<problem>/theory/`, `docs/<problem>/paper/` |
| Code package `<problem>_model` | `<problem>_model` | importable Python package at the repo root |
| Objective sense | `<minimize / maximize>` | drives the P9 gap sign |
| Cornflow app | `<yes / no>` | yes ⇒ P3 checker subclasses `ExperimentCore`; no ⇒ stdlib mixin fallback |
| Solver stack | `<e.g. Pyomo + Gurobi (gurobi_direct) / Pyomo + HiGHS>` | fixed in P6 |

---

## A. Assets (reusable layer)

Bundled with the kit. Status: `planned` / `draft` / `stable`. `Type` is `template`
or `skill`. Templates live in `templates/`; skills are driver skills under
`.claude/skills/`.

**Accounting notes.**
- **Asset IDs are stable handles** — never renumbered once assigned; the **Phase**
  column tracks the current phase number.
- **Governance agents** (`methodology-curator`, `methodology-auditor`), the
  **phase-P7 method-review agents** (`theory-paper-digest`, `theory-synthesize`),
  and the **phase-P11 paper agents** (`paper-bibreviewer`, `paper-writer`) live in
  `.claude/agents/` — tracked here as a note, not as asset rows.
- **Phase P7 (Method review & transfer)** has no single `p7-*` driver skill; it is
  realized by the two skills `digest-paper` + `synthesize-theory`.
- Package markers (`__init__.py`), the LaTeX **build harness** (`main.tex` +
  `compile.py`), dependency manifests (`requirements.txt`), and the checks-output
  schema (`solution_checks.json`, whose template lives inside the checker template)
  are **exempt from the two-layer rule**.

| ID | Type | Phase | Path | Status | Notes |
|----|------|-------|------|--------|-------|
| A-P1-tpl              | template | P1 | `templates/problem-description.template.tex` | draft | Presentation + Decision/Requirements(`[RQxx]`)/Objective/Input |
| A-P2-tpl-doc          | template | P2 | `templates/data-model.template.tex` | draft | Data-model doc skeleton |
| A-P2-tpl-schema       | template | P2 | `templates/instance-schema.template.json` | draft | Instance JSON-Schema (draft-07) skeleton |
| A-P2-tpl-gen          | template | P2 | `templates/instance_generator.template.py` | draft | Seeded stdlib instance generator |
| A-P3-tpl-sol-schema   | template | P3 | `templates/solution-schema.template.json` | draft | Candidate-solution JSON-Schema skeleton |
| A-P3-tpl-sol-checker  | template | P3 | `templates/solution-checker.template.py` | draft | One `check_rqXX` per `[RQxx]`; cornflow `ExperimentCore.check()` (+ stdlib fallback) |
| A-P4-tpl-viz-contract | template | P4 | `templates/visualization-contract.template.py` | draft | `visualize(instance, solution, out_path)` contract |
| A-P4-tpl-viz-static   | template | P4 | `templates/visualize-static.template.py` | draft | matplotlib static backend skeleton |
| A-P4-tpl-viz-dynamic  | template | P4 | `templates/visualize-dynamic.template.html` | draft | self-contained HTML/JS dynamic backend skeleton |
| A-P5-tpl              | template | P5 | `templates/milp-formulation.template.tex` | draft | MILP formulation (fleets style; params UPPERCASE, vars lowercase; interleaved) |
| A-P6-tpl              | template | P6 | `templates/milp-implementation.template.py` | draft | Pyomo implementation scaffold; extracts to P3 solution schema + runs P3 checker |
| A-P8-tpl              | template | P8 | `templates/heuristic-design.template.py` | draft | Heuristic-design scaffold: constructive builder + deterministic P3-schema evaluator (reusable core) + iterated-greedy/local-search loop with multi-restart |
| A-P9-tpl-runner       | template | P9 | `templates/experiment-runner.template.py` | draft | Systematic experiment harness (benchmark × methods × configs; P3 compliance gate; dual persistence JSON + results.csv ledger; gap + absolute Δ; git/env/seed stamps) |
| A-P9-tpl-protocol     | template | P9 | `templates/experiment-protocol.template.md` | draft | Battery protocol doc skeleton (benchmark, cached baseline, gap + Δ, judging order, outputs layout, reproducibility, noise floor) |
| A-P10-tpl             | template | P10 | `templates/report.template.tex` | draft | Conclusions-report skeleton (Overview / Methods [exact + heuristic] / Experimental setup / Results table / Discussion + honest caveats / Conclusions / Methodology retrospective) |
| A-algdoc-tpl          | template | P5/P6/P8 | `templates/algorithm-doc.template.tex` | draft | Detailed-algorithm-doc skeleton (Overview / per-stage pseudocode / core routine-evaluator / complexity / parameter table / worked micro-example / rationale + limitations) — template layer of the "document algorithms in detail" convention |
| A-P11-tpl             | template | P11 | `templates/paper.template.tex` | draft | Journal-agnostic scientific-paper skeleton (title/abstract/keywords / intro + contribution bullets / related work / problem statement / methods [exact+heuristic] / experiments + results / discussion / conclusions / references); guidance to adapt document class + citation style per target journal |
| A-P0-skill  | skill | P0 | `.claude/skills/p0-intake/SKILL.md` | stable | Intake & scoping |
| A-P1-skill  | skill | P1 | `.claude/skills/p1-formalize/SKILL.md` | stable | Formalization |
| A-P2-skill  | skill | P2 | `.claude/skills/p2-data-model/SKILL.md` | stable | Data model & instances |
| A-P3-skill  | skill | P3 | `.claude/skills/p3-solution-checker/SKILL.md` | stable | Solution model & checker |
| A-P4-skill  | skill | P4 | `.claude/skills/p4-visualize/SKILL.md` | stable | Solution visualization |
| A-P5-skill  | skill | P5 | `.claude/skills/p5-formulate-milp/SKILL.md` | stable | MILP formulation |
| A-P6-skill  | skill | P6 | `.claude/skills/p6-implement-milp/SKILL.md` | stable | MILP implementation (default Pyomo+Gurobi; HiGHS fallback) |
| A-review-digest-skill | skill | P7 | `.claude/skills/digest-paper/SKILL.md` | stable | Method review: digest one source → transfer analysis (agent `theory-paper-digest`) |
| A-review-synth-skill  | skill | P7 | `.claude/skills/synthesize-theory/SKILL.md` | stable | Method review: synthesize digests → 2–4 candidate approaches (agent `theory-synthesize`) |
| A-P8-skill  | skill | P8 | `.claude/skills/p8-heuristic/SKILL.md` | stable | Heuristic design |
| A-P9-skill  | skill | P9 | `.claude/skills/p9-experiments/SKILL.md` | stable | Experimentation & comparison |
| A-P10-skill | skill | P10 | `.claude/skills/p10-report/SKILL.md` | stable | Reporting & synthesis |
| A-P11-litreview-skill | skill | P11 | `.claude/skills/paper-litreview/SKILL.md` | stable | Scientific paper (optional): related-work review + bibliography (agent `paper-bibreviewer`) |
| A-P11-write-skill     | skill | P11 | `.claude/skills/paper-write/SKILL.md` | stable | Scientific paper (optional): draft the manuscript in journal style (agent `paper-writer`) |

> Phase P0 (Intake & scoping) has no template (it is a lightweight checklist).
> All other phases P1–P10 ship at least one template.

---

## B. Case-study status (YOUR problem)

Progress of applying the methodology to your problem. Status: `not-started` /
`in-progress` / `done`. Fill artifact paths as you go.

| Phase | Status | Concrete artifact(s) | Extracted asset | Notes |
|-------|--------|----------------------|-----------------|-------|
| P0 Intake & scoping | not-started | — | — | |
| P1 Formalization | not-started | — | A-P1-tpl | |
| P2 Data model & instances | not-started | — | A-P2-tpl-* | |
| P3 Solution model & checker | not-started | — | A-P3-tpl-* | |
| P4 Solution visualization | not-started | — | A-P4-tpl-viz-* | static or dynamic per case |
| P5 MILP formulation | not-started | — | A-P5-tpl, A-algdoc-tpl | |
| P6 MILP implementation | not-started | — | A-P6-tpl | pick solver stack |
| P7 Method review & transfer | not-started | — | A-review-* | digest a curated subset → synthesis; log what you skip |
| P8 Heuristic design | not-started | — | A-P8-tpl, A-algdoc-tpl | pick a candidate from the P7 synthesis |
| P9 Experimentation & comparison | not-started | — | A-P9-tpl-runner, A-P9-tpl-protocol | compare technique(s) |
| P10 Reporting & synthesis | not-started | — | A-P10-tpl | |
| P11 Scientific paper (optional) | not-started | — | A-P11-tpl / A-P11-*-skill | OPTIONAL; turn the P0–P10 artifacts into a journal manuscript (`paper-litreview` → `paper-write`) |

---

## C. Decision log

Chronological record of **methodological** decisions (not domain decisions).
Add a row per decision: `Date | Decision | Rationale`. Use the current date;
never invent past dates.

| Date | Decision | Rationale |
|------|----------|-----------|
| | | |
