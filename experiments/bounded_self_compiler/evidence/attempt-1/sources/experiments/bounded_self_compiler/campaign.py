"""The one frozen finite self-compiler campaign; no automatic retry."""
import argparse
from copy import deepcopy
import json
import traceback
from language import canonical, decode_target, encode_source, seed_compile, integer, node, prim, seq
from checker import receive_compilation
from fixtures import cases, program
from reference import Budget, receive, source_execute, initial, transition, normalize_data
from runtime import ROOT, HERE, Trial, profile


def must_refuse(function):
    try: function()
    except (ValueError,AssertionError): return
    raise AssertionError('negative control was accepted')


def run(t):
    budget=Budget()
    s=json.loads((ROOT/'programs/bounded-self-compiler/compiler.source.adva').read_text())
    data=encode_source(s)
    c1=seed_compile(s)
    assert c1==json.loads((ROOT/'programs/bounded-self-compiler/compiler.seed.adva').read_text())
    t.save('compiler.source.adva',s);t.save('compiler.c1.adva',c1)
    receipts=[]
    def checked(name,src,target):
        receipt=receive_compilation(src,target,budget)
        t.save(name+'.receipt.json',receipt);receipts.append(name)
        return receipt
    checked('c1',s,c1)
    one=t.native('self-c1',c1,data)
    assert one['status']=='Returned'
    c2=decode_target(one['state']['phase']['value'])
    checked('c2',s,c2);t.save('compiler.c2.adva',c2)
    two=t.native('self-c2',c2,data)
    assert two['status']=='Returned'
    c3=decode_target(two['state']['phase']['value'])
    checked('c3',s,c3);t.save('compiler.c3.adva',c3)
    assert canonical(c1)==canonical(c2)==canonical(c3)
    native_replayed=0
    for name,compiler in [('self-c1',c1),('self-c2',c2)]:
        check=t.native(name+'-checked',compiler,data,quantum=0,check=t.out/(name+'.run.adva'))
        native_replayed+=check['verified_steps']
    fixture_results=[];received_edges=0;oracle_events=0
    for name,src,arg in cases():
        t.save(name+'.source.adva',src)
        targets=[]
        for stage,compiler in [('c1',c1),('c2',c2)]:
            result=t.native(name+'-'+stage,compiler,encode_source(src))
            assert result['status']=='Returned'
            target=decode_target(result['state']['phase']['value'])
            receipt=checked(name+'-'+stage,src,target)
            targets.append(target)
        assert targets[0]==targets[1]
        target=targets[1]
        result=t.native(name+'-execute',target,arg,fuel=2048)
        receive(result,target,arg,2048,profile(),budget)
        received_edges+=result['state']['spent']
        expected,events=source_execute(src,arg,budget)
        assert result['state']['phase']==expected,(name,result['state']['phase'],expected)
        state=initial(target);actual=[]
        for edge in result['trace']:
            pc=state['pc'];state=transition(target,normalize_data(arg),state,budget)
            if str(pc) in receipt['primitive_paths']:
                actual.append({'path':receipt['primitive_paths'][str(pc)],
                               'registers':deepcopy(state['registers']),'phase':deepcopy(state['phase'])})
        assert actual==events,name
        oracle_events+=len(events)
        fixture_results.append({'name':name,'phase':expected,'target_steps':result['state']['spent'],
                                'primitive_events':len(events),'target_instructions':len(target['code'])})
    # Independent direct source execution of the compiler on a small program.
    small=cases()[0][1]
    expected,events=source_execute(s,encode_source(small),budget)
    native=json.loads((t.out/'literal-c1.run.adva').read_text())
    assert expected==native['state']['phase']
    t.save('compiler-source-oracle.json',{'phase':expected,'primitive_events':len(events)})
    # Source mutation changes actual generated code, defeating an opaque self-copy.
    mutant=deepcopy(s)
    def mutate(b):
        if b['kind']=='prim' and b['instruction']=={'op':'node','tag':16,'fields':[12,13,14],'dst':9}:
            b['instruction']['tag']=15;return True
        for key in ('items','yes','no','body'):
            if key in b:
                children=b[key] if key=='items' else [b[key]]
                for child in children:
                    if mutate(child): return True
        return False
    assert mutate(mutant)
    m=t.native('changed-source',c2,encode_source(mutant))
    changed=decode_target(m['state']['phase']['value'])
    assert changed!=c2
    checked('changed-source',mutant,changed)
    t.save('mutant.source.adva',mutant)
    mutant_result=t.native('mutant-execute',changed,encode_source(cases()[2][1]))
    assert mutant_result['status']=='Returned'
    must_refuse(lambda:decode_target(mutant_result['state']['phase']['value']))
    must_refuse(lambda:receive_compilation(s,changed,budget))
    bad=deepcopy(c2)
    first=next(i for i in bad['code'] if i['op']=='branch');first['yes']+=1
    t.save('mutated-target.adva',bad)
    must_refuse(lambda:receive_compilation(s,bad,budget))
    # Checkpoint lineage and negative receiving context controls.
    prefix=t.native('prefix',c2,data,quantum=17)
    assert prefix['status']=='Suspended'
    resumed=t.native('resumed',c2,data,resume=t.out/'prefix.run.adva')
    native_replayed+=17
    assert resumed['state']==two['state'] and resumed['trace']==two['trace']
    t.native('changed-fuel',c2,data,fuel=199999,resume=t.out/'prefix.run.adva',refuse=True)
    t.native('changed-input',c2,integer(0),resume=t.out/'prefix.run.adva',refuse=True)
    altered=deepcopy(prefix);altered['trace'][0]['state_digest']='00'
    path=t.save('altered-checkpoint.adva',altered)
    t.native('changed-trace',c2,data,resume=path,refuse=True)
    zero=t.native('zero-fuel',c2,data,fuel=0)
    assert zero['status']=='FuelExhausted' and zero['state']['spent']==0
    loop={'schema':c2['schema'],'name':'bounded-loop','registers':c2['registers'],
          'code':[{'op':'jump','target':0}]}
    exhausted=t.native('loop-fuel',loop,integer(0),fuel=23)
    assert exhausted['status']=='FuelExhausted' and exhausted['state']['spent']==23
    malformed=node(240,[data['fields'][0],data['fields'][1],node(99,[])])
    rejected=t.native('malformed-source',c2,malformed)
    assert rejected['status']=='Rejected'
    must_refuse(lambda:encode_source({**s,'body':{'kind':'unknown'}}))
    bad=deepcopy(c2);bad['code'][0]={'op':'input','dst':15}
    t.native('static-type',bad,data,fuel=0,refuse=True)
    # Invoke the actual CLI against an existing output; retain its refusal.
    import subprocess
    import time
    before=(t.out/'zero-fuel.run.adva').read_bytes();started=time.monotonic()
    command=[str(t.binary),'data-run-v1',str(t.out/'zero-fuel.program.adva'),'--input',
        str(t.out/'zero-fuel.input.json'),'--fuel','0','--quantum','0','--output',str(t.out/'zero-fuel.run.adva')]
    assert len(t.calls)<48
    r=subprocess.run(command,capture_output=True,timeout=t.remaining())
    t.save('no-clobber.stdout.txt',r.stdout);t.save('no-clobber.stderr.txt',r.stderr)
    assert r.returncode!=0 and (t.out/'zero-fuel.run.adva').read_bytes()==before
    t.calls.append({'name':'no-clobber','exit_code':r.returncode,'status':'Refused','steps':0,
                    'sha256':None,'wall_seconds':time.monotonic()-started})
    summary={'status':'Passed','profile':profile(),'stages_equal':True,
        'compiler_instructions':len(c1['code']),'compiler_registers':len(c1['registers']),
        'self_compilation_steps':[one['state']['spent'],two['state']['spent']],
        'source_compiler_oracle_primitive_events':len(events),
        'native_replayed_steps':native_replayed,'independent_fixture_edges':received_edges,
        'fixture_primitive_events':oracle_events,'reference_work_units':budget.steps,
        'fixtures':fixture_results,'receipts':receipts,'native_calls':len(t.calls),
        'controls':['source mutation changes target','original-source mismatch refused','target branch mutation refused',
            '17-step resume identical','changed fuel/input/trace refused','zero/loop fuel exhausted',
            'malformed source rejected','static type rejected','no-clobber refused'],
        'residual':['bounded structured research subset','external Python seed and structural receiver',
            'Rust generic VM and wire codec remain trusted imports','self-applicable specializer not implemented',
            'no second/third Futamura projection, speedup, native identity or PSC0 promotion']}
    t.save('summary.json',summary)
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--binary',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();t=Trial(a.binary,a.output);status='Failed';extra={}
    try: extra={'summary':run(t)};status='Passed'
    except Exception as e: extra={'error':str(e),'traceback':traceback.format_exc()}
    finally: print(json.dumps(t.finish(status,extra)))
    if status!='Passed':raise SystemExit(1)
