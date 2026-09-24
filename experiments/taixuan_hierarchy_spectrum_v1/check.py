#!/usr/bin/env python3
"""External finite calibration. Original contribution under Unknown v0.3.

Author: Codex (OpenAI); account proxy is not correctness evidence.
No semantic identities, geometry admission, or physical dynamics are created.
"""
import argparse
import cmath
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
from itertools import product
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
        self.started = time.monotonic()
        self.cases = 0

    def charge(self, count=1):
        self.cases += count
        if self.cases > self.budget['max_charged_cases']:
            raise Limit('charged case limit')
        if time.monotonic() - self.started > self.budget['worker_wall_seconds']:
            raise Limit('cooperative wall limit')


ZERO = (0,) * 6
ONE = (1, 0, 0, 0, 0, 0)


def add(*values):
    return tuple(map(sum, zip(*values)))


def scale(n, value):
    return tuple(n * x for x in value)


def multiply(a, b):
    coefficients = [0] * 11
    for i in range(6):
        for j in range(6):
            coefficients[i + j] += a[i] * b[j]
    for i in range(10, 5, -1):
        coefficients[i - 3] -= coefficients[i]
        coefficients[i - 6] -= coefficients[i]
    return tuple(coefficients[:6])


def shift(z, axis, amount=1, modulus=9):
    return tuple((v + amount) % modulus if i == axis else v
                 for i, v in enumerate(z))


