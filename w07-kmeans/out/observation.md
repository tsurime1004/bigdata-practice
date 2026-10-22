# Task 1 observations

For an empty cluster, I move its centroid to the point furthest from that point's current cluster mean; keeping the old centroid instead would be stable but could leave the cluster unused. Across 40 seeds, random initialization recovered the blobs 27 times, while k-means++ recovered them 40 times.
k-means++ pays for distances before iteration to obtain more reliable, well-separated starts, although random initialization may be preferable when initialization cost dominates or many restarts are cheap. SSE alone cannot select k because it never increases as k grows and reaches zero when every point gets its own cluster.

# Task 2 observations

For n=1000, contrast fell below 1 at dimension 50. Changing n at a fixed dimension changed the extreme-based contrast, so both dimension and sample size matter.
This does not directly threaten Jaccard LSH: shingle sets and Jaccard similarity are not uniform Euclidean points, so their similarity distribution must be measured separately.

# Task 3 observations

I store one upper bound and one lower bound per point (two extra numbers). The maximum of the second-nearest-centroid lower bound and half the nearest centroid-to-centroid distance eliminates most work; maintaining it costs centroid-pair distances, k centroid-movement distances, and O(n) bound updates per iteration.
The final SSE difference was exactly zero because the bounds only skip comparisons that the triangle inequality proves cannot change an assignment. The first iteration used 240,078 of 1,151,064 distance calls (20.9%) because no point had usable bounds yet.
