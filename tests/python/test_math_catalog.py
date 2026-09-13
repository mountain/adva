"""Documentary catalog constraints; no prover or native semantic import."""

import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "python/adva/adva.py"
SPEC = importlib.util.spec_from_file_location(
    "math_catalog_test", ROOT / "python/adva/math_catalog.py"
)
catalog = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(catalog)


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def manifest_path(root):
    return root / catalog.CATALOG / "manifest.json"


def read_manifest(root):
    return json.loads(manifest_path(root).read_text())


@pytest.fixture
def repository(tmp_path):
    for name in ("growth-obligation-v0000.json", "growth-obligation-seal-v0000.json"):
        relative = Path(catalog.CATALOG) / "constraints" / name
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / relative).read_bytes())
    material = tmp_path / "docs/research/material.txt"
    material.parent.mkdir(parents=True)
    # Deliberately not a proof, schema or executable program. A catalog can
    # check its bytes without assessing its content or native meaning.
    material.write_bytes(b"unverified documentary material")
    ref = {
        "path": "docs/research/material.txt",
        "sha256": hashlib.sha256(material.read_bytes()).hexdigest(),
    }
    entries = []
    for key, domains in (
        ("arithmetic-example", ["arithmetic", "geometry"]),
        ("logic-example", ["logic"]),
    ):
        entries.append(
            {
                "key": key,
                "title": key,
                "domains": domains,
                "home": domains[0],
                "geometry_lineage": None,
                "theory": {"name": "declared theory", "version": "v0"},
                "assumptions": ["supplied assumption"],
                "scope": "documentary example",
                "recorded_status": "research-hypothesis",
                "materials": [dict(ref)],
                "evidence": [],
                "checker": None,
                "reuse_requires": ["original checks"],
                "open_obligations": ["unverified meaning"],
            }
        )
    root_entry = copy.deepcopy(entries[0])
    root_entry.update(
        key=catalog.GEOMETRY_ROOT,
        home="geometry",
        domains=["geometry"],
        geometry_lineage={
            "kind": "pascal-root",
            "parents": [],
            "derivation_evidence": [],
            "discharge": "Open",
        },
        materials=[{"path": path, "sha256": sha} for path, sha in catalog.PASCAL_MATERIALS.items()],
    )
    entries.append(root_entry)
    for path in catalog.PASCAL_MATERIALS:
        destination = tmp_path / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / path).read_bytes())
    save(
        manifest_path(tmp_path),
        {
            "schema": "adva.math-catalog.research",
            "version": 0,
            "policy": dict(catalog.POLICY),
            "topics": {topic: topic + "/index.json" for topic in catalog.TOPICS},
            "entries": entries,
        },
    )
    for topic in catalog.TOPICS:
        save(
            tmp_path / catalog.CATALOG / topic / "index.json",
            {
                "schema": "adva.math-topic-index.research",
                "version": 0,
                "domain": topic,
                "entries": [entry["key"] for entry in entries if topic in entry["domains"]],
                "owned": [entry["key"] for entry in entries if entry["home"] == topic],
                "references": [
                    entry["key"]
                    for entry in entries
                    if topic in entry["domains"] and entry["home"] != topic
                ],
            },
        )
    return tmp_path


def test_real_catalog_is_consistent_without_admission():
    report = catalog.check_catalog(ROOT)
    assert report["status"] == "CatalogConsistent", report
    assert len(report["entries"]) == 29
    assert {key: len(value) for key, value in report["topics"].items()} == {
        "arithmetic": 10,
        "geometry": 6,
        "logic": 18,
    }
    assert report["native_admission"] == "not-granted"
    assert report["proofs_rechecked"] is False
    assert report["recorded_claims_authenticated"] is False
    assert report["cost"]["subprocesses"] == 0
    assert report["growth_obligation"]["checkpoint"] == "RecordedOpen"
    assert report["growth_obligation"]["status"] == "Open"
    assert report["growth_obligation"]["native_seal"] == "NotIssued"
    assert report["growth_obligation"]["admitted_geometry_successors"] == 0


