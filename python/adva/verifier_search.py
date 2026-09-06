"""Research 0152 supervisor; no arithmetic or semantic-identity authority.

Called by adva.py. Rust emits all syntax, witnesses, scores and proof text.
This module only checks the transport, invokes trusted local verifiers and
retains bounded evidence. Linux resource limits are required.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import resource
import shutil
import signal
import subprocess
import time
from contextlib import suppress
from pathlib import Path

DATABASE_SHA256 = "cf534eb74bd665c41a3ba8867296ad969e80834c750eea2094f6428e9af1f931"
FILE_LIMIT = 32 * 1024 * 1024
TOTAL_LIMIT = 128 * 1024 * 1024
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}


def mm_commands(path, pattern):
    # Otherwise the Metamath CLI consumes later commands as pagination input
    # and can spin at EOF. Every invocation must disable interactive paging.
    return f'SET SCROLL CONTINUOUS\nREAD "{path}"\nVERIFY PROOF {pattern}\nEXIT\n'


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def child_limits():
    resource.setrlimit(resource.RLIMIT_AS, (8 * 1024**3,) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (FILE_LIMIT,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (160, 160))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def checked_lean_log(log, labels):
    """Fail closed on missing/duplicate axiom audits or unexpected dependencies."""
    audits = re.findall(
        r"'(adva152\w+)' (?:does not depend on any axioms|depends on axioms: \[([^\]]*)\])",
        log,
    )
    if [name for name, _ in audits] != labels:
        raise ValueError("Lean axiom audit labels differ from the Rust batch")
    result = {}
    for name, raw in audits:
        axioms = {item.strip() for item in raw.split(",") if item.strip()}
        if not axioms <= ALLOWED_AXIOMS:
            raise ValueError(f"Lean unapproved axioms: {sorted(axioms - ALLOWED_AXIOMS)}")
        result[name] = sorted(axioms)
    if re.search(r"\b(?:error|warning):", log, re.IGNORECASE):
        raise ValueError("Lean reported an error or warning")
    return result


def checked_mm_log(log, labels=None):
    """The CLI may exit zero on proof errors; its exit code is insufficient."""
    if re.search(r"\?Error|\bwarning\b|not proved|\bfailed\b", log, re.IGNORECASE):
        raise ValueError("Metamath reported an error, incomplete proof or warning")
    if labels is None:
        if "All proofs in the database were verified" not in log:
            raise ValueError("Metamath full dependency audit did not finish")
    elif re.findall(r"\badva152(?:e[0-9]+|cal[0-9]+)\b", log) != labels:
        raise ValueError("Metamath verified-label trace differs from the Rust batch")


def unpack_export(raw, mode):
    obj = json.loads(raw)
    if obj.get("schema") != "adva.three-verifier-search.research.v0":
        raise ValueError("unsupported Rust export schema")
    if obj.get("status") != "ProvisionalRustChecked" or obj.get("mode") != mode:
        raise ValueError("Rust export status/mode mismatch")
    if mode == "calibrate":
        result = obj["result"]
        if len(result["controls"]) != 5 or any(v is not True for v in result["controls"].values()):
            raise ValueError("Rust negative controls failed")
        edges = result["edges"]
        if len(edges) != 4:
            raise ValueError("calibration edge count mismatch")
    else:
        arms = obj["result"]["arms"]
        if len(arms) != 12:
            raise ValueError("round must contain twelve arms")
        edges = []
        for arm in arms:
            if arm["status"] not in {"Reached", "Unknown"}:
                raise ValueError("unexpected Rust search outcome")
            if arm["steps"] != len(arm["path"]) or not 0 <= arm["steps"] <= 48:
                raise ValueError("Rust path length exceeds contract")
            edges.extend(item["edge"] for item in arm["path"])
        if obj["counts"]["selected"] != len(edges):
            raise ValueError("Rust selected-edge count mismatch")
    labels = [edge["label"] for edge in edges]
    if len(set(labels)) != len(labels) or any(
        not re.fullmatch(r"adva152(?:e|cal)[0-9]+", label) for label in labels
    ):
        raise ValueError("invalid or repeated proof label")
    # Do not synthesize or repair semantic syntax here. Copy reviewed Rust output.
    if any(not isinstance(edge[field], str) for edge in edges for field in ("lean", "metamath")):
        raise ValueError("proof transport must contain strings")
    return obj, edges, labels


class Supervisor:
    def __init__(self, output):
        self.started = time.monotonic()
        self.deadline = self.started + 900
        self.output = Path(output).resolve()
        self.output.mkdir(parents=False, exist_ok=False)
        self.calls = []

    def space(self):
        total = sum(p.stat().st_size for p in self.output.iterdir() if p.is_file())
        if total > TOTAL_LIMIT:
            raise TimeoutError("Unknown: retained-byte budget exhausted")
        return total

    def save(self, name, raw):
        if isinstance(raw, str):
            raw = raw.encode()
        if len(raw) > FILE_LIMIT or self.space() + len(raw) > TOTAL_LIMIT:
            raise TimeoutError("Unknown: checkpoint byte budget exhausted")
        with (self.output / name).open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        return self.output / name

    def call(self, name, command, input_text=None):
        self.space()
        remaining = self.deadline - time.monotonic() - 5
        if remaining <= 0 or len(self.calls) >= 24:
            raise TimeoutError("Unknown: shared time/subprocess budget exhausted")
        # Reserve enough space for both capped streams before launching a child.
        if self.space() + 2 * FILE_LIMIT > TOTAL_LIMIT:
            raise TimeoutError("Unknown: insufficient bounded log reserve")
        if input_text is not None:
            self.save(name + ".stdin", input_text)
        entry = {"name": name, "command": list(map(str, command)), "status": "Started"}
        self.calls.append(entry)
        start = time.monotonic()
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        with (
            (self.output / (name + ".stdout")).open("xb") as stdout,
            (self.output / (name + ".stderr")).open("xb") as stderr,
        ):
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE if input_text is not None else subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
                start_new_session=True,
                preexec_fn=child_limits,
            )
            timeout = False
            try:
                process.communicate(
                    None if input_text is None else input_text.encode(), timeout=min(180, remaining)
                )
            except subprocess.TimeoutExpired:
                timeout = True
            finally:
                with suppress(ProcessLookupError):
                    os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                after = resource.getrusage(resource.RUSAGE_CHILDREN)
                entry.update(
                    returncode=process.returncode,
                    wall_seconds=time.monotonic() - start,
                    cpu_seconds=after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime,
                    status="Unknown" if timeout else "Completed",
                )
        self.space()
        if timeout:
            raise TimeoutError(f"Unknown: {name} exceeded shared/child wall time")
        if process.returncode in (-signal.SIGXCPU, -signal.SIGXFSZ, -signal.SIGKILL):
            entry["status"] = "Unknown"
            raise TimeoutError(f"Unknown: {name} terminated at a process resource boundary")
        raw = (self.output / (name + ".stdout")).read_bytes()
        err = (self.output / (name + ".stderr")).read_bytes()
        return process.returncode, raw, err


def run(args):
    """One no-retry finite invocation, dispatched exclusively by adva.py."""
    supervisor = Supervisor(args.output)
    report = {
        "schema": "adva.three-verifier-run.research.v0",
        "status": "Blocked",
        "rounds": [],
        "calls": supervisor.calls,
        "allowed_action": None,
    }
    try:
        native = shutil.which(str(args.native))
        lean = shutil.which(str(args.lean))
        mm = shutil.which(str(args.metamath))
        if not all((native, lean, mm)):
            raise ValueError("required Rust, Lean or Metamath executable is missing")
        database = args.database.resolve()
        # Metamath command/include syntax has no general shell-style escaping.
        for path in (database, supervisor.output):
            if not re.fullmatch(r"[A-Za-z0-9_./-]+", str(path)):
                raise ValueError("Metamath paths must use plain non-space ASCII path characters")
        if digest(database) != DATABASE_SHA256:
            raise ValueError("set.mm digest differs from the pinned audited contract")
        report["tools"] = {
            "native": {"path": native, "sha256": digest(native)},
            "lean": {"path": lean, "sha256": digest(lean)},
            "metamath": {"path": mm, "sha256": digest(mm)},
            "database": {"path": str(database), "sha256": digest(database)},
        }
        root = Path(__file__).resolve().parents[2]
        report["implementation_sha256"] = {
            str(p.relative_to(root)): digest(p)
            for p in (
                Path(__file__),
                Path(__file__).with_name("adva.py"),
                root / "docs/research/0152-three-verifier-residual-search.md",
                root / "crates/adva-witness/examples/verifier_search.rs",
            )
        }
        rc, raw, err = supervisor.call("lean-version", [lean, "--version"])
        if rc or err or b"version 4.24.0" not in raw or b"797c613" not in raw:
            raise ValueError("Lean release/version mismatch")
        report["tools"]["lean"]["version"] = raw.decode().strip()
        rc, raw, err = supervisor.call("metamath-base", [mm], mm_commands(database, "*"))
        if rc or err or b"0.199.pre" not in raw:
            raise ValueError("Metamath release/base execution failure")
        checked_mm_log(raw.decode())
        report["base_audit"] = "Passed"

        total_candidates = total_units = total_selected = 0
        for mode in ("calibrate", "2", "3", "4"):
            command = [native, mode, str(args.library.resolve())]
            rc, raw, err = supervisor.call(f"rust-{mode}", command)
            if rc or err:
                raise ValueError(f"Rust {mode} execution failed")
            obj, edges, labels = unpack_export(raw, mode)
            total_candidates += obj["counts"]["enumerated"] * 2  # includes exact replay
            total_units += obj["library_units"] * 2
            total_selected += len(edges)
            if total_candidates > 250_000 or total_units > 50_000 or total_selected > 1732:
                raise TimeoutError("Unknown: aggregate Rust/replay resource limit exceeded")
            rc, replay, err = supervisor.call(f"replay-{mode}", command)
            if rc or err or replay != raw:
                raise ValueError("Rust deterministic replay differs from the provisional export")
            lean_file = supervisor.save(
                f"proofs-{mode}.lean", "import Init\n" + "".join(edge["lean"] for edge in edges)
            )
            mm_file = supervisor.save(
                f"proofs-{mode}.mm",
                f"$[ {database} $]\n" + "".join(edge["metamath"] for edge in edges),
            )
            rc, log, err = supervisor.call(f"lean-{mode}", [lean, str(lean_file)])
            if rc or err:
                raise ValueError(f"Lean {mode} proof check failed")
            axioms = checked_lean_log(log.decode(), labels)
            rc, log, err = supervisor.call(
                f"metamath-{mode}", [mm], mm_commands(mm_file, "adva152*")
            )
            if rc or err:
                raise ValueError(f"Metamath {mode} proof check failed")
            checked_mm_log(log.decode(), labels)
            if mode == "calibrate":
                bad = supervisor.save(
                    "negative.lean", "import Init\n" + obj["result"]["lean_false"]
                )
                rc, log, err = supervisor.call("lean-negative", [lean, str(bad)])
                if rc == 0 or b"error:" not in log + err:
                    raise ValueError("Lean false-equality control did not reject")
                sorry = supervisor.save("sorry.lean", "import Init\n" + obj["result"]["lean_sorry"])
                rc, log, err = supervisor.call("lean-sorry", [lean, str(sorry)])
                if rc or err or b"sorryAx" not in log:
                    raise ValueError("Lean sorry-dependency control did not expose sorryAx")
                try:
                    checked_lean_log(log.decode(), ["adva152sorry"])
                except ValueError:
                    pass
                else:
                    raise ValueError("Lean axiom admission incorrectly accepted sorryAx")
                bad_mm = supervisor.save(
                    "negative.mm", f"$[ {database} $]\n" + obj["result"]["metamath_false"]
                )
                rc, log, err = supervisor.call(
                    "metamath-negative", [mm], mm_commands(bad_mm, "adva152bad")
                )
                if err or b"?Error" not in log or b"adva152bad" not in log:
                    raise ValueError("Metamath false-equality control did not reject explicitly")
                report["calibration"] = {
                    "status": "Passed",
                    "controls": obj["result"]["controls"],
                    "external_controls": [
                        "LeanFalseRejected",
                        "LeanSorryRejected",
                        "MetamathFalseRejected",
                    ],
                }
            else:
                arms = [
                    {
                        k: arm[k]
                        for k in (
                            "depth",
                            "expand",
                            "seed",
                            "policy",
                            "status",
                            "steps",
                            "residual",
                            "stop_reason",
                        )
                    }
                    for arm in obj["result"]["arms"]
                ]
                report["rounds"].append(
                    {
                        "depth": int(mode),
                        "status": "ThreeVerifierChecked",
                        "counts": obj["counts"],
                        "arms": arms,
                    }
                )
            supervisor.save(
                f"admission-{mode}.json",
                json.dumps(
                    {
                        "status": "ThreeVerifierChecked",
                        "labels": labels,
                        "axioms": axioms,
                        "export_sha256": hashlib.sha256(raw).hexdigest(),
                    },
                    indent=2,
                )
                + "\n",
            )
            print(
                json.dumps({"mode": mode, "status": "ThreeVerifierChecked", "edges": len(edges)}),
                flush=True,
            )
        if digest(database) != DATABASE_SHA256:
            raise ValueError("database changed during the run")
        report.update(
            status="Completed",
            allowed_action="retain-scoped-calibration-and-search-evidence",
            aggregate={
                "enumerated_including_replay": total_candidates,
                "library_units_including_replay": total_units,
                "selected_edges_including_calibration": total_selected,
            },
        )
    except TimeoutError as error:
        report.update(status="Unknown", reason=str(error))
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        report.update(status="Blocked", reason=str(error))
    finally:
        report["cost"] = {
            "wall_seconds_before_final_checkpoint": time.monotonic() - supervisor.started,
            "child_cpu_seconds": sum(c.get("cpu_seconds", 0) for c in supervisor.calls),
            "children": len(supervisor.calls),
            "child_peak_rss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            "retained_bytes_before_final_checkpoint": supervisor.space(),
        }
        supervisor.save("report.json", json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report
