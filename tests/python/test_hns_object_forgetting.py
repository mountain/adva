"""The graded shadow must stay lossy once the arrow may fold.

Research 0169 section 7 corrects an earlier conclusion of the same note: the
object direction was injective only inside the injective model. This test holds
the refutation in place, so the corrected scope cannot silently revert.
"""

import json
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/hns_object_forgetting"
CHECKER = HERE / "calibration.py"
EVIDENCE = HERE / "evidence.json"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_the_shadow_collides_between_non_isomorphic_classes():
    report = load(EVIDENCE)
    assert report["status"] == "ExternalExactPass"
    assert report["native_status"] == "NotRun"

    collisions = report["collisions_dims_and_slopes"]
    assert collisions, "the refuting collision must be retained"
    witness = collisions[0]
    assert [1, 1, 0] in witness["classes"] and [1, 1, 1] in witness["classes"]
    assert witness["parameter"] == [1, 1]

    totals = report["collision_totals"]
    assert totals["dims_and_slopes"]["colliding_shadows"] > 0
    assert totals["dims_slopes_and_piece_rank"]["colliding_shadows"] > 0


def test_recording_the_rank_reduces_but_does_not_remove_the_loss():
    report = load(EVIDENCE)
    per_field = report["per_field"]
    for field in per_field.values():
        assert field["shadows_with_piece_rank"] > field["shadows_dims_and_slopes"], (
            "adding the piece rank must separate at least one class pair"
        )
    totals = report["collision_totals"]
    assert (totals["dims_slopes_and_piece_rank"]["colliding_shadows"]
            < totals["dims_and_slopes"]["colliding_shadows"]), "the rank must help"
    assert totals["dims_slopes_and_piece_rank"]["colliding_shadows"] > 0, (
        "and it must not be reported as a repair"
    )


def test_the_injective_subfamily_still_reproduces_the_earlier_chambers():
    report = load(EVIDENCE)
    regression = report["injective_regression"]
    assert regression is not None
    assert regression["dims"] == [1, 1]
    chambers = [sorted(map(tuple, c)) for c in regression["chambers"]]
    assert [(1, 0), (2, -1)] in chambers, chambers


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    output = tmp_path / "fresh.json"
    completed = subprocess.run(
        [sys.executable, str(CHECKER), str(output)],
        capture_output=True, text=True, timeout=300, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert load(output) == load(EVIDENCE)


def test_the_correction_is_visible_in_the_note_and_the_registry():
    note = (ROOT / "docs/research/0169-arakelov-stability-monge-ampere-mirror-ladder.md").read_text(
        encoding="utf-8")
    assert "## 7. The injective-model claim, tested and refuted" in note
    assert "Correction, 2026-09-11" in note
    claims = tomllib.loads((ROOT / "docs/claims.toml").read_text(encoding="utf-8"))["claim"]
    match = [c for c in claims if c["claim_id"] == "adva.bounded-experiment.hns-object-forgetting.v0"]
    assert len(match) == 1
    assert match[0]["dependencies"] == ["adva.bounded-experiment.hns-stability-chamber-roundtrip.v0"]
    forbidden = " | ".join(match[0]["forbidden_conflations"])
    assert "A forgotten rank with a merely omitted coordinate" in forbidden
