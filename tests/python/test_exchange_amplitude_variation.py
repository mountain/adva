"""Bounded exchange amplitude variation calibration; external evidence, no admission.

The assertions here are about what the retained checker decided by exact arithmetic
on one declared twelve-phase fixture.  They are not claims about any physical
object, they promote no native identity, and they confirm no exchange: the retained
evidence records that no declared real loop realises the transposition.

The checker is invoked without `-S` because its declared external library (sympy)
must be importable; the run remains an external exact calibration either way.
"""

import hashlib
import json
import subprocess
import sys
import tomllib
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/exchange_amplitude_variation_v1"
CHECKER = HERE / "calibration.py"
CONTRACT = HERE / "contract.json"
CONTRACT_INITIAL = HERE / "contract-initial.json"
EVIDENCE = HERE / "evidence.json"
CLAIM_ID = "adva.bounded-experiment.exchange-amplitude-variation.v0"


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
    assert report["contract_sha256"] == digest(CONTRACT)
    assert report["contract_initial_sha256"] == digest(CONTRACT_INITIAL)
    assert report["assertions"] <= contract["budgets"]["max_assertions"]
    assert report["limits"] == contract["budgets"]
    assert all(report["checks"].values())


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


def test_an_existing_output_is_never_overwritten(tmp_path):
    output = tmp_path / "keep.json"
    output.write_text("retained", encoding="utf-8")
    completed = invoke(CHECKER, output)
    assert completed.returncode != 0
    assert output.read_text(encoding="utf-8") == "retained"


def test_the_fixture_and_the_side_identity_are_asserted_not_assumed():
    fixture = section("S1_fixture_and_side_identity")
    assert fixture["reference_is_an_exact_periodic_orbit"] is True
    assert fixture["reference_path"] == [0, 1, 2, 1, 0, -1, -2, -1, 0, 1, 0, -1, 0]
    assert fixture["dilations"][:2] == ["1/2", "3/4"]
    assert fixture["dilations"][2:] == ["1"] * 10
    assert fixture["curvatures"][:2] == ["1/8", "1/8"]
    assert fixture["curvatures"][2:] == ["0"] * 10
    identity = fixture["side_identity_for_a_general_h"]
    assert identity["h_m_equals_h_2_for_m_equals_3_to_12"] is True
    assert identity["h_1"] == "h**2/8 + h/2"
    assert identity["h_2"] == identity["composed_return"]
    assert identity["annual_return"] != identity["composed_return"]
    assert fixture["E_p_q_at_zero_is_zero_for_declared_parameters"]
    assert fixture["side_amplitude_model"]["sides_2_to_11"].startswith("exactly 1")


def test_the_unperturbed_return_factors_in_Q_sqrt17():
    unperturbed = section("S2_unperturbed_return")
    assert unperturbed["factorisation_checked_by_field_arithmetic"] is True
    assert "8 sqrt(17)" in unperturbed["factorisation_in_Q_sqrt17_y"]
    assert unperturbed["return_polynomial"] == "h**4 + 8*h**3 + 64*h**2 + 192*h - 512"
    assert unperturbed["shifted_polynomial"] == "y**4 + 40*y**2 - 688"
    assert unperturbed["two_real_roots"] == "h = -2 +- sqrt(8 sqrt(17) - 20)"
    assert unperturbed["conjugate_pair"] == "h = -2 +- i sqrt(8 sqrt(17) + 20)"
    assert unperturbed["sign_conditions"]["8_sqrt17_minus_20_positive"] is True
    assert unperturbed["sturm"]["distinct_real_roots"] == 2
    assert unperturbed["sturm"]["exact_brackets"] == {"negative_root_in": "(-6, -5)",
                                                      "positive_root_in": "(3/2, 17/10)"}


