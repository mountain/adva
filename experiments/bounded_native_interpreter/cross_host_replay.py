#!/usr/bin/env python3
"""Receive the retained bounded-interpreter archive on this host, receiving-only.

Every checkpoint artifact in the retained primary and fresh archives is re-received
with `adva data-run --check --quantum 0`, supplying the retained program, input and
original lifetime fuel independently of the checkpoint. A reception grants no object
execution quantum, so this launches no campaign, resets no fuel and answers no new
research question: it checks whether the retained bytes still travel.

A reception counts as matched when the call exits 0 with `Verified` and its
`verified_steps`, final `state` and `profile` equal the retained artifact. Note that
a retained `Rejected` run is also re-received as `Verified`: admission verifies the
record, it does not re-run the rejection or restate a terminal status.

Exit status is 0 when every checkpoint matched, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
import tarfile
from collections import Counter

STATUS = re.compile(r"^status=([A-Za-z]+);")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--binary", required=True, help="path to the built adva binary")
    parser.add_argument(
        "--evidence",
        default=str(pathlib.Path(__file__).resolve().parent / "evidence/attempt-1"),
        help="directory holding the retained archives",
    )
    parser.add_argument("--workdir", required=True, help="fresh scratch directory for this run")
    parser.add_argument(
        "--archives", default="primary,fresh", help="comma-separated archive names to replay"
    )
    return parser.parse_args()


def unpack(evidence: pathlib.Path, workdir: pathlib.Path, name: str) -> pathlib.Path:
    target = workdir / name
    target.mkdir(parents=True, exist_ok=False)
    with tarfile.open(evidence / f"{name}.tar.gz", "r:gz") as bundle:
        for member in bundle.getmembers():
            if not member.isfile() or pathlib.Path(member.name).name != member.name:
                raise SystemExit(f"refusing unexpected archive member: {member.name}")
        # `filter` is absent from older patch releases of the declared 3.11 floor.
        bundle.extractall(target, **({"filter": "data"} if hasattr(tarfile, "data_filter") else {}))
    return target


def replay(binary: str, root: pathlib.Path, run: pathlib.Path, out_dir: pathlib.Path):
    """Return (name, verdict, detail, retained terminal status)."""
    base = run.name[: -len(".run.adva")]
    program, given = root / f"{base}.program.adva", root / f"{base}.input.json"
    if not (program.exists() and given.exists()):
        return base, "SKIP", "program or input absent from the archive", None
    record = json.loads(run.read_text())
    if "fuel" not in record:
        return base, "SKIP", f"not a checkpoint record: {sorted(record)}", None
    out = out_dir / f"{root.name}-{base}.adva"
    if out.exists():
        out.unlink()
    done = subprocess.run(
        [
            binary,
            "data-run",
            str(program),
            "--input",
            str(given),
            "--fuel",
            str(record["fuel"]),
            "--quantum",
            "0",
            "--check",
            str(run),
            "--output",
            str(out),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    matched_status = STATUS.match(done.stdout.strip())
    observed = matched_status.group(1) if matched_status else f"exit={done.returncode}"
    if observed != "Verified" or not out.exists():
        return base, "MISMATCH", f"status={observed} stderr={done.stderr.strip()[:80]!r}", record["status"]
    received = json.loads(out.read_text())
    same = (
        received["verified_steps"] == len(record["trace"]),
        received["state"] == record["state"],
        received["profile"] == record["profile"],
    )
    if all(same):
        return base, "MATCH", "", record["status"]
    return base, "MISMATCH", f"steps,state,profile equal = {same}", record["status"]


def main() -> int:
    args = parse_args()
    evidence = pathlib.Path(args.evidence)
    workdir = pathlib.Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    out_dir = workdir / "received"
    out_dir.mkdir(exist_ok=True)

    rows = []
    for name in args.archives.split(","):
        root = unpack(evidence, workdir, name.strip())
        for run in sorted(root.glob("*.run.adva")):
            base, verdict, detail, status = replay(args.binary, root, run, out_dir)
            rows.append((root.name, base, verdict, detail, status))

    print("=== reception verdict ===")
    for (archive, verdict), count in sorted(
        Counter((r[0], r[2]) for r in rows).items(), key=lambda item: (item[0][0], item[0][1])
    ):
        print(f"  {archive:10s} {verdict:10s} {count}")
    print("=== retained terminal status of every replayed artifact ===")
    for (archive, status), count in sorted(
        Counter((r[0], str(r[4])) for r in rows).items(), key=lambda item: (item[0][0], item[0][1])
    ):
        print(f"  {archive:10s} {status:14s} {count}")
    print(f"total artifacts: {len(rows)}   matched: {sum(r[2] == 'MATCH' for r in rows)}")
    for row in rows:
        if row[2] != "MATCH":
            print(f"  {row[2]} {row[0]}/{row[1]}: {row[3]}")
    return 1 if any(r[2] == "MISMATCH" for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