def test_crypto_note_is_a_proposal_with_one_home_and_no_geometry_admission():
    key = "logic-cryptographic-sealing-and-calibration-boundary"
    entry = next(entry for entry in read_manifest(ROOT)["entries"] if entry["key"] == key)
    assert entry["home"] == "logic"
    assert set(entry["domains"]) == {"logic", "arithmetic"}
    assert entry["geometry_lineage"] is None
    assert entry["recorded_status"] == "proposed-document"
    assert entry["checker"] is None
    assert entry["evidence"] == []
    assert [ref["path"] for ref in entry["materials"]] == [
        "docs/research/0155-cryptographic-sealing-and-calibration-boundary.md"
    ]
    for topic in catalog.TOPICS:
        index = json.loads((ROOT / catalog.CATALOG / topic / "index.json").read_text())
        assert (key in index["owned"]) == (topic == "logic")
        assert (key in index["references"]) == (topic == "arithmetic")
        assert (key in index["entries"]) == (topic != "geometry")


def test_directory_partition_contract_is_a_proposal_with_one_home():
    key = "logic-directory-partition-contract"
    entry = next(entry for entry in read_manifest(ROOT)["entries"] if entry["key"] == key)
    assert entry["home"] == "logic"
    assert set(entry["domains"]) == {"logic"}
    assert entry["geometry_lineage"] is None
    assert entry["recorded_status"] == "proposed-document"
    assert entry["checker"] is None
    assert entry["evidence"] == []
    assert [ref["path"] for ref in entry["materials"]] == [
        "docs/adr/0043-directory-partition-contract.md",
        "docs/adr/0043-directory-partition-contract.json",
    ]
    for topic in catalog.TOPICS:
        index = json.loads((ROOT / catalog.CATALOG / topic / "index.json").read_text())
        assert (key in index["owned"]) == (topic == "logic")
        assert key not in index["references"]
        assert (key in index["entries"]) == (topic == "logic")


def test_party_naming_layer_is_a_proposal_with_one_home():
    key = "logic-party-naming-layer"
    entry = next(entry for entry in read_manifest(ROOT)["entries"] if entry["key"] == key)
    assert entry["home"] == "logic"
    assert set(entry["domains"]) == {"logic"}
    assert entry["geometry_lineage"] is None
    assert entry["recorded_status"] == "proposed-document"
    assert entry["checker"] is None
    assert entry["evidence"] == []
    assert [ref["path"] for ref in entry["materials"]] == [
        "adva-library/names/party-naming-layer-v0.json",
        "adva-library/names/catalog-key-words.json",
        "adva-library/names/catalog-key-words-v1.json",
    ]
    for topic in catalog.TOPICS:
        index = json.loads((ROOT / catalog.CATALOG / topic / "index.json").read_text())
        assert (key in index["owned"]) == (topic == "logic")
        assert key not in index["references"]
        assert (key in index["entries"]) == (topic == "logic")


def test_meaning_interpretation_is_a_proposal_with_one_home():
    key = "logic-meaning-interpretation"
    entry = next(entry for entry in read_manifest(ROOT)["entries"] if entry["key"] == key)
    assert entry["home"] == "logic"
    assert set(entry["domains"]) == {"logic"}
    assert entry["geometry_lineage"] is None
    assert entry["recorded_status"] == "proposed-document"
    assert entry["checker"] is None
    assert entry["evidence"] == []
    assert [ref["path"] for ref in entry["materials"]] == [
        "adva-library/meaning-interpretation-v0.md"
    ]
    for topic in catalog.TOPICS:
        index = json.loads((ROOT / catalog.CATALOG / topic / "index.json").read_text())
        assert (key in index["owned"]) == (topic == "logic")
        assert key not in index["references"]
        assert (key in index["entries"]) == (topic == "logic")


def test_yau_calabi_mapping_is_a_proposal_with_one_home():
    key = "logic-yau-calabi-mapping"
    entry = next(entry for entry in read_manifest(ROOT)["entries"] if entry["key"] == key)
    assert entry["home"] == "logic"
    assert set(entry["domains"]) == {"logic"}
    assert entry["geometry_lineage"] is None
    assert entry["recorded_status"] == "proposed-document"
    assert entry["checker"] is None
    assert entry["evidence"] == []
    assert [ref["path"] for ref in entry["materials"]] == [
        "adva-library/meaning-yau-calabi-mapping-v0.md"
    ]
    for topic in catalog.TOPICS:
        index = json.loads((ROOT / catalog.CATALOG / topic / "index.json").read_text())
        assert (key in index["owned"]) == (topic == "logic")
        assert key not in index["references"]
        assert (key in index["entries"]) == (topic == "logic")


