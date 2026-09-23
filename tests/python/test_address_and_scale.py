"""Bounded address-and-scale calibration; external evidence, no admission.

The assertions here are about what the retained checker decided by exhaustion.
They are not claims about any text, and they promote no native identity.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/address_and_scale"
CHECKER = HERE / "checker.py"
CONTRACT = HERE / "contract.json"
EVIDENCE = HERE / "evidence.json"
NOTE = ROOT / "docs/research/0217-what-the-address-sees-and-what-the-grid-already-forces.md"
CLAIM_ID = "adva.bounded-experiment.address-and-scale.v0"
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


def test_the_stated_formula_is_the_coordinate_formula():
    s = section("S1_declared_algorithm")
    assert s["heads"] == 81
    assert s["heads_reproduced"] == 81
    assert s["the_two_formulas_agree_on_every_head"] is True
    assert s["place_weights"] == {"family": [0, 1, 2], "section": [0, 3, 6],
                                  "district": [0, 9, 18], "quarter": [0, 27, 54]}
    assert "27" in s["coordinate_formula"]


def test_the_nine_rows_are_a_fiber_of_two_places():
    s = section("S2_nine_rows")
    assert s["heads"] == [1, 10, 19, 28, 37, 46, 55, 64, 73]
    assert s["count"] == 9 and s["spacing"] == 9
    assert s["place_constraints_needed"] == 2
    assert s["first_two_places_free"] is True
    assert s["the_nine_are_the_fiber_over_two_fixed_places"] is True


def test_the_split_is_a_congruence_for_no_nontrivial_modulus():
    s = section("S3_modulus")
    assert s["cut"] == 47 and s["sides"] == [47, 34]
    assert s["moduli_exhausted"] == 80
    assert s["moduli_that_work"] == [81]
    assert s["nontrivial_moduli_that_work"] == 0
    assert s["failing_moduli"] == 79
    assert s["small_case_tail_outnumbers_the_classes"] is True
    assert s["large_case_tail_elements_are_distinct"] is True
    assert s["the_cut_is_not_a_congruence"] is True


def test_the_boundary_is_the_translate_of_the_other_boundary():
    s = section("S4_translate")
    assert s["pairs"] == {"before": [7, 47], "after": [8, 48]}
    assert s["shift"] == [1, 2, 1, 1]
    assert s["the_two_pairs_share_one_shift"] is True
    assert s["shift_order"] == 3
    assert s["orbit_before"] == [7, 47, 69]
    assert s["orbit_after"] == [8, 48, 67]
    assert s["orbits_disjoint"] is True
    assert s["three_cycles"] == 27 and s["cycle_length"] == 3
    assert s["the_boundary_is_the_translate_of_the_other_boundary"] is True


def test_the_river_pairing_is_a_quotient_by_five():
    s = section("S5_river")
    assert s["fibers_of_reduction_modulo_five"] == [[1, 6], [2, 7], [3, 8], [4, 9], [5]]
    assert s["river_pairs"] == {"water": [1, 6], "fire": [2, 7], "wood": [3, 8],
                                "metal": [4, 9], "earth": [5]}
    assert s["every_pair_differs_by_five"] is True
    assert s["the_shift_on_ten_residues_has_no_fixed_point"] is True
    assert s["the_fifth_pair_is_five_against_ten_on_ten_numbers"] is True
    assert s["restricting_to_one_to_nine_leaves_exactly_one_number_without_a_partner"] == 5
    assert s["the_label_is_a_function_of_the_class"] is True


def test_the_calendar_arithmetic_is_the_texts_own():
    s = section("S6_calendar")
    assert s["cycle_float"] == 364.5 and s["year_float"] == 365.5
    assert s["two_extra_praises_are_one_day"] is True
    assert s["boundary_spacing"] == "9/2"
    assert s["boundary_count"] == 81
    assert s["cut_day_float"] == 211.5
    assert s["sides_in_praises"] == [423, 306]
    assert s["node_spacing"] == "731/48"


def test_the_near_miss_is_what_the_grid_forces():
    s = section("S6_calendar")
    assert s["grid_reach"] == "9/4" and s["grid_reach_days"] == 2.25
    assert len(s["nodes"]) == 24
    assert s["reported_node"] == 15
    assert s["reported_node_gap_days"] == "41/24"
    assert s["reported_rank_by_closeness"] == 14
    assert s["nodes_compared"] == 23
    # a closer node exists, far closer, and the reported one is worse than the median
    assert s["best_node"] == 14
    assert s["best_relative_float"] < s["reported_relative_float"] / 50
    assert float(__import__("fractions").Fraction(s["median_relative"])) < s["reported_relative_float"]
    assert s["every_node_is_within_the_reach_by_construction"] is True
    assert s["the_reported_near_miss_is_worse_than_the_median"] is True


def test_the_contract_states_its_protected_boundaries():
    contract = load(CONTRACT)
    protected = " ".join(contract["protected"])
    for phrase in (
        "no corpus count from any external repository is imported",
        "not against a collated edition",
        "are about definability in two declared algebras",
        "No floating-point value",
        "No native Rust witness",
    ):
        assert phrase in protected, phrase
    assert contract["input_document"] == (
        "docs/research/0217-what-the-address-sees-and-what-the-grid-already-forces.md"
    )
    assert contract["level"].startswith("External exact")
    assert NOTE.is_file()


def test_the_note_states_the_residual_and_imports_no_text():
    text = NOTE.read_text(encoding="utf-8")
    assert "Residual" in text
    flat = " ".join(text.split()).lower()
    for phrase in ("no text and no corpus count is imported",
                   "wenyan-relation-learning",
                   "the two invisibility results are about two declared algebras"):
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
    assert any("grid" in item for item in claim["forbidden_conflations"])
    for symbol in claim["code_symbol"].split("; "):
        assert (ROOT / symbol).is_file(), symbol
    assert claim["counterexample_boundary"].startswith("No text")
