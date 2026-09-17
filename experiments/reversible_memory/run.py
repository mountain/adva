#!/usr/bin/env python3
"""Original finite reversible-memory producer/control supervisor, Unknown v0.3.
ChatGPT (OpenAI), via Mingli Yuan's authorized account proxy; not his review.
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
PROFILE='adva.research.reversible-memory.v0'
WORK=0
CONTROL=0

def tick(n=1):
    global WORK
    WORK+=n
    if WORK>30000: raise TimeoutError('producer-work')

def rat(x):
    x=F(x);return [x.numerator,x.denominator]
def vec(xs):return [rat(x) for x in xs]
def put(p,x):p.write_text(json.dumps(x,sort_keys=True,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def request(name,m,rate,initial_one=0,mode='iid',schedule=None,H=6):
    q=F(rate);r=F(initial_one);weights=[]
    for s in range(2):
        for bits in itertools.product((0,1),repeat=m):
            p=F(1)
            if mode=='parity':p=F(1,2**(m-1)) if sum(bits)%2==0 else F(0)
            else:
                for e in bits:p*=q if e else 1-q;tick()
            weights.append((r if s else 1-r)*p);tick()
    return {'question':name,'system_states':['zero','one'],'environment':['e'+str(j) for j in range(m)],
            'horizon':H,'schedule':list(range(H)) if schedule is None else schedule,'initial_joint':vec(weights),
            'flip_rate':rat(q),'history':[name+':declared'],'scope':'finite-reversible-bit-environment'}

def classify(e,rows):
    first=next((r['step'] for r in rows if not r['history_match']),None)
    kind='UnknownCoverage' if len(rows)<e['horizon'] else 'Counterexample' if first is not None else 'VerifiedMarkovHorizon'
    return {'kind':kind,'first_failure':first}

def produce(e,keep=None):
    m=len(e['environment']);H=e['horizon'];q=F(*e['flip_rate']);paths=[]
    for s in range(2):
        for mask,bits in enumerate(itertools.product((0,1),repeat=m)):
            cur=s;path=[s]
            for j in e['schedule']:cur=(cur+bits[j])%2;path.append(cur);tick()
            paths.append((tuple(path),F(*e['initial_joint'][s*(2**m)+mask])))
    rows=[]
    for t in range(1,H+1):
        prior=[F(0),F(0)];law=[F(0),F(0)];pairs=[[F(0),F(0)],[F(0),F(0)]];groups={}
        for path,p in paths:
            prior[path[t-1]]+=p;law[path[t]]+=p;pairs[path[t-1]][path[t]]+=p
            h=path[:t]
            if h not in groups:groups[h]=[F(0),F(0)]
            groups[h][0]+=p
            if path[t]!=path[t-1]:groups[h][1]+=p
            tick()
        predicted=[prior[0]*(1-q)+prior[1]*q,prior[0]*q+prior[1]*(1-q)]
        adjacent=all(pairs[a][b]==prior[a]*(q if a!=b else 1-q) for a,b in itertools.product((0,1),repeat=2))
        witness=None;positive=0
        for h,(mass,flip) in sorted(groups.items()):
            tick()
            if mass==0:continue
            positive+=1
            if flip!=q*mass and witness is None:
                witness={'history':list(h),'history_mass':rat(mass),'flip_mass':rat(flip),'required_flip_mass':rat(q*mass)}
        rows.append({'step':t,'law':vec(law),'predicted_law':vec(predicted),'marginal_match':law==predicted,
                     'adjacent_match':adjacent,'history_match':witness is None,'positive_histories':positive,
                     'null_histories':2**t-positive,'witness':witness})
    if keep is not None:rows=rows[:keep]
    return {'profile':PROFILE,'request':copy.deepcopy(e),'micro':{'states':2**(m+1),'gate_bijections':H*2**(m+1),'roundtrip_states':2**(m+1)},
            'trace':rows,'claim':classify(e,rows)}

def limit_child():
    resource.setrlimit(resource.RLIMIT_CPU,(3,3))
    resource.setrlimit(resource.RLIMIT_AS,(134217728,134217728))
    resource.setrlimit(resource.RLIMIT_FSIZE,(262144,262144))

class Campaign:
    def __init__(self,out):
        self.out=out;self.start=time.perf_counter();self.runs=[];self.assertions=0;self.receiver_work=0
        self.times={k:0. for k in ('construction_seconds','receiving_seconds','serialization_seconds','control_seconds','reuse_construction_seconds','reuse_receiving_seconds','context_construction_seconds')}
    def check(self,x,msg):
        self.assertions+=1
        if not x:raise AssertionError(msg)
    def save(self,p,x):
        t=time.perf_counter();put(p,x);self.times['serialization_seconds']+=time.perf_counter()-t
    def build(self,e,**kw):
        t=time.perf_counter();c=produce(e,**kw);dt=time.perf_counter()-t;self.times['construction_seconds']+=dt
        if e['question']=='reuse-third':self.times['reuse_construction_seconds']+=dt
        return c
    def call(self,name,e,c,expected,prefix):
        self.check(len(self.runs)<36,'receiver-call-cap');d=self.out/name;d.mkdir(parents=True)
        self.save(d/'expected.json',e);self.save(d/'candidate.json',c)
        self.check(all((d/n).stat().st_size<=65536 for n in ('expected.json','candidate.json')),'wire-cap')
        args=[sys.executable,'-B','-S',str(ROOT/'receive.py'),'--expected',str(d/'expected.json'),'--candidate',str(d/'candidate.json')]
        self.save(d/'command.json',{'argv':args})
        row={'case':name};self.runs.append(row);remaining=30-(time.perf_counter()-self.start)
        if remaining<=0:raise TimeoutError('campaign-wall')
        t=time.perf_counter()
        with (d/'stdout.json').open('wb') as out,(d/'stderr.txt').open('wb') as err:
            p=subprocess.Popen(args,stdout=out,stderr=err,preexec_fn=limit_child)
            try:p.wait(timeout=min(3,remaining))
            finally:
                if p.poll() is None:p.kill();p.wait(timeout=.2)
        dt=time.perf_counter()-t;self.times['receiving_seconds']+=dt
        if e['question']=='reuse-third':self.times['reuse_receiving_seconds']+=dt
        row.update(returncode=p.returncode,wall_seconds=dt)
        self.check(p.returncode==0,(name,p.returncode,(d/'stderr.txt').read_text()))
        ans=json.loads((d/'stdout.json').read_text());self.receiver_work+=ans['work_units']
        row.update(outcome=ans['outcome'],reason=ans['reason'],work_units=ans['work_units'])
        self.check(ans['outcome']==expected,(name,ans['outcome'],ans['reason']))
        self.check(ans['verified_prefix']==c['trace'][:prefix],(name,'prefix'))
        self.check(all(ans[k] is False for k in ('native_authority','close_authorized','free_authorized')),'authority')
        wanted=c['claim'] if expected in ('VerifiedMarkovHorizon','Counterexample') else None
        self.check(ans['accepted_result']==wanted,(name,'accepted'))
        first=next(({'step':r['step'],**r['witness']} for r in c['trace'][:prefix] if r['witness'] is not None),None)
        self.check(ans['verified_counterexample']==first,(name,'retained-counterexample'))
        missing={'missing_steps':list(range(prefix+1,e['horizon']+1))} if expected=='UnknownCoverage' else None
        self.check(ans['obstruction']==missing,(name,'coverage'))
        self.check(ans['expected_request']==(None if expected=='InvalidContext' else e),(name,'request'))
        self.check(self.receiver_work+WORK+CONTROL<=100000,'total-work')
        return ans


def execute(camp):
    global CONTROL
    fixture_started=time.perf_counter()
    specs=[
        ('fresh-quarter',request('fresh-quarter',6,F(1,4)),'VerifiedMarkovHorizon'),
        ('reuse-third',request('reuse-third',6,F(1,3),F(1,3)),'VerifiedMarkovHorizon'),
        ('repeated-quarter',request('repeated-quarter',1,F(1,4),schedule=[0]*6),'Counterexample'),
        ('stationary-memory',request('stationary-memory',1,F(1,2),F(1,2),schedule=[0]*6),'Counterexample'),
        ('parity-six',request('parity-six',6,F(1,2),mode='parity'),'Counterexample'),
        ('fresh-fair',request('fresh-fair',6,F(1,2)),'VerifiedMarkovHorizon'),
        ('identity',request('identity',1,0,schedule=[0]*6),'VerifiedMarkovHorizon'),
        ('swap',request('swap',1,1,F(1,3),schedule=[0]*6),'VerifiedMarkovHorizon'),
        ('zero-horizon',request('zero-horizon',1,F(1,4),H=0),'VerifiedMarkovHorizon'),
        ('repeated-index',request('repeated-index',6,F(1,4),schedule=[0,0,2,3,4,5]),'Counterexample')]
    camp.times['context_construction_seconds']+=time.perf_counter()-fixture_started
    saved={}
    for name,e,kind in specs:
        c=camp.build(e);saved[name]=(e,c);camp.call('valid/'+name,e,c,kind,len(c['trace']))
    t=time.perf_counter()
    camp.check([r['law'][0] for r in saved['fresh-quarter'][1]['trace']]==vec([F(3,4),F(5,8),F(9,16),F(17,32),F(33,64),F(65,128)]),'analytic-iid')
    for name,first in [('repeated-quarter',2),('stationary-memory',2),('parity-six',6),('repeated-index',2)]:
        camp.check(saved[name][1]['claim']['first_failure']==first,'first-failure')
    hidden=saved['stationary-memory'][1]['trace'];camp.check(all(r['marginal_match'] and r['adjacent_match'] for r in hidden),'adjacent-laws-hide-memory')
    parity=saved['parity-six'][1]['trace'];fresh=saved['fresh-fair'][1]['trace']
    camp.check(parity[:5]==fresh[:5] and parity[5]['law']==vec([1,0]),'five-steps-identical')
    controls=[]
    e=saved['parity-six'][0];weights=[F(*r) for r in e['initial_joint'][:64]]
    for omitted in range(6):
        masses={bits:F(0) for bits in itertools.product((0,1),repeat=5)}
        for mask,bits in enumerate(itertools.product((0,1),repeat=6)):
            key=bits[:omitted]+bits[omitted+1:];masses[key]+=weights[mask];CONTROL+=1
        camp.check(all(p==F(1,32) for p in masses.values()),'every-five-bit-subset-iid')
        controls.append({'omitted_environment':omitted,'masses':[rat(masses[b]) for b in sorted(masses)]})
    for name,(e,c) in saved.items():
        for state in range(2**(len(e['environment'])+1)):
            bits=len(e['environment']);mask=state%(2**bits);s=state//(2**bits);cur=s
            for j in e['schedule']+list(reversed(e['schedule'])):
                cur=(cur+((mask//(2**(bits-1-j)))%2))%2;CONTROL+=1
            camp.check(cur==s,'full-state-roundtrip')
    q=F(1,4);K=[[1-q,q],[q,1-q]];inv=[[F(3,2),F(-1,2)],[F(-1,2),F(3,2)]]
    for a,b in itertools.product((0,1),repeat=2):
        camp.check(sum(K[a][j]*inv[j][b] for j in range(2))==int(a==b),'matrix-inverse')
        camp.check(K[a][b]/2==K[b][a]/2,'detailed-balance');CONTROL+=4
    camp.times['control_seconds']+=time.perf_counter()-t
    camp.save(camp.out/'independent-controls.json',{'five-bit-marginals':controls,'quarter_kernel_inverse':[[rat(x) for x in r] for r in inv],'all_state_roundtrips_checked':True})
    for name,keep in [('fresh-quarter',5),('parity-six',5),('stationary-memory',2)]:
        e,_=saved[name];c=camp.build(e,keep=keep);camp.call('partial/'+name,e,c,'UnknownCoverage',keep)
    base,cert=saved['fresh-quarter'];bad=[]
    def alter(name,path,value,prefix,source='fresh-quarter'):
        e,c=saved[source];c=copy.deepcopy(c);at=c
        for k in path[:-1]:at=at[k]
        at[path[-1]]=value;bad.append((name,e,c,prefix))
    alter('profile',['profile'],'adva.research.reversible-memory.v1',0)
    alter('labels',['request','system_states'],['one','zero'],0)
    changed=copy.deepcopy(base);changed['schedule']=[0,0,2,3,4,5];bad.append(('recomputed-schedule',base,camp.build(changed),0))
    changed=copy.deepcopy(saved['fresh-fair'][0]);changed['initial_joint']=saved['parity-six'][0]['initial_joint'];bad.append(('recomputed-law',saved['fresh-fair'][0],camp.build(changed),0))
    alter('micro',['micro','roundtrip_states'],0,0)
    alter('law',['trace',1,'law'],vec([1,0]),1)
    alter('adjacent-bool',['trace',0,'adjacent_match'],1,0)
    alter('history-bool',['trace',1,'history_match'],True,1,'stationary-memory')
    alter('witness-mass',['trace',1,'witness','history_mass'],[1,1],1,'stationary-memory')
    alter('missing-witness',['trace',5,'witness'],None,5,'parity-six')
    alter('false-claim',['claim','kind'],'VerifiedMarkovHorizon',6,'parity-six')
    alter('skipped-step',['trace',1,'step'],3,1)
    c=copy.deepcopy(cert);c['free_authorized']=True;bad.append(('extra-authority',base,c,0))
    for name,e,c,prefix in bad:camp.call('evidence/'+name,e,c,'InvalidEvidence',prefix)
    contexts=[]
    def context(name,key,value):
        e=copy.deepcopy(base);e[key]=value;contexts.append((name,e))
    context('missing-mass','initial_joint',base['initial_joint'][:-1])
    weights=copy.deepcopy(base['initial_joint']);weights[0]=[-1,1];context('negative-mass','initial_joint',weights)
    weights=copy.deepcopy(base['initial_joint']);weights[0]=[0,1];context('wrong-total','initial_joint',weights)
    context('zero-denominator','flip_rate',[1,0])
    context('boolean-horizon','horizon',True)
    context('horizon-cap','horizon',7)
    context('duplicate-label','system_states',['same','same'])
    context('schedule-index','schedule',[6,1,2,3,4,5])
    context('scope','scope','universal')
    context('float','flip_rate',[0.25,1])
    for name,e in contexts:camp.call('context/'+name,e,cert,'InvalidContext',0)
    camp.check(len(camp.runs)==36,'declared-cases')


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(134217728,134217728))
    a.output.mkdir(parents=True,exist_ok=False);camp=Campaign(a.output);failure=None
    camp.save(a.output/'contract.json',json.loads((ROOT/'contract.json').read_text()))
    try:execute(camp)
    except Exception as exc:failure={'type':type(exc).__name__,'message':str(exc)}
    size=sum(p.stat().st_size for p in a.output.rglob('*') if p.is_file());elapsed=time.perf_counter()-camp.start
    if size>2097152 or elapsed>30:failure=failure or {'type':'BudgetExceeded','message':'campaign boundary'}
    result={'profile':PROFILE,'success':failure is None,'failure':failure,'receiver_calls':len(camp.runs),'assertions':camp.assertions,
            'receiver_work':camp.receiver_work,'producer_work':WORK,'control_work':CONTROL,'search_candidates':0,'wall_seconds':elapsed,
            'phases':camp.times,'cases':camp.runs,'child_maxrss_kib':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            'supervisor_maxrss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'evidence_bytes_before_summary':size,
            'python':sys.version,'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ('receive.py','run.py','contract.json')},
            'limits':'Linux RSS per-process high water, not aggregate memory; reports, review and network outside campaign timing. Reuse times are subsets of construction/receiving.'}
    put(a.output/'execution.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('cases','source_sha256')}))
    return 0 if failure is None else 1

if __name__=='__main__':raise SystemExit(main())