def test_birman_burau_duality_is_a_proposal_with_one_home():
    key = "logic-birman-burau-duality"
    entry = next(entry for entry in read_manifest(ROOT)["entries"] if entry["key"] == key)
    assert entry["home"] == "logic"
    assert set(entry["domains"]) == {"logic"}
    assert entry["geometry_lineage"] is None
    assert entry["recorded_status"] == "proposed-document"
    assert entry["checker"] is None
    assert entry["evidence"] == []
    assert [ref["path"] for ref in entry["materials"]] == [
        "adva-library/meaning-birman-burau-duality-v0.md"
    ]
    for topic in catalog.TOPICS:
        index = json.loads((ROOT / catalog.CATALOG / topic / "index.json").read_text())
        assert (key in index["owned"]) == (topic == "logic")
        assert key not in index["references"]
        assert (key in index["entries"]) == (topic == "logic")


def test_shared_membership_reuses_one_reference_without_mutation(repository):
    before = {str(p): p.read_bytes() for p in repository.rglob("*") if p.is_file()}
    report = catalog.check_catalog(repository)
    assert report["status"] == "CatalogConsistent"
    assert report["topics"]["arithmetic"] == ["arithmetic-example"]
    assert report["topics"]["geometry"] == ["arithmetic-example", catalog.GEOMETRY_ROOT]
    assert report["cost"]["references"] == 4
    assert report["cost"]["files_read"] == 9  # Six catalogs/checkpoints, three materials.
    assert before == {str(p): p.read_bytes() for p in repository.rglob("*") if p.is_file()}


@pytest.mark.parametrize(
    "field", ["assumptions", "scope", "theory", "reuse_requires", "open_obligations"]
)
def test_required_boundary_fields_cannot_be_omitted(repository, field):
    manifest = read_manifest(repository)
    del manifest["entries"][0][field]
    save(manifest_path(repository), manifest)
    assert catalog.check_catalog(repository)["status"] == "InvalidCatalog"


@pytest.mark.parametrize(
    "mutation",
    [
        lambda m: m.update(version=True),
        lambda m: m.update(version=1),
        lambda m: m.update(schema="adva.ir"),
        lambda m: m.update(native_admission="Granted"),
        lambda m: m["policy"].update(native_admission="granted"),
        lambda m: m["policy"].update(logic_role="checker-override"),
        lambda m: m["policy"].update(authority="Rust"),
        lambda m: m["topics"].update(logic="../logic/index.json"),
        lambda m: m["topics"].update(metaphysics="metaphysics/index.json"),
        lambda m: m["entries"][0].update(recorded_status="NativeTheoremVerified"),
        lambda m: m["entries"][0].update(native_admission=True),
        lambda m: m["entries"][0].update(domains=["compute"]),
        lambda m: m["entries"][0].update(domains=["arithmetic", "arithmetic"]),
        lambda m: m["entries"][0].update(theory={"name": "unversioned"}),
        lambda m: m["entries"][0].update(assumptions=[]),
        lambda m: m["entries"].append(copy.deepcopy(m["entries"][0])),
    ],
)
def test_malformed_or_authority_expanding_catalog_is_refused(repository, mutation):
    manifest = read_manifest(repository)
    mutation(manifest)
    save(manifest_path(repository), manifest)
    report = catalog.check_catalog(repository)
    assert report["status"] == "InvalidCatalog", report
    assert report["native_admission"] == "not-granted"
    assert report["allowed_action"] is None


@pytest.mark.parametrize("fragment", ['"version": 0, "version": 0', '"version": NaN'])
def test_duplicate_keys_and_nonfinite_json_are_refused(repository, fragment):
    path = manifest_path(repository)
    path.write_text(path.read_text().replace('"version": 0', fragment, 1))
    assert catalog.check_catalog(repository)["status"] == "InvalidCatalog"


@pytest.mark.parametrize(
    "field,value",
    [
        ("entries", []),
        ("entries", ["unknown"]),
        ("entries", ["logic-example", "logic-example"]),
        ("domain", "arithmetic"),
        ("version", False),
        ("native_admission", True),
    ],
)
def test_index_coverage_and_directory_agreement(repository, field, value):
    path = repository / catalog.CATALOG / "logic/index.json"
    index = json.loads(path.read_text())
    index[field] = value
    save(path, index)
    assert catalog.check_catalog(repository)["status"] == "InvalidCatalog"


