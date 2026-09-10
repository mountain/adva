"""Verify retained bytes and recorded outcomes; no native execution or authentication."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path

REPORT_SHA256 = "51694ca9400e5561591832bb9909ae62cbb8ef38274c8b98ba86420e674fd614"
MAX_BYTES = 67_108_864


def verify(root):
    root = root.resolve()
    manifest = json.loads((root / "manifest.json").read_bytes())
    retained = {}
    if len(manifest["files"]) != 54:
        raise ValueError("retained file coverage differs")
    for name, pin in manifest["files"].items():
        path = (root / pin["stored_path"]).resolve()
        if not path.is_relative_to(root) or path.stat().st_size > MAX_BYTES:
            raise ValueError(f"invalid stored path/size: {name}")
        stored = path.read_bytes()
        if (
            len(stored) != pin["stored_bytes"]
            or hashlib.sha256(stored).hexdigest() != pin["stored_sha256"]
        ):
            raise ValueError(f"stored bytes differ: {name}")
        if pin["encoding"] == "gzip":
            with gzip.open(path, "rb") as stream:
                raw = stream.read(MAX_BYTES + 1)
        elif pin["encoding"] == "identity":
            raw = stored
        else:
            raise ValueError(f"unsupported encoding: {name}")
        if (
            len(raw) > MAX_BYTES
            or len(raw) != pin["original_bytes"]
            or hashlib.sha256(raw).hexdigest() != pin["original_sha256"]
        ):
            raise ValueError(f"original bytes differ: {name}")
        retained[name] = raw

    if hashlib.sha256(retained["report.json"]).hexdigest() != REPORT_SHA256:
        raise ValueError("recorded report differs")
    report = json.loads(retained["report.json"])
    if set(retained) != set(report["files"]) | {"report.json"}:
        raise ValueError("original inventory coverage differs")
    for name, pin in report["files"].items():
        raw = retained[name]
        if len(raw) != pin["bytes"] or hashlib.sha256(raw).hexdigest() != pin["sha256"]:
            raise ValueError(f"original inventory mismatch: {name}")
    native = json.loads(retained["native-load.json"])
    if (
        report["status"] != "VariationObserved"
        or len(native["controls"]) != 8
        or not all(native["controls"].values())
        or native["native_load_invocations"] != 8
    ):
        raise ValueError("recorded finite outcome differs")
    for name, digest_key in (
        ("predecessor-handoff.json", "predecessor_sha256"),
        ("prior-advance.json", "prior_advance_sha256"),
    ):
        if hashlib.sha256(retained[name]).hexdigest() != report[digest_key]:
            raise ValueError(f"predecessor binding differs: {name}")
    return {
        "status": "RetainedBytesAndRecordedOutcomeChecked",
        "retained_files": len(retained),
        "scope": "Stored and decompressed bytes plus recorded outcomes; no native replay.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--evidence", type=Path, default=Path(__file__).resolve().parent / "evidence/run-01"
    )
    print(json.dumps(verify(parser.parse_args().evidence), indent=2))
