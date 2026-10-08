#!/usr/bin/env python3
"""Independent bounded receiver for external finite program-positivity claims.

The producer is never imported. Arithmetic dependencies are reconstructed and
evaluated recursively. Positivity families are derived as ordinary sets by
enumerating every family of subsets, independently of complement-choice code.
One process-wide budget and immutable cache serve all receiver calls.
"""

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import time

HERE = Path(__file__).resolve().parent
REQUEST_SCHEMA = "adva.external-program-positivity-request.v0"
REPORT_SCHEMA = "adva.external-program-positivity-report.v0"
BATCH_SCHEMA = "adva.external-program-positivity-batch.v0"
VERIFY_SCHEMA = "adva.external-program-positivity-verification.v0"
MAX_FUEL = 10_000_000
MAX_WALL = 12.0
MAX_BYTES = 1_048_576
NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,31}\Z")
NUMBER = re.compile(r"(?:0|-?[1-9][0-9]*)(?:/[1-9][0-9]*)?\Z")
OPS = {"const": 1, "neg": 1, "add": 2, "sub": 2, "mul": 2, "div": 2}
COMPARE = {"eq", "ne", "lt", "le", "gt", "ge"}
REPORT_KEYS = {"schema", "request_sha256", "binding", "status", "scope", "n",
               "full_mask", "trace", "regions", "models", "queries", "census",
               "fuel", "residuals", "failure"}
QUERY_KEYS = {"name", "mask", "classification", "positive_model_count",
              "negative_model_count", "positive_witness", "negative_witness", "inhabited"}
_budget = None
_cache = {}
_cache_hits = 0


class Rejected(Exception):
    pass


class Limit(Exception):
    pass


class ArithmeticFailure(Exception):
    def __init__(self, index, step):
        self.index, self.step = index, step


class Budget:
    def __init__(self):
        self.used = 0
        self.candidates = 0
        self.deadline = time.monotonic() + MAX_WALL

    def tick(self, cost=1):
        if self.used + cost > MAX_FUEL:
            raise Limit("The shared receiver fuel was exhausted.")
        if time.monotonic() >= self.deadline:
            raise Limit("The shared receiver deadline was reached.")
        self.used += cost


def require(condition, reason):
    if not condition:
        raise Rejected(reason)


def fields(value, required, optional=()):
    require(type(value) is dict and set(required) <= set(value)
            and set(value) <= set(required) | set(optional), "Unexpected or missing object fields.")


def equal(actual, expected, location):
    _budget.tick()
    require(type(actual) is type(expected), location + ": wrong value type.")
    if type(expected) is dict:
        require(set(actual) == set(expected), location + ": wrong object fields.")
        for key in expected:
            equal(actual[key], expected[key], location + "." + str(key))
    elif type(expected) in (list, tuple):
        require(len(actual) == len(expected), location + ": wrong sequence length.")
        for i, (left, right) in enumerate(zip(actual, expected)):
            equal(left, right, location + "." + str(i))
    else:
        require(actual == expected, location + ": incorrect value.")


def canonical(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def bounded_read(path, maximum=MAX_BYTES):
    with Path(path).open("rb") as stream:
        result = stream.read(maximum + 1)
    require(len(result) <= maximum, "A file exceeds its fixed byte bound.")
    return result


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, "Duplicate JSON field.")
        value[key] = item
    return value


def decode(data):
    def bad_constant(value):
        raise Rejected("Nonfinite JSON number.")
    return json.loads(data.decode("utf-8"), object_pairs_hook=unique_object,
                      parse_constant=bad_constant)


def identifier(value):
    require(type(value) is str and NAME.fullmatch(value) is not None
            and value not in {"all", "empty"}, "Invalid or reserved identifier.")


def sequence(value, maximum, minimum=0):
    require(type(value) is list and minimum <= len(value) <= maximum, "List exceeds grammar bounds.")


def names(value, maximum, allowed=None):
    sequence(value, maximum)
    require(all(type(x) is str for x in value) and len(set(value)) == len(value),
            "A name list is invalid or repeated.")
    if allowed is not None:
        require(set(value) <= set(allowed), "Unknown region name.")


