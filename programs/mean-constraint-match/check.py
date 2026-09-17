#!/usr/bin/env python3
"""Finite, external checker for the mean-constraint-match research program.

Project-original contribution under Unknown v0.3.
Authored by ChatGPT (OpenAI), submitted through Mingli Yuan's authorized
account proxy; account use is not personal authorship or verification.

Without --binary this is explicitly an ExternalSimulation, not Rust execution,
a native checkpoint, a semantic identity, or a native certificate. With
--binary, every checkpoint is independently replayed by `adva data-run --check`.
The fixed fixtures are evidence only for this finite contract.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
from fractions import Fraction
from typing import Any


PROGRAM_SCHEMA = "adva.data-machine.program.research.v0"
FUEL = 2048
CALL_LIMIT = 32
SECONDS_PER_CALL = 30
TOTAL_SECONDS = 120
MEMORY_BYTES = 256 * 1024 * 1024
FILE_BYTES = 2 * 1024 * 1024
TOTAL_BYTES = 32 * 1024 * 1024
I64_MIN, I64_MAX = -(2**63), 2**63 - 1


class Refused(ValueError):
    """A malformed input/program or a rejected simulated instruction."""


class BudgetExhausted(RuntimeError):
    """No automatic continuation is permitted."""


def integer(value: int) -> dict[str, Any]:
    return {"kind": "integer", "value": value}


def node(tag: int, *fields: dict[str, Any]) -> dict[str, Any]:
    return {"kind": "node", "tag": tag, "fields": list(fields)}


def request(n: int, k: int, a: int, b: int) -> dict[str, Any]:
    return node(0, *(integer(v) for v in (n, k, a, b)))


def exact_int(value: Any, lower: int = I64_MIN, upper: int = I64_MAX) -> bool:
    return type(value) is int and lower <= value <= upper


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise Refused(reason)


def data_size(value: Any) -> int:
    """Strict wire-shape gate; Python bool is deliberately not an integer."""
    pending = [(value, 1)]
    count = 0
    while pending:
        item, depth = pending.pop()
        count += 1
        require(count <= 127 and depth <= 12, "data capacity exceeded")
        require(type(item) is dict, "data must be an object")
        if item.get("kind") == "integer":
            require(set(item) == {"kind", "value"}, "invalid integer data fields")
            require(exact_int(item["value"]), "invalid i64 data value")
        elif item.get("kind") == "node":
            require(set(item) == {"kind", "tag", "fields"}, "invalid node data fields")
            require(exact_int(item["tag"], 0, 255), "invalid node tag")
            require(type(item["fields"]) is list and len(item["fields"]) <= 8,
                    "invalid node fields")
            pending.extend((child, depth + 1) for child in item["fields"])
        else:
            raise Refused("unknown data kind")
    return count


def validate_program(program: Any) -> None:
    """Validate only the declared finite opcode subset, without native authority."""
    require(type(program) is dict and set(program) == {"schema", "name", "registers", "code"},
            "invalid program fields")
    require(program["schema"] == PROGRAM_SCHEMA, "unsupported program schema")
    require(type(program["name"]) is str and 0 < len(program["name"].encode()) <= 64,
            "invalid program name")
    registers, code = program["registers"], program["code"]
    require(type(registers) is list and 1 <= len(registers) <= 16, "register capacity exceeded")
    require(type(code) is list and 1 <= len(code) <= 128, "code capacity exceeded")
    names: set[str] = set()
    for reg in registers:
        require(type(reg) is dict and set(reg) == {"name", "kind"}, "invalid register")
        name = reg["name"]
        require(type(name) is str and 0 < len(name) <= 32 and name.isascii()
                and all(c.isalnum() or c == "_" for c in name) and name not in names,
                "invalid or duplicate register name")
        require(reg["kind"] in {"integer", "boolean", "data"}, "unsupported register type")
        names.add(name)

    def reg(index: Any, kind: str | None = None) -> str:
        require(exact_int(index, 0, len(registers) - 1), "invalid register index")
        actual = registers[index]["kind"]
        require(kind is None or kind == actual, "register type mismatch")
        return actual

    def target(index: Any) -> None:
        require(exact_int(index, 0, len(code) - 1), "jump outside program")

    fields_by_op = {
        "input": {"dst"}, "constant": {"dst", "value"}, "copy": {"src", "dst"},
        "tag": {"src", "dst"}, "field": {"src", "arity", "index", "dst"},
        "as_integer": {"src", "dst"}, "box_integer": {"src", "dst"},
        "node": {"tag", "fields", "dst"}, "add": {"left", "right", "dst"},
        "multiply": {"left", "right", "dst"}, "equal": {"left", "right", "dst"},
        "jump": {"target"}, "branch": {"condition", "yes", "no"},
        "return": {"src"}, "reject": {"reason"},
    }
    for ins in code:
        require(type(ins) is dict and ins.get("op") in fields_by_op, "unsupported opcode")
        op = ins["op"]
        require(set(ins) == fields_by_op[op] | {"op"}, "invalid instruction fields")
        if op == "input":
            reg(ins["dst"], "data")
        elif op == "constant":
            reg(ins["dst"], "integer")
            require(exact_int(ins["value"]), "invalid i64 constant")
        elif op == "copy":
            reg(ins["dst"], reg(ins["src"]))
        elif op in {"tag", "as_integer", "box_integer"}:
            reg(ins["src"], "integer" if op == "box_integer" else "data")
            reg(ins["dst"], "data" if op == "box_integer" else "integer")
        elif op == "field":
            reg(ins["src"], "data")
            reg(ins["dst"], "data")
            require(exact_int(ins["arity"], 1, 8)
                    and exact_int(ins["index"], 0, ins["arity"] - 1), "invalid field shape")
        elif op == "node":
            reg(ins["dst"], "data")
            require(exact_int(ins["tag"], 0, 255), "invalid node tag")
            require(type(ins["fields"]) is list and len(ins["fields"]) <= 8,
                    "node arity exceeds 8")
            for index in ins["fields"]:
                reg(index, "data")
        elif op in {"add", "multiply", "equal"}:
            reg(ins["left"], "integer")
            reg(ins["right"], "integer")
            reg(ins["dst"], "boolean" if op == "equal" else "integer")
        elif op == "jump":
            target(ins["target"])
        elif op == "branch":
            reg(ins["condition"], "boolean")
            target(ins["yes"])
            target(ins["no"])
        elif op == "return":
            reg(ins["src"], "data")
        else:
            require(type(ins["reason"]) is str and 0 < len(ins["reason"].encode()) <= 128,
                    "invalid rejection reason")
    require(code[-1]["op"] in {"return", "reject", "jump", "branch"},
            "program can fall off its last instruction")


def fixtures() -> list[tuple[str, Any]]:
    """Fixed before execution; no search, adaptive retries, or scope widening."""
    return [
        ("primary", request(3, 1, 1, 2)),
        ("fresh", request(5, 2, 2, 3)),
        ("unreduced", request(3, 1, 2, 4)),
        ("simple-nonmatch", request(3, 1, 1, 3)),
        ("boundary-match", request(2, 1, 1, 1)),
        ("boundary-optimum-nonmatch", request(3, 2, 1, 1)),
        ("full-support", request(1, 1, 1, 1)),
        ("maximum-admissible", request(6, 6, 8, 8)),
        ("negative-n", request(-1, 1, 1, 2)),
        ("zero-a", request(3, 1, 0, 2)),
        ("domain-equality-false-positive", request(3, 2, 2, 1)),
        ("n-over-cap", request(7, 1, 1, 6)),
        ("b-over-cap", request(3, 1, 1, 9)),
        ("boolean-is-not-integer", node(0, integer(True), integer(1), integer(1), integer(2))),
        ("unknown-data-schema", {"kind": "tuple", "fields": []}),
        ("wrong-arity", node(0, integer(3), integer(1), integer(1))),
    ]


def oracle(value: Any) -> dict[str, Any]:
    """Independent subset enumeration, separate from the program's closed forms."""
    try:
        data_size(value)
    except Refused as exc:
        return {"status": "InputRejected", "reason": str(exc)}
    if value.get("kind") != "node" or value["tag"] != 0 or len(value["fields"]) != 4:
        return {"status": "Rejected", "reason": "wrong request shape"}
    if any(field["kind"] != "integer" for field in value["fields"]):
        return {"status": "Rejected", "reason": "request fields must be integer data"}
    n, k, a, b = (field["value"] for field in value["fields"])
    if not (1 <= k <= n <= 6 and 1 <= a <= b <= 8):
        return {"status": "Rejected", "reason": "outside finite arithmetic domain"}
    # At most 64 subsets: use their literal weights, not the binomial moment
    # identities implemented by the candidate program.
    weighted_subsets = [(mask.bit_count(), a**mask.bit_count() * b**(n - mask.bit_count()))
                        for mask in range(1 << n)]
    total_weight = sum(weight for _, weight in weighted_subsets)
    mean_ratio = sum((Fraction(j, k) * weight for j, weight in weighted_subsets), Fraction(0)) / total_weight
    second_moment = sum((Fraction(j, k)**2 * weight for j, weight in weighted_subsets), Fraction(0)) / total_weight
    variance_ratio = second_moment - mean_ratio**2
    omitted_weight = sum(weight for j, weight in weighted_subsets if j > k)
    match, full = int(mean_ratio == 1), int(omitted_weight == 0)
    gap_witness = a**n if k < n else 0
    z_numerator = (a + b)**n
    require(Fraction(n * a, k * (a + b)) == mean_ratio,
            "closed mean pair disagrees with independent subset enumeration")
    require(Fraction(n * a * b, k * k * (a + b)**2) == variance_ratio,
            "closed variance pair disagrees with independent subset enumeration")
    require(z_numerator == total_weight and full == int(k == n)
            and 0 <= gap_witness <= omitted_weight,
            "coverage witness disagrees with independent subset enumeration")
    output = node(0,
                  node(1, integer(n * a), integer(k * (a + b))),
                  node(2, integer(n * a * b), integer(k * k * (a + b)**2)),
                  node(3, node(4, integer(match), integer(full)),
                       integer(gap_witness), integer(z_numerator)))
    return {"status": "Returned", "value": output,
            "independent_arithmetic": {
                "mean_ratio": str(mean_ratio), "variance_ratio": str(variance_ratio),
                "oracle": "Exact Fraction moments over every finite subset",
                "enumerated_subsets": len(weighted_subsets), "second_moment": str(second_moment),
                "enumerated_total_weight": total_weight,
                "match_residual": n * a - k * (a + b),
                "mean_constraint_match": bool(match), "full_coverage": bool(full),
                "omitted_full_support_probability_lower_bound": str(Fraction(gap_witness, z_numerator)),
                "gap_scope": "One omitted full-support term when k<n; not complete tail mass",
            }}


