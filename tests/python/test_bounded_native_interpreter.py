"""Receive the frozen native campaign; this does not launch another search."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile

import blake3
import pytest

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments/bounded_native_interpreter"
EVIDENCE = EXP / "evidence/attempt-1"
SPEC = importlib.util.spec_from_file_location("bounded_machine_reference", EXP / "reference.py")
R = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(R)


def read_archive(name):
    with tarfile.open(EVIDENCE / (name + ".tar.gz"), "r:gz") as bundle:
        members = bundle.getmembers()
        assert len(members) <= 1000
        assert sum(m.size for m in members) <= 25165824
        assert all(m.isfile() and Path(m.name).name == m.name and m.size <= 2097152 for m in members)
        return {m.name: bundle.extractfile(m).read() for m in members}


def test_frozen_sources_and_complete_native_archives_are_bound():
    manifest = json.loads((EVIDENCE / "source-manifest.json").read_text())
    for name, digest in manifest.items():
        saved = (EVIDENCE / "sources" / name).read_bytes()
        assert hashlib.sha256(saved).hexdigest() == digest
        if name in {"crates/adva-witness/src/data_machine.rs",
                    "programs/bounded-interpreter/interpreter.adva",
                    "experiments/bounded_native_interpreter/reference.py",
                    "experiments/bounded_native_interpreter/contract.json"}:
            assert (ROOT / name).read_bytes() == saved
    # Historical dependency/CLI bytes remain pinned without freezing unrelated
    # future repository changes. A live profile mismatch still rejects natively.
    profile = blake3.blake3(b"adva.data-machine.transition.v0\0")
    profile.update((EVIDENCE / "sources/crates/adva-witness/src/data_machine.rs").read_bytes())
    profile.update((EVIDENCE / "sources/Cargo.lock").read_bytes())
    assert json.loads((EVIDENCE / "results.json").read_text())["profile"] == profile.hexdigest()
    execution = json.loads((EVIDENCE / "execution.json").read_text())
    assert execution["status"] == "Passed" and execution["deterministic_results_equal"]
    for process in execution["processes"]:
        archive = process["archive"]
        assert process["exit_code"] == 0 and not process["timed_out"]
        assert hashlib.sha256((EVIDENCE / archive["path"]).read_bytes()).hexdigest() == archive["sha256"]
        assert len(read_archive(process["name"])) == archive["files"]


def test_independent_receiver_checks_every_retained_native_state_edge():
    files = read_archive("primary")
    summary = json.loads(files["summary.json"])
    budget = R.Budget()
    regular = 0
    for row in summary["rows"]:
        if "sha256" not in row:
            continue
        name = row["name"]
        raw = files[name + ".run.adva"]
        assert hashlib.sha256(raw).hexdigest() == row["sha256"]
        if row["status"] == "Verified":
            continue
        report = json.loads(raw)
        program = json.loads(files[name + ".program.adva"])
        data = json.loads(files[name + ".input.json"])
        state = R.receive(report, program, data, report["fuel"], summary["profile"], budget)
        if name.startswith("regular-"):
            regular += 1
            assert state["phase"] == {"kind": "returned", "value": R.integer(R.arithmetic_oracle(data))}
    assert regular == summary["regular_cases"] == 129
    assert budget.steps == summary["reference_steps"] == 16911


def test_fresh_process_matches_and_continuation_keeps_the_same_history():
    primary, fresh = read_archive("primary"), read_archive("fresh")
    assert primary.keys() == fresh.keys()
    for name in primary:
        if not name.endswith((".stdout.txt", ".stderr.txt")) and name != "cost.json":
            assert primary[name] == fresh[name]
    whole = json.loads(primary["sample.run.adva"])
    resumed = json.loads(primary["resumed.run.adva"])
    assert whole["trace"] == resumed["trace"] and whole["state"] == resumed["state"]
    assert resumed["segments"][1] == {"start": 17, "end": 134, "replayed": 17}
    exhausted = json.loads(primary["still-exhausted.run.adva"])
    assert exhausted["status"] == "FuelExhausted" and exhausted["state"]["spent"] == 17
    loop = json.loads(primary["loop.run.adva"])
    assert loop["status"] == "FuelExhausted" and loop["state"]["phase"] == {"kind": "running"}


def test_independent_reception_refuses_trace_and_context_mutations():
    files = read_archive("primary")
    original = json.loads(files["prefix.run.adva"])
    for field in ("digest", "pc", "fuel"):
        report = json.loads(files["prefix.run.adva"])
        if field == "digest":
            report["trace"][2]["state_digest"] = "00"
        elif field == "pc":
            report["trace"][2]["next_pc"] += 1
        else:
            report["fuel"] = True
        with pytest.raises(AssertionError):
            R.receive(report, original["program"], original["input"], 2048, original["profile"], R.Budget())
