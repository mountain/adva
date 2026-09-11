#!/usr/bin/env python3
"""Public AEG receipt-feed checker (self-contained; no AEG access needed).

Usage: python3 feed_check.py <feed_dir>

Verifies: coverage 1..N exactly once, byte pins, predecessor continuity,
and the disclosure scan (no undeclared private-path patterns).
"""
import hashlib
import json
import pathlib
import re
import sys

PRIVATE_PATTERNS = [re.compile(r"/Users/"), re.compile(r"/home/"),
                    re.compile(r"/private/"), re.compile(r"/var/")]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(feed_dir):
    feed_dir = pathlib.Path(feed_dir)
    feed = json.loads((feed_dir / "feed.json").read_text())
    disclosure = json.loads((feed_dir / "disclosure.json").read_text())
    entries = feed["entries"]
    findings = []
    nums = [e["receipt"] for e in entries]
    if sorted(nums) != list(range(1, len(entries) + 1)):
        findings.append(f"coverage violation: {sorted(nums)}")
    by_num = {}
    for e in entries:
        p = feed_dir / e["path"]
        if not p.exists():
            findings.append(f"receipt-{e['receipt']:02d} missing")
            continue
        if sha(p) != e["sha256"]:
            findings.append(f"receipt-{e['receipt']:02d} pin mismatch")
        by_num[e["receipt"]] = e
    for e in entries:
        n = e["receipt"]
        if n == 1:
            if e["canonical_predecessor"] is not None:
                findings.append("root must have null predecessor")
            continue
        canon = by_num.get(e["canonical_predecessor"])
        if canon is None:
            findings.append(f"receipt-{n:02d} predecessor missing from feed")
            continue
        on_disk = json.loads((feed_dir / e["path"]).read_text()).get("predecessor_sha256")
        if on_disk != canon["sha256"]:
            if e.get("repair"):
                pass  # declared repair: acceptable, kept visible in feed.json
            else:
                findings.append(f"receipt-{n:02d} predecessor mismatch")
    # disclosure scan
    declared = {(x["receipt"], x["pattern"]) for x in disclosure["exceptions"]}
    for e in entries:
        raw = (feed_dir / e["path"]).read_text()
        for pat in PRIVATE_PATTERNS:
            hits = pat.findall(raw)
            if hits and (e["receipt"], pat.pattern) not in declared:
                findings.append(
                    f"receipt-{e['receipt']:02d} undeclared private-pattern hit: {pat.pattern}")
    if disclosure["undeclared"]:
        findings.append("disclosure manifest lists undeclared exceptions")
    status = "FeedConsistent" if not findings else "Rejected"
    print(json.dumps({"schema": "aeg.feed.check", "version": 0,
                      "status": status, "entries": len(entries),
                      "findings": findings,
                      "declared_exceptions": disclosure["exceptions"]},
                     indent=2, ensure_ascii=False))
    return 0 if status == "FeedConsistent" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
