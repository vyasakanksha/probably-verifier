""" In this file we define all the ghost wrapper functions for verification.
Author: vyasakanksha@gmail.com """

from ghost_vars import Event
import functools, copy

# Converts all the wrapper funtions into decorators what wrap the 
# probabilistic function.
def condition(pre_condition=None, determ_subproc=None, sample_space=None):
    def decorator(func):
        @functools.wraps(func) # presever name, docstring, etc
        def wrapper(*args, **kwargs): #NOTE: no self
            a = {}
            # checks precondition statements
            if pre_condition is not None:
               assert pre_condition(*args, **kwargs)
            # Inits each var in sample space as an event
            if sample_space is not None:
                try:
                    events = sample_space.split(',')
                except AttributeError as err:
                    print('Error: sample space should be a comma separated string')
                    raise
                for e in events:
                    e = e.strip()
                    try:
                        exec("%s = Event().__nonzero__()" % (e)) in globals()
                    except SyntaxError as err:
                        print('Error: invalid event in sample space')
                        raise
            retval = func(*args, **kwargs) # call original function or method
            # Sets the status of the randomized variable to 0
            if determ_subproc is not None:
                kwargs['rvar'].status = 0
            return retval
        return wrapper
    return decorator

def pre_condition(check):
    return condition(pre_condition=check)

def sample_space(lst):
    return condition(sample_space=lst)

def determ_subproc():
    return condition(determ_subproc=0)


