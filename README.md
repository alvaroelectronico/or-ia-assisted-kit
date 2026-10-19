# Methodology Kit — from *problem description* to *solution*

A **portable, reusable methodology** for taking a written combinatorial-optimization
problem from a plain description to a working, verified solution (heuristics **and**
a MILP, compared). It is designed to be run with Claude Code (skills + subagents)
and has lightweight governance that keeps the process reproducible.

Everything here is problem-agnostic: templates use `<PLACEHOLDER>`s, and skills refer
to a generic `<problem>` and a `<problem>_model/` code package. Each repository that
uses the kit binds those placeholders once, in its registry (§0 *Project binding*).

Version: see [`VERSION`](VERSION) · history: [`CHANGELOG.md`](CHANGELOG.md).

---

## 1. What's inside

```
or-ia-assisted-kit/
  README.md                ← this file: what the kit is + how to reuse it
  VERSION, CHANGELOG.md    ← kit version (semver) and release notes
  kit.py                   ← install / status / update / resolve / promote / doctor
  claude-snippet.md        ← block injected into the target repo's CLAUDE.md
  tests/test_kit.py        ← tests for kit.py
  .claude/
    skills/   (14)         ← phase driver skills p0-intake … p10-report (no P7 driver)
                             + P7 method review: digest-paper, synthesize-theory
                             + P11 paper (optional): paper-litreview, paper-write
    agents/   (6)          ← governance: methodology-curator, methodology-auditor
                             + P7: theory-paper-digest, theory-synthesize
                             + P11: paper-bibreviewer, paper-writer
  docs/methodology/
    README.md              ← the PLAYBOOK (phases, two-layer principle, governance)
    registry.md            ← per-repo living log — ships BLANK (binding, assets, status, decisions)
    templates/  (17)       ← the reusable layer
```

Only `.claude/skills/`, `.claude/agents/`, `docs/methodology/README.md` and
`docs/methodology/templates/` are copied into a target repo and kept in sync
(**kit-managed**). `registry.md` is copied once and then belongs to the target. The
kit's own `README.md`, `kit.py`, `tests/`, `VERSION` and `CHANGELOG.md` stay in the
kit.

> The Python templates are **fill-in skeletons**: they contain `<PLACEHOLDER>`
> tokens and are not importable until filled. They are copied into the case's
> code package and completed during the matching phase. They are not a library.

## 2. The phases

| ID | Phase | Produces | Skill |
|----|-------|----------|-------|
| P0 | Intake & scoping | Scoped brief + Project binding | `p0-intake` |
| P1 | Formalization | Decision / Requirements (`[RQxx]`) / Objective / Input | `p1-formalize` |
| P2 | Data model & instances | Data model + JSON schema + instance generator | `p2-data-model` |
| P3 | Solution model & checker | Solution schema + per-requirement checker | `p3-solution-checker` |
| P4 | Solution visualization | Case-specific renderer (static image or dynamic HTML) | `p4-visualize` |
| P5 | MILP formulation | Mathematical model (LaTeX, no code) | `p5-formulate-milp` |
| P6 | MILP implementation | Executable model (Pyomo + solver) | `p6-implement-milp` |
| P7 | Method review & transfer | Per-source digests + 2–4 candidate approaches | `digest-paper` + `synthesize-theory` |
| P8 | Heuristic design | Constructive + local-search heuristic (from a P7 candidate) | `p8-heuristic` |
| P9 | Experimentation & comparison | Logged battery, KPIs, exact-vs-heuristic gap | `p9-experiments` |
| P10 | Reporting & synthesis | Conclusions + methodology retrospective | `p10-report` |
| P11 | Scientific paper *(optional)* | Related work + bibliography + journal-style draft | `paper-litreview` + `paper-write` |

The playbook ([`docs/methodology/README.md`](docs/methodology/README.md)) is the
authoritative description: the two-layer (instance + template) principle, the P7 and
P11 workflows, the governance loop and the folder conventions.

