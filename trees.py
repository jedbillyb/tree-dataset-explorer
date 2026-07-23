#!/usr/bin/env python3
"""Explore, sample, and summarise the tree dataset.

Data lives in ``trees_data.csv`` next to this script with columns:
    Tree, Type, Girth, Age, Disease, Height, Value

Subcommands
-----------
    show    print the full record(s) for one or more trees by id
    sample  pick a random sample (default 20) and summarise it
    stats   summarise the whole population, optionally per type
    filter  list trees matching type / girth / age / disease criteria

Examples
--------
    python trees.py show 1 3 42
    python trees.py sample -n 20 --seed 7
    python trees.py stats --by-type
    python trees.py filter --type Oak --min-girth 2.0
    python trees.py filter --diseased --field Girth
"""

import argparse
import csv
import random
import statistics
from pathlib import Path

CSV = Path(__file__).with_name("trees_data.csv")

# Numeric columns we can compute statistics over.
NUMERIC = ("Girth", "Age", "Height", "Value")


def load():
    """Return {tree_id: {column: value}} with numbers parsed."""
    trees = {}
    with CSV.open() as f:
        for r in csv.DictReader(f):
            trees[int(r["Tree"])] = {
                "Type": r["Type"],
                "Girth": float(r["Girth"]),
                "Age": int(r["Age"]),
                "Disease": int(r["Disease"]),
                "Height": float(r["Height"]),
                "Value": float(r["Value"]),
            }
    return trees


