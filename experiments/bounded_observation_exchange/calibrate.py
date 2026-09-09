"""Reproduce synthetic protocol controls; never represents a reply from AEG."""
import copy
import json
import resource
import sys
import time
from pathlib import Path

from check_exchange import FIELDS, LIMIT, METHOD, check, digest

ROOT = Path(__file__).resolve().parent


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def main():
    started = time.perf_counter()
    request = (ROOT / "request.json").read_bytes()
    baseline = dict(zip(FIELDS, ("synthetic task A", "Unknown", "need witness")))
    reply = {"version": 1, "request_sha256": digest(request), "method": METHOD,
             "sender_claim": "SYNTHETIC FIXTURE, not the AEG peer",
             "before": {"record_ref": "fixture:before", "projection": baseline},
             "after": {"record_ref": "fixture:after", "projection": {**baseline, "result": "candidate recorded"}},
             "omissions": "All source records omitted; this tests literal comparison only."}
    cases = [("new disclosed difference", request, encode(reply), "VariationObserved")]
    same = copy.deepcopy(reply)
    same["after"]["projection"] = dict(baseline)
    cases.append(("same disclosed projection", request, encode(same), "EvidenceStutter"))
    partial = copy.deepcopy(reply)
    partial["after"]["projection"]["residual"] = None
    cases.append(("difference with incomplete coverage", request, encode(partial), "Unknown"))
    cases.append(("no real reply", request, None, "Unknown"))
    for name, key, value in [("wrong request", "request_sha256", "0" * 64),
                              ("wrong method", "method", "other-v1"),
                              ("boolean version", "version", True)]:
        bad = copy.deepcopy(reply)
        bad[key] = value
        cases.append((name, request, encode(bad), "Rejected"))
    cases.append(("duplicate JSON key", request, b'{"version":1,"version":1}', "Rejected"))
    cases.append(("byte budget", request, b" " * (LIMIT + 1), "Rejected"))
    bad = copy.deepcopy(reply)
    del bad["after"]["projection"]["residual"]
    cases.append(("omitted field", request, encode(bad), "Rejected"))
    # Replay under a changed question must not acquire the old acknowledgement.
    new_request = json.loads(request)
    new_request["question"] = "A different question"
    cases.append(("replay against changed question", encode(new_request), encode(reply), "Rejected"))
    reuse = copy.deepcopy(reply)
    reuse["before"]["record_ref"] = "fixture:B0"
    reuse["after"]["record_ref"] = "fixture:B1"
    reuse["before"]["projection"] = dict(zip(FIELDS, ("task B", "candidate", "missing coverage")))
    reuse["after"]["projection"] = dict(zip(FIELDS, ("task B", "candidate", "missing source witness")))
    cases.append(("new-instance reuse", request, encode(reuse), "VariationObserved"))
    constructed = time.perf_counter()
    results = []
    for name, req, resp, expected in cases:
        result = check(req, resp)
        if result["status"] != expected:
            raise AssertionError((name, expected, result))
        if result["semantic_acceptance"] != "Withheld" or result["resource_grant"] != 0:
            raise AssertionError("acceptance/resource boundary crossed")
        results.append({"name": name, "expected": expected, "result": result})
    # Repeated delivery is a pure replay, with no grant or persistent state mutation.
    first = check(request, encode(reply))
    if check(request, encode(reply)) != first:
        raise AssertionError("same bytes changed result")
    results.append({"name": "repeat delivery", "result": first, "expected": "VariationObserved"})
    verified = time.perf_counter()
    payload = encode({"synthetic_cases": results})
    if json.loads(payload)["synthetic_cases"] != results:
        raise AssertionError("serialization changed evidence")
    serialized = time.perf_counter()
    fixtures = [{"name": name, "request_utf8": req.decode(),
                 "response_utf8": resp.decode() if resp is not None else None,
                 "expected": expected} for name, req, resp, expected in cases]
    (ROOT / "fixtures.json").write_bytes(encode(fixtures))
    (ROOT / "synthetic-response.json").write_bytes(encode(reply))
    template = copy.deepcopy(reply)
    template["sender_claim"] = "TEMPLATE ONLY: replace with an authorized sender label"
    for side in ("before", "after"):
        template[side] = {"record_ref": "replace-with-opaque-record-label", "projection": dict.fromkeys(FIELDS)}
    template["omissions"] = "Describe what is withheld or unverified. This template is not a peer reply."
    (ROOT / "response-template.json").write_bytes(encode(template))
    # The live exchange status is maintained separately; calibration must not reset it.
    saved = time.perf_counter()
    evidence = {"kind": "synthetic protocol calibration", "real_peer_reply": "AwaitingReply",
                "passed": len(results), "results": results,
                "metrics": {"construct_seconds": constructed - started,
                            "verify_including_reuse_seconds": verified - constructed,
                            "serialization_replay_seconds": serialized - verified,
                            "artifact_writes_seconds": saved - serialized,
                            "measured_elapsed_seconds": saved - started,
                            "maxrss_native_units": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                            "maxrss_unit": "KiB" if sys.platform.startswith("linux") else "platform-dependent",
                            "candidate_searches": 0,
                            "excluded": "research, coding, network, publication, final evidence file write"}}
    (ROOT / "evidence.json").write_bytes(encode(evidence))
    print(json.dumps({"passed": len(results), "metrics": evidence["metrics"]}, indent=2))


if __name__ == "__main__":
    main()
