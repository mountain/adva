"""Read archived JSON without importing the producer or its dataclasses."""

import hashlib
import json
from pathlib import Path
import resource
import subprocess
import time
import tomllib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    started = time.perf_counter()
    attempt = HERE / "evidence/attempt-1"
    target = HERE / "validation.json"
    if target.exists() or (HERE / "manifest.json").exists():
        raise ValueError("refuse to overwrite archived validation")
    contract = json.loads((HERE / "contract.json").read_bytes())
    result = json.loads((attempt / "execution.json").read_bytes())
    supervision = json.loads((attempt / "supervision.json").read_bytes())
    evidence = json.loads((attempt / "cases.json").read_bytes())
    checks = 0

    def check(condition):
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError("archive check failed: " + str(checks))

    check(result == json.loads((attempt / "stdout.txt").read_bytes()))
    check(supervision["status"] == "Completed" and supervision["returncode"] == 0)
    check((attempt / "stderr.txt").read_bytes() == b"")
    check(result["script_sha256"] == hashlib.sha256((HERE / "run.py").read_bytes()).hexdigest())
    check(result["contract_sha256"] == hashlib.sha256((HERE / "contract.json").read_bytes()).hexdigest())
    for path, digest in contract["input_sha256"].items():
        check(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest)
    rows = {row["case"]: row for row in evidence["records"]}
    check(len(rows) == 15)
    for name in ("canonical", "fresh"):
        forward = rows[name]
        reverse = rows[name + "-reversed"]
        a = forward["expected_source"]["channels"][0]["thread"]
        b = reverse["expected_source"]["channels"][0]["thread"]
        check(a != b and a == b[::-1])
        check(sorted(a, key=lambda x: x["name"]) == sorted(b, key=lambda x: x["name"]))
        check(forward["output"]["am"] == reverse["output"]["am"])
        check(forward["output"]["open_line"] != reverse["output"]["open_line"])
        for row in (forward, reverse):
            check(row["output"]["status"] == "PairedResearchRecord")
            check(row["output"]["open_line"] == row["candidate"])
            for key in ("ports", "channels", "open_ports", "holes", "residuals"):
                check(row["output"]["open_line"][key] == row["expected_source"][key])
    for name in contract["candidate_refusals"] + contract["source_refusals"]:
        check(rows[name]["outcome"] == "Refused")
    check(rows["reverse-word"]["candidate"] == rows["canonical-reversed"]["candidate"])
    check(len(evidence["old_profile_refusals"]) == 2)
    claims = (ROOT / "docs/claims.toml").read_bytes()
    baseline = subprocess.check_output(["git", "show", contract["base_commit"] + ":docs/claims.toml"], cwd=ROOT)
    check(claims.startswith(baseline))
    parsed = tomllib.loads(claims.decode())
    identifiers = [row["claim_id"] for row in parsed["claim"]]
    check(len(identifiers) == len(set(identifiers)))
    paths = sorted(p for p in HERE.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    check(sum(p.stat().st_size for p in paths) < 1048576)
    manifest = {str(p.relative_to(ROOT)): {"bytes": p.stat().st_size,
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths}
    serialized = json.dumps(manifest, sort_keys=True, indent=2).encode() + b"\n"
    for path, entry in json.loads(serialized).items():
        check(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == entry["sha256"])
    (HERE / "manifest.json").write_bytes(serialized)
    target.write_text(json.dumps({"status": "Passed", "checks": checks,
        "files": len(paths), "seconds_before_summary": time.perf_counter() - started,
        "peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "scope": "Read-only archived evidence checks and hash manifest; no producer re-execution or independent WholeCut6 validity proof"}, indent=2) + "\n")
    print(target.read_text())


if __name__ == "__main__":
    main()
