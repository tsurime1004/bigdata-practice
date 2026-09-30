# Observations

## Task 1 — PageRank Failures and Repair

- In the broken version, rank reaching a dead end has no outgoing edge and disappears. The repaired version redistributes that rank uniformly across every node, modeling a surfer choosing a new page.
- Uniform teleportation fixes both failures: it replaces rank lost at dead ends and continually lets surfers escape spider traps. Beta is the probability of following a link; with probability 1 - beta, the surfer teleports to a uniformly selected node.

## Task 2 — Convergence

- As beta approached 1, convergence slowed: iterations rose from 14 at beta 0.50 to 24 at beta 0.99 because weaker teleportation makes the random walk mix more slowly.
- Increasing the graph from 1,200 to 6,000 nodes changed iterations only from 20 to 22 at beta 0.85, while wall time grew about 5.8x; iterations reflect mixing, whereas each iteration must process the larger graph.
- The top-10 order first changed at beta 0.70 (relative to beta 0.50), so beta is part of the ranking methodology and should be reported with published rankings.

## Task 3 — Sparse PageRank

- Instead of an n-by-n transition matrix, the implementation uses the graph's adjacency lists plus two n-element rank vectors, so its float storage is 2n rather than n squared (the integer adjacency storage is proportional to n + edges).
- Teleportation and dead-end redistribution give the same scalar contribution to every node. That scalar is computed once per iteration and used to initialize the next rank vector, so no dense matrix or all-pairs operation is needed.
- The worst per-node difference from the dense answer was 1.17e-15. This harmless round-off comes from adding mathematically equivalent floating-point contributions in a different order.

## Task 4 — Local and Distributed PageRank (Optional)

- The single-process version crossed the chosen interactive usability boundary at 500,000 nodes: ten iterations took 43.39 seconds and peaked at 130.6 MB, so time gave out before memory. Spark finished the same graph in 20.32 seconds and both versions ranked node 112 first.
- At 50,000 nodes Spark took 14.22 seconds versus 3.57 seconds locally, making Spark 4.0x slower because job startup, RDD joins, shuffles, serialization, and scheduling dominate the small computation. I would reach for Spark only when the graph no longer fits or runs acceptably on one machine, or when it is already distributed.
- Local peak memory grew from 2.4 MB at 10,000 nodes to 14.1 MB at 50,000, 28.2 MB at 100,000, and 130.6 MB at 500,000. Spark partitions graph and rank state across workers, so per-worker memory follows partition size rather than the complete graph, although total cluster memory and local-mode memory still grow.
- Spark ranks summed to 0.9959 at 50,000 nodes because `reduceByKey` omits zero-in-degree nodes, so teleportation is not applied to every node; their rank then leaks when they disappear from the next join, analogous to the lost-rank failure from Task 1. Keeping the complete node set each iteration, left-joining contributions with zero defaults, and redistributing any true dangling-node mass would conserve rank.
