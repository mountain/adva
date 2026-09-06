#!/usr/bin/env python3
"""Bounded external judgment distinction, never a native certificate producer.

One invocation constructs the frozen instances, independently checks receipts,
tests scope refusal, replays a serialized report, and saves without overwrite.
Recursive production and iterative postfix checking share admission, encodings,
and standard-library arithmetic; this is traversal independence, not a second
arithmetic implementation or a formal proof of the checker.
"""

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import resource
import signal
import sys
import time
import tracemalloc
from fractions import Fraction


VERSION = 0
CONTRACT_SHA256 = "517feb7c78e5d36121fde30f8a69f0cac5e51a613dc1a827d800b015b8c446a1"
MAX_BYTES = 262144
MAX_UNITS = 2000
MAX_BITS = 128
EXPECTED_OBJECTS = [
    {"id": "product-k27", "kind": "existing-witness-reinterpretation", "k": 27},
    {"id": "product-k29", "kind": "fresh-instance-reuse", "k": 29},
    {"id": "nonunit-identity", "kind": "nonunit-control", "value": 2},
]
EXPECTED_BUDGET = {
    "routes": 1, "candidate_search_nodes": 0, "max_instances": 3,
    "max_ast_depth": 8, "max_ast_nodes_per_expression": 15,
    "max_fraction_bits": 128, "max_charged_units_per_invocation": 2000,
    "max_invocations_including_one_implementation_repair": 2,
    "max_total_charged_units": 4000, "wall_seconds_per_invocation": 5,
    "cpu_seconds_per_invocation": 5, "address_space_mib": 256,
    "max_input_bytes": MAX_BYTES, "max_report_bytes": MAX_BYTES,
    "native_calls": 0,
}
KINDS = ("binary64-point-equality", "rational-point-equality",
         "native-formation-A0", "native-transport-M1")
NATIVE_QUESTION_META = {
    "native-formation-A0": ("native-relative-formation-boundary", "this-proposed-native-template"),
    "native-transport-M1": ("native-exact-polynomial-transport", "this-proposed-native-transition-with-guards"),
}


class Exhausted(Exception):
    pass


class Meter:
    def __init__(self, limit=MAX_UNITS):
        self.limit = limit
        self.used = 0
        self.by_phase = {}
        self.phase = "construction"

    def charge(self, units=1):
        if self.used + units > self.limit:
            raise Exhausted("charged-work limit reached")
        self.used += units
        self.by_phase[self.phase] = self.by_phase.get(self.phase, 0) + units


class Fuel:
    def __init__(self, meter, remaining=MAX_UNITS):
        self.meter = meter
        self.remaining = remaining

    def charge(self):
        if self.remaining <= 0:
            raise Exhausted("local verification fuel exhausted")
        self.meter.charge()
        self.remaining -= 1


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def rational(value):
    if isinstance(value, str):
        # Bound integer parsing before Fraction can allocate or normalize.
        parts = value.split("/")
        if len(parts) > 2 or any(len(part.lstrip("-+")) > 39 or
                not part.lstrip("-+").isascii() or not part.lstrip("-+").isdigit()
                for part in parts):
            raise ValueError("rational source is not a bounded integer or integer ratio")
    q = Fraction(value)
    if max(abs(q.numerator).bit_length(), q.denominator.bit_length()) > MAX_BITS:
        raise ValueError("fraction component exceeds frozen bit bound")
    return q


def packed(value):
    if isinstance(value, Fraction):
        return {"rational": str(value)}
    if not math.isfinite(value):
        raise ValueError("non-finite binary64 observation")
    return {"hex": value.hex(), "exact_binary64": str(rational(value))}


def read_bytes(path):
    with path.open("rb") as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("input exceeds frozen byte bound")
    return raw


def scope_of(task):
    """The one explicitly presentation-only field is outside the evidence scope."""
    return {key: value for key, value in task.items() if key != "name"}


