"""Check two finite premises for a parametric growing-stack certificate.

The old machine supplies proposals and concrete controls.  The receiving
macro checker uses the independently compiled named representation and an
opaque stack-tail token.  It checks a structural natural-number recurrence;
it is not a general termination prover or a native Adva judgment.
"""
import argparse
import copy
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import resource
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "keraia_read_machine"))
sys.path.insert(0, str(ROOT / "keraia_cycle_mass"))

import cycles as old_cycles
import machine as M
import oracle as O
from syntax import Budget, I, R

PROFILE = M.PROFILE
COST = M.COST
SCHEMA = "adva.external.keraia-parametric-frame-recurrence.v0"
TAIL = ("opaque-ordered-stack-prefix",)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def app_code(a, b):
    return "1" + a + b


def d_term(arity):
    body = ("v", 0)
    for _ in range(arity - 1):
        body = ("a", body, ("v", 0))
    return ("l", body)


def p_term(arity):
    d = d_term(arity)
    body = d
    for _ in range(arity - 1):
        body = ("a", body, d)
    return body


def encode_term(term):
    if term[0] == "v":
        return ["v", term[1]]
    if term[0] == "l":
        return ["l", encode_term(term[1])]
    if term[0] == "a":
        return ["a", encode_term(term[1]), encode_term(term[2])]
    return ["r"]


def compile_source_named(source, budget):
    end = O.first_tree_end(source, budget)
    if end is None:
        raise ValueError("incomplete source")
    term = O.debruijn(O.compile_string(source[:end], budget), budget)
    return term, end


def named_step(control, stack, cursor, source, budget):
    """Independent pure step with an opaque prefix at stack index zero."""
    if not stack or stack[0] != TAIL:
        raise ValueError("missing opaque ordered prefix")
    if control[0] == "a":
        return control[1], stack + [control[2]], cursor, "Push"
    if control[0] == "l" and len(stack) > 1:
        argument = stack[-1]
        if argument == TAIL:
            raise ValueError("macro attempted to consume opaque prefix")
        function = O.named(control, budget)
        reduced = O.substitute_named(function[2], function[1], O.named(argument, budget), budget)
        O.size(reduced, budget)
        return O.debruijn(reduced, budget), stack[:-1], cursor, "Beta"
    if control == R and len(stack) > 1:
        raise ValueError("read is not a pure growth edge")
    raise ValueError("return or free head is not a pure growth edge")


def propose(source, arity, budget):
    compiled, end = compile_source_named(source, budget)
    d, p = d_term(arity), p_term(arity)
    if compiled != ("a", d, d):
        raise ValueError("source does not compile to declared self-application")
    # Two-step stem: push D, then beta to P.
    frame = M.Frame(compiled, (), end)
    counts = {"execution_steps": 0}
    stem = M.pure_segment(frame, 2, budget, counts)
    if stem.steps != 2 or stem.end != M.Frame(p, (), end):
        raise AssertionError("unexpected stem")
    control, stack, cursor = p, [TAIL], end
    actions = []
    frames = [{"control": encode_term(control), "stack": [list(TAIL)], "cursor": cursor}]
    for _ in range(arity):
        control, stack, cursor, action = named_step(control, stack, cursor, source, budget)
        actions.append(action)
        frames.append({"control": encode_term(control),
                       "stack": [list(TAIL) if x == TAIL else encode_term(x) for x in stack],
                       "cursor": cursor})
    delta = len(stack) - 1
    return {
        "schema": SCHEMA,
        "source": source,
        "profile": PROFILE,
        "cost_convention": COST,
        "arity": arity,
        "stem_steps": 2,
        "template_head": encode_term(p),
        "stack_atom": encode_term(d),
        "macro_actions": actions,
        "symbolic_frames": frames,
        "stack_delta": delta
    }


def decode_term(data, budget, depth=0):
    budget.tick()
    if type(data) is not list or not data:
        raise ValueError("term shape")
    if data == ["r"]:
        return R
    if len(data) == 2 and data[0] == "v" and type(data[1]) is int and 0 <= data[1] < depth:
        return ("v", data[1])
    if len(data) == 2 and data[0] == "l":
        return ("l", decode_term(data[1], budget, depth + 1))
    if len(data) == 3 and data[0] == "a":
        return ("a", decode_term(data[1], budget, depth), decode_term(data[2], budget, depth))
    raise ValueError("invalid or open term")


