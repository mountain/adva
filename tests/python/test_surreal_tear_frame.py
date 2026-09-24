"""Replay check for the surreal tear frame round.

The checker is standard-library only, so this replay needs no external library.  It
re-runs the enumeration on a copy and asserts that the fresh evidence equals the retained
evidence field for field, that the recorded self-checks are true, and that the criterion
itself is exercised in BOTH directions on planted cases -- a clock that descends must
return None and a clock that does not must return a witness pair.
"""
import json, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/surreal_tear_frame"
EVIDENCE = EXPERIMENT / "evidence.json"
NOTE = ROOT / "docs/research/0223-surreal-order-and-the-tear.md"
CLAIMS = ROOT / "docs/claims.toml"
CRITERION = "q(h)=q(h') => c(h)=c(h')"


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def replay(tmp_path):
    copied = tmp_path / "surreal_tear_frame"
    shutil.copytree(EXPERIMENT, copied)
    done = subprocess.run([sys.executable, str(copied / "calibration.py")],
                          cwd=tmp_path, capture_output=True, text=True, timeout=900, check=False)
    assert done.returncode == 0, done.stderr
    return load(copied / "evidence.json")


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    fresh = replay(tmp_path)
    retained = load(EVIDENCE)
    assert fresh == retained


def test_the_recorded_self_checks_all_pass():
    report = load(EVIDENCE)
    checks = report["self_checks"]
    assert checks, "the run must record its own checks"
    assert all(checks.values()), checks
    assert report["criterion"] == CRITERION


def test_the_criterion_is_exercised_in_both_directions():
    """A criterion that only ever says TEAR, or only ever says DESCENDS, decides nothing."""
    sys.path.insert(0, str(EXPERIMENT))
    import calibration as C
    histories = ["ab", "ba", "a", "b", ""]
    state = lambda h: "".join(sorted(h))          # endpoint: the multiset
    descends = C.find_tear_witness(histories, state, lambda h: len(set(h)))
    tears = C.find_tear_witness(histories, state, lambda h: h)
    assert descends is None, "a clock that descends must give no witness"
    assert tears is not None, "a clock that does not descend must give a witness"
    h0, h1 = tears
    assert state(h0) == state(h1) and h0 != h1


def test_no_nonstandard_import_is_used():
    source = (EXPERIMENT / "calibration.py").read_text(encoding="utf-8")
    lines = [l.strip() for l in source.splitlines() if l.strip().startswith(("import ", "from "))]
    assert lines, "the checker must import something"
    for line in lines:
        for bad in ("sympy", "numpy", "scipy", "pyscf", "adva", "helgoland"):
            assert bad not in line, (bad, line)


def test_the_reading_and_the_0021_boundary_are_visible(tmp_path):
    note = NOTE.read_text(encoding="utf-8")
    for phrase in ("0021", "呈现", "撕裂", "不主张"):
        assert phrase in note, phrase
    claims = __import__("tomllib").loads(CLAIMS.read_text(encoding="utf-8"))["claim"]
    match = [c for c in claims if c["claim_id"] == "adva.bounded-experiment.surreal-tear-frame.v0"]
    assert len(match) == 1
    entry = match[0]
    assert entry["status"] == "bounded-experiment"
    assert "experiments/surreal_tear_frame/calibration.py" in entry["code_symbol"]
    assert "0223-surreal-order-and-the-tear.md" in entry["code_symbol"]
    joined = " | ".join(entry["forbidden_conflations"])
    assert "a presentation with its objectification" in joined
    assert "0021" in entry["counterexample_boundary"]
