@precondition(True)
@postcondition(And(ret >= x), (ret >= y), Or((ret == x), ret == y))
def max3i(x, y): 
    if x > y:
        return x
    else: 
        return y
