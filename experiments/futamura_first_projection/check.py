#!/usr/bin/env python3
"""The first Futamura-style observation, bounded and executed.

The agenda names this calibration in section 1.5 step 5 and in section 4: compile
one fixed static expression into an ordinary Adva program, and check that residual
execution agrees with the interpreter under a declared observation, while the
source-to-residual correspondence and the forgotten structure stay explicit.

What runs here:

- `I` is the unchanged frozen arithmetic interpreter
  (`programs/bounded-interpreter/interpreter.adva`, 51 instructions). It interprets
  tagged trees with tags 0 (literal), 1 (addition) and 2 (multiplication).
- `C` is the compiler. It is built from `I` by a declared rule: every instruction up
  to the interpreter's final `return` is kept byte for byte, that `return` becomes a
  jump into an appended emission epilogue, and the epilogue folds the completed value
  into a residual program as data. The construction is checked instruction by
  instruction.
- The residual is emitted as finite tagged data, in the declared encoding `R`: a
  program node (tag 7) whose fields are instruction nodes — tag 0 `constant value dst`,
  tag 2 `box_integer src dst`, tag 1 `return src`. The checker instantiates that data
  into a real program file, because this profile has no loader instruction.
- Family: the 129 frozen regular arithmetic trees from the retained bounded-interpreter
  archive. Nothing new is searched for.

Observations compared for every one of the 129 trees: the interpreter's returned value,
the directly executed residual's returned value, and an independent recursive
arithmetic oracle over the same tree. Costs are recorded for all three, so the compile
time is not hidden.
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

MAX_LAUNCHES = 512
FUEL = 2048
QUANTUM = 2048

# Declared residual encoding R: program node tag, and instruction tags.
RESIDUAL_PROGRAM_TAG = 7
INSTRUCTION_TAGS = {
    0: ("constant", ("value", "dst")),
    2: ("box_integer", ("src", "dst")),
    1: ("return", ("src",)),
}
# The instantiated residual uses one integer register and one data register.
RESIDUAL_REGISTERS = [("r0", "integer"), ("r1", "data")]

EPILOGUE = [
    {"op": "constant", "dst": 7, "value": 0},
    {"op": "box_integer", "src": 7, "dst": 11},
    {"op": "constant", "dst": 7, "value": 1},
    {"op": "box_integer", "src": 7, "dst": 12},
    {"op": "as_integer", "src": 5, "dst": 6},
    {"op": "box_integer", "src": 6, "dst": 13},
    {"op": "node", "tag": 0, "fields": [13, 11], "dst": 14},
    {"op": "node", "tag": 2, "fields": [11, 12], "dst": 15},
    {"op": "node", "tag": 1, "fields": [12], "dst": 11},
    {"op": "node", "tag": 7, "fields": [14, 15, 11], "dst": 13},
    {"op": "return", "src": 13},
]
EPILOGUE_REGISTERS = [("zero", "data"), ("one", "data"), ("value_data", "data"),
                      ("instr_a", "data"), ("instr_b", "data")]
INTERPRETER_RETURN_INDEX = 48


def build_compiler(interpreter: dict) -> dict:
    """The declared compiler: the interpreter's body plus a checked emission epilogue."""
    program = json.loads(json.dumps(interpreter))
    entry = len(interpreter["code"])
    program["name"] = "futamura-compile-fixed-expression"
    program["registers"].extend({"name": name, "kind": kind}
                                for name, kind in EPILOGUE_REGISTERS)
    program["code"][INTERPRETER_RETURN_INDEX] = {"op": "jump", "target": entry}
    program["code"].extend(json.loads(json.dumps(EPILOGUE)))
    return program


def compiler_relationship(interpreter: dict, compiler: dict) -> dict:
    """Check instruction by instruction that the compiler is the interpreter plus epilogue."""
    kept = [i for i in range(len(interpreter["code"])) if i != INTERPRETER_RETURN_INDEX]
    same = all(compiler["code"][i] == interpreter["code"][i] for i in kept)
    return {
        "interpreter_instructions": len(interpreter["code"]),
        "compiler_instructions": len(compiler["code"]),
        "epilogue_instructions": len(EPILOGUE),
        "body_identical_except_final_return": same,
        "final_return_replaced_by": compiler["code"][INTERPRETER_RETURN_INDEX],
        "registers_added": len(EPILOGUE_REGISTERS),
    }


