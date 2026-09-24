"""Replay check for the shell-density hump round.

The checker uses the standard library only, so this replay needs no external
library and no quantum chemistry: it re-runs the reconstruction on a copy (the
calibration writes its evidence beside itself) and then asserts the frozen shape
of the result -- the closed-form table, the two live prediction channels, the
rejected third channel, the six controls that must stay detected, and the
retained ratios that must still transcribe.
"""

import hashlib
import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/shell_density_hump"
EVIDENCE = EXPERIMENT / "evidence.json"
CONTRACT = EXPERIMENT / "contract.json"
NOTE = ROOT / "docs/research/0222-shell-density-hump-criterion.md"
CLAIMS = ROOT / "docs/claims.toml"

BODY_SHA256 = "6323cbd2b529d9d93d02094f18ba5791ce0042e68f7c6fc91876cd182be981cb"
ROWS = 22
SCAN_ROWS = 18
PATTERNS = 11
AGREEMENTS = 22
MAX_WALL_SECONDS = 25.0

TWO_ELECTRON_C = 1.0826822658929016          # 8 / e^2
ONE_ELECTRON_C = 0.5413411329464508          # 4 / e^2
M_SHELL_LARGEST_C = 0.8061130185984938
K_THRESHOLD = 0.9236320123663312


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def body_digest(report):
    """The checker's own documented method for its cost-excluded digest."""
    body = json.dumps({k: v for k, v in report.items() if k != "cost"},
                      indent=2, sort_keys=True)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def replay(tmp_path):
    copied = tmp_path / "shell_density_hump"
    shutil.copytree(EXPERIMENT, copied)
    completed = subprocess.run(
        [sys.executable, str(copied / "calibration.py")],
        cwd=tmp_path, capture_output=True, text=True, timeout=900, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return load(copied / "evidence.json")


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    fresh = replay(tmp_path)
    retained = load(EVIDENCE)
    assert fresh["status"] == "MatchedFiniteScope"
    assert fresh["all_checks_pass"] and fresh["all_controls_detected"]
    assert body_digest(fresh) == body_digest(retained)
    assert fresh["constants"] == retained["constants"]


def test_the_cost_excluded_body_digest_is_reproducible():
    report = load(EVIDENCE)
    assert body_digest(report) == BODY_SHA256
    assert report["cost"]["evidence_body_sha256_excluding_cost"] == BODY_SHA256


def test_the_run_stays_inside_its_declared_budget():
    report = load(EVIDENCE)
    contract = load(CONTRACT)
    assert report["cost"]["wall_seconds"] < MAX_WALL_SECONDS
    assert report["cost"]["wall_seconds"] <= contract["budget"]["wall_seconds"]
    assert contract["schema"] == "adva.research.shell-density-hump-contract.v0"
    assert contract["name"] == "shell-density-hump"
    assert contract["base_commit"].startswith("0d831e7")
    assert len(contract["acceptance"]) >= 8
    assert len(contract["protected"]) >= 6


def test_every_check_passes_and_every_control_is_detected():
    report = load(EVIDENCE)
    checks = report["checks"]
    assert len(checks) == 11
    for name, entry in checks.items():
        assert entry["pass"], name
    controls = report["negative_controls"]
    assert len(controls) == 6
    for name, entry in controls.items():
        assert entry.get("detected") or entry.get("detected_at_2s"), name


def test_the_closed_form_is_reproduced_before_anything_else_is_read():
    """The instrument must first pass on objects whose answers are known."""
    report = load(EVIDENCE)
    table = report["constants"]
    assert len(table) == PATTERNS
    assert abs(table["K (1s2)"]["c"] - TWO_ELECTRON_C) < 1e-9
    assert abs(table["K (1s1)"]["c"] - ONE_ELECTRON_C) < 1e-9
    assert abs(table["K (1s2)"]["x_star"] - 1.0) < 1e-7
    assert abs(table["K (1s1)"]["x_star"] - 1.0) < 1e-7
    check1 = report["checks"]["check1_k_constant"]
    assert check1["rt_10_pointwise_worst_deviation_from_2exp"] < 1e-15
    check0 = report["checks"]["check0_normalisation"]
    assert check0["worst_deviation"] < check0["tolerance"]
    for value in check0["values"].values():
        assert abs(value - 1.0) < 1e-9


def test_the_position_of_a_flat_maximum_is_reported_at_its_float_limit():
    report = load(EVIDENCE)
    check2 = report["checks"]["check2_argmax"]
    assert abs(check2["l_deviation_from_observed"]) < check2["tolerance"]
    limit = check2["float_resolution_limit"]
    deviation = check2["k_worst_deviation"]
    assert 2e-8 < limit < 2.5e-8
    assert 0.0 < deviation < limit, (deviation, limit)
    assert deviation > limit / 10.0, (deviation, limit)
    note = NOTE.read_text(encoding="utf-8")
    assert "分辨率极限" in note, "the position limit must be stated in the note"


def test_the_slater_channel_predicts_without_reading_the_measured_value():
    report = load(EVIDENCE)
    channel = report["channels"]["slater"]
    assert channel["agreements"] == AGREEMENTS
    assert channel["rows"] == ROWS
    assert channel["uses_the_measured_value"] is False
    check5 = report["checks"]["check5_slater_channel"]
    assert check5["rows_checked"] == ROWS
    for row in check5["rows"]:
        assert row["agrees"], row
        # The prediction is formed from zeta, Z and the threshold alone.
        expected = ">" if row["zeta_over_Z"] > row["threshold_1_over_c"] else "<"
        assert row["predicted"] == expected
        assert row["slater_zeta"] == row["Z"] - row["slater_screening"]


def test_the_position_channel_agrees_and_is_a_second_measurement_channel():
    report = load(EVIDENCE)
    channel = report["channels"]["position"]
    assert channel["agreements"] == AGREEMENTS
    assert channel["rows"] == ROWS
    assert channel["uses_the_measured_value"] is False
    table = report["constants"]
    for row in report["checks"]["check6_position_channel"]["rows"]:
        assert row["agrees"], row
        assert abs(row["zeta_from_position"]
                   - table[row["pattern"]]["x_star"] / row["r_hump"]) < 1e-12


def test_the_value_channel_is_information_free_and_is_not_counted_as_live():
    report = load(EVIDENCE)
    check7 = report["checks"]["check7_value_channel_is_information_free"]
    assert check7["comparisons"] == 2 * ROWS
    assert check7["unchanged"] == 2 * ROWS
    assert check7["changed"] == []
    assert check7["is_information_free"] is True
    assert report["channels"]["value"]["uses_the_measured_value"] is True
    assert "information free" in report["channels"]["value"]["verdict"]


def test_only_the_k_and_l_shells_exceed_z_and_the_m_cap_holds():
    report = load(EVIDENCE)
    check8 = report["checks"]["check8_two_shell_cap"]
    assert check8["largest_c_among_M_patterns"] == M_SHELL_LARGEST_C
    assert check8["M_c_below_one"] is True
    assert check8["M_measured_below_Z"] is True
    exceeding = check8["measured_shells_exceeding_Z"]
    assert exceeding["M"] == []
    assert exceeding["K"] == ["Ar", "C", "Cl", "N", "O", "P", "S", "Si"]
    assert exceeding["L"] == ["Ar", "Cl", "P", "S", "Si"]
    assert check8["shells_that_exceed_Z_among_measured"] == ["K", "L"]


def test_the_onset_is_predicted_at_beryllium_with_its_thin_margin_reported():
    report = load(EVIDENCE)
    check9 = report["checks"]["check9_onset_from_slater"]
    assert check9["threshold_zeta_over_Z"] == K_THRESHOLD
    assert 3.0 < check9["predicted_first_Z_strictly_above"] < 4.0
    assert check9["scan_first_atom"] == "Be"
    assert check9["scan_first_Z"] == 4
    assert check9["margin_at_Be"] < 1e-3
    assert check9["scan_value_at_Li"] < 1.0


def test_the_controls_reproduce_the_failures_that_actually_happened():
    report = load(EVIDENCE)
    controls = report["negative_controls"]
    wrong_laguerre = controls["wrong_laguerre_convention"]
    assert abs(wrong_laguerre["integral_1s"] - 4.0) < 1e-9
    cubed = controls["cubed_factorial"]
    assert cubed["invisible_at_1s"] is True
    assert cubed["detected_at_2s"] is True
    assert abs(cubed["integral_2s"] - 0.25) < 1e-9
    assert controls["criterion_as_zeta_above_Z"]["mismatches"] > 0
    assert controls["single_global_threshold"]["wrong"] > 0
    flipped = controls["flipped_measurement"]
    assert flipped["agreements_after_flip"] == AGREEMENTS - 1


def test_no_external_library_and_no_subprocess_is_used():
    report = load(EVIDENCE)
    tooling = report["tooling"]
    assert tooling["external_library_used"] is False
    assert tooling["numpy_used"] is False
    assert tooling["sympy_used"] is False
    assert tooling["pyscf_used"] is False
    assert tooling["subprocesses"] == 0
    source = (EXPERIMENT / "calibration.py").read_text(encoding="utf-8")
    import_lines = [line.strip() for line in source.splitlines()
                    if line.strip().startswith(("import ", "from "))]
    assert import_lines, "the checker must import something"
    for line in import_lines:
        for module in ("numpy", "scipy", "sympy", "pyscf", "subprocess"):
            assert module not in line, (module, line)
    assert sorted(import_lines) == sorted([
        "from __future__ import annotations",
        "import hashlib", "import json", "import math", "import pathlib", "import sys",
        "import time",
    ]), import_lines


def test_the_retained_rows_are_evidence_and_say_so():
    report = load(EVIDENCE)
    retained = report["retained_measurements"]
    assert len(retained["rows"]) == ROWS
    assert len(retained["scan"]) == SCAN_ROWS
    assert retained["ls_not_recorded_for"] == ["Ar", "Cl"]
    joined = " ".join(report["not_claimed"])
    assert "not recomputed here" in joined
    assert "PySCF" in joined


def test_the_reading_is_visible_in_the_note_and_the_registry():
    note = NOTE.read_text(encoding="utf-8")
    for phrase in ("恒真", "Slater", "峰位", "Be", "MatchedFiniteScope", "不主张"):
        assert phrase in note, phrase
    claims = tomllib.loads(CLAIMS.read_text(encoding="utf-8"))["claim"]
    match = [c for c in claims
             if c["claim_id"] == "adva.bounded-experiment.shell-density-hump.v0"]
    assert len(match) == 1
    entry = match[0]
    assert entry["status"] == "bounded-experiment"
    assert "0222-shell-density-hump-criterion.md" in entry["code_symbol"]
    assert "experiments/shell_density_hump/calibration.py" in entry["code_symbol"]
    forbidden = " | ".join(entry["forbidden_conflations"])
    assert "density above Z with a count of classical particles" in forbidden
    assert "An information-free channel with a prediction" in forbidden
    assert "No native certificate follows" in entry["counterexample_boundary"]