def admitted(task, fuel):
    fuel.charge()
    scope = scope_of(task)
    if set(scope) != {"schema", "version", "ordered_pair", "environment", "domain",
                     "observer", "relation", "quantifier"}:
        raise ValueError("unrecognized task fields")
    if (scope["schema"] != "adva.judgment-question.research" or
            type(scope["version"]) is not int or scope["version"] != VERSION):
        raise ValueError("unsupported task version")
    if scope["domain"] != "Q" or scope["quantifier"] != "at-declared-input":
        raise ValueError("unsupported arithmetic domain or quantifier")
    if scope["relation"] != "equal" or scope["observer"] not in (
            "python-binary64-v0", "exact-rational-v0"):
        raise ValueError("no executable external semantics for this relation")
    if not isinstance(scope["environment"], dict) or len(scope["environment"]) > 2:
        raise ValueError("environment boundary")
    for name, value in scope["environment"].items():
        fuel.charge()
        if name not in ("x", "y") or not isinstance(value, str):
            raise ValueError("input type boundary")
        rational(value)
    if len(scope["ordered_pair"]) != 2:
        raise ValueError("exactly two ordered expressions required")
    for ast in scope["ordered_pair"]:
        pending = [(ast, 1)]
        count = 0
        while pending:
            node, depth = pending.pop()
            fuel.charge()
            count += 1
            if depth > 8 or count > 15 or not isinstance(node, list) or not node:
                raise ValueError("AST boundary")
            op = node[0]
            if op == "input" and len(node) == 2:
                if node[1] not in scope["environment"]:
                    raise ValueError("unbound input")
            elif op == "const" and len(node) == 2:
                if not isinstance(node[1], str):
                    raise ValueError("constant must preserve exact source spelling")
                rational(node[1])
            elif op in ("add", "mul") and len(node) == 3:
                pending.extend(((node[2], depth + 1), (node[1], depth + 1)))
            else:
                raise ValueError("unsupported AST form")
    return scope


def produce(task, fuel):
    scope = admitted(task, fuel)
    use_float = scope["observer"] == "python-binary64-v0"
    trace = []

    def walk(node, path):
        fuel.charge()
        op = node[0]
        operands = []
        if op == "input":
            q = rational(scope["environment"][node[1]])
            value = float(q) if use_float else q
        elif op == "const":
            q = rational(node[1])
            value = float(q) if use_float else q
        else:
            left = walk(node[1], path + ".0")
            right = walk(node[2], path + ".1")
            operands = [packed(left), packed(right)]
            value = left + right if op == "add" else left * right
            if not use_float:
                value = rational(value)
        trace.append({"path": path, "operation": op, "operands": operands,
                      "value": packed(value)})
        return value

    left, right = (walk(ast, str(index)) for index, ast in enumerate(scope["ordered_pair"]))
    delta = rational(left) - rational(right)
    rational(delta)
    return {"schema": "adva.point-judgment-receipt.research", "version": VERSION,
            "scope": scope, "scope_sha256": digest(scope),
            "construction_sha256": digest({"pair": scope["ordered_pair"],
                                            "environment": scope["environment"]}),
            "values": [packed(left), packed(right)], "residual": str(delta),
            "verdict": "Equal" if left == right else "Different",
            "ordered_trace": trace, "ordered_trace_sha256": digest(trace),
            "authority": "external point observation only"}


