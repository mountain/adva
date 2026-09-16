"""One mutation-control preflight explicitly allocated by contract-v1."""
import argparse
from copy import deepcopy
import json
import traceback
from language import seed_compile,encode_source,decode_target
from checker import receive_compilation
from reference import Budget
from runtime import ROOT,Trial
from fixtures import cases
from campaign import must_refuse

p=argparse.ArgumentParser();p.add_argument('--binary',required=True);p.add_argument('--output',required=True)
a=p.parse_args();t=Trial(a.binary,a.output,preflight=True);status='Failed';extra={}
try:
    s=json.loads((ROOT/'programs/bounded-self-compiler/compiler.source.adva').read_text())
    mutant=deepcopy(s)
    pending=[mutant['body']];found=False
    while pending:
        b=pending.pop()
        if b['kind']=='prim' and b['instruction']=={'op':'node','tag':16,'fields':[12,13,14],'dst':9}:
            b['instruction']['tag']=15;found=True;break
        if b['kind']=='seq':pending.extend(reversed(b['items']))
        elif b['kind']=='if':pending.extend([b['no'],b['yes']])
        elif b['kind']=='while':pending.append(b['body'])
    assert found
    t.save('mutant.source.adva',mutant)
    result=t.native('changed-source',seed_compile(s),encode_source(mutant))
    changed=decode_target(result['state']['phase']['value'])
    receive_compilation(mutant,changed,Budget())
    must_refuse(lambda:receive_compilation(s,changed,Budget()))
    result=t.native('changed-compiler-execute',changed,encode_source(cases()[2][1]))
    assert result['status']=='Returned'
    must_refuse(lambda:decode_target(result['state']['phase']['value']))
    extra={'source_mutation_changed_compiler':True,'compiler_mutation_changed_behavior':True,
           'original_source_correspondence_refused':True,'malformed_target_decoding_refused':True}
    status='Passed'
except Exception as e:extra={'error':str(e),'traceback':traceback.format_exc()}
finally:print(json.dumps(t.finish(status,extra)))
if status!='Passed':raise SystemExit(1)
