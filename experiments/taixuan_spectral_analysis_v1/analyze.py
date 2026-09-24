"""Original bounded spectral instruments; Codex (OpenAI), Unknown v0.3."""
import argparse
from collections import Counter
import hashlib
import itertools
import json
import math
from pathlib import Path
import resource
import subprocess
import sys
import time


class Limit(Exception):
    pass


class Meter:
    def __init__(self, budget):
        self.budget = budget
        self.cases = 0
        self.start = time.monotonic()

    def charge(self, n=1):
        self.cases += n
        if self.cases > self.budget['max_case_units']:
            raise Limit('case-unit limit')
        if time.monotonic()-self.start > self.budget['wall_seconds_per_launch']:
            raise Limit('wall limit')


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def coarse(field):
    # Time is outside the four spatial/address coordinates.
    return field.reshape(3,3,3,3,3,3,3,3).mean(axis=(1,3,5,7))


def phase1(contract, meter):
    import numpy as np
    assert np.__version__ == contract['dependencies']['numpy']
    cfg = contract['phase1']
    modes = [tuple(k) for k in cfg['positive_modes']]
    velocity = cfg['velocity']
    shape = (9,)*4
    size = 9**4
    threshold = cfg['support_threshold']

    def transfer(k):
        return np.prod([np.mean(np.exp(2j*np.pi*x*np.arange(3)/9)) for x in k])

    def initial(seed, extra=False):
        c = np.zeros(shape, dtype=complex)
        for j, k in enumerate(modes):
            h = transfer(k)
            amplitude = (1 if abs(h)>1e-10 else .7)/max(abs(h), 1 if abs(h)<1e-10 else 0)
            amplitude *= 1+.15*seed*math.cos(j+.2)
            a = amplitude*np.exp(1j*(.19*j+.29*seed*(j+1)))
            c[k] = a
            c[tuple((-x)%9 for x in k)] = a.conjugate()
        if extra:
            k = tuple(cfg['stress_mode'])
            c[k] = 2/abs(transfer(k))
            c[tuple((-x)%9 for x in k)] = c[k].conjugate()
        return (np.fft.ifftn(c)*size).real

    def evolve(field, alpha):
        meter.charge(size*9)
        shifted = np.roll(field, velocity, axis=(0,1,2,3))
        return (1-8*alpha)*shifted + alpha*sum(
            np.roll(shifted, sign, axis=i) for i in range(4) for sign in [-1,1])

    def trajectory(seed, alpha, frames, extra=False):
        values = [initial(seed, extra)]
        for _ in range(frames-1):
            values.append(evolve(values[-1], alpha))
        return np.array(values)

    def spectra(series):
        meter.charge(series.size*4)
        return np.fft.fftn(series, axes=(1,2,3,4))/np.prod(series.shape[1:])

    def fit(series):
        f = spectra(series).reshape(len(series), -1)
        y = spectra(np.array([coarse(v) for v in series])).reshape(len(series), -1)
        support = np.max(abs(f),axis=0)>threshold
        csupport = np.max(abs(y),axis=0)>threshold
        multipliers = np.zeros(f.shape[1],complex)
        multipliers[support] = np.sum(f[:-1,support].conj()*f[1:,support],axis=0)/np.sum(abs(f[:-1,support])**2,axis=0)
        ar1 = np.zeros(y.shape[1],complex)
        ar3 = np.zeros((y.shape[1],3),complex)
        condition = []
        for k in np.flatnonzero(csupport):
            ar1[k] = np.vdot(y[:-1,k],y[1:,k])/np.vdot(y[:-1,k],y[:-1,k])
            x = np.stack([y[2:-1,k],y[1:-2,k],y[:-3,k]],axis=1)
            beta, _, rank, singular = np.linalg.lstsq(x,y[3:,k],rcond=None)
            assert rank == 3
            ar3[k] = beta
            condition.append(float(singular[0]/singular[-1]))
        return dict(support=support, coarse_support=csupport, multipliers=multipliers,
                    ar1=ar1, ar3=ar3, condition=condition)

    def forecast(model, history, horizon, fine=True):
        f = spectra(history)[-1].reshape(-1)
        unsupported = np.flatnonzero((abs(f)>threshold)&~model['support'])
        if fine and len(unsupported):
            return {'status':'RefusedUnsupportedModes', 'count':int(len(unsupported))}
        y = spectra(np.array([coarse(v) for v in history])).reshape(len(history),-1)
        state1 = y[-1].copy()
        memory = list(y)
        out = {'ar1':[], 'ar3':[], 'fine':[]}
        for _ in range(horizon):
            state1 *= model['ar1']
            next3 = np.sum(np.stack(memory[-3:][::-1],axis=1)*model['ar3'],axis=1)
            memory.append(next3)
            out['ar1'].append((np.fft.ifftn(state1.reshape((3,)*4))*81).real)
            out['ar3'].append((np.fft.ifftn(next3.reshape((3,)*4))*81).real)
            if fine:
                f *= model['multipliers']
                out['fine'].append((np.fft.ifftn(f.reshape(shape))*size).real)
        return {k:np.array(v) for k,v in out.items()}

    results = []
    for alpha in cfg['diffusion']:
        train = trajectory(0,alpha,cfg['training_frames'])
        model = fit(train)  # Called before constructing any test trajectory.
        # Bundle accessor explicitly excludes all future values.
        bundle = {'training':train, 'future':np.full((2,*shape),1e9)}
        poisoned = fit(bundle['training'])
        assert all(np.array_equal(model[k],poisoned[k]) for k in ['multipliers','ar1','ar3'])
        grids = np.indices(shape)
        laplacian = sum(2-2*np.cos(2*np.pi*grids[i]/9) for i in range(4))
        expected = np.exp(-2j*np.pi*sum(grids[i]*velocity[i] for i in range(4))/9)*(1-alpha*laplacian)
        multiplier_error = float(np.max(abs(model['multipliers'][model['support']]-expected.ravel()[model['support']])))
        assert multiplier_error < 1e-10
        totals = Counter()
        curves = {k:np.zeros(cfg['horizons']) for k in ['truth','ar1','ar3','fine_coarse','fine_full']}
        qiong_curves = None
        for seed in cfg['test_fixture_ids']:
            truth = trajectory(seed,alpha,3+cfg['horizons'])
            predicted = forecast(model,truth[:3],cfg['horizons'])
            y = np.array([coarse(v) for v in truth[3:]])
            fine_y = np.array([coarse(v) for v in predicted['fine']])
            curves['truth'] += np.sum(y*y,axis=(1,2,3,4))
            for name, pred in [('ar1',predicted['ar1']),('ar3',predicted['ar3']),('fine_coarse',fine_y)]:
                error = np.sum((pred-y)**2,axis=(1,2,3,4))
                curves[name] += error
                totals[name] += float(error.sum())
            fine_error = np.sum((predicted['fine']-truth[3:])**2,axis=(1,2,3,4))
            curves['fine_full'] += fine_error
            totals['fine_full'] += float(fine_error.sum())
            totals['coarse_truth_energy'] += float(np.sum(y*y))
            totals['fine_truth_energy'] += float(np.sum(truth[3:]**2))
            if seed == 1:
                q = (slice(None),2,1,1,2)
                qiong_curves = {'truth':y[q].tolist(),'ar1':predicted['ar1'][q].tolist(),
                                'ar3':predicted['ar3'][q].tolist(),'fine':fine_y[q].tolist()}
        nmse = {k:totals[k]/totals['coarse_truth_energy'] for k in ['ar1','ar3','fine_coarse']}
        nmse['fine_full'] = totals['fine_full']/totals['fine_truth_energy']
        assert nmse['ar3'] < cfg['tolerance'] and nmse['fine_full'] < cfg['tolerance']
        stress = trajectory(3,alpha,3+cfg['horizons'],extra=True)
        refused = forecast(model,stress[:3],cfg['horizons'])
        assert refused['status']=='RefusedUnsupportedModes'
        stress_coarse = forecast(model,stress[:3],cfg['horizons'],fine=False)['ar3']
        stress_truth = np.array([coarse(v) for v in stress[3:]])
        stress_nmse = float(np.sum((stress_coarse-stress_truth)**2)/np.sum(stress_truth**2))
        results.append({'diffusion':alpha,'fine_modes_learned':int(model['support'].sum()),
                        'coarse_modes_active':int(model['coarse_support'].sum()),
                        'max_learned_multiplier_error':multiplier_error,
                        'ar1_max_multiplier_magnitude':float(abs(model['ar1']).max()),
                        'ar3_max_design_condition':max(model['condition']),
                        'test_nmse':nmse,'nmse_by_lead':{k:(curves[k]/curves['truth']).tolist() for k in ['ar1','ar3','fine_coarse']},
                        'qiong_test_seed_1':qiong_curves,'future_poison_does_not_change_fit':True,
                        'untrained_mode_refusal':refused,'stress_ar3_nmse':stress_nmse})
    # A nonzero forever-persistent mode can be invisible in every block average.
    z0 = np.indices(shape)[0]
    invisible = np.cos(2*np.pi*3*z0/9)
    assert np.max(abs(coarse(invisible))) < 1e-12
    moved = evolve(invisible,0)
    assert np.max(abs(coarse(moved))) < 1e-12
    assert abs(np.sum(moved*moved)-np.sum(invisible*invisible)) < 1e-9
    return {'cases':results,'invisible_mode':[3,0,0,0],
            'invisible_mode_persistent_energy':float(np.sum(invisible*invisible)),
            'scope':'Synthetic noiseless linear dynamics. Four address coordinates plus a separate discrete evolution time. No atmospheric forecast.'}


