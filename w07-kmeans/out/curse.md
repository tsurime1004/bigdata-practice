# Distance Contrast Across Dimensions

## Measurements

| dimension | points | sampled pairs | min | max | mean | contrast | relative SD | seconds |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 50 | 500 | 19955 | 1.9595 | 3.7769 | 2.8758 | 0.9275 | 0.0819 | 0.077 |
| 2 | 1000 | 19978 | 0.0027 | 1.3255 | 0.5210 | 488.5816 | 0.4759 | 0.016 |
| 5 | 1000 | 19977 | 0.1106 | 1.6874 | 0.8842 | 14.2566 | 0.2816 | 0.019 |
| 10 | 1000 | 19977 | 0.4385 | 2.1595 | 1.2735 | 3.9252 | 0.1927 | 0.026 |
| 20 | 1000 | 19981 | 0.8208 | 2.6699 | 1.8153 | 2.2527 | 0.1352 | 0.036 |
| 50 | 1000 | 19977 | 1.9092 | 3.7849 | 2.8673 | 0.9824 | 0.0830 | 0.073 |
| 100 | 1000 | 19974 | 3.2057 | 4.9535 | 4.0681 | 0.5452 | 0.0598 | 0.121 |
| 200 | 1000 | 19980 | 4.8709 | 6.6818 | 5.7761 | 0.3718 | 0.0414 | 0.220 |

## Interpretation (A3–A5)

For n=1000, contrast first falls below 1 at dimension **50**, and below 0.5 at dimension **200**. It changes from 488.582 at d=2 to 0.372 at d=200; nearest and furthest sampled distances therefore become less distinguishable in relative terms.

Mean distance grows from 0.521 to 5.776. The observed mean/sqrt(d) range is 0.368–0.408, close to a constant (the theoretical large-d value is sqrt(1/6) ≈ 0.408), so growth is approximately sqrt(d), not linear in d.

Relative SD falls from 0.476 to 0.041. Relative SD is the cleaner measure of overall distance concentration because it uses the whole sample; contrast depends on two extreme observations and hence on sample size.

## Point-count comparison (A6)

At fixed dimension 50, contrast was n=500: 0.928, n=1000: 0.982. Thus n can affect contrast: a larger candidate set gives more chances to observe unusually near or far pairs. Dimension drives distance concentration, while contrast based on extrema is also sample-size dependent.

## Machine and runtime (A7)

Platform: `Linux-6.6.87.2-microsoft-standard-WSL2-x86_64-with-glibc2.39`; processor: `x86_64`; Python: `3.12.3`. The largest run (d=200, n=1000, 19980 sampled pairs) took 0.220 seconds.

## Connection to Week 3 LSH (A8)

This experiment does not directly invalidate Week 3's LSH result. It measures Euclidean distances between uniform points in a unit cube, whereas that LSH used Jaccard similarity on structured shingle sets. A concentration problem could still occur if the dataset's Jaccard similarities themselves become nearly equal, but that must be measured on those sets rather than inferred from this Euclidean experiment.
