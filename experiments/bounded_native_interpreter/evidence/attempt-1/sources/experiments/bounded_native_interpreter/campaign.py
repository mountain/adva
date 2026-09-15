"""One frozen finite campaign; failures keep all files and stop this process."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import time

import blake3

import reference as R

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def save(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write("\n")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Campaign:
    def __init__(self, binary, output, contract):
        self.binary = binary
        self.output = output
        self.contract = contract
        self.budget = R.Budget(contract["campaign_limits"]["max_reference_steps_per_process"])
        self.program = json.loads((ROOT / "programs/bounded-interpreter/interpreter.adva").read_text())
        h = blake3.blake3(b"adva.data-machine.transition.v0\0")
        h.update((ROOT / "crates/adva-witness/src/data_machine.rs").read_bytes())
        h.update((ROOT / "Cargo.lock").read_bytes())
        self.profile = h.hexdigest()
        self.launches = 0
        self.checks = 0
        self.rows = []
        self.native_seconds = 0.0

    def check(self, condition):
        self.checks += 1
        if not condition:
            raise AssertionError("campaign check failed: " + str(self.checks))

    def launch(self, name, data, *, program=None, fuel=2048, quantum=2048,
               resume=None, check=None, admission_failure=False, raw_data=None):
        program = self.program if program is None else program
        self.launches += 1
        if self.launches > self.contract["campaign_limits"]["max_native_launches_per_process"]:
            raise RuntimeError("native launch budget exhausted")
        used = sum(p.stat().st_size for p in self.output.iterdir() if p.is_file())
        if used + 3 * 2097152 > self.contract["campaign_limits"]["artifact_bytes_per_process"]:
            raise RuntimeError("insufficient artifact reserve for another native call")
        program_path = self.output / (name + ".program.adva")
        input_path = self.output / (name + ".input.json")
        result_path = self.output / (name + ".run.adva")
        save(program_path, program)
        if raw_data is None:
            save(input_path, data)
        else:
            with input_path.open("x") as stream:
                stream.write(raw_data)
        cmd = [str(self.binary), "data-run", str(program_path), "--input", str(input_path),
               "--fuel", str(fuel), "--quantum", str(quantum), "--output", str(result_path)]
        if resume is not None:
            cmd += ["--resume", str(resume)]
        if check is not None:
            cmd += ["--check", str(check)]
        started = time.monotonic()
        completed = subprocess.run(cmd, capture_output=True, timeout=10, check=False)
        self.native_seconds += time.monotonic() - started
        (self.output / (name + ".stdout.txt")).write_bytes(completed.stdout)
        (self.output / (name + ".stderr.txt")).write_bytes(completed.stderr)
        row = {"name": name, "exit_code": completed.returncode}
        if admission_failure:
            self.check(completed.returncode == 2 and not result_path.exists())
            row["status"] = "AdmissionRejected"
            self.rows.append(row)
            return None, result_path
        report = json.loads(result_path.read_text())
        if check is not None:
            self.check(completed.returncode == 0)
            self.check(report["profile"] == self.profile)
            row.update(status="Verified", verified_steps=report["verified_steps"])
        else:
            R.receive(report, program, data, fuel, self.profile, self.budget)
            self.check(completed.returncode == (2 if report["status"] == "Rejected" else 0))
            row.update(status=report["status"], steps=report["state"]["spent"],
                       segment=report["segments"][-1])
        row["sha256"] = digest(result_path)
        self.rows.append(row)
        return report, result_path

    def execute(self):
        inputs = list(R.regular_inputs())
        self.check(len(inputs) == self.contract["family"]["expected_regular_cases"])
        for i, data in enumerate(inputs):
            report, _ = self.launch(f"regular-{i:03}", data)
            self.check(report["state"]["phase"] == {"kind": "returned", "value": R.integer(R.arithmetic_oracle(data))})

        sample = R.node(1, R.literal(2), R.node(2, R.literal(3), R.literal(4)))
        whole, whole_path = self.launch("sample", sample)
        self.check(whole["state"]["phase"] == {"kind": "returned", "value": R.integer(14)})
        prefix, prefix_path = self.launch("prefix", sample, quantum=17)
        self.check(prefix["status"] == "Suspended")
        resumed, _ = self.launch("resumed", sample, resume=prefix_path)
        self.check(resumed["trace"] == whole["trace"] and resumed["state"] == whole["state"])
        reception, _ = self.launch("reception", sample, quantum=0, check=whole_path)
        self.check(reception["verified_steps"] == whole["state"]["spent"])
        self.check(reception["state"] == whole["state"])
        exhausted, exhausted_path = self.launch("exhausted", sample, fuel=17)
        still, _ = self.launch("still-exhausted", sample, fuel=17, resume=exhausted_path)
        self.check(still["status"] == "FuelExhausted" and still["trace"] == exhausted["trace"])
        zero, _ = self.launch("zero", sample, fuel=0)
        self.check(zero["status"] == "FuelExhausted" and not zero["trace"])

        large = R.node(1, R.literal(9007199254740993), R.literal(2))
        report, _ = self.launch("large-exact", large)
        self.check(report["state"]["phase"] == {"kind": "returned", "value": R.integer(9007199254740995)})
        for label, value in (("minimum", -(2**63)), ("maximum", 2**63 - 1)):
            report, _ = self.launch(label, R.literal(value))
            self.check(report["state"]["phase"] == {"kind": "returned", "value": R.integer(value)})

        bad_objects = [R.node(99), R.node(0), R.node(0, R.node(0)),
                       R.node(1, R.literal(1), R.literal(2), R.literal(3)), R.integer(1),
                       R.node(1, R.literal(2**63 - 1), R.literal(1)),
                       R.node(1, R.literal(-(2**63)), R.literal(-1)),
                       R.node(2, R.literal(-(2**63)), R.literal(-1)),
                       R.node(2, R.literal(0), R.node(1, R.literal(2**63 - 1), R.literal(1)))]
        for i, data in enumerate(bad_objects):
            report, _ = self.launch(f"object-refusal-{i}", data)
            self.check(report["status"] == "Rejected")
            try:
                R.arithmetic_oracle(data)
            except R.Refusal:
                self.check(True)
            else:
                self.check(False)

        changed = deepcopy(self.program)
        for op in changed["code"]:
            if op["op"] == "add":
                op["op"] = "multiply"
        data = R.node(1, R.literal(2), R.literal(3))
        report, _ = self.launch("changed-program", data, program=changed)
        self.check(report["state"]["phase"] == {"kind": "returned", "value": R.integer(6)})

        generic = deepcopy(self.program)
        generic["name"] = "generic-tree-construction"
        generic["code"] = [{"op": "input", "dst": 2}, {"op": "copy", "src": 2, "dst": 3},
                           {"op": "node", "tag": 77, "fields": [2, 3], "dst": 4}, {"op": "return", "src": 4}]
        report, _ = self.launch("generic-node", R.integer(5), program=generic)
        self.check(report["state"]["phase"] == {"kind": "returned", "value": R.node(77, R.integer(5), R.integer(5))})
        loop = deepcopy(self.program)
        loop["code"] = [{"op": "jump", "target": 0}]
        report, _ = self.launch("loop", R.integer(0), program=loop, fuel=23)
        self.check(report["status"] == "FuelExhausted" and report["state"]["spent"] == 23)

        mutations = [deepcopy(prefix) for _ in range(6)]
        mutations[0]["state"]["spent"] = 0
        mutations[1]["state"]["registers"][0] = None
        mutations[2]["trace"][2]["state_digest"] = "0" * 64
        mutations[3]["trace"].pop(2)
        mutations[4]["profile"] = "stale"
        mutations[5]["segments"][0]["end"] = 0
        for i, mutation in enumerate(mutations):
            path = self.output / f"tampered-{i}.adva"
            save(path, mutation)
            self.launch(f"checkpoint-refusal-{i}", sample, resume=path, admission_failure=True)
        self.launch("input-context-refusal", R.literal(0), resume=prefix_path, admission_failure=True)
        self.launch("program-context-refusal", sample, program=changed, resume=prefix_path, admission_failure=True)
        self.launch("fuel-context-refusal", sample, fuel=18, resume=exhausted_path, admission_failure=True)

        bad_programs = [deepcopy(self.program) for _ in range(5)]
        bad_programs[0]["schema"] = "unknown"
        bad_programs[1]["code"][0] = {"op": "clear", "stack": 2}
        bad_programs[2]["code"][0] = {"op": "jump", "target": 10000}
        bad_programs[3]["registers"][1]["name"] = "work"
        bad_programs[4]["code"][0] = {"op": "constant", "dst": 7, "value": True}
        for i, p in enumerate(bad_programs):
            self.launch(f"program-refusal-{i}", sample, program=p, admission_failure=True)
        raw_cases = ['{"kind":"integer","value":true}', '{"kind":"integer","value":1.0}',
                     '{"kind":"integer","value":1,"extra":0}', '{"kind":"integer","value":1,"value":2}']
        for i, raw in enumerate(raw_cases):
            self.launch(f"raw-refusal-{i}", None, raw_data=raw, admission_failure=True)

        # Publication is separately exercised; the original accepted bytes must survive.
        before = whole_path.read_bytes()
        self.launches += 1
        self.check(self.launches <= self.contract["campaign_limits"]["max_native_launches_per_process"])
        started = time.monotonic()
        result = subprocess.run([str(self.binary), "data-run", str(self.output / "sample.program.adva"),
            "--input", str(self.output / "sample.input.json"), "--fuel", "2048", "--quantum", "2048",
            "--output", str(whole_path)], capture_output=True, timeout=10, check=False)
        self.native_seconds += time.monotonic() - started
        (self.output / "no-clobber.stderr.txt").write_bytes(result.stderr)
        self.check(result.returncode == 2 and whole_path.read_bytes() == before)
        self.rows.append({"name": "no-clobber", "exit_code": result.returncode, "status": "PublicationRejected"})
        return {"status": "Passed", "profile": self.profile, "regular_cases": len(inputs),
                "checks": self.checks, "native_launches": self.launches,
                "reference_steps": self.budget.steps,
                "sample_steps": whole["state"]["spent"], "rows": self.rows,
                "native_instruction_work_upper_bound": self.launches * 2 * 2048,
                "cost_note": "The upper bound includes execution and prefix checking, including rejected receptions. Prefix replay is not lifetime execution fuel. Host observations are recorded separately."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    contract = json.loads((HERE / "contract.json").read_text())
    limits = contract["campaign_limits"]
    resource.setrlimit(resource.RLIMIT_AS, (limits["address_space_bytes"],) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (limits["cpu_seconds_per_process"],) * 2)
    args.output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    campaign = Campaign(args.binary.resolve(), args.output.resolve(), contract)
    try:
        report = campaign.execute()
        stored = sum(p.stat().st_size for p in args.output.iterdir() if p.is_file())
        if stored + 65536 > limits["artifact_bytes_per_process"]:
            raise RuntimeError("artifact capacity exceeded")
        save(args.output / "summary.json", report)
        save(args.output / "cost.json", {"wall_seconds": time.monotonic() - started,
             "native_call_wall_seconds": campaign.native_seconds, "artifact_bytes_before_summary": stored,
             "parent_max_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
             "child_max_rss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
             "child_user_seconds": resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime,
             "child_system_seconds": resource.getrusage(resource.RUSAGE_CHILDREN).ru_stime})
        print(json.dumps({k: report[k] for k in ("status", "regular_cases", "checks", "native_launches", "reference_steps", "sample_steps")}))
    except Exception as exc:
        save(args.output / "failure.json", {"error": type(exc).__name__, "message": str(exc),
             "native_launches": campaign.launches, "checks": campaign.checks,
             "reference_steps": campaign.budget.steps, "wall_seconds": time.monotonic() - started})
        raise


if __name__ == "__main__":
    main()
