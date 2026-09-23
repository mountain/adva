"""Bounded eighty-one magic square calibration; external evidence, no admission.

The assertions here are about what the retained checker decided by exhaustion.
They are not claims about any text, and they promote no native identity.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/eighty_one_magic_square"
CHECKER = HERE / "checker.py"
CONTRACT = HERE / "contract.json"
EVIDENCE = HERE / "evidence.json"
NOTE = ROOT / "docs/research/0215-the-magic-square-exists-and-the-address-is-not-it.md"
CLAIM_ID = "adva.bounded-experiment.eighty-one-magic-square.v0"
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


def invoke(checker, output, timeout=1200):
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


def test_the_address_forces_a_grid_and_the_grid_is_not_magic():
    s = section("S1_canonical_grid")
    assert s["heads"] == 81
    assert s["entry_at_row_column"] == "9 r + c + 1"
    assert s["magic_constant"] == 369
    assert s["canonical_grid_is_magic"] is False
    assert s["row_sums"] == [81 * r + 45 for r in range(9)]
    assert s["column_sums"] == [9 * c + 333 for c in range(9)]
    assert s["row_sums"][0] == 45 and s["row_sums"][8] == 693
    assert s["column_sums"][0] == 333 and s["column_sums"][8] == 405


def test_four_of_the_twenty_lines_already_reach_the_magic_constant():
    s = section("S1_canonical_grid")
    assert s["lines_attaining_the_magic_constant"] == 4
    assert s["lines_in_total"] == 20
    assert s["diagonal_sums"] == [369, 369]
    assert s["middle_row_sum"] == 369 and s["middle_column_sum"] == 369
    assert s["main_diagonal"] == [10 * i + 1 for i in range(9)]
    assert s["other_diagonal"] == [8 * i + 9 for i in range(9)]


def test_the_affine_family_and_the_derived_magic_constant():
    s = section("S2_linear_family")
    assert s["entries_are_a_permutation_iff_the_matrix_is_invertible"] is True
    assert s["row_sum_closed_form"] == "n n (n-1) / 2 + n (n-1) / 2 + n"
    assert s["row_sum_equals_the_magic_constant"] is True
    assert s["magic_constants"] == {"3": 15, "5": 65, "9": 369}
    assert s["unit_row_coefficient_cases_checked"] == 6864


def test_the_affine_magic_squares_are_counted():
    s = section("S3_magic_counts")
    assert s["linear_magic_squares_by_order"] == {"3": 8, "5": 1472, "9": 3528}
    assert s["coefficient_matrices_admitting_a_magic_square"] == {"3": 8, "5": 192, "9": 648}
    # order three validates the family against the classical count of all 3x3 magic squares
    assert s["order_three_matches_the_classical_count"] is True
    # the family is odd-order only, which is where this repo's own order-four line sits outside it
    assert s["even_orders_checked"] == [4, 6, 8]
    assert s["affine_magic_squares_at_even_orders"] == {"4": 0, "6": 0, "8": 0}
    assert s["the_family_is_odd_order_only"] is True


def test_the_invertibility_mistake_is_retained_as_evidence():
    s = section("S3_magic_counts")
    assert s["linear_magic_squares_by_the_weaker_determinant_test"] == {"3": 8, "5": 1472, "9": 6024}
    assert s["the_two_invertibility_tests_agree_at_prime_orders"] is True
    assert s["the_weaker_test_over_counts_at_order_nine_by"] == 2496


def test_the_standard_construction_shares_one_matrix_across_the_orders():
    s = section("S3_magic_counts")
    assert s["declared_construction_is_magic_and_permuting"] is True
    assert s["declared_construction_is_affine"] is True
    params = s["declared_construction_parameters"]
    assert {k: (v["alpha"], v["beta"], v["gamma"], v["delta"]) for k, v in params.items()} == {
        "3": (1, 1, 1, 2), "5": (1, 1, 1, 2), "9": (1, 1, 1, 2)}
    assert {k: v["centre"] for k, v in params.items()} == {"3": 5, "5": 13, "9": 41}
    assert {k: (v["e"], v["f"]) for k, v in params.items()} == {"3": (2, 1), "5": (3, 1), "9": (5, 1)}
    assert s["one_coefficient_matrix_for_every_odd_order"] is True
    assert s["shifts_differ_between_the_orders"] is True


def test_preserving_none_of_thirty_five_pairs_is_ordinary():
    s = section("S4_relation_preservation")
    assert s["unordered_pairs"] == 3240
    assert s["expected_preserved_pairs"] == "245/648"
    assert s["markov_bound_on_preserving_none"] == "403/648"
    assert s["markov_bound_approx"] == "0.6219"
    assert s["independent_pair_estimate_approx"] == "0.6838"
    assert s["observed_preserved_pairs"] == 0
    assert s["preservation_of_none_is_not_evidence_of_antagonism"] is True


def test_the_alignment_statistic_separates_aligned_from_mixed():
    s = section("S5_class_alignment")
    assert s["first_pair_labelling_incidences"] == {"rows": 9, "columns": 81}
    assert s["second_pair_labelling_incidences"] == {"rows": 81, "columns": 9}
    assert s["block_labelling_incidences"] == {"rows": 27, "columns": 27}
    assert s["aligned_total_incidence"] == 90
    assert s["block_total_incidence"] == 54
    assert s["maximum_total_incidence"] == 162
    assert s["the_canonical_grid_aligns_both_coarsenings"] is True


def test_a_manifest_cannot_show_its_own_loss():
    s = section("S6_index_derived_count")
    assert s["snapshot"] == 136 and s["later_inserts"] == 2 and s["corpus_works"] == 138
    assert s["works_lost_from_the_manifest"] == [136, 137]
    assert s["lost_share"] == "1/69"
    assert s["the_manifest_is_internally_consistent"] is True
    assert s["no_statistic_from_the_manifest_can_detect_the_loss"] is True
    assert s["largest_work_share_of_characters"] == "872624/7386225"
    assert s["largest_work_readable_share"] == "3654/26533"


def test_the_contract_states_its_protected_boundaries():
    contract = load(CONTRACT)
    protected = " ".join(contract["protected"])
    for phrase in (
        "no corpus count from any external repository is imported",
        "no claim that a magic square is or is not part of any tradition",
        "does not establish that the permutation is what the external record says it is",
        "No floating-point value",
        "No native Rust witness",
    ):
        assert phrase in protected, phrase
    assert contract["input_document"] == (
        "docs/research/0215-the-magic-square-exists-and-the-address-is-not-it.md"
    )
    assert contract["level"].startswith("External exact")
    assert NOTE.is_file()


def test_the_note_states_the_residual_and_imports_no_text():
    text = NOTE.read_text(encoding="utf-8")
    assert "Residual" in text
    flat = " ".join(text.split()).lower()
    for phrase in ("no text and no corpus count is imported",
                   "wenyan-relation-learning",
                   "the affine family is not claimed to exhaust"):
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
    assert any("magic square" in item for item in claim["forbidden_conflations"])
    for symbol in claim["code_symbol"].split("; "):
        assert (ROOT / symbol).is_file(), symbol
    assert claim["counterexample_boundary"].startswith("No text")
