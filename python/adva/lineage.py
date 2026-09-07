"""Research 0156 Phases 0-1: documentary tamper-evident lineage for finite
arithmetic discovery sequences, with the Phase 1 disclosure boundary.

Scope and boundaries (mirror docs/research/0156-tamper-evident-arithmetic-lineage.md):

- This module is a **documentary integrity adapter**. It hashes, chains and
  pins bytes. It performs **no semantic judgment**: a record whose shape is
  valid here has not been checked as a mathematical statement.
- Stdlib-only (hashlib/json/pathlib/time/secrets). Phase 1 implements the
  disclosure boundary: a record may carry a ``secret_slot`` holding a Pedersen
  commitment plus a Schnorr NIZK (Fiat-Shamir) proof of knowledge of an
  opening. The hidden content never enters the chain in plaintext; after
  disclosure anyone verifies the opening directly. Phase 2 (predicate SNARK)
  is not implemented, and no native Seal is issued.
- The Phase 1 group is a pinned 128-bit safe-prime subgroup (research scale,
  NOT production scale). Its parameters are versioned constants below; the
  second generator's discrete log is derived from a nothing-up-my-sleeve hash
  and is known, which is documented and acceptable only for the disclosure
  boundary where hiding relies on the commitment equation, not on an unknown
  relation. Production use requires an independent group-parameter decision.
- Ed25519 support is provided only when the optional ``cryptography`` package
  is importable (see Research 0155 section 3). Without it, signature-related
  operations report ``Unknown`` with a retained reason, never a fallback
  downgrade to "hash only".

Layout conventions (v0):

- Records: ``<root>/lineage/<package>/records/<seq:06d>.json``, stored as
  canonical JSON bytes; ``seq`` is a positive integer, contiguous from 1.
- Anchors: fresh-only files (any operator-chosen path, conventionally
  ``<root>/lineage/anchors/<global_seq:04d>.json``). An anchor pins one
  checkpoint per package plus a chained ``prev_anchor_sha256``. Moving a
  reviewed anchor into place as "the current anchor" is an operator step;
  there is no automatic resealing command.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import secrets
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

RECORD_SCHEMA = "adva.arithmetic-lineage.record.v0"
CHECKPOINT_SCHEMA = "adva.arithmetic-lineage.checkpoint.v0"
ANCHOR_SCHEMA = "adva.arithmetic-lineage.anchor.v0"
INCLUSION_REQUEST_SCHEMA = "adva.arithmetic-lineage.inclusion-request.v0"
SIGNATURE_REQUEST_SCHEMA = "adva.arithmetic-lineage.signature-request.v0"
TAMPER_REPORT_SCHEMA = "adva.arithmetic-lineage.tamper-report.v0"
VERIFY_REPORT_SCHEMA = "adva.arithmetic-lineage.verify-report.v0"
KEY_ISSUE_RECORD_SCHEMA = "adva.key-issue.record.v0"
KEY_ISSUE_REPORT_SCHEMA = "adva.key-issue.report.v0"
UPDATE_REPORT_SCHEMA = "adva.arithmetic-lineage.update-report.v0"
DISCLOSURE_REQUEST_SCHEMA = "adva.arithmetic-lineage.disclosure-request.v0"

# Phase 1 pinned group parameters (research scale; see module docstring).
# q = 2r + 1 safe prime (128-bit); G, H are generators of the r-order subgroup.
PHASE1_Q = 322872484535397780528067544767737952967
PHASE1_R = 161436242267698890264033772383868976483
PHASE1_G = 25
PHASE1_H = 71533574933411570582921841641289478467

PACKAGES = frozenset({"arithmetic", "geometry", "logic"})
VERDICTS = frozenset({"Verified", "Rejected", "Unknown"})
PURPOSES = frozenset({"anchor-signing"})
BUDGET_KEYS = frozenset({"units", "wall_ms", "bytes_read", "bytes_written"})

GENESIS_TAG = "ali-lineage-v0/genesis"
LINK_TAG = "ali-lineage-v0/link"
LEAF_TAG = "ali-lineage-v0/leaf"
NODE_TAG = "ali-lineage-v0/node"
ANCHOR_TAG = "ali-lineage-v0/anchor"
KEY_ID_TAG = "ali-lineage-v0/key-id"

# Proposal 7.4 candidate budget defaults (documentary checks only).
MAX_RECORDS = 100_000
MAX_FILE_BYTES = 256 * 1024
MAX_TOTAL_BYTES = 64 * 1024 * 1024
MAX_WALL_SECONDS = 5.0
MAX_STRING_CHARS = 4096
MAX_LIST_ITEMS = 16


class BudgetExceeded(Exception):
    """Internal marker for a declared resource bound; surfaced as Unknown."""


class _Budget:
    def __init__(self, *, max_records: int = MAX_RECORDS,
                 max_file_bytes: int = MAX_FILE_BYTES,
                 max_total_bytes: int = MAX_TOTAL_BYTES,
                 max_wall_seconds: float = MAX_WALL_SECONDS) -> None:
        self.max_records = max_records
        self.max_file_bytes = max_file_bytes
        self.max_total_bytes = max_total_bytes
        self.max_wall_seconds = max_wall_seconds
        self.records = 0
        self.total_bytes = 0
        self.wall_ms = 0
        self._deadline = time.monotonic() + max_wall_seconds

    def tick(self, *, count: int = 0, size: int = 0) -> None:
        if count:
            self.records += count
            if self.records > self.max_records:
                raise BudgetExceeded("record count budget exceeded")
        if size:
            self.total_bytes += size
            if self.total_bytes > self.max_total_bytes:
                raise BudgetExceeded("total read budget exceeded")
        if (self.records % 64 == 0 or size) and time.monotonic() > self._deadline:
            raise BudgetExceeded("cooperative wall-time budget exceeded")

    def spent(self) -> dict[str, int]:
        return {
            "units": self.records,
            "wall_ms": max(0, int((time.monotonic() - (self._deadline
                              - self.max_wall_seconds)) * 1000)),
            "bytes_read": self.total_bytes,
        }


# ---------------------------------------------------------------------------
# Canonical serialization
# ---------------------------------------------------------------------------

def canonical_bytes(value: Any, _depth: int = 0) -> bytes:
    """Deterministic UTF-8 JSON bytes for the supported subset.

    Supported: dict[str, ...] (sorted keys), list, str, int (not bool), bool,
    None. Floats are rejected (exact-arithmetic discipline). Duplicate keys are
    impossible here because Python dicts cannot hold them; parsing guards that
    separately (see parse_json).
    """
    if _depth > 32:
        raise ValueError("canonical encoding depth exceeds 32")
    if value is None:
        return b"null"
    if isinstance(value, bool):
        return b"true" if value else b"false"
    if isinstance(value, int):
        return str(value).encode("utf-8")
    if isinstance(value, str):
        return _json_dump(value)
    if isinstance(value, list):
        parts = [canonical_bytes(item, _depth + 1) for item in value]
        return b"[" + b",".join(parts) + b"]"
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise ValueError("canonical encoding requires string keys")
        items = sorted(value.items())
        parts = [(_json_dump(key) + b":"
                  + canonical_bytes(item, _depth + 1)) for key, item in items]
        return b"{" + b",".join(parts) + b"}"
    raise ValueError(f"unsupported canonical type: {type(value).__name__}")


def _json_dump(text: str) -> bytes:
    return json.dumps(text, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def parse_json(raw: bytes) -> Any:
    """Parse JSON bytes, refusing duplicate keys and non-finite constants."""

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def constant(value: str) -> None:
        raise ValueError("non-finite JSON constant")

    return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                      parse_constant=constant)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hash(*items: Any) -> str:
    return sha256_hex(canonical_bytes(list(items)))


# ---------------------------------------------------------------------------
# Strict shape validators (math_catalog style)
# ---------------------------------------------------------------------------

def _fail(context: str, message: str) -> ValueError:
    return ValueError(f"{context}: {message}")


def _object(value: Any, keys: frozenset[str], context: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise _fail(context, "expected an object with string keys")
    unknown = set(value) - keys
    if unknown:
        raise _fail(context, f"unexpected keys: {sorted(unknown)}")
    return value


def _text(value: Any, context: str, *, maximum: int = MAX_STRING_CHARS) -> str:
    if not isinstance(value, str):
        raise _fail(context, "expected a string")
    if not value or len(value) > maximum:
        raise _fail(context, "string must be non-empty and within length bound")
    return value


def _hex(value: Any, context: str, length: int) -> str:
    text = _text(value, context, maximum=length)
    if len(text) != length or any(c not in "0123456789abcdef" for c in text):
        raise _fail(context, f"expected {length} lowercase hex characters")
    return text


def _nonnegative_int(value: Any, context: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise _fail(context, "expected a non-negative integer")
    return value


def _string_list(value: Any, context: str) -> list[str]:
    if not isinstance(value, list) or len(value) > MAX_LIST_ITEMS:
        raise _fail(context, "expected a bounded list")
    return [_text(item, context) for item in value]


def _seq_list(value: Any, context: str, *, bound: int) -> list[int]:
    if not isinstance(value, list) or len(value) > MAX_LIST_ITEMS:
        raise _fail(context, "expected a bounded list")
    result = []
    for item in value:
        number = _nonnegative_int(item, context)
        if not 1 <= number < bound:
            raise _fail(context, f"citation seq must be in [1, {bound - 1}]")
        if result and number <= result[-1]:
            raise _fail(context, "citations must be strictly increasing")
        result.append(number)
    return result


# ---------------------------------------------------------------------------
# Record validation (L0 shape; no semantic judgment)
# ---------------------------------------------------------------------------

def validate_record(value: Any, *, seq: int, package: str) -> dict[str, Any]:
    context = f"record {package}/{seq}"
    record = _object(value, frozenset({
        "schema", "version", "package", "seq", "proposition", "environment",
        "checker", "verdict", "residual", "cites_same_home", "cites_cross",
        "budget_consumed", "secret_slot", "digest",
    }), context)
    if record.get("schema") != RECORD_SCHEMA:
        raise _fail(context, "schema mismatch")
    if record.get("version") != 0:
        raise _fail(context, "only version 0 is supported")
    if record.get("package") != package:
        raise _fail(context, "package does not match its chain")
    if record.get("seq") != seq:
        raise _fail(context, "seq does not match its file position")
    _text(record.get("proposition"), f"{context}.proposition")

    environment = record.get("environment")
    if not isinstance(environment, dict) or not all(
            isinstance(name, str) for name in environment):
        raise _fail(f"{context}.environment", "expected an object with string keys")
    if len(environment) > MAX_LIST_ITEMS:
        raise _fail(f"{context}.environment", "too many bindings")
    for name, binding in environment.items():
        _text(name, f"{context}.environment key")
        if isinstance(binding, bool) or not isinstance(binding, (str, int)):
            raise _fail(f"{context}.environment", "bindings must be strings or integers")

    checker = _object(record.get("checker"), frozenset({"id", "version"}), f"{context}.checker")
    _text(checker.get("id"), f"{context}.checker.id")
    _text(checker.get("version"), f"{context}.checker.version")

    if record.get("verdict") not in VERDICTS:
        raise _fail(context, f"verdict must be one of {sorted(VERDICTS)}")
    residual = record.get("residual")
    if residual is not None:
        _text(residual, f"{context}.residual", maximum=1024)

    _seq_list(record.get("cites_same_home"), f"{context}.cites_same_home", bound=seq)
    cross: list[Any] = record.get("cites_cross")
    if not isinstance(cross, list) or len(cross) > MAX_LIST_ITEMS:
        raise _fail(f"{context}.cites_cross", "expected a bounded list")
    previous: tuple[str, int] | None = None
    for item in cross:
        cite = _object(item, frozenset({"package", "seq", "digest"}), f"{context}.cites_cross")
        if cite.get("package") not in PACKAGES:
            raise _fail(f"{context}.cites_cross", "unknown cited package")
        cited_seq = _nonnegative_int(cite.get("seq"), f"{context}.cites_cross")
        _hex(cite.get("digest"), f"{context}.cites_cross", 64)
        order = (cite["package"], cited_seq)
        if previous is not None and order <= previous:
            raise _fail(f"{context}.cites_cross", "citations must be strictly ordered")
        previous = order

    budget = _object(record.get("budget_consumed"), BUDGET_KEYS, f"{context}.budget_consumed")
    if "units" not in budget:
        raise _fail(f"{context}.budget_consumed", "units is required")
    for key, amount in budget.items():
        _nonnegative_int(amount, f"{context}.budget_consumed.{key}")

    if "secret_slot" in record:
        slot = record["secret_slot"]
        if slot is not None:
            _validate_secret_slot(slot, context)

    digest = _hex(record.get("digest"), f"{context}.digest", 64)
    body = {key: value for key, value in record.items() if key != "digest"}
    if sha256_hex(canonical_bytes(body)) != digest:
        raise _fail(context, "digest does not match its record content")
    return record


def _record_file_name(seq: int) -> str:
    return f"{seq:06d}.json"


def records_dir(root: Path, package: str) -> Path:
    return root / "lineage" / package / "records"


def read_record_bytes(root: Path, package: str, seq: int, budget: _Budget) -> bytes:
    path = records_dir(root, package) / _record_file_name(seq)
    budget.tick(count=1)
    if not path.is_file():
        raise FileNotFoundError(str(path))
    raw = path.read_bytes()
    if len(raw) > budget.max_file_bytes:
        raise BudgetExceeded(f"file exceeds byte bound: {path}")
    budget.tick(size=len(raw))
    return raw


# ---------------------------------------------------------------------------
# Hash chain
# ---------------------------------------------------------------------------

def genesis_hash(package: str) -> str:
    if package not in PACKAGES:
        raise ValueError(f"unknown package: {package}")
    return _hash(GENESIS_TAG, package)


def chain_link_hash(prev: str, package: str, seq: int, digest: str,
                    cites_cross: list[dict[str, Any]]) -> str:
    return _hash(LINK_TAG, prev, package, seq, digest, cites_cross)


def compute_chain(package: str, count: int,
                  read: Callable[[int], tuple[bytes, dict[str, Any]]]) -> dict[str, Any]:
    """Recompute the full chain from records 1..count.

    ``read(seq)`` returns (raw file bytes, parsed record) and raises
    BudgetExceeded / FileNotFoundError / ValueError as needed. This function
    returns the aggregate chain state and the per-link ledger; it does not
    compare against any stored expectation (see tamper_check for divergence).
    """
    head = genesis_hash(package)
    links: list[dict[str, Any]] = []
    digests: list[str] = []
    for seq in range(1, count + 1):
        _raw, record = read(seq)
        digest = record["digest"]
        head = chain_link_hash(head, package, seq, digest, record["cites_cross"])
        links.append({"seq": seq, "digest": digest, "chain_sha256": head})
        digests.append(digest)
    merkle_root, height = merkle_root_and_height(digests)
    return {
        "package": package,
        "count": count,
        "last_seq": count,
        "chain_head": head,
        "merkle_root": merkle_root,
        "height": height,
        "links": links,
    }


# ---------------------------------------------------------------------------
# Merkle tree over record digests
# ---------------------------------------------------------------------------

def _merkle_leaf(index: int, digest: str) -> str:
    return _hash(LEAF_TAG, index, digest)


def _merkle_node(left: str, right: str) -> str:
    return _hash(NODE_TAG, left, right)


def merkle_root_and_height(digests: list[str]) -> tuple[str, int]:
    if not digests:
        return _merkle_node(_merkle_leaf(0, "0" * 64), _merkle_leaf(1, "0" * 64)), 0
    level = [_merkle_leaf(index, digest) for index, digest in enumerate(digests)]
    height = 1
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [_merkle_node(level[i], level[i + 1]) for i in range(0, len(level), 2)]
        height += 1
    return level[0], height


def inclusion_proof(digests: list[str], seq: int) -> dict[str, Any]:
    """Proof that the record at ``seq`` (1-based) is a leaf of the tree."""
    if not 1 <= seq <= len(digests):
        raise ValueError("seq outside the digest list")
    index = seq - 1
    level = [_merkle_leaf(i, digest) for i, digest in enumerate(digests)]
    path: list[dict[str, str]] = []
    cursor = index
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        sibling = cursor ^ 1
        path.append({"dir": "L" if sibling < cursor else "R",
                     "hash": level[sibling]})
        cursor //= 2
        level = [_merkle_node(level[i], level[i + 1]) for i in range(0, len(level), 2)]
    return {"seq": seq, "digest": digests[index], "path": path}


def verify_inclusion(root: str, proof: dict[str, Any]) -> bool:
    digest = _hex(proof.get("digest"), "inclusion proof", 64)
    seq = _nonnegative_int(proof.get("seq"), "inclusion proof")
    if seq < 1:
        return False
    cursor = _merkle_leaf(seq - 1, digest)
    path = proof.get("path")
    if not isinstance(path, list) or len(path) > 64:
        return False
    for step in path:
        if not isinstance(step, dict):
            return False
        direction = step.get("dir")
        sibling = step.get("hash")
        if direction not in ("L", "R") or not isinstance(sibling, str) \
                or len(sibling) != 64:
            return False
        if direction == "L":
            cursor = _merkle_node(sibling, cursor)
        else:
            cursor = _merkle_node(cursor, sibling)
    return cursor == root


# ---------------------------------------------------------------------------
# Checkpoints and anchors
# ---------------------------------------------------------------------------

def build_checkpoint(chain: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": CHECKPOINT_SCHEMA,
        "version": 0,
        "package": chain["package"],
        "merkle_root": chain["merkle_root"],
        "chain_head": chain["chain_head"],
        "count": chain["count"],
        "last_seq": chain["last_seq"],
        "height": chain["height"],
    }


def validate_checkpoint(value: Any) -> dict[str, Any]:
    context = "checkpoint"
    checkpoint = _object(value, frozenset({
        "schema", "version", "package", "merkle_root", "chain_head",
        "count", "last_seq", "height",
    }), context)
    if checkpoint.get("schema") != CHECKPOINT_SCHEMA or checkpoint.get("version") != 0:
        raise _fail(context, "schema mismatch")
    if checkpoint.get("package") not in PACKAGES:
        raise _fail(context, "unknown package")
    _hex(checkpoint.get("merkle_root"), f"{context}.merkle_root", 64)
    _hex(checkpoint.get("chain_head"), f"{context}.chain_head", 64)
    count = _nonnegative_int(checkpoint.get("count"), f"{context}.count")
    last_seq = _nonnegative_int(checkpoint.get("last_seq"), f"{context}.last_seq")
    height = _nonnegative_int(checkpoint.get("height"), f"{context}.height")
    if count != last_seq:
        raise _fail(context, "count and last_seq must agree")
    if count > MAX_RECORDS:
        raise _fail(context, "count exceeds declared bound")
    if height > 64:
        raise _fail(context, "height exceeds declared bound")
    return checkpoint


def anchor_hash(anchor: dict[str, Any]) -> str:
    """Hash of an anchor's pinned content, excluding self_sha256/signatures."""
    return _hash(ANCHOR_TAG, anchor["global_seq"], anchor["checkpoints"],
                 anchor["prev_anchor_sha256"])


