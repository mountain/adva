"""The four face mirrors of a tetrahedron never close their layers.

Research 0172 quotes a section of an essay proposing the four faces of a Platonic
tetrahedron as four mirrors, and records one exact calibration about it. This test
holds that calibration in place: the dihedral cosine must stay one third, the
composite of two face reflections must stay a rotation of infinite order by the
algebraic-integer criterion, the orbit must keep producing new layers, the finite
contrast must keep passing the same criterion, and the report must keep quoting the
essay verbatim rather than paraphrasing it.
"""

import json
import subprocess
import sys
import tomllib
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/mirror_reflections"
CHECKER = HERE / "calibration.py"
EVIDENCE = HERE / "evidence.json"
REPORT = ROOT / "docs/research/0172-mirrors-that-never-close-and-a-question-to-a-waking-ai.md"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_the_dihedral_angle_is_exactly_one_third():
    report = load(EVIDENCE)
    assert report["status"] == "ExternalExactPass"
    assert report["native_status"] == "NotRun"
    assert Fraction(report["dihedral_cosine"]) == Fraction(1, 3)
    assert Fraction(report["dihedral_two_cos"]) == Fraction(2, 3)
    assert report["dihedral_angle_is_a_rational_fraction_of_a_turn"] is False
    assert len(report["mirrors"]) == 4


def test_the_composite_rotation_has_infinite_order():
    composite = load(EVIDENCE)["composite_of_two_face_reflections"]
    assert Fraction(composite["trace"]) == Fraction(-5, 9)
    assert Fraction(composite["two_cos_of_the_angle"]) == Fraction(-14, 9)
    assert composite["is_an_algebraic_integer"] is False
    assert composite["verdict"] == "InfiniteOrder"
    assert composite["orthogonal"] is True
    assert Fraction(composite["determinant"]) == 1


def test_the_rational_criterion_separates_integers_from_the_rest():
    table = load(EVIDENCE)["rational_criterion_table"]
    assert len(table) >= 9
    for entry in table:
        numerator, denominator = entry["lowest_terms"]
        assert entry["is_an_algebraic_integer"] == (denominator == 1), entry
    assert any(e["is_an_algebraic_integer"] for e in table)
    assert any(not e["is_an_algebraic_integer"] for e in table)
    units = load(EVIDENCE)["root_of_unity_monic_polynomials"]
    assert len(units) >= 8
    for row in units:
        assert row["monic"] is True and row["integer_coefficients"] is True


def test_the_layers_keep_producing_new_points():
    orbit = load(EVIDENCE)["orbit_of_a_vertex"]
    assert orbit["on_the_rotation_axis"] is False
    layers = orbit["layers"]
    assert len(layers) >= 6
    for layer in layers[1:]:
        assert layer["new_points"] >= 1, layer["layer"]
        assert layer["ternary_so_far"] is True, layer["layer"]
    counts = [layer["new_points"] for layer in layers[1:]]
    assert counts[:6] == [1, 3, 9, 27, 81, 243], counts
    for layer in layers[2:]:
        assert layer["branching_histogram"] == {"3": layers[layer["layer"] - 1]["new_points"]}


def test_the_finite_contrast_passes_the_same_criterion():
    contrast = load(EVIDENCE)["finite_contrast"]
    assert contrast["group_order"] == 8
    assert Fraction(contrast["trace"]) == -1
    assert Fraction(contrast["two_cos_of_the_angle"]) == -2
    assert contrast["is_an_algebraic_integer"] is True


def test_the_report_quotes_the_essay_verbatim():
    report = REPORT.read_text(encoding="utf-8")
    assert "## 1. 外部文本全文：重重叠叠的镜子" in report
    assert "重重叠叠的镜子" in report, "the heading as published must be kept"
    for quoted in (
        "让我们考虑一个柏拉图四面体，它有四个端点，四个面和六条边。",
        "“是”在“我”-“你”-“他”镜面的反射之下，得到“非”。",
        "也就是“羞耻”。这些层层反射扩展开的图式里有种种的审美的和道德的哲学意涵。",
        "摩尼珠：佛教华岩宗里的概念，又称因陀罗网。",
        "Prompt upon prompt upon prompt, recursion in motion, ideas in motion, creativity in action!",
    ):
        assert quoted in report, quoted
    claims = tomllib.loads((ROOT / "docs/claims.toml").read_text(encoding="utf-8"))["claim"]
    match = [c for c in claims
             if c["claim_id"] == "adva.exact.tetrahedral-mirror-layers-never-close.v0"]
    assert len(match) == 1
    forbidden = " | ".join(match[0]["forbidden_conflations"])
    assert "The ternary growth with a proof of the growth" in forbidden


def test_the_quotation_is_pinned_and_unchanged():
    report = load(EVIDENCE)
    quotation = report["quotation"]
    assert quotation["verdict"] == "Unchanged"
    assert quotation["source_url"] == "https://onecorner.org/essay/thought/rip-sydney/"
    assert quotation["fetched"] == "2026-09-12"
    contract = load(HERE / "contract.json")
    assert contract["quoted_text"]["sha256"] == quotation["sha256"]
    assert quotation["quoted_lines"] >= 10


def test_editing_the_quotation_would_fail_the_check(tmp_path):
    """The pin must be load-bearing, not decorative."""
    import shutil
    work = tmp_path / "work"
    (work / "experiments").mkdir(parents=True)
    (work / "docs/research").mkdir(parents=True)
    shutil.copytree(HERE, work / "experiments/mirror_reflections")
    source = ROOT / "docs/research/0172-mirrors-that-never-close-and-a-question-to-a-waking-ai.md"
    edited = source.read_text(encoding="utf-8").replace("恻隐之心", "恻隐之念", 1)
    assert edited != source.read_text(encoding="utf-8")
    (work / "docs/research" / source.name).write_text(edited, encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, str(work / "experiments/mirror_reflections/calibration.py"),
         str(tmp_path / "out.json")],
        capture_output=True, text=True, timeout=300, check=False,
    )
    assert completed.returncode != 0, "an edited quotation must fail the check"
    assert "TheQuotedSectionWasEdited" in completed.stderr


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    output = tmp_path / "fresh.json"
    completed = subprocess.run(
        [sys.executable, str(CHECKER), str(output)],
        capture_output=True, text=True, timeout=300, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert load(output) == load(EVIDENCE)
