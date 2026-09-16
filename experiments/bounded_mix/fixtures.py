"""Two small object languages plus generic v1 source-control fixtures."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from experiments.bounded_self_compiler.language import SOURCE, prim as p, seq, if_, while_, seed_compile, node, integer

REGS=[{'name':n,'kind':k} for n,k in [
    ('bundle','data'),('program','data'),('argument','data'),('a','data'),('b','data'),
    ('x','integer'),('y','integer'),('z','integer'),('tag','integer'),('probe','integer'),
    ('condition','boolean')]]


def lower(name,body):
    return seed_compile({'schema':SOURCE,'name':name,'registers':REGS,'body':body})


def interpreters():
    unpack=seq(p('input',dst=0),p('field',src=0,arity=2,index=0,dst=1),
               p('field',src=0,arity=2,index=1,dst=2),p('as_integer',src=2,dst=5))
    result=seq(p('box_integer',src=5,dst=3),p('return',src=3))
    affine=lower('affine-object-interpreter',seq(unpack,
        p('field',src=1,arity=2,index=0,dst=3),p('as_integer',src=3,dst=6),
        p('field',src=1,arity=2,index=1,dst=4),p('as_integer',src=4,dst=7),
        p('multiply',left=5,right=6,dst=5),p('add',left=5,right=7,dst=5),result))
    tagged=lower('tagged-object-interpreter',seq(unpack,
        p('tag',src=1,dst=8),p('constant',dst=9,value=0),p('equal',left=8,right=9,dst=10),
        p('field',src=1,arity=1,index=0,dst=3),p('as_integer',src=3,dst=6),
        if_(10,p('add',left=5,right=6,dst=5),seq(p('constant',dst=9,value=1),
            p('equal',left=8,right=9,dst=10),if_(10,p('multiply',left=5,right=6,dst=5),
                p('reject',reason='unsupported object tag')))),result))
    return [('affine',affine,[node(0,[integer(2),integer(3)]),node(0,[integer(-1),integer(7)])]),
            ('tagged',tagged,[node(0,[integer(5)]),node(1,[integer(3)]),node(2,[integer(1)])])]


def controls():
    repeated=lower('repeated-input',seq(p('input',dst=0),p('input',dst=1),p('return',src=1)))
    loop=lower('bounded-loop-and-branch',seq(p('input',dst=0),p('field',src=0,arity=2,index=1,dst=2),
        p('as_integer',src=2,dst=5),p('constant',dst=6,value=-1),p('constant',dst=7,value=0),
        p('equal',left=5,right=7,dst=10),
        if_(10,p('equal',left=6,right=7,dst=10),p('equal',left=7,right=7,dst=10)),
        while_(10,seq(p('add',left=5,right=6,dst=5),p('equal',left=5,right=7,dst=10),
            if_(10,p('equal',left=6,right=7,dst=10),p('equal',left=7,right=7,dst=10)))),
        p('box_integer',src=5,dst=3),p('return',src=3)))
    uninitialized=lower('uninitialized',p('return',src=3))
    return [('repeated-input',repeated,integer(9),integer(2)),
            ('loop',loop,node(9,[]),integer(3)),
            ('uninitialized',uninitialized,integer(0),integer(0))]