def decode_stack(data, budget):
    if type(data) is not list or not data or data[0] != list(TAIL):
        raise ValueError("symbolic stack must begin with the opaque prefix")
    return [TAIL] + [decode_term(x, budget) for x in data[1:]]


def check(receipt, expected_source, expected_arity, budget):
    try:
        budget.tick()
        required = {"schema", "source", "profile", "cost_convention", "arity",
                    "stem_steps", "template_head", "stack_atom", "macro_actions",
                    "symbolic_frames", "stack_delta"}
        if type(receipt) is not dict or set(receipt) != required:
            return False
        if (receipt["schema"] != SCHEMA or receipt["source"] != expected_source
                or receipt["profile"] != PROFILE or receipt["cost_convention"] != COST
                or type(receipt["arity"]) is not int or receipt["arity"] != expected_arity
                or not 3 <= expected_arity <= 16
                or type(receipt["stem_steps"]) is not int or receipt["stem_steps"] != 2
                or type(receipt["stack_delta"]) is not int or receipt["stack_delta"] <= 0):
            return False
        compiled, end = compile_source_named(expected_source, budget)
        d = d_term(expected_arity)
        p = p_term(expected_arity)
        if compiled != ("a", d, d):
            return False
        # Receiver replays the finite stem with its own named transition.
        control, stack, cursor = compiled, [TAIL], end
        for _ in range(2):
            control, stack, cursor, _ = named_step(control, stack, cursor, expected_source, budget)
        if control != p or stack != [TAIL] or cursor != end:
            return False
        if decode_term(receipt["template_head"], budget) != p or decode_term(receipt["stack_atom"], budget) != d:
            return False
        actions, frames = receipt["macro_actions"], receipt["symbolic_frames"]
        if (type(actions) is not list or len(actions) != expected_arity
                or type(frames) is not list or len(frames) != len(actions) + 1):
            return False
        control, stack, cursor = p, [TAIL], end
        for index, expected_action in enumerate(actions):
            budget.tick()
            if (type(expected_action) is not str
                    or decode_term(frames[index]["control"], budget) != control
                    or decode_stack(frames[index]["stack"], budget) != stack
                    or type(frames[index]["cursor"]) is not int
                    or frames[index]["cursor"] != cursor):
                return False
            control, stack, cursor, action = named_step(control, stack, cursor, expected_source, budget)
            if action != expected_action:
                return False
        if (decode_term(frames[-1]["control"], budget) != control
                or decode_stack(frames[-1]["stack"], budget) != stack
                or type(frames[-1]["cursor"]) is not int or frames[-1]["cursor"] != cursor):
            return False
        suffix = stack[1:]
        return (control == p and cursor == end and suffix == [d] * receipt["stack_delta"]
                and receipt["stack_delta"] == expected_arity - 2
                and all(a in ("Push", "Beta") for a in actions))
    except (ValueError, TypeError, KeyError, IndexError):
        return False


def concrete_replay(source, arity, n, budget):
    d, p = d_term(arity), p_term(arity)
    end = O.first_tree_end(source, budget)
    frame = M.Frame(p, tuple([d] * n), end)
    counts = {"execution_steps": 0}
    result = M.pure_segment(frame, arity, budget, counts)
    expected = M.Frame(p, tuple([d] * (n + arity - 2)), end)
    return result.steps == arity and result.stop == "UnknownFuel" and result.end == expected


def mutate(receipt, field, value):
    changed = copy.deepcopy(receipt)
    changed[field] = value
    return changed


