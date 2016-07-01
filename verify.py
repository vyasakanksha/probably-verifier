import ast, astunparse, codegen, unparse, copy
from astmonkey import transformers
from logic_statements import Int, Solver

class PStmt():
    typ = ""
    value = []

    def __init__(self, typ, value):
        self.typ = typ
        self.value = value

    def __repr__(self):
        return str(self.typ + ":" + str(self.value))

toverify = [] # Functions that need to be verified.
verification = []
codes = ""

# Any statement that is not in this list is outside the scope of this verification engine
cons = [ast.For, ast.If, ast.While, ast.With, ast.Call, ast.Assign, ast.Print, ast.Return, ast.Compare, ast.Num, ast.BoolOp, ast.Name, ast.Subscript, ast.Attribute, ast.List, ast.Tuple, ast.operator, ast.cmpop, ast.arguments, ast.expr_context, ast.BinOp, ast.boolop, ast.UnaryOp, ast.Dict,ast.Set, ast.Str, ast.keyword, ast.FunctionDef]

stmt = [ast.Assign, ast.Return, ast.FunctionDef]

# Test file
f = open('test.py', 'r+')
contents = f.read()

""" Identify functions to verify """
code = ast.parse(contents)
print(ast.dump(code))

# Find all the function declarations
fn = [x for x in ast.walk(code) if isinstance(x, ast.FunctionDef)]

# Identify the ones that don't have @verified as a decorator
for i in fn:
    if not any(d.func.id == 'verified' for d in i.decorator_list):
        toverify.append(i)

# Identify the ones that don't have @verified as a decorator
for i in toverify:
    print  ast.dump(i)

class Paths(ast.NodeVisitor):
    paths = [[]]

    def visit_FunctionDef(self, node):
        self.paths = [[]]
        print("fdef")
        print ast.dump(node)
        pre = [d for d in node.decorator_list if d.func.id == 'precondition']

        precondition = PStmt("precondition",  [codegen.to_source(a) for a in pre[0].args])

        self.paths[-1].append(precondition)
        self.generic_visit(node)
        return self.paths

    def visit_For(self, node):
        print("For")
        print ast.dump(node)

        inv_node = [n for n in node.body if (isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and (n.value.func.id == 'invariant'))]

        print eval(codegen.to_source(node.iter))[0]

        pre_inv = PStmt("stmt", str(node.target.id +  ' = ' + str(eval(codegen.to_source(node.iter))[0])))
        post_inv = PStmt("stmt", str(node.target.id + '=' + str(codegen.to_source(node.iter.args[0]))))
        inv = PStmt('stmt',  [codegen.to_source(a) for a in inv_node[0].value.args])

        self.paths[-1].append(pre_inv)
        self.paths[-1].append(inv)
        self.paths.append([])
        self.paths[-1].append(inv)
        self.generic_visit(node)
        a = PStmt("assign", [node.target.id, node.target.id + '+ 1'])
        self.paths[-1].append(a)
        self.paths[-1].append(inv)
        self.paths.append([])
        self.paths[-1].append(inv)
        self.paths[-1].append(post_inv)
    
    def visit_While(self, node):
        print("while")
        print ast.dump(node)

        print codegen.to_source(node.test)
        
        inv_node = [n for n in node.body if (isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and (n.value.func.id == 'invariant'))]
        inv = PStmt('stmt',  [codegen.to_source(a) for a in inv_node[0].value.args])
        post_inv = PStmt("stmt", str("Not" + codegen.to_source(node.test)))

        self.paths[-1].append(inv)
        self.paths.append([])
        self.paths[-1].append(inv)
        self.generic_visit(node)
        self.paths[-1].append(inv)
        self.paths.append([])
        self.paths[-1].append(inv)
        self.paths[-1].append(post_inv)

    def visit_Assign(self, node):
        print("Assign")
        print ast.dump(node)
        if isinstance(node.targets[0], ast.Name):
            a = PStmt("assign", [node.targets[0].id, codegen.to_source(node.value)])
            if isinstance(node.value, ast.Call):
                print ast.dump(node.value)
                a = [f for f in  toverify if node.value.func.id == f.name]
                if len(a) > 0:
                    fprecond, fpostcond = self.find_conds(a[0])
                    
                    self.paths[-1].append(fprecond)
                    self.paths.append([])
                    self.paths[-1].append(fpostcond)
                    a = PStmt("assign", [node.targets[0].id, "ret" + node.value.func.id])
        #elif isinstance(node.targets[0], ast.Tuple):
        self.paths[-1].append(a)
    
    def visit_Return(self, node):
        print("Return")
        print ast.dump(node)
        a = PStmt("return",['ret', node.value.id])# [node.targets[0].id, codegen.to_source(node.value)])
        self.paths[-1].append(a)
    
    def visit_Call(self, node):
        a = [f for f in  toverify if node.func.id == f.name]
        if len(a) > 0:
            fprecond, fpostcond = self.find_conds(a[0])
            self.paths[-1].append(fprecond)
            self.paths.append([])
            self.paths[-1].append(fpostcond)
            self.generic_visit(node)
        else: 
            self.generic_visit(node)
    
    def visit_If(self, node):
        print("if")
        print codegen.to_source(node.test)
        ifs = PStmt("IFSTART", codegen.to_source(node.test))
        ife = PStmt("IFEND", 7)
        self.paths[-1].append(ifs)
        self.generic_visit(node)
        self.paths[-1].append(ife)

    def find_conds(self, node):
        pre = [d for d in node.decorator_list if d.func.id == 'precondition']
        post = [d for d in node.decorator_list if d.func.id == 'postcondition']

        precond = PStmt("stmt",  [codegen.to_source(p) for p in pre[0].args])
        postcond = PStmt("stmt", [codegen.to_source(p) for p in post[0].args])

        return precond, postcond


