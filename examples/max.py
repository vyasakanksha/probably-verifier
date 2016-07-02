@precondition(True)
@postcondition(ret >= a and ret >= b and (ret == a or ret == b))
def max(x, y):
    m = x + y;
    m = m - x;
    return m;
