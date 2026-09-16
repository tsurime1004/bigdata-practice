# Observations

## Task 2

The crossover on this WSL2 machine, Intel Core i9-14900HX with 15 GiB RAM available, was between 2,000 and 4,000 documents; interpolating the measured times gives about n = 3,100. The quadratic check held: each doubling made brute force take about 4x longer after the smallest point. The unpleasant size was n = 4,000, where time ran out first: brute force took 52.88s and the full row took about 98s, while memory was still comfortable.
