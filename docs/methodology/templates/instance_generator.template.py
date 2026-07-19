"""TEMPLATE — Synthetic instance generator (methodology asset A-P2-tpl-gen).

Copy this file next to your problem's code, rename it, fill every <PLACEHOLDER>,
and delete guidance comments. The result must produce a JSON instance that
conforms to the instance JSON schema (A-P2-tpl-schema) and matches the data
model .tex (A-P2-tpl-doc) field-for-field.

Design contract (keep all of it):
  * Pure standard library only  -> runs with no extra dependencies.
  * Deterministic given ``seed`` -> use one ``random.Random(seed)`` instance,
    never the module-level ``random`` functions, so runs are reproducible.
  * Two entry points: a ``generate_instance(...)`` function (keyword-only args
    with sensible defaults) AND an argparse CLI runnable as
    ``python -m <package>.<module>``.
  * Sizes and ranges are parameters, not literals buried in the body.

Usage:
    python -m <package>.<module> --out instance.json --seed 1 \\
        --<index-count> 20 --<entity-count> 50
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

# Attribute pools for synthetic entities. Choose value sets that EXERCISE the
# rules the solver keys on (e.g. include every category the rules branch on).
<CATEGORICAL_A> = ["<val1>", "<val2>", "<val3>"]
<CATEGORICAL_B> = ["<val1>", "<val2>"]


def generate_instance(
    *,
    n_<index>: int = 20,            # size of the index set (e.g. customers)
    n_<entity>: int = 50,           # size of the entity set (e.g. items/SKUs)
    min_<numeric>: float = 1.0,     # numeric-attribute range (lo)
    max_<numeric>: float = 40.0,    # numeric-attribute range (hi)
    min_<integer>: int = 10,        # integer-attribute range (lo)
    max_<integer>: int = 200,       # integer-attribute range (hi)
    max_<entity>_per_<index>: int = 8,   # sparsity knob for demand
    max_<quantity>_per_line: int = 6,    # per-line demand cap
    n_<relation>_pairs: int = 5,    # size of the optional relation; drop if unused
    <count_param>: int = 100,       # config: resource count/capacity
    <size_param>: float = 200.0,    # config: global size/capacity
    <modifier>_fraction: float = 0.2,    # fraction of index elements with a modifier
    min_<modifier>: float = 0.6,         # modifier lower bound (value in (0,1])
    seed: int = 0,
) -> dict:
    """Build one instance dict. See module docstring / data model for fields."""
    rng = random.Random(seed)

    # --- entity set with per-element attributes -----------------------------
    <entities> = [
        {
            "id": f"E{i:04d}",
            "<numeric_attr>": round(rng.uniform(min_<numeric>, max_<numeric>), 2),
            "<integer_attr>": rng.randint(min_<integer>, max_<integer>),
            "<categorical_a>": rng.choice(<CATEGORICAL_A>),
            "<categorical_b>": rng.choice(<CATEGORICAL_B>),
        }
        for i in range(1, n_<entity> + 1)
    ]
    <entity>_ids = [e["id"] for e in <entities>]

    # --- optional relation: unordered, unique id pairs ----------------------
    # Attempt cap avoids an infinite loop when few distinct pairs are possible.
    pairs: set[tuple[str, str]] = set()
    max_attempts = n_<relation>_pairs * 20
    attempts = 0
    while (
        len(pairs) < n_<relation>_pairs
        and attempts < max_attempts
        and len(<entity>_ids) >= 2
    ):
        a, b = rng.sample(<entity>_ids, 2)
        pairs.add(tuple(sorted((a, b))))
        attempts += 1
    <relation> = [list(p) for p in sorted(pairs)]

    # --- index set ----------------------------------------------------------
    <index_elems> = [f"I{i:04d}" for i in range(1, n_<index> + 1)]

    # --- sparse demand: each index element requests a random subset ----------
    demand = []
    for c in <index_elems>:
        k = rng.randint(1, min(max_<entity>_per_<index>, n_<entity>))
        for s in rng.sample(<entity>_ids, k):
            demand.append(
                {"<index_ref>": c, "<entity_ref>": s,
                 "<quantity>": rng.randint(1, max_<quantity>_per_line)}
            )

    # --- optional per-index modifier: default 1.0, a minority perturbed ------
    <modifier_map> = {
        c: (round(rng.uniform(min_<modifier>, 1.0), 2)
            if rng.random() < <modifier>_fraction else 1.0)
        for c in <index_elems>
    }

    return {
        "<ENTITY_SET>": <entities>,
        "<relation>": <relation>,
        "<INDEX_SET>": <index_elems>,
        "demand": demand,
        "config": {
            "<count_param>": <count_param>,
            "<size_param>": <size_param>,
            "<per_index_modifier>": <modifier_map>,
        },
    }


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Generate a synthetic <PROBLEM> instance (JSON)."
    )
    p.add_argument("--out", type=Path, default=Path("instance.json"),
                   help="Output JSON path (default: instance.json).")
    p.add_argument("--seed", type=int, default=0)
    # Expose the sizes/knobs most likely to vary between runs; keep the rest as
    # function defaults. Use dest= to map CLI names to generate_instance kwargs.
    p.add_argument("--<index-count>", type=int, default=20, dest="n_<index>")
    p.add_argument("--<entity-count>", type=int, default=50, dest="n_<entity>")
    p.add_argument("--<count-param>", type=int, default=100, dest="<count_param>")
    p.add_argument("--<size-param>", type=float, default=200.0, dest="<size_param>")
    return p


def main(argv=None) -> int:
    args = _build_arg_parser().parse_args(argv)
    instance = generate_instance(
        n_<index>=args.n_<index>,
        n_<entity>=args.n_<entity>,
        <count_param>=args.<count_param>,
        <size_param>=args.<size_param>,
        seed=args.seed,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(instance, indent=2), encoding="utf-8")
    print(
        f"[instance_generator] wrote {args.out} "
        f"({len(instance['<INDEX_SET>'])} <index>, {len(instance['<ENTITY_SET>'])} <entity>, "
        f"{len(instance['demand'])} demand lines, seed={args.seed})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