def build_anchor(global_seq: int, checkpoints: dict[str, Any | None],
                 prev_anchor_sha256: str) -> dict[str, Any]:
    anchor = {
        "schema": ANCHOR_SCHEMA,
        "version": 0,
        "global_seq": global_seq,
        "checkpoints": {package: checkpoints.get(package) for package in sorted(PACKAGES)},
        "prev_anchor_sha256": prev_anchor_sha256,
        "signatures": [],
        "self_sha256": "",
    }
    anchor["self_sha256"] = anchor_hash(anchor)
    return anchor


def validate_anchor(value: Any) -> dict[str, Any]:
    context = "anchor"
    anchor = _object(value, frozenset({
        "schema", "version", "global_seq", "checkpoints", "prev_anchor_sha256",
        "signatures", "self_sha256",
    }), context)
    if anchor.get("schema") != ANCHOR_SCHEMA or anchor.get("version") != 0:
        raise _fail(context, "schema mismatch")
    _nonnegative_int(anchor.get("global_seq"), f"{context}.global_seq")
    checkpoints = _object(anchor.get("checkpoints"), frozenset(PACKAGES), f"{context}.checkpoints")
    if not any(checkpoints.get(package) is not None for package in sorted(PACKAGES)):
        raise _fail(f"{context}.checkpoints", "at least one checkpoint is required")
    for package in sorted(PACKAGES):
        if checkpoints[package] is not None:
            validate_checkpoint(checkpoints[package])
    previous = anchor.get("prev_anchor_sha256")
    if previous not in ("", None):
        _hex(previous, f"{context}.prev_anchor_sha256", 64)
    signatures = anchor.get("signatures")
    if not isinstance(signatures, list) or len(signatures) > MAX_LIST_ITEMS:
        raise _fail(f"{context}.signatures", "expected a bounded list")
    for signature in signatures:
        _object(signature, frozenset({"key_id", "pubkey_hex", "signature_hex"}),
                f"{context}.signatures")
    self_hash = _hex(anchor.get("self_sha256"), f"{context}.self_sha256", 64)
    if anchor_hash(anchor) != self_hash:
        raise _fail(context, "self_sha256 does not match its anchor content")
    return anchor


