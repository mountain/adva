"""Restricted documentary names; no theorem or title-meaning admission."""

import copy
import hashlib
import itertools
import json
import shutil
import subprocess
import sys

import pytest
import test_math_catalog as catalog_tests
from test_math_catalog import (
    CLI,
    ROOT,
    catalog,
    read_manifest,
    save,
    save_catalog,
)

repository = catalog_tests.repository


@pytest.fixture
def named_repository(repository):
    manifest = read_manifest(repository)
    owner = copy.deepcopy(manifest["entries"][1])
    owner["key"] = catalog.KEY_WORDS_OWNER
    source = ROOT / catalog.KEY_WORDS_SOURCE
    destination = repository / catalog.KEY_WORDS_SOURCE
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(source.read_bytes())
    source_ref = {
        "path": catalog.KEY_WORDS_SOURCE,
        "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    }
    owner["materials"] = [
        source_ref,
        {"path": catalog.KEY_WORDS_PATH, "sha256": "0" * 64},
    ]
    manifest["entries"].append(owner)
    save_catalog(repository, manifest)
    document = json.loads((ROOT / catalog.KEY_WORDS_PATH).read_text())
    document["entries"] = [
        {"key": e["key"], "key_words": e["key"].split("-")} for e in manifest["entries"]
    ]
    repin(repository, document)
    return repository


def repin(root, document):
    path = root / catalog.KEY_WORDS_PATH
    save(path, document)
    manifest = read_manifest(root)
    owner = next(e for e in manifest["entries"] if e["key"] == catalog.KEY_WORDS_OWNER)
    next(r for r in owner["materials"] if r["path"] == catalog.KEY_WORDS_PATH)[
        "sha256"
    ] = hashlib.sha256(path.read_bytes()).hexdigest()
    save_catalog(root, manifest)


def doc(root):
    return json.loads((root / catalog.KEY_WORDS_PATH).read_text())


def test_actual_catalog_v1_checks_all_eighteen_names():
    report = catalog.check_catalog(ROOT, key_words=True)
    assert report["status"] == "CatalogConsistent", report
    names = report["key_words"]
    assert names["status"] == "MatchedDeclaredKeys"
    assert len(names["entries"]) == 18
    assert {e["key"] for e in names["entries"]} == {
        e["key"] for e in read_manifest(ROOT)["entries"]
    }
    assert sum(e["historical_exception"] for e in names["entries"]) == 7
    assert names["title_semantics_checked"] is False
    assert report["native_admission"] == "not-granted"
    assert report["growth_obligation"]["status"] == "Open"


def test_repinning_omitted_fifteenth_key_still_fails(tmp_path):
    root = tmp_path / "omitted"
    shutil.copytree(ROOT, root)
    document = doc(root)
    document["entries"] = [
        e for e in document["entries"] if e["key"] != "logic-yau-calabi-mapping"
    ]
    repin(root, document)
    assert catalog.check_catalog(root)["status"] == "CatalogConsistent"
    report = catalog.check_catalog(root, key_words=True)
    assert report["status"] == "InvalidCatalog"
    assert "cover every declared catalog key" in report["reason"]


def test_actual_catalog_growth_requires_nineteenth_name(tmp_path):
    root = tmp_path / "expanded"
    shutil.copytree(ROOT, root)
    manifest = read_manifest(root)
    added = copy.deepcopy(manifest["entries"][-1])
    added["key"] = "logic-next-observation"
    manifest["entries"].append(added)
    save_catalog(root, manifest)
    assert catalog.check_catalog(root)["status"] == "CatalogConsistent"
    assert catalog.check_catalog(root, key_words=True)["status"] == "InvalidCatalog"

    words = {"key": added["key"], "key_words": ["logic", "next", "observation"]}
    source_path = root / catalog.KEY_WORDS_SOURCE
    source = json.loads(source_path.read_text())
    source["entries"].append(words)
    save(source_path, source)
    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    owner = next(e for e in manifest["entries"] if e["key"] == catalog.KEY_WORDS_OWNER)
    next(r for r in owner["materials"] if r["path"] == catalog.KEY_WORDS_SOURCE)[
        "sha256"
    ] = source_hash
    save_catalog(root, manifest)
    document = doc(root)
    document["source_document"]["sha256"] = source_hash
    document["entries"].append(words)
    repin(root, document)
    report = catalog.check_catalog(root, key_words=True)
    assert report["status"] == "CatalogConsistent", report
    assert len(report["key_words"]["entries"]) == 19
    assert report["native_admission"] == "not-granted"
    assert report["key_words"]["title_semantics_checked"] is False
    assert report["growth_obligation"]["status"] == "Open"


WORDS = ("logic", "a", "b", "a1", "q4", "m6")
SEQUENCES = tuple(p for n in range(1, 5) for p in itertools.permutations(WORDS, n))


@pytest.mark.parametrize("words", SEQUENCES)
def test_all_516_declared_sequences_roundtrip(words):
    key = catalog.link_words(list(words))
    assert catalog.unlink_key(key) == list(words)
    assert key.count("-") == len(words) - 1


def test_finite_images_are_injective_and_order_is_retained():
    images = [catalog.link_words(list(p)) for p in SEQUENCES]
    assert len(images) == len(set(images)) == 516
    assert catalog.link_words(["a", "b"]) != catalog.link_words(["b", "a"])
    ambiguous_pairs = (["a-b", "c"], ["a", "b-c"])
    assert "-".join(ambiguous_pairs[0]) == "-".join(ambiguous_pairs[1])


@pytest.mark.parametrize(
    "words",
    [
        [],
        [""],
        ["a-b", "c"],
        ["a", "b-c"],
        ["A"],
        ["a a"],
        ["a_b"],
        ["\uff41"],
        ["a", "a"],
        [None],
        [True],
        [1],
        "abc",
        ("a", "b"),
    ],
)
def test_malformed_or_ambiguous_words_are_not_normalized(words):
    with pytest.raises(ValueError):
        catalog.link_words(words)


@pytest.mark.parametrize("key", ["", "-a", "a-", "a--b", "A-b", "a-a", "a_b", None])
def test_unlink_refuses_noncanonical_names(key):
    with pytest.raises(ValueError):
        catalog.unlink_key(key)


@pytest.mark.parametrize(
    "words", [[str(i) for i in range(17)], ["a" * 81], ["a" * 40, "b" * 40]]
)
def test_codec_resource_limits_are_unknown(words):
    with pytest.raises(catalog.CatalogLimitError):
        catalog.link_words(words)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda d: d["entries"].pop(),
        lambda d: d["entries"].append(copy.deepcopy(d["entries"][0])),
        lambda d: d["entries"][0]["key_words"].reverse(),
        lambda d: d["entries"][0].update(key_words=["arithmetic-example"]),
        lambda d: d["entries"][0].update(key_words=["arithmetic", "arithmetic"]),
        lambda d: d["entries"].append(
            {"key": "logic-foreign", "key_words": ["logic", "foreign"]}
        ),
        lambda d: d["grandfathered_keys"].append("logic-foreign"),
        lambda d: d["grandfathered_keys"].pop(),
        lambda d: d["policy"].update(normalization="lowercase"),
        lambda d: d.update(version=True),
        lambda d: d.update(version=0),
        lambda d: d.update(native_admission="granted"),
        lambda d: d["source_document"].update(sha256="f" * 64),
    ],
)
def test_repinning_cannot_replace_word_checks(named_repository, mutation):
    d = doc(named_repository)
    mutation(d)
    repin(named_repository, d)
    assert catalog.check_catalog(named_repository)["status"] == "CatalogConsistent"
    result = catalog.check_catalog(named_repository, key_words=True)
    assert result["status"] == "InvalidCatalog", result


