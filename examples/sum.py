@precondition(x >= 0)
@postcondition(ret == x + y)
def sum(x, y):
    i = 0
    z = y
    while i < x:
        z = z + 1
        i = i + 1
    return z