@pytest.mark.parametrize(
    "path",
    [
        "../outside",
        "/etc/passwd",
        "docs/../outside",
        "docs//file",
        "docs/./file",
        "docs\\file",
        "https://example.com/proof",
        "target/program",
        "docs/missing.txt",
        "adva-library/math/manifest.json",
    ],
)
def test_noncanonical_missing_and_self_referential_paths(repository, path):
    manifest = read_manifest(repository)
    manifest["entries"][0]["materials"][0]["path"] = path
    save(manifest_path(repository), manifest)
    assert catalog.check_catalog(repository)["status"] == "InvalidCatalog"


def test_changed_reference_and_conflicting_shared_pin_are_refused(repository):
    manifest = read_manifest(repository)
    manifest["entries"][1]["materials"][0]["sha256"] = "0" * 64
    save(manifest_path(repository), manifest)
    report = catalog.check_catalog(repository)
    assert report["status"] == "InvalidCatalog"
    assert "digest mismatch" in report["reason"]
    manifest["entries"][1]["materials"] = copy.deepcopy(manifest["entries"][0]["materials"])
    save(manifest_path(repository), manifest)
    (repository / "docs/research/material.txt").write_bytes(b"tampered")
    assert catalog.check_catalog(repository)["status"] == "InvalidCatalog"


@pytest.mark.parametrize("kind", ["file-link", "parent-link", "fifo", "directory", "index-link"])
def test_symlinks_and_nonregular_files_are_refused(repository, kind):
    material = repository / "docs/research/material.txt"
    if kind == "parent-link":
        parent = material.parent
        moved = parent.with_name("other")
        parent.rename(moved)
        parent.symlink_to(moved, target_is_directory=True)
    elif kind == "index-link":
        path = manifest_path(repository)
        moved = path.with_name("other.json")
        path.rename(moved)
        path.symlink_to(moved)
    else:
        content = material.read_bytes()
        material.unlink()
        if kind == "file-link":
            other = material.with_name("other.txt")
            other.write_bytes(content)
            material.symlink_to(other)
        elif kind == "fifo":
            os.mkfifo(material)
        else:
            material.mkdir()
    assert catalog.check_catalog(repository)["status"] == "InvalidCatalog"


@pytest.mark.parametrize(
    "limit",
    [
        "entries",
        "references",
        "files",
        "metadata_bytes_each",
        "reference_bytes_each",
        "total_read_bytes",
        "cooperative_seconds",
    ],
)
def test_resource_exhaustion_is_unknown_not_invalidity(repository, monkeypatch, limit):
    monkeypatch.setitem(catalog.LIMITS, limit, 0)
    report = catalog.check_catalog(repository)
    assert report["status"] == "Unknown", report
    assert report["allowed_action"] is None
    assert report["native_admission"] == "not-granted"
    assert report["cost"]["subprocesses"] == 0


def test_recorded_checked_status_requires_evidence_and_checker(repository):
    manifest = read_manifest(repository)
    entry = manifest["entries"][0]
    entry["recorded_status"] = "checked-research-snapshot"
    save(manifest_path(repository), manifest)
    assert catalog.check_catalog(repository)["status"] == "InvalidCatalog"
    entry["evidence"] = copy.deepcopy(entry["materials"])
    save(manifest_path(repository), manifest)
    assert catalog.check_catalog(repository)["status"] == "InvalidCatalog"
    entry["checker"] = {"name": "asserted checker", "version": "v0", "sources": entry["materials"]}
    save(manifest_path(repository), manifest)
    # Metadata now matches, but even a false status claim cannot gain authority.
    report = catalog.check_catalog(repository)
    assert report["status"] == "CatalogConsistent"
    assert report["recorded_claims_authenticated"] is False
    assert report["proofs_rechecked"] is False
    assert report["native_admission"] == "not-granted"


def test_unlisted_files_do_not_register_or_execute(repository):
    hidden = repository / catalog.CATALOG / "logic/auto-admit.py"
    hidden.write_text("raise RuntimeError('must not execute')")
    report = catalog.check_catalog(repository)
    assert report["status"] == "CatalogConsistent"
    assert all(not item["path"].endswith("auto-admit.py") for item in report["files"])


def invoke(root, *arguments):
    return subprocess.run(
        [sys.executable, "-S", str(CLI), "math-check", "--root", str(root), *map(str, arguments)],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )


