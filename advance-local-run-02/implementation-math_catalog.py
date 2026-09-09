"""Read-only math topic catalog checks, never proof or semantic admission.

Only the six named catalog/checkpoint files and their declared references are
read. Referenced content is hashed, not parsed, imported, evaluated or executed.
Catalog keys and SHA256 values are documentary coordinates, not semantic IDs.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import time
from contextlib import ExitStack
from pathlib import Path
from typing import Any

CATALOG = "adva-library/math"
TOPICS = ("arithmetic", "geometry", "logic")
GEOMETRY_ROOT = "pascal-research-presentations"
GROWTH_OBLIGATION_SHA256 = "8f3f457b4991752ec1284968c8e36feffb0ce59aa96d6f63993c3f98396a2c03"
PASCAL_MATERIALS = {
    "adva-library/pascal-task.adva": (
        "60d3ca374486239afb82bbe31d821a4d0c02ef947ccf62557753e85137087a5d"
    ),
    "adva-library/pascal-witness.adva": (
        "f20338add39c292db6bac482a2c9265353d6a5a1a5189cc2823398ddc29fe448"
    ),
}
RESERVED_HOMES = {
    "polynomial-shadow-epochs": "arithmetic",
    "composite-proposal-recipes": "arithmetic",
    "three-verifier-arithmetic-calibration": "arithmetic",
    "frozen-policy-campaign": "arithmetic",
    GEOMETRY_ROOT: "geometry",
    "q4-m6-relation-presentations": "geometry",
    "fixed-checking-rule-boundary": "logic",
    "logic-as-research-content": "logic",
}
POLICY = {
    "authority": "documentary-only",
    "native_admission": "not-granted",
    "logic_role": "research-object-not-checker-override",
}
STATUSES = frozenset(
    {
        "proposed-document",
        "research-hypothesis",
        "checked-research-snapshot",
        "replayable-proposal-journal",
        "external-calibration-record",
        "bounded-research-evidence",
        "finite-policy-evidence",
        "checker-boundary-description",
    }
)
UNCHECKED_STATUSES = frozenset({"proposed-document", "research-hypothesis"})
LIMITS = {
    "entries": 32,
    "references": 256,
    "files": 96,
    "metadata_bytes_each": 262_144,
    "reference_bytes_each": 8 * 1024 * 1024,
    "total_read_bytes": 32 * 1024 * 1024,
    "cooperative_seconds": 5,
}


class CatalogLimitError(Exception):
    """The bounded metadata check did not finish; this is not invalidity."""


def _object(value: Any, keys: set[str], context: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError(f"{context}: missing or unknown fields")
    return value


def _text(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 4096:
        raise ValueError(f"{context}: expected nonempty bounded text")
    return value


def _array(value: Any, context: str, maximum: int = 16, *, empty: bool = False) -> list[Any]:
    if not isinstance(value, list) or (not value and not empty):
        raise ValueError(f"{context}: expected {'possibly empty' if empty else 'nonempty'} array")
    if len(value) > maximum:
        raise CatalogLimitError(f"{context}: array limit {maximum} exceeded")
    return value


def _strings(value: Any, context: str, *, empty: bool = False) -> list[str]:
    values = [_text(item, context) for item in _array(value, context, empty=empty)]
    if len(set(values)) != len(values):
        raise ValueError(f"{context}: duplicate value")
    return values


def _pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _nonfinite(value: str) -> None:
    raise ValueError(f"nonfinite JSON token: {value}")


def _schema(document: dict[str, Any], schema: str) -> None:
    if document["schema"] != schema or type(document["version"]) is not int:
        raise ValueError("unsupported schema/version")
    if document["version"] != 0:
        raise ValueError("unsupported schema/version")


def _path(value: Any) -> list[str]:
    path = _text(value, "reference path")
    parts = path.split("/")
    if len(path) > 240 or len(parts) > 12:
        raise ValueError("reference path is too long")
    if any(not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", part) for part in parts):
        raise ValueError("path must be canonical repository-relative components")
    if parts[0] not in {
        "adva-library",
        "docs",
        "crates",
        "python",
        "programs",
        "tests",
        "experiments",
        "examples",
    }:
        raise ValueError("path is outside the documentary reference roots")
    return parts


class _Reader:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve(strict=True)
        self.deadline = time.monotonic() + LIMITS["cooperative_seconds"]
        self.bytes_read = 0
        self.references = 0
        self.files: dict[str, dict[str, Any]] = {}

    def tick(self) -> None:
        if time.monotonic() >= self.deadline:
            raise CatalogLimitError("cooperative time limit exceeded")

    def read(self, path: str, *, metadata: bool = False) -> bytes:
        self.tick()
        parts = _path(path)
        if len(self.files) >= LIMITS["files"]:
            raise CatalogLimitError("file limit exceeded")
        limit = LIMITS["metadata_bytes_each" if metadata else "reference_bytes_each"]
        digest = hashlib.sha256()
        chunks = []
        size = 0
        # No followed symlink in any path component; nonregular files are
        # refused before reading. This is not a sandbox or an atomic snapshot
        # of a concurrently changing repository. Use a quiescent checkout.
        with ExitStack() as stack:
            flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
            directory = os.open(self.root, flags)
            stack.callback(os.close, directory)
            for part in parts[:-1]:
                directory = os.open(part, flags, dir_fd=directory)
                stack.callback(os.close, directory)
            fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
            stack.callback(os.close, fd)
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode):
                raise ValueError(f"not a regular file: {path}")
            if info.st_size > limit or self.bytes_read + info.st_size > LIMITS["total_read_bytes"]:
                raise CatalogLimitError(f"file byte limit exceeded: {path}")
            while True:
                self.tick()
                remaining = min(limit - size, LIMITS["total_read_bytes"] - self.bytes_read)
                if remaining <= 0:
                    if os.fstat(fd).st_size != size:
                        raise CatalogLimitError("read byte budget exceeded")
                    break
                chunk = os.read(fd, min(65_536, remaining))
                if not chunk:
                    break
                size += len(chunk)
                self.bytes_read += len(chunk)
                if size > limit or self.bytes_read > LIMITS["total_read_bytes"]:
                    raise CatalogLimitError("read byte budget exceeded")
                digest.update(chunk)
                if metadata:
                    chunks.append(chunk)
        self.files[path] = {"path": path, "sha256": digest.hexdigest(), "bytes": size}
        return b"".join(chunks)

    def document(self, path: str) -> Any:
        return json.loads(
            self.read(path, metadata=True).decode("utf-8"),
            object_pairs_hook=_pairs,
            parse_constant=_nonfinite,
        )

    def reference(self, value: Any) -> None:
        self.tick()
        self.references += 1
        if self.references > LIMITS["references"]:
            raise CatalogLimitError("reference limit exceeded")
        ref = _object(value, {"path", "sha256"}, "reference")
        path = _text(ref["path"], "reference path")
        _path(path)
        if path == CATALOG or path.startswith(CATALOG + "/"):
            raise ValueError("catalog records cannot cite the catalog itself as evidence")
        sha = ref["sha256"]
        if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
            raise ValueError("reference requires a lowercase SHA256")
        if path not in self.files:
            self.read(path)
        if self.files[path]["sha256"] != sha:
            raise ValueError(f"reference digest mismatch: {path}")


def _references(value: Any, reader: _Reader, *, empty: bool = False) -> None:
    seen = set()
    for ref in _array(value, "references", empty=empty):
        reader.reference(ref)
        if ref["path"] in seen:
            raise ValueError("duplicate reference within a reference list")
        seen.add(ref["path"])


def _growth_obligation(reader: _Reader) -> dict[str, Any]:
    path = CATALOG + "/constraints/growth-obligation-v0000.json"
    obligation = reader.document(path)
    if reader.files[path]["sha256"] != GROWTH_OBLIGATION_SHA256:
        raise ValueError("the fixed growth obligation changed; no automatic resealing")
    seal = _object(
        reader.document(CATALOG + "/constraints/growth-obligation-seal-v0000.json"),
        {
            "schema",
            "version",
            "kind",
            "obligation",
            "obligation_sha256",
            "status",
            "native_seal",
            "allowed_action",
        },
        "documentary obligation checkpoint",
    )
    _schema(seal, "adva.documentary-obligation-seal.research")
    if seal != {
        "schema": "adva.documentary-obligation-seal.research",
        "version": 0,
        "kind": "documentary-checkpoint-not-rust-Seal",
        "obligation": "constraints/growth-obligation-v0000.json",
        "obligation_sha256": GROWTH_OBLIGATION_SHA256,
        "status": "RecordedOpen",
        "native_seal": "NotIssued",
        "allowed_action": "retain-growth-obligation",
    }:
        raise ValueError("invalid checkpoint or attempted native Seal/obligation discharge")
    return {
        "key": obligation["key"],
        "sha256": GROWTH_OBLIGATION_SHA256,
        "checkpoint": "RecordedOpen",
        "status": "Open",
        "native_seal": "NotIssued",
        "geometry_root": GEOMETRY_ROOT,
        "admitted_geometry_successors": 0,
    }


def _lineage(entry: dict[str, Any], reader: _Reader) -> dict[str, Any] | None:
    lineage = entry["geometry_lineage"]
    if entry["home"] != "geometry":
        if lineage is not None:
            raise ValueError("geometry lineage cannot cross a home-directory boundary")
        return None
    lineage = _object(
        lineage, {"kind", "parents", "derivation_evidence", "discharge"}, "geometry lineage"
    )
    kind = _text(lineage["kind"], "lineage kind")
    if kind not in {"pascal-root", "candidate", "external-reference"}:
        raise ValueError("unsupported geometry lineage kind")
    if lineage["discharge"] != "Open":
        raise ValueError("native geometry discharge is not implemented")
    parents = _strings(lineage["parents"], "geometry parents", empty=True)
    _references(lineage["derivation_evidence"], reader, empty=True)
    if kind == "candidate":
        if not parents or entry["recorded_status"] not in UNCHECKED_STATUSES:
            raise ValueError("a geometry successor needs parents and remains a proposal")
    elif parents or lineage["derivation_evidence"]:
        raise ValueError("roots/external references cannot pretend to have derivation parents")
    if entry["key"] == GEOMETRY_ROOT:
        materials = {ref["path"]: ref["sha256"] for ref in entry["materials"]}
        if (
            kind != "pascal-root"
            or materials != PASCAL_MATERIALS
            or entry["recorded_status"] not in UNCHECKED_STATUSES
        ):
            raise ValueError("the Pascal root must retain its exact unadmitted presentations")
    elif kind == "pascal-root":
        raise ValueError("geometry cannot install an alternative root")
    return {"kind": kind, "parents": parents, "discharge": "Open"}


def _geometry_graph(entries: list[dict[str, Any]]) -> None:
    prior: dict[str, dict[str, Any]] = {}
    for entry in entries:
        lineage = entry["geometry_lineage"]
        if lineage is not None and lineage["kind"] == "candidate":
            for parent_key in lineage["parents"]:
                parent = prior.get(parent_key)
                if (
                    parent is None
                    or parent["home"] != "geometry"
                    or parent["geometry_lineage"]["kind"] == "external-reference"
                ):
                    raise ValueError(
                        "geometry parents must precede it and descend from Pascal in geometry"
                    )
        prior[entry["key"]] = entry
    if GEOMETRY_ROOT not in prior or prior[GEOMETRY_ROOT]["home"] != "geometry":
        raise ValueError("the required Pascal geometry root is missing")


def _entry(value: Any, reader: _Reader) -> dict[str, Any]:
    entry = _object(
        value,
        {
            "key",
            "title",
            "domains",
            "home",
            "geometry_lineage",
            "theory",
            "assumptions",
            "scope",
            "recorded_status",
            "materials",
            "evidence",
            "checker",
            "reuse_requires",
            "open_obligations",
        },
        "entry",
    )
    key = _text(entry["key"], "catalog key")
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,79}", key):
        raise ValueError("invalid documentary catalog key")
    _text(entry["title"], "title")
    domains = _strings(entry["domains"], "domains")
    if not set(domains) <= set(TOPICS):
        raise ValueError("unknown topic domain")
    home = _text(entry["home"], "home directory")
    if home not in domains or home != RESERVED_HOMES.get(key, key.split("-", 1)[0]):
        raise ValueError("home directory must match the reserved key or its topic prefix")
    theory = _object(entry["theory"], {"name", "version"}, "theory")
    for name, text in theory.items():
        _text(text, "theory " + name)
    _text(entry["scope"], "scope")
    for field in ("assumptions", "reuse_requires", "open_obligations"):
        _strings(entry[field], field)
    status = _text(entry["recorded_status"], "recorded status")
    if status not in STATUSES:
        raise ValueError("unsupported recorded status; no native admission status exists")
    unchecked = status in UNCHECKED_STATUSES
    _references(entry["materials"], reader)
    _references(entry["evidence"], reader, empty=unchecked)
    checker = entry["checker"]
    if checker is None:
        if not unchecked:
            raise ValueError("recorded evidence requires an explicit checker description")
    else:
        checker = _object(checker, {"name", "version", "sources"}, "checker")
        _text(checker["name"], "checker name")
        _text(checker["version"], "checker version")
        _references(checker["sources"], reader)
    return {
        "key": key,
        "domains": domains,
        "home": home,
        "recorded_status": status,
        "geometry_lineage": _lineage(entry, reader),
    }


def check_catalog(root: Path) -> dict[str, Any]:
    """Check documentary structure/integrity; never authenticate its claims.

    The time bound is cooperative between local reads, not an OS watchdog.
    No retries, child processes, recursive catalog imports or evidence replay.
    """
    started = time.monotonic()
    report: dict[str, Any] = {
        "schema": "adva.math-catalog-check.research",
        "version": 0,
        "status": "InvalidCatalog",
        "reason": None,
        **POLICY,
        "allowed_action": None,
        "proofs_rechecked": False,
        "recorded_claims_authenticated": False,
        "topics": {},
        "entries": [],
        "growth_obligation": None,
        "files": [],
        "limits": dict(LIMITS),
        "cost": {"files_read": 0, "bytes_read": 0, "references": 0, "subprocesses": 0},
    }
    reader = None
    try:
        if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
            raise ValueError("catalog descriptor-relative checks require a POSIX platform")
        reader = _Reader(Path(root))
        manifest = _object(
            reader.document(CATALOG + "/manifest.json"),
            {
                "schema",
                "version",
                "policy",
                "topics",
                "entries",
            },
            "manifest",
        )
        _schema(manifest, "adva.math-catalog.research")
        if manifest["policy"] != POLICY:
            raise ValueError("catalog cannot change authority, admission or the logic role")
        if manifest["topics"] != {topic: topic + "/index.json" for topic in TOPICS}:
            raise ValueError("topic paths must be the three fixed v0 indexes")
        obligation = _growth_obligation(reader)
        entries = []
        keys = set()
        for value in _array(manifest["entries"], "entries", LIMITS["entries"]):
            reader.tick()
            entry = _entry(value, reader)
            if entry["key"] in keys:
                raise ValueError("duplicate catalog key")
            keys.add(entry["key"])
            entries.append(entry)
        _geometry_graph(entries)
        topics = {}
        for topic in TOPICS:
            index = _object(
                reader.document(f"{CATALOG}/{topic}/index.json"),
                {
                    "schema",
                    "version",
                    "domain",
                    "entries",
                    "owned",
                    "references",
                },
                "topic index",
            )
            _schema(index, "adva.math-topic-index.research")
            if index["domain"] != topic:
                raise ValueError("topic directory and declared domain differ")
            members = _array(index["entries"], "topic entries", LIMITS["entries"], empty=True)
            if any(not isinstance(key, str) for key in members) or len(set(members)) != len(
                members
            ):
                raise ValueError("topic keys must be unique strings")
            expected = {entry["key"] for entry in entries if topic in entry["domains"]}
            if set(members) != expected:
                raise ValueError("topic membership does not match the manifest")
            for field, local in (("owned", True), ("references", False)):
                partition = _array(index[field], "topic partition", LIMITS["entries"], empty=True)
                if any(not isinstance(key, str) for key in partition) or len(set(partition)) != len(
                    partition
                ):
                    raise ValueError("topic partition keys must be unique strings")
                expected_partition = {
                    entry["key"]
                    for entry in entries
                    if topic in entry["domains"] and (entry["home"] == topic) == local
                }
                if set(partition) != expected_partition:
                    raise ValueError("cross-topic reference cannot become local ownership")
            topics[topic] = members
        reader.tick()
        report.update(
            status="CatalogConsistent",
            allowed_action="browse-declared-references",
            topics=topics,
            entries=entries,
            growth_obligation=obligation,
        )
    except CatalogLimitError as error:
        report.update(status="Unknown", reason=str(error)[:2048])
    except (OSError, ValueError, RecursionError) as error:
        report["reason"] = str(error)[:2048]
    finally:
        if reader is not None:
            report["files"] = list(reader.files.values())
            report["cost"].update(
                files_read=len(reader.files),
                bytes_read=reader.bytes_read,
                references=reader.references,
            )
        report["cost"]["wall_seconds_before_serialization"] = time.monotonic() - started
    return report
