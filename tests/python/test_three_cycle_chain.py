"""The paired test for the three-cycle chain calibration; external evidence only.

The assertions here are about what the retained checker decided by exact arithmetic on one
declared annual return, one declared three-cycle chain and one declared reservoir.  They are
not claims about any physical object, they promote no native identity, and they confirm no
forecast: the chain is future, observational verification is Unavailable, and the retained
payload records both the failed drift control and the four Undecided items.

The checker is invoked without `-S` because its declared external library (sympy) must be
importable; the run remains an external exact calibration either way.

The record carries no claim for this run: the parent session adds the claim to
`docs/claims.toml` with its note, so the last test asserts the claim is absent rather than
dropping the binding.
"""

import hashlib
import json
import subprocess
import sys
import tomllib
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/three_cycle_chain_v1"
CHECKER = HERE / "calibration.py"
CONTRACT = HERE / "contract.json"
EVIDENCE = HERE / "evidence.json"
CLAIM_ID = "adva.bounded-experiment.three-cycle-chain.v0"
DECLARED_CONTRACT_SHA256 = \
    "a3dc2e8d86e45139484fceed571ef99ea3b63f18748c6f1c82bb031a3305a965"

ZERO = ["0", "0", "0"]
CLOSURE_AMPLITUDE = ["0", "1", "0"]
SLOW_COMPONENT = ["0", "1/2", "0"]


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
    assert report["schema"] == "adva.external.three-cycle-chain-calibration.v1"
    assert report["version"] == 1
    assert report["checker_sha256"] == digest(CHECKER)
    assert report["contract_sha256"] == digest(CONTRACT) == DECLARED_CONTRACT_SHA256
    assert report["contract_sha256_declared"] == DECLARED_CONTRACT_SHA256
    assert report["assertions"] <= contract["budgets"]["max_assertions"]
    assert report["limits"] == contract["budgets"]
    assert report["limits"]["child_processes"] == 0
    assert report["limits"]["routes"] == 1
    assert all(report["checks"].values())
    assert report["tooling"]["python_library"] == "sympy"
    assert report["tooling"]["declared_external_library"] is True
    assert report["tooling"]["declared_not_native_authority"] is True
    assert report["tooling"]["exact_only"] is True
    assert report["tooling"]["not_implemented"]


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
    assert fresh["controls"] == retained["controls"]
    assert fresh["undecided"] == retained["undecided"]
    assert fresh["modelling_choices"] == retained["modelling_choices"]
    assert fresh["what_is_not_claimed"] == retained["what_is_not_claimed"]
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
    assert completed.returncode == 2
    assert "refusing to overwrite" in completed.stdout
    assert output.read_text(encoding="utf-8") == "retained"


def test_the_chain_reports_each_cycle_separately_with_its_exact_seam_state():
    chain = section("S1_chain")
    assert chain["annual_return"] == "E(h) = (3/8) h + (1/8) h^2 + (1/64) h^3 + (1/512) h^4"
    assert chain["closure_polynomial"] == "512 (E(h) - h) = h (h^3 + 8 h^2 + 64 h - 320)"
    assert chain["declared_seam"] == "December 2026 / January 2027"
    assert chain["cycles"] == ["C1", "C2", "C3"]
    assert chain["cycle_spans"] == {"C1": "2026-12 to 2027-12",
                                   "C2": "2027-12 to 2028-12",
                                   "C3": "2028-12 to 2029-12"}
    assert chain["every_cycle_reported_separately"] is True
    assert chain["every_cycle_is_a_genuine_return"] is True
    assert chain["closure_status_by_cycle"] == {"C1": "ClosedByFixedPoint",
                                                "C2": "ClosedByFixedPoint",
                                                "C3": "ClosedByFixedPoint"}
    assert chain["seam_states"] == [CLOSURE_AMPLITUDE] * 4
    assert len(chain["seams"]) == 3
    for row in chain["seams"]:
        assert row["entry_seam_state"] == row["exit_seam_state"] == CLOSURE_AMPLITUDE
        assert row["closure_defect"] == ZERO
        assert row["drift"] == ZERO
        assert row["genuine_return"] is True
        assert row["closure_status"] == "ClosedByFixedPoint"
    assert chain["field_of_the_seam_state"]["field"].startswith("Q(w)")
    amplitude = chain["closure_amplitude"]
    assert amplitude["value"] == "3.2035072879526181..."
    assert amplitude["field_coordinates"] == CLOSURE_AMPLITUDE
    assert amplitude["real_exits_of_the_closure_cubic"] == 1
    assert amplitude["trivial_exit"] == "h = 0, since E(0) = 0 identically"
    low, high = (Fraction(amplitude["isolation_interval"][0]),
                 Fraction(amplitude["isolation_interval"][1]))
    assert Fraction(3) < low < high < Fraction(4)
    cumulative = chain["cumulative_composition"]
    assert cumulative["polynomial_degree"] == 64
    assert cumulative["cofactor_degree"] == 60
    assert cumulative["cofactor_real_roots"] == 0
    assert cumulative["real_root_count"] == 2
    counterfactual = chain["counterfactual_chain"]
    assert counterfactual["seed"] == ["1/4", "1", "0"]
    assert counterfactual["closes_in_C1"] is False
    assert counterfactual["all_drifts_nonzero"] is True
    assert counterfactual["cycles"][0]["drift"] == ["62497/131072", "-487/8192", "-13/4096"]


