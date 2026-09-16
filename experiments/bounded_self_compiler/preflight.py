"""One retained, finite receiving preflight; caller allocates a fresh numbered path."""
import argparse
import json
import traceback
from language import decode_target, encode_source, seed_compile
from checker import receive_compilation
from reference import Budget
from runtime import Trial, ROOT, sha

p=argparse.ArgumentParser();p.add_argument('--binary',required=True);p.add_argument('--output',required=True)
a=p.parse_args();t=Trial(a.binary,a.output,preflight=True)
status='Failed'; extra={}
try:
    s=json.loads((ROOT/'programs/bounded-self-compiler/compiler.source.adva').read_text())
    seed=seed_compile(s);data=encode_source(s)
    t.save('source.adva',s)
    t.save('contract.json',json.loads((ROOT/'experiments/bounded_self_compiler/contract.json').read_text()))
    t.save('source-digests.json',{str(p.relative_to(ROOT)):sha(p) for pattern in
        ['experiments/bounded_self_compiler/*.py','crates/adva-witness/src/data_machine_v1.rs',
         'crates/adva-witness/src/bin/support/data_machine_v1_cli.rs'] for p in ROOT.glob(pattern)})
    result=t.native('self',seed,data)
    assert result['status']=='Returned',result['state']['phase']
    target=decode_target(result['state']['phase']['value'])
    assert target==seed
    receipt=receive_compilation(s,target,Budget())
    t.save('receipt.json',receipt)
    reception=t.native('check',seed,data,quantum=0,check=t.out/'self.run.adva')
    assert reception['verified_steps']==result['state']['spent']
    extra={'compiler_instructions':len(seed['code']),'compiler_steps':result['state']['spent'],
           'canonical_stage_equality':True,'received_blocks':len(receipt['blocks'])}
    status='Passed'
except Exception as e:
    extra={'error':str(e),'traceback':traceback.format_exc()}
finally:
    print(json.dumps(t.finish(status,extra)))
if status!='Passed': raise SystemExit(1)
