"""Bounded Kerr calibration; external evidence, no admission and no physical claim.

The assertions here are about what the retained checker decided by exact symbolic
computation. They are not claims about any real object.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/kerr_vacuum"
CHECKER = HERE / "checker.py"
CONTRACT = HERE / "contract.json"
EVIDENCE = HERE / "evidence.json"
NOTE = ROOT / "docs/research/0226-the-kerr-line-element-is-vacuum.md"
CLAIM_ID = "adva.bounded-experiment.kerr-vacuum.v0"
TIMING_KEYS = ("installed_limits",)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def payload(report):
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


def test_the_machinery_is_calibrated_before_it_is_trusted():
    s = section("S0_calibration")
    assert s["time_phi_block_determinant_is_minus_delta_sin_squared"] is True
    assert s["g_times_inverse_is_the_identity"] is True
    assert s["mismatched_product_rows"] == []
    assert s["calibration_pairs"] == 14
    assert s["declared_tolerance"] == "1e-6"
    assert float(s["worst_relative_disagreement"]) < 1e-6
    assert "only floating-point arithmetic" in s["note"]


def test_every_declared_parameter_pair_is_vacuum():
    s = section("S1_vacuum")
    assert s["every_pair_is_vacuum"] is True
    assert s["pairs_examined"] == 5
    labels = [row["label"] for row in s["parameter_pairs"]]
    assert labels == ["Schwarzschild reduction", "slowly spinning", "the declared black hole",
                      "no horizon, A above M", "a second mass"]
    for row in s["parameter_pairs"]:
        assert row["ricci_components"] == 10
        assert row["nonvanishing_ricci_components"] == {}
        assert row["every_ricci_component_vanishes"] is True
    # the spin above the mass is still vacuum, which is a statement about the metric only
    above = [row for row in s["parameter_pairs"] if row["spin_above_mass"]]
    assert len(above) == 1 and above[0]["spin"] == "7/5"
    # Schwarzschild is the small case: fewer symbols and fewer Riemann components
    schwarzschild = s["parameter_pairs"][0]
    assert schwarzschild["christoffel_symbols"] == 9
    assert schwarzschild["riemann_components_with_c_less_than_d"] == 12
    for row in s["parameter_pairs"][1:]:
        assert row["christoffel_symbols"] == 20
        assert row["riemann_components_with_c_less_than_d"] == 44


def test_the_kretschmann_scalar_matches_the_closed_form_and_the_known_limit():
    s = section("S2_kretschmann")
    for row in s["parameter_pairs"]:
        assert row["equals_the_declared_closed_form"] is True, row["label"]
        assert row["kretschmann_denominators"]["delta"] >= 0
    schwarzschild = s["parameter_pairs"][0]
    assert schwarzschild["schwarzschild_reduction_to_48_M_squared_over_r_sixth"] is True
    for row in s["parameter_pairs"][1:]:
        assert row["schwarzschild_reduction_to_48_M_squared_over_r_sixth"] is None
        assert row["kretschmann_numerator_terms"] > 800
    assert s["vanishing_locus"][
        "kretschmann_numerator_vanishes_exactly_on_r_squared_equal_A_squared_c_squared"] is True


def test_the_signature_has_exactly_one_negative_direction_everywhere_declared():
    s = section("S3_signature")
    assert s["black_hole"] == {"mass": "1", "spin": "3/5"}
    assert s["every_declared_point_has_exactly_one_negative_direction"] is True
    assert len(s["points"]) == 6
    for row in s["points"]:
        assert row["signature"] == [3, 1], row["label"]
        assert row["exactly_one_negative_direction"] is True
    # g_rr changes sign and the signature does not
    assert s["inside_the_horizon_still_has_one_negative_direction"] is True
    assert s["inside_the_ergosphere_still_has_one_negative_direction"] is True
    inside = [row for row in s["points"] if row["g_rr_negative"]]
    assert len(inside) == 3
    ergo = [row for row in s["points"] if row["g_tt_positive"]]
    assert len(ergo) == 4
    assert "degenerate" in s["degeneracy"]


def test_horizons_ergosphere_area_and_smarr_hold_exactly():
    s = section("S4_horizons")
    assert s["mass"] == "1" and s["spin"] == "3/5"
    assert s["discriminant"] == "16/25"
    assert s["delta_vanishes_at_both_radii"] is True
    assert s["r_plus_squared_plus_A_squared_is_2_M_r_plus"] is True
    assert s["horizon_area_equals_four_pi_r_plus_squared_plus_A_squared"] is True
    assert s["horizon_area_equals_eight_pi_M_r_plus"] is True
    assert s["smarr_identity_M_equals_kappa_A_over_4pi_plus_two_Omega_J"] is True
    assert s["extremality_condition_is_A_squared_at_most_M_squared"] is True
    assert s["pairs_with_spin_above_mass"] == ["7/5"]
    assert s["the_pair_above_M_has_no_real_horizon"] is True
    assert len(s["ergosphere"]) == 4
    for row in s["ergosphere"]:
        assert row["g_tt_at_that_radius_is_zero"] is True
    assert "pi is a symbol" in s["pi_convention"]


def test_the_refusals_are_declared_and_retained():
    s = section("S5_refusals")
    assert s["refusal_count"] >= 5
    assert any("observation" in item for item in s["refusals"])
    assert any("frame" in item for item in s["refusals"])


def test_the_contract_states_its_protected_boundaries():
    contract = load(CONTRACT)
    protected = " ".join(contract["protected"])
    for phrase in (
        "No physical claim is made anywhere in this experiment",
        "The Einstein equations are not derived here",
        "This experiment is not connected to the {e, i, iota} frame",
        "Coordinate singularities are not physical singularities",
        "Native admission is NotGranted",
    ):
        assert phrase in protected, phrase
    assert contract["level"].startswith("External exact symbolic")
    assert contract["base_commit"] == "df793aad6ef607c832161bcd12769de373bf5b39"
    assert len(contract["objects"]["declared_parameter_pairs"]) == 5
    assert len(contract["objects"]["signature_points"]) == 6
    assert NOTE.is_file()


def test_the_note_keeps_the_boundary_and_claims_no_observation():
    text = NOTE.read_text(encoding="utf-8")
    assert "Residual" in text
    flat = " ".join(text.split())
    for phrase in ("no physical claim",
                   "Einstein equations are not derived",
                   "is not connected to the frame",
                   "48 M squared over r to the sixth"):
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
    assert any("observation" in item for item in claim["forbidden_conflations"])
    for symbol in claim["code_symbol"].split("; "):
        assert (ROOT / symbol).is_file(), symbol
    assert claim["counterexample_boundary"].startswith("No physical")