def if_situation(paths):
    newp = []
    for p in paths:
        ifindex = [p.index(s) for s in p if s.typ == "IFSTART"]
        ifeindex = [p.index(s) for s in p if s.typ == "IFEND"]
        if len(ifindex) > 0:
            p1 = copy.deepcopy(p)

            p[ifindex[0]] = PStmt("stmt", p[ifindex[0]].value)
            p1[ifindex[0]] = PStmt("stmt", "Not" + str(p[ifindex[0]].value))

            del p[ifeindex[0]]
            del p1[ifindex[0]+1:ifeindex[0]+1]

            newp.append(p)
            newp.append(p1)
    if len(newp) > 0:
        return if_situation(newp)
    else: 
        return paths

def returns(path, fname, postcond):
    for p in range(len(path)):
        print p, path[p]
        if path[p].typ == "return":
            path[p] = PStmt("Return", ["ret" + fname, path[p].value[1]])
            path.append(postcond)
    print "RETURN", path
    return path


print('xx')

vcode = []
postconds = []

for i in range(len(toverify)):
    post = [str(d.args for d in toverify[i].decorator_list if d.func.id == 'postcondition']
    temp =  [str(codegen.to_source(a)).replace("ret", "ret" + toverify[i].name) for a in post[0].args]
    postcond = PStmt("postcondition", temp)
    postconds.append(postconds)

    def walk(node):
        print 'NODE', node
        if not hasattr(node, 'body'):
            return
        for p in node.body:
            walk(p)

    p = Paths().visit(toverify[i])
    vcode.append(p)

for j in range(len(vcode)):
    p = vcode[j]
    print "Path"
    for i in range(len(p)):
        p[i:i] = if_situation([p[i]])
        del p[i]
        
    for i in range(len(p)):
        p[i] = returns(p[i], toverify[j].name, postconds[j])

    print "START"
    for i in p:
        print i
    print "END"

"""
for i in range(len(toverify)):
    node = ast.parse(ast.walk(toverify[i]))
    for f in node:
        print f
        if any(isinstance(f, s) for s in stmt):
            print f
            if isinstance(f, ast.FunctionDef):
                node, precondition, postcondition = Logify().visit(f)
                verification[i].append(codegen.to_source(precondition))
            else: 
                node, verify_stmt = Logify().visit(f)
                verification[i].append(codegen.to_source(verify_stmt))
            print 'GGGG', codegen.to_source(node)
            codes += codegen.to_source(node)
    print 'v', verification
    print ast.dump(node)
    print codes
"""

print verification

