"""Frozen external joint-model campaign. Run with an outer 45-second timeout.

Codex (OpenAI), Unknown v0.3; Mingli Yuan account proxy, not endorsement.
"""

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ENGINE = HERE.parent
ROOT = ENGINE.parents[1]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bindings():
    paths = [ENGINE / name for name in ("meta.py", "verifier.py", "contract.json")]
    paths += [HERE / name for name in ("model.py", "checker.py", "run.py", "contract.json", "requests.json")]
    paths += [ROOT / "tests/python/test_epistemic_positivity.py"]
    return {str(p.relative_to(ROOT)): digest(p) for p in paths}


def construct(legacy):
    fixed = legacy["marked_zero"]
    opposite = legacy["marked_one"]
    for report in (fixed, opposite):
        if report["status"] != "Analyzed" or len(report["models"]) != 1 or len(report["models"][0]["realizers"]) != 1:
            raise ValueError("Unique checked static realizer required")
    rows = fixed["models"][0]["positive_masks"]
    replies = [entry["outputs"]["reply"] for entry in fixed["trace"]]
    base = {"positive_extensions": [rows[:], rows[:]], "modal": [[True, False], [False, True]],
            "sender": [0, 1], "transcripts": [[value] for value in replies]}
    cases = {name: copy.deepcopy(base) for name in (
        "equal_reply", "repeated_reply", "spoofed_claim", "trusted_binding", "fixed_sender",
        "conflated_relations", "swapped_positive")}
    cases["repeated_reply"]["transcripts"] = [[value]*4 for value in replies]
    cases["spoofed_claim"]["transcripts"] = [[value, "claimed-source:0"] for value in replies]
    cases["trusted_binding"]["transcripts"] = [[value, f"trusted-source:{i}"] for i, value in enumerate(replies)]
    cases["fixed_sender"]["sender"] = [0, 0]
    cases["conflated_relations"]["modal"] = [[True, True], [True, True]]
    other = opposite["models"][0]["positive_masks"]
    cases["swapped_positive"]["positive_extensions"] = [other[:], other[:]]
    return cases


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def campaign():
    start = time.monotonic()
    contract = json.loads((HERE / "contract.json").read_text())
    report = {"schema": "adva.external-epistemic-positivity-evidence.v0", "status": "Unknown",
              "native_authority": "NotGranted", "source_bindings": bindings(),
              "static_reports": {}, "static_receiving": {}, "models": {}, "results": {}, "receiving": {}}
    try:
        meta = load(ENGINE / "meta.py", "epistemic_legacy_meta")
        receiver = load(ENGINE / "verifier.py", "epistemic_legacy_receiver")
        producer = load(HERE / "model.py", "epistemic_bit_model")
        checker = load(HERE / "checker.py", "epistemic_set_checker")
        requests = json.loads((HERE / "requests.json").read_text())
        require(len(requests) == contract["bounds"]["static_requests"], "request count")
        for name, request in requests.items():
            result = meta.analyze(request)
            report["static_reports"][name] = result
            receipt = receiver.verify(request, result)
            report["static_receiving"][name] = receipt
            require(receipt["status"] == ("NoClaim" if name == "zero_fuel" else "Verified"), "legacy receiving: " + name)
        expected = {"joint": "Underdetermined", "marked_zero": "ForcedPositive", "marked_one": "ForcedNegative",
                    "conflict": "Inconsistent", "zero_fuel": "Unknown"}
        for name, status in expected.items():
            actual = next(q for q in report["static_reports"][name]["queries"] if q["name"] == "selected")
            require(actual["classification"] == status, "legacy query: " + name)
        report["models"] = construct(report["static_reports"])
        require(set(report["models"]) == set(contract["cases"]), "model cases")
        for name, model in report["models"].items():
            result = producer.evaluate(model)
            report["results"][name] = result
            receipt = checker.verify(model, result)
            report["receiving"][name] = receipt
            require(receipt["status"] == "Verified", "joint model receiving: " + name)
            require(time.monotonic()-start < contract["bounds"]["campaign_wall_seconds"], "campaign deadline")
        r = report["results"]
        for name in ("equal_reply", "repeated_reply", "spoofed_claim", "swapped_positive"):
            require(r[name]["ontology_satisfied"] and r[name]["knows_exists"] == [True, True]
                    and r[name]["necessarily_exists"] == [True, True]
                    and r[name]["identity_status"] == ["Underdetermined"]*2
                    and r[name]["non_saturation_witness"] == [0, 1], "ambiguity control: " + name)
        require(r["equal_reply"]["sender_godlike"] == [True, False], "base role")
        require(r["swapped_positive"]["sender_godlike"] == [False, True], "swapped interpretation")
        require(r["trusted_binding"]["ontology_satisfied"] and r["trusted_binding"]["identity_status"] == ["KnownTrue", "KnownFalse"]
                and r["trusted_binding"]["identity_descends"], "trusted binding")
        require(r["fixed_sender"]["ontology_satisfied"] and r["fixed_sender"]["identity_status"] == ["KnownTrue"]*2, "fixed sender")
        require(not r["conflated_relations"]["ontology_satisfied"]
                and not r["conflated_relations"]["checks"]["A4"]["holds"]
                and not r["conflated_relations"]["checks"]["A5"]["holds"], "modality conflation must fail")
        require(report["source_bindings"] == bindings(), "source changed")
        report["status"] = "Passed"
    except (ValueError, OSError, KeyError) as error:
        report["failure"] = str(error)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    # Refuse overwrite before executing; failures remain in their own report.
    with args.output.open("x") as stream:
        report = campaign()
        encoded = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
        if len(encoded.encode()) > 1_048_576:
            raise ValueError("output bound")
        stream.write(encoded)
    print(json.dumps({"status": report["status"], "models": len(report["results"]),
                      "failure": report.get("failure")}))
    return 0 if report["status"] == "Passed" else 1


if __name__ == "__main__":
    sys.exit(main())
