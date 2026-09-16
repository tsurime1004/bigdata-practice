# Observations

## Task 1

The minhash code walks each row once because that is the version that can be streamed; scanning once per column would multiply the read cost and assumes the matrix is easy to revisit. For LSH I require the signature length to divide evenly by the band count, and raise `ValueError` for leftover rows instead of silently dropping or padding them. The S1-S4 estimate was 1.0 while the true Jaccard similarity is 2/3; using more hash functions would narrow that sampling error, at the cost of more signature computation and storage.

## Task 2

The crossover on this WSL2 machine, Intel Core i9-14900HX with 15 GiB RAM available, was between 2,000 and 4,000 documents; interpolating the measured times gives about n = 3,100. The quadratic check held: each doubling made brute force take about 4x longer after the smallest point. The unpleasant size was n = 4,000, where time ran out first: brute force took 52.88s and the full row took about 98s, while memory was still comfortable.

## Task 3

I used `n = 120` minhashes split into `b = 30` bands, so `r = n/b = 4` rows per band. The S-curve step is about `(1/b)^(1/r) = (1/30)^(1/4) = 0.427`, below the 0.6 threshold, which deliberately favors recall over extra candidates; the measured run kept 100.0% recall with only 1,620 comparisons. Moving the step the wrong way, for example by using fewer wider bands such as `b = 10, r = 12`, makes the threshold much higher at `(1/10)^(1/12) = 0.825`, which would miss many 0.6-similar pairs. The harness ignoring hashing is fair while exact similarity dominates cost, but at much larger document counts or with very long shingles/signatures the 120 hash computations per document and bucket storage would need to be counted too.
