"""Re-receive two frozen self compilations using the current native binary."""
import argparse
import json
from pathlib import Path
import subprocess
from regression import read_archive,bound_sources
from runtime import Trial

p=argparse.ArgumentParser();p.add_argument('--binary',required=True);p.add_argument('--output',required=True)
a=p.parse_args();t=Trial(a.binary,a.output,preflight=True);bound_sources();files=read_archive('primary')
steps=0
for name in ('self-c1','self-c2'):
    checkpoint=t.save(name+'.checkpoint.adva',files[name+'.run.adva'])
    program=json.loads(files[name+'.program.adva']);data=json.loads(files[name+'.input.json'])
    result=t.native(name+'-receiving',program,data,quantum=0,check=checkpoint)
    expected=json.loads(files[name+'.run.adva'])
    assert result['state']==expected['state'] and result['verified_steps']==expected['state']['spent']
    steps+=result['verified_steps']
t.finish('Passed',{'verified_steps':steps});print(json.dumps({'status':'Passed','verified_steps':steps}))
