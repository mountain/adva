#!/usr/bin/env python3
"""One pinned iota process on a three-dimensional cubical subgraph.

Original contribution by Codex (OpenAI), Unknown v0.3, through Mingli Yuan's
authorized account proxy. External research evidence, not native admission.
"""
import argparse
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import resource
import signal
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


class Refused(ValueError):
    pass


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


class Budget:
    def __init__(self, limits):
        self.limits = limits
        self.work = self.assertions = 0

    def tick(self, n=1):
        self.work += n
        if self.work > self.limits['counted_work_per_check']:
            raise TimeoutError('counted work exhausted')

    def require(self, condition, reason):
        self.tick()
        self.assertions += 1
        if not condition:
            raise Refused(reason)


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def binding(f):
    return {
        'family_sha256': digest(canonical(f)),
        'history_sha256': digest(canonical(f['events'])),
        'entry_roles': f['entry_roles'], 'exit_roles': f['exit_roles'],
        'clocks': f['clocks'], 'final_apertures': f['final_apertures'],
        'ancestry_reference': f['full_process_sha256'],
        'residual': ['directed events', 'copy/discard history',
                     'domain policies', 'full ancestry remains external'],
        'operator_parameter': 'dimensionless; distinct from event clock',
        'metric_and_observer': 'identity in the sorted cut basis',
    }


def propose(f):
    return {
        'schema': 'adva.research.iota-grid-candidate.v0',
        'binding': binding(f),
        'vertices': [{'mask': c['mask'],
                      'position': [(c['mask'] >> i) & 1 for i in range(3)],
                      'term': c['term']} for c in f['cuts']],
        'edges': deepcopy(f['edges']),
    }


def receive(candidate, f, budget):
    """Reconstruct causal cuts and grid adjacency; source reduction is separate."""
    need = budget.require
    need(set(candidate) == {'schema', 'binding', 'vertices', 'edges'}, 'candidate fields')
    need(candidate['schema'] == 'adva.research.iota-grid-candidate.v0', 'candidate schema')
    need(candidate['binding'] == binding(f), 'process or observation binding changed')
    need(len(f['events']) == 3, 'three-event scope')
    vertices = candidate['vertices']
    need(len(vertices) == 6 and len(candidate['edges']) == 7, 'six-vertex seven-edge scope')
    terms = {c['mask']: c['term'] for c in f['cuts']}
    legal = set()
    for pos in itertools.product((0, 1), repeat=3):
        budget.tick()
        if all(not pos[i] or all(pos[d] for d in e['deps'])
               for i, e in enumerate(f['events'])):
            legal.add(pos)
    positions, masks = set(), set()
    for v in vertices:
        need(set(v) == {'mask', 'position', 'term'}, 'vertex fields')
        pos = v['position']
        need(isinstance(pos, list) and len(pos) == 3
             and all(type(x) is int and x in (0, 1) for x in pos), 'binary grid coordinate')
        mask = sum(x * (2 ** i) for i, x in enumerate(pos))
        need(type(v['mask']) is int and v['mask'] == mask, 'mask/position correspondence')
        need(tuple(pos) in legal, 'causally forbidden vertex')
        need(mask not in masks and tuple(pos) not in positions, 'duplicate vertex')
        need(v['term'] == terms.get(mask), 'cut term changed')
        masks.add(mask)
        positions.add(tuple(pos))
    need(positions == legal and masks == set(terms), 'cut coverage changed')
    actual = []
    for a, b in itertools.permutations(vertices, 2):
        budget.tick()
        delta = [y-x for x, y in zip(a['position'], b['position'])]
        if sum(abs(x) for x in delta) == 1 and sum(delta) == 1:
            actual.append([a['mask'], b['mask'], delta.index(1)])
    need(sorted(candidate['edges']) == sorted(actual), 'grid edge or event label changed')
    need(sorted(actual) == sorted(f['edges']), 'source/grid transition mismatch')
    return sorted(vertices, key=lambda v: v['mask']), sorted(actual)


