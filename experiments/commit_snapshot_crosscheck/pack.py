#!/usr/bin/env python3
"""Package and byte-check this original finite experiment, Unknown v0.3."""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile
import time


def main(source, destination):
    started = time.perf_counter()
    destination.mkdir(parents=True, exist_ok=False)
    files = sorted(path for path in source.rglob("*") if path.is_file())
    assert files and not any(path.is_symlink() for path in source.rglob("*"))
    entries = [{"path": str(path.relative_to(source)), "bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in files]
    archive = destination / "attempt-1.tar.gz"
    with tarfile.open(archive, "w:gz") as output:
        for path in files:
            output.add(path, arcname=str(path.relative_to(source)), recursive=False)
    with tarfile.open(archive, "r:gz") as saved:
        assert sorted(saved.getnames()) == sorted(entry["path"] for entry in entries)
        for entry in entries:
            body = saved.extractfile(entry["path"]).read()
            assert len(body) == entry["bytes"]
            assert hashlib.sha256(body).hexdigest() == entry["sha256"]
    (destination / "execution.json").write_bytes((source / "execution.json").read_bytes())
    manifest = {"archive": archive.name,
                "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
                "files": entries, "file_count": len(entries),
                "expanded_bytes": sum(entry["bytes"] for entry in entries),
                "pack_and_verify_seconds": time.perf_counter() - started,
                "boundary": "Byte preservation only, not independent semantics or authentication."}
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({key: value for key, value in manifest.items() if key != "files"},
                     sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    main(args.source.resolve(), args.destination.resolve())
