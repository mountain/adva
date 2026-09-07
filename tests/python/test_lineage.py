"""Research 0156 Phases 0-1: documentary tamper-evident lineage tests.

These tests cover byte integrity, chain replay, divergence localization,
Merkle inclusion, anchor chaining, the CLI surface commands and the Phase 1
disclosure boundary (Pedersen commitment, Schnorr NIZK, disclosure verify).
They perform no semantic judgment and require no optional Ed25519 backend
(no-backend paths must report Unknown, never a downgraded "hash only" result).
"""

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "python/adva/adva.py"
SPEC = importlib.util.spec_from_file_location(
    "lineage_test", ROOT / "python/adva/lineage.py"
)
lineage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(lineage)


def record(seq, proposition, verdict="Verified", residual=None, cites=None):
    body = {
        "schema": lineage.RECORD_SCHEMA,
        "version": 0,
        "package": "arithmetic",
        "seq": seq,
        "proposition": proposition,
        "environment": {"x": "134217729/134217728", "y": "134217727/134217728"},
        "checker": {"id": "exact-rational-v0", "version": "0"},
        "verdict": verdict,
        "residual": residual,
        "cites_same_home": cites or ([seq - 1] if seq > 1 else []),
        "cites_cross": [],
        "budget_consumed": {"units": 12},
        "secret_slot": None,
    }
    body["digest"] = lineage.sha256_hex(lineage.canonical_bytes(body))
    return body


def write_record(root, package, seq, body):
    path = lineage.records_dir(root, package) / f"{seq:06d}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(lineage.canonical_bytes(body))
    return path


@pytest.fixture
def repository(tmp_path):
    write_record(tmp_path, "arithmetic", 1, record(1, "mul(x, y) == const(1)"))
    write_record(tmp_path, "arithmetic", 2, record(2, "2*3*5+1 == 31"))
    write_record(tmp_path, "arithmetic", 3,
                 record(3, "tamper-control", "Rejected", "-1/18014398509481984"))
    report = lineage.lineage_update(tmp_path, "arithmetic", 0,
                                    tmp_path / "lineage" / "anchors" / "0000.json")
    assert report["status"] == "CheckpointBuilt", report
    return tmp_path, Path(report["anchor"]["path"])


# --- canonical serialization -------------------------------------------------

def test_canonical_bytes_deterministic_and_strict():
    assert lineage.canonical_bytes({"b": 1, "a": [True, None, "x"]}) == \
        b'{"a":[true,null,"x"],"b":1}'
    assert lineage.canonical_bytes({"a": "中"}) == b'{"a":"\xe4\xb8\xad"}'
    with pytest.raises(ValueError):
        lineage.canonical_bytes({"a": 1.5})
    with pytest.raises(ValueError):
        lineage.canonical_bytes({1: "int key"})
    deep: dict = {"a": 1}
    for _ in range(40):
        deep = {"a": [deep]}
    with pytest.raises(ValueError):
        lineage.canonical_bytes(deep)


def test_parse_json_rejects_duplicate_keys_and_constants():
    with pytest.raises(ValueError):
        lineage.parse_json(b'{"a":1,"a":2}')
    with pytest.raises(ValueError):
        lineage.parse_json(b'{"a":NaN}')


# --- record validation -------------------------------------------------------

def test_record_validation_accepts_and_rejects():
    good = record(1, "p", "Verified")
    validated = lineage.validate_record(good, seq=1, package="arithmetic")
    assert validated["digest"] == good["digest"]
    mutations = [
        lambda r: r.update(verdict="Maybe"),
        lambda r: r.update(schema="other-schema"),
        lambda r: r.update(digest="0" * 64),
        lambda r: r.update(seq=7),
        lambda r: r.update(secret_slot={"x": 1}),
        lambda r: r.update(cites_same_home=[1]),
        lambda r: r.update(proposition=""),
        lambda r: r.update(budget_consumed={"units": -1}),
        lambda r: r.update(environment={"x": 1.5}),
        lambda r: r.update(cites_cross=[{"package": "geometry", "seq": 1,
                                         "digest": "zz" * 32}]),
    ]
    for mutate in mutations:
        broken = copy.deepcopy(good)
        mutate(broken)
        with pytest.raises(ValueError):
            lineage.validate_record(broken, seq=1, package="arithmetic")


# --- tamper-check ------------------------------------------------------------

