"""Finite training/verification supervisor; Codex (OpenAI), Unknown v0.3."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--ledger',type=Path,required=True);p.add_argument('--stage',choices=['training','verification'],required=True)
    p.add_argument('--worker',action='store_true');a=p.parse_args()
    if not __debug__ or sys.flags.optimize:raise RuntimeError('Unoptimized Python is required')
    here=Path(__file__).parent;c=json.loads((here/'contract.json').read_text());b=c['budget']
    if a.worker:
        resource.setrlimit(resource.RLIMIT_CPU,(b[a.stage+'_cpu_seconds'],)*2)
        resource.setrlimit(resource.RLIMIT_AS,(b['address_space_bytes'],)*2)
        resource.setrlimit(resource.RLIMIT_FSIZE,(b['max_output_bytes'],)*2)
        start=time.monotonic()
        try:
            name='learn' if a.stage=='training' else 'verify'
            spec=importlib.util.spec_from_file_location('memory_worker',here/(name+'.py'))
            m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
            r=m.run(c,a.root,a.output)
        except FileNotFoundError as exc:r={'status':'Unavailable','reason':str(exc)}
        except MemoryError:r={'status':'Unknown','reason':'memory limit'}
        except Exception as exc:
            import traceback
            r={'status':'Failure','reason':repr(exc),'traceback':traceback.format_exc()}
        r['resources']={'wall_seconds':time.monotonic()-start,'cpu_seconds':time.process_time(),
                        'peak_rss_kib_linux':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
        (a.output/(a.stage+'-receipt.json')).write_text(json.dumps(r,indent=2)+'\n');return
    rows=json.loads(a.ledger.read_text()) if a.ledger.exists() else []
    if sum(x['stage']==a.stage for x in rows)>=b[a.stage+'_launches']:raise RuntimeError('Launch budget spent')
    if a.stage=='training':a.output.mkdir(parents=True,exist_ok=False)
    elif not (a.output/'report.json').exists():raise RuntimeError('Completed training required')
    row={'stage':a.stage,'status':'Started','output':str(a.output),'contract_sha256':hashlib.sha256((here/'contract.json').read_bytes()).hexdigest()}
    rows.append(row);a.ledger.write_text(json.dumps(rows,indent=2)+'\n')
    command=[sys.executable,str(Path(__file__).resolve()),'--worker','--root',str(a.root),'--output',str(a.output),
             '--ledger',str(a.ledger),'--stage',a.stage]
    log=a.output/(a.stage+'.log')
    with log.open('x') as f:
        try:
            done=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,timeout=b[a.stage+'_wall_seconds'])
            path=a.output/(a.stage+'-receipt.json')
            r=json.loads(path.read_text()) if path.exists() else {'status':'Unknown' if done.returncode<0 else 'Failure','returncode':done.returncode}
        except subprocess.TimeoutExpired:r={'status':'Unknown','reason':'parent wall timeout'}
    if sum(f.stat().st_size for f in a.output.rglob('*') if f.is_file())>b['max_output_bytes']:
        r={'status':'Unknown','reason':'total output size limit'}
    (a.output/(a.stage+'-receipt.json')).write_text(json.dumps(r,indent=2)+'\n')
    row['status']=r['status'];a.ledger.write_text(json.dumps(rows,indent=2)+'\n')
    print(json.dumps(r,indent=2))
    if r['status']!='Pass':raise SystemExit(1)


if __name__=='__main__':main()
