"""
TEMPLATE (methodology asset A-P3-tpl-sol-checker) — P3 Solution model & checker.

Purpose
-------
A problem-agnostic skeleton for the solution CHECKER: it verifies that a
candidate solution satisfies every tagged requirement `[RQxx]` from the P1
formalization, and recomputes the objective.

Preferred mechanism — REUSE cornflow (`cornflow_client.ExperimentCore`)
----------------------------------------------------------------------
Do NOT hand-roll a runner. Subclass `ExperimentCore` and rely on its built-in
`check()`:

  * `ExperimentCore.check()` calls `launch_all_checks()`, which AUTO-DISCOVERS
    every method whose name starts with `check_`, runs each one, and returns a
    single dict.
  * The dict is keyed by the method name WITH the leading `check_` STRIPPED
    (so `check_rq01` -> key `rq01`); the value is that method's returned
    list/dict of errors.
  * Only NON-EMPTY results are included. Therefore an EMPTY dict `{}` means the
    solution is FEASIBLE (every requirement passed).
  * The aggregated dict is validated against `schema_checks`, loaded from
    `solution_checks.json`.

Naming contract (traceability)
------------------------------
  * ONE method per requirement: `check_rq01`, `check_rq02`, …, `check_rqNN`.
    The `rqXX` suffix MUST match the stable `[RQxx]` id assigned in P1, so each
    requirement maps one-to-one to exactly one check and to one key in the
    output dict.
  * Each `check_rqXX` returns a LIST of error entries (dicts). Empty list = pass.
    Each entry SHOULD be `{"error_type": <short label>, "error_message": <detail>}`
    (this is the entry shape the checks-output schema below validates), and the
    message should carry enough context to locate the violation (ids, the
    offending value, the bound it broke).

Fill in
-------
  * Replace `<Problem>` / `<...>` placeholders.
  * Add/remove `check_rqXX` methods so there is exactly one per `[RQxx]`.
  * Implement `get_objective()` to recompute the objective from the solution.
  * Author `schemas/solution.json` (solution schema, from
    solution-schema.template.json) and `schemas/solution_checks.json`
    (schema of the AGGREGATED check output). The checks-output schema is an
    object with `additionalProperties: false` and ONE OPTIONAL property per
    requirement — key `rqNN` (the `check_`-stripped method name) whose value is
    an `errorList` (array of `{error_type, error_message}` entries). A property
    is present only when that requirement fails, so the EMPTY object `{}` means
    the solution is feasible.

Non-cornflow fallback
---------------------
If the project is NOT a cornflow app, keep the `check_rqXX` methods and
`get_objective()` exactly as-is and replace only the base class, mirroring
cornflow's `check()` / `launch_all_checks` semantics. Two equivalent ways:

(a) Class-based mixin (PREFERRED — swap-in compatible: to move onto cornflow
    later, just change the base class to `ExperimentCore` and delete the mixin):

        class _CheckMixin:
            def get_check_methods(self):
                return [m for m in dir(self)
                        if m.startswith("check_") and callable(getattr(self, m))]

            def launch_all_checks(self) -> dict:
                results = {}
                for name in self.get_check_methods():
                    try:
                        out = getattr(self, name)()
                    except Exception:
                        out = [{"error_type": "Check execution error",
                                "error_message": f"{name} raised an exception"}]
                    if out:                                   # keep only non-empty
                        results[name.split("check_", 1)[1]] = out   # strip "check_"
                return results

            def check(self) -> dict:
                return self.launch_all_checks()

        class Experiment(_CheckMixin):   # subclass ExperimentCore on cornflow
            ...

(b) Standalone functions + a small aggregator:

        def check_all(instance, solution) -> dict:
            checks = {name[6:]: fn(instance, solution)      # strip "check_"
                      for name, fn in globals().items()
                      if name.startswith("check_") and name != "check_all"}
            return {k: v for k, v in checks.items() if v}    # keep only non-empty

Either way, keep the same `[RQxx]`->key mapping and the "empty dict = feasible"
convention.
"""

import os

from cornflow_client import ExperimentCore
from cornflow_client.core.tools import load_json

from .instance import Instance
from .solution import Solution


class Experiment(ExperimentCore):
    # Schema of the AGGREGATED check output; one property per `rqXX` key.
    schema_checks = load_json(
        os.path.join(os.path.dirname(__file__), "../schemas/solution_checks.json")
    )

    def __init__(self, instance: Instance, solution: Solution):
        if solution is None:
            solution = Solution(dict())
        super().__init__(instance, solution)

    @property
    def instance(self) -> Instance:
        return super().instance

    @property
    def solution(self) -> Solution:
        return super().solution

    @solution.setter
    def solution(self, value):
        self._solution = value

    def get_objective(self) -> float:
        """Recompute the objective from the solution's realized decisions.

        Must return the same value the technique reports (within tolerance);
        the experimentation phase relies on this to compare techniques fairly.
        """
        # <compute objective from self.instance and self.solution>
        return 0

    # -- One method per requirement [RQxx]; empty list = requirement satisfied --

    def check_rq01(self) -> list:
        """[RQ01] <requirement statement>.

        Returns:
            list: error entries, each locating a violation of RQ01
                  (e.g. {"error_type": "RQ01 <label>",
                         "error_message": f"<entity> {id}: {value} > {bound}"}).
                  Empty list = pass.
        """
        errors = []
        # <inspect self.instance + self.solution; append an entry per violation>
        return errors

    def check_rq02(self) -> list:
        """[RQ02] <requirement statement>. Empty list = pass."""
        errors = []
        # <check logic>
        return errors

    # ... add check_rq03 ... check_rqNN, exactly one per tagged [RQxx].
