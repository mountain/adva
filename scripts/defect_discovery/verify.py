#!/usr/bin/env python3
"""Verify completion, retained source identity, and internal replay consistency."""
import argparse
import json
import pathlib

from run import CONTRACT, SOURCES, classify, digest, encode


def read(path):
    with path.open("rb") as f:
        data = f.read(CONTRACT["max_source_bytes"] + 1)
    if len(data) > CONTRACT["max_source_bytes"]:
        raise ValueError("artifact too large")
    return data


def verify(root):
    complete = json.loads(read(root / "COMPLETE.json"))
    if set(complete["sha256"]) != {"report.json", "report.md"}:
        raise ValueError("incomplete report manifest")
    for name, expected in complete["sha256"].items():
        if digest(read(root / name)) != expected:
            raise ValueError(f"report hash mismatch: {name}")
    report = json.loads(read(root / "report.json"))
    if report["schema"] != "adva.defect-discovery.report.v1" or complete["schema"] != report["schema"]:
        raise ValueError("unsupported report schema")
    if report["contract"] != CONTRACT:
        raise ValueError("unsupported finite contract")
    expected_sources = {p for paths in SOURCES.values() for p in paths}
    expected_sources.update({"scripts/defect_discovery/run.py", "scripts/defect_discovery/probes.py"})
    if set(report["source_sha256"]) != expected_sources:
        raise ValueError("unsupported or incomplete source set")
    for name, expected in report["source_sha256"].items():
        if digest(read(root / "sources" / name)) != expected:
            raise ValueError(f"source hash mismatch: {name}")
    if [p["id"] for p in report["probes"]] != list(SOURCES):
        raise ValueError("missing, duplicate, or unsupported probes")
    for p in report["probes"]:
        if len(p["replays"]) > 2:
            raise ValueError("replay budget exceeded")
        for receipt in p["replays"]:
            if "result" in receipt:
                cases = receipt["result"]["cases"]
                if not 0 < len(cases) <= CONTRACT["max_cases_per_probe"]:
                    raise ValueError("invalid case count")
                if any(c["verdict"] not in ("Pass", "Violation") for c in cases):
                    raise ValueError("unknown case verdict")
                if receipt["exit_code"] != 0 or receipt["timed_out"]:
                    raise ValueError("failed worker cannot supply completed evidence")
                if digest(encode(receipt["result"])) != receipt["result_sha256"]:
                    raise ValueError("replay content hash mismatch")
        if classify(p["replays"]) != p["state"]:
            raise ValueError("evidence state disagrees with replays")
    return dict(state="IntegrityCheckedNotCorrectnessCertified",
                probes={p["id"]: p["state"] for p in report["probes"]})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report_directory", type=pathlib.Path)
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.report_directory)))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, f"Unknown: report not accepted: {exc}\n")