def number(text):
    _budget.tick()
    require(type(text) is str and len(text) <= 80 and NUMBER.fullmatch(text) is not None,
            "A rational token is malformed.")
    value = Fraction(text)
    require(str(value) == text, "A rational token is not canonical.")
    return small(value)


def small(value):
    require(abs(value.numerator).bit_length() <= 1024 and value.denominator.bit_length() <= 1024,
            "A rational exceeds the receiver bit bound.")
    return value


class Request:
    """Independently validate the external grammar and retain a dependency DAG."""
    def __init__(self, value):
        _budget.tick()
        self.value = value
        fields(value, {"schema", "program", "fillings", "observations", "properties", "theory", "query"},
               {"domain", "limits"})
        require(value["schema"] == REQUEST_SCHEMA, "Unsupported request schema for a decisive claim.")
        require(len(canonical(value)) <= 65536, "Request byte bound exceeded.")
        if "limits" in value:
            fields(value["limits"], {"fuel"})
            require(type(value["limits"]["fuel"]) is int and 0 <= value["limits"]["fuel"] <= 200000,
                    "Invalid producer fuel limit.")
        program = value["program"]
        fields(program, {"holes", "steps", "outputs"})
        names(program["holes"], 8)
        self.holes = tuple(program["holes"])
        for hole in self.holes:
            identifier(hole)
        sequence(program["steps"], 64)
        available = set(self.holes)
        self.steps = {}
        for step in program["steps"]:
            _budget.tick()
            fields(step, {"name", "op", "args"})
            identifier(step["name"])
            require(step["name"] not in available, "Repeated SSA name.")
            require(type(step["op"]) is str and step["op"] in OPS, "Unsupported arithmetic operation.")
            sequence(step["args"], OPS[step["op"]], OPS[step["op"]])
            for operand in step["args"]:
                if step["op"] == "const":
                    number(operand)
                else:
                    self.token(operand, available)
            self.steps[step["name"]] = step
            available.add(step["name"])
        self.outputs = program["outputs"]
        require(type(self.outputs) is dict and 1 <= len(self.outputs) <= 8, "Output bound violated.")
        for label, operand in self.outputs.items():
            identifier(label)
            self.token(operand, available)
        sequence(value["fillings"], 4, 1)
        self.fillings = value["fillings"]
        for row in self.fillings:
            fields(row, self.holes)
            for text in row.values():
                number(text)
        for field, cap in (("observations", 8), ("properties", 16)):
            require(type(value[field]) is dict and len(value[field]) <= cap, "Named-region bound violated.")
            for name in value[field]:
                identifier(name)
        require(not (set(value["observations"]) & set(value["properties"])), "Overlapping region names.")
        self.tree_nodes = 0
        self.available = available
        for tree in value["observations"].values():
            self.predicate_valid(tree)
        sequence(value.get("domain", []), 8)
        for tree in value.get("domain", []):
            self.predicate_valid(tree)
        self.region_names = set(value["observations"]) | set(value["properties"]) | {"all", "empty"}
        for tree in value["properties"].values():
            self.region_valid(tree)
        seen, active = set(), set()
        def visit(name):
            _budget.tick()
            if name in seen or name not in value["properties"]:
                return
            require(name not in active, "Cyclic named property.")
            active.add(name)
            def walk(tree):
                _budget.tick()
                if type(tree) is str:
                    visit(tree)
                else:
                    for child in tree["args"]:
                        walk(child)
            walk(value["properties"][name])
            active.remove(name)
            seen.add(name)
        for name in value["properties"]:
            visit(name)
        theory = value["theory"]
        fields(theory, {"policy", "positive", "negative"}, {"marked"})
        require(theory["policy"] in {"basic", "joint", "marked"}, "Unsupported positivity policy.")
        if theory["policy"] == "marked":
            require(type(theory.get("marked")) is int and 0 <= theory["marked"] < len(self.fillings),
                    "Invalid marked filling index.")
        else:
            require("marked" not in theory, "Extraneous marked index.")
        names(theory["positive"], 24, self.region_names)
        names(theory["negative"], 24, self.region_names)
        names(value["query"], 16, self.region_names)

    def token(self, value, available, allow_output=False):
        _budget.tick()
        require(type(value) is str, "A token must be a string.")
        if value in available or allow_output and value.startswith("out.") and value[4:] in self.outputs:
            return
        require(not NAME.fullmatch(value) and not value.startswith("out."), "Unavailable token reference.")
        number(value)

    def node(self, depth):
        _budget.tick()
        self.tree_nodes += 1
        require(self.tree_nodes <= 256 and depth <= 16, "Tree node or depth bound violated.")

    def predicate_valid(self, tree, depth=1):
        self.node(depth)
        fields(tree, {"op", "args"})
        op = tree["op"]
        require(type(op) is str, "Predicate operation must be a string.")
        if op in COMPARE:
            sequence(tree["args"], 2, 2)
            for item in tree["args"]:
                self.token(item, self.available, True)
        else:
            require(op in {"and", "or", "not"}, "Unsupported predicate operation.")
            sequence(tree["args"], 256, 1 if op == "not" else 2)
            require(op != "not" or len(tree["args"]) == 1, "Wrong predicate negation arity.")
            for item in tree["args"]:
                self.predicate_valid(item, depth + 1)

    def region_valid(self, tree, depth=1):
        self.node(depth)
        if type(tree) is str:
            require(tree in self.region_names, "Unknown Boolean region.")
            return
        fields(tree, {"op", "args"})
        op = tree["op"]
        require(type(op) is str and op in {"and", "or", "not", "xor"}, "Unsupported region operation.")
        sequence(tree["args"], 256, 1 if op == "not" else 2)
        require(op != "not" or len(tree["args"]) == 1, "Wrong region negation arity.")
        require(op != "xor" or len(tree["args"]) == 2, "Wrong xor arity.")
        for item in tree["args"]:
            self.region_valid(item, depth + 1)

    def execute(self):
        """Resolve each node through its dependencies; retain source-order traces."""
        traces = []
        for index, filling in enumerate(self.fillings):
            _budget.tick()
            memo = {name: number(text) for name, text in filling.items()}
            def operand(token):
                _budget.tick()
                if token in memo:
                    return memo[token]
                if token in self.steps:
                    step = self.steps[token]
                    values = tuple(operand(t) for t in step["args"])
                    op = step["op"]
                    if op == "const":
                        result = values[0]
                    elif op == "neg":
                        result = -values[0]
                    elif op == "add":
                        result = values[0] + values[1]
                    elif op == "sub":
                        result = values[0] - values[1]
                    elif op == "mul":
                        result = values[0] * values[1]
                    else:
                        if values[1] == 0:
                            raise ArithmeticFailure(index, token)
                        result = values[0] / values[1]
                    memo[token] = small(result)
                    return result
                return number(token)
            trace = {"index": index, "filling": dict(filling), "steps": [],
                     "outputs": {}, "observations": {}, "domain": []}
            traces.append(trace)
            try:
                for name in self.steps:
                    trace["steps"].append({"name": name, "value": str(operand(name))})
                output_numbers = {label: operand(token) for label, token in self.outputs.items()}
                trace["outputs"] = {label: str(value) for label, value in output_numbers.items()}
                def observation_token(token):
                    if token.startswith("out."):
                        return output_numbers[token[4:]]
                    return operand(token)
                def predicate(tree):
                    _budget.tick()
                    op = tree["op"]
                    if op in COMPARE:
                        left, right = (observation_token(t) for t in tree["args"])
                        return {"eq": lambda: left == right, "ne": lambda: left != right,
                                "lt": lambda: left < right, "le": lambda: left <= right,
                                "gt": lambda: left > right, "ge": lambda: left >= right}[op]()
                    values = [predicate(child) for child in tree["args"]]
                    return all(values) if op == "and" else any(values) if op == "or" else not values[0]
                for tree in self.value.get("domain", []):
                    valid = predicate(tree)
                    trace["domain"].append(valid)
                    require(valid, "A decisive or undefined claim includes a failed domain guard.")
                trace["observations"] = {label: predicate(tree) for label, tree in self.value["observations"].items()}
            except ArithmeticFailure as failure:
                return traces, failure
        return traces, None

    def regions(self, traces):
        carrier = frozenset(range(len(self.fillings)))
        result = {"all": carrier, "empty": frozenset()}
        for name in self.value["observations"]:
            result[name] = frozenset(t["index"] for t in traces if t["observations"][name])
        def named(name):
            _budget.tick()
            if name not in result:
                result[name] = region(self.value["properties"][name])
            return result[name]
        def region(tree):
            _budget.tick()
            if type(tree) is str:
                return named(tree)
            values = [region(child) for child in tree["args"]]
            if tree["op"] == "not":
                return carrier - values[0]
            if tree["op"] == "xor":
                return values[0].symmetric_difference(values[1])
            if tree["op"] == "and":
                return frozenset.intersection(*values)
            return frozenset.union(*values)
        for name in self.value["properties"]:
            named(name)
        return result


