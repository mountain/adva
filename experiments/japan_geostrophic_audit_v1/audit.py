"""Original finite geostrophic review. Codex (OpenAI), Unknown v0.3."""
from pathlib import Path
import json,hashlib,sys,csv
import numpy as np
from scipy.interpolate import RegularGridInterpolator

HERE=Path(__file__).parent
G=9.80665; A=6371000.; OMEGA=7.292115e-5

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()

def load(p):
 with np.load(p,allow_pickle=False) as f:return {k:f[k] for k in f.files}

def geowind(phi,lat,lon):
 """Input GEOPOTENTIAL in m2/s2. No extra g. Full periodic longitude required."""
 p=np.deg2rad(lat);l=np.deg2rad(lon);dl=float(np.diff(l).mean())
 if not np.allclose(np.diff(l),dl) or not np.isclose(dl*len(l),2*np.pi):raise ValueError('Full regular periodic longitude required')
 dp=np.gradient(phi,p,axis=-2,edge_order=2)
 dlambda=(np.roll(phi,-1,axis=-1)-np.roll(phi,1,axis=-1))/(2*dl)
 f=2*OMEGA*np.sin(p);safe=np.where(abs(lat)>=10,f,np.nan)
 return np.stack([-dp/(A*safe[:,None]),dlambda/(A*safe[:,None]*np.cos(p)[:,None])],axis=-1)

def remap(x,lat,lon,tl,to):
 y,z=np.meshgrid(tl,to,indexing='ij');points=np.stack([y.ravel(),z.ravel()],axis=1)
 e=np.concatenate([x,x[:,:1]],axis=1);good=np.isfinite(e);axes=(lat[::-1],np.r_[lon,360.])
 n=RegularGridInterpolator(axes,np.where(good,e,0)[::-1])(points)
 d=RegularGridInterpolator(axes,good.astype(float)[::-1])(points)
 return np.divide(n,d,out=np.full_like(n,np.nan),where=d>1e-12).reshape(len(tl),len(to),*x.shape[2:])

def weights(lat,lon,region):
 half=abs(float(np.diff(lat).mean()))/2;hl=float(np.diff(lon).mean())/2
 n=np.minimum(lat+half,region['north']);s=np.maximum(lat-half,region['south'])
 dy=np.maximum(0,np.sin(np.deg2rad(n))-np.sin(np.deg2rad(s)))
 dx=np.maximum(0,np.minimum(lon+hl,region['east'])-np.maximum(lon-hl,region['west']))
 return dy[:,None]*np.deg2rad(dx)[None,:]

def mean(x,w):
 good=(w>0)&np.isfinite(x);return float(np.sum(x[good]*w[good])/w[good].sum()) if good.any() else None

def rms(v,w):return np.sqrt(mean(np.sum(v*v,axis=-1),w))

def diagnostics(v,phi,lat,lon,w,part,parent=None):
 vg=geowind(phi,lat,lon);speed=np.linalg.norm(v,axis=-1);gs=np.linalg.norm(vg,axis=-1)
 good=np.isfinite(v).all(axis=-1)&np.isfinite(vg).all(axis=-1);ww=np.where(good,w,0.)
 if not ww.any():raise ValueError('No common valid support')
 r=v-vg;threshold=2 if part=='anomaly' else 5
 strong=(np.linalg.norm(parent,axis=-1)>=20) if part=='anomaly' else (speed>=20)
 eligible=good&strong&(speed>=threshold)&(gs>=threshold)
 den=np.where((speed>0)&(gs>0),speed*gs,1.)
 angle=np.degrees(np.arccos(np.clip(np.sum(v*vg,axis=-1)/den,-1,1)))
 speed_rms=rms(v,ww);res=rms(r,ww)
 return {'rms_wind_m_s':float(speed_rms),'rms_geostrophic_m_s':float(rms(vg,ww)),
  'rms_residual_m_s':float(res),'residual_over_wind_rms':float(res/speed_rms) if speed_rms>0 else None,
  'mean_speed_m_s':mean(speed,ww),'max_speed_m_s':float(np.max(speed[ww>0])),
  'strong_direction_abs_mean_deg':mean(angle,ww*eligible),'direction_area_fraction':float(np.sum(ww*eligible)/ww.sum()),
  'valid_area_fraction':float(ww.sum()/w.sum())},r

