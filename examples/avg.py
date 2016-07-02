@precondition(x >= y and y >= z)
@precondition(x >= ret and ret >= y and ret >= z and (x == y ==> ret == x))
def avg(x, y, z):
    return (x + y)/2

    
