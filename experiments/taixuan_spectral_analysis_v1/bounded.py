"""Bounded external research runner. Codex (OpenAI), Unknown v0.3."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import subprocess
import sys
import time


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--contract', type=Path, required=True)
    p.add_argument('--input-root', type=Path, required=True)
    p.add_argument('--output', type=Path)
    p.add_argument('--ledger', type=Path)
    p.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    a = p.parse_args()
    c = json.loads(a.contract.read_text())
    b = c['budget']
    module_path = a.contract.parent / c['worker']
    if a.worker:
        resource.setrlimit(resource.RLIMIT_CPU, (b['cpu_seconds'],)*2)
        resource.setrlimit(resource.RLIMIT_AS, (b['address_space_bytes'],)*2)
        resource.setrlimit(resource.RLIMIT_FSIZE, (b['max_json_bytes'],)*2)
        start = time.monotonic()
        result = {'contract_sha256': digest(a.contract), 'runner_sha256': digest(__file__),
                  'worker_sha256': digest(module_path)}
        try:
            assert __debug__, 'optimized Python is unsupported'
            assert digest(module_path) == c['worker_sha256']
            assert digest(__file__) == c['runner_sha256']
            for pin in c['local_evidence']:
                path = a.contract.parent / pin['path']
                assert digest(path) == pin['sha256'], str(path)
                assert json.loads(path.read_text())['status'] == 'Pass'
            spec = importlib.util.spec_from_file_location('spectral_worker', module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            result.update(status='Pass', results=module.run(c, a.input_root))
        except FileNotFoundError as exc:
            result.update(status='Unavailable', reason=str(exc))
        except MemoryError:
            result.update(status='Unknown', reason='memory limit')
        except Exception as exc:
            import traceback
            result.update(status='Failure', reason=repr(exc), traceback=traceback.format_exc())
        result['resources'] = {'wall_seconds': time.monotonic()-start,
                               'cpu_seconds': time.process_time(),
                               'peak_rss_kib_linux': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
        encoded = json.dumps(result, indent=2)+'\n'
        if len(encoded.encode()) > b['max_json_bytes']:
            encoded = json.dumps({'status':'Unknown', 'reason':'output limit'})
        print(encoded, end='')
        return
    if not a.output or not a.ledger:
        p.error('--output and --ledger required')
    rows = json.loads(a.ledger.read_text()) if a.ledger.exists() else []
    assert len(rows) < b['launches'], 'launch budget spent'
    with a.output.open('x') as stream:
        stream.write('{"status":"Started"}\n')
    row = {'contract_sha256':digest(a.contract), 'output':str(a.output), 'status':'Started'}
    rows.append(row)
    a.ledger.write_text(json.dumps(rows, indent=2)+'\n')
    command = [sys.executable, str(Path(__file__).resolve()), '--worker', '--contract',
               str(a.contract.resolve()), '--input-root', str(a.input_root.resolve())]
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=b['wall_seconds'])
        if proc.returncode == 0:
            result = json.loads(proc.stdout)
        else:
            result = {'status':'Unknown' if proc.returncode < 0 else 'Failure',
                      'returncode':proc.returncode, 'stderr':proc.stderr[:4000]}
    except subprocess.TimeoutExpired:
        result = {'status':'Unknown', 'reason':'wall limit'}
    a.output.write_text(json.dumps(result, indent=2)+'\n')
    row.update(status=result['status'], sha256=digest(a.output))
    a.ledger.write_text(json.dumps(rows, indent=2)+'\n')
    print(json.dumps({'status':result['status'], 'resources':result.get('resources'),
                      'reason':result.get('reason')}))
    if result['status'] != 'Pass':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
