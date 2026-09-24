"""Read-only reproduction of six published physical rows, no training or search.

Codex (OpenAI), project-original contribution under Unknown v0.3.
Uses independently written explicit finite differences, no audit.py imports.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import signal
import numpy as np


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).parent)
    parser.add_argument('--frozen', type=Path, help='Optional full local frozen-input verification')
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_CPU, (40, 40))
    resource.setrlimit(resource.RLIMIT_AS, (3 * 1024**3, 3 * 1024**3))
    signal.alarm(60)
    root = args.root
    pins = json.loads((root / 'verification-inputs.json').read_text())
    for name, pin in pins['files'].items():
        if digest(root / name) != pin:
            raise ValueError('Changed input: ' + name)
    frozen_count = None
    if args.frozen:
        frozen = json.loads((root / 'freeze-manifest.json').read_text())
        for row in frozen['files']:
            p = args.frozen / row['frozen_path']
            if p.stat().st_size != row['bytes'] or digest(p) != row['sha256']:
                raise ValueError('Changed frozen input: ' + row['frozen_path'])
        frozen_count = len(frozen['files'])
    with np.load(root / 'diagnostic-fields.npz', allow_pickle=False) as f:
        data = {k: f[k] for k in f.files}
    metrics = json.loads((root / 'metrics.json').read_text())
    lat, lon = data['lat'], data['lon']
    phi = np.deg2rad(lat)
    dphi = phi[1] - phi[0]
    dlambda = np.deg2rad(lon[1] - lon[0])
    if not np.allclose(np.diff(phi), dphi) or not np.isclose(len(lon)*dlambda, 2*np.pi):
        raise ValueError('Unexpected grid')
    coriolis = 2 * 7.292115e-5 * np.sin(phi)
    coriolis[np.abs(lat) < 10] = np.nan

    def geo(p):
        dp = np.empty_like(p)
        dp[1:-1] = (p[2:] - p[:-2]) / (2*dphi)
        dp[0] = (-3*p[0] + 4*p[1] - p[2]) / (2*dphi)
        dp[-1] = (3*p[-1] - 4*p[-2] + p[-3]) / (2*dphi)
        east = (p[:, (np.arange(len(lon))+1) % len(lon)] -
                p[:, (np.arange(len(lon))-1) % len(lon)]) / (2*dlambda)
        return np.stack((-dp/(6371000*coriolis[:, None]),
                         east/(6371000*coriolis[:, None]*np.cos(phi)[:, None])), axis=-1)

    def area(south, north, west, east):
        hn = abs(lat[1]-lat[0])/2
        he = (lon[1]-lon[0])/2
        n = np.minimum(north, lat+hn)
        s = np.maximum(south, lat-hn)
        dy = np.maximum(0, np.sin(np.deg2rad(n))-np.sin(np.deg2rad(s)))
        dx = np.maximum(0, np.minimum(east, lon+he)-np.maximum(west, lon-he))
        return dy[:, None]*np.deg2rad(dx)[None, :]

    checked = []
    maximum = 0.0
    parent = data['forecast_wind']
    for part, wind, height in [
        ('total', parent, data['forecast_phi']),
        ('climatology', data['baseline_wind'], data['baseline_phi']),
        ('anomaly', parent-data['baseline_wind'], data['forecast_phi']-data['baseline_phi']),
    ]:
        vg = geo(height)
        speed = np.linalg.norm(wind, axis=-1)
        gs = np.linalg.norm(vg, axis=-1)
        strong = (np.linalg.norm(parent, axis=-1) >= 20) if part == 'anomaly' else speed >= 20
        threshold = 2 if part == 'anomaly' else 5
        eligible = strong & (speed >= threshold) & (gs >= threshold)
        angle = np.degrees(np.arctan2(np.abs(wind[..., 0]*vg[..., 1]-wind[..., 1]*vg[..., 0]),
                                     np.sum(wind*vg, axis=-1)))
        for region, bounds in [('review', (20,60,120,200)), ('focus', (25,45,140,180))]:
            w = area(*bounds)
            good = (w > 0) & np.isfinite(vg).all(axis=-1) & np.isfinite(wind).all(axis=-1)
            def weighted(values, mask=good):
                return float(np.sum(values[mask]*w[mask])/np.sum(w[mask]))
            calc = {key: float(np.sqrt(weighted(np.sum(v*v, axis=-1))))
                    for key, v in [('rms_wind_m_s',wind), ('rms_geostrophic_m_s',vg),
                                   ('rms_residual_m_s',wind-vg)]}
            calc['direction_area_fraction'] = float(w[good & eligible].sum()/w[good].sum())
            calc['strong_direction_abs_mean_deg'] = weighted(angle, good & eligible) if (good & eligible).any() else None
            row = next(x for x in metrics if x['group']=='forecast' and
                       x['representation']=='matched_hybrid_fine' and x['part']==part and x['region']==region)
            for key, value in calc.items():
                if value is None:
                    if row[key] is not None:
                        raise ValueError('Unexpected direction value')
                else:
                    delta = abs(value-row[key]); maximum = max(maximum, delta)
                    if delta > 1e-8:
                        raise ValueError(f'Metric mismatch: {part}/{region}/{key}: {delta}')
            checked.append({'part':part, 'region':region, **calc})
    report = json.loads((root / 'report.json').read_text())
    if report['requested_forecast_available'] or report['audited_url_frame'] != '2026-01':
        raise ValueError('Changed target binding')
    print(json.dumps({'status':'Pass', 'reproduced_rows':checked,
                      'max_absolute_metric_difference':maximum,
                      'frozen_files_checked':frozen_count,
                      'scope':'Independent arithmetic on published unquantized fields; no independent source authentication or forecast validation'}, indent=2))


if __name__ == '__main__':
    main()
