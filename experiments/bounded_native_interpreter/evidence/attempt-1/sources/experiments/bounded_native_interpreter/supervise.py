"""Freeze source bytes, run one primary/fresh pair, retain complete archives."""
import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import sys
import tarfile
import time

from campaign import HERE, ROOT, digest, save

SOURCES = [
    "Cargo.toml", "Cargo.lock", "rust-toolchain.toml",
    "crates/adva-witness/Cargo.toml", "crates/adva-witness/src/data_machine.rs",
    "crates/adva-witness/src/lib.rs", "crates/adva-witness/src/bin/adva.rs",
    "crates/adva-witness/src/bin/support/data_machine_cli.rs",
    "crates/adva-witness/src/bin/support/native_run_cli.rs",
    "programs/bounded-interpreter/interpreter.adva",
    "programs/bounded-interpreter/instruction-labels.json",
    "programs/bounded-interpreter/input.json",
    "experiments/bounded_native_interpreter/contract.json",
    "experiments/bounded_native_interpreter/reference.py",
    "experiments/bounded_native_interpreter/campaign.py",
    "experiments/bounded_native_interpreter/supervise.py",
    "experiments/bounded_native_interpreter/preflight.py",
]


def archive(directory, destination):
    originals = {p.name: digest(p) for p in directory.iterdir() if p.is_file()}
    with destination.open("xb") as output:
        with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode="w|") as bundle:
                for name in sorted(originals):
                    raw = (directory / name).read_bytes()
                    info = tarfile.TarInfo(name)
                    info.size = len(raw)
                    info.mode = 0o644
                    bundle.addfile(info, io.BytesIO(raw))
    with tarfile.open(destination, "r:gz") as bundle:
        restored = {m.name: hashlib.sha256(bundle.extractfile(m).read()).hexdigest()
                    for m in bundle.getmembers()}
    if restored != originals:
        raise RuntimeError("archive did not preserve all original bytes")
    return {"path": destination.name, "sha256": digest(destination),
            "files": len(originals), "bytes": destination.stat().st_size}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    contract = json.loads((HERE / "contract.json").read_text())
    resource.setrlimit(resource.RLIMIT_AS, (805306368,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (240,) * 2)
    manifest = {}
    for name in SOURCES:
        destination = args.output / "sources" / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, destination)
        manifest[name] = digest(destination)
    save(args.output / "source-manifest.json", manifest)
    record = {"status": "Running", "contract_sha256": manifest["experiments/bounded_native_interpreter/contract.json"],
              "binary_sha256": digest(args.binary), "processes": []}
    started = time.monotonic()
    previous = None
    try:
        for name in ("primary", "fresh"):
            if any(digest(ROOT / p) != h for p, h in manifest.items()):
                raise RuntimeError("source changed after freeze")
            directory = args.output / ("raw-" + name)
            command = [sys.executable, "-B", str(HERE / "campaign.py"), "--binary",
                       str(args.binary.resolve()), "--output", str(directory.resolve())]
            child = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
            timed_out = False
            try:
                stdout, stderr = child.communicate(timeout=contract["campaign_limits"]["wall_seconds_per_process"])
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(child.pid, signal.SIGKILL)
                stdout, stderr = child.communicate()
            (args.output / (name + ".stdout.txt")).write_bytes(stdout)
            (args.output / (name + ".stderr.txt")).write_bytes(stderr)
            item = {"name": name, "exit_code": child.returncode, "timed_out": timed_out}
            if directory.exists():
                item["archive"] = archive(directory, args.output / (name + ".tar.gz"))
                if (directory / "cost.json").exists():
                    item["cost"] = json.loads((directory / "cost.json").read_text())
            record["processes"].append(item)
            if timed_out or child.returncode != 0:
                raise RuntimeError(name + " failed; no automatic retry")
            summary = json.loads((directory / "summary.json").read_text())
            if previous is not None and previous != summary:
                raise RuntimeError("fresh process result differs")
            previous = summary
            # The verified archive retains every original byte before cleanup.
            shutil.rmtree(directory)
        save(args.output / "results.json", previous)
        record["status"] = "Passed"
        record["deterministic_results_equal"] = True
    except Exception as exc:
        record["status"] = "Failed"
        record["error"] = str(exc)
        raise
    finally:
        record["wall_seconds"] = time.monotonic() - started
        save(args.output / "execution.json", record)
    print(json.dumps({"status": "Passed", "native_launches": 2 * previous["native_launches"],
                      "reference_steps": 2 * previous["reference_steps"], "output": str(args.output)}))


if __name__ == "__main__":
    main()