def region_mask(region):
    return sum(1 << point for point in region)


def families(n):
    """All ordinary set families, filtered by complement and inclusion axioms."""
    global _cache_hits
    if n in _cache:
        _cache_hits += 1
        return _cache[n]
    carrier = frozenset(range(n))
    subsets = tuple(frozenset(i for i in range(n) if mask & (1 << i)) for mask in range(1 << n))
    accepted = []
    for encoded in range(1 << len(subsets)):
        _budget.tick()
        _budget.candidates += 1
        family = frozenset(subsets[i] for i in range(len(subsets)) if encoded & (1 << i))
        upward = True
        for lower in subsets:
            for upper in subsets:
                if lower.issubset(upper):
                    _budget.tick()
                    if lower in family and upper not in family:
                        upward = False
                        break
            if not upward:
                break
        if not upward:
            continue
        complement = True
        for region in subsets:
            _budget.tick()
            if (region in family) == ((carrier - region) in family):
                complement = False
                break
        if complement:
            accepted.append(family)
    _cache[n] = tuple(accepted)
    return _cache[n]


def realizers(family, n):
    result = set(range(n))
    for region in family:
        _budget.tick()
        result.intersection_update(region)
    return sorted(result)


def common_report(request, report):
    fields(report, REPORT_KEYS)
    equal(report["schema"], REPORT_SCHEMA, "report.schema")
    equal(report["scope"], "declared-finite-carrier", "report.scope")
    equal(report["request_sha256"], digest(canonical(request)), "report.request_sha256")
    equal(report["binding"], {"producer_sha256": digest(bounded_read(HERE / "meta.py")),
                              "contract_sha256": digest(bounded_read(HERE / "contract.json"))}, "report.binding")
    fuel = report["fuel"]
    fields(fuel, {"limit", "used", "remaining"})
    require(all(type(fuel[key]) is int for key in fuel), "Producer fuel must use integer counts.")
    limit = 200000
    if type(request) is dict and type(request.get("limits")) is dict:
        proposed = request["limits"].get("fuel")
        if type(proposed) is int and 0 <= proposed <= 200000:
            limit = proposed
    require(fuel["limit"] == limit and 0 <= fuel["used"] <= limit
            and fuel["remaining"] == limit - fuel["used"], "Producer fuel accounting is invalid.")
    require(type(report["n"]) is int and 0 <= report["n"] <= 4, "Invalid reported carrier size.")
    equal(report["full_mask"], (1 << report["n"]) - 1, "report.full_mask")
    sequence(report["trace"], 4)
    require(type(report["regions"]) is dict and len(report["regions"]) <= 26,
            "Invalid region report bound.")
    require(all(type(mask) is int and 0 <= mask <= report["full_mask"] for mask in report["regions"].values()),
            "Invalid region mask.")
    sequence(report["models"], 256)
    sequence(report["queries"], 16)
    fields(report["census"], {"candidate_count", "surviving_count", "complete"})
    require(type(report["census"]["candidate_count"]) is int and 0 <= report["census"]["candidate_count"] <= 256,
            "Invalid census candidate count.")
    sequence(report["residuals"], 16)
    require(all(type(text) is str and len(text) <= 1024 for text in report["residuals"]),
            "Invalid residual text.")


