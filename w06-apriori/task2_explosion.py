#!/usr/bin/env python3
"""Week 6 · Task 2 — Lower the threshold until your machine says no.

Textbook §6.1, §6.2.

Support is a knob, and turning it down is how you find the interesting rules.
It is also how you run out of memory, and where that happens is a fact about
your laptop rather than about the algorithm.

    python3 task2_explosion.py --supports 400,200,100,50,25
    python3 task2_explosion.py --supports 12,6            # careful

Lower the threshold until something gives. Write down where and what.
"""
import argparse, json, math, os, platform, time, tracemalloc

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def machine():
    processor = platform.processor()
    concurrent = []
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as cpuinfo:
            for line in cpuinfo:
                if line.startswith("model name"):
                    processor = line.split(":", 1)[1].strip()
                    break
    except OSError:
        pass
    try:
        for pid in os.listdir("/proc"):
            if not pid.isdigit() or int(pid) == os.getpid():
                continue
            try:
                with open(f"/proc/{pid}/comm", encoding="utf-8") as process:
                    concurrent.append(process.read().strip())
            except OSError:
                continue
    except OSError:
        pass

    info = {"platform": platform.platform(),
            "processor": processor or platform.machine(),
            "cpu_count": os.cpu_count(),
            "python": platform.python_version(),
            "concurrent_processes": sorted(concurrent)}
    try:
        info["ram_bytes"] = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
    except (AttributeError, OSError, ValueError):
        info["ram_bytes"] = None
    try:
        info["load_average"] = list(os.getloadavg())
    except (AttributeError, OSError):
        info["load_average"] = None
    try:
        info["running_processes"] = sum(name.isdigit() for name in os.listdir("/proc"))
    except OSError:
        info["running_processes"] = None
    return info


def growth_text(rows, field):
    """Describe average growth when support is halved."""
    factors = []
    ordered = sorted(rows, key=lambda row: row["support"], reverse=True)
    for before, after in zip(ordered, ordered[1:]):
        if before[field] and after["support"]:
            halving_steps = math.log2(before["support"] / after["support"])
            if halving_steps > 0:
                factors.append((after[field] / before[field]) ** (1 / halving_steps))
    if not factors:
        return "계산할 수 없음"
    return f"지원도를 한 단계 낮출 때 평균 약 {sum(factors) / len(factors):.2f}배"


