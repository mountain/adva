#!/usr/bin/env python3
"""Actual pre-build refusals for one successor consumer; no native admission.

Codex (OpenAI), through Mingli Yuan's authorized account proxy, not his
review or endorsement. Project-original contribution under Unknown v0.3.
"""
import argparse
import copy
import importlib.util
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('machine_dependency', ROOT / 'scripts/check_machine_dependency.py')
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


def run(machine, output):
    machine, output = machine.resolve(), output.resolve()
    saved_lock = CHECK.LOCK
    lock = CHECK.read(saved_lock)
    CHECK.checkout(machine, lock['machine']['revision'])
    prior = CHECK.read(ROOT / lock['previous_lock']['path'])
    CHECK.require(prior['machine']['revision'] != lock['machine']['revision'], 'control needs distinct predecessor')
    output.mkdir(parents=True, exist_ok=False)
    summary = {'schema': 'adva.knowledge.migration-refusals.v0', 'status': 'Error',
        'consumer': 'scripts/check_machine_dependency.py', 'machine_revision': lock['machine']['revision'],
        'lock_sha256': CHECK.sha(saved_lock), 'checker_sha256': CHECK.sha(ROOT / 'scripts/check_machine_dependency.py'),
        'controls': [], 'scope': 'actual receiver refusals before build; no native semantic admission'}
    try:
        altered = copy.deepcopy(lock)
        altered['machine']['spec_catalog_sha256'] = '0' * 64
        mismatch = output / 'pin-mismatch.lock.json'
        CHECK.save(mismatch, altered)
        cases = [('pin-mismatch', machine, mismatch, 'pinned input differs: spec/catalog.json')]
        for name, revision, change in (
                ('moving-head', lock['machine']['revision'], 'advance'),
                ('dirty-tracked', lock['machine']['revision'], 'tracked'),
                ('dirty-untracked', lock['machine']['revision'], 'untracked')):
            tree = output / (name + '-checkout')
            subprocess.run(['git', '-C', str(machine), 'worktree', 'add', '--detach', str(tree), revision],
                           check=True, capture_output=True, timeout=45)
            if change == 'advance':
                (tree / 'g4-moving-head.txt').write_text('synthetic successor HEAD control\n')
                subprocess.run(['git', '-C', str(tree), 'add', 'g4-moving-head.txt'], check=True)
                subprocess.run(['git', '-C', str(tree), '-c', 'user.name=G4 fixture',
                                '-c', 'user.email=fixture@example.invalid', 'commit', '-qm',
                                'Synthetic moving HEAD control'], check=True, capture_output=True)
            elif change == 'tracked':
                with (tree / 'spec/catalog.json').open('ab') as stream:
                    stream.write(b'\n')
            elif change == 'untracked':
                (tree / 'g4-injected-input.txt').write_text('synthetic unauthorized input\n')
            expected = 'dependency revision differs from lock' if change == 'advance' else 'dependency checkout contains changes'
            cases.append((name, tree, saved_lock, expected))
        for name, tree, selected, expected in cases:
            CHECK.LOCK = selected
            code = CHECK.check(tree, output / name)
            evidence = output / name / 'evidence'
            report = CHECK.read(evidence / 'report.json')
            CHECK.require(code == 1 and report['status'] == 'Error', name + ' was not refused')
            CHECK.require(report.get('error', {}).get('message') == expected, name + ' failed for another reason')
            CHECK.require(report['checks'] == [] and report['commands'] == [], name + ' reached execution')
            CHECK.pins(evidence, CHECK.read(evidence / 'manifest.json')['files'])
            summary['controls'].append({'name': name, 'status': 'RefusedAsExpected', 'exit_code': code,
                'error': report['error'], 'observed_head': CHECK.git(tree, 'rev-parse', 'HEAD'),
                'locked_revision': lock['machine']['revision'], 'commands': 0, 'report': name + '/evidence/report.json',
                'report_sha256': CHECK.sha(evidence / 'report.json')})
        summary['status'] = 'Passed'
    except Exception as error:
        summary['error'] = {'type': type(error).__name__, 'message': str(error)}
    finally:
        CHECK.LOCK = saved_lock
    CHECK.save(output / 'report.json', summary)
    return 0 if summary['status'] == 'Passed' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--machine', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='new scratch directory outside repositories')
    args = parser.parse_args()
    return run(args.machine, args.output)


if __name__ == '__main__':
    raise SystemExit(main())