# ---------------------------------------------------------------------------
# Ed25519 backend (optional, Research 0155 section 3 discipline)
# ---------------------------------------------------------------------------

def _ed25519_backend() -> Any | None:
    try:
        from cryptography.exceptions import (
            InvalidSignature,  # type: ignore[import-not-found]
        )
        from cryptography.hazmat.primitives import (
            serialization,  # type: ignore[import-not-found]
        )
        from cryptography.hazmat.primitives.asymmetric import (
            ed25519,  # type: ignore[import-not-found]
        )
        return ed25519, serialization, InvalidSignature
    except ImportError:
        return None


def backend_available() -> bool:
    return _ed25519_backend() is not None


def generate_signing_keypair() -> tuple[str, str]:
    """Return (private_seed_hex, public_key_hex); requires the optional backend."""
    backend = _ed25519_backend()
    if backend is None:
        raise BudgetExceeded("ed25519 backend missing; no fallback signing is provided")
    ed25519, serialization, _invalid = backend
    private = ed25519.Ed25519PrivateKey.generate()
    public = private.public_key()
    raw_public = public.public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    raw_seed = private.private_bytes(
        serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
        serialization.NoEncryption())
    return raw_seed.hex(), raw_public.hex()


def key_id_for(pubkey_hex: str) -> str:
    public = _hex(pubkey_hex, "pubkey_hex", 64)
    return "ed25519:" + sha256_hex(canonical_bytes([KEY_ID_TAG, public]))[:32]


