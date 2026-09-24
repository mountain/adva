"""Bounded signature calibration for the received frame; external evidence, no admission.

The assertions here are about what the retained checker decided by exact
computation. They are not claims about any physical object, and they promote no
native identity.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/iota_frame_signature"
CHECKER = HERE / "checker.py"
CONTRACT = HERE / "contract.json"
EVIDENCE = HERE / "evidence.json"
NOTE = ROOT / "docs/research/0225-a-complex-structure-admits-only-even-signatures.md"
CLAIM_ID = "adva.bounded-experiment.iota-frame-signature.v0"
TIMING_KEYS = ("installed_limits",)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def payload(report):
    """The mathematical payload, with timings and platform facts removed."""
    return {
        key: value
        for key, value in report.items()
        if not key.endswith("_ns")
        and not key.startswith("rss_high_water")
        and key not in TIMING_KEYS
    }


def invoke(checker, output, timeout=600):
    return subprocess.run(
        [sys.executable, "-S", str(checker), "--output", str(output)],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def section(name):
    return load(EVIDENCE)["sections"][name]


def test_retained_evidence_is_an_external_pass_inside_the_contract():
    report = load(EVIDENCE)
    contract = load(CONTRACT)
    assert report["status"] == "ExternalExactPass"
    assert report["checker_sha256"] == digest(CHECKER)
    assert report["contract_sha256"] == digest(CONTRACT)
    assert report["assertions"] <= contract["budget"]["max_assertions"]
    assert report["limits"] == contract["budget"]


def test_fresh_run_reproduces_the_retained_mathematical_payload(tmp_path):
    output = tmp_path / "fresh.json"
    completed = invoke(CHECKER, output)
    assert completed.returncode == 0, completed.stderr
    assert payload(load(output)) == payload(load(EVIDENCE))


def test_an_existing_output_is_never_overwritten(tmp_path):
    output = tmp_path / "keep.json"
    output.write_text("retained", encoding="utf-8")
    completed = invoke(CHECKER, output)
    assert completed.returncode != 0
    assert output.read_text(encoding="utf-8") == "retained"


def test_the_frame_instance_is_rebuilt_from_the_received_process():
    s = section("S0_frame_instance")
    assert s["process"] == "chain-and-single"
    assert s["cuts"] == 6 and s["carrier_dimension"] == 12
    assert s["degrees"] == ["2", "3", "2", "2", "3", "2"]
    assert s["d_max"] == "3" and s["h0_scale"] == "L/6"
    assert s["metric_G"] == "I"
    assert s["inertia_of_G"] == [12, 0]
    assert all(s["checks"].values())


def test_the_compatibility_system_has_the_declared_dimensions():
    s = section("S1_compatibility_system")
    assert s["general_dimension_is_two_n_squared"] is True
    assert s["symmetric_dimension_is_n_squared"] is True
    assert s["every_solution_commutes_with_J"] is True
    assert [row["n"] for row in s["orders"]] == [1, 2, 3]
    for row in s["orders"]:
        assert row["general_solution_dimension"] == 2 * row["n"] ** 2
        assert row["symmetric_solution_dimension"] == row["n"] ** 2
        assert row["general_solutions_have_the_block_shape"] is True
        assert row["every_basis_solution_commutes_with_J"] is True


def test_every_symmetric_nondegenerate_member_has_even_indices():
    s = section("S2_exhaustive_inertia")
    assert s["every_symmetric_nondegenerate_member_has_even_indices"] is True
    sizes = {1: 7, 2: 2401, 3: 19683}
    for row in s["families"]:
        assert row["members_examined"] == sizes[row["n"]]
        assert row["members_with_an_odd_index"] == []
        assert row["every_index_is_even"] is True
        assert row["nondegenerate_members"] == row["members_examined"] - row["degenerate_members"]
        for key in row["signatures_seen"]:
            positive, negative = (int(part) for part in key.split(","))
            assert positive % 2 == 0 and negative % 2 == 0
            assert positive + negative == 2 * row["n"]
    assert section("S2_exhaustive_inertia")["families"][1]["signatures_seen"] == {
        "0,4": 105, "2,2": 2138, "4,0": 105,
    }


def test_exactly_one_negative_direction_is_unreachable_on_four_dimensions():
    s = section("S3_four_dimensional_conclusion")
    assert s["carrier_dimension"] == 4
    assert s["reachable_signatures"] == [[0, 4], [2, 2], [4, 0]]
    assert s["unreachable_signatures"] == [[1, 3], [3, 1]]
    assert s["exactly_one_negative_direction_is_unreachable"] is True


def test_a_lorentzian_metric_costs_the_frame_identity():
    s = section("S4_lorentzian_cost")
    assert s["instance"]["carrier_dimension"] == 4
    assert s["instance"]["degrees"] == ["1", "1"]
    assert s["instance"]["d_max"] == "1" and s["instance"]["h0_scale"] == "L/2"
    identity = s["identity_metric"]
    assert identity["signature"] == [4, 0]
    assert identity["A_is_skew"] is True
    assert identity["residual_A_transpose_plus_A"] == [
        ["0"] * 4 for _ in range(4)
    ]
    lorentzian = s["lorentzian_metric"]
    assert lorentzian["signature"] == [3, 1]
    assert lorentzian["J_is_orthogonal"] is False
    assert lorentzian["A_is_skew"] is False
    assert lorentzian["residual_J_transpose_G_J_minus_G"] == [
        ["0", "0", "0", "0"],
        ["0", "-2", "0", "0"],
        ["0", "0", "0", "0"],
        ["0", "0", "0", "2"],
    ]
    assert lorentzian["residual_J_transpose_G_J_minus_G_absolute_sum"] == "4"
    assert lorentzian["residual_A_transpose_G_plus_G_A_absolute_sum"] == "4"
    assert s["the_frame_identity_holds_for_one_metric_and_fails_for_the_other"] is True


def test_the_involution_route_does_reach_a_lorentzian_signature():
    s = section("S5_involution_route")
    assert s["involution_diagonal"] == [1, 1, -1, -1]
    assert s["involution_squares_to_identity"] is True
    assert s["involution_is_compatible_with_the_lorentzian_metric"] is True
    assert s["involution_equals_J"] is False
    assert s["complex_structure_is_compatible_with_the_lorentzian_metric"] is False
    assert s["lorentzian_signature"] == [3, 1]


def test_the_refusals_are_declared_and_retained():
    s = section("S6_refusals")
    assert s["refusal_count"] >= 5
    assert any("physical spacetime" in item for item in s["refusals"])
    assert any("unreachable in general" in item for item in s["refusals"])


def test_the_contract_states_its_protected_boundaries():
    contract = load(CONTRACT)
    protected = " ".join(contract["protected"])
    for phrase in (
        "No physical claim is made anywhere in this experiment",
        "A signature is a property of a declared rational symmetric form",
        "not about reachability in general",
        "the earlier reading that a split structure must give two positives and two negatives",
        "Native admission is NotGranted",
    ):
        assert phrase in protected, phrase
    assert contract["level"].startswith("External exact")
    assert contract["base_commit"] == "ed38456ab4dd628a484874fa41dc97bd6fbb54ab"
    assert contract["objects"]["complex_structure_orders"] == [1, 2, 3]
    assert NOTE.is_file()


def test_the_note_retains_the_correction_and_claims_no_physics():
    text = NOTE.read_text(encoding="utf-8")
    assert "Residual" in text
    flat = " ".join(text.split())
    for phrase in ("no physical claim",
                   "That reading is wrong",
                   "never published",
                   "not decided here",
                   "a signature is a property of a declared rational form"):
        assert phrase in flat, phrase


def test_the_registered_claim_points_at_existing_artifacts():
    import tomllib

    claims = tomllib.loads((ROOT / "docs/claims.toml").read_text(encoding="utf-8"))["claim"]
    matches = [c for c in claims if c["claim_id"] == CLAIM_ID]
    assert len(matches) == 1
    claim = matches[0]
    assert claim["status"] == "bounded-experiment"
    assert claim["dimension"].startswith("external")
    assert claim["dependencies"] == []
    assert len(claim["forbidden_conflations"]) >= 8
    assert any("inertia" in item for item in claim["forbidden_conflations"])
    for symbol in claim["code_symbol"].split("; "):
        assert (ROOT / symbol).is_file(), symbol
    assert claim["counterexample_boundary"].startswith("No physical")
