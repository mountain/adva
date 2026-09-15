"""Receive the retained self-interpretation scaling preflight; it launches no run.

The preflight's checker (`experiments/self_interpretation_scaling/check.py`)
generates meta programs, interprets object programs of a declared subset and
submits two over-bound programs to the CLI. Nothing here re-executes that: this
test reads the retained record, rebuilds the length model from the generator, and
checks that the recorded prices, refusals and positive results are the declared
ones.
"""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments/self_interpretation_scaling"
EVIDENCE = EXP / "evidence/attempt-1"

SPEC = importlib.util.spec_from_file_location("scaling_check", EXP / "check.py")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


def results():
    return json.loads((EVIDENCE / "results.json").read_text())


def cases():
    return {case["name"]: case for case in results()["cases"]}


def test_the_record_is_a_completed_attempt():
    record = results()
    assert record["verdict"] == "Passed" and not record["failures"]
    assert record["launches"] == 11 <= 24
    assert len(record["cases"]) == 11


def test_the_subset_interpreter_returns_the_declared_values():
    recorded = cases()
    for name, value, steps in (
        ("A2-input-then-return-slot1", 7, 35),
        ("A2-input-then-return-slot0", 9, 29),
        ("A3-three-object-instructions", 4, 44),
        ("B2-constant-then-return", 5, 44),
    ):
        assert recorded[name]["status"] == "Returned"
        assert recorded[name]["returned_value"] == {"kind": "integer", "value": value}
        assert recorded[name]["steps"] == steps


def test_object_level_refusals_carry_their_retained_reason():
    recorded = cases()
    for name, reason in (
        ("refusal-unsupported-object-opcode", "unsupported object opcode"),
        ("refusal-fell-off-the-end", "object program fell off its end"),
        ("refusal-return-slot-out-of-range", "object return register out of range"),
        ("refusal-input-slot-out-of-range", "object register index out of range"),
        ("refusal-object-reads-unwritten-slot", "uninitialized register"),
    ):
        assert recorded[name]["status"] == "Rejected"
        assert recorded[name]["phase_reason"] == reason
        assert recorded[name]["steps"] > 0


def test_the_instruction_bound_refuses_the_larger_metas():
    recorded = cases()
    lengths = results()["subset_interpreter"]["meta_program_lengths"]
    bound = results()["subset_interpreter"]["declared_instruction_bound"]
    assert lengths["B2"] == 108 <= bound < lengths["C2"] == 166
    assert results()["nineteen_opcode_ladder"]["generated_instructions"] == 295
    for name in ("refusal-meta-four-opcodes-166", "refusal-meta-nineteen-opcode-floor"):
        assert recorded[name]["exit_code"] == 2
        assert "invalid program schema or capacity" in recorded[name]["stderr"]
        assert "status" not in recorded[name]


def test_the_length_model_still_describes_the_generator():
    record = results()
    shapes = {
        "A1": (["input", "return"], 1),
        "A2": (["input", "return"], 2),
        "A3": (["input", "return"], 3),
        "B1": (["input", "constant", "return"], 1),
        "B2": (["input", "constant", "return"], 2),
        "C1": (["input", "constant", "copy", "return"], 1),
        "C2": (["input", "constant", "copy", "return"], 2),
    }
    bodies = CHECK.body_lengths()
    for name, (ops, length) in shapes.items():
        generated = len(CHECK.meta_program(ops, length)["code"])
        assert generated == record["subset_interpreter"]["meta_program_lengths"][name]
        assert generated == CHECK.reconstructed_length(ops, length, bodies)
    assert [op for op in ("input", "return", "constant", "copy") if op not in bodies] == []
    assert record["subset_interpreter"]["measured_body_lengths"] == {
        "input": 13, "return": 11, "constant": 16, "copy": 26
    }
    assert record["subset_interpreter"]["block_cost_per_extra_object_instruction"] == 33
    assert record["subset_interpreter"]["opcode_case_cost_per_block"] == 19


def test_the_nineteen_opcode_ladder_holds_nineteen_declared_placeholders():
    generated = CHECK.meta_program(CHECK.FULL_GRAMMAR_ORDER, 1)
    assert len(generated["code"]) == 295
    assert len(CHECK.FULL_GRAMMAR_ORDER) == 19
    assert len(CHECK.PLACEHOLDER_OPS) == 15
    assert results()["nineteen_opcode_ladder"]["admitted"] is False


def test_the_native_step_prices_are_recorded_per_interpreted_instruction():
    prices = results()["executed_steps_per_object_instruction"]
    assert prices == {
        "A2-input-then-return-slot1": 17.5,
        "A2-input-then-return-slot0": 14.5,
        "A3-three-object-instructions": 14.67,
        "B2-constant-then-return": 22.0,
    }
