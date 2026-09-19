"""Reference lambda/Iota helpers for the external murphy experiment.

Authored by ChatGPT (OpenAI). Standard library only. No eta rule or shortest-code claim.
Imported by research.py, adjoint.py and text_probe.py; no file writes on import.
"""
import json, pathlib, sys, time
from functools import lru_cache
sys.setrecursionlimit(20000)
started=time.monotonic()
work=0
def tick():
    global work
    work+=1
    if work>4_000_000 or time.monotonic()-started>30:
        raise TimeoutError('Verification budget exceeded; no equality claim')
V=lambda n:('v',n)
A=lambda f,x:('a',f,x)
L=lambda n,t:('l',n,t)
C=lambda n:('c',n)
def apps(*terms):
    result=terms[0]
    for term in terms[1:]:result=A(result,term)
    return result
def lams(names,term):
    for name in reversed(names.split()):term=L(name,term)
    return term
def left(t):return lams('l R',A(V('R'),L('r',A(t,A(V('l'),V('r'))))))
def bigleft(t):return L('x',A(V('x'),left(t)))
def right(c,l):return L('r',A(c,A(l,V('r'))))
def closure(tree):
    tag,*args=tree
    es=[closure(t) for t in args]
    if tag in ('I','K','S'):return C(tag)
    if tag=='Basis':return C('j')
    if tag=='One':return L('c',bigleft(V('c')))
    if tag=='Zero':return L('c',A(V('c'),C('j')))
    if tag=='Trivial':return L('x',A(V('x'),C('I')))
    if tag=='K1':return L('ignored',es[0])
    if tag=='S1':return apps(C('S'),*es)
    if tag=='S2':return apps(C('S'),*es)
    if tag=='Left':return left(es[0])
    if tag=='BigLeft':return bigleft(es[0])
    if tag=='Right':return right(*es)
    if tag=='BigRight':return L('R',A(V('R'),right(*es)))
    raise ValueError(tag)
@lru_cache(maxsize=100000)
def free(t):
    if t[0]=='v':return frozenset([t[1]])
    if t[0]=='c':return frozenset()
    if t[0]=='l':return free(t[2])-frozenset([t[1]])
    return free(t[1])|free(t[2])
def abstract(name,t):
    tick()
    if name not in free(t):return A(C('K'),t)
    if t==V(name):return C('I')
    if t[0]!='a':raise ValueError('Uneliminated abstraction')
    return apps(C('S'),abstract(name,t[1]),abstract(name,t[2]))
def ski(t):
    tick()
    if t[0]=='l':return abstract(t[1],ski(t[2]))
    if t[0]=='a':return A(ski(t[1]),ski(t[2]))
    return t
j=C('j')
iota_i=A(j,j)
iota_k=A(j,A(j,A(j,j)))
iota_s=A(j,iota_k)
def to_iota(t):
    if t[0]=='a':return A(to_iota(t[1]),to_iota(t[2]))
    if t[0]=='c':return {'I':iota_i,'K':iota_k,'S':iota_s,'j':j}[t[1]]
    raise ValueError('Not closed')
def encode(t):return 'i' if t==j else '*'+encode(t[1])+encode(t[2])
def decode(code):
    pos=0
    def tree():
        nonlocal pos
        c=code[pos];pos+=1
        if c=='i':return j
        if c=='*':return A(tree(),tree())
        raise ValueError('Invalid Iota character')
    t=tree()
    if pos!=len(code):raise ValueError('Unread Iota suffix')
    return t
def db(t,names=()):
    if t[0]=='v':return ('v',names.index(t[1]))
    if t[0]=='c':return t
    if t[0]=='l':return ('l',db(t[2],(t[1],)+names))
    return A(db(t[1],names),db(t[2],names))
x,y,z=map(V,['x','y','z'])
definitions={
    'I':db(L('x',x)),
    'K':db(lams('x y',x)),
    'S':db(lams('x y z',A(A(x,z),A(y,z)))),
    'j':db(L('x',apps(x,C('S'),C('K')))),
}
@lru_cache(maxsize=200000)
def shift(t,delta,cutoff=0):
    tick()
    if t[0]=='v':return ('v',t[1]+delta if t[1]>=cutoff else t[1])
    if t[0]=='c':return t
    if t[0]=='l':return ('l',shift(t[1],delta,cutoff+1))
    return A(shift(t[1],delta,cutoff),shift(t[2],delta,cutoff))
@lru_cache(maxsize=200000)
def subst(t,index,replacement):
    tick()
    if t[0]=='v':return replacement if t[1]==index else t
    if t[0]=='c':return t
    if t[0]=='l':return ('l',subst(t[1],index+1,shift(replacement,1)))
    return A(subst(t[1],index,replacement),subst(t[2],index,replacement))
def beta(body,arg):return shift(subst(body,0,shift(arg,1)),-1)
@lru_cache(maxsize=200000)
def whnf(t):
    tick()
    if t[0]=='c':return whnf(definitions[t[1]])
    if t[0]!='a':return t
    f=whnf(t[1])
    if f[0]=='l':return whnf(beta(f[1],t[2]))
    return A(f,t[2])
@lru_cache(maxsize=200000)
def normal(t):
    tick()
    t=whnf(t)
    if t[0]=='l':return ('l',normal(t[1]))
    if t[0]=='a':return A(normal(t[1]),normal(t[2]))
    return t
def pretty(t,names=()):
    if t[0]=='v':return names[t[1]]
    if t[0]=='l':
        name=chr(97+len(names))
        return '(λ'+name+'.'+pretty(t[1],(name,)+names)+')'
    return '('+pretty(t[1],names)+' '+pretty(t[2],names)+')'
