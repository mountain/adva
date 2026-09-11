"""Re-run the bounded lattice-gate calibration and compare it with its witness.

This test is deliberately self-contained: it imports only the standard library,
drives the frozen external checker as a child process, and compares the
mathematical projections of two runs. It does not import the `adva` Python
package, so it runs wherever a plain interpreter is available even when the
native extension has not been built.

Authored by deepseek-v4-flash (DeepSeek Harness), committed through Mingli
Yuan's GitHub account as an authorized proxy.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "experiments" / "reflexive_lattice_gate" / "calibration.py"
WITNESS = ROOT / "experiments" / "reflexive_lattice_gate" / "evidence.json"
COST = ROOT / "experiments" / "reflexive_lattice_gate" / "execution-cost.json"

# Host facts and budget counters are not results; they are compared separately.
HOST_FIELDS = {"elapsed_before_final_write_ns", "peak_rss_kib", "limits_installed",
               "platform", "work_units", "contract_sha256", "source_sha256"}

EXPECTED_STATUS = {
    "square_2d": "ReflexiveForSomeLattice",
    "reflexive_triangle_2d": "ReflexiveForSomeLattice",
    "cube_3d": "ReflexiveForSomeLattice",
    "sheared_cube_3d": "ReflexiveForSomeLattice",
    "reflexive_simplex_3d": "ReflexiveForSomeLattice",
    "to24_3d": "NoCompatibleLattice",
    "unimodular_image_of_to24_3d": "NoCompatibleLattice",
    "twice_to24_3d": "NoCompatibleLattice",
}


def run_fresh(tmp_path):
    output = tmp_path / "fresh.json"
    subprocess.run([sys.executable, "-S", str(SCRIPT), "--output", str(output)],
                   check=True, capture_output=True, cwd=str(ROOT))
    return json.loads(output.read_text())


def projections(report):
    return {key: value for key, value in report.items() if key not in HOST_FIELDS}


def fixture_map(report):
    return {record["status"]: record for record in report["fixtures"]}


def test_fresh_run_reproduces_the_retained_mathematical_projections(tmp_path):
    fresh = run_fresh(tmp_path)
    witness = json.loads(WITNESS.read_text())
    assert fresh["status"] == "Passed"
    assert projections(fresh) == projections(witness)


def test_every_expected_verdict_is_present(tmp_path):
    fresh = run_fresh(tmp_path)
    seen = [record.get("status") for record in fresh["fixtures"]]
    assert seen == list(EXPECTED_STATUS.values())
    assert all(record["bipolar_recovers_primal"] for record in fresh["fixtures"])


def test_to24_fails_with_the_documented_pairing_and_denominators(tmp_path):
    fresh = run_fresh(tmp_path)
    to24 = [record for record in fresh["fixtures"] if record["primal_vertices"] == 24]
    assert len(to24) == 3
    for record in to24:
        assert record["status"] == "NoCompatibleLattice"
        assert record.get("certificate"), "a failing fixture must carry a certificate"
    assert fresh["documented_pairing_recheck"] == {
        "primal_vertex_is_a_vertex": True,
        "polar_vertex_is_a_polar_vertex": True,
        "pairing": "1/2",
        "nonintegral": True,
    }
    assert fresh["fixtures"][5]["certificate_distinct_values"] == ["-1/2", "-1/3", "1/3", "1/2"]
    assert fresh["fixtures"][5]["polar_common_denominator"] == 6


def test_positive_rows_admit_their_own_minimal_lattice(tmp_path):
    fresh = run_fresh(tmp_path)
    positive = [record for record in fresh["fixtures"]
                if record["status"] == "ReflexiveForSomeLattice"]
    assert len(positive) == 5
    for record in positive:
        assert record["minimal_lattice_index_in_zd"] is not None
        assert record["polar_common_denominator"] == 1
    # The square and the cube are positive cases whose minimal lattice is not Z^d.
    indices = sorted(record["minimal_lattice_index_in_zd"] for record in positive)
    assert indices == [1, 1, 2, 4, 4]


def test_every_refusal_is_recorded_as_a_refusal(tmp_path):
    fresh = run_fresh(tmp_path)
    refusals = fresh["refusal_controls"]
    assert refusals["forged_polar_vertex"]["status"] == "RefusedForgedPolarVertex"
    assert refusals["epsilon_integrality"]["status"] == "RefusedEpsilonIntegrality"
    assert refusals["incomplete_coverage"]["status"] == "UnknownCoverage"
    assert refusals["non_full_dimensional"]["status"] == "InvalidDomain"
    assert refusals["origin_on_boundary"]["status"] == "InvalidDomain"
    assert refusals["wrong_dual_transport"]["status"] == "RefusedMismatch"
    assert refusals["wrong_dual_transport"]["applying_A_instead_matches"] is False


def test_existing_output_path_is_refused(tmp_path):
    output = tmp_path / "taken.json"
    output.write_text("{}")
    result = subprocess.run([sys.executable, "-S", str(SCRIPT), "--output", str(output)],
                            capture_output=True, cwd=str(ROOT))
    assert result.returncode != 0
    assert b"refusing to overwrite" in result.stderr


def test_cost_record_states_its_own_limits_and_the_retained_failure():
    cost = json.loads(COST.read_text())
    assert cost["correction_replays"] == 1
    assert cost["attempt_1"]["outcome"].startswith("aborted")
    assert cost["attempt_2"]["limits_installed"]["address_space_bytes"].startswith("not-installed")
    assert cost["attempt_2"]["limits_installed"]["cpu_seconds"] == 25
