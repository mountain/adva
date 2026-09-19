#!/usr/bin/env python3
"""Package and hash-check this original finite experiment, Unknown v0.3."""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile
import time


def main(source, destination):
    started = time.perf_counter()
    destination.mkdir(parents=True, exist_ok=False)
    files = sorted(p for p in source.rglob('*') if p.is_file())
    assert files and not any(p.is_symlink() for p in source.rglob('*'))
    entries = [{"path": str(p.relative_to(source)), "bytes": p.stat().st_size,
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
    archive = destination / 'attempt-1.tar.gz'
    with tarfile.open(archive, 'w:gz') as output:
        for p in files:
            output.add(p, arcname=str(p.relative_to(source)), recursive=False)
    with tarfile.open(archive, 'r:gz') as saved:
        assert sorted(saved.getnames()) == sorted(e['path'] for e in entries)
        for entry in entries:
            body = saved.extractfile(entry['path']).read()
            assert len(body) == entry['bytes']
            assert hashlib.sha256(body).hexdigest() == entry['sha256']
    (destination / 'execution.json').write_bytes((source / 'execution.json').read_bytes())
    manifest = {"archive": archive.name, "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
                "files": entries, "file_count": len(entries),
                "expanded_bytes": sum(e['bytes'] for e in entries),
                "pack_and_verify_seconds": time.perf_counter() - started,
                "boundary": "Byte preservation only, not an independent rerun or a proof of the receiver."}
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({k: v for k, v in manifest.items() if k != 'files'}))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('source', type=Path)
    p.add_argument('destination', type=Path)
    args = p.parse_args()
    main(args.source.resolve(), args.destination.resolve())
