"""One separately bounded exact replay of the frozen audit; no model fitting.
Codex (OpenAI), original contribution under Unknown v0.3.
"""
from pathlib import Path
import hashlib,json,os,resource,signal,subprocess,sys,time,argparse
HERE=Path(__file__).resolve().parent

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser();p.add_argument('--frozen',type=Path,required=True);p.add_argument('--worker',action='store_true');a=p.parse_args()
 contract=json.loads((HERE/'replay-contract.json').read_text());out=HERE/'exact-replay';ledger=HERE/'exact-replay-ledger.json'
 if a.worker:
  resource.setrlimit(resource.RLIMIT_CPU,(540,540));resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,)*2);resource.setrlimit(resource.RLIMIT_FSIZE,(150000000,)*2)
  from audit import run
  result=run(a.frozen,out);(out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');return
 if ledger.exists(): raise SystemExit('Replay allowance already spent; retain this ledger. No automatic retry.')
 if not a.frozen.is_dir(): raise SystemExit('Unavailable: full frozen input cache required, see freeze-manifest.json; not bundled with public report.')
 for name,h in contract['source_pins'].items():
  if sha(HERE/name)!=h: raise SystemExit('Replay source pin changed: '+name)
 out.mkdir(exist_ok=False)
 receipt={'status':'Started','contract_sha256':sha(HERE/'replay-contract.json'),'scope':'one exact reproduction; no new model selection','started_utc_epoch':time.time()}
 with ledger.open('x') as f:json.dump(receipt,f,indent=2)
 env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
 with (out/'run.log').open('x') as log:
  proc=subprocess.Popen([sys.executable,str(HERE/'reproduce_full.py'),'--worker','--frozen',str(a.frozen.resolve())],stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env=env)
  try:
   rc=proc.wait(timeout=600)
   if rc!=0:receipt.update(status='Failure',returncode=rc)
   elif sum(f.stat().st_size for f in out.rglob('*') if f.is_file())>150000000:receipt.update(status='Unknown',reason='output allowance exceeded')
   elif sha(out/'metrics.json')!=contract['expected_metrics_sha256']:receipt.update(status='Failure',reason='metrics differ; no silent repair')
   else:receipt.update(status='Pass',metric_bytes_equal=True)
  except subprocess.TimeoutExpired:
   os.killpg(proc.pid,signal.SIGKILL);proc.wait();receipt.update(status='Unknown',reason='wall limit')
 receipt['wall_seconds']=time.time()-receipt['started_utc_epoch'];ledger.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
 if receipt['status']!='Pass':raise SystemExit(1)
if __name__=='__main__':main()
