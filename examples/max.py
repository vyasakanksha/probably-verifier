@precondition(True)
@postcondition(And(And(ret >= x, ret >= y), (Or(ret == x,ret == y))))
def max(x, y):
    m = x + y;
    m = m - x;
    return m;
