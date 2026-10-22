#!/usr/bin/env python3
"""Week 7 · Task 1 — k-means, and the thing that decides the answer.

Textbook §7.1 (clustering, the curse of dimensionality), §7.3 (k-means).

k-means is four lines: pick centroids, assign every point to the nearest one,
move each centroid to the mean of its points, repeat. It always converges.

It converges to a **local** optimum, and which one depends entirely on where you
started. That is not a footnote - it is the difference between a clustering that
means something and one that does not, and you can watch it happen on nine points.

    python3 task1_kmeans.py --verify
"""
import argparse, math, random

# Three obvious blobs of three points each. Any sensible clustering finds them.
BLOBS = [(0.0, 0.0), (0.2, 0.1), (0.1, 0.2),
         (8.0, 8.0), (8.2, 8.1), (8.1, 8.2),
         (0.0, 8.0), (0.2, 8.1), (0.1, 8.2)]


def euclidean(a, b):
    """Distance between two points of any dimension."""
    if len(a) != len(b):
        raise ValueError("points must have the same dimension")
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def assign(points, centroids):
    """Nearest centroid for each point. Return a list of centroid indices.

    Ties go to the lower index, so that everybody's answer is the same.
    """
    if not centroids:
        raise ValueError("at least one centroid is required")

    # min() keeps the first item when keys tie, hence the lower index wins.
    return [min(range(len(centroids)),
                key=lambda i: euclidean(point, centroids[i]))
            for point in points]


def update(points, labels, k):
    """Move each centroid to the mean of its points.

    An empty cluster has no mean. Decide what you do - and say so, because the
    choice changes the result and there is more than one defensible answer.
    """
    if k <= 0:
        raise ValueError("k must be positive")
    if not points:
        raise ValueError("at least one point is required")
    if len(points) != len(labels):
        raise ValueError("points and labels must have the same length")

    dimension = len(points[0])
    if any(len(point) != dimension for point in points):
        raise ValueError("all points must have the same dimension")
    if any(label < 0 or label >= k for label in labels):
        raise ValueError("labels must be centroid indices")

    counts = [0] * k
    sums = [[0.0] * dimension for _ in range(k)]
    for point, label in zip(points, labels):
        counts[label] += 1
        for axis, value in enumerate(point):
            sums[label][axis] += value

    centroids = [None] * k
    for cluster in range(k):
        if counts[cluster]:
            centroids[cluster] = tuple(
                total / counts[cluster] for total in sums[cluster]
            )

    # Empty-cluster policy: move it to a point furthest from the centroid of
    # that point's current cluster.  This gives the unused cluster a useful
    # starting position instead of attempting to take the mean of no points.
    used = set()
    for cluster in range(k):
        if centroids[cluster] is None:
            candidates = (i for i in range(len(points)) if i not in used)
            point_index = max(
                candidates,
                key=lambda i: euclidean(points[i], centroids[labels[i]]),
            )
            centroids[cluster] = tuple(points[point_index])
            used.add(point_index)

    return centroids


def kmeans(points, k, init="random", seed=246, max_iter=100):
    """Run to convergence. Return (labels, centroids, sse).

    `sse` is the sum over points of the squared distance to their own centroid.
    It is what k-means minimises, and it is how you compare two runs.

    `init` is either:
        "random"   pick k points at random as the starting centroids
        "++"       k-means++ (§7.3.2): pick the first at random, then pick each
                   next one with probability proportional to the squared distance
                   to the nearest centroid already chosen

    Set `kmeans.iterations` to how many passes you used.
    """
    if not points:
        raise ValueError("at least one point is required")
    if k <= 0 or k > len(points):
        raise ValueError("k must be between 1 and the number of points")
    if max_iter <= 0:
        raise ValueError("max_iter must be positive")
    if init not in ("random", "++"):
        raise ValueError("init must be 'random' or '++'")

    rng = random.Random(seed)
    if init == "random":
        indices = rng.sample(range(len(points)), k)
    else:
        indices = [rng.randrange(len(points))]
        while len(indices) < k:
            squared = [
                min(euclidean(point, points[i]) ** 2 for i in indices)
                for point in points
            ]
            total = sum(squared)
            if total == 0:
                # All remaining points coincide with an existing centroid.
                remaining = [i for i in range(len(points)) if i not in indices]
                indices.append(rng.choice(remaining))
            else:
                # choices() implements probability proportional to D(x)^2.
                indices.append(rng.choices(range(len(points)),
                                           weights=squared, k=1)[0])

    centroids = [tuple(points[i]) for i in indices]
    previous_labels = None
    labels = []

    for iteration in range(1, max_iter + 1):
        labels = assign(points, centroids)
        if labels == previous_labels:
            kmeans.iterations = iteration
            return labels, centroids, sse_of(points, labels, centroids)
        previous_labels = labels
        centroids = update(points, labels, k)

    # The final update may change the closest centroid when max_iter is hit,
    # so return labels that correspond to the returned centroids.
    labels = assign(points, centroids)
    kmeans.iterations = max_iter
    return labels, centroids, sse_of(points, labels, centroids)


def sse_of(points, labels, centroids):
    """Sum of squared distances from each point to its assigned centroid."""
    if len(points) != len(labels):
        raise ValueError("points and labels must have the same length")
    if any(label < 0 or label >= len(centroids) for label in labels):
        raise ValueError("labels must be centroid indices")
    return sum(euclidean(point, centroids[label]) ** 2
               for point, label in zip(points, labels))


# ------------------------------------------------------------------- harness
def verify():
    fails = 0

    def check(label, ok, detail=""):
        nonlocal fails
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<50} {detail}")
        fails += not ok

    try:
        check("distance in 2d", abs(euclidean((0, 0), (3, 4)) - 5) < 1e-9)
        check("distance in 5d",
              abs(euclidean((0,) * 5, (1,) * 5) - math.sqrt(5)) < 1e-9)
    except NotImplementedError:
        print("  euclidean is still a stub"); return 1

    try:
        labels, cents, sse = kmeans(BLOBS, 3, init="++", seed=1)
    except NotImplementedError:
        print("  kmeans is still a stub"); return 1

    groups = {}
    for p, l in zip(BLOBS, labels):
        groups.setdefault(l, []).append(p)
    check("three clusters of three", sorted(len(g) for g in groups.values()) == [3, 3, 3],
          sorted(len(g) for g in groups.values()))
    check("the three blobs were recovered",
          all(max(q[0] for q in g) - min(q[0] for q in g) < 1 and
              max(q[1] for q in g) - min(q[1] for q in g) < 1
              for g in groups.values()))
    check("sse is small when clusters are right", sse < 1.0, f"sse {sse:.4f}")

    # Bad luck with random starts should sometimes be visibly worse.
    randoms = [kmeans(BLOBS, 3, init="random", seed=s)[2] for s in range(40)]
    plusplus = [kmeans(BLOBS, 3, init="++", seed=s)[2] for s in range(40)]
    check("random init sometimes lands badly", max(randoms) > min(randoms) * 5,
          f"sse from {min(randoms):.3f} to {max(randoms):.3f}")
    check("k-means++ is more reliable than random",
          sum(plusplus) / len(plusplus) <= sum(randoms) / len(randoms),
          f"mean sse: ++ {sum(plusplus) / len(plusplus):.3f} vs "
          f"random {sum(randoms) / len(randoms):.3f}")

    print(f"\n  {'all ok' if not fails else str(fails) + ' failed'}")
    return 1 if fails else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    raise SystemExit(verify() if a.verify else p.print_help())
