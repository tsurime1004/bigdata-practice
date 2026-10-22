#!/usr/bin/env python3
"""Week 7 · Task 3 — The same clustering, with far fewer distances.

Textbook §7.3, and §7.1.3 for why distance is the expensive part.

`NaiveKMeans` does what the definition says: every iteration, compare every
point with every centroid. That is n x k distance computations per pass, and on
a real dataset the distance computation is almost the entire cost.

Most of that work is wasted. After the first couple of iterations, most points
do not change cluster, and most centroids barely move. The triangle inequality
lets you prove a point cannot have changed cluster **without measuring it**.

    python3 bench.py
    python3 bench.py --yours

Correctness first: your final SSE must match the baseline's. Fewer distances
with a worse clustering is not an improvement, it is a different algorithm.
"""


class NaiveKMeans:
    """Every point against every centroid, every iteration."""

    def __init__(self, k, max_iter=50):
        self.k, self.max_iter = k, max_iter

    def run(self, points, initial_centroids, distance):
        centroids = list(initial_centroids)
        labels = [None] * len(points)
        for self.iterations in range(1, self.max_iter + 1):
            changed = False
            for i, p in enumerate(points):
                best, bi = None, 0
                for j, c in enumerate(centroids):
                    d = distance(p, c)
                    if best is None or d < best - 1e-12:
                        best, bi = d, j
                if labels[i] != bi:
                    labels[i] = bi
                    changed = True
            centroids = _means(points, labels, self.k, centroids)
            if not changed:
                break
        return labels, centroids


def _means(points, labels, k, previous):
    out = []
    for j in range(k):
        group = [p for p, l in zip(points, labels) if l == j]
        if group:
            out.append(tuple(sum(v) / len(group) for v in zip(*group)))
        else:
            out.append(previous[j])
    return out


class YourKMeans:
    """Your k-means.

        __init__(k, max_iter=50)
        run(points, initial_centroids, distance) -> (labels, centroids)

    Same starting centroids, same `distance` function - which is counted. That
    counter is your score.

    The idea, from §7.3 and the triangle inequality:

        if a point is much closer to its current centroid than that centroid
        moved, and than any other centroid could have come, then it cannot have
        changed cluster, and you do not have to measure anything

    Keeping enough bookkeeping to make that test cheap, without keeping so much
    that the bookkeeping costs more than the distances, is the task.

    You may call `distance` on two centroids, and those calls are counted too -
    which is the correct accounting, since that is real work. There are k of
    them and n points, and k is much smaller than n. That asymmetry is the
    whole opening.
    """

    def __init__(self, k, max_iter=50):
        if k <= 0:
            raise ValueError("k must be positive")
        if max_iter <= 0:
            raise ValueError("max_iter must be positive")
        self.k = k
        self.max_iter = max_iter
        self.iterations = 0
        self.first_iteration_calls = 0
        self.bound_prunes = 0

    def run(self, points, initial_centroids, distance):
        if len(initial_centroids) != self.k:
            raise ValueError("initial_centroids must contain k centroids")
        if not points:
            raise ValueError("at least one point is required")

        centroids = list(initial_centroids)
        labels = [None] * len(points)

        # Hamerly bounds: upper[i] bounds the distance to the assigned centre;
        # lower[i] bounds the distance to every competing centre.
        upper = [float("inf")] * len(points)
        lower = [0.0] * len(points)
        calls = 0

        def measured(a, b):
            nonlocal calls
            calls += 1
            return distance(a, b)

        for iteration in range(1, self.max_iter + 1):
            self.iterations = iteration

            # separation[j] is half the distance from centre j to its nearest
            # other centre.  If upper <= separation, no rival can be closer.
            separation = [float("inf")] * self.k
            for left in range(self.k):
                for right in range(left + 1, self.k):
                    gap = measured(centroids[left], centroids[right]) / 2.0
                    if gap < separation[left]:
                        separation[left] = gap
                    if gap < separation[right]:
                        separation[right] = gap

            changed = False
            for i, point in enumerate(points):
                assigned = labels[i]
                if assigned is not None:
                    threshold = max(lower[i], separation[assigned])
                    if upper[i] <= threshold:
                        self.bound_prunes += 1
                        continue

                    # Tighten a possibly stale upper bound before paying for a
                    # full scan.  Often this alone proves the assignment safe.
                    upper[i] = measured(point, centroids[assigned])
                    if upper[i] <= threshold:
                        self.bound_prunes += 1
                        continue

                best_distance = None
                second_distance = float("inf")
                best_index = 0
                for j, centroid in enumerate(centroids):
                    if assigned is not None and j == assigned:
                        candidate = upper[i]
                    else:
                        candidate = measured(point, centroid)

                    # Match NaiveKMeans's deterministic lower-index tie rule.
                    if (best_distance is None or
                            candidate < best_distance - 1e-12):
                        second_distance = best_distance if best_distance is not None else float("inf")
                        best_distance, best_index = candidate, j
                    elif candidate < second_distance:
                        second_distance = candidate

                if labels[i] != best_index:
                    labels[i] = best_index
                    changed = True
                upper[i] = best_distance
                lower[i] = second_distance

            new_centroids = _means(points, labels, self.k, centroids)
            movement = [measured(old, new)
                        for old, new in zip(centroids, new_centroids)]
            largest_movement = max(movement)
            if iteration == 1:
                self.first_iteration_calls = calls

            # Triangle inequality keeps the bounds valid after centres move.
            for i, label in enumerate(labels):
                upper[i] += movement[label]
                lower[i] = max(0.0, lower[i] - largest_movement)
            centroids = new_centroids

            if not changed:
                break

        self.distance_calls = calls
        return labels, centroids
