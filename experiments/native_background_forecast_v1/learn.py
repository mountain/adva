"""Original training-only native-background forecast correction; Unknown v0.3."""
from datetime import datetime, timezone
import hashlib
import importlib
import json
from pathlib import Path
import sys
import numpy as np
from scipy.interpolate import RegularGridInterpolator


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1048576),b''):h.update(block)
    return h.hexdigest()


def setup(root):
    sys.path.insert(0,str(root/'xue-study/experiments/multivariate-refinement'))
    return importlib.import_module('project')


def monthly_mean(training_values,training_valid,training_months):
    means=[];counts=[]
    for month in range(12):
        at=training_months==month;mask=training_valid[at]
        count=mask.sum(axis=0)
        numerator=np.where(mask[:,:,None],training_values[at],0.).sum(axis=0)
        means.append(np.divide(numerator,count[:,None],out=np.full_like(numerator,np.nan),where=count[:,None]>0))
        counts.append(count)
    return np.array(means),np.array(counts)


def interpolate_background(values,lat,lon,target_lat,target_lon):
    # Normalize over finite neighbors; missing cells are not observed zeroes.
    values=np.asarray(values)
    extended=np.concatenate([values,values[:,:1]],axis=1)
    finite=np.isfinite(extended)
    yy,xx=np.meshgrid(target_lat,target_lon,indexing='ij');points=np.stack([yy.ravel(),xx.ravel()],axis=1)
    axes=(lat[::-1],np.r_[lon,360.])
    numerator=RegularGridInterpolator(axes,np.where(finite,extended,0.)[::-1],bounds_error=True)(points)
    denominator=RegularGridInterpolator(axes,finite.astype(float)[::-1],bounds_error=True)(points)
    return np.divide(numerator,denominator,out=np.full_like(numerator,np.nan),where=denominator>1e-12)


