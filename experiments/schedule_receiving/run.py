"""Bounded supervisor. Codex (OpenAI), project-original, Unknown v0.3."""
import copy
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    out = Path(sys.argv[1]).resolve()
    out.mkdir(parents=True, exist_ok=False)
    contract = json.loads((HERE / 'contract.json').read_text())
    start = time.perf_counter()
    records = []
    totals = {'work_units': 0, 'receiver_launches': 0, 'serialization_seconds': 0.0}

    def dump(name, value):
        t = time.perf_counter()
        path = out / name
        path.write_text(json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n')
        totals['serialization_seconds'] += time.perf_counter() - t
        return path

    def limits():
        resource.setrlimit(resource.RLIMIT_AS, (contract['process_address_space_bytes'],) * 2)

    def launch(label, command, build=False):
        t = time.perf_counter()
        p = subprocess.run(command, capture_output=True, text=True,
                           timeout=contract['build_timeout_seconds'] if build else contract['process_timeout_seconds'],
                           preexec_fn=None if build else limits)
        (out / (label + '.stdout')).write_text(p.stdout)
        (out / (label + '.stderr')).write_text(p.stderr)
        # Cumulative child maximum; build is explicitly included.
        records.append({'label': label, 'seconds': time.perf_counter()-t,
                        'exit_code': p.returncode,
                        'cumulative_child_maxrss_kib': resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss})
        if p.returncode:
            raise RuntimeError(label + ' failed')
        return p.stdout

    try:
        cargo = str(Path.home() / '.cargo/bin/cargo')
        launch('build', [cargo, 'build', '--manifest-path', str(HERE / 'Cargo.toml'), '--bins'], True)
        binary = HERE / 'target/debug'
        bundle = json.loads(launch('produce', [str(binary / 'produce')]))
        dump('bundle.json', bundle)
        cases = bundle['cases']
        checks = []
        for case in cases:
            for query, expected in [('all', 'Descends'), ('first', 'NonSaturated')]:
                request = copy.deepcopy(case['request']); request['query'] = query
                checks.append((case['name']+'-'+query, case['archive'], request, expected))
        a, r = cases[0]['archive'], cases[0]['request']
        def control(label, mutate, expected):
            aa, rr = copy.deepcopy(a), copy.deepcopy(r)
            mutate(aa, rr)
            checks.append((label, aa, rr, expected))
        control('wrong-diagram', lambda a,r:a.update(diagram=cases[1]['archive']['diagram']), 'InvalidContext')
        control('wrong-slice', lambda a,r:a.update(slice=cases[1]['archive']['slice']), 'InvalidContext')
        control('wrong-path', lambda a,r:a['receipts'][0]['steps'][0]['result']['after'].update(completed=[]), 'InvalidEvidence')
        control('wrong-word', lambda a,r:a['receipts'][0]['word'].reverse(), 'InvalidEvidence')
        control('incomplete-coverage', lambda a,r:a['receipts'].pop(), 'UnknownCoverage')
        control('duplicate-word', lambda a,r:a['receipts'].append(copy.deepcopy(a['receipts'][0])), 'InvalidEvidence')
        control('wrong-final', lambda a,r:a['receipts'][0].update(final_ideal=[]), 'InvalidEvidence')
        control('unknown-query', lambda a,r:r.update(query='identity'), 'InvalidEvidence')
        results = []
        for label, archive, request, expected in checks:
            if totals['receiver_launches'] >= contract['max_receiver_launches'] or totals['work_units'] + 1000 > contract['max_total_work_units']:
                raise RuntimeError('cumulative budget exhausted before launch')
            ap = dump(label+'.archive.json', archive)
            rp = dump(label+'.request.json', request)
            totals['receiver_launches'] += 1
            result = json.loads(launch(label, [str(binary/'receive'), str(ap), str(rp)]))
            totals['work_units'] += result['work_units']
            assert result['work_units'] <= 1000, result
            assert result['outcome'] == expected, (label, result)
            if expected == 'NonSaturated':
                assert result['left']['final_ideal'] == result['right']['final_ideal']
                assert result['left']['word'][0] != result['right']['word'][0]
            results.append({'label': label, 'expected': expected, 'result': result})
        dump('results.json', results)
        status = 'Passed'
    except Exception as error:
        status = 'ImplementationFailure'
        dump('failure.json', {'type': type(error).__name__, 'message': str(error)})
        raise
    finally:
        dump('execution.json', {'status':status, 'records':records, 'totals':totals,
             'total_seconds':time.perf_counter()-start,
             'supervisor_maxrss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
             'memory_note':'Child maximum includes build; not simultaneous memory. Per-receiver peak not separately measured.',
             'search':'Finite complete permutation coverage, not solver optimization',
             'native_recompilation_in_receiver':False})
        manifest = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file()}
        (out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')


if __name__ == '__main__':
    main()