def simulate(program: dict[str, Any], value: Any, deadline: float) -> dict[str, Any]:
    """Small integer VM: no native digests, certificates, identities, or profiles."""
    try:
        data_size(value)
    except Refused as exc:
        return {"schema": "adva.mean-match.external-simulation.v0", "execution": "ExternalSimulation",
                "status": "InputRejected", "reason": str(exc), "steps": 0}
    state: dict[str, Any] = {"pc": 0, "registers": [None] * len(program["registers"]),
                             "spent": 0, "phase": {"kind": "running"}}
    trace: list[dict[str, int]] = []

    def get(current: dict[str, Any], index: int, kind: str | None = None) -> Any:
        item = current["registers"][index]
        require(item is not None, "uninitialized register")
        require(kind is None or item["kind"] == kind, "unexpected register value type")
        return item if kind is None else item["value"]

    for _ in range(FUEL):
        if time.monotonic() >= deadline:
            return {"schema": "adva.mean-match.external-simulation.v0", "execution": "ExternalSimulation",
                    "status": "Unknown", "reason": "wall-time budget exhausted", "state": state,
                    "trace": trace, "steps": state["spent"]}
        if state["phase"]["kind"] != "running":
            break
        pc = state["pc"]
        require(0 <= pc < len(program["code"]), "program counter outside code")
        ins = program["code"][pc]
        op = ins["op"]
        nxt = copy.deepcopy(state)
        nxt["pc"] += 1

        def put(kind: str, item: Any) -> None:
            nxt["registers"][ins["dst"]] = {"kind": kind, "value": copy.deepcopy(item)}

        try:
            if op == "input":
                put("data", value)
            elif op == "constant":
                put("integer", ins["value"])
            elif op == "copy":
                nxt["registers"][ins["dst"]] = copy.deepcopy(get(nxt, ins["src"]))
            elif op == "tag":
                src = get(nxt, ins["src"], "data")
                put("integer", src["tag"] if src["kind"] == "node" else -1)
            elif op == "field":
                src = get(nxt, ins["src"], "data")
                require(src["kind"] == "node" and len(src["fields"]) == ins["arity"],
                        "data shape mismatch")
                put("data", src["fields"][ins["index"]])
            elif op == "as_integer":
                src = get(nxt, ins["src"], "data")
                require(src["kind"] == "integer", "expected integer data")
                put("integer", src["value"])
            elif op == "box_integer":
                put("data", integer(get(nxt, ins["src"], "integer")))
            elif op == "node":
                built = node(ins["tag"], *(get(nxt, r, "data") for r in ins["fields"]))
                data_size(built)
                put("data", built)
            elif op in {"add", "multiply", "equal"}:
                left, right = get(nxt, ins["left"], "integer"), get(nxt, ins["right"], "integer")
                if op == "equal":
                    put("boolean", left == right)
                else:
                    result = left + right if op == "add" else left * right
                    require(exact_int(result), "integer overflow")
                    put("integer", result)
            elif op == "jump":
                nxt["pc"] = ins["target"]
            elif op == "branch":
                nxt["pc"] = ins["yes"] if get(nxt, ins["condition"], "boolean") else ins["no"]
            elif op == "return":
                nxt["phase"] = {"kind": "returned", "value": copy.deepcopy(get(nxt, ins["src"], "data"))}
            elif op == "reject":
                raise Refused(ins["reason"])
            else:
                raise Refused("unsupported opcode")
            nodes = sum(data_size(item["value"]) if item["kind"] == "data" else 1
                        for item in nxt["registers"] if item is not None)
            if nxt["phase"]["kind"] == "returned":
                nodes += data_size(nxt["phase"]["value"])
            require(nodes <= 8192, "state capacity exceeded")
        except Refused as exc:
            nxt = copy.deepcopy(state)
            nxt["phase"] = {"kind": "rejected", "reason": str(exc)}
        nxt["spent"] += 1
        trace.append({"pc": pc, "next_pc": nxt["pc"]})
        state = nxt
    status = {"returned": "Returned", "rejected": "Rejected", "running": "FuelExhausted"}[state["phase"]["kind"]]
    return {"schema": "adva.mean-match.external-simulation.v0", "execution": "ExternalSimulation",
            "status": status, "state": state, "trace": trace, "steps": state["spent"]}


