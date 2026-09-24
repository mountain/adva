"""Original aggregate diagnostics of private frozen xue inputs; Unknown v0.3.

The existing spherical evaluator is a separately installed, hash-pinned input.
No source data, coefficients or evaluator implementation are distributed here.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def run(c, root):
    import numpy as np
    import scipy
    from scipy.fft import dctn
    assert np.__version__ == c['dependencies']['numpy']
    assert scipy.__version__ == c['dependencies']['scipy']
    assert sum(p['bytes'] for p in c['input_pins']) <= c['budget']['max_input_bytes']
    for pin in c['input_pins']:
        path = root / pin['path']
        assert path.stat().st_size == pin['bytes'], str(path)
        assert sha(path) == pin['sha256'], str(path)
    source_hashes = {p['path']:p['sha256'] for p in c['input_pins']}
    spec = importlib.util.spec_from_file_location('frozen_xue_spherical_evaluator', root/c['evaluator'])
    evaluator = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = evaluator
    spec.loader.exec_module(evaluator)
    source = root / c['source_directory']
    with np.load(source/'u500.npz', allow_pickle=False) as u, np.load(source/'v500.npz', allow_pickle=False) as v:
        assert all(np.array_equal(u[k], v[k]) for k in ['time','lat','lon'])
        dates, lat, lon = (u[k] for k in ['time','lat','lon'])
        uval, vval = u['values'].astype(float), v['values'].astype(float)
    assert uval.shape == vval.shape == (564,73,144)
    assert np.array_equal(dates, np.arange('1979-01','2026-01', dtype='datetime64[M]').astype(str))
    assert np.array_equal(lat, np.arange(90,-90.01,-2.5))
    assert np.array_equal(lon, np.arange(0,360,2.5))
    expected_targets = np.arange('2020-01','2026-01',dtype='datetime64[M]').astype(str)
    tids = np.flatnonzero(np.isin(dates, expected_targets))
    assert np.array_equal(dates[tids], expected_targets)
    freq = np.rint(np.fft.fftfreq(9)*9).astype(int)
    k = np.maximum(abs(freq[:,None]), abs(freq[None,:]))
    dctk = np.maximum(np.arange(9)[:,None], np.arange(9)[None,:])
    rows = []
    checks = {'max_relative_block_identity_error':0., 'max_relative_parseval_error':0.,
              'max_relative_dct_parseval_error':0., 'source_hashes_match_both_archives':True}
    cases = 0
    for archive in c['archives']:
        folder = root / archive['path']
        report = json.loads((folder/'report.json').read_text())
        assert report['degree'] == archive['degree']
        assert report['training'] == ['1979-01','2014-12']
        assert report['validation'] == ['2015-01','2019-12']
        assert report['development_backtest'] == ['2020-01','2025-12']
        for code, rawname in [('u500','uwnd'), ('v500','vwnd')]:
            recorded = next(x for x in report['sources'] if x['code'] == code)
            assert recorded['level_hpa'] == 500 and recorded['source_units'] == 'm/s'
            assert recorded['sha256'] == source_hashes[f"{c['source_directory']}/{code}.npz"]
            assert recorded['source_sha256'] == source_hashes[f"{c['source_directory']}/ncep.reanalysis.derived__pressure__{rawname}.mon.mean.nc"]
        channel = next(x for x in report['channels'] if x['name'] == 'wind500')
        assert channel['fields'] == ['u500','v500'] and channel['transform'] == 'identity'
        with np.load(folder/'backtest.npz', allow_pickle=False) as back:
            assert np.array_equal(back['target_months'], expected_targets)
            stored = {m:back[m][...,channel['start']:channel['stop']] for m in c['models']}
        assert all(x.shape == (6,72,2*((archive['degree']+1)**2-1)) for x in stored.values())
        for patch in c['patches']:
            plat = patch['center_lat'] + np.arange(4,-5,-1)*2.5
            plon = patch['center_lon'] + np.arange(-4,5)*2.5
            yi = np.array([int(np.flatnonzero(lat == x)[0]) for x in plat])
            xi = np.array([int(np.flatnonzero(lon == x)[0]) for x in plon])
            truth = np.stack([uval[np.ix_(tids,yi,xi)], vval[np.ix_(tids,yi,xi)]],axis=-1)
            assert truth.shape == (72,9,9,2) and np.isfinite(truth).all()
            wlat = np.sin(np.deg2rad(plat+1.25))-np.sin(np.deg2rad(plat-1.25))
            weights = np.broadcast_to(wlat[:,None], (9,9)).copy()
            weights /= weights.sum()
            bw = weights.reshape(3,3,3,3).sum(axis=(1,3))
            basis = evaluator.SphereBasis(evaluator.latlon_points(plat,plon), archive['degree']).vector
            assert basis.shape == (81,2,stored[c['models'][0]].shape[-1])
            for name, coefficients in stored.items():
                for lead in c['leads']:
                    cases += 1
                    assert cases <= c['budget']['max_diagnostic_rows']
                    predicted = np.einsum('tp,ncp->tnc', coefficients[lead-1],basis).reshape(72,9,9,2)
                    error = predicted - truth
                    weighted = error*weights[None,:,:,None]
                    average = weighted.reshape(72,3,3,3,3,2).sum(axis=(2,4))/bw[None,:,:,None]
                    lifted = average.repeat(3,axis=1).repeat(3,axis=2)
                    residual = error-lifted
                    energy = lambda f: np.sum(weights[None,:,:,None]*f*f,axis=(1,2,3))
                    total, coarse, detail = energy(error), energy(lifted), energy(residual)
                    scaled = error*np.sqrt(weights)[None,:,:,None]
                    power = abs(np.fft.fftn(scaled, axes=(1,2), norm='ortho'))**2
                    cosine = dctn(scaled, axes=(1,2), norm='ortho', type=2)**2
                    for key, defect in [('max_relative_block_identity_error',total-coarse-detail),
                                        ('max_relative_parseval_error',total-power.sum(axis=(1,2,3))),
                                        ('max_relative_dct_parseval_error',total-cosine.sum(axis=(1,2,3)))]:
                        val = float(np.max(abs(defect)/np.maximum(total,1e-30)))
                        checks[key] = max(checks[key], val)
                        assert val < c['tolerance']
                    band = lambda array, mask: float(array[:,mask,:].sum(axis=(1,2)).mean())
                    mse = float(total.mean())
                    rows.append({'degree':archive['degree'], 'patch':patch['name'], 'model':name, 'lead_months':lead,
                                 'vector_mse':mse, 'vector_rmse':float(np.sqrt(mse)),
                                 'coarse_mse':float(coarse.mean()), 'detail_mse':float(detail.mean()),
                                 'detail_fraction':float(detail.mean()/mse),
                                 'dft_band_mse':{'zero':band(power,k==0),'one':band(power,k==1),'two_to_four':band(power,k>=2)},
                                 'dft_above_one_fraction':band(power,k>=2)/mse,
                                 'dct_above_two_fraction':band(cosine,dctk>=3)/mse})
    assert cases == c['budget']['max_diagnostic_rows']
    return {'rows':rows, 'checks':checks, 'target_months':len(expected_targets),
            'diagnostic_rows':cases, 'units':{'mse':'m^2 s^-2','rmse':'m s^-1'},
            'raw_sample_values_distributed':False,
            'source_authenticity_reservation':c['source_authenticity_reservation'],
            'scope':c['scope']}
