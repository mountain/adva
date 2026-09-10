#!/usr/bin/env python3
"""Project a receipt into a bounded-exchange response with a byte-level witness.

Deterministic mapping (declared, not semantic):
  task     <- receipt.delta.kind + ": " + receipt.delta.description
  result   <- receipt.status + "; evidence keys: " + sorted evidence keys
  residual <- "documented_holes: " + receipt.documented_holes (joined)
Each field is truncated to 1024 characters with a trailing "..." marker.

Writes:
  response-from-<N>.json      ordinary three-field response (binds request bytes)
  projection-witness-<N>.json byte-level witness: receipt pin, JSON pointers,
                              exact excerpts, and the feed path for verification.

Usage:
  python3 project_receipt.py <before-receipt> <after-receipt> <request.json>
Produces a genuine before/after response from the two pinned receipts.
"""
import hashlib
import json
import pathlib
import sys

AEG = pathlib.Path("/Users/mingli/Adva/AEG")
ROUND = AEG / "trials" / "bounded-exchange-round-01"
FEED = AEG / "trials" / "aeg-feed"
LIMIT = 1024


def sha_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def truncate(s):
    if len(s) <= LIMIT:
        return s
    return s[:LIMIT - 3] + "..."


def find_receipt(n):
    hits = [p for p in AEG.glob(f"trials/**/receipt-{n:02d}.json")
            if "aeg-feed" not in p.parts]
    assert len(hits) == 1, f"receipt-{n:02d}: {len(hits)} matches"
    return hits[0]


def projection_of(receipt):
    delta = receipt.get("delta", {})
    task = truncate(f"{delta.get('kind', 'unknown')}: {delta.get('description', '')}")
    evidence = receipt.get("evidence", {})
    result = truncate(receipt.get("status", "Unknown") + "; evidence keys: "
                      + ", ".join(sorted(evidence.keys())))
    holes = receipt.get("documented_holes", [])
    residual = truncate("documented_holes: " + " | ".join(holes)
                        if holes else "documented_holes: none declared")
    return {"task": task, "result": result, "residual": residual}


def main(before_n, after_n, request_path, feed_dir=None):
    request_path = pathlib.Path(request_path)
    request_raw = request_path.read_bytes()
    before_path = find_receipt(before_n)
    after_path = find_receipt(after_n)
    before = json.loads(before_path.read_text())
    after = json.loads(after_path.read_text())
    proj_b = projection_of(before)
    proj_a = projection_of(after)
    response = {
        "version": 1,
        "request_sha256": sha_bytes(request_raw),
        "method": "declared-field-projection-v1",
        "sender_claim": ("AEG operator mechanical projection; "
                         "label unauthenticated"),
        "before": {"record_ref": f"receipt-{before_n:02d}",
                   "projection": proj_b},
        "after": {"record_ref": f"receipt-{after_n:02d}",
                  "projection": proj_a},
        "omissions": ("Mechanical projection of receipt fields; no semantic "
                      "acceptance; witness carries byte pointers."),
    }
    out_r = ROUND / f"response-from-{before_n:02d}-to-{after_n:02d}.json"
    out_r.write_text(json.dumps(response, indent=2, ensure_ascii=False) + "\n")
    # byte-level witness
    pointers = {"task": "/delta/kind and /delta/description",
                "result": "/status and /evidence",
                "residual": "/documented_holes"}
    witness = {
        "schema": "aeg.projection-witness", "version": 0,
        "before": {"receipt": before_n,
                   "receipt_sha256": sha_bytes(before_path.read_bytes()),
                   "feed_path": f"receipts/receipt-{before_n:02d}.json"},
        "after": {"receipt": after_n,
                  "receipt_sha256": sha_bytes(after_path.read_bytes()),
                  "feed_path": f"receipts/receipt-{after_n:02d}.json"},
        "request_sha256": sha_bytes(request_raw),
        "response_sha256": sha_bytes(out_r.read_bytes()),
        "pointers": pointers,
        "excerpts": {
            "before": {
                "delta_kind": before.get("delta", {}).get("kind"),
                "delta_description": before.get("delta", {}).get("description"),
                "status": before.get("status"),
                "documented_holes": before.get("documented_holes"),
            },
            "after": {
                "delta_kind": after.get("delta", {}).get("kind"),
                "delta_description": after.get("delta", {}).get("description"),
                "status": after.get("status"),
                "documented_holes": after.get("documented_holes"),
            },
        },
        "note": ("field values above are quoted verbatim from the pinned "
                 "receipt bytes; a receiver holding the feed can verify "
                 "excerpt equality and the projection rule"),
    }
    out_w = ROUND / f"projection-witness-{before_n:02d}-to-{after_n:02d}.json"
    out_w.write_text(json.dumps(witness, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {out_r.name} and {out_w.name}")
    print("before pin:", witness["before"]["receipt_sha256"][:16], "...")
    print("after pin: ", witness["after"]["receipt_sha256"][:16], "...")
    print("response pin:", witness["response_sha256"][:16], "...")
    for side, proj in (("before", proj_b), ("after", proj_a)):
        print(f"  {side}.task: {proj['task'][:80]}")


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]))
