import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_pending_effect_witness_evidence_and_claim_are_bound():
    execution = json.loads(
        (ROOT / "experiments/pending_effect_witness/evidence/attempt-1/execution.json").read_text()
    )
    assert execution["status"] == "Passed"
    assert execution["assertions"] == 145
    assert execution["tool_processes"] == 10
    assert execution["target_processes"] == 0
    assert execution["work_units"] == 6194
    outcomes = [case["receipt"]["outcome"] for case in execution["cases"]]
    assert outcomes.count("EffectWitnessVerified") == 2
    assert outcomes.count("NoEffectWitnessVerified") == 1
    assert outcomes.count("UnknownConsumptionState") == 3
    assert outcomes.count("InvalidContext") == 2
    assert outcomes.count("InvalidEvidence") == 2
    for case in execution["cases"]:
        receipt = case["receipt"]
        for flag in (
            "effect_authority",
            "retry_authority",
            "refund_authority",
            "mutation_authority",
            "native_authority",
            "free_authority",
        ):
            assert receipt[flag] is False

    claims = (ROOT / "docs/claims.toml").read_text()
    assert claims.count('claim_id = "adva.bounded-experiment.pending-effect-witness.v0"') == 1
    assert "docs/research/0249-pending-effect-and-bounded-no-effect-witnesses.md" in claims


def test_wrapper_failure_precedes_the_only_experiment_execution():
    failure = json.loads(
        (ROOT / "experiments/pending_effect_witness/evidence/prior-wrapper-failure.json").read_text()
    )
    assert failure["classification"] == "PreExecutionEnvironmentFailure"
    assert failure["receiver_processes"] == 0
    assert failure["target_processes"] == 0
    assert failure["output_created"] is False
    assert failure["implementation_correction_replay"] is False