def verify_ed25519(pubkey_hex: str, message: Any, signature_hex: str) -> bool:
    backend = _ed25519_backend()
    if backend is None:
        raise BudgetExceeded("ed25519 backend missing; verification not attempted")
    ed25519, _serialization, invalid_signature = backend
    public = _hex(pubkey_hex, "pubkey_hex", 64)
    signature = bytes.fromhex(_hex(signature_hex, "signature_hex", 128))
    key = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(public))
    try:
        key.verify(signature, canonical_bytes(message))
    except invalid_signature:
        return False
    return True


def sign_ed25519(private_seed_hex: str, message: Any) -> str:
    backend = _ed25519_backend()
    if backend is None:
        raise BudgetExceeded("ed25519 backend missing; signing not attempted")
    ed25519, _serialization, _invalid = backend
    seed = bytes.fromhex(_hex(private_seed_hex, "private_seed_hex", 64))
    private = ed25519.Ed25519PrivateKey.from_private_bytes(seed)
    return private.sign(canonical_bytes(message)).hex()


# ---------------------------------------------------------------------------
# Phase 1 disclosure boundary: Pedersen commitments + Schnorr NIZK
# ---------------------------------------------------------------------------

def _decimal(value: Any, context: str) -> int:
    text = _text(value, context, maximum=64)
    if not text.isdigit() or (len(text) > 1 and text[0] == "0"):
        raise _fail(context, "expected a canonical decimal string without leading zeros")
    return int(text)


