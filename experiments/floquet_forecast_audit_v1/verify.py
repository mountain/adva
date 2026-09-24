"""Independent column-coordinate check using only the public frozen model.
Codex (OpenAI), original contribution under Unknown v0.3. No fitting or search.
"""
from pathlib import Path
import argparse,hashlib,json,resource,signal
import numpy as np

def main():
 p=argparse.ArgumentParser();p.add_argument('--model',type=Path,required=True);p.add_argument('--root',type=Path,default=Path(__file__).parent);a=p.parse_args()
 resource.setrlimit(resource.RLIMIT_CPU,(40,40));resource.setrlimit(resource.RLIMIT_AS,(3*1024**3,)*2);signal.alarm(60)
 c=json.loads((a.root/'contract.json').read_text());r=json.loads((a.root/'report.json').read_text());pin=next(x for x in c['inputs'] if x['role']=='model')
 if not a.model.is_file():raise SystemExit('Unavailable: frozen model.npz required')
 if hashlib.sha256(a.model.read_bytes()).hexdigest()!=pin['sha256']:raise ValueError('Model hash mismatch')
 with np.load(a.model,allow_pickle=False) as f:V=f['vectors'];maps=f['maps']
 E=V.T@maps[0].T;M=np.linalg.matrix_power(E,12)
 def op(a):return float(np.linalg.svd(a,compute_uv=False)[0])
 got={'monthly_spectral_radius':float(max(abs(np.linalg.eigvals(E)))), 'annual_spectral_radius':float(max(abs(np.linalg.eigvals(M)))), 'annual_latent_operator_norm':op(M),'annual_full_encoded_operator_norm':op(maps[0].T@np.linalg.matrix_power(E,11))}
 errors={k:abs(v-r[k]) for k,v in got.items()}
 rows=[]
 for h in range(1,7):
  direct=maps[h-1].T;iterated=maps[0].T@np.linalg.matrix_power(E,h-1)
  delta=float(np.linalg.norm(direct-iterated)/np.linalg.norm(direct));expected=r['direct_vs_iterated'][h-1]['relative_operator_frobenius'];errors[f'lead_{h}']=abs(delta-expected);rows.append({'lead_months':h,'relative_operator_frobenius':delta})
 if max(errors.values())>1e-10:raise ValueError('Independent coordinate check failed '+str(errors))
 print(json.dumps({'status':'Pass','method':'Column-coordinate propagation, numpy eigvals/matrix_power and singular-value decomposition; source hash verified','values':got,'direct_vs_iterated':rows,'max_absolute_difference':max(errors.values()),'scope':'Same frozen parameters, independent algebraic evaluation; no independent data or forecast skill'},indent=2))
if __name__=='__main__':main()
