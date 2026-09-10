#!/usr/bin/env python3
"""Build the public AEG receipt feed (anchor for cross-interface exchange).

Copies the AEG receipt chain byte-exactly into a public feed directory,
writes the feed index and the disclosure manifest, then self-checks.
Receipts are summaries/pins/holes only; source materials (PDFs, text
layers) never leave the local workspace.
"""
import hashlib
import json
import pathlib
import re
import subprocess
import sys

AEG = pathlib.Path("/Users/mingli/Adva/AEG")
FEED = AEG / "trials" / "aeg-feed"
RECEIPTS = FEED / "receipts"
PRIVATE_PATTERNS = [re.compile(r"/Users/"), re.compile(r"/home/"),
                    re.compile(r"/private/"), re.compile(r"/var/")]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def find_receipts():
    out = {}
    for p in AEG.glob("trials/**/receipt-*.json"):
        if "aeg-feed" in p.parts:
            continue
        m = re.search(r"receipt-(\d+)\.json$", str(p))
        if m:
            out[int(m.group(1))] = p
    return out


def main():
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    found = find_receipts()
    ledger = json.loads((AEG / "trials" / "receipt-ledger" / "ledger.json").read_text())
    repairs = {e["receipt"]: e.get("repair") for e in ledger["entries"]}
    entries = []
    for n in sorted(found):
        src = found[n]
        dst = RECEIPTS / f"receipt-{n:02d}.json"
        dst.write_bytes(src.read_bytes())
        entries.append({"receipt": n, "path": f"receipts/receipt-{n:02d}.json",
                        "sha256": sha(dst),
                        "canonical_predecessor": n - 1 if n > 1 else None,
                        "repair": repairs.get(n)})
    # disclosure scan across the published bytes
    REVIEW = {(20, "/Users/"): ("home-root mention of the operator account "
                                "only; no deeper paths, no secrets")}
    for pat in PRIVATE_PATTERNS:
        REVIEW[(23, pat.pattern)] = (
            "self-referential pattern-name mentions inside receipt-23's "
            "documentation of the disclosure preflight tool; not actual paths")
    exceptions = []
    for e in entries:
        raw = (RECEIPTS / f"receipt-{e['receipt']:02d}.json").read_text()
        for pat in PRIVATE_PATTERNS:
            hits = pat.findall(raw)
            if hits:
                exceptions.append({"receipt": e["receipt"],
                                   "pattern": pat.pattern, "count": len(hits),
                                   "declared_scope": REVIEW.get((e["receipt"], pat.pattern))})
    feed = {
        "schema": "aeg.feed.receipts", "version": 0,
        "generated_by": "AEG build_feed.py (local; label unauthenticated)",
        "entries": entries,
        "status": "Proposed",
    }
    (FEED / "feed.json").write_text(json.dumps(feed, indent=2, ensure_ascii=False) + "\n")
    disclosure = {
        "schema": "aeg.feed.disclosure", "version": 0,
        "policy": ("receipts only: summaries, pins, declared holes; no source "
                   "documents, no full texts, no secrets, no private filesystem "
                   "paths beyond declared exceptions"),
        "scan_patterns": [p.pattern for p in PRIVATE_PATTERNS],
        "exceptions": exceptions,
        "undeclared": [x for x in exceptions if x["declared_scope"] is None],
    }
    (FEED / "disclosure.json").write_text(json.dumps(disclosure, indent=2, ensure_ascii=False) + "\n")
    (FEED / "feed_check.py").write_text(
        (AEG / "trials" / "aeg-feed-checker.py").read_text())
    result = subprocess.run([sys.executable, str(FEED / "feed_check.py"),
                             str(FEED)], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
