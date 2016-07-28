@precondition(True)
@postcondition(And(ret >= x), (ret >= y),(ret >= z), Or((ret == x), ret == y, ret >= z))
def max3(x, y): 
    m = x
    if y > m:
        m = y
    if z > m:
        m = z
    return m
