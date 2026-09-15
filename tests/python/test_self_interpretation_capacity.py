"""Receive the retained self-interpretation capacity preflight; it launches no run.

The preflight's own checker (`experiments/self_interpretation_capacity/check.py`)
generates its programs and executes twelve bounded cases. Nothing here re-executes
them: this test reads the retained record, recomputes the encoding count from the
unchanged object program, and checks that the recorded refusals sit exactly where
the declared bound is.
"""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments/self_interpretation_capacity"
EVIDENCE = EXP / "evidence/attempt-1"
OBJECT = ROOT / "programs/bounded-interpreter/interpreter.adva"

SPEC = importlib.util.spec_from_file_location("capacity_check", EXP / "check.py")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


def results():
    return json.loads((EVIDENCE / "results.json").read_text())


def cases():
    return {case["name"]: case for case in results()["cases"]}


def test_the_record_is_a_completed_attempt():
    record = results()
    assert record["verdict"] == "Passed" and not record["failures"]
    assert record["launches"] <= 24
    assert len(record["cases"]) == 12


def test_the_declared_data_bound_stops_the_inspectable_encoding():
    counting = results()["counting"]
    direct = counting["direct"]
    assert counting["instructions"] == 51
    assert direct["nodes"] == 169 and not direct["within_node_bound"]
    assert direct["nodes"] == (
        1 + direct["group_nodes"] + direct["instruction_nodes"] + direct["operand_leaves"]
    )
    assert direct["operand_leaves"] == 110
    assert direct["instructions_with_text_operands"] == 2
    packed = counting["packed"]
    assert packed["nodes"] == 110 and packed["within_node_bound"]
    assert not packed["decodable_in_language"]


def test_the_count_recomputes_from_the_object_program():
    recomputed = CHECK.count_encoding(json.loads(OBJECT.read_text()))
    assert recomputed == results()["counting"]


def test_the_bound_is_located_from_both_sides():
    recorded = cases()
    assert recorded["input-127-nodes"]["status"] == "Returned"
    assert recorded["input-127-nodes"]["input_nodes"] == 127
    for name, message in (
        ("input-128-nodes", "data capacity exceeded"),
        ("input-depth-13", "data capacity exceeded"),
        ("input-arity-9", "node arity exceeds 8"),
    ):
        assert recorded[name]["exit_code"] == 2
        assert message in recorded[name]["stderr"]
        assert "status" not in recorded[name]


def test_dispatch_and_index_costs_are_recorded_and_linear():
    record = results()
    recorded = cases()
    assert record["program_lengths"]["dispatch_ladder_17"] == 90
    assert record["program_lengths"]["dispatch_ladder_17"] <= record["limits"]["program_instructions"]
    assert recorded["dispatch-tag-0"]["steps"] == 9
    assert recorded["dispatch-tag-16"]["steps"] == 57
    assert record["dispatch_step_counts"]["dispatch-tag-unmatched"] == 56
    assert record["index_step_counts"] == {"0": 8, "4": 24, "8": 40}
    assert record["program_lengths"]["static_index_ladder_16"] == 85


def test_every_executed_case_returns_its_declared_value():
    recorded = cases()
    assert recorded["dispatch-tag-0"]["returned_value"] == {"kind": "integer", "value": 100}
    assert recorded["dispatch-tag-8"]["returned_value"] == {"kind": "integer", "value": 108}
    assert recorded["dispatch-tag-16"]["returned_value"] == {"kind": "integer", "value": 116}
    assert recorded["dispatch-tag-unmatched"]["returned_value"] == {"kind": "integer", "value": 999}
    assert recorded["index-ladder-5"]["returned_value"] == {"kind": "integer", "value": 205}
    assert recorded["index-step-8"]["returned_value"] == {"kind": "integer", "value": 8}
