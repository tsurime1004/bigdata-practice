# Task 2 curve

Machine: WSL2 Linux on Intel(R) Core(TM) i9-14900HX, 32 logical CPUs, 15 GiB RAM available to WSL. I was running the terminal/Codex session, with no other heavy workload intentionally running.

| n | brute time (s) | brute comparisons | brute peak memory | LSH time (s) | LSH comparisons | LSH peak memory |
|---:|---:|---:|---:|---:|---:|---:|
| 250 | 0.18 | 31,125 | 7,416 B | 2.75 | 21 | 3,148,736 B |
| 500 | 0.84 | 124,750 | 8,120 B | 5.52 | 88 | 6,042,196 B |
| 1,000 | 3.38 | 499,500 | 10,680 B | 11.32 | 292 | 12,436,164 B |
| 2,000 | 13.05 | 1,999,000 | 21,400 B | 22.64 | 1,465 | 25,171,420 B |
| 4,000 | 52.88 | 7,998,000 | 22,584 B | 45.40 | 5,527 | 51,155,668 B |

## A4 quadratic check

Doubling `n` should make brute force take about 4 times longer:

| from n | to n | time ratio |
|---:|---:|---:|
| 250 | 500 | 4.56x |
| 500 | 1,000 | 4.04x |
| 1,000 | 2,000 | 3.86x |
| 2,000 | 4,000 | 4.05x |

This fits the quadratic expectation closely. The first jump is a little high, but after that the ratios stay near 4x.

## A5 largest-n memory

At the largest measured size, `n = 4,000`, brute force used 22,584 bytes of traced peak memory, while LSH used 51,155,668 bytes, about 48.8 MiB. The LSH memory is much higher because it stores signatures, band buckets, and candidate sets.

## A7 crossover

Brute force was faster through `n = 2,000`: 13.05s for brute force versus 22.64s for LSH. At `n = 4,000`, LSH became faster: 45.40s versus 52.88s. Linear interpolation between those two measurements puts the crossover at about `n = 3,100`, so on this machine the practical crossover is between 2,000 and 4,000 documents.

## A8 why LSH loses at small n

LSH pays a fixed linear setup cost before it can skip comparisons: it computes 120 minhash values for every document, splits each signature into 30 bands, hashes every band into buckets, and then builds candidate pairs. At small `n`, the brute-force comparison count is still small enough that this setup work costs more than just comparing every pair. Once `n` grows, the quadratic comparison count catches up and LSH wins.

## Unpleasant size

`n = 4,000` was the first unpleasant size in this run: the brute-force phase alone took 52.88 seconds, and the full row took about 98 seconds including LSH. Time ran out first; memory was still comfortable.
