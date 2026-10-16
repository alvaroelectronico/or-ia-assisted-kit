# Changelog

All notable changes to the methodology kit. Versions follow semver:
**major** = a phase, skill/agent name or file layout changes (targets must
adapt); **minor** = new templates/skills or new guidance; **patch** = fixes.

## 1.1.0 — 2026-10-16

- Added `kit.py` (install / status / update / resolve / promote / doctor) and a
  lock file (`.methodology-kit.lock.json`) for three-way syncing between the kit
  and the repositories that use it.
- Added registry **§0 Project binding** (problem slug, code package, objective
  sense, cornflow yes/no, solver stack); P0 now fills it and the playbook tells
  every phase to resolve `<problem>` / `<problem>_model` from it.
- Added `claude-snippet.md`, injected into the target's `CLAUDE.md` between
  `methodology-kit` markers.
- P6: solver stack is a kit *default* (Pyomo + Gurobi; HiGHS fallback), not a
  project decision; replaced the reference to a non-existent `verify` skill with
  an explicit end-to-end check.
- P9: gap sign stated for both minimisation and maximisation.
- P5: clarified that no `milp-modeler` agent ships with the kit.
- P8/P10: point at the existing templates instead of "extract on first run".
- Registry §B: P5/P8/P9/P10 rows list their shipped templates.
- README: corrected skill/agent counts and dependency phases; reuse instructions
  rewritten around `kit.py`.
- Removed a stray, repository-specific `.code-workspace` file.

## 1.0.0 — 2026-07 (initial export)

- First snapshot exported by hand from the warehouse case study: 17 templates,
  14 skills, 6 agents, playbook and a blank registry.