def no_claim(request, report):
    equal(report["models"], [], "report.models")
    equal(report["census"]["surviving_count"], 0, "report.census.surviving_count")
    equal(report["census"]["complete"], False, "report.census.complete")
    require(type(report["failure"]) is dict, "A withheld result must explain its failure.")
    require(type(report["failure"].get("code")) is str and type(report["failure"].get("message")) is str,
            "Invalid failure explanation.")
    query_names = request.get("query", []) if type(request) is dict else []
    if type(query_names) is not list:
        query_names = []
    query_names = [name for name in query_names[:16] if type(name) is str and len(name) <= 32]
    equal(len(report["queries"]), len(query_names), "report.queries.count")
    for name, query in zip(query_names, report["queries"]):
        fields(query, QUERY_KEYS)
        expected = {"name": name, "mask": report["regions"].get(name), "classification": "Unknown",
                    "positive_model_count": 0, "negative_model_count": 0,
                    "positive_witness": None, "negative_witness": None,
                    "inhabited": {"value": None, "filling_indices": []}}
        equal(query, expected, "report.query")


def analyzed(valid, report, traces):
    request = valid.value
    n = len(valid.fillings)
    equal(report["n"], n, "report.n")
    equal(report["trace"], traces, "report.trace")
    equal(report["failure"], None, "report.failure")
    regions = valid.regions(traces)
    equal(report["regions"], {name: region_mask(region) for name, region in regions.items()}, "report.regions")
    selected = []
    for family in families(n):
        _budget.tick()
        common = realizers(family, n)
        theory = request["theory"]
        if theory["policy"] == "joint" and not common:
            continue
        if theory["policy"] == "marked" and theory["marked"] not in common:
            continue
        if not all(regions[name] in family for name in theory["positive"]):
            continue
        if any(regions[name] in family for name in theory["negative"]):
            continue
        selected.append(family)
    expected_masks = {tuple(sorted(region_mask(region) for region in family)) for family in selected}
    observed_masks = set()
    for model in report["models"]:
        fields(model, {"positive_masks", "realizers"})
        masks = model["positive_masks"]
        require(type(masks) is list and all(type(mask) is int and 0 <= mask < 1 << n for mask in masks),
                "A reported model contains invalid regions.")
        require(masks == sorted(set(masks)), "A reported model repeats or reorders regions.")
        key = tuple(masks)
        require(key not in observed_masks, "A reported model is duplicated.")
        require(key in expected_masks, "A reported model violates the declared positivity theory.")
        observed_masks.add(key)
        family = next(f for f in selected if tuple(sorted(region_mask(s) for s in f)) == key)
        equal(model["realizers"], realizers(family, n), "report.model.realizers")
    require(observed_masks == expected_masks, "The reported surviving model census is incomplete.")
    equal(report["census"], {"candidate_count": 1 << (1 << (n - 1)),
                             "surviving_count": len(selected), "complete": True}, "report.census")
    equal(len(report["queries"]), len(request["query"]), "report.queries.count")
    for name, query in zip(request["query"], report["queries"]):
        mask = region_mask(regions[name])
        positive = [i for i, model in enumerate(report["models"]) if mask in model["positive_masks"]]
        negative = [i for i, model in enumerate(report["models"]) if mask not in model["positive_masks"]]
        if not report["models"]:
            classification = "Inconsistent"
        elif not negative:
            classification = "ForcedPositive"
        elif not positive:
            classification = "ForcedNegative"
        else:
            classification = "Underdetermined"
        expected = {"name": name, "mask": mask, "classification": classification,
                    "positive_model_count": len(positive), "negative_model_count": len(negative),
                    "positive_witness": positive[0] if positive else None,
                    "negative_witness": negative[0] if negative else None,
                    "inhabited": {"value": bool(regions[name]), "filling_indices": sorted(regions[name])}}
        equal(query, expected, "report.query")


