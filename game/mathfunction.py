from math import sqrt


def sign(x):
    return 1 if x >= 0 else -1


def clamp(min_n, n, max_n):
    return max(min(max_n, n), min_n)


def distanse2D(p0, p1):
    return sqrt((p1[0] - p0[0]) ** 2 + (p1[1] - p0[1]) ** 2)