def test_tamper_check_intact(repository):
    root, anchor = repository
    report = lineage.tamper_check(root, anchor)
    assert report["status"] == "Intact", report
    assert report["packages"]["arithmetic"]["checkpoint_match"] is True


def test_tamper_check_locate_content_byte(repository):
    root, anchor = repository
    path = lineage.records_dir(root, "arithmetic") / "000002.json"
    text = json.loads(path.read_bytes())
    text["proposition"] = "2*3*5+1 == 32"
    path.write_bytes(lineage.canonical_bytes(text))
    report = lineage.tamper_check(root, anchor)
    assert report["status"] == "Tampered"
    divergence = report["packages"]["arithmetic"]["first_divergence"]
    assert divergence["seq"] == 2
    assert "digest" in divergence["reason"]


def test_tamper_check_digest_only_tamper(repository):
    root, anchor = repository
    path = lineage.records_dir(root, "arithmetic") / "000002.json"
    text = json.loads(path.read_bytes())
    text["digest"] = "f" * 64
    path.write_bytes(lineage.canonical_bytes(text))
    report = lineage.tamper_check(root, anchor)
    assert report["status"] == "Tampered"
    assert report["packages"]["arithmetic"]["first_divergence"]["seq"] == 2


def test_tamper_check_missing_record(repository):
    root, anchor = repository
    (lineage.records_dir(root, "arithmetic") / "000002.json").unlink()
    report = lineage.tamper_check(root, anchor)
    assert report["status"] == "Tampered"
    divergence = report["packages"]["arithmetic"]["first_divergence"]
    assert divergence["kind"] == "missing-record"
    assert divergence["seq"] == 2


def test_tamper_check_rewritten_checkpoint_caught_by_anchor(repository):
    root, anchor = repository
    anchor_body = json.loads(anchor.read_bytes())
    anchor_body["checkpoints"]["arithmetic"]["chain_head"] = "0" * 64
    anchor.write_bytes(lineage.canonical_bytes(anchor_body))
    report = lineage.tamper_check(root, anchor)
    assert report["status"] == "Tampered"
    assert report["anchor"]["match"] is False


def test_tamper_check_missing_anchor(repository):
    root, _anchor = repository
    report = lineage.tamper_check(root, root / "lineage" / "nope.json")
    assert report["status"] == "Unknown"
    assert "anchor file missing" in report["reason"]


def test_tamper_check_prev_anchor_chain(repository):
    root, first = repository
    report = lineage.lineage_update(root, "arithmetic", 1,
                                    root / "lineage" / "anchors" / "0001.json")
    assert report["status"] == "CheckpointBuilt"
    second = Path(report["anchor"]["path"])
    assert json.loads(second.read_bytes())["prev_anchor_sha256"] == \
        json.loads(first.read_bytes())["self_sha256"]
    assert lineage.tamper_check(root, second, prev_anchor_path=first)["status"] == "Intact"
    forged = json.loads(first.read_bytes())
    forged["self_sha256"] = "0" * 64
    fake = root / "lineage" / "anchors" / "fake.json"
    fake.write_bytes(lineage.canonical_bytes(forged))
    report = lineage.tamper_check(root, second, prev_anchor_path=fake)
    assert report["status"] == "Tampered"
    assert "prev anchor invalid" in report["reason"]
    assert "self_sha256" in report["reason"]


def test_tamper_check_budget_exhaustion_is_unknown(repository):
    root, anchor = repository
    report = lineage.tamper_check(root, anchor,
                                  budget=lineage._Budget(max_records=1))
    assert report["status"] == "Unknown"
    assert "budget" in report["reason"]


# --- Merkle inclusion --------------------------------------------------------

def test_merkle_inclusion_verified_and_rejected(repository):
    root, anchor = repository
    anchor_body = json.loads(anchor.read_bytes())
    checkpoint = anchor_body["checkpoints"]["arithmetic"]
    digests = [json.loads((lineage.records_dir(root, "arithmetic")
                           / f"{i:06d}.json").read_bytes())["digest"] for i in (1, 2, 3)]
    proof = lineage.inclusion_proof(digests, 2)
    request = {"schema": lineage.INCLUSION_REQUEST_SCHEMA, "version": 0,
               "package": "arithmetic", "seq": proof["seq"],
               "digest": proof["digest"], "path": proof["path"]}
    good = root / "inclusion-good.json"
    good.write_bytes(lineage.canonical_bytes(request))
    assert lineage.verify("inclusion", good, anchor_path=anchor)["status"] == "Verified"
    assert lineage.merkle_root_and_height(digests)[0] == checkpoint["merkle_root"]
    forged = copy.deepcopy(request)
    forged["path"][0]["hash"] = "0" * 64
    bad = root / "inclusion-bad.json"
    bad.write_bytes(lineage.canonical_bytes(forged))
    assert lineage.verify("inclusion", bad, anchor_path=anchor)["status"] == "Rejected"


