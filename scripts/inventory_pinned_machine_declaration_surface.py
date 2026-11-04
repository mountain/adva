#!/usr/bin/env python3
"""Fail-closed inventory of one pinned adva-machine declaration surface."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from pathlib import PurePosixPath
import subprocess
import sys
import time


EXPECTED_REVISION = "a0b710a2517f06f2fe03cc463e855548adf418ac"
EXACT_PATHS = {
    "Cargo.toml",
    "pyproject.toml",
    "spec/catalog.json",
    "toolchain/cli.py",
    "exchange_routine/cli.py",
}
GLOBS = (
    "toolchain/*",
    "exchange_routine/*",
    "schemas/*",
    "spec/framework/*",
    "crates/*/Cargo.toml",
    "crates/*/src/main.rs",
    "crates/*/src/bin/*",
    "experiments/*/Cargo.toml",
    "experiments/*/src/main.rs",
    "experiments/*/src/bin/*",
)
MAX_FILES = 1_000
MAX_BYTES = 5_000_000
MAX_FILE_BYTES = 1_000_000
MAX_HITS = 100_000
TERMS = (
    "AcceptedCurrentFixture",
    "native-input-binding",
    "opaque fixture",
    "import_diagram_json",
    "DiagramValidationCertificate",
    "SourceId",
    "OccurrenceId",
    "occurrence map",
    "occurrence_map",
    "qualified source",
    "qualified endpoint",
    "receiver outcome",
    "native_admission",
    "receive",
    "request",
    "outcome",
)


class Refused(RuntimeError):
    """A preflight invariant failed before content search."""


def git(machine: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(machine), *args],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
    return completed.stdout


def tracked_regular_files(machine: Path) -> dict[str, int]:
    result: dict[str, int] = {}
    for line in git(machine, "ls-tree", "-r", "-l", "HEAD").splitlines():
        metadata, path = line.split("\t", 1)
        mode, kind, _object, size_text = metadata.split()
        if kind == "blob" and mode.startswith("100") and size_text.isdigit():
            result[path] = int(size_text)
    return result


def catalog_paths(machine: Path) -> set[str]:
    raw = (machine / "spec/catalog.json").read_bytes()
    catalog = json.loads(raw)
    files = catalog.get("files")
    if not isinstance(files, dict) or not all(isinstance(path, str) for path in files):
        raise Refused("spec catalog files must be a string-keyed object")
    return set(files)


def selected_paths(machine: Path, tracked: dict[str, int]) -> list[str]:
    selected = set(EXACT_PATHS) | catalog_paths(machine)
    selected.update(
        path
        for path in tracked
        if any(PurePosixPath(path).match(pattern) for pattern in GLOBS)
    )
    if any("evidence" in PurePosixPath(path).parts for path in selected):
        raise Refused("selection unexpectedly contains an evidence path")
    return sorted(selected)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def preflight(machine: Path) -> tuple[list[dict[str, object]], str]:
    revision = git(machine, "rev-parse", "HEAD").strip()
    if revision != EXPECTED_REVISION:
        raise Refused(f"revision mismatch: {revision}")
    if git(machine, "status", "--porcelain", "--untracked-files=all"):
        raise Refused("machine checkout is not clean")
    tracked = tracked_regular_files(machine)
    paths = selected_paths(machine, tracked)
    if len(paths) > MAX_FILES:
        raise Refused(f"selected file count {len(paths)} exceeds {MAX_FILES}")
    missing = [path for path in paths if path not in tracked]
    if missing:
        raise Refused(f"selected paths are not tracked regular files: {missing}")
    total = sum(tracked[path] for path in paths)
    if total > MAX_BYTES:
        raise Refused(f"selected bytes {total} exceeds {MAX_BYTES}")
    oversized = [path for path in paths if tracked[path] > MAX_FILE_BYTES]
    if oversized:
        raise Refused(f"selected files exceed individual limit: {oversized}")
    manifest: list[dict[str, object]] = []
    for path in paths:
        raw = (machine / path).read_bytes()
        if len(raw) != tracked[path]:
            raise Refused(f"size changed during preflight: {path}")
        manifest.append({"path": path, "bytes": len(raw), "sha256": sha256(raw)})
    aggregate = sha256(
        json.dumps(manifest, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    )
    return manifest, aggregate


def search(machine: Path, manifest: list[dict[str, object]]) -> list[dict[str, object]]:
    hits: list[dict[str, object]] = []
    folded = tuple((term, term.casefold()) for term in TERMS)
    for entry in manifest:
        path = str(entry["path"])
        try:
            text = (machine / path).read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            raise Refused(f"selected file is not UTF-8: {path}") from error
        for number, line in enumerate(text.splitlines(), 1):
            lowered = line.casefold()
            matched = [term for term, needle in folded if needle in lowered]
            if matched:
                hits.append({"path": path, "line": number, "terms": matched, "text": line})
                if len(hits) > MAX_HITS:
                    raise Refused(f"candidate line count exceeds {MAX_HITS}")
    return hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--machine", type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic_ns()
    try:
        manifest, aggregate = preflight(args.machine.resolve())
        preflight_finished = time.monotonic_ns()
        hits = search(args.machine.resolve(), manifest)
        finished = time.monotonic_ns()
        report = {
            "schema": "adva.research.pinned-machine-declaration-surface.inventory.v0",
            "status": "InventoryComplete",
            "machine_revision": EXPECTED_REVISION,
            "selection": {
                "files": len(manifest),
                "bytes": sum(int(entry["bytes"]) for entry in manifest),
                "aggregate_sha256": aggregate,
                "manifest": manifest,
            },
            "search": {
                "candidate_lines": len(hits),
                "hits": hits,
            },
            "cost": {
                "preflight_nanoseconds": preflight_finished - started,
                "search_nanoseconds": finished - preflight_finished,
                "total_nanoseconds": finished - started,
            },
        }
        print(json.dumps(report, ensure_ascii=True, indent=2))
        return 0
    except (Refused, OSError, ValueError, subprocess.SubprocessError) as error:
        report = {
            "schema": "adva.research.pinned-machine-declaration-surface.inventory.v0",
            "status": "RefusedBeforeSearch",
            "reason": str(error),
            "cost": {"total_nanoseconds": time.monotonic_ns() - started},
        }
        print(json.dumps(report, ensure_ascii=True, indent=2))
        return 2


if __name__ == "__main__":
    sys.exit(main())
