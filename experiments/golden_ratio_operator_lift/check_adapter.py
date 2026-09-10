"""Real Python CLI integration checks against the pinned external checker."""
import argparse
import base64
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CLI = ROOT/'python/adva/adva.py'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--output', required=True)
    output = Path(parser.parse_args().output)
    if output.exists():
        raise SystemExit('fresh output required')
    resource.setrlimit(resource.RLIMIT_CPU, (15, 15))
    resource.setrlimit(resource.RLIMIT_AS, (256*1024*1024,)*2)
    start = time.perf_counter()
    fixture = json.loads((HERE/'receipt-evidence.json').read_text())
    source = {c['name']: c for c in fixture['cases']}
    rows = []
    specs = [
        ('fresh-nonstandard-basis', 'ClosedForAllTranslationsByLinearity', 0),
        ('whitespace-only', 'ClosedForAllTranslationsByLinearity', 0),
        ('self-rehashed-operator-old-anchor', 'InvalidContextBinding', 2),
        ('missing-third-direction', 'UnknownCoverage', 3),
        ('third-direction-refutes', 'Refuted', 2),
        ('forged-zero', 'InvalidEvidence', 2),
        ('bad-question', 'InputError', 2),
        ('oversized-input', 'InputError', 2),
        ('symlink-input', 'InputError', 2),
    ]
    last_closed = None
    with tempfile.TemporaryDirectory(prefix='adva-operator-integration-') as td:
        root = Path(td)
        for name, expected, code in specs:
            folder = root/name; folder.mkdir()
            case = (source[name] if name in {'fresh-nonstandard-basis',
                    'self-rehashed-operator-old-anchor', 'missing-third-direction',
                    'third-direction-refutes', 'forged-zero'}
                    else source['fresh-nonstandard-basis'])
            incoming = case['raw_json'].encode()
            context = (json.loads(source['standard-basis']['raw_json'])['context']
                       if name == 'self-rehashed-operator-old-anchor' else json.loads(case['raw_json'])['context'])
            question = {'schema':'adva.external.operator-question.v0',
                        'question_id': name, 'context': context}
            question_bytes = (json.dumps(question, indent=2)+'\n').encode()
            if name == 'whitespace-only':
                incoming = (' \n'+json.dumps(json.loads(incoming), indent=2)+'\n ').encode()
            if name == 'bad-question':
                question_bytes = b'{"schema":false}'
            if name == 'oversized-input':
                incoming = b' '*16385
            qp, rp, out = folder/'question.json', folder/'receipt.json', folder/'report.json'
            qp.write_bytes(question_bytes)
            if name == 'symlink-input':
                original = folder/'original.json'; original.write_bytes(incoming); rp.symlink_to(original)
            else:
                rp.write_bytes(incoming)
            t = time.perf_counter()
            run = subprocess.run([sys.executable, '-B', '-S', str(CLI), 'operator-check',
                                  '--question', str(qp), '--receipt', str(rp), '--output', str(out)],
                                 capture_output=True, text=True, timeout=5)
            elapsed = time.perf_counter()-t
            assert run.returncode == code, (name, run.stdout, run.stderr)
            report = json.loads(out.read_text())
            assert report['status'] == expected, (name, report)
            assert report['native_free'] == report['native_admission'] == 'NotGranted'
            assert qp.read_bytes() == question_bytes and rp.read_bytes() == incoming
            good_input = name not in {'bad-question', 'oversized-input', 'symlink-input'}
            assert report['cost']['backend_invocations'] == int(good_input)
            if good_input:
                assert base64.b64decode(report['local_question']['base64']) == question_bytes
                assert base64.b64decode(report['incoming_receipt']['base64']) == incoming
                assert report['incoming_receipt']['sha256'] == digest(incoming)
                assert report['execution'] == 'Completed'
            if name == 'fresh-nonstandard-basis':
                last_closed = report
            rows.append({'case':name, 'expected_status':expected, 'exit_code':run.returncode,
                         'process_seconds':elapsed, 'inputs_unchanged':True,
                         'question_bytes_sha256':digest(question_bytes),
                         'receipt_bytes_sha256':digest(incoming), 'report':report})
            if time.perf_counter()-start > 15:
                raise TimeoutError('integration suite wall budget')
        # The output still exists: the CLI must refuse before launching a checker.
        before = out.read_bytes()
        run = subprocess.run([sys.executable, '-B', '-S', str(CLI), 'operator-check',
                              '--question', str(qp), '--receipt', str(rp), '--output', str(out)],
                             capture_output=True, text=True, timeout=3)
        assert run.returncode == 2 and out.read_bytes() == before
        rows.append({'case':'fresh-output-no-overwrite', 'exit_code':2, 'output_unchanged':True})
    spec = importlib.util.spec_from_file_location('external_adapter_test', ROOT/'python/adva/operator_receipt.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    positive = last_closed['external_result']
    context_sha = last_closed['expected_context_sha256']
    for name in ['backend-context-mismatch', 'backend-native-escalation', 'backend-exit-mismatch']:
        obj = copy.deepcopy(positive); code = 0
        if name == 'backend-context-mismatch': obj['context_sha256'] = '0'*64
        if name == 'backend-native-escalation': obj['native_admission'] = 'Granted'
        if name == 'backend-exit-mismatch': code = 2
        try:
            module.accept_result(json.dumps(obj).encode(), code, context_sha)
        except ValueError:
            rows.append({'case':name, 'status':'ProtocolRejected'})
        else:
            raise AssertionError(name)
    result = {'status':'Passed', 'checks':len(rows), 'cases':rows,
              'cost':{'suite_wall_seconds':time.perf_counter()-start,
                      'cli_invocations':10, 'backend_invocations':6,
                      'suite_peak_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                      'search_candidates':0, 'research_and_coding_seconds':None},
              'correction_replays':1,
              'prior_attempt':'adapter-first-failure.json; 7 CLI and 6 backend calls before fixture error',
              'pins':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in
                      [CLI, ROOT/'python/adva/operator_receipt.py', Path(__file__),
                       HERE/'adapter-contract.json', HERE/'adapter-correction-contract.json',
                       HERE/'adapter-first-failure.json', HERE/'receipt.py', HERE/'receipt-evidence.json']}}
    t=time.perf_counter(); payload=json.dumps(result, indent=2)+'\n'
    assert json.loads(payload)==result
    result['cost']['serialization_roundtrip_seconds']=time.perf_counter()-t
    payload=json.dumps(result, indent=2)+'\n'; assert len(payload.encode())<=524288
    with output.open('x') as f: f.write(payload)
    print(json.dumps({'status':'Passed','checks':len(rows),'cost':result['cost']}))


if __name__ == '__main__':
    main()