def test_the_superseded_collapse_witness_is_reproduced_and_why_it_matters():
    superseded = section("S3_superseded_collapse_witness")
    assert superseded["superseded_sha256_matches"] is True
    assert superseded["double_root"] == {"y": "2", "h": "0", "multiplicity": 2}
    assert superseded["first_factor_at_the_collapsed_parameters"] == "(y - 2)^2"
    assert superseded["J_inf_at_the_collapsed_branch"] == "0"
    assert all(value == "0" for value in superseded["amplitudes_at_the_collapsed_branch"])
    assert superseded["terminal_amplitude_at_the_collapsed_branch"] == "0"
    assert len(superseded["branches_at_plus_minus_eps"]) == 4
    for row in superseded["branches_at_plus_minus_eps"]:
        assert row["J_inf_of_the_two_branches"] == row["eps"], row["eps"]
    assert "the collapse is excluded" in superseded["why_the_initial_contract_was_superseded"]
    assert superseded["the_reference_is_never_a_branch_in_the_frozen_family"].startswith(
        "E_{p,q}(0) = 0")


def test_the_discriminant_variety_is_exact_and_its_branches_are_declared():
    discriminant = section("S4_discriminant_variety")
    assert discriminant["total_degree"] == 12
    assert discriminant["degree_in_p"] == 8
    assert discriminant["degree_in_q"] == 5
    assert discriminant["term_count"] == 52
    multiplicities = {row["factor"]: row["multiplicity"]
                      for row in discriminant["factorisation"]}
    assert multiplicities["8*p + 1"] == 6
    assert multiplicities["8*q + 1"] == 2
    assert multiplicities["64*q + 17"] == 2
    assert multiplicities["2048*p**2 + 608*p - 8*q + 43"] == 1
    assert [branch["name"] for branch in discriminant["declared_branches"]] == \
        ["B1", "B2", "B3", "B4"]
    assert len(discriminant["sign_rule_checks"]) == 13
    applicable = 0
    on_a_branch = 0
    for row in discriminant["sign_rule_checks"]:
        if row["sign_D_rule_applies"]:
            applicable += 1
            assert row["sign_D_rule_agrees"] is True, row["label"]
            assert row["sign_disc_rule_agrees"] is True, row["label"]
        else:
            on_a_branch += 1
            assert row["D"] == "0", row["label"]
    assert applicable == 7
    assert on_a_branch == 6


def test_every_declared_case_reports_a_chain_a_remainder_and_a_cross_check():
    cases = section("S5_case_analysis")
    assert cases["variables_and_order"] == ["h", "p", "q", "lam"]
    assert [row["case"] for row in cases["cases"]] == ["C1", "C2", "C3", "C4", "C5"]
    for row in cases["cases"]:
        assert row["verdict"], row["case"]
        if row["case"] == "C5":
            assert row["system"] == []
            continue
        assert row["chain"], row["case"]
        assert row["remainder"] is not None
        assert row["cross_check_verdict"], row["case"]
    c1 = cases["cases"][0]
    assert c1["verdict"] == "EmptyCase_no_stationary_candidate"
    assert c1["solutions"]["groebner_basis_is_one"] is True
    assert "G = -1 identically" in c1["solutions"]["certificate"]
    for row in cases["cases"][1:2] + cases["cases"][3:4]:
        assert row["remainder_is_zero"] is True
        assert row["groebner_membership"] is True
        assert row["verdict"] == "OnTheDiscriminantVariety"
        assert row["solutions"]["declared_instances"]
        for instance in row["solutions"]["declared_instances"]:
            assert instance["D_at_that_point"] == "0"
            assert instance["on_the_discriminant_variety"] is True
            assert "B1" in instance["declared_branch_membership"]


def test_real_root_structure_is_counted_and_isolated_exactly():
    roots = section("S6_real_root_structure")
    counts = dict(roots["counts"])
    assert counts["frozen"] == 2
    assert counts["the declared J_inf witness"] == 2
    assert counts["above the parabola with q > -1/8"] == 4
    assert counts["below q = -1/8"] == 0
    assert counts["the tangency vertex of B1 and B2"] == 1
    assert counts["the triple point of B1, B3 and B4"] == 1
    exceptional = roots["exceptional_points"]
    assert "(h - 32/3)^4" in exceptional["vertex_of_B1_and_B2"]
    assert exceptional["triple_point_of_B1_B3_B4"].endswith("the only finite root is h = 8/3")
    for row in roots["points"]:
        assert row["side_of_the_discriminant_variety"]
        for root in row["roots"]:
            for endpoint in root["isolation_interval"]:
                assert "/" in endpoint or endpoint.lstrip("-").isdigit()
            assert root["G_prime_sign_definite"] in (True, False)
            assert root["root_is_on_the_simple_side"] == (
                root["is_simple"] and root["G_prime_sign_definite"])


