"""Protocol and observation boundaries; no new native or SKI research execution."""

import copy

import pytest
from adva.advance import observe, partitions, require_pin
from adva.quine_relay import digest


def test_changed_predecessor_is_not_a_continuation():
    raw = b'{"round":5}\n'
    require_pin(raw, digest(raw))
    with pytest.raises(ValueError, match="pinned input"):
        require_pin(raw + b" ", digest(raw))


def test_equal_values_and_histograms_retain_an_order_collision():
    a = {
        "value": 7,
        "node_count": 3,
        "operation_histogram": {"a": 2, "b": 1},
        "ordered_operation_names": ["a", "a", "b"],
    }
    b = {**a, "ordered_operation_names": ["a", "b", "a"]}
    ladder = partitions({"original": a, "reordered": b})
    assert [len(level["classes"]) for level in ladder] == [1, 1, 1, 2]
    assert ladder[-1]["classes"] == [["original"], ["reordered"]]


def test_observer_refinement_keeps_prior_value_distinctions():
    a = {
        "value": 7,
        "node_count": 1,
        "operation_histogram": {"constant": 1},
        "ordered_operation_names": ["constant"],
    }
    b = {**a, "value": 8}
    assert [len(level["classes"]) for level in partitions({"a": a, "b": b})] == [2] * 4


@pytest.fixture
def native_protocol():
    # A protocol fixture, not an admitted diagram or a fabricated native execution.
    def wire(node):
        return {"producer": {"kind": "node", "node": node}}

    def node(n, name, inputs):
        return {
            "id": n,
            "inputs": [wire(i) for i in inputs],
            "operation": {"namespace": "adva.builtin", "version": 1, "name": name},
        }

    return {
        "status": "ByteFrontierEvaluated",
        "compilation": {
            "certificate": dict.fromkeys(
                ("types", "linear_use", "diagram_integrity", "module_links", "call_history"),
                "checked",
            ),
            "result": {
                "nodes": [
                    node(0, "constant", []),
                    node(1, "constant", []),
                    node(2, "add", [0, 1]),
                    node(3, "constant", []),
                ],
                "outputs": [wire(2), wire(3)],
            },
        },
        "evaluation": {
            "values": [7, 8],
            "certificate": {
                "diagram_integrity": "checked",
                "operation_rules_checked": True,
                "input_types_checked": True,
                "executed_nodes": [0, 1, 2, 3],
            },
        },
    }


def test_each_output_reads_only_its_explicit_dependency_cone(native_protocol):
    before = copy.deepcopy(native_protocol)
    rows = observe(native_protocol, bytes([7, 8]))
    assert [r["retained_native_node_ids"] for r in rows] == [[0, 1, 2], [3]]
    assert [r["ordered_operation_names"] for r in rows] == [
        ["constant", "constant", "add"],
        ["constant"],
    ]
    assert native_protocol == before


def test_unexecuted_nodes_cannot_support_observation(native_protocol):
    native_protocol["evaluation"]["certificate"]["executed_nodes"].pop()
    with pytest.raises(ValueError, match="execution coverage"):
        observe(native_protocol, bytes([7, 8]))


@pytest.mark.parametrize("field", ["linear_use", "diagram_integrity", "types"])
def test_missing_native_checks_are_refused(native_protocol, field):
    native_protocol["compilation"]["certificate"].pop(field)
    with pytest.raises(ValueError, match="compilation certificate"):
        observe(native_protocol, bytes([7, 8]))


def test_bytes_must_match_fresh_native_values(native_protocol):
    with pytest.raises(ValueError, match="value/output protocol"):
        observe(native_protocol, bytes([7, 9]))


def test_boolean_cannot_impersonate_a_native_number(native_protocol):
    native_protocol["evaluation"]["values"] = [True, 8]
    with pytest.raises(ValueError, match="value/output protocol"):
        observe(native_protocol, bytes([1, 8]))
