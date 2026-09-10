"""Bounded golden-ratio calibration boundary; external evidence, no admission."""

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CALIBRATION = ROOT / "experiments/golden_ratio/calibration.py"
CONTRACT = ROOT / "experiments/golden_ratio/contract.json"
EVIDENCE = ROOT / "experiments/golden_ratio/evidence.json"
INDEX = ROOT / "adva-library/golden-ratio/index.json"
TERMS = ROOT / "docs/terminology/golden-ratio-receipt-v0.json"
MANIFEST = ROOT / "adva-library/math/manifest.json"

SPEC = importlib.util.spec_from_file_location("golden_calibration", CALIBRATION)
calibration = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(calibration)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def invoke(root, output):
    return subprocess.run(
        [
            sys.executable,
            "-S",
            str(CALIBRATION),
            "--root",
            str(root),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


@pytest.fixture
def staged_copy(tmp_path):
    """A writable copy of everything one run reads."""
    root = tmp_path / "checkout"
    shutil.copytree(ROOT / "adva-library/golden-ratio", root / "adva-library/golden-ratio")
    (root / "experiments/golden_ratio").mkdir(parents=True)
    shutil.copyfile(CONTRACT, root / "experiments/golden_ratio/contract.json")
    (root / "docs/terminology").mkdir(parents=True)
    shutil.copyfile(TERMS, root / "docs/terminology/golden-ratio-receipt-v0.json")
    return root


def test_staged_index_matches_every_delivered_artifact():
    index = load(INDEX)
    assert index["schema"] == "adva.golden-ratio-resource-index.research"
    assert index["authority"]["native_admission"] == "not-granted"
    assert index["authority"]["plates_are_evidence"] is False
    assert index["authority"]["pdf_is_evidence"] is False
    assert len(index["artifacts"]) == 15
    for artifact in index["artifacts"]:
        path = ROOT / artifact["staged_path"]
        assert path.is_file(), artifact["staged_path"]
        assert path.stat().st_size == artifact["bytes"]
        assert digest(path) == artifact["sha256"]
    excluded = {entry["name"] for entry in index["delivery"]["excluded_delivered_entries"]}
    assert excluded == {".DS_Store"}


def test_retained_evidence_records_a_passed_bounded_run():
    report = load(EVIDENCE)
    assert report["status"] == "Passed", report.get("reason")
    assert report["authority"]["native_admission"] == "not-granted"
    assert report["authority"]["plates_are_evidence"] is False
    assert report["authority"]["recorded_claims_authenticated"] is False
    cost = report["cost"]
    assert cost["checks"] <= report["budget"]["max_checks"]
    assert cost["nodes"] <= report["budget"]["max_nodes"]
    assert cost["wall_seconds_before_serialization"] <= report["budget"]["max_seconds"]
    assert cost["child_processes"] == 1
    assert cost["subprocesses_beyond_replay"] == 0
    assert len(report["refusals"]) == 8
    assert {entry["outcome"] for entry in report["refusals"]} == {"Refused"}
    assert [r["receipt_kind"] for r in report["receipts"]] == list(calibration.RECEIPT_KINDS)
    for receipt in report["receipts"]:
        assert set(receipt) == set(calibration.RECEIPT_FIELDS) | {"receipt_kind"}
    assert all(entry["holds"] for entry in report["relabeling_refusals"])
    assert report["residuals"]
    assert report["external_replay"]["status"] == "ReplayedAgreement"
    assert report["contract"]["sha256"] == digest(CONTRACT)


def test_fresh_run_reproduces_the_retained_evidence(tmp_path):
    output = tmp_path / "fresh.json"
    completed = invoke(ROOT, output)
    assert completed.returncode == 0, completed.stderr
    fresh = load(output)
    retained = load(EVIDENCE)
    fresh.pop("cost")
    retained.pop("cost")
    assert fresh == retained


def test_tampered_plate_is_refused(staged_copy, tmp_path):
    plate = staged_copy / "adva-library/golden-ratio/plates/whirling-squares.webp"
    plate.write_bytes(plate.read_bytes() + b"\x00")
    output = tmp_path / "tampered.json"
    completed = invoke(staged_copy, output)
    assert completed.returncode == 2, completed.stdout
    report = load(output)
    assert report["status"] == "Invalid"
    assert "artifact-digest" in report["reason"] or "artifact-bytes" in report["reason"]


def test_tampered_container_member_is_refused(staged_copy, tmp_path):
    index = staged_copy / "adva-library/golden-ratio/index.json"
    document = json.loads(index.read_text(encoding="utf-8"))
    entry = next(e for e in document["digest_records"]["container_members"] if e["name"] == "evidence.json")
    entry["sha256"] = "0" * 64
    index.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output = tmp_path / "container.json"
    completed = invoke(staged_copy, output)
    assert completed.returncode == 2, completed.stdout
    assert load(output)["status"] == "Invalid"


def test_missing_receipt_contract_is_invalid(tmp_path):
    root = tmp_path / "checkout"
    shutil.copytree(ROOT / "adva-library/golden-ratio", root / "adva-library/golden-ratio")
    (root / "experiments/golden_ratio").mkdir(parents=True)
    shutil.copyfile(CONTRACT, root / "experiments/golden_ratio/contract.json")
    output = tmp_path / "missing.json"
    completed = invoke(root, output)
    assert completed.returncode == 2, completed.stdout
    assert load(output)["status"] == "Invalid"


def test_existing_output_is_never_overwritten(tmp_path):
    output = tmp_path / "keep.json"
    output.write_text("retained", encoding="utf-8")
    completed = invoke(ROOT, output)
    assert completed.returncode == 2
    assert output.read_text(encoding="utf-8") == "retained"
    missing_parent = tmp_path / "absent" / "report.json"
    completed = invoke(ROOT, missing_parent)
    assert completed.returncode == 2
    assert not missing_parent.exists()


def test_receipt_contract_matches_the_checker():
    terms = load(TERMS)
    assert terms["status"] == "Proposed"
    assert terms["authority"]["native_admission"] == "NotGranted"
    assert tuple(terms["fields"]) == calibration.RECEIPT_FIELDS
    assert tuple(terms["kinds"]) == calibration.RECEIPT_KINDS
    assert {term["name"] for term in terms["terms"]} == set(calibration.RECEIPT_KINDS)
    assert all(term["status"] == "Proposed" for term in terms["terms"])
    assert len(terms["relabeling_prohibitions"]) == 4


def test_catalog_entries_keep_the_external_reference_boundary():
    entries = {entry["key"]: entry for entry in load(MANIFEST)["entries"]}
    arithmetic = entries["arithmetic-golden-ratio-receipt-calibration"]
    geometry = entries["geometry-golden-ratio-external-reference"]
    assert arithmetic["recorded_status"] == "external-calibration-record"
    assert arithmetic["home"] == "arithmetic"
    assert arithmetic["geometry_lineage"] is None
    assert geometry["home"] == "geometry"
    assert geometry["geometry_lineage"] == {
        "kind": "external-reference",
        "parents": [],
        "derivation_evidence": [],
        "discharge": "Open",
    }
    for entry in (arithmetic, geometry):
        assert entry["checker"] is not None
        assert entry["evidence"] and entry["open_obligations"]
        for reference in entry["materials"] + entry["evidence"] + entry["checker"]["sources"]:
            assert digest(ROOT / reference["path"]) == reference["sha256"], reference["path"]
