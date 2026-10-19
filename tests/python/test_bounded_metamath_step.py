"""Receive finite Adva proof executions; external truth never replaces native traces."""

import hashlib
import importlib.util
import json
import tarfile
from copy import deepcopy
from pathlib import Path

import blake3
import pytest

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments/bounded_metamath_step"
EVIDENCE = EXP / "evidence/attempt-1"


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def archive(name):
    path = EVIDENCE / (name + ".tar.gz")
    with tarfile.open(path, "r:gz") as stream:
        members = stream.getmembers()
        assert len(members) < 500
        assert sum(m.size for m in members) < 67108864
        assert all(m.isfile() and Path(m.name).name == m.name for m in members)
        return {m.name: stream.extractfile(m).read() for m in members}


def test_program_is_the_reviewed_author_output_and_uses_only_existing_instructions():
    author = module("metamath_author", EXP / "author.py")
    program, labels = author.generated()
    assert program == json.loads((ROOT / "programs/bounded-metamath-step/checker.adva").read_text())
    assert labels == json.loads(
        (ROOT / "programs/bounded-metamath-step/instruction-labels.json").read_text()
    )
    assert len(program["registers"]) == 32
    assert len(program["code"]) == 264
    assert {x["op"] for x in program["code"]} <= {
        "input",
        "constant",
        "clear",
        "tag",
        "length",
        "field",
        "field_dynamic",
        "as_integer",
        "box_integer",
        "equal",
        "add",
        "branch",
        "jump",
        "node",
        "pack",
        "stack_length",
        "push",
        "pop",
        "return",
        "reject",
    }


def test_external_exit_zero_and_success_summary_cannot_hide_proof_errors():
    run = module("metamath_supervisor", EXP / "run.py")
    success = "All proofs in the database were verified in 0.00 s."
    assert run.external_accepted(success, "", 0)
    assert not run.external_accepted("?Error wrong substitution\n" + success, "", 0)
    assert not run.external_accepted(success, "?Warning incomplete proof", 0)
    assert not run.external_accepted(
        "No errors were found. However, proofs were not checked.", "", 0
    )
    assert not run.external_accepted(success, "", 1)


def test_frozen_sources_and_both_archives_have_exact_bindings():
    manifest = json.loads((EVIDENCE / "source-manifest.json").read_text())
    for name, digest in manifest.items():
        saved = EVIDENCE / "sources" / name
        assert hashlib.sha256(saved.read_bytes()).hexdigest() == digest
        # Historical VM and lock changes do not rewrite this retained run.
        if name.startswith(
            ("programs/bounded-metamath-step/", "experiments/bounded_metamath_step/")
        ):
            assert (ROOT / name).read_bytes() == saved.read_bytes()
    receipt = json.loads((EVIDENCE / "execution.json").read_text())
    assert receipt["status"] == "Passed"
    assert receipt["deterministic_native_reports"] is True
    for name in ("primary", "fresh"):
        raw = (EVIDENCE / f"{name}.tar.gz").read_bytes()
        assert hashlib.sha256(raw).hexdigest() == receipt["archives"][name]


def test_every_native_edge_and_external_control_is_received():
    files = archive("primary")
    result = json.loads(files["result.json"])
    source = EVIDENCE / "sources"
    reference = module(
        "metamath_frozen_instruction_reference",
        source / "experiments/bounded_self_compiler/reference.py",
    )
    program = json.loads((source / "programs/bounded-metamath-step/checker.adva").read_text())
    profile = blake3.blake3(b"adva.data-machine.transition.v1\0")
    profile.update((source / "crates/adva-witness/src/data_machine_v1.rs").read_bytes())
    profile.update((source / "Cargo.lock").read_bytes())
    assert result["profile"] == profile.hexdigest()
    assert result["status"] == "Passed"
    budget = reference.Budget(200000)
    run = module("metamath_external_log_reader", EXP / "run.py")
    for row in result["rows"]:
        name = row["name"]
        raw = files[name + ".run.adva"]
        assert hashlib.sha256(raw).hexdigest() == row["report_sha256"]
        report = json.loads(raw)
        data = json.loads(files[name + ".input.json"])
        selected = (
            json.loads(files[name + ".program.adva"]) if name.endswith("mutation") else program
        )
        state = reference.receive(report, selected, data, report["fuel"], result["profile"], budget)
        receipt = json.loads(files[name + ".receipt.adva"])
        assert receipt["state"] == state
        assert receipt["verified_steps"] == row["spent"] == state["spent"]
        if "external" in row:
            external = row["external"]
            stdout = files[name + "-metamath.stdout"]
            assert hashlib.sha256(stdout).hexdigest() == external["stdout_sha256"]
            assert hashlib.sha256(files[name + ".mm"]).hexdigest() == external["fixture_sha256"]
            assert (
                run.external_accepted(
                    stdout.decode(),
                    files[name + "-metamath.stderr"].decode(),
                    0,
                )
                == external["accepted"]
            )
    assert budget.steps == result["reference_steps"]
    cases = json.loads((source / "experiments/bounded_metamath_step/cases.json").read_text())
    assert result["cases"] == len(cases) == 21
    for case in cases:
        row = next(x for x in result["rows"] if x["name"] == case["name"])
        assert row["status"] == case["native"]
        assert row["external"]["accepted"] == case["external"]
    assert sum(x["status"] == "Returned" for x in result["rows"][:21]) == 8


def test_fresh_native_reports_match_and_budget_is_not_validity():
    a, b = archive("primary"), archive("fresh")
    result = json.loads(a["result.json"])
    for row in result["rows"]:
        name = row["name"]
        assert a[name + ".run.adva"] == b[name + ".run.adva"]
        assert a[name + ".receipt.adva"] == b[name + ".receipt.adva"]
    whole = json.loads(a["whole.run.adva"])
    resumed = json.loads(a["resumed.run.adva"])
    assert whole["trace"] == resumed["trace"]
    assert whole["state"] == resumed["state"]
    exhausted = json.loads(a["still-exhausted.run.adva"])
    assert exhausted["status"] == "FuelExhausted"
    assert exhausted["state"]["spent"] == 17
    assert exhausted["state"]["phase"] == {"kind": "running"}
    for name in ("token-bound", "proof-bound"):
        row = next(x for x in result["rows"] if x["name"] == name)
        assert row["status"] == "Rejected" and row["external"]["accepted"]


def test_independent_receiving_refuses_an_altered_trace():
    files = archive("primary")
    report = json.loads(files["substitute-once.run.adva"])
    reference = module(
        "metamath_mutation_reference",
        EVIDENCE / "sources/experiments/bounded_self_compiler/reference.py",
    )
    altered = deepcopy(report)
    altered["trace"][5]["state_digest"] = "00"
    with pytest.raises(AssertionError):
        reference.receive(
            altered,
            report["program"],
            report["input"],
            report["fuel"],
            report["profile"],
            reference.Budget(),
        )