def _verify(request, report):
    _budget.tick()
    common_report(request, report)
    status = report["status"]
    if status in {"InvalidInput", "Unsupported", "Unknown"}:
        no_claim(request, report)
        return "NoClaim", "No decisive positivity claim was emitted; no semantic theorem is verified."
    require(status in {"Analyzed", "UndefinedOnCarrier"}, "Unknown producer outcome.")
    valid = Request(request)
    traces, arithmetic_failure = valid.execute()
    if status == "UndefinedOnCarrier":
        no_claim(request, report)
        require(arithmetic_failure is not None, "The alleged zero divisor does not occur.")
        equal(report["n"], len(valid.fillings), "report.n")
        equal(report["trace"], traces, "report.trace")
        equal(report["regions"], {}, "report.regions")
        equal(report["census"]["candidate_count"], 0, "report.census.candidate_count")
        equal(report["failure"], {"code": "division_by_zero", "message": "A declared filling has a zero divisor.",
                                  "filling_index": arithmetic_failure.index, "step": arithmetic_failure.step,
                                  "denominator": "0"}, "report.failure")
        return "Verified", "The finite zero-divisor witness is verified; no positivity conclusion follows."
    require(arithmetic_failure is None, "The program is undefined on its declared carrier.")
    analyzed(valid, report, traces)
    return "Verified", "Finite arithmetic, region incidence, complete model census and query witnesses are verified."


