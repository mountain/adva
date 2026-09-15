#!/usr/bin/env python3
"""Bounded scaling preflight for a self-interpreter of the machine's own grammar.

The capacity preflight next door measured that the full instruction grammar has no
inspectable representation inside the declared node bound, and that a 17-case
dispatch ladder spends 90 of 128 instructions. This preflight asks the follow-up
question with execution instead of arithmetic: what does it actually cost to
interpret a *strict subset* of this machine's own instruction grammar inside the
same profile, and what would the full grammar therefore demand of each declared
bound?

A generated meta program receives an encoded object program as data and interprets
it. The object language is the declared subset: `input d`, `return s`,
`constant v d` and `copy s d`, with two object register slots and a fixed object
program length, because indexed access in this profile is static. The meta program
is a program in the same language as the objects it interprets.

Nothing here changes the machine, its profile, its bounds or the object interpreter.
Failures and refusals are declared outcomes and are retained with their stderr.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

MAX_LAUNCHES = 24
DECLARED_INSTRUCTIONS = 128
# prologue 3, one fetch 2, one dispatch 3, the per-block unsupported-opcode reject 1,
# and the terminal reject 1.
FIXED_OVERHEAD = 10
DISPATCH_PER_OPCODE = 3
BLOCK_OVERHEAD = 2  # one field fetch and one tag read per object instruction

# Object-language tags, its program/bundle tags, and its register slots.
TAG = {"input": 0, "return": 1, "constant": 3, "copy": 4}
OBJECT_PROGRAM_TAG = 2
BUNDLE_TAG = 5
SLOTS = (0, 1)

# Meta register file: bundle, program, objin, instr, r0, r1, tmp, opcode, operand,
# operand2, probe, test, boxed.
BUNDLE, PROGRAM, OBJIN, INSTR, R0, R1, TMP, FIELD = 0, 1, 2, 3, 4, 5, 6, 7
OPCODE, OPERAND, OPERAND2, PROBE = 8, 9, 10, 11
TEST, BOXED = 12, 13
REGISTERS = [
    ("bundle", "data"), ("program", "data"), ("objin", "data"), ("instr", "data"),
    ("r0", "data"), ("r1", "data"), ("tmp", "data"), ("field_value", "data"),
    ("opcode", "integer"), ("operand", "integer"), ("operand2", "integer"),
    ("probe", "integer"), ("test", "boolean"), ("boxed", "data"),
]


def program(name: str, code: list[dict]) -> dict:
    return {
        "schema": "adva.data-machine.program.research.v0",
        "name": name,
        "registers": [{"name": n, "kind": k} for n, k in REGISTERS],
        "code": code,
    }


def emit_operand(emit, code, *, arity: int, index: int, dst: int) -> None:
    """Extract one integer operand of the current instruction, keeping INSTR intact."""
    emit({"op": "field", "src": INSTR, "arity": arity, "index": index, "dst": FIELD})
    emit({"op": "as_integer", "src": FIELD, "dst": dst})


def compare_register(emit, register: int, value: int) -> int:
    emit({"op": "constant", "dst": PROBE, "value": value})
    emit({"op": "equal", "left": register, "right": PROBE, "dst": TEST})
    return emit({"op": "branch", "condition": TEST, "yes": 0, "no": 0})


def write_slot_ladder(emit, code, operand: int, source: int) -> list[int]:
    """Write `source` into object slot 0 or 1, selected by the integer `operand`."""
    jumps = []
    for slot in SLOTS:
        branch = compare_register(emit, operand, slot)
        code[branch]["yes"] = len(code)
        emit({"op": "copy", "src": source, "dst": R0 + slot})
        jumps.append(emit({"op": "jump", "target": 0}))
        code[branch]["no"] = len(code)
    emit({"op": "reject", "reason": "object register index out of range"})
    return jumps


def body_input(emit, code) -> list[int]:
    emit_operand(emit, code, arity=1, index=0, dst=OPERAND)
    return write_slot_ladder(emit, code, OPERAND, OBJIN)


def body_constant(emit, code) -> list[int]:
    emit_operand(emit, code, arity=2, index=0, dst=OPERAND)
    emit({"op": "box_integer", "src": OPERAND, "dst": BOXED})
    emit_operand(emit, code, arity=2, index=1, dst=OPERAND2)
    return write_slot_ladder(emit, code, OPERAND2, BOXED)


def body_copy(emit, code) -> list[int]:
    emit_operand(emit, code, arity=2, index=0, dst=OPERAND)
    read_jumps = []
    for slot in SLOTS:
        branch = compare_register(emit, OPERAND, slot)
        code[branch]["yes"] = len(code)
        emit({"op": "copy", "src": R0 + slot, "dst": TMP})
        read_jumps.append(emit({"op": "jump", "target": 0}))
        code[branch]["no"] = len(code)
    emit({"op": "reject", "reason": "object source register out of range"})
    read_done = len(code)
    for jump in read_jumps:
        code[jump]["target"] = read_done
    emit_operand(emit, code, arity=2, index=1, dst=OPERAND2)
    return write_slot_ladder(emit, code, OPERAND2, TMP)


def body_return(emit, code) -> list[int]:
    emit_operand(emit, code, arity=1, index=0, dst=OPERAND)
    for slot in SLOTS:
        branch = compare_register(emit, OPERAND, slot)
        code[branch]["yes"] = len(code)
        emit({"op": "return", "src": R0 + slot})
        code[branch]["no"] = len(code)
    emit({"op": "reject", "reason": "object return register out of range"})
    return []


BODIES = {"input": body_input, "return": body_return,
          "constant": body_constant, "copy": body_copy}

# A nineteenth-opcode ladder needs fifteen opcodes this preflight does not implement.
# They are charged the shortest measured body as declared placeholders, so the ladder's
# length is a lower bound: generating it measures the size, it does not interpret.
PLACEHOLDER_OPS = [f"unmeasured_{index}" for index in range(15)]
for _index, _op in enumerate(PLACEHOLDER_OPS):
    TAG[_op] = 10 + _index
    BODIES[_op] = body_return
FULL_GRAMMAR_ORDER = ["input", "constant", "copy", "return"] + PLACEHOLDER_OPS


def meta_program(ops: list[str], length: int) -> dict:
    """Generate a meta program that interprets object programs of `length` instructions."""
    code: list[dict] = []

    def emit(instruction: dict) -> int:
        code.append(instruction)
        return len(code) - 1

    emit({"op": "input", "dst": BUNDLE})
    emit({"op": "field", "src": BUNDLE, "arity": 2, "index": 0, "dst": PROGRAM})
    emit({"op": "field", "src": BUNDLE, "arity": 2, "index": 1, "dst": OBJIN})
    entries: list[int] = []
    pending: list[list[int]] = []
    for index in range(length):
        entries.append(len(code))
        emit({"op": "field", "src": PROGRAM, "arity": length, "index": index, "dst": INSTR})
        emit({"op": "tag", "src": INSTR, "dst": OPCODE})
        jumps: list[int] = []
        for op in ops:
            emit({"op": "constant", "dst": PROBE, "value": TAG[op]})
            emit({"op": "equal", "left": OPCODE, "right": PROBE, "dst": TEST})
            branch = emit({"op": "branch", "condition": TEST, "yes": 0, "no": 0})
            code[branch]["yes"] = len(code)
            jumps.extend(BODIES[op](emit, code))
            code[branch]["no"] = len(code)
        emit({"op": "reject", "reason": "unsupported object opcode"})
        pending.append(jumps)
    end = len(code)
    emit({"op": "reject", "reason": "object program fell off its end"})
    for index, jumps in enumerate(pending):
        target = entries[index + 1] if index + 1 < length else end
        for jump in jumps:
            code[jump]["target"] = target
    return program(f"meta-{'-'.join(ops)}-{length}", code)


def body_lengths() -> dict[str, int]:
    """Measured length of each opcode body, taken from generated programs."""
    lengths = {}
    for op in BODIES:
        one = meta_program([op], 1)["code"]
        lengths[op] = len(one) - FIXED_OVERHEAD
    return lengths


def reconstructed_length(ops: list[str], length: int, bodies: dict[str, int]) -> int:
    """The length model: fixed overhead once, then one block per object instruction."""
    per_block = BLOCK_OVERHEAD + DISPATCH_PER_OPCODE * len(ops) + sum(bodies[op] for op in ops) + 1
    return 3 + length * per_block + 1


def object_instruction(tag: int, operands: list[int]) -> dict:
    return {"kind": "node", "tag": tag,
            "fields": [{"kind": "integer", "value": v} for v in operands]}


def bundle(instructions: list[dict], objin: int) -> dict:
    return {"kind": "node", "tag": BUNDLE_TAG,
            "fields": [{"kind": "node", "tag": OBJECT_PROGRAM_TAG, "fields": instructions},
                       {"kind": "integer", "value": objin}]}


class Runner:
    def __init__(self, binary: str, workdir: pathlib.Path):
        self.binary = binary
        self.workdir = workdir
        self.launches = 0

    def run(self, name: str, prog: dict, data: dict) -> dict:
        if self.launches >= MAX_LAUNCHES:
            raise SystemExit(f"launch budget of {MAX_LAUNCHES} exhausted before {name}")
        self.launches += 1
        program_path = self.workdir / "programs" / f"{name}.adva"
        input_path = self.workdir / "inputs" / f"{name}.json"
        output_path = self.workdir / "runs" / f"{name}.run.adva"
        for parent in (program_path.parent, input_path.parent, output_path.parent):
            parent.mkdir(parents=True, exist_ok=True)
        program_path.write_text(json.dumps(prog, indent=2) + "\n")
        input_path.write_text(json.dumps(data, indent=2) + "\n")
        done = subprocess.run(
            [self.binary, "data-run", str(program_path), "--input", str(input_path),
             "--fuel", "2048", "--quantum", "2048", "--output", str(output_path)],
            check=False, capture_output=True, text=True, timeout=20,
        )
        (self.workdir / "runs" / f"{name}.stderr.txt").write_text(done.stderr)
        observed = {"name": name, "exit_code": done.returncode,
                    "stderr": done.stderr.strip()}
        if output_path.exists():
            record = json.loads(output_path.read_text())
            observed["status"] = record["status"]
            observed["steps"] = len(record["trace"])
            phase = record["state"].get("phase", {})
            observed["phase_kind"] = phase.get("kind")
            observed["phase_reason"] = phase.get("reason")
            observed["returned_value"] = phase.get("value")
        return observed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--binary", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    out = pathlib.Path(args.output)
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"{out} already holds a retained attempt; choose a new directory")
    out.mkdir(parents=True, exist_ok=True)

    # Shapes measured without execution: one more opcode case, one more object
    # instruction, and the two metas that cannot be admitted at all.
    shapes = {
        "A1": (["input", "return"], 1),
        "A2": (["input", "return"], 2),
        "A3": (["input", "return"], 3),
        "B1": (["input", "constant", "return"], 1),
        "B2": (["input", "constant", "return"], 2),
        "C1": (["input", "constant", "copy", "return"], 1),
        "C2": (["input", "constant", "copy", "return"], 2),
    }
    metas = {name: meta_program(*shape) for name, shape in shapes.items()}
    lengths = {name: len(meta["code"]) for name, meta in metas.items()}
    bodies = body_lengths()

    runner = Runner(args.binary, out)
    cases: list[dict] = []

    def declared(name, prog, data, expect, object_instructions):
        observed = runner.run(name, prog, data)
        observed.update({"expected": expect, "object_instructions": object_instructions})
        cases.append(observed)

    # Positive cases: the meta program interprets object programs it has never seen.
    declared("A2-input-then-return-slot1", metas["A2"],
             bundle([object_instruction(TAG["input"], [1]),
                     object_instruction(TAG["return"], [1])], 7), "returned 7", 2)
    declared("A2-input-then-return-slot0", metas["A2"],
             bundle([object_instruction(TAG["input"], [0]),
                     object_instruction(TAG["return"], [0])], 9), "returned 9", 2)
    declared("A3-three-object-instructions", metas["A3"],
             bundle([object_instruction(TAG["input"], [1]),
                     object_instruction(TAG["input"], [0]),
                     object_instruction(TAG["return"], [0])], 4), "returned 4", 3)
    declared("B2-constant-then-return", metas["B2"],
             bundle([object_instruction(TAG["constant"], [5, 1]),
                     object_instruction(TAG["return"], [1])], 0), "returned 5", 2)

    # Declared refusals: outside the subset, falling off the end, out-of-range slots,
    # and an object read of a slot the object program never wrote.
    declared("refusal-unsupported-object-opcode", metas["A2"],
             bundle([object_instruction(9, [0]),
                     object_instruction(TAG["return"], [0])], 1),
             "runtime refusal: unsupported object opcode", 0)
    declared("refusal-fell-off-the-end", metas["A2"],
             bundle([object_instruction(TAG["input"], [0]),
                     object_instruction(TAG["input"], [1])], 1),
             "runtime refusal: object program fell off its end", 0)
    declared("refusal-return-slot-out-of-range", metas["A2"],
             bundle([object_instruction(TAG["input"], [0]),
                     object_instruction(TAG["return"], [3])], 1),
             "runtime refusal: object return register out of range", 0)
    declared("refusal-input-slot-out-of-range", metas["A2"],
             bundle([object_instruction(TAG["input"], [5]),
                     object_instruction(TAG["return"], [0])], 1),
             "runtime refusal: object register index out of range", 0)
    declared("refusal-object-reads-unwritten-slot", metas["A1"],
             bundle([object_instruction(TAG["return"], [0])], 1),
             "runtime refusal: uninitialized register", 1)

    # The meta program itself, at two sizes, cannot be admitted.
    declared("refusal-meta-four-opcodes-166", metas["C2"],
             bundle([object_instruction(TAG["input"], [0]),
                     object_instruction(TAG["return"], [0])], 1),
             "admission refusal: invalid program schema or capacity", 0)
    floor_meta = meta_program(FULL_GRAMMAR_ORDER, 1)
    declared("refusal-meta-nineteen-opcode-floor", floor_meta,
             bundle([object_instruction(TAG["input"], [0])], 1),
             "admission refusal: invalid program schema or capacity", 0)

    failures = []
    for case in cases:
        expected = case["expected"]
        if expected.startswith("returned "):
            wanted = int(expected.split()[1])
            value = case.get("returned_value")
            if case.get("status") != "Returned" or value != {"kind": "integer", "value": wanted}:
                failures.append(f"{case['name']}: expected {wanted}, saw {case}")
            continue
        if expected.startswith("runtime refusal: "):
            reason = expected.split(": ", 1)[1]
            if case.get("phase_kind") != "rejected" or case.get("phase_reason") != reason:
                failures.append(f"{case['name']}: expected runtime refusal '{reason}', saw {case}")
            continue
        text = expected.split(": ", 1)[1]
        if case["exit_code"] != 2 or text not in case["stderr"]:
            failures.append(f"{case['name']}: expected admission refusal '{text}', saw {case}")

    positive = [c for c in cases if c["expected"].startswith("returned ") and c.get("steps")]
    steps_per_object_step = {
        c["name"]: round(c["steps"] / c["object_instructions"], 2) for c in positive
    }
    model_checks = {
        name: {
            "generated": lengths[name],
            "reconstructed": reconstructed_length(shapes[name][0], shapes[name][1], bodies),
        }
        for name in shapes
    }
    model_checks["nineteen_opcode_ladder"] = {
        "generated": len(floor_meta["code"]),
        "reconstructed": reconstructed_length(FULL_GRAMMAR_ORDER, 1, bodies),
    }
    model_failures = [n for n, c in model_checks.items() if c["generated"] != c["reconstructed"]]
    failures.extend(f"length model disagrees with generated code: {n}" for n in model_failures)

    record = {
        "schema": "adva.self-interpretation-scaling.result.v0",
        "subset_interpreter": {
            "object_language": "input d, return s, constant v d, copy s d; two object slots",
            "meta_program_lengths": lengths,
            "declared_instruction_bound": DECLARED_INSTRUCTIONS,
            "measured_body_lengths": {op: bodies[op] for op in BODIES if op in TAG and op in ("input", "return", "constant", "copy")},
            "placeholder_body_length": bodies[PLACEHOLDER_OPS[0]],
            "block_cost_per_extra_object_instruction": lengths["A2"] - lengths["A1"],
            "opcode_case_cost_per_block": lengths["B1"] - lengths["A1"],
            "length_model_checks": model_checks,
            "metas_over_the_bound": {n: v for n, v in lengths.items() if v > DECLARED_INSTRUCTIONS},
        },
        "executed_steps_per_object_instruction": steps_per_object_step,
        "nineteen_opcode_ladder": {
            "generated_instructions": len(floor_meta["code"]),
            "declared_instruction_bound": DECLARED_INSTRUCTIONS,
            "admitted": False,
            "composition": "three prologue instructions, one fetch of two, nineteen dispatch cases of three, the four measured bodies, fifteen placeholder bodies charged the shortest measured body, one unsupported-opcode reject and one terminal reject",
            "placeholder_declaration": "the fifteen unmeasured opcodes are placeholders whose bodies are the shortest measured body, so this total understates any real nineteen-opcode meta; one object instruction only, no object register file, no provenance and no object fuel",
        },
        "launches": runner.launches,
        "cases": cases,
        "failures": failures,
        "verdict": "Passed" if not failures else "Failed",
    }
    (out / "results.json").write_text(json.dumps(record, indent=2) + "\n")

    print("meta program lengths         :", lengths)
    print("measured opcode bodies       :", bodies)
    print("per extra object instruction :", lengths["A2"] - lengths["A1"])
    print("per opcode case per block    :", lengths["B1"] - lengths["A1"])
    print("metas over the 128 bound     :", record["subset_interpreter"]["metas_over_the_bound"])
    print("native steps per object step :", steps_per_object_step)
    print("19-opcode ladder vs 128      :", len(floor_meta["code"]))
    print("length model checks          :",
          {n: (c["generated"], c["reconstructed"]) for n, c in model_checks.items() if
           c["generated"] != c["reconstructed"]} or "all agree")
    print("launches                     :", runner.launches, f"(budget {MAX_LAUNCHES})")
    for case in cases:
        print(f"  {case['name']:38s} exit={case['exit_code']} "
              f"status={case.get('status', '-'):9s} steps={case.get('steps', '-')} "
              f"{case['stderr'].splitlines()[0][:44] if case['stderr'] else ''}")
    print("verdict                      :", record["verdict"])
    for failure in failures:
        print("  FAIL", failure)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
