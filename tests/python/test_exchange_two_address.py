"""The paired test for the two-address exchange calibration; external evidence only.

The assertions here are about what the retained checker decided by exact arithmetic on one
declared twelve-phase fixture and one declared paired carrier.  They are not claims about any
physical object, they promote no native identity, and they confirm no exchange: the retained
evidence records that the two readings differ in their real-branch count and that whether the
declared time conditions change what is reachable is NotDecided.

The checker is invoked without `-S` because its declared external library (sympy) must be
importable; the run remains an external exact calibration either way.

The record carries no claim for this run: the parent session adds the claim to
`docs/claims.toml` with its note, so the last test asserts the claim is absent rather than
dropping the binding.
"""

import hashlib
import json
import math
import subprocess
import sys
import tomllib
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/two_address_exchange_v1"
CHECKER = HERE / "calibration.py"
CONTRACT = HERE / "contract.json"
EVIDENCE = HERE / "evidence.json"
CLAIM_ID = "adva.bounded-experiment.two-address-exchange.v0"
DECLARED_CONTRACT_SHA256 = \
    "fbaeffb2dc53d4ca7dcc875fa1ebdec8cf6220bde8b15fcc3f45a358c8d7e13e"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    """Load JSON and refuse any floating-point literal in it."""
    def no_float(text):
        raise AssertionError(f"a floating-point literal is present: {text}")

    return json.loads(Path(path).read_text(encoding="utf-8"), parse_float=no_float)


