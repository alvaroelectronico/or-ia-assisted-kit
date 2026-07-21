# Methodology — From Problem Description to Solution

A reproducible, LLM/agent-assisted method for going from **a written problem
description** to **a working solution built with some technique** (heuristic,
MILP, or other), and for **capturing that process as reusable assets** so it can
be repeated in similar future contexts.

**Your problem** is the worked example (case study) that exercises and matures
this methodology. Everything in this reusable layer must stay usable independently
of any single case — templates carry `<PLACEHOLDER>`s, skills refer to a generic
`<problem>` and a `<problem>_model/` code package.

> All methodology content is written in **English**.

---

## 1. Core principle — two layers per artifact

Every artifact we produce has two layers:

1. **Instance layer** — the concrete content for the problem at hand (e.g. the
   MILP for *your* problem).
2. **Template layer** — the generalized, reusable version of it (e.g. a MILP
   formulation template with placeholders and guidance).

When we finish a piece of concrete work, we **systematize** it: extract or
update the template layer so the next problem starts from a mold, not a blank
page.

---

## 2. Phases

Each phase consumes the previous phase's output, produces a concrete artifact,
and yields a reusable asset. A phase is **done** only when both its concrete
artifact and its extracted/updated asset are recorded in the registry.

| ID | Phase | Concrete output | Reusable asset (template/skill) |
|----|-------|-----------------|---------------------------------|
| P0 | **Intake & scoping** | Raw problem statement + clarifying Q&A captured | Intake checklist |
| P1 | **Formalization** | *Decision / Requirements / Objective / Input* spec | Problem-description template |
| P2 | **Data model & instances** | Data-model document (`.tex`) + input schema + synthetic instance generator | Data-model + instance-schema + generator template |
| P3 | **Solution model & checker** | Solution schema + requirement checker (one `check_rqXX` per RQ) + checks schema | Solution-schema + solution-checker template |
| P4 | **Solution visualization** | Case-specific renderer: static image or dynamic animation/HTML via the `visualize()` contract | Visualization contract + static & dynamic skeletons |
| P5 | **MILP formulation** | Sets, params, variables, constraints, objective (`.tex`, mathematical model only — no code) | MILP formulation template |
| P6 | **MILP implementation** | Executable model (code) realizing the P5 formulation, running on the generated instances | MILP implementation template |
| P7 | **Method review & transfer** | Per-source digests + a synthesis with 2–4 candidate approaches (each tagged for the MILP and/or heuristic phase) | digest + synthesis agents/skills (theory-paper-digest / theory-synthesize; digest-paper / synthesize-theory) |
| P8 | **Heuristic design** | Constructive logic + local search / metaheuristic | Heuristic design template |
| P9 | **Experimentation & comparison** | Runs of each technique over instances; KPIs; exact-vs-heuristic gap; tables/figures | Experiment-runner template + experiment-protocol template |
| P10 | **Reporting & synthesis** | Conclusions report + methodology retrospective | Report template (`templates/report.template.tex`) |
| P11 | **Scientific paper** *(optional)* | Related-work review + bibliography + a journal-style manuscript draft | paper skeleton template + litreview/write skills & agents |

Phases are not strictly linear — later phases feed corrections back to earlier
ones (e.g. an MILP forces the formalization to be sharpened). Every such loop is
logged as a decision.

> **P9 is systematic, not ad hoc.** The experiment harness dual-logs every run
> (rich per-run JSON + an append-only CSV ledger), gates every solution through
> the P3 checker, caches the exact baseline, and compares with one fixed gap
> convention (`(baseline − method)/baseline`, plus absolute Δ). The detail lives
> in the P9 skill and the experiment-runner + experiment-protocol templates.

> **Requirement traceability.** Requirements carry stable `[RQxx]` IDs assigned
> in P1 (never reused or renumbered). The P3 checker verifies them one-to-one —
> one `check_rqXX` method per `[RQxx]`. On cornflow projects the checker reuses
> `ExperimentCore.check()`, which auto-discovers every `check_*` method and
> returns only the non-empty results (empty ⇒ feasible), rather than a custom
> runner.

