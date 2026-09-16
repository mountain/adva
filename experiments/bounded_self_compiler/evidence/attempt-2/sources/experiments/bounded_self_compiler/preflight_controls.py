"""Finite engineering receiving preflight for the declared fixture family."""
import argparse
import json
import traceback
from language import seed_compile, encode_source, decode_target
from checker import receive_compilation
from reference import Budget, receive, source_execute
from runtime import ROOT, Trial, profile
from fixtures import cases

p=argparse.ArgumentParser();p.add_argument('--binary',required=True);p.add_argument('--output',required=True)
a=p.parse_args();t=Trial(a.binary,a.output,preflight=True);status='Failed';extra={}
try:
    budget=Budget()
    s=json.loads((ROOT/'programs/bounded-self-compiler/compiler.source.adva').read_text())
    c=seed_compile(s)
    rows=[]
    for name,src,data in cases():
        r=t.native(name+'-compile',c,encode_source(src))
        assert r['status']=='Returned'
        target=decode_target(r['state']['phase']['value'])
        receipt=receive_compilation(src,target,budget)
        t.save(name+'.receipt.json',receipt)
        r=t.native(name+'-run',target,data,fuel=2048)
        receive(r,target,data,2048,profile(),budget)
        phase,events=source_execute(src,data,budget)
        assert r['state']['phase']==phase
        rows.append({'name':name,'phase':phase,'primitive_events':len(events)})
    phase,events=source_execute(s,encode_source(cases()[0][1]),budget)
    assert phase==json.loads((t.out/'literal-compile.run.adva').read_text())['state']['phase']
    extra={'rows':rows,'compiler_source_oracle_events':len(events),'reference_work_units':budget.steps}
    status='Passed'
except Exception as e:extra={'error':str(e),'traceback':traceback.format_exc()}
finally:print(json.dumps(t.finish(status,extra)))
if status!='Passed':raise SystemExit(1)