def test_the_step_count_and_the_remainder_are_counted_in_the_same_unit():
    steps = section("S2_step_count")
    assert steps["steps_per_cycle"] == 9
    assert steps["groups_per_cycle"] == 3
    assert steps["steps_per_group"] == 3
    assert steps["end_block_steps"] == 2
    assert steps["cycles"] == 3
    assert steps["total_step_count"] == 27
    assert steps["remainder"] == 6
    assert steps["total_with_the_end_block"] == 33
    assert Fraction(steps["remainder_as_a_fraction_of_the_baseline"]) == Fraction(2, 9)
    assert Fraction(steps["remainder_in_the_step_unit"]) == 486
    division = steps["cycle_division"]
    assert division["phases_per_cycle"] == 12
    assert division["units_per_cycle"] == 27
    assert division["zan_per_cycle"] == 729
    assert Fraction(division["zan_per_unit"]) == 27
    assert Fraction(division["zan_per_phase"]) == Fraction(243, 4)
    assert division["identities"] == ["729 = 27 * 27", "729 = 12 * 243/4", "729 = 9 * 81"]
    rows = steps["accepted_and_rejected"]
    assert len(rows) == 3
    assert rows[0]["accepted"] is True
    assert rows[0]["block_steps"] == 2
    assert rows[0]["rejection_reasons"] == []
    assert rows[1]["accepted"] is False and rows[1]["block_steps"] == 1
    assert rows[2]["accepted"] is False and rows[2]["block_steps"] == 3
    assert "exactly 2 extra steps" in rows[1]["rejection_reasons"][0]
    assert "not 3" in rows[2]["rejection_reasons"][0]
    assert steps["both_rejections_asserted"] is True
    assert steps["three_by_three_decomposition"]["total"] == 87
    assert steps["phase_reading"]["total"] == 42
    assert steps["phase_reading"]["remainder_matches_the_step_reading"] is True


