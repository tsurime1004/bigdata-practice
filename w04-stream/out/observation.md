# Week 4 Observations

## Task 1

A Bloom filter cannot have a false negative because `add` sets every bit checked by `__contains__`, and bits are never cleared. The predicted false-positive rate was 0.860% and the measured rate was 0.915%; the small difference is expected from finite sampling and hash randomness.

For Flajolet–Martin I averaged trailing-zero maxima within groups and took the median of those group means before exponentiating: it estimated 21,247 versus 19,953 true (1.06x). On the same data, directly averaging `2^R` gave 49,792 (outlier-sensitive), while the median gave 16,384 (restricted to powers of two).

Reservoir sampling keeps only `k` values: at stream index `i`, `randrange(i + 1)` selects whether the new item replaces one of them, giving every item probability `k/n` without learning `n`. Across 4,000 trials its frequency spread was 8.9% around the expected 1,000.

## Task 2

The practical stopping point was 6,400,000 items: Exact still completed in 10.77 s using 188.29 MB, but FM took 1,887.46 s (about 31 minutes), so time—not memory—ended the experiment before Exact itself became unbearable. Exact memory grew roughly linearly (3.93 to 188.29 MB, about 48x for 64x more input; about 4x for each later 4x step), while fixed-register FM stayed below 0.40 MB with no growth trend.

FM ratios at 100,000, 400,000, 1,600,000, and 6,400,000 items were 1.377x, 1.108x, 1.061x, and 1.262x: accuracy improved and then worsened rather than changing monotonically. Factor-of-two accuracy is adequate for rough capacity planning or traffic trends, but not for billing, compliance, or decisions needing an exact unique-user count.

## Task 3

I changed the number of hashes to the optimum `k = (m/n) ln 2 = 10 ln 2 = 6.93`, rounded to 7. The theoretical floor is `(0.6185)^10 ≈ 0.819%`; the measured rate was 0.799% (sampling variation), with zero false negatives and 80,000 bits, cutting the 9.511% baseline by 91.6% and reaching the strong target.

If `n` were unknown, I would use a scalable Bloom filter that adds a new appropriately sized filter as capacity is reached (or estimate cardinality and resize before saturation). Guessing too low saturates the bits and raises false positives; guessing too high preserves accuracy but wastes memory.
