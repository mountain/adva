#!/usr/bin/env python3
"""Exact finite interval-extension audit; see contract.json.

ChatGPT (OpenAI), through Mingli Yuan's account as an authorized proxy.
The session supervisor is adapted from the byte-pinned preceding experiment.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import itertools
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


class Refused(Exception):
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


def compile_map(raw):
    if not 2 <= len(raw) <= RULES['max_nodes']:
        raise Refused('RefusedNodeCount')
    nodes = [(Q(x), Q(y)) for x, y in raw]
    if any(x >= y for (x, _), (y, _) in zip(nodes, nodes[1:])):
        raise Refused('RefusedNodeOrder')
    low, high = nodes[0][0], nodes[-1][0]
    if any(not low <= y <= high for _, y in nodes):
        raise Refused('RefusedSelfMap')
    pieces = []
    for (x, y), (u, v) in zip(nodes, nodes[1:]):
        a = (v-y)/(u-x)
        b = y-a*x
        check('affine-shared-endpoints', a*x+b == y and a*u+b == v)
        pieces.append((x, u, a, b))
    return pieces


def evaluate(pieces, x):
    tick()
    for lo, hi, a, b in pieces:
        if lo <= x <= hi:
            return a*x+b
    raise Refused('RefusedEvaluationDomain')


def bind(pieces, embedding, g):
    if len(set(embedding)) != len(g) or any(evaluate(pieces, x) != embedding[g[i]]
                                         for i, x in enumerate(embedding)):
        raise Refused('RefusedOrbitBinding')


def periodic_points(pieces, depth):
    """Exhaust every affine branch word; no root scan or tolerance is used."""
    if not 1 <= depth <= RULES['max_depth']:
        raise Exhausted('depth')
    roots = {}
    counts = {'words': 0, 'empty_domains': 0, 'no_root': 0, 'duplicate_roots': 0}
    for word in itertools.product(range(len(pieces)), repeat=depth):
        counts['words'] += 1
        tick()
        lo, hi = pieces[0][0], pieces[-1][1]
        A, B = Q(1), Q(0)
        for letter in word:
            tick()
            lower, upper, a, b = pieces[letter]
            if A == 0:
                if not lower <= B <= upper:
                    lo, hi = Q(1), Q(0)
                    break
            else:
                u, v = sorted(((lower-B)/A, (upper-B)/A))
                lo, hi = max(lo, u), min(hi, v)
                if lo > hi:
                    break
            A, B = a*A, a*B+b
        if lo > hi:
            counts['empty_domains'] += 1
            continue
        if A == 1:
            if B != 0:
                counts['no_root'] += 1
                continue
            if lo < hi:
                raise Refused('RefusedNonisolatedPeriodicInterval')
            x = lo
        else:
            x = -B/(A-1)
        if not lo <= x <= hi:
            counts['no_root'] += 1
            continue
        check('root-affine-equation', A*x+B == x)
        y = x
        first_return = None
        for k in range(1, depth+1):
            y = evaluate(pieces, y)
            if y == x and first_return is None:
                first_return = k
        check('direct-orbit-rechecks-root', y == x)
        check('least-period-divides-iterate', first_return is not None and depth%first_return == 0)
        if x in roots:
            counts['duplicate_roots'] += 1
        else:
            roots[x] = {'point': str(x), 'least_period': first_return, 'branch_word': list(word),
                        'initial_interval': [str(lo), str(hi)], 'iterate_affine': [str(A), str(B)]}
    check('complete-itinerary-count', counts['words'] == len(pieces)**depth)
    check('all-words-accounted', sum(counts[k] for k in ('empty_domains', 'no_root', 'duplicate_roots'))+len(roots) == counts['words'])
    return {'depth': depth, 'counts': counts, 'roots': [roots[x] for x in sorted(roots)]}


def mathematics(contract):
    source = HERE.parent.parent/contract['input']['path']
    raw = source.read_bytes()
    check('input-byte-cap', len(raw) <= RULES['max_artifact_bytes'])
    blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    check('source-report-byte-pin', blob == contract['input']['git_blob'])
    inputs = json.loads(raw)
    selected = [c for c in inputs['witnesses']['quotients'] if c['name'] == 'descent-finite-three-cycle']
    check('unique-source-fixture', len(selected) == 1)
    f, q = selected[0]['F'], selected[0]['q']
    check('frozen-source-tables', f == [2,3,4,5,0,1] and q == [0,0,1,1,2,2])
    for i in range(len(q)):
        for j in range(len(q)):
            check('source-fibre-constancy', q[i] != q[j] or q[f[i]] == q[f[j]])
    g = [q[f[q.index(i)]] for i in range(3)]
    check('rederived-quotient', g == [1,2,0])
    check('source-only-period-three', all(g[i] != i and g[g[i]] != i and g[g[g[i]]] == i for i in range(3)))
    answer = {'source': {'F': f, 'q': q, 'g': g, 'periods': [3]}, 'maps': [], 'controls': []}
    check('frozen-six-map-profile', len(contract['fixtures']) == 6)
    all_pieces = []
    for fixture in contract['fixtures']:
        pieces = compile_map(fixture['nodes'])
        all_pieces.append(pieces)
        row = {'name': fixture['name'], 'nodes': fixture['nodes'],
               'pieces': [[str(v) for v in p] for p in pieces]}
        if 'embedding' in fixture:
            embedding = [Q(x) for x in fixture['embedding']]
            bind(pieces, embedding, g)
            row['embedding'] = fixture['embedding']
            a, b, c = embedding
            d = evaluate(pieces, c)
            check('strict-period-three-hypothesis', d <= a < b < c or d >= a > b > c)
            row['theorem_boundary'] = 'ImportedSharkovskyHypothesisSatisfiedForExtension'
            missing = (pieces[0][0]+pieces[0][1])/2
            check('embedding-omits-interval-point', missing not in embedding)
            row['point_outside_embedding'] = str(missing)
        else:
            x = Q(fixture['fixed_observation'])
            check('singleton-observation-preserved', evaluate(pieces, x) == x)
            row['fixed_observation'] = str(x)
            if 'period_three_start' in fixture:
                a = Q(fixture['period_three_start'])
                b = evaluate(pieces, a)
                c = evaluate(pieces, b)
                d = evaluate(pieces, c)
                check('singleton-tent-period-three', d == a and len({a,b,c}) == 3)
                row['period_three_orbit'] = [str(v) for v in (a,b,c,d)]
        row['iterates'] = [periodic_points(pieces, n) for n in range(1, RULES['max_depth']+1)]
        answer['maps'].append(row)
    def points(row, depth, exact=False):
        return {Q(r['point']) for r in row['iterates'][depth-1]['roots']
                if not exact or r['least_period'] == depth}
    linear, bent = answer['maps'][:2]
    check('linear-fixed-point', points(linear, 1) == {Q(4,3)})
    check('linear-two-cycle', points(linear, 2, True) == {Q(2,3), Q(5,3)})
    check('bent-two-cycle', points(bent, 2, True) == {Q(12,17), Q(28,17)})
    check('new-periodic-points-not-source-states', not (points(linear, 1)|points(linear, 2, True)) & {Q(0),Q(1),Q(2)})
    check('same-source-distinct-extensions', evaluate(all_pieces[0], Q(1,2)) != evaluate(all_pieces[1], Q(1,2)))
    for index in (2,3):
        a,b = map(Q, contract['fixtures'][index]['transport'])
        transported_nodes = sorted((a*Q(x)+b, a*Q(y)+b) for x,y in contract['fixtures'][0]['nodes'])
        check('affine-conjugacy-piece-data', transported_nodes == [(Q(x),Q(y)) for x,y in contract['fixtures'][index]['nodes']])
        for n in range(1, RULES['max_depth']+1):
            check('all-fixed-points-transport', {a*x+b for x in points(linear,n)} == points(answer['maps'][index],n))
            check('least-periods-transport', {a*x+b for x in points(linear,n,True)} == points(answer['maps'][index],n,True))
    for n in range(1,RULES['max_depth']+1):
        check('constant-only-fixed-point', points(answer['maps'][4],n) == {Q(0)})
        check('tent-exact-fixed-count', len(points(answer['maps'][5],n)) == 2**n)
        for row in answer['maps'][:4]:
            check('extension-has-each-tested-least-period', bool(points(row,n,True)))
    controls = [
        ('node-order', lambda: compile_map([['0','0'],['0','0']]), 'RefusedNodeOrder'),
        ('image-outside', lambda: compile_map([['0','0'],['1','2']]), 'RefusedSelfMap'),
        ('source-orbit-mismatch', lambda: bind(compile_map([['0','1'],['2','0']]), [Q(0),Q(1),Q(2)], g), 'RefusedOrbitBinding'),
        ('identity-interval', lambda: periodic_points(compile_map([['0','0'],['1','1']]), 1), 'RefusedNonisolatedPeriodicInterval')]
    for name, action, expected in controls:
        try:
            action()
        except Refused as error:
            check('control-'+name, str(error) == expected)
            answer['controls'].append({'name': name, 'status': str(error)})
        else:
            raise AssertionError('control accepted: '+name)
    encoded = json.dumps(answer,sort_keys=True)
    check('JSON-witness-roundtrip', json.dumps(json.loads(encoded),sort_keys=True) == encoded)
    return answer


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
    report = {'schema': 'adva.external.sharkovsky-interval-extension.v0', 'status': 'UnknownResource',
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
    ledger = {'schema': 'adva.external.sharkovsky-interval-extension-session.v0', 'status': 'Running',
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
