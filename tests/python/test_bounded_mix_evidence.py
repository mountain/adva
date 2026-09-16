"""Receive retained evidence without rerunning a finite research campaign."""
import hashlib
import json
from pathlib import Path
import sys
import tarfile

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments.bounded_mix.receive import receive, wire
from experiments.bounded_mix.fixtures import interpreters
from experiments.bounded_mix.campaign_v2 import select, V2, receipt
from experiments.bounded_mix.runtime_v2 import profile
from experiments.bounded_self_compiler.language import TARGET, decode_target

EVIDENCE = ROOT / 'experiments/bounded_mix/evidence'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


@pytest.fixture(scope='module')
def bundles():
    result = {}
    for name in ('preflight-01', 'v1-attempt-01', 'v2-attempt-01'):
        folder = EVIDENCE / name
        record = json.loads((folder / 'retention.json').read_bytes())
        archive = folder / record['archive']
        assert sha(archive.read_bytes()) == record['archive_sha256']
        with tarfile.open(archive, 'r:gz') as bundle:
            members = bundle.getmembers()
            assert len(members) == len(record['files']) <= 600
            assert sum(m.size for m in members) == record['uncompressed_bytes'] <= 256 * 1024**2
            assert all(m.isfile() and Path(m.name).name == m.name for m in members)
            assert {m.name for m in members} == set(record['files'])
            raw = {m.name: bundle.extractfile(m).read() for m in members}
        for file, value in raw.items():
            assert sha(value) == record['files'][file]['sha256']
            assert len(value) == record['files'][file]['bytes']
            if (folder / file).exists():
                assert (folder / file).read_bytes() == value
        manifest = json.loads(raw['source-manifest.json'])
        for path, entry in manifest.items():
            assert sha(raw[entry['snapshot']]) == entry['sha256']
            if path.startswith(('programs/', 'crates/')) or path.endswith('Cargo.lock'):
                assert (ROOT / path).read_bytes() == raw[entry['snapshot']]
        result[name] = raw
    return result


def read(bundle, name):
    return json.loads(bundle[name])


def terminal(bundle, name):
    return read(bundle, name + '.run.adva')['state']['phase']


def test_native_compilation_preflight_and_v1_obstruction_are_both_retained(bundles):
    pre = bundles['preflight-01']
    compiled = read(pre, 'compile-mix.run.adva')
    mix = read(pre, 'mix.program.adva')
    assert decode_target(compiled['state']['phase']['value']) == mix
    assert mix == json.loads((ROOT / 'programs/bounded-mix/mix.seed.adva').read_bytes())
    reception = read(pre, 'receive-mix-compilation.run.adva')
    assert reception['verified_steps'] == compiled['state']['spent'] == 14407
    assert reception['state'] == compiled['state']
    assert terminal(pre, 'source') == terminal(pre, 'residual')

    old = bundles['v1-attempt-01']
    failed = read(old, 'third-generation.run.adva')
    assert failed['status'] == 'Rejected' and failed['state']['spent'] == 58551
    assert failed['state']['phase'] == {'kind': 'rejected', 'reason': 'node arity exceeds 2048'}
    assert not read(old, 'summary.json')['third']['executed_compiler_generator']
    for name, interpreter, programs in interpreters():
        for i, static in enumerate(programs):
            first = read(old, f'{name}-{i}-first.target.adva')
            second = read(old, f'{name}-{i}-second.target.adva')
            assert first == second
            assert receive(interpreter, static, first) == read(old, f'{name}-{i}-first.receipt.json')
            for dynamic in (7, -3, 2**63 - 1):
                assert terminal(old, f'{name}-{i}-direct-{dynamic}') == terminal(old, f'{name}-{i}-residual-{dynamic}')
    for name in ('repeated-input', 'loop', 'uninitialized'):
        assert terminal(old, name + '-direct') == terminal(old, name + '-residual')


