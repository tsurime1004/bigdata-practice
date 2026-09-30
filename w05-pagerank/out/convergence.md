# PageRank Convergence Measurements

## Results

| Nodes | Beta | Tolerance | Iterations | Seconds | Top 10 |
|---:|---:|---:|---:|---:|---|
| 1,200 | 0.50 | 1e-10 | 14 | 0.007732 | p00009, p00001, p00006, p00005, p00003, p00002, p00000, p00004, p00007, p00008 |
| 1,200 | 0.70 | 1e-10 | 17 | 0.009105 | p00009, p00001, p00006, p00005, p00003, p00002, p00004, p00000, p00007, p00008 |
| 1,200 | 0.85 | 1e-10 | 20 | 0.010384 | p00009, p00001, p00006, p00005, p00003, p00002, p00004, p00000, p00007, p00008 |
| 1,200 | 0.95 | 1e-10 | 23 | 0.011747 | p00009, p00001, p00006, p00005, p00003, p00002, p00004, p00000, p00007, p00008 |
| 1,200 | 0.99 | 1e-10 | 24 | 0.013128 | p00009, p00001, p00006, p00005, p00003, p00002, p00004, p00000, p00007, p00008 |
| 1,200 | 0.85 | 1e-06 | 12 | 0.006182 | p00009, p00001, p00006, p00005, p00003, p00002, p00004, p00000, p00007, p00008 |
| 6,000 | 0.85 | 1e-10 | 22 | 0.060554 | p00009, p00001, p00006, p00005, p00003, p00002, p00004, p00000, p00007, p00008 |
| 6,000 | 0.95 | 1e-10 | 24 | 0.064365 | p00009, p00001, p00006, p00005, p00003, p00002, p00004, p00000, p00007, p00008 |

## A3 — Effect of beta

For 1,200 nodes at tolerance 1e-10, the iteration count increased from 14 at beta=0.50 to 24 at beta=0.99. As beta approaches 1, teleportation becomes weaker, so the Markov chain mixes more slowly and the initial rank distribution is forgotten more slowly.

## A4 — Graph size

At beta=0.85 and tolerance 1e-10, graph size grew 5.0x (1,200 to 6,000 nodes). Iterations changed from 20 to 22, while wall time changed from 0.010384s to 0.060554s (5.8x). Iteration count is governed mainly by the graph's mixing behavior; wall time also pays for processing every node and edge on every iteration.

## A5 — Tolerance

Tightening tolerance from 1e-06 to 1e-10 added 8 iterations (2.00 per decimal digit) for beta=0.85 on 1,200 nodes. A stricter threshold requires the remaining geometric error to decay further.

## A6 — Top-10 stability

Relative to beta=0.50, the first sampled change occurs at beta=0.70. The top 10 changes from [p00009, p00001, p00006, p00005, p00003, p00002, p00000, p00004, p00007, p00008] to [p00009, p00001, p00006, p00005, p00003, p00002, p00004, p00000, p00007, p00008]. Therefore beta is part of the ranking methodology, not merely a runtime setting.

## A7 — Machine

- Platform: Linux-6.6.87.2-microsoft-standard-WSL2-x86_64-with-glibc2.39
- Processor: x86_64 (32 logical CPUs)
- RAM: 15.44 GiB
- Python: 3.12.3
- Other activity: Not controlled; load_average records other system activity during the final measurement.
- Load average (1/5/15 min): [0.21, 0.1, 0.13]

Timing is wall-clock time and may vary with concurrent system activity.