def controls():
 lat=np.arange(87.5,-90,-2.5);lon=np.arange(0,360,2.5);p,l=np.meshgrid(np.deg2rad(lat),np.deg2rad(lon),indexing='ij')
 phi=-A*OMEGA*20*np.sin(p)**2+3000*np.cos(p)*np.sin(l)
 expected=np.stack([20*np.cos(p)+3000*np.sin(l)/(2*OMEGA*A),3000*np.cos(l)/(2*OMEGA*A*np.sin(p))],axis=-1)
 got=geowind(phi,lat,lon);mask=(abs(lat)>=20)&(abs(lat)<=60)
 error=float(np.max(abs(got[mask]-expected[mask])));assert error<.04,error
 np.testing.assert_allclose(geowind(phi[::-1],lat[::-1],lon)[::-1],got,atol=1e-11,equal_nan=True)
 np.testing.assert_allclose(geowind(np.roll(phi,13,axis=1),lat,lon),np.roll(got,13,axis=1),atol=1e-11,equal_nan=True)
 np.testing.assert_allclose(geowind((phi/G)*G,lat,lon),got,atol=1e-10,equal_nan=True)
 np.testing.assert_allclose(geowind(phi+.2*phi,lat,lon),got+geowind(.2*phi,lat,lon),atol=1e-10,equal_nan=True)
 assert np.nanmax(abs(geowind(phi*G,lat,lon)-got))>100
 return {'analytic_max_abs_error_m_s':error,'latitude_reverse':True,'periodic_roll':True,'height_geopotential_units':True,'double_g_negative_control_rejected':True,'linearity':True}

