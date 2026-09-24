"""Bounded Lorentzian-reading calibration; external evidence, no admission, no physical claim.

The assertions here are about what the retained checker decided by exact
computation on declared rational matrices. They are not claims about any process.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/lorentzian_frame_reading"
CHECKER = HERE / "checker.py"
CONTRACT = HERE / "contract.json"
EVIDENCE = HERE / "evidence.json"
NOTE = ROOT / "docs/research/0227-what-the-involution-route-costs.md"
CLAIM_ID = "adva.bounded-experiment.lorentzian-frame-reading.v0"
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


def test_the_frame_reproduces_its_own_identities_first():
    s = section("S0_frame_instance")
    assert s["process"] == "chain-and-single"
    assert s["cuts"] == 6 and s["carrier_dimension"] == 12
    assert s["d_max"] == "3" and s["h0_scale"] == "L/6"
    assert s["checked_degree"] == 12
    assert s["J_squared_is_minus_identity"] is True
    assert s["H_commutes_with_J"] is True
    assert s["A_is_skew_for_the_identity_metric"] is True
    assert s["wick_identity_(-J)^k_A^k_equals_(-H)^k_mismatched_degrees"] == []
    assert s["invariance_identity_U_transpose_G_U_equals_G_degrees_with_nonzero_coefficient"] == []


def test_the_sign_in_the_exponent_is_the_sign_of_the_structure_square():
    s = section("S1_sign_lemma")
    assert "sigma^k H^k" in s["identity"]
    assert len(s["instances"]) == 2
    complex_structure, involution = s["instances"]
    assert complex_structure["sigma"] == -1
    assert involution["sigma"] == 1
    for row in s["instances"]:
        assert row["squares_to_sigma_identity"] is True
        assert row["commutes_with_H"] is True
        assert row["mismatched_degrees"] == []
    # at sigma = -1 the odd coefficients are minus the power of H
    for entry in complex_structure["first_degrees"]:
        expected_plus = entry["k"] % 2 == 0
        assert entry["equals_plus_H_power_k"] is expected_plus
        assert entry["equals_minus_one_power_k_times_H_power_k"] is True
    # at sigma = +1 every coefficient is plus the power of H
    for entry in involution["first_degrees"]:
        assert entry["equals_plus_H_power_k"] is True
        assert entry["equals_minus_one_power_k_times_H_power_k"] is (entry["k"] % 2 == 0)
    assert "exponential of minus H" in s["reading_at_sigma_minus_one"]
    assert "time reverse" in s["reading_at_sigma_plus_one"]
    assert s["the_sign_in_the_exponent_is_the_sign_of_the_structure_square"] is True


def test_the_lorentzian_carrier_has_the_signature_but_not_the_skewness():
    s = section("S2_lorentzian_carrier")
    assert s["instance"] == {"cuts": 2, "carrier_dimension": 4,
                             "d_max": "1", "h0_scale": "L/2"}
    assert s["lorentzian_signature"] == [3, 1]
    assert s["involution_squares_to_identity"] is True
    assert s["involution_is_compatible_with_the_metric"] is True
    assert s["complex_structure_is_compatible_with_the_metric"] is False
    assert s["A_K_is_skew"] is False
    assert s["residual_A_K_transpose_G_plus_G_A_K"] == [
        ["-1", "1", "0", "0"],
        ["1", "-1", "0", "0"],
        ["0", "0", "1", "0"],
        ["0", "0", "0", "-1"],
    ]
    assert s["residual_absolute_sum"] == "6"
    assert s["skewness_condition_is_H_anticommuting_with_G_K"] is True
    assert s["H_anticommutes_with_G_K"] is False


def test_no_nondegenerate_metric_satisfies_both_obligations():
    s = section("S3_impossibility")
    assert s["no_nondegenerate_metric_satisfies_both"] is True
    assert len(s["instances"]) == 2
    for row in s["instances"]:
        assert row["solution_dimension"] == 2
        assert row["basis_determinants"] == ["0", "0"]
        assert row["determinants_at_the_sample_values"] == ["0", "0", "0", "0", "0"]
        assert row["every_element_of_the_solution_space_is_degenerate"] is True
    four, twelve = s["instances"]
    assert four["carrier_dimension"] == 4 and four["unknowns"] == 10 and four["rank"] == 8
    assert twelve["carrier_dimension"] == 12 and twelve["unknowns"] == 78
    assert twelve["rank"] == 76
    assert "graph Laplacian" in s["structural_reason"]
    assert "elementary argument" in s["bounded_to"]


def test_the_refusals_are_declared_and_retained():
    s = section("S4_refusals")
    assert s["refusal_count"] >= 5
    assert any("thermodynamics" in item for item in s["refusals"])
    assert any("Kerr" in item for item in s["refusals"])


def test_the_contract_states_its_protected_boundaries():
    contract = load(CONTRACT)
    protected = " ".join(contract["protected"])
    for phrase in (
        "No physical claim is made anywhere in this experiment",
        "the general statement about connected cut graphs is recorded as an elementary argument",
        "What is excluded is one declared pair of obligations",
        "This experiment is not connected to the Kerr experiment",
        "Native admission is NotGranted",
    ):
        assert phrase in protected, phrase
    assert contract["level"].startswith("External exact finite rational linear algebra")
    assert contract["base_commit"] == "47f080c82bad7771ba50e33e67be87d1b3e38f24"
    assert contract["objects"]["checked_degree"] == 12
    assert contract["objects"]["degeneracy_witness"]["sample_values"] == [0, 1, 2, 3, 4]
    assert NOTE.is_file()


def test_the_note_keeps_the_boundary_and_claims_no_process():
    text = NOTE.read_text(encoding="utf-8")
    assert "Residual" in text
    flat = " ".join(text.split())
    for phrase in ("no physical claim",
                   "the sign in the exponent is exactly the sign of the structure's square",
                   "No nondegenerate metric",
                   "not connected to the Kerr experiment"):
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
    assert any("heat" in item for item in claim["forbidden_conflations"])
    for symbol in claim["code_symbol"].split("; "):
        assert (ROOT / symbol).is_file(), symbol
    assert claim["counterexample_boundary"].startswith("No physical")
