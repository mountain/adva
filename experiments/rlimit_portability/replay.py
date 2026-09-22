"""Opt-in engineering replay; never executes or changes a legacy main().

Original contribution under Unknown v0.3 by ChatGPT (OpenAI).
Prepared for Mingli Yuan; account ownership is not review or endorsement.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def checked_inputs(root=ROOT):
    raw = (HERE / 'contract.json').read_bytes()
    profile = json.loads(raw)
    inputs = {}
    for name, expected in profile['inputs'].items():
        data = (root / name).read_bytes()
        if digest(data) != expected:
            raise ValueError('source/evidence pin mismatch: ' + name)
        inputs[name] = data
    return raw, profile, inputs


def install_limits(host=None, api=resource):
    host = sys.platform if host is None else host
    if host not in ('linux', 'darwin'):
        raise ValueError('unsupported platform')
    # Never turn an installation error into success, including on Linux.
    installed = {}
    for name, value in [('RLIMIT_CPU', 8), ('RLIMIT_FSIZE', 1048576), ('RLIMIT_CORE', 0)]:
        kind = getattr(api, name)
        soft, hard = api.getrlimit(kind)
        cap = value if hard == api.RLIM_INFINITY else min(value, hard)
        if soft != api.RLIM_INFINITY:
            cap = min(cap, soft)
        api.setrlimit(kind, (cap, cap))
        installed[name] = {'status': 'installed', 'value': cap}
    if host == 'linux':
        kind = api.RLIMIT_AS
        soft, hard = api.getrlimit(kind)
        cap = min([256 * 1024**2] + [v for v in (soft, hard) if v != api.RLIM_INFINITY])
        api.setrlimit(kind, (cap, cap))
        installed['RLIMIT_AS'] = {'status': 'installed', 'value': cap}
    else:
        installed['RLIMIT_AS'] = {'status': 'not-installed', 'reason': 'Darwin observation-only memory profile'}
    return installed


def payload(report):
    # Compare every mathematical field, not just a success flag or row count.
    return {k: report[k] for k in ('status', 'frames', 'identities', 'rows',
                                   'controls', 'residual', 'new_native_words')}


def worker():
    started = time.monotonic()
    installed = install_limits()
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError('wall budget')))
    signal.alarm(10)
    raw, profile, inputs = checked_inputs()
    source = 'experiments/frame_covariance/run.py'
    module = types.ModuleType('frozen_frame_covariance')
    module.__file__ = str(ROOT / source)
    # Execute the exact verified bytes, with __name__ != '__main__'.
    exec(compile(inputs[source], module.__file__, 'exec'), module.__dict__)
    contract = json.loads(inputs['experiments/frame_covariance/contract.json'])
    expected = json.loads(inputs['experiments/frame_covariance/evidence.json'])
    observed = module.packed(module.trial(contract))
    equal = payload(observed) == payload(expected)
    if not equal:
        raise AssertionError('frozen mathematical payload differs')
    report = {
        'schema': profile['schema'], 'status': 'ReproducedFinitePayload',
        'profile_sha256': digest(raw), 'runner_sha256': digest(Path(__file__).read_bytes()),
        'input_sha256': profile['inputs'], 'platform': sys.platform, 'python': sys.version,
        'limits': installed, 'original_resource_contract_claim': False,
        'native_admission': 'NotGranted', 'new_research_claim': False,
        'payload_equal': equal, 'payload_sha256': digest(json.dumps(payload(observed), sort_keys=True).encode()),
        'rows': len(observed['rows']), 'logical_checks': module.CHECKS,
        'controls': len(observed['controls']),
        'peak_rss_platform_units': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'peak_rss_unit': 'bytes' if sys.platform == 'darwin' else 'KiB',
        'wall_seconds_before_serialization': time.monotonic() - started,
        'residual': profile['residual'],
    }
    data = json.dumps(report, indent=2, sort_keys=True).encode() + b'\n'
    if len(data) > 1048576:
        raise ValueError('artifact budget')
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()
    # Keep the alarm active through serialization, checkpointing and process exit.


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        worker()
        return 0
    if args.output is None:
        parser.error('--output is required and must be a fresh directory')
    checked_inputs()
    args.output.mkdir(parents=False, exist_ok=False)
    report = {'status': 'Unknown', 'attempts': 1, 'automatic_retries': 0,
              'host': sys.platform, 'darwin_execution': sys.platform == 'darwin'}
    started = time.monotonic()
    with (args.output / 'replay.json').open('xb') as out, (args.output / 'stderr.txt').open('xb') as err:
        proc = subprocess.Popen([sys.executable, '-I', '-B', str(Path(__file__).resolve()), '--worker'],
                                stdin=subprocess.DEVNULL, stdout=out, stderr=err, start_new_session=True)
        try:
            proc.wait(timeout=12)
            report['status'] = 'Completed' if proc.returncode == 0 else 'Failed'
        except subprocess.TimeoutExpired:
            report['reason'] = 'outer wall timeout'
        finally:
            try:
                import os
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()
    report.update(exit_code=proc.returncode, wall_seconds=time.monotonic()-started)
    for name in ('replay.json', 'stderr.txt'):
        report[name + '_sha256'] = digest((args.output / name).read_bytes())
    with (args.output / 'execution.json').open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    return 0 if report['status'] == 'Completed' else 2


if __name__ == '__main__':
    raise SystemExit(main())
