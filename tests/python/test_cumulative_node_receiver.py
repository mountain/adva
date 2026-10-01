import hashlib
import json
from pathlib import Path
import tarfile
import tomllib


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments" / "cumulative_node_receiver"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_cumulative_node_receiver_evidence_is_self_consistent():
    evidence = EXPERIMENT / "evidence"
    manifest = json.loads((evidence / "manifest.json").read_text())
    execution = json.loads((evidence / "execution.json").read_text())
    prior = json.loads((evidence / "prior-invalid-context.json").read_text())
    contract = json.loads((EXPERIMENT / "contract.json").read_text())

    assert manifest["classification"] == {
        "attempt-1": "InvalidContext",
        "attempt-2": "PassedAfterCorrectionReplay",
    }
    archive = evidence / manifest["archive"]
    assert sha(archive) == manifest["archive_sha256"]
    actual = {}
    with tarfile.open(archive, "r:gz") as bundle:
        for member in bundle.getmembers():
            assert member.isfile() and not member.issym() and not member.islnk()
            body = bundle.extractfile(member).read()
            actual[member.name] = {"bytes": len(body),
                                   "sha256": hashlib.sha256(body).hexdigest()}
    assert actual == manifest["entries"]
    assert len(actual) == manifest["files"] == 40
    assert sum(item["bytes"] for item in actual.values()) == manifest["expanded_bytes"]

    assert execution["status"] == "PassedAfterCorrectionReplay"
    assert execution["failure"] is None
    assert execution["main_at_start"] == contract["main_at_start"]
    assert execution["implementation_correction_replays"] == 1
    assert execution["prior_invalid_context_reserved_units"] == 30722
    assert execution["replay_reserved_units"] == 30722
    assert execution["cumulative_reserved_units"] == 61444
    assert execution["node_processes"] == 2
    assert execution["reported_work_units"] == 6841 + 14207
    assert [run["outcome"] for run in execution["runs"]] == [
        "ProvenUncommittedLedger", "StoredCommitted"
    ]
    assert all(run["reserved_units"] == 15361 and run["reported_work"] <= 15360
               for run in execution["runs"])
    assert prior["classification"] == "InvalidContext"
    assert prior["reserved_units_retained"] == 30722
    assert prior["recorded_main"] != prior["actual_main"] == contract["main_at_start"]

    for name, expected in execution["source_sha256"].items():
        assert sha(ROOT / name) == expected
    assert sha(ROOT / "experiments/commit_snapshot_crosscheck/evidence/attempt-1.tar.gz") == \
        contract["pins"]["archive_sha256"]


def test_cumulative_node_receiver_claim_is_bounded():
    claims = tomllib.loads((ROOT / "docs" / "claims.toml").read_text())["claim"]
    claim = next(item for item in claims
                 if item["claim_id"] == "adva.bounded-experiment.cumulative-node-receiver.v0")
    assert claim["status"] == "bounded-experiment"
    assert claim["dependencies"] == []
    assert "No authentication" in claim["counterexample_boundary"]
    assert "A correction replay with a reset resource account" in claim["forbidden_conflations"]