def parent(z):
    return tuple(v // 3 for v in z)


def residue(z):
    return tuple(v % 3 for v in z)


def exact_fourier(meter):
    t = (0, 1, 0, 0, 0, 0)
    powers = [ONE]
    for _ in range(9):
        powers.append(multiply(powers[-1], t))
    assert powers[9] == ONE and all(powers[k] != ONE for k in range(1, 9))
    p = lambda k: powers[k % 9]
    counts = {}
    for n, root_step in [(9, 1), (3, 3)]:
        for k, ell in product(range(n), repeat=2):
            meter.charge()
            inner = add(*(p(root_step * (k - ell) * z) for z in range(n)))
            assert inner == scale(n, ONE) if k == ell else inner == ZERO
        for k, z in product(range(n), repeat=2):
            meter.charge()
            eigenvalue = add(scale(2, ONE), scale(-1, p(root_step * k)),
                             scale(-1, p(-root_step * k)))
            actual = add(scale(2, p(root_step * k * z)),
                         scale(-1, p(root_step * k * (z + 1))),
                         scale(-1, p(root_step * k * (z - 1))))
            assert actual == multiply(eigenvalue, p(root_step * k * z))
        counts[str(n)] = {'gram_pairs': n*n, 'eigenvector_entries': n*n}
    one_axis = [add(scale(2, ONE), scale(-1, p(k)), scale(-1, p(-k)))
                for k in range(9)]
    cyclic = Counter()
    for k in product(range(9), repeat=4):
        meter.charge()
        cyclic[add(*(one_axis[v] for v in k))] += 1
    digitwise = Counter()
    for k in product(range(3), repeat=8):
        meter.charge()
        digitwise[3 * sum(v != 0 for v in k)] += 1
    assert dict(digitwise) == {3*j: math.comb(8, j)*2**j for j in range(9)}
    assert sum(cyclic.values()) == sum(digitwise.values()) == 6561
    assert cyclic[ZERO] == digitwise[0] == 1
    assert add(*(scale(count, value) for value, count in cyclic.items())) == scale(8*6561, ONE)
    assert sum(value*count for value, count in digitwise.items()) == 16*6561
    root = cmath.exp(2j*math.pi/9)
    rows = []
    for value, multiplicity in cyclic.items():
        approximate = sum(c * root**j for j, c in enumerate(value))
        assert abs(approximate.imag) < 1e-10
        rows.append({'cyclotomic_coefficients': list(value),
                     'approximate_eigenvalue': approximate.real,
                     'multiplicity': multiplicity})
    rows.sort(key=lambda row: row['approximate_eigenvalue'])
    return {
        'exact_ring': 'Z[t]/(t^6+t^3+1), t a primitive ninth root',
        'one_axis_checks': counts,
        'tensor_basis_count_each': 6561,
        'cyclic_nine_four': {'group_exponent': 9, 'degree': 8, 'trace': 8*6561,
                            'distinct_eigenvalues': len(rows), 'spectrum': rows},
        'ternary_eight': {'group_exponent': 3, 'degree': 16, 'trace': 16*6561,
                         'spectrum': [{'eigenvalue': k, 'multiplicity': v}
                                      for k, v in sorted(digitwise.items())]},
        'scope': 'Positive unnormalized graph Laplacians on two declared periodic finite groups.'
    }


def transform(values, inverse, meter):
    """Separable unitary DFT on lexicographic (Z/9)^4; no FFT dependency."""
    n = len(values)
    assert n == 9**4
    sign = 1 if inverse else -1
    roots = [[cmath.exp(sign*2j*math.pi*k*x/9)/3 for x in range(9)]
             for k in range(9)]
    out = list(values)
    for axis in range(4):
        stride = 9**(3-axis)
        new = [0j] * n
        for block in range(0, n, 9*stride):
            for offset in range(stride):
                line = [out[block+offset+x*stride] for x in range(9)]
                for k in range(9):
                    meter.charge(9)
                    new[block+offset+k*stride] = sum(roots[k][x]*line[x] for x in range(9))
        out = new
    return out


def run(repo, contract, meter):
    verified_pins = []
    read_bytes = 0
    for pin in contract['input_pins']:
        path = repo / pin['path']
        read_bytes += path.stat().st_size
        if read_bytes > contract['budget']['max_input_bytes']:
            raise Limit('input byte limit')
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == pin['sha256'], 'input pin mismatch: ' + pin['path']
        verified_pins.append(pin)
    points = list(product(range(9), repeat=4))
    index = {z: i for i, z in enumerate(points)}
    qiong = (2, 1, 1, 2)
    assert 1 + sum(v*w for v, w in zip(qiong, (27, 9, 3, 1))) == 69
    fibres = defaultdict(list)
    pairs = set()
    for z in points:
        meter.charge()
        a, b = parent(z), residue(z)
        assert tuple(3*x+y for x, y in zip(a, b)) == z
        pairs.add((a, b))
        fibres[a].append(z)
    assert len(pairs) == 6561 and len(fibres) == 81
    assert {len(f) for f in fibres.values()} == {81}
    assert set(fibres[qiong]) == set(product(range(6, 9), range(3, 6), range(3, 6), range(6, 9)))

    unit_factor_failures = 0
    for z in points:
        for axis in range(4):
            meter.charge()
            assert residue(shift(z, axis)) == shift(residue(z), axis, modulus=3)
            assert parent(shift(z, axis, 3)) == shift(parent(z), axis, modulus=3)
            if parent(shift(z, axis)) != shift(parent(z), axis, modulus=3):
                unit_factor_failures += 1
    witness = [(6, 3, 3, 6), (8, 3, 3, 6)]
    assert parent(witness[0]) == parent(witness[1]) == qiong
    assert parent(shift(witness[0], 0)) != parent(shift(witness[1], 0))
    labels = [parent(z) for z in points]
    sizes = [len(set(labels))]
    stable = False
    for _ in range(contract['fixed_family']['partition_refinement_round_cap']):
        classes = {}
        refined = []
        for i, z in enumerate(points):
            meter.charge()
            signature = (labels[i], *(labels[index[shift(z, axis)]] for axis in range(4)))
            if signature not in classes:
                classes[signature] = len(classes)
            refined.append(classes[signature])
        if len(classes) == sizes[-1]:
            stable = True
            break
        sizes.append(len(classes))
        labels = refined
    if not stable:
        raise Limit('partition refinement round limit')
    assert sizes[-1] == len(points)

    field = {z: sum((i+1)*(v-4) for i, v in enumerate(z))
             + (z[0] % 3-1)*(z[1] % 3-1) for z in points}
    means = {a: Fraction(sum(field[z] for z in f), len(f)) for a, f in fibres.items()}
    residual = {z: Fraction(field[z]) - means[parent(z)] for z in points}
    for a, fibre in fibres.items():
        meter.charge(len(fibre))
        assert sum(residual[z] for z in fibre) == 0
        assert all(means[a] + residual[z] == field[z] for z in fibre)
    energy = sum(Fraction(v*v) for v in field.values())
    coarse_energy = sum(81*v*v for v in means.values())
    detail_energy = sum(v*v for v in residual.values())
    assert energy == coarse_energy + detail_energy and detail_energy > 0
    coarse_values = [float(means[parent(z)]) for z in points]
    values = [field[z] for z in points]
    coefficients = transform(values, False, meter)
    reconstructed = transform(coefficients, True, meter)
    norm = max(1, max(abs(v) for v in values))
    error = max(abs(a-b) for a, b in zip(values, reconstructed)) / norm
    spectral_energy = sum(abs(v)**2 for v in coefficients)
    parseval_error = abs(spectral_energy-float(energy))/max(1, float(energy))
    assert error < 1e-10 and parseval_error < 1e-10
    corrupted = list(reconstructed)
    corrupted[0] += 1
    assert max(abs(a-b) for a, b in zip(values, corrupted))/norm > 1e-10
    assert coarse_values != values
    # One coordinate already refutes homomorphism under the label encoding.
    assert (2+1) % 9 != 3*((0+0) % 3) + ((2+1) % 3)
    spectra = exact_fourier(meter)
    return {
        'input_pins_verified': verified_pins,
        'addresses': {'coarse': 81, 'fine': len(points), 'ordered_pairs': len(pairs),
                      'children_per_parent': 81, 'qiong_ordinal': 69,
                      'qiong_zero_based': list(qiong), 'qiong_children': len(fibres[qiong])},
        'observers': {
            'unit_shift_cases': len(points)*4,
            'residue_is_unit_translation_factor': True,
            'block_parent_is_triple_translation_factor': True,
            'block_parent_unit_shift_commuting_failures': unit_factor_failures,
            'block_parent_not_any_autonomous_unit_factor_witness': [
                {'fine': list(z), 'parent': list(parent(z)), 'next_fine': list(shift(z, 0)),
                 'next_parent': list(parent(shift(z, 0)))} for z in witness],
            'minimal_stable_refinement_sizes': sizes,
            'stable_check_completed': stable,
            'refinement_scope': 'All four positive unit translations on the declared periodic grid.'},
        'multiresolution': {'coarse_dimension': 81, 'residual_dimension': 6480,
                            'exact_reconstruction': True, 'all_residual_fibre_means_zero': True,
                            'energy': str(energy), 'coarse_energy': str(coarse_energy),
                            'detail_energy': str(detail_energy),
                            'qiong_coarse_field_value': str(means[qiong])},
        'fourier_replay': {'relative_max_reconstruction_error': error,
                           'relative_parseval_error': parseval_error, 'tolerance': 1e-10,
                           'kind': 'Numerical synthetic-field calibration, not observed climate data.'},
        'spectra': spectra,
        'negative_controls_rejected': ['floor_as_unit_translation_factor',
                                      'encoding_as_group_isomorphism',
                                      'drop_residual_without_loss',
                                      'corrupted_fourier_reconstruction'],
        'open': ['Four-dimensional geometric monotile', 'Local matching and recognizability',
                 'Tiling existence and exclusion of all infinite-order symmetries',
                 'Spectra of an actual nonperiodic hull', 'Physical space-time and forecast validation'],
        'native_admission': 'NotRequested; external research only'
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--ledger', type=Path)
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    contract_path = Path(__file__).with_name('contract.json')
    contract_bytes = contract_path.read_bytes()
    contract = json.loads(contract_bytes)
    budget = contract['budget']
    if args.worker:
        resource.setrlimit(resource.RLIMIT_CPU, (budget['worker_cpu_seconds'],)*2)
        resource.setrlimit(resource.RLIMIT_AS, (budget['worker_address_space_bytes'],)*2)
        resource.setrlimit(resource.RLIMIT_FSIZE, (budget['max_output_bytes'],)*2)
        meter = Meter(budget)
        result = {'schema': 'adva.research.taixuan-hierarchy-spectrum-evidence.v1',
                  'contract_sha256': hashlib.sha256(contract_bytes).hexdigest(),
                  'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        try:
            result['results'] = run(args.repo_root, contract, meter)
            result['status'] = 'Pass'
        except (Limit, MemoryError) as exc:
            result.update(status='Unknown', reason=str(exc) or 'memory limit')
        except Exception as exc:
            import traceback
            result.update(status='Failure', reason=repr(exc), traceback=traceback.format_exc())
        result['resources'] = {'charged_cases': meter.cases,
                               'wall_seconds': time.monotonic()-meter.started,
                               'cpu_seconds': time.process_time(),
                               'peak_rss_kib_linux': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                               'python': sys.version.split()[0]}
        payload = json.dumps(result, indent=2, ensure_ascii=False) + '\n'
        if len(payload.encode()) > budget['max_output_bytes']:
            payload = json.dumps({'status': 'Unknown', 'reason': 'output byte limit'})+'\n'
        sys.stdout.write(payload)
        return
    if args.output is None or args.ledger is None:
        parser.error('--output and --ledger are required')
    ledger = json.loads(args.ledger.read_text()) if args.ledger.exists() else {'launches': []}
    if len(ledger['launches']) >= budget['normal_launches']:
        raise SystemExit('Refused: declared launch budget spent; no automatic reset')
    if args.output.exists():
        raise SystemExit('Refused: preserve existing evidence; choose a new output')
    entry = {'contract_sha256': hashlib.sha256(contract_bytes).hexdigest(),
             'output': str(args.output), 'status': 'Started'}
    ledger['launches'].append(entry)
    args.ledger.write_text(json.dumps(ledger, indent=2)+'\n')
    try:
        completed = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--worker',
                                    '--repo-root', str(args.repo_root.resolve())],
                                   capture_output=True, text=True,
                                   timeout=budget['worker_wall_seconds'])
        if completed.returncode != 0:
            result = {'status': 'Unknown' if completed.returncode < 0 else 'Failure',
                      'reason': 'worker exit', 'returncode': completed.returncode,
                      'stderr': completed.stderr[:4000]}
        else:
            result = json.loads(completed.stdout)
    except subprocess.TimeoutExpired:
        result = {'status': 'Unknown', 'reason': 'supervisor wall timeout'}
    payload = json.dumps(result, indent=2, ensure_ascii=False)+'\n'
    if len(payload.encode()) > budget['max_output_bytes']:
        result = {'status': 'Unknown', 'reason': 'supervisor output byte limit'}
        payload = json.dumps(result)+'\n'
    args.output.write_text(payload)
    entry['status'] = result['status']
    entry['evidence_sha256'] = hashlib.sha256(payload.encode()).hexdigest()
    args.ledger.write_text(json.dumps(ledger, indent=2)+'\n')
    print(json.dumps({'status': result['status'], 'output': str(args.output),
                      'resources': result.get('resources'), 'reason': result.get('reason')}))
    if result['status'] != 'Pass':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
