"""Audit the fixed peer text evidence without importing its native binary."""
import copy
import hashlib
import json
import resource
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PEER = ROOT / "experiments/advance_symbol_surface"
REPORT_HASH = "51694ca9400e5561591832bb9909ae62cbb8ef38274c8b98ba86420e674fd614"
BINARY = "_native.abi3.so"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    with path.open("rb") as stream:
        raw = stream.read(262145)
    require(len(raw) <= 262144, "text file budget")
    return raw


def check(manifest, retained, reply):
    require(len(manifest["files"]) == 54, "archive inventory size")
    expected = set(manifest["files"]) - {BINARY}
    require(set(retained) == expected and len(expected) == 53, "text coverage gap")
    for name, raw in retained.items():
        pin = manifest["files"][name]
        require(pin["encoding"] == "identity", "text encoding")
        require(len(raw) == pin["original_bytes"] == pin["stored_bytes"], "length mismatch")
        require(digest(raw) == pin["original_sha256"] == pin["stored_sha256"], "digest mismatch")
    require(digest(retained["report.json"]) == REPORT_HASH == reply["evidence"]["report_sha256"], "report binding")
    report = json.loads(retained["report.json"])
    native = json.loads(retained["native-load.json"])
    require(set(report["files"]) | {"report.json"} == set(manifest["files"]), "inventory coverage")
    for name, pin in report["files"].items():
        archived = manifest["files"][name]
        require(pin["bytes"] == archived["original_bytes"] and pin["sha256"] == archived["original_sha256"], "inventory pin")
    require(digest(retained["predecessor-handoff.json"]) == report["predecessor_sha256"] == reply["predecessor"]["sha256"], "predecessor binding")
    require(digest(retained["prior-advance.json"]) == report["prior_advance_sha256"] == reply["prior_advance_sha256"], "prior binding")
    doc = json.loads(retained["source/symbol-surface.adva"])
    obligations = json.loads(retained["source/obligations.json"])["items"]
    sites = [item["document_frontier_coordinate"] for item in obligations]
    require(len(sites) == 9 and all(x["status"] == "Open" for x in obligations), "open obligations")
    require([x["id"] for x in obligations] == native["remaining_annotation_ids"] == reply["remaining_obligations"], "obligation IDs")
    require(reply["observation"]["difference"] == report["finding"], "reply finding")
    source_names = [n for n in retained if n.startswith("source/")]
    require(len(source_names) == 8, "source coverage")
    for name in source_names:
        require(retained[name] == retained["library-" + name], "source/library difference")
    for i, name in enumerate(["presentation.json", "contract.json", "obligations.json"]):
        require(doc["carriers"][i]["carrier"]["structure"] == "sha256:" + digest(retained["source/" + name]), "payload reference")
    good = ["original", "library-copy", "unchanged-control", "payload-resolution-boundary"]
    bad = {"unknown-reference": "unknown carrier", "undeclared-site": "undeclared", "partial-output": "partially", "unknown-entrypoint": "unknown Adva entry point"}
    calls = native["calls"]
    require(len(calls) == native["native_load_invocations"] == 8, "call count")
    require(len({x["name"] for x in calls}) == 8 and {x["name"] for x in calls} == set(good) | set(bad), "call coverage")
    require(len(native["controls"]) == 8 and all(x is True for x in native["controls"].values()), "recorded controls")
    require(native["controls"] == report["controls"], "report controls")
    for call in calls:
        case = json.loads(retained["cases/" + call["name"] + ".json"])
        if call["name"] in bad:
            require(call["status"] == case["status"] == "Rejected", "recorded rejection")
            require(call["error"] == case["error"] and bad[call["name"]] in call["error"], "rejection detail")
        else:
            require(call["status"] == "NativeEnvelopeLoaded" and case == native["baseline"], "recorded loaded result")
    loaded = native["baseline"]
    transition = loaded["transition"]
    require(transition["state"] == "ready" and transition["recorded_output"] is None, "output boundary")
    require(transition["admission"] == {"mechanism": "verify", "status": "conditional", "remaining_subject": {"sites": sites}}, "conditional boundary")
    require(transition["form"]["declared_subject"]["sites"] == sites and transition["form"]["discharges"] == [], "formation boundary")
    require(all(native[k] == 0 for k in ["arithmetic_evaluations", "proof_replays", "game_moves"]), "reported scope")
    return {"text_files_checked": 53, "archive_files_declared": 54, "recorded_native_calls_checked": 8,
            "remaining_obligations": 9, "source_pairs_checked": 8,
            "native_document_digest_as_recorded": loaded["certificate"]["document_digest"]}


def main():
    started = time.perf_counter_ns()
    evidence = PEER / "evidence/run-01"
    manifest = json.loads(read(evidence / "manifest.json"))
    reply = json.loads(read(PEER / "reply.json"))
    retained = {}
    for name, pin in manifest["files"].items():
        if name == BINARY:
            continue
        path = (evidence / pin["stored_path"]).resolve()
        require(path.is_relative_to(evidence.resolve()), "path boundary")
        retained[name] = read(path)
    result = check(manifest, retained, reply)
    controls = {}
    shortened = dict(retained)
    shortened.pop("cases/partial-output.json")
    wrong_reply = copy.deepcopy(reply)
    wrong_reply["predecessor"]["sha256"] = "0" * 64
    for name, data, response in [("missing_text", shortened, reply), ("wrong_predecessor", retained, wrong_reply)]:
        try:
            check(manifest, data, response)
        except ValueError:
            controls[name] = "Rejected"
        else:
            raise ValueError("control unexpectedly accepted: " + name)
    result.update(status="TextEvidenceChecked", complete_archive_status="Unknown",
                  source_commit="e0e3433ebcaa2da6ec3e0bc1f67bd316f2c38547",
                  native_replay="NotRun", native_binary_checked=False,
                  residual="Native gzip artifact excluded from this text-only audit; no build authentication or native replay",
                  controls=controls, wall_ms_before_serialization=(time.perf_counter_ns() - started) / 1e6,
                  process_peak_rss_kib_linux=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  unmeasured=["retrieval", "authoring", "report serialization"])
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
