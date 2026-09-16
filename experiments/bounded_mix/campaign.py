"""One finite v1 binding/self-application campaign, including capacity refusal."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys
import traceback

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from experiments.bounded_mix.runtime import Trial
from experiments.bounded_mix.preflight import freeze
from experiments.bounded_mix.receive import wire, binding, receive
from experiments.bounded_mix.fixtures import interpreters, controls
from experiments.bounded_self_compiler.language import decode_target, node, integer, canonical


def run(t,preflight):
    freeze(t)
    preflight=Path(preflight)
    assert json.loads((preflight/'cost.json').read_text())['status']=='Passed'
    mix=json.loads((preflight/'mix.program.adva').read_text())
    assert mix==json.loads((ROOT/'programs/bounded-mix/mix.seed.adva').read_text())
    t.save('mix.program.adva',mix)
    receipts=[];pairs=[];compilers={}

    def specialize(label,q,s,compiler=mix):
        result=t.native(label,compiler,node(42,[wire(q),s]))
        assert result['status']=='Returned',(label,result['state']['phase'])
        target=decode_target(result['state']['phase']['value'])
        receipt=receive(q,s,target);t.save(label+'.receipt.json',receipt)
        t.save(label+'.target.adva',target);receipts.append(label)
        return target

    for name,interpreter,programs in interpreters():
        t.native(name+'-source-admission',interpreter,integer(0),fuel=0,quantum=0)
        compiler=specialize(name+'-compiler',mix,wire(interpreter))
        compilers[name]=compiler
        t.native(name+'-compiler-admission',compiler,integer(0),fuel=0,quantum=0)
        for index,p in enumerate(programs):
            label=f'{name}-{index}'
            residual=specialize(label+'-first',interpreter,p)
            generated=t.native(label+'-second',compiler,p)
            assert generated['status']=='Returned'
            second=decode_target(generated['state']['phase']['value'])
            assert canonical(second)==canonical(residual)
            t.save(label+'-second.target.adva',second)
            t.save(label+'-second.receipt.json',receive(interpreter,p,second))
            receipts.append(label+'-second')
            for dynamic in (7,-3,2**63-1):
                d=integer(dynamic)
                direct=t.native(label+f'-direct-{dynamic}',interpreter,node(42,[p,d]))
                executed=t.native(label+f'-residual-{dynamic}',residual,d)
                assert direct['status'] in ('Returned','Rejected')
                assert direct['state']['phase']==executed['state']['phase']
                pairs.append({'name':label,'dynamic':dynamic,'phase':direct['state']['phase'],
                              'source_steps':direct['state']['spent'],'residual_steps':executed['state']['spent']})
    for name,q,s,d in controls():
        t.native(name+'-source-admission',q,integer(0),fuel=0,quantum=0)
        residual=specialize(name+'-binding',q,s)
        direct=t.native(name+'-direct',q,node(42,[s,d]))
        result=t.native(name+'-residual',residual,d)
        assert direct['state']['phase']==result['state']['phase']
        pairs.append({'name':name,'phase':direct['state']['phase'],
                      'source_steps':direct['state']['spent'],'residual_steps':result['state']['spent']})

    # Source mutation must change generated target bytes and observed behavior.
    interpreter=interpreters()[0][1]
    mutant=deepcopy(interpreter)
    next(i for i in mutant['code'] if i['op']=='multiply')['op']='add'
    p=interpreters()[0][2][0]
    altered=specialize('changed-source',mutant,p)
    observed=t.native('changed-source-execution',altered,integer(7))
    assert observed['state']['phase']['value']==integer(12)
    original=json.loads((t.out/'affine-0-first.target.adva').read_text())
    assert altered!=original

    # Executed checkpoint/zero-fuel/malformed-input controls are separately charged.
    q,s,d=controls()[0][1:]
    bundle=node(42,[wire(q),s])
    prefix=t.native('prefix',mix,bundle,quantum=17)
    resumed=t.native('resumed',mix,bundle,resume=t.out/'prefix.run.adva')
    whole=json.loads((t.out/'repeated-input-binding.run.adva').read_text())
    assert prefix['status']=='Suspended' and resumed['state']==whole['state'] and resumed['trace']==whole['trace']
    t.native('changed-fuel',mix,bundle,fuel=199999,resume=t.out/'prefix.run.adva',refuse=True)
    zero=t.native('zero-fuel',mix,bundle,fuel=0)
    assert zero['status']=='FuelExhausted'
    malformed=t.native('malformed-tag',mix,node(41,[wire(q),s]))
    assert malformed['status']=='Rejected' and malformed['state']['phase']['reason']=='mix input tag'
    deep=integer(0)
    for _ in range(12):deep=node(0,[deep])
    deep_result=t.native('deep-literal',mix,node(42,[wire(q),deep]))
    assert deep_result['status']=='Rejected' and deep_result['state']['phase']['reason']=='mix static literal depth'

    # A v1 program may construct code larger than v1 can admit. Keep the actual
    # refusal, and never relabel the independently predicted code as native output.
    expected,offset=binding(mix,wire(mix))
    t.save('third-predicted.target.adva',expected)
    third=t.native('third-generation',mix,node(42,[wire(mix),wire(mix)]))
    obstruction={'predicted_instructions':len(expected['code']),'prefix':offset,
                 'native_status':third['status'],'phase':third['state']['phase'],
                 'native_steps':third['state']['spent'],'executed_compiler_generator':False}
    if third['status']=='Returned':
        candidate=decode_target(third['state']['phase']['value'])
        assert canonical(candidate)==canonical(expected)
        t.native('third-admission',candidate,integer(0),fuel=0,quantum=0,refuse=True)
    else:
        assert third['status']=='Rejected'
        assert 'arity' in third['state']['phase']['reason']
    t.save('third-capacity-obstruction.json',obstruction)
    summary={'status':'PassedWithThirdCapacityObstruction','mix_instructions':len(mix['code']),
             'first_second_code_equalities':5,'terminal_pairs':pairs,'structural_receipts':receipts,
             'compiler_instructions':{n:len(p['code']) for n,p in compilers.items()},'third':obstruction,
             'native_calls':len(t.calls),
             'residual':['conservative input binding only','no static computation elimination',
                         'third compiler generator not executed in v1','bounded observations, not unrestricted laws']}
    t.save('summary.json',summary)
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--binary',required=True);p.add_argument('--output',required=True)
    p.add_argument('--preflight',required=True)
    a=p.parse_args();t=Trial(a.binary,a.output);status='Failed';extra={}
    try:extra={'summary':run(t,a.preflight)};status='PassedWithThirdCapacityObstruction'
    except Exception as error:extra={'error':str(error),'traceback':traceback.format_exc()}
    finally:t.finish(status,extra);print(json.dumps({'status':status,**extra}))
    if status=='Failed':raise SystemExit(1)
