#!/usr/bin/env python3
"""Frozen external knowledge-boundary calibration; never a native free producer."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import shutil
import signal
import sys
import time
import tracemalloc

CONTRACT_HASH = "840404e857a3d99626ee0f6876b310823ee0a0a5577834b58d30462ddbfcb389"
CHECKER_HASH = "2f1c1e90e3dc1ffd11c8e6d7630eed6bdf2956df7ea3492f144631c6b5d1b842"
METHOD_HASH = "d9d71c7dd2f4703fd8673f5cc7f8d3d26e06ceebf4ab1935c7e0147cedf72553"
MAX_BYTES = 262144
SUBJECT_KEYS = {"schema", "version", "name", "question", "candidate_universe",
                "candidate_coverage", "active_candidate_ids", "requested_action",
                "method_sha256", "remaining_fuel", "spent_fuel", "history"}
OBJECT_KEYS = {"schema", "version", "name", "question", "receipt", "source"}
EVENT_KEYS = {"index", "scope_sha256", "method_sha256", "before", "after", "status",
              "remaining_before", "remaining_after", "spent_before", "spent_after"}


def read(path):
    with Path(path).open("rb") as handle:
        data = handle.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("input-byte-boundary")
    return data


def parse(raw):
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ValueError("duplicate-json-key")
            value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite-json")))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked_module(root):
    path = root / "experiments/judgment_distinction/calibration.py"
    raw = read(path)
    if sha(raw) != CHECKER_HASH:
        raise ValueError("pinned-checker-byte-mismatch")
    spec = importlib.util.spec_from_file_location("adva_0142_checked", path)
    module = importlib.util.module_from_spec(spec)
    # Execute exactly the verified bytes; avoid a second path read or stale pyc.
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return module


class TaskFuel:
    """A local view of one shared invocation Fuel, never an independent grant."""
    def __init__(self, shared, remaining):
        self.shared, self.remaining = shared, remaining

    def charge(self):
        if self.remaining <= 0:
            raise self.shared.meter.exhausted("task-fuel-exhausted")
        self.shared.charge()
        self.remaining -= 1


class Runner:
    def __init__(self, old, contract, method, method_raw):
        self.old, self.contract, self.method = old, contract, method
        self.method_hash = sha(method_raw)
        if self.method_hash != METHOD_HASH:
            raise ValueError("pinned-method-byte-mismatch")
        self.meter = old.Meter(limit=2000)
        self.meter.exhausted = old.Exhausted
        self.shared = old.Fuel(self.meter, 2000)
        self.times = {"construction_ns": 0, "checking_ns": 0, "filtering_ns": 0}

    def charge(self, phase, fuel=None):
        self.meter.phase = phase
        (fuel or self.shared).charge()

    def q(self, text, fuel):
        self.charge("candidate_validation", fuel)
        if type(text) is not str:
            raise ValueError("candidate-prediction-not-string")
        q = self.old.rational(text)
        if str(q) != text or q.denominator & (q.denominator - 1):
            raise ValueError("prediction-not-canonical-dyadic")
        return q

    def validate_subject(self, s, fuel):
        if (type(s) is not dict or set(s) != SUBJECT_KEYS or
                s["schema"] != "adva.knowledge-subject.research" or
                type(s["version"]) is not int or s["version"] != 0 or
                type(s["name"]) is not str or type(s["requested_action"]) is not str):
            raise ValueError("unsupported-subject-schema")
        if any(type(s[key]) is not int or not 0 <= s[key] <= 500
               for key in ("remaining_fuel", "spent_fuel")):
            raise ValueError("subject-fuel-boundary")
        history = s["history"]
        if type(history) is not list or len(history) > 18:
            raise ValueError("history-boundary")
        previous = None
        for index, event in enumerate(history):
            self.charge("history_validation", fuel)
            if type(event) is not dict or set(event) != EVENT_KEYS or event["index"] != index:
                raise ValueError("history-schema")
            if any(type(event[key]) is not int or event[key] < 0 for key in
                   ("remaining_before", "remaining_after", "spent_before", "spent_after")):
                raise ValueError("history-fuel-types")
            if (event["remaining_after"] > event["remaining_before"] or
                    event["remaining_before"] - event["remaining_after"] !=
                    event["spent_after"] - event["spent_before"]):
                raise ValueError("history-fuel-reset")
            if previous and any(event[a] != previous[b] for a, b in
                                (("before", "after"), ("remaining_before", "remaining_after"),
                                 ("spent_before", "spent_after"))):
                raise ValueError("history-chain-gap")
            if (event["scope_sha256"] != self.old.digest(self.old.scope_of(s["question"])) or
                    event["method_sha256"] != self.method_hash):
                raise ValueError("history-scope-change")
            previous = event
        if previous:
            if any(s[a] != previous[b] for a, b in (("active_candidate_ids", "after"),
                   ("remaining_fuel", "remaining_after"), ("spent_fuel", "spent_after"))):
                raise ValueError("history-state-mismatch")
        elif s["spent_fuel"] != 0:
            raise ValueError("spent-fuel-without-history")

    def gate(self, subject, method, obj):
        started = time.perf_counter_ns()
        present = [role for role, value in zip(("subject", "method", "object"),
                                              (subject, method, obj)) if value is not None]
        s = copy.deepcopy(subject)
        before = copy.deepcopy(s.get("active_candidate_ids")) if type(s) is dict else None
        if type(before) is not list:
            before = None
        initial = s.get("remaining_fuel", 0) if type(s) is dict else 0
        fuel = TaskFuel(self.shared, initial if type(initial) is int and initial >= 0 else 0)
        valid_subject, check, survivors, growth = False, None, before, None

        def finish(status, reason):
            self.times["checking_ns"] += time.perf_counter_ns() - started
            spent = initial - fuel.remaining if type(initial) is int else 0
            event = None
            if valid_subject:
                event = {"index": len(s["history"]), "scope_sha256": self.old.digest(
                    self.old.scope_of(s["question"])), "method_sha256": self.method_hash,
                    "before": before, "after": survivors if status == "TaskBoundarySatisfied" else before,
                    "status": status, "remaining_before": initial, "remaining_after": fuel.remaining,
                    "spent_before": s["spent_fuel"], "spent_after": s["spent_fuel"] + spent}
                s["history"].append(event)
                s["active_candidate_ids"] = event["after"]
                s["remaining_fuel"], s["spent_fuel"] = fuel.remaining, event["spent_after"]
            return {"result": {"status": status, "reason": reason,
                    "knowledge": growth if status == "TaskBoundarySatisfied" else "NoUpdate",
                    "before": before, "after": survivors if status == "TaskBoundarySatisfied" else before,
                    "next_proposal_before": before[0] if before else None,
                    "next_proposal_after": (survivors[0] if survivors else None) if
                        status == "TaskBoundarySatisfied" else (before[0] if before else None),
                    "free_candidate": "external-learn-checkpoint" if status == "TaskBoundarySatisfied" else None,
                    "native_free": "Unimplemented"}, "history": s.get("history", []) if type(s) is dict else [],
                    "evidence": {"roles_present": present, "point_check": check,
                        "candidate_filter_crosscheck": status in ("TaskBoundarySatisfied", "ModelGap"),
                        "knowledge_is_scope_local": True},
                    "resource": {"local_spent": spent, "local_remaining": fuel.remaining,
                        "global_spent": self.meter.used, "global_remaining": self.shared.remaining},
                    "next_subject": s, "event": event}

        try:
            if len(present) != 3:
                return finish("Blocked", "missing-role")
            self.validate_subject(s, fuel)
            valid_subject = True
            self.charge("gate_validation", fuel)
            if (type(method) is not dict or self.old.encoded(method) != self.old.encoded(self.method) or
                    method.get("obligations") != self.contract["required_obligations"] or
                    method.get("checker_sha256") != CHECKER_HASH or
                    s["method_sha256"] != self.method_hash):
                return finish("Blocked", "unsupported-or-unbound-method")
            if (type(obj) is not dict or set(obj) != OBJECT_KEYS or
                    obj["schema"] != "adva.knowledge-object.research" or
                    type(obj["version"]) is not int or obj["version"] != 0 or
                    type(obj["name"]) is not str or type(obj["source"]) is not dict or
                    type(obj["receipt"]) is not dict):
                return finish("Blocked", "unsupported-object-schema")
            if (type(s["question"]) is not dict or type(obj["question"]) is not dict or
                    s["question"].get("observer") != "exact-rational-v0" or
                    self.old.encoded(self.old.scope_of(s["question"])) !=
                    self.old.encoded(self.old.scope_of(obj["question"]))):
                return finish("Blocked", "question-object-scope-mismatch")
            universe, coverage, active = (s[key] for key in
                ("candidate_universe", "candidate_coverage", "active_candidate_ids"))
            if (type(universe) is not list or len(universe) != 2 or
                    any(type(c) is not dict or set(c) != {"id", "prediction"} or
                        type(c["id"]) is not str for c in universe)):
                return finish("Blocked", "candidate-universe-schema")
            ids = [c["id"] for c in universe]
            if (ids != method["candidate_ids"] or type(coverage) is not list or
                    coverage != ids or type(active) is not list or not active or
                    any(type(i) is not str for i in active) or len(set(active)) != len(active) or
                    not set(active) <= set(ids)):
                return finish("Blocked", "incomplete-declared-candidate-coverage")
            if s["requested_action"] != method["allowed_action"]:
                return finish("Blocked", "requested-capability-unimplemented")
            predictions = {c["id"]: self.q(c["prediction"], fuel) for c in universe}
            self.meter.phase = "receipt_check"
            check = self.old.check(s["question"], obj["receipt"], fuel)
            if check["status"] != "Accepted":
                return finish("Unknown" if check["status"] == "Unknown" else "Blocked", check["reason"])
            for step in obj["receipt"]["ordered_trace"]:
                self.charge("nonzero_guard", fuel)
                if self.old.rational(step["value"]["rational"]) == 0:
                    return finish("Blocked", "declared-nonzero-trace-guard")
            filter_started = time.perf_counter_ns()
            actual = self.old.rational(check["recomputed_values"][0]["rational"])
            survivors, separate = [], []
            for candidate in active:
                self.charge("filtering", fuel)
                prediction = predictions[candidate]
                if prediction == actual:
                    survivors.append(candidate)
                self.charge("integer_filter_crosscheck", fuel)
                if prediction.numerator * actual.denominator == actual.numerator * prediction.denominator:
                    separate.append(candidate)
            self.times["filtering_ns"] += time.perf_counter_ns() - filter_started
            if survivors != separate:
                return finish("Blocked", "filter-crosscheck-failed")
            if not survivors:
                return finish("ModelGap", "declared-hypotheses-miss-verified-observation")
            growth = "NewConstraint" if survivors != before else "NoNewConstraint"
            return finish("TaskBoundarySatisfied", "all-declared-obligations-checked")
        except self.old.Exhausted as exc:
            return finish("Unknown", str(exc))
        except (ValueError, TypeError, KeyError, IndexError, ZeroDivisionError, OverflowError) as exc:
            return finish("Blocked", str(exc))


def execute(root, contract, roles, raws):
    started = time.perf_counter_ns()
    old = checked_module(root)
    subject, method, obj = roles
    runner = Runner(old, contract, method, raws[1])
    if (method.get("schema") != "adva.knowledge-method.research" or
            type(method.get("version")) is not int or method["version"] != 0 or
            method.get("algorithm") != "exact-value-filter-v0" or
            method.get("candidate_ids") != ["unit", "dyadic-product"] or
            type(method.get("max_candidates")) is not int or method["max_candidates"] != 2 or
            method.get("require_nonzero_trace") is not True or
            method.get("allowed_action") != "external-learn-checkpoint" or
            method.get("obligations") != contract["required_obligations"]):
        raise ValueError("unsupported-method-profile")
    pool = {"subject-base": subject, "method": method, "object-base": obj}
    cases = []

    def trial(name, refs, expected):
        runner.charge("presence_baseline")
        values = [pool[ref] if ref else None for ref in refs]
        outcome = runner.gate(*values)
        next_subject = outcome.pop("next_subject")
        outcome.pop("event")
        cases.append({"id": name, "input_refs": refs, "expected_status": expected,
            "presence_only_admits": all(refs), "outcome": outcome,
            "expectation_met": outcome["result"]["status"] == expected})
        return next_subject

    pool["subject-updated"] = trial("main", ["subject-base", "method", "object-base"], "TaskBoundarySatisfied")
    pool["subject-repeated"] = trial("repeat", ["subject-updated", "method", "object-base"], "TaskBoundarySatisfied")
    build_start = time.perf_counter_ns()
    runner.charge("construction")
    fresh_s, fresh_o = copy.deepcopy(subject), copy.deepcopy(obj)
    runner.charge("construction")
    # Candidate supplied from the frozen formula BEFORE any receipt is generated.
    fresh_s["candidate_universe"][1]["prediction"] = str(old.rational((1 << 60) - 1) / (1 << 60))
    fresh_q = old.task_for({"id": "product-k30", "k": 30}, "exact-rational-v0")
    fresh_s["name"], fresh_s["question"] = "fresh-k30", fresh_q
    fresh_o["question"] = copy.deepcopy(fresh_q)
    fresh_o["receipt"] = old.produce(fresh_q, runner.shared)
    fresh_o["source"] = {"kind": "fresh-recursive-producer", "checker_sha256": CHECKER_HASH}
    pool["subject-fresh"], pool["object-fresh"] = fresh_s, fresh_o
    runner.times["construction_ns"] += time.perf_counter_ns() - build_start
    reuse_start = time.perf_counter_ns()
    trial("fresh-k30", ["subject-fresh", "method", "object-fresh"], "TaskBoundarySatisfied")
    runner.times["fresh_reuse_checking_ns"] = time.perf_counter_ns() - reuse_start
    for mask in range(7):
        refs = [ref if mask & (1 << i) else None for i, ref in
                enumerate(("subject-base", "method", "object-base"))]
        trial("missing-roles-" + str(mask), refs, "Blocked")
    for name, expected in (("stale-scope", "Blocked"), ("forged-receipt", "Blocked"),
            ("omitted-coverage", "Blocked"), ("native-free", "Blocked"), ("zero-fuel", "Unknown"),
            ("zero-guard", "Blocked"), ("empty-survivor", "ModelGap"), ("rename-only", "TaskBoundarySatisfied")):
        construction_start = time.perf_counter_ns()
        runner.charge("construction")
        s = copy.deepcopy(pool["subject-repeated"] if name == "rename-only" else subject)
        o = obj
        if name == "stale-scope":
            s["question"]["environment"]["x"] = "1"
        elif name == "forged-receipt":
            o = copy.deepcopy(obj)
            o["receipt"]["verdict"] = "Equal"
        elif name == "omitted-coverage":
            s["candidate_coverage"] = ["unit"]
        elif name == "native-free":
            s["requested_action"] = "native-free"
        elif name == "zero-fuel":
            s["remaining_fuel"] = 0
        elif name == "zero-guard":
            s["question"]["environment"]["x"] = "0"
            s["candidate_universe"][1]["prediction"] = "0"
            o = copy.deepcopy(obj)
            o["question"] = copy.deepcopy(s["question"])
            o["receipt"] = old.produce(s["question"], runner.shared)
            o["source"] = {"kind": "fresh-zero-control", "checker_sha256": CHECKER_HASH}
        elif name == "empty-survivor":
            s["candidate_universe"][1]["prediction"] = "2"
        elif name == "rename-only":
            s["name"], s["question"]["name"] = "renamed-subject", "renamed-display-question"
        skey, okey = "subject-" + name, "object-base"
        pool[skey] = s
        if o is not obj:
            okey = "object-" + name
            pool[okey] = o
        runner.times["construction_ns"] += time.perf_counter_ns() - construction_start
        trial(name, [skey, "method", okey], expected)
    by_id = {c["id"]: c for c in cases}
    result = lambda name: by_id[name]["outcome"]["result"]
    acceptance = {"exactly_18_trials": len(cases) == 18,
        "all_expected_outcomes": all(c["expectation_met"] for c in cases),
        "main_strict_update": result("main")["before"] == ["unit", "dyadic-product"] and
            result("main")["after"] == ["dyadic-product"] and result("main")["knowledge"] == "NewConstraint",
        "repeat_no_new_constraint": result("repeat")["knowledge"] == "NoNewConstraint",
        "fresh_correct_candidate_retained": result("fresh-k30")["after"] == ["dyadic-product"],
        "refusals_keep_active_candidates": all(c["outcome"]["result"]["before"] ==
            c["outcome"]["result"]["after"] for c in cases if c["expected_status"] != "TaskBoundarySatisfied"),
        "rename_no_new_constraint": result("rename-only")["knowledge"] == "NoNewConstraint",
        "no_repeat_or_rename_fuel_reset": all(c["outcome"]["resource"]["local_remaining"] <
            pool[c["input_refs"][0]]["remaining_fuel"] for c in (by_id["repeat"], by_id["rename-only"]))}
    report = {"schema": "adva.knowledge-boundary-report.research", "version": 0,
        "contract_sha256": CONTRACT_HASH, "checker_sha256": CHECKER_HASH,
        "runner_sha256": sha(read(Path(__file__))), "input_sha256": [sha(raw) for raw in raws],
        "status": "Completed" if all(acceptance.values()) else "Incomplete",
        "role_pool": pool, "cases": cases, "acceptance": acceptance,
        "comparison": {"same_fixed_cases": 18,
            "presence_only_admissions": sum(c["presence_only_admits"] for c in cases),
            "complete_gate_admissions": sum(c["outcome"]["result"]["status"] == "TaskBoundarySatisfied" for c in cases),
            "unsupported_presence_only_admissions": sum(c["presence_only_admits"] and
                c["outcome"]["result"]["status"] != "TaskBoundarySatisfied" for c in cases),
            "meaning": "Unsupported permission, not necessarily a false arithmetic proposition; no speedup claim"},
        "capabilities": {"external_python": "Executed", "native_adva_on_path": shutil.which("adva"),
            "native_free": "Unimplemented", "native_calls": 0},
        "boundary": "External typed subject/method/object positions; no intrinsic K/t/X assignment, native triadic certificate, A0/M1, or universal knowledge theorem"}
    serialize_start = time.perf_counter_ns()
    runner.charge("serialization")
    payload = old.encoded(report)
    if len(payload) > MAX_BYTES:
        raise ValueError("report-byte-boundary")
    runner.times["payload_serialization_ns"] = time.perf_counter_ns() - serialize_start
    replay_start = time.perf_counter_ns()
    runner.charge("serialized_replay")
    restored = parse(payload)
    replay_checks = []
    for name in ("main", "forged-receipt"):
        original = next(c for c in restored["cases"] if c["id"] == name)
        replayed = runner.gate(*(restored["role_pool"][ref] for ref in original["input_refs"]))
        replay_checks.append({"id": name, "same_result_and_history":
            old.encoded(replayed["result"]) == old.encoded(original["outcome"]["result"]) and
            old.encoded(replayed["history"]) == old.encoded(original["outcome"]["history"]),
            "charged_units": replayed["resource"]["local_spent"]})
    runner.times["serialized_replay_ns"] = time.perf_counter_ns() - replay_start
    report["serialized_replay"] = {"payload_sha256": sha(payload), "cases": replay_checks,
        "coverage": "Reconstruct the strict update and forged-receipt refusal from serialized roles; compare result/history; all rechecking charged to the same global budget"}
    if not all(r["same_result_and_history"] for r in replay_checks):
        report["status"] = "Incomplete"
    runner.times["elapsed_ns_before_final_encode_and_save"] = time.perf_counter_ns() - started
    report["costs"] = {"charged_units": runner.meter.used, "remaining_global_fuel": runner.shared.remaining,
        "by_phase": runner.meter.by_phase, "timings": runner.times,
        "python_tracemalloc_peak_bytes": tracemalloc.get_traced_memory()[1],
        "process_peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "units": "One unit per named admitted check, AST visit, candidate comparison, guard, history entry, construction/control batch or serialization/replay batch; not instruction counts",
        "accounting": "All branches share the global invocation budget; branch-local fuel is a declared history resource, not a global anti-replay service. Checking includes nested filtering time. Final encode/save, authoring and network costs excluded, not zero."}
    return report, old


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("contract", "subject", "method", "object", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_BYTES,) * 2)
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("wall-budget-exhausted")))
    signal.alarm(5)
    tracemalloc.start()
    if args.output.exists():
        parser.exit(2, "output exists; refusing overwrite\n")
    try:
        contract_raw = read(args.contract)
        if sha(contract_raw) != CONTRACT_HASH:
            raise ValueError("frozen-contract-byte-mismatch")
        raws = [read(path) for path in (args.subject, args.method, args.object)]
        report, old = execute(Path(__file__).resolve().parents[2], parse(contract_raw),
                              [parse(raw) for raw in raws], raws)
        output = old.encoded(report)
        if len(output) > MAX_BYTES:
            raise ValueError("final-report-byte-boundary")
    except Exception as exc:
        output = (json.dumps({"schema": "adva.knowledge-boundary-report.research", "version": 0,
            "status": "Unknown", "reason": str(exc), "native_calls": 0,
            "costs": "Missing because execution could not finish report construction"}) + "\n").encode()
        report = {"status": "Unknown"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as handle:
        handle.write(output)
    signal.alarm(0)
    print(json.dumps({"status": report["status"], "output": str(args.output)}))
    return 0 if report["status"] == "Completed" else 1


if __name__ == "__main__":
    sys.exit(main())
