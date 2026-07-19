# Methodology Kit — from *problem description* to *solution*

A **portable, reusable methodology** for taking a written combinatorial-optimization
problem from a plain description to a working, verified solution (heuristics **and**
a MILP, compared), LLM/agent-assisted, with lightweight governance that keeps the
whole process reproducible. Drop this kit into a brand-new project and follow the
phases.

It is a **self-contained snapshot** exported from a worked case study. Everything
here is problem-agnostic: templates use `<PLACEHOLDER>`s, skills refer to a generic
`<problem>` and a `<problem>_model/` code package.

---

## What's inside

```
methodology-kit/
  README.md                     ← you are here (what it is + how to reuse)
  .claude/
    skills/                     ← phase driver skills (p0-intake … p10-report)
                                  + 2 method-review skills for P7 (digest-paper, synthesize-theory)
    agents/                     ← 2 governance agents (curator + auditor)
                                  + 2 method-review agents (theory-paper-digest, theory-synthesize)
  docs/
    methodology/
      README.md                 ← the PLAYBOOK (phases, two-layer principle, governance)
      registry.md               ← living log — ships BLANK (fill it for your problem)
      templates/                ← the reusable layer (13 templates)
```

- **Skills** (`.claude/skills/`) — the reproducible recipe for each phase. Each one
  states its inputs, steps, done-criteria, governance, and which template(s) to apply.
- **Agents** (`.claude/agents/`) — the governance pair `methodology-curator` (records
  progress + extracts templates) and `methodology-auditor` (read-only consistency
  checks); plus the **method-review** pair `theory-paper-digest` (digest one source)
  and `theory-synthesize` (turn digests into candidate approaches) — see §"Method
  review" below.
- **Playbook** (`docs/methodology/README.md`) — the authoritative description of the
  method: the phases, the two-layer (instance + template) principle, and how the
  governance loop works.
- **Templates** (`docs/methodology/templates/`) — parameterized documents/code you
  fill in per problem (problem description, data model, instance schema + generator,
  solution schema + checker, visualization contract + backends, MILP formulation,
  MILP implementation).
- **Registry** (`docs/methodology/registry.md`) — the living record of assets,
  case-study progress, and decisions. It ships with the asset list filled and the
  case/decision sections **empty**, ready for your problem.

## The phases

| ID | Phase | Produces | Skill |
|----|-------|----------|-------|
| P0 | Intake & scoping | Scoped brief from a raw description | `p0-intake` |
| P1 | Formalization | Decision / Requirements (`[RQxx]`) / Objective / Input | `p1-formalize` |
| P2 | Data model & instances | Data model + JSON schema + instance generator | `p2-data-model` |
| P3 | Solution model & checker | Solution schema + per-requirement checker | `p3-solution-checker` |
| P4 | Solution visualization | Case-specific renderer (static image or dynamic HTML) | `p4-visualize` |
| P5 | MILP formulation | Mathematical model (LaTeX, no code) | `p5-formulate-milp` |
| P6 | MILP implementation | Executable model (Pyomo + solver) | `p6-implement-milp` |
| P7 | Method review & transfer | Per-source digests + synthesis of 2–4 candidate approaches | `digest-paper` + `synthesize-theory` |
| P8 | Heuristic design | Constructive + local-search heuristic (from a P7 candidate) | `p8-heuristic` |
| P9 | Experimentation & comparison | KPIs, exact-vs-heuristic gap | `p9-experiments` |
| P10 | Reporting & synthesis | Conclusions + methodology retrospective | `p10-report` |

Phases are not strictly linear — later phases can feed corrections back to earlier
ones; every such loop is logged in the registry.

## Phase P7 — Method review & transfer

Before committing to the heuristic, survey the literature and judge how each method
transfers to *your* problem. This is **phase P7** — run it after P6 (MILP
implementation) and before P8 (heuristic); it feeds P8 and can also feed the MILP
(matheuristic candidates reuse P5/P6). It has no single `p7-*` driver skill; it is
realized by **two skills + two agents**:

- `/digest-paper <path> [focus]` → the `theory-paper-digest` agent reads one source
  and writes `docs/<problem>/theory/digests/<slug>.md`, tying *what transfers* to
  your `[RQxx]` requirements, decisions and objective.