def content_hash(content: Any) -> int:
    """Hash canonical bytes of a JSON document into the Phase 1 exponent range."""
    digest = hashlib.sha256(canonical_bytes(content)).digest()
    return int.from_bytes(digest, "big") % PHASE1_R


def commit_content(content: Any, blinding: int | None = None) -> tuple[int, int]:
    """Pedersen commitment C = G^{H(content)} * H^{blinding} (mod Q).

    Returns (C, blinding); a fresh blinding is drawn from the system CSPRNG
    when none is supplied. The blinding must remain secret until disclosure.
    """
    if blinding is None:
        blinding = secrets.randbelow(PHASE1_R - 1) + 1
    if not 1 <= blinding < PHASE1_R:
        raise ValueError("blinding must be in [1, R)")
    value = pow(PHASE1_G, content_hash(content), PHASE1_Q) * \
        pow(PHASE1_H, blinding, PHASE1_Q) % PHASE1_Q
    return value, blinding


def _challenge(*values: Any) -> int:
    digest = hashlib.sha256(
        canonical_bytes([str(value) for value in values])).digest()
    return int.from_bytes(digest, "big") % PHASE1_R


def prove_opening(content: Any, blinding: int) -> dict[str, int]:
    """Schnorr NIZK (Fiat-Shamir) of knowledge of an opening (m, b) of C."""
    commitment, _ = commit_content(content, blinding)
    k1 = secrets.randbelow(PHASE1_R - 1) + 1
    k2 = secrets.randbelow(PHASE1_R - 1) + 1
    t = pow(PHASE1_G, k1, PHASE1_Q) * pow(PHASE1_H, k2, PHASE1_Q) % PHASE1_Q
    challenge = _challenge(PHASE1_Q, PHASE1_G, PHASE1_H, commitment, t)
    s1 = (k1 + challenge * content_hash(content)) % PHASE1_R
    s2 = (k2 + challenge * blinding) % PHASE1_R
    return {"t": t, "s1": s1, "s2": s2}


def verify_opening(commitment: int, proof: dict[str, int]) -> bool:
    """Public verification that the prover knows an opening of ``commitment``."""
    t, s1, s2 = proof["t"], proof["s1"], proof["s2"]
    if not (1 <= t < PHASE1_Q and 0 <= s1 < PHASE1_R and 0 <= s2 < PHASE1_R):
        return False
    challenge = _challenge(PHASE1_Q, PHASE1_G, PHASE1_H, commitment, t)
    left = pow(PHASE1_G, s1, PHASE1_Q) * pow(PHASE1_H, s2, PHASE1_Q) % PHASE1_Q
    right = t * pow(commitment, challenge, PHASE1_Q) % PHASE1_Q
    return left == right