def grid_laplacian(vertices, edges, algebra, budget):
    indices = {v['mask']: i for i, v in enumerate(vertices)}
    lap = algebra.zero(len(vertices))
    for left, right, _ in edges:
        budget.tick()
        i, j = indices[left], indices[right]
        lap[i][i] += 1
        lap[j][j] += 1
        lap[i][j] -= 1
        lap[j][i] -= 1
    return lap


def run(contract, budget):
    need = budget.require
    for path, expected in contract['inputs'].items():
        need(digest((ROOT/path).read_bytes()) == expected, 'pinned input differs: '+path)
    old = module(ROOT/contract['process_checker'], 'pinned_process_checker')
    m = module(ROOT/contract['algebra'], 'pinned_frame_algebra')
    m.ACCOUNT = budget
    families = json.loads((ROOT/contract['processes']).read_text())
    by_name = {f['name']: f for f in families}
    f = by_name[contract['family']]
    summaries = [old.check_family(by_name[name], budget)
                 for name in contract['replayed_families']]
    candidate = propose(f)
    vertices, edges = receive(candidate, f, budget)
    lap = grid_laplacian(vertices, edges, m, budget)
    n = len(vertices)
    scale = 2 * max(lap[i][i] for i in range(n))
    h0 = m.scale(lap, 1/scale)
    h, j = m.zero(2*n), m.zero(2*n)
    for a in range(n):
        j[a][a+n], j[a+n][a] = Q(-1), Q(1)
        for b in range(n):
            h[a][b] = h[a+n][b+n] = h0[a][b]
    cuts, source_h, source_j = m.base(f)
    need(cuts == [v['mask'] for v in vertices], 'cut basis order')
    need(h == source_h and j == source_j, 'source/grid operator correspondence')
    identity = m.eye(2*n)
    need(m.mul(j, j) == m.scale(identity, -1), 'J squared')
    need(m.transpose(h) == h, 'H symmetry')
    need(m.mul(j, h) == m.mul(h, j), 'complex linearity')
    need(all(sum(abs(x) for x in row) <= 1 for row in h), 'operator row bound')
    a = m.scale(m.mul(j, h), -1)
    need(m.transpose(a) == m.scale(a, -1), 'generator skew symmetry')
    u = m.coefficients(a, contract['series_order'])
    source_u = m.coefficients(m.scale(m.mul(source_j, source_h), -1), contract['series_order'])
    heat = m.coefficients(m.scale(h, -1), contract['series_order'])
    phase = identity
    for k in range(contract['series_order']+1):
        need(u[k] == source_u[k], 'exponential coefficient correspondence')
        need(m.mul(phase, u[k]) == heat[k], 'Wick coefficient')
        phase = m.mul(m.scale(j, -1), phase)
    controls = []

    def reject(name, altered, source=f):
        try:
            receive(altered, source, budget)
        except Refused as exc:
            controls.append({'name': name, 'status': 'Rejected', 'reason': str(exc)})
        else:
            raise AssertionError('negative control accepted: '+name)

    changed = deepcopy(candidate)
    changed['vertices'] += [{'mask': k, 'position': [(k>>i)&1 for i in range(3)],
                             'term': 'forbidden'} for k in (2, 6)]
    reject('complete-the-cube', changed)
    changed = deepcopy(candidate)
    changed['vertices'][0] = {'mask': 2, 'position': [0, 1, 0], 'term': 'forbidden'}
    reject('same-size-forbidden-vertex', changed)
    changed = deepcopy(candidate)
    changed['edges'][0][:2] = changed['edges'][0][1::-1]
    reject('reverse-causal-edge', changed)
    changed = deepcopy(candidate)
    changed['edges'][0][2] = 2
    reject('relabel-event-axis', changed)
    changed = deepcopy(candidate)
    changed['vertices'][0]['term'] = f['normal']
    reject('replace-source-cut-by-normal-form', changed)
    changed = deepcopy(candidate)
    changed['binding'].pop('clocks')
    reject('erase-event-clock', changed)
    changed_source = deepcopy(f)
    changed_source['exit_roles'] = [1, 0, 2]
    need(changed_source['exit_roles'] != f['exit_roles'], 'role control nontrivial')
    reject('same-graph-different-roles', candidate, changed_source)
    left, right = by_name['independent-iota'], by_name['changed-roles']
    need(m.base(left)[1] == m.base(right)[1] and binding(left) != binding(right),
         'retained same-operator/different-role witness')
    # Principal submatrix of the full cube Laplacian leaves boundary killing.
    # The induced-subgraph Laplacian used by the source instead has zero row sums.
    boundary_leaks = [3-lap[i][i] for i in range(n)]
    need(any(boundary_leaks) and all(sum(row) == 0 for row in lap), 'boundary control')
    controls.append({'name': 'restrict-full-cube-laplacian', 'status': 'Rejected',
                     'reason': 'nonzero row sums; wrong boundary condition',
                     'row_sum_residual': [str(x) for x in boundary_leaks]})
    need([c['name'] for c in controls] == contract['controls'], 'control coverage')
    return {
        'status': 'GridCorrespondenceChecked', 'candidate': candidate,
        'source_replay': summaries, 'controls': controls,
        'cut_basis': cuts, 'laplacian': m.encode(lap), 'normalization': str(scale),
        'H0': m.encode(h0), 'J': m.encode(j), 'G': m.encode(identity), 'O': m.encode(identity),
        'coefficient_sha256': digest(canonical([m.encode(c) for c in u])),
        'coefficient_orders_checked': list(range(contract['series_order']+1)),
        'tail': {'parameter_abs_max': 1, 'operator_norm_bound': 1,
                 'bound': '3/13!', 'norm': 'unchanged identity metric'},
        'full_cube_laplacian_row_residual': [str(x) for x in boundary_leaks],
        'native_admission': 'NotGranted', 'native_execution': 'NotRun',
        'new_transport': 'NotRun', 'same_author_checker': True,
        'open': contract['open'],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    # Exclusive output creation precedes execution; no earlier evidence is replaced.
    with args.output.open('x') as output:
        raw_contract = (HERE/'contract.json').read_bytes()
        contract = json.loads(raw_contract)
        limits = contract['limits']
        start, cpu = time.monotonic(), time.process_time()
        budget = Budget(limits)
        def expired(*_):
            raise TimeoutError('wall/CPU budget exhausted')
        resource.setrlimit(resource.RLIMIT_AS, (limits['memory_bytes'],)*2)
        resource.setrlimit(resource.RLIMIT_CPU, (limits['cpu_seconds'], limits['cpu_seconds']+1))
        resource.setrlimit(resource.RLIMIT_FSIZE, (limits['artifact_bytes'],)*2)
        signal.signal(signal.SIGALRM, expired)
        signal.signal(signal.SIGXCPU, expired)
        signal.alarm(limits['wall_seconds'])
        report = {'schema': 'adva.research.iota-grid-result.v0',
                  'contract_sha256': digest(raw_contract),
                  'checker_sha256': digest(Path(__file__).read_bytes()),
                  'source_commit': contract['source_commit']}
        code = 1
        try:
            report.update(run(contract, budget))
            code = 0
        except (TimeoutError, MemoryError, FileNotFoundError) as exc:
            report.update(status='Unknown', reason=str(exc))
        except Exception as exc:
            report.update(status='Failed', reason=type(exc).__name__+': '+str(exc))
        report.update(assertions=budget.assertions, counted_work=budget.work,
                      wall_seconds=time.monotonic()-start, cpu_seconds=time.process_time()-cpu,
                      peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        # Keep the alarm active through serialization and checkpointing.
        payload = json.dumps(report, indent=2, sort_keys=True)+'\n'
        if len(payload.encode()) > limits['artifact_bytes']:
            raise RuntimeError('evidence exceeds artifact budget; no complete checkpoint')
        output.write(payload)
        output.flush()
        signal.alarm(0)
    print(json.dumps({k: report[k] for k in ('status', 'assertions', 'counted_work')}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
