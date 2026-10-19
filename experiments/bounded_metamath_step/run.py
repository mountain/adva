"""Finite native proof-step regressions; no proof evaluator is a runtime callback.

Codex (OpenAI), Unknown v0.3, through Mingli Yuan's authorized account proxy.
The Python instruction reference and external Metamath are independent oracles.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import resource
import subprocess
import time
from copy import deepcopy
from pathlib import Path

import blake3

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PROGRAM = ROOT / "programs/bounded-metamath-step/checker.adva"
REFERENCE = ROOT / "experiments/bounded_self_compiler/reference.py"
SPEC = importlib.util.spec_from_file_location("metamath_instruction_reference", REFERENCE)
R = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(R)


def read(path):
    return json.loads(path.read_bytes())


def save(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, reason):
    if not condition:
        raise AssertionError(reason)


def expression(kind, tokens):
    return R.node(1, R.integer(kind), R.node(2, *(R.integer(x) for x in tokens)))


def encode(case):
    return R.node(
        10,
        R.node(11, *(R.integer(x) for x in case["proof"])),
        expression(case["type"], case["tokens"]),
    )


def metamath_text(case):
    """A fixed wire codec, not a parser, substitution engine or proof checker."""
    labels = {100: "fq", 101: "at", 102: "fr", 200: "ax", 201: "neg", 202: "dup"}
    tokens = {1: "wff", 2: "|-", 3: "term", 4: "~", 5: "a", 10: "p", 11: "q", 12: "r"}
    target = " ".join(tokens[x] for x in [case["type"], *case["tokens"]])
    proof = " ".join(labels.get(x, "absent") for x in case["proof"])
    return (HERE / "database.mm").read_text() + f"result $p {target} $= {proof} $.\n"


def external_accepted(stdout, stderr, returncode):
    text = stdout + stderr
    return (
        returncode == 0
        and "All proofs in the database were verified" in text
        and "?" not in text
        and "incomplete" not in text.lower()
        and "not proved" not in text.lower()
    )


class Regression:
    def __init__(self, binary, metamath, output):
        self.binary = binary.resolve()
        self.metamath = metamath.resolve()
        self.output = output.resolve()
        self.output.mkdir(parents=True, exist_ok=False)
        self.contract = read(HERE / "contract.json")
        self.limits = self.contract["bounds"]
        self.started = time.monotonic()
        self.calls = []
        self.rows = []
        self.budget = R.Budget(self.limits["reference_steps"])
        self.program = read(PROGRAM)
        h = blake3.blake3(b"adva.data-machine.transition.v1\0")
        h.update((ROOT / "crates/adva-witness/src/data_machine_v1.rs").read_bytes())
        h.update((ROOT / "Cargo.lock").read_bytes())
        self.profile = h.hexdigest()

    def child_limits(self):
        resource.setrlimit(resource.RLIMIT_CPU, (15, 15))
        resource.setrlimit(resource.RLIMIT_AS, (1073741824, 1073741824))
        resource.setrlimit(resource.RLIMIT_FSIZE, (8388608, 8388608))

    def command(self, name, argv, stdin=None, codes=(0,)):
        remaining = self.limits["wall_seconds"] - (time.monotonic() - self.started)
        require(remaining > 0, "shared deadline exceeded")
        require(len(self.calls) < self.limits["calls_per_invocation"], "child count exceeded")
        used = sum(p.stat().st_size for p in self.output.rglob("*") if p.is_file())
        # stdout, stderr and one native report each have a per-file bound.
        # Reserve the final summary separately before starting another child.
        reserve = 3 * self.limits["child_file_bytes"] + 1048576
        require(used + reserve <= self.limits["artifact_bytes"], "artifact reserve exceeded")
        argv = [str(x) for x in argv]
        row = {"name": name, "argv": argv, "stdin": stdin, "returncode": None}
        self.calls.append(row)
        with (
            (self.output / f"{name}.stdout").open("xb") as out,
            (self.output / f"{name}.stderr").open("xb") as err,
        ):
            proc = subprocess.run(
                argv,
                input=stdin.encode() if stdin is not None else None,
                stdout=out,
                stderr=err,
                timeout=min(remaining, self.limits["child_wall_seconds"]),
                preexec_fn=self.child_limits,
                check=False,
            )
        row["returncode"] = proc.returncode
        require(proc.returncode in codes, f"{name}: unexpected exit {proc.returncode}")
        return proc.returncode

    def native(self, name, data, *, program=None, fuel=8192, quantum=8192, resume=None):
        program = self.program if program is None else program
        pp = PROGRAM
        if program != self.program:
            pp = self.output / f"{name}.program.adva"
            save(pp, program)
        ip = self.output / f"{name}.input.json"
        rp = self.output / f"{name}.run.adva"
        save(ip, data)
        cmd = [
            self.binary,
            "data-run-v1",
            pp,
            "--input",
            ip,
            "--fuel",
            str(fuel),
            "--quantum",
            str(quantum),
            "--output",
            rp,
        ]
        if resume is not None:
            cmd.extend(["--resume", resume])
        self.command(name, cmd, codes=(0, 2))
        report = read(rp)
        state = R.receive(report, program, data, fuel, self.profile, self.budget)
        receipt = self.output / f"{name}.receipt.adva"
        self.command(
            name + "-replay",
            [
                self.binary,
                "data-run-v1",
                pp,
                "--input",
                ip,
                "--fuel",
                str(fuel),
                "--quantum",
                "0",
                "--check",
                rp,
                "--output",
                receipt,
            ],
        )
        received = read(receipt)
        require(received["state"] == state, "native replay state differs")
        require(received["verified_steps"] == state["spent"], "native replay steps differ")
        row = {
            "name": name,
            "status": report["status"],
            "phase": state["phase"],
            "spent": state["spent"],
            "report_sha256": sha(rp),
        }
        self.rows.append(row)
        return report, rp

    def external(self, case):
        name = case["name"]
        fixture = self.output / f"{name}.mm"
        fixture.write_text(metamath_text(case))
        rc = self.command(
            name + "-metamath",
            [self.metamath],
            stdin=f'SET SCROLL CONTINUOUS\nREAD "{fixture}"\nVERIFY PROOF *\nEXIT\n',
        )
        stdout = (self.output / f"{name}-metamath.stdout").read_text()
        stderr = (self.output / f"{name}-metamath.stderr").read_text()
        accepted = external_accepted(stdout, stderr, rc)
        require(accepted == case["external"], f"{name}: external expectation differs")
        return {
            "accepted": accepted,
            "fixture_sha256": sha(fixture),
            "stdout_sha256": sha(self.output / f"{name}-metamath.stdout"),
        }

    def run(self):
        cases = read(HERE / "cases.json")
        for case in cases:
            report, _ = self.native(case["name"], encode(case))
            require(report["status"] == case["native"], f"{case['name']}: status differs")
            if case["native"] == "Returned":
                require(
                    report["state"]["phase"]["value"] == expression(case["type"], case["tokens"]),
                    "returned expression differs",
                )
            else:
                require(
                    report["state"]["phase"]["reason"] == case["reason"],
                    f"{case['name']}: failure reason differs: {report['state']['phase']}",
                )
            self.rows[-1]["external"] = self.external(case)

        sample = encode(cases[3])
        whole, _ = self.native("whole", sample)
        prefix, prefix_path = self.native("prefix", sample, quantum=17)
        require(prefix["status"] == "Suspended", "quantum did not suspend")
        resumed, _ = self.native("resumed", sample, resume=prefix_path)
        require(
            resumed["trace"] == whole["trace"] and resumed["state"] == whole["state"],
            "continuation changed execution",
        )
        exhausted, exhausted_path = self.native("fuel-exhausted", sample, fuel=17)
        still, _ = self.native("still-exhausted", sample, fuel=17, resume=exhausted_path)
        require(
            still["status"] == "FuelExhausted" and still["trace"] == exhausted["trace"],
            "continuation refilled fuel",
        )

        malformed = deepcopy(sample)
        malformed["tag"] = 99
        rejected, _ = self.native("malformed-root", malformed)
        require(rejected["status"] == "Rejected", "malformed root accepted")
        malformed = deepcopy(sample)
        malformed["fields"][1]["fields"][1]["fields"][0] = R.node(77)
        rejected, _ = self.native("noninteger-token", malformed)
        require(rejected["status"] == "Rejected", "noninteger token accepted")
        malformed = deepcopy(sample)
        malformed["fields"][1]["fields"].append(R.integer(5))
        rejected, _ = self.native("wrong-expression-arity", malformed)
        require(rejected["status"] == "Rejected", "wrong arity accepted")

        # Keep expected input short so these exercise construction bounds,
        # rather than being refused by the expected-expression precheck.
        for name, labels in [
            ("runtime-negation-bound", [100, 201, 201, 201, 201, 200]),
            ("runtime-duplication-bound", [100, 201, 201, 202]),
        ]:
            data = encode({"proof": labels, "type": 2, "tokens": [11]})
            bounded, _ = self.native(name, data)
            require(
                bounded["state"]["phase"] == {"kind": "rejected", "reason": "token bound"},
                "runtime substitution bound not enforced",
            )
        at_cap = encode({"proof": [100] * 4, "type": 1, "tokens": [11]})
        report, _ = self.native("stack-at-cap", at_cap)
        require(
            report["state"]["phase"]
            == {
                "kind": "rejected",
                "reason": "non-singleton proof stack",
            },
            "depth four was not admitted",
        )

        changed = deepcopy(self.program)
        changed_count = 0
        for instruction in changed["code"]:
            if instruction["op"] == "constant" and instruction["value"] == 200:
                instruction["value"] = 999
                changed_count += 1
        require(changed_count == 1, "mutation must alter exactly one label dispatch")
        changed_report, _ = self.native("program-mutation", encode(cases[2]), program=changed)
        require(changed_report["status"] == "Rejected", "program mutation had no effect")

        # A deliberately weakened scope guard must accept the otherwise exact
        # substitution that the independent Metamath checker rejects.
        changed = deepcopy(self.program)
        labels = read(ROOT / "programs/bounded-metamath-step/instruction-labels.json")
        destination = labels["reject_inactive_label"]
        guard = [x for x in changed["code"] if x["op"] == "branch" and x["yes"] == destination]
        require(len(guard) == 1, "scope mutation must alter exactly one branch")
        guard[0]["yes"] = labels["floating_q"]
        scope_case = next(x for x in cases if x["name"] == "scope-violation")
        weakened, _ = self.native("scope-guard-mutation", encode(scope_case), program=changed)
        require(weakened["status"] == "Returned", "scope negative control did not penetrate")
        require(
            weakened["state"]["phase"]["value"] == expression(2, [11]),
            "scope control changed the substitution",
        )

        # Context substitution must fail before a forged continuation can run.
        forged = self.output / "forged.input.json"
        save(forged, encode(cases[0]))
        rc = self.command(
            "changed-input-resume",
            [
                self.binary,
                "data-run-v1",
                PROGRAM,
                "--input",
                forged,
                "--fuel",
                "8192",
                "--quantum",
                "8192",
                "--resume",
                prefix_path,
                "--output",
                self.output / "forged.run.adva",
            ],
            codes=(2,),
        )
        require(
            rc == 2 and not (self.output / "forged.run.adva").exists(),
            "changed input continuation admitted",
        )
        return {
            "cases": len(cases),
            "rows": self.rows,
            "profile": self.profile,
            "reference_steps": self.budget.steps,
            "commands": self.calls,
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--metamath", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run = Regression(args.binary, args.metamath, args.output)
    result = {
        "status": "Failed",
        "commands": run.calls,
        "rows": run.rows,
        "native_binary_sha256": sha(run.binary),
        "metamath_binary_sha256": sha(run.metamath),
    }
    try:
        result.update(run.run())
        result["status"] = "Passed"
    except Exception as error:
        result["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        result["wall_seconds"] = time.monotonic() - run.started
        save(run.output / "result.json", result)
        used = sum(p.stat().st_size for p in run.output.rglob("*") if p.is_file())
        require(used <= run.limits["artifact_bytes"], "final artifact bytes exceeded")
        require(result["wall_seconds"] <= run.limits["wall_seconds"], "final deadline exceeded")


if __name__ == "__main__":
    main()
