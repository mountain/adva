"""TC-050: exercise the live application replay boundary against frozen v0."""
import json
import subprocess
import sys

import pytest

from test_recovery_receipt_application import EXPERIMENT

ARCHIVE = EXPERIMENT / 'evidence' / 'attempt-1'


def invoke(program, ledger, recovery):
    result = subprocess.run(
        [sys.executable, str(EXPERIMENT / program), '--ledger', str(ledger),
         '--recovery', str(recovery)], capture_output=True, check=True, timeout=5)
    return json.loads(result.stdout)


MUTATIONS = [
    ('attempt_id', ''), ('attempt_id', 1), ('channel_id', ''), ('channel_id', None),
    *[(key, bad) for key in ('pair_digest', 'source_pending_sha256',
                            'witness_sha256') for bad in (None, 'A' * 64, '0' * 63)],
    *[('coverage', bad) for bad in (None, [], [0], [0, 1, 2], [True, 3],
                                  [0, False], [-1, 3], [3, 0], [0, 3.0])],
    ('result_sha256', None), ('result_sha256', 'bad'),
    ('state', 'cancelled'),
    ('attempt_id', 'other'), ('pair_digest', '0' * 64),
    ('witness_sha256', '0' * 64), ('channel_id', 'other'),
    ('coverage', [0, 2]), ('result_sha256', '0' * 64),
]


@pytest.mark.parametrize('key,bad', MUTATIONS)
def test_corrupt_same_receipt_terminal_rejected(tmp_path, key, bad):
    terminal = json.loads((ARCHIVE / 'application/alpha/ledger.json').read_bytes())
    terminal[key] = bad
    raw = json.dumps(terminal, sort_keys=True, separators=(',', ':')).encode()
    ledger = tmp_path / 'ledger.json'
    ledger.write_bytes(raw)
    recovery = ARCHIVE / 'parent/alpha-positive/receipt.json'
    # Each control directly demonstrates the old replay shortcut.
    assert invoke('apply_frozen_v0.py', ledger, recovery)['outcome'] == 'ReplayRefused'
    result = invoke('apply.py', ledger, recovery)
    assert result['outcome'] == 'InvalidEvidence'
    assert result['ledger_mutated'] is False
    assert result['target_processes'] == 0
    assert all(result[key] is False for key in
               ('effect_authority', 'retry_authority', 'refund_authority',
                'native_authority', 'free_authority'))
    assert ledger.read_bytes() == raw


@pytest.mark.parametrize('case,parent', [('alpha', 'alpha-positive'), ('gamma', 'gamma-negative')])
def test_live_application_and_exact_replay(tmp_path, case, parent):
    recovery = ARCHIVE / f'parent/{parent}/receipt.json'
    ledger = tmp_path / 'ledger.json'
    ledger.write_bytes((ARCHIVE / f'parent/{parent}/ledger.json').read_bytes())
    assert invoke('apply.py', ledger, recovery)['outcome'] == 'ResolutionApplied'
    raw = ledger.read_bytes()
    assert raw == (ARCHIVE / f'application/{case}/ledger.json').read_bytes()
    assert invoke('apply.py', ledger, recovery)['outcome'] == 'ReplayRefused'
    assert ledger.read_bytes() == raw


@pytest.mark.parametrize('bad', [None, 'A' * 64, '0' * 63])
def test_invalid_receipt_digest_rejected_before_conflict(tmp_path, bad):
    terminal = json.loads((ARCHIVE / 'application/alpha/ledger.json').read_bytes())
    terminal['recovery_receipt_sha256'] = bad
    raw = json.dumps(terminal, sort_keys=True, separators=(',', ':')).encode()
    ledger = tmp_path / 'ledger.json'
    ledger.write_bytes(raw)
    recovery = ARCHIVE / 'parent/alpha-positive/receipt.json'
    assert invoke('apply_frozen_v0.py', ledger, recovery)['outcome'] == 'ConflictRefused'
    assert invoke('apply.py', ledger, recovery)['outcome'] == 'InvalidEvidence'
    assert ledger.read_bytes() == raw


def test_cancelled_terminal_requires_null_result(tmp_path):
    terminal = json.loads((ARCHIVE / 'application/gamma/ledger.json').read_bytes())
    terminal['result_sha256'] = '0' * 64
    raw = json.dumps(terminal, sort_keys=True, separators=(',', ':')).encode()
    ledger = tmp_path / 'ledger.json'
    ledger.write_bytes(raw)
    recovery = ARCHIVE / 'parent/gamma-negative/receipt.json'
    assert invoke('apply_frozen_v0.py', ledger, recovery)['outcome'] == 'ReplayRefused'
    assert invoke('apply.py', ledger, recovery)['outcome'] == 'InvalidEvidence'
    assert ledger.read_bytes() == raw
