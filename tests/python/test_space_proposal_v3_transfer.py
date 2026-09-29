"""Independent receiving checks for the Research 0244 stationary successor.

No parent fixture or assertion is relaxed. Matrices and trajectories below are
recomputed from the retained witness, independently of the successor builder.
"""

import hashlib
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys
import tomllib
from fractions import Fraction as F

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/space_proposal_v3_transfer_v1"
CHECKER = HERE / "calibration.py"
NOTE = "0245-proposal-three-an-exactly-stationary-measure-carrying-successor.md"


def load(path):
    return json.loads(path.read_text())


def module():
    spec = importlib.util.spec_from_file_location("stationary_successor", CHECKER)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


@pytest.fixture(scope="module")
def report():
    return load(HERE / "evidence.json")


def matrix(rows):
    return [[F(x) for x in row] for row in rows]


def step(p, mu):
    out = [F(0)] * len(mu)
    for i, mass in enumerate(mu):
        for j, probability in enumerate(p[i]):
            out[j] += mass * probability
    return out


def test_frozen_sources_and_protected_sections(report):
    contract = load(HERE / "contract.json")
    assert report["protected_files"] == contract["protected_files"]
    for path, sha in contract["protected_files"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == sha
    parent = load(ROOT / "experiments/space_proposal_v3/evidence.json")
    for name in contract["protected_sections"]:
        data = json.dumps(parent["sections"][name], sort_keys=True, separators=(",", ":"))
        assert hashlib.sha256(data.encode()).hexdigest() == report["protected_section_sha256"][name]
    assert parent["sections"]["S3_the_spacetime_group_conditions"][
        "the_declared_uniform_measure_is_exactly_stationary"] is False
    assert report["parent_replay_equal"] is True


def test_cycle_uses_only_original_edges_and_is_not_an_endpoint_gradient(report):
    vertices = [tuple(v) for v in report["vertices"]]
    assert [vertices[i] for i in report["cycle"]] == [
        (-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1)]
    reflection = report["antipodal"]
    assert all(vertices[reflection[i]] == tuple(-x for x in v)
               for i, v in enumerate(vertices))
    edges = {tuple(e) for e in report["edges"]}
    assert len(edges) == 30
    c = matrix(report["current_and_observable"])
    assert sum(x * x for row in c for x in row) == 16
    for i in range(20):
        assert sum(c[i]) == 0
        for j in range(20):
            assert c[i][j] == -c[j][i] == -c[reflection[i]][reflection[j]]
            assert not c[i][j] or tuple(sorted((i, j))) in edges
    cycle = report["cycle"]
    assert sum(c[cycle[k]][cycle[(k + 1) % 4]] for k in range(4)) == 4
    assert sorted(map(len, report["components"])) == [4, 4, 4, 8]


def test_every_operator_is_doubly_stochastic_with_stationary_uniform_measure(report):
    edges = {tuple(e) for e in report["edges"]}
    c = matrix(report["current_and_observable"])
    assert set(report["operators"]) == {"0", "1/4", "-1/4", "1/2", "-1/2"}
    for bias, record in report["operators"].items():
        p = matrix(record["matrix"])
        assert all(x >= 0 for row in p for x in row)
        assert all(sum(row) == 1 for row in p)
        assert all(sum(p[i][j] for i in range(20)) == 1 for j in range(20))
        assert step(p, [F(1, 20)] * 20) == [F(1, 20)] * 20
        for i in range(20):
            for j in range(20):
                supported = i == j or tuple(sorted((i, j))) in edges
                assert (p[i][j] > 0) == supported
                assert p[i][j] == F(supported, 4) + F(bias) * c[i][j] / 16
        assert min(x for row in p for x in row if x) >= F(7, 32)


def test_independently_carried_flow_and_actual_field_symmetry(report):
    d = matrix(report["current_and_observable"])
    reflection = report["antipodal"]
    expected = {"invariant": F(0), "broken_uniform": F(1, 10), "broken_shifted": F(3, 80)}
    assert len(report["cases"]) == 9
    for key, record in report["cases"].items():
        name, g = key.split("/")
        matrices = [matrix(report["operators"][k]["matrix"]) for k in record["operator_keys"]]
        mu, flows = [F(1, 20)] * 20, []
        for s, p in enumerate(matrices):
            assert mu == [F(x) for x in record["states"][s]]
            # Edge-current form is independent of the builder's ordered-hop summation.
            net = {(i, j): mu[i] * p[i][j] - mu[j] * p[j][i] for i, j in report["edges"]}
            flows.append(sum(net[i, j] * d[i][j] for i, j in report["edges"]))
            assert all(sum(mu[i] * p[i][j] - mu[j] * p[j][i] for j in range(20)) == 0
                       for i in range(20))
            for axis in range(3):
                assert sum(net[i, j] * (report["vertices"][j][axis] - report["vertices"][i][axis])
                           for i, j in report["edges"]) == 0
            mu = step(p, mu)
        assert mu == [F(x) for x in record["states"][-1]] == [F(1, 20)] * 20
        assert flows == [F(x) for x in record["flows"]]
        assert sum(flows) == F(record["transport"]) == int(g) * expected[name]
        field_invariant = all(matrices[(s + 2) % 4][reflection[i]][reflection[j]] == matrices[s][i][j]
                              for s in range(4) for i in range(20) for j in range(20))
        assert field_invariant == record["antipodal_half_period_invariant"]
        assert field_invariant == (name == "invariant" or int(g) == 0)
        if field_invariant:
            assert flows[2:] == [-x for x in flows[:2]]


def test_negative_controls_distinguish_marginals_stationarity_and_positivity(report):
    controls = report["controls"]
    assert len(controls) == 11 and all(row["rejected"] for row in controls.values())
    a = controls["row_stochastic_but_not_stationary"]["audit"]
    assert all(F(x) == 0 for x in a["row_sum_residual"])
    assert sorted(F(x) for x in a["uniform_drift"] if F(x)) == [-F(1, 1280), F(1, 1280)]
    b = controls["uniform_stationary_but_not_row_stochastic"]["audit"]
    assert b["uniform_stationary"] and not b["doubly_stochastic"]
    assert any(F(x) for x in b["row_sum_residual"])
    c = controls["unit_marginals_but_negative_entry"]["audit"]
    assert not c["nonnegative"]
    assert all(F(x) == 0 for x in c["row_sum_residual"] + c["column_sum_residual"])
    d = controls["row_normalized_frozen_weight_candidate"]["audit"]
    assert d["nonnegative"] and not d["uniform_stationary"]
    assert all(F(x) == 0 for x in d["row_sum_residual"])
    assert max(abs(F(x)) for x in d["uniform_drift"]) == F(3, 160)


def test_gate_actually_rejects_each_bad_candidate():
    m = module()
    # These are fresh test-side candidates, not retained Boolean verdicts.
    good = [[F(3, 4), F(1, 4)], [F(1, 4), F(3, 4)]]
    assert m.accept(good)["doubly_stochastic"]
    row_only = [[F(1, 2), F(1, 2)], [F(1, 4), F(3, 4)]]
    for bad in (row_only, list(map(list, zip(*row_only))), [[F(2), F(-1)], [F(-1), F(2)]]):
        with pytest.raises(ValueError, match="not doubly stochastic"):
            m.accept(bad)
    for malformed in ([], [[F(1)], []], [[1.0]]):
        with pytest.raises(ValueError):
            m.accept(malformed)


def test_carry_does_not_reset_measure_or_transpose_direction(report):
    m = module()
    p = matrix(report["operators"]["1/2"]["matrix"])
    d = matrix(report["current_and_observable"])
    initial = [F(i == report["cycle"][0]) for i in range(20)]
    result = m.trajectory([p, p], initial, d)
    assert result["states"][1] == p[report["cycle"][0]]
    assert result["states"][2] == step(p, step(p, initial))
    assert result["states"][1] != [F(1, 20)] * 20
    assert result["flows"][0] == F(1, 16)


def test_0242_reference_retains_its_own_measure_and_nonzero(report):
    reference = report["independent_reference_0242"]
    value = F(-2395373021828541, 130893752065903472383)
    assert F(reference["R4/1"]["transport"]) == value
    assert F(reference["R4/-1"]["transport"]) == -value
    assert not reference["R4/1"]["uniform"]
    for row in reference.values():
        assert row["initial"] == row["final"]
    a = report["controls"]["0242_R4_wrong_uniform_measure"]["audit"]
    assert not a["uniform_stationary"]
    assert sorted(F(x) for x in a["uniform_drift"] if F(x)) == [-F(1, 96), F(1, 96)]


def invoke(checker, output):
    return subprocess.run([sys.executable, "-B", str(checker), "--output", str(output)],
                          text=True, capture_output=True, timeout=65)


def test_fresh_and_relocated_replays_are_byte_identical_and_refuse_overwrite(tmp_path):
    first = tmp_path / "fresh.json"
    run = invoke(CHECKER, first)
    assert run.returncode == 0, run.stdout + run.stderr
    assert first.read_bytes() == (HERE / "evidence.json").read_bytes()
    copy_root = tmp_path / "copy"
    paths = list(load(HERE / "contract.json")["protected_files"]) + [
        "experiments/space_proposal_v3_transfer_v1/contract.json",
        "experiments/space_proposal_v3_transfer_v1/calibration.py"]
    for path in paths:
        destination = copy_root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / path, destination)
    second = tmp_path / "relocated.json"
    run = invoke(copy_root / "experiments/space_proposal_v3_transfer_v1/calibration.py", second)
    assert run.returncode == 0, run.stdout + run.stderr
    assert first.read_bytes() == second.read_bytes()
    before = second.read_bytes()
    assert invoke(CHECKER, second).returncode == 2
    assert second.read_bytes() == before
    protected = copy_root / "experiments/space_proposal_v3/evidence.json"
    protected.write_text(protected.read_text() + "\n")
    refused = tmp_path / "must-not-exist.json"
    run = invoke(copy_root / "experiments/space_proposal_v3_transfer_v1/calibration.py", refused)
    assert run.returncode == 1 and "protected source changed" in run.stdout
    assert not refused.exists()


def test_successor_claim_is_separate_and_carries_residual():
    claims = tomllib.loads((ROOT / "docs/claims.toml").read_text())["claim"]
    matches = [row for row in claims
               if row["claim_id"] == "adva.bounded-experiment.space-proposal-v3-transfer.v1"]
    assert len(matches) == 1
    claim = matches[0]
    assert claim["status"] == "bounded-experiment"
    for path in ("space_proposal_v3_transfer_v1/calibration.py", "space_proposal_v3_transfer_v1/contract.json",
                 "space_proposal_v3_transfer_v1/evidence.json", NOTE):
        assert path in claim["code_symbol"]
    for residual in ("circulation", "not unique", "placement", "NotGranted"):
        assert residual in claim["counterexample_boundary"]