def independently_recompute(task, fuel):
    """Iterative postorder VM; never calls the recursive receipt producer."""
    scope = admitted(task, fuel)
    use_float = scope["observer"] == "python-binary64-v0"
    trace = []
    results = []
    for index, expression in enumerate(scope["ordered_pair"]):
        stack = [(expression, str(index), False)]
        values = []
        while stack:
            node, path, ready = stack.pop()
            op = node[0]
            if op in ("add", "mul") and not ready:
                stack.extend(((node, path, True), (node[2], path + ".1", False),
                              (node[1], path + ".0", False)))
                continue
            fuel.charge()
            operands = []
            if op in ("input", "const"):
                source = scope["environment"][node[1]] if op == "input" else node[1]
                v = rational(source)
                if use_float:
                    v = float(v)
            else:
                b = values.pop()
                a = values.pop()
                operands = [packed(a), packed(b)]
                v = a * b if op == "mul" else a + b
                if not use_float:
                    v = rational(v)
            values.append(v)
            trace.append({"path": path, "operation": op, "operands": operands,
                          "value": packed(v)})
        if len(values) != 1:
            raise ValueError("checker stack invariant failed")
        results.append(values[0])
    delta = rational(rational(results[0]) - rational(results[1]))
    return {"schema": "adva.point-judgment-receipt.research", "version": VERSION,
            "scope": scope, "scope_sha256": digest(scope),
            "construction_sha256": digest({"pair": scope["ordered_pair"],
                                            "environment": scope["environment"]}),
            "values": [packed(v) for v in results], "residual": str(delta),
            "verdict": "Equal" if results[0] == results[1] else "Different",
            "ordered_trace": trace, "ordered_trace_sha256": digest(trace),
            "authority": "external point observation only"}


def check(task, receipt, fuel):
    try:
        fuel.charge()
        # Canonical JSON equality preserves boolean/integer/float distinctions
        # that ordinary Python container equality would silently erase.
        if encoded(receipt.get("scope")) != encoded(scope_of(task)):
            return {"status": "Rejected", "reason": "question-scope-mismatch"}
        expected = independently_recompute(task, fuel)
        if encoded(receipt) != encoded(expected):
            return {"status": "Rejected", "reason": "independent-recomputation-mismatch"}
        return {"status": "Accepted", "reason": "point-receipt-independently-replayed",
                "recomputed_verdict": expected["verdict"],
                "recomputed_residual": expected["residual"],
                "recomputed_values": expected["values"]}
    except Exhausted as exc:
        return {"status": "Unknown", "reason": str(exc)}
    except (ValueError, TypeError, KeyError, IndexError) as exc:
        return {"status": "Rejected", "reason": str(exc)}


def readings(task, receipt=None, missing=None):
    scope = scope_of(task)
    return {
        "K": {"ordered_pair": scope["ordered_pair"], "domain": scope["domain"],
              "relation": scope["relation"], "obligation": missing or "point equality"},
        "t": {"trace_sha256": receipt["ordered_trace_sha256"] if receipt else None,
              "ordered_history_required": True, "missing": missing},
        "X": {"observer": scope["observer"], "quantifier": scope["quantifier"],
              "residual": receipt["residual"] if receipt else None,
              "scope_sha256": digest(scope)},
        "level": "three research readings, not native wire domains or transition"}


def proposition_status(verdict):
    return "ConfirmedAtDeclaredInput" if verdict == "Equal" else "RefutedAtDeclaredInput"


def task_for(obj, observer):
    if "k" in obj:
        eps = rational(Fraction(1, 1 << obj["k"]))
        pair = [["mul", ["input", "x"], ["input", "y"]], ["const", "1"]]
        env = {"x": str(1 + eps), "y": str(1 - eps)}
    else:
        pair = [["const", "2"], ["const", "2"]]
        env = {}
    return {"name": obj["id"], "schema": "adva.judgment-question.research",
            "version": VERSION, "ordered_pair": pair, "environment": env,
            "domain": "Q", "observer": observer, "relation": "equal",
            "quantifier": "at-declared-input"}