def invoke(checker, output, timeout=900):
    return subprocess.run(
        [sys.executable, str(checker), "--output", str(output)],
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
    assert report["contract_sha256"] == digest(CONTRACT) == DECLARED_CONTRACT_SHA256
    assert report["contract_sha256_declared"] == DECLARED_CONTRACT_SHA256
    assert report["assertions"] <= contract["budgets"]["max_assertions"]
    assert report["limits"] == contract["budgets"]
    assert all(report["checks"].values())
    assert contract["budgets"]["child_processes"] == 0


def test_fresh_run_reproduces_the_retained_mathematical_payload(tmp_path):
    output = tmp_path / "fresh.json"
    completed = invoke(CHECKER, output)
    assert completed.returncode == 0, completed.stderr
    fresh = load(output)
    retained = load(EVIDENCE)
    assert fresh["status"] == retained["status"]
    assert fresh["assertions"] == retained["assertions"]
    assert fresh["sections"] == retained["sections"]
    assert fresh["tooling"] == retained["tooling"]
    assert fresh["undecided"] == retained["undecided"]
    assert fresh["checks"] == retained["checks"]
    assert digest(output) == digest(EVIDENCE)


def test_two_fresh_runs_are_byte_identical(tmp_path):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    assert invoke(CHECKER, first).returncode == 0
    assert invoke(CHECKER, second).returncode == 0
    assert digest(first) == digest(second) == digest(EVIDENCE)


def test_an_existing_output_is_never_overwritten(tmp_path):
    output = tmp_path / "keep.json"
    output.write_text("retained", encoding="utf-8")
    completed = invoke(CHECKER, output)
    assert completed.returncode != 0
    assert output.read_text(encoding="utf-8") == "retained"


def test_the_two_addresses_are_a_bijection_and_each_alone_is_not():
    addresses = section("S1_two_addresses")
    carrier = addresses["carrier"]
    assert carrier["first_address_points"] == 81
    assert carrier["paired_points"] == 6561
    assert carrier["fine_points"] == 6561
    assert carrier["points_in_each_fixed_a_fibre"] == 81
    assert carrier["points_in_each_fixed_b_fibre"] == 81
    assert carrier["bijection_exhausted"] is True
    assert carrier["pair_recovers_the_fine_point"] is True
    assert carrier["neither_address_alone_recovers_the_fine_point"] is True
    assert addresses["map"] == ("e(a, b)_i = 3 a_i + b_i from {0,1,2}^4 x {0,1,2}^4 onto "
                                "{0,...,8}^4")
    assert addresses["componentwise_inverse_pair"] == {"first": "a = floor(z/3)",
                                                       "second": "b = z mod 3"}
    readings = addresses["declared_readings"]
    assert [row["reading"] for row in readings] == ["nested spatial: coarse cell / child",
                                                    "ordered state: source / target"]
    for row in readings:
        assert tuple(3 * row["a"][i] + row["b"][i] for i in range(4)) == tuple(row["z"])
    qiong = addresses["declared_qiong_fibre"]
    assert qiong["a"] == [2, 1, 1, 2]
    assert qiong["fine_points"] == 81
    assert qiong["arithmetic_ordinal"] == 69
    assert qiong["set"] == "{6,7,8} x {3,4,5} x {3,4,5} x {6,7,8}"


def test_the_two_observations_the_diagonal_and_the_two_bases():
    observations = section("S2_observations_and_spectra")
    measured = observations["observations"]
    assert measured["q_block"] == "q_block(z) = floor(z/3), componentwise"
    assert measured["q_phase"] == "q_phase(z) = z mod 3, componentwise"
    assert measured["each_is_81_valued"] is True
    assert measured["exhausted_point_generator_pairs"] == 26244
    assert measured["q_phase_law_holds_on"] == 26244
    assert measured["q_block_law_holds_on"] == 26244
    assert observations["mutual_measuring"]["returns_the_fine_point"] is True

    diagonal = observations["diagonal_a_equals_b"]
    assert diagonal["size"] == 81
    assert diagonal["largest_coordinate_amplitude"] == "8"
    assert diagonal["locus"] == "z = 4 a, every coordinate of z in {0,4,8}"
    assert diagonal["conditions_agreeing_here"] == ["a = b", "q_block(z) = q_phase(z)"]
    assert diagonal["not_closed_under_the_declared_translations"] is True
    assert len(diagonal["points"]) == 81
    for row in diagonal["points"]:
        assert len(row["fine_point"]) == 4
        assert all(value in (0, 4, 8) for value in row["fine_point"])
        assert row["fine_point"] == [4 * value for value in row["block_equals_phase"]]
        assert row["coordinate_amplitude"] == max(row["fine_point"])
        assert all(value in (True, False)
                   for value in row["returns_to_its_own_block_after_three_steps"])

    bases = observations["character_bases"]
    assert bases["base_9"]["characters"] == 6561
    assert bases["base_3"]["characters"] == 6561
    assert bases["base_9"]["distinct_eigenvalues_measured"] == 65
    assert bases["base_3"]["distinct_eigenvalues_measured"] == 9
    assert bases["base_9"]["graph_degree"] == 8
    assert bases["base_3"]["graph_degree"] == 16
    assert bases["base_9"]["trace"] == 8 * 6561
    assert bases["base_3"]["trace"] == 16 * 6561
    assert bases["single_zero_mode_each"] is True
    length_3 = {int(row[0][0]): row[1] for row in bases["eigenvalue_multiplicities"]["length_3"]}
    assert length_3 == {3 * j: math.comb(8, j) * 2 ** j for j in range(9)}
    assert sum(length_3.values()) == 6561
    length_9 = {int(row[0][0]): row[1]
                for row in bases["eigenvalue_multiplicities"]["length_9"]
                if row[0][1:] == ["0", "0", "0", "0", "0"]}
    assert length_9 == {0: 1, 3: 8, 6: 216, 9: 416, 12: 16}
    assert sum(row[1] for row in bases["eigenvalue_multiplicities"]["length_9"]) == 6561
    assert len(bases["eigenvalue_multiplicities"]["length_9"]) == 65
    intersection = bases["eigenvalue_intersection"]
    assert intersection["values"] == [0, 3, 6, 9, 12]
    assert intersection["multiplicities"]["0"] == {
        "multiplicity_on_the_length_9_carrier": 1,
        "multiplicity_on_the_length_3_carrier": 1}
    assert intersection["multiplicities"]["3"] == {
        "multiplicity_on_the_length_9_carrier": 8,
        "multiplicity_on_the_length_3_carrier": 16}
    assert intersection["multiplicities"]["6"] == {
        "multiplicity_on_the_length_9_carrier": 216,
        "multiplicity_on_the_length_3_carrier": 112}
    assert intersection["multiplicities"]["9"] == {
        "multiplicity_on_the_length_9_carrier": 416,
        "multiplicity_on_the_length_3_carrier": 448}
    assert intersection["multiplicities"]["12"] == {
        "multiplicity_on_the_length_9_carrier": 16,
        "multiplicity_on_the_length_3_carrier": 1120}


def test_the_spectral_crossing_is_declared_exactly_and_not_dropped():
    crossing = section("S2_observations_and_spectra")["spectral_crossing"]
    assert crossing["agreeing_pairs"] == 81
    assert len(crossing["agreeing_base_9_frequencies"]) == 81
    assert len(crossing["agreeing_base_3_frequencies"]) == 81
    assert crossing["is_a_bijection_of_81_frequencies"] is True
    assert crossing["maximum_amplitude"] == "1"
    assert crossing["neither_base_contains_the_other"] is True
    assert "k = 3 c" in crossing["declared_reading"]
    assert "3 c_i" in crossing["criterion"]
    for k, c4 in zip(crossing["agreeing_base_9_frequencies"],
                     crossing["agreeing_base_3_frequencies"], strict=True):
        assert k == [3 * value for value in c4[:4]]
        assert c4[:4] == c4[4:]
    assert "not a reason to substitute" in crossing["relation_to_0228_section_5"]


def test_t1_places_the_two_extras_at_the_declared_end_and_rejects_the_controls():
    extra = section("S3_extra_block")
    assert extra["cycle"] == {"phases": 12, "unit_time_step": "one phase",
                              "closure_after": "twelve unit steps",
                              "declared_end_index": 12}
    structure = extra["declared_structure"]
    assert structure["extra_states"] == ["yong-9", "yong-6"]
    assert structure["count"] == 2
    assert structure["states_in_the_cycle_with_the_block"] == 14
    assert structure["positions"] == {"phase_order": list(range(12)),
                                      "extra_block_at": [12, 13], "total_states": 14}
    assert "用九" in structure["structural_position"]
    assert "踦" in structure["structural_position"]
    rows = extra["accepted_and_rejected"]
    assert len(rows) == 3
    assert rows[0]["accepted"] is True
    assert rows[0]["rejection_reasons"] == []
    assert rows[0]["at_the_declared_end"] is True
    assert rows[0]["is_doubling"] is True
    assert rows[1]["accepted"] is False
    assert rows[2]["accepted"] is False
    for row in rows[1:]:
        assert row["rejection_reasons"], "a rejection must name its rule"
        assert row["rejection_produced_by"] == "the declared structural rules"
    assert "index 12" in rows[1]["rejection_reasons"][0]
    assert "index 6" in rows[1]["rejection_reasons"][0]
    assert "exactly two extra states" in rows[2]["rejection_reasons"][0]
    assert extra["negative_controls"] == {
        "count": 2, "both_rejected": True, "rejection_is_asserted_not_narrated": True,
        "declared_failure_modes": ["an extra block placed in the interior",
                                   "a third extra state"]}


def test_t2_reports_the_closure_cubic_its_three_exits_and_the_closed_form():
    closure = section("S4_closure")
    assert closure["nontrivial_branch_at_p_eq_q_eq_0"] == "h^3 + 8 h^2 + 64 h - 320 = 0"
    exits = closure["three_exits"]
    assert len(exits) == 3
    assert exits[0]["value"] == "0"
    assert "E_{p,q}(0) = 0" in exits[0]["status"]
    assert exits[1]["value"] == "h*"
    assert exits[1]["correctly_rounded_prefix"] == "3.2035072879526181"
    low, high = (Fraction(exits[1]["isolation_interval"][0]),
                 Fraction(exits[1]["isolation_interval"][1]))
    assert Fraction(3) < low < high < Fraction(4)
    assert "not real" in exits[2]["status"]
    assert "-814" in exits[2]["status"]
    assert exits[2]["value"] == "-5.6017536439763091 +- 8.2771295362453176 i"

    cardano = closure["cardano"]
    assert cardano["depressed_cubic"] == "y^3 + 128/3 y - 12224/27 = 0 with y = h + 8/3"
    assert cardano["discriminant"] == "1461248/27 = (32/9)^2 * 4281"
    assert cardano["discriminant_positive"] is True
    assert cardano["exactly_one_real_root_by_monotonicity"] is True
    enclosure = cardano["closed_form_enclosure"]
    assert enclosure["inside_the_open_interval_5_6"] is True
    assert Fraction(enclosure["u_plus_v_enclosed_in"][0]) > 5
    assert Fraction(enclosure["u_plus_v_enclosed_in"][1]) < 6
    assert Fraction(enclosure["u_enclosed_in"][0]) > 7
    assert Fraction(enclosure["u_enclosed_in"][1]) < 8
    assert Fraction(enclosure["v_enclosed_in"][0]) > -2
    assert Fraction(enclosure["v_enclosed_in"][1]) < -1
    assert "u^3 + v^3" in cardano["why_the_closed_form_is_the_real_root"]
    assert "(32/9) sqrt(4281)" in cardano["closed_form"]

    perturbed = closure["perturbed_closure_members"]
    assert [row["p"] for row in perturbed] == ["0", "1", "-2"]
    for row in perturbed:
        assert row["degree"] == 3
        assert row["constant_term"] == "-5/8"


def test_the_two_closure_readings_are_kept_side_by_side_and_differ():
    comparison = section("S4_closure")["comparison_with_the_declared_level_reading"]
    level = comparison["declared_level_reading"]
    closure = comparison["closure_reading"]
    assert level["distinct_real_roots"] == 2
    assert closure["nontrivial_distinct_real_roots"] == 1
    assert closure["total_exits"] == 3
    assert closure["trivial_exit"] == "h = 0, a root for every (p, q)"
    assert level["largest_branch_amplitude"] == "2 + sqrt(8 sqrt(17) - 20)"
    assert level["real_branches"] == "h = -2 +- sqrt(8 sqrt(17) - 20)"
    assert "-512" in closure["why_one_real"]
    difference = comparison["difference"]
    assert difference["counts_differ"] is True
    assert difference["real_branch_count"] == {"declared_level": 2,
                                               "closure_nontrivial_branch": 1}
    assert difference["kept_side_by_side"] is True
    assert difference["not_substituted"] is True
    assert "one against two" in difference["statement"] or "different number" in \
        difference["statement"]


def test_t3_reports_every_declared_candidate_separately_with_its_amplitude():
    crossings = section("S5_crossing_candidates")
    assert crossings["candidate_count"] == 3
    assert crossings["every_declared_candidate_reported_separately"] is True
    candidates = crossings["candidates"]
    assert sorted(candidates) == ["i_year_seam_side_0", "ii_mutual_measuring_diagonal",
                                  "iii_spectral_crossing"]

    seam = candidates["i_year_seam_side_0"]
    assert seam["decided"] is True
    assert seam["maximum_amplitude"] == "2 + sqrt(8 sqrt(17) - 20)"
    coupling = seam["time_coupling"]
    assert coupling["maximum"] == "31/512"
    assert coupling["attained_at_side"] == 0
    assert coupling["defects"][:2] == ["-31/512", "-15/512"]
    assert coupling["defects"][2:] == ["0"] * 10
    assert coupling["side_0_seam_value"] == "1/8"
    spatial = seam["spatial_amplitude"]
    assert spatial["declared_level_reading_maximum"] == "1"
    assert spatial["branch_reading_maximum"] == "2 + sqrt(8 sqrt(17) - 20)"
    assert spatial["attained_at_side"] == 0
    assert spatial["branch_reading_side_0"] == "|h|"
    assert spatial["branch_reading_side_1"] == "|E_0(h)|"
    assert spatial["branch_reading_side_1_exact"].startswith("sqrt(17) - 3")
    assert "E_0^2 + 6 E_0 - 8 = 0" in spatial["branch_reading_side_1_exact"]
    side_one_low = Fraction(spatial["branch_reading_side_1_enclosure"][0])
    side_one_high = Fraction(spatial["branch_reading_side_1_enclosure"][1])
    assert Fraction(1) < side_one_low < side_one_high < Fraction(9, 8)
    rows = spatial["per_side_amplitudes"]
    assert [row["side"] for row in rows] == ["side_0", "side_1", "sides_2_to_11",
                                             "terminal_boundary_12"]
    assert all(row["attained"] is True for row in rows)
    assert all(row["declared_level_reading"] == "1" for row in rows)
    amplitudes = [Fraction(row["branch_reading_maximum"]) for row in rows]
    assert amplitudes[2] == amplitudes[3] == Fraction(1)
    assert amplitudes[0] > amplitudes[1] > Fraction(1)
    assert max(amplitudes) == amplitudes[0]
    assert amplitudes[0] == Fraction(spatial["branch_reading_maximum_enclosure"][1])

    diagonal = candidates["ii_mutual_measuring_diagonal"]
    assert diagonal["size"] == 81
    assert diagonal["maximum_amplitude"] == "8"
    assert diagonal["decided"] is True
    assert diagonal["undecided_part"]

    spectral = candidates["iii_spectral_crossing"]
    assert spectral["declared"] is True
    assert spectral["crossing_frequencies"] == 81
    assert spectral["maximum_amplitude"] == "1"
    assert spectral["decided"] is True
    assert "k_i = 3 c_i" in spectral["declaration"]


def test_the_block_witness_fails_the_time_iteration_by_the_witness():
    witness = section("S6_controls")["block_witness"]
    rows = witness["witness"]
    assert rows["first_point"] == [6, 3, 3, 6]
    assert rows["second_point"] == [8, 3, 3, 6]
    assert rows["common_block"] == [2, 1, 1, 2]
    assert rows["first_after_T_0"] == [7, 3, 3, 6]
    assert rows["second_after_T_0"] == [0, 3, 3, 6]
    assert rows["block_after_T_0"] == [[2, 1, 1, 2], [0, 1, 1, 2]]
    assert witness["produced_by_the_witness"] is True
    assert witness["equal_inputs_different_successors"] is True
    assert witness["no_deterministic_update_on_the_81_block_labels_exists"] is True
    assert "F(q_block(z)) = q_block(T_0 z)" in witness["why"]
    assert witness["count_of_failures_of_the_particular_equation"] == 17496
    assert witness["refinement_chain_of_class_counts"][:3] == [81, 1296, 6561]
    assert witness["qiong_fibre_of_the_witness"] == "{6,7,8} x {3,4,5} x {3,4,5} x {6,7,8}"


def test_the_extrusion_countermodel_is_reproduced_and_judged_degenerate():
    extrusion = section("S6_controls")["extrusion"]
    assert extrusion["reproduced"] is True
    assert extrusion["declared_period"] == [0, 0, 0, 1]
    assert extrusion["period_verified_exactly"] is True
    assert extrusion["diagonal_variant_period_verified_exactly"] is True
    assert extrusion["verdict"] == "Degenerate"
    assert extrusion["not_a_time_resource"] is True
    assert "not a time resource" in extrusion["why_degenerate"]
    assert "diagonal" in extrusion["why_degenerate"]
    assert len(extrusion["declared_control"]) > 0


def test_the_identity_loop_control_and_the_realisation_control_are_reported():
    controls = section("S6_controls")
    identity = controls["identity_loop_control"]
    assert identity["permutation"] == "identity"
    assert identity["falsifiable"] is True
    assert identity["agrees_with_the_first_scheme"] is True
    assert len(identity["loops"]) == 2
    for row in identity["loops"]:
        assert row["verdict"] == "DecidedIdentity"
        assert row["permutation_of_the_two_real_branches"] == "identity"
        assert row["branches_stay_separated"] is True
        assert row["branch_count_per_sample"] == 2
        assert row["sample_points"] == 64
        assert Fraction(row["minimum_exact_gap_between_the_branches"]) > 0
    realisation = controls["realisation_control"]
    assert realisation["control_outcome"] == "FAILED_TO_DISCRIMINATE"
    assert realisation["retained"] is True
    assert realisation["reproduced"] is True
    assert realisation["discriminating_variant"]


def test_the_amplitude_floor_witness_of_the_first_scheme_is_reproduced():
    witness = section("S6_controls")["amplitude_floor_witness"]
    assert (witness["p"], witness["q"]) == ("-2", "17/10")
    assert witness["J_inf"] == "1"
    assert witness["attained"] is True
    assert witness["on_the_discriminant_variety"] is False
    assert witness["in_the_interior"] is True
    assert len(witness["branches"]) == 2
    for row in witness["branches"]:
        assert Fraction(row["abs_h_upper_bound"]) < 1
        assert Fraction(row["abs_E_0_upper_bound"]) < 1
        assert row["below_the_frozen_level"] is True


def test_the_baseline_comparison_states_what_it_could_not_decide():
    baseline = section("S7_baseline_comparison")
    first = baseline["first_scheme"]
    assert first["amplitude_floor"] == "J_inf = 1"
    assert first["attained_at"] == "(p, q) = (-2, 17/10)"
    assert first["on_the_discriminant_variety"] is False
    assert first["no_declared_real_loop_realises_the_transposition"] is True
    second = baseline["second_scheme"]
    assert second["unperturbed_closure_amplitude"] == "h* = 3.2035072879526181..."
    assert second["real_branches_of_the_nontrivial_closure_branch"] == 1
    assert second["real_branches_of_the_declared_level_reading"] == 2
    low, high = (Fraction(second["enclosure"][0]), Fraction(second["enclosure"][1]))
    assert Fraction(3) < low < high < Fraction(4)
    level_low = Fraction(second["largest_level_branch_amplitude_enclosure"][0])
    level_high = Fraction(second["largest_level_branch_amplitude_enclosure"][1])
    assert level_low > high > Fraction(1)
    assert level_high > level_low
    side_by_side = baseline["side_by_side"]
    assert side_by_side["the_numbers_are_not_comparable_directly"] is True
    assert side_by_side["real_branch_counts"] == {"level_reading": 2, "closure_reading": 1}
    verdict = baseline["do_the_time_conditions_change_what_is_reachable"]
    assert verdict["verdict"] == "NotDecided"
    assert verdict["reason"]
    assert verdict["retained_partial_result"]["closure_real_branches"] == 1
    assert verdict["retained_partial_result"]["level_real_branches"] == 2
    assert verdict["retained_partial_result"]["first_scheme_floor"] == "1"


def test_the_boundaries_are_retained_and_nothing_native_is_claimed():
    report = load(EVIDENCE)
    contract = load(CONTRACT)
    assert report["protected"] == contract["protected"]
    assert report["residual"] == contract["residual"]
    assert report["level"] == contract["level"]
    assert report["tooling"]["declared_not_native_authority"] is True
    assert report["tooling"]["polynomial_library"] == "sympy"
    assert report["tooling"]["exact_only"] is True
    assert report["tooling"]["not_implemented"]
    claims = report["what_is_not_claimed"]
    assert claims["native_certificate"] is False
    assert claims["native_admission"] == "NotGranted"
    assert claims["stable_api_change"] is False
    assert claims["physical_claim"] is False
    assert claims["forecast"] is False
    assert claims["meteorological_data_used"] is False
    assert claims["no_wind_gap_no_plateau_no_january_circulation"] is True
    assert claims["exchange_realised_by_a_declared_real_loop"] is False
    assert claims["time_direction_is_a_declared_order_resource_only"] is True
    assert claims["no_rust_source_or_lock_changed"] is True
    assert claims["no_note_or_contract_edited"] is True
    assert claims["no_claim_added_to_docs_claims_toml"] is True
    assert claims["meteorological_correspondence"].startswith("Declared correspondence only")
    assert "Unavailable" in claims["meteorological_data_side"]


def test_the_undecided_items_and_the_modelling_choices_are_declared():
    report = load(EVIDENCE)
    undecided = report["undecided"]
    assert len(undecided) == 3
    items = [row["item"] for row in undecided]
    assert any("reachable" in item for item in items)
    assert any("spectra" in item or "spectral" in item for item in items)
    assert any("closed form" in item for item in items)
    for row in undecided:
        assert row["reason"]
        assert row["retained_partial_result"] is not None
    choices = report["modelling_choices"]
    for key in ("two_addresses", "mutual_measuring", "time_enters_on_the_target_side",
                "t1_placement", "t1_rejection_rule", "t2_closure", "t2_nontrivial_branch",
                "t2_real_root", "t2_closed_form", "t3_candidates", "t3_amplitudes",
                "spectral_crossing_declaration", "identity_loop", "extrusion",
                "resource_limits"):
        assert choices[key], key
    assert "decimal" in choices["t2_real_root"]
    assert "互度" in choices["mutual_measuring"]
    assert "floor(z/3)" in choices["mutual_measuring"]
    assert "one phase" in choices["time_enters_on_the_target_side"]
    assert "negative control" in choices["t1_placement"]
    assert "two extra" in choices["t1_rejection_rule"]
    assert "index 12" in choices["t1_rejection_rule"]
    assert "fixed point" in choices["t2_closure"]
    assert "k = 3 c" in choices["t3_candidates"]
    assert "separately" in choices["t3_candidates"]
    assert "equal-rank" in choices["spectral_crossing_declaration"]
    assert "rlimit_portability" in choices["resource_limits"]


def test_the_two_refused_conclusions_are_stated_in_the_contract_itself():
    contract = load(CONTRACT)
    assert contract["acceptance"].startswith("Every acceptance assertion is exact")
    assert "no floating-point value" in contract["acceptance"]
    assert contract["meteorological_correspondence"]["status"].startswith(
        "Declared correspondence only")
    assert contract["meteorological_correspondence"]["data_side"].startswith("Unavailable")
    assert contract["budgets"]["routes"] == 1
    assert len(contract["controls"]) == 6
    assert any("extrusion" in row for row in contract["controls"])
    assert any("block-address" in row for row in contract["controls"])


def test_the_claim_is_registered_once_and_binds_the_checker_and_the_note():
    """The record carries exactly one claim, and it names the checker, the evidence and the note.

    The checker was written while this test asserted the claim's absence, because a claim lives in
    `docs/claims.toml` and the checker's own run may not write there.  The parent session added
    the claim with the note; the assertion is inverted rather than dropped, so the binding stays
    checked.
    """
    claims = tomllib.loads((ROOT / "docs/claims.toml").read_text(encoding="utf-8"))["claim"]
    matches = [claim for claim in claims if claim["claim_id"] == CLAIM_ID]
    assert len(matches) == 1, "exactly one claim must be registered"
    claim = matches[0]
    assert claim["status"] == "bounded-experiment"
    for symbol in ("two_address_exchange_v1/calibration.py", "two_address_exchange_v1/contract.json",
                   "two_address_exchange_v1/evidence.json", "0236-two-addresses-at-once"):
        assert symbol in claim["code_symbol"], symbol
    assert "NotDecided" in claim["counterexample_boundary"], "the boundary must retain the undecided verdict"
    assert "NotGranted" in claim["counterexample_boundary"], "the boundary must record native admission"
    assert claim["forbidden_conflations"], "the claim must name its conflations"
