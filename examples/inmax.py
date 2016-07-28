@precondition(True)
@postcondition(And((ret <= x), (ret <= y), Or((ret == x), (ret == y))))
def min(x, y):
    if x < y:
        return x
    else:
        return y

@precondition(True)
@postcondition(And((ret <= x), (ret <= y), Or((ret == x), (ret == y))))
def max(x, y):
    z = min(x, y)
    return x + y - z
    
