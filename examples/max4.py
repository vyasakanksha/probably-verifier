@precondition(True)
@postcondition(And(ret >= x), (ret >= y), (ret >= z), Or((ret == x), (ret == y), (ret == z))) 
def max4(x, y, z):
    if x > y and x > z:
        return x
    elif y > x and y > z:
        return y 
    else:
        return z