def verify_disclosure(content: Any, blinding: int, commitment: int) -> bool:
    """Direct opening check after disclosure: C == G^{H(content)} * H^{blinding}."""
    expected, _ = commit_content(content, blinding)
    return expected == commitment


def build_secret_slot(content: Any, blinding: int | None = None) -> tuple[dict[str, Any], int]:
    """Build a record secret_slot for hidden content; returns (slot, blinding).

    The slot holds only the commitment and the public NIZK; the blinding and
    the content stay with the discloser until the disclosure step.
    """
    commitment, blinding = commit_content(content, blinding)
    proof = prove_opening(content, blinding)
    slot = {
        "commitment": {"q": str(PHASE1_Q), "g": str(PHASE1_G),
                       "h": str(PHASE1_H), "c": str(commitment)},
        "proof": {"t": str(proof["t"]), "s1": str(proof["s1"]),
                  "s2": str(proof["s2"])},
    }
    return slot, blinding


def _validate_secret_slot(slot: Any, context: str) -> None:
    """Validate a record secret_slot: pinned group, well-formed, proof verifies."""
    target = _object(slot, frozenset({"commitment", "proof"}), f"{context}.secret_slot")
    commitment = _object(target.get("commitment"), frozenset({"q", "g", "h", "c"}),
                         f"{context}.secret_slot.commitment")
    q = _decimal(commitment.get("q"), f"{context}.secret_slot.commitment.q")
    g = _decimal(commitment.get("g"), f"{context}.secret_slot.commitment.g")
    h = _decimal(commitment.get("h"), f"{context}.secret_slot.commitment.h")
    c = _decimal(commitment.get("c"), f"{context}.secret_slot.commitment.c")
    if (q, g, h) != (PHASE1_Q, PHASE1_G, PHASE1_H):
        raise _fail(context, "secret_slot group parameters must equal the pinned Phase 1 constants")
    proof = _object(target.get("proof"), frozenset({"t", "s1", "s2"}),
                    f"{context}.secret_slot.proof")
    t = _decimal(proof.get("t"), f"{context}.secret_slot.proof.t")
    s1 = _decimal(proof.get("s1"), f"{context}.secret_slot.proof.s1")
    s2 = _decimal(proof.get("s2"), f"{context}.secret_slot.proof.s2")
    if not verify_opening(c, {"t": t, "s1": s1, "s2": s2}):
        raise _fail(context, "secret_slot NIZK proof does not verify against the commitment")


# ---------------------------------------------------------------------------
# tamper-check
# ---------------------------------------------------------------------------

def tamper_check(root: Path, anchor_path: Path, *,
                 prev_anchor_path: Path | None = None,
                 budget: _Budget | None = None) -> dict[str, Any]:
    budget = budget or _Budget()
    report: dict[str, Any] = {
        "schema": TAMPER_REPORT_SCHEMA,
        "version": 0,
        "status": "Intact",
        "anchor": {"path": str(anchor_path), "match": None,
                   "prev_anchor_match": None},
        "packages": {},
        "budget_spent": budget.spent(),
    }
    try:
        raw = anchor_path.read_bytes()
        budget.tick(size=len(raw))
        anchor = validate_anchor(parse_json(raw))
    except FileNotFoundError:
        report.update(status="Unknown", reason="anchor file missing")
        return report
    except ValueError as error:
        report.update(status="Tampered",
                      anchor={"path": str(anchor_path), "match": False,
                              "reason": f"anchor invalid: {error}",
                              "prev_anchor_match": None})
        return report
    report["anchor"] = {
        "path": str(anchor_path),
        "global_seq": anchor["global_seq"],
        "match": True,
        "prev_anchor_match": None,
    }
    if prev_anchor_path is not None:
        try:
            previous = validate_anchor(parse_json(prev_anchor_path.read_bytes()))
        except ValueError as error:
            report.update(status="Tampered",
                          reason=f"prev anchor invalid: {error}")
            return report
        except FileNotFoundError as error:
            report.update(status="Unknown",
                          reason=f"prev anchor missing: {error}")
            return report
        match = previous["self_sha256"] == anchor["prev_anchor_sha256"]
        report["anchor"]["prev_anchor_match"] = match
        if not match:
            report.update(status="Tampered", reason="prev_anchor mismatch")
            return report

    first_divergence: dict[str, Any] | None = None
    try:
        for package in sorted(PACKAGES):
            checkpoint = anchor["checkpoints"].get(package)
            if checkpoint is None:
                report["packages"][package] = {"checkpoint": None, "records": 0,
                                               "first_divergence": None,
                                               "checkpoint_match": None}
                continue
            package_report = _check_package(root, package, checkpoint, budget)
            report["packages"][package] = package_report
            if package_report["first_divergence"] is not None \
                    or not package_report["checkpoint_match"]:
                first_divergence = package_report["first_divergence"]
                if first_divergence is None:
                    first_divergence = package_report["checkpoint_diff"]
    except BudgetExceeded as error:
        report.update(status="Unknown", reason=str(error),
                      budget_spent=budget.spent())
        return report
    if first_divergence is not None:
        report.update(status="Tampered", first_divergence=first_divergence)
    report["budget_spent"] = budget.spent()
    return report


