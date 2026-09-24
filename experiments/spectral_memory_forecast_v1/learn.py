"""Original validation-selected spectral memory learner; Codex, Unknown v0.3."""
from datetime import datetime, timezone
import hashlib
import importlib
import json
from pathlib import Path
import sys
import numpy as np


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()


def external(root):
    sys.path.insert(0,str(root/'xue-study/experiments/multivariate-refinement'))
    return importlib.import_module('train')


def low_indices(channels):
    out=[]
    for ch in channels:
        a=ch['start']
        out.extend(range(a,a+49) if len(ch['fields'])==1 else
                   list(range(a,a+48))+list(range(a+168,a+216)))
    return np.array(out,dtype=int)


def history(z,origins,lag):
    origins=np.asarray(origins,dtype=int)
    if origins.min()<lag-1 or origins.max()>=len(z):raise ValueError('history outside supplied observations')
    return np.concatenate([z[origins-j] for j in range(lag)],axis=1)


def fit_maps(training,ztraining,lag,penalty):
    # API receives training arrays only, not a whole-array index selector.
    maps=[]; ranges=[]
    for lead in range(1,7):
        targets=np.arange(lead+lag-1,len(training));origins=targets-lead
        a=history(ztraining,origins,lag);b=training[targets]
        maps.append(np.linalg.solve(a.T@a/len(a)+penalty*np.eye(a.shape[1]),a.T@b/len(a)))
        ranges.append({'lead':lead,'pairs':len(targets),'first_history':int(origins[0]-lag+1),
                       'last_origin':int(origins[-1]),'last_target':int(targets[-1])})
    return np.stack(maps),ranges


def incumbent(x,origins,vectors,maps):
    return np.stack([(x[o]@vectors)@maps[i] for i,o in enumerate(origins)])


def candidate(base,z,origins,indices,maps,lag,weight):
    pred=base.copy()
    for i,o in enumerate(origins):
        learned=history(z,o,lag)@maps[i]
        pred[i,:,indices]=((1-weight)*base[i][:,indices]+weight*learned).T
    return pred


def apply_choices(options,choices,channels):
    result=options['incumbent_L12'].copy()
    for ch in channels:
        sl=slice(ch['start'],ch['stop'])
        result[...,sl]=options[choices[ch['name']]['selected']][...,sl]
    return result


def metrics(projection,pred,targets,channels):
    out={}
    for ch in channels:
        n=ch['name'];sl=slice(ch['start'],ch['stop'])
        delta=pred[...,sl]-projection[n+'_c'][targets][None,:,:]
        indices=projection[n+'_gram_index'][targets]
        costs=np.zeros(delta.shape[:2])
        for g in np.unique(indices):
            at=np.flatnonzero(indices==g);d=delta[:,at,:]
            costs[:,at]=np.sum((d@projection[n+'_gram_bank'][g])*d,axis=2)
        resolved=costs.mean(axis=1)
        out[n]={'resolved_mse':resolved.tolist(),
                'full_mse':(resolved+projection[n+'_residual'][targets].mean()).tolist(),
                'units':'log(kg kg-1)' if n.startswith('q') else ch['units']}
    return out