# --- signature and key-issue (backend-independent) ---------------------------

def test_verify_signature_backend_independent(repository):
    root, _anchor = repository
    request = {"schema": lineage.SIGNATURE_REQUEST_SCHEMA, "version": 0,
               "key_id": "ed25519:test", "pubkey_hex": "11" * 32,
               "message": {"purpose": "anchor-signing"},
               "signature_hex": "22" * 64}
    path = root / "sig.json"
    path.write_bytes(lineage.canonical_bytes(request))
    report = lineage.verify("signature", path)
    if lineage.backend_available():
        assert report["status"] == "Rejected"  # garbage signature
    else:
        assert report["status"] == "Unknown"
        assert "ed25519 backend missing" in report["reason"]


def test_verify_signature_roundtrip_when_backend_present(repository):
    if not lineage.backend_available():
        pytest.skip("optional ed25519 backend not installed")
    root, _anchor = repository
    seed, public = lineage.generate_signing_keypair()
    message = {"purpose": "anchor-signing", "home": "test"}
    signature = lineage.sign_ed25519(seed, message)
    request = {"schema": lineage.SIGNATURE_REQUEST_SCHEMA, "version": 0,
               "key_id": lineage.key_id_for(public), "pubkey_hex": public,
               "message": message, "signature_hex": signature}
    path = root / "sig.json"
    path.write_bytes(lineage.canonical_bytes(request))
    assert lineage.verify("signature", path)["status"] == "Verified"
    request["message"] = {"purpose": "anchor-signing", "home": "other"}
    path.write_bytes(lineage.canonical_bytes(request))
    assert lineage.verify("signature", path)["status"] == "Rejected"


def test_key_issue_purpose_gate_and_backend_gate(tmp_path):
    blocked = lineage.key_issue(purpose="other-purpose", home="h",
                                policy_version="v0")
    assert blocked["status"] == "Blocked"
    report = lineage.key_issue(purpose="anchor-signing", home="h",
                               policy_version="v0",
                               private_out=tmp_path / "private.key")
    if lineage.backend_available():
        assert report["status"] == "Issued"
        record = report["record"]
        assert record["schema"] == lineage.KEY_ISSUE_RECORD_SCHEMA
        assert record["key_id"].startswith("ed25519:")
        assert (tmp_path / "private.key").exists()
    else:
        assert report["status"] == "Unknown"
        assert "backend missing" in report["reason"]


# --- CLI surface -------------------------------------------------------------

def run_cli(*arguments):
    return subprocess.run([sys.executable, str(CLI), *arguments],
                          capture_output=True, text=True, check=False)


def test_cli_tamper_check_exit_codes(repository):
    root, anchor = repository
    intact = run_cli("tamper-check", "--root", str(root), "--anchor", str(anchor))
    assert intact.returncode == 0, intact.stderr
    path = lineage.records_dir(root, "arithmetic") / "000001.json"
    text = json.loads(path.read_bytes())
    text["proposition"] = "tampered"
    path.write_bytes(lineage.canonical_bytes(text))
    tampered = run_cli("tamper-check", "--root", str(root), "--anchor", str(anchor))
    assert tampered.returncode == 2
    assert '"status": "Tampered"' in tampered.stdout
    missing = run_cli("tamper-check", "--root", str(root),
                      "--anchor", str(root / "nope.json"))
    assert missing.returncode == 3
    assert "Unknown" in missing.stdout


def test_cli_verify_inclusion_exit_codes(repository):
    root, anchor = repository
    digests = [json.loads((lineage.records_dir(root, "arithmetic")
                           / f"{i:06d}.json").read_bytes())["digest"] for i in (1, 2, 3)]
    proof = lineage.inclusion_proof(digests, 2)
    request = {"schema": lineage.INCLUSION_REQUEST_SCHEMA, "version": 0,
               "package": "arithmetic", "seq": proof["seq"],
               "digest": proof["digest"], "path": proof["path"]}
    good = root / "inc.json"
    good.write_bytes(lineage.canonical_bytes(request))
    result = run_cli("verify", "--kind", "inclusion", "--input", str(good),
                     "--anchor", str(anchor))
    assert result.returncode == 0
    request["digest"] = "0" * 64
    good.write_bytes(lineage.canonical_bytes(request))
    result = run_cli("verify", "--kind", "inclusion", "--input", str(good),
                     "--anchor", str(anchor))
    assert result.returncode == 2