> **Document algorithms in detail.** The algorithm phases (P5 formulation, P6
> implementation, P8 heuristic) each produce a **detailed** description — per-stage
> pseudocode, the objective/evaluator, complexity, a parameter table, design
> rationale, a worked micro-example, and limitations — as a dedicated doc (e.g.
> `docs/<problem>/heuristic.tex`), not merely the P10 report summary. The
> template layer of this convention is
> [`templates/algorithm-doc.template.tex`](templates/algorithm-doc.template.tex).

> **Solution-layer phases.** P4 visualization is a solution-layer phase and a
> sibling of the P3 checker: both consume the P3 solution schema — the checker
> *validates* a solution, the visualizer *renders* it. Because visualization is
> problem-specific and its medium varies, its reusable asset is a `visualize()`
> contract + reference skeletons; the medium (static image vs dynamic
> animation/HTML) is chosen per case.

### Phase P7 — Method review & transfer (how it works)

P7 surveys **existing techniques** (papers, book chapters, prior solutions)
before committing to the algorithmic approach. It is realized not by a single
`p7-*` driver skill but by **two skills + two agents**:

- **`/digest-paper <path> [focus]`** (skill) → **`theory-paper-digest`** (agent)
  — reads **ONE** source and writes a **structured transfer analysis**: what the
  source does and specifically *what transfers* to the problem at hand, tied
  back to the problem's `[RQxx]` requirements, decisions and objective. One
  digest per source.
- **`/synthesize-theory [focus]`** (skill) → **`theory-synthesize`** (agent) —
  **cross-reads** the digests and distils **2–4 candidate approaches** (each with
  effort/fit trade-offs and a recommendation, tagged for the MILP and/or
  heuristic phase).

**Sequencing.** Run P7 **after P6 (MILP implementation)**. It feeds **P8
(heuristic design)** primarily, and can also feed the **MILP** side — candidate
matheuristics reuse the P5 formulation / P6 implementation.

**Folder convention.** P7 outputs live under `docs/<problem>/theory/`:

- `inspiration/` — the raw sources under review (papers, chapters).
- `digests/` — one transfer-analysis digest per source (from `digest-paper`).
- `synthesis.md` — the cross-source synthesis with candidate approaches (from
  `synthesize-theory`).

**Curate, don't exhaust.** You are not required to digest every available
source. Pick a **relevant subset** for the problem and **log what you skipped**
(and why it was out of scope, plus that it remains available on request) — never
silently truncate the corpus. The registry records the coverage limit so the
audit trail stays honest.

### Phase P11 — Scientific paper (optional)

P11 is an **OPTIONAL** final phase: it does **not** gate methodology completion
(the methodology is complete at P10). When a submittable write-up is wanted, P11
turns the finished case study (the P0–P10 artifacts) into a **scientific-journal
manuscript**. Like P7, it has **no single `p11-*` driver skill** — it is realized
by **two skills + two agents**:

- **`/paper-litreview [focus]`** (skill) → **`paper-bibreviewer`** (agent) —
  builds the paper's **related-work positioning** + a **BibTeX bibliography** from
  the case artifacts, the **P7 digests** (reused, not re-digested), user-provided
  sources, and (if available) a literature search. Outputs
  `docs/<problem>/paper/related_work.tex` + `references.bib`. This is scholarly
  **positioning for publication** ("unlike X, we …"), *distinct* from P7's
  method-transfer analysis — but it **reuses P7's digests** as its starting corpus.
- **`/paper-write [target-journal-or-style]`** (skill) → **`paper-writer`** (agent)
  — drafts `docs/<problem>/paper/paper.tex` in scientific-journal style,
  **adapting** to a target journal's structure, tone and citation conventions
  (inferred from a journal name, an author-guide URL, or example papers under
  `docs/<problem>/paper/style/`; neutral `article` default when none is given). It
  consumes the P0–P10 artifacts + the P11 related-work + bibliography and applies
  the paper skeleton template.

**Folder convention.** P11 outputs live under `docs/<problem>/paper/`:

- `sources/` — user-provided source material for the review.
- `style/` — target-journal example papers / author guides (style reference).
- `related_work.tex` + `references.bib` — from `paper-litreview`.
- `paper.tex` — the manuscript draft from `paper-write`.

