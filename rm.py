from ghost_vars import Randomized
from ghost_funcs import determ_subproc, pre_condition, sample_space
import random, sympy

@sample_space('PRIME, NOTPRIME')
@pre_condition(lambda n, k: n >= 5 and k > 0)
@post_condition(lambda ret: P[NOTPRIME] <= (0.25)^k if ret is True else NOTPRIME)
def rmprimality(n, k):
    i = 0
    w = Randomized()
    
    invarient(lambda w: P[PRIME] <= (0.25)^i and w.status is 0);
    for i in range(k):
        w = Randomized(range(2, n-1))
        
        x = isWitness(p=n, rvar=w)

        if x:
            return False
    return True

@verified()
@sample_space('WITNESS, NOTWITNESS')
@determ_subproc()
@pre_condition(lambda p,rvar: p >= 5 and rvar.status is 1 and rvar.univ == range(2, n-1))
@post_condition(lambda ret: WITNESS if ret is True else NOTWITNESS)
def isWitness(p, rvar):
    possibleWitness = rvar.value
    
    @verified()
    def decompose(n):
       exponentOfTwo = 0
     
       while n % 2 == 0:
          n = n/2
          exponentOfTwo += 1
     
       return int(exponentOfTwo), int(n)

    exponent, remainder = decompose(p - 1)
    possibleWitness = pow(possibleWitness, remainder, p)

    if possibleWitness == 1 or possibleWitness == p - 1:
        return False

    for _ in range(exponent):
        possibleWitness = pow(possibleWitness, 2, p)

        if possibleWitness == p - 1:
            return False
    return True

for i in range(100):
    n = random.choice(range(6,100))
    print(n)
    a = rmprimality(n, 10000)
    b = sympy.isprime(n)
    if a != b:
        print(a,b)
