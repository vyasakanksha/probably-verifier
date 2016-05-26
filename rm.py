from ghost_vars import Randomized
from ghost_funcs import determ_subproc, pre_condition, sample_space
import random, sympy

@sample_space('PRIME, NOTPRIME')
@pre_condition(lambda n,k: n >= 5 and k > 0)
#@postcondition: if return = True: assert P[NOTPRIME] <= (0.25)^k, if return = False: assert P[NOTPRIME] = 1)
def rmprimality(n, k):
    i = 0
    w = Randomized()
    
    for i in range(k):
        #@invarient(P[PRIME] <= (0.25)^i, w.status = 0)
        w = Randomized(range(2, n-1))
        
        x = isWitness(p=n, rvar=w)

        if x:
            return False
    return True

@sample_space('WITNESS, NOTWITNESS')
@determ_subproc()
@pre_condition(lambda p,rvar: p >= 5 and rvar.status is 1 and rvar.univ == range(2, n-1))
#@postcondition(if return = True: WITNESS, if return = False: NOTWITNESS)
def isWitness(p, rvar):
    possibleWitness = rvar.value

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
