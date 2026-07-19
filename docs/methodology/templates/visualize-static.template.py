"""
TEMPLATE (methodology asset A-P4-tpl-viz-static) — P4 Solution visualization
(STATIC backend).

Purpose
-------
A matplotlib-based reference skeleton for the STATIC visualization medium: turn a
P3 solution into a single fixed image (PNG/SVG/PDF). It conforms to the P4
contract (`visualization-contract.template.py`): `render_static(...)` is what the
contract's `visualize()` dispatches to when the chosen medium is static, and it
returns the `artifact_path`.

Use the static medium for a fixed SNAPSHOT of the solution (an assignment, a
selection, a final layout). If the solution is best understood by PLAYING BACK a
temporal/sequential structure, prefer the dynamic backend
(`visualize-dynamic.template.html`).

Design rules
------------
  * Read-only over `instance` / `solution`; depend only on the P2 + P3 schemas.
  * Deterministic layout: fix ordering / any positional seed so the image is
    reproducible.
  * Return the path actually written.

Fill in
-------
  * Replace `<...>` placeholders with your problem's entities/decisions.
  * Draw the solution's KEY STRUCTURE (the thing a human needs to judge the
    solution) and annotate the objective. Keep the figure legible, not exhaustive.
"""

# NOTE: matplotlib is the only non-stdlib dependency of this backend.
import matplotlib

matplotlib.use("Agg")  # headless / reproducible; no interactive backend needed
import matplotlib.pyplot as plt


def render_static(instance: dict, solution: dict, out_path: str) -> str:
    """Render `solution` as a static image at `out_path`; return that path.

    Called by the contract's `visualize()`. Signature mirrors the contract so the
    backend is swappable.
    """
    # --- 1. Pull the decisions to draw (schema fields only) -----------------
    # <primary> = solution["<primary_decision>"]        # e.g. list of assignments
    # <objective> = solution.get("objective")
    # <entities> = instance["<entity_catalog>"]         # for labels / ordering

    # --- 2. Set up the figure ----------------------------------------------
    fig, ax = plt.subplots(figsize=(<W>, <H>))          # e.g. (10, 6)

    # --- 3. Draw the solution's key structure ------------------------------
    # Guidance: pick ONE primary visual encoding that matches the decision:
    #   * assignment / grouping  -> grouped bars, a matrix/heatmap, or swimlanes
    #   * selection / packing    -> stacked bars (capacity vs used), a treemap
    #   * sequence / schedule     -> a Gantt-style broken_barh over an x-axis of
    #                               steps/time (also renderable dynamically)
    # Iterate over the decisions and emit patches/bars; label by entity id.
    #
    # for row in <primary>:
    #     ax.<plot>(...)                                # honor a FIXED ordering

    # --- 4. Annotate + label -----------------------------------------------
    ax.set_title(f"<PROBLEM> solution — objective = {<objective>}")
    ax.set_xlabel("<x meaning>")
    ax.set_ylabel("<y meaning>")
    # ax.legend(loc="best")

    # --- 5. Save (extension of out_path picks PNG/SVG/PDF) -----------------
    fig.tight_layout()
    fig.savefig(out_path, dpi=<DPI>, bbox_inches="tight")  # e.g. dpi=150
    plt.close(fig)                                          # free the figure
    return out_path
