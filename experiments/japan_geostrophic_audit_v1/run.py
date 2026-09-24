"""One bounded diagnostic launch; no training or automatic retry."""
from pathlib import Path
import argparse,json,os,resource,subprocess,sys,time,hashlib,signal
HERE=Path(__file__).parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--frozen',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True);p.add_argument('--worker',action='store_true');a=p.parse_args()
 if not __debug__:raise RuntimeError('Unoptimized Python required')
 c=json.loads((HERE/'contract.json').read_text());b=c['budget']
 if a.worker:
  resource.setrlimit(resource.RLIMIT_CPU,(b['cpu_seconds'],)*2);resource.setrlimit(resource.RLIMIT_AS,(b['address_space_bytes'],)*2);resource.setrlimit(resource.RLIMIT_FSIZE,(b['output_bytes'],)*2)
  start=time.monotonic()
  try:
   from audit import run
   result=run(a.frozen,a.output)
  except FileNotFoundError as exc:result={'status':'Unavailable','reason':str(exc)}
  except Exception as exc:
   import traceback
   result={'status':'Failure','reason':repr(exc),'traceback':traceback.format_exc()}
  result['resources']={'wall_seconds':time.monotonic()-start,'cpu_seconds':time.process_time(),'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
  (a.output/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');return
 rows=json.loads(a.ledger.read_text()) if a.ledger.exists() else []
 if len(rows)>=b['diagnostic_launches']:raise RuntimeError('Diagnostic launch allowance spent')
 for name,h in c['implementation_pins'].items():
  if hashlib.sha256((HERE/name).read_bytes()).hexdigest()!=h:raise ValueError('Source pin mismatch')
 a.output.mkdir(parents=True,exist_ok=False);entry={'status':'Started','contract_sha256':hashlib.sha256((HERE/'contract.json').read_bytes()).hexdigest(),'output':str(a.output)};rows.append(entry);a.ledger.write_text(json.dumps(rows,indent=2)+'\n')
 with (a.output/'run.log').open('x') as log:
  process=subprocess.Popen([sys.executable,str(HERE/'run.py'),'--worker','--frozen',str(a.frozen),'--output',str(a.output),'--ledger',str(a.ledger)],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  try:
   code=process.wait(timeout=b['wall_seconds']);result=json.loads((a.output/'receipt.json').read_text()) if (a.output/'receipt.json').exists() else {'status':'Unknown' if code<0 else 'Failure','returncode':code}
  except subprocess.TimeoutExpired:
   os.killpg(process.pid,signal.SIGKILL);process.wait();result={'status':'Unknown','reason':'wall limit'}
 if sum(x.stat().st_size for x in a.output.rglob('*') if x.is_file())>b['output_bytes']:result={'status':'Unknown','reason':'output size limit'}
 (a.output/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');entry['status']=result['status'];a.ledger.write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(result,indent=2))
 if result['status']!='Pass':raise SystemExit(1)

if __name__=='__main__':main()
