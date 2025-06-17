# x, y: ndarray, dtype=bool, index 0 should be True
def CalcRemainder(x, y):
    x = x.copy()
    for i in range(x.shape[0] - y.shape[0] + 1):
        if x[i]:
            x[i:i + y.shape[0]] ^= y
    return x[-y.shape[0] + 1:]
