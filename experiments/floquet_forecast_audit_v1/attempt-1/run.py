"""One supervised fixed diagnostic launch, with persistent fuel and no retry."""
from pathlib import Path
import argparse,hashlib,json,os,resource,signal,subprocess,sys,time
HERE=Path(__file__).resolve().parent

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--worker',action='store_true');a=parser.parse_args();c=json.loads((HERE/'contract.json').read_text());out=HERE/'run-01';ledger=HERE/'launch-ledger.json';b=c['budget']
 if not __debug__:raise RuntimeError('Unoptimized Python required')
 if a.worker:
  resource.setrlimit(resource.RLIMIT_CPU,(b['cpu_seconds'],)*2);resource.setrlimit(resource.RLIMIT_AS,(b['address_space_bytes'],)*2);resource.setrlimit(resource.RLIMIT_FSIZE,(b['output_bytes'],)*2)
  start=time.monotonic()
  try:
   from audit import run
   r=run(out)
  except FileNotFoundError as e:r={'status':'Unavailable','reason':str(e)}
  except Exception as e:
   import traceback
   r={'status':'Failure','reason':repr(e),'traceback':traceback.format_exc()}
  r['resources']={'wall_seconds':time.monotonic()-start,'cpu_seconds':time.process_time(),'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss};(out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');return
 if ledger.exists():raise RuntimeError('One launch allowance already spent; no automatic reset')
 for name,h in c['source_pins'].items():
  if hashlib.sha256((HERE/name).read_bytes()).hexdigest()!=h:raise ValueError('Source pin mismatch')
 out.mkdir(exist_ok=False);entry={'status':'Started','contract_sha256':hashlib.sha256((HERE/'contract.json').read_bytes()).hexdigest()}
 with ledger.open('x') as f:json.dump(entry,f,indent=2)
 with (out/'run.log').open('x') as log:
  env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1');p=subprocess.Popen([sys.executable,str(HERE/'run.py'),'--worker'],stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env=env)
  try:
   code=p.wait(timeout=b['wall_seconds']);r=json.loads((out/'receipt.json').read_text()) if (out/'receipt.json').exists() else {'status':'Unknown' if code<0 else 'Failure','returncode':code}
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait();r={'status':'Unknown','reason':'wall limit'}
 if sum(x.stat().st_size for x in out.rglob('*') if x.is_file())>b['output_bytes']:r={'status':'Unknown','reason':'output allowance exceeded'}
 (out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');entry['status']=r['status'];ledger.write_text(json.dumps(entry,indent=2)+'\n');print(json.dumps(r,indent=2))
 if r['status']!='Pass':raise SystemExit(1)
if __name__=='__main__':main()