def test_the_three_by_three_role_typing_executes_every_calamity_counterpart():
    roles = section("S3_role_typing")
    assert [row["role"] for row in roles["role_groups"]] == [
        "lower: deliberation", "middle: fortune", "upper: calamity"]
    assert all(len(row["members"]) == 3 for row in roles["role_groups"])
    assert roles["groups_per_cycle"] == 3
    assert roles["steps_per_group"] == 3
    assert roles["steps_per_cycle"] == 9
    assert roles["visible_failure_branch"] == "the upper, calamity group"
    assert roles["exit_clause"].startswith("終養始")
    assert roles["exit_clause_position_in_the_cycle"] == 9
    assert roles["conditions_declared"] == 9
    assert roles["every_condition_has_a_calamity_counterpart"] is True
    executions = roles["condition_executions"]
    assert [row["condition"] for row in executions] == [f"condition_{index}"
                                                        for index in range(1, 10)]
    for row in executions:
        assert row["counterpart_executed"] is True
        assert row["failure_branch_produced"] is True
        assert row["control_outcome"] == "Discriminated"
        assert row["discriminates"] is True
        assert row["success_holds"] is True
        assert row["calamity_counterpart"]
        assert row["counterpart_branch"]
    assert roles["failed_controls"] == []
    assert roles["no_control_dropped"] is True
    technique = roles["decision_to_technique"]
    assert technique["nonlinear_phases"] == [0, 1]
    assert technique["translation_phases"] == list(range(2, 12))
    assert technique["per_phase"]["0"] == "add-scale"
    assert technique["per_phase"]["5"] == "translation"
    assert "recomputation" in technique["independently_recovered"]
    recovered_leading = Fraction(technique["recovered_leading_coefficient"])
    assert recovered_leading > 0
    assert recovered_leading.numerator == 1
    assert technique["recovered_quotient_is_exact"] is True
    assert Fraction(technique["composition_leading_coefficient"]) == Fraction(1, 512) ** 21
    assert Fraction(technique["composition_leading_coefficient"]) * 512 \
        == Fraction(technique["recovered_leading_coefficient"])
    assert technique["recovered_quotient_degree"] == 60
    placement = roles["placement"]
    assert placement["declared_seam"] == "December 2026 / January 2027"
    accepted = placement["accepted_and_rejected"]
    assert accepted[0]["accepted"] is True
    assert all(row["accepted"] is False for row in accepted[1:])
    assert all(row["rejection_reasons"] for row in accepted[1:])


def test_the_fast_and_slow_split_conserves_the_slow_component_at_every_seam():
    split = section("S5_fast_and_slow")
    assert split["slow_conserved_in_the_primary"] is True
    assert split["fast_reset_allowed_in_the_primary"] is True
    assert split["carry_rule_injective_in_the_primary"] is True
    assert split["slow_component_carried_in_the_alternative"] is False
    assert [row["cycle"] for row in split["primary"]] == ["C1", "C2", "C3"]
    for row in split["primary"]:
        assert row["slow_drift"] == ZERO
        assert row["slow_conserved"] is True
        assert row["fast_reset_allowed"] is True
        assert row["slow_component"] == SLOW_COMPONENT
        assert row["fast_component"] == SLOW_COMPONENT
        assert row["fast_plus_slow"] == CLOSURE_AMPLITUDE
        assert row["seam_state"] == CLOSURE_AMPLITUDE
    assert all(row["slow_conserved"] is False for row in split["declared_alternative"])
    contrast = section("S3_role_typing")["slow_component_contrast"]
    assert contrast["primary_slow_drift_per_seam"] == [ZERO] * 3
    assert contrast["conserved_in_the_primary"] is True
    assert contrast["not_conserved_in_the_open_ocean_variant"] is True


def test_the_declared_reservoir_is_evaluated_exactly_and_declared_as_a_model():
    reservoir = section("S4_reservoir")
    assert reservoir["declared_model"] is True
    assert reservoir["not_a_claim_about_the_ocean"] is True
    assert Fraction(reservoir["relaxation_coefficient"]) == Fraction(1, 30)
    assert Fraction(reservoir["time_constant"]) == 30
    assert reservoir["reference_value"] == ["0", "1/60", "0"]
    assert reservoir["freshwater_source_term"] == ["0", "29/60", "0"]
    assert reservoir["steady_value"] == SLOW_COMPONENT
    assert reservoir["source_term_times_the_time_constant"] == reservoir["reference_value"]
    assert reservoir["steady_is_the_chain_seam_slow_component"] is True
    assert reservoir["slow_component_conserved"] is True
    assert reservoir["slow_drift_per_seam"] == [ZERO] * 3
    assert reservoir["time_scale_mismatch_is_retained"] is True
    assert "declarations chosen for exactness" in reservoir["why_this_is_a_declared_model"]
    assert "claim about any ocean" in reservoir["why_this_is_a_declared_model"]
    consistency = reservoir["seam_consistency"]
    assert consistency["chain_seam_state"] == CLOSURE_AMPLITUDE
    assert "stationary" in consistency["requirement"]
    displaced = reservoir["displaced_reservoir"]
    assert [Fraction(row[0]) for row in displaced["drifts"]] == [
        Fraction(-1, 120), Fraction(-29, 3600), Fraction(-841, 108000)]
    assert displaced["each_drift_is_the_previous_times_29_over_30"] is True
    assert displaced["first_drift_is_minus_the_relaxation_coefficient_times_the_displacement"]
    open_ocean = reservoir["open_ocean_reading"]
    assert open_ocean["conserved"] is False
    assert [Fraction(row[1]) for row in open_ocean["drifts"]] == [
        Fraction(-1, 60), Fraction(-29, 1800), Fraction(-841, 54000)]
    assert open_ocean["first_drift_is_minus_the_relaxation_coefficient_times_the_slow_component"]