def test_the_constrained_minimum_is_the_plateau_and_not_the_discriminant():
    minimality = section("S7_minimality_and_second_variation")
    witness = minimality["witness"]
    assert witness["J_inf"] == "1"
    assert witness["is_attained"] is True
    assert witness["on_the_discriminant_variety"] is False
    assert witness["in_the_interior_of_the_feasible_region"] is True
    for row in witness["branches"]:
        assert row["below_the_frozen_level"] is True
        assert Fraction(row["abs_E_0_upper_bound"]) < 1
        assert Fraction(row["abs_h_upper_bound"]) < 1
    bounded = 0
    for row in minimality["floor_table"]:
        assert row["frozen_side_and_all_twelve_sides_included"] is True
        if row["J_inf_upper_bound"] is not None:
            bounded += 1
            assert Fraction(row["J_inf_upper_bound"]) >= 1
            assert Fraction(row["J_2_upper_bound"]) > 20
    assert bounded >= 4
    frozen_row = next(row for row in minimality["floor_table"] if row["label"] == "frozen")
    assert Fraction(frozen_row["J_2_upper_bound"]) < 57
    assert minimality["second_variation"]["verdict"] == \
        "SecondVariationZero_NonIsolatedMinimum"
    assert minimality["second_variation"]["second_variation"].startswith("0 identically")
    plateau = minimality["plateau_box"]
    assert plateau["rounds"][-1]["all_conditions_decided_and_true"] is True
    assert "interval-subdivision" in plateau["method"] or "interval" in plateau["method"]
    conjecture = minimality["declared_conjecture"]
    assert conjecture["decision_for_the_minimiser"] == "False"
    assert conjecture["decision_for_the_stationary_candidates"] == "True"
    j_two = minimality["control_functional_J_2"]
    assert j_two["infimum"].startswith("20")
    assert j_two["on_the_discriminant_variety"] is False
    bounds = [Fraction(row["J_2_upper_bound"]) for row in j_two["escape_ray"]["rows"]]
    assert bounds == sorted(bounds, reverse=True)
    assert all(bound > 20 for bound in bounds)
    assert bounds[-1] - 20 < Fraction(1, 100)


def test_every_declared_loop_reports_a_permutation_or_an_explicit_undecided():
    exchange = section("S8_exchange_protocol")
    loops = {row["loop"]: row for row in exchange["loops"]}
    assert len(loops) == 5
    control = loops["L0 identity control, non-encircling"]
    assert control["crossing_count"] == 0
    assert control["permutation_of_the_four_roots"] == "identity"
    assert exchange["identity_control"]["permutation"] == "identity"
    assert exchange["identity_control"]["falsifiable"] is True
    smooth = loops["L1 around a smooth point of the branch B1"]
    assert smooth["crossing_count"] == 2
    assert smooth["permutation_of_the_four_roots"] == "identity"
    assert smooth["verdict"] == "DecidedIdentity"
    assert sorted(run[0] for run in smooth["sub_arc_runs"]) == [2, 4]
    for row in exchange["loops"]:
        assert row["permutation_of_the_four_roots"] in ("identity", "Undecided")
        assert row["justification"]
        if row["verdict"] == "Undecided":
            assert row["permutation_of_the_four_roots"] == "Undecided"
    wide = loops["L4 a wide loop crossing every branch"]
    assert wide["crossing_count"] == 10
    assert wide["irrational_crossings"] == 2
    assert wide["verdict"] == "Undecided"
    degenerate = loops["L3 around the degenerate triple point"]
    assert degenerate["crossing_count"] == 8
    assert degenerate["irrational_crossings"] == 2
    branch_2 = loops["L2 around a smooth point of the branch B2"]
    assert branch_2["crossing_count"] == 2
    assert branch_2["crossings_per_branch"] == [["B2", 2]]
    assert branch_2["verdict"] == "Undecided"
    assert len(exchange["undecided_loops"]) == 3
    assert "no declared real loop realises" in exchange["finding"]


