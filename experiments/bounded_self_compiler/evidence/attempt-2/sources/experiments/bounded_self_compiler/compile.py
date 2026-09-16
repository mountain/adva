"""A reusable finite compilation command for the declared structured subset."""
import argparse
import json
from pathlib import Path
import traceback
from checker import receive_compilation
from language import decode_target, encode_source, integer
from reference import Budget
from runtime import Trial, sha


def read(path):
    path=Path(path)
    if not path.is_file() or path.stat().st_size>524288:
        raise ValueError('source/compiler file exceeds the finite input boundary')
    def pairs(items):
        result={}
        for k,v in items:
            if k in result:raise ValueError('duplicate JSON key')
            result[k]=v
        return result
    return json.loads(path.read_text(),object_pairs_hook=pairs)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source');p.add_argument('--compiler',required=True)
    p.add_argument('--binary',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();t=Trial(a.binary,a.output,preflight=True);status='Failed';extra={}
    try:
        s=read(a.source);compiler=read(a.compiler)
        t.save('source.adva',s)
        t.save('inputs.json',{'source_file_sha256':sha(a.source),'compiler_file_sha256':sha(a.compiler),
                             'fuel':200000,'wall_seconds':180,'cpu_seconds':160,
                             'address_space_bytes':1024**3,'artifact_bytes':96*1024**2})
        r=t.native('compilation',compiler,encode_source(s))
        if r['status']!='Returned':raise ValueError('compilation did not return: '+r['status'])
        target=decode_target(r['state']['phase']['value'])
        receipt=receive_compilation(s,target,Budget())
        admission=t.native('target-admission',target,integer(0),fuel=0,quantum=0)
        assert admission['status']=='FuelExhausted' and admission['state']['spent']==0
        t.save('program.adva',target);t.save('compilation-receipt.json',receipt)
        extra={'target':str(t.out/'program.adva'),'compilation_steps':r['state']['spent'],
               'target_instructions':len(target['code']),'target_admission':'Rust, zero execution fuel'}
        status='Passed'
    except Exception as e:extra={'error':str(e),'traceback':traceback.format_exc()}
    finally:print(json.dumps(t.finish(status,extra)))
    if status!='Passed':raise SystemExit(1)

if __name__=='__main__':main()
