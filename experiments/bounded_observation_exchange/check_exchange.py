"""Local, bounded checking of disclosed field differences; no native admission."""
import argparse
import hashlib
import json
from pathlib import Path

LIMIT = 16384
FIELDS = ("task", "result", "residual")
METHOD = "declared-field-projection-v1"


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def decode(raw):
    if len(raw) > LIMIT:
        raise ValueError("byte budget exceeded")
    def invalid_constant(value):
        raise ValueError("non-JSON constant: " + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid_constant)


def read(path):
    with Path(path).open("rb") as stream:
        return stream.read(LIMIT + 1)


def check(request_raw, response_raw=None):
    report = {"status": "Unknown", "acknowledge": None,
              "source_binding": "Unverified", "semantic_acceptance": "Withheld",
              "native_admission": "not-granted", "resource_grant": 0}
    try:
        request = decode(request_raw)
        if (type(request) is not dict or request.get("version") != 1
                or type(request.get("version")) is not int
                or request.get("method") != METHOD
                or request.get("fields") != list(FIELDS)):
            raise ValueError("unsupported request contract")
        if response_raw is None:
            report["reason"] = "AwaitingReply"
            return report
        response = decode(response_raw)
        required = {"version", "request_sha256", "method", "sender_claim",
                    "before", "after", "omissions"}
        if type(response) is not dict or set(response) != required:
            raise ValueError("response shape mismatch")
        if type(response["version"]) is not int or response["version"] != 1:
            raise ValueError("response version mismatch")
        if response["request_sha256"] != digest(request_raw):
            raise ValueError("response belongs to a different request byte sequence")
        if response["method"] != METHOD:
            raise ValueError("observation method mismatch")
        for field in ("sender_claim", "omissions"):
            if type(response[field]) is not str or not 1 <= len(response[field]) <= 1024:
                raise ValueError("missing or oversized " + field)
        for side in ("before", "after"):
            snapshot = response[side]
            if type(snapshot) is not dict or set(snapshot) != {"record_ref", "projection"}:
                raise ValueError("snapshot shape mismatch")
            if type(snapshot["record_ref"]) is not str or not 1 <= len(snapshot["record_ref"]) <= 256:
                raise ValueError("invalid external record reference")
            values = snapshot["projection"]
            if type(values) is not dict or set(values) != set(FIELDS):
                raise ValueError("projection must explicitly list all three fields")
            if any(v is not None and (type(v) is not str or len(v) > 1024) for v in values.values()):
                raise ValueError("projection fields must be bounded strings or null")
        report["acknowledge"] = {"request_sha256": digest(request_raw),
                                 "response_sha256": digest(response_raw)}
        before, after = (response[s]["projection"] for s in ("before", "after"))
        missing = [k for k in FIELDS if before[k] is None or after[k] is None]
        changed = [k for k in FIELDS if k not in missing and before[k] != after[k]]
        report.update(missing_fields=missing, changed_fields=changed,
                      scope="literal equality of the three disclosed strings only")
        report["status"] = ("Unknown" if missing else
                            "VariationObserved" if changed else "EvidenceStutter")
        report["reason"] = "DisclosureIncomplete" if missing else "DeclaredProjectionCompared"
        report["next_obligation"] = "Supply an authorized source-to-projection witness before semantic acceptance."
    except (ValueError, TypeError, KeyError, RecursionError) as error:
        report.update(status="Rejected", reason=str(error))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request")
    parser.add_argument("response", nargs="?")
    args = parser.parse_args()
    try:
        report = check(read(args.request), read(args.response) if args.response else None)
    except OSError as error:
        report = {"status": "Unknown", "reason": str(error), "native_admission": "not-granted"}
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
