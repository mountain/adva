"""One bounded campaign; Codex (OpenAI), Unknown v0.3. No native Python authority."""
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
    logs, results = [], []
    account = {'launches': 0, 'counted_units': 0, 'serialization_seconds': 0.0}
    status = 'ImplementationFailure'

    def write(name, data):
        t = time.perf_counter()
        p = out / name
        p.write_text(json.dumps(data, sort_keys=True, separators=(',', ':')) + '\n')
        account['serialization_seconds'] += time.perf_counter() - t
        return p

    def launch(label, command, build=False):
        assert account['launches'] < contract['max_processes_including_build']
        assert account['counted_units'] + 2000 <= contract['total_counted_units']
        account['launches'] += 1
        t = time.perf_counter()
        p = subprocess.run(command, capture_output=True, text=True, timeout=contract['build_timeout_seconds'] if build else contract['runtime_timeout_seconds'])
        (out / (label + '.stdout')).write_text(p.stdout)
        (out / (label + '.stderr')).write_text(p.stderr)
        logs.append({'label': label, 'wall_seconds': time.perf_counter()-t, 'returncode': p.returncode})
        assert p.returncode == 0, (label, p.stderr)
        if build:
            return None
        data = json.loads(p.stdout)
        units = sum(data.get(k, {}).get('counted_units', 0) for k in ('cost', 'verification_cost', 'baseline_cost'))
        account['counted_units'] += units
        assert units <= 2000, (label, units)
        return data

    try:
        cargo = str(Path.home() / '.cargo/bin/cargo')
        launch('build', [cargo, 'build', '--manifest-path', str(HERE/'Cargo.toml')], True)
        target = Path(os.environ.get('CARGO_TARGET_DIR', str(HERE/'target')))
        binary = str(target / 'debug/schedule-prefix')
        old = json.loads((ROOT/'experiments/schedule_receiving/evidence/attempt-1/bundle.json').read_text())
        cases = [(c['name'], {'diagram':c['archive']['diagram'], 'diagram_hash':c['request']['diagram_hash']}) for c in old['cases']]
        cases.append(('two-chains', launch('fresh', [binary, 'fresh'])))
        produced = []
        for name, data in cases:
            input_path = write(name+'.input.json', data)
            tree = launch(name+'-produce', [binary, 'produce', str(input_path)])
            tree_path = write(name+'.tree.json', tree)
            result = launch(name+'-verify', [binary, 'verify', str(input_path), str(tree_path)])
            assert result['outcome'] == 'Verified', result
            assert result['first_query']['outcome'] == 'NonSaturated', result
            assert result['whole_query'] == 'Descends', result
            assert len(result['legal_words']) == {'diamond':2,'three':6,'delayed':2,'two-chains':6}[name]
            assert result['naive_cut_dedup']['lost_histories'] == len(result['legal_words'])-1
            results.append({'name':name, 'producer_cost':tree['cost'], 'result':result})
            produced.append((input_path, tree))
        input_path, tree = produced[0]
        controls = []
        def mutate(name, function, expected):
            candidate = copy.deepcopy(tree)
            function(candidate)
            controls.append((name, candidate, expected))
        mutate('missing-edge', lambda t:t['records'][0]['edges'].pop(), 'UnknownCoverage')
        mutate('missing-leaf', lambda t:t['records'].pop(), 'UnknownCoverage')
        mutate('wrong-cut', lambda t:t['records'][1].update(cut=[]), 'InvalidEvidence')
        mutate('forged-step', lambda t:t['records'][0]['edges'][0]['step']['result']['after'].update(completed=[]), 'InvalidEvidence')
        mutate('duplicate-prefix', lambda t:t['records'].append(copy.deepcopy(t['records'][0])), 'InvalidEvidence')
        mutate('wrong-binding', lambda t:t.update(diagram_hash='wrong'), 'InvalidContext')
        def collapse(t):
            unique = {}
            for record in t['records']:
                unique.setdefault(tuple(record['cut']), record)
            t['records'] = list(unique.values())
        mutate('cut-dedup', collapse, 'UnknownCoverage')
        mutate('unreachable-prefix', lambda t:t['records'].append({'word':[999], 'cut':[], 'edges':[]}), 'InvalidEvidence')
        for name, candidate, expected in controls:
            p = write(name+'.tree.json', candidate)
            result = launch(name, [binary, 'verify', str(input_path), str(p)])
            assert result['outcome'] == expected, (name, result)
            results.append({'name':name, 'expected':expected, 'result':result})
        status = 'Passed'
    except Exception as error:
        write('failure.json', {'type':type(error).__name__, 'message':str(error)})
        raise
    finally:
        write('results.json', results)
        write('execution.json', {'status':status,'account':account,'processes':logs,
              'wall_seconds':time.perf_counter()-start,
              'supervisor_peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              'all_children_peak_rss_kib_including_build':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
              'memory_scope':'Native process VmHWM in each output; build included only in aggregate child high-water mark; no hard memory cap'})
        sources = ['contract.json', 'Cargo.toml', 'Cargo.lock', 'src/main.rs', 'run.py']
        write('sources.json', {p:hashlib.sha256((HERE/p).read_bytes()).hexdigest() for p in sources if (HERE/p).exists()})
        manifest = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file()}
        (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')


if __name__ == '__main__':
    main()