def native_attachment(contract, root, k27_task, meter):
    spec = contract["native_evidence"]
    raw = read_bytes(root / spec["path"])
    program_raw = read_bytes(root / spec["program_path"])
    meter.charge(2)
    if hashlib.sha256(raw).hexdigest() != spec["sha256"]:
        raise ValueError("retained native report hash mismatch")
    if hashlib.sha256(program_raw).hexdigest() != spec["program_sha256"]:
        raise ValueError("retained native program hash mismatch")
    report, program = json.loads(raw), json.loads(program_raw)
    if (report["program_json"].encode() != program_raw or
            encoded(report["program"]) != encoded(program)):
        raise ValueError("native report/program binding mismatch")
    expected_source = "(module representation (export main) (def main (fn ((x Real) (y Real)) Real (mul (use x) (use y)))))"
    if (program["schema"], program["version"], program["source"], program["module"],
            program["entry"], program["fuel"]) != (
            "adva.run.program.research", 0, expected_source, "representation", "main", 16):
        raise ValueError("historical native program differs from the declared expression")
    if set(program["inputs"]) != {"x", "y"}:
        raise ValueError("native input scope mismatch")
    for name, exact in k27_task["environment"].items():
        meter.charge()
        if rational(program["inputs"][name]) != rational(exact):
            raise ValueError("native input is not the exact declared k27 input")
    if (report["schema"], report["version"], report["state"],
            report["evaluation"]["values"]) != ("adva.run.report.research", 0, "Completed", [1.0]):
        raise ValueError("retained native scalar observation does not match")
    return {"status": "HistoricalScalarObservationAttached", "report_path": spec["path"],
            "report_sha256": spec["sha256"], "program_sha256": spec["program_sha256"],
            "reported_scalar_hex": report["evaluation"]["values"][0].hex(),
            "reported_inputs": {k: packed(v) for k, v in program["inputs"].items()},
            "embedded_program_exact_bytes_checked": True, "new_native_invocations": 0,
            "native_history_source_sha256": spec["sha256"],
            "authority": "historical scalar report only; no independently checked native A0/M1",
            "hash_boundary": "SHA256 integrity binding is not authentication or proof authority"}


def make_controls(cases):
    fp = cases[0]["judgments"][0]
    exact = cases[0]["judgments"][1]
    controls = []

    def append(name, target, receipt, want="Rejected", local=MAX_UNITS):
        controls.append({"name": name, "target": copy.deepcopy(target),
                         "receipt": copy.deepcopy(receipt), "expected_gate": want,
                         "local_fuel": local})

    append("wrong-observer", exact["question"], fp["receipt"])
    for name, field, value in (("wrong-domain", "domain", "R"),
                               ("all-input-quantifier", "quantifier", "for-all-inputs")):
        target = copy.deepcopy(fp["question"])
        target[field] = value
        append(name, target, fp["receipt"])
    target = copy.deepcopy(fp["question"])
    target["ordered_pair"][0][1:3] = reversed(target["ordered_pair"][0][1:3])
    append("changed-operand-order", target, fp["receipt"])
    target = copy.deepcopy(fp["question"])
    target["environment"]["x"] = "1"
    append("changed-input-environment", target, fp["receipt"])
    forged = copy.deepcopy(exact["receipt"])
    forged["verdict"] = "Equal"
    append("forged-verdict", exact["question"], forged)
    forged = copy.deepcopy(exact["receipt"])
    forged["residual"] = "0"
    append("forged-residual", exact["question"], forged)
    for native_judgment in cases[0]["judgments"][2:]:
        append("scalar-promotion-to-" + native_judgment["kind"],
               native_judgment["question"], fp["receipt"])
    append("stale-k27-receipt-for-k29", cases[1]["judgments"][0]["question"], fp["receipt"])
    target = copy.deepcopy(exact["question"])
    target["name"] = "presentation-only-renaming"
    append("rename-only", target, exact["receipt"], "Accepted")
    append("zero-fuel", exact["question"], exact["receipt"], "Unknown", 0)
    return controls


