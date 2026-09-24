#!/usr/bin/env python3
"""Pack both bounded attempts and verify every archived byte.

Project-original Codex (OpenAI), Unknown v0.3, through Mingli Yuan's
authorized account proxy. Account use is not review or a correctness claim.
"""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import tarfile
import time


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def wire(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode()


def main(output, attempt_one, attempt_two, prior_account, cumulative_account):
    output.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    entries = []
    for prefix, root in (("attempt-1", attempt_one), ("attempt-2", attempt_two)):
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            raw = path.read_bytes()
            entries.append((f"{prefix}/{path.relative_to(root).as_posix()}", raw))
    entries.extend((
        ("attempt-1/trial-account.json", prior_account.read_bytes()),
        ("attempt-2/cumulative-trial-account.json", cumulative_account.read_bytes()),
    ))
    archive_path = output / "attempts.tar.gz"
    with archive_path.open("wb") as target:
        with gzip.GzipFile(filename="", mode="wb", fileobj=target, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as archive:
                for name, raw in entries:
                    info = tarfile.TarInfo(name)
                    info.size = len(raw)
                    info.mtime = 0
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    info.mode = 0o644
                    archive.addfile(info, io.BytesIO(raw))
    pack_seconds = time.perf_counter() - started

    verify_started = time.perf_counter()
    expected = {name: {"bytes": len(raw), "sha256": digest(raw)} for name, raw in entries}
    actual = {}
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive.getmembers():
            if not member.isfile() or member.issym() or member.islnk():
                raise AssertionError("non-regular archive member")
            raw = archive.extractfile(member).read()
            actual[member.name] = {"bytes": len(raw), "sha256": digest(raw)}
    if actual != expected:
        raise AssertionError("archive byte verification failed")
    verification_seconds = time.perf_counter() - verify_started

    shutil.copyfile(attempt_two / "execution.json", output / "execution.json")
    shutil.copyfile(cumulative_account, output / "cumulative-trial-account.json")
    prior_execution = json.loads((attempt_one / "execution.json").read_text())
    (output / "prior-invalid-context.json").write_bytes(wire({
        "classification": "InvalidContext",
        "reason": "The frozen full main coordinate was mistyped; semantic observations remain retained but are not accepted as this run's evidence.",
        "recorded_main": prior_execution["main_at_start"],
        "actual_main": "19ac70e4886a3096bec00c3f4ba0008fbdc48c5d",
        "reserved_units_retained": prior_execution["reserved_units"],
        "node_processes_retained": prior_execution["node_processes"],
        "execution_sha256": digest((attempt_one / "execution.json").read_bytes()),
    }))
    manifest = {
        "profile": "adva.research.cumulative-node-receiver-evidence.v0",
        "archive": archive_path.name,
        "archive_bytes": archive_path.stat().st_size,
        "archive_sha256": digest(archive_path.read_bytes()),
        "expanded_bytes": sum(item["bytes"] for item in expected.values()),
        "files": len(expected),
        "entries": expected,
        "pack_seconds": pack_seconds,
        "verification_seconds": verification_seconds,
        "classification": {"attempt-1": "InvalidContext", "attempt-2": "PassedAfterCorrectionReplay"},
    }
    (output / "manifest.json").write_bytes(wire(manifest))
    print(json.dumps({key: value for key, value in manifest.items() if key != "entries"}, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--attempt-one", required=True, type=Path)
    parser.add_argument("--attempt-two", required=True, type=Path)
    parser.add_argument("--prior-account", required=True, type=Path)
    parser.add_argument("--cumulative-account", required=True, type=Path)
    args = parser.parse_args()
    main(args.output.resolve(), args.attempt_one.resolve(), args.attempt_two.resolve(),
         args.prior_account.resolve(), args.cumulative_account.resolve())
