import ast, astunparse, codegen, unparse, copy, sys, subprocess, os, errno
from astmonkey import transformers
from logic_statements import Int, Solver
from hoareify import hoareify
sys.path.append("/Users/vyasa/Research/probably-verifier")
from z3.build.z3 import Int, solve, Implies, Solver, And, Or, Not

def apply_implication(lst):
    if len(lst) <= 1:
        return lst
    else:
       return "Implies(" + apply_and(lst[1:]) + "," + lst[0] + ")"

def apply_and(lst):
    if len(lst) > 1:
        return "(And(" + ','.join(lst) + "))"
    else:
        return "(" + ','.join(lst) + ")"


def apply_hoare(hoare_stmts):
    z3code = ""
    final_hoare = []
    solver = []
    print "HO", hoare_stmts
    for stmt in hoare_stmts:
        final_hoare = [stmt[-1].value]
        hoarestmt = ""
        for k in reversed(stmt[0:-1]):
            if k.typ == 'STMT':
                final_hoare.append(k.value)
            if k.typ == 'ASSIGNMENT':
                final_hoare = [j.replace(k.value[0], k.value[1]) for j in final_hoare]
        final_hoare = apply_implication(final_hoare)
        solver.append(final_hoare)
    print "\nFINALH\n"
    for s in solver:
        print s


    z3code = ("s = Solver()\n")
    for v in var:
        z3code += v + " = Int('" + v + "')\n"

    for s in solver:
        z3code += "s.add(Not(" + s + '))\n'
    z3code += "check = s.check()\n"

    print "\n",  z3code, "\n"
    exec(z3code)
    print check
    if str(check) is 'sat':
        for s in solver:
            z3code += "solve(Not(" + s + '))\n'
            exec(z3code)

toverify = []
solver = []
# Any statement that is not in this list is outside the scope of this verification engine
cons = [ast.For, ast.If, ast.While, ast.With, ast.Call, ast.Assign, ast.Print, ast.Return, ast.Compare, ast.Num, ast.BoolOp, ast.Name, ast.Subscript, ast.Attribute, ast.List, ast.Tuple, ast.operator, ast.cmpop, ast.arguments, ast.expr_context, ast.BinOp, ast.boolop, ast.UnaryOp, ast.Dict,ast.Set, ast.Str, ast.keyword, ast.FunctionDef]

stmt = [ast.Assign, ast.Return, ast.FunctionDef]

# Test file
try:
    f = open(sys.argv[1], 'r+')
except:
    raise "No Argument"
contents = f.read()

""" Identify functions to verify """
code = ast.parse(contents)

# Find all the function declarations
fn = [x for x in ast.walk(code) if isinstance(x, ast.FunctionDef)]

# Identify the ones that don't have @verified as a decorator
for i in fn:
    if not any(d.func.id == 'verified' for d in i.decorator_list):
        toverify.append(i)

# Identify the ones that don't have @verified as a decorator
for i in toverify:
    print i.name
    var = [x.id for x in ast.walk(code) if isinstance(x, ast.Name)]

    var = set(var) - set(['precondition', 'postcondition', 'True', 'Flase', 'verified', 'proof_truth', 'range', 'invariant', 'And', 'Or', 'Implies', 'ret'] + [k.name for k in toverify])
    #print [k.name for k in toverify]
    #print "XXX", var
    #var = [x.replace(k.name, "ret" + k.name) for x in var if k.name in toverify]

    var = var | set(["ret" + k.name for k in toverify])
    #print 'VAR', var

    #print ast.dump(i)
    hoare_stmts = hoareify(i, toverify)
    print "\nSTMTS"
    for stmt in hoare_stmts:
        print 'h', stmt

    apply_hoare(hoare_stmts)

