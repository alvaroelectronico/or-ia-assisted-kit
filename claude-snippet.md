## Methodology kit (problem description → solution)

This repository applies the reusable **combinatorial-optimization methodology
kit** (phases P0–P10, optional P11). Managed by `kit.py`; the files it manages
are listed in `.methodology-kit.lock.json`.

- **Playbook:** `docs/methodology/README.md` — phases, two-layer
  (instance + template) principle, governance. Read it before any phase.
- **Registry:** `docs/methodology/registry.md` — §0 *Project binding* resolves
  the generic `<problem>` / `<problem>_model` placeholders used by every skill,
  agent and template; then assets, case-study status and the decision log.
- **Phase skills:** `/p0-intake` → `/p1-formalize` → `/p2-data-model` →
  `/p3-solution-checker` → `/p4-visualize` → `/p5-formulate-milp` →
  `/p6-implement-milp` → P7 (`/digest-paper`, `/synthesize-theory`) →
  `/p8-heuristic` → `/p9-experiments` → `/p10-report`; optional P11
  (`/paper-litreview`, `/paper-write`).
- **Governance:** after a phase produces something, invoke the
  `methodology-curator` agent (sole writer of the registry and templates);
  run `methodology-auditor` (read-only) before each phase transition.
- **Conventions:** all generated content in English; model parameters
  UPPERCASE, decision variables lowercase, sets calligraphic; every
  requirement has a stable `[RQxx]` ID checked one-to-one by `check_rqXX`.
