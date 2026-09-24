"""Bounded gain-and-coverage calibration; external evidence, no admission.

The assertions here are about what the retained checker decided by exhaustion.
They are not claims about any text or corpus, and they promote no native identity.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/gain_and_coverage"
CHECKER = HERE / "checker.py"
CONTRACT = HERE / "contract.json"
EVIDENCE = HERE / "evidence.json"
NOTE = ROOT / "docs/research/0213-gain-coverage-and-the-number-that-was-already-fixed.md"
CLAIM_ID = "adva.bounded-experiment.gain-and-coverage.v0"
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


def invoke(checker, output, timeout=900):
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


def test_the_reduction_is_a_quotient_by_doubling():
    s = section("S1_doubling_quotient")
    assert s["lands_in_the_unit_octave"] is True
    assert s["factors_through_the_odd_part"] is True
    assert s["fibres_are_the_doubling_orbits"] is True
    assert s["odd_numbers_are_the_smallest_element_of_their_fibre"] is True
    assert s["identified_pair_example"] == [3, 12]
    assert s["fixed_points_are_the_powers_of_two"] is True
    assert s["fixed_point_count_to_the_limit"] == 11
    assert s["limit"] == 2000


def test_every_exact_hit_of_every_division_is_a_power_of_two():
    s = section("S2_exact_hits")
    assert s["only_the_unison_is_rational"] is True
    assert all(v == [0] for v in s["rational_positions_per_division"].values())
    assert s["divisions_checked"] == 8
    assert s["exact_hit_sets_identical_for_every_declared_division"] is True
    assert s["per_declared_limit"]["122"]["count"] == 7
    assert s["per_declared_limit"]["122"]["values"] == [1, 2, 4, 8, 16, 32, 64]
    assert s["per_declared_limit"]["1651"]["count"] == 11
    assert s["per_declared_limit"]["1651"]["values"] == [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
    for N in ("122", "1651"):
        assert s["per_declared_limit"][N]["count"] == s["per_declared_limit"][N]["binary_exponent_plus_one"]


def test_the_reported_maximum_distance_is_the_covering_radius():
    s = section("S3_coverage")
    assert s["covering_radius"] == "1/44"
    assert s["covering_radius_by_division"] == {"2": "1/4", "3": "1/6", "5": "1/10",
                                                "12": "1/24", "22": "1/44", "53": "1/106"}
    assert s["reported_maximum_distance"] == "0.02272"
    assert s["reported_maximum_is_the_covering_radius"] is True
    assert s["every_subset_satisfies_the_bound"] is True


def test_coverage_follows_from_the_point_count_alone():
    s = section("S3_coverage")
    assert s["coverage_threshold"] == {"1_percent": 113, "point_1_percent": 1237}
    measured = s["measured_coverage"]
    assert measured["1651"] == {"coverage_at_1_percent": 22, "coverage_at_point_1_percent": 22}
    assert measured["122"] == {"coverage_at_1_percent": 22, "coverage_at_point_1_percent": 4}
    # the two declared limits straddle the finer threshold and both clear the coarser one
    assert 1651 > s["coverage_threshold"]["point_1_percent"] > 122
    assert 122 > s["coverage_threshold"]["1_percent"]
    assert s["thresholds_are_odd_serial_number_index_bounds"] is True


def test_the_count_coincidence_is_one_of_fifteen():
    s = section("S4_count_arithmetic")
    assert s["residues"] == {"magneticSpaceGroups": 1, "typeIII": 3, "magneticLayerGroups": 0,
                             "magneticRodGroups": 20, "greyOrColorless": 10,
                             "magneticPointGroups": 12}
    assert s["exact_multiples"] == ["magneticLayerGroups"]
    assert s["probability_of_at_least_one"] == "27613783/113379904"
    assert s["probability_of_at_least_one_six_decimals"] == "0.243551"
    assert s["expected_number_of_exact_multiples"] == "3/11"
    assert s["expected_count_is_below_one"] is True
    assert s["moduli_count"] == 15
    assert "22" in s["moduli_dividing_at_least_one_count"]


def test_the_gain_column_and_the_spread_column_order_the_rows_differently():
    s = section("S5_gain_and_spread")
    shares = {k: v["top3_share"] for k, v in s["classes"].items()}
    assert shares == {"position": "1117/1119", "ganzhi": "1523/3957", "naming": "123/400",
                      "bracket": "190/213", "grade": "452/1939"}
    for k, v in s["classes"].items():
        assert v["top3_share"] != v["reported"]  # exact fractions, not the rounded report
    assert s["order_by_gain"] == ["bracket", "naming", "ganzhi", "grade", "position"]
    assert s["order_by_spread"] == ["grade", "naming", "ganzhi", "bracket", "position"]
    assert s["rank_correlation_gain_versus_spread"] == "-1/10"
    assert s["rank_correlation_magnitude"] == "1/10"
    assert s["largest_gain_row"] == "bracket" and s["smallest_gain_row"] == "position"
    assert s["largest_gain_is_less_concentrated_than_the_smallest"] is True


def test_gain_does_not_determine_spread():
    s = section("S5_gain_and_spread")
    ranges = s["achievable_share_ranges_for_a_fixed_gain"]
    assert ranges["12_over_6"] == {"min": "1/2", "max": "1", "distinct": 7}
    assert ranges["24_over_4"] == {"min": "3/4", "max": "1", "distinct": 7}
    assert s["exhausted_compositions"] == 9113


def test_the_published_top_three_bounds_rather_than_determines_the_spread():
    s = section("S5_gain_and_spread")
    from fractions import Fraction as F

    bounds = s["effective_works_bounds"]
    assert bounds["position"]["effective_works_low"] == "139129/67567"
    assert bounds["position"]["effective_works_high"] == "1252161/608101"
    # the narrowest class is pinned to within a percent, the widest is not pinned at all
    narrow = F(bounds["position"]["effective_works_high"]) / F(bounds["position"]["effective_works_low"])
    assert narrow < F(1001, 1000)
    assert s["widest_effective_works_ratio_class"] == "grade"
    widest = bounds["grade"]
    assert widest["effective_works_low"] == "3759721/2280419"
    assert widest["effective_works_high"] == "327095727/8235919"
    assert F(widest["effective_works_high"]) / F(widest["effective_works_low"]) > 24


def test_the_spread_baseline_is_the_corpus_itself():
    s = section("S5_gain_and_spread")
    assert s["corpus_sizes"] == [4000, 3000, 2000, 500, 500]
    assert s["corpus_baseline_share"] == "9/10"
    assert s["corpus_baseline_is_not_the_uniform_value"] is True


def test_a_gate_can_pass_while_its_named_content_is_absent():
    s = section("S6_threshold_versus_content")
    assert s["non_speech_numerator"] == 16 and s["unread"] == 190
    assert s["non_speech_share"] == "8/95"
    assert s["non_speech_share_four_decimals_exact"] == "0.0842"
    assert s["gate"] == "1/20" and s["gate_passes"] is True
    assert s["largest_numerator_still_below_the_gate"] == 9
    assert s["components_exactly_zero"] == ["自始", "凡皆"]
    assert s["component_vectors_with_the_same_aggregate"] == 969
    assert s["vectors_putting_everything_on_one_component"] == 1
    assert s["the_aggregate_does_not_determine_the_components"] is True
    assert sum(s["classification"].values()) == 190
    assert s["dominant_cause_share"] == "169/190"


def test_the_contract_states_its_protected_boundaries():
    contract = load(CONTRACT)
    protected = " ".join(contract["protected"])
    for phrase in (
        "or corpus count is imported",
        "most favourable to the claim",
        "says anything about serial numbers",
        "No floating-point value",
        "No native Rust witness",
    ):
        assert phrase in protected, phrase
    assert contract["input_document"] == (
        "docs/research/0213-gain-coverage-and-the-number-that-was-already-fixed.md"
    )
    assert contract["level"].startswith("External exact")
    assert NOTE.is_file()


def test_the_note_states_the_residual_and_imports_no_text():
    text = NOTE.read_text(encoding="utf-8")
    assert "Residual" in text
    flat = " ".join(text.split()).lower()
    for phrase in ("no text and no corpus count is imported",
                   "wenyan-relation-learning",
                   "the thresholds are computed for the two declared tolerances only"):
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
    assert any("covering radius" in item for item in claim["forbidden_conflations"])
    for symbol in claim["code_symbol"].split("; "):
        assert (ROOT / symbol).is_file(), symbol
    assert claim["counterexample_boundary"].startswith("No text")
