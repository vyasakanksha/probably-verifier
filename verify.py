import ast, astunparse, codegen, unparse, copy, sys
from astmonkey import transformers
from logic_statements import Int, Solver
from hoareify import hoareify

toverify = []

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
    print  ast.dump(i)

#for i in ast.walk(code):
#    a = [j for j in cons if not isinstance(i, j)]
#    print a

hoareify(toverify)


