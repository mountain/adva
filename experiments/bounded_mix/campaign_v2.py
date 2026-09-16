"""One v2 continuation under its own frozen contract; no old run is resumed."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import traceback

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from experiments.bounded_mix.runtime_v2 import Trial, profile
from experiments.bounded_mix.preflight import freeze
from experiments.bounded_mix.receive import wire, receive
from experiments.bounded_mix.fixtures import interpreters, controls
from experiments.bounded_mix.author import R
from experiments.bounded_self_compiler.language import TARGET, decode_target, node, integer, canonical

V2='adva.data-machine.program.research.v2'


def select(program,version):
    """The wire omits schema. Profile choice changes no instruction or operand."""
    assert program['schema'] in (TARGET,V2)
    return {**deepcopy(program),'schema':version}


def encoded(program):return wire(select(program,TARGET))
def decoded(data):return select(decode_target(data),V2)
def sha(value):return hashlib.sha256(canonical(value)).hexdigest()


def receipt(q,s,target):
    r=receive(select(q,TARGET),s,select(target,TARGET))
    return {**r,'native_schema':V2,'native_source_sha256':sha(q),
            'native_residual_sha256':sha(target),'native_profile':profile(),
            'codec_boundary':'Version selection only; normalized correspondence hashes use v1 schema.'}


def run(t,preflight,v1):
    freeze(t)
    contract=json.loads((ROOT/'experiments/bounded_mix/contract-v1.json').read_text())
    for entry in (contract['supersedes'],contract['capacity_evidence']):
        assert hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest()==entry['sha256']
    t.save('contract-v1.json',contract)
    t.save('native-v2-source.rs',(ROOT/'crates/adva-witness/src/data_machine_v2.rs').read_bytes())
    t.save('native-v2-cli.rs',(ROOT/'crates/adva-witness/src/bin/support/data_machine_v2_cli.rs').read_bytes())
    t.save('native-bin-entry.rs',(ROOT/'crates/adva-witness/src/bin/adva.rs').read_bytes())
    t.save('native-lib-entry.rs',(ROOT/'crates/adva-witness/src/lib.rs').read_bytes())
    preflight=Path(preflight);v1=Path(v1)
    assert json.loads((preflight/'cost.json').read_text())['status']=='Passed'
    assert json.loads((v1/'cost.json').read_text())['status']=='PassedWithThirdCapacityObstruction'
    mix=select(json.loads((preflight/'mix.program.adva').read_text()),V2)
    t.save('mix.program.adva',mix)
    records=[];pairs=[];compilers=[]

    def specialize(label,q,s):
        r=t.native(label,mix,node(42,[encoded(q),s]))
        assert r['status']=='Returned',(label,r['state']['phase'])
        target=decoded(r['state']['phase']['value'])
        t.save(label+'.target.adva',target);t.save(label+'.receipt.json',receipt(q,s,target))
        records.append(label)
        return target

    cogen=specialize('third-generation',mix,encoded(mix))
    assert len(cogen['code'])==3959
    received=t.native('third-reception',mix,node(42,[encoded(mix),encoded(mix)]),quantum=0,
                      check=t.out/'third-generation.run.adva')
    t.native('third-admission',cogen,integer(0),fuel=0,quantum=0)
    replayed=received['verified_steps']
    for name,old_interpreter,programs in interpreters():
        interpreter=select(old_interpreter,V2)
        compiler=specialize(name+'-direct-compiler',mix,encoded(interpreter))
        generated=t.native(name+'-generated-compiler',cogen,encoded(interpreter))
        assert generated['status']=='Returned'
        via_third=decoded(generated['state']['phase']['value'])
        assert canonical(via_third)==canonical(compiler)
        t.save(name+'-generated-compiler.target.adva',via_third)
        t.save(name+'-generated-compiler.receipt.json',receipt(mix,encoded(interpreter),via_third))
        received=t.native(name+'-compiler-reception',cogen,encoded(interpreter),quantum=0,
                          check=t.out/(name+'-generated-compiler.run.adva'))
        replayed+=received['verified_steps']
        compilers.append({'interpreter':name,'compiler_instructions':len(compiler['code']),
                          'direct_and_cogen_equal':True,'sha256':sha(compiler)})
        for i,p in enumerate(programs):
            label=f'{name}-{i}'
            residual=specialize(label+'-direct-residual',interpreter,p)
            r=t.native(label+'-compiled-residual',via_third,p)
            assert r['status']=='Returned'
            compiled=decoded(r['state']['phase']['value'])
            assert canonical(compiled)==canonical(residual)
            t.save(label+'-compiled-residual.target.adva',compiled)
            t.save(label+'-compiled-residual.receipt.json',receipt(interpreter,p,compiled))
            for x in (7,2**63-1):
                direct=t.native(label+f'-direct-{x}',interpreter,node(42,[p,integer(x)]))
                result=t.native(label+f'-residual-{x}',compiled,integer(x))
                assert direct['status'] in ('Returned','Rejected')
                assert direct['state']['phase']==result['state']['phase']
                pairs.append({'case':label,'dynamic':x,'phase':direct['state']['phase'],
                              'source_steps':direct['state']['spent'],'residual_steps':result['state']['spent']})

    # Check continuation on a small compilation, without paying the large cogen
    # construction again. A v1 checkpoint must fail even for matching opcodes.
    _,old_q,s,d=controls()[0]
    q=select(old_q,V2);bundle=node(42,[encoded(q),s])
    prefix=t.native('prefix',mix,bundle,quantum=17)
    assert prefix['status']=='Suspended'
    resumed=t.native('resumed',mix,bundle,resume=t.out/'prefix.run.adva')
    assert resumed['status']=='Returned'
    receive(old_q,s,decode_target(resumed['state']['phase']['value']))
    t.native('changed-fuel',mix,bundle,fuel=199999,resume=t.out/'prefix.run.adva',refuse=True)
    foreign=t.save('foreign-v1-checkpoint.adva',(v1/'prefix.run.adva').read_bytes())
    t.native('foreign-profile',mix,bundle,quantum=0,check=foreign,refuse=True)

    # Mutate mix's actual emission instruction, not a host encoder or fixture.
    mutant=deepcopy(mix)
    candidates=[i for i in mutant['code'] if i=={'op':'constant','dst':R['number'],'value':42}]
    assert len(candidates)==1
    candidates[0]['value']=43
    bad=t.native('mutated-mix',mutant,bundle)
    assert bad['status']=='Returned'
    bad_target=decoded(bad['state']['phase']['value'])
    try:receipt(q,s,bad_target)
    except ValueError:pass
    else:raise AssertionError('mutated mix escaped correspondence checking')
    bad_run=t.native('mutated-residual',bad_target,d)
    assert bad_run['state']['phase']['value']==node(43,[s,d])
    zero=t.native('zero-fuel',mix,bundle,fuel=0)
    assert zero['status']=='FuelExhausted'
    malformed=t.native('malformed-tag',mix,node(41,[encoded(q),s]))
    assert malformed['status']=='Rejected'
    t.native('new-arity-cap',mix,node(0,[integer(0)]*4097),fuel=0,quantum=0,refuse=True)
    assert len(t.calls)==48
    summary={'status':'Passed','profile':profile(),'mix_instructions':len(mix['code']),
             'cogen_instructions':len(cogen['code']),'cogen_registers':len(cogen['registers']),
             'cogen_generated_admitted_and_executed':True,'compilers':compilers,
             'first_second_code_equalities':5,'second_third_code_equalities':2,
             'terminal_pairs':pairs,'native_replayed_steps':replayed+17,
             'native_calls':len(t.calls),'direct_receipts':records,
             'controls':['actual mix source mutation changes output and fails correspondence',
                         'mutated residual changes returned pair tag','17-step continuation received',
                         'changed fuel refused','v1 checkpoint refused','zero fuel exhausted',
                         'malformed input tag rejected','4097 node arity refused'],
             'residual':['conservative input binding only','no static arithmetic folding or interpreter elimination',
                         'finite source boundary and capacities','external source admission, loader and structural receipts',
                         'no unrestricted correctness, speedup, native identity or stable API promotion']}
    t.save('summary.json',summary)
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--binary',required=True);p.add_argument('--output',required=True)
    p.add_argument('--preflight',required=True);p.add_argument('--v1-evidence',required=True)
    a=p.parse_args();t=Trial(a.binary,a.output);status='Failed';extra={}
    try:extra={'summary':run(t,a.preflight,a.v1_evidence)};status='Passed'
    except Exception as error:extra={'error':str(error),'traceback':traceback.format_exc()}
    finally:t.finish(status,extra);print(json.dumps({'status':status,**extra}))
    if status!='Passed':raise SystemExit(1)
