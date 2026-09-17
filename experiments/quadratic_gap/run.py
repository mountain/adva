#!/usr/bin/env python3
"""Original bounded quadratic producer/supervisor, Unknown v0.3.

ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy; not his review.
The receiving implementation and legacy experiments are not imported.
"""
import argparse
import copy
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent
PROFILE='adva.research.quadratic-gap.v0'
PRODUCER_WORK=0
POINT_WORK=0


def tick(n=1):
    global PRODUCER_WORK
    PRODUCER_WORK+=n
    if PRODUCER_WORK>10000:raise TimeoutError('producer-work')


def rat(x):x=F(x);return [x.numerator,x.denominator]
def vec(x):return [rat(v) for v in x]
def vals(x):return [F(*v) for v in x]
def put(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n')


def request(name,H,c,d,box,tol=F(1,64)):
    return {'question':'quadratic-'+name,'axes':['x','y'][:len(c)],'H':[vec(r) for r in H],
            'c':vec(c),'d':rat(d),'box':[vec(v) for v in box],'tolerance':rat(tol),
            'history':[name+':declared'],'scope':'all-rational-points-in-box'}


def polynomial(e):
    n=len(e['axes']);p={tuple([0]*n):F(*e['d'])}
    for i in range(n):
        power=[0]*n;power[i]=1;p[tuple(power)]=F(*e['c'][i]);tick()
        for j in range(n):
            power=[0]*n;power[i]+=1;power[j]+=1;key=tuple(power)
            p[key]=p.get(key,F(0))+F(*e['H'][i][j])/2;tick()
    return p


def evalpoly(p,x):
    out=F(0)
    for powers,coefficient in p.items():
        term=coefficient
        for a,k in zip(x,powers):term*=a**k;tick()
        out+=term;tick()
    return out


def derivative(p,i):
    d={}
    for powers,coefficient in p.items():
        tick()
        if powers[i]:
            out=list(powers);out[i]-=1;d[tuple(out)]=coefficient*powers[i]
    return d


def produce(e,x,z):
    x=list(map(F,x));p=polynomial(e);upper=evalpoly(p,x)
    out={'profile':PROFILE,'request':copy.deepcopy(e),'point':vec(x),'upper':rat(upper),
         'lower':None,'claim':{'kind':'UnknownLowerBound','gap':None}}
    if z is None:return out
    z=list(map(F,z));g=[evalpoly(derivative(p,i),z) for i in range(len(x))]
    corners=[];lower=evalpoly(p,z)
    for a,h,b in zip(z,g,e['box']):
        l,u=vals(b);left=h*(l-a);right=h*(u-a);tick(2)
        corners.append(l if left<=right else u);lower+=min(left,right)
    gap=upper-lower
    kind='ExactOptimal' if gap==0 else 'EpsilonOptimal' if gap<=F(*e['tolerance']) else 'VerifiedGap'
    out['lower']={'anchor':vec(z),'gradient':vec(g),'corner':vec(corners),'value':rat(lower)}
    out['claim']={'kind':kind,'gap':rat(gap)}
    return out


def direct(e,x):
    global POINT_WORK
    n=len(x);out=F(*e['d'])
    for i in range(n):
        out+=F(*e['c'][i])*x[i];POINT_WORK+=1
        for j in range(n):out+=x[i]*F(*e['H'][i][j])*x[j]/2;POINT_WORK+=1
    if POINT_WORK>10000:raise TimeoutError('point-work')
    return out


def limits():
    resource.setrlimit(resource.RLIMIT_CPU,(3,3))
    resource.setrlimit(resource.RLIMIT_AS,(134217728,134217728))
    resource.setrlimit(resource.RLIMIT_FSIZE,(262144,262144))


class Campaign:
    def __init__(self,out):
        self.out=out;self.started=time.perf_counter();self.runs=[];self.assertions=0;self.work=0
        self.phases={k:0. for k in ('construction_seconds','receiving_seconds','serialization_seconds','point_observation_seconds')}
    def check(self,condition,message):
        self.assertions+=1
        if not condition:raise AssertionError(message)
    def save(self,p,x):
        t=time.perf_counter();put(p,x);self.phases['serialization_seconds']+=time.perf_counter()-t
    def build(self,e,x,z):
        t=time.perf_counter();out=produce(e,x,z);self.phases['construction_seconds']+=time.perf_counter()-t;return out
    def call(self,name,e,c,kind,feasible,lower):
        self.check(len(self.runs)<48,'process-budget');d=self.out/name;d.mkdir(parents=True)
        self.save(d/'expected.json',e);self.save(d/'candidate.json',c)
        self.check(all((d/n).stat().st_size<=32768 for n in ('expected.json','candidate.json')),'wire-budget')
        args=[sys.executable,'-B','-S',str(ROOT/'receive.py'),'--expected',str(d/'expected.json'),'--candidate',str(d/'candidate.json')]
        self.save(d/'command.json',{'argv':args});row={'case':name};self.runs.append(row)
        remaining=30-(time.perf_counter()-self.started)
        if remaining<=0:raise TimeoutError('campaign-wall')
        t=time.perf_counter()
        with (d/'stdout.json').open('wb') as out,(d/'stderr.txt').open('wb') as err:
            p=subprocess.Popen(args,stdout=out,stderr=err,preexec_fn=limits)
            try:p.wait(timeout=min(3,remaining))
            finally:
                if p.poll() is None:p.kill();p.wait(timeout=.2)
        elapsed=time.perf_counter()-t;self.phases['receiving_seconds']+=elapsed
        row.update(returncode=p.returncode,wall_seconds=elapsed)
        self.check(p.returncode==0,(name,p.returncode,(d/'stderr.txt').read_text()))
        answer=json.loads((d/'stdout.json').read_text());self.work+=answer['work_units']
        row.update(outcome=answer['outcome'],reason=answer['reason'],work_units=answer['work_units'])
        self.check(answer['outcome']==kind,(name,answer))
        self.check(answer['expected_request']==(None if name=='context/float-number' else e),'request-retained')
        self.check(all(answer[k] is False for k in ('native_authority','close_authorized','free_authorized')),'no-native-authority')
        self.check(answer['verified_feasible']==({'point':c['point'],'upper':c['upper']} if feasible else None),'feasible-retention')
        self.check(answer['verified_lower']==(c['lower'] if lower else None),'lower-retention')
        accepted=kind in ('ExactOptimal','EpsilonOptimal','VerifiedGap')
        wanted={'kind':kind,'lower':c['lower']['value'],'upper':c['upper'],'gap':c['claim']['gap']} if accepted else None
        self.check(answer['accepted_result']==wanted,'accepted-scope')
        self.check(0<=answer['work_units']<=10000 and self.work+PRODUCER_WORK+POINT_WORK<=100000,'work-budget')
        if accepted:
            self.check(F(*wanted['gap'])==F(*wanted['upper'])-F(*wanted['lower'])>=0,'gap-identity')
        if name in ('valid/tiny-positive-gap','valid/epsilon-boundary'):
            self.check(F(*wanted['gap'])>0 and kind!='ExactOptimal','epsilon-not-exact')
        return answer
    def samples(self,name,e,c):
        t=time.perf_counter();rows=[]
        choices=[]
        for raw in e['box']:
            l,u=vals(raw);choices.append(sorted({l,(l+u)/2,u}))
        for point in itertools.product(*choices):
            value=direct(e,point);rows.append({'point':vec(point),'value':rat(value)})
            if c['lower'] is not None:self.check(F(*c['lower']['value'])<=value,'lower-sample')
        self.check(direct(e,vals(c['point']))==F(*c['upper']),'candidate-direct-evaluation')
        self.phases['point_observation_seconds']+=time.perf_counter()-t
        self.save(self.out/'valid'/name/'point-observations.json',rows)


def execute(camp):
    H=[[2,1],[1,2]];box=[[0,1],[0,1]]
    interior=request('interior',H,[-1,-1],0,box)
    specs=[
        ('interior',interior,[F(1,3)]*2,[F(1,3)]*2,'ExactOptimal'),
        ('nonoptimal',request('nonoptimal',H,[-1,-1],0,box),[0,0],[F(1,3)]*2,'VerifiedGap'),
        ('weak-bound',request('weak-bound',H,[-1,-1],0,box),[F(1,3)]*2,[0,0],'VerifiedGap'),
        ('active-boundary',request('active-boundary',H,[1,-2],0,box),[0,1],[0,1],'ExactOptimal'),
        ('rank-one',request('rank-one',[[2,2],[2,2]],[-2,-2],1,box),[1,0],[F(1,2)]*2,'ExactOptimal'),
        ('rank-one-tie',request('rank-one-tie',[[2,2],[2,2]],[-2,-2],1,box),[0,1],[F(1,2)]*2,'ExactOptimal'),
        ('constant',request('constant',[[0,0],[0,0]],[0,0],3,box),[0,1],[1,1],'ExactOptimal'),
        ('reuse-negative',request('reuse-negative',[[2]],[1],F(1,4),[[-1,0]],F(1,32)),[F(-3,4)],[F(-1,2)],'VerifiedGap'),
        ('tiny-positive-gap',request('tiny-positive-gap',[[2]],[0],0,[[0,1]]),[F(1,64)],[0],'EpsilonOptimal'),
        ('epsilon-boundary',request('epsilon-boundary',[[2]],[0],0,[[0,1]],F(1,16)),[F(1,4)],[0],'EpsilonOptimal'),
        ('signed-linear',request('signed-linear',[[0]],[-2],0,[[-1,2]]),[2],[0],'ExactOptimal'),
        ('singleton',request('singleton',[[2]],[0],0,[[1,1]],0),[1],[0],'VerifiedGap'),
        ('outside-anchor',request('outside-anchor',[[2]],[0],0,[[0,1]]),[0],[-1],'VerifiedGap'),
        ('no-lower',request('no-lower',H,[-1,-1],0,box),[0,0],None,'UnknownLowerBound'),
        ('constant-no-lower',request('constant-no-lower',[[0]],[0],3,[[0,1]]),[0],None,'UnknownLowerBound')]
    saved={}
    for name,e,x,z,kind in specs:
        r=camp.build(e,x,z);saved[name]=(e,r)
        camp.call('valid/'+name,e,r,kind,True,z is not None);camp.samples(name,e,r)
    for name in ('interior','active-boundary','rank-one','rank-one-tie','constant'):
        camp.check(saved[name][1]['claim']['gap']==[0,1],'exact-zero-gap')
    camp.check(saved['weak-bound'][1]['point']==saved['interior'][1]['point'],'optimal-point-positive-gap-control')
    camp.check(saved['weak-bound'][1]['claim']['gap']==[5,3],'weak-bound-gap')
    camp.check(saved['active-boundary'][1]['lower']['gradient']==[[2,1],[0,1]],'nonstationary-boundary-optimum')
    camp.check(saved['rank-one'][1]['point']!=saved['rank-one-tie'][1]['point'],'multiple-optimal-points')
    base,receipt=saved['interior'];bad=[]
    def alter(name,source,path,value,feasible=False,lower=False):
        e,r=saved[source];r=copy.deepcopy(r);at=r
        for k in path[:-1]:at=at[k]
        at[path[-1]]=value;bad.append((name,e,r,feasible,lower))
    alter('outside-candidate','interior',['point'],vec([2,0]))
    alter('upper-without-half','interior',['upper'],[0,1])
    alter('wrong-gradient','interior',['lower','gradient'],vec([1,0]),True)
    alter('wrong-corner','active-boundary',['lower','corner'],vec([1,0]),True)
    alter('wrong-lower','interior',['lower','value'],[0,1],True)
    alter('wrong-gap','nonoptimal',['claim','gap'],[0,1],True,True)
    alter('false-exact','tiny-positive-gap',['claim','kind'],'ExactOptimal',True,True)
    alter('false-epsilon','nonoptimal',['claim','kind'],'EpsilonOptimal',True,True)
    alter('tied-corner-policy','constant',['lower','corner'],vec([1,1]),True)
    for name,path,value in [
        ('changed-H',['H'],[vec([2,0]),vec([0,2])]),
        ('changed-c',['c'],vec([0,-1])),('changed-constant',['d'],[1,1]),
        ('changed-box',['box'],[vec([0,2]),vec([0,1])]),('changed-axes',['axes'],['y','x']),
        ('changed-tolerance',['tolerance'],[1,2]),('changed-history',['history'],['rebound']),
        ('changed-question',['question'],'another-problem')]:
        alter(name,'interior',['request']+path,value)
    alter('wrong-profile','interior',['profile'],'adva.research.quadratic-gap.v1')
    e,r=saved['interior'];r=copy.deepcopy(r);r['free_authorized']=True;bad.append(('extra-authority',e,r,False,False))
    alter('changed-anchor','interior',['lower','anchor'],vec([0,0]),True)
    for index,(name,e,r,f,l) in enumerate(bad):
        if name=='changed-constant':
            shifted=copy.deepcopy(e);shifted['d']=[1,1]
            fresh=camp.build(shifted,vals(receipt['point']),vals(receipt['lower']['anchor']))
            camp.check(fresh['claim']['gap']==receipt['claim']['gap'],'shift-retains-gap')
            camp.check(F(*fresh['upper'])-F(*receipt['upper'])==1,'shifted-upper')
            camp.check(F(*fresh['lower']['value'])-F(*receipt['lower']['value'])==1,'shifted-lower')
            bad[index]=(name,e,fresh,f,l)
    camp.check(len(bad)==20,'declared-evidence-controls')
    for name,e,r,f,l in bad:camp.call('evidence/'+name,e,r,'InvalidEvidence',f,l)
    contexts=[]
    def context(name,key,value):
        e=copy.deepcopy(base);e[key]=value;contexts.append((name,e))
    context('dimension-three','axes',['x','y','z'])
    context('duplicate-axes','axes',['x','x'])
    context('matrix-shape','H',[vec([2,1])])
    context('vector-shape','c',vec([-1]))
    context('nonsymmetric','H',[vec([2,1]),vec([0,2])])
    context('positive-determinant-negative-diagonals','H',[vec([-1,0]),vec([0,-1])])
    context('nonnegative-diagonals-indefinite','H',[vec([0,1]),vec([1,0])])
    context('reversed-box','box',[vec([1,0]),vec([0,1])])
    context('negative-tolerance','tolerance',[-1,1])
    context('zero-denominator','d',[1,0])
    context('float-number','d',[0.0,1])
    context('boolean-number','d',[False,1])
    context('history-capacity','history',['a','b','c','d','e'])
    for name,e in contexts:camp.call('context/'+name,e,receipt,'InvalidContext',False,False)
    camp.check(len(camp.runs)==48,'exact-declared-process-count')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);a=parser.parse_args()
    a.output.mkdir(parents=True,exist_ok=False);camp=Campaign(a.output);failure=None
    camp.save(a.output/'contract.json',json.loads((ROOT/'contract.json').read_text()))
    try:execute(camp)
    except Exception as exc:failure={'type':type(exc).__name__,'message':str(exc)}
    elapsed=time.perf_counter()-camp.started
    size=sum(p.stat().st_size for p in a.output.rglob('*') if p.is_file())
    if elapsed>30 or size>2097152:failure=failure or {'type':'BudgetExceeded','message':'campaign wall/evidence bound'}
    result={'profile':PROFILE,'success':failure is None,'failure':failure,'receiver_calls':len(camp.runs),
            'assertions':camp.assertions,'receiver_work':camp.work,'producer_work':PRODUCER_WORK,'point_work':POINT_WORK,
            'search_candidates':0,'wall_seconds':elapsed,'phases':camp.phases,'cases':camp.runs,
            'child_maxrss_kib':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            'supervisor_maxrss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'evidence_bytes_before_summary':size,'python':sys.version,
            'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ('receive.py','run.py','contract.json')},
            'limits':'RSS is Linux process high water, not aggregate. Reading, review, network, final archive/report costs are not in campaign time.'}
    put(a.output/'execution.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('cases','source_sha256')}))
    return 0 if failure is None else 1


if __name__=='__main__':raise SystemExit(main())