def run(contract,root,out):
    if not __debug__:raise RuntimeError('Python optimization is unsupported')
    if np.__version__!=contract['dependencies']['numpy']:raise RuntimeError('NumPy version mismatch')
    for pin in contract['input_pins']:
        p=root/pin['path']
        if p.stat().st_size!=pin['bytes'] or sha(p)!=pin['sha256']:raise ValueError(f'changed input: {p}')
    folder=root/contract['source_archive']; legacy=external(root)
    with np.load(folder/'projection-L12.npz',allow_pickle=False) as f:p={k:f[k] for k in f.files}
    with np.load(folder/'model.npz',allow_pickle=False) as f:
        old={k:f[k] for k in ['climatology','scale','vectors','maps']}
    prior=json.loads((folder/'report.json').read_text())
    channels=json.loads(str(p['channels_json'])); c=p['coefficients']; dates=p['dates']
    if c.shape!=(564,2698):raise ValueError('Unexpected source dimensions')
    expected=np.arange('1979-01','2026-01',dtype='datetime64[M]').astype(str)
    np.testing.assert_array_equal(dates,expected)
    months=dates.astype('datetime64[M]').astype(int)%12
    train=np.arange(432); valid=np.arange(432,492);test=np.arange(492,564)
    climatology=np.stack([c[train[months[train]==m]].mean(axis=0) for m in range(12)])
    np.testing.assert_allclose(climatology,old['climatology'],rtol=0,atol=1e-12)
    scale=np.zeros(c.shape[1])
    for ch in channels:
        sl=slice(ch['start'],ch['stop'])
        scale[sl]=max(float(np.sqrt(np.mean(np.sum((c[train,sl]-climatology[months[train],sl])**2,axis=1)))),1e-12)
    np.testing.assert_allclose(scale,old['scale'],rtol=0,atol=1e-12)
    x=(c-climatology[months])/scale
    indices=low_indices(channels)
    if len(indices)!=778:raise ValueError('Low-degree dimension mismatch')
    lowvectors=np.linalg.svd(x[train][:,indices],full_matrices=False)[2][:contract['rank']].T
    z=x[:,indices]@lowvectors
    decode=lambda a,targets:a*scale+climatology[months[targets]]
    origins=lambda targets:[targets-lead for lead in range(1,7)]
    norm_metrics=metrics(p,climatology[months[train]][None,:,:],train,channels)
    normalizers={n:row['full_mse'][0] for n,row in norm_metrics.items()}
    def losses(pred,targets):
        scored=metrics(p,decode(pred,targets),targets,channels)
        per={n:float(np.mean(s['full_mse'])/normalizers[n]) for n,s in scored.items()}
        return float(np.mean(list(per.values()))),per
    base=incumbent(x,origins(valid),old['vectors'],old['maps'])
    vb={'incumbent_L12':base,'seasonal':np.zeros_like(base)}
    candidate_rows=[]; winners={}; pair_ranges=[];fit_count=0
    for lag in contract['history_lengths']:
        best=None
        for penalty in contract['ridge_penalties']:
            maps,ranges=fit_maps(x[train][:,indices],z[train],lag,penalty)
            fit_count+=len(maps);pair_ranges.append({'history':lag,'penalty':penalty,'ranges':ranges})
            for weight in contract['blend_weights']:
                pred=candidate(base,z,origins(valid),indices,maps,lag,weight)
                loss,per=losses(pred,valid)
                row={'history':lag,'penalty':penalty,'blend':weight,'validation_loss':loss,'per_channel_loss':per}
                candidate_rows.append(row)
                if best is None or loss<best[0]:best=(loss,row,maps.copy(),pred)
        key='best_one_frame' if lag==1 else 'best_three_frame'
        winners[key]={'choice':best[1],'maps':best[2]};vb[key]=best[3]
        print('Selected family',key,json.dumps(best[1]),flush=True)
    if fit_count!=contract['budget']['max_training_fits'] or len(candidate_rows)!=contract['budget']['max_validation_candidates']:
        raise ValueError('Unexpected candidate count')
    vl={name:losses(value,valid) for name,value in vb.items()}
    order=['incumbent_L12','seasonal','best_one_frame','best_three_frame']; choices={}
    for ch in channels:
        n=ch['name'];best=min(order,key=lambda name:vl[name][1][n]);baseline=vl['incumbent_L12'][1][n]
        gain=1-vl[best][1][n]/baseline
        selected=best if gain>=contract['switch_min_validation_gain'] else 'incumbent_L12'
        choices[n]={'selected':selected,'best_validation_candidate':best,'best_validation_gain':gain,
                    'candidate_validation_losses':{name:vl[name][1][n] for name in order}}
    # Freeze selection to disk before constructing or scoring development predictions.
    selection={'winners':{k:v['choice'] for k,v in winners.items()},'channels':choices,
               'candidates':candidate_rows,'training_pairs':pair_ranges,'fits':fit_count,
               'selection_uses_development_targets':False}
    (out/'selection.json').write_text(json.dumps(selection,indent=2)+'\n')
    def options_from(arr,os):
        b=incumbent(arr,os,old['vectors'],old['maps']); zz=arr[:,indices]@lowvectors
        opts={'incumbent_L12':b,'seasonal':np.zeros_like(b)}
        for key,w in winners.items():
            q=w['choice'];opts[key]=candidate(b,zz,os,indices,w['maps'],q['history'],q['blend'])
        return opts
    opts=options_from(x,origins(test));opts['selected_guarded']=apply_choices(opts,choices,channels)
    actual={k:decode(v,test) for k,v in opts.items()}
    with np.load(folder/'backtest.npz',allow_pickle=False) as oldback:
        np.testing.assert_allclose(actual['incumbent_L12'],oldback['joint'],rtol=0,atol=1e-10)
    poisoned=x.copy();poisoned[492:]=1e8
    a=apply_choices(options_from(x,[np.array([491])]*6),choices,channels)
    b=apply_choices(options_from(poisoned,[np.array([491])]*6),choices,channels)
    np.testing.assert_array_equal(a,b)
    scored={k:metrics(p,v,test,channels) for k,v in actual.items()}
    print('Evaluating physical humidity',flush=True)
    humidity=legacy.physical_humidity(p,actual,test,channels)
    physical={}
    for key in actual:
        per={ch['name']:(np.square(humidity[ch['name']][key]['full_rmse_kg_kg']).tolist()
             if ch['name'].startswith('q') else scored[key][ch['name']]['full_mse']) for ch in channels}
        aggregate=np.mean([np.array(per[n])/prior['cross_resolution_comparison']['training_normalizers'][n] for n in per],axis=0)
        physical[key]={'per_channel_mse':per,'normalized_physical_mse':aggregate.tolist(),
                       'mean_normalized_physical_mse':float(aggregate.mean())}
    ref=physical['incumbent_L12'];new=physical['selected_guarded']
    gains={n:1-float(np.mean(new['per_channel_mse'][n])/np.mean(ref['per_channel_mse'][n])) for n in ref['per_channel_mse']}
    total_gain=1-new['mean_normalized_physical_mse']/ref['mean_normalized_physical_mse']
    gate=contract['promotion_gate']
    eligible=(total_gain>=gate['min_development_aggregate_physical_gain'] and
              gains['wind500']>=-gate['max_wind500_relative_degradation'] and
              min(gains.values())>=-gate['max_channel_relative_degradation'])
    fo=options_from(x,[np.array([563])]*6)
    selected=apply_choices(fo,choices,channels)[:,0,:]
    forecast=selected*scale+climatology[np.arange(6)]
    if not np.isfinite(forecast).all():raise ValueError('Nonfinite forecast')
    grid=legacy.forecast_grids(p,forecast,channels)
    if any(np.nanmin(grid[n])<=0 for n in ['q850','q700']):raise ValueError('Humidity is not positive')
    target_months=np.array(contract['target_months'])
    np.savez_compressed(out/'forecast.npz',months=target_months,coefficients=forecast,**grid)
    coarse={k:(v[::2] if k in ['lat','lon'] else v[:,::2,::2]) for k,v in grid.items()}
    np.savez_compressed(out/'forecast-on-coarse-grid.npz',months=target_months,coefficients=forecast,**coarse)
    np.savez_compressed(out/'backtest.npz',target_months=dates[test],**actual)
    saved={**old,'low_indices':indices,'low_vectors':lowvectors,'channels_json':p['channels_json'],
           'selection_json':np.array(json.dumps(selection)),
           **{k+'_maps':v['maps'] for k,v in winners.items()}}
    np.savez_compressed(out/'model.npz',**saved)
    ranges={n:{'min':float(np.nanmin(v)),'max':float(np.nanmax(v)),'finite_fraction':float(np.isfinite(v).mean())}
            for n,v in grid.items() if n not in ['lat','lon']}
    report={'version':contract['version'],'generated_utc':datetime.now(timezone.utc).isoformat(),
            'status':'historical-origin experimental monthly forecast; not operational weather',
            'initial_month':contract['initial_month'],'target_months':contract['target_months'],
            'degree':12,'grid_step_degrees':1.25,'channels':channels,'physical_variables':16,
            'native_adva':False,'assimilation':False,'training':contract['training'],'validation':contract['validation'],
            'development_backtest':contract['development_backtest'],'prior_exposure':contract['prior_exposure'],
            'selection':selection,'validation_losses':{k:v[0] for k,v in vl.items()},
            'metrics':scored,'physical_humidity':humidity,'physical_evaluation':physical,
            'development_gain_vs_incumbent':{'aggregate_physical_mse':total_gain,'per_channel':gains},
            'numerical_promotion_gate_passed':bool(eligible),'release_gate':'Pending independent replay, encoding and web checks',
            'forecast_ranges':ranges,'sources':prior['sources'],'contract_sha256':sha(Path(__file__).with_name('contract.json')),
            'source_authenticity_reservation':'The user questions authenticity of the entire data chain. Same-source hashes and reproducibility do not resolve it. No independent source verification performed.',
            'limitations':['Historical 2025-12 origin, January-June 2026 monthly means, generated retrospectively.',
                           'Prior-exposed development comparison, no fresh confirmatory test or as-of observations.',
                           'Low degree within L12 is not the original L6 fit; spectral degree and grid are unchanged.',
                           'Validation fallback may retain the incumbent or seasonal baseline for some channels.',
                           'SST remains download-only; no conservation, physical floor or teleconnection attribution implied.'],
            'checks':{'training_normalization_reproduced':True,'incumbent_backtest_reproduced':True,
                      'forecast_origin_future_poison_unchanged':True,'training_fits':fit_count,'validation_candidates':len(candidate_rows)}}
    (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    return {'status':'Pass','numerical_promotion_gate_passed':bool(eligible),'aggregate_gain':total_gain,
            'per_channel_gain':gains,'selected_channels':{n:q['selected'] for n,q in choices.items()}}
