#!/usr/bin/env python3
"""Original finite dynamics producer and supervisor, Unknown v0.3.

ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy; not his review.
No receiving or legacy implementation is imported.
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
PROFILE='adva.research.markov-horizon.v0'
PRODUCER_WORK=0
CONTROL_WORK=0


def tick(n=1):
    global PRODUCER_WORK
    PRODUCER_WORK+=n
    if PRODUCER_WORK>10000:raise TimeoutError('producer-work')


def rat(v):v=F(v);return [v.numerator,v.denominator]
def vec(v):return [rat(x) for x in v]
def vals(v):return [F(*x) for x in v]
def put(p,v):p.write_text(json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n')


def step(p,K):
    tick(4);return [sum((p[i]*K[i][j] for i in range(2)),F(0)) for j in range(2)]


def tv(p,r):
    tick(2);return sum((abs(x-y) for x,y in zip(p,r)),F(0))/2


def request(name,a,b,initial,stationary,N=4,initial_error=0,errors=None,tolerance=F(1,64)):
    a,b=F(a),F(b)
    return {'question':'dynamics-'+name,'states':['left','right'],'direction':'row',
            'kernel':[vec([a,1-a]),vec([b,1-b])],'initial':vec(initial),'stationary':vec(stationary),
            'horizon':N,'initial_error':rat(initial_error),'step_errors':vec([0]*N if errors is None else errors),
            'tolerance':rat(tolerance),'history':[name+':declared'],'scope':'two-state-time-homogeneous-probability-dynamics'}


def classify(e,q,trace):
    bound=trace[-1]['stationary_bound'];length=len(trace)
    kind='UnknownCoverage' if length<e['horizon']+1 else 'CertifiedTolerance' if F(*bound)<=F(*e['tolerance']) else 'VerifiedHorizon'
    return {'kind':kind,'regime':'StrictContraction' if q<1 else 'Nonexpansive','steps':length-1,'final_bound':bound}


def produce(e,approx_initial=None,noise=None,keep=None):
    K=list(map(vals,e['kernel']));p=vals(e['initial']);stationary=vals(e['stationary'])
    h=p[:] if approx_initial is None else list(map(F,approx_initial));N=e['horizon']
    q=max(tv(r,s) for r in K for s in K);trace=[];B=F(*e['initial_error']);factor=F(1);d0=tv(p,stationary)
    for k in range(N+1):
        residual=None
        if k:
            predicted=step(h,K);delta=F(0) if noise is None else F(noise[k-1]);h=[predicted[0]+delta,predicted[1]-delta]
            p=step(p,K);residual=rat(tv(h,predicted));B=q*B+F(*e['step_errors'][k-1]);factor*=q;tick(3)
        trace.append({'index':k,'exact':vec(p),'approx':vec(h),'error_to_exact':rat(tv(h,p)),
                      'step_residual':residual,'propagated_bound':rat(B),'distance_to_stationary':rat(tv(h,stationary)),
                      'stationary_bound':rat(factor*d0+B)})
    if keep is not None:trace=trace[:keep]
    return {'profile':PROFILE,'request':copy.deepcopy(e),'q':rat(q),'trace':trace,'claim':classify(e,q,trace)}


def limits():
    resource.setrlimit(resource.RLIMIT_CPU,(3,3));resource.setrlimit(resource.RLIMIT_AS,(134217728,134217728));resource.setrlimit(resource.RLIMIT_FSIZE,(262144,262144))


class Campaign:
    def __init__(self,out):
        self.out=out;self.started=time.perf_counter();self.runs=[];self.assertions=0;self.work=0
        self.phases={k:0. for k in ('construction_seconds','receiving_seconds','serialization_seconds','control_seconds')}
    def check(self,condition,message):
        self.assertions+=1
        if not condition:raise AssertionError(message)
    def save(self,p,value):
        t=time.perf_counter();put(p,value);self.phases['serialization_seconds']+=time.perf_counter()-t
    def build(self,e,**kw):
        t=time.perf_counter();value=produce(e,**kw);self.phases['construction_seconds']+=time.perf_counter()-t;return value
    def call(self,name,e,c,wanted,prefix):
        self.check(len(self.runs)<50,'process-budget');d=self.out/name;d.mkdir(parents=True)
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
        elapsed=time.perf_counter()-t;self.phases['receiving_seconds']+=elapsed;row.update(returncode=p.returncode,wall_seconds=elapsed)
        self.check(p.returncode==0,(name,p.returncode,(d/'stderr.txt').read_text()))
        answer=json.loads((d/'stdout.json').read_text());self.work+=answer['work_units'];row.update(outcome=answer['outcome'],reason=answer['reason'],work_units=answer['work_units'])
        self.check(answer['outcome']==wanted,(name,answer))
        self.check(answer['expected_request']==(None if name=='context/float-number' else e),'request-retention')
        self.check(answer['verified_prefix']==c['trace'][:prefix],'verified-prefix-retention')
        self.check(all(answer[k] is False for k in ('native_authority','close_authorized','free_authorized')),'no-native-authority')
        accepted=wanted in ('CertifiedTolerance','VerifiedHorizon')
        result={**c['claim'],'actual_final_distance':c['trace'][-1]['distance_to_stationary']} if accepted else None
        self.check(answer['accepted_result']==result,'accepted-result-scope')
        missing={'missing_indices':list(range(len(c['trace']),e['horizon']+1))} if wanted=='UnknownCoverage' else None
        self.check(answer['obstruction']==missing,'explicit-coverage-residual')
        self.check(0<=answer['work_units']<=10000 and self.work+PRODUCER_WORK+CONTROL_WORK<=100000,'work-budget')
        return answer
    def controls(self,name,e,c):
        global CONTROL_WORK
        t=time.perf_counter();rows=[];K=list(map(vals,e['kernel']));q=F(*c['q'])
        for x,y in itertools.product((F(0),F(1,3),F(1)),repeat=2):
            p=[x,1-x];r=[y,1-y]
            # Direct full-row arithmetic, independent of the receiver scalar update.
            pp=[sum(p[i]*K[i][j] for i in range(2)) for j in range(2)]
            rr=[sum(r[i]*K[i][j] for i in range(2)) for j in range(2)]
            before=sum(abs(p[i]-r[i]) for i in range(2))/2;after=sum(abs(pp[i]-rr[i]) for i in range(2))/2;CONTROL_WORK+=12
            self.check(sum(pp)==1 and min(pp)>=0,'mass-nonnegative')
            self.check(after==q*before,'finite-distance-identity')
            rows.append({'p':vec(p),'r':vec(r),'before':rat(before),'after':rat(after)})
        for r in c['trace']:
            self.check(F(*r['error_to_exact'])<=F(*r['propagated_bound']),'propagated-error')
            self.check(F(*r['distance_to_stationary'])<=F(*r['stationary_bound']),'stationarity-bound')
        if CONTROL_WORK>10000:raise TimeoutError('control-work')
        self.phases['control_seconds']+=time.perf_counter()-t;self.save(self.out/'valid'/name/'pair-controls.json',rows)


def execute(camp):
    half=F(1,2);quarter=F(1,4);one=[1,0];fair=[half,half]
    primary=request('mixing',F(3,4),quarter,one,fair,tolerance=F(1,32))
    specs=[
        ('mixing',primary,{},'CertifiedTolerance'),
        ('reuse-asymmetric',request('reuse-asymmetric',half,quarter,one,[F(1,3),F(2,3)],N=3),{},'CertifiedTolerance'),
        ('alternating',request('alternating',quarter,F(3,4),one,fair),{},'VerifiedHorizon'),
        ('equal-rows',request('equal-rows',quarter,quarter,one,[quarter,F(3,4)],N=2,tolerance=0),{},'CertifiedTolerance'),
        ('equal-rows-zero-horizon',request('equal-rows-zero-horizon',quarter,quarter,one,[quarter,F(3,4)],N=0,tolerance=0),{},'VerifiedHorizon'),
        ('identity',request('identity',1,0,one,fair),{},'VerifiedHorizon'),
        ('swap',request('swap',0,1,one,fair),{},'VerifiedHorizon'),
        ('swap-stationary',request('swap-stationary',0,1,fair,fair,tolerance=0),{},'CertifiedTolerance'),
        ('absorbing-stationary',request('absorbing-stationary',1,half,one,one,tolerance=0),{},'CertifiedTolerance'),
        ('identity-stationary',request('identity-stationary',1,0,one,one,tolerance=0),{},'CertifiedTolerance'),
        ('initial-perturbation',request('initial-perturbation',F(3,4),quarter,one,fair,N=3,initial_error=F(1,16),tolerance=F(1,16)),{'approx_initial':[F(15,16),F(1,16)]},'VerifiedHorizon'),
        ('accumulated-noise',request('accumulated-noise',F(3,4),quarter,one,fair,errors=[F(1,16)]*4,tolerance=F(1,8)),{'noise':[F(1,16)]*4},'VerifiedHorizon'),
        ('loose-budget',request('loose-budget',F(3,4),quarter,one,fair,errors=[F(1,8)]*4,tolerance=F(1,8)),{},'VerifiedHorizon'),
        ('unclamped-budget',request('unclamped-budget',1,0,one,one,initial_error=1,errors=[1]*4,tolerance=1),{},'VerifiedHorizon'),
        ('stationary-zero-horizon',request('stationary-zero-horizon',F(3,4),quarter,fair,fair,N=0,initial_error=F(1,16),tolerance=F(1,16)),{},'CertifiedTolerance')]
    saved={}
    for name,e,kwargs,kind in specs:
        c=camp.build(e,**kwargs);saved[name]=(e,c);camp.call('valid/'+name,e,c,kind,len(c['trace']));camp.controls(name,e,c)
    camp.check([r['exact'][0] for r in saved['mixing'][1]['trace']]==[[1,1],[3,4],[5,8],[9,16],[17,32]],'analytic-mixing-trace')
    noisy=saved['accumulated-noise'][1]['trace']
    camp.check([r['approx'][0] for r in noisy]==[[1,1],[13,16],[23,32],[43,64],[83,128]],'analytic-noisy-trace')
    camp.check(all(r['error_to_exact']==r['propagated_bound'] for r in noisy),'sharp-propagated-error')
    camp.check(noisy[-1]['stationary_bound']==[19,128],'analytic-noisy-stationarity-bound')
    camp.check(saved['unclamped-budget'][1]['trace'][-1]['propagated_bound']==[5,1],'no-implicit-clamp')
    camp.check(saved['swap'][1]['trace'][0]['exact']==saved['swap'][1]['trace'][2]['exact']!=saved['swap'][1]['trace'][1]['exact'],'periodic-not-stationary')
    ca=saved['absorbing-stationary'][1];ci=saved['identity-stationary'][1]
    camp.check(ca['trace']==ci['trace'] and ca['q']!=ci['q'],'same-trace-different-global-factor')
    for source in ('mixing','equal-rows'):
        e,_=saved[source];c=camp.build(e,keep=2);camp.call('partial/'+source,e,c,'UnknownCoverage',2)
    bad=[]
    def alter(name,source,path,value,prefix):
        e,c=saved[source];c=copy.deepcopy(c);at=c
        for k in path[:-1]:at=at[k]
        at[path[-1]]=value;bad.append((name,e,c,prefix))
    alter('wrong-factor','mixing',['q'],[0,1],0)
    alter('wrong-exact-step','mixing',['trace',1,'exact'],vec([half,half]),1)
    alter('approx-mass','mixing',['trace',1,'approx'],vec([half,quarter]),1)
    alter('wrong-residual','mixing',['trace',1,'step_residual'],[1,16],1)
    en=copy.deepcopy(saved['accumulated-noise'][0]);en['step_errors'][0]=[1,32]
    bad.append(('understated-local-budget',en,camp.build(en,noise=[F(1,16)]*4),1))
    en=copy.deepcopy(saved['initial-perturbation'][0]);en['initial_error']=[0,1]
    bad.append(('understated-initial-budget',en,camp.build(en,approx_initial=[F(15,16),F(1,16)]),0))
    alter('wrong-propagated-bound','accumulated-noise',['trace',2,'propagated_bound'],[0,1],2)
    alter('wrong-stationary-distance','mixing',['trace',2,'distance_to_stationary'],[0,1],2)
    alter('wrong-stationary-bound','mixing',['trace',2,'stationary_bound'],[0,1],2)
    alter('false-tolerance','loose-budget',['claim','kind'],'CertifiedTolerance',5)
    alter('false-contraction','swap',['claim','regime'],'StrictContraction',5)
    ei,_=saved['identity-stationary'];changed=copy.deepcopy(ei);changed['kernel']=saved['absorbing-stationary'][0]['kernel']
    fresh=camp.build(changed);camp.check(fresh['trace']==ci['trace'] and fresh['q']!=ci['q'],'changed-unused-row-witness')
    bad.append(('changed-unused-row',ei,fresh,0))
    for name,key,value in [('changed-initial','initial',vec(fair)),('changed-horizon','horizon',3),('changed-history','history',['rebound']),('changed-states','states',['right','left'])]:
        alter(name,'mixing',['request',key],value,0)
    alter('wrong-profile','mixing',['profile'],'adva.research.markov-horizon.v1',0)
    alter('skipped-step','mixing',['trace',2,'index'],3,2)
    e,c=saved['mixing'];c=copy.deepcopy(c);c['free_authorized']=True;bad.append(('extra-authority',e,c,0))
    camp.check(len(bad)==19,'declared-evidence-count')
    for name,e,c,prefix in bad:camp.call('evidence/'+name,e,c,'InvalidEvidence',prefix)
    base,receipt=saved['mixing'];contexts=[]
    def context(name,key,value):
        e=copy.deepcopy(base);e[key]=value;contexts.append((name,e))
    context('state-dimension','states',['a','b','c'])
    context('duplicate-states','states',['a','a'])
    context('kernel-shape','kernel',[vec([half,half])])
    context('negative-kernel','kernel',[vec([-1,2]),vec([quarter,F(3,4)])])
    context('row-mass','kernel',[vec([1,1]),vec([quarter,F(3,4)])])
    context('initial-mass','initial',vec([half,quarter]))
    context('nonstationary-reference','stationary',vec(one))
    context('horizon-cap','horizon',7)
    context('boolean-horizon','horizon',True)
    context('error-list-length','step_errors',vec([0,0,0]))
    context('negative-error','initial_error',[-1,16])
    context('float-number','initial_error',[0.0,1])
    context('history-cap','history',['a','b','c','d','e'])
    context('wrong-direction','direction','column')
    for name,e in contexts:camp.call('context/'+name,e,receipt,'InvalidContext',0)
    camp.check(len(camp.runs)==50,'declared-process-count')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);a=parser.parse_args()
    a.output.mkdir(parents=True,exist_ok=False);camp=Campaign(a.output);failure=None
    camp.save(a.output/'contract.json',json.loads((ROOT/'contract.json').read_text()))
    try:execute(camp)
    except Exception as exc:failure={'type':type(exc).__name__,'message':str(exc)}
    elapsed=time.perf_counter()-camp.started;size=sum(p.stat().st_size for p in a.output.rglob('*') if p.is_file())
    if elapsed>30 or size>2097152:failure=failure or {'type':'BudgetExceeded','message':'wall/evidence bound'}
    result={'profile':PROFILE,'success':failure is None,'failure':failure,'receiver_calls':len(camp.runs),'assertions':camp.assertions,
            'receiver_work':camp.work,'producer_work':PRODUCER_WORK,'control_work':CONTROL_WORK,'search_candidates':0,
            'wall_seconds':elapsed,'phases':camp.phases,'cases':camp.runs,
            'child_maxrss_kib':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,'supervisor_maxrss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'evidence_bytes_before_summary':size,'python':sys.version,
            'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ('receive.py','run.py','contract.json')},
            'limits':'Linux process high-water RSS, not aggregate memory. Reading, review, network, final archive/report costs not in campaign time.'}
    put(a.output/'execution.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('cases','source_sha256')}))
    return 0 if failure is None else 1


if __name__=='__main__':raise SystemExit(main())
