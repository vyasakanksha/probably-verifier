@precondition(And(x >= y, y >= z))
@postcondition(And(x >= ret, ret >= y, ret >= z, (Implies((x == y), (ret == x)))))
def avg(x, y, z):
    return (x + y)/2

    