The reusable asset is the journal-agnostic skeleton
[`templates/paper.template.tex`](templates/paper.template.tex) (title/authors,
abstract, keywords, introduction + explicit contribution bullets, related work
`\input`, problem statement, methods, experiments & results, discussion,
conclusions & future work, references). No invented numbers or citations: results
trace to the P9 ledger / P10 report, citations resolve in `references.bib`, and
the report's honest caveats are carried over.

---

## 3. Asset types

- **Templates** — parameterized documents/code with placeholders and guidance. Live in [`templates/`](templates/).
- **Skills** — Claude Code skills that execute a phase. Most phases have a single
  driver skill in `.claude/skills/` (`p0-intake`, `p1-formalize`, `p2-data-model`,
  `p3-solution-checker`, `p4-visualize`, `p5-formulate-milp`, `p6-implement-milp`,
  `p8-heuristic`, `p9-experiments`, `p10-report`); each states the phase's inputs,
  steps, done-when and governance, and applies that phase's template(s). **Phase
  P7 (Method review & transfer) and the optional P11 (Scientific paper) are the
  exceptions**: P7 has no single `p7-*` driver skill but is realized by the two
  skills `digest-paper` and `synthesize-theory`, and P11 likewise by the two
  skills `paper-litreview` and `paper-write` (each dispatching to an agent — see
  §2's "Phase P7" / "Phase P11" subsections).
  Optional per-phase *agents* (e.g. a formulation/heuristic design panel for
  P5/P8, a fan-out runner for P9) may be added later. All skills are registered in
  the registry's Assets section.
- **Agent prompts** — the governance agents in `.claude/agents/` (see §4), plus
  the phase-P7 *method-review* agents `theory-paper-digest` and `theory-synthesize`
  (see §2's "Phase P7 — Method review & transfer" subsection) and the optional
  phase-P11 *paper* agents `paper-bibreviewer` and `paper-writer` (see §2's "Phase
  P11 — Scientific paper (optional)" subsection).

---

## 4. Governance — how the methodology is recorded and systematized

Two agents govern this methodology; neither solves the domain problem, they keep
the *method* honest and reusable:

- **`methodology-curator`** — after concrete work is produced, it **records**
  progress into [`registry.md`](registry.md) (assets, case-study status,
  decision log) and **systematizes** the work by extracting/updating the
  matching template. It is the only writer of the registry and of `templates/`.
- **`methodology-auditor`** — read-only. It **audits** consistency and
  completeness: does each concrete artifact conform to its template, are the
  case study and the generic assets in sync, what is missing or drifting. It
  reports gaps; the curator acts on them.

Typical loop: do the concrete phase work → invoke `methodology-curator` to
record + systematize → periodically invoke `methodology-auditor` to check for
drift and gaps.

---

## 5. Directory map

```
docs/methodology/
  README.md        # this playbook
  registry.md      # living registry: assets, case-study status, decision log
  templates/       # reusable templates (the systematized layer)
docs/<problem>/theory/   # phase P7 method-review outputs (per problem)
  inspiration/     # raw sources under review
  digests/         # one transfer-analysis digest per source
  synthesis.md     # cross-source synthesis + candidate approaches
docs/<problem>/paper/    # phase P11 (optional) scientific-paper outputs (per problem)
  sources/         # user-provided source material for the review
  style/           # target-journal example papers / author guides
  related_work.tex # from paper-litreview
  references.bib   # from paper-litreview
  paper.tex        # manuscript draft from paper-write
.claude/skills/    # per-phase driver skills (one per phase except P7 and P11)
  p0-intake/ p1-formalize/ p2-data-model/ p3-solution-checker/
  p4-visualize/ p5-formulate-milp/ p6-implement-milp/
  p8-heuristic/ p9-experiments/ p10-report/
  digest-paper/ synthesize-theory/   # phase P7 method-review skills (no p7-* driver)
  paper-litreview/ paper-write/       # phase P11 paper skills (no p11-* driver)
.claude/agents/
  methodology-curator.md
  methodology-auditor.md
  theory-paper-digest.md              # phase P7: one source → transfer analysis
  theory-synthesize.md                # phase P7: digests → candidate approaches
  paper-bibreviewer.md                # phase P11: related work + bibliography
  paper-writer.md                     # phase P11: journal-style manuscript draft
```
