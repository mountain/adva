"""Bounded period-three matrix calibration; external evidence, no admission."""

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tomllib
from fractions import Fraction as F
from pathlib import Path



ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/li_yorke_period_three"
CHECKER = HERE / "replay.py"
CONTRACT = HERE / "contract.json"
EVIDENCE = HERE / "evidence.json"
CLAIMS = ROOT / "docs/claims.toml"
NOTE_0167 = ROOT / "docs/research/0167-li-yorke-period-three-and-homotopy-continuation.md"
NOTE_0168 = ROOT / "docs/research/0168-triadic-cycle-and-continuation-discipline.md"
CLAIM_ID = "adva.bounded-experiment.li-yorke-period-three-matrix.v0"
TIMING_KEYS = ("installed_limits",)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def payload(report):
    """The mathematical payload, with timings and platform facts removed."""
    return {
        key: value
        for key, value in report.items()
        if not key.endswith("_ns")
        and not key.startswith("rss_high_water")
        and key not in TIMING_KEYS
    }


def invoke(checker, output, timeout=60):
    return subprocess.run(
        [sys.executable, "-S", str(checker), "--output", str(output)],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def test_retained_evidence_is_an_external_pass_inside_the_contract():
    report = load(EVIDENCE)
    contract = load(CONTRACT)
    assert report["status"] == "ExternalExactPass"
    assert report["native_status"] == "NotRun"
    assert report["counts"]["assertions"] <= contract["budget"]["max_assertions"]
    assert report["contract_sha256"] == digest(CONTRACT)
    assert report["code_sha256"] == digest(CHECKER)
    installed = report["installed_limits"]
    assert set(installed) == {"RLIMIT_CPU", "RLIMIT_AS", "RLIMIT_FSIZE"}
    assert installed["RLIMIT_CPU"] == "installed"
    assert installed["RLIMIT_AS"].startswith("refused")
    assert installed["RLIMIT_FSIZE"] == "installed"


def test_the_interval_graph_is_derived_and_matches_the_classical_graph():
    report = load(EVIDENCE)
    contract = load(CONTRACT)
    assert report["derived_interval_graph"] == [[0, 1], [1, 1]]
    assert report["derived_interval_graph"] == contract["objects"]["li_yorke_interval_graph"]
    assert report["interval_graph"] == [[0, 1], [1, 1]]
    assert report["shared_characteristic"] == [1, -1, -1]
    assert report["atlas_matrix_square_trace"] == 3
    assert report["atlas_matrix_square_characteristic"] == [1, -3, 1]
    assert report["wrong_matrix_control_characteristic"] == [1, -2, -1]
    assert report["golden_matrix"] == [[1, 1], [1, 0]]


def test_the_exact_three_cycle_satisfies_the_printed_hypothesis():
    report = load(EVIDENCE)
    a, b, c, d = report["tent_cycle"]
    assert (a, b, c, d) == ("2/7", "4/7", "6/7", "2/7")
    assert d == a and a < b < c


def test_every_period_occurs_and_the_lucas_count_is_a_lower_bound():
    report = load(EVIDENCE)
    fixed = report["fixed_point_counts"]
    least = report["least_period_counts"]
    lucas = report["lucas_lower_bounds"]
    for depth in range(1, 9):
        key = str(depth)
        assert int(fixed[key]) == 2 ** depth
        assert int(lucas[key]) <= int(fixed[key])
    assert int(least["3"]) == 6
    assert int(least["5"]) == 30
    assert int(least["7"]) == 126


def test_the_two_controls_refuse_the_dynamical_reading():
    report = load(EVIDENCE)
    assert report["one_hole_self_map_image"] == ["3/2", "2"]
    assert report["one_hole_two_cycle_polynomial"] == [1, -1, -1]
    assert report["one_hole_cycle_roots_in_interval"] == 1
    assert report["golden_bracket"] == ["8/5", "13/8"]
    assert report["rotation_isometry_grid"] == 12
    assert report["rotation_period_exactly_three"] == "1/4"


def test_fresh_run_reproduces_the_retained_mathematical_payload(tmp_path):
    output = tmp_path / "fresh.json"
    completed = invoke(CHECKER, output)
    assert completed.returncode == 0, completed.stderr
    assert payload(load(output)) == payload(load(EVIDENCE))


def test_an_existing_output_is_never_overwritten(tmp_path):
    output = tmp_path / "keep.json"
    output.write_text("retained", encoding="utf-8")
    completed = invoke(CHECKER, output)
    assert completed.returncode != 0
    assert output.read_text(encoding="utf-8") == "retained"


def test_the_cover_relation_is_computed_from_the_tent_map():
    """The graph is derived from exact images, not supplied as data."""
    spec = importlib.util.spec_from_file_location("li_yorke_replay", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    a, b, c = F(2, 7), F(4, 7), F(6, 7)
    intervals = ((a, b), (b, c))
    graph = tuple(
        tuple(1 if module.contains(module.tent_image(*src), dst) else 0 for dst in intervals)
        for src in intervals
    )
    assert graph == ((0, 1), (1, 1))
    # The discriminating facts, so the derived graph is not the vacuous all-ones
    # matrix: I1 covers I2 but not itself, and I2 covers both.
    assert not module.contains(module.tent_image(*intervals[0]), intervals[0])
    assert module.contains(module.tent_image(*intervals[1]), intervals[0])
    assert module.contains(module.tent_image(*intervals[1]), intervals[1])


def test_a_declared_graph_inconsistent_with_its_characteristic_is_refused(tmp_path):
    staged = tmp_path / "staged"
    shutil.copytree(HERE, staged)
    contract = json.loads((staged / "contract.json").read_text(encoding="utf-8"))
    contract["objects"]["li_yorke_interval_graph"] = [[0, 1], [0, 1]]
    (staged / "contract.json").write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    output = tmp_path / "tampered.json"
    completed = invoke(staged / "replay.py", output)
    assert completed.returncode != 0
    assert "Graph" in completed.stderr or "Covering" in completed.stderr
    assert not output.exists()


def test_the_contract_states_its_protected_boundaries():
    contract = load(CONTRACT)
    protected = " ".join(contract["protected"])
    for phrase in (
        "Li-Yorke map",
        "identifies two spaces",
        "No native Rust witness",
        "No floating-point value",
        "imported theorems",
    ):
        assert phrase in protected, phrase
    assert contract["budget"]["wall_seconds"] == 30
    assert contract["input_document"] == (
        "docs/research/0167-li-yorke-period-three-and-homotopy-continuation.md"
    )


def test_the_registered_claim_points_at_existing_artifacts():
    claims = tomllib.loads(CLAIMS.read_text(encoding="utf-8"))["claim"]
    matches = [claim for claim in claims if claim["claim_id"] == CLAIM_ID]
    assert len(matches) == 1
    claim = matches[0]
    assert claim["status"] == "bounded-experiment"
    assert claim["dimension"].startswith("external")
    assert claim["dependencies"] == ["adva.bounded-experiment.golden-ratio-receipt-calibration.v0"]
    assert len(claim["forbidden_conflations"]) >= 10
    assert any("characteristic polynomial" in item for item in claim["forbidden_conflations"])
    for symbol in claim["code_symbol"].split("; "):
        assert (ROOT / symbol).is_file(), symbol
    assert claim["counterexample_boundary"].startswith("The identity established is an identity")


def test_the_notes_exist_and_keep_their_non_claims():
    assert NOTE_0167.is_file() and NOTE_0168.is_file()
    audit = NOTE_0167.read_text(encoding="utf-8")
    plan = NOTE_0168.read_text(encoding="utf-8")
    for phrase in ("scrambled set", "never claims sensitivity", "outside reading", "Flagged"):
        assert phrase in audit, phrase
    for phrase in ("research plan", "tau_n", "does not claim", "Track B"):
        assert phrase in plan, phrase
    assert "Open" in plan and "three-machine identification" in plan
