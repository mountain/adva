"""Integrity and finite artifact boundary; not native receiver evidence."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "experiments/schedule_state_dag"
EVIDENCE = PACKAGE / "evidence/attempt-1"


def test_state_dag_archive_and_source_integrity():
    manifest = json.loads((EVIDENCE / "manifest.json").read_text())
    assert set(manifest) == {p.name for p in EVIDENCE.iterdir() if p.name != "manifest.json"}
    for name, digest in manifest.items():
        assert hashlib.sha256((EVIDENCE / name).read_bytes()).hexdigest() == digest
    for name, digest in json.loads((EVIDENCE / "sources.json").read_text()).items():
        assert hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest() == digest


def test_state_sharing_preserves_paths_without_cost_claim():
    rows = json.loads((EVIDENCE / "results.json").read_text())
    execution = json.loads((EVIDENCE / "execution.json").read_text())
    assert execution["status"] == "PassedArtifactLevel"
    assert execution["native_receiver_executed"] is False
    expected = [("diamond", 7, 5, 2, 13, 30),
                ("three", 16, 8, 6, 31, 67),
                ("delayed", 9, 6, 2, 17, 38),
                ("two-chains", 19, 9, 6, 37, 77)]
    for row, (name, prefixes, states, words, forming, receiving) in zip(rows[:4], expected):
        assert (row["name"], row["prefix_records"], row["dag_states"]) == (name, prefixes, states)
        assert len({tuple(w) for w in row["legal_words"]}) == words
        assert row["formation_cost"]["counted_units"] == forming
        assert row["receiving_cost"]["counted_units"] == receiving
    assert sum(x["formation_cost"]["counted_units"] + x["receiving_cost"]["counted_units"] for x in rows[:4]) == 310
    assert [(x["name"], x["outcome"]) for x in rows[4:]] == [
        ("missing-edge", "UnknownCoverage"), ("missing-state", "UnknownCoverage"),
        ("wrong-next", "InvalidEvidence"), ("duplicate-state", "InvalidEvidence"),
        ("wrong-binding", "InvalidContext"), ("unreachable-state", "InvalidEvidence")]
    assert sum(x["cost"]["counted_units"] for x in rows[4:]) == 114


if __name__ == "__main__":
    test_state_dag_archive_and_source_integrity()
    test_state_sharing_preserves_paths_without_cost_claim()
    print("2 state-DAG artifact checks passed; native receiver remains Unknown")
