#!/usr/bin/env python3
"""Bounded self-interpretation capacity preflight.

Two things are measured, both finite and both declared in `contract.json`:

1. Counting. The unchanged 51-instruction object interpreter is encoded under one
   declared scheme, and the exact node total is compared with the profile's declared
   data bound. No execution is claimed for the counting part.
2. Execution. Deterministic generated programs exercise the declared bounds through
   the unchanged `adva data-run` entry: the node, depth and arity bounds at admission,
   the instruction cost of an opcode dispatch ladder, and the cost of a data-driven
   index step against a static index ladder.

This launches no search and no research campaign, changes no machine byte, and widens
no bound. Refusals are expected outcomes here and are retained with their stderr.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from collections import deque

# Declared profile bounds, copied from crates/adva-witness/src/data_machine.rs.
LIMITS = {
    "program_instructions": 128,
    "registers": 16,
    "data_nodes": 127,
    "data_depth": 12,
    "node_arity": 8,
    "stack_items": 256,
    "state_nodes": 8192,
    "lifetime_fuel": 2048,
    "program_bytes": 32768,
}

# Operand fields that are numeric register indices or declared immediates. `node`'s
# field list and `reject`'s string reason are handled separately.
OPERANDS = {
    "input": ("dst",),
    "constant": ("dst", "value"),
    "copy": ("src", "dst"),
    "clear": ("stack",),
    "push": ("stack", "src"),
    "pop": ("stack", "dst"),
    "is_empty": ("stack", "dst"),
    "tag": ("src", "dst"),
    "field": ("src", "arity", "index", "dst"),
    "as_integer": ("src", "dst"),
    "box_integer": ("src", "dst"),
    "node": ("dst",),
    "add": ("left", "right", "dst"),
    "multiply": ("left", "right", "dst"),
    "equal": ("left", "right", "dst"),
    "jump": ("target",),
    "branch": ("condition", "yes", "no"),
    "return": ("src",),
    "reject": (),
}

# Instructions whose operand vocabulary includes something a finite tree of integers
# cannot carry.
TEXT_OPERANDS = {"reject": ("reason",)}

MAX_LAUNCHES = 24


def count_encoding(program: dict) -> dict:
    """Exact node totals of the two declared encoding schemes for one object program."""
    code = program["code"]
    per_op: dict[str, int] = {}
    operand_leaves = 0
    text_operands = 0
    for instruction in code:
        op = instruction["op"]
        per_op[op] = per_op.get(op, 0) + 1
        operand_leaves += len(OPERANDS[op])
        if op == "node":
            operand_leaves += len(instruction.get("fields", []))
        text_operands += len(TEXT_OPERANDS.get(op, ()))
    instructions = len(code)
    groups = -(-instructions // LIMITS["node_arity"])
    direct = {
        "scheme": "one node per instruction, one node spine of groups, one integer leaf per numeric operand",
        "nodes": 1 + groups + instructions + operand_leaves,
        "depth": 4,
        "group_nodes": groups,
        "instruction_nodes": instructions,
        "operand_leaves": operand_leaves,
        "per_op": dict(sorted(per_op.items())),
        "instructions_with_text_operands": text_operands,
    }
    packed = {
        "scheme": "one node per instruction with all numeric operands packed into one integer leaf",
        "nodes": 1 + groups + 2 * instructions,
        "depth": 4,
        "decodable_in_language": False,
        "why_not": "unpacking base-N operands needs integer division, modulo or a bit operation; the declared vocabulary has add, multiply, equal and comparison-free control only",
    }
    for entry in (direct, packed):
        entry["within_node_bound"] = entry["nodes"] <= LIMITS["data_nodes"]
        entry["within_depth_bound"] = entry["depth"] <= LIMITS["data_depth"]
    return {"instructions": instructions, "direct": direct, "packed": packed}


def tree_exact(nodes: int, arity: int = 8, max_depth: int = 12) -> dict:
    """A depth-first-stable tree with exactly `nodes` values, within arity and depth."""
    root = {"kind": "node", "tag": 0, "fields": []}
    queue = deque([(root, 1)])
    total = 1
    while total < nodes:
        parent, depth = queue.popleft()
        if depth >= max_depth or len(parent["fields"]) >= arity:
            continue
        child = {"kind": "node", "tag": 0, "fields": []}
        parent["fields"].append(child)
        total += 1
        queue.append((child, depth + 1))
        if len(parent["fields"]) < arity:
            queue.append((parent, depth))
        if not queue:
            raise SystemExit("cannot build the requested tree inside arity and depth")
    return root


def tree_chain(depth: int) -> dict:
    node: dict = {"kind": "node", "tag": 0, "fields": [{"kind": "integer", "value": 0}]}
    for _ in range(depth - 1):
        node = {"kind": "node", "tag": 0, "fields": [node]}
    return node


def tree_wide(arity: int) -> dict:
    return {
        "kind": "node",
        "tag": 0,
        "fields": [{"kind": "integer", "value": i} for i in range(arity)],
    }


def count_nodes(value: dict) -> int:
    if value["kind"] == "integer":
        return 1
    return 1 + sum(count_nodes(field) for field in value["fields"])


def program(name: str, registers: list[tuple[str, str]], code: list[dict]) -> dict:
    return {
        "schema": "adva.data-machine.program.research.v0",
        "name": name,
        "registers": [{"name": n, "kind": k} for n, k in registers],
        "code": code,
    }


def identity_program() -> dict:
    return program("capacity-identity", [("item", "data")],
                   [{"op": "input", "dst": 0}, {"op": "return", "src": 0}])


def dispatch_program(name: str, tags: list[int], base: int, fallback: int) -> dict:
    """A linear opcode ladder: no ordering comparison exists, so equality ladders only."""
    registers = [("item", "data"), ("tag", "integer"), ("probe", "integer"),
                 ("test", "boolean"), ("result", "integer"), ("boxed", "data")]
    code: list[dict] = [{"op": "input", "dst": 0}, {"op": "as_integer", "src": 0, "dst": 1}]
    exits = []
    for index, tag in enumerate(tags):
        code.append({"op": "constant", "dst": 2, "value": tag})
        code.append({"op": "equal", "left": 1, "right": 2, "dst": 3})
        branch_at = len(code)
        code.append({"op": "branch", "condition": 3, "yes": 0, "no": 0})
        yes_at = len(code)
        code.append({"op": "constant", "dst": 4, "value": base + index})
        jump_at = len(code)
        code.append({"op": "jump", "target": 0})
        code[branch_at]["yes"] = yes_at
        code[branch_at]["no"] = len(code)
        exits.append(jump_at)
    code.append({"op": "constant", "dst": 4, "value": fallback})
    exit_at = len(code)
    code.append({"op": "box_integer", "src": 4, "dst": 5})
    code.append({"op": "return", "src": 5})
    for jump_at in exits:
        code[jump_at]["target"] = exit_at
    return program(name, registers, code)


def index_step_program() -> dict:
    """One data-driven index iteration: compare, branch, increment, jump."""
    registers = [("item", "data"), ("count", "integer"), ("one", "integer"),
                 ("counter", "integer"), ("test", "boolean"), ("boxed", "data")]
    code = [
        {"op": "input", "dst": 0},
        {"op": "as_integer", "src": 0, "dst": 1},
        {"op": "constant", "dst": 2, "value": 1},
        {"op": "constant", "dst": 3, "value": 0},
        {"op": "equal", "left": 3, "right": 1, "dst": 4},
        {"op": "branch", "condition": 4, "yes": 8, "no": 6},
        {"op": "add", "left": 3, "right": 2, "dst": 3},
        {"op": "jump", "target": 4},
        {"op": "box_integer", "src": 1, "dst": 5},
        {"op": "return", "src": 5},
    ]
    return program("capacity-index-step", registers, code)


class Runner:
    def __init__(self, binary: str, workdir: pathlib.Path):
        self.binary = binary
        self.workdir = workdir
        self.launches = 0

    def run(self, name: str, prog: dict, data: dict, fuel: int = 2048, quantum: int = 2048) -> dict:
        if self.launches >= MAX_LAUNCHES:
            raise SystemExit(f"launch budget of {MAX_LAUNCHES} exhausted before {name}")
        self.launches += 1
        program_path = self.workdir / "programs" / f"{name}.adva"
        input_path = self.workdir / "inputs" / f"{name}.json"
        output_path = self.workdir / "runs" / f"{name}.run.adva"
        program_path.parent.mkdir(parents=True, exist_ok=True)
        input_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        program_path.write_text(json.dumps(prog, indent=2) + "\n")
        input_path.write_text(json.dumps(data, indent=2) + "\n")
        done = subprocess.run(
            [self.binary, "data-run", str(program_path), "--input", str(input_path),
             "--fuel", str(fuel), "--quantum", str(quantum), "--output", str(output_path)],
            check=False, capture_output=True, text=True, timeout=20,
        )
        (self.workdir / "runs" / f"{name}.stderr.txt").write_text(done.stderr)
        observed = {"name": name, "exit_code": done.returncode, "stdout": done.stdout.strip(),
                    "stderr": done.stderr.strip().splitlines()[0] if done.stderr.strip() else ""}
        if output_path.exists():
            record = json.loads(output_path.read_text())
            observed["status"] = record["status"]
            observed["steps"] = len(record["trace"])
            observed["returned_value"] = returned_value(record)
            observed["input_nodes"] = count_nodes(record["input"])
        return observed


def returned_value(record: dict) -> dict | None:
    phase = record["state"].get("phase", {})
    if phase.get("kind") == "returned":
        return phase.get("value")
    return None


def as_integer(value: dict | None) -> int | None:
    if value is None or value.get("kind") != "integer":
        return None
    return value["value"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--binary", required=True)
    parser.add_argument("--object-program", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    out = pathlib.Path(args.output)
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"{out} already holds a retained attempt; choose a new directory")
    out.mkdir(parents=True, exist_ok=True)

    object_program = json.loads(pathlib.Path(args.object_program).read_text())
    counting = count_encoding(object_program)
    (out / "encoding-count.json").write_text(json.dumps(counting, indent=2) + "\n")

    runner = Runner(args.binary, out)
    cases: list[dict] = []

    # Declared bound at admission: the accepted input must sit exactly one node below
    # the first refusal, and both refusals must name the bound they hit.
    identity = identity_program()
    for name, data, expect in (
        ("input-127-nodes", tree_exact(127), "accepted"),
        ("input-128-nodes", tree_exact(128), "data capacity exceeded"),
        ("input-depth-13", tree_chain(13), "data capacity exceeded"),
        ("input-arity-9", tree_wide(9), "node arity exceeds 8"),
    ):
        observed = runner.run(name, identity, data)
        observed["expected"] = expect
        cases.append(observed)

    # Opcode dispatch ladder: 17 cases, distinct declared values, one unmatched fallback.
    ladder = dispatch_program("capacity-dispatch-17", list(range(17)), base=100, fallback=999)
    ladder_instructions = len(ladder["code"])
    for name, tag, expect in (
        ("dispatch-tag-0", 0, 100), ("dispatch-tag-8", 8, 108),
        ("dispatch-tag-16", 16, 116), ("dispatch-tag-unmatched", 99, 999),
    ):
        observed = runner.run(name, ladder, {"kind": "integer", "value": tag})
        observed["expected"] = f"returned {expect}"
        observed["expected_value"] = expect
        cases.append(observed)

    # One data-driven index iteration, at three workloads.
    index = index_step_program()
    for name, count in (("index-step-0", 0), ("index-step-4", 4), ("index-step-8", 8)):
        observed = runner.run(name, index, {"kind": "integer", "value": count})
        observed["expected"] = f"returned {count}"
        observed["expected_value"] = count
        cases.append(observed)

    # The program-size alternative to the data-driven loop.
    static_ladder = dispatch_program("capacity-index-16", list(range(16)), base=200, fallback=-1)
    observed = runner.run("index-ladder-5", static_ladder, {"kind": "integer", "value": 5})
    observed["expected"] = "returned 205"
    observed["expected_value"] = 205
    cases.append(observed)

    failures = []
    for case in cases:
        expected = case["expected"]
        if expected == "accepted":
            if case.get("status") != "Returned" or case["exit_code"] != 0:
                failures.append(f"{case['name']}: expected an accepted return, saw {case}")
        elif expected.startswith("returned "):
            wanted = case.get("expected_value")
            if as_integer(case.get("returned_value")) != wanted or case.get("status") != "Returned":
                failures.append(f"{case['name']}: expected {wanted}, saw {case}")
        else:
            if case["exit_code"] == 0 or expected not in case["stderr"]:
                failures.append(f"{case['name']}: expected refusal '{expected}', saw {case}")

    deltas = {}
    for key, count in (("index-step-0", 0), ("index-step-4", 4), ("index-step-8", 8)):
        deltas[count] = next(c for c in cases if c["name"] == key).get("steps")
    dispatch_steps = {c["name"]: c.get("steps") for c in cases if c["name"].startswith("dispatch-")}

    summary = {
        "schema": "adva.self-interpretation-capacity.result.v0",
        "limits": LIMITS,
        "object_program": args.object_program,
        "launches": runner.launches,
        "counting": counting,
        "program_lengths": {
            "object_interpreter": counting["instructions"],
            "dispatch_ladder_17": ladder_instructions,
            "index_step_loop": len(index["code"]),
            "static_index_ladder_16": len(static_ladder["code"]),
        },
        "cases": cases,
        "index_step_counts": deltas,
        "dispatch_step_counts": dispatch_steps,
        "failures": failures,
        "verdict": "Passed" if not failures else "Failed",
    }
    (out / "results.json").write_text(json.dumps(summary, indent=2) + "\n")

    print(f"direct encoding nodes      : {counting['direct']['nodes']} "
          f"(bound {LIMITS['data_nodes']}, within={counting['direct']['within_node_bound']})")
    print(f"packed encoding nodes      : {counting['packed']['nodes']} "
          f"(within={counting['packed']['within_node_bound']}, decodable=False)")
    print(f"dispatch ladder 17 cases   : {ladder_instructions} instructions "
          f"(bound {LIMITS['program_instructions']})")
    print(f"static index ladder 16     : {len(static_ladder['code'])} instructions")
    print(f"index step steps at 0/4/8  : {deltas.get(0)}/{deltas.get(4)}/{deltas.get(8)}")
    print(f"dispatch steps             : {dispatch_steps}")
    print(f"launches                   : {runner.launches} (budget {MAX_LAUNCHES})")
    for case in cases:
        print(f"  {case['name']:24s} exit={case['exit_code']} "
              f"status={case.get('status', '-'):10s} steps={case.get('steps', '-')} "
              f"{('stderr=' + case['stderr'][:40]) if case['stderr'] else ''}")
    print(f"verdict                    : {summary['verdict']}")
    for failure in failures:
        print(f"  FAIL {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
