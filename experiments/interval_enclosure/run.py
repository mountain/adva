#!/usr/bin/env python3
"""Original finite interval producer and independent supervisor, Unknown v0.3.

ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy; not his review.
No legacy campaign or receiving implementation is imported.
"""
import argparse
import copy
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent
PROFILE='adva.research.interval-enclosure.v0'
PRODUCER_WORK=0
POINT_WORK=0


def tick(n=1):
    global PRODUCER_WORK
    PRODUCER_WORK+=n
    if PRODUCER_WORK>10000:raise TimeoutError('producer-work-limit')


def rat(q):q=F(q);return [q.numerator,q.denominator]
def iv(v):return list(map(rat,v))
def vals(v):return [F(*x) for x in v]
def put(path,obj):path.write_text(json.dumps(obj,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def var(name='x'):return {'op':'var','name':name}
def const(v):return {'op':'const','value':rat(v)}
def op(name,left,right):return {'op':name,'left':left,'right':right}


def fixture(name,boxes,nodes,grid=None):
    return {'question':'interval-'+name,'variables':[{'name':k,'interval':iv(v)} for k,v in boxes.items()],
            'nodes':nodes,'mode':'exact-rational' if grid is None else 'outward-grid','grid':grid,
            'epsilon':[1,16],'history':[name+':declared'],'scope':'all-rational-valuations-in-box'}


def result_for(interval,epsilon):
    lo,hi=interval
    zero='ExactZero' if lo==hi==0 else 'StrictPositive' if lo>0 else 'StrictNegative' if hi<0 else 'ZeroUndetermined'
    one='ExactOne' if lo==hi==1 else 'ExcludesOne' if hi<1 or lo>1 else 'OneUndetermined'
    return {'kind':'enclosure','interval':iv(interval),'zero_class':zero,'one_class':one,'within_epsilon':-epsilon<=lo and hi<=epsilon}


def produce(e):
    boxes={v['name']:vals(v['interval']) for v in e['variables']};ranges=[];trace=[]
    for i,node in enumerate(e['nodes']):
        name=node['op'];tick()
        if name=='var':raw=boxes[node['name']]
        elif name=='const':raw=[F(*node['value'])]*2
        else:
            a,b=ranges[node['left']],ranges[node['right']]
            if name=='div' and b[0]<=0<=b[1]:
                return {'profile':PROFILE,'request':copy.deepcopy(e),'trace':trace,'result':{'kind':'unknown-domain','node':i,'denominator':iv(b)}}
            if name=='add':corners=[x+y for x in a for y in b]
            elif name=='sub':corners=[x-y for x in a for y in b]
            elif name=='mul':corners=[x*y for x in a for y in b]
            else:corners=[x/y for x in a for y in b]
            tick(4);raw=[min(corners),max(corners)]
        if e['mode']=='outward-grid':
            n=e['grid'];rounded=[F((raw[0]*n).__floor__(),n),F((raw[1]*n).__ceil__(),n)];tick(2)
        else:rounded=raw[:]
        trace.append({'index':i,'tight':iv(raw),'enclosure':iv(rounded)});ranges.append(rounded)
    return {'profile':PROFILE,'request':copy.deepcopy(e),'trace':trace,'result':result_for(ranges[-1],F(*e['epsilon']))}


def evaluate(e,point):
    global POINT_WORK
    values=[]
    for n in e['nodes']:
        POINT_WORK+=1
        if POINT_WORK>10000:raise TimeoutError('point-work-limit')
        if n['op']=='var':value=point[n['name']]
        elif n['op']=='const':value=F(*n['value'])
        else:
            x,y=values[n['left']],values[n['right']]
            if n['op']=='add':value=x+y
            elif n['op']=='sub':value=x-y
            elif n['op']=='mul':value=x*y
            else:value=x/y
        values.append(value)
    return values[-1]


def limits():
    resource.setrlimit(resource.RLIMIT_CPU,(3,3));resource.setrlimit(resource.RLIMIT_AS,(134217728,134217728));resource.setrlimit(resource.RLIMIT_FSIZE,(262144,262144))


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
        self.check(len(self.runs)<53,'process-cap');d=self.out/name;d.mkdir(parents=True)
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
        answer=json.loads((d/'stdout.json').read_text());self.work+=answer['work_units'];row.update(outcome=answer['outcome'],reason=answer['reason'],work_units=answer['work_units'])
        self.check(answer['outcome']==wanted,(name,answer));self.check(answer['expected_request']==(None if name=='context/float-endpoint' else e),'expected-or-raw-parse-failure-retained')
        self.check(all(answer[k] is False for k in ('native_authority','close_authorized','free_authorized')),'no-native-authority')
        self.check(0<=answer['work_units']<=10000 and self.work+PRODUCER_WORK+POINT_WORK<=100000,'work-bounds')
        accepted=wanted=='VerifiedEnclosure'
        self.check(answer['accepted_result']==r['result'] if accepted else answer['accepted_result'] is None,'accepted-result-scope');self.check(bool(answer['semantic_delta'])==accepted,'semantic-delta-scope')
        if wanted in ('VerifiedEnclosure','UnknownDomain'):
            self.check(answer['verified_prefix']==r['trace'],'complete-verified-prefix-preserved')
            if not accepted:
                self.check(answer['obstruction']['node']==r['result']['node'] and answer['obstruction']['denominator']==r['result']['denominator'],'exact-domain-obstruction')
            self.observe(name,e,r)
        return answer
    def observe(self,name,e,r):
        t=time.perf_counter();names=[v['name'] for v in e['variables']];choices=[]
        for v in e['variables']:
            lo,hi=vals(v['interval']);choices.append(sorted({lo,(lo+hi)/2,hi}))
        rows=[]
        for point_values in itertools.product(*choices):
            point=dict(zip(names,point_values));row={'valuation':{k:rat(v) for k,v in point.items()}}
            try:value=evaluate(e,point)
            except ZeroDivisionError:row['outcome']='UndefinedAtSample';self.check(r['result']['kind']=='unknown-domain','accepted-domain-includes-sampled-pole')
            else:
                row.update(outcome='DefinedAtSample',value=rat(value))
                if r['result']['kind']=='enclosure':
                    lo,hi=vals(r['result']['interval']);self.check(lo<=value<=hi,'sample-contained')
            rows.append(row)
        self.phases['independent_observation_seconds']+=time.perf_counter()-t
        self.save(self.out/name/'point-observations.json',{'scope':'Finite rational samples; not proof of full-box enclosure, identity or domain safety. Shared variable names use the same assigned value.','samples':rows})


def main(out):
    out.mkdir(parents=True,exist_ok=False);c=Campaign(out);failure=None
    def deadline(*_):raise TimeoutError('campaign-wall-limit')
    signal.signal(signal.SIGALRM,deadline);signal.setitimer(signal.ITIMER_REAL,30)
    try:
        c.save(out/'contract.json',json.loads((ROOT/'contract.json').read_text()));cases={};receipts={}
        def add(name,boxes,nodes,grid=None,outcome='VerifiedEnclosure'):
            e=fixture(name,boxes,nodes,grid);r=c.build(e);cases[name]=e;receipts[name]=r;c.call('valid/'+name,e,r,outcome)
        add('round-positive',{'x':[F(1,3),F(2,3)]},[var()],8)
        add('复用-round-negative',{'x':[F(-2,3),F(-1,3)]},[var()],8)
        signs={'N':[-2,-1],'Z':[-1,1],'P':[1,2]}
        for left,a in signs.items():
            for right,b in signs.items():add('sign-'+left+right,{'x':a,'y':b},[var(),var('y'),op('mul',0,1)])
        add('negative-quotient',{'x':[1,2],'y':[-4,-2]},[var(),var('y'),op('div',0,1)])
        add('nested',{'x':[F(1,3),F(2,3)],'y':[F(1,8),F(1,4)]},[var(),var('y'),op('add',0,1),op('sub',0,1),op('mul',2,3)])
        add('exact-zero',{},[const(F(1,3)),op('sub',0,0)])
        add('small-positive',{},[const(F(1,64))])
        add('small-uncertain',{'x':[F(-1,64),F(1,64)]},[var()])
        add('dependency-zero',{'x':[1,2]},[var(),op('sub',0,0)])
        add('fine-denominator',{'x':[F(1,64),F(1,32)]},[const(1),var(),op('div',0,1)],64)
        add('dependency-one',{'x':[1,2]},[var(),op('div',0,0)])
        add('exact-one',{},[const(F(1,3)),op('div',0,0)])
        c.check(len(cases)==20,'declared-complete-fixtures')
        add('cross-zero',{'x':[-1,1]},[const(1),var(),op('div',0,1)],outcome='UnknownDomain')
        add('touch-zero',{'x':[0,1]},[const(0),var(),op('div',0,1)],outcome='UnknownDomain')
        add('dependency-domain',{'x':[1,2]},[var(),op('sub',0,0),const(1),op('add',1,2),op('div',0,3)],outcome='UnknownDomain')
        add('coarse-denominator',{'x':[F(1,64),F(1,32)]},[const(1),var(),op('div',0,1)],16,outcome='UnknownDomain')
        add('masked-pole',{'x':[-1,1]},[const(0),const(1),var(),op('div',1,2),op('mul',0,3)],outcome='UnknownDomain')
        for name in ('small-positive','small-uncertain'):
            c.check(receipts[name]['result']['within_epsilon'] is True and receipts[name]['result']['zero_class']!='ExactZero','epsilon-not-exact-zero')
        c.check(receipts['dependency-zero']['result']['interval']==iv([-1,1]),'dependency-zero-retained')
        c.check(receipts['dependency-one']['result']['interval']==iv([F(1,2),2]),'dependency-one-retained')
        controls=[]
        def mutate(label,key,edit):
            r=copy.deepcopy(receipts[key]);edit(r);controls.append((label,cases[key],r))
        def bad_round(r,index,direction):
            node=r['trace'][0];raw=vals(node['tight']);n=r['request']['grid']
            node['enclosure'][index]=rat(F((raw[index]*n).__ceil__() if direction=='up' else (raw[index]*n).__floor__(),n))
            r['result']=result_for(vals(node['enclosure']),F(*r['request']['epsilon']))
        for key,prefix in (('round-positive','positive'),('复用-round-negative','negative')):
            mutate(prefix+'-inward-lower',key,lambda r:bad_round(r,0,'up'))
            mutate(prefix+'-inward-upper',key,lambda r:bad_round(r,1,'down'))
        mutate('missing-trace','nested',lambda r:r['trace'].pop())
        mutate('wrong-tight','round-positive',lambda r:r['trace'][0].__setitem__('tight',iv([F(1,4),F(3,4)])))
        mutate('diagonal-only-product','sign-ZZ',lambda r:r['trace'][-1].__setitem__('tight',iv([1,1])))
        mutate('wrong-negative-quotient','negative-quotient',lambda r:r['trace'][-1].__setitem__('tight',iv([F(-1,2),F(-1,2)])))
        mutate('small-positive-as-zero','small-positive',lambda r:r['result'].__setitem__('zero_class','ExactZero'))
        mutate('small-uncertain-as-zero','small-uncertain',lambda r:r['result'].__setitem__('zero_class','ExactZero'))
        def shortcut(r,value):
            r['trace'][-1]['tight']=iv([value,value]);r['trace'][-1]['enclosure']=iv([value,value]);r['result']=result_for([F(value),F(value)],F(*r['request']['epsilon']))
        mutate('dependency-zero-shortcut','dependency-zero',lambda r:shortcut(r,0))
        mutate('dependency-one-shortcut','dependency-one',lambda r:shortcut(r,1))
        mutate('invented-domain-completion','dependency-domain',lambda r:r.__setitem__('result',result_for([F(1),F(2)],F(1,16))))
        mutate('changed-box','round-positive',lambda r:r['request']['variables'][0].__setitem__('interval',iv([F(1,4),F(2,3)])))
        mutate('changed-history','nested',lambda r:r['request'].__setitem__('history',['other-history']))
        mutate('changed-grid','round-positive',lambda r:r['request'].__setitem__('grid',16))
        mutate('changed-expression','small-positive',lambda r:r['request']['nodes'][0].__setitem__('value',rat(F(1,32))))
        mutate('wrong-profile','exact-zero',lambda r:r.__setitem__('profile','adva.research.linear-system.v0'))
        c.check(len(controls)==18,'declared-evidence-controls')
        for name,e,r in controls:c.call('evidence/'+name,e,r,'InvalidEvidence')
        # Exact endpoint witnesses show why inward rounding is unsafe. This does
        # not describe dependency shortcuts, which can be mathematically sound.
        rounding=[]
        for name,e,r in controls[:4]:
            original=vals(e['variables'][0]['interval']);submitted=vals(r['result']['interval']);witness=original[0] if name.endswith('lower') else original[1]
            c.check(not submitted[0]<=witness<=submitted[1],'inward-rule-excludes-legal-endpoint')
            rounding.append({'case':name,'legal_endpoint':rat(witness),'submitted_interval':iv(submitted)})
        c.save(out/'rounding-counterexamples.json',rounding)
        invalid=[]
        def bad(label,key,edit):
            e=copy.deepcopy(cases[key]);edit(e);invalid.append((label,e))
        bad('reversed-box','round-positive',lambda e:e['variables'][0]['interval'].reverse())
        bad('missing-variable','round-positive',lambda e:e.__setitem__('variables',[]))
        bad('unknown-operation','small-positive',lambda e:e['nodes'][0].__setitem__('op','sqrt'))
        bad('zero-grid','round-positive',lambda e:e.__setitem__('grid',0))
        bad('float-endpoint','round-positive',lambda e:e['variables'][0]['interval'][0].__setitem__(0,1.0))
        bad('zero-denominator','round-positive',lambda e:e['variables'][0]['interval'][0].__setitem__(1,0))
        bad('zero-epsilon','small-positive',lambda e:e.__setitem__('epsilon',[0,1]))
        bad('boolean-reference','exact-zero',lambda e:e['nodes'][1].__setitem__('left',False))
        bad('history-capacity','small-positive',lambda e:e.__setitem__('history',['a','b','c','d','e']))
        bad('node-cap','small-positive',lambda e:e.__setitem__('nodes',[const(0) for _ in range(8)]))
        for name,e in invalid:c.call('context/'+name,e,receipts['round-positive'],'InvalidContext')
        c.check(len(c.runs)==53,'complete-case-coverage')
    except Exception as exc:failure={'type':type(exc).__name__,'message':str(exc)}
    finally:signal.setitimer(signal.ITIMER_REAL,0)
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'run.py',ROOT/'receive.py',ROOT/'contract.json')}
    report={'profile':PROFILE,'status':'Passed' if failure is None else 'Failed','failure':failure,'calls':len(c.runs),'assertions':c.assertions,'receiver_work_units':c.work,'producer_work_units':PRODUCER_WORK,'point_work_units':POINT_WORK,'search_candidates':0,'wall_seconds':time.perf_counter()-c.started,'phases':c.phases,'runs':c.runs,'source_sha256':hashes,'python_version':sys.version,'child_peak_rss_kib':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,'supervisor_peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'native_authority':False,'new_native_vocabulary':[],'cost_scope':'Instrumented phases omit some copying and setup; campaign wall includes bookkeeping. Final report/archive/research/review/network separate and not fully measured; no speedup claim.'}
    put(out/'execution.json',report);print(json.dumps({k:v for k,v in report.items() if k not in ('runs','source_sha256')},sort_keys=True));return 0 if failure is None else 1


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);raise SystemExit(main(p.parse_args().output.resolve()))
