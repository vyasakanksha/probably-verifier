@precondition(x >= 0)
@postcondition(ret == x + y)
def sumrec(x, y):
    if x == 0:
        return y
    else:
        z = sumrec(x - 1, y + 1)
        return z


@precondition(x >= 0)
@postcondition(r == x)
def f(x):
    y = 0
    z = sumrec(x, y)
    return z