def run(frozen,out):
 c=json.loads((HERE/'contract.json').read_text());freeze=json.loads((HERE/'freeze-manifest.json').read_text())
 assert sha(HERE/'freeze-manifest.json')==c['freeze_sha256']
 for row in freeze['files']:
  if sha(frozen/row['frozen_path'])!=row['sha256']:raise ValueError('Freeze changed '+row['frozen_path'])
 checks=controls();sys.path.insert(0,str(frozen/'runtime/typed-spectrum'));from spectrum import SphereBasis,latlon_points
 root=frozen/'site/research/native-background-l12-v1';model=load(root/'model.npz');bg=load(root/'background.npz');forecast=load(root/'forecast.npz')
 proj=load(frozen/'original-l12/projection-L12.npz');back=load(root/'backtest-coefficients.npz');prior=json.loads((root/'report.json').read_text())
 channels={x['name']:x for x in prior['channels']};sl=lambda n:slice(channels[n]['start'],channels[n]['stop'])
 dates=proj['dates'].astype('datetime64[M]');years=dates.astype('datetime64[Y]').astype(int)+1970;months=dates.astype(int)%12+1
 raw={}
 for n in ['u500','v500','z500','msl']:
  d=load(frozen/'reference'/f'{n}.npz');idx=np.argsort(-d['lat']);idx=idx[abs(d['lat'][idx])<89.99]
  np.testing.assert_array_equal(d['time'].astype('datetime64[M]'),dates)
  raw[n]=d['values'][:,idx];lat=d['lat'][idx].astype(float);lon=d['lon'].astype(float)
 assert np.array_equal(lat,proj['z500_lat']) and np.array_equal(lon,proj['z500_lon'])
 fine_lat=forecast['lat'];fine_lon=forecast['lon'];b_native=SphereBasis(latlon_points(lat,lon),12);b_fine=SphereBasis(latlon_points(fine_lat,fine_lon),12)
 def syn(coeff,b,kind):
  matrix=b.vector if kind=='wind500' else b.scalar
  return np.einsum('ncp,p->nc',matrix,coeff).reshape((len(fine_lat),len(fine_lon),2) if b is b_fine else (len(lat),len(lon),2)) if kind=='wind500' else (matrix@coeff).reshape((len(fine_lat),len(fine_lon)) if b is b_fine else (len(lat),len(lon)))
 def spectrum_pair(coeff,b):return syn(coeff[sl('wind500')],b,'wind500'),syn(coeff[sl('z500')],b,'z500')
 climates={};rows=[];map_arrays={};native_checks={}
 def emit(label,representation,month,year,v,p,climate,ll,lo,group):
  bv,bp=climate
  for part,vv,pp in [('total',v,p),('climatology',bv,bp),('anomaly',v-bv,p-bp)]:
   for region,r in c['regions'].items():
    metric,res=diagnostics(vv,pp,ll,lo,weights(ll,lo,r),part,parent=v)
    rows.append({'group':group,'label':label,'representation':representation,'month':month,'year':year,'part':part,'region':region,**metric})
  return
 for month in c['reference_calendar_months']:
  t=(years<=2014)&(months==month);native_v=np.stack([raw['u500'][t].astype(float).mean(axis=0),raw['v500'][t].astype(float).mean(axis=0)],axis=-1);native_p=raw['z500'][t].astype(float).mean(axis=0)
  msl=raw['msl'][t].astype(float).mean(axis=0)
  np.testing.assert_allclose(native_v,bg['wind500_mean'][month-1],atol=1e-12,rtol=1e-12)
  np.testing.assert_allclose(native_p,bg['z500_mean'][month-1,:,:,0],atol=1e-9,rtol=1e-12)
  clim_c=model['climatology'][month-1]
  cn=spectrum_pair(clim_c,b_native);cf=spectrum_pair(clim_c,b_fine)
  nvfine=remap(native_v,lat,lon,fine_lat,fine_lon);npfine=remap(native_p,lat,lon,fine_lat,fine_lon)
  hybrid=(nvfine,cf[1]);climates[month]={'native':(native_v,native_p),'L12_native':cn,'L12_fine':cf,'matched_hybrid_fine':hybrid,'native_fine':(nvfine,npfine),'msl':msl}
  for rep,base in [('native',(native_v,native_p)),('L12_native',cn),('L12_fine',cf),('matched_hybrid_fine',hybrid)]:
   ll,lo=(lat,lon) if rep in ['native','L12_native'] else (fine_lat,fine_lon)
   for region,r in c['regions'].items():
    metric,_=diagnostics(*base,ll,lo,weights(ll,lo,r),'climatology');rows.append({'group':'training_climatology','label':'1979-2014','representation':rep,'month':month,'year':None,'part':'climatology','region':region,**metric})
  for i in np.flatnonzero((years>=2015)&(months==month)):
   v=np.stack([raw['u500'][i],raw['v500'][i]],axis=-1).astype(float);p=raw['z500'][i].astype(float)
   low_n=spectrum_pair(proj['coefficients'][i],b_native);low_f=spectrum_pair(proj['coefficients'][i],b_fine)
   hybrid_ref=(nvfine+low_f[0]-cf[0],low_f[1])
   for rep,pair in [('native',(v,p)),('L12_native',low_n),('L12_fine',low_f),('matched_hybrid_fine',hybrid_ref)]:
    ll,lo=(lat,lon) if rep in ['native','L12_native'] else (fine_lat,fine_lon)
    emit(str(dates[i]),rep,month,int(years[i]),*pair,climates[month][rep],ll,lo,'historical_reference')
  native_checks[str(month)]={'mean_samples':int(t.sum()),'reference_samples':int(np.sum((years>=2015)&(months==month)))}
  print('Historical reference complete, month',month,flush=True)
 # Actual linked January frame. Never relabel this as December.
 month=1;ix=int(np.flatnonzero(forecast['months']=='2026-01')[0]);v=np.stack([forecast['u500'][ix],forecast['v500'][ix]],axis=-1).astype(float);p=forecast['z500'][ix].astype(float)
 base=climates[1]['matched_hybrid_fine'];pure=spectrum_pair(forecast['spectral_anomaly_coefficients'][ix],b_fine)
 errors={'wind_m_s':float(np.nanmax(abs(v-base[0]-pure[0]))),'geopotential_m2_s2':float(np.nanmax(abs(p-base[1]-pure[1])))}
 assert errors['wind_m_s']<1e-5 and errors['geopotential_m2_s2']<.01,errors
 emit('2026-01 linked frame','matched_hybrid_fine',1,2026,v,p,base,fine_lat,fine_lon,'forecast')
 emit('2026-01 native-mean decomposition','physical_native_mean_baseline',1,2026,v,p,climates[1]['native_fine'],fine_lat,fine_lon,'forecast')
 # Quantized browser input as a distinct display-sensitivity calculation.
 import zarr
 wire={};metas={}
 for bundle,names in [('wind500',['ugrd500','vgrd500']),('hgt500',['hgt500']),('prmsl',['prmsl'])]:
  path=frozen/'site/data/ctcal12.2026010100/v1'/f'{bundle}.zarr';z=zarr.open_group(path,mode='r');meta=dict(z.attrs)['xue'];metas[bundle]=meta
  for name in names:
   q=next(x['quantization'] for x in meta['variables'] if x['id']==name);codes=z[name][ix].astype(float);wire[name]=np.where(codes==q['nodataCode'],np.nan,q['offset']+q['scale']*codes)
 assert metas['wind500']['time']==metas['hgt500']['time']==metas['prmsl']['time']
 qv=np.stack([wire['ugrd500'],wire['vgrd500']],axis=-1);qp=wire['hgt500']*G
 emit('2026-01 quantized grid','quantized_display_input',1,2026,qv,qp,base,fine_lat,fine_lon,'display_sensitivity')
 quantization={'wind_component_max_abs_m_s':float(np.nanmax(abs(qv-v))),'height_max_abs_m':float(np.nanmax(abs(qp-p))/G),'wind_geopotential_common_times':True,'display_height_step_m':8,'note':'Geostrophic derivative of quantized grid is only a sensitivity test, not the preferred physical estimate or the smoothed rendered contour.'}
 # Global L12 forecast comparison reconstitutes native-background wind as its archived spectral mean.
 total_c=model['climatology'][0]+forecast['spectral_anomaly_coefficients'][ix];lp=spectrum_pair(total_c,b_fine)
 emit('2026-01 both variables L12','L12_fine',1,2026,*lp,climates[1]['L12_fine'],fine_lat,fine_lon,'forecast')
 decomposition={}
 for region,r in c['regions'].items():
  w=weights(fine_lat,fine_lon,r);bv,bp=base;dv=v-bv;dp=p-bp
  energy=mean(np.sum(v*v,axis=-1),w);be=mean(np.sum(bv*bv,axis=-1),w);ae=mean(np.sum(dv*dv,axis=-1),w);cross=2*mean(np.sum(bv*dv,axis=-1),w)
  assert abs(energy-be-ae-cross)<1e-8
  speed=np.linalg.norm(v,axis=-1);bs=np.linalg.norm(bv,axis=-1);along=np.sum(bv*dv,axis=-1)/np.maximum(bs,1e-12)
  allowed=w>0;maxpos=np.unravel_index(np.nanargmax(np.where(allowed,speed,np.nan)),speed.shape);bpos=np.unravel_index(np.nanargmax(np.where(allowed,bs,np.nan)),bs.shape)
  cols=np.flatnonzero(w.sum(axis=0)>0);rr=np.flatnonzero(w.sum(axis=1)>0);axis_lat=fine_lat[rr[np.argmax(speed[np.ix_(rr,cols)],axis=0)]];baxis=fine_lat[rr[np.argmax(bs[np.ix_(rr,cols)],axis=0)]]
  physical_p=climates[1]['native_fine'][1];geobias=geowind(bp-physical_p,fine_lat,fine_lon)
  decomposition[region]={'energy_m2_s2':{'total':energy,'baseline':be,'anomaly':ae,'cross_term':cross},'anomaly_over_total_rms':float(np.sqrt(ae/energy)),
   'mean_speed_change_m_s':mean(speed-bs,w),'mean_along_baseline_change_m_s':mean(along,w),
   'mean_strong_zone_along_change_m_s':mean(along,w*(bs>=20)),
   'forecast_max':{'speed_m_s':float(speed[maxpos]),'latitude':float(fine_lat[maxpos[0]]),'longitude_e':float(fine_lon[maxpos[1]])},
   'baseline_max':{'speed_m_s':float(bs[bpos]),'latitude':float(fine_lat[bpos[0]]),'longitude_e':float(fine_lon[bpos[1]])},
   'median_grid_jet_axis_shift_deg':float(np.median(axis_lat-baxis)),
   'height_learned_anomaly_rms_m':float(np.sqrt(mean(dp*dp,w))/G),
   'height_static_representation_bias_rms_m':float(np.sqrt(mean((bp-physical_p)**2,w))/G),
   'height_static_bias_geostrophic_rms_m_s':float(rms(geobias,w))}
 # Historical regional forecast error: exposed development, not untouched skill.
 skills=[]
 for month in [1,12]:
  ids=np.flatnonzero((years>=2020)&(months==month));bv,bp=climates[month]['native'];cn=climates[month]['L12_native']
  for lead in c['historical_skill_leads']:
   for region,r in c['regions'].items():
    w=weights(lat,lon,r);errors_=[];baseline_=[];zerr=[];zbase=[]
    for i in ids:
     coef=back['incumbent_coefficients'][lead-1,i-492];vv,pp=spectrum_pair(coef,b_native);vv=bv+vv-cn[0]
     truth=np.stack([raw['u500'][i],raw['v500'][i]],axis=-1);errors_.append(mean(np.sum((vv-truth)**2,axis=-1),w));baseline_.append(mean(np.sum((bv-truth)**2,axis=-1),w))
     zerr.append(mean((pp-raw['z500'][i])**2,w)/G**2);zbase.append(mean((bp-raw['z500'][i])**2,w)/G**2)
    skills.append({'calendar_month':month,'lead_months':lead,'region':region,'samples':len(ids),'years':[2020,2025],'status':'exposed_development_not_independent','wind_vector_rmse_m_s':float(np.sqrt(np.mean(errors_))),'native_seasonal_vector_rmse_m_s':float(np.sqrt(np.mean(baseline_))),'wind_mse_skill_vs_native_climatology':float(1-np.mean(errors_)/np.mean(baseline_)),'height_rmse_m':float(np.sqrt(np.mean(zerr))),'native_seasonal_height_rmse_m':float(np.sqrt(np.mean(zbase)))})
 # Noncommutation control with one explicitly defined, nonsingular belt projection.
 belt=(abs(lat)>=10);area=np.repeat(np.cos(np.deg2rad(lat[belt])),len(lon));area/=area.sum();sv=b_native.scalar.reshape(len(lat),len(lon),-1)[belt].reshape(-1,169);vv=b_native.vector.reshape(len(lat),len(lon),2,-1)[belt].reshape(-1,336);wv=np.repeat(area,2)
 gs=sv.T@(area[:,None]*sv);gv=vv.T@(wv[:,None]*vv);conditions={'scalar':float(np.linalg.cond(gs)),'vector':float(np.linalg.cond(gv))}
 assert max(conditions.values())<1e10,conditions
 invs=np.linalg.solve(gs,sv.T*area);invv=np.linalg.solve(gv,vv.T*wv)
 commutators=[]
 for month in [1,12]:
  instances=[('climatology',climates[month]['native'][1])]+[(str(dates[i]),raw['z500'][i].astype(float)) for i in np.flatnonzero((years>=2015)&(months==month))]
  for label,phi in instances:
   ps=(b_native.scalar@(invs@phi[belt].ravel())).reshape(len(lat),len(lon));gp=geowind(ps,lat,lon);g=geowind(phi,lat,lon)
   pg=(b_native.vector.reshape(-1,336)@(invv@g[belt].ravel())).reshape(len(lat),len(lon),2)
   for region,r in c['regions'].items():
    commutators.append({'month':month,'label':label,'region':region,'rms_commutator_m_s':float(rms(gp-pg,weights(lat,lon,r)))})
 # Reference ranges are empirical 11-year distributions, never forecast CIs.
 reference=[]
 for month in [1,12]:
  for rep in ['native','L12_native','L12_fine','matched_hybrid_fine']:
   for part in ['total','anomaly']:
    for region in c['regions']:
     chosen=[x for x in rows if x['group']=='historical_reference' and x['month']==month and x['representation']==rep and x['part']==part and x['region']==region]
     stats={}
     for key in ['rms_residual_m_s','rms_wind_m_s','rms_geostrophic_m_s','strong_direction_abs_mean_deg']:
      a=np.array([x[key] for x in chosen if x[key] is not None]);stats[key]={'min':float(a.min()),'median':float(np.median(a)),'max':float(a.max()),'count':len(a)} if len(a) else None
     reference.append({'month':month,'representation':rep,'part':part,'region':region,'years':[2015,2025],'statistics':stats})
 map_arrays={'lat':fine_lat,'lon':fine_lon,'forecast_wind':v,'forecast_phi':p,'baseline_wind':base[0],'baseline_phi':base[1],
  'native_baseline_phi':climates[1]['native_fine'][1],'december_baseline_wind':climates[12]['native_fine'][0],
  'december_baseline_phi':climates[12]['native_fine'][1],'forecast_msl_pa':forecast['msl'][ix],'baseline_msl_pa':remap(climates[1]['msl'],lat,lon,fine_lat,fine_lon)}
 for name,vv,pp in [('total',v,p),('baseline',base[0],base[1]),('anomaly',v-base[0],p-base[1])]:map_arrays[name+'_residual']=vv-geowind(pp,fine_lat,fine_lon)
 np.savez_compressed(out/'diagnostic-fields.npz',**map_arrays)
 report={'status':'Completed with target-time mismatch','requested_forecast':'2026-12','requested_forecast_available':False,'audited_url_frame':'2026-01',
  'initial_input_cutoff':'2025-12','run_container_time':'2026-01-01T00:00:00Z','valid_time_label':'2026-01-15T00:00:00Z','averaging_period':['2026-01-01T00:00:00Z','2026-02-01T00:00:00Z'],
  'training':['1979-01','2014-12'],'selection':['2015-01','2019-12'],'generation':prior['generated_utc'],'reference_data':'Frozen NCEP/NCAR Reanalysis 1 monthly means; cached through 2025-12, no independent source authentication',
  'checks':checks,'forecast_reconstruction_max_error':errors,'reference_counts':native_checks,'quantization':quantization,'decomposition':decomposition,'reference_ranges':reference,'regional_development_skill':skills,
  'commutator_definition':c['commutator'],'commutator_gram_condition':conditions,'commutator_rows':commutators,
  'published_global_metric':prior['development_physical_metrics']['wind500'],
  'source_coupling':'u/v from a shared vector harmonic block, Z from a distinct scalar block; all predicted through the same 64-dimensional EOF state and 6 direct ridge maps. Wind is not diagnosed from Z, no explicit geostrophic constraint; statistical coupling means outputs are not independent.',
  'display':'Colour = magnitude of monthly-mean u/v after quantization/interpolation, not monthly mean of instantaneous speed. Particles advect in the displayed real monthly vector frame using visual Euler steps, bilinear sampling, time scaling and random reseeding; no synoptic trajectory claim. Filled frames can blend, particles update on real decoded frames. hgt500 contours have separate display smoothing.',
  'floquet_scope':c['imported_assumptions']['Floquet'],
  'notebook':'User-supplied Observable code independently generates idealized cosine samples; 384 months cover 32 ideal years. Its AR1 text describes an earlier version, not ctcal12. It supplies no forecast source or physical verification.',
  'December_missing_metrics':{'total_residual':None,'anomaly_residual':None,'new_signal':None,'forecast_skill_at_lead_12':None,'reason':'No forecast array with target 2026-12; no substitution or extrapolation'},
  'limitations':['January URL audit is not a December-2026 forecast audit','Geostrophic residual is a balance diagnostic, not truth error; finite difference, mean-field nonlinear effects and representation contribute','No untouched independent hindcast and no future verification','Reference ranges use 11 historical same-calendar-month fields, not confidence limits','ENSO causation not tested; no event-specific ENSO index or composite analysis','Source authenticity concern retained'],
  'contract_sha256':sha(HERE/'contract.json'),'freeze_sha256':sha(HERE/'freeze-manifest.json')}
 (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');(out/'metrics.json').write_text(json.dumps(rows,indent=2,allow_nan=False)+'\n')
 with (out/'metrics.csv').open('w') as stream:
  writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 with (out/'regional-development-skill.csv').open('w') as stream:
  writer=csv.DictWriter(stream,fieldnames=list(skills[0]));writer.writeheader();writer.writerows(skills)
 from render import render
 render(out,c)
 for row in freeze['files']:
  if sha(frozen/row['frozen_path'])!=row['sha256']:raise ValueError('Freeze modified during run')
 return {'status':'Pass','target_status':'2026-12 unavailable; actual linked 2026-01 audited','metric_rows':len(rows),'reference_months':22,'checks':checks,'decomposition':decomposition}