def test_both_variants_are_reported_side_by_side_and_the_memory_control_discriminates():
    variants = section("S6_variants")
    assert variants["reported_side_by_side"] is True
    assert variants["neither_variant_is_substituted_for_the_other"] is True
    primary = variants["primary"]
    alternative = variants["declared_alternative"]
    assert primary["seed"] == alternative["seed"] == CLOSURE_AMPLITUDE
    assert primary["seam_states"] == [CLOSURE_AMPLITUDE] * 4
    assert alternative["seam_states"] == [CLOSURE_AMPLITUDE] * 4
    assert primary["drifts"] == [ZERO] * 3
    assert alternative["drifts"] == [ZERO] * 3
    assert primary["closes_in_every_cycle"] is True
    assert alternative["closes_in_every_cycle"] is True
    assert primary["slow_component_conserved"] is True
    assert primary["keeps_the_carried_memory"] is True
    assert alternative["slow_component_conserved"] is False
    assert alternative["keeps_the_carried_memory"] is False
    assert alternative["slow_component_at_every_seam"] == "none carried"
    control = variants["memory_control"]
    assert control["discriminates_on_the_slow_channel"] is True
    assert control["primary_keeps_the_carried_state"] is True
    assert control["alternative_keeps_the_carried_slow_component"] is False
    assert control["displacement"] == ["1/4", "0", "0"]
    assert control["primary_slow_response_at_the_first_seam"] == ["-1/120", "0", "0"]
    assert control["open_ocean_slow_response_at_the_first_seam"] == ["0", "-1/60", "0"]
    assert control["primary_slow_response_at_the_first_seam"] != \
        control["open_ocean_slow_response_at_the_first_seam"]
    assert "does not separate" in control["variants_that_do_not_discriminate"]


def test_the_sealing_side_is_a_bound_and_a_violation_is_detected():
    sealing = section("S3_role_typing")["sealing"]
    primary = sealing["primary"]
    assert primary["violated"] is False
    assert primary["per_cycle_leakage"] == ["0", "0", "0"]
    assert primary["cumulative_leakage"] == ["0", "0", "0"]
    assert primary["leakage_can_cancel_a_violation"] is False
    assert primary["reported_at_every_cycle"] is True
    assert primary["bound"] == "cumulative leakage <= 0"
    leaked = sealing["declared_leaking_chain"]
    assert leaked["violated"] is True
    assert leaked["cumulative_leakage"] == ["1/1000", "1/500", "3/1000"]
    assert Fraction(sealing["signed_term_counterexample"]) == 0
    assert "cannot cancel a violation" in sealing["reading"]