def verify(request, report):
    """Check one parsed claim under the shared process budget; no producer import."""
    global _budget
    if _budget is None:
        _budget = Budget()
    try:
        status, reason = _verify(request, report)
    except Limit as error:
        status, reason = "Unknown", str(error)
    except (Rejected, ArithmeticFailure, KeyError, TypeError, ValueError, ZeroDivisionError,
            OSError, RecursionError, UnicodeError, OverflowError) as error:
        status, reason = "Rejected", str(error)
    return {"schema": VERIFY_SCHEMA, "status": status, "reason": reason,
            "scope": "declared-finite-carrier", "work": _budget.used,
            "family_candidates": _budget.candidates, "cache_hits": _cache_hits}


def verify_batch(cases, batch):
    """Verify at most fourteen requests, retaining each claim's distinct outcome."""
    global _budget
    if _budget is None:
        _budget = Budget()
    try:
        require(type(cases) is dict and 1 <= len(cases) <= 14, "Invalid receiver batch size.")
        fields(batch, {"schema", "reports"})
        equal(batch["schema"], BATCH_SCHEMA, "batch.schema")
        require(type(batch["reports"]) is dict and set(batch["reports"]) == set(cases),
                "Receiver batch case names differ.")
        reports = {name: verify(request, batch["reports"][name]) for name, request in cases.items()}
        statuses = {report["status"] for report in reports.values()}
        status = "Rejected" if "Rejected" in statuses else "Unknown" if "Unknown" in statuses else "Verified"
        return {"schema": VERIFY_SCHEMA, "status": status, "reports": reports,
                "work": _budget.used, "family_candidates": _budget.candidates, "cache_hits": _cache_hits,
                "verifier_sha256": digest(bounded_read(Path(__file__).resolve()))}
    except Limit as error:
        status, reason = "Unknown", str(error)
    except (Rejected, KeyError, TypeError, ValueError, OSError, RecursionError, UnicodeError) as error:
        status, reason = "Rejected", str(error)
    return {"schema": VERIFY_SCHEMA, "status": status, "reason": reason,
            "work": _budget.used, "family_candidates": _budget.candidates, "cache_hits": _cache_hits}


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_path", type=Path, help="Single request or mapping of batch cases")
    parser.add_argument("report_path", type=Path, help="Corresponding single report or batch evidence")
    args = parser.parse_args(argv)
    try:
        request = decode(bounded_read(args.input_path))
        report = decode(bounded_read(args.report_path))
        if type(request) is dict and request.get("schema") == REQUEST_SCHEMA:
            result = verify(request, report)
        else:
            result = verify_batch(request, report)
    except (Rejected, ValueError, UnicodeError, OSError, RecursionError) as error:
        result = {"schema": VERIFY_SCHEMA, "status": "Rejected", "reason": str(error)}
    print(json.dumps(result, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")))
    return {"Verified": 0, "NoClaim": 0, "Rejected": 2, "Unknown": 3}[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
