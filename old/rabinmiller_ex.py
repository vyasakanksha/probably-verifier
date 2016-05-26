import random as rand

 precondition: w is uniformly random in [1,n-2], n>3
def isWittness(w, n):
 postcondition: return = False, P[n is not prime] = 1 and return = True, P[n is not prime] <(0.25)

# precondition: n > 3, k > 0
def rmprimality(n, k):
   univ_list = range(1, n - 2)
   W = PDist(univ_list)
   for _ in range(k):
   # midcondition: x = True, P[n is not prime] < (0.25)
   #                return = False, P[n is not prime] = 1 
      w = rand.choice(W)
      x = isWittness(w, n)

      if x is False:
         result x
   return x
# postcondition: return = True, P[n is not prime] < (0.25)^k 
#                return = False, P[n is not prime] = 1 