def test_the_baselines_are_reproduced_and_the_ordering_is_asserted_exactly():
    baselines = section("S7_baselines")
    assert baselines["all_three_reproduced"] is True
    floor = baselines["first_scheme_floor"]
    assert floor["statement"] == "J_inf = 1"
    assert floor["attained_at"] == "(-2, 17/10)"
    assert floor["witness"] == ["-2", "17/10"]
    assert floor["perturbed_curvatures"] == ["-15/8", "73/40"]
    assert floor["off_the_discriminant_variety"] is True
    assert floor["level_one_real_branches"] == 2
    assert floor["floor_attained_exactly"] is True
    assert floor["reproduced"] is True
    for key in ("negative_branch_enclosure", "positive_branch_enclosure"):
        low, high = (Fraction(floor[key][0]), Fraction(floor[key][1]))
        assert Fraction(-1) < low < high < Fraction(1)
    closure = baselines["closure_amplitude"]
    assert closure["statement"] == "3.2035072879526181..."
    assert closure["real_exits"] == 1
    low, high = (Fraction(closure["isolation_interval"][0]),
                 Fraction(closure["isolation_interval"][1]))
    assert Fraction(3) < low < high < Fraction(4)
    level = baselines["level_reading_largest_amplitude"]
    assert level["statement"] == "2 + sqrt(8 sqrt(17) - 20) = 5.6034490429..."
    assert level["real_branches"] == 2
    assert level["distinct_real_roots"] == 2
    assert level["exact_form"] == "2 + sqrt(8 sqrt(17) - 20)"
    assert level["shifted_quartic"] == "u^4 + 40 u^2 - 688 with u = h + 2"
    root_low, root_high = (Fraction(level["root_enclosure"][0]),
                           Fraction(level["root_enclosure"][1]))
    assert Fraction(5) < root_low < root_high < Fraction(6)
    radius_low, radius_high = (Fraction(level["square_root_enclosure"][0]),
                               Fraction(level["square_root_enclosure"][1]))
    assert Fraction(7, 2) < radius_low < radius_high < Fraction(15, 4)
    form_low, form_high = (Fraction(level["declared_form_enclosure"][0]),
                           Fraction(level["declared_form_enclosure"][1]))
    assert form_low == 2 + radius_low and form_high == 2 + radius_high
    ordering = baselines["asserted_ordering"]
    assert ordering["statement"] == \
        "1 < 3.2035072879526181... < 2 + sqrt(8 sqrt(17) - 20)"
    assert ordering["asserted_exactly"] is True
    assert ordering["no_decimal_was_compared"] is True
    assert Fraction(ordering["floor"]) < Fraction(ordering["closure_interval"][0])
    assert Fraction(ordering["closure_interval"][1]) < Fraction(ordering["level_interval"][0])


def test_the_drift_control_failed_and_is_retained_rather_than_repaired():
    controls = load(EVIDENCE)["controls"]
    drift = controls["drift"]
    assert drift["outcome"] == "FAILED_TO_PRODUCE_THE_DECLARED_CHAIN"
    assert drift["retained"] is True
    assert drift["failed_to_discriminate"] is True
    assert drift["a_real_chain_that_closes_in_C1_but_drifts_later"] == "does not exist"
    assert drift["exact_drift_of_the_primary_chain"] == [ZERO] * 3
    assert drift["counterfactual_chain_seed"] == ["1/4", "1", "0"]
    assert all(row != ZERO for row in drift["counterfactual_chain_drifts"])
    assert "pointwise condition E(h) = h" in drift["detail"]
    assert controls["memory"]["outcome"] == "Discriminated"
    assert controls["memory"]["primary_keeps_the_memory"] is True
    assert controls["memory"]["atmospheric_loses_the_memory"] is True
    assert controls["placement"]["outcome"] == "Discriminated"
    assert controls["leakage"]["outcome"] == "Discriminated"
    assert controls["remainder"]["outcome"] == "Discriminated"
    assert controls["baselines"]["outcome"] == "Discriminated"
    assert [row["declared"] for row in controls.values()]
    assert controls["drift"]["declared"].startswith("Iterability")


def test_the_boundaries_are_retained_and_nothing_native_is_claimed():
    report = load(EVIDENCE)
    contract = load(CONTRACT)
    assert report["protected"] == contract["protected"]
    assert report["residual"] == contract["residual"]
    assert report["level"] == contract["level"]
    assert report["question"] == contract["question"]
    verification = report["verification_status"]
    assert verification["observational"] == "Unavailable"
    assert verification["reason"] == contract["verification_status"]["reason"]
    assert verification["data_authenticity_reservation"] == \
        contract["verification_status"]["data_authenticity_reservation"]
    assert "authenticity" in verification["data_authenticity_reservation"]
    assert verification["xue_study_data_used"] is False
    assert verification["future_chain"] is True
    claims = report["what_is_not_claimed"]
    assert claims["native_certificate"] is False
    assert claims["native_admission"] == "NotGranted"
    assert claims["stable_api_change"] is False
    assert claims["physical_claim"] is False
    assert claims["forecast"] is False
    assert claims["skill_claim"] is False
    assert claims["meteorological_data_used"] is False
    assert claims["xue_study_data_used"] is False
    assert claims["observational_verification"] == "Unavailable"
    assert claims["chain_is_future_and_unverified"] is True
    assert claims["reservoir_is_a_declared_model_not_a_claim_about_the_ocean"] is True
    assert claims["no_wind_gap_no_plateau_no_december_2026_no_january_2027"] is True
    assert claims["no_seal_no_transport_no_terminology_home"] is True
    assert claims["no_rust_source_or_lock_changed"] is True
    assert claims["no_note_or_contract_edited"] is True
    assert claims["no_claim_added_to_docs_claims_toml"] is True


