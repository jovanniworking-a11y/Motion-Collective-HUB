# ml03 · Group clips by look (k-means)
Give every clip two numbers, average brightness and amount of motion, and let the computer find the groups (dark slow
clips, bright fast clips…). Nobody labels anything: that's unsupervised learning.

Fill in `exercise.py`, from scratch with NumPy:
1. `assign(points, centers)`: for each point, the index of the nearest center.
2. `update(points, labels, k)`: each new center = the mean of its points.
3. `kmeans(points, k, steps=20, seed=0)`: start from `k` random points as centers, then repeat assign + update. Return `(centers, labels)`.

Why the check runs your k-means 10 times: a bad random start can leave two centers in one group and miss another.
Real tools do the same thing (restart several times, keep the run with the smallest total distance).
