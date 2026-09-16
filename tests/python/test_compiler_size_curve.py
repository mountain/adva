"""Receive the retained compiler size curve; it launches no run.

The curve's checker (`experiments/compiler_size_curve/check.py`) generates a compiler
for each declared source shape, executes the whole family for every shape that fits and
submits the full-language ceiling compiler. Nothing here re-executes that: this test
reads the retained record and regenerates the compilers.
"""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments/compiler_size_curve"
EVIDENCE = EXP / "evidence/attempt-1"

SPEC = importlib.util.spec_from_file_location("curve_check", EXP / "check.py")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


def results():
    return json.loads((EVIDENCE / "results.json").read_text())


def curve():
    return {entry["axis"]: entry for entry in results()["curve"]}


def test_the_record_is_a_completed_attempt():
    record = results()
    assert record["verdict"] == "Passed" and not record["failures"]
    assert record["declared_bound"] == 128
    assert len(record["curve"]) == 10
    assert record["launches"] == 43 <= 256


def test_the_curve_matches_its_declared_axes():
    entries = results()["curve"]
    opcode_axis = [e for e in entries if e["axis"] == "opcodes" and e["length"] == 3]
    assert [e["compiler_instructions"] for e in opcode_axis] == [101, 146, 194, 257]
    assert [e["within_bound"] for e in opcode_axis] == [True, False, False, False]
    length_axis = [e for e in entries if e["axis"] == "length"]
    assert [e["compiler_instructions"] for e in length_axis] == [37, 69, 101]
    slot_axis = [e for e in entries if e["axis"] == "slots"]
    assert [e["compiler_instructions"] for e in slot_axis] == [69, 69]


def test_every_curve_entry_regenerates_from_the_generator():
    for entry in results()["curve"]:
        program = CHECK.compiler_program(entry["ops"], entry["slots"], entry["length"])
        assert len(program["code"]) == entry["compiler_instructions"], entry


def test_the_ceiling_is_a_lower_bound_and_was_refused():
    ceiling = results()["ceiling"]
    assert ceiling["compiler_instructions"] == 201 > ceiling["declared_bound"] == 128
    assert ceiling["opcodes"] == 19
    assert len(ceiling["placeholders"]) == 12
    assert ceiling["exit_code"] == 2
    assert "status" not in ceiling
    retained = json.loads((EVIDENCE / "ceiling-compiler.adva").read_text())
    assert len(retained["code"]) == 201
    assert retained == CHECK.compiler_program(CHECK.ALL_OPS, 2, 1)


def test_values_and_refusals_both_agree_with_the_independent_reference():
    cases = results()["cases"]
    returned = [c for c in cases if c["expected_status"] == "Returned"]
    refused = [c for c in cases if c["expected_status"] == "Rejected"]
    assert len(cases) == 28 and len(returned) == 16 and len(refused) == 12
    for case in cases:
        assert case["expected_status"] == case["residual_status"]
        assert case["expected_value"] == case["residual_value"]
    assert {c["expected_value"] for c in returned} == {3, 7, 9}
    assert {c["residual_instructions"] for c in cases} <= {3, 4, 6}


def test_the_reference_is_independent_of_the_generated_programs():
    """The reference executes the declared semantics itself; check it on one program."""
    program = CHECK.source_program(("input", "input"), 2, 3, 0)
    assert CHECK.reference(program, 7, 2) == ("Returned", 7)
    unwritten = CHECK.source_program(("input", "input"), 2, 2, 1)
    assert CHECK.reference(unwritten, 7, 2) == ("Rejected", None)


def test_the_retained_archive_holds_the_raw_attempt():
    record = results()["retained"]
    assert record["archive"] == "attempt.tar.gz"
    assert record["archive_files"] == 128
    assert record["archive_digests_verified"] is True
    assert (EVIDENCE / record["archive"]).exists()
