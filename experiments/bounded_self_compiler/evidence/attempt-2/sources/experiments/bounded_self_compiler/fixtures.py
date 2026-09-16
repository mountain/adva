from language import SOURCE, prim as p, seq, if_, while_, integer, node

REGS = [{'name':n,'kind':k} for n,k in [('x','integer'),('one','integer'),('limit','integer'),
        ('condition','boolean'),('data','data'),('temp','data'),('stack','stack'),('length','integer')]]

def program(name, body):
    return {'schema':SOURCE,'name':name,'registers':REGS,'body':body}
def ret(): return seq(p('box_integer',src=0,dst=4),p('return',src=4))
def constant(n): return p('constant',dst=0,value=n)
def loop(n):
    return seq(constant(0),p('constant',dst=1,value=1),p('constant',dst=2,value=n),p('constant',dst=7,value=0),
        p('equal',left=0,right=2,dst=3),if_(3,p('equal',left=1,right=7,dst=3),p('equal',left=1,right=1,dst=3)),
        while_(3,seq(p('add',left=0,right=1,dst=0),p('equal',left=0,right=2,dst=3),
            if_(3,p('equal',left=1,right=7,dst=3),p('equal',left=1,right=1,dst=3)))))
def cases():
    bodies = [
        ('literal',seq(constant(-7),ret()),integer(0)),
        ('exact-large',seq(constant(9007199254740993),p('constant',dst=1,value=2),p('add',left=0,right=1,dst=0),ret()),integer(0)),
    ]
    for yes in (True,False):
        bodies.append(('if-'+str(yes).lower(),seq(constant(0),p('constant',dst=1,value=int(not yes)),
            p('equal',left=0,right=1,dst=3),if_(3,constant(11),constant(22)),ret()),integer(0)))
    for n,name in ((0,'zero'),(5,'five')):
        bodies.append(('while-'+name,seq(loop(n),ret()),integer(0)))
    bodies += [
        ('nested-control',seq(loop(3),p('equal',left=0,right=2,dst=3),if_(3,seq(loop(2),p('multiply',left=0,right=2,dst=0)),constant(-1)),ret()),integer(0)),
        ('data-fields',seq(p('input',dst=4),p('length',src=4,dst=7),p('constant',dst=0,value=1),
            p('field_dynamic',src=4,index=0,dst=5),p('clear',stack=6),p('push',stack=6,src=5),
            p('box_integer',src=7,dst=4),p('push',stack=6,src=4),p('stack_length',stack=6,dst=7),
            p('pack',stack=6,tag=77,dst=4),p('return',src=4)),node(42,[integer(3),integer(9)])),
        ('overflow',seq(constant(2**63-1),p('constant',dst=1,value=1),p('add',left=0,right=1,dst=0),ret()),integer(0)),
        ('bad-dynamic-field',seq(p('input',dst=4),constant(-1),p('field_dynamic',src=4,index=0,dst=5),p('return',src=5)),node(1,[])),
    ]
    return [(name,program(name,body),data) for name,body,data in bodies]
