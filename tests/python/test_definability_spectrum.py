"""The definability spectrum of the address algebra; external evidence only.

The assertions here are about what the retained checker decided by exhaustion
and by exact binomial counting. They price definability inside a declared
algebra. They are not claims about any text.
"""

import hashlib
import json
import subprocess
import sys
from fractions import Fraction as F
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/definability_spectrum"
CHECKER = HERE / "checker.py"
CONTRACT = HERE / "contract.json"
EVIDENCE = HERE / "evidence.json"
NOTE = ROOT / "docs/research/0219-the-definability-spectrum-of-the-address-algebra.md"
CLAIM_ID = "adva.bounded-experiment.definability-spectrum.v0"
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


def test_the_algebra_at_each_level_has_two_to_the_three_to_the_k_sets():
    s = section("S1_spectrum")
    assert s["heads"] == 81 and s["places"] == 4
    assert s["exhausted_up_to_level"] == 2 and s["levels_beyond_exhaustion"] == 2
    levels = s["per_level"]
    assert sorted(levels) == ["0", "1", "2", "3", "4"]
    for k in range(5):
        row = levels[str(k)]
        assert row["subsets"] == comb(4, k)
        assert row["blocks_per_partition"] == 3 ** k
        assert row["block_size"] == 3 ** (4 - k)
        assert row["blocks_per_partition"] * row["block_size"] == 81
        # a partition into m blocks of equal size generates two to the m sets
        assert row["sets_per_algebra"] == 2 ** (3 ** k)
    assert levels["0"]["sets_per_algebra"] == 2
    assert levels["1"]["sets_per_algebra"] == 8
    assert levels["2"]["sets_per_algebra"] == 512
    assert levels["3"]["sets_per_algebra"] == 134217728
    assert levels["4"]["sets_per_algebra"] == 2 ** 81 == 2417851639229258349412352
    assert s["power_set_size"] == 2 ** 81


def test_the_union_up_to_two_places_is_enumerated_and_is_smaller_than_the_sum():
    s = section("S1_spectrum")
    assert s["cumulative_sets_by_level"] == {"0": 2, "1": 26, "2": 3014}
    assert s["beyond_exhaustion_are_counted_not_enumerated"] is True
    # two plus four algebras of eight plus six of five hundred twelve
    assert 2 + 4 * 8 + 6 * 512 == 3106 > 3014
    assert 2 + 4 * 8 == 34 > 26
    # the whole spectrum is tiny against the power set it lives in
    assert 3014 < 2 ** 81


def test_every_defined_set_at_two_places_has_size_a_multiple_of_nine():
    s = section("S1_spectrum")
    distribution = s["size_distribution_up_to_two_places"]
    assert s["all_defined_sizes_are_multiples_of_nine"] is True
    assert all(int(size) % 9 == 0 for size in distribution)
    assert sum(distribution.values()) == 3014
    assert distribution["9"] == 54
    assert distribution["81"] == 1 and distribution["0"] == 1
    # six two-place partitions, each with nine blocks, one block per choice
    assert 6 * 9 == 54
    assert distribution["18"] == 216 and distribution["27"] == 480


def test_the_algebras_are_nested_and_adding_a_place_enlarges_strictly():
    s = section("S2_lattice")
    assert s["nested_pairs_checked"] == 33
    assert s["monotone"] is True
    assert s["adding_a_place_strictly_enlarges"] is True
    assert s["empty_place_set_gives_two_sets"] is True
    assert s["different_single_places_give_different_algebras"] is True
    assert s["two_single_places_share_only_the_two_trivial_sets"] is True
    assert s["membership_is_tested_directly_not_by_enumeration"] is True
    assert s["exhausted_levels"] == 2