def test_unregistered_document_does_not_gain_admission(repository):
    path = repository / catalog.KEY_WORDS_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((ROOT / catalog.KEY_WORDS_PATH).read_bytes())
    assert catalog.check_catalog(repository)["status"] == "CatalogConsistent"
    assert (
        catalog.check_catalog(repository, key_words=True)["status"] == "InvalidCatalog"
    )


def test_new_instance_reuses_the_contract_without_changing_exception_list(
    named_repository,
):
    manifest = read_manifest(named_repository)
    fresh = copy.deepcopy(manifest["entries"][1])
    fresh["key"] = "logic-fresh-word"
    manifest["entries"].append(fresh)
    save_catalog(named_repository, manifest)
    d = doc(named_repository)
    d["entries"].append({"key": fresh["key"], "key_words": ["logic", "fresh", "word"]})
    repin(named_repository, d)
    result = catalog.check_catalog(named_repository, key_words=True)
    assert result["status"] == "CatalogConsistent", result
    assert result["key_words"]["entries"][-1]["words"] == ["logic", "fresh", "word"]
    manifest = read_manifest(named_repository)
    manifest["entries"][-1]["title"] = (
        "A different human title, not a proven interpretation"
    )
    save_catalog(named_repository, manifest)
    assert (
        catalog.check_catalog(named_repository, key_words=True)["status"]
        == "CatalogConsistent"
    )


def test_word_budget_returns_unknown_at_catalog_boundary(named_repository):
    d = doc(named_repository)
    d["entries"][0]["key_words"] = [str(i) for i in range(17)]
    repin(named_repository, d)
    assert (
        catalog.check_catalog(named_repository, key_words=True)["status"] == "Unknown"
    )


def test_cli_opt_in_without_site_packages(named_repository, tmp_path):
    output = tmp_path / "checked.json"
    args = [
        sys.executable,
        "-S",
        str(CLI),
        "math-check",
        "--key-words",
        "--root",
        str(named_repository),
        "--output",
        str(output),
    ]
    result = subprocess.run(
        args, capture_output=True, text=True, timeout=15, check=False
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == json.loads(output.read_text())
    assert json.loads(result.stdout)["key_words"]["status"] == "MatchedDeclaredKeys"
    before = output.read_bytes()
    result = subprocess.run(
        args, capture_output=True, text=True, timeout=15, check=False
    )
    assert result.returncode == 2 and output.read_bytes() == before
