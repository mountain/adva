"""Fixed Floquet/semigroup audit of the frozen ctcal12 learner, no fitting.
Codex (OpenAI), project-original contribution under Unknown v0.3.
"""
from pathlib import Path
import json,hashlib,csv
import numpy as np
from scipy.linalg import eigvals
from scipy.optimize import linear_sum_assignment
HERE=Path(__file__).resolve().parent

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()

def power(a,n):
 result=np.eye(len(a))
 for _ in range(n):result=result@a
 return result

def norm(a):return float(np.linalg.norm(a))
def gain(a):return float(np.sqrt(max(0,np.linalg.eigvalsh(a@a.T)[-1])))
def rms(a):return float(np.sqrt(np.mean(np.sum(abs(a)**2,axis=-1))))

def run(out):
 c=json.loads((HERE/'contract.json').read_text())
 for pin in c['inputs']:
  p=Path(pin['path'])
  if not p.is_file():raise FileNotFoundError(str(p))
  if sha(p)!=pin['sha256']:raise ValueError('Changed frozen input '+str(p))
 paths={x['role']:Path(x['path']) for x in c['inputs']}
 with np.load(paths['model'],allow_pickle=False) as f:model={k:f[k] for k in f.files}
 with np.load(paths['projection'],allow_pickle=False) as f:coeff=f['coefficients'];dates=f['dates'].astype('datetime64[M]')
 with np.load(paths['forecast'],allow_pickle=False) as f:saved=f['spectral_anomaly_coefficients'];target_months=f['months'].tolist()
 V=model['vectors'];R=model['maps'];clim=model['climatology'];scale=model['scale']
 assert V.shape==(2698,64) and R.shape==(6,64,2698) and clim.shape==(12,2698)
 assert np.all(scale>0) and np.all(np.diff(dates.astype(int))==1)
 orth=norm(V.T@V-np.eye(64));assert orth<1e-10,orth
 months=dates.astype(int)%12;x=(coeff-clim[months])/scale;z=x@V
 saved_check=float(np.max(abs(np.stack([z[-1]@r*scale for r in R])-saved)));assert saved_check<1e-8,saved_check
 # Row-vector convention: x_{t+1}=x_t V R1, z_{t+1}=z_t B, B=R1 V.
 B=R[0]@V;annual=power(B,12)
 w=eigvals(B);wa=eigvals(annual);rr,cc=linear_sum_assignment(abs(w[:,None]**12-wa[None,:]));spectral_match=float(np.max(abs(w[rr]**12-wa[cc])));assert spectral_match<1e-8
 np.testing.assert_allclose(annual,np.linalg.matrix_power(B,12),rtol=1e-12,atol=1e-12)
 # Independent recurrence in the full 2698-dimensional encoded state.
 probes=x[::32].copy();step=probes.copy()
 for _ in range(12):step=(step@V)@R[0]
 closed=probes@V@power(B,11)@R[0];recurrence_error=float(np.max(abs(step-closed)));assert recurrence_error<1e-10
 # Exact original controls: damped rotation, stable nonnormal transient, and inconsistent direct map.
 theta=.17;rot=.9*np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])
 expected=.9**12*np.array([[np.cos(12*theta),-np.sin(12*theta)],[np.sin(12*theta),np.cos(12*theta)]])
 rotation_error=norm(power(rot,12)-expected);assert rotation_error<1e-12
 nonnormal=np.array([[.8,1.],[0.,.8]]);assert max(abs(eigvals(nonnormal)))<1 and gain(nonnormal)>1
 assert norm(rot@rot-(rot@rot+np.eye(2)*.1))>.1
 modes=[]
 for i,value in enumerate(w):
  annual_value=value**12
  modes.append({'index':i,'monthly_real':float(value.real),'monthly_imag':float(value.imag),'monthly_modulus':float(abs(value)),
   'annual_real':float(annual_value.real),'annual_imag':float(annual_value.imag),'annual_modulus':float(abs(annual_value)),
   'annual_phase_radians_principal':float(np.angle(annual_value)),
   'annual_stability':'decay' if abs(annual_value)<1-1e-8 else ('growth' if abs(annual_value)>1+1e-8 else 'near_unit_uncertain')})
 modes.sort(key=lambda q:-q['annual_modulus'])
 gains=[];differences=[];compositions=[]
 for n in range(1,13):
  bp=power(B,n);full_reduced=power(B,n-1)@R[0]
  gains.append({'months':n,'latent_operator_norm':gain(bp),'full_encoded_operator_norm':gain(full_reduced),'spectral_radius_power':float(max(abs(w))**n)})
  if n<=6:
   diff=R[n-1]-full_reduced
   differences.append({'lead_months':n,'relative_operator_frobenius':norm(diff)/norm(R[n-1]),
    'latent_relative_frobenius':norm(R[n-1]@V-bp)/norm(R[n-1]@V),
    'last_origin_normalized_output_difference_rms':float(np.linalg.norm(z[-1]@diff)),
    'last_origin_relative_output_difference':float(np.linalg.norm(z[-1]@diff)/max(np.linalg.norm(z[-1]@R[n-1]),1e-30))})
 for i in range(1,7):
  for j in range(1,7-i):
   direct=R[i+j-1];composed=(R[i-1]@V)@R[j-1]
   compositions.append({'first_months':i,'then_months':j,'target_lead':i+j,'relative_frobenius':norm(direct-composed)/norm(direct)})
 innovation=z[1:]-z[:-1]@B
 groups={'training':(dates>=np.datetime64('1979-01'))&(dates<np.datetime64('2015-01')),'validation':(dates>=np.datetime64('2015-01'))&(dates<np.datetime64('2020-01')),'exposed_development':dates>=np.datetime64('2020-01')}
 innovation_rows=[];annual_rows=[]
 for label,mask in groups.items():
  ids=np.flatnonzero(mask & (np.arange(len(dates))>=1))
  e=innovation[ids-1];actual=z[ids]
  seasonal=[]
  for month in range(12):
   keep=months[ids]==month;seasonal.append({'target_month':month+1,'samples':int(keep.sum()),'innovation_rms':rms(e[keep])})
  innovation_rows.append({'split':label,'samples':len(ids),'actual_latent_rms':rms(actual),'innovation_rms':rms(e),'innovation_over_actual_rms':rms(e)/rms(actual),'seasonal':seasonal})
  # This is an ex-post identity, not an operational 12-month forecast evaluation.
  targets=np.flatnonzero(mask & (np.arange(len(dates))>=12));origins=targets-12
  autonomous=z[origins]@annual
  accumulated=np.zeros_like(autonomous)
  for j in range(12):accumulated+=innovation[origins+j]@power(B,11-j)
  closure=float(np.max(abs(z[targets]-autonomous-accumulated)));assert closure<1e-10
  annual_rows.append({'split':label,'target_samples':len(targets),'first_target':str(dates[targets[0]]),'last_target':str(dates[targets[-1]]),
   'actual_latent_rms':rms(z[targets]),'autonomous_latent_rms':rms(autonomous),'accumulated_innovation_rms':rms(accumulated),
   'accumulated_innovation_over_actual_rms':rms(accumulated)/rms(z[targets]),'reconstruction_max_abs':closure,
   'scope':'Ex-post algebraic decomposition; realized future innovations are used, may cross split boundaries, never a forecast skill score'})
 rho=float(max(abs(w)));radius_year=float(max(abs(wa)));sigma_year=gains[-1]
 report={'status':'Completed','target':'frozen ctcal12 normalized learned anomaly state; original first annual-spectrum method as currently published',
  'source_model_shapes':{'vectors':list(V.shape),'maps':list(R.shape),'climatology':list(clim.shape)},'forecast_target_months':target_months,
  'normalization':'Training-only 12 monthly means, fixed channel scale, 64 shared EOF coordinates. Euclidean gains are in these normalized coordinates, not atmospheric energy.',
  'seasonality':'Climatology depends on calendar month; the six forecast maps do not. No learned monthly coefficient family A_1,...,A_12 exists in this model.',
  'homogeneous_extension':'Use only the published one-step map recursively: row z_{t+1}=z_t B, B=R1 V. This defines a constant (thus periodic) homogeneous surrogate. Annual column monodromy is (B^12)^T.',
  'direct_family_consistent_at_1e-8':all(q['relative_frobenius']<=1e-8 for q in compositions),
  'direct_family_caveat':'Six separately fitted direct lead maps need not compose. Annual B^12 characterizes an explicitly added iterated one-step interpretation; it is not an annual operator validated for the entire published direct family.',
  'monthly_spectral_radius':rho,'annual_spectral_radius':radius_year,'annual_latent_operator_norm':sigma_year['latent_operator_norm'],'annual_full_encoded_operator_norm':sigma_year['full_encoded_operator_norm'],
  'max_latent_gain_over_1_to_12':max(q['latent_operator_norm'] for q in gains),'max_full_encoded_gain_over_1_to_12':max(q['full_encoded_operator_norm'] for q in gains),
  'modes':modes,'gains':gains,'direct_vs_iterated':differences,'semigroup_compositions':compositions,
  'one_step_innovations':innovation_rows,'annual_realized_innovation_identity':annual_rows,
  'checks':{'basis_orthogonality_frobenius':orth,'saved_published_anomaly_max_abs':saved_check,'annual_spectral_mapping_max_abs':spectral_match,'full_state_recurrence_max_abs':recurrence_error,'damped_rotation_max_abs':rotation_error,'nonnormal_transient_control':True,'inconsistent_direct_map_negative_control':True},
  'limitations':['No new weather forecast, no retraining or assimilation','This is a coordinate-dependent finite model diagnosis, not real-atmosphere stability','Inhomogeneous residuals mix omitted state, bias, nonlinear dynamics, stochastic and observation effects; no identification of their causes','Realized innovation identity is not independent predictive skill','No new December 2026 forecast or verification','First-method ideal Floquet result retained conditional on periodic homogeneous linear approximation; nonlinear and stochastic forcing treated separately'],
  'contract_sha256':sha(HERE/'contract.json')}
 (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
 for name,rows in [('multipliers',modes),('gains',gains),('direct-vs-iterated',differences),('semigroup-compositions',compositions)]:
  with (out/(name+'.csv')).open('w') as f:
   writer=csv.DictWriter(f,fieldnames=rows[0],lineterminator='\n');writer.writeheader();writer.writerows(rows)
 from render import render
 render(report,out)
 return {'status':'Pass','scientific_outcome':{'periodic_coefficients':'constant one-step anomaly map; periodic climatology is not a season-dependent propagator','direct_family_composition':report['direct_family_consistent_at_1e-8'],'annual_spectral_radius':radius_year,'annual_latent_operator_norm':sigma_year['latent_operator_norm']},'checks':report['checks']}
