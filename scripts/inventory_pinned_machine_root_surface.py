#!/usr/bin/env python3
"""Inventory one pinned adva-machine surface with root-anchored selectors."""

from __future__ import annotations

import argparse
from fnmatch import fnmatchcase
import hashlib
import json
from pathlib import Path, PurePosixPath
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
ROOT_PATTERNS = (
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
MAX_SEARCH_NS = 30_000_000_000
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


class RefusedBeforeSearch(RuntimeError):
    """A repository or manifest invariant failed before content search."""


class RefusedDuringSearch(RuntimeError):
    """A bounded content-search invariant failed after manifest completion."""


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
        raise RefusedBeforeSearch("spec catalog files must be a string-keyed object")
    return set(files)


def root_match(path: str, pattern: str) -> bool:
    path_parts = PurePosixPath(path).parts
    pattern_parts = PurePosixPath(pattern).parts
    return len(path_parts) == len(pattern_parts) and all(
        fnmatchcase(path_part, pattern_part)
        for path_part, pattern_part in zip(path_parts, pattern_parts, strict=True)
    )


def selected_paths(machine: Path, tracked: dict[str, int]) -> list[str]:
    selected = set(EXACT_PATHS) | catalog_paths(machine)
    selected.update(
        path
        for path in tracked
        if any(root_match(path, pattern) for pattern in ROOT_PATTERNS)
    )
    if any("evidence" in PurePosixPath(path).parts for path in selected):
        raise RefusedBeforeSearch("selection unexpectedly contains an evidence path")
    return sorted(selected)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def preflight(machine: Path) -> tuple[list[dict[str, object]], str]:
    revision = git(machine, "rev-parse", "HEAD").strip()
    if revision != EXPECTED_REVISION:
        raise RefusedBeforeSearch(f"revision mismatch: {revision}")
    if git(machine, "status", "--porcelain", "--untracked-files=all"):
        raise RefusedBeforeSearch("machine checkout is not clean")
    tracked = tracked_regular_files(machine)
    paths = selected_paths(machine, tracked)
    if len(paths) > MAX_FILES:
        raise RefusedBeforeSearch(f"selected file count {len(paths)} exceeds {MAX_FILES}")
    missing = [path for path in paths if path not in tracked]
    if missing:
        raise RefusedBeforeSearch(f"selected paths are not tracked regular files: {missing}")
    total = sum(tracked[path] for path in paths)
    if total > MAX_BYTES:
        raise RefusedBeforeSearch(f"selected bytes {total} exceeds {MAX_BYTES}")
    oversized = [path for path in paths if tracked[path] > MAX_FILE_BYTES]
    if oversized:
        raise RefusedBeforeSearch(f"selected files exceed individual limit: {oversized}")
    manifest: list[dict[str, object]] = []
    for path in paths:
        raw = (machine / path).read_bytes()
        if len(raw) != tracked[path]:
            raise RefusedBeforeSearch(f"size changed during preflight: {path}")
        manifest.append({"path": path, "bytes": len(raw), "sha256": sha256(raw)})
    aggregate = sha256(
        json.dumps(manifest, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    )
    return manifest, aggregate


def search(machine: Path, manifest: list[dict[str, object]]) -> list[dict[str, object]]:
    started = time.monotonic_ns()
    hits: list[dict[str, object]] = []
    folded = tuple((term, term.casefold()) for term in TERMS)
    for entry in manifest:
        if time.monotonic_ns() - started > MAX_SEARCH_NS:
            raise RefusedDuringSearch("search wall limit exceeded")
        path = str(entry["path"])
        try:
            text = (machine / path).read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            raise RefusedDuringSearch(f"selected file is not UTF-8: {path}") from error
        for number, line in enumerate(text.splitlines(), 1):
            lowered = line.casefold()
            matched = [term for term, needle in folded if needle in lowered]
            if matched:
                hits.append({"path": path, "line": number, "terms": matched, "text": line})
                if len(hits) > MAX_HITS:
                    raise RefusedDuringSearch(f"candidate line count exceeds {MAX_HITS}")
    return hits


def selection_record(
    manifest: list[dict[str, object]], aggregate: str
) -> dict[str, object]:
    return {
        "files": len(manifest),
        "bytes": sum(int(entry["bytes"]) for entry in manifest),
        "aggregate_sha256": aggregate,
        "manifest": manifest,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--machine", type=Path, required=True)
    args = parser.parse_args()
    machine = args.machine.resolve()
    started = time.monotonic_ns()
    manifest: list[dict[str, object]] | None = None
    aggregate: str | None = None
    preflight_finished: int | None = None
    try:
        manifest, aggregate = preflight(machine)
        preflight_finished = time.monotonic_ns()
        hits = search(machine, manifest)
        finished = time.monotonic_ns()
        report = {
            "schema": "adva.research.pinned-machine-root-surface.inventory.v0",
            "status": "InventoryComplete",
            "machine_revision": EXPECTED_REVISION,
            "selection": selection_record(manifest, aggregate),
            "search": {"candidate_lines": len(hits), "hits": hits},
            "cost": {
                "preflight_nanoseconds": preflight_finished - started,
                "search_nanoseconds": finished - preflight_finished,
                "total_nanoseconds": finished - started,
            },
        }
        print(json.dumps(report, ensure_ascii=True, indent=2))
        return 0
    except RefusedDuringSearch as error:
        finished = time.monotonic_ns()
        report = {
            "schema": "adva.research.pinned-machine-root-surface.inventory.v0",
            "status": "RefusedDuringSearch",
            "reason": str(error),
            "machine_revision": EXPECTED_REVISION,
            "selection": selection_record(manifest or [], aggregate or ""),
            "cost": {
                "preflight_nanoseconds": (preflight_finished or started) - started,
                "search_nanoseconds": finished - (preflight_finished or started),
                "total_nanoseconds": finished - started,
            },
        }
        print(json.dumps(report, ensure_ascii=True, indent=2))
        return 3
    except (
        RefusedBeforeSearch,
        OSError,
        ValueError,
        subprocess.SubprocessError,
    ) as error:
        report = {
            "schema": "adva.research.pinned-machine-root-surface.inventory.v0",
            "status": "RefusedBeforeSearch",
            "reason": str(error),
            "cost": {"total_nanoseconds": time.monotonic_ns() - started},
        }
        print(json.dumps(report, ensure_ascii=True, indent=2))
        return 2


if __name__ == "__main__":
    sys.exit(main())