def _check_package(root: Path, package: str, checkpoint: dict[str, Any],
                   budget: _Budget) -> dict[str, Any]:
    directory = records_dir(root, package)
    if checkpoint["count"] > 0 and not directory.is_dir():
        return {"checkpoint": checkpoint, "records": 0, "first_divergence": {
            "seq": 1, "kind": "missing-directory", "expected": "records dir",
            "actual": None}, "checkpoint_match": False, "checkpoint_diff": None}

    def read(seq: int) -> tuple[bytes, dict[str, Any]]:
        raw = read_record_bytes(root, package, seq, budget)
        record = parse_json(raw)
        if canonical_bytes(record) != raw:
            raise _fail(f"record {package}/{seq}", "file bytes are not canonical")
        return raw, validate_record(record, seq=seq, package=package)

    chain: dict[str, Any] | None = None
    divergence: dict[str, Any] | None = None
    try:
        for seq in range(1, checkpoint["count"] + 1):
            raw = read_record_bytes(root, package, seq, budget)
            try:
                record = validate_record(parse_json(raw), seq=seq, package=package)
            except ValueError as error:
                divergence = {"seq": seq, "kind": "invalid-record",
                              "reason": str(error)}
                break
            if canonical_bytes(record) != raw:
                divergence = {"seq": seq, "kind": "non-canonical-file",
                              "expected": "canonical bytes", "actual": "modified bytes"}
                break
        if divergence is None:
            chain = compute_chain(package, checkpoint["count"], read)
    except FileNotFoundError as error:
        path = Path(str(error))
        try:
            seq = int(path.stem)
        except ValueError:
            seq = checkpoint["count"] + 1
        divergence = {"seq": seq, "kind": "missing-record", "expected": str(path),
                      "actual": None}
    except BudgetExceeded:
        raise
    except ValueError as error:
        divergence = {"seq": None, "kind": "invalid-record", "reason": str(error)}

    if chain is None:
        return {"checkpoint": checkpoint, "records": checkpoint["count"],
                "first_divergence": divergence, "checkpoint_match": False,
                "checkpoint_diff": None}
    mismatch = []
    for field in ("count", "last_seq", "chain_head", "merkle_root", "height"):
        if chain[field] != checkpoint[field]:
            mismatch.append({"field": field, "expected": checkpoint[field],
                             "actual": chain[field]})
    return {"checkpoint": checkpoint, "records": chain["count"],
            "first_divergence": divergence, "checkpoint_match": not mismatch,
            "checkpoint_diff": mismatch or None}


# ---------------------------------------------------------------------------
# verify (inclusion / signature)
# ---------------------------------------------------------------------------

def verify(kind: str, input_path: Path, *, anchor_path: Path | None = None,
           budget: _Budget | None = None) -> dict[str, Any]:
    budget = budget or _Budget()
    report: dict[str, Any] = {
        "schema": VERIFY_REPORT_SCHEMA, "version": 0, "kind": kind,
        "status": "Unknown", "detail": None, "budget_spent": budget.spent(),
    }
    try:
        raw = input_path.read_bytes()
        budget.tick(size=len(raw))
        document = parse_json(raw)
        if kind == "inclusion":
            if anchor_path is None:
                report.update(reason="--anchor is required for inclusion checks")
                return report
            anchor = validate_anchor(parse_json(anchor_path.read_bytes()))
            request = _object(document, frozenset({
                "schema", "version", "package", "seq", "digest", "path",
            }), "inclusion request")
            if request.get("schema") != INCLUSION_REQUEST_SCHEMA \
                    or request.get("version") != 0:
                raise _fail("inclusion request", "schema mismatch")
            package = request.get("package")
            checkpoint = anchor["checkpoints"].get(package)
            if checkpoint is None:
                report.update(status="Unknown",
                              reason=f"no checkpoint for package {package}")
                return report
            proof = {"seq": request.get("seq"), "digest": request.get("digest"),
                     "path": request.get("path")}
            ok = verify_inclusion(checkpoint["merkle_root"], proof)
            report.update(status="Verified" if ok else "Rejected",
                          detail={"root": checkpoint["merkle_root"]})
            return report
        if kind == "signature":
            request = _object(document, frozenset({
                "schema", "version", "key_id", "pubkey_hex", "message",
                "signature_hex",
            }), "signature request")
            if request.get("schema") != SIGNATURE_REQUEST_SCHEMA \
                    or request.get("version") != 0:
                raise _fail("signature request", "schema mismatch")
            if not backend_available():
                report.update(status="Unknown",
                              reason="ed25519 backend missing (stdlib-only runtime)")
                return report
            ok = verify_ed25519(request.get("pubkey_hex"), request.get("message"),
                                request.get("signature_hex"))
            report.update(status="Verified" if ok else "Rejected",
                          detail={"key_id": request.get("key_id")})
            return report
        if kind == "disclosure":
            request = _object(document, frozenset({
                "schema", "version", "commitment", "content", "blinding", "proof",
            }), "disclosure request")
            if request.get("schema") != DISCLOSURE_REQUEST_SCHEMA \
                    or request.get("version") != 0:
                raise _fail("disclosure request", "schema mismatch")
            _validate_secret_slot(
                {"commitment": request.get("commitment"),
                 "proof": request.get("proof")}, "disclosure request")
            commitment = int(request["commitment"]["c"])
            blinding = _decimal(request.get("blinding"), "disclosure request.blinding")
            ok = verify_disclosure(request.get("content"), blinding, commitment)
            report.update(status="Verified" if ok else "Rejected",
                          detail={"commitment_c": request["commitment"]["c"]})
            return report
        raise ValueError(f"unknown verify kind: {kind}")
    except BudgetExceeded as error:
        report.update(status="Unknown", reason=str(error),
                      budget_spent=budget.spent())
        return report
    except FileNotFoundError as error:
        report.update(status="Unknown", reason=f"input missing: {error}")
        return report
    except (ValueError, json.JSONDecodeError) as error:
        report.update(status="Rejected", reason=str(error))
        return report
    finally:
        report["budget_spent"] = budget.spent()


