---
name: p4-visualize
description: >
  Phase P4 of the combinatorial-problem methodology — Solution visualization.
  Use after P3, to build a case-specific visualizer that renders a candidate
  solution as a static image or a dynamic animation/HTML, from the solution
  schema. Follows docs/methodology/README.md.
---

# P4 — Solution visualization

Build a renderer that turns a solution into a human-readable picture. It is
case-specific and its medium varies (static or dynamic), so the reusable asset
is a **contract + reference skeletons**, not a fixed renderer.

## Inputs
- The P2 instance schema and the P3 solution schema (only the schemas are needed
  to build the renderer; real solutions from P6/P8 are used to exercise it).

## Templates
- `docs/methodology/templates/visualization-contract.template.py`
- `docs/methodology/templates/visualize-static.template.py`
- `docs/methodology/templates/visualize-dynamic.template.html`

## Contract (keep it)
Implement `visualize(instance, solution, out_path) -> artifact_path`, consuming
exactly `instance.json` (P2) + `solution.json` (P3). Any technique's output is
rendered the same way.

## Steps
1. **Choose the medium.** Static (e.g. matplotlib → PNG/SVG) for a fixed
   snapshot; dynamic (animation / self-contained HTML) when the solution has a
   temporal/sequential structure worth playing back. State the choice.
2. Implement `<problem>_model/visualize.py` conforming to the contract; render
   the solution's key structure (e.g. for a sequential problem: the event/step
   sequence, resource occupancy over steps, and per-entity contents/progress).
3. Produce a sample artifact from a solved instance and eyeball it.

## Reusable asset
- Extract/refresh the visualization contract + the static and dynamic skeletons.

## Done when
- `visualize()` produces an artifact for a sample solution; the medium
  (static/dynamic) is chosen and documented.

## Governance
- Invoke `methodology-curator` to record P4 and extract/refresh the templates.

## Next
- P5 MILP formulation (`p5-formulate-milp`).
