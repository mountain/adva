"""The stability round-trip experiment must keep the asymmetry it reports.

Research 0169 states that the forward direction is injective in the object and
many-to-one in the stability parameter. This test holds both halves of that: the
injectivity assertion is in the run itself, and here the retained evidence must
still show a non-degenerate parameter witness, a chamber larger than one, a wall
inside the grid, and an exact re-run.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/hns_stability_chamber_roundtrip"
CHECKER = HERE / "calibration.py"
EVIDENCE = HERE / "evidence.json"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_the_retained_run_reports_the_asymmetry():
    report = load(EVIDENCE)
    assert report["status"] == "ExternalExactPass"
    assert report["native_status"] == "NotRun"

    # the object direction: injective, and asserted by the run over every class
    assert report["object_map_is_injective"] is True
    assert report["distinct_iso_classes"] >= 2

    # the parameter direction: many-to-one, and the witness is not degenerate
    witness = report["parameter_forgetting_witness"]
    assert witness is not None
    assert witness["nondegenerate"] is True
    assert len(witness["parameters"]) > 1, witness
    assert report["parameter_witness_is_nondegenerate"] is True
    assert report["parameter_witness_count"] > 0

    # a chamber, and a wall inside the declared grid
    partition = report["sample_chamber_partition"]
    assert partition is not None
    assert any(len(chamber) > 1 for chamber in partition["chambers"]), partition
    assert report["wall_count"] > 0
    assert report["chamber_partition_count"] > 0


def test_the_run_stays_inside_its_contract():
    report = load(EVIDENCE)
    contract = load(HERE / "contract.json")
    assert report["counts"]["assertions"] <= contract["budget"]["max_assertions"]
    assert report["counts"]["carriers"] == report["distinct_iso_classes"]
    # one representative per isomorphism class, so carriers cannot exceed the
    # number of dimension pairs the fields and ambient dimensions allow
    assert report["counts"]["carriers"] == 18


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    output = tmp_path / "fresh.json"
    completed = subprocess.run(
        [sys.executable, str(CHECKER), str(output)],
        capture_output=True, text=True, timeout=300, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert load(output) == load(EVIDENCE)


def test_the_claim_keeps_the_two_collapses_forbidden():
    """The ladder's two forbidden collapses must survive in the registry."""
    import tomllib

    claims = tomllib.loads((ROOT / "docs/claims.toml").read_text(encoding="utf-8"))["claim"]
    match = [c for c in claims
             if c["claim_id"] == "adva.bounded-experiment.hns-stability-chamber-roundtrip.v0"]
    assert len(match) == 1
    forbidden = " | ".join(match[0]["forbidden_conflations"])
    assert "Hermitian-Yang-Mills equation with complex Monge-Ampere" in forbidden
    assert "Slope stability with K-stability" in forbidden
    assert "metric mirror symmetry" in forbidden
    assert "Arakelov" in match[0]["counterexample_boundary"]