def write_report(data):
    rows = sorted(data["runs"], key=lambda row: row["support"], reverse=True)
    host = data["machine"]
    ram = host.get("ram_bytes")
    ram_text = f"{ram / 1024 ** 3:.1f} GiB" if ram else "확인 불가"
    load = host.get("load_average")
    load_text = ", ".join(f"{value:.2f}" for value in load) if load else "확인 불가"

    lines = [
        "# Task 2 · Support threshold explosion",
        "",
        "## 측정 환경",
        "",
        f"- CPU: {host['processor']} ({host.get('cpu_count', '확인 불가')} logical CPUs)",
        f"- RAM: {ram_text}",
        f"- OS: {host['platform']}",
        f"- Python: {host['python']}",
        f"- 측정 시작 시 시스템 부하(1/5/15분): {load_text}",
        f"- 함께 실행 중이던 프로세스(측정 Python 제외): "
        f"{len(host.get('concurrent_processes', []))}개 "
        f"({', '.join(host.get('concurrent_processes', [])) or '없음'})",
        "",
        "## 측정 결과",
        "",
        "| support | frequent pairs | peak counters | time (s) | peak memory (MiB) |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(f"| {row['support']:,} | {row['frequent_pairs']:,} | "
                     f"{row['peak_counters']:,} | {row['seconds']:.2f} | "
                     f"{row['peak_bytes'] / 1024 ** 2:.1f} |")

    # Mermaid keeps the plot self-contained in the required Markdown output.
    supports = [row["support"] for row in reversed(rows)]
    counters = [row["peak_counters"] for row in reversed(rows)]
    pairs = [row["frequent_pairs"] for row in reversed(rows)]
    by_support = {row["support"]: row for row in rows}
    high = by_support.get(400, rows[0])
    middle = by_support.get(50, rows[len(rows) // 2])
    low = by_support.get(3, rows[-1])
    counter_growth = middle["peak_counters"] / high["peak_counters"]
    answer_growth = middle["frequent_pairs"] / high["frequent_pairs"]
    low_counter_growth = low["peak_counters"] / middle["peak_counters"]
    low_answer_growth = low["frequent_pairs"] / middle["frequent_pairs"]
    search_gap = middle["peak_counters"] / middle["frequent_pairs"]
    lines += [
        "",
        "## 증가 곡선",
        "",
        "두 값의 크기 차이가 커서 각각의 축으로 표시했다.",
        "",
        "```mermaid",
        "xychart-beta",
        f"    x-axis \"support (낮음 → 높음)\" {supports}",
        '    y-axis "peak counters" 0 --> ' + str(max(counters, default=0)),
        f"    line {counters}",
        "```",
        "",
        "```mermaid",
        "xychart-beta",
        f"    x-axis \"support (낮음 → 높음)\" {supports}",
        '    y-axis "frequent pairs" 0 --> ' + str(max(pairs, default=0)),
        f"    line {pairs}",
        "```",
        "",
        "## 관찰",
        "",
        f"- support {high['support']}→{middle['support']}에서 카운터는 {counter_growth:.1f}배, "
        f"정답 쌍은 {answer_growth:.1f}배 증가했다. 지원도를 절반씩 낮출 때로 환산하면 "
        f"각각 약 {counter_growth ** (1 / math.log2(high['support'] / middle['support'])):.2f}배와 "
        f"{answer_growth ** (1 / math.log2(high['support'] / middle['support'])):.2f}배다.",
        f"- support {middle['support']}→{low['support']}에서는 관측 가능한 후보 공간이 거의 포화되어 "
        f"카운터는 {low_counter_growth:.2f}배에 그쳤지만 정답은 {low_answer_growth:.1f}배 늘었다.",
        f"- support {middle['support']}에서 정답 {middle['frequent_pairs']:,}개를 찾는 데 "
        f"후보 {middle['peak_counters']:,}개, 즉 약 {search_gap:.0f}배의 카운터가 필요했다. "
        "정답보다 훨씬 큰 후보 공간을 유지해야 하는 이 간극 때문에 임계값을 조금 낮추는 것도 비싸다.",
        f"- 가장 부담스러웠던 측정은 support {data['stopped']['support']}였고, "
        f"중단/종료 판단 근거는 `{data['stopped']['reason']}`이다.",
        "",
    ]
    with open(os.path.join(OUT, "explosion.md"), "w", encoding="utf-8") as report:
        report.write("\n".join(lines))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--supports", default="400,200,100,50,25")
    p.add_argument("--stopped-reason", default=None,
                   help="why the lowest support was the stopping point")
    a = p.parse_args()
    os.makedirs(OUT, exist_ok=True)

    import bench
    from task3_pcy import PlainApriori
    baskets = bench.build()

    rows = []
    supports = [int(x.strip()) for x in a.supports.split(",")]
    if any(value <= 0 for value in supports):
        p.error("supports must be positive integers")
    for support in supports:
        algo = PlainApriori(support)
        tracemalloc.start()
        t0 = time.perf_counter()
        pairs = algo.run(baskets)
        elapsed = time.perf_counter() - t0
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        row = {"support": support, "frequent_pairs": len(pairs),
               "peak_counters": algo.peak_counters, "seconds": elapsed,
               "peak_bytes": peak_bytes}
        rows.append(row)
        print(f"  support {support:>5}   pairs {len(pairs):>7,}   "
              f"counters {algo.peak_counters:>10,}   "
              f"{elapsed:>7.2f}s   {peak_bytes / 1e6:>8.1f} MB")

    path = os.path.join(OUT, "explosion.json")
    prior = json.load(open(path)) if os.path.exists(path) else {"runs": []}
    prior["machine"] = machine()
    # A repeated support replaces its earlier measurement instead of making
    # the curve contain duplicate x-axis values.
    merged = {row["support"]: row for row in prior.get("runs", [])}
    merged.update({row["support"]: row for row in rows})
    prior["runs"] = sorted(merged.values(), key=lambda row: row["support"], reverse=True)
    lowest = min(rows, key=lambda row: row["support"])
    reason = (a.stopped_reason or
              f"이번 실행의 최저 support; {lowest['seconds']:.2f}초, "
              f"peak {lowest['peak_bytes'] / 1024 ** 2:.1f} MiB까지 측정 후 정상 종료")
    prior["stopped"] = {"support": lowest["support"], "reason": reason}
    with open(path, "w", encoding="utf-8") as output:
        json.dump(prior, output, indent=2, ensure_ascii=False)
    write_report(prior)
    print(f"\n  -> out/explosion.json  ({len(prior['runs'])} run(s))")
    print("  -> out/explosion.md")
    print("  Keep halving the support until it is unbearable. Record where with")
    print("  --stopped-reason 'what ran out or why you stopped'.")


if __name__ == "__main__":
    main()
