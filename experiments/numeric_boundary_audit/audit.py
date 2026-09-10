"""Finite audit: C scalar model, actual Python method extracts, exact oracles."""
import ast
from fractions import Fraction
import hashlib
import json
import math
from numbers import Real
from pathlib import Path
import resource
import struct
import subprocess
import tempfile
import time
from types import SimpleNamespace
from typing import Mapping

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def bits(value):
    return struct.pack('>d', value).hex()


def method(path, cls, name, env):
    tree = ast.parse(path.read_text())
    klass = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == cls)
    fn = next(x for x in klass.body if isinstance(x, ast.FunctionDef) and x.name == name)
    module = ast.Module(body=[fn], type_ignores=[])
    exec(compile(module, str(path), 'exec'), env)
    return env[name]


def run():
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix='adva-float-audit-') as tmp:
        executable = Path(tmp) / 'model'
        build_start = time.perf_counter()
        subprocess.run(['cc', '-std=c11', '-O0', '-fno-fast-math', str(HERE/'scalar_model.c'), '-lm', '-o', str(executable)],
                       check=True, capture_output=True, timeout=10)
        build_ms = (time.perf_counter()-build_start)*1000
        result = subprocess.run([str(executable)], check=True, capture_output=True, timeout=5)
        model = json.loads(result.stdout)
    log_results = []
    for row in model['log_chain']:
        expected = math.ldexp(1.0, row['x_exponent'])
        assert math.isfinite(expected)
        row['exact_derivative'] = f"2^{row['x_exponent']}"
        row['expected_binary64_bits'] = bits(expected)
        row['current_matches_exact'] = row['current_gradient_bits'] == bits(expected)
        row['alternative_matches_exact'] = row['alternative_gradient_bits'] == bits(expected)
        assert row['alternative_matches_exact'] and row['log_value_finite']
        log_results.append(row)
    assert sum(not row['current_matches_exact'] for row in log_results) == 3
    rational_results = []
    for row in model['rational_conversion']:
        exact = Fraction(row['numerator'], row['denominator'])
        nearest = float(exact)
        lower, upper = math.nextafter(nearest, -math.inf), math.nextafter(nearest, math.inf)
        # These fixed cases are not halfway ties: verify the chosen oracle by exact distances.
        assert abs(Fraction(nearest)-exact) < abs(Fraction(lower)-exact)
        assert abs(Fraction(nearest)-exact) < abs(Fraction(upper)-exact)
        row['nearest_bits'] = bits(nearest)
        row['current_is_nearest'] = row['current_bits'] == bits(nearest)
        row['exact_is_one'] = exact == 1
        rational_results.append(row)
    assert sum(not row['current_is_nearest'] for row in rational_results) == 2
    env = {'Mapping': Mapping, 'Real': Real}
    validate = method(ROOT/'python/adva/core.py', 'KernelFunction', '_check_inputs', env)
    fake_function = SimpleNamespace(signature=SimpleNamespace(input_names=['x']))
    inputs = []
    for name, value in [('finite', 1.0), ('nan', math.nan), ('positive_inf', math.inf), ('boolean', True)]:
        try:
            checked = validate(fake_function, {'x': value})
            inputs.append({'case': name, 'status': 'AcceptedByPythonInputMethod',
                           'finite': math.isfinite(checked['x']), 'bits': bits(checked['x'])})
        except TypeError as error:
            inputs.append({'case': name, 'status': 'Rejected', 'error': str(error)})
    assert [r['status'] for r in inputs] == ['AcceptedByPythonInputMethod']*3 + ['Rejected']
    installed = {}
    mock_resource = SimpleNamespace(RLIMIT_AS='AS', RLIMIT_CPU='CPU', RLIMIT_FSIZE='FSIZE', RLIMIT_CORE='CORE',
                                    setrlimit=lambda key, value: installed.__setitem__(key, value))
    restrictions = method(ROOT/'python/adva/quine_relay.py', 'Supervisor', 'restrictions',
                          {'sys': SimpleNamespace(platform='linux'), 'math': math, 'resource': mock_resource})
    limits = {'address_space_bytes': 2**31, 'aggregate_child_cpu_seconds': 10,
              'child_cpu_seconds': 5, 'max_file_bytes': 2**20}
    budgets = []
    for remaining in [0.25, 1.25, 2.0]:
        fake_supervisor = SimpleNamespace(limits=limits, child_cpu_start=0.0,
                                         child_cpu=lambda: 10-remaining)
        installed.clear()
        restrictions(fake_supervisor)
        cpu = installed['CPU'][0]
        budgets.append({'remaining_cpu_seconds': remaining, 'installed_child_cpu_seconds': cpu,
                        'not_above_remaining': cpu <= remaining,
                        'execution': 'Exact source method with mocked setrlimit; no child launched'})
    assert [r['not_above_remaining'] for r in budgets] == [False, True, True]
    inventory = []
    paths = sorted(list((ROOT/'crates').glob('*/src/**/*.rs')) + list((ROOT/'python/adva').glob('*.py')))
    for path in paths:
        data = path.read_bytes()
        inventory.append({'path': str(path.relative_to(ROOT)), 'bytes': len(data),
                          'sha256': hashlib.sha256(data).hexdigest(),
                          'git_blob': hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()})
    return {'schema': 'adva.numeric-boundary-audit.v0',
            'source_commit': '7be406bfa6a3b7a5ef619081157e3b113da0cd40',
            'status': 'SourceAuditAndExternalReproductions', 'native_adva_execution': 'NotRun',
            'native_toolchain': 'Unavailable in this receiving environment',
            'log_gradient_model': log_results, 'rational_conversion_model': rational_results,
            'python_input_method': inputs, 'resource_limit_method': budgets,
            'source_inventory': inventory, 'source_files': len(paths),
            'c_build_ms': build_ms, 'wall_ms_before_serialization': (time.perf_counter()-started)*1000,
            'python_process_peak_rss_kib_linux': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'max_child_rss_kib_linux': resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            'rss_scope': 'Separate parent and maximum completed-child peaks; not simultaneous aggregate peak',
            'unmeasured': ['source retrieval', 'research and authoring', 'report serialization'],
            'remaining': ['Rust native bit-pattern replay', 'Numeric policy/version decision before stable fixes',
                          'Research 0141 parser-versus-serializer mismatch remains unresolved']}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2, allow_nan=False))
