#!/usr/bin/env python3
"""Original bounded rational solver producer, Unknown v0.3.

ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy; not his review.
Gaussian elimination produces witnesses; the separate receiver checks equations.
"""
import argparse
import copy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent
PROFILE='adva.research.linear-system.v0'
PRODUCER_WORK=0


def tick(n=1):
    global PRODUCER_WORK
    PRODUCER_WORK+=n
    if PRODUCER_WORK>10000:raise TimeoutError('producer-work-limit')


def rat(q):q=F(q);return [q.numerator,q.denominator]
def vector(v):return [F(*x) for x in v]
def matrix(m):return [vector(row) for row in m]
def wire(m):return [[rat(x) for x in row] for row in m]
def mv(a,v):return [sum(x*y for x,y in zip(row,v)) for row in a]
def mm(a,b):return [[sum(a[i][k]*b[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
def transpose(m):return list(map(list,zip(*m)))
def put(path,obj):path.write_text(json.dumps(obj,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n')


def fixture(name,a,b,bases=None):
    identity=[[1,0],[0,1]];p,q=bases or (identity,identity)
    return {'question':'linear-'+name,
            'domain':{'id':name+':domain','dimension':2,'basis':wire(transpose(p))},
            'codomain':{'id':name+':codomain','dimension':2,'basis':wire(transpose(q))},
            'operator':{'domain':name+':domain','codomain':name+':codomain','action':'left-on-column','matrix':wire(a)},
            'rhs':{'space':name+':codomain','coordinates':list(map(rat,b))},
            'interpretation':'all-solutions-over-Q','history':[name+':declared']}


def produce(e):
    a=matrix(e['operator']['matrix']);b=vector(e['rhs']['coordinates'])
    rows=[a[i]+[b[i]] for i in range(2)];transform=[[F(i==j) for j in range(2)] for i in range(2)]
    pivots=[]
    for col in range(2):
        r=len(pivots);pivot=next((i for i in range(r,2) if rows[i][col]!=0),None);tick(2)
        if pivot is None:continue
        rows[r],rows[pivot]=rows[pivot],rows[r];transform[r],transform[pivot]=transform[pivot],transform[r]
        scale=rows[r][col];rows[r]=[x/scale for x in rows[r]];transform[r]=[x/scale for x in transform[r]];tick(5)
        for i in range(2):
            if i==r:continue
            factor=rows[i][col];rows[i]=[x-factor*y for x,y in zip(rows[i],rows[r])]
            transform[i]=[x-factor*y for x,y in zip(transform[i],transform[r])];tick(10)
        pivots.append(col)
    bad=next((i for i in range(2) if rows[i][:2]==[0,0] and rows[i][2]!=0),None)
    if bad is not None:claim={'kind':'inconsistent','left_witness':[rat(x/rows[bad][2]) for x in transform[bad]]};tick(2)
    elif len(pivots)==2:claim={'kind':'unique','solution':[rat(rows[i][2]) for i in range(2)],'inverse':wire(transform)}
    else:
        x=[F(0),F(0)]
        for i,j in enumerate(pivots):x[j]=rows[i][2]
        basis=[]
        for free in sorted(set(range(2))-set(pivots)):
            v=[F(0),F(0)];v[free]=F(1)
            for i,j in enumerate(pivots):v[j]=-rows[i][free]
            basis.append(list(map(rat,v)))
        claim={'kind':'affine-family','particular':list(map(rat,x)),'kernel_basis':basis}
    return {'profile':PROFILE,'request':copy.deepcopy(e),'claim':claim}


def limits():
    resource.setrlimit(resource.RLIMIT_CPU,(3,3))
    resource.setrlimit(resource.RLIMIT_AS,(134217728,134217728))
    resource.setrlimit(resource.RLIMIT_FSIZE,(262144,262144))


class Campaign:
    def __init__(self,out):
        self.out=out;self.started=time.perf_counter();self.runs=[];self.assertions=0;self.work=0
        self.phases={'construction_seconds':0.,'receiving_seconds':0.,'serialization_seconds':0.,'independent_observation_seconds':0.}
    def check(self,c,message):
        self.assertions+=1
        if not c:raise AssertionError(message)
    def save(self,path,obj):
        t=time.perf_counter();put(path,obj);self.phases['serialization_seconds']+=time.perf_counter()-t
    def build(self,e):
        t=time.perf_counter();r=produce(e);self.phases['construction_seconds']+=time.perf_counter()-t;return r
    def call(self,name,e,r,wanted):
        self.check(len(self.runs)<44,'process-cap');d=self.out/name;d.mkdir(parents=True)
        self.save(d/'expected.json',e);self.save(d/'candidate.json',r)
        self.check(all((d/n).stat().st_size<=32768 for n in ('expected.json','candidate.json')),'wire-limit')
        args=[sys.executable,'-B','-S',str(ROOT/'receive.py'),'--expected',str(d/'expected.json'),'--candidate',str(d/'candidate.json')]
        self.save(d/'command.json',{'argv':args});row={'case':name};self.runs.append(row)
        remaining=30-(time.perf_counter()-self.started)
        if remaining<=0:raise TimeoutError('campaign-wall-limit')
        t=time.perf_counter()
        with (d/'stdout.json').open('wb') as out,(d/'stderr.txt').open('wb') as err:
            p=subprocess.Popen(args,stdout=out,stderr=err,preexec_fn=limits)
            try:p.wait(timeout=min(3,remaining))
            finally:
                if p.poll() is None:p.kill();p.wait(timeout=.2)
        elapsed=time.perf_counter()-t;self.phases['receiving_seconds']+=elapsed;row.update(returncode=p.returncode,wall_seconds=elapsed)
        self.check(p.returncode==0,(name,p.returncode,(d/'stderr.txt').read_text()))
        result=json.loads((d/'stdout.json').read_text());row.update(outcome=result['outcome'],reason=result['reason'],work_units=result['work_units']);self.work+=result['work_units']
        self.check(result['outcome']==wanted,(name,result));self.check(result['expected_request']==(None if name=='context/float-entry' else e),'expected-request-or-raw-parse-failure-preserved')
        self.check(all(result[k] is False for k in ('native_authority','close_authorized','free_authorized')),'no-native-authority')
        self.check(0<=result['work_units']<=10000,'receiver-work-limit');self.check(self.work+PRODUCER_WORK<=100000,'aggregate-work-limit')
        accepted=wanted in ('UniqueSolution','InconsistentSystem','AffineSolutionFamily')
        self.check(result['accepted_claim']==r['claim'] if accepted else result['accepted_claim'] is None,'accepted-claim-scope')
        self.check(bool(result['semantic_delta'])==accepted,'semantic-delta-scope')
        if accepted:self.observe(name,e,r['claim'])
        return result
    def observe(self,name,e,claim):
        t=time.perf_counter();a=matrix(e['operator']['matrix']);b=vector(e['rhs']['coordinates']);kind=claim['kind'];notes={}
        # Receiver uses certificate equations; independent supervisor evaluates actual
        # supplied points and ambient-coordinate reconstructions on selected cases.
        if kind=='inconsistent':
            y=vector(claim['left_witness']);left=mv(transpose(a),y);contradiction=sum(x*z for x,z in zip(y,b))
            self.check(left==[0,0] and contradiction==1,'independent-left-witness');notes={'left':list(map(rat,left)),'contradiction':rat(contradiction)}
        else:
            x=vector(claim['solution'] if kind=='unique' else claim['particular']);basis=[] if kind=='unique' else [vector(v) for v in claim['kernel_basis']]
            parameters=[F(0),F(1,2),F(-2)]
            points=[x] if not basis else [[x[i]+sum((t if j==0 else -t)*v[i] for j,v in enumerate(basis)) for i in range(2)] for t in parameters]
            for point in points:self.check(mv(a,point)==b,'independent-family-point')
            notes={'sampled_points':list(map(lambda v:list(map(rat,v)),points)),'scope':'Samples check examples; complete-family justification is the receiver rank/basis argument.'}
        self.phases['independent_observation_seconds']+=time.perf_counter()-t;self.save(self.out/name/'independent-observation.json',notes)


def main(out):
    out.mkdir(parents=True,exist_ok=False);c=Campaign(out);failure=None
    def deadline(*_):raise TimeoutError('campaign-wall-limit')
    signal.signal(signal.SIGALRM,deadline);signal.setitimer(signal.ITIMER_REAL,30)
    try:
        c.save(out/'contract.json',json.loads((ROOT/'contract.json').read_text()))
        p=[[1,1],[0,1]];pi=[[1,-1],[0,1]];q=[[0,1],[1,0]]
        data={'unique':([[2,1],[3,2]],[4,7]),'family':([[1,2],[3,6]],[3,9]),'inconsistent':([[1,2],[3,6]],[3,10])}
        cases={};receipts={};wanted={'unique':'UniqueSolution','family':'AffineSolutionFamily','inconsistent':'InconsistentSystem'}
        for name,(a,b) in data.items():
            e=fixture(name,a,b);r=c.build(e);cases[name]=e;receipts[name]=r;c.call('primary/'+name,e,r,wanted[name])
            ae=mm(q,mm(a,p));be=mv(q,b);re=fixture('复用-'+name,ae,be,(p,q));rr=c.build(re);cases['reuse-'+name]=re;receipts['reuse-'+name]=rr;c.call('reuse/'+name,re,rr,wanted[name])
            t=time.perf_counter();original=r['claim'];changed=rr['claim']
            if name=='unique':
                c.check(mv(p,vector(changed['solution']))==vector(original['solution']),'actual-domain-coordinate-transport')
                c.check(matrix(changed['inverse'])==mm(pi,mm(matrix(original['inverse']),q)),'two-space-inverse-transport')
            elif name=='inconsistent':c.check(vector(changed['left_witness'])==mv(transpose(q),vector(original['left_witness'])),'codomain-covector-transport')
            else:
                xp=mv(p,vector(changed['particular']));vp=mv(p,vector(changed['kernel_basis'][0]))
                c.check(mv(a,xp)==b and mv(a,vp)==[0,0],'family-ambient-transport')
            c.phases['independent_observation_seconds']+=time.perf_counter()-t
        for name,a,b in [('zero-family',[[0,0],[0,0]],[0,0]),('zero-inconsistent',[[0,0],[0,0]],[0,1]),('rational-unique',[[F(1,2),F(1,3)],[F(2,3),F(-1,2)]],[0,F(17,6)])]:
            e=fixture(name,a,b);r=c.build(e);cases[name]=e;receipts[name]=r;c.call(name+'/valid',e,r,{'unique':'UniqueSolution','inconsistent':'InconsistentSystem','affine-family':'AffineSolutionFamily'}[r['claim']['kind']])
        alt=copy.deepcopy(receipts['family']);alt['claim']['particular']=[[1,1],[1,1]];alt['claim']['kernel_basis']=[[[2,1],[-1,1]]]
        c.call('family/alternate-parameterization',cases['family'],alt,'AffineSolutionFamily')
        for name in ('family','zero-family'):
            r=copy.deepcopy(receipts[name]);r['claim']['kernel_basis']=r['claim']['kernel_basis'][:-1]
            answer=c.call(name+'/partial-basis',cases[name],r,'UnknownCoverage')
            c.check(answer['diagnostics']['missing_kernel_directions']==1,'explicit-missing-direction')
            c.check(answer['diagnostics']['particular_residual']==[[0,1],[0,1]],'partial-particular-retained')
        controls=[]
        def mutation(label,key,edit):
            r=copy.deepcopy(receipts[key]);edit(r);controls.append((label,cases[key],r))
        mutation('wrong-solution','unique',lambda r:r['claim']['solution'].__setitem__(0,[2,1]))
        mutation('wrong-inverse','unique',lambda r:r['claim']['inverse'][0].__setitem__(0,[1,1]))
        mutation('missing-inverse','unique',lambda r:r['claim'].pop('inverse'))
        mutation('singular-as-unique','family',lambda r:r.__setitem__('claim',{'kind':'unique','solution':r['claim']['particular'],'inverse':wire([[1,0],[0,1]])}))
        mutation('wrong-covector-direction','reuse-inconsistent',lambda r:r['claim'].__setitem__('left_witness',list(map(rat,mv(pi,vector(receipts['inconsistent']['claim']['left_witness']))))))
        mutation('zero-inconsistency-witness','inconsistent',lambda r:r['claim'].__setitem__('left_witness',[[0,1],[0,1]]))
        mutation('wrong-particular','family',lambda r:r['claim'].__setitem__('particular',[[0,1],[0,1]]))
        mutation('not-a-kernel-vector','family',lambda r:r['claim'].__setitem__('kernel_basis',[[[1,1],[0,1]]]))
        mutation('zero-kernel-vector','family',lambda r:r['claim'].__setitem__('kernel_basis',[[[0,1],[0,1]]]))
        mutation('duplicate-kernel-vector','family',lambda r:r['claim']['kernel_basis'].append(copy.deepcopy(r['claim']['kernel_basis'][0])))
        mutation('dependent-zero-matrix-basis','zero-family',lambda r:r['claim'].__setitem__('kernel_basis',wire([[1,0],[2,0]])))
        mutation('nonsingular-as-family','unique',lambda r:r.__setitem__('claim',{'kind':'affine-family','particular':r['claim']['solution'],'kernel_basis':[]}))
        mutation('changed-question','unique',lambda r:r['request'].__setitem__('question','another-problem'))
        mutation('erased-history','family',lambda r:r['request'].__setitem__('history',[]))
        mutation('changed-domain-basis','unique',lambda r:r['request']['domain'].__setitem__('basis',wire(transpose(p))))
        mutation('changed-codomain-basis','inconsistent',lambda r:r['request']['codomain'].__setitem__('basis',wire(transpose(q))))
        mutation('transposed-operator','unique',lambda r:r['request']['operator'].__setitem__('matrix',list(map(list,zip(*r['request']['operator']['matrix'])))))
        mutation('changed-rhs','unique',lambda r:r['request']['rhs']['coordinates'].__setitem__(0,[5,1]))
        mutation('noncanonical-rational','unique',lambda r:r['claim']['solution'].__setitem__(0,[2,2]))
        mutation('wrong-profile','unique',lambda r:r.__setitem__('profile','adva.external.operator-lift-receipt.v0'))
        c.check(len(controls)==20,'declared-evidence-controls')
        for name,e,r in controls:c.call('evidence/'+name,e,r,'InvalidEvidence')
        bad=[]
        def context(label,edit):
            e=copy.deepcopy(cases['unique']);edit(e);bad.append((label,e))
        context('singular-domain-basis',lambda e:e['domain'].__setitem__('basis',wire([[1,0],[2,0]])))
        context('singular-codomain-basis',lambda e:e['codomain'].__setitem__('basis',wire([[0,0],[0,1]])))
        context('boolean-dimension',lambda e:e['domain'].__setitem__('dimension',True))
        context('wrong-dimension',lambda e:e['codomain'].__setitem__('dimension',3))
        context('operator-domain-mismatch',lambda e:e['operator'].__setitem__('domain','other-domain'))
        context('rhs-space-mismatch',lambda e:e['rhs'].__setitem__('space',e['domain']['id']))
        context('wrong-action',lambda e:e['operator'].__setitem__('action','right-on-row'))
        context('matrix-shape',lambda e:e['operator']['matrix'].pop())
        context('float-entry',lambda e:e['operator']['matrix'][0].__setitem__(0,[2.0,1]))
        context('zero-denominator',lambda e:e['operator']['matrix'][0].__setitem__(0,[2,0]))
        context('entry-cap',lambda e:e['rhs']['coordinates'].__setitem__(0,[65,1]))
        context('history-capacity',lambda e:e.__setitem__('history',['a','b','c','d','e']))
        for name,e in bad:c.call('context/'+name,e,receipts['unique'],'InvalidContext')
        c.check(len(c.runs)==44,'complete-declared-case-coverage')
    except Exception as exc:failure={'type':type(exc).__name__,'message':str(exc)}
    finally:signal.setitimer(signal.ITIMER_REAL,0)
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'run.py',ROOT/'receive.py',ROOT/'contract.json')}
    report={'profile':PROFILE,'status':'Passed' if failure is None else 'Failed','failure':failure,'calls':len(c.runs),'assertions':c.assertions,'receiver_work_units':c.work,'producer_work_units':PRODUCER_WORK,'search_candidates':0,'wall_seconds':time.perf_counter()-c.started,'phases':c.phases,'runs':c.runs,'source_sha256':hashes,'python_version':sys.version,'child_peak_rss_kib':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,'supervisor_peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'native_authority':False,'new_native_vocabulary':[],'cost_scope':'Instrumented phases omit some setup/copying; campaign wall includes bookkeeping. Final report/archive/research/review/network unmeasured separately; no speedup claim.'}
    put(out/'execution.json',report);print(json.dumps({k:v for k,v in report.items() if k not in ('runs','source_sha256')},sort_keys=True));return 0 if failure is None else 1


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);raise SystemExit(main(p.parse_args().output.resolve()))