def test_cli_lineage_update_refuses_overwrite(repository):
    root, _anchor = repository
    existing = root / "lineage" / "anchors" / "0000.json"
    result = run_cli("lineage-update", "--root", str(root), "--package", "arithmetic",
                     "--global-seq", "1", "--anchor-out", str(existing))
    assert result.returncode == 2
    assert "Blocked" in result.stdout


def test_cli_key_issue_bad_purpose_blocked(tmp_path):
    output = tmp_path / "record.json"
    result = run_cli("key-issue", "--purpose", "nope", "--home", "h",
                     "--policy-version", "v0", "--output", str(output))
    assert result.returncode == 2
    assert "Blocked" in result.stdout


# --- Phase 1 disclosure boundary --------------------------------------------

def secret_record(seq, slot):
    body = {
        "schema": lineage.RECORD_SCHEMA, "version": 0, "package": "arithmetic",
        "seq": seq, "proposition": "undisclosed-candidate",
        "environment": {"note": "hidden content committed; see secret_slot"},
        "checker": {"id": "merge-residual-v0", "version": "0"},
        "verdict": "Unknown", "residual": None,
        "cites_same_home": [seq - 1] if seq > 1 else [], "cites_cross": [],
        "budget_consumed": {"units": 1}, "secret_slot": slot,
    }
    body["digest"] = lineage.sha256_hex(lineage.canonical_bytes(body))
    return body


def test_phase1_commitment_proof_and_disclosure():
    hidden = {"answer": 14}
    slot, blinding = lineage.build_secret_slot(hidden)
    commitment = int(slot["commitment"]["c"])
    proof = {key: int(value) for key, value in slot["proof"].items()}
    assert lineage.verify_opening(commitment, proof)
    tampered = dict(proof, t=(proof["t"] + 1) % lineage.PHASE1_Q)
    assert not lineage.verify_opening(commitment, tampered)
    assert lineage.verify_disclosure(hidden, blinding, commitment)
    assert not lineage.verify_disclosure({"answer": 15}, blinding, commitment)


def test_phase1_secret_slot_record_on_chain(tmp_path):
    slot, _blinding = lineage.build_secret_slot({"answer": 14})
    write_record(tmp_path, "arithmetic", 1, secret_record(1, slot))
    report = lineage.lineage_update(tmp_path, "arithmetic", 0,
                                    tmp_path / "lineage" / "anchors" / "0000.json")
    assert report["status"] == "CheckpointBuilt"
    anchor = Path(report["anchor"]["path"])
    assert lineage.tamper_check(tmp_path, anchor)["status"] == "Intact"


def test_phase1_broken_proof_and_foreign_group_rejected(tmp_path):
    slot, _blinding = lineage.build_secret_slot({"answer": 14})
    broken = secret_record(1, {
        "commitment": slot["commitment"],
        "proof": dict(slot["proof"], s1="1"),
    })
    with pytest.raises(ValueError):
        lineage.validate_record(broken, seq=1, package="arithmetic")
    foreign = secret_record(1, {
        "commitment": dict(slot["commitment"], q=str(lineage.PHASE1_Q + 6)),
        "proof": slot["proof"],
    })
    with pytest.raises(ValueError):
        lineage.validate_record(foreign, seq=1, package="arithmetic")


def test_cli_verify_disclosure_exit_codes(tmp_path):
    hidden = {"answer": 14}
    slot, blinding = lineage.build_secret_slot(hidden)
    request = {"schema": lineage.DISCLOSURE_REQUEST_SCHEMA, "version": 0,
               "commitment": slot["commitment"], "content": hidden,
               "blinding": str(blinding), "proof": slot["proof"]}
    good = tmp_path / "disclosure.json"
    good.write_bytes(lineage.canonical_bytes(request))
    result = run_cli("verify", "--kind", "disclosure", "--input", str(good))
    assert result.returncode == 0
    request["content"] = {"answer": 15}
    good.write_bytes(lineage.canonical_bytes(request))
    result = run_cli("verify", "--kind", "disclosure", "--input", str(good))
    assert result.returncode == 2
