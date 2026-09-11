"""The residual of the graded shadow is an extension class, not a coordinate.

Research 0169 section 8 shows that the key used in section 7 was already the
strongest piece-level key that exists, exhibits two objects whose graded pieces
agree as objects, and computes Ext^1 by two independent routes to name what
distinguishes them. This test holds that reading in place: the loss must not be
described as an omitted coordinate, and the strongest key must not be presented
as a repair.
"""

import json
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/hns_extension_residual"
CHECKER = HERE / "calibration.py"
EVIDENCE = HERE / "evidence.json"
SIBLING = ROOT / "experiments/hns_object_forgetting/evidence.json"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_the_strongest_piece_level_key_still_collides():
    report = load(EVIDENCE)
    assert report["status"] == "ExternalExactPass"
    assert report["native_status"] == "NotRun"
    assert report["collision_count"] > 0
    for collision in report["collisions_under_the_strongest_key"]:
        assert collision["all_classes_share_one_dimension_vector"] is True
        assert collision["collision_is_the_whole_class_set"] is True
        assert (len(collision["gluing_ranks"])
                == collision["predicted_number_of_gluing_ranks"])


def test_the_witness_has_identical_pieces_as_objects():
    report = load(EVIDENCE)
    witnesses = report["witnesses_with_identical_piece_objects"]
    assert witnesses, "the witness with identical piece objects must be retained"
    witness = witnesses[0]
    pieces = witness["pieces_of_the_rank_one_object"]
    assert [pc["dims"] for pc in pieces] == [[0, 1], [1, 0]]
    assert [pc["piece_rank"] for pc in pieces] == [0, 0]
    assert [pc["iso_type"] for pc in pieces] == [[0, 1, 0], [1, 0, 0]]
    assert witness["rank_zero_object"] != witness["rank_one_object"]


def test_the_difference_is_a_non_split_extension():
    report = load(EVIDENCE)
    for field, table in report["ext1_tables"].items():
        row = [r for r in table
               if r["quotient"] == [1, 0, 0] and r["subobject"] == [0, 1, 0]]
        assert len(row) == 1, field
        assert row[0]["ext1_dim"] == 1
        assert row[0]["split_only"] is False
        assert [1, 1, 0] in row[0]["middle_terms"]
        assert [1, 1, 1] in row[0]["middle_terms"]
        reversed_row = [r for r in table
                        if r["quotient"] == [0, 1, 0] and r["subobject"] == [1, 0, 0]]
        assert len(reversed_row) == 1
        assert reversed_row[0]["ext1_dim"] == 0
        assert reversed_row[0]["middle_terms"] == [[1, 1, 0]], (
            "the reversed orientation has only the split extension"
        )


def test_the_two_keys_agree_with_the_sibling_run():
    report = load(EVIDENCE)
    sibling = load(SIBLING)
    assert report["cross_experiment"]["sibling_colliding_shadows"] == report["collision_count"]
    for field, entry in report["per_field"].items():
        assert entry["strongest_key_shadows"] == sibling["per_field"][field]["shadows_with_piece_rank"]


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    output = tmp_path / "fresh.json"
    completed = subprocess.run(
        [sys.executable, str(CHECKER), str(output)],
        capture_output=True, text=True, timeout=300, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert load(output) == load(EVIDENCE)


def test_the_reading_is_visible_in_the_note_and_the_registry():
    note = (ROOT / "docs/research/0169-arakelov-stability-monge-ampere-mirror-ladder.md").read_text(
        encoding="utf-8")
    assert "## 8. Is the forgotten object an extension class, or a coordinate?" in note
    assert "the strongest piece-level key that exists" in note
    claims = tomllib.loads((ROOT / "docs/claims.toml").read_text(encoding="utf-8"))["claim"]
    match = [c for c in claims
             if c["claim_id"] == "adva.bounded-experiment.hns-extension-residual.v0"]
    assert len(match) == 1
    assert match[0]["dependencies"] == ["adva.bounded-experiment.hns-object-forgetting.v0"]
    forbidden = " | ".join(match[0]["forbidden_conflations"])
    assert "A forgotten rank with a merely omitted coordinate" in forbidden
    assert "An extension class in a finite hereditary model with an extension class in a surface" in forbidden
