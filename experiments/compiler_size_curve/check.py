#!/usr/bin/env python3
"""How large the source language can grow before an in-language compiler stops fitting.

The three earlier measurements gave isolated points: a four-opcode meta interpreter is
166 instructions against a declared bound of 128, a nineteen-opcode ladder is 295, and
a two-opcode compiler is 41. This experiment turns them into a curve.

A generated compiler, written in the research data-machine language, lowers programs of
a declared subset of that same machine's instruction language into machine programs.
Each source instruction is lowered by a declared rule (one source instruction becomes
one to three target instructions, with slots held as a data register and an integer
register pair), so the residual is a real program that the checker instantiates and
executes directly; expected values come from an independent host-side reference
implementation of the same declared semantics.

The compiler is generated *per source language shape* — opcode set, slot count, program
length — because indexed access and register selection are static in this profile. The
curve is therefore a surface, and the ceiling it reports is the bootstrapping budget:
what a compiler written in this language, for this language, would have to fit in.

No optimisation is performed, deliberately: the curve must price fetch, dispatch,
operand extraction and lowering, not the cleverness of one pass.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import tarfile

MAX_LAUNCHES = 256
FUEL = 2048
QUANTUM = 2048

PROGRAM_TAG = 2            # source program node
BLOCK_TAG = 9              # emitted residual spine node
EMPTY_TAG = 8              # the empty residual accumulator
# Declared source tag, operand names in the machine's own order, and the lowering rule.
SUBSET = [
    ("input", 0, ("dst",)),
    ("return", 1, ("src",)),
    ("constant", 3, ("dst", "value")),
    ("copy", 4, ("src", "dst")),
    ("add", 5, ("left", "right", "dst")),
]
TARGET_ONLY = [("as_integer", 6, ("src", "dst")), ("box_integer", 7, ("src", "dst"))]
# Opcodes of the machine's full instruction language that this preflight declares no
# lowering for. They are charged the cheapest measured lowering and given their own
# tags, so the full-language compiler is a measured lower bound rather than a guess.
PLACEHOLDER_TAGS: dict[str, int] = {}
TAG_OF = {name: tag for name, tag, _ in SUBSET + TARGET_ONLY}
OPERANDS_OF = {name: operands for name, _, operands in SUBSET + TARGET_ONLY}
# The full declared instruction language, for the ceiling measurement.
ALL_OPS = ["input", "constant", "copy", "clear", "push", "pop", "is_empty", "tag",
           "field", "as_integer", "box_integer", "node", "add", "multiply", "equal",
           "jump", "branch", "return", "reject"]

# Compiler register file.
BUNDLE, PROGRAM, INSTR, TMP, ACC, B0, B1, B2 = 0, 1, 2, 3, 4, 5, 6, 7
OPCODE, OPERAND, OPERAND2, OPERAND3, SHIFT, PROBE = 8, 9, 10, 11, 12, 13
TEST = 14
COMPILER_REGISTERS = [
    ("bundle", "data"), ("program", "data"), ("instr", "data"), ("tmp", "data"),
    ("acc", "data"), ("b0", "data"), ("b1", "data"), ("b2", "data"),
    ("opcode", "integer"), ("operand", "integer"), ("operand2", "integer"),
    ("operand3", "integer"), ("shift", "integer"), ("probe", "integer"),
    ("test", "boolean"),
]


def compiler_program(ops: list[str], slots: int, length: int) -> dict:
    """Generate a compiler for one declared source shape."""
    code: list[dict] = []

    def emit(instruction: dict) -> int:
        code.append(instruction)
        return len(code) - 1

    def extract(op: str, position: int, index: int, dst: int) -> None:
        """Read one operand of the source instruction at `position` as an integer."""
        emit({"op": "field", "src": PROGRAM, "arity": length, "index": position, "dst": INSTR})
        emit({"op": "field", "src": INSTR, "arity": len(OPERANDS_OF[op]), "index": index,
              "dst": TMP})
        emit({"op": "as_integer", "src": TMP, "dst": dst})

    def shifted(source: int, dst: int) -> None:
        """Target register index for a slot: the integer bank starts at `slots`."""
        emit({"op": "add", "left": source, "right": SHIFT, "dst": dst})

    def boxed(source: int, dst: int) -> None:
        emit({"op": "box_integer", "src": source, "dst": dst})

    def append() -> None:
        """Append the instruction node in TMP to the left-nested residual spine."""
        emit({"op": "node", "tag": BLOCK_TAG, "fields": [ACC, TMP], "dst": ACC})

    def target(op: str, fields: list[int]) -> None:
        tag = TAG_OF.get(op)
        if tag is None:
            tag = PLACEHOLDER_TAGS.setdefault(op, 10 + len(PLACEHOLDER_TAGS))
        emit({"op": "node", "tag": tag, "fields": fields, "dst": TMP})
        append()

    def lower(op: str, position: int) -> None:
        if op == "input":
            extract(op, position, 0, OPERAND)
            boxed(OPERAND, B0)
            target("input", [B0])
            shifted(OPERAND, OPERAND2)
            boxed(OPERAND2, B1)
            target("as_integer", [B0, B1])
        elif op == "return":
            extract(op, position, 0, OPERAND)
            shifted(OPERAND, OPERAND2)      # the slot's integer register
            boxed(OPERAND2, B0)
            boxed(OPERAND, B1)              # the slot's data register
            target("box_integer", [B0, B1])
            boxed(OPERAND, B2)
            target("return", [B2])
        elif op == "constant":
            extract(op, position, 0, OPERAND)
            extract(op, position, 1, OPERAND2)
            shifted(OPERAND, OPERAND3)
            boxed(OPERAND3, B0)
            boxed(OPERAND2, B1)
            target("constant", [B0, B1])
        elif op == "copy":
            extract(op, position, 0, OPERAND)
            extract(op, position, 1, OPERAND2)
            shifted(OPERAND, OPERAND3)
            boxed(OPERAND3, B0)
            shifted(OPERAND2, OPERAND3)
            boxed(OPERAND3, B1)
            target("copy", [B0, B1])
        elif op == "add":
            extract(op, position, 0, OPERAND)
            extract(op, position, 1, OPERAND2)
            extract(op, position, 2, OPERAND3)
            shifted(OPERAND, OPERAND)
            shifted(OPERAND2, OPERAND2)
            shifted(OPERAND3, OPERAND3)
            boxed(OPERAND, B0)
            boxed(OPERAND2, B1)
            boxed(OPERAND3, B2)
            target("add", [B0, B1, B2])
        else:
            # Declared placeholder: one target instruction with one boxed operand.
            emit({"op": "constant", "dst": PROBE, "value": 0})
            boxed(PROBE, B0)
            target(op, [B0])

    emit({"op": "input", "dst": BUNDLE})
    emit({"op": "field", "src": BUNDLE, "arity": 2, "index": 0, "dst": PROGRAM})
    emit({"op": "constant", "dst": SHIFT, "value": slots})
    emit({"op": "node", "tag": EMPTY_TAG, "fields": [], "dst": ACC})
    for position in range(length):
        emit({"op": "field", "src": PROGRAM, "arity": length, "index": position, "dst": INSTR})
        emit({"op": "tag", "src": INSTR, "dst": OPCODE})
        body_exits: list[int] = []
        for op in ops:
            tag = TAG_OF.get(op)
            if tag is None:
                tag = PLACEHOLDER_TAGS.setdefault(op, 10 + len(PLACEHOLDER_TAGS))
            emit({"op": "constant", "dst": PROBE, "value": tag})
            emit({"op": "equal", "left": OPCODE, "right": PROBE, "dst": TEST})
            branch = emit({"op": "branch", "condition": TEST, "yes": len(code) + 1, "no": 0})
            body = len(code)
            lower(op, position)
            # A body must not fall through into the next opcode case.
            body_exits.append(emit({"op": "jump", "target": 0}))
            code[branch]["yes"] = body
            code[branch]["no"] = len(code)
        emit({"op": "reject", "reason": "source instruction outside the declared subset"})
        after_position = len(code)
        for jump in body_exits:
            code[jump]["target"] = after_position
    emit({"op": "return", "src": ACC})
    return {
        "schema": "adva.data-machine.program.research.v0",
        "name": f"lowering-compiler-{'-'.join(ops)}-{slots}s-{length}x",
        "registers": [{"name": n, "kind": k} for n, k in COMPILER_REGISTERS],
        "code": code,
    }


def source_instruction(op: str, slots: int, position: int) -> dict:
    """A declared source instruction with deterministic operands."""
    values = {
        "input": [position % slots],
        "return": [position % slots],
        "constant": [position % slots, 3 + position],
        "copy": [(position + 1) % slots, position % slots],
        "add": [position % slots, (position + 1) % slots, position % slots],
    }[op]
    return {"kind": "node", "tag": TAG_OF[op],
            "fields": [{"kind": "integer", "value": v} for v in values]}


def source_program(pair: tuple[str, ...], slots: int, length: int,
                   return_slot: int = 0) -> dict:
    """A declared source program: the pair cycles over the non-return positions."""
    fields = [source_instruction(pair[position % len(pair)], slots, position)
              for position in range(length - 1)]
    fields.append({"kind": "node", "tag": TAG_OF["return"],
                   "fields": [{"kind": "integer", "value": return_slot}]})
    return {"kind": "node", "tag": PROGRAM_TAG, "fields": fields}


def reference(program: dict, dynamic: int, slots: int) -> tuple[str, int | None]:
    """The declared semantics, implemented independently of both generated programs."""
    bank: list[int | None] = [None] * slots
    for instruction in program["fields"]:
        tag = instruction["tag"]
        values = [field["value"] for field in instruction["fields"]]
        if tag == TAG_OF["input"]:
            bank[values[0]] = dynamic
        elif tag == TAG_OF["constant"]:
            bank[values[0]] = values[1]
        elif tag == TAG_OF["copy"]:
            if bank[values[0]] is None:
                return "Rejected", None
            bank[values[1]] = bank[values[0]]
        elif tag == TAG_OF["add"]:
            if bank[values[0]] is None or bank[values[1]] is None:
                return "Rejected", None
            bank[values[2]] = bank[values[0]] + bank[values[1]]
        elif tag == TAG_OF["return"]:
            if bank[values[0]] is None:
                return "Rejected", None
            return "Returned", bank[values[0]]
        else:
            return "Rejected", None
    return "Rejected", None


def flatten(residual: dict) -> list[dict]:
    """Read the declared residual encoding: a left-nested spine of instruction nodes."""
    if residual["tag"] == EMPTY_TAG:
        return []
    if residual["tag"] == BLOCK_TAG:
        left, right = residual["fields"]
        return flatten(left) + flatten(right)
    return [residual]


def instantiate(residual: dict, slots: int) -> dict:
    """Instantiate emitted data into a real machine program with the declared register file."""
    registers = [{"name": f"d{index}", "kind": "data"} for index in range(slots)]
    registers += [{"name": f"i{index}", "kind": "integer"} for index in range(slots)]
    code = []
    for node in flatten(residual):
        tag = node["tag"]
        values = [field["value"] for field in node["fields"]]
        if tag == TAG_OF["input"]:
            code.append({"op": "input", "dst": values[0]})
        elif tag == TAG_OF["return"]:
            code.append({"op": "return", "src": values[0]})
        elif tag == TAG_OF["constant"]:
            code.append({"op": "constant", "dst": values[0], "value": values[1]})
        elif tag == TAG_OF["copy"]:
            code.append({"op": "copy", "src": values[0], "dst": values[1]})
        elif tag == TAG_OF["add"]:
            code.append({"op": "add", "left": values[0], "right": values[1], "dst": values[2]})
        elif tag == TAG_OF["as_integer"]:
            code.append({"op": "as_integer", "src": values[0], "dst": values[1]})
        elif tag == TAG_OF["box_integer"]:
            code.append({"op": "box_integer", "src": values[0], "dst": values[1]})
        else:
            raise SystemExit(f"emitted tag {tag} is outside the declared lowering table")
    return {"schema": "adva.data-machine.program.research.v0",
            "name": "lowering-residual", "registers": registers, "code": code}


class Runner:
    def __init__(self, binary: str, workdir: pathlib.Path):
        self.binary = binary
        self.workdir = workdir
        self.launches = 0

    def run(self, name: str, prog: dict, data: dict) -> dict:
        if self.launches >= MAX_LAUNCHES:
            raise SystemExit(f"launch budget of {MAX_LAUNCHES} exhausted at {name}")
        self.launches += 1
        program_path = self.workdir / "raw" / "programs" / f"{name}.adva"
        input_path = self.workdir / "raw" / "inputs" / f"{name}.json"
        output_path = self.workdir / "raw" / "runs" / f"{name}.run.adva"
        for parent in (program_path.parent, input_path.parent, output_path.parent):
            parent.mkdir(parents=True, exist_ok=True)
        program_path.write_text(json.dumps(prog, indent=2) + "\n")
        input_path.write_text(json.dumps(data, indent=2) + "\n")
        done = subprocess.run(
            [self.binary, "data-run", str(program_path), "--input", str(input_path),
             "--fuel", str(FUEL), "--quantum", str(QUANTUM), "--output", str(output_path)],
            check=False, capture_output=True, text=True, timeout=20)
        observed = {"exit_code": done.returncode, "stderr": done.stderr.strip().splitlines()[:1]}
        if output_path.exists():
            record = json.loads(output_path.read_text())
            phase = record["state"].get("phase", {})
            observed.update({"status": record["status"], "steps": len(record["trace"]),
                             "value": (phase.get("value") or {}).get("value")})
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

    # The curve: opcode set, source length and slot count, each measured by generating
    # the compiler for that shape and counting its instructions.
    grid = []
    for count in (2, 3, 4, 5):
        ops = ["input", "return"] + ["constant", "copy", "add"][: count - 2]
        grid.append(("opcodes", len(ops), 2, 3, sorted(ops)))
    for length in (1, 2, 3):
        grid.append(("length", 2, 2, length, ["input", "return"]))
    grid.append(("opcodes", 3, 2, 2, ["input", "return", "constant"]))
    for slots in (2, 3):
        grid.append(("slots", 2, slots, 2, ["input", "return"]))
    curve = []
    for axis, count, slots, length, ops in grid:
        program = compiler_program(ops, slots, length)
        curve.append({
            "axis": axis, "opcodes": count, "slots": slots, "length": length,
            "compiler_instructions": len(program["code"]),
            "within_bound": len(program["code"]) <= 128,
            "ops": ops,
        })
    (out / "curve.json").write_text(json.dumps(curve, indent=2) + "\n")

    runner = Runner(args.binary, out)
    cases = []
    failures = []
    executed_shapes = set()
    for entry in curve:
        shape = (tuple(entry["ops"]), entry["slots"], entry["length"])
        if not entry["within_bound"] or entry["length"] < 2 or shape in executed_shapes:
            continue
        executed_shapes.add(shape)
        ops = entry["ops"]
        slots, length = entry["slots"], entry["length"]
        compiler = compiler_program(ops, slots, length)
        (out / "compilers").mkdir(exist_ok=True)
        (out / "compilers" / f"c{entry['opcodes']}-{slots}s.json").write_text(
            json.dumps(compiler, indent=2) + "\n")
        non_return = [op for op in ops if op != "return"]
        for first in non_return:
            for second in non_return:
              # Two declared return slots per pair: one that a position writes and one
              # that stays unwritten, so both outcomes are exercised.
              for return_slot in sorted({0, min(1, slots - 1)}):
                label = (f"c{entry['opcodes']}-{slots}s-{length}x-{first}-{second}"
                         f"-r{return_slot}")
                program = source_program((first, second), slots, length, return_slot)
                compiled = runner.run(f"{label}.compiled", compiler,
                                      {"kind": "node", "tag": 4, "fields": [program,
                                                                            {"kind": "integer", "value": 0}]})
                if compiled.get("status") != "Returned":
                    failures.append(f"{label}: the compiler did not return: {compiled}")
                    continue
                record = json.loads(
                    (out / "raw" / "runs" / f"{label}.compiled.run.adva").read_text())
                residual = record["state"]["phase"]["value"]
                (out / "residuals").mkdir(exist_ok=True)
                (out / "residuals" / f"{label}.json").write_text(
                    json.dumps(residual, indent=2) + "\n")
                for dynamic in (7, 9):
                    expected_status, expected_value = reference(program, dynamic, slots)
                    direct = runner.run(f"{label}.residual.{dynamic}",
                                        instantiate(residual, slots),
                                        {"kind": "integer", "value": dynamic})
                    row = {"case": label, "dynamic": dynamic, "slots": slots,
                           "opcodes": entry["opcodes"],
                           "compiler_instructions": entry["compiler_instructions"],
                           "residual_instructions": len(instantiate(residual, slots)["code"]),
                           "expected_status": expected_status, "expected_value": expected_value,
                           "residual_status": direct.get("status"),
                           "residual_value": direct.get("value"),
                           "residual_steps": direct.get("steps"),
                           "compile_steps": compiled.get("steps")}
                    cases.append(row)
                    if (row["expected_status"] != row["residual_status"]
                            or row["expected_value"] != row["residual_value"]):
                        failures.append(f"{label} x={dynamic}: {row}")

    # The ceiling: a compiler for the machine's whole declared instruction language.
    ceiling_program = compiler_program(ALL_OPS, 2, 1)
    (out / "ceiling-compiler.adva").write_text(json.dumps(ceiling_program, indent=2) + "\n")
    ceiling = runner.run("ceiling-nineteen-opcodes", ceiling_program,
                         {"kind": "node", "tag": 4,
                          "fields": [source_program(("input", "input"), 2, 3),
                                     {"kind": "integer", "value": 0}]})
    ceiling.update({"compiler_instructions": len(ceiling_program["code"]),
                    "declared_bound": 128,
                    "opcodes": len(ALL_OPS),
                    "placeholders": sorted(PLACEHOLDER_TAGS),
                    "placeholder_note": "opcodes with no measured lowering are charged the "
                                        "cheapest measured one, so this size is a lower bound"})

    raw = out / "raw"
    digests = {}
    archive = out / "attempt.tar.gz"
    with tarfile.open(archive, "w:gz") as bundle:
        for path in sorted(raw.rglob("*")):
            if path.is_file():
                relative = str(path.relative_to(raw))
                bundle.add(path, arcname=relative)
                digests[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    with tarfile.open(archive, "r:gz") as check:
        for member in check.getmembers():
            if member.isfile():
                assert hashlib.sha256(check.extractfile(member).read()).hexdigest() \
                    == digests[member.name], f"archive digest mismatch for {member.name}"
    shutil.rmtree(raw)
    retained = {"archive": archive.name, "archive_files": len(digests),
                "archive_bytes": archive.stat().st_size, "archive_digests_verified": True,
                "loose": "curve.json, ceiling-compiler.adva, compilers/, residuals/ and results.json"}

    record = {
        "schema": "adva.compiler-size-curve.result.v0",
        "retained": retained,
        "declared_bound": 128,
        "curve": curve,
        "ceiling": ceiling,
        "cases": cases,
        "launches": runner.launches,
        "failures": failures,
        "verdict": "Passed" if not failures else "Failed",
    }
    (out / "results.json").write_text(json.dumps(record, indent=2) + "\n")

    print("compiler size curve (instructions against the declared bound of 128):")
    for entry in curve:
        print(f"  axis={entry['axis']:8s} opcodes={entry['opcodes']} slots={entry['slots']} "
              f"length={entry['length']} -> {entry['compiler_instructions']:4d} "
              f"{'fits' if entry['within_bound'] else 'over'}")
    print(f"ceiling: compiler for {ceiling['opcodes']} opcodes = "
          f"{ceiling['compiler_instructions']} instructions, exit={ceiling.get('exit_code')}, "
          f"status={ceiling.get('status')}")
    print(f"executed cases: {len(cases)}  failures: {len(failures)}")
    print(f"retained: {retained}")
    print(f"launches: {runner.launches} (budget {MAX_LAUNCHES})")
    print(f"verdict: {record['verdict']}")
    for failure in failures[:5]:
        print("  FAIL", failure)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
