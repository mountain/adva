"""Replay check for the HNS wall-localization round.

The retained evidence is not trusted: the calibration is re-run on a temporary
copy and every non-timing field must match. The wall set, the fibre correction
and the seam refusal are asserted separately, so a green run states exactly what
it checked.
"""

import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/hns_wall_localization"
EVIDENCE = EXPERIMENT / "evidence.json"
SIBLING = ROOT / "experiments/hns_object_forgetting/evidence.json"
NOTE = ROOT / "docs/research/0169-arakelov-stability-monge-ampere-mirror-ladder.md"
CLAIMS = ROOT / "docs/claims.toml"
SIBLING_SHA = "09280cf0cd5e3bdd17b32200f0d7121d1bbe31a8eafec6a4f4b85912fd59d550"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    copied = tmp_path / "hns_wall_localization"
    shutil.copytree(EXPERIMENT, copied)
    shutil.copytree(EXPERIMENT.parent / "hns_object_forgetting", tmp_path / "hns_object_forgetting")
    completed = subprocess.run(
        [sys.executable, str(copied / "calibration.py")],
        cwd=copied, capture_output=True, text=True, timeout=300, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    fresh = load(copied / "evidence.json")
    retained = load(EVIDENCE)
    fresh.pop("cost", None)
    retained.pop("cost", None)
    assert fresh == retained
    assert retained["status"] == "ExternalExactPass"
    assert all(retained["checks"].values())


def test_the_imported_model_is_the_frozen_sibling():
    report = load(EVIDENCE)
    interface = report["interface"]
    assert interface["sibling_evidence_sha256"] == SIBLING_SHA
    assert interface["sibling_evidence_unchanged"]
    assert interface["agrees"]
    sibling = load(SIBLING)
    assert interface["objects_rerun"] == sibling["counts"]["objects"]
    assert interface["filtrations_rerun_including_the_regression_block"] == sibling["counts"]["filtrations"]
    assert interface["collisions_rerun"] == sibling["collision_totals"]["dims_and_slopes"]["colliding_shadows"]


def test_the_wall_set_is_one_line():
    walls = load(EVIDENCE)["walls"]
    assert walls["primitive_wall_directions"] == [[-1, 1], [1, -1]]
    assert walls["slope_equality_identity_mismatches"] == 0
    assert walls["identically_tied_pair_count"] == 7
    assert walls["genuine_wall_pair_count"] == 59
    assert len(walls["identity_checked_over"]) == 17


def test_the_fibre_is_finer_than_a_cell():
    fibre = load(EVIDENCE)["fibre"]
    assert fibre["class_parameter_pairs"] == 5168
    assert fibre["same_cell_implies_same_filtration_type"]
    assert fibre["same_cell_different_graded_data_total"] == 2080
    assert fibre["same_cell_different_graded_data"]
    assert fibre["different_cell_same_graded_data_total"] == 92
    assert fibre["every_different_cell_shared_key_is_a_single_piece"]
    assert fibre["criterion_mismatches"] == []


def test_the_criterion_was_validated_before_the_seam_was_judged():
    validation = load(EVIDENCE)["criterion_validation"]
    assert validation["square_2d"]["verdict"] == "Pass"
    assert validation["reflexive_triangle_2d"]["verdict"] == "Pass"
    assert validation["twice_square_2d"]["verdict"] == "Pass"
    assert validation["halves_triangle_2d"]["verdict"] == "Pass"
    assert validation["halves_triangle_2d"]["minimal_witness_lattice"]["all_vertices_integral"] is False
    assert validation["square_2d"]["minimal_witness_lattice"]["all_vertices_integral"] is True
    assert validation["thirds_triangle_2d"]["verdict"] == "Fail"
    assert validation["thirds_triangle_2d"]["witness"]["pairing"] == "-2/3"


def test_no_seam_candidate_reached_the_criterion_as_a_canonical_polytope():
    candidates = load(EVIDENCE)["s1_candidates"]
    assert "RefusedAtHypothesis" in candidates["canonical_half_plane_intersection"]["verdict"]
    assert "RefusedAtHypothesis" in candidates["hull_of_wall_normals"]["verdict"]
    assert "RefusedAtHypothesis" in candidates["weight_polytope_of_the_declared_range"]["verdict"]
    grid = candidates["hull_of_the_declared_grid"]
    assert grid["criterion_result"]["verdict"] == "Fail"
    assert grid["criterion_result"]["witness"]["pairing"] == "1/5"
    assert "non-canonical" in grid["verdict"]


def test_the_reading_is_visible_in_the_note_and_the_registry():
    note = NOTE.read_text(encoding="utf-8")
    assert "## 9. Where the walls are, and what the backward fibre really is" in note
    assert "Section 4's chamber reading is refuted" in note
    assert "Seam S1 is refused, with reasons." in note
    claims = tomllib.loads(CLAIMS.read_text(encoding="utf-8"))["claim"]
    match = [c for c in claims if c["claim_id"] == "adva.bounded-experiment.hns-wall-localization.v0"]
    assert len(match) == 1
    assert match[0]["dependencies"] == ["adva.bounded-experiment.hns-extension-residual.v0"]
    forbidden = " | ".join(match[0]["forbidden_conflations"])
    assert "A chamber of the parameter grid with a chamber of the wall arrangement" in forbidden
    assert "Refusing four constructions with proving the seam cannot be bridged" in forbidden
    boundary = match[0]["counterexample_boundary"]
    assert "scopes rather than deletes the earlier reading" in boundary
    assert "rank-two dimension-vector space" in boundary
