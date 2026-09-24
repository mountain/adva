"""Bounded declared-invariance calibration; external evidence, no admission.

The assertions here are about what the retained checker decided by exhaustion.
They are not claims about any text or corpus, and they promote no native identity.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/declared_invariance"
CHECKER = HERE / "checker.py"
CONTRACT = HERE / "contract.json"
EVIDENCE = HERE / "evidence.json"
NOTE = ROOT / "docs/research/0212-what-a-declared-invariance-already-fixes.md"
CLAIM_ID = "adva.bounded-experiment.declared-invariance.v0"
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


def test_the_axis_swaps_are_the_three_opposite_edge_pairs():
    s = section("S1_two_symmetry_sets")
    assert s["vertices"] == 4 and s["edges"] == 6 and s["perfect_matchings"] == 3
    assert s["axis_swaps"] == 3
    assert s["axis_swaps_commute_pairwise"] is True
    assert s["klein_group_order"] == 4
    assert s["klein_orbits_on_edges"] == [[[0, 1], [2, 3]], [[0, 2], [1, 3]], [[0, 3], [1, 2]]]
    assert s["klein_orbit_sizes"] == [2, 2, 2]
    # the edge action is not free: each swap fixes the two edges of its own matching
    assert s["klein_edge_action_is_free"] is False
    assert s["klein_edge_stabiliser_size"] == 2


def test_the_four_face_mirrors_generate_an_infinite_closure():
    s = section("S1_two_symmetry_sets")
    assert s["face_mirrors"] == 4
    assert s["face_mirror_coxeter_relations_hold"] is True
    assert s["faces_of_the_fundamental_alcove"] == 4
    assert s["closure_is_infinite"] is True
    assert s["elements_found"] == 5781
    assert s["elements_found_through_length"] == 20
    assert s["alcove_count_shells"][:5] == [1, 4, 10, 20, 34]
    # the exact polynomial counts, not only their growth order
    assert s["shell_count_closed_form"] == "2 n^2 + 2 for n >= 1"
    assert s["alcove_count_closed_form"] == "1 + 2 n + n (n + 1) (2 n + 1) / 3"
    assert s["alcove_count_is_cubic"] is True
    assert s["fourth_difference_of_the_cumulative_count"] == 0
    assert s["second_difference_of_the_shell_count"] == 4


def test_the_finite_group_is_exactly_the_origin_stabiliser():
    s = section("S1_two_symmetry_sets")
    assert s["origin_stabiliser_order"] == 24
    assert s["origin_stabiliser_length_profile"] == [1, 3, 5, 6, 5, 3, 1]
    assert s["finite_part_is_exactly_the_origin_stabiliser"] is True
    # the order-four group sits inside the finite part but does not generate the closure
    assert s["klein_is_a_subgroup_of_the_finite_part"] is True
    assert s["klein_generates_the_closure"] is False


def test_a_rank_one_matrix_has_one_argmax_column_for_every_row():
    s = section("S2_rank_one_collapse")
    assert s["declared_matrix_is_rank_one"] is True
    assert s["distinct_row_argmax_columns"] == 1
    assert s["the_one_argmax_column"] == 4
    assert s["rank_one_sweep_matrices_checked"] == 1701
    assert s["rank_one_row_specific_information"] == 0


def test_the_rank_one_diagonal_share_exceeds_chance_with_no_information():
    s = section("S2_rank_one_collapse")
    assert s["rank_one_diagonal_share"] == "11/45"
    assert s["chance_share"] == "1/5"
    assert s["rank_one_excess_over_chance"] == "2/45"


def test_the_optimal_assignment_does_not_repair_the_reading():
    s = section("S2_rank_one_collapse")
    assert s["assignment_optimum_is_margin_determined"] is True
    assert s["sorted_weights_make_the_identity_the_unique_optimum"] is True
    # a non-monotone pair, so the claim is not an accident of sorted weights
    assert s["unsorted_weights_do_not_make_the_identity_an_optimum"] is True
    assert s["assignment_reading_threshold_on_the_grid"] == "0"
    assert s["row_reading_threshold_on_the_grid"] == "5"
    assert s["the_two_readings_disagree"] is True
    assert s["per_row_threshold_closed_form"] == ["4", "3/2", "2/3", "1/4", "-1/5"]
    readings = {r["t"]: r for r in s["grid_readings"]}
    assert readings["0"]["identity_is_the_unique_assignment_optimum"] is True
    assert readings["0"]["every_row_uniquely_recovers_its_column"] is False
    # perturbation four succeeds only through a tie in the first row
    assert readings["4"]["every_row_argmax_contains_its_column"] is True
    assert readings["4"]["every_row_uniquely_recovers_its_column"] is False
    assert readings["4"]["rows_tied_with_an_earlier_column"] == [0]
    assert readings["5"]["every_row_uniquely_recovers_its_column"] is True


def test_the_permutation_null_cannot_tell_two_networks_apart_by_their_margins():
    s = section("S3_exact_null")
    same = s["same_margins_different_observed"]
    assert same["observed_reciprocity"] == [6, 0]
    assert same["exact_null_law_identical"] is True
    assert same["support"] == [0, 6]
    assert same["exact_null_mean"] == "14/5"
    assert same["exact_null_mean_as_a_share_of_six_edges"] == "7/15"
    # a perfectly reciprocal network is not significant under its own null
    assert same["null_mass_at_a_fully_reciprocal_network"] == "4/45"
    assert same["one_sided_p_value_for_the_fully_reciprocal_network"] == "4/45"
    assert s["null_law_depends_only_on_the_two_margins"] is True
    assert s["families"] == 5 and s["distinct_marginal_pairs"] < s["families"]


def test_the_exact_null_is_enumerated_and_not_sampled():
    s = section("S3_exact_null")
    assert s["permutation_counts"] == {"4": 24, "5": 120, "6": 720}
    assert s["exhausted_permutations_total"] == 1608
    assert s["chain"] == {"observed": 0, "mean": "1", "variance": "2", "support_min": 0,
                          "support_max": 4, "mass_strictly_below_observed": "0",
                          "permutations": 120}
    assert s["four_edge_law"]["mean"] == "7/6"
    assert s["four_edge_law"]["mass_strictly_below_observed"] == "5/6"


def test_the_guessed_closed_form_for_the_null_mean_is_recorded_as_refuted():
    s = section("S3_exact_null")
    assert s["squared_overlap_guess_is_the_exact_mean"] is False
    ratios = [row["ratio"] for row in s["squared_overlap_guess"]]
    assert ratios and all(r != "1" for r in ratios)
    assert "21/5" in ratios


def test_the_contract_states_its_protected_boundaries():
    contract = load(CONTRACT)
    protected = " ".join(contract["protected"])
    for phrase in (
        "no corpus count",
        "declared synthetic objects",
        "are the symmetry of any text",
        "No floating-point value",
        "No native Rust witness",
    ):
        assert phrase in protected, phrase
    assert contract["input_document"] == (
        "docs/research/0212-what-a-declared-invariance-already-fixes.md"
    )
    assert contract["level"].startswith("External exact")
    assert NOTE.is_file()


def test_the_note_states_the_residual_and_imports_no_text():
    text = NOTE.read_text(encoding="utf-8")
    assert "Residual" in text
    flat = " ".join(text.split()).lower()
    for phrase in ("no text and no corpus count is imported",
                   "attributed and not re-run",
                   "wenyan-relation-learning",
                   "no closed form for the exact null mean is established"):
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
    assert any("optimal assignment" in item for item in claim["forbidden_conflations"])
    for symbol in claim["code_symbol"].split("; "):
        assert (ROOT / symbol).is_file(), symbol
    assert claim["counterexample_boundary"].startswith("No text")