def test_actual_third_output_is_admitted_executed_and_natively_replayed(bundles):
    b = bundles['v2-attempt-01']
    assert b['native-v2-source.rs'] == (ROOT / 'crates/adva-witness/src/data_machine_v2.rs').read_bytes()
    generated = read(b, 'third-generation.run.adva')
    cogen = read(b, 'third-generation.target.adva')
    mix = read(b, 'mix.program.adva')
    assert generated['status'] == 'Returned'
    assert select(decode_target(generated['state']['phase']['value']), V2) == cogen
    assert len(cogen['code']) == 3959 and len(cogen['registers']) == 57
    assert receipt(mix, wire(select(mix, TARGET)), cogen) == read(b, 'third-generation.receipt.json')
    admitted = read(b, 'third-admission.run.adva')
    assert admitted['program'] == cogen and admitted['status'] == 'FuelExhausted'
    replay = read(b, 'third-reception.run.adva')
    assert replay['verified_steps'] == generated['state']['spent']
    assert replay['state'] == generated['state']
    for name, interpreter, programs in interpreters():
        direct = read(b, name + '-direct-compiler.target.adva')
        run = read(b, name + '-generated-compiler.run.adva')
        compiler = read(b, name + '-generated-compiler.target.adva')
        assert run['program'] == cogen and run['status'] == 'Returned'
        assert select(decode_target(run['state']['phase']['value']), V2) == compiler == direct
        assert receipt(mix, wire(interpreter), compiler) == read(b, name + '-generated-compiler.receipt.json')
        replay = read(b, name + '-compiler-reception.run.adva')
        assert replay['verified_steps'] == run['state']['spent']
        assert replay['state'] == run['state']
        for i, static in enumerate(programs):
            residual = read(b, f'{name}-{i}-direct-residual.target.adva')
            compiled = read(b, f'{name}-{i}-compiled-residual.run.adva')
            assert compiled['program'] == compiler
            assert select(decode_target(compiled['state']['phase']['value']), V2) == residual
            assert receipt(select(interpreter, V2), static, residual) == read(b, f'{name}-{i}-compiled-residual.receipt.json')
            for dynamic in (7, 2**63 - 1):
                assert terminal(b, f'{name}-{i}-direct-{dynamic}') == terminal(b, f'{name}-{i}-residual-{dynamic}')


def test_actual_mutation_continuation_and_rejection_controls(bundles):
    b = bundles['v2-attempt-01']
    prefix = read(b, 'prefix.run.adva')
    resumed = read(b, 'resumed.run.adva')
    assert prefix['state']['spent'] == 17
    assert resumed['trace'][:17] == prefix['trace']
    assert resumed['segments'][-1]['replayed'] == 17
    assert resumed['fuel'] == prefix['fuel'] == 200000
    mutation = read(b, 'mutated-mix.run.adva')
    target = select(decode_target(mutation['state']['phase']['value']), V2)
    original = decode_target(mutation['input']['fields'][0])
    static = mutation['input']['fields'][1]
    with pytest.raises(ValueError, match='correspondence'):
        receipt(select(original, V2), static, target)
    assert terminal(b, 'mutated-residual')['value']['tag'] == 43
    calls = {c['name']: c for c in read(b, 'cost.json')['native_calls']}
    for name in ('changed-fuel', 'foreign-profile', 'new-arity-cap'):
        assert calls[name]['status'] == 'Refused'
        assert calls[name]['exit_code'] != 0
        assert b[name + '.stderr.txt']
        assert name + '.run.adva' not in b
    assert calls['zero-fuel']['status'] == 'FuelExhausted'
    assert calls['malformed-tag']['status'] == 'Rejected'


def test_contract_lineage_profiles_and_finite_costs(bundles):
    successor = json.loads((ROOT / 'experiments/bounded_mix/contract-v1.json').read_bytes())
    for key in ('supersedes', 'capacity_evidence'):
        entry = successor[key]
        assert sha((ROOT / entry['path']).read_bytes()) == entry['sha256']
    for name, calls, wall, cpu, size in (
        ('preflight-01', 6, 180, 160, 96),
        ('v1-attempt-01', 67, 1200, 1080, 256),
        ('v2-attempt-01', 48, 1200, 1080, 256),
    ):
        b = bundles[name]
        cost = read(b, 'cost.json')
        assert len(cost['native_calls']) == calls
        assert cost['wall_seconds'] < wall and cost['cpu_seconds_including_native'] < cpu
        assert cost['artifact_bytes_before_cost'] < size * 1024**2
        assert cost['status'] == ('PassedWithThirdCapacityObstruction' if name == 'v1-attempt-01' else 'Passed')
        for call in cost['native_calls']:
            if call['sha256']:
                raw = b[call['name'] + '.run.adva']
                assert sha(raw) == call['sha256']
                assert read(b, call['name'] + '.run.adva')['profile'] == cost['profile']
        if name == 'v2-attempt-01':
            assert cost['profile'] == profile()
            assert read(b, 'contract-v1.json') == successor
            summary = read(b, 'summary.json')
            assert summary['first_second_code_equalities'] == 5
            assert summary['second_third_code_equalities'] == 2
            assert len(summary['terminal_pairs']) == 10
