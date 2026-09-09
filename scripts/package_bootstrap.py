"""Create an authorized-collaborator source bundle from the frozen input list."""
import gzip
import hashlib
import io
import sys
import tarfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]


def package(output):
    manifest = ROOT / "bootstrap/inputs.sha256"
    entries = {}
    for line in manifest.read_text().splitlines():
        expected, name = line.split(None, 1)
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or name in entries:
            raise ValueError("invalid or duplicate source path")
        data = (ROOT / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f"source pin differs: {name}")
        entries[name] = data
    entries["bootstrap/inputs.sha256"] = manifest.read_bytes()
    # Exclusive output creation: a failed write may leave a partial archive;
    # never replace another user's archive or silently retry.
    with Path(output).open("xb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w|") as archive:
                for name, data in sorted(entries.items()):
                    info = tarfile.TarInfo("adva-bootstrap/" + name)
                    info.size = len(data)
                    info.mode = 0o644
                    info.mtime = 0
                    archive.addfile(info, io.BytesIO(data))
    return {"files": len(entries), "archive_sha256": hashlib.sha256(Path(output).read_bytes()).hexdigest()}


if __name__ == "__main__":
    print(package(sys.argv[1]))
