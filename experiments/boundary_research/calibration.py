#!/usr/bin/env python3
"""Research 0144: one frozen external boundary revision, never native free."""
import argparse
import copy
import hashlib
import json
import resource
import signal
import time
from fractions import Fraction
from pathlib import Path

CONTRACT = "e11b9a87c868ca831ff82d4f6a61a07d6cf167d00cda9c6ce5362f5ed1bf971c"
SOURCE = "c6e5f7a88dabbb3141d16e3fbe9da59853dba79db756f2f6ee868b33956df09f"
LIMIT = 262144
OBLIGATIONS = ["observation", "model-gap", "native-free"]
PARTITION = {"discharged": ["observation"], "retained": ["native-free"],
             "replaced": {"model-gap": ["candidate-v2"]}}


def encoded(x):
    return (json.dumps(x, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def digest(x):
    return hashlib.sha256(encoded(x)).hexdigest()


def scope(q):
    return {k: v for k, v in q.items() if k != "name"}


def unique_pairs(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError("duplicate JSON key")
        out[k] = v
    return out


def decode(raw):
    if len(raw) > LIMIT:
        raise ValueError("file-size-bound")
    return json.loads(raw, object_pairs_hook=unique_pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite")))


def read(path, expected):
    with Path(path).open("rb") as f:
        raw = f.read(LIMIT + 1)
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("pinned-input-hash")
    return decode(raw)


class Exhausted(Exception):
    pass


class Meter:
    def __init__(self):
        self.spent = 0

    def use(self, ledger=None):
        if self.spent >= 2000 or (ledger is not None and ledger[0] <= 0):
            raise Exhausted("finite-fuel-exhausted")
        self.spent += 1
        if ledger is not None:
            ledger[0] -= 1
            ledger[1] += 1


def rational(raw, meter, ledger=None):
    meter.use(ledger)
    if not isinstance(raw, str) or len(raw) > 80:
        raise ValueError("rational-encoding")
    parts = raw.split("/")
    if len(parts) not in (1, 2) or any(not p.lstrip("-").isdigit() for p in parts):
        raise ValueError("rational-encoding")
    nums = [int(p) for p in parts]
    if any(abs(n).bit_length() > 128 for n in nums) or (len(nums) == 2 and nums[1] <= 0):
        raise ValueError("rational-domain-bound")
    value = Fraction(*nums)
    if str(value) != raw:
        raise ValueError("noncanonical-rational")
    return value


def unique(xs):
    return isinstance(xs, list) and all(isinstance(x, str) for x in xs) and len(set(xs)) == len(xs)


def point(q, meter, ledger=None):
    meter.use(ledger)
    fixed = {"schema": "adva.judgment-question.research", "version": 0,
             "domain": "Q", "observer": "exact-rational-v0", "quantifier": "at-declared-input",
             "relation": "equal", "ordered_pair": [["mul", ["input", "x"], ["input", "y"]], ["const", "1"]]}
    if (set(q) != set(fixed) | {"name", "environment"} or type(q["version"]) is not int
            or any(q[k] != v for k, v in fixed.items())):
        raise ValueError("question-shape")
    if set(q["environment"]) != {"x", "y"}:
        raise ValueError("environment-shape")
    x, y = (rational(q["environment"][k], meter, ledger) for k in ("x", "y"))
    p = x * y
    if max(abs(p.numerator).bit_length(), p.denominator.bit_length()) > 128:
        raise ValueError("product-domain-bound")
    if not any(x == Fraction((1 << k) + 1, 1 << k) and y == Fraction((1 << k) - 1, 1 << k)
               for k in (27, 30)):
        raise ValueError("outside-frozen-points")
    return p


def binding(src):
    return digest({"boundary_version": 0, "question": scope(src["subject"]["question"]),
                   "candidates": src["subject"]["candidate_universe"],
                   "history": src["case"]["outcome"]["history"], "obligations": OBLIGATIONS})


def reconstruct(src, meter, ledger):
    q = src["subject"]["question"]
    p = point(q, meter, ledger)
    obj, old = src["object"], src["case"]["outcome"]
    receipt = obj["receipt"]
    if (scope(obj["question"]) != scope(q) or receipt["scope"] != scope(q)
            or receipt["scope_sha256"] != digest(scope(q))
            or receipt["values"] != [{"rational": str(p)}, {"rational": "1"}]
            or receipt["residual"] != str(p - 1) or receipt["verdict"] != "Different"):
        raise ValueError("stale-or-false-point-data")
    cs = src["subject"]["candidate_universe"]
    if cs != [{"id": "unit", "prediction": "1"}, {"id": "dyadic-product", "prediction": "2"}]:
        raise ValueError("source-candidate-scope")
    refs = []
    for c in cs:
        v = rational(c["prediction"], meter, ledger)
        if v == p:
            raise ValueError("source-is-not-model-gap")
        refs.append({"id": c["id"], "prediction": str(v), "observed": str(p),
                     "difference": str(v - p), "scope_sha256": digest(scope(q))})
    h = old["history"]
    if (old["result"]["status"] != "ModelGap" or len(h) != 1 or h[0]["status"] != "ModelGap"
            or h[0]["scope_sha256"] != digest(scope(q))
            or [h[0]["remaining_before"], h[0]["spent_before"]] != [500, 0]
            or [h[0]["remaining_after"], h[0]["spent_after"]] != [477, 23]
            or [old["resource"]["local_remaining"], old["resource"]["local_spent"]] != [477, 23]):
        raise ValueError("source-post-ledger")
    return p, refs


def proposal(src, meter):
    meter.use()
    p = point(src["subject"]["question"], meter)
    _, refs = reconstruct(src, meter, [477, 23])
    return {"name": "revised-question", "source_binding": binding(src),
            "question": copy.deepcopy(src["subject"]["question"]), "method_version": 0,
            "boundary_version": 1, "partition": copy.deepcopy(PARTITION),
            "target_obligations": ["native-free", "candidate-v2"],
            "candidate": {"id": "dyadic-product-v2", "prediction": str(p)},
            "old_refutations": refs, "remaining_fuel": 477, "spent_fuel": 23,
            "requested_action": "external-revised-checkpoint"}


def gate(src, prop, meter):
    requested_ledger = [prop.get("remaining_fuel", 0), prop.get("spent_fuel", 0)]
    ledger = [477, 23]
    initial = list(ledger)
    base = meter.spent
    result = {"status": "Blocked", "old_task_status": "ModelGap", "new_boundary": None,
              "permitted_action": None, "native_free": "Unimplemented", "residual": ["native-free", "model-gap"]}
    refs, p = [], None
    try:
        meter.use()
        if any(type(v) is not int for v in requested_ledger) or requested_ledger != [477, 23]:
            if all(type(v) is int for v in requested_ledger) and requested_ledger == [0, 500]:
                raise Exhausted("finite-fuel-exhausted")
            raise ValueError("source-fuel-not-inherited")
        meter.use(ledger)
        p, refs = reconstruct(src, meter, ledger)
        if prop["source_binding"] != binding(src) or scope(prop["question"]) != scope(src["subject"]["question"]):
            raise ValueError("source-or-question-binding")
        if prop["old_refutations"] != refs:
            raise ValueError("old-refutation-not-retained")
        if prop.get("rename_only") is True:
            result.update(status="ModelGap", reason="display-rename-only-no-revision")
        else:
            part = prop["partition"]
            if set(part) != {"discharged", "retained", "replaced"} or not isinstance(part["replaced"], dict):
                raise ValueError("partition-shape")
            pieces = [part["discharged"], part["retained"], list(part["replaced"])]
            if not all(unique(x) for x in pieces) or not unique(sum(pieces, [])) or set(sum(pieces, [])) != set(OBLIGATIONS):
                raise ValueError("source-obligation-not-exactly-once")
            children = list(part["replaced"].values())
            if not all(unique(x) for x in children):
                raise ValueError("duplicate-replacement-obligation")
            targets = part["retained"] + sum(children, [])
            if (not unique(targets) or not unique(prop["target_obligations"])
                    or set(targets) != set(prop["target_obligations"]) or part != PARTITION):
                raise ValueError("target-obligation-conservation")
            meter.use(ledger)
            if (type(prop["boundary_version"]) is not int or type(prop["method_version"]) is not int
                    or prop["boundary_version"] != 1 or prop["method_version"] != 0):
                raise ValueError("boundary-or-method-version")
            if prop["requested_action"] != "external-revised-checkpoint":
                raise ValueError("native-free-unimplemented")
            c = prop["candidate"]
            if c["id"] != "dyadic-product-v2":
                raise ValueError("candidate-identity")
            v = rational(c["prediction"], meter, ledger)
            x, y = (rational(src["subject"]["question"]["environment"][k], meter, ledger) for k in ("x", "y"))
            independent = v.numerator * x.denominator * y.denominator == v.denominator * x.numerator * y.numerator
            if (v == p) != independent or not independent:
                raise ValueError("candidate-prediction-refuted")
            result.update(status="TaskBoundarySatisfied", reason="checked-external-boundary-revision",
                          new_boundary=1, permitted_action="external-revised-checkpoint", residual=["native-free"],
                          integer_crosscheck=independent, checked_new_obligations=["candidate-v2"])
    except Exhausted as e:
        result.update(status="Unknown", reason=str(e))
    except (ValueError, KeyError, TypeError, IndexError, ZeroDivisionError) as e:
        result.update(status="Blocked", reason=str(e))
    event = {"source_binding": binding(src), "status": result["status"], "remaining_before": initial[0],
             "spent_before": initial[1], "remaining_after": ledger[0], "spent_after": ledger[1],
             "global_charged_units": meter.spent - base, "local_charged_units": ledger[1] - initial[1],
             "requested_ledger": requested_ledger, "old_task_remains_open": True}
    return {"result": result, "old_refutations": refs, "recomputed_observation": None if p is None else str(p),
            "source_obligations": OBLIGATIONS, "proposed_partition": prop.get("partition"),
            "proposed_target_obligations": prop.get("target_obligations"), "resource": event,
            "source_history": copy.deepcopy(src["case"]["outcome"]["history"]), "transition_history": [event]}


def fresh_source(src, meter):
    meter.use()
    out = copy.deepcopy(src)
    q = out["subject"]["question"]
    q["name"] = "product-k30"
    q["environment"] = {"x": str(Fraction((1 << 30) + 1, 1 << 30)), "y": str(Fraction((1 << 30) - 1, 1 << 30))}
    p = point(q, meter)
    out["object"]["question"] = copy.deepcopy(q)
    out["object"]["receipt"] = {"scope": scope(q), "scope_sha256": digest(scope(q)),
                                  "values": [{"rational": str(p)}, {"rational": "1"}],
                                  "residual": str(p - 1), "verdict": "Different",
                                  "authority": "new external point data, constructed in this run"}
    out["object"]["source"] = {"meaning": "fresh calibration fixture; not a historical receipt"}
    out["case"]["outcome"]["history"][0]["scope_sha256"] = digest(scope(q))
    out.pop("origin_commit", None)
    out.pop("origin_report_sha256", None)
    out["case"]["outcome"].pop("evidence", None)
    out["note"] = "Fresh k30 synthetic ModelGap fixture; prescribed 477/23 post-ledger, independently reconstructed before revision."
    return out


def run(contract, src, meter):
    costs = {}
    t = time.perf_counter_ns()
    main = proposal(src, meter)
    new_src = fresh_source(src, meter)
    new = proposal(new_src, meter)
    cases = [(name, copy.deepcopy(src), copy.deepcopy(main)) for name in contract["trials"]]
    cases[1][2]["name"] = "display-renamed"; cases[1][2]["rename_only"] = True
    cases[1][2]["candidate"] = None
    cases[1][2]["boundary_version"] = 0
    cases[1][2]["partition"] = {"discharged": [], "retained": list(OBLIGATIONS), "replaced": {}}
    cases[1][2]["target_obligations"] = list(OBLIGATIONS)
    cases[2][2]["partition"]["retained"] = []
    cases[2][2]["target_obligations"] = ["candidate-v2"]
    cases[3][2]["partition"]["discharged"].append("native-free")
    cases[4][2]["source_binding"] = "stale"
    cases[5][2]["candidate"]["prediction"] = "1"
    cases[6][2]["remaining_fuel"] = 500; cases[6][2]["spent_fuel"] = 0
    cases[7][2]["remaining_fuel"] = 0; cases[7][2]["spent_fuel"] = 500
    cases[8][2]["requested_action"] = "native-free"
    cases[9][2]["old_refutations"] = []
    cases[10] = (contract["trials"][10], new_src, new)
    cases[11][2]["question"] = copy.deepcopy(new_src["subject"]["question"])
    for _ in cases:
        meter.use()
    costs["construction_ns"] = time.perf_counter_ns() - t
    records = []
    t = time.perf_counter_ns()
    for i, (name, source, prop) in enumerate(cases):
        started = time.perf_counter_ns()
        outcome = gate(source, prop, meter)
        elapsed = time.perf_counter_ns() - started
        expected = "TaskBoundarySatisfied" if i in (0, 10) else "ModelGap" if i == 1 else "Unknown" if i == 7 else "Blocked"
        records.append({"id": name, "proposal": prop, "source": "fresh-k30" if i == 10 else "historical-k27",
                        "outcome": outcome, "expected_status": expected,
                        "expectation_met": outcome["result"]["status"] == expected, "checking_ns": elapsed})
    costs["checking_ns"] = time.perf_counter_ns() - t
    costs["fresh_reuse_checking_ns"] = records[10]["checking_ns"]
    t = time.perf_counter_ns()
    meter.use()
    serialized = encoded({"sources": {"historical-k27": src, "fresh-k30": new_src}, "cases": records})
    restored = decode(serialized)
    costs["serialization_roundtrip_ns"] = time.perf_counter_ns() - t
    replay = []
    t = time.perf_counter_ns()
    for i in (0, 2):
        r = restored["cases"][i]
        again = gate(restored["sources"][r["source"]], r["proposal"], meter)
        replay.append({"id": r["id"], "matches": again == r["outcome"], "outcome": again})
    costs["reconstruction_ns"] = time.perf_counter_ns() - t
    return {"schema": "adva.boundary-research-report.research", "version": 0,
            "scope": contract["scope"], "contract_sha256": CONTRACT, "source_sha256": SOURCE,
            "sources": {"historical-k27": src, "fresh-k30": new_src}, "cases": records,
            "serialized_reconstruction": replay, "all_expectations_met": all(r["expectation_met"] for r in records) and all(r["matches"] for r in replay),
            "costs": costs, "charged_units": meter.spent, "max_charged_units": 2000,
            "search_nodes": 0, "native_calls": 0, "invocations_in_this_report": 1,
            "unmeasured": ["research and implementation wall time", "complete toolchain runnability", "global anti-fork resource conservation"],
            "cost_note": "Fresh reuse timing is a subset of checking time. Final report encoding/writing and host process startup are outside phase timings; measured by host supervisor if supplied.",
            "residual": ["native-free", "native cut/translation semantics", "automatic candidate generation", "real user utility"]}


def main():
    parser = argparse.ArgumentParser()
    for flag in ("contract", "source", "output"):
        parser.add_argument("--" + flag, required=True)
    args = parser.parse_args()
    if Path(args.output).exists():
        raise ValueError("output-already-exists")
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(Exhausted("wall-bound")))
    signal.alarm(5)
    start = time.perf_counter_ns()
    contract, source = read(args.contract, CONTRACT), read(args.source, SOURCE)
    report = run(contract, source, Meter())
    report["runner_elapsed_ns_before_final_write"] = time.perf_counter_ns() - start
    report["process_peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    report["peak_rss_platform"] = "Linux ru_maxrss KiB; whole process, not file size"
    raw = encoded(report)
    if len(raw) > LIMIT:
        raise ValueError("report-size-bound")
    with Path(args.output).open("xb") as f:
        f.write(raw)
    signal.alarm(0)
    print(json.dumps({"all_expectations_met": report["all_expectations_met"], "trials": len(report["cases"]),
                      "charged_units": report["charged_units"], "report_bytes": len(raw)}))
    return 0 if report["all_expectations_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
