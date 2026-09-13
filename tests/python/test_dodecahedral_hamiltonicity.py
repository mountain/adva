"""Replay check for the dodecahedral Hamiltonicity calibration.

The recorded evidence is not trusted: the checker is re-run on a temporary copy
and every non-timing field must match. The counts, the vacuity of the declared
rule and the two-sided controls are asserted separately so that a green run
states exactly what it checked.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/dodecahedral_hamiltonicity"
RECORDED = EXPERIMENT / "evidence.json"
COMPARED_KEYS = (
    "status",
    "checks",
    "G1",
    "G2",
    "face_systems",
    "isomorphism",
    "hamiltonian",
    "controls",
)


def test_the_recorded_counts_are_reproduced(tmp_path):
    copied = tmp_path / "experiment"
    shutil.copytree(EXPERIMENT, copied)
    result = subprocess.run(
        [sys.executable, str(copied / "checker.py")],
        cwd=copied,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, result.stderr
    replay = json.loads((copied / "evidence.json").read_text(encoding="utf-8"))
    recorded = json.loads(RECORDED.read_text(encoding="utf-8"))
    for key in COMPARED_KEYS:
        assert replay[key] == recorded[key], key
    assert recorded["status"] == "Checked"
    assert all(recorded["checks"].values())


def test_the_counts_and_the_declared_rule():
    recorded = json.loads(RECORDED.read_text(encoding="utf-8"))
    for name in ("G1", "G2"):
        block = recorded["hamiltonian"][name]
        assert block["undirected_unrooted"] == 30
        assert block["oriented_rooted_at_0"] == 60
        assert block["identity_oriented_is_twice_undirected"]
        assert block["face_consecutive_undirected"] == block["undirected_unrooted"] == 30
        assert block["every_cycle_satisfies_declared_rule"]
        assert block["face_runs_per_cycle_histogram"] == {"4": 30}
        assert block["per_face_counts"] == [10] * 12
        assert block["total_face_run_incidences"] == 120


def test_both_constructions_agree_and_the_isomorphism_is_exhibited():
    recorded = json.loads(RECORDED.read_text(encoding="utf-8"))
    assert recorded["isomorphism"]["error"] is None
    assert recorded["isomorphism"]["triangle_sums_graph"]["isomorphic_to_G1"]
    for field in ("vertices", "edges", "degrees", "girth"):
        assert recorded["G1"][field] == recorded["G2"][field], field
    assert recorded["face_systems"]["G1_faces_are_pentagons"]
    assert recorded["face_systems"]["errors"] == {"G1": None, "G2": None}


def test_the_controls_are_two_sided():
    recorded = json.loads(RECORDED.read_text(encoding="utf-8"))
    controls = {c["name"]: c for c in recorded["controls"]}
    assert controls["Petersen"]["undirected_unrooted"] == 0
    assert controls["cut-vertex bowtie"]["undirected_unrooted"] == 0
    assert controls["K4"]["undirected_unrooted"] == 3
    assert controls["Q3"]["undirected_unrooted"] == controls["Q3"]["dp_oriented_rooted_at_0"] // 2 == 6
    assert all(c["dp_agrees"] and c["matches"] for c in recorded["controls"])


def test_the_declared_budget_was_respected():
    recorded = json.loads(RECORDED.read_text(encoding="utf-8"))
    assert recorded["cost"]["nodes"] <= recorded["budget"]["nodes"]
    assert recorded["cost"]["subprocesses"] <= 1
    assert RECORDED.stat().st_size <= 1024 * 1024


def test_the_herschel_deviation_stays_visible():
    contract = json.loads((EXPERIMENT / "contract.json").read_text(encoding="utf-8"))
    recorded = json.loads(RECORDED.read_text(encoding="utf-8"))
    assert "Herschel" in contract["deviation_note"]
    assert all(c["name"] != "Herschel" for c in recorded["controls"])
