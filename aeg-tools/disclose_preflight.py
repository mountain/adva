#!/usr/bin/env python3
"""Disclosure preflight: enforce the exchange permission boundary before send.

Checks a response file (and optional attachment): byte budget 16384, no
private filesystem-path patterns, field length bounds, request-sha binding,
method/version shape, and that the attachment keeps within its budget.

Usage:
  python3 disclose_preflight.py <request.json> <response.json> [attachment.json]
Exit 0 = ClearToSend; 1 = Blocked (findings printed).
"""
import hashlib
import json
import pathlib
import re
import sys

PRIVATE = [re.compile(r"/Users/"), re.compile(r"/home/"),
           re.compile(r"/private/"), re.compile(r"/var/"),
           re.compile(r"/Library/"), re.compile(r"/tmp/")]
LIMIT = 16384
FIELD_LIMIT = 1024


def sha_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def scan(raw, label, findings):
    for pat in PRIVATE:
        hits = pat.findall(raw)
        if hits:
            findings.append(f"{label}: private-pattern hit {pat.pattern} x{len(hits)}")


def main(request_path, response_path, attachment_path=None):
    findings = []
    req_raw = pathlib.Path(request_path).read_bytes()
    resp_raw = pathlib.Path(response_path).read_bytes()
    if len(resp_raw) > LIMIT:
        findings.append(f"response exceeds byte budget: {len(resp_raw)}")
    scan(resp_raw.decode(errors="replace"), "response", findings)
    try:
        resp = json.loads(resp_raw)
    except Exception as e:
        findings.append(f"response not valid JSON: {e}")
        resp = None
    if resp is not None:
        if resp.get("request_sha256") != sha_bytes(req_raw):
            findings.append("response does not bind the given request bytes")
        if resp.get("method") != "declared-field-projection-v1":
            findings.append("unexpected method")
        for side in ("before", "after"):
            proj = resp.get(side, {}).get("projection", {})
            for k in ("task", "result", "residual"):
                v = proj.get(k)
                if v is not None and (not isinstance(v, str) or len(v) > FIELD_LIMIT):
                    findings.append(f"{side}.{k} out of bounds")
        for k in ("sender_claim", "omissions"):
            v = resp.get(k)
            if not isinstance(v, str) or not 1 <= len(v) <= FIELD_LIMIT:
                findings.append(f"{k} missing or out of bounds")
    if attachment_path:
        att_raw = pathlib.Path(attachment_path).read_bytes()
        if len(att_raw) > LIMIT:
            findings.append(f"attachment exceeds byte budget: {len(att_raw)}")
        scan(att_raw.decode(errors="replace"), "attachment", findings)
    status = "ClearToSend" if not findings else "Blocked"
    print(json.dumps({"schema": "aeg.disclosure-preflight", "version": 0,
                      "status": status, "findings": findings,
                      "response_bytes": len(resp_raw)},
                     indent=2, ensure_ascii=False))
    return 0 if status == "ClearToSend" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2],
                  sys.argv[3] if len(sys.argv) > 3 else None))
