# Task 2 — Exact Distinct Counting Limits

## Measurements

Memory values are peak allocations reported by `tracemalloc`.

| Stream size | True distinct | Exact time | Exact peak memory | FM time | FM peak memory | FM estimate | FM ratio |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100,000 | 36,702 | 0.15 s | 3.93 MB | 29.19 s | 0.394 MB | 50,535 | 1.377x |
| 400,000 | 146,970 | 0.63 s | 11.59 MB | 118.24 s | 0.004 MB | 162,773 | 1.108x |
| 1,600,000 | 587,625 | 2.64 s | 46.65 MB | 485.90 s | 0.004 MB | 623,487 | 1.061x |
| 6,400,000 | 2,349,909 | 10.77 s | 188.29 MB | 1,887.46 s | 0.395 MB | 2,965,821 | 1.262x |

## Growth and accuracy

Exact memory grew from 3.93 MB to 188.29 MB, about 48x, while the stream grew 64x. After the smallest run, each 4x increase in stream size produced approximately 4x memory growth (11.59 → 46.65 → 188.29 MB), confirming roughly linear growth with `n`.

FM memory showed no growth with stream size. Its measured peak stayed below 0.40 MB and is determined by the fixed 64 hash registers, not by `n`. The 0.004–0.395 MB variation is measurement/runtime overhead rather than stream-dependent storage.

The FM ratios were 1.377x, 1.108x, 1.061x, and 1.262x in increasing size order. Accuracy improved through 1,600,000 items and then became worse at 6,400,000; it did not improve monotonically with stream size, but every estimate remained within the required factor of two.

## Stopping point

The experiment became unpleasant at 6,400,000 items because FM took 1,887.46 seconds, about 31 minutes. We stopped there rather than increasing the stream size further. At that size, Exact used 188.29 MB but completed in 10.77 seconds; time in the current FM implementation was the limiting practical cost.

## Machine and environment

- CPU: Intel Core i9-14900HX, 32 logical CPUs (16 cores), x86_64
- RAM: 16,187,520 kB (about 16.6 GB) visible to WSL2
- Platform: Linux 6.6.87.2, Microsoft WSL2, glibc 2.39
- Python: 3.12.3
- Other workloads: not recorded during the measurements