def test_the_undecided_items_and_the_modelling_choices_are_declared():
    report = load(EVIDENCE)
    undecided = report["undecided"]
    assert len(undecided) == 4
    items = [row["item"] for row in undecided]
    assert any("drift in C2 or C3" in item for item in items)
    assert any("period-three" in item for item in items)
    assert any("freshwater" in item for item in items)
    assert any("forecast maps" in item for item in items)
    for row in undecided:
        assert row["reason"]
        assert row["retained_partial_result"] is not None
    choices = report["modelling_choices"]
    for key in ("annual_return", "closure_reading", "cumulative_reading", "seam_field",
                "chain_operator", "seam_state", "role_typing", "decision_to_technique",
                "calamity_counterparts", "end_block", "step_count", "fast_and_slow",
                "declared_reservoir", "declared_alternative", "sealing", "baselines",
                "exactness", "resource_limits"):
        assert choices[key], key
    assert "終養始" in choices["closure_reading"]
    assert "Q(w)" in choices["seam_field"]
    assert "declared model" in choices["declared_reservoir"]
    assert "not a claim about the ocean" in choices["declared_reservoir"]
    assert "exactly two extra steps" in choices["end_block"]
    assert "declared convention" in choices["fast_and_slow"]
    assert "one-sided bound" in choices["sealing"]
    assert "rlimit_portability" in choices["resource_limits"]
    assert "fractions.Fraction" in choices["exactness"]


def test_the_contract_still_carries_the_acceptance_and_control_clauses():
    contract = load(CONTRACT)
    assert contract["acceptance"].startswith("Every acceptance assertion is exact")
    assert "no floating-point value" in contract["acceptance"]
    assert contract["verification_status"]["observational"] == "Unavailable"
    assert contract["budgets"]["routes"] == 1
    assert contract["budgets"]["correction_replays"] == 1
    assert contract["budgets"]["child_processes"] == 0
    assert len(contract["controls"]) == 6
    assert any("Iterability" in row for row in contract["controls"])
    assert any("Leakage" in row for row in contract["controls"])
    assert "slow component must be conserved" in \
        contract["declared_reading"]["fast_and_slow_remainder"]


def test_the_claim_is_registered_once_and_binds_the_checker_and_the_note():
    """The record carries exactly one claim for this run, and it names the checker and the note.

    The checker was written while this test asserted the claim's absence, because a claim lives in
    `docs/claims.toml` and the checker's own run may not write there.  The parent session added the
    claim with the note; the assertion is inverted rather than dropped, so the binding stays
    checked.
    """
    claims = tomllib.loads((ROOT / "docs/claims.toml").read_text(encoding="utf-8"))["claim"]
    matches = [claim for claim in claims if claim["claim_id"] == CLAIM_ID]
    assert len(matches) == 1, "exactly one claim must be registered for this run"
    claim = matches[0]
    assert claim["status"] == "bounded-experiment"
    for symbol in ("three_cycle_chain_v1/calibration.py", "three_cycle_chain_v1/contract.json",
                   "three_cycle_chain_v1/evidence.json", "0238-three-chained-annual-cycles"):
        assert symbol in claim["code_symbol"], symbol
    assert "failed to discriminate" in claim["counterexample_boundary"].lower(), \
        "the boundary must retain the failed drift control"
    assert "NotGranted" in claim["counterexample_boundary"], "the boundary must record native admission"
    assert claim["forbidden_conflations"], "the claim must name its conflations"
