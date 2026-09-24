"""Independent mean/interpolation replay and regional scoring; Unknown v0.3."""
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


def bilinear(values,lat,lon,target_lat,target_lon):
    # Explicit four-corner calculation independent of the fitting script's RGI.
    a=lat[::-1];b=np.r_[lon,360.]
    yy,xx=np.meshgrid(target_lat,target_lon,indexing='ij');y=yy.ravel();x=xx.ravel()
    i=np.clip(np.searchsorted(a,y,side='right')-1,0,len(a)-2)
    j=np.clip(np.searchsorted(b,x,side='right')-1,0,len(b)-2)
    dy=(y-a[i])/(a[i+1]-a[i]);dx=(x-b[j])/(b[j+1]-b[j])
    if min(dy.min(),dx.min())<-1e-12 or max(dy.max(),dx.max())>1+1e-12:raise ValueError('Interpolation extrapolation')
    v=np.concatenate([values[::-1],values[::-1,:1]],axis=1)
    numerator=np.zeros((len(y),values.shape[-1]));denominator=np.zeros_like(numerator)
    for di,dj,w in [(0,0,(1-dy)*(1-dx)),(1,0,dy*(1-dx)),(0,1,(1-dy)*dx),(1,1,dy*dx)]:
        sample=v[i+di,j+dj];valid=np.isfinite(sample)
        numerator+=np.where(valid,sample,0)*w[:,None];denominator+=valid*w[:,None]
    result=np.divide(numerator,denominator,out=np.full_like(numerator,np.nan),where=denominator>1e-12)
    return result,(i+(dy>.5),j+(dx>.5))


