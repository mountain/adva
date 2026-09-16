"""Receive the retained dynamic-residual calibration; it launches no run.

The calibration's checker (`experiments/futamura_dynamic_residual/check.py`) generates
its compiler, compiles all eight declared source programs and executes every emitted
residual directly. Nothing here re-executes that: this test reads the retained record,
regenerates the compiler and re-decodes the residuals.
"""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments/futamura_dynamic_residual"
EVIDENCE = EXP / "evidence/attempt-1"

SPEC = importlib.util.spec_from_file_location("dynamic_residual_check", EXP / "check.py")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


def results():
    return json.loads((EVIDENCE / "results.json").read_text())


def test_the_record_is_a_completed_attempt():
    record = results()
    assert record["verdict"] == "Passed" and not record["failures"]
    assert len(record["cases"]) == 16
    assert record["launches"] == 40 <= 96


def test_the_compiler_regenerates_byte_for_byte():
    regenerated = CHECK.compiler_program()
    retained = json.loads((EVIDENCE / "compiler.adva").read_text())
    assert regenerated == retained
    assert len(regenerated["code"]) == 41
    assert len(regenerated["registers"]) == 12
    assert results()["compiler"]["instructions"] == 41
    assert results()["compiler"]["registers"] == 12


def test_the_interpreter_is_the_reused_subset_interpreter():
    retained = json.loads((EVIDENCE / "interpreter.adva").read_text())
    assert retained == CHECK.SCALING_CHECK.meta_program(["input", "return"], 3)
    assert len(retained["code"]) == results()["interpreter"]["instructions"] == 103


def test_values_and_refusals_both_agree_after_compilation():
    cases = results()["cases"]
    returned = [c for c in cases if c["interpreted_status"] == "Returned"]
    refused = [c for c in cases if c["interpreted_status"] == "Rejected"]
    assert len(returned) == 12 and len(refused) == 4
    for case in cases:
        assert case["interpreted_status"] == case["residual_status"]
        assert case["interpreted_value"] == case["residual_value"]
        if case["interpreted_status"] == "Returned":
            assert case["residual_value"] == case["dynamic"]
            assert case["residual_instructions"] == 2
        else:
            assert case["residual_value"] is None
            assert case["residual_instructions"] == 1


def test_the_residual_is_shorter_than_the_source_and_the_cost_is_recorded():
    cases = results()["cases"]
    assert {c["residual_instructions"] for c in cases} == {1, 2}
    assert {c["source_instructions"] for c in cases} == {3}
    interpreted = sum(c["interpreted_steps"] for c in cases)
    residual = sum(c["residual_steps"] for c in cases)
    compiled = sum(c["compile_steps"] for c in cases)
    assert (interpreted, compiled, residual) == (728, 592, 28)
    assert compiled + residual < interpreted


def test_every_emitted_residual_decodes_inside_the_declared_encoding():
    for residual_path in sorted((EVIDENCE / "residuals").glob("*.json")):
        residual = json.loads(residual_path.read_text())
        code = CHECK._decode(residual)
        assert 1 <= len(code) <= 2
        assert code[-1]["op"] == "return"
        for instruction in code:
            assert instruction["op"] in {"input", "return"}


def test_the_retained_archive_holds_the_raw_attempt():
    record = results()["retained"]
    assert record["archive"] == "attempt.tar.gz"
    assert record["archive_files"] == 120
    assert record["archive_digests_verified"] is True
    assert (EVIDENCE / record["archive"]).exists()