---

## 3. How the kit is reused across repositories

**Decision:** the kit lives in **its own git repository** and is the single source of
truth for the reusable layer. Each project that uses it receives a **copy** of the
kit-managed files plus a lock file, `.methodology-kit.lock.json`, written and read
by `kit.py`. The lock records the kit version and, per file, the hash of the kit
content it was installed from. That gives a three-way comparison for every file:

| local vs base | kit vs base | state | what `update` does |
|---|---|---|---|
| same | same | `ok` | nothing |
| changed | same | `local` (template matured here) | keeps it; candidate for `promote` |
| same | changed | `upstream` (kit improved) | overwrites with the kit version |
| changed | changed | `conflict` | writes `<file>.kit-new` next to it for a manual merge |

Changes flow both ways:

```
            kit.py install / update
  kit repo ───────────────────────────▶ project repo (copy + lock)
     ▲                                        │
     └──────────── kit.py promote ────────────┘
        (only generic improvements; case-specific terms are blocked)
```

**Why copies instead of the alternatives:**

- **Git submodule / subtree:** Claude Code does pick up a nested `.claude/` (e.g.
  `vendor/methodology-kit/.claude/`), but only **scoped to that subfolder**, so the
  skills would not apply to the project's own `docs/` and code. Symlinking the
  folders into the root is fragile on Windows. A submodule mounted at `.claude/`
  would take over that folder, so the project couldn't keep its own skills or
  settings there.
- **Claude Code plugin:** good for distributing skills and agents. However, the
  methodology expects the `methodology-curator` agent to *edit the templates inside
  the project* as they mature. Plugin files live in a user-level cache outside the
  repo, are not versioned with the project, and are replaced on plugin update.
  Plugin skills are also namespaced (`/<plugin>:p0-intake`), which breaks the plain
  names the skills and playbook use to refer to each other. A plugin could be
  revisited for the skills and agents alone if the templates ever become stable.
- **Hand copying (what v1.0 did):** it drifted. Fifteen files had diverged between the
  case study and the exported kit by the time it was reviewed. `kit.py` makes the
  divergence visible (`status`) and recoverable (`update`, `promote`).

---

## 4. Instructions

Requirements: Git, Python ≥ 3.10 (standard library only for `kit.py`), Claude Code
(CLI, desktop or VS Code extension). All commands work in Git Bash and PowerShell;
paths below assume the kit is cloned **next to** your projects:

```
repos/
  or-ia-assisted-kit/   ← the kit repo
  my-new-problem/       ← a project that uses it
```

### 4.1 One time: get the kit

```bash
cd repos                               # the folder that holds your projects
git clone https://github.com/alvaroelectronico/or-ia-assisted-kit.git
cd or-ia-assisted-kit
python -m unittest discover tests      # kit.py tests
python kit.py doctor                   # kit self-consistency
```

The kit was extracted, with its history, from the warehouse case-study repository
(`parfois-calculo-previo-almacen`), which now uses it like any other project.
**Edit generic assets in the kit repo** (or promote them from a project, §4.5),
never by copying files by hand.

### 4.2 Start a new project with the kit

```bash
cd ../my-new-problem                   # an existing git repo (can be empty)
python ../or-ia-assisted-kit/kit.py install .
```

This:
- copies the 14 skills, 6 agents, the playbook and 17 templates;
- seeds a blank `docs/methodology/registry.md` (only if there is none);
- appends the kit block to `CLAUDE.md` (it is created if missing). The block sits
  between `<!-- methodology-kit:start/end -->` markers and is refreshed on every
  `update`, so write your own notes outside it;
- writes `.methodology-kit.lock.json`.

If a file already exists with different content (e.g. the project has its own
`.claude/skills/p0-intake/`), `install` stops and lists the clashes. Re-run with
`--adopt` to keep your versions and track them as local changes, or `--force` to
overwrite them with the kit's.