def oracle(tree: dict) -> int:
    """A direct recursive arithmetic oracle over the same tree, independent of both programs."""
    if tree["kind"] == "integer":
        return tree["value"]
    if tree["tag"] == 0:
        return tree["fields"][0]["value"]
    left, right = (oracle(field) for field in tree["fields"])
    return left + right if tree["tag"] == 1 else left * right


def instantiate(residual: dict) -> dict:
    """Instantiate emitted residual data into a real program, by the declared encoding R."""
    code = []
    for instruction in residual["fields"]:
        name, operands = INSTRUCTION_TAGS[instruction["tag"]]
        values = [field["value"] for field in instruction["fields"]]
        code.append({"op": name, **dict(zip(operands, values))})
    return {
        "schema": "adva.data-machine.program.research.v0",
        "name": "futamura-residual",
        "registers": [{"name": n, "kind": k} for n, k in RESIDUAL_REGISTERS],
        "code": code,
    }


def frozen_run(archive: pathlib.Path, name: str) -> bytes | None:
    with tarfile.open(archive, "r:gz") as bundle:
        try:
            return bundle.extractfile(name).read()
        except KeyError:
            return None


def frozen_trees(archive: pathlib.Path) -> list[tuple[str, dict]]:
    with tarfile.open(archive, "r:gz") as bundle:
        members = [m for m in bundle.getmembers() if m.name.startswith("regular-")
                   and m.name.endswith(".input.json")]
        return sorted(((m.name, json.loads(bundle.extractfile(m).read())) for m in members),
                      key=lambda pair: pair[0])


