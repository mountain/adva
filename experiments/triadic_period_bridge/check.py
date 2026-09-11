#!/usr/bin/env python3
"""Finite correction witnesses for Research 0168, external mathematics only.

Authored by ChatGPT (OpenAI), through Mingli Yuan's account as an authorized
proxy. See contract.json for the imported real-order rules and run budget.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import platform
import resource
import signal
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
RULES = {}
WORK = 0
CHECKS = []


class Exhausted(Exception):
    pass


def tick():
    global WORK
    WORK += 1
    if WORK > RULES['max_work_units_per_child']:
        raise Exhausted('work cap')


def check(name, value):
    tick()
    if len(CHECKS) >= RULES['max_assertions_per_child']:
        raise Exhausted('assertion cap')
    CHECKS.append({'name': name, 'passed': bool(value)})
    if not value:
        raise AssertionError(name)


def mul(a, b):
    out = [0]*(len(a)+len(b)-1)
    if len(out)-1 > RULES['max_polynomial_degree']:
        raise Exhausted('polynomial degree')
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            tick()
            out[i+j] += x*y
    return out


def iterate(f, x, count):
    for _ in range(count):
        tick()
        x = f(x)
    return x


def tent(x):
    if not 0 <= x <= 1:
        raise ValueError('outside tent domain')
    return 2*x if x <= Q(1, 2) else 2-2*x


def orbit(f, a):
    b, c, d = (iterate(f, a, k) for k in (1, 2, 3))
    return (a, b, c, d)


def strict_hypothesis(points):
    a, b, c, d = points
    return d <= a < b < c or d >= a > b > c


def least_periods(table):
    """Return periods of periodic states only; transients are explicitly zero."""
    result = []
    for state in range(len(table)):
        end = state
        period = 0
        for k in range(1, len(table)+1):
            tick()
            end = table[end]
            if end == state:
                period = k
                break
        result.append(period)
    return result


def descend(f, q):
    n = len(f)
    if n > RULES['max_states']:
        raise Exhausted('state cap')
    check('finite-total-map', len(q) == n and all(type(x) is int and 0 <= x < n for x in f))
    check('surjective-quotient-labels', sorted(set(q)) == list(range(max(q)+1)))
    for a in range(n):
        for b in range(a+1, n):
            tick()
            if q[a] == q[b] and q[f[a]] != q[f[b]]:
                return {'status': 'RefusedDescent', 'pair': [a, b],
                        'same_observation': q[a], 'next_observations': [q[f[a]], q[f[b]]]}
    g = [q[f[q.index(v)]] for v in range(max(q)+1)]
    for a in range(n):
        check('quotient-commuting-square', q[f[a]] == g[q[a]])
    periods = least_periods(g)
    return {'status': 'Descends', 'g': g, 'injective': len(set(g)) == len(g),
            'state_least_periods': periods, 'periods': sorted(set(periods)-{0}),
            'interval_theorem': 'RefusedDomainFiniteSet'}


def mathematics(contract):
    witnesses = {}
    # This is a coefficient certificate with explicit sign rules, not sampling
    # all real x. See the correction note for the real zero-exclusion argument.
    poly = [0, 1]
    for _ in range(3):
        poly = mul(poly, poly)
    check('square-third-iterate', poly == [0]*8+[1])
    difference = poly[:]
    difference[1] -= 1
    positive_factor = [1]*7
    factor = mul([0, -1, 1], positive_factor)
    check('square-factor-certificate', difference == factor)
    check('positive-factor-on-nonnegative-reals', positive_factor[0] > 0 and all(x >= 0 for x in positive_factor))
    check('square-negative-region-even-power', (len(poly)-1)%2 == 0 and poly[-1] == 1)
    check('square-collision', Q(-1, 2)**2 == Q(1, 2)**2)
    for x in (0, 1):
        check('square-zero-is-fixed', x*x == x)
    broken = positive_factor[:]
    broken[0] = 2
    check('perturbed-factor-refused', mul([0, -1, 1], broken) != difference)
    witnesses['square'] = {'domain': ['-1', '1'], 'collision': ['-1/2', '1/2'],
        'third_iterate_minus_x_coefficients': difference, 'factors': [[0, -1, 1], positive_factor],
        'real_roots_in_domain': [0, 1], 'least_period_three': False,
        'proof_boundary': 'Coefficient identity plus declared real-order sign argument; no sample extrapolation.'}

    check('tent-continuous-at-join', 2*Q(1, 2) == 2-2*Q(1, 2))
    check('tent-piece-endpoints-in-domain', [tent(Q(x, 2)) for x in range(3)] == [0, 1, 0])
    positive = orbit(tent, Q(2, 7))
    check('tent-exact-orbit', positive == (Q(2, 7), Q(4, 7), Q(6, 7), Q(2, 7)))
    check('tent-strict-Li-Yorke-hypothesis', strict_hypothesis(positive))
    check('tent-minimal-period-three', positive[0] == positive[3] and len(set(positive[:3])) == 3)
    check('tent-fixed-point-refuses-strict-hypothesis', not strict_hypothesis(orbit(tent, Q(2, 3))))
    check('identity-cube-is-not-minimal-period-three', not strict_hypothesis(orbit(lambda x: x, Q(1, 2))))
    witnesses['tent'] = {'orbit': [str(x) for x in positive],
        'status': 'ImportedIntervalHypothesisSatisfied', 'all_periods_enumerated': False,
        'fixed_point_control': [str(x) for x in orbit(tent, Q(2, 3))]}

    # Encode (phase, value) as 2*phase+value. None are Adva identities.
    step = [2*((i//2+1)%3)+i%2 for i in range(6)]
    q = [i%2 for i in range(6)]
    return_map = [iterate(lambda x: step[x], i, 3) for i in range(6)]
    check('role-step-period-three', least_periods(step) == [3]*6)
    check('full-cycle-return-identity', return_map == list(range(6)))
    check('full-cycle-return-period-one', least_periods(return_map) == [1]*6)
    role_quotient = descend(step, q)
    check('forget-phase-identity', role_quotient['g'] == [0, 1])
    check('finite-role-cycle-refuses-interval-theorem', role_quotient['interval_theorem'] == 'RefusedDomainFiniteSet')
    witnesses['roles'] = {'S': step, 'S_cubed': return_map, 'phase_zero_return': return_map[:2],
        'forget_phase': q, 'quotient': role_quotient}

    quotient_rows = []
    for fixture in contract['fixtures']['quotients']:
        answer = descend(fixture['F'], fixture['q'])
        check('quotient-'+fixture['name'], answer['status'] == fixture['expected'])
        if answer['status'] == 'Descends':
            check('derived-not-injected-quotient', answer['g'] == fixture['g'])
            check('quotient-periods', answer['periods'] == fixture['periods'])
        else:
            a, b = answer['pair']
            check('descent-failure-witness', fixture['q'][a] == fixture['q'][b] and
                  fixture['q'][fixture['F'][a]] != fixture['q'][fixture['F'][b]])
        quotient_rows.append({'name': fixture['name'], 'F': fixture['F'], 'q': fixture['q'], 'result': answer})
    witnesses['quotients'] = quotient_rows

    histories = [(first,)+(0,)*(length-1) for length in range(1, RULES['max_history_length']+1)
                 for first in range(2)]
    images = [h+(0,) for h in histories]
    check('history-append-injective-on-finite-profile', len(set(images)) == len(histories))
    for h, image in zip(histories, images):
        check('history-prefix-recovery', image[:-1] == h)
        check('history-projection-commutes', image[-1] == 0)
        check('history-length-increases', len(image) == len(h)+1)
    check('singleton-has-no-append-preimage', all(len(h)+1 >= 2 for h in histories))
    witnesses['history'] = {'base_F': [0, 0], 'histories': histories, 'images': images,
        'no_preimage_singleton': [0], 'global_reason': 'Every nonempty history gains one entry; a singleton cannot be an image.',
        'scope': 'Prefix recovery on the finite profile and the stated length argument; no two-sided inverse or chaos verdict.'}
    encoded = json.dumps(witnesses, sort_keys=True)
    decoded = json.loads(encoded)
    check('JSON-witness-roundtrip', json.dumps(decoded, sort_keys=True) == encoded)
    return decoded


def alarm(signum, frame):
    raise Exhausted('wall or CPU limit')


def install(role):
    if platform.system() != 'Linux':
        raise Exhausted('Linux limit semantics required')
    memory = RULES['address_space_bytes_per_process']
    resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
    resource.setrlimit(resource.RLIMIT_CPU, (RULES[role+'_cpu_soft_seconds'], RULES[role+'_cpu_hard_seconds']))
    resource.setrlimit(resource.RLIMIT_FSIZE, (RULES['max_artifact_bytes'], RULES['max_artifact_bytes']))
    signal.signal(signal.SIGALRM, alarm)
    signal.signal(signal.SIGXCPU, alarm)
    signal.alarm(RULES[role+'_alarm_seconds'])


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def publish(path, value, replace=False):
    raw = (json.dumps(value, sort_keys=True, indent=2)+'\n').encode()
    if len(raw) > RULES['max_artifact_bytes']:
        raise Exhausted('artifact bytes')
    if replace:
        tmp = path.with_suffix('.pending.json')
        with tmp.open('xb') as f:
            f.write(raw)
        tmp.replace(path)
    else:
        with path.open('xb') as f:
            f.write(raw)


def child(contract, output, compare):
    start = time.monotonic()
    report = {'schema': 'adva.external.triadic-period-bridge.v0', 'status': 'UnknownResource',
              'source_sha256': digest(Path(__file__).read_bytes()),
              'contract_sha256': digest((HERE/'contract.json').read_bytes()),
              'native_authority': 'NotGranted', 'limits_installed': False}
    try:
        install('child')  # Failure is fatal to the trial, not a passing warning.
        report['limits_installed'] = True
        report['witnesses'] = mathematics(contract)
        if compare:
            raw = compare.read_bytes()
            if len(raw) > RULES['max_artifact_bytes']:
                raise Exhausted('comparison bytes')
            prior = json.loads(raw)
            check('fresh-process-full-witness-replay', prior['status'] == 'Passed' and
                  prior['witnesses'] == report['witnesses'] and
                  prior['source_sha256'] == report['source_sha256'] and
                  prior['contract_sha256'] == report['contract_sha256'])
        report['status'] = 'Passed'
    except (Exhausted, MemoryError) as error:
        report['reason'] = str(error)
    except Exception as error:
        report['status'], report['reason'] = 'Failed', type(error).__name__+': '+str(error)
    report['checks'] = CHECKS
    report['cost'] = {'work_units': WORK, 'assertions': len(CHECKS),
                      'before_publication_seconds': time.monotonic()-start,
                      'peak_rss_KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    publish(output, report)
    print(json.dumps({'status': report['status'], 'through_publication_seconds': time.monotonic()-start}))
    return 0 if report['status'] == 'Passed' else 1


def session(contract, folder):
    start = time.monotonic()
    install('supervisor')
    folder.mkdir(parents=True, exist_ok=True)
    ledger_path = folder/'execution.json'
    ledger = {'schema': 'adva.external.triadic-period-bridge-session.v0', 'status': 'Running',
              'source_sha256': digest(Path(__file__).read_bytes()),
              'contract_sha256': digest((HERE/'contract.json').read_bytes()),
              'supervisor_limits_installed': True, 'attempts': []}
    publish(ledger_path, ledger)  # Exclusive reservation; an old session is not resumed.
    for ordinal, name in enumerate(('attempt-01.json', 'replay-01.json'), 1):
        if ordinal > RULES['max_children']:
            raise Exhausted('child count')
        output = folder/name
        entry = {'ordinal': ordinal, 'output': name, 'status': 'Running'}
        ledger['attempts'].append(entry)
        publish(ledger_path, ledger, replace=True)
        command = [sys.executable, '-B', '-S', str(Path(__file__).resolve()), '--child', str(output)]
        if ordinal == 2:
            command += ['--compare', str(folder/'attempt-01.json')]
        tick_start = time.monotonic()
        try:
            process = subprocess.run(command, capture_output=True, text=True, timeout=RULES['child_outer_seconds'])
            entry.update(returncode=process.returncode, stdout=process.stdout[:4096], stderr=process.stderr[:4096])
        except subprocess.TimeoutExpired:
            entry.update(returncode=124, stdout='', stderr='Outer timeout; child killed')
        entry['elapsed_seconds'] = time.monotonic()-tick_start
        entry['status'] = 'Finished'
        entry['report_exists'] = output.exists()
        if output.exists():
            entry['report_sha256'] = digest(output.read_bytes())
        publish(ledger_path, ledger, replace=True)
        if entry['returncode'] != 0:
            ledger['status'] = 'FailedOrUnknown'
            break
    else:
        ledger['status'] = 'Passed'
    ledger['before_final_checkpoint_seconds'] = time.monotonic()-start
    publish(ledger_path, ledger, replace=True)
    total = sum(p.stat().st_size for p in folder.glob('*.json'))
    if total > RULES['max_session_artifact_bytes']:
        raise Exhausted('aggregate artifact bytes')
    print(json.dumps({'status': ledger['status'], 'through_final_checkpoint_seconds': time.monotonic()-start,
                      'artifact_bytes': total, 'attempts': len(ledger['attempts'])}))
    return 0 if ledger['status'] == 'Passed' else 1


def main():
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--session', type=Path)
    modes.add_argument('--child', type=Path)
    parser.add_argument('--compare', type=Path)
    args = parser.parse_args()
    raw = (HERE/'contract.json').read_bytes()
    if len(raw) > 32768:
        raise Exhausted('contract bytes')
    contract = json.loads(raw)
    RULES.update(contract['budget'])
    return session(contract, args.session.resolve()) if args.session else child(contract, args.child, args.compare)


if __name__ == '__main__':
    raise SystemExit(main())