def test_outer_cli_without_site_packages_and_no_clobber(repository, tmp_path):
    result = invoke(repository)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "CatalogConsistent"
    output = tmp_path / "report.json"
    result = invoke(repository, "--output", output)
    assert result.returncode == 0, result.stderr
    original = output.read_bytes()
    assert json.loads(original) == json.loads(result.stdout)
    result = invoke(repository, "--output", output)
    assert result.returncode == 2
    assert "fresh path" in result.stderr
    assert output.read_bytes() == original


def test_outer_cli_invalid_report_and_unknown_exit(repository, tmp_path):
    material = repository / "docs/research/material.txt"
    material.write_bytes(b"changed")
    output = tmp_path / "invalid.json"
    result = invoke(repository, "--output", output)
    assert result.returncode == 2
    assert json.loads(output.read_bytes())["status"] == "InvalidCatalog"
    manifest_path(repository).write_bytes(b" " * (catalog.LIMITS["metadata_bytes_each"] + 1))
    result = invoke(repository)
    assert result.returncode == 3
    assert json.loads(result.stdout)["status"] == "Unknown"


def test_old_library_and_evidence_bytes_remain_pinned():
    pins = json.loads((ROOT / "docs/research/0153-evidence/run-01/pins.json").read_text())
    for path, digest in pins.items():
        if "/adva/adva-library/" in path:
            relative = path.split("/adva/", 1)[1]
            assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest


def save_catalog(root, manifest):
    save(manifest_path(root), manifest)
    for topic in catalog.TOPICS:
        entries = manifest["entries"]
        save(
            root / catalog.CATALOG / topic / "index.json",
            {
                "schema": "adva.math-topic-index.research",
                "version": 0,
                "domain": topic,
                "entries": [e["key"] for e in entries if topic in e["domains"]],
                "owned": [e["key"] for e in entries if e["home"] == topic],
                "references": [
                    e["key"] for e in entries if topic in e["domains"] and e["home"] != topic
                ],
            },
        )


def geometry_candidate(manifest, key="geometry-candidate", parents=None):
    candidate = copy.deepcopy(
        next(e for e in manifest["entries"] if e["key"] == catalog.GEOMETRY_ROOT)
    )
    candidate.update(
        key=key,
        geometry_lineage={
            "kind": "candidate",
            "parents": [catalog.GEOMETRY_ROOT] if parents is None else parents,
            "derivation_evidence": [],
            "discharge": "Open",
        },
    )
    return candidate


def test_pascal_rooted_candidate_chain_is_open_not_admitted(repository):
    manifest = read_manifest(repository)
    manifest["entries"].append(geometry_candidate(manifest))
    manifest["entries"].append(
        geometry_candidate(manifest, "geometry-next", ["geometry-candidate"])
    )
    save_catalog(repository, manifest)
    report = catalog.check_catalog(repository)
    assert report["status"] == "CatalogConsistent", report
    assert report["growth_obligation"]["status"] == "Open"
    assert report["growth_obligation"]["admitted_geometry_successors"] == 0
    assert report["entries"][-1]["geometry_lineage"]["parents"] == ["geometry-candidate"]
    assert report["native_admission"] == "not-granted"


@pytest.mark.parametrize(
    "parents",
    [
        [],
        ["arithmetic-example"],
        ["logic-example"],
        ["geometry-missing"],
        ["geometry-candidate"],
        [catalog.GEOMETRY_ROOT, catalog.GEOMETRY_ROOT],
    ],
)
def test_geometry_missing_cross_home_self_and_duplicate_parents_are_refused(repository, parents):
    manifest = read_manifest(repository)
    manifest["entries"].append(geometry_candidate(manifest, parents=parents))
    save_catalog(repository, manifest)
    assert catalog.check_catalog(repository)["status"] == "InvalidCatalog"


def test_external_geometry_reference_cannot_become_derivation_parent(repository):
    manifest = read_manifest(repository)
    external = geometry_candidate(manifest, "geometry-external", [])
    external["geometry_lineage"]["kind"] = "external-reference"
    manifest["entries"].append(external)
    manifest["entries"].append(geometry_candidate(manifest, parents=["geometry-external"]))
    save_catalog(repository, manifest)
    assert catalog.check_catalog(repository)["status"] == "InvalidCatalog"