- `/synthesize-theory [focus]` → the `theory-synthesize` agent cross-reads all digests
  and writes `docs/<problem>/theory/synthesis.md` with 2–4 candidate approaches
  (each tagged for the MILP and/or heuristic phase) and a recommendation.

Curate a **relevant subset** of sources (don't digest everything), and log what you
skipped. Outputs live under `docs/<problem>/theory/` (`inspiration/`, `digests/`,
`synthesis.md`).

---

## How to reuse it in a project from scratch

1. **Copy the kit's `.claude/` and `docs/` into your new project's root.**
   ```bash
   cp -r methodology-kit/.claude   <new-project>/
   cp -r methodology-kit/docs      <new-project>/
   ```
   If the target already has a `.claude/`, merge (copy the `skills/` and `agents/`
   subfolders in).

2. **Start a fresh Claude Code session** in the new project so it discovers the 10
   skills (`p0-intake` … `p10-report`, plus the P7 method-review skills) and the 4
   agents. (In the VS Code extension:
   new chat, or “Developer: Reload Window”.)

3. **Work the phases in order.** Invoke each phase's skill — type `/p0-intake` (then
   `/p1-formalize`, …) or ask Claude to *use skill `pN-...`*. Each skill tells you
   exactly what to produce and applies its template(s). You create, as you go:
   - `docs/<problem>/` — the problem's docs (problem description, data model, MILP
     formulation, …), compiled by a small `main.tex` + `compile.py` harness.
   - `<problem>_model/` — the problem's code package (instance generator, schemas,
     solution checker, MILP model, heuristics, visualizer).

4. **Run the governance loop.** After a phase produces something, invoke
   `methodology-curator` to record it in `registry.md` and extract/update its
   template. Before moving between phases, invoke `methodology-auditor` to catch
   drift. The registry is your living log for the new problem.

5. **Repeat** through P10. By the end you have both a solution and an updated,
   more-mature set of templates for the *next* problem.

### Quick start (TL;DR)
> Copy `.claude/` + `docs/` → new session → `/p0-intake` → follow each skill P0→P10,
> invoking `methodology-curator` after each phase and `methodology-auditor` between
> phases.

---

## Core conventions (details in the playbook)

- **Two layers per artifact.** Everything you make has an *instance* (your problem's
  concrete artifact) and a *template* (its generalized, reusable form). The curator
  keeps the template layer in sync.
- **English** for all generated content (docs, LaTeX, comments).
- **Model naming (hard rule).** Parameters **UPPERCASE**, decision variables
  **lowercase**, sets calligraphic — so data vs decisions is obvious at a glance.
- **Requirement traceability.** Each requirement gets a stable `[RQxx]` ID in P1;
  the P3 checker verifies them one-to-one (`check_rqXX`).
- **Solution checking.** On cornflow projects, reuse `ExperimentCore.check()` (it
  auto-runs every `check_*` method; empty result ⇒ feasible). A dependency-free
  fallback is included.
- **Visualization** is a *contract* (`visualize(instance, solution, out_path)`) with
  pluggable static/dynamic backends — the medium is chosen per case.

## Dependencies (code phases P2/P3/P6/P7)

- Python 3.10+ (standard library covers P2/P3).
- For the MILP (P6): `pyomo` + a solver — **Gurobi** (`gurobipy`, pin the major
  version to your local Gurobi **license**) or the license-free **HiGHS** (`highspy`).
- Optional: `jsonschema` (validate instances/solutions against the schemas).

```bash
pip install pyomo jsonschema
pip install "gurobipy<13"     # match your Gurobi license major version, OR:
pip install highspy           # license-free alternative
```

## Governance agents

- **`methodology-curator`** (read/write) — after concrete work is produced, records
  progress in `registry.md` and extracts/updates the matching template. Sole writer
  of the registry and templates.
- **`methodology-auditor`** (read-only) — audits consistency/fidelity between
  templates, artifacts, and the registry; reports fixes for the curator.

---

*Keep this kit in sync if the methodology evolves in the source project: re-export
`docs/methodology/` (playbook + templates), `.claude/skills/`, and `.claude/agents/`,
and reset `registry.md`'s case-study and decision-log sections.*
