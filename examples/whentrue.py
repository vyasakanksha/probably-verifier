@precondition(True)
@postcondition(r1 > r2)
def whentrue(x):
    r1 = x + 1;
    r1 = 2 * r1;
    r2 = 3 * x;
    r2 = r2 + 1;
    return r1, r2

    
