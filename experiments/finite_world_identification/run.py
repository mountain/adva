"""Replay Rust judgments; Python handles processes, byte bindings and comparison only."""

import argparse
import hashlib
import json
import os
import resource
import shutil
import signal
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def limits(build=False):
    resource.setrlimit(resource.RLIMIT_AS, (4 * 1024**3, 4 * 1024**3))
    cap = (512 if build else 8) * 1024**2
    resource.setrlimit(resource.RLIMIT_FSIZE, (cap, cap))
    resource.setrlimit(resource.RLIMIT_CPU, (600, 600))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    staged = ROOT / "crates/adva-lisp/tests/finite_world_identification.rs"
    if staged.exists():
        raise SystemExit("Refused: ephemeral test path already exists")
    paths = [
        ROOT / "Cargo.toml",
        ROOT / "Cargo.lock",
        HERE / "worlds.rs",
        HERE / "contract.json",
        Path(__file__).resolve(),
    ]
    for crate in ("adva-ir", "adva-lisp"):
        paths += list((ROOT / "crates" / crate).rglob("*.rs"))
        paths.append(ROOT / "crates" / crate / "Cargo.toml")
    bindings = {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)
    }
    (output / "bindings.json").write_text(json.dumps(bindings, indent=2) + "\n")
    started = time.monotonic()
    result = {
        "status": "ImplementationFailure",
        "baseline": "8585c5b965b84422b802d50f11f375aea171bd27",
    }
    try:
        shutil.copyfile(HERE / "worlds.rs", staged)
        commands = [
            (
                [
                    "cargo",
                    "test",
                    "--locked",
                    "-p",
                    "adva-lisp",
                    "--test",
                    "finite_world_identification",
                    "--no-run",
                ],
                600,
                "build.log",
            ),
            (
                [
                    "cargo",
                    "test",
                    "--locked",
                    "-p",
                    "adva-lisp",
                    "--test",
                    "finite_world_identification",
                    "--",
                    "--nocapture",
                    "--test-threads=1",
                ],
                120,
                "test.log",
            ),
        ]
        for command, timeout, name in commands:
            with (output / name).open("wb") as log:
                process = subprocess.Popen(
                    command,
                    cwd=ROOT,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    preexec_fn=lambda build=name == "build.log": limits(build),
                    env=os.environ.copy(),
                    start_new_session=True,
                )
                try:
                    code = process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                    raise
            if code:
                raise RuntimeError(f"{name}: exit {code}")
        lines = (output / "test.log").read_text().splitlines()
        markers = [
            line.split("WORLD_EVIDENCE=", 1)[1] for line in lines if "WORLD_EVIDENCE=" in line
        ]
        if len(markers) != 1:
            raise RuntimeError("missing or repeated Rust evidence marker")
        native = markers[0] + "\n"
        if len(native.encode()) > 2 * 1024**2:
            raise RuntimeError("native evidence exceeds retained-byte cap")
        json.loads(native)  # representation check only; no semantic reconstruction
        (output / "native.json").write_text(native)
        frozen = HERE / "evidence.json"
        if frozen.exists():
            if frozen.read_bytes() != native.encode():
                raise RuntimeError("Rust replay differs from frozen native evidence")
            result["status"] = "ExactNativeReplayMatched"
        else:
            result["status"] = "UnfrozenNativeReplay"
        result["native_sha256"] = hashlib.sha256(native.encode()).hexdigest()
    except subprocess.TimeoutExpired:
        result["status"] = "UnknownTimeout"
        raise
    finally:
        staged.unlink(missing_ok=True)
        result["wall_seconds"] = time.monotonic() - started
        (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