def test_the_prior_is_an_exact_ratio_of_two_finite_counts():
    s = section("S3_prior")
    assert s["the_prior_is_about_the_algebra_not_the_text"] is True
    assert s["a_prior_of_one_means_no_constraint"] is True
    assert s["exhausted_up_to_level"] == 2
    rows = s["rows"]
    assert set(rows) == {
        "all_heads",
        "first_quarter",
        "nine_district_representatives",
        "three_quarter_representatives",
        "cut_before",
        "cut_after",
        "two_prison_heads",
        "orbit_of_seven",
    }
    for name, row in rows.items():
        prior = F(row["prior"])
        assert prior == F(row["definable_of_that_size_at_that_level"],
                          row["all_sets_of_that_size"]), name
        assert 0 < prior <= 1, name
        # the divisibility theorem holds of every declared division
        assert row["size"] % 3 ** (4 - row["mu"]) == 0, name
        # a set needing all four places is not constrained at all
        if row["mu"] == 4:
            assert prior == 1, name
    assert rows["all_heads"]["mu"] == 0 and rows["all_heads"]["size"] == 81
    assert rows["first_quarter"]["mu"] == 1 and rows["first_quarter"]["size"] == 27
    # twelve, not the four hundred eighty that the two-place union would give:
    # a one-place division into three blocks of twenty seven has three of them
    # and there are four places, and no two of those twelve blocks coincide
    assert rows["first_quarter"]["definable_of_that_size_at_that_level"] == 12 == 4 * 3
    assert s["the_quarter_count_moved_from_480_to_12_when_the_level_was_restricted"] is True
    # the most constrained entry in the table is the coarsest division, not the nine
    assert F(rows["first_quarter"]["prior"]) < F(rows["nine_district_representatives"]["prior"])
    nine = rows["nine_district_representatives"]
    assert nine["mu"] == 2 and nine["size"] == 9
    assert nine["definable_of_that_size_at_that_level"] == 54
    assert F(nine["prior"]) == F(54, 260887834350) < F(1, 10 ** 9)
    three = rows["three_quarter_representatives"]
    assert three["mu"] == 3 and three["size"] == 3
    assert three["definable_of_that_size_at_that_level"] == 108
    assert F(three["prior"]) == F(108, 85320) == F(1, 790) > F(1, 1000)
    # the set of size three that needs four places is the honest exception:
    # the bound is necessary and not sufficient
    assert rows["orbit_of_seven"]["mu"] == 4 and rows["orbit_of_seven"]["size"] == 3


def test_the_declared_divisions_sit_on_declared_levels():
    s = section("S4_placement")
    assert len(s["pairs_of_places"]) == 6
    assert s["block_sizes_across_all_levels"] == [1, 3, 9, 27, 81]
    assert s["the_nine_are_a_block_of"] == [[2, 3]]
    assert s["the_three_are_a_block_of"] == [[1, 2, 3]]
    assert s["the_quarter_is_a_block_of"] == [[0]]
    assert s["the_nine_are_the_block_containing_the_first_head"] is True
    # of the six two-place partitions exactly one has a declared block
    found = s["declared_sets_found_among_two_place_blocks"]
    assert found == {"(0, 1)": 0, "(0, 2)": 0, "(0, 3)": 0,
                     "(1, 2)": 0, "(1, 3)": 0, "(2, 3)": 1}
    # the organisation is by the last places, and it is recorded, not explained
    assert s["named_divisions_by_level"] == {
        "single_places": 1,
        "the_nine_district_representatives": 2,
        "the_three_quarter_representatives": 3,
        "the_cut_sides": 4,
    }
    assert s["the_cut_sides_are_unions_of_blocks_and_not_blocks"] is True
    assert s["the_cut_is_the_only_named_division_needing_all_four_places"] is True


def test_the_nine_meet_fifty_four_rivals_and_the_price_is_reported_as_a_ratio():
    s = section("S5_rivals")
    assert s["rivals_of_size_nine"] == 54
    assert s["all_sets_of_size_nine"] == 260887834350
    assert s["rivals_containing_the_first_head"] == 6
    assert s["each_rival_belongs_to_exactly_one_partition"] is True
    assert s["the_nine_are_among_the_origin_blocks"] is True
    # the reported reciprocal is the floor of the exact one, so it understates
    # the price denominator and slightly overstates the probability
    assert s["the_rivals_are_one_in"] == 260887834350 // 54 == 4831256191
    assert 260887834350 % 54 == 36
    assert F(1, s["the_rivals_are_one_in"]) > F(54, 260887834350)
    # six partitions, and one of them holds the block containing the first head
    assert s["rivals_containing_the_first_head"] * 9 == 54


def test_the_contract_states_its_protected_boundaries():
    contract = load(CONTRACT)
    protected = " ".join(contract["protected"])
    for phrase in (
        "No classical text, edition, transcription, commentary, name table",
        "not a p-value for any text",
        "No statistical claim of any kind",
        "the overlaps between subsets at those levels are not subtracted",
        "No floating-point value",
        "No native Rust witness",
    ):
        assert phrase in protected, phrase
    assert contract["input_document"] == (
        "docs/research/0219-the-definability-spectrum-of-the-address-algebra.md"
    )
    assert contract["level"].startswith("External exact")
    assert contract["objects"]["expected_cumulative"] == {"0": 2, "1": 26, "2": 3014}
    assert contract["objects"]["expected_nine_element_sets_at_two_places"] == 54
    assert contract["objects"]["expected_three_element_sets_at_three_places"] == 108
    assert NOTE.is_file()


def test_the_note_states_the_residual_and_imports_no_text():
    text = NOTE.read_text(encoding="utf-8")
    assert "Residual" in text
    flat = " ".join(text.split()).lower()
    for phrase in ("no text and no corpus count is imported",
                   "not a p-value for any text",
                   "recorded and not explained",
                   "the overlaps are not subtracted"):
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
    assert any("price" in item for item in claim["forbidden_conflations"])
    for symbol in claim["code_symbol"].split("; "):
        assert (ROOT / symbol).is_file(), symbol
    assert claim["counterexample_boundary"].startswith("No classical text")
