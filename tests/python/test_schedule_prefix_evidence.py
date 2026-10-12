"""Integrity and finite evidence consistency, not a substitute for native replay."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / 'experiments/schedule_prefix'
EVIDENCE = PACKAGE / 'evidence/attempt-1'


def test_prefix_archive_and_source_integrity():
    manifest = json.loads((EVIDENCE / 'manifest.json').read_text())
    assert set(manifest) == {p.name for p in EVIDENCE.iterdir() if p.name != 'manifest.json'}
    for name, digest in manifest.items():
        assert hashlib.sha256((EVIDENCE / name).read_bytes()).hexdigest() == digest
    for name, digest in json.loads((EVIDENCE / 'sources.json').read_text()).items():
        assert hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest() == digest


def test_prefix_cost_and_history_boundary():
    rows = json.loads((EVIDENCE / 'results.json').read_text())
    execution = json.loads((EVIDENCE / 'execution.json').read_text())
    assert execution['status'] == 'Passed'
    assert len(rows) == 12
    assert execution['account']['launches'] == 18
    assert execution['account']['counted_units'] == 470
    units = 0
    for row, size in zip(rows[:4], [2, 6, 2, 6]):
        result = row['result']
        assert result['outcome'] == 'Verified'
        words = result['legal_words']
        assert len({tuple(w) for w in words}) == size
        witness = result['first_query']
        assert witness['outcome'] == 'NonSaturated'
        assert witness['left'] in words and witness['right'] in words
        assert witness['left'][0] != witness['right'][0]
        assert sorted(witness['left']) == sorted(witness['right'])
        assert result['naive_cut_dedup']['lost_histories'] == size - 1
        units += row['producer_cost']['counted_units']
        units += result['verification_cost']['counted_units'] + result['baseline_cost']['counted_units']
    for row in rows[4:]:
        assert row['result']['outcome'] == row['expected']
        units += row['result']['verification_cost']['counted_units']
    assert units == 470
    assert rows[10]['name'] == 'cut-dedup'
    assert rows[10]['result']['outcome'] == 'UnknownCoverage'


if __name__ == '__main__':
    test_prefix_archive_and_source_integrity()
    test_prefix_cost_and_history_boundary()
    print('2 prefix evidence checks passed; native replay remains separate')
