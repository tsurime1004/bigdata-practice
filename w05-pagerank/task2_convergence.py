#!/usr/bin/env python3
"""Week 5 · Task 2 — How long does it take to converge, and on what?

Textbook §5.1, §5.2.

The textbook says PageRank converges. It does not say in how many iterations,
because the answer depends on beta, on the graph, and on what you are willing
to call "converged". Those three knobs are yours to turn, on your machine,
with a graph big enough that you can feel the cost.

    python3 task2_convergence.py --betas 0.5,0.7,0.85,0.95,0.99
    python3 task2_convergence.py --nodes 20000 --betas 0.85,0.95

Your timings are about your hardware. The iteration counts are not - those are
about the mathematics, and everybody should get the same ones.
"""
import argparse, json, os, platform, time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def machine():
    info = {"platform": platform.platform(),
            "processor": platform.processor() or platform.machine(),
            "cpu_count": os.cpu_count(),
            "python": platform.python_version()}
    try:
        pages = os.sysconf("SC_PHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
        info["ram_gib"] = round(pages * page_size / 1024 ** 3, 2)
    except (AttributeError, OSError, ValueError):
        info["ram_gib"] = None
    try:
        info["load_average"] = [round(value, 2) for value in os.getloadavg()]
        info["other_activity"] = (
            "Not controlled; load_average records other system activity "
            "during the final measurement."
        )
    except (AttributeError, OSError):
        info["other_activity"] = "Not controlled or available on this platform."
    return info


def _fmt_top(top):
    return ", ".join(top)


def write_report(data):
    """Write the human-readable A2--A7 analysis from all accumulated runs."""
    runs = data["runs"]
    ordered = sorted(runs, key=lambda row: (row["nodes"], row["tol"], row["beta"]))
    lines = [
        "# PageRank Convergence Measurements",
        "",
        "## Results",
        "",
        "| Nodes | Beta | Tolerance | Iterations | Seconds | Top 10 |",
        "|---:|---:|---:|---:|---:|---|",
    ]
    for row in ordered:
        lines.append(
            f"| {row['nodes']:,} | {row['beta']:.2f} | {row['tol']:.0e} | "
            f"{row['iterations']} | {row['seconds']:.6f} | {_fmt_top(row['top10'])} |"
        )

    # A3: use a like-for-like size/tolerance group with the most beta values.
    beta_groups = {}
    for row in runs:
        beta_groups.setdefault((row["nodes"], row["tol"]), []).append(row)
    beta_group = max(beta_groups.values(), key=lambda group: len({r["beta"] for r in group}))
    beta_group = sorted(beta_group, key=lambda row: row["beta"])
    first, last = beta_group[0], beta_group[-1]
    trend = "increased" if last["iterations"] > first["iterations"] else "did not increase"
    lines += [
        "",
        "## A3 — Effect of beta",
        "",
        f"For {first['nodes']:,} nodes at tolerance {first['tol']:.0e}, the iteration "
        f"count {trend} from {first['iterations']} at beta={first['beta']:.2f} to "
        f"{last['iterations']} at beta={last['beta']:.2f}. As beta approaches 1, "
        "teleportation becomes weaker, so the Markov chain mixes more slowly and "
        "the initial rank distribution is forgotten more slowly.",
    ]

    # A4: find matching beta/tolerance runs across graph sizes.
    size_groups = {}
    for row in runs:
        size_groups.setdefault((row["beta"], row["tol"]), {})[row["nodes"]] = row
    size_candidates = [group for group in size_groups.values() if len(group) >= 2]
    lines += ["", "## A4 — Graph size", ""]
    if size_candidates:
        group = max(size_candidates, key=lambda g: max(g) / min(g))
        small, large = group[min(group)], group[max(group)]
        ratio = large["nodes"] / small["nodes"]
        time_ratio = large["seconds"] / max(small["seconds"], 1e-15)
        lines.append(
            f"At beta={small['beta']:.2f} and tolerance {small['tol']:.0e}, graph size "
            f"grew {ratio:.1f}x ({small['nodes']:,} to {large['nodes']:,} nodes). "
            f"Iterations changed from {small['iterations']} to {large['iterations']}, "
            f"while wall time changed from {small['seconds']:.6f}s to "
            f"{large['seconds']:.6f}s ({time_ratio:.1f}x). Iteration count is governed "
            "mainly by the graph's mixing behavior; wall time also pays for processing "
            "every node and edge on every iteration."
        )
    else:
        lines.append("Run the same beta and tolerance at two graph sizes to complete A4.")

    # A5: find matching beta/size runs across tolerances.
    tol_groups = {}
    for row in runs:
        tol_groups.setdefault((row["beta"], row["nodes"]), {})[row["tol"]] = row
    tol_candidates = [group for group in tol_groups.values() if len(group) >= 2]
    lines += ["", "## A5 — Tolerance", ""]
    if tol_candidates:
        group = max(tol_candidates, key=lambda g: max(g) / min(g))
        strict, loose = group[min(group)], group[max(group)]
        digits = abs(__import__("math").log10(loose["tol"] / strict["tol"]))
        extra = strict["iterations"] - loose["iterations"]
        lines.append(
            f"Tightening tolerance from {loose['tol']:.0e} to {strict['tol']:.0e} "
            f"added {extra} iterations ({extra / digits:.2f} per decimal digit) for "
            f"beta={strict['beta']:.2f} on {strict['nodes']:,} nodes. A stricter "
            "threshold requires the remaining geometric error to decay further."
        )
    else:
        lines.append("Run the same beta and graph size at two tolerances to complete A5.")

    # A6: compare each beta with the lowest-beta top 10 in the richest group.
    baseline = beta_group[0]
    changed = next((row for row in beta_group[1:]
                    if row["top10"] != baseline["top10"]), None)
    lines += ["", "## A6 — Top-10 stability", ""]
    if changed:
        lines.append(
            f"Relative to beta={baseline['beta']:.2f}, the first sampled change occurs "
            f"at beta={changed['beta']:.2f}. The top 10 changes from "
            f"[{_fmt_top(baseline['top10'])}] to [{_fmt_top(changed['top10'])}]. "
            "Therefore beta is part of the ranking methodology, not merely a runtime setting."
        )
    else:
        lines.append(
            f"The top 10 did not change across the sampled beta range "
            f"{baseline['beta']:.2f}–{last['beta']:.2f}. This result is stable for this "
            "graph and sample, but it does not prove beta-independence on other graphs."
        )

    env = data["machine"]
    lines += [
        "",
        "## A7 — Machine",
        "",
        f"- Platform: {env.get('platform', 'unknown')}",
        f"- Processor: {env.get('processor', 'unknown')} ({env.get('cpu_count', 'unknown')} logical CPUs)",
        f"- RAM: {env.get('ram_gib', 'unknown')} GiB",
        f"- Python: {env.get('python', 'unknown')}",
        f"- Other activity: {env.get('other_activity', 'unknown')}",
        f"- Load average (1/5/15 min): {env.get('load_average', 'unavailable')}",
        "",
        "Timing is wall-clock time and may vary with concurrent system activity.",
        "",
    ]
    with open(os.path.join(OUT, "convergence.md"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--betas", default="0.5,0.7,0.85,0.95,0.99")
    p.add_argument("--nodes", type=int, default=None,
                   help="graph size; default is the harness graph")
    p.add_argument("--tol", type=float, default=1e-10)
    a = p.parse_args()
    os.makedirs(OUT, exist_ok=True)

    import bench
    if a.nodes:
        bench.NODES = a.nodes
    graph = bench.build()

    from task1_pagerank import pagerank

    rows = []
    for beta in [float(x) for x in a.betas.split(",")]:
        t0 = time.perf_counter()
        ranks = pagerank(graph, beta=beta, iterations=500, tol=a.tol)
        elapsed = time.perf_counter() - t0
        iters = getattr(pagerank, "iterations", None)
        top = sorted(ranks.items(), key=lambda kv: -kv[1])[:10]
        rows.append({"beta": beta, "nodes": len(graph), "tol": a.tol,
                     "iterations": iters, "seconds": elapsed,
                     "top10": [k for k, _ in top]})
        print(f"  beta {beta:<5}  {str(iters):>4} iterations  {elapsed:>7.3f}s   "
              f"top: {', '.join(k for k, _ in top[:3])}")

    path = os.path.join(OUT, "convergence.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as handle:
            prior = json.load(handle)
    else:
        prior = {"runs": []}
    prior["machine"] = machine()
    prior["runs"].extend(rows)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(prior, handle, indent=2)
    write_report(prior)
    print(f"\n  -> out/convergence.json  ({len(prior['runs'])} run(s))")
    print("  -> out/convergence.md")


if __name__ == "__main__":
    main()
