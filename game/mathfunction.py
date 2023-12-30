def sign(x):
    return 1 if x >= 0 else -1


def clamp(min_n, n, max_n):
    return max(min(max_n, n), min_n)