def run(contract,root,out):
    if not __debug__:raise RuntimeError('Unoptimized Python required')
    vc=json.loads(Path(__file__).with_name('verification-contract.json').read_text())
    for name,digest in vc['artifact_pins'].items():
        if sha(out/name)!=digest:raise ValueError(f'Changed artifact {name}')
    for name,digest in vc['implementation_pins'].items():
        if sha(Path(__file__).with_name(name))!=digest:raise ValueError(f'Changed checker {name}')
    for pin in contract['input_pins']:
        if sha(root/pin['path'])!=pin['sha256']:raise ValueError('Changed external input')
    sys.path.insert(0,str(root/'xue-study/experiments/typed-spectrum'))
    sphere=importlib.import_module('spectrum')
    source=root/contract['source_archive']; raw=root/'climatetensor-inputs/ncep-multivariate'
    with np.load(out/'model.npz',allow_pickle=False) as f:m={k:f[k] for k in f.files}
    with np.load(out/'background.npz',allow_pickle=False) as f:bg={k:f[k] for k in f.files}
    with np.load(out/'forecast.npz',allow_pickle=False) as f:forecast={k:f[k] for k in f.files}
    with np.load(out/'forecast-on-coarse-grid.npz',allow_pickle=False) as f:coarse={k:f[k] for k in f.files}
    with np.load(source/'projection-L12.npz',allow_pickle=False) as f:
        coefficients=f['coefficients']; dates=f['dates'];channels=json.loads(str(f['channels_json']))
    with np.load(source/'model.npz',allow_pickle=False) as f:
        for key in ['climatology','scale','vectors','maps']:np.testing.assert_array_equal(m[key],f[key])
    choices=json.loads(str(m['selection_json']))['channels']
    month=np.arange(432)%12;mean_errors={}
    for ch in channels:
        n=ch['name'];all_fields=[]
        for code in ch['fields']:
            with np.load(raw/(code+'.npz'),allow_pickle=False) as f:
                order=np.argsort(-f['lat']);order=order[abs(f['lat'][order])<89.999]
                values=f['values'][:432,order].astype(float)
                np.testing.assert_array_equal(f['lat'][order],bg[n+'_lat'])
                np.testing.assert_array_equal(f['lon'],bg[n+'_lon'])
            # Every cell of the training-fixed domain is finite throughout training.
            mask=bg[n+'_domain']
            if not np.isfinite(values[:,mask]).all():raise ValueError('Training-fixed domain inconsistent')
            means=np.stack([values[month==k][:,mask].mean(axis=0) for k in range(12)])
            all_fields.append(means)
        independent=np.stack(all_fields,axis=-1)
        saved=bg[n+'_mean'][:,mask,:]
        error=float(np.max(abs(independent-saved)))
        np.testing.assert_allclose(independent,saved,rtol=1e-13,atol=1e-10)
        mean_errors[n]=error
    state=(coefficients[-1]-m['climatology'][11])/m['scale']
    latent=state@m['vectors'];anomalies=np.stack([latent@m['maps'][lead]*m['scale'] for lead in range(6)])
    np.testing.assert_allclose(anomalies,forecast['spectral_anomaly_coefficients'],rtol=1e-12,atol=1e-10)
    lat=forecast['lat'];lon=forecast['lon'];basis=sphere.SphereBasis(sphere.latlon_points(lat,lon),12)
    replay={};grid_errors={}
    for ch in channels:
        n=ch['name'];sl=slice(ch['start'],ch['stop'])
        matrix=basis.vector if len(ch['fields'])==2 else basis.scalar[:,None,:]
        noise=np.array([np.tensordot(matrix,anomalies[k,sl],axes=(2,0)) for k in range(6)])
        values=[];nearest=None
        for k in range(6):
            native,nearest=bilinear(bg[n+'_mean'][k],bg[n+'_lat'],bg[n+'_lon'],lat,lon)
            if choices[n]['use_native_background']:
                v=native*np.exp(noise[k]) if n.startswith('q') else native+noise[k]
            else:
                climate=np.tensordot(matrix,m['climatology'][k,sl],axes=(2,0))
                v=np.exp(climate+noise[k]) if n.startswith('q') else climate+noise[k]
            values.append(v)
        domain=np.c_[bg[n+'_domain'][::-1],bg[n+'_domain'][::-1,:1]]
        mask=domain[nearest]
        values=np.where(mask[None,:,None],np.array(values),np.nan)
        for j,code in enumerate(ch['fields']):replay[code]=values[:,:,j].reshape(6,len(lat),len(lon)).astype('float32')
    for ch in channels:
        if ch['level'] is not None:
            for code in ch['fields']:replay[code]=np.where(replay['sp']>=ch['level']*100,replay[code],np.nan)
    for code,value in replay.items():
        np.testing.assert_array_equal(np.isfinite(value),np.isfinite(forecast[code]))
        np.testing.assert_allclose(value,forecast[code],rtol=2e-6,atol=1e-6,equal_nan=True)
        grid_errors[code]=float(np.nanmax(abs(value.astype(float)-forecast[code])))
        np.testing.assert_array_equal(coarse[code],forecast[code][:,::2,::2])
    np.testing.assert_array_equal(coarse['lat'],lat[::2]);np.testing.assert_array_equal(coarse['lon'],lon[::2])
    # Same predeclared patches as Research 0229; no region-specific selection.
    with np.load(out/'backtest-coefficients.npz',allow_pickle=False) as f:bc=f['incumbent_coefficients']
    wind=next(ch for ch in channels if ch['name']=='wind500');sl=slice(wind['start'],wind['stop'])
    native={}
    for code in ['u500','v500']:
        with np.load(raw/(code+'.npz'),allow_pickle=False) as f:
            native[code]=f['values'][-72:].astype(float);rlat=f['lat'];rlon=f['lon']
    regions=[]
    for name,y,x in [('East Asia',32.5,150),('North America',40,295),('Middle East',27.5,50)]:
        py=y+np.arange(4,-5,-1)*2.5;px=x+np.arange(-4,5)*2.5
        yi=np.array([np.flatnonzero(rlat==v)[0] for v in py]);xi=np.array([np.flatnonzero(rlon==v)[0] for v in px])
        byi=np.array([np.flatnonzero(bg['wind500_lat']==v)[0] for v in py])
        bxi=np.array([np.flatnonzero(bg['wind500_lon']==v)[0] for v in px])
        truth=np.stack([native[n][:,yi][:,:,xi] for n in ['u500','v500']],axis=-1)
        pb=sphere.SphereBasis(sphere.latlon_points(py,px),12).vector
        spectral_clim=np.einsum('tp,ncp->tnc',m['climatology'][np.arange(72)%12,sl],pb).reshape(72,9,9,2)
        native_clim=bg['wind500_mean'][np.arange(72)%12][:,byi][:,:,bxi]
        w=np.broadcast_to((np.sin(np.deg2rad(py+1.25))-np.sin(np.deg2rad(py-1.25)))[:,None],(9,9)).copy();w/=w.sum()
        for lead in [1,6]:
            old=np.einsum('tp,ncp->tnc',bc[lead-1,:,sl],pb).reshape(72,9,9,2)
            new=old-spectral_clim+native_clim if choices['wind500']['use_native_background'] else old
            score=lambda f:float(np.mean(np.sum((f-truth)**2*w[None,:,:,None],axis=(1,2,3))))
            a,b=score(old),score(new)
            regions.append({'region':name,'lead_months':lead,'old_vector_rmse':float(np.sqrt(a)),
                            'new_vector_rmse':float(np.sqrt(b)),'mse_gain':1-b/a})
    result={'status':'Pass','training_background_independent_mean_max_error':mean_errors,
            'saved_anomaly_model_replayed':True,'independent_bilinear_full_grid_max_abs_error':grid_errors,
            'all_coarse_samples_exact':True,'native_field_count':16,'regional_results':regions,
            'source_authenticity_reservation':contract['source_authenticity_reservation']}
    (out/'quality-check.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
