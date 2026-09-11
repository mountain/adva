#!/usr/bin/env python3
"""Exclusive, finite attempt ledger; never starts a continuation automatically.

ChatGPT (OpenAI), through Mingli Yuan's account as an authorized proxy.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['first', 'correction', 'replay'])
    parser.add_argument('--compare')
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    contract_raw = (here/'contract.json').read_bytes()
    digest = hashlib.sha256(contract_raw).hexdigest()
    contract = json.loads(contract_raw)
    limits = contract['budget']
    ledger_path, lock = here/'execution.json', here/'execution.lock'
    with lock.open('x'):
        pass
    try:
        ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {
            'schema': 'adva.external.borromean-longitude-session.v0',
            'contract_sha256': digest, 'attempts': [],
            'authorship': 'ChatGPT (OpenAI), account proxy is not review or a correctness guarantee.'}
        attempts = ledger['attempts']
        assert ledger['contract_sha256'] == digest, 'contract changed within session'
        assert len(attempts) < limits['max_process_attempts'], 'session exhausted'
        assert all(a['state'] == 'Finished' for a in attempts), 'unfinished attempt retained; stop'
        assert (args.mode == 'first') == (not attempts), 'first only once'
        assert args.mode != 'correction' or (
            sum(a['mode'] == 'correction' for a in attempts) < limits['max_correction_attempts']
            and attempts[-1]['returncode'] != 0), 'correction requires a retained failure'
        assert args.mode != 'replay' or (
            args.compare and attempts[-1]['returncode'] == 0 and
            sum(a['mode'] == 'replay' for a in attempts) < limits['max_successful_fresh_replays']), 'replay requires a passed attempt'
        used = sum(a['elapsed_including_ledger_seconds'] for a in attempts)
        assert used+limits['per_attempt_outer_seconds'] <= limits['total_outer_seconds'], 'total wall budget'
        ordinal = len(attempts)+1
        output = here/('replay-01.json' if args.mode == 'replay' else f'attempt-{ordinal:02}.json')
        assert not output.exists(), 'do not overwrite evidence'
        source = (here/'check.py').read_bytes()
        entry = {'ordinal': ordinal, 'mode': args.mode, 'state': 'Running',
                 'source_sha256': hashlib.sha256(source).hexdigest(), 'output': output.name,
                 'outer_seconds': limits['per_attempt_outer_seconds']}
        attempts.append(entry)
        started = time.monotonic()
        def save():
            temporary = here/'execution.pending.json'
            temporary.write_text(json.dumps(ledger, indent=2, sort_keys=True)+'\n')
            temporary.replace(ledger_path)
        save()  # Reserve the attempt before it can consume mathematical fuel.
        cmd = [sys.executable, '-B', '-S', str(here/'check.py'), '--output', str(output)]
        if args.compare:
            cmd += ['--compare', str(Path(args.compare).resolve())]
        try:
            completed = subprocess.run(cmd, capture_output=True, text=True,
                                       timeout=limits['per_attempt_outer_seconds'])
            entry.update(returncode=completed.returncode, stdout=completed.stdout[:16384],
                         stderr=completed.stderr[:16384])
        except subprocess.TimeoutExpired:
            entry.update(returncode=124, stdout='', stderr='Outer timeout; child killed')
        if entry['returncode'] != 0:
            snapshot = here/f'failed-source-{ordinal:02}.py'
            with snapshot.open('xb') as destination:
                destination.write(source)
            entry['retained_failed_source'] = snapshot.name
        entry['report_exists'] = output.exists()
        if output.exists():
            entry['report_sha256'] = hashlib.sha256(output.read_bytes()).hexdigest()
        entry['state'] = 'Finished'
        entry['elapsed_before_final_ledger_seconds'] = time.monotonic()-started
        entry['elapsed_including_ledger_seconds'] = time.monotonic()-started
        save()
        # Finalize measured checkpoint cost. This last fixed-size replacement
        # itself is bounded by the parent tool and not part of child CPU data.
        entry['elapsed_including_ledger_seconds'] = time.monotonic()-started
        save()
        print(json.dumps(entry))
        return entry['returncode']
    finally:
        lock.unlink()


if __name__ == '__main__':
    raise SystemExit(main())