def write_json(path: Path, value: Any) -> None:
    payload = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode()
    if len(payload) > FILE_BYTES:
        raise BudgetExhausted("single artifact byte limit exceeded")
    with path.open("xb") as stream:
        stream.write(payload)


def peak_rss_kib(who: int) -> int:
    measured = resource.getrusage(who).ru_maxrss
    return int(measured / 1024) if sys.platform == "darwin" else int(measured)


def install_memory_limit() -> None:
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    cap = MEMORY_BYTES if hard == resource.RLIM_INFINITY else min(MEMORY_BYTES, hard)
    if soft != resource.RLIM_INFINITY:
        cap = min(cap, soft)
    resource.setrlimit(resource.RLIMIT_AS, (cap, hard))


def child_limits() -> None:
    install_memory_limit()
    resource.setrlimit(resource.RLIMIT_FSIZE, (FILE_BYTES, FILE_BYTES))
    resource.setrlimit(resource.RLIMIT_CPU, (SECONDS_PER_CALL, SECONDS_PER_CALL))


class Runner:
    def __init__(self, output: Path, program_path: Path, program: dict[str, Any], binary: str | None):
        self.output, self.program_path, self.program, self.binary = output, program_path, program, binary
        self.started = time.monotonic()
        self.deadline = self.started + TOTAL_SECONDS
        self.calls = 0
        self.costs: list[dict[str, Any]] = []

    def allowance(self) -> float:
        if self.calls >= CALL_LIMIT:
            raise BudgetExhausted("call limit exhausted")
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise BudgetExhausted("total wall-time limit exhausted")
        # Reserve one run's raw streams/report plus the final retained summary.
        if sum(p.stat().st_size for p in self.output.iterdir() if p.is_file()) + 4 * FILE_BYTES > TOTAL_BYTES:
            raise BudgetExhausted("total artifact byte limit exhausted")
        self.calls += 1
        return min(SECONDS_PER_CALL, remaining)

    def external(self, name: str, value: Any) -> tuple[dict[str, Any], dict[str, Any]]:
        limit = self.allowance()
        started = time.monotonic()
        result = simulate(self.program, value, started + limit)
        cost = {"call": self.calls, "label": name, "kind": "ExternalSimulation",
                "elapsed_seconds": time.monotonic() - started, "steps": result["steps"],
                "peak_rss_kib": peak_rss_kib(resource.RUSAGE_SELF), "native_calls": 0}
        self.costs.append(cost)
        write_json(self.output / f"{name}.simulation.json", result)
        write_json(self.output / f"{name}.cost.json", cost)
        return result, cost

    def native(self, name: str, input_path: Path, checkpoint: Path | None = None) -> tuple[Any, dict[str, Any]]:
        limit = self.allowance()
        result_path = self.output / f"{name}.adva"
        argv = [self.binary, "data-run", str(self.program_path), "--input", str(input_path),
                "--fuel", str(FUEL), "--quantum", "0" if checkpoint else str(FUEL),
                "--output", str(result_path)]
        if checkpoint is not None:
            argv.extend(["--check", str(checkpoint)])
        started = time.monotonic()
        timed_out = False
        error = None
        returncode = None
        with (self.output / f"{name}.stdout.txt").open("xb") as stdout, \
                (self.output / f"{name}.stderr.txt").open("xb") as stderr:
            try:
                proc = subprocess.Popen(argv, stdout=stdout, stderr=stderr,
                                        start_new_session=True, preexec_fn=child_limits)
                try:
                    returncode = proc.wait(timeout=limit)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    os.killpg(proc.pid, signal.SIGKILL)
                    returncode = proc.wait()
            except OSError as exc:
                error = str(exc)
        result = None
        if result_path.exists():
            try:
                require(result_path.stat().st_size <= FILE_BYTES, "native report exceeds byte limit")
                result = json.loads(result_path.read_text())
            except (ValueError, OSError) as exc:
                error = f"cannot parse retained native report: {exc}"
        cost = {"call": self.calls, "label": name, "kind": "RustDataRunCheck" if checkpoint else "RustDataRun",
                "argv": argv, "returncode": returncode, "timed_out": timed_out, "error": error,
                "elapsed_seconds": time.monotonic() - started,
                "children_cumulative_peak_rss_kib": peak_rss_kib(resource.RUSAGE_CHILDREN),
                "report_path": result_path.name if result_path.exists() else None}
        if isinstance(result, dict):
            cost["steps"] = result.get("verified_steps", result.get("state", {}).get("spent"))
        self.costs.append(cost)
        write_json(self.output / f"{name}.cost.json", cost)
        return result, cost


