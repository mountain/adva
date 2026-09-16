"""Migration boundaries: changed dependencies/history cannot pass by value alone."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("machine_dependency", ROOT / "scripts/check_machine_dependency.py")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


def repository(path):
    path.mkdir()
    subprocess.run(["git", "init", "-q", path], check=True)
    (path / "input").write_text("original")
    subprocess.run(["git", "-C", str(path), "add", "input"], check=True)
    subprocess.run(["git", "-C", str(path), "-c", "user.name=Fixture",
                    "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture"], check=True)
    return CHECK.git(path, "rev-parse", "HEAD")


def test_wrong_dependency_revision_is_refused(tmp_path):
    root = tmp_path / "dependency"
    repository(root)
    with pytest.raises(ValueError, match="revision differs"):
        CHECK.checkout(root, "0" * 40)


@pytest.mark.parametrize("path", ["input", "injected.py"])
def test_modified_or_untracked_dependency_is_refused(tmp_path, path):
    root = tmp_path / "dependency"
    revision = repository(root)
    (root / path).write_text("changed")
    with pytest.raises(ValueError, match="contains changes"):
        CHECK.checkout(root, revision)


def test_subdirectory_cannot_masquerade_as_dependency(tmp_path):
    root = tmp_path / "dependency"
    revision = repository(root)
    child = root / "child"
    child.mkdir()
    with pytest.raises(ValueError, match="independent checkout"):
        CHECK.checkout(child, revision)


def test_changed_input_is_refused_before_execution(tmp_path):
    subject = tmp_path / "input"
    subject.write_text("original")
    pinned = {"input": CHECK.sha(subject)}
    subject.write_text("changed")
    with pytest.raises(ValueError, match="pinned input differs"):
        CHECK.pins(tmp_path, pinned)


def test_equal_value_does_not_hide_changed_history():
    report = json.loads((ROOT / "docs/research/0140-native-run-evidence/arithmetic-result.adva").read_bytes())
    altered = copy.deepcopy(report)
    altered["compilation"] = {"history": "lost"}
    assert altered["evaluation"] == report["evaluation"]
    assert CHECK.native_observer(altered) != CHECK.native_observer(report)
    timing_only = copy.deepcopy(report)
    timing_only["phase_seconds"] = {"total_before_serialization": 100}
    assert CHECK.native_observer(timing_only) == CHECK.native_observer(report)


def test_existing_output_is_never_reused(tmp_path):
    marker = tmp_path / "report.json"
    marker.write_text("previous evidence")
    with pytest.raises(FileExistsError):
        CHECK.check(None, tmp_path)
    assert marker.read_text() == "previous evidence"


def test_retained_inputs_still_match_the_dependency_lock():
    CHECK.pins(ROOT, CHECK.read(CHECK.LOCK)["knowledge_inputs"])


def test_successor_lock_preserves_the_original_receipt_bindings():
    lock = CHECK.read(CHECK.LOCK)
    seen = {CHECK.sha(CHECK.LOCK)}
    while "previous_lock" in lock:
        previous = lock["previous_lock"]
        path = ROOT / previous["path"]
        digest = CHECK.sha(path)
        assert digest == previous["sha256"] and digest not in seen
        seen.add(digest)
        lock = CHECK.read(path)
    for run in ("continuity-01", "continuity-02", "ci-01-failed", "continuity-03"):
        assert CHECK.sha(ROOT / "dependencies/evidence" / run / "dependency.lock.json") in seen


@pytest.mark.parametrize("run", ("continuity-01", "continuity-02", "continuity-03"))
def test_retained_run_binds_inputs_history_and_native_replay(run):
    evidence = ROOT / "dependencies/evidence" / run
    manifest = CHECK.read(evidence / "manifest.json")
    assert set(manifest["files"]) == {
        p.relative_to(evidence).as_posix() for p in evidence.rglob("*")
        if p.is_file() and p.name != "manifest.json"
    }
    CHECK.pins(evidence, manifest["files"])
    report = CHECK.read(evidence / "report.json")
    lock = CHECK.read(evidence / "dependency.lock.json")
    assert report["knowledge"]["checker_sha256"] == CHECK.sha(evidence / "checker.py")
    if run == "continuity-03":
        assert CHECK.sha(ROOT / "scripts/check_machine_dependency.py") == CHECK.sha(evidence / "checker.py")
        # A successor must retain this exact receipt lock in its predecessor chain.
        active = CHECK.read(CHECK.LOCK)
        expected = CHECK.sha(evidence / "dependency.lock.json")
        seen = {CHECK.sha(CHECK.LOCK)}
        while "previous_lock" in active:
            prior = ROOT / active["previous_lock"]["path"]
            actual = CHECK.sha(prior)
            assert actual == active["previous_lock"]["sha256"] and actual not in seen
            seen.add(actual)
            active = CHECK.read(prior)
        assert expected in seen
    assert report["knowledge"]["lock_sha256"] == CHECK.sha(evidence / "dependency.lock.json")
    assert report["dependencies"]["machine_revision"] == lock["machine"]["revision"]
    assert report["dependencies"]["library_revision"] == lock["library"]["revision"]
    assert CHECK.native_observer(CHECK.read(evidence / "library-arithmetic-result.adva")) == (
        CHECK.native_observer(CHECK.read(evidence / "inputs/historical-arithmetic-result.adva")))
    for case, row in zip(("returned", "rejected", "suspended"), report["checks"][1:], strict=True):
        result = CHECK.read(evidence / case / "report.json")
        request = CHECK.read(evidence / "inputs" / (case + ".request.json"))
        raw = CHECK.read(evidence / case / result["execution"]["artifact"])
        receipt = CHECK.read(evidence / case / result["verification"]["artifact"])
        assert CHECK.sha(evidence / case / result["execution"]["artifact"]) == result["execution"]["sha256"]
        assert result["binary_sha256"] == report["build"]["binary_sha256"]
        assert result["outcome"] == row["outcome"]
        for field in ("program", "input", "fuel"):
            assert raw[field] == request[field]
        assert receipt["state"] == raw["state"]
        assert receipt["profile"] == raw["profile"] == result["native_profile"]
        assert receipt["verified_steps"] == raw["state"]["spent"] == len(raw["trace"]) == row["steps"]
        assert result["cost"]["native_calls"] == 3
    assert report["status"] == "Passed" and len(report["checks"]) == 4


def test_first_ci_failure_remains_a_failed_dependency_acquisition():
    evidence = ROOT / "dependencies/evidence/ci-01-failed"
    CHECK.pins(evidence, CHECK.read(evidence / "manifest.json")["files"])
    report = CHECK.read(evidence / "report.json")
    assert report["status"] == "Error" and report["checks"] == []
    assert report["error"]["message"] == "library-fetch failed; see retained stderr"
    assert "Permission denied (publickey)" in (evidence / "logs/library-fetch.stderr").read_text()
    assert not any(command["label"] == "build" for command in report["commands"])
