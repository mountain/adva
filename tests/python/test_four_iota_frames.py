"""Bounded four-iota-frame calibration; external evidence, no admission.

The assertions here are about what the retained checker decided by exhaustion.
They are not claims about any physical object, and they promote no native identity.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/four_iota_frames"
CHECKER = HERE / "checker.py"
CONTRACT = HERE / "contract.json"
EVIDENCE = HERE / "evidence.json"
NOTE = ROOT / "docs/research/0224-four-left-nested-iota-frames.md"
CLAIM_ID = "adva.bounded-experiment.four-iota-frames.v0"
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


def test_the_machinery_reproduces_the_received_cut_masks():
    s = section("S0_machinery_reproduces_received_cuts")
    assert len(s["families"]) == 12
    assert s["families_reproduced"] == 12
    assert s["every_family_reproduced"] is True
    assert s["pins_agree_with_the_received_dependencies_record"] is True
    for row in s["families"]:
        assert row["masks_agree"] is True, row["name"]
        assert row["declared_cuts"] == row["recomputed_cuts"], row["name"]


def test_the_four_towers_are_one_value_and_four_ledgers():
    s = section("S1_tower_reductions")
    assert s["event_counts"] == [0, 5, 10, 15]
    assert s["every_normal_form_is_iota"] is True
    for row in s["towers"]:
        assert row["normal_form"] == "i"
        assert row["event_count"] == len(row["events"])
        assert row["iota_leaves"] == 2 * row["k"] + 1
        assert row["source"].endswith("i")
    assert s["the_four_values_are_equal_and_the_four_ledgers_are_not"] is True


def test_every_cut_graph_is_a_path():
    s = section("S2_cut_structure")
    assert s["cut_counts"] == [1, 6, 11, 16]
    assert s["carrier_dimensions"] == [2, 12, 22, 32]
    assert s["every_cut_graph_is_a_path"] is True
    assert s["intrinsic_causal_dimension_claimed"] == 1
    for row in s["towers"]:
        assert row["cut_set_is_the_prefixes_of_a_total_order"] is True
        assert row["cut_graph_is_a_path"] is True
        assert len(row["edges"]) == row["cuts"] - 1
        assert sorted(row["degrees"]) == sorted(
            [1, 1] + [2] * (row["cuts"] - 2)
        ) if row["cuts"] > 2 else row["degrees"] == [0]


def test_the_frame_operators_hold_and_no_carrier_is_four_dimensional():
    s = section("S3_frame_operators")
    assert s["carrier_dimensions_are_pairwise_distinct"] is True
    assert s["no_carrier_dimension_is_four"] is True
    assert s["no_carrier_dimension_is_three_plus_one"] is True
    for row in s["towers"]:
        assert all(row["checks"].values()), row["k"]
        assert row["carrier_dimension"] == 2 * row["cuts"]
    assert s["towers"][0]["denominator"] == "1"
    assert s["towers"][0]["h0_scale"] == "L"
    assert [row["h0_scale"] for row in s["towers"][1:]] == ["L/4", "L/4", "L/4"]


def test_the_family_grows_by_one_five_event_cell():
    s = section("S4_unit_cell")
    assert s["cell"]["rules"] == ["i", "i", "s", "s", "k"]
    assert s["cell"]["events"] == 5
    assert s["cell"]["source"] == "@@iii"
    for row in s["towers"]:
        assert row["rules_are_the_cell_repeated"] is True, row["k"]
        assert row["blocks_are_chained"] is True, row["k"]
        assert row["events_equal_five_k"] is True, row["k"]
        assert row["events"] == 5 * row["k"]
        assert row["cuts"] == 5 * row["k"] + 1
        assert row["carrier_dimension"] == 10 * row["k"] + 2


def test_equal_dimension_does_not_make_two_frames_the_same_frame():
    s = section("S5_same_dimension_different_operator")
    assert s["same_cut_count"] is True
    assert s["same_carrier_dimension"] is True
    assert s["same_operator"] is False
    assert s["same_degrees"] is False
    assert s["received"]["name"] == "chain-and-single"
    assert s["received"]["charpoly_factorisation_claimed"] == "x (x-1) (x-2) (x-3)^2 (x-5)"
    assert s["received"]["spectrum_is_integral"] is True
    assert s["tower_k1"]["charpoly_factorisation_claimed"] == "x (x-1) (x-2) (x-3) (x^2-4x+1)"
    assert s["tower_k1"]["discriminant_of_the_quadratic_factor"] == 12
    assert s["tower_k1"]["quadratic_factor_is_irrational"] is True
    assert s["received"]["laplacian_charpoly"] != s["tower_k1"]["laplacian_charpoly"]


def test_the_role_obstruction_is_retained_and_not_repaired():
    s = section("S6_role_obstruction_and_refusals")
    assert s["received_families"] == 12
    assert s["received_families_carrying_an_aperture"] == 12
    assert s["towers_declare_no_port"] is True
    assert s["roles_bound"] is False
    assert all(not leaves for leaves in s["tower_aperture_leaves"].values())
    assert s["refusal_count"] >= 5
    assert any("one frame because their four normal forms are equal" in item
               for item in s["refusals"])
    assert any("physical metric" in item for item in s["refusals"])


def test_the_contract_states_its_protected_boundaries():
    contract = load(CONTRACT)
    protected = " ".join(contract["protected"])
    for phrase in (
        "No physical claim is made anywhere in this experiment",
        "is not decided here; the obstruction is retained instead",
        "Value equality is not used to identify processes",
        "Native admission is NotGranted",
        "No floating-point value enters any acceptance test",
    ):
        assert phrase in protected, phrase
    assert contract["level"].startswith("External exact")
    assert contract["base_commit"] == "9e567c1521ba7965f0580bada21c04389f9283ad"
    assert contract["objects"]["towers"] == ["i", "@@iii", "@@@@iiiii", "@@@@@@iiiiiii"]
    assert NOTE.is_file()


def test_the_note_states_the_residual_and_claims_no_physics():
    text = NOTE.read_text(encoding="utf-8")
    assert "Residual" in text
    flat = " ".join(text.split())
    for phrase in ("not claimed to be well-formed received source terms",
                   "physical spacetime",
                   "decided, checked or claimed here",
                   "no external corpus is opened"):
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
    assert any("path" in item for item in claim["forbidden_conflations"])
    for symbol in claim["code_symbol"].split("; "):
        assert (ROOT / symbol).is_file(), symbol
    assert claim["counterexample_boundary"].startswith("No physical")