Then:

1. **Commit** the result (`.claude/`, `docs/methodology/`, `CLAUDE.md`,
   `.methodology-kit.lock.json`). The lock file must be versioned; it is what makes
   later updates safe.
2. **Open a new Claude Code session** in the project so it discovers the skills and
   agents. In VS Code, start a new chat or run *Developer: Reload Window*. Typing `/`
   should list `p0-intake` … `p10-report`.
3. **Run `/p0-intake`** with the raw problem description. Besides the scoped brief,
   P0 fills **registry §0 Project binding**: the problem slug (→ `docs/<slug>/`),
   the code package (→ `<slug>_model/`), the objective sense and cornflow yes/no.
   Every later skill reads those values.
4. *(Recommended)* List the project's domain words in the lock's
   `"forbidden_terms"` (e.g. `["vehicle", "depot", "acme"]`). `promote` then refuses
   to send any file that mentions them back to the kit. The slug and package from §0
   are blocked automatically.

### 4.3 Work the phases

- Invoke each phase skill in order (`/p1-formalize`, `/p2-data-model`, …), or ask
  Claude to "use skill `p3-solution-checker`". Each skill names its inputs, its
  template(s), its steps and when it is done.
- P7 is two skills: `/digest-paper <path-to-pdf> [focus]` once per source, then
  `/synthesize-theory`. P11 (optional) is `/paper-litreview` then
  `/paper-write <journal>`.
- **Governance loop:** after each phase, ask Claude to invoke `methodology-curator`
  (it records progress in the registry and refreshes the template). Before moving
  to the next phase, ask it to run `methodology-auditor` (read-only drift report).
- The curator is *expected* to improve templates in place. Those edits show up as
  `local` in `kit.py status` and can be promoted later (§4.5).

### 4.4 Pull kit improvements into a project

```bash
git -C ../or-ia-assisted-kit pull
python ../or-ia-assisted-kit/kit.py status .            # what differs, per file
python ../or-ia-assisted-kit/kit.py update . --dry-run  # what would change
python ../or-ia-assisted-kit/kit.py update .
```

- `upstream` files are overwritten; `local` files are left alone; files the kit
  added are copied; files the kit dropped are deleted if you never touched them;
  files you deleted are restored.
- Each `conflict` gets a `<file>.kit-new` next to it (exit code 1). Merge it into
  `<file>` by hand (or ask Claude to merge it), then:
  ```bash
  python ../or-ia-assisted-kit/kit.py resolve . docs/methodology/templates/report.template.tex
  ```
  This deletes the `.kit-new` file and records the merge. Don't commit `.kit-new`
  files.
- Read `CHANGELOG.md` for the version jump. A **major** bump means names or layout
  changed and the registry may need a decision-log entry.
- Commit the updated files and lock file in the project.

### 4.5 Send improvements from a project back to the kit

When a template or skill matured during a project in a way that helps *any*
problem:

```bash
python ../or-ia-assisted-kit/kit.py status .                    # `local` = candidates
python ../or-ia-assisted-kit/kit.py promote .                   # preview diffs
python ../or-ia-assisted-kit/kit.py promote . <file> --apply    # copy selected files
```

- Files with case-specific terms (`forbidden_terms` + the §0 slug/package) are
  **blocked**. Rewrite those passages with `<PLACEHOLDER>`s first, or use `--force`
  if a term is a false positive.
- `conflict` files are blocked until you `update` and merge.
- Then finish in the kit repo:
  ```bash
  cd ../or-ia-assisted-kit
  python kit.py doctor --forbid <domain words of that project>
  python -m unittest discover tests
  # bump VERSION, add a CHANGELOG entry, commit, open a PR
  ```
- Other projects receive the change on their next `update`.

### 4.6 Adopt the kit in a repo that already has the methodology

