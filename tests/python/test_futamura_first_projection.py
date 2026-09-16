"""Receive the retained first-Futamura-projection calibration; it launches no run.

The calibration's checker (`experiments/futamura_first_projection/check.py`) builds a
compiler from the frozen interpreter, compiles all 129 frozen arithmetic trees,
instantiates every emitted residual and executes it directly. Nothing here re-executes
that: this test reads the retained record, rebuilds the compiler from the frozen
interpreter and re-checks the construction rule and the recorded accounting.
"""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments/futamura_first_projection"
EVIDENCE = EXP / "evidence/attempt-1"
INTERPRETER = ROOT / "programs/bounded-interpreter/interpreter.adva"

SPEC = importlib.util.spec_from_file_location("futamura_check", EXP / "check.py")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


def results():
    return json.loads((EVIDENCE / "results.json").read_text())


def test_the_record_is_a_completed_attempt():
    record = results()
    assert record["verdict"] == "Passed" and not record["failures"]
    assert record["family"] == 129
    assert record["launches"] == 387 <= 512
    assert len(record["cases"]) == 129


def test_the_compiler_is_the_frozen_interpreter_plus_a_declared_epilogue():
    interpreter = json.loads(INTERPRETER.read_text())
    compiler = json.loads((EVIDENCE / "compiler.adva").read_text())
    relationship = CHECK.compiler_relationship(interpreter, CHECK.build_compiler(interpreter))
    assert relationship["body_identical_except_final_return"] is True
    assert relationship["interpreter_instructions"] == 51
    assert relationship["compiler_instructions"] == 62
    assert relationship["epilogue_instructions"] == 11
    assert relationship["registers_added"] == 5
    assert compiler == CHECK.build_compiler(interpreter)
    assert results()["compiler_relationship"] == relationship


def test_every_case_agrees_three_ways_and_the_residual_is_three_instructions():
    cases = results()["cases"]
    assert len({c["residual_instructions"] for c in cases}) == 1
    assert cases[0]["residual_instructions"] == 3
    for case in cases:
        assert case["interpreted_value"] == case["residual_value"] == case["oracle_value"]
        assert case["residual_steps"] == 3
        assert case["interpreted_steps"] >= 24
        assert case["compile_steps"] >= 35


def test_the_accounting_records_the_compile_cost_and_the_reuse_break_even():
    totals = results()["totals"]
    assert totals["total_interpreted_steps"] == 15966
    assert totals["total_compile_plus_residual_steps"] == 17772
    assert totals["total_compile_plus_residual_steps"] > totals["total_interpreted_steps"]
    assert totals["residual_steps_min"] == totals["residual_steps_max"] == 3
    for case in results()["cases"]:
        compile_cost = case["compile_steps"]
        saved = case["interpreted_steps"] - case["residual_steps"]
        assert (case["compile_steps"] + 2 * case["residual_steps"]
                <= 2 * case["interpreted_steps"]), case
        assert saved > 0
        assert compile_cost > 0


def test_the_interpreted_side_is_the_frozen_campaign_evidence():
    assert results()["interpreted_side_matches_frozen_run_bytes"] is True


def test_the_residual_encoding_instantiates_to_the_declared_program():
    residual = json.loads((EVIDENCE / "residuals" / "regular-000.json").read_text())
    program = CHECK.instantiate(residual)
    assert residual["tag"] == CHECK.RESIDUAL_PROGRAM_TAG
    assert [instruction["op"] for instruction in program["code"]] == [
        "constant", "box_integer", "return"]
    assert program["registers"] == [{"name": "r0", "kind": "integer"},
                                    {"name": "r1", "kind": "data"}]
    assert program["code"][0]["value"] == -1


def test_the_retained_archive_holds_the_raw_attempt():
    record = results()["retained"]
    assert record["archive"] == "attempt.tar.gz"
    assert record["archive_files"] == 1161
    assert record["archive_digests_verified"] is True
    assert (EVIDENCE / record["archive"]).exists()