def run(contract,root,out):
    if not __debug__:raise RuntimeError('Unoptimized Python required')
    if np.__version__!=contract['dependencies']['numpy']:raise RuntimeError('NumPy version mismatch')
    for pin in contract['input_pins']:
        f=root/pin['path']
        if f.stat().st_size!=pin['bytes'] or sha(f)!=pin['sha256']:raise ValueError(f'Changed source {f}')
    project=setup(root);folder=root/contract['source_archive']
    with np.load(folder/'projection-L12.npz',allow_pickle=False) as f:p={k:f[k] for k in f.files}
    with np.load(folder/'model.npz',allow_pickle=False) as f:m={k:f[k] for k in ['climatology','scale','vectors','maps']}
    prior=json.loads((folder/'report.json').read_text());channels=prior['channels']
    c=p['coefficients'];dates=p['dates'];months=dates.astype('datetime64[M]').astype(int)%12
    np.testing.assert_array_equal(dates,np.arange('1979-01','2026-01',dtype='datetime64[M]').astype(str))
    x=(c-m['climatology'][months])/m['scale'];training=np.arange(432);valid=np.arange(432,492);test=np.arange(492,564)
    def predict(targets):
        return np.stack([(x[targets-lead]@m['vectors'])@m['maps'][lead-1]*m['scale']+
                         m['climatology'][months[targets]] for lead in range(1,7)])
    cp_valid=predict(valid)
    pressure_cache={}
    def inputs(ch):
        arrays=[]
        for code in ch['fields']:
            v,lat,lon,d=project.load_field(code)
            np.testing.assert_array_equal(d,dates)
            arrays.append(v.reshape(len(d),-1))
        y=np.stack(arrays,axis=2);fixed=p[ch['name']+'_domain'].ravel()
        good=fixed[None,:]&np.isfinite(y).all(axis=2)
        if ch['level'] is not None:
            key=(tuple(lat),tuple(lon))
            if key not in pressure_cache:pressure_cache[key]=project.interpolate_surface_pressure(lat,lon)
            good &= pressure_cache[key]>=ch['level']*100
        basis,w=project.geometry(tuple(lat),tuple(lon),12)
        matrix=basis.vector if len(arrays)==2 else basis.scalar[:,None,:]
        return y,lat,lon,good,matrix,w
    def score(ch,bg,coeff,targets,data):
        y,lat,lon,good,matrix,w=data;n=ch['name'];sl=slice(ch['start'],ch['stop'])
        climate=np.einsum('tp,ncp->tnc',m['climatology'][months[targets],sl],matrix)
        native=bg[months[targets]]
        weights=good[targets]*w[None,:];weights/=weights.sum(axis=1)[:,None]
        target=np.where(good[targets,:,None],y[targets],0.)
        scores={'incumbent_L12':[],'native_seasonal':[],'native_background_plus_learned_anomaly':[]}
        for lead in range(6):
            spectral=np.einsum('tp,ncp->tnc',coeff[lead,:,sl],matrix)
            if n.startswith('q'):
                incumbent=np.exp(spectral);corrected=native*np.exp(spectral-climate)
            else:incumbent=spectral;corrected=native+spectral-climate
            for key,array in [('incumbent_L12',incumbent),('native_seasonal',native),
                              ('native_background_plus_learned_anomaly',corrected)]:
                if not np.isfinite(array[good[targets]]).all():raise ValueError(f'Nonfinite valid {n}')
                delta=np.where(good[targets,:,None],array,0.)-target
                scores[key].append(float(np.mean(np.sum(delta*delta*weights[:,:,None],axis=(1,2)))))
        return scores
    backgrounds={};choices={};vmetrics={};counts={}
    for ch in channels:
        n=ch['name'];data=inputs(ch);y,lat,lon,good,_,_=data
        bg,cnt=monthly_mean(y[training],good[training],months[training])
        fixed=p[n+'_domain'].ravel()
        if np.any(cnt[:,fixed]==0):raise ValueError('Unobserved training background cell')
        backgrounds[n+'_mean']=bg.reshape(12,len(lat),len(lon),len(ch['fields']))
        backgrounds[n+'_lat']=lat;backgrounds[n+'_lon']=lon;backgrounds[n+'_domain']=p[n+'_domain']
        counts[n]={'minimum_samples_per_month_on_domain':int(cnt[:,fixed].min()),'maximum_samples':int(cnt.max())}
        scores=score(ch,bg,cp_valid,valid,data);vmetrics[n]=scores
        gain=1-np.mean(scores['native_background_plus_learned_anomaly'])/np.mean(scores['incumbent_L12'])
        choices[n]={'use_native_background':bool(gain>=contract['switch_min_validation_gain']),
                    'validation_physical_mse_gain':float(gain)}
        print('Validation',n,json.dumps(choices[n]),flush=True)
    selection={'channels':choices,'validation_metrics':vmetrics,'training_samples_per_month':counts,
               'selection_uses_development_targets':False,'source':'1979-2014 only for background means'}
    (out/'selection.json').write_text(json.dumps(selection,indent=2)+'\n')
    np.savez_compressed(out/'background.npz',**backgrounds)
    # All choices are frozen before construction/scoring of development forecasts.
    cp_test=predict(test)
    with np.load(folder/'backtest.npz',allow_pickle=False) as f:
        np.testing.assert_allclose(cp_test,f['joint'],rtol=0,atol=1e-10)
    dmetrics={};native_checks={}
    for ch in channels:
        n=ch['name'];bg=backgrounds[n+'_mean'].reshape(12,-1,len(ch['fields']))
        scores=score(ch,bg,cp_test,test,inputs(ch))
        expected=(np.square(prior['physical_humidity'][n]['joint']['full_rmse_kg_kg']) if n.startswith('q')
                  else np.array(prior['metrics']['joint'][n]['full_mse']))
        discrepancy=float(np.max(abs(np.array(scores['incumbent_L12'])-expected)/np.maximum(expected,1e-30)))
        if discrepancy>1e-8:raise ValueError(f'Incumbent native score mismatch {n}: {discrepancy}')
        native_checks[n]=discrepancy
        scores['selected_calibrated']=scores['native_background_plus_learned_anomaly' if choices[n]['use_native_background'] else 'incumbent_L12']
        dmetrics[n]=scores
    norms=prior['cross_resolution_comparison']['training_normalizers'];aggregate={}
    for variant in contract['comparators']:
        values=np.mean([np.array(dmetrics[n][variant])/norms[n] for n in dmetrics],axis=0)
        aggregate[variant]={'normalized_physical_mse':values.tolist(),'mean':float(values.mean())}
    gains={n:1-float(np.mean(s['selected_calibrated'])/np.mean(s['incumbent_L12'])) for n,s in dmetrics.items()}
    gain=1-aggregate['selected_calibrated']['mean']/aggregate['incumbent_L12']['mean']
    g=contract['promotion_gate']
    eligible=(gain>=g['min_development_aggregate_physical_gain'] and gains['wind500']>=-g['max_wind500_relative_degradation']
              and min(gains.values())>=-g['max_channel_relative_degradation'])
    forecast_anomaly=(x[-1]@m['vectors'])@m['maps']*m['scale']
    lat=np.arange(87.5,-88, -1.25);lon=np.arange(0,360,1.25)
    basis,_=project.geometry(tuple(lat),tuple(lon),12)
    grid={'lat':lat,'lon':lon};output_domains={}
    yy,xx=np.meshgrid(lat,lon,indexing='ij');points=np.stack([yy.ravel(),xx.ravel()],axis=1)
    for ch in channels:
        n=ch['name'];sl=slice(ch['start'],ch['stop'])
        matrix=basis.vector if len(ch['fields'])==2 else basis.scalar[:,None,:]
        anomaly=np.einsum('tp,ncp->tnc',forecast_anomaly[:,sl],matrix)
        native_lat=backgrounds[n+'_lat'];native_lon=backgrounds[n+'_lon'];domain=backgrounds[n+'_domain']
        domain=np.c_[domain,domain[:,0]]
        mask=RegularGridInterpolator((native_lat[::-1],np.r_[native_lon,360.]),domain[::-1].astype(float),method='nearest',bounds_error=False,fill_value=0.)(points)>=.5
        output_domains[n]=mask.reshape(len(lat),len(lon))
        if choices[n]['use_native_background']:
            background=np.array([interpolate_background(backgrounds[n+'_mean'][month],native_lat,native_lon,lat,lon) for month in range(6)])
            fields=background*np.exp(anomaly) if n.startswith('q') else background+anomaly
        else:
            climate=np.einsum('tp,ncp->tnc',m['climatology'][:6,sl],matrix)
            fields=np.exp(climate+anomaly) if n.startswith('q') else climate+anomaly
        for j,code in enumerate(ch['fields']):
            grid[code]=np.where(mask[None,:],fields[:,:,j],np.nan).reshape(6,len(lat),len(lon)).astype('float32')
    for ch in channels:
        if ch['level'] is not None:
            for code in ch['fields']:grid[code]=np.where(grid['sp']>=ch['level']*100,grid[code],np.nan)
    if any(np.nanmin(grid[n])<=0 for n in ['q850','q700','sp']):raise ValueError('Nonpositive humidity or pressure')
    target_months=np.array(contract['target_months'])
    np.savez_compressed(out/'forecast.npz',months=target_months,spectral_anomaly_coefficients=forecast_anomaly,**grid)
    coarse={k:(v[::2] if k in ['lat','lon'] else v[:,::2,::2]) for k,v in grid.items()}
    np.savez_compressed(out/'forecast-on-coarse-grid.npz',months=target_months,spectral_anomaly_coefficients=forecast_anomaly,**coarse)
    np.savez_compressed(out/'model.npz',**m,channels_json=p['channels_json'],selection_json=np.array(json.dumps(selection)))
    np.savez_compressed(out/'backtest-coefficients.npz',target_months=dates[test],incumbent_coefficients=cp_test,
                        spectral_anomalies=cp_test-m['climatology'][months[test]][None,:,:])
    report={'version':contract['version'],'generated_utc':datetime.now(timezone.utc).isoformat(),
            'status':'historical-origin monthly forecast with training-only background correction',
            'initial_month':'2025-12','target_months':contract['target_months'],'training':contract['training'],
            'validation':contract['validation'],'development_backtest':contract['development_backtest'],
            'prior_exposure':'Validation and development intervals previously inspected; no new independent confirmation.',
            'degree':12,'grid_step_degrees':1.25,'physical_variables':16,'channels':channels,'native_adva':False,'assimilation':False,
            'selection':selection,'development_physical_metrics':dmetrics,'aggregate':aggregate,
            'development_gain_vs_incumbent':{'aggregate_physical_mse':gain,'per_channel':gains},
            'numerical_promotion_gate_passed':bool(eligible),'release_gate':'Pending independent replay, encoder and browser checks',
            'checks':{'incumbent_native_relative_errors':native_checks,'positive_humidity_and_surface_pressure':True},
            'forecast_ranges':{n:{'min':float(np.nanmin(v)),'max':float(np.nanmax(v)),'finite_fraction':float(np.isfinite(v).mean())}
                               for n,v in grid.items() if n not in ['lat','lon']},
            'sources':prior['sources'],'contract_sha256':sha(Path(__file__).with_name('contract.json')),
            'source_authenticity_reservation':contract['source_authenticity_reservation'],
            'method':contract['method'],'limitations':['This gain is a training-background representation correction, not demonstrated benefit from temporal memory.',
                'Original L12 anomalies are unchanged. No submonthly skill, new observation, assimilation or conservation law is added.',
                'The full forecast is not representable by the L12 coefficients alone; background.npz and channel choices are part of the model.',
                'Interpolated native background provides display values; output grid spacing is not verified forecast resolution.',
                'SST remains download-only. Data authenticity is unresolved.']}
    (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    return {'status':'Pass','numerical_promotion_gate_passed':bool(eligible),'aggregate_gain':gain,'per_channel_gain':gains,
            'selected_channels':{n:q['use_native_background'] for n,q in choices.items()}}
