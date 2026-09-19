"""Reproduce the finite murphy publication unit without native Adva execution.

Authored by ChatGPT (OpenAI); original contribution under Unknown v0.3.
Python 3.10+, Node.js, POSIX resource limits. Fresh output is mandatory.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--repository', type=Path, default=HERE.parents[1])
    args = parser.parse_args()
    out, repo = args.output.resolve(), args.repository.resolve()
    out.mkdir(parents=True, exist_ok=False)
    contract = load(HERE/'contract.json')
    limits = contract['limits']
    started = time.monotonic()
    result = {'schema': 'adva.murphy.publication-result.v1', 'native_runs': 0,
              'contract_sha256': sha(HERE/'contract.json'), 'stages': [], 'checks': []}
    def need(ok, name):
        if not ok:
            raise AssertionError(name)
        result['checks'].append(name)
    def run(name, command):
        seconds = min(limits['max_seconds_per_child'],
                      limits['total_wall_seconds']-(time.monotonic()-started))
        if seconds <= 0:
            raise TimeoutError('total publication budget exhausted')
        def bounded():
            resource.setrlimit(resource.RLIMIT_CPU, (limits['max_cpu_seconds_per_child'],)*2)
            resource.setrlimit(resource.RLIMIT_FSIZE, (limits['max_output_file_bytes'],)*2)
            if command[0] == sys.executable:
                resource.setrlimit(resource.RLIMIT_AS, (limits['python_address_space_bytes'],)*2)
        try:
            p = subprocess.run([str(x) for x in command], capture_output=True, timeout=seconds,
                               preexec_fn=bounded, cwd=HERE)
        except subprocess.TimeoutExpired as error:
            (out/(name+'.stdout')).write_bytes(error.stdout or b'')
            (out/(name+'.stderr')).write_bytes(error.stderr or b'')
            result['stages'].append({'stage': name, 'status': 'Unknown', 'reason': 'timeout'})
            raise TimeoutError(name+' exceeded remaining wall budget') from error
        (out/(name+'.stdout')).write_bytes(p.stdout)
        (out/(name+'.stderr')).write_bytes(p.stderr)
        result['stages'].append({'stage': name, 'returncode': p.returncode})
        if p.returncode:
            # Do not relabel a child's explicit Unknown as a mathematical failure.
            for directory in (name,):
                record = out/directory/'result.json'
                if record.exists() and load(record).get('status') == 'Unknown':
                    raise TimeoutError(name+' reported Unknown')
            if p.returncode < 0:
                raise TimeoutError(name+' terminated by a resource signal')
            raise RuntimeError(name+' failed; inspect retained stdout/stderr/result')
    try:
        name = load(HERE/'murphy.json')
        need(sha(HERE/'murphy.iota') == name['iota_sha256'], 'named program digest')
        need((HERE/'murphy.iota').read_bytes() == (HERE/'inputs/P.iota').read_bytes(), 'murphy aliases P exactly')
        need(len((HERE/'murphy.iota').read_text().strip()) == 823, 'murphy character count')
        zot = repo/'experiments/zot_prefix_machine'
        node = ['node', '--max-old-space-size='+str(limits['node_max_old_space_mib'])]
        run('zot', [*node, HERE/'zot_trace.cjs', zot/'machine.cjs', zot/'reference-zot.js', out/'zot-trace.json'])
        actual, frozen = load(out/'zot-trace.json'), load(HERE/'evidence/zot-trace.json')
        actual.pop('runtime'); frozen.pop('runtime')
        need(actual == frozen, 'all 125 Zot transition records replay exactly excluding host runtime label')
        run('translation', [sys.executable, HERE/'zot_to_iota.py', out/'zot-trace.json', out/'translation'])
        need((out/'translation/zot_0001011011_value.iota').read_bytes() == (HERE/'murphy.iota').read_bytes(),
             'fresh Zot-to-Iota translation matches named program')
        fresh = load(out/'translation/zot_0001011011_iota_evidence.json')
        frozen = load(HERE/'evidence/translation.json')
        need(all(frozen[k] == v for k,v in fresh.items()), 'translation evidence matches retained projection')
        run('cbv', [*node, HERE/'verify_iota_cbv.cjs', HERE/'murphy.iota'])
        cbv = load(out/'cbv.stdout')
        need(cbv['printerInvocations'] == 0 and cbv['K4IProbe'], 'independent eager Iota wrapper observation')
        run('research', [sys.executable, HERE/'research.py', '--output', out/'research'])
        fresh, frozen = load(out/'research/result.json'), load(HERE/'evidence/result.json')
        need(fresh['status'] == 'CheckedWithinDeclaredScope', 'research completed')
        fresh.pop('wall_seconds'); frozen.pop('wall_seconds')
        need(fresh == frozen, 'all 400 base checks and witnesses replay excluding elapsed time')
        for filename in ['PP.iota','C.iota','J.iota','N.iota','PP-trace.json']:
            need((out/'research'/filename).read_bytes() == (HERE/'evidence'/filename).read_bytes(), filename+' byte replay')
        run('adjoint', [sys.executable, HERE/'adjoint.py', '--base', out/'research', '--output', out/'adjoint'])
        fresh, frozen = load(out/'adjoint/result.json'), load(HERE/'adjoint_evidence/result.json')
        need(fresh.pop('base_result_sha256') == sha(out/'research/result.json'), 'new adjoint binds new base result')
        need(frozen.pop('base_result_sha256') == sha(HERE/'evidence/result.json'), 'old adjoint binds old base result')
        need(fresh == frozen, 'all 16 adjoint checks replay excluding verified timing-derived digest')
        for filename in ['transpose2.iota','conjugate2.iota','adjoint2.iota']:
            need((out/'adjoint'/filename).read_bytes() == (HERE/'adjoint_evidence'/filename).read_bytes(), filename+' byte replay')
        run('text', [sys.executable, HERE/'text_probe.py', '--output', out/'text'])
        text = load(out/'text/result.json')
        need(text['status'] == 'CheckedWithinDeclaredScope', 'text probe completed')
        need([c['contractions'] for c in text['cases']] == [898,1813,823,1645], 'four previously observed text counts')
        need(not text['C_twice_equals_input'], 'coordinate conjugation law does not extend to this character chain')
        expected_text = HERE/'evidence/text-probe.json'
        if expected_text.exists():
            need(text == load(expected_text), 'frozen text probe replays exactly')
        else:
            result['text_evidence_mode'] = 'first retained publication capture of the already observed cases'
        result['status'] = 'CheckedWithinDeclaredScope'
    except (TimeoutError, FileNotFoundError) as error:
        result.update(status='Unknown', reason=str(error))
    except Exception as error:
        result.update(status='Failed', reason=repr(error))
    result['wall_seconds'] = time.monotonic()-started
    (out/'publication-result.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'CheckedWithinDeclaredScope' else 1


if __name__ == '__main__':
    raise SystemExit(main())
