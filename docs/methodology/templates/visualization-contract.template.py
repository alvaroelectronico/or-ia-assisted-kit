"""
TEMPLATE (methodology asset A-P4-tpl-viz-contract) — P4 Solution visualization.

Purpose
-------
The problem-agnostic CONTRACT every case-specific visualizer conforms to. P4 is a
SOLUTION-LAYER phase (a sibling of the P3 checker): both consume the P3 solution
schema, but where the checker VALIDATES a solution, the visualizer RENDERS it into
a human-readable artifact. Visualization is inherently case-specific and its
MEDIUM varies (a static image vs a dynamic animation/HTML), so the reusable asset
is this contract + two reference skeletons, NOT a fixed renderer.

The contract
------------
    visualize(instance, solution, out_path) -> artifact_path

  * `instance`  — the P2 input object (a dict parsed from `instance.json`, or a
                  loaded Instance). Read-only.
  * `solution`  — the P3 candidate solution (a dict parsed from `solution.json`,
                  or a loaded Solution). Read-only. ANY technique's output (MILP
                  from P6, heuristic from P7) is rendered identically — the
                  visualizer depends only on the schema, never on how the
                  solution was produced.
  * `out_path`  — where to write the artifact. Treat its extension as the medium
                  request (e.g. `.png`/`.svg` -> static, `.html` -> dynamic), or
                  ignore it and always emit your chosen medium.
  * RETURNS the path actually written (`artifact_path`), so callers/tests can
    locate the artifact without re-deriving the name.

Design rules (keep these; they are what make the asset reusable)
----------------------------------------------------------------
  * Read-only: never mutate `instance` or `solution`.
  * Depend only on the P2 + P3 SCHEMAS, not on any solver/heuristic internals.
  * Deterministic: same inputs -> same artifact (fix any layout seed/ordering).
  * One backend module per medium; this file only LOADS + DISPATCHES.

Fill in
-------
  * Replace `<...>` placeholders and pick the default medium for your problem.
  * Point the backends at your `visualize_static` / `visualize_dynamic` modules
    (from `visualize-static.template.py` / `visualize-dynamic.template.html`).
  * State in a comment WHY the chosen medium fits (static snapshot vs playback of
    a temporal/sequential structure), as the P4 skill requires.
"""

import json
import os


def _load(obj_or_path):
    """Accept either an already-parsed dict/object or a path to a JSON file.

    Lets `visualize()` be called both from tests (dicts in memory) and from a
    CLI (paths on disk) without changing the contract.
    """
    if isinstance(obj_or_path, str):
        with open(obj_or_path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    # <if you use loaded Instance/Solution objects, coerce to dict here>
    return obj_or_path


def _pick_medium(solution, out_path) -> str:
    """Decide 'static' or 'dynamic' for this call.

    Guidance: choose STATIC (matplotlib -> PNG/SVG) for a fixed snapshot, and
    DYNAMIC (self-contained HTML/JS animation) when the solution has a
    temporal/sequential structure worth playing back. Default below dispatches on
    the requested file extension; hardcode a single medium instead if your
    problem only ever needs one.
    """
    ext = os.path.splitext(out_path)[1].lower()
    if ext in (".html", ".htm"):
        return "dynamic"
    if ext in (".png", ".svg", ".pdf", ".jpg", ".jpeg"):
        return "static"
    return "<DEFAULT_MEDIUM>"  # e.g. "static"


def visualize(instance, solution, out_path) -> str:
    """Render `solution` (for `instance`) into an artifact at `out_path`.

    Returns the path actually written (`artifact_path`). This is the ONLY public
    entry point of the P4 layer; keep this signature stable across problems.
    """
    instance = _load(instance)
    solution = _load(solution)

    medium = _pick_medium(solution, out_path)

    if medium == "static":
        # from .visualize_static import render_static
        # return render_static(instance, solution, out_path)
        raise NotImplementedError("<wire up the static backend>")
    elif medium == "dynamic":
        # from .visualize_dynamic import render_dynamic
        # return render_dynamic(instance, solution, out_path)
        raise NotImplementedError("<wire up the dynamic backend>")
    raise ValueError(f"Unknown visualization medium: {medium!r}")


if __name__ == "__main__":
    # Minimal CLI: python -m <problem>_model.visualize <instance.json> <solution.json> <out_path>
    import sys

    inst, sol, out = sys.argv[1], sys.argv[2], sys.argv[3]
    written = visualize(inst, sol, out)
    print(f"wrote {written}")
