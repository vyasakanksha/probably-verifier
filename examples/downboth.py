@precondition(And(x >= 0, y >= 0))
@postcondition(ret == z + x + y)
def downboth():
    if x == 0 and y ==0:
        return z
    elif x > y:
        w = downboth((x-1),y,(z-1))
        return w
    else:
        w = downboth(x, (y-1), z+1)
        return w

@precondition(And(x >= 0, y >= 0))
@postcondition(ret == x + y)
def f():
    z = 0
    w = downboth(x,y,z)
    return w

