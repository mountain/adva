#!/usr/bin/env python3
"""Original bounded external verifier. Codex (OpenAI), Unknown v0.3.
Documentary keys and hashes do not allocate native Adva identities.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
from itertools import product, combinations
from math import comb, prod
from pathlib import Path
import hashlib
import json
import resource
import signal
import sys

class Limit(Exception): pass
class Refused(Exception): pass
NODES = 0
LIMIT = 300000

def tick(n=1):
    global NODES
    NODES += n
    if NODES > LIMIT: raise Limit('finite node allowance exhausted')

def require(ok, message):
    if not ok: raise Refused(message)

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def power(f,x,n):
    for _ in range(n): x=f(x)
    return x

def binary():
    xs=list(product(range(2),repeat=6)); tick(len(xs))
    complement=lambda x:tuple(1-a for a in x)
    reverse=lambda x:x[::-1]
    nuclear=lambda x:(x[1],x[2],x[3],x[2],x[3],x[4])
    def orbits(fs):
        pending=set(xs); sizes=[]
        while pending:
            reached={next(iter(pending))}; todo=list(reached)
            while todo:
                x=todo.pop()
                for f in fs:
                    y=f(x)
                    if y not in reached: reached.add(y); todo.append(y)
            pending-=reached; sizes.append(len(reached))
        return len(sizes)
    counts=[orbits([complement]),orbits([reverse]),orbits([complement,reverse])]
    require(counts==[32,36,20],'binary orbit count')
    images=[len({power(nuclear,x,n) for x in xs}) for n in [1,2]]
    require(images==[16,4],'nuclear image sizes')
    require(all(power(nuclear,x,4)==power(nuclear,x,2) for x in xs),'nuclear fourth power')
    require(all(nuclear(f(x))==f(nuclear(x)) for x in xs for f in [complement,reverse]),'commutation')
    edges={(x,tuple(v^(i==j) for j,v in enumerate(x))) for x in xs for i in range(6)}
    masks={(x,tuple(a^b for a,b in zip(x,m))) for x in xs for m in xs}
    require(len(edges)==384 and len(masks)==4096,'binary transitions')
    return dict(states=len(xs),one_bit_edges=len(edges),state_mask_pairs=len(masks),orbit_counts=counts,nuclear_image_sizes=images)

def syllogisms():
    # atom numbers encode membership of S,M,P in bits 0,1,2.
    worlds=[]
    for mask in range(1,256):
        sets=[sum((1<<a) for a in range(8) if mask>>a&1 and a>>i&1) for i in range(3)]
        worlds.append(sets)
    def holds(letter,a,b):
        return {'A':a & ~b == 0,'E':a & b == 0,'I':a & b != 0,'O':a & ~b != 0}[letter]
    figures=[((1,2),(0,1)),((2,1),(0,1)),((1,2),(1,0)),((2,1),(1,0))]
    totals=[]
    for nonempty in [False,True]:
        counts=[]
        for major,minor in figures:
            valid=0
            for mood in product('AEIO',repeat=3):
                good=True
                for s in worlds:
                    tick()
                    if nonempty and not all(s): continue
                    if holds(mood[0],s[major[0]],s[major[1]]) and holds(mood[1],s[minor[0]],s[minor[1]]) and not holds(mood[2],s[0],s[2]):
                        good=False;break
                valid+=good
            counts.append(valid)
        totals.append(counts)
    require(totals==[[4,4,4,3],[6,6,6,6]],'categorical logic counts')
    return dict(nonempty_universe_masks=len(worlds),contracts=512,valid_by_figure=totals)

HEADS=list(product(range(3),repeat=4))
def addr(h): return HEADS[h-1]
def add(x,v): return tuple((a+b)%3 for a,b in zip(x,v))

def address():
    values=[sum(a*w for a,w in zip(x,[27,9,3,1])) for x in HEADS]
    require(values==list(range(81)),'head address bijection')
    result={}
    for b,n in [(3,4),(2,6)]:
        xs=list(product(range(b),repeat=n));tick(len(xs))
        hist=Counter(sum(a!=b for a,b in zip(x,xs[(i+1)%len(xs)])) for i,x in enumerate(xs))
        result[f'{b}^{n}']=[hist[i] for i in range(1,n+1)]
    require(result=={'3^4':[54,18,6,3],'2^6':[32,16,8,4,2,2]},'odometer profiles')
    zs=list(product(range(3),repeat=2));changes=[]
    for h in HEADS:
        for i in range(8): changes.append(sum(a!=b for a,b in zip(zs[i],zs[i+1])))
    tick(729)
    require(len(changes)==648 and changes.count(2)==162,'partial successor')
    return dict(heads=81,addresses=81*len(zs),successors=len(changes),boundaries=81,two_place_carries=changes.count(2),odometer=result)

def translations():
    orders=Counter()
    for v in HEADS:
        tick();x=(0,)*4;k=0
        while True:
            x=add(x,v);k+=1
            if x==(0,)*4:break
            require(k<=3,'unexpected translation order')
        orders[k]+=1
    require(dict(orders)=={1:1,3:80},'translation orders')
    for x in HEADS:
        for y in HEADS:
            if x!=y:
                tick();v=tuple((b-a)%3 for a,b in zip(x,y))
                require(y in [x,add(x,v),add(add(x,v),v)],'total pair relation')
    v=(1,2,1,1)
    require(add(addr(7),v)==addr(47) and add(addr(8),v)==addr(48),'declared common displacement')
    return dict(orders={str(k):v for k,v in orders.items()},nontrivial_shifts=80,cycles_per_nontrivial_shift=27,ordered_distinct_pairs=6480)

def carry_relation():
    orbit=[];x=0
    while x not in orbit:orbit.append(x);x=(x+40)%81;tick()
    edges=[(h,h+40) for h in range(1,42)]
    degrees=Counter(v for e in edges for v in e)
    differences={tuple((b-a)%3 for a,b in zip(addr(h),addr(k))) for h,k in edges}
    require(len(orbit)==81 and x==0,'cyclic index translation order')
    require(len(edges)==41 and degrees[41]==2 and max(degrees.values())==2,'not a matching')
    require(len(differences)>1,'carry translation differs from vector translation')
    return dict(cyclic_order=len(orbit),nonwrapping_edges=len(edges),shared_vertex=41,distinct_digit_displacements=len(differences))

def magic():
    grid=[[9*r+c+1 for c in range(9)] for r in range(9)]
    sums=[sum(row) for row in grid]+[sum(grid[r][c] for r in range(9)) for c in range(9)]+[sum(grid[r][r] for r in range(9)),sum(grid[r][8-r] for r in range(9))]
    require(sums.count(369)==4,'natural grid line sums')
    M=[[(-1 if i==j else 1)%3 for j in range(4)] for i in range(4)]
    def value(x): return 1+sum(3**i*(sum(a*b for a,b in zip(row,x))%3) for i,row in enumerate(M))
    require(sorted(value(x) for x in HEADS)==list(range(1,82)),'magic permutation')
    line_sums=[]
    for axis in range(4):
        for rest in product(range(3),repeat=3):
            tick();line=[]
            for t in range(3):
                x=list(rest);x.insert(axis,t);line.append(value(x))
            line_sums.append(sum(line))
    require(set(line_sums)=={123} and len(line_sums)==108,'coordinate line sums')
    diagonals=[sum(value(tuple(t*a%3 for a in d)) for t in range(3)) for d in product([1,2],repeat=4) if d[0]==1]
    require(sorted(diagonals)==[6,12,30,84,123,123,123,123],'central diagonals')
    return dict(natural_magic_lines=sums.count(369),coordinate_lines=len(line_sums),coordinate_sum=123,diagonal_sums=sorted(diagonals))

def observable(A,S):
    fibres=defaultdict(set)
    for i,x in enumerate(HEADS):fibres[tuple(x[j] for j in S)].add(i)
    return all(not(f&A) or f<=A for f in fibres.values())
def mu(A):
    for k in range(5):
        for S in combinations(range(4),k):
            tick()
            if observable(A,S):return k

def definability():
    sets={'prefix47':set(range(47)),'tail34':set(range(47,81)),'quarter':set(range(27)),'district_representatives':set(range(0,81,9)),'quarter_representatives':{0,27,54},'orbit7':{6,46,68}}
    mus={n:mu(A) for n,A in sets.items()}
    require(list(mus.values())==[4,4,1,2,3,4],'minimal coordinate counts')
    union=set();levels=[]
    for k in range(3):
        for S in combinations(range(4),k):
            fibres=defaultdict(int)
            for i,x in enumerate(HEADS):fibres[tuple(x[j] for j in S)]|=1<<i
            blocks=list(fibres.values())
            for mask in range(1<<len(blocks)):
                tick();union.add(sum(block for j,block in enumerate(blocks) if mask>>j&1))
        levels.append(len(union))
    hist=Counter(x.bit_count() for x in union)
    require(levels==[2,26,3014],'definability spectrum')
    require([hist[i] for i in range(0,82,9)]==[1,54,216,480,756,756,480,216,54,1],'size spectrum')
    witnesses={}
    for m in range(2,81):
        tick();w=next(((a,b) for a in range(1,48) for b in range(48,82) if a%m==b%m),None)
        require(w is not None,'nontrivial modulus unexpectedly separates cut');witnesses[str(m)]=w
    return dict(mu=mus,cumulative_counts=levels,size_counts={str(k):v for k,v in sorted(hist.items())},congruence_failures=len(witnesses),congruence_witnesses=witnesses)

def calendar_crt():
    for x in range(12):
        tick();require((4*(x%3)+9*(x%4))%12==x,'CRT roundtrip')
    require(4*4%12==4 and 9*9%12==9 and 4*9%12==0 and (4+9)%12==1,'orthogonal idempotents')
    fibres={tuple(x%m for m in [1,2,3,4]) for x in range(12)}
    require(len(fibres)==12,'redundant observations')
    require(len({tuple(x%m for m in [1,2,3,4]) for x in [9,21,33]})==1,'unbounded aliases')
    require((4*2+9)%12==5 and (4*0+9)%12==9,'source fidelity counterexample')
    original=[prod(y for j,y in enumerate([1,2,3,4]) if j!=i) for i in range(4)]
    before=[12,12,4,9];after=[12,24,4,9]
    rem=[33%m or m for m in [1,2,3,4]]
    require(sum(original)==50 and sum(before)==37 and sum(after)==49,'representative arithmetic')
    require(all((a-b)%12==0 for a,b in zip(after,before)),'coefficient equivalence')
    weighted=sum(a*b for a,b in zip(after,rem));require(weighted==57 and weighted%12==9,'positive remainders')
    for x,m in product(range(25),range(2,8)):
        tick();q,r=divmod(x,m);require(x==q*m+r and 0<=r<m,'source division witness')
    river=defaultdict(list)
    for x in range(1,10):river[x%5].append(x)
    require(sorted(map(len,river.values()))==[1,2,2,2,2],'residue partition')
    require(all(((x+5)%10+5)%10==x and (x+5)%10!=x for x in range(10)),'ten point involution')
    share=Q(2091,6800);rounded=(2*share.numerator*1000+share.denominator)//(2*share.denominator)
    require(rounded==308,'exact decimal rounding')
    return dict(calendar_days=[str(Q(729,2)),str(Q(731,2)),str(9*40)],crt_fibres=len(fibres),aliases=[9,21,33],source=5,altered_answer=9,coefficient_sums=[50,37,49],weighted_sum=weighted,rounding_thousandths=rounded)

def coverage():
    probability=sum(((-1)**j*Q(comb(2,j)*comb(729-9*j,9),comb(729,9)) for j in range(3)),Q())
    expected=81*(1-Q(comb(720,9),comb(729,9)))
    require(probability==Q(3133760077447169,308069738356701321),'block null')
    overlap=Q(35*35,comb(81,2));require(overlap==Q(245,648),'edge overlap mean')
    # Small exhaustive analogue independently checks inclusion-exclusion.
    observed=sum(bool(set(s)&{0,1}) and bool(set(s)&{2,3}) for s in combinations(range(6),3))
    tick(comb(6,3));formula=sum((-1)**j*comb(2,j)*comb(6-2*j,3) for j in range(3))
    require(observed==formula,'inclusion-exclusion control')
    return dict(two_head_probability=str(probability),expected_heads=str(expected),expected_edge_overlap=str(overlap),zero_overlap_lower_bound=str(1-overlap),small_null_count=observed)

def observation():
    p=[0,0,1,1];q=[0,0,0,0]
    def decidable(labels,reading):return all(labels[i]==labels[j] for i in range(4) for j in range(4) if reading[i]==reading[j])
    hypotheses=list(product(range(2),repeat=4));tick(len(hypotheses))
    P={h for h in hypotheses if decidable(h,p)};Qset={h for h in hypotheses if decidable(h,q)}
    require(len(P)==4 and len(Qset)==2 and Qset<P,'coarsening loses distinctions')
    h1={h for h in hypotheses if h[0]==0};h2={h for h in h1 if h[2]==1};bad={h for h in h1 if h[0]==1}
    require(len(h1)==8 and len(h2)==4 and not bad,'version space')
    source_a=['row_a','row_b'];source_b=source_a+['row_c'];index=source_a.copy()
    require(set(source_a)-set(index)==set() and set(source_b)-set(index)=={'row_c'},'missing row cannot be detected from same index')
    return dict(fine_decidable_questions=len(P),coarse_decidable_questions=len(Qset),hypothesis_counts=[16,len(h1),len(h2),len(bad)],same_index_distinct_sources=True)

def segmentation():
    text='abcd';segmentations=[]
    for mask in range(8):
        tick();cuts=[0]+[i for i in range(1,4) if mask>>(i-1)&1]+[4]
        segmentations.append([text[a:b] for a,b in zip(cuts,cuts[1:])])
    require(len({tuple(s) for s in segmentations})==8 and {''.join(s) for s in segmentations}=={text},'segmentation erasure')
    require({len(s) for s in segmentations}=={1,2,3,4},'count depends on cuts')
    def jaccard(a,b):return Q(len(set(a)&set(b)),len(set(a)|set(b)))
    require(jaccard('ab','baaa')==1 and 'ab'!='baaa','Jaccard order and multiplicity loss')
    def align(a,b):
        dp=[[0]*(len(b)+1) for _ in range(len(a)+1)]
        for i in range(len(a)+1):dp[i][0]=-i
        for j in range(len(b)+1):dp[0][j]=-j
        for i in range(1,len(a)+1):
            for j in range(1,len(b)+1):
                dp[i][j]=max(dp[i-1][j]-1,dp[i][j-1]-1,dp[i-1][j-1]+(2 if a[i-1]==b[j-1] else -1))
        return dp[-1][-1]
    def brute(a,b):
        tick()
        if not a:return -len(b)
        if not b:return -len(a)
        return max(brute(a[1:],b)-1,brute(a,b[1:])-1,brute(a[1:],b[1:])+(2 if a[0]==b[0] else -1))
    strings=['','a','b','ab','ba','aaa']
    for a,b in product(strings,repeat=2):require(align(a,b)==brute(a,b),'alignment DP against all paths')
    require(24+1+5==30 and 1<=25<=30 and Q(1+30,2)!=25,'internal unit arithmetic')
    return dict(segmentations=len(segmentations),same_erased_string=True,unit_counts=[1,2,3,4],jaccard_counterexample=['ab','baaa'],alignment_pairs=len(strings)**2,verse25_is_midpoint=False)

SECTIONS={f.__name__:f for f in [binary,syllogisms,address,translations,carry_relation,magic,definability,calendar_crt,coverage,observation,segmentation]}
def run(root, expected=None):
    contract=json.loads((root/'contract.json').read_text())
    require(contract['sections']==list(SECTIONS),'section contract mismatch')
    require(contract['limits']['maximum_counted_nodes']==LIMIT,'node limit mismatch')
    files=['README.md','claims.json','sources.json','corrections.json','contract.json','proofs.md','check.py']
    bindings={n:digest(root/n) for n in files}
    if expected is not None:require(bindings==expected['bindings'],'received bytes differ from source-run evidence')
    claims=json.loads((root/'claims.json').read_text())['claims']
    ids={c['id'] for c in claims};require(len(ids)==len(claims)==72,'claim inventory')
    sources={s['id'] for s in json.loads((root/'sources.json').read_text())['sources']}
    for c in claims:
        require(set(c['sources'])<=sources,'unresolved source key')
        require(c['fresh_check'] is None or c['fresh_check'] in SECTIONS,'unknown check key')
    for c in json.loads((root/'corrections.json').read_text())['corrections']:require(set(c['sources'])<=sources,'unresolved correction source')
    results={name:f() for name,f in SECTIONS.items()}
    return {'schema':'adva.research.yi-taixuan-weishi-evidence.v1','status':'ExternalExactPass','bindings':bindings,'sections':results,'counted_nodes':NODES,'checked_claims':[c['id'] for c in claims if c['fresh_check']],'existing_evidence_claims':[c['id'] for c in claims if not c['fresh_check']],'native_admission':'NotGranted','corpus_replay':'NotRun','limits_installed':['RLIMIT_CPU','RLIMIT_AS','RLIMIT_FSIZE','wall_alarm'],'automatic_retries':0}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--expect',type=Path);args=parser.parse_args()
    if args.output.exists():print('Rejected: output already exists',file=sys.stderr);return 2
    resource.setrlimit(resource.RLIMIT_CPU,(25,25));resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456));resource.setrlimit(resource.RLIMIT_FSIZE,(1048576,1048576))
    def timeout(*_):raise Limit('wall deadline exhausted')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(30)
    try:
        expected=json.loads(args.expect.read_text()) if args.expect else None
        result=run(Path(__file__).resolve().parent,expected)
        if expected is not None:require(json.loads(json.dumps(result))==expected,'post-arrival result differs from retained source result')
        code=0
    except (Limit,MemoryError,FileNotFoundError) as e:result={'status':'Unknown','reason':str(e),'counted_nodes':NODES};code=3
    except (Refused,ValueError,KeyError) as e:result={'status':'Rejected','reason':str(e),'counted_nodes':NODES};code=2
    with args.output.open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'status':result['status'],'counted_nodes':NODES}));return code
if __name__=='__main__':sys.exit(main())
