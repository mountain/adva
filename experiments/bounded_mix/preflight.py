"""One explicitly bounded preflight: compile mix with the received Adva compiler."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import traceback

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
# The older independently received checker uses local sibling imports.
sys.path.append(str(ROOT/'experiments/bounded_self_compiler'))
from experiments.bounded_mix.runtime import Trial
from experiments.bounded_mix.receive import wire, binding, receive
from experiments.bounded_mix.fixtures import controls
from experiments.bounded_self_compiler.language import decode_target, encode_source, canonical, node
from experiments.bounded_self_compiler.checker import receive_compilation
from experiments.bounded_self_compiler.reference import Budget


def freeze(t):
    paths=sorted((ROOT/'experiments/bounded_mix').glob('*.py'))+[
        ROOT/'experiments/bounded_mix/contract.json',
        ROOT/'programs/bounded-mix/mix.source.adva',ROOT/'programs/bounded-mix/mix.seed.adva',
        ROOT/'crates/adva-witness/src/data_machine_v1.rs',ROOT/'Cargo.lock']
    manifest={}
    for i,p in enumerate(paths):
        raw=p.read_bytes();t.save(f'source-{i:02d}.bin',raw)
        manifest[str(p.relative_to(ROOT))]={'sha256':hashlib.sha256(raw).hexdigest(),'snapshot':f'source-{i:02d}.bin'}
    t.save('source-manifest.json',manifest)


def run(t):
    freeze(t)
    source=json.loads((ROOT/'programs/bounded-mix/mix.source.adva').read_text())
    compiler=json.loads((ROOT/'programs/bounded-self-compiler/compiler.seed.adva').read_text())
    compiled=t.native('compile-mix',compiler,encode_source(source))
    assert compiled['status']=='Returned'
    mix=decode_target(compiled['state']['phase']['value'])
    assert canonical(mix)==canonical(json.loads((ROOT/'programs/bounded-mix/mix.seed.adva').read_text()))
    t.save('mix.program.adva',mix)
    t.save('mix.compilation-receipt.json',receive_compilation(source,mix,Budget()))
    t.native('receive-mix-compilation',compiler,encode_source(source),quantum=0,check=t.out/'compile-mix.run.adva')
    _,q,s,d=controls()[0]
    mixed=t.native('mix-literal',mix,node(42,[wire(q),s]))
    assert mixed['status']=='Returned'
    residual=decode_target(mixed['state']['phase']['value'])
    t.save('literal.binding-receipt.json',receive(q,s,residual))
    t.native('receive-mix-literal',mix,node(42,[wire(q),s]),quantum=0,check=t.out/'mix-literal.run.adva')
    direct=t.native('source',q,node(42,[s,d]))
    result=t.native('residual',residual,d)
    assert direct['state']['phase']==result['state']['phase']
    expected,offset=binding(mix,wire(mix))
    capacity={'third_projection_predicted_instructions':len(expected['code']),
              'v1_instruction_limit':2048,'literal_prefix_instructions':offset,
              'status':'Fits' if len(expected['code'])<=2048 else 'CapacityObstruction',
              'boundary':'Independent construction only; not yet a native third-projection execution.'}
    t.save('capacity-preflight.json',capacity)
    return {'mix_instructions':len(mix['code']),'mix_registers':len(mix['registers']),
            'compile_mix_steps':compiled['state']['spent'],'literal_mix_steps':mixed['state']['spent'],
            'capacity':capacity}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--binary',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();t=Trial(a.binary,a.output,preflight=True);status='Failed';extra={}
    try:extra=run(t);status='Passed'
    except Exception as error:extra={'error':str(error),'traceback':traceback.format_exc()}
    finally:t.finish(status,extra);print(json.dumps({'status':status,**extra}))
    if status!='Passed':raise SystemExit(1)
