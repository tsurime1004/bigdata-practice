#!/usr/bin/env python3
"""Week 7 · Task 2 — Watch distance stop meaning anything.

Textbook §7.1.3, the curse of dimensionality.

In two dimensions "nearest" is obvious. In two hundred, every point is roughly
the same distance from every other point, and a method built on "nearest" has
nothing left to stand on.

That is usually stated as a fact to accept. Here you measure it, on your own
machine, and find the dimension where it starts to bite for **your** data size.

    python3 task2_curse.py --dims 2,5,10,20,50,100,200
    python3 task2_curse.py --dims 500,1000 --points 2000

The contrast ratio is the number to watch.
"""
import argparse, json, math, os, platform, random, time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def machine():
    return {"platform": platform.platform(),
            "processor": platform.processor() or platform.machine(),
            "python": platform.python_version()}


def euclid(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def sample_distances(n, dim, pairs, seed=246):
    rng = random.Random(seed + dim)
    pts = [tuple(rng.random() for _ in range(dim)) for _ in range(n)]
    ds = []
    for _ in range(pairs):
        i, j = rng.randrange(n), rng.randrange(n)
        if i != j:
            ds.append(euclid(pts[i], pts[j]))
    return ds


def measure(n, dim, pairs):
    """Measure sampled pair distances for one (n, dimension) setting."""
    t0 = time.perf_counter()
    ds = sample_distances(n, dim, pairs)
    elapsed = time.perf_counter() - t0
    if not ds:
        raise ValueError("no distinct point pairs were sampled")

    lo, hi = min(ds), max(ds)
    mean = sum(ds) / len(ds)
    variance = sum((distance - mean) ** 2 for distance in ds) / len(ds)
    stdev = math.sqrt(variance)
    return {"dim": dim, "points": n, "pairs": len(ds),
            "min": lo, "max": hi, "mean": mean, "stdev": stdev,
            "contrast": (hi - lo) / lo if lo else None,
            "relative_stdev": stdev / mean if mean else None,
            "seconds": elapsed}


def threshold_dimension(rows, threshold):
    """First measured dimension whose contrast is below threshold."""
    matches = [row["dim"] for row in rows
               if row["contrast"] is not None
               and row["contrast"] < threshold]
    return min(matches) if matches else None


def write_report(data):
    """Write the A2--A8 discussion from all accumulated measurements."""
    rows = sorted(data["runs"], key=lambda row: (row["points"], row["dim"]))
    lines = ["# Distance Contrast Across Dimensions", "",
             "## Measurements", "",
             "| dimension | points | sampled pairs | min | max | mean | "
             "contrast | relative SD | seconds |",
             "|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(
            f"| {row['dim']} | {row['points']} | {row['pairs']} | "
            f"{row['min']:.4f} | {row['max']:.4f} | {row['mean']:.4f} | "
            f"{row['contrast']:.4f} | {row['relative_stdev']:.4f} | "
            f"{row['seconds']:.3f} |"
        )

    # Use the point count with the widest dimension coverage for A3--A5.
    point_counts = sorted({row["points"] for row in rows})
    primary_n = max(point_counts,
                    key=lambda n: sum(row["points"] == n for row in rows))
    primary = sorted((row for row in rows if row["points"] == primary_n),
                     key=lambda row: row["dim"])
    below_one = threshold_dimension(primary, 1.0)
    below_half = threshold_dimension(primary, 0.5)
    one_text = str(below_one) if below_one is not None else "not in the measured range"
    half_text = (str(below_half) if below_half is not None
                 else "not in the measured range")
    first, last = primary[0], primary[-1]
    sqrt_ratios = [row["mean"] / math.sqrt(row["dim"]) for row in primary]

    lines.extend([
        "", "## Interpretation (A3–A5)", "",
        f"For n={primary_n}, contrast first falls below 1 at dimension "
        f"**{one_text}**, and below 0.5 at dimension **{half_text}**. "
        f"It changes from {first['contrast']:.3f} at d={first['dim']} to "
        f"{last['contrast']:.3f} at d={last['dim']}; nearest and furthest "
        "sampled distances therefore become less distinguishable in relative terms.",
        "",
        f"Mean distance grows from {first['mean']:.3f} to {last['mean']:.3f}. "
        f"The observed mean/sqrt(d) range is {min(sqrt_ratios):.3f}–"
        f"{max(sqrt_ratios):.3f}, close to a constant (the theoretical "
        "large-d value is sqrt(1/6) ≈ 0.408), so growth is approximately "
        "sqrt(d), not linear in d.",
        "",
        f"Relative SD falls from {first['relative_stdev']:.3f} to "
        f"{last['relative_stdev']:.3f}. Relative SD is the cleaner measure of "
        "overall distance concentration because it uses the whole sample; "
        "contrast depends on two extreme observations and hence on sample size.",
    ])

    by_dim = {}
    for row in rows:
        by_dim.setdefault(row["dim"], []).append(row)
    comparisons = [(dim, values) for dim, values in by_dim.items()
                   if len({row["points"] for row in values}) > 1]
    lines.extend(["", "## Point-count comparison (A6)", ""])
    if comparisons:
        dim, values = min(comparisons, key=lambda item: abs(item[0] - 50))
        values = sorted(values, key=lambda row: row["points"])
        summary = ", ".join(
            f"n={row['points']}: {row['contrast']:.3f}" for row in values
        )
        lines.append(
            f"At fixed dimension {dim}, contrast was {summary}. Thus n can "
            "affect contrast: a larger candidate set gives more chances to "
            "observe unusually near or far pairs. Dimension drives distance "
            "concentration, while contrast based on extrema is also sample-size "
            "dependent."
        )
    else:
        lines.append("No fixed dimension has yet been measured at two point counts.")

    machine_info = data["machine"]
    largest = max(rows, key=lambda row: row["dim"] * row["pairs"])
    lines.extend([
        "", "## Machine and runtime (A7)", "",
        f"Platform: `{machine_info['platform']}`; processor: "
        f"`{machine_info['processor']}`; Python: `{machine_info['python']}`. "
        f"The largest run (d={largest['dim']}, n={largest['points']}, "
        f"{largest['pairs']} sampled pairs) took {largest['seconds']:.3f} seconds.",
        "", "## Connection to Week 3 LSH (A8)", "",
        "This experiment does not directly invalidate Week 3's LSH result. It "
        "measures Euclidean distances between uniform points in a unit cube, "
        "whereas that LSH used Jaccard similarity on structured shingle sets. "
        "A concentration problem could still occur if the dataset's Jaccard "
        "similarities themselves become nearly equal, but that must be measured "
        "on those sets rather than inferred from this Euclidean experiment.",
        "",
    ])
    with open(os.path.join(OUT, "curse.md"), "w", encoding="utf-8") as report:
        report.write("\n".join(lines))


def write_observation(data):
    """Write the concise Task 2 observations requested by README."""
    rows = data["runs"]
    primary_n = max({row["points"] for row in rows},
                    key=lambda n: sum(row["points"] == n for row in rows))
    primary = [row for row in rows if row["points"] == primary_n]
    below_one = threshold_dimension(primary, 1.0)
    threshold = (str(below_one) if below_one is not None
                 else "the measured range")
    text = (
        "# Task 2 observations\n\n"
        f"For n={primary_n}, contrast fell below 1 at dimension {threshold}. "
        "Changing n at a fixed dimension changed the extreme-based contrast, "
        "so both dimension and sample size matter.\n"
        "This does not directly threaten Jaccard LSH: shingle sets and Jaccard "
        "similarity are not uniform Euclidean points, so their similarity "
        "distribution must be measured separately.\n"
    )
    with open(os.path.join(OUT, "observation.md"), "w", encoding="utf-8") as output:
        output.write(text)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dims", default="2,5,10,20,50,100,200")
    p.add_argument("--points", type=int, default=1000)
    p.add_argument("--pairs", type=int, default=20000)
    a = p.parse_args()
    dims = [int(value.strip()) for value in a.dims.split(",") if value.strip()]
    if not dims or any(dim <= 0 for dim in dims):
        p.error("--dims must contain positive integers")
    if a.points < 2:
        p.error("--points must be at least 2")
    if a.pairs <= 0:
        p.error("--pairs must be positive")
    os.makedirs(OUT, exist_ok=True)

    rows = []
    for dim in dims:
        row = measure(a.points, dim, a.pairs)
        rows.append(row)
        print(f"  dim {dim:>5}   mean {row['mean']:>7.3f}   "
              f"min {row['min']:>7.3f}   max {row['max']:>7.3f}   "
              f"contrast {row['contrast']:>7.3f}   "
              f"rel.sd {row['relative_stdev']:>6.3f}")

    path = os.path.join(OUT, "curse.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as source:
            prior = json.load(source)
    else:
        prior = {"runs": []}

    # Ensure A6 is represented even on a clean, single invocation: repeat one
    # moderate dimension with a different number of generated points.
    existing = prior.get("runs", []) + rows
    has_n_comparison = any(
        len({row["points"] for row in existing if row["dim"] == dim}) > 1
        for dim in {row["dim"] for row in existing}
    )
    if not has_n_comparison:
        compare_dim = min(dims, key=lambda dim: abs(dim - 50))
        compare_n = max(2, a.points // 2)
        if compare_n == a.points:
            compare_n = a.points + 1
        comparison = measure(compare_n, compare_dim, a.pairs)
        rows.append(comparison)
        print(f"  A6 comparison: dim {compare_dim}, points {compare_n}, "
              f"contrast {comparison['contrast']:.3f}")

    prior["machine"] = machine()
    keyed = {(row["dim"], row["points"], row["pairs"]): row
             for row in prior.get("runs", [])}
    keyed.update({(row["dim"], row["points"], row["pairs"]): row
                  for row in rows})
    prior["runs"] = sorted(keyed.values(),
                           key=lambda row: (row["points"], row["dim"]))
    with open(path, "w", encoding="utf-8") as output:
        json.dump(prior, output, indent=2)
    write_report(prior)
    write_observation(prior)
    print(f"\n  -> out/curse.json  ({len(prior['runs'])} measurement(s))")
    print("  -> out/curse.md")
    print("  -> out/observation.md")


if __name__ == "__main__":
    main()