def phase2(contract, meter):
    import numpy as np
    groups = []
    fixtures = [('constant',[]),('period_three_stripe',[(3,0,0,0)]),
                ('four_primitive_modes',[tuple(int(i==j) for i in range(4)) for j in range(4)])]
    for name,support in fixtures:
        periods = []
        for p in itertools.product(range(9),repeat=4):
            meter.charge()
            if all(sum(a*b for a,b in zip(k,p))%9==0 for k in support):
                periods.append(p)
        groups.append({'fixture':name,'torus_period_count_including_zero':len(periods),
                       'sample_periods':[list(p) for p in periods[:5]],
                       'full_space_period_always_present':[9,0,0,0]})
    assert [g['torus_period_count_including_zero'] for g in groups]==[6561,2187,1]

    def dihedral(s,n):
        return min(tuple(sorted((sign*x+t)%n for x in s))
                   for sign in [-1,1] for t in range(n))

    searches = []
    for n in [9,27]:
        seen = {}
        found = None
        count = 0
        words = (tuple(i for i in range(9) if mask>>i&1) for mask in range(512)) if n==9 else itertools.combinations(range(27),4)
        for s in words:
            meter.charge()
            count += 1
            corr = [0]*n
            for a in s:
                for b in s:
                    corr[(a-b)%n] += 1
            key = tuple(corr)
            if key in seen and found is None:
                old = seen[key]
                if dihedral(old,n) != dihedral(s,n):
                    found = (old,s,key)
            else:
                seen.setdefault(key,s)
        row = {'length':n,'enumerated_words':count,'autocorrelation_classes':len(seen),'non_dihedral_pair_found':found is not None}
        if found:
            a,b,corr = found
            x = np.zeros(n);x[list(a)]=1
            y = np.zeros(n);y[list(b)]=1
            assert np.max(abs(abs(np.fft.fft(x))**2-abs(np.fft.fft(y))**2))<1e-10
            witness = None
            for u,v in itertools.combinations(range(1,n),2):
                meter.charge()
                ca=sum(x[t]*x[(t+u)%n]*x[(t+v)%n] for t in range(n))
                cb=sum(y[t]*y[(t+u)%n]*y[(t+v)%n] for t in range(n))
                if ca!=cb and witness is None:witness={'offsets':[0,u,v],'counts':[int(ca),int(cb)]}
            row.update(first_set=list(a),second_set=list(b),exact_autocorrelation=list(corr),triple_witness=witness)
        searches.append(row)
    return {'period_tests':groups,'homometry_search':searches,
            'scope':'Finite periodic arrays and local word counts. No legal geometric tile or infinite nonperiodicity is certified.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase',type=int,choices=[1,2],required=True)
    parser.add_argument('--repo-root',type=Path,required=True)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--ledger',type=Path)
    parser.add_argument('--previous',type=Path)
    parser.add_argument('--worker',action='store_true',help=argparse.SUPPRESS)
    args=parser.parse_args()
    cp=Path(__file__).with_name('contract.json'); contract=json.loads(cp.read_text()); b=contract['budget']
    if args.worker:
        resource.setrlimit(resource.RLIMIT_CPU,(b['cpu_seconds_per_launch'],)*2)
        resource.setrlimit(resource.RLIMIT_AS,(b['address_space_bytes'],)*2)
        meter=Meter(b)
        report={'phase':args.phase,'contract_sha256':digest(cp),'checker_sha256':digest(__file__)}
        try:
            assert __debug__, 'optimized Python disables assertions'
            for pin in contract['input_pins']:assert digest(args.repo_root/pin['path'])==pin['sha256']
            if args.phase==2:
                assert args.previous and json.loads(args.previous.read_text())['status']=='Pass'
                assert json.loads(args.previous.read_text())['phase']==1
                report['preceding_evidence_sha256']=digest(args.previous)
            report['results']=(phase1 if args.phase==1 else phase2)(contract,meter)
            report['status']='Pass'
        except (Limit,MemoryError) as exc:report.update(status='Unknown',reason=str(exc))
        except Exception as exc:
            import traceback
            report.update(status='Failure',reason=repr(exc),traceback=traceback.format_exc())
        report['resources']={'case_units':meter.cases,'wall_seconds':time.monotonic()-meter.start,
                             'cpu_seconds':time.process_time(),'peak_rss_kib_linux':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
        text=json.dumps(report,indent=2)+'\n'
        assert len(text.encode())<=b['max_json_bytes']
        print(text,end='');return
    if not args.output or not args.ledger:parser.error('--output and --ledger required')
    ledger=json.loads(args.ledger.read_text()) if args.ledger.exists() else []
    assert sum(r['phase']==args.phase for r in ledger)<b['launches_per_phase'],'launch budget spent'
    assert not args.output.exists(),'do not overwrite evidence'
    row={'phase':args.phase,'output':str(args.output),'status':'Started'};ledger.append(row)
    args.ledger.write_text(json.dumps(ledger,indent=2)+'\n')
    cmd=[sys.executable,str(Path(__file__).resolve()),'--worker','--phase',str(args.phase),'--repo-root',str(args.repo_root)]
    if args.previous:cmd+=['--previous',str(args.previous)]
    try:
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=b['wall_seconds_per_launch'])
        report=json.loads(r.stdout) if r.returncode==0 else {'status':'Unknown' if r.returncode<0 else 'Failure','returncode':r.returncode,'stderr':r.stderr[:4000]}
    except subprocess.TimeoutExpired:report={'status':'Unknown','reason':'parent wall timeout'}
    args.output.write_text(json.dumps(report,indent=2)+'\n');row['status']=report['status'];row['sha256']=digest(args.output)
    args.ledger.write_text(json.dumps(ledger,indent=2)+'\n')
    print(json.dumps({'phase':args.phase,'status':report['status'],'resources':report.get('resources'),'reason':report.get('reason')}))
    if report['status']!='Pass':raise SystemExit(1)


if __name__=='__main__':main()