Use this for the original case-study repository, or any repo seeded by hand-copying
the kit:

```bash
python ../or-ia-assisted-kit/kit.py install . --adopt
python ../or-ia-assisted-kit/kit.py status .
```

`--adopt` keeps every differing file and marks it `local`; the existing registry is
never touched. Then go through the `local` files. Where only case references differ
(e.g. `docs/<case>/` instead of `docs/<problem>/`), it is usually best to take the
kit version: restore it with `git checkout`/delete the file and run `update`, and
rely on §0 Project binding instead. Promote the files that contain real
improvements.

### 4.7 Troubleshooting

| Symptom | Fix |
|---|---|
| `/p0-intake` not listed | Start a new Claude Code session (skills are discovered at session start). |
| Skill names collide with the project's own skills | `install` reports the clash. Rename the project skill, or `--adopt` and merge by hand. |
| Every file shows `local` after a fresh clone on Windows | Shouldn't happen: hashes ignore CRLF/LF. Check that a formatter didn't rewrite the files (e.g. Black on templates). |
| `update` exits with code 1 | There are conflicts. Merge each `.kit-new` and `resolve`. |
| `promote` says `blocked` | A forbidden/case term was found. Generalize the text or use `--force`. |
| `error: … has no .methodology-kit.lock.json` | Run `install` first (or `install --adopt` for an existing setup). |

---

## 5. Core conventions (details in the playbook)

- **Two layers per artifact.** Everything you make has an *instance* (your problem's
  concrete artifact) and a *template* (its generalized, reusable form). The curator
  keeps the template layer in sync.
- **English** for all generated content (docs, LaTeX, comments).
- **Model naming (hard rule).** Parameters **UPPERCASE**, decision variables
  **lowercase**, sets calligraphic.
- **Requirement traceability.** Each requirement gets a stable `[RQxx]` ID in P1;
  the P3 checker verifies them one-to-one (`check_rqXX`).
- **Solution checking.** On cornflow projects, reuse `ExperimentCore.check()` (it
  auto-runs every `check_*` method; an empty result means feasible). The checker
  template also ships a dependency-free fallback.
- **Visualization** is a *contract* (`visualize(instance, solution, out_path)`) with
  pluggable static and dynamic backends; the medium is chosen per case.
- **Experiments** are systematic: every run passes the P3 checker, is logged twice
  (JSON + CSV ledger), and is compared with one fixed gap convention plus the
  absolute Δ.

## 6. Dependencies of the project code (phases P2–P9)

- Python 3.10+ (the standard library covers P2/P3 and the P9 harness).
- For the MILP (P6): `pyomo` + a solver. Use **Gurobi** (`gurobipy`; pin the major
  version to your local Gurobi **license**) or the license-free **HiGHS** (`highspy`).
- P4 static backend: `matplotlib`. Optional: `jsonschema` (validate instances and
  solutions against the schemas); `cornflow-client` if the project is a cornflow app.
- LaTeX docs: a TeX distribution with `pdflatex`.

```bash
pip install pyomo jsonschema matplotlib
pip install "gurobipy<13"     # match your Gurobi license major version, OR:
pip install highspy           # license-free alternative
```

## 7. Maintaining the kit

- `python kit.py doctor [--forbid TERM ...]` checks that skill and agent frontmatter
  names match their folders and files, that agents referenced by skills exist, that
  every `templates/…` path and `pN-…` skill mentioned anywhere exists, that registry
  asset rows point at shipped files, and (optionally) that no forbidden term appears.
- `python -m unittest discover tests` tests `kit.py` against a disposable copy of
  the kit.
- Versioning: **major** = a phase, a skill/agent name or the file layout changes;
  **minor** = new templates, skills or guidance; **patch** = fixes. Record every
  release in `CHANGELOG.md`.
- Keep the shipped `registry.md` blank in §0, §B and §C. Only §A (the asset list)
  carries content.