def observed(result: Any, cost: dict[str, Any], expected_status: str, native: bool) -> tuple[str, Any]:
    if cost.get("timed_out"):
        return "Unknown", None
    if cost.get("error"):
        return "ExecutionFailure", None
    if not isinstance(result, dict):
        if native and expected_status == "InputRejected" and cost.get("returncode") not in {None, 0}:
            return "InputRejected", None
        return "ExecutionFailure", None
    status = result.get("status", "ExecutionFailure")
    if native:
        if result.get("schema") != "adva.data-machine.run.research.v0":
            return "ExecutionFailure", None
        if status == "Returned" and cost.get("returncode") != 0:
            return "ExecutionFailure", None
        if status == "Rejected" and cost.get("returncode") in {None, 0}:
            return "ExecutionFailure", None
    value = result.get("state", {}).get("phase", {}).get("value") if status == "Returned" else None
    return status, value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="new evidence directory; never overwrite")
    parser.add_argument("--binary", help="existing adva executable; absent means ExternalSimulation")
    parser.add_argument("--program", type=Path, default=Path(__file__).with_name("mean-constraint-match.adva"))
    args = parser.parse_args()
    if args.output.exists():
        parser.error("--output must be a new directory; previous evidence is retained")
    args.output.mkdir(parents=True, exist_ok=False)
    output = args.output.resolve()
    rows: list[dict[str, Any]] = []
    runner: Runner | None = None
    conclusion = "Unknown"
    failure = None
    program_bytes = b""
    started = time.monotonic()
    try:
        install_memory_limit()
        require(args.program.stat().st_size <= 32768, "program exceeds 32768 bytes")
        program_bytes = args.program.read_bytes()
        program = json.loads(program_bytes)
        validate_program(program)
        cases = fixtures()
        require(len(cases) <= 16, "fixture limit exceeded")
        # Bind execution to retained bytes so concurrent source edits cannot change a run.
        program_path = output / "program.adva"
        with program_path.open("xb") as stream:
            stream.write(program_bytes)
        binary = str(Path(args.binary).resolve()) if args.binary else None
        if binary is not None:
            require(Path(binary).is_file() and os.access(binary, os.X_OK), "binary is not executable")
        runner = Runner(output, program_path, program, binary)
        runner.started, runner.deadline = started, started + TOTAL_SECONDS
        contract = {
            "schema": "adva.mean-match.finite-check-contract.v0",
            "authorship": "ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy",
            "contribution": "Project-original under Unknown v0.3; account use is not personal verification",
            "question": "Does the fixed program match independently enumerated subset moments and reject the declared invalid fixtures?",
            "level": "Research data-machine program; arithmetic meanings interpreted externally",
            "execution": "RustDataRunWithIndependentReplay" if binary else "ExternalSimulation",
            "domain": "integer 1<=k<=n<=6 and 1<=a<=b<=8; booleans excluded",
            "program_sha256": hashlib.sha256(program_bytes).hexdigest(),
            "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "fixture_order": [name for name, _ in cases],
            "fixtures": [{"id": name, "input": value, "expected": oracle(value)} for name, value in cases],
            "limits": {"fixtures": 16, "calls_including_replay": CALL_LIMIT, "steps_per_call": FUEL,
                       "seconds_per_call": SECONDS_PER_CALL, "total_seconds": TOTAL_SECONDS,
                       "bytes_per_process_address_space": MEMORY_BYTES,
                       "maximum_concurrent_processes": 2, "bytes_per_artifact": FILE_BYTES,
                       "total_artifact_bytes": TOTAL_BYTES, "continuations": 0},
            "enforcement": "Fixed fixtures; fuel; monotonic deadlines; subprocess timeout/process-group kill; RLIMIT_AS/FSIZE/CPU; artifact size checks",
            "protected_obligations": ["Integer domain precedes matching", "No bool-as-int coercion",
                                      "Coverage and mean match are separate", "Gap witness is only one omitted term",
                                      "Every retained Rust checkpoint receives a separate --check call",
                                      "Malformed wire input has no checkpoint and is not replayable"],
            "residuals": ["No physical energy claim", "The program's gap output is not full tail mass",
                          "No general theorem from fixtures", "External simulation is not native execution",
                          "No stable semantic operations or native identity authority added"],
        }
        write_json(output / "contract.json", contract)
        for name, value in cases:
            expected = oracle(value)
            input_path = output / f"{name}.input.json"
            write_json(input_path, value)
            if binary:
                result, cost = runner.native(f"{name}.run", input_path)
            else:
                result, cost = runner.external(f"{name}.run", value)
            status, actual_value = observed(result, cost, expected["status"], bool(binary))
            row = {"id": name, "expected_status": expected["status"], "observed_status": status,
                   "arithmetic_or_rejection_matches": status == expected["status"]
                   and (status != "Returned" or actual_value == expected["value"]),
                   "expected": expected, "execution_cost": cost}
            rows.append(row)
            if isinstance(result, dict) and status not in {"InputRejected", "ExecutionFailure", "Unknown"}:
                if binary:
                    checked, replay_cost = runner.native(f"{name}.check", input_path,
                                                         output / f"{name}.run.adva")
                    replay_ok = (isinstance(checked, dict) and replay_cost["returncode"] == 0
                                 and not replay_cost["timed_out"] and replay_cost["error"] is None
                                 and checked.get("state") == result.get("state")
                                 and checked.get("profile") == result.get("profile")
                                 and checked.get("verified_steps") == result.get("state", {}).get("spent"))
                    row["replay"] = {"kind": "IndependentRustCheck", "matches": replay_ok, "cost": replay_cost}
                else:
                    checked, replay_cost = runner.external(f"{name}.replay", value)
                    replay_ok = checked == result
                    row["replay"] = {"kind": "ExternalSimulationRepeat", "matches": replay_ok, "cost": replay_cost,
                                     "native_verification": False}
            else:
                replay_ok = status == "InputRejected" and row["arithmetic_or_rejection_matches"]
                row["replay"] = {"kind": "NotApplicable", "reason": "No valid execution checkpoint"}
            row["passed"] = row["arithmetic_or_rejection_matches"] and replay_ok
            write_json(output / f"{name}.comparison.json", row)
            if status in {"Unknown", "FuelExhausted", "Suspended"} or cost.get("timed_out"):
                raise BudgetExhausted(f"{name}: {status}")
            if not row["passed"]:
                conclusion, failure = "Failed", f"First mismatch retained: {name}"
                break
        else:
            conclusion = "Passed"
    except BudgetExhausted as exc:
        conclusion, failure = "Unknown", str(exc)
    except (Refused, ValueError, OSError, MemoryError, subprocess.SubprocessError) as exc:
        conclusion, failure = "Failed", f"{type(exc).__name__}: {exc}"
    report = {
        "schema": "adva.mean-match.finite-check-result.v0", "status": conclusion,
        "execution": "RustDataRunWithIndependentReplay" if args.binary else "ExternalSimulation",
        "native_verification": bool(args.binary) and conclusion == "Passed",
        "failure": failure, "completed_fixtures": len(rows), "rows": rows,
        "program_sha256": hashlib.sha256(program_bytes).hexdigest() if program_bytes else None,
        "cost": {"calls_including_replay": runner.calls if runner else 0,
                 "native_calls": runner.calls if runner and args.binary else 0,
                 "elapsed_seconds": time.monotonic() - started,
                 "self_peak_rss_kib": peak_rss_kib(resource.RUSAGE_SELF),
                 "children_cumulative_peak_rss_kib": peak_rss_kib(resource.RUSAGE_CHILDREN),
                 "calls": runner.costs if runner else []},
        "residuals": ["Finite fixture evidence only", "Gap witness is not full omitted tail mass",
                      "ExternalSimulation cannot establish native execution or native certificates"],
        "authorship": "ChatGPT (OpenAI), authorized account proxy; Unknown v0.3",
    }
    try:
        write_json(output / "result.json", report)
    except (OSError, BudgetExhausted, MemoryError) as exc:
        print(f"Could not retain final result: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"status": conclusion, "execution": report["execution"],
                      "completed_fixtures": len(rows), "result": str(output / "result.json")}))
    return 0 if conclusion == "Passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