# ---------------------------------------------------------------------------
# key-issue
# ---------------------------------------------------------------------------

def key_issue(*, purpose: str, home: str, policy_version: str,
              private_out: Path | None = None,
              budget: _Budget | None = None) -> dict[str, Any]:
    budget = budget or _Budget()
    report: dict[str, Any] = {
        "schema": KEY_ISSUE_REPORT_SCHEMA, "version": 0, "status": "Issued",
        "record": None, "reason": None, "budget_spent": budget.spent(),
    }
    if purpose not in PURPOSES:
        report.update(status="Blocked", reason=f"undeclared purpose: {purpose}")
        return report
    _text(home, "key-issue home")
    _text(policy_version, "key-issue policy version")
    if not backend_available():
        report.update(status="Unknown",
                      reason="ed25519 backend missing; no key generation without it")
        return report
    seed, public = generate_signing_keypair()
    record: dict[str, Any] = {
        "schema": KEY_ISSUE_RECORD_SCHEMA, "version": 0, "purpose": purpose,
        "home": home, "policy_version": policy_version,
        "key_id": key_id_for(public), "pubkey_hex": public,
        "note": ("public record only; the private seed is never retained here. "
                 "Custody, rotation and revocation follow Research 0155 "
                 "section 6.2 and remain operator responsibilities."),
    }
    if private_out is not None:
        if private_out.exists() or private_out.is_symlink():
            report.update(status="Blocked",
                          reason="--private-out must be a fresh path")
            return report
        private_out.write_bytes((seed + "\n").encode("utf-8"))
        with contextlib.suppress(OSError):
            private_out.chmod(0o600)
    report["record"] = record
    report["budget_spent"] = budget.spent()
    return report


# ---------------------------------------------------------------------------
# lineage-update (checkpoint/anchor builder; never reseals in place)
# ---------------------------------------------------------------------------

def lineage_update(root: Path, package: str, global_seq: int,
                   anchor_out: Path, *, budget: _Budget | None = None) -> dict[str, Any]:
    budget = budget or _Budget()
    report: dict[str, Any] = {
        "schema": UPDATE_REPORT_SCHEMA, "version": 0, "status": "CheckpointBuilt",
        "anchor": None, "reason": None, "budget_spent": budget.spent(),
    }
    if package not in PACKAGES:
        report.update(status="Blocked", reason=f"unknown package: {package}")
        return report
    if anchor_out.exists() or anchor_out.is_symlink():
        report.update(status="Blocked", reason="--anchor-out must be a fresh path")
        return report
    try:
        directory = records_dir(root, package)
        if not directory.is_dir():
            report.update(status="Unknown",
                          reason=f"records dir missing: {directory}")
            return report
        count = 0
        for path in sorted(directory.iterdir()):
            if path.is_file() and path.name.endswith(".json"):
                count += 1
        if count == 0:
            report.update(status="Unknown", reason="no records found")
            return report

        def read(seq: int) -> tuple[bytes, dict[str, Any]]:
            raw = read_record_bytes(root, package, seq, budget)
            record = parse_json(raw)
            if canonical_bytes(record) != raw:
                raise _fail(f"record {package}/{seq}", "file bytes are not canonical")
            return raw, validate_record(record, seq=seq, package=package)

        chain = compute_chain(package, count, read)
        checkpoint = build_checkpoint(chain)
        checkpoints: dict[str, Any | None] = {name: None for name in sorted(PACKAGES)}
        checkpoints[package] = checkpoint
        anchors_dir = root / "lineage" / "anchors"
        previous: dict[str, Any] | None = None
        if anchors_dir.is_dir():
            for path in sorted(anchors_dir.iterdir()):
                if path.is_file() and path.name.endswith(".json"):
                    candidate = validate_anchor(parse_json(path.read_bytes()))
                    if previous is None or candidate["global_seq"] > previous["global_seq"]:
                        previous = candidate
        prev_hash = previous["self_sha256"] if previous is not None else ""
        anchor = build_anchor(global_seq, checkpoints, prev_hash)
        anchor_out.parent.mkdir(parents=True, exist_ok=True)
        anchor_out.write_bytes(canonical_bytes(anchor))
        report["anchor"] = {"path": str(anchor_out), "global_seq": global_seq,
                            "self_sha256": anchor["self_sha256"],
                            "prev_anchor_sha256": prev_hash,
                            "checkpoints": checkpoints}
    except BudgetExceeded as error:
        report.update(status="Unknown", reason=str(error),
                      budget_spent=budget.spent())
        return report
    except (ValueError, OSError) as error:
        report.update(status="Blocked", reason=str(error))
        return report
    report["budget_spent"] = budget.spent()
    return report


# ---------------------------------------------------------------------------
# Shared exit-code mapping (documentary checks; no semantic authority)
# ---------------------------------------------------------------------------

def exit_code(status: str) -> int:
    if status in ("Intact", "Verified", "Issued", "CheckpointBuilt"):
        return 0
    if status in ("Tampered", "Rejected", "Blocked"):
        return 2
    return 3
