"""The core-plus-shell carrier must stay exact, and truncation must fail identifiably.

Research 0189 records the first rung: with the shell form fixed to a symbolically
unexpanded expression, distributivity becomes a checkable identity and truncation
is shown to break identifiability rather than distributivity. This test holds the
result in place, including the correction to the proposal, which is the part most
likely to be quietly softened.
"""

import json
import subprocess
import sys
import tomllib
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/aeg_core_shell_symbolic"
CHECKER = HERE / "calibration.py"
EVIDENCE = HERE / "evidence.json"
NOTE = ROOT / "docs/research/0189-core-shell-and-symbolically-unexpanded-shell.md"
SCANNER = ROOT / "scripts/float_aperture_scan.py"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def controls(kind):
    return [r for r in load(EVIDENCE)["truncation_controls"] if r["kind"].startswith(kind)]


def test_the_two_routes_agree_exactly_and_at_sample_points():
    report = load(EVIDENCE)
    assert report["status"] == "ExternalExactPass"
    assert report["native_status"] == "NotRun"
    assert "symbolically unexpanded" in report["shell_form"]
    assert report["routes"], "the routes must be retained"
    for route in report["routes"]:
        assert route["values_equal_exactly"] is True
        assert route["sample_points_agree"] >= 5
    assert any(route["representatives_literally_equal"] is False for route in report["routes"]), (
        "the pair decides value, not structure, and at least one route must show it")


def test_core_plus_shell_equals_the_whole_expression():
    identifiability = load(EVIDENCE)["identifiability"]
    assert identifiability
    assert all(r["carrier_denotes_the_whole_expression"] for r in identifiability)
    resolved = [r for r in identifiability if r["shell_empty"]]
    frozen = [r for r in identifiability if not r["shell_empty"]]
    assert resolved and frozen, "both the resolved and the frozen case must be exercised"
    for row in frozen:
        assert row["verdict"] == "UnknownWithRetainedShell"
        assert row["reason"] and row["shell_expression"] and row["shell_denotation"]


def test_a_shared_truncation_does_not_break_the_identity():
    shared = controls("one shared truncation")
    assert shared, "the shared-truncation control must be retained"
    for row in shared:
        assert row["identity_holds"] is True, (
            "the proposal's claim that truncation alone tears distributivity is refuted here")
        assert row["carried_shell_equals_the_exact_residual"] is False
        assert row["exact_residual"]


def test_per_branch_truncation_breaks_it_and_the_difference_is_an_identity():
    branch = controls("per-branch truncation")
    assert branch
    broken = [r for r in branch if r["identity_breaks"]]
    unbroken = [r for r in branch if not r["identity_breaks"]]
    assert broken and unbroken, "the control must fire on some members and not others"
    for row in unbroken:
        assert row["outer_terms_are_equal"] is True
    for row in broken:
        assert row["outer_terms_are_equal"] is False
        assert row["exact_difference"] != "0"
        assert row["difference_equals_outer_difference_times_linearisation_difference"] is True
        assert row["linearisation_difference"]


def test_the_leak_is_the_residual_times_the_outer_factor():
    leak = controls("the residual multiplied by the outer factor")
    assert leak
    for row in leak:
        assert row["residual"] and row["leaked"] and row["leaked"] != row["residual"]


def test_the_new_carrier_introduces_none_of_the_listed_apertures(tmp_path):
    """The contract promises the scanner classifies this checker exact-only."""
    out = tmp_path / "scan.json"
    completed = subprocess.run([sys.executable, str(SCANNER), "--json", str(out)],
                               capture_output=True, text=True, timeout=300, check=False,
                               cwd=ROOT)
    assert completed.returncode == 0, completed.stderr
    report = json.loads(out.read_text(encoding="utf-8"))
    entry = [e for e in report["experiments"] if e["experiment"] == HERE.name]
    assert len(entry) == 1, "the scanner must see this experiment"
    counts = entry[0]["counts"]
    assert counts["binary64"] == 0 and counts["host"] == 0 and counts["drift"] == 0, counts
    assert entry[0]["verdict"] == "exact-only", entry[0]["verdict"]


def test_the_note_keeps_the_correction_and_the_registry_agrees():
    note = NOTE.read_text(encoding="utf-8")
    assert "反证" in note, "the correction to the proposal must stay in the note"
    assert "可识别性" in note
    claims = tomllib.loads((ROOT / "docs/claims.toml").read_text(encoding="utf-8"))["claim"]
    match = [c for c in claims
             if c["claim_id"] == "adva.bounded-experiment.aeg-core-shell-symbolic.v0"]
    assert len(match) == 1
    forbidden = " | ".join(match[0]["forbidden_conflations"])
    assert "One shared truncation with a torn distributive identity" in forbidden
    assert "A refusal to round with a claim that nothing was lost" in forbidden


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    output = tmp_path / "fresh.json"
    completed = subprocess.run([sys.executable, str(CHECKER), str(output)],
                               capture_output=True, text=True, timeout=300, check=False)
    assert completed.returncode == 0, completed.stderr
    assert load(output) == load(EVIDENCE)
