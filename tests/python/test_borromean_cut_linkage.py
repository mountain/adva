"""Replay check for the cut-linkage round.

Standard library only. The checker is replayed on a copy because it writes its evidence
beside itself, and the frozen outcomes are asserted rather than described.
"""

import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/borromean_cut_linkage"
EVIDENCE = EXPERIMENT / "evidence.json"
NOTE = ROOT / "docs/research/0187-cut-linkage-after-cutting.md"
CLAIMS = ROOT / "docs/claims.toml"
RETAINED = ROOT / "experiments/golden_ratio/calibration.py"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def replay(tmp_path):
    """Replay on a copy that keeps the layout the checker reads.

    The checker reads the retained golden-ratio calibration and evidence through paths
    relative to the repository root, so the copy has to carry them too.
    """
    copied = tmp_path / "experiments/borromean_cut_linkage"
    shutil.copytree(EXPERIMENT, copied)
    retained = tmp_path / "experiments/golden_ratio"
    retained.mkdir(parents=True)
    for name in ("calibration.py", "evidence.json"):
        shutil.copyfile(ROOT / "experiments/golden_ratio" / name, retained / name)
    completed = subprocess.run(
        [sys.executable, str(copied / "calibration.py")],
        cwd=tmp_path, capture_output=True, text=True, timeout=600, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return load(copied / "evidence.json")


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    fresh = replay(tmp_path)
    assert fresh["status"] == "ExternalExactPass"
    assert all(fresh["checks"].values())
    retained = load(EVIDENCE)
    for key in ("self_computed", "controls_built_here", "the_contrast",
                "imported_not_verified_here", "what_would_decide_the_unknown"):
        assert fresh[key] == retained[key], key


def test_the_pairwise_linking_numbers_recompute_to_zero():
    linking = load(EVIDENCE)["self_computed"]["linking_numbers"]
    assert set(linking) == {"z0|x0", "z0|y0", "x0|y0"}
    for pair, entry in linking.items():
        assert entry["computed"] == 0, pair
        assert entry["computed_reverse"] == 0, pair
        assert entry["they_agree"], pair
        assert entry["retained_projection_crossings"]["forward_sum"] == 0
    source = load(EVIDENCE)["self_computed"]["source"]
    assert source["path"] == "experiments/golden_ratio/calibration.py"
    assert len(source["sha256"]) == 64
    assert source["sha256"] == __import__("hashlib").sha256(RETAINED.read_bytes()).hexdigest()


def test_the_triple_intersection_sign_agrees_with_the_retained_record():
    triple = load(EVIDENCE)["self_computed"]["triple_intersection"]
    assert triple["cyclic_orders_share_one_sign"]
    assert triple["cyclic_sign"] == 1
    assert set(triple["signed_sums_by_order"]) == {
        "z0,x0,y0", "x0,y0,z0", "y0,z0,x0", "z0,y0,x0", "x0,z0,y0", "y0,x0,z0"}
    for order, recorded in triple["retained_recorded"].items():
        assert recorded["signed_sum"] == 1, order


def test_every_cut_is_unknown_and_says_why():
    cuts = load(EVIDENCE)["self_computed"]["cuts"]
    assert set(cuts) == {"z0", "x0", "y0"}
    for cut, entry in cuts.items():
        assert entry["surviving_linking_number"] == 0, cut
        assert entry["linking_number_decides_inseparability"] is False, cut
        assert entry["outcome"] == "Unknown", cut
        assert "cannot decide" in entry["reason"], cut
        assert "undefined" in entry["milnor_invariant_after_the_cut"], cut
        verdicts = {test["verdict"] for test in entry["separation_tests"]}
        assert verdicts == {"inconclusive"}, cut


def test_the_linked_control_survives_the_cut_and_the_split_control_is_decided():
    controls = load(EVIDENCE)["controls_built_here"]
    linked = controls["hopf_style_linked_pair"]
    assert linked["linking_one_way"] == -1
    assert linked["linking_the_other_way"] == -1
    assert len(linked["crossings_inside_the_disk"]) == 1
    assert "stays inseparable" in linked["outcome"]
    bystander = controls["bystander"]
    assert bystander["linking_to_the_pair"] == [0, 0]
    split = controls["split_pair"]
    assert split["linking"] == 0
    assert any(test["decisive"] for test in split["separation_tests"])
    assert "separating plane" in split["outcome"]


def test_the_contrast_between_pairwise_and_triple_linking_is_recorded():
    contrast = load(EVIDENCE)["the_contrast"]
    assert contrast["pairwise_linking_under_a_cut"].startswith("survives")
    assert "removes its" in contrast["triple_linking_under_a_cut"]
    assert "Unknown rather than a guess" in contrast["consequence"]


def test_the_rational_ratio_companion_shows_the_golden_ratio_is_not_the_reason():
    companion = load(EVIDENCE)["controls_built_here"]["rational_ratio_companion"]
    assert set(companion["pairwise_linking"].values()) == {0}
    assert companion["triple_intersection_sign"] == 1
    assert "not the golden ratio in particular" in companion["outcome"]
    retained = load(EVIDENCE)["controls_built_here"]["retained_squares_companion"]
    for phrase in ("m = 1", "t = 1", "mu = 0"):
        assert phrase in retained["retained_values"], phrase
    assert "not recomputed" in retained["what_it_is"]


def test_imported_and_computed_are_separated():
    report = load(EVIDENCE)
    imported = report["imported_not_verified_here"]
    assert len(imported) == 3
    assert any("Mellor" in entry["statement"] for entry in imported)
    assert any("NOT transferred" in entry["source"] for entry in imported)
    text = " | ".join(report["what_is_not_claimed"])
    assert "not a native certificate" in text
    assert "Unknown here" in text


def test_the_reading_is_visible_in_the_note_and_the_registry():
    note = NOTE.read_text(encoding="utf-8")
    for phrase in ("剪断", "Unknown", "Mellor", "抗剪", "分离平面"):
        assert phrase in note, phrase
    claims = tomllib.loads(CLAIMS.read_text(encoding="utf-8"))["claim"]
    match = [c for c in claims
             if c["claim_id"] == "adva.bounded-experiment.borromean-cut-linkage.v0"]
    assert len(match) == 1
    assert match[0]["dependencies"] == ["adva.bounded-experiment.leak-wall.v0"]
    forbidden = " | ".join(match[0]["forbidden_conflations"])
    assert "A zero linking number with separability" in forbidden
    assert "No native certificate follows" in match[0]["counterexample_boundary"]