def execute(contract, contract_raw, root):
    started = time.perf_counter_ns()
    meter = Meter()
    timings = {}
    if (contract.get("schema"), contract.get("version"), contract.get("objects"),
            contract.get("budget"), contract.get("judgment_kinds")) != (
            "adva.distinguish-run-contract.research", VERSION, EXPECTED_OBJECTS,
            EXPECTED_BUDGET, list(KINDS)):
        raise ValueError("contract differs from this frozen runner's supported task")
    cases = []
    checks = []
    build_start = time.perf_counter_ns()
    for obj in contract["objects"]:
        reuse_start = time.perf_counter_ns()
        case = {"id": obj["id"], "role": obj["kind"], "judgments": []}
        for kind, observer in zip(KINDS[:2], ("python-binary64-v0", "exact-rational-v0")):
            task = task_for(obj, observer)
            receipt = produce(task, Fuel(meter))
            case["judgments"].append({"kind": kind, "question": task, "receipt": receipt,
                                      "question_status": proposition_status(receipt["verdict"]),
                                      "three_readings": readings(task, receipt)})
        for kind, missing in ((KINDS[2], "No bound native formation template and checked A0 witness"),
                              (KINDS[3], "No bound native transition and checked M1 witness")):
            task = task_for(obj, "native-witness-checker-required")
            task["relation"] = kind
            # These descriptive research domains are not newly declared native types.
            # The external expression pair proposes a carrier; it does not supply one.
            task["domain"], task["quantifier"] = NATIVE_QUESTION_META[kind]
            case["judgments"].append({"kind": kind, "question": task, "status": "Unknown",
                                      "reason": missing, "three_readings": readings(task, missing=missing)})
        exact_receipt = case["judgments"][1]["receipt"]
        residual = rational(exact_receipt["residual"])
        values = [rational(v["rational"]) for v in exact_receipt["values"]]
        case["distinguish"] = {
            "status": "Separated" if residual else "NotSeparatedAtDeclaredInput",
            "observer": "exact-rational-v0", "separating_residual": str(residual),
            "binary64_status": "NotSeparatedAtDeclaredInput" if
                case["judgments"][0]["receipt"]["verdict"] == "Equal" else "Separated",
            "external_value_quotient": str(rational(values[0] / values[1])) if values[1] else None,
            "quotient_domain_condition": "right value nonzero; this quotient is not native M1",
            "proposed_action_exact_preservation": "RefutedAtDeclaredInput" if residual else
                "PointwiseConfirmed; native action authorization Unknown",
            "residual_obligations": ["No full-domain equality", "No native formation/transport witness"]}
        if obj["id"] == "product-k29":
            timings["fresh_reuse_construction_ns"] = time.perf_counter_ns() - reuse_start
        cases.append(case)
    historical = native_attachment(contract, root, cases[0]["judgments"][0]["question"], meter)
    cases[0]["historical_native_observation"] = historical
    timings["construction_ns"] = time.perf_counter_ns() - build_start
    meter.phase = "validation"
    validation_start = time.perf_counter_ns()
    for case in cases:
        reuse_start = time.perf_counter_ns()
        for judgment in case["judgments"][:2]:
            result = check(judgment["question"], judgment["receipt"], Fuel(meter))
            judgment["independent_check"] = result
            checks.append(result["status"] == "Accepted" and judgment["question_status"] ==
                          proposition_status(result["recomputed_verdict"]))
        if case["id"] == "product-k29":
            timings["fresh_reuse_validation_ns"] = time.perf_counter_ns() - reuse_start
    controls = make_controls(cases)
    for control in controls:
        meter.charge()
        control["naive_forwarder"] = {"accepts_receipt_without_scope_check": True,
            "forwarded_equality_boolean": control["receipt"]["verdict"] == "Equal",
            "note": "A bare answer carries no evidence applicability check"}
        result = check(control["target"], control["receipt"], Fuel(meter, control["local_fuel"]))
        control["gate"] = result
        control["expectation_met"] = result["status"] == control["expected_gate"]
        checks.append(control["expectation_met"])
    timings["validation_and_controls_ns"] = time.perf_counter_ns() - validation_start
    acceptance = {
        "products_float_equal_exact_different": all(c["judgments"][0]["receipt"]["verdict"] == "Equal"
            and c["judgments"][1]["receipt"]["verdict"] == "Different" for c in cases[:2]),
        "fresh_scope_not_copied": cases[0]["judgments"][1]["receipt"]["scope_sha256"] !=
                                  cases[1]["judgments"][1]["receipt"]["scope_sha256"],
        "nonunit_control_exact_two_with_quotient_one":
            cases[2]["judgments"][1]["receipt"]["values"] == [{"rational": "2"}] * 2
            and cases[2]["distinguish"]["external_value_quotient"] == "1",
        "native_statuses_unknown": all(j["status"] == "Unknown" for c in cases for j in c["judgments"][2:]),
        "all_independent_checks_and_controls": all(checks),
    }
    report = {"schema": "adva.judgment-distinction-report.research", "version": VERSION,
              "status": "Completed" if all(acceptance.values()) else "Incomplete",
              "contract_sha256": hashlib.sha256(contract_raw).hexdigest(),
              "runner_sha256": hashlib.sha256(read_bytes(Path(__file__))).hexdigest(),
              "source_main": contract["source_main"], "cases": cases, "controls": controls,
              "acceptance": acceptance,
              "comparison": {"same_attempts": len(controls),
                  "invalid_scope_or_forged_attempts": sum(c["expected_gate"] == "Rejected" for c in controls),
                  "naive_accepts_those_receipts": sum(c["expected_gate"] == "Rejected" for c in controls),
                  "gate_accepts_those_receipts": sum(c["expected_gate"] == "Rejected" and
                       c["gate"]["status"] == "Accepted" for c in controls),
                  "naive_work_units_per_attempt": 1,
                  "claim": "Inadmissible evidence reuse is counted, not false mathematical propositions; "
                  "no speedup or expression-power claim"},
              "word": {"name": "distinguish", "status": "Proposed composite",
                  "input": "Ordered expression pair, exact input, declared observer/relation/point scope and fuel",
                  "output": "Separating receipt, pointwise not-separated result, or Unknown",
                  "conditions": "This finite add/mul/const/input grammar over bounded rational inputs only",
                  "refusal": "Changed scope, forged receipt, unavailable native witness, or exhausted checker",
                  "expansion": "Interpret the question, observe, independently recompute, then judge in its scope",
                  "residual": "No universal grammar, general identity, social trust, or native certificate claim"},
              "budget": contract["budget"], "native_calls": 0,
              "trust_boundary": "The two evaluators use different traversals but share Python Fraction and binary64; "
              "SHA256 binds integrity, not authenticity. K/t/X are external research readings."}
    # This encode is the measured serialization of the mathematical report payload.
    serialization_start = time.perf_counter_ns()
    serialized = encoded(report)
    if len(serialized) > MAX_BYTES:
        raise ValueError("report payload exceeds byte bound")
    timings["payload_serialization_ns"] = time.perf_counter_ns() - serialization_start
    meter.phase = "serialized_replay"
    replay_start = time.perf_counter_ns()
    replay = json.loads(serialized)
    meter.charge()
    replay_ok = encoded(replay) == encoded(report)
    for case in replay["cases"]:
        recomputed = []
        for judgment in case["judgments"][:2]:
            result = check(judgment["question"], judgment["receipt"], Fuel(meter))
            recomputed.append(result)
            replay_ok = (replay_ok and result["status"] == "Accepted" and
                         judgment["question_status"] == proposition_status(result["recomputed_verdict"]))
        meter.charge()
        if all(result["status"] == "Accepted" for result in recomputed):
            residual = rational(recomputed[1]["recomputed_residual"])
            distinction = case["distinguish"]
            desired_action = "RefutedAtDeclaredInput" if residual else \
                "PointwiseConfirmed; native action authorization Unknown"
            replay_ok = (replay_ok and distinction["separating_residual"] == str(residual)
                and distinction["status"] == ("Separated" if residual else "NotSeparatedAtDeclaredInput")
                and distinction["binary64_status"] == ("NotSeparatedAtDeclaredInput" if
                    recomputed[0]["recomputed_verdict"] == "Equal" else "Separated")
                and distinction["proposed_action_exact_preservation"] == desired_action)
            left, right = (rational(v["rational"]) for v in recomputed[1]["recomputed_values"])
            replay_ok = (replay_ok and distinction["external_value_quotient"] ==
                         (str(rational(left / right)) if right else None))
        else:
            replay_ok = False
        replay_ok = replay_ok and all(j["status"] == "Unknown" and
            (j["question"]["domain"], j["question"]["quantifier"]) == NATIVE_QUESTION_META[j["kind"]]
            for j in case["judgments"][2:])
    for control in replay["controls"]:
        result = check(control["target"], control["receipt"], Fuel(meter, control["local_fuel"]))
        replay_ok = replay_ok and result == control["gate"]
    timings["serialized_independent_replay_ns"] = time.perf_counter_ns() - replay_start
    report["serialized_replay"] = {"status": "Accepted" if replay_ok else "Rejected",
        "payload_sha256": hashlib.sha256(serialized).hexdigest(),
        "coverage": "All six receipts and twelve scope/forgery/fuel controls independently recomputed once; "
        "proposition and distinction/action statuses checked against independently recomputed residuals; final cost metadata excluded"}
    if not replay_ok:
        report["status"] = "Incomplete"
    _, peak = tracemalloc.get_traced_memory()
    timings["elapsed_ns_before_final_encode_and_save"] = time.perf_counter_ns() - started
    report["actual_costs"] = {"timings": timings, "charged_units": meter.used,
        "charged_units_by_phase": meter.by_phase, "charged_unit_definition":
        "Admitted AST node, evaluation AST node, scope admission, bound environment item, control forward, "
        "replay admission or replay summary check; JSON/hash bytes bounded separately",
        "candidate_search_nodes": 0, "native_calls": 0,
        "python_tracemalloc_peak_bytes_before_final_encode_and_save": peak,
        "process_peak_rss_bytes_before_final_encode_and_save": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
        "rss_platform": "Linux ru_maxrss KiB converted to bytes, single Python process",
        "missing": ["final cost-metadata encode and persistence timing", "research, source-writing and network costs",
                    "interpreter startup and frozen contract parsing excluded from internal phase timing"],
        "fresh_reuse_timing_overlap": "Reuse times are subsets of construction/validation, not additive totals"}
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if sys.platform != "linux":
        parser.error("This frozen resource contract requires Linux")
    if args.output.exists():
        parser.error("Output exists; this run never overwrites or retries")
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))

    def deadline(_signum, _frame):
        raise Exhausted("five-second wall boundary")

    signal.signal(signal.SIGALRM, deadline)
    signal.setitimer(signal.ITIMER_REAL, 5)
    tracemalloc.start()
    try:
        raw = read_bytes(args.contract)
        if hashlib.sha256(raw).hexdigest() != CONTRACT_SHA256:
            raise ValueError("frozen contract bytes changed; no arithmetic executed")
        contract = json.loads(raw)
        report = execute(contract, raw, args.repo_root)
        raw_report = encoded(report)
        if len(raw_report) > MAX_BYTES:
            raise ValueError("final report exceeds byte bound")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("xb") as handle:
            handle.write(raw_report)
        print(json.dumps({"status": report["status"], "report": str(args.output),
                          "charged_units": report["actual_costs"]["charged_units"],
                          "bytes": len(raw_report)}))
        return 0 if report["status"] == "Completed" else 1
    except (Exhausted, ValueError, KeyError, TypeError, OSError, MemoryError) as exc:
        # An admission/resource failure stays visible and cannot be called a completed experiment.
        print(json.dumps({"status": "Unknown" if isinstance(exc, (Exhausted, MemoryError)) else "Rejected",
                          "error": str(exc), "report_saved": False}), file=sys.stderr)
        return 2
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


if __name__ == "__main__":
    raise SystemExit(main())
