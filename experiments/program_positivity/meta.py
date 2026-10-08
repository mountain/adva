#!/usr/bin/env python3
"""Bounded, external finite positivity metaprogram.

Input is data, never executable host code.  This module creates no native Adva
identities or certificates.  Its complete conclusions concern only the supplied
finite carrier and the explicitly selected static positivity interpretation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from fractions import Fraction
from pathlib import Path


REQUEST_SCHEMA = "adva.external-program-positivity-request.v0"
REPORT_SCHEMA = "adva.external-program-positivity-report.v0"
BATCH_SCHEMA = "adva.external-program-positivity-batch.v0"
MAX_REQUEST_BYTES = 65536
MAX_FUEL = 200000
MAX_BITS = 1024
MAX_DEPTH = 16
MAX_TREE_NODES = 256
IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,31}\Z")
RATIONAL = re.compile(r"(?:0|-?[1-9][0-9]*)(?:/[1-9][0-9]*)?\Z")
ARITIES = {"const": 1, "neg": 1, "add": 2, "sub": 2, "mul": 2, "div": 2}
COMPARISONS = {"eq", "ne", "lt", "le", "gt", "ge"}
RESERVED = {"all", "empty"}


class _Stop(Exception):
    def __init__(self, status, code, message, **details):
        super().__init__(message)
        self.status = status
        self.failure = {"code": code, "message": message, **details}


class _Budget:
    """Logical fuel charges validation, arithmetic, predicates and model checks."""

    def __init__(self, limit):
        self.limit = limit
        self.used = 0
        self.deadline = time.monotonic() + 8

    def tick(self, amount=1):
        if time.monotonic() > self.deadline:
            raise _Stop("Unknown", "deadline", "The per-request deadline was reached.")
        if self.used + amount > self.limit:
            raise _Stop("Unknown", "fuel", "The declared logical fuel was exhausted.")
        self.used += amount

    def snapshot(self):
        return {"limit": self.limit, "used": self.used, "remaining": self.limit - self.used}


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def _binding():
    here = Path(__file__).resolve()
    return {
        "producer_sha256": hashlib.sha256(here.read_bytes()).hexdigest(),
        "contract_sha256": hashlib.sha256(here.with_name("contract.json").read_bytes()).hexdigest(),
    }


def _invalid(code, message, **details):
    raise _Stop("InvalidInput", code, message, **details)


def _unsupported(code, message, **details):
    raise _Stop("Unsupported", code, message, **details)


def _keys(value, required, optional=()):
    if not isinstance(value, dict) or set(value) - set(required) - set(optional) or set(required) - set(value):
        _invalid("object_keys", "An object has missing or unexpected fields.")


def _identifier(value):
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value) or value in RESERVED:
        _invalid("identifier", "An identifier is invalid or reserved.")


def _list(value, maximum, label, minimum=0):
    if not isinstance(value, list) or not minimum <= len(value) <= maximum:
        _invalid("list_bound", "A list is outside its declared finite bound.", field=label)


def _mapping(value, maximum, label, minimum=0):
    if not isinstance(value, dict) or not minimum <= len(value) <= maximum:
        _invalid("mapping_bound", "A mapping is outside its declared finite bound.", field=label)
    for name in value:
        _identifier(name)


def _unique_names(value, maximum, label, allowed=None):
    _list(value, maximum, label)
    if any(not isinstance(name, str) for name in value) or len(set(value)) != len(value):
        _invalid("name_list", "A name list contains invalid or repeated names.", field=label)
    if allowed is not None and any(name not in allowed for name in value):
        _invalid("unknown_region", "A name does not identify a declared region.", field=label)


def _fraction(token, budget):
    budget.tick()
    if not isinstance(token, str) or len(token) > 80 or not RATIONAL.fullmatch(token):
        _invalid("rational", "A literal is not a canonical bounded rational string.")
    value = Fraction(token)
    if _qstr(value) != token:
        _invalid("rational", "A rational literal is not reduced or has a redundant denominator.")
    return _bounded(value)


def _qstr(value):
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _bounded(value):
    if abs(value.numerator).bit_length() > MAX_BITS or value.denominator.bit_length() > MAX_BITS:
        raise _Stop("Unknown", "rational_bits", "The exact rational bit bound was reached.")
    return value


def _token(token, names, outputs, budget):
    budget.tick()
    if not isinstance(token, str):
        _invalid("token", "An arithmetic operand must be a string token.")
    if token in names:
        return
    if outputs is not None and token.startswith("out.") and token[4:] in outputs:
        return
    if IDENTIFIER.fullmatch(token) or token.startswith("out."):
        _invalid("reference", "An operand refers to an unavailable name.", token=token)
    _fraction(token, budget)


def _value(token, environment, outputs, budget):
    budget.tick()
    if token in environment:
        return environment[token]
    if outputs is not None and token.startswith("out."):
        return outputs[token[4:]]
    return _fraction(token, budget)


class _Trees:
    def __init__(self, budget):
        self.budget = budget
        self.nodes = 0

    def node(self, depth):
        self.budget.tick()
        self.nodes += 1
        if self.nodes > MAX_TREE_NODES or depth > MAX_DEPTH:
            _invalid("tree_bound", "Predicate or region trees exceed the declared bound.")

    def predicate(self, tree, names, outputs, depth=1):
        self.node(depth)
        _keys(tree, ("op", "args"))
        op, args = tree["op"], tree["args"]
        if not isinstance(op, str):
            _invalid("predicate_operation", "A predicate operation must be a string.")
        if op in COMPARISONS:
            _list(args, 2, "predicate arguments", 2)
            for token in args:
                _token(token, names, outputs, self.budget)
        elif op in {"and", "or", "not"}:
            _list(args, MAX_TREE_NODES, "predicate arguments", 1 if op == "not" else 2)
            if op == "not" and len(args) != 1:
                _invalid("predicate_arity", "Negation takes exactly one argument.")
            for child in args:
                self.predicate(child, names, outputs, depth + 1)
        else:
            _unsupported("predicate_operation", "The predicate operation is outside the grammar.", operation=op)

    def region(self, tree, names, depth=1):
        self.node(depth)
        if isinstance(tree, str):
            if tree not in names:
                _invalid("region_reference", "A region tree refers to an unknown region.", name=tree)
            return
        _keys(tree, ("op", "args"))
        op, args = tree["op"], tree["args"]
        if not isinstance(op, str):
            _invalid("region_operation", "A region operation must be a string.")
        if op not in {"and", "or", "not", "xor"}:
            _unsupported("region_operation", "The region operation is outside the grammar.", operation=op)
        _list(args, MAX_TREE_NODES, "region arguments", 1 if op == "not" else 2)
        if op == "not" and len(args) != 1 or op == "xor" and len(args) != 2:
            _invalid("region_arity", "Negation takes one argument and xor takes two.")
        for child in args:
            self.region(child, names, depth + 1)


def _validate(request, budget):
    budget.tick()
    _keys(request, ("schema", "program", "fillings", "observations", "properties", "theory", "query"),
          ("domain", "limits"))
    if request["schema"] != REQUEST_SCHEMA:
        _unsupported("schema", "The request schema is unsupported.")
    if "limits" in request:
        _keys(request["limits"], ("fuel",))
    program = request["program"]
    _keys(program, ("holes", "steps", "outputs"))
    _unique_names(program["holes"], 8, "holes")
    names = set()
    for name in program["holes"]:
        budget.tick()
        _identifier(name)
        names.add(name)
    _list(program["steps"], 64, "steps")
    for step in program["steps"]:
        budget.tick()
        _keys(step, ("name", "op", "args"))
        _identifier(step["name"])
        if step["name"] in names:
            _invalid("duplicate_step", "A step repeats a hole or earlier step name.")
        op = step["op"]
        if not isinstance(op, str):
            _invalid("operation", "An arithmetic operation must be a string.")
        if op not in ARITIES:
            _unsupported("operation", "The arithmetic operation is outside the grammar.", operation=op)
        _list(step["args"], ARITIES[op], "arithmetic arguments", ARITIES[op])
        for token in step["args"]:
            if op == "const":
                _fraction(token, budget)
            else:
                _token(token, names, None, budget)
        names.add(step["name"])
    outputs = program["outputs"]
    _mapping(outputs, 8, "outputs", 1)
    for token in outputs.values():
        _token(token, names, None, budget)
    _list(request["fillings"], 4, "fillings", 1)
    for filling in request["fillings"]:
        budget.tick()
        if not isinstance(filling, dict) or set(filling) != set(program["holes"]):
            _invalid("filling", "A filling must supply exactly the declared holes.")
        for value in filling.values():
            _fraction(value, budget)
    observations, properties = request["observations"], request["properties"]
    _mapping(observations, 8, "observations")
    _mapping(properties, 16, "properties")
    if set(observations) & set(properties):
        _invalid("region_names", "Observation and property names must be disjoint.")
    trees = _Trees(budget)
    for tree in observations.values():
        trees.predicate(tree, names, outputs)
    guards = request.get("domain", [])
    _list(guards, 8, "domain")
    for tree in guards:
        trees.predicate(tree, names, outputs)
    region_names = set(observations) | set(properties) | RESERVED
    for tree in properties.values():
        trees.region(tree, region_names)
    visiting, finished = set(), set()

    def visit(name):
        budget.tick()
        if name in finished or name not in properties:
            return
        if name in visiting:
            _invalid("property_cycle", "Named property dependencies contain a cycle.")
        visiting.add(name)

        def scan(tree):
            budget.tick()
            if isinstance(tree, str):
                visit(tree)
            else:
                for child in tree["args"]:
                    scan(child)

        scan(properties[name])
        visiting.remove(name)
        finished.add(name)

    for name in properties:
        visit(name)
    theory = request["theory"]
    _keys(theory, ("policy", "positive", "negative"), ("marked",))
    policy = theory["policy"]
    if not isinstance(policy, str):
        _invalid("policy", "The positivity policy must be a string.")
    if policy not in {"basic", "joint", "marked"}:
        _unsupported("policy", "The positivity policy is unsupported.")
    if policy == "marked":
        if "marked" not in theory or type(theory["marked"]) is not int or not 0 <= theory["marked"] < len(request["fillings"]):
            _invalid("marked", "The marked policy requires a valid filling index.")
    elif "marked" in theory:
        _invalid("marked", "A marked index is valid only for the marked policy.")
    _unique_names(theory["positive"], 24, "positive premises", region_names)
    _unique_names(theory["negative"], 24, "negative premises", region_names)
    _unique_names(request["query"], 16, "query", region_names)


def _predicate(tree, environment, outputs, budget):
    budget.tick()
    op, args = tree["op"], tree["args"]
    if op in COMPARISONS:
        left, right = (_value(token, environment, outputs, budget) for token in args)
        if op == "eq":
            return left == right
        if op == "ne":
            return left != right
        if op == "lt":
            return left < right
        if op == "le":
            return left <= right
        if op == "gt":
            return left > right
        return left >= right
    # All branches are charged and evaluated, so logical fuel does not hide work.
    values = [_predicate(child, environment, outputs, budget) for child in args]
    if op == "and":
        return all(values)
    if op == "or":
        return any(values)
    return not values[0]


def _execute(request, report, budget):
    program = request["program"]
    for index, filling in enumerate(request["fillings"]):
        budget.tick()
        environment = {name: _fraction(value, budget) for name, value in filling.items()}
        trace = {"index": index, "filling": dict(filling), "steps": [], "outputs": {}, "observations": {}, "domain": []}
        report["trace"].append(trace)
        for step in program["steps"]:
            budget.tick()
            args = [_value(token, environment, None, budget) for token in step["args"]]
            op = step["op"]
            if op == "const":
                value = args[0]
            elif op == "neg":
                value = -args[0]
            elif op == "add":
                value = args[0] + args[1]
            elif op == "sub":
                value = args[0] - args[1]
            elif op == "mul":
                value = args[0] * args[1]
            else:
                if args[1] == 0:
                    raise _Stop("UndefinedOnCarrier", "division_by_zero", "A declared filling has a zero divisor.",
                                filling_index=index, step=step["name"], denominator="0")
                value = args[0] / args[1]
            environment[step["name"]] = _bounded(value)
            trace["steps"].append({"name": step["name"], "value": _qstr(value)})
        outputs = {name: _value(token, environment, None, budget) for name, token in program["outputs"].items()}
        trace["outputs"] = {name: _qstr(value) for name, value in outputs.items()}
        for guard_index, tree in enumerate(request.get("domain", [])):
            valid = _predicate(tree, environment, outputs, budget)
            trace["domain"].append(valid)
            if not valid:
                _invalid("domain_guard", "A declared filling violates a domain guard; it was not discarded.",
                         filling_index=index, guard_index=guard_index)
        trace["observations"] = {
            name: _predicate(tree, environment, outputs, budget)
            for name, tree in request["observations"].items()
        }


def _regions(request, report, budget):
    full = report["full_mask"]
    regions = {"all": full, "empty": 0}
    for name in request["observations"]:
        mask = 0
        for entry in report["trace"]:
            budget.tick()
            if entry["observations"][name]:
                mask |= 1 << entry["index"]
        regions[name] = mask
    properties = request["properties"]

    def name_mask(name):
        budget.tick()
        if name not in regions:
            regions[name] = tree_mask(properties[name])
        return regions[name]

    def tree_mask(tree):
        budget.tick()
        if isinstance(tree, str):
            return name_mask(tree)
        op = tree["op"]
        values = [tree_mask(child) for child in tree["args"]]
        if op == "not":
            return full ^ values[0]
        if op == "xor":
            return values[0] ^ values[1]
        result = full if op == "and" else 0
        for value in values:
            budget.tick()
            result = result & value if op == "and" else result | value
        return result

    for name in properties:
        name_mask(name)
    report["regions"] = regions


def _census(request, report, budget):
    full = report["full_mask"]
    pairs = [(mask, full ^ mask) for mask in range(full + 1) if mask < (full ^ mask)]
    candidate_total = 1 << len(pairs)
    if candidate_total > 256:
        raise _Stop("Unknown", "candidate_bound", "The complement-choice candidate bound was reached.")
    theory, regions = request["theory"], report["regions"]
    positive_premises = [regions[name] for name in theory["positive"]]
    negative_premises = [regions[name] for name in theory["negative"]]
    models = []
    for choice in range(candidate_total):
        budget.tick()
        report["census"]["candidate_count"] += 1
        positive = set()
        for bit, pair in enumerate(pairs):
            budget.tick()
            positive.add(pair[(choice >> bit) & 1])
        accepted = True
        for smaller in sorted(positive):
            for larger in range(full + 1):
                budget.tick()
                if smaller & larger == smaller and larger not in positive:
                    accepted = False
                    break
            if not accepted:
                break
        if not accepted:
            continue
        common = full
        for mask in sorted(positive):
            budget.tick()
            common &= mask
        if theory["policy"] == "joint" and not common:
            continue
        if theory["policy"] == "marked" and not (common & (1 << theory["marked"])):
            continue
        for mask in positive_premises:
            budget.tick()
            if mask not in positive:
                accepted = False
        for mask in negative_premises:
            budget.tick()
            if mask in positive:
                accepted = False
        if accepted:
            models.append({"positive_masks": sorted(positive),
                           "realizers": [index for index in range(report["n"]) if common & (1 << index)]})
    report["models"] = models
    report["census"]["surviving_count"] = len(models)
    report["census"]["complete"] = True


def _queries(request, report, budget):
    queries = []
    models = report["models"]
    for name in request["query"]:
        budget.tick()
        mask = report["regions"][name]
        positive, negative = [], []
        for index, model in enumerate(models):
            budget.tick()
            (positive if mask in model["positive_masks"] else negative).append(index)
        if not models:
            classification = "Inconsistent"
        elif not negative:
            classification = "ForcedPositive"
        elif not positive:
            classification = "ForcedNegative"
        else:
            classification = "Underdetermined"
        queries.append({"name": name, "mask": mask, "classification": classification,
                        "positive_model_count": len(positive), "negative_model_count": len(negative),
                        "positive_witness": positive[0] if positive else None,
                        "negative_witness": negative[0] if negative else None,
                        "inhabited": {"value": bool(mask),
                                      "filling_indices": [index for index in range(report["n"]) if mask & (1 << index)]}})
    report["queries"] = queries


def analyze(request):
    """Analyze one strict JSON request without executing arbitrary source code."""
    limit = MAX_FUEL
    failure = None
    if isinstance(request, dict) and isinstance(request.get("limits"), dict) and "fuel" in request["limits"]:
        proposed = request["limits"]["fuel"]
        if type(proposed) is not int or not 0 <= proposed <= MAX_FUEL:
            failure = {"code": "fuel_limit", "message": "Fuel must be an integer between zero and the fixed maximum."}
        else:
            limit = proposed
    budget = _Budget(limit)
    request_digest = None
    try:
        encoded = _canonical(request)
        request_digest = hashlib.sha256(encoded).hexdigest()
        if len(encoded) > MAX_REQUEST_BYTES:
            failure = {"code": "request_bytes", "message": "The canonical request exceeds its byte bound."}
    except (TypeError, ValueError, UnicodeError, RecursionError):
        failure = {"code": "json", "message": "The request is not strict JSON data."}
    query_names = request.get("query", []) if isinstance(request, dict) else []
    if not isinstance(query_names, list):
        query_names = []
    query_names = [name for name in query_names[:16] if isinstance(name, str) and len(name) <= 32]
    report = {
        "schema": REPORT_SCHEMA, "request_sha256": request_digest, "binding": _binding(),
        "status": "InvalidInput" if failure else "Unknown", "scope": "declared-finite-carrier",
        "n": 0, "full_mask": 0, "trace": [], "regions": {}, "models": [],
        "queries": [], "census": {"candidate_count": 0, "surviving_count": 0, "complete": False},
        "fuel": budget.snapshot(), "residuals": [], "failure": failure,
    }
    try:
        if failure:
            raise _Stop("InvalidInput", **failure)
        budget.tick(max(1, (len(encoded) + 63) // 64))
        _validate(request, budget)
        report["n"] = len(request["fillings"])
        report["full_mask"] = (1 << report["n"]) - 1
        _execute(request, report, budget)
        _regions(request, report, budget)
        _census(request, report, budget)
        _queries(request, report, budget)
        report["status"] = "Analyzed"
        report["residuals"] = ["Behavior outside the declared finite carrier is unresolved.",
                               "The selected static policy is not a decision of intrinsic or full modal positivity."]
    except _Stop as stopped:
        report["status"] = stopped.status
        report["failure"] = stopped.failure
        # An incomplete census or query sweep never exposes a partial model list
        # as exhaustive, and never emits a decisive query classification.
        report["models"] = []
        report["census"]["surviving_count"] = 0
        report["census"]["complete"] = False
        report["queries"] = [{"name": name, "mask": report["regions"].get(name), "classification": "Unknown",
                              "positive_model_count": 0, "negative_model_count": 0,
                              "positive_witness": None, "negative_witness": None,
                              "inhabited": {"value": None, "filling_indices": []}}
                             for name in query_names]
        report["residuals"] = ["No decisive positivity claim is made for this request."]
    report["fuel"] = budget.snapshot()
    return report


def _pairs_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("Duplicate JSON object key.")
        value[key] = item
    return value


def _read_json(path, maximum):
    with Path(path).open("rb") as source:
        data = source.read(maximum + 1)
    if len(data) > maximum:
        raise ValueError("Input file exceeds its byte bound.")
    return json.loads(data.decode("utf-8"), object_pairs_hook=_pairs_object,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError("Nonfinite JSON number.")))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", nargs="?", help="Strict JSON request file")
    parser.add_argument("--batch", help="Mapping of case names to requests, at most 14 cases")
    parser.add_argument("--output", required=True, help="New report path; existing output is refused before analysis")
    args = parser.parse_args(argv)
    if bool(args.request) == bool(args.batch):
        parser.error("Supply exactly one request path or --batch.")
    try:
        # Exclusive creation precedes even reading the input or invoking analyze.
        with open(args.output, "x", encoding="utf-8") as destination:
            if args.batch:
                cases = _read_json(args.batch, 14 * MAX_REQUEST_BYTES)
                if not isinstance(cases, dict) or not 1 <= len(cases) <= 14:
                    raise ValueError("Batch must be a mapping containing 1..14 requests.")
                for name in cases:
                    _identifier(name)
                result = {"schema": BATCH_SCHEMA, "reports": {name: analyze(request) for name, request in cases.items()}}
            else:
                result = analyze(_read_json(args.request, MAX_REQUEST_BYTES))
            encoded = json.dumps(result, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2) + "\n"
            if len(encoded.encode("utf-8")) > 1048576:
                raise ValueError("Output file exceeds its byte bound.")
            destination.write(encoded)
    except (OSError, ValueError, UnicodeError, RecursionError, _Stop) as error:
        print(f"metaprogram: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
