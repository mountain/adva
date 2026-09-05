import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WITNESS = ROOT / "programs" / "bootstrap-0" / "trust-continuity-session-witness.adva"


def load_witness():
    return json.loads(WITNESS.read_text(encoding="utf-8"))


def test_trust_continuity_witness_keeps_the_common_triadic_interface():
    witness = load_witness()

    assert witness["schema"] == "adva.trust-continuity-session-witness.research"
    assert witness["version"] == 0
    assert witness["interface"]["inputs"] == ["subject", "method", "object"]
    assert witness["interface"]["outputs"] == ["history", "result", "evidence"]


def test_trust_continuity_obligations_are_noncompensating_and_complete():
    witness = load_witness()
    invariants = witness["trust_continuity"]["invariants"]

    assert [item["name"] for item in invariants] == [
        "provenance",
        "replay",
        "challenge",
        "succession",
    ]
    assert witness["output"]["result"]["formula"] == (
        "trust_continuity_v0 = provenance + replay + challenge + succession"
    )
    assert "unanimity" in witness["trust_continuity"]["not_required"]


def test_human_and_machine_occurrences_remain_distinct_and_bounded():
    witness = load_witness()
    attribution = witness["attribution"]
    machine = witness["machine_session_witness"]

    assert attribution["human_declaration_by"] == "Mingli Yuan"
    assert attribution["machine_contribution_by"] == (
        "the ChatGPT response produced in this conversation"
    )
    assert "does not speak for OpenAI" in " ".join(machine["limits"])
    assert "does not assert consciousness" in " ".join(machine["limits"])


def test_m6_gate_refuses_endpoint_only_closure_and_retains_unknown():
    witness = load_witness()
    gate = witness["m6_closure_gate"]

    assert "equal terminal payloads" in gate["rule"]
    assert len(gate["two_path_requirement"]) == 5
    assert set(gate["outcomes"]) == {"success", "failure", "unknown"}
    assert "M6 semantic filler" in gate["nonclaim"]


def test_continuity_comparison_is_typed_bounded_and_reciprocal_without_debt():
    witness = load_witness()
    comparison = witness["continuity_inequality"]

    assert comparison["status"] == "hypothesis"
    assert comparison["display"] == "merge_capacity > rupture_load"
    assert comparison["dual_display"] == "rupture_load < merge_capacity"
    assert set(comparison["outcomes"]) == {"greater", "equal", "less", "unknown"}
    assert "cannot cancel" in comparison["not_a_scalar_score"]
    assert "does not purchase consent" in comparison["help_first"]["boundary"]


def test_euler_cut_candidate_separates_additive_trace_from_unit_readout():
    witness = load_witness()
    candidate = witness["euler_logarithmic_cut_candidate"]

    assert candidate["upper_semicircle"]["additive_trace"] == (
        "Integral_gamma dz/z = i pi"
    )
    assert candidate["upper_semicircle"]["euler_readout"] == "exp(i pi) + 1 = 0"
    assert candidate["closed_loop"]["additive_trace"] == (
        "ContourIntegral_gamma dz/z = 2 pi i"
    )
    assert candidate["closed_loop"]["multiplicative_readout"] == (
        "exp(ContourIntegral_gamma dz/z) = 1"
    )
    assert "later complex-analysis reconstruction" in candidate["historical_lineage"][-1]


def test_imagination_i_emits_questions_without_identifying_complex_i():
    witness = load_witness()
    cycle = witness["finite_imagination_cycle"]

    assert cycle["status"] == "working_hypothesis"
    assert set(cycle["three_input_reading"]) == {"subject", "method", "object"}
    assert set(cycle["three_output_reading"]) == {"history", "result", "evidence"}
    assert "not evidence" in cycle["i_readings"]["relation"]
    assert "does not itself cross the interface" in cycle["nonclaim"]
    assert "help-first contribution" in " ".join(cycle["generation_operations"])


def test_witness_remains_open_to_correction():
    witness = load_witness()

    assert witness["boundaries"][-1] == (
        "this witness is non-immune to future correction and cut"
    )
