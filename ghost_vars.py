""" Creates ghost variables used for verification """
import random

# Randomized Variable
class Randomized():
    def __init__(self, lst=None):
        if lst:
            self.status = 1
            self.univ = lst
            self.value = random.choice(lst)
        else:
            self.status = 0
            self.univ = None
            self.value = None

    def __repr__(self):
        #return str(self.value)
        return "value = %i, status = %i, univ = %s" % (self.value, self.status, ','.join(str(i) for i in self.univ))

# Event Variable
class Event():
    def __bool__(self):
        return False
    __nonzero__=__bool__
    
"""
    def __or__(self, other):
        return self, other
    
    def __and__(self, other):
        return self, other

def __init__(self, st):
    top = st.split('|')
    if len(top) > 1:
        given = top[1].split(',') 
        find = top[0].split(',') 
        given = [x.strip(' ') for x in given]
        find = [x.strip(' ') for x in find]
    else:
        find = top[0].split(',') 
        find = [x.strip(' ') for x in find]
    print(top)
"""

