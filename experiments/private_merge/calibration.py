#!/usr/bin/env python3
"""One fixed external private merge calibration; no old suite execution."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import resource
import time
import merge as protocol

CONTRACT_SHA = "4b9092955efa1328f10bd111c4c18304fe367838a2528f404df66058f11120b5"

CASES = [["full-main", "FiniteMergeVerified"], ["missing-right", "Unknown"],
         ["partial-right", "Unknown"], ["exact-duplicate-left", "FiniteMergeVerified"],
         ["reversed-arrival", "FiniteMergeVerified"], ["conflicting-duplicate", "Blocked"],
         ["purpose-drift", "Blocked"], ["subject-drift", "Blocked"],
         ["privacy-downgrade", "Blocked"], ["copied-root-fuel", "Blocked"],
         ["forged-trace", "Blocked"], ["erased-pending", "Blocked"],
         ["fresh-coefficients", "FiniteMergeVerified"], ["genuine-root-counterexample", "Refuted"]]


def validate_contract(c):
    if (c["schema"] != "adva.private-merge-run-contract.research" or type(c["version"]) is not int
            or c["version"] != 0 or c["source_sha256"] != protocol.SOURCE_SHA
            or protocol.encoded(c["cases"]) != protocol.encoded(CASES)):
        raise ValueError("frozen calibration contract mismatch")
    required = {"subprocess_seconds": 5, "global_units": 2000, "root_grant": 256,
                "fork_cost": 1, "left_work": 5, "right_work": 7, "partial_right_work": 2,
                "branch_reserve": 64, "merge_reserve": 64, "max_receipts": 3,
                "max_json_bytes": 262144, "new_searches": 0, "calibration_invocations": 1,
                "standalone_cli_replays": 1, "implementation_error_repair_replays": 1}
    if protocol.encoded(c["limits"]) != protocol.encoded(required):
        raise ValueError("frozen limits mismatch")
    if (c["arithmetic"]["main_coefficients"] != [2, 3, 1]
            or c["arithmetic"]["fresh_coefficients"] != [-1, 2, 3]
            or c["arithmetic"]["inputs"] != list(range(-3, 4))
            or c["partition"] != {"left": [-3, -2, -1], "right": [0, 1, 2, 3]}):
        raise ValueError("frozen arithmetic fixture mismatch")


def build(root, meter, both=True):
    meter.charge()  # physical construction of one declared root-local fork
    result = [protocol.make_branch(root, "left", meter)]
    if both:
        result.append(protocol.make_branch(root, "right", meter))
    return result


def run(contract, output):
    meter, records = protocol.OLD.Meter(), []
    phases = {"construction_ns": 0, "checking_ns": 0, "serialization_ns": 0, "fresh_reuse_ns": 0}
    start = time.perf_counter_ns()
    main_root = protocol.root_question()
    main_receipts = build(main_root, meter)
    phases["construction_ns"] += time.perf_counter_ns() - start
    for name, expected in CASES:
        start = time.perf_counter_ns()
        root, receipts = copy.deepcopy(main_root), copy.deepcopy(main_receipts)
        if name == "missing-right":
            receipts = receipts[:1]
        elif name == "partial-right":
            root = protocol.root_question(right_work=2)
            receipts = build(root, meter)
        elif name == "exact-duplicate-left":
            receipts.append(copy.deepcopy(receipts[0]))
        elif name == "reversed-arrival":
            receipts.reverse()
        elif name == "conflicting-duplicate":
            receipts.append(copy.deepcopy(receipts[0]))
            receipts[-1]["receipt"]["reason"] = "conflicting payload with unchanged branch id"
        elif name == "purpose-drift":
            receipts[0]["profile"]["value_direction"] = "publish results regardless of subject purpose"
        elif name == "subject-drift":
            receipts[0]["profile"]["subject"]["name"] = "different-subject"
        elif name == "privacy-downgrade":
            receipts[0]["profile"]["privacy"]["policy"] = "public"
        elif name == "copied-root-fuel":
            receipts[0]["final_ledger"]["initial"] = 256
        elif name == "forged-trace":
            point = next(e for e in receipts[0]["receipt"]["events"] if e["kind"] == "point")
            point["values"]["source_trace"][0] += 1
        elif name == "erased-pending":
            root = protocol.root_question(right_work=2)
            receipts = build(root, meter)
            receipts[1]["receipt"]["pending"] = []
        elif name == "fresh-coefficients":
            root = protocol.root_question((-1, 2, 3))
            receipts = build(root, meter)
        elif name == "genuine-root-counterexample":
            root = protocol.root_question(target_coefficients=(2, 3, 2))
            receipts = build(root, meter, both=False)
        construction_elapsed = time.perf_counter_ns() - start
        phases["construction_ns"] += construction_elapsed
        t = time.perf_counter_ns()
        result = protocol.merge(root, receipts, meter)
        check_elapsed = time.perf_counter_ns() - t
        phases["checking_ns"] += check_elapsed
        record = {"id": name, "root": root, "receipts": receipts, "result": result,
                  "expected_status": expected, "expectation_met": result["semantic"]["status"] == expected,
                  "construction_ns": construction_elapsed, "checking_ns": check_elapsed}
        t = time.perf_counter_ns()
        # merge's audit reserve already charged the serialization of this checkpoint.
        data = protocol.encoded(record)
        if len(data) > protocol.MAX_BYTES:
            raise ValueError("case size bound")
        phases["serialization_ns"] += time.perf_counter_ns() - t
        if name == "fresh-coefficients":
            phases["fresh_reuse_ns"] = construction_elapsed + check_elapsed
        records.append(record)
    by_name = {r["id"]: r for r in records}
    projection_checks = {}
    for name in ("exact-duplicate-left", "reversed-arrival"):
        projection_checks[name] = {
            "same_semantic_projection": protocol.encoded(by_name[name]["result"]["semantic"]) == protocol.encoded(by_name["full-main"]["result"]["semantic"]),
            "same_historical_cost": by_name[name]["result"]["historical_resource"] == by_name["full-main"]["result"]["historical_resource"],
            "arrival_history_retained": by_name[name]["result"]["arrival_history"] != by_name["full-main"]["result"]["arrival_history"]}
    # Three physical writes are an explicitly separated experiment checkpoint cost,
    # not grants for child continuation or hidden work in a logical root.
    for _ in range(3):
        meter.charge()
    t = time.perf_counter_ns()
    protocol.save_new(output / "main-root.json", main_root)
    protocol.save_new(output / "main-receipts.json", main_receipts)
    phases["serialization_ns"] += time.perf_counter_ns() - t
    report = {"schema": "adva.private-merge-calibration.research", "version": 0,
              "cases": records, "projection_checks": projection_checks,
              "all_expectations_met": all(r["expectation_met"] for r in records),
              "all_projection_checks_met": all(all(check.values()) for check in projection_checks.values()),
              "global_physical_units": meter.spent, "global_limit_across_calibration_and_cli": 2000,
              "standalone_cli_replay": "NotRun by calibration; caller must add its actual physical cost",
              "experiment_checkpoint_units": 3, "native_calls": 0, "search_nodes": 0,
              "costs": {**phases, "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                        "peak_rss_scope": "Linux calibration Python process",
                        "phase_note": "Fresh reuse overlaps construction/checking. Final report disk write is measured by outer supervisor.",
                        "authoring_research_network": "Missing"}}
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol.restrict_runtime()
    with args.contract.open("rb") as stream:
        contract_raw = stream.read(protocol.MAX_BYTES + 1)
    if len(contract_raw) > protocol.MAX_BYTES or hashlib.sha256(contract_raw).hexdigest() != CONTRACT_SHA:
        raise ValueError("frozen contract bytes mismatch")
    contract = json.loads(contract_raw)
    validate_contract(contract)
    args.output_dir.mkdir(parents=True, exist_ok=False)
    report = run(contract, args.output_dir)
    report["contract_sha256"] = CONTRACT_SHA
    report["dependency_sha256"] = protocol.SOURCE_SHA
    size = protocol.save_new(args.output_dir / "report.json", report)
    print(json.dumps({"cases": len(report["cases"]), "all_expectations_met": report["all_expectations_met"],
                      "all_projection_checks_met": report["all_projection_checks_met"],
                      "physical_units": report["global_physical_units"], "report_bytes": size}))
    if not report["all_expectations_met"] or not report["all_projection_checks_met"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