def run(output):
    contract = json.loads((HERE / "contract.json").read_text())
    budget = Budget(contract["limits"])
    evidence = {"schema": "adva.external.keraia-parametric-frame-recurrence.evidence.v0",
                "status": "Running", "checks": [], "failures": [], "instances": [],
                "negative_controls": [], "timings": {}}
    assertions = 0
    def require(condition, label):
        nonlocal assertions
        budget.tick()
        assertions += 1
        if not condition:
            raise AssertionError(label)
    started = time.monotonic()
    try:
        instances = [(3, "110011000"), (4, "11001110000")]
        for arity, abstraction in instances:
            source = app_code(abstraction, abstraction)
            receipt = propose(source, arity, budget)
            require(check(receipt, source, arity, budget), f"D{arity} receiver")
            old = old_cycles.propose(source, 128, budget)
            require(old["status"] == "UnknownFuel" and old.get("head_only_repeat") is not None,
                    f"D{arity} old exact-cycle baseline")
            probes = {}
            for n in (0, 1, 2, 5):
                probes[str(n)] = concrete_replay(source, arity, n, budget)
                require(probes[str(n)], f"D{arity} concrete n={n}")
            evidence["instances"].append({
                "name": f"D{arity}-self-application",
                "source": source,
                "source_bits": len(source),
                "arity": arity,
                "macro_steps": len(receipt["macro_actions"]),
                "stack_delta": receipt["stack_delta"],
                "old_exact_cycle_result": old["status"],
                "old_head_repeat_observed": old.get("head_only_repeat") is not None,
                "concrete_probes": probes,
                "certificate": receipt,
                "certificate_sha256": digest(receipt)
            })
        evidence["checks"].append("two independently compiled parametric premises accepted; old exact-state cycle search remained UnknownFuel")
        evidence["checks"].append("concrete receiver-selected n=0,1,2,5 probes agree with each symbolic recurrence")

        base = evidence["instances"][0]["certificate"]
        source = base["source"]
        controls = [
            ("source", mutate(base, "source", source[:-1] + ("1" if source[-1] == "0" else "0")), source, 3),
            ("profile", mutate(base, "profile", "other"), source, 3),
            ("cost", mutate(base, "cost_convention", "other"), source, 3),
            ("boolean_arity", mutate(base, "arity", True), source, 3),
            ("boolean_delta", mutate(base, "stack_delta", True), source, 3),
            ("zero_delta", mutate(base, "stack_delta", 0), source, 3),
            ("wrong_delta", mutate(base, "stack_delta", 2), source, 3),
            ("wrong_head", mutate(base, "template_head", base["stack_atom"]), source, 3),
            ("wrong_atom", mutate(base, "stack_atom", base["template_head"]), source, 3),
            ("wrong_action", mutate(base, "macro_actions", ["Beta"] + base["macro_actions"][1:]), source, 3),
            ("wrong_arity_context", base, source, 4)
        ]
        bad_cursor = copy.deepcopy(base)
        bad_cursor["symbolic_frames"][1]["cursor"] -= 1
        controls.append(("changed_cursor", bad_cursor, source, 3))
        bad_tail = copy.deepcopy(base)
        bad_tail["symbolic_frames"][1]["stack"] = bad_tail["symbolic_frames"][1]["stack"][1:] + [list(TAIL)]
        controls.append(("tail_moved", bad_tail, source, 3))
        bad_frame = copy.deepcopy(base)
        bad_frame["symbolic_frames"] = bad_frame["symbolic_frames"][:-1]
        controls.append(("missing_frame", bad_frame, source, 3))
        bad_fields = copy.deepcopy(base)
        bad_fields["extra"] = "not allowed"
        controls.append(("extra_field", bad_fields, source, 3))
        for name, candidate, expected_source, expected_arity in controls:
            refused = not check(candidate, expected_source, expected_arity, budget)
            require(refused, "negative control " + name)
            evidence["negative_controls"].append({"name": name, "refused": refused})
        evidence["checks"].append("all malformed, context-changed and head-only shortcuts were refused")
        evidence["result"] = {
            "verdict": "Passed",
            "conditional_conclusion": "For each accepted instance and every n>=0, the checked pure macro maps F(n) to F(n+delta) with delta>0. Induction keeps the head non-returning and input-free, so every suffix extension of the complete program prefix diverges under the declared deterministic profile.",
            "scope": "Two fixed closed self-application sources and one parametric stack family per source",
            "residual": "No branch outside the template is classified. The implication is conditional on the declared interpreter and symbolic-tail rule; it is not a general nontermination decision or Omega convergence result."
        }
        evidence["status"] = "Passed"
    except Exception as exc:
        evidence["status"] = "Failed"
        evidence["failures"].append({"type": type(exc).__name__, "message": str(exc)})
    evidence["timings"]["inside_seconds"] = time.monotonic() - started
    evidence["cost"] = {
        "assertions": assertions,
        "host_work_units": budget.work,
        "search_candidates": 0,
        "self_reported_max_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    }
    evidence["deterministic_sha256"] = digest({k: v for k, v in evidence.items()
                                               if k not in ("timings", "cost", "deterministic_sha256")})
    output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    return evidence["status"] == "Passed"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("refusing to overwrite " + str(args.output))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    raise SystemExit(0 if run(args.output) else 1)