def summarise(values):
    """Return a dict of summary statistics for a list of numbers."""
    values = list(values)
    if not values:
        return {}
    return {
        "n": len(values),
        "min": min(values),
        "max": max(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
    }


def print_summary(label, values):
    s = summarise(values)
    if not s:
        print(f"{label}: (no data)")
        return
    print(f"{label}:")
    print(f"    n      = {s['n']}")
    print(f"    min    = {s['min']:.2f}")
    print(f"    max    = {s['max']:.2f}")
    print(f"    mean   = {s['mean']:.3f}")
    print(f"    median = {s['median']:.2f}")
    print(f"    stdev  = {s['stdev']:.3f}")


def type_counts(trees):
    """Return {type: count} for the given trees, ordered by descending count."""
    counts = {}
    for rec in trees.values():
        counts[rec["Type"]] = counts.get(rec["Type"], 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def print_type_breakdown(label, trees):
    """Print each type's count and share of the population as a percentage."""
    counts = type_counts(trees)
    total = sum(counts.values())
    print(f"{label} (n = {total}):")
    for typ, c in counts.items():
        print(f"    {typ:<8} {c:>4}  {c / total * 100:6.2f}%")


HEADER = f"{'Tree':>5}  {'Type':<6} {'Girth':>6} {'Age':>4} {'Dis':>3} {'Height':>7} {'Value':>7}"


def print_row(t, rec):
    print(f"{t:>5}  {rec['Type']:<6} {rec['Girth']:>6.1f} {rec['Age']:>4} "
          f"{rec['Disease']:>3} {rec['Height']:>7.1f} {rec['Value']:>7.0f}")


def print_table(trees, ids):
    print(HEADER)
    for t in ids:
        print_row(t, trees[t])


# --- subcommands -----------------------------------------------------------

def cmd_show(trees, a):
    missing = [t for t in a.ids if t not in trees]
    if missing:
        print(f"No such tree(s): {missing}")
    ids = [t for t in a.ids if t in trees]
    if ids:
        print_table(trees, ids)


def allocate(n, counts, min_each=0):
    """Split ``n`` across the keys of ``counts`` in proportion to their sizes.

    Uses largest-remainder rounding so the parts start out summing to ``n``.
    With ``min_each`` any key that would round down below that (e.g. a rare
    type rounding away to zero) is bumped up to the minimum instead. Those
    bumps are added on top, so the returned parts can total slightly more than
    ``n`` -- the trade-off for guaranteeing every type is represented.
    """
    total = sum(counts.values())
    exact = {k: n * c / total for k, c in counts.items()}
    alloc = {k: int(v) for k, v in exact.items()}
    remainder = n - sum(alloc.values())
    # Hand out the leftover seats to the largest fractional parts.
    order = sorted(exact, key=lambda k: exact[k] - alloc[k], reverse=True)
    for k in order[:remainder]:
        alloc[k] += 1
    # Round up any type that still falls short of the minimum.
    for k in alloc:
        if alloc[k] < min_each:
            alloc[k] = min_each
    return alloc


def cmd_sample(trees, a):
    if a.seed is not None:
        random.seed(a.seed)
    pop = sorted(trees)
    if a.n > len(pop) and not a.replace:
        raise SystemExit(f"cannot sample {a.n} without replacement from {len(pop)} trees")

    if a.stratified:
        # Keep each type's share of the sample equal to its share of the population.
        by_type = {}
        for t, rec in trees.items():
            by_type.setdefault(rec["Type"], []).append(t)
        alloc = allocate(a.n, {typ: len(ids) for typ, ids in by_type.items()}, min_each=1)
        sample = []
        for typ, k in alloc.items():
            ids = by_type[typ]
            if a.replace:
                sample += [random.choice(ids) for _ in range(k)]
            else:
                if k > len(ids):
                    raise SystemExit(
                        f"cannot draw {k} {typ} without replacement from {len(ids)}"
                    )
                sample += random.sample(ids, k)
        sample = sorted(sample)
    elif a.replace:
        sample = [random.choice(pop) for _ in range(a.n)]
    else:
        sample = sorted(random.sample(pop, a.n))

    mode = "with" if a.replace else "without"
    kind = "stratified " if a.stratified else ""
    # Stratified rounding-up can push the total a little above the requested n.
    note = f" (rounded up from {a.n})" if len(sample) != a.n else ""
    print(f"Random {kind}sample of {len(sample)} trees{note} ({mode} replacement):")
    print(sample)
    print()
    print_table(trees, sample)
    print()
    print_summary(f"{a.field} (sample)", [trees[t][a.field] for t in sample])
    print()
    print_summary(f"{a.field} (population)", [rec[a.field] for rec in trees.values()])
    print()
    print_type_breakdown("Type mix (sample)", {t: trees[t] for t in sample})
    print()
    print_type_breakdown("Type mix (population)", trees)


def cmd_stats(trees, a):
    if a.by_type:
        print_type_breakdown("Type mix", trees)
        print()
        types = sorted({rec["Type"] for rec in trees.values()})
        for typ in types:
            vals = [rec[a.field] for rec in trees.values() if rec["Type"] == typ]
            print_summary(f"{typ} {a.field}", vals)
            print()
    else:
        for field in NUMERIC:
            print_summary(field, [rec[field] for rec in trees.values()])
            print()


def cmd_filter(trees, a):
    ids = []
    for t, rec in sorted(trees.items()):
        if a.type and rec["Type"].lower() != a.type.lower():
            continue
        if a.min_girth is not None and rec["Girth"] < a.min_girth:
            continue
        if a.max_girth is not None and rec["Girth"] > a.max_girth:
            continue
        if a.min_age is not None and rec["Age"] < a.min_age:
            continue
        if a.diseased and rec["Disease"] != 1:
            continue
        if a.healthy and rec["Disease"] != 0:
            continue
        ids.append(t)

    if not ids:
        print("No trees match those criteria.")
        return
    print_table(trees, ids)
    print()
    print_summary(f"{a.field} (matched {len(ids)})", [trees[t][a.field] for t in ids])


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("show", help="print records for tree ids")
    s.add_argument("ids", type=int, nargs="+")
    s.set_defaults(func=cmd_show)

    s = sub.add_parser("sample", help="random sample + stats")
    s.add_argument("-n", type=int, default=20, help="sample size (default 20)")
    s.add_argument("--replace", action="store_true", help="sample with replacement")
    s.add_argument("--stratified", action="store_true",
                   help="keep each type's share equal to its population share")
    s.add_argument("--seed", type=int, help="RNG seed for reproducibility")
    s.add_argument("--field", choices=NUMERIC, default="Girth", help="field to summarise")
    s.set_defaults(func=cmd_sample)

    s = sub.add_parser("stats", help="population statistics")
    s.add_argument("--by-type", action="store_true", help="break down by tree type")
    s.add_argument("--field", choices=NUMERIC, default="Girth", help="field when --by-type")
    s.set_defaults(func=cmd_stats)

    s = sub.add_parser("filter", help="list trees matching criteria")
    s.add_argument("--type", help="tree type, e.g. Oak")
    s.add_argument("--min-girth", type=float)
    s.add_argument("--max-girth", type=float)
    s.add_argument("--min-age", type=int)
    s.add_argument("--diseased", action="store_true", help="only diseased trees")
    s.add_argument("--healthy", action="store_true", help="only healthy trees")
    s.add_argument("--field", choices=NUMERIC, default="Girth", help="field to summarise")
    s.set_defaults(func=cmd_filter)

    a = p.parse_args()
    a.func(load(), a)


if __name__ == "__main__":
    main()
