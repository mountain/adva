"""Archive consistency checks; these do not substitute for Rust semantic replay."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / 'experiments/schedule_receiving/evidence/attempt-1'


def test_complete_archive_inventory():
    manifest = json.loads((EVIDENCE / 'manifest.json').read_text())
    actual = {p.name for p in EVIDENCE.iterdir() if p.is_file() and p.name != 'manifest.json'}
    assert set(manifest) == actual
    for name, expected in manifest.items():
        assert hashlib.sha256((EVIDENCE / name).read_bytes()).hexdigest() == expected


def test_receiving_outcomes_and_counterpairs():
    results = json.loads((EVIDENCE / 'results.json').read_text())
    execution = json.loads((EVIDENCE / 'execution.json').read_text())
    assert execution['status'] == 'Passed'
    assert len(results) == execution['totals']['receiver_launches'] == 14
    assert sum(r['result']['work_units'] for r in results) == execution['totals']['work_units'] == 363
    for row in results:
        result = row['result']
        assert result['outcome'] == row['expected']
        if result['outcome'] == 'NonSaturated':
            a, b = result['left'], result['right']
            assert a['final_ideal'] == b['final_ideal']
            assert a['word'][0] != b['word'][0]
            assert a['steps'] != b['steps']
    assert next(r for r in results if r['label'] == 'incomplete-coverage')['result']['outcome'] == 'UnknownCoverage'


if __name__ == '__main__':
    test_complete_archive_inventory()
    test_receiving_outcomes_and_counterpairs()
    print('2 archive checks passed; Rust semantic replay is separate')