def test_the_controls_are_reported_including_the_failed_one():
    controls = section("S9_controls")
    assert controls["superseded_collapse_witness"]["reproduced"] is True
    frozen = controls["frozen_unperturbed_roots"]
    assert frozen["reproduced"] is True
    assert frozen["distinct_real_roots"] == 2
    assert frozen["conjugate_pair"] == "h = -2 +- i sqrt(8 sqrt(17) + 20)"
    deleted = controls["deleted_side_control"]
    assert deleted["single_side_deletion_moves_the_minimiser"] is False
    assert deleted["control_outcome"].startswith("FAILED_TO_DISCRIMINATE")
    assert deleted["discriminating_variant"]["levels_along_the_escape_ray"]
    for row in deleted["declared_single_side_deletions"]:
        assert row["minimum_moves"] is False
        assert row["floor_remains_one"] is True
    realisations = controls["two_realisations"]
    assert [row["label"] for row in realisations] == ["frozen", "declared witness",
                                                     "equal perturbations"]
    assert realisations[0]["realisations_agree"] is True
    assert realisations[1]["realisations_agree"] is False
    assert controls["reference_is_never_a_branch"]["checked"] is True
    assert controls["identity_loop_control"]["permutation"] == "identity"


def test_the_boundaries_are_retained_and_nothing_native_is_claimed():
    report = load(EVIDENCE)
    contract = load(CONTRACT)
    assert report["protected"] == contract["protected"]
    assert report["residual"] == contract["residual"]
    assert report["level"] == contract["level"]
    claims = report["what_is_not_claimed"]
    assert claims["native_certificate"] is False
    assert claims["native_admission"] == "NotGranted"
    assert claims["physical_claim"] is False
    assert claims["forecast"] is False
    assert claims["meteorological_data_used"] is False
    assert claims["exchange_realised_by_a_declared_real_loop"] is False
    assert report["tooling"]["declared_not_native_authority"] is True
    assert report["tooling"]["polynomial_library"] == "sympy"
    assert len(report["undecided"]) == 2
    for item in report["undecided"]:
        assert item["reason"]
        assert item["retained_partial_result"] is not None
    assert report["modelling_choices"]["loops"]
    assert "circular" in report["modelling_choices"]["case_stationarity_system"]


def test_the_two_refused_conclusions_are_stated_in_the_contract_itself():
    contract = load(CONTRACT)
    assert contract["correction"]["supersedes"].endswith("contract-initial.json")
    assert "degenerate" in contract["correction"]["reason"]
    assert contract["constraint"]["declared_conjecture"].startswith("The constrained minimum")
    assert contract["budgets"]["child_processes"] == 0
    assert contract["meteorological_correspondence"]["status"].startswith(
        "Declared correspondence only")


def test_the_claim_is_registered_once_and_binds_the_checker_and_the_note():
    """The record carries one claim, and it names the checker, the evidence and the note.

    The checker was written while this test asserted that no claim existed, because a
    claim lives in `docs/claims.toml` and the checker's own run may not write there.
    The claim was added with the note; the assertion is inverted here rather than
    dropped, so the binding stays checked.
    """
    claims = tomllib.loads((ROOT / "docs/claims.toml").read_text(encoding="utf-8"))["claim"]
    matches = [claim for claim in claims if claim["claim_id"] == CLAIM_ID]
    assert len(matches) == 1, "exactly one claim must be registered"
    claim = matches[0]
    assert claim["status"] == "bounded-experiment"
    for symbol in ("calibration.py", "contract.json", "contract-initial.json",
                   "evidence.json", "0235-the-cheapest-exchange"):
        assert symbol in claim["code_symbol"], symbol
    assert "Undecided" in claim["counterexample_boundary"], "the boundary must retain the undecided loops"
    assert "NotGranted" in claim["counterexample_boundary"], "the boundary must record native admission"
    assert claim["forbidden_conflations"], "the claim must name its conflations"
