"""Bounded magic hypercube calibration; external evidence, no admission.

The assertions here are about what the retained checker decided by exhaustion.
They are not claims about any text, and they promote no native identity.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/magic_hypercube"
CHECKER = HERE / "checker.py"
CONTRACT = HERE / "contract.json"
EVIDENCE = HERE / "evidence.json"
NOTE = ROOT / "docs/research/0216-the-magic-hypercube-and-a-cut-the-address-cannot-see.md"
CLAIM_ID = "adva.bounded-experiment.magic-hypercube.v0"
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


def test_the_declared_construction_is_a_permutation_with_constant_lines():
    s = section("S1_hypercube")
    assert s["places"] == 4 and s["order"] == 3 and s["cells"] == 81
    assert s["every_entry_nonzero"] is True
    assert s["determinant_modulo_three"] == 2
    assert s["is_a_permutation_of_one_to_eighty_one"] is True
    assert s["coordinate_lines"] == 108 and s["lines_per_place"] == 27
    assert s["line_sum"] == 123
    assert s["line_sum_is_the_hypercube_magic_constant"] is True


def test_the_condition_is_sufficient_and_necessary_on_the_declared_families():
    s = section("S1_hypercube")
    assert s["zero_free_matrices_exhausted"] == 65536
    assert s["zero_free_matrices_with_constant_lines"] == 65536
    assert s["necessity_family_exhausted"] == 22440
    assert s["necessity_family_members_with_constant_lines"] == 0
    assert s["condition"] == "constant coordinate lines hold exactly when every entry is nonzero"


def test_there_are_many_magic_hypercubes_not_one():
    s = section("S1_hypercube")
    assert s["invertible_zero_free_matrices"] == 22272
    assert s["distinct_magic_hypercubes"] == 22272
    assert s["invertible_zero_free_matrices"] < s["zero_free_matrices_exhausted"]


def test_the_main_diagonals_are_not_coordinate_lines():
    s = section("S2_diagonals")
    assert s["diagonal_directions"] == 8
    assert s["diagonal_sums"] == [6, 12, 30, 84, 123]
    assert s["diagonal_directions_reaching_the_line_sum"] == 4
    assert s["diagonals_are_constant"] is False
    assert s["the_declared_construction_is_magic_along_coordinate_lines_only"] is True


def test_the_matrix_gives_the_coordinate_lines_and_the_shift_the_diagonals():
    s = section("S2_diagonals")
    assert s["two_place_coordinate_lines"] == 6
    assert s["two_place_rows_and_columns"] == [[15, 15, 15], [15, 15, 15]]
    assert s["two_place_diagonals"] == [6, 18]
    assert s["shifted_two_place_square"] == [[8, 1, 6], [3, 5, 7], [4, 9, 2]]
    assert s["shifted_two_place_diagonals"] == [15, 15]
    assert s["the_matrix_gives_the_coordinate_lines_and_the_shift_buys_the_diagonals"] is True


def test_no_proper_subset_of_the_places_sees_the_cut():
    s = section("S3_cut")
    assert s["heads"] == 81 and s["cut"] == 47 and s["sides"] == [47, 34]
    assert s["head_before_the_cut"] == [2, 3, 1, 2]
    assert s["head_after_the_cut"] == [2, 3, 1, 3]
    assert s["places_differing"] == [3]
    assert s["subsets_exhausted"] == 15
    assert s["subsets_separating_the_cut"] == [[0, 1, 2, 3]]
    assert s["proper_subsets_separating_the_cut"] == 0
    assert s["cut_lies_inside_the_second_place_range"] is True
    assert s["the_cut_is_invisible_to_any_proper_subset_of_the_places"] is True


def test_the_proxy_chain_and_its_one_checked_statistic():
    s = section("S4_proxy_chain")
    assert s["readings_recorded"] == 4
    assert s["refuted"] == 2 and s["demoted_to_proxy"] == 1 and s["exact"] == 1
    assert s["three_head_selections"] == 85320
    assert s["selections_with_at_least_fourteen"] == 4735
    assert s["exact_share"] == "947/17064"
    assert s["exact_share_approx"] == "0.055497"
    assert s["reported_p_value"] == "0.0555"
    assert s["above_the_declared_threshold"] is True
    assert s["readings"]["v4_position"]["status"].startswith("exact")


def test_the_contract_states_its_protected_boundaries():
    contract = load(CONTRACT)
    protected = " ".join(contract["protected"])
    for phrase in (
        "no corpus count from any external repository is imported",
        "the whole content of the diagonal section is that they are not the only lines one could declare",
        "a statement about definability, not about why the cut is where it is",
        "No floating-point value",
        "No native Rust witness",
    ):
        assert phrase in protected, phrase
    assert contract["input_document"] == (
        "docs/research/0216-the-magic-hypercube-and-a-cut-the-address-cannot-see.md"
    )
    assert contract["level"].startswith("External exact")
    assert NOTE.is_file()


def test_the_note_states_the_residual_and_imports_no_text():
    text = NOTE.read_text(encoding="utf-8")
    assert "Residual" in text
    flat = " ".join(text.split()).lower()
    for phrase in ("no text and no corpus count is imported",
                   "wenyan-relation-learning",
                   "the cut is described, not explained"):
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
    assert any("coordinate line" in item for item in claim["forbidden_conflations"])
    for symbol in claim["code_symbol"].split("; "):
        assert (ROOT / symbol).is_file(), symbol
    assert claim["counterexample_boundary"].startswith("No text")