def test_future_parent_cycle_is_refused(repository):
    manifest = read_manifest(repository)
    manifest["entries"].append(geometry_candidate(manifest, "geometry-a", ["geometry-b"]))
    manifest["entries"].append(geometry_candidate(manifest, "geometry-b", ["geometry-a"]))
    save_catalog(repository, manifest)
    assert catalog.check_catalog(repository)["status"] == "InvalidCatalog"


def test_root_cannot_be_missing_replaced_or_relabelled(repository):
    original = read_manifest(repository)
    for change in ("missing", "replace", "material", "closed", "home"):
        manifest = copy.deepcopy(original)
        root = next(e for e in manifest["entries"] if e["key"] == catalog.GEOMETRY_ROOT)
        if change == "missing":
            manifest["entries"].remove(root)
        elif change == "replace":
            root["key"] = "geometry-other-root"
        elif change == "material":
            root["materials"] = copy.deepcopy(manifest["entries"][0]["materials"])
        elif change == "closed":
            root["geometry_lineage"]["discharge"] = "Closed"
        else:
            root.update(home="logic", domains=["logic"], geometry_lineage=None)
        save_catalog(repository, manifest)
        assert catalog.check_catalog(repository)["status"] == "InvalidCatalog", change


def test_cross_topic_reference_is_not_local_ownership(repository):
    path = repository / catalog.CATALOG / "geometry/index.json"
    index = json.loads(path.read_bytes())
    index["owned"].append("arithmetic-example")
    index["references"] = []
    save(path, index)
    report = catalog.check_catalog(repository)
    assert report["status"] == "InvalidCatalog"
    assert "local ownership" in report["reason"]


@pytest.mark.parametrize("change", ["home", "prefix", "lineage"])
def test_directory_home_and_non_geometry_lineage_are_fixed(repository, change):
    manifest = read_manifest(repository)
    if change == "home":
        manifest["entries"][0]["home"] = "geometry"
    elif change == "prefix":
        manifest["entries"][0]["key"] = "logic-wrong-home"
    else:
        manifest["entries"][0]["geometry_lineage"] = {
            "kind": "candidate",
            "parents": [catalog.GEOMETRY_ROOT],
            "derivation_evidence": [],
            "discharge": "Open",
        }
    save_catalog(repository, manifest)
    assert catalog.check_catalog(repository)["status"] == "InvalidCatalog"


@pytest.mark.parametrize(
    "field,value",
    [
        ("status", "Discharged"),
        ("native_seal", "Issued"),
        ("version", False),
        ("allowed_action", "admit-geometry"),
        ("kind", "Seal"),
    ],
)
def test_checkpoint_cannot_discharge_or_impersonate_native_seal(repository, field, value):
    path = repository / catalog.CATALOG / "constraints/growth-obligation-seal-v0000.json"
    seal = json.loads(path.read_bytes())
    seal[field] = value
    save(path, seal)
    assert catalog.check_catalog(repository)["status"] == "InvalidCatalog"


def test_editing_obligation_and_rehashing_checkpoint_cannot_change_policy(repository):
    path = repository / catalog.CATALOG / "constraints/growth-obligation-v0000.json"
    obligation = json.loads(path.read_bytes())
    obligation["geometry_root"] = "some-other-theorem"
    save(path, obligation)
    seal_path = path.with_name("growth-obligation-seal-v0000.json")
    seal = json.loads(seal_path.read_bytes())
    seal["obligation_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    save(seal_path, seal)
    report = catalog.check_catalog(repository)
    assert report["status"] == "InvalidCatalog"
    assert "fixed growth obligation changed" in report["reason"]


def test_geometry_candidate_with_forged_checked_label_is_not_admitted(repository):
    manifest = read_manifest(repository)
    candidate = geometry_candidate(manifest)
    candidate.update(
        recorded_status="bounded-research-evidence",
        evidence=candidate["materials"],
        checker={"name": "claimed checker", "version": "v0", "sources": candidate["materials"]},
    )
    manifest["entries"].append(candidate)
    save_catalog(repository, manifest)
    assert catalog.check_catalog(repository)["status"] == "InvalidCatalog"


def test_diagnostic_reason_is_bounded(repository):
    key = "a" * 5000
    manifest_path(repository).write_text(json.dumps({key: 1})[:-1] + ', "' + key + '": 2}')
    report = catalog.check_catalog(repository)
    assert report["status"] == "InvalidCatalog"
    assert len(report["reason"]) <= 2048