class Runner:
    def __init__(self, binary: str, workdir: pathlib.Path):
        self.binary = binary
        self.workdir = workdir
        self.launches = 0

    def run(self, relative: str, prog: dict, data: dict) -> dict:
        if self.launches >= MAX_LAUNCHES:
            raise SystemExit(f"launch budget of {MAX_LAUNCHES} exhausted at {relative}")
        self.launches += 1
        program_path = self.workdir / "raw" / "programs" / f"{relative}.adva"
        input_path = self.workdir / "raw" / "inputs" / f"{relative}.json"
        output_path = self.workdir / "raw" / "runs" / f"{relative}.run.adva"
        for parent in (program_path.parent, input_path.parent, output_path.parent):
            parent.mkdir(parents=True, exist_ok=True)
        program_path.write_text(json.dumps(prog, indent=2) + "\n")
        input_path.write_text(json.dumps(data, indent=2) + "\n")
        done = subprocess.run(
            [self.binary, "data-run", str(program_path), "--input", str(input_path),
             "--fuel", str(FUEL), "--quantum", str(QUANTUM), "--output", str(output_path)],
            check=False, capture_output=True, text=True, timeout=20,
        )
        observed = {"exit_code": done.returncode, "stderr": done.stderr.strip()}
        if output_path.exists():
            record = json.loads(output_path.read_text())
            phase = record["state"].get("phase", {})
            observed.update({
                "status": record["status"],
                "steps": len(record["trace"]),
                "value": (phase.get("value") or {}).get("value"),
                "program_instructions": len(record["program"]["code"]),
            })
        return observed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--binary", required=True)
    parser.add_argument("--interpreter", required=True)
    parser.add_argument("--archive", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    out = pathlib.Path(args.output)
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"{out} already holds a retained attempt; choose a new directory")
    out.mkdir(parents=True, exist_ok=True)

    interpreter = json.loads(pathlib.Path(args.interpreter).read_text())
    compiler = build_compiler(interpreter)
    relationship = compiler_relationship(interpreter, compiler)
    (out / "compiler.adva").write_text(json.dumps(compiler, indent=2) + "\n")

    trees = frozen_trees(pathlib.Path(args.archive))
    runner = Runner(args.binary, out)
    frozen_sample = frozen_run(pathlib.Path(args.archive), "regular-000.run.adva")
    cases = []
    failures = []
    for name, tree in trees:
        stem = name.split(".")[0]
        interpreted = runner.run(f"{stem}.interpreted", interpreter, tree)
        compiled = runner.run(f"{stem}.compiled", compiler, tree)
        if compiled.get("status") != "Returned":
            failures.append(f"{stem}: the compiler did not return: {compiled}")
            continue
        residual_path = out / "residuals" / f"{stem}.json"
        residual_path.parent.mkdir(parents=True, exist_ok=True)
        # The emitted residual is read back from the compiler's own run record.
        record = json.loads((out / "raw" / "runs" / f"{stem}.compiled.run.adva").read_text())
        residual = record["state"]["phase"]["value"]
        residual_path.write_text(json.dumps(residual, indent=2) + "\n")
        program = instantiate(residual)
        direct = runner.run(f"{stem}.residual", program, {"kind": "integer", "value": 0})
        expected = oracle(tree)
        row = {
            "case": stem,
            "interpreted_value": interpreted.get("value"),
            "interpreted_steps": interpreted.get("steps"),
            "compile_steps": compiled.get("steps"),
            "residual_value": direct.get("value"),
            "residual_steps": direct.get("steps"),
            "residual_bytes": len(json.dumps(residual)),
            "residual_instructions": len(program["code"]),
            "oracle_value": expected,
        }
        cases.append(row)
        if not (row["interpreted_value"] == row["residual_value"] == expected):
            failures.append(f"{stem}: values disagree: {row}")

    steps = [c["interpreted_steps"] for c in cases if c["interpreted_steps"]]
    residual_steps = [c["residual_steps"] for c in cases if c["residual_steps"]]
    compile_steps = [c["compile_steps"] for c in cases if c["compile_steps"]]
    sample_path = out / "raw" / "runs" / "regular-000.interpreted.run.adva"
    sample_matches_frozen = (sample_path.exists() and frozen_sample is not None
                             and sample_path.read_bytes() == frozen_sample)
    record = {
        "schema": "adva.futamura-first-projection.result.v0",
        "interpreted_side_matches_frozen_run_bytes": sample_matches_frozen,
        "family": len(trees),
        "compiler_relationship": relationship,
        "observation": "returned integer value, plus status; the trace is deliberately not compared, because compilation changes it",
        "forgotten_structure": "the tree's shape, its literals and the interpreter's own evaluation order are absent from the residual; what is retained is the folded value and the declared residual encoding",
        "totals": {
            "interpreted_steps_min": min(steps), "interpreted_steps_max": max(steps),
            "compile_steps_min": min(compile_steps), "compile_steps_max": max(compile_steps),
            "residual_steps_min": min(residual_steps), "residual_steps_max": max(residual_steps),
            "total_interpreted_steps": sum(steps),
            "total_compile_plus_residual_steps": sum(compile_steps) + sum(residual_steps),
        },
        "cases": cases,
        "launches": runner.launches,
        "failures": failures,
        "verdict": "Passed" if not failures and relationship["body_identical_except_final_return"] else "Failed",
    }
    raw = out / "raw"
    digests = {}
    archive = out / "attempt.tar.gz"
    with tarfile.open(archive, "w:gz") as bundle:
        for path in sorted(raw.rglob("*")):
            if path.is_file():
                relative = str(path.relative_to(raw))
                bundle.add(path, arcname=relative)
                digests[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    with tarfile.open(archive, "r:gz") as bundle:
        for member in bundle.getmembers():
            if member.isfile():
                assert hashlib.sha256(bundle.extractfile(member).read()).hexdigest() \
                    == digests[member.name], f"archive digest mismatch for {member.name}"
    shutil.rmtree(raw)
    record["retained"] = {
        "archive": archive.name,
        "archive_files": len(digests),
        "archive_bytes": archive.stat().st_size,
        "archive_digests_verified": True,
        "loose": "compiler.adva, results.json and residuals/ keep the compiler and every emitted residual",
    }
    (out / "results.json").write_text(json.dumps(record, indent=2) + "\n")

    print("compiler relationship        :", relationship)
    print("family                       :", len(trees), "frozen trees")
    print("interpreted steps  min/max   :", min(steps), max(steps))
    print("compile steps      min/max   :", min(compile_steps), max(compile_steps))
    print("residual steps     min/max   :", min(residual_steps), max(residual_steps))
    print("totals interpreted           :", sum(steps))
    print("totals compile+residual      :", sum(compile_steps) + sum(residual_steps))
    print("residual instructions        :", sorted({c["residual_instructions"] for c in cases}))
    print("interpreted side == frozen   :", record["interpreted_side_matches_frozen_run_bytes"])
    print("retained                     :", record["retained"])
    print("launches                     :", runner.launches, f"(budget {MAX_LAUNCHES})")
    print("verdict                      :", record["verdict"])
    for failure in failures[:5]:
        print("  FAIL", failure)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
