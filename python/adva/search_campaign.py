"""Research 0153: bounded policy comparison and 100 frozen-policy rounds.

Outer transport only. Arithmetic syntax, visits and judgments come from Rust.
The Research 0152 proof-log admission rules are imported without modification.
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

if __package__:
    from . import verifier_search as frozen
else:
    import verifier_search as frozen

FILE_LIMIT = 32 * 1024**2
TOTAL_LIMIT = 512 * 1024**2
FINAL_RESERVE = 1024**2
POLICIES = ("random", "tabu", "hybrid")
COUNTS = ("enumerated", "witness_checks", "memory_comparisons", "selection_scans", "work_units")
OLD_RUST_SHA = "ee938cb0589c16cb0765e5c2d9a992e51c9106d59790d2a3bd1c3a461f7b04ca"
OLD_PYTHON_SHA = "388553cd6293576b5b449ecafe7fba50c2cb8bf6bc93a459a42de110febab6a3"
LEAN_SHA = "8fadc3ed92cc9decb94c96ee9c0876e91e03a3a5e69138f32114f02789e2766c"
MM_SHA = "475a7ca3b9cc8b5c6e82d4a10f25e9a10b72adc0297391a12e54364e1b173397"


def _decode(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def constant(_):
        raise ValueError("non-finite JSON constant")

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


def expected_arms(mode):
    fields = mode.split(":")
    if len(fields) == 2 and fields[0] == "pilot" and fields[1] in ("2", "3", "4"):
        return [
            (int(fields[1]), direction, seed, policy)
            for direction in (True, False)
            for seed in (1, 7, 19)
            for policy in POLICIES
        ]
    if len(fields) == 4 and fields[0] == "round":
        number = int(fields[1])
        if 1 <= number <= 100 and fields[2] in POLICIES and fields[3] in POLICIES:
            return [
                (2 + (number - 1) % 3, direction, 1000 + number, policy)
                for direction, policy in ((True, fields[2]), (False, fields[3]))
            ]
    raise ValueError("request outside finite campaign contract")


def unpack(raw, mode):
    obj = _decode(raw)
    if (
        obj.get("schema") != "adva.search-campaign.batch.research.v0"
        or obj.get("status") != "ProvisionalRustChecked"
        or obj.get("mode") != mode
        or obj.get("frozen_blocks_matched") is not True
    ):
        raise ValueError("Rust campaign envelope mismatch")
    counts = obj["counts"]
    if any(
        type(counts.get(k)) is not int or counts[k] < 0
        for k in (*COUNTS, "selected", "bounded_exclusions")
    ):
        raise ValueError("invalid Rust cost ledger")
    if counts["work_units"] != sum(counts[k] for k in COUNTS[:-1]):
        raise ValueError("unbalanced Rust work ledger")
    if counts["work_units"] > 500_000:
        raise ValueError("Rust batch exceeded work cap")
    if type(obj["library_units"]) is not int or not 0 <= obj["library_units"] <= 200:
        raise ValueError("invalid library loading cost")
    if mode == "calibrate":
        # Envelope-only adaptation; reuse the frozen calibration protocol checks.
        adapted = {**obj, "schema": "adva.three-verifier-search.research.v0"}
        _, edges, labels = frozen.unpack_export(json.dumps(adapted), mode)
        return obj, edges, labels
    arms = obj["result"]["arms"]
    expected = expected_arms(mode)
    if len(arms) != len(expected):
        raise ValueError("missing or extra campaign arms")
    edges = []
    for arm, want in zip(arms, expected, strict=True):
        if (
            type(arm["expand"]) is not bool
            or type(arm["depth"]) is not int
            or type(arm["seed"]) is not int
        ):
            raise ValueError("invalid arm request echo types")
        if tuple(arm[k] for k in ("depth", "expand", "seed", "policy")) != want:
            raise ValueError("arm request/order differs from frozen schedule")
        path = arm["path"]
        if type(arm["steps"]) is not int or arm["steps"] != len(path) or not 0 <= len(path) <= 48:
            raise ValueError("path length outside finite contract")
        if arm["status"] not in {"Reached", "Unknown"}:
            raise ValueError("unexpected search status")
        if (arm["status"] == "Reached") != (arm["final"] == arm["target"]):
            raise ValueError("final/target fields contradict search status")
        if arm["status"] == "Unknown" and len(path) != 48:
            raise ValueError("unexpected Unknown stopping point")
        previous = arm["initial"]
        for item in path:
            edge = item["edge"]
            if edge["before"] != previous:
                raise ValueError("exported path has a broken consecutive boundary")
            previous = edge["after"]
            selected = item["selected_index"]
            if type(selected) is not int or not 0 <= selected < len(item["candidates"]):
                raise ValueError("invalid selected index")
            if (
                selected not in item["eligible_indices"]
                or item["candidates"][selected]["move"] != edge["move"]
            ):
                raise ValueError("selected edge differs from candidate trace")
            edges.append(edge)
        if previous != arm["final"]:
            raise ValueError("exported final boundary differs from path")
        if any(type(arm["cost"].get(k)) is not int or arm["cost"][k] < 0 for k in COUNTS):
            raise ValueError("invalid per-arm costs")
        if arm["cost"]["work_units"] != sum(arm["cost"][k] for k in COUNTS[:-1]):
            raise ValueError("unbalanced per-arm costs")
    if counts["selected"] != len(edges) or any(
        counts[k] != sum(a["cost"][k] for a in arms) for k in COUNTS
    ):
        raise ValueError("batch totals differ from arm ledgers")
    labels = [edge["label"] for edge in edges]
    if len(set(labels)) != len(labels) or any(
        not re.fullmatch(r"adva152e[0-9]+", label) for label in labels
    ):
        raise ValueError("invalid/repeated proof labels")
    if any(not isinstance(edge[k], str) for edge in edges for k in ("lean", "metamath")):
        raise ValueError("proof transport must contain strings")
    return obj, edges, labels


def baseline_matches(arms, prior):
    """Regression comparison of Rust exports; not a new semantic judgment."""
    for arm in arms:
        if arm["policy"] != "random":
            continue
        old = next(
            a
            for a in prior["result"]["arms"]
            if a["policy"] == "random" and a["expand"] == arm["expand"] and a["seed"] == arm["seed"]
        )
        for field in ("initial", "target", "final", "status", "steps", "residual"):
            if arm[field] != old[field]:
                raise ValueError("random control differs from frozen Research 0152")
        for current, previous in zip(arm["path"], old["path"], strict=True):
            if any(
                current["edge"][k] != previous["edge"][k]
                for k in ("before", "after", "move", "witness")
            ):
                raise ValueError("random path/witness differs from frozen baseline")
            if [(x["move"], x["residual"]) for x in current["candidates"]] != [
                (x["move"], x["residual"]) for x in previous["candidates"]
            ]:
                raise ValueError("random neighborhood differs from frozen baseline")


def choose_policies(arms):
    table = []
    winners = {}
    for direction, name in ((True, "expansion"), (False, "contraction")):
        rows = []
        for index, policy in enumerate(POLICIES):
            sample = [a for a in arms if a["expand"] == direction and a["policy"] == policy]
            if len(sample) != 9 or {(a["depth"], a["seed"]) for a in sample} != {
                (d, s) for d in (2, 3, 4) for s in (1, 7, 19)
            }:
                raise ValueError("pilot ranking lacks the exact nine matched cases")
            row = {
                "direction": name,
                "policy": policy,
                "reached": sum(a["status"] == "Reached" for a in sample),
                "work_units": sum(a["cost"]["work_units"] for a in sample),
                "steps": sum(a["steps"] for a in sample),
                "tie_order": index,
            }
            rows.append(row)
        winner = min(
            rows, key=lambda r: (-r["reached"], r["work_units"], r["steps"], r["tie_order"])
        )
        if winner["reached"] == 0:
            raise ValueError("insufficient pilot success for continuation")
        winners[name] = winner["policy"]
        table.extend(rows)
    return {
        "status": "FrozenPilotSelection",
        "winners": winners,
        "comparison": table,
        "scope": "Best under the declared pilot ordering, not generally optimal",
    }


class Supervisor:
    def __init__(self, output):
        self.started = time.monotonic()
        self.deadline = self.started + 4800
        self.output = Path(output).resolve()
        self.output.mkdir(parents=False, exist_ok=False)
        self.calls = []
        self.pins = {}
        self.pin_scans = 0
        self.pin_seconds = 0.0

    def check_time(self):
        if time.monotonic() >= self.deadline - 5:
            raise TimeoutError("Unknown: shared campaign deadline exhausted")

    def check_pins(self):
        self.check_time()
        start = time.monotonic()
        for path, expected in self.pins.items():
            self.check_time()
            if frozen.digest(path) != expected:
                raise ValueError(f"protected file changed: {path}")
        self.pin_scans += 1
        self.pin_seconds += time.monotonic() - start

    def space(self):
        total = sum(p.stat().st_size for p in self.output.iterdir() if p.is_file())
        if total > TOTAL_LIMIT:
            raise TimeoutError("Unknown: retained-byte budget exhausted")
        return total

    def save(self, name, raw, final=False):
        if not final:
            self.check_time()
        if not isinstance(raw, bytes):
            raw = (
                raw.encode()
                if isinstance(raw, str)
                else (json.dumps(raw, indent=2, sort_keys=True) + "\n").encode()
            )
        reserve = 0 if final else FINAL_RESERVE
        if len(raw) > FILE_LIMIT or self.space() + len(raw) + reserve > TOTAL_LIMIT:
            raise TimeoutError("Unknown: checkpoint byte budget exhausted")
        with (self.output / name).open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        return self.output / name

    def call(self, name, command, input_text=None):
        self.check_pins()
        if len(self.calls) >= 424:
            raise TimeoutError("Unknown: shared child count exhausted")
        if self.space() + 2 * FILE_LIMIT + FINAL_RESERVE > TOTAL_LIMIT:
            raise TimeoutError("Unknown: insufficient log/checkpoint reserve")
        if input_text is not None:
            self.save(name + ".stdin", input_text)
        remaining = self.deadline - time.monotonic() - 5
        if remaining <= 0:
            raise TimeoutError("Unknown: shared deadline exhausted")
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
                preexec_fn=frozen.child_limits,
            )
            timed_out = False
            try:
                process.communicate(
                    None if input_text is None else input_text.encode(), timeout=min(180, remaining)
                )
            except subprocess.TimeoutExpired:
                timed_out = True
            finally:
                with suppress(ProcessLookupError):
                    os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                after = resource.getrusage(resource.RUSAGE_CHILDREN)
                entry.update(
                    returncode=process.returncode,
                    wall_seconds=time.monotonic() - start,
                    cpu_seconds=after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime,
                    status="Unknown" if timed_out else "Completed",
                )
        self.space()
        if timed_out or process.returncode in (-signal.SIGXCPU, -signal.SIGXFSZ, -signal.SIGKILL):
            entry["status"] = "Unknown"
            raise TimeoutError(f"Unknown: {name} hit a child resource boundary")
        return (
            process.returncode,
            (self.output / (name + ".stdout")).read_bytes(),
            (self.output / (name + ".stderr")).read_bytes(),
        )


def protected_paths(root, args, native, lean, mm):
    paths = [
        Path(native).resolve(),
        Path(lean).resolve(),
        Path(mm).resolve(),
        args.database.resolve(),
        root / "Cargo.lock",
        Path(__file__).resolve(),
        Path(frozen.__file__).resolve(),
        Path(__file__).with_name("adva.py"),
        root / "docs/research/0153-frozen-verifier-search-campaign.md",
        root / "crates/adva-witness/examples/search_campaign.rs",
    ]
    paths.extend(
        root / "crates/adva-witness/src" / name
        for name in (
            "library_checkpoint.rs",
            "arithmetic.rs",
            "witness.rs",
            "boundary.rs",
            "seed.rs",
        )
    )
    paths.extend(
        root / "crates/adva-witness/examples" / name
        for name in (
            "library_stability.rs",
            "library_epoch.rs",
            "library_generation.rs",
            "verifier_search.rs",
        )
    )
    paths.extend(args.library.resolve() / f"epoch-{n:04}.json" for n in (0, 1))
    paths.extend(root / f"adva-library/exploration/0151/stage-{n:04}.json" for n in range(3))
    paths.extend(root / f"docs/research/0152-evidence/run-02/rust-{d}.stdout" for d in (2, 3, 4))
    return list(dict.fromkeys(paths))


def negative_controls(supervisor, obj, lean, mm, database):
    result = obj["result"]
    bad = supervisor.save("negative.lean", "import Init\n" + result["lean_false"])
    rc, log, err = supervisor.call("lean-negative", [lean, str(bad)])
    if rc == 0 or b"error:" not in log + err:
        raise ValueError("Lean false equality did not reject")
    sorry = supervisor.save("sorry.lean", "import Init\n" + result["lean_sorry"])
    rc, log, err = supervisor.call("lean-sorry", [lean, str(sorry)])
    if rc or err or b"sorryAx" not in log:
        raise ValueError("Lean sorry dependency did not appear")
    try:
        frozen.checked_lean_log(log.decode(), ["adva152sorry"])
    except ValueError:
        pass
    else:
        raise ValueError("sorryAx was incorrectly admitted")
    bad_mm = supervisor.save("negative.mm", f"$[ {database} $]\n" + result["metamath_false"])
    _, log, err = supervisor.call(
        "metamath-negative", [mm], frozen.mm_commands(bad_mm, "adva152bad")
    )
    if err or b"?Error" not in log or b"adva152bad" not in log:
        raise ValueError("Metamath false equality did not reject explicitly")
    return {
        "rust": result["controls"],
        "external": ["LeanFalseRejected", "LeanSorryRejected", "MetamathFalseRejected"],
    }


def summary_arms(obj):
    return [
        {k: v for k, v in arm.items() if k not in {"path", "initial", "target", "final"}}
        for arm in obj["result"]["arms"]
    ]


def run(args):
    supervisor = Supervisor(args.output)
    report = {
        "schema": "adva.search-campaign.research.v0",
        "status": "Blocked",
        "pilot": [],
        "rounds": [],
        "calls": supervisor.calls,
        "allowed_action": None,
    }
    totals = {
        "work_units_including_replay": 0,
        "enumerated_including_replay": 0,
        "library_units_including_replay": 0,
        "selected_edges_including_calibration": 0,
    }
    unreported_native_calls = []

    def interrupted(_number, _frame):
        raise TimeoutError("Unknown: outer campaign supervisor requested termination")

    prior_handler = signal.signal(signal.SIGTERM, interrupted)
    try:
        root = Path(__file__).resolve().parents[2]
        native, lean, mm = (shutil.which(str(p)) for p in (args.native, args.lean, args.metamath))
        if not all((native, lean, mm)):
            raise ValueError("required Rust/Lean/Metamath executable unavailable")
        database = args.database.resolve()
        for path in (database, supervisor.output):
            if not re.fullmatch(r"[A-Za-z0-9_./-]+", str(path)):
                raise ValueError("Metamath paths require plain non-space ASCII path characters")
        fixed = {
            root / "crates/adva-witness/examples/verifier_search.rs": OLD_RUST_SHA,
            Path(frozen.__file__): OLD_PYTHON_SHA,
            Path(lean): LEAN_SHA,
            Path(mm): MM_SHA,
            database: frozen.DATABASE_SHA256,
            root / "Cargo.lock": "b687d45dd12b4da84efdb0f258c8990fd867e23b666e38d6fdea59b7ac5b5e16",
            args.library.resolve()
            / "epoch-0000.json": "27016fc510e067caa930eb4e75b0d445342d4c1bc611dcf5b2577644e96ff8bb",
            args.library.resolve()
            / "epoch-0001.json": "eafbee5a0e8d56d326088c608ee34e3f5557c55a9f1cdb40feb7aa73342013bb",
        }
        if any(frozen.digest(p) != sha for p, sha in fixed.items()):
            raise ValueError("frozen Research 0152 verifier/database pin mismatch")
        supervisor.pins = {
            str(p): frozen.digest(p) for p in protected_paths(root, args, native, lean, mm)
        }
        supervisor.save("pins.json", supervisor.pins)
        report["pins_sha256"] = frozen.digest(supervisor.output / "pins.json")
        rc, log, err = supervisor.call("lean-version", [lean, "--version"])
        if rc or err or b"version 4.24.0" not in log or b"797c613" not in log:
            raise ValueError("Lean version mismatch")
        report["lean_version"] = log.decode().strip()
        rc, log, err = supervisor.call("metamath-base", [mm], frozen.mm_commands(database, "*"))
        if rc or err or b"0.199.pre" not in log:
            raise ValueError("Metamath base execution/version failure")
        frozen.checked_mm_log(log.decode())
        report["base_audit"] = "Passed"

        def native_export(name, mode):
            if (
                totals["work_units_including_replay"] + 500_000 > 25_000_000
                or totals["library_units_including_replay"] + 200 > 50_000
            ):
                raise TimeoutError("Unknown: insufficient shared native reservation")
            totals["work_units_including_replay"] += 500_000
            totals["library_units_including_replay"] += 200
            unreported_native_calls.append(
                {
                    "name": name,
                    "work_upper_bound": 500_000,
                    "library_upper_bound": 200,
                    "meaning": "Reservation, not an exact spent ledger",
                }
            )
            rc, raw, err = supervisor.call(name, [native, mode, str(args.library.resolve())])
            if rc == 3:
                raise TimeoutError("Unknown: Rust batch exhausted declared work")
            if rc or err:
                raise ValueError(f"Rust {name} failed")
            obj, edges, labels = unpack(raw, mode)
            totals["work_units_including_replay"] -= 500_000 - obj["counts"]["work_units"]
            totals["library_units_including_replay"] -= 200 - obj["library_units"]
            totals["enumerated_including_replay"] += obj["counts"]["enumerated"]
            unreported_native_calls.pop()
            return obj, edges, labels, raw

        def batch(name, mode, selection_sha=None):
            obj, edges, labels, raw = native_export("rust-" + name, mode)
            totals["selected_edges_including_calibration"] += len(edges)
            if (
                totals["work_units_including_replay"] > 25_000_000
                or totals["enumerated_including_replay"] > 1_560_576
                or totals["library_units_including_replay"] > 50_000
                or totals["selected_edges_including_calibration"] > 12_196
            ):
                raise TimeoutError("Unknown: shared Rust/replay budget exhausted")
            _, _, _, replay = native_export("replay-" + name, mode)
            if replay != raw:
                raise ValueError(f"Rust {name} deterministic replay differs")
            if mode.startswith("pilot:"):
                depth = int(mode.split(":")[1])
                baseline_matches(
                    obj["result"]["arms"],
                    _decode(
                        (
                            root / f"docs/research/0152-evidence/run-02/rust-{depth}.stdout"
                        ).read_bytes()
                    ),
                )
            lean_file = supervisor.save(
                f"proofs-{name}.lean", "import Init\n" + "".join(e["lean"] for e in edges)
            )
            mm_file = supervisor.save(
                f"proofs-{name}.mm", f"$[ {database} $]\n" + "".join(e["metamath"] for e in edges)
            )
            rc, log, err = supervisor.call("lean-" + name, [lean, str(lean_file)])
            if rc or err:
                raise ValueError(f"Lean {name} failed")
            axioms = frozen.checked_lean_log(log.decode(), labels)
            rc, log, err = supervisor.call(
                "metamath-" + name, [mm], frozen.mm_commands(mm_file, "adva152*")
            )
            if rc or err:
                raise ValueError(f"Metamath {name} failed")
            frozen.checked_mm_log(log.decode(), labels)
            receipt = {
                "status": "ThreeVerifierChecked",
                "mode": mode,
                "labels": labels,
                "axioms": axioms,
                "export_sha256": hashlib.sha256(raw).hexdigest(),
                "selection_sha256": selection_sha,
                "counts": obj["counts"],
            }
            if mode == "calibrate":
                receipt["controls"] = negative_controls(supervisor, obj, lean, mm, database)
            else:
                receipt["arms"] = summary_arms(obj)
            supervisor.save("admission-" + name + ".json", receipt)
            print(
                json.dumps(
                    {
                        "batch": name,
                        "status": receipt["status"],
                        "edges": len(edges),
                        "reached": sum(a["status"] == "Reached" for a in receipt.get("arms", [])),
                    }
                ),
                flush=True,
            )
            return receipt

        report["calibration"] = batch("calibrate", "calibrate")
        for depth in (2, 3, 4):
            report["pilot"].append(batch(f"pilot-{depth}", f"pilot:{depth}"))
        selection = choose_policies([a for b in report["pilot"] for a in b["arms"]])
        supervisor.save("selection.json", selection)
        selection_sha = frozen.digest(supervisor.output / "selection.json")
        supervisor.pins[str(supervisor.output / "selection.json")] = selection_sha
        report["selection"] = selection
        print(json.dumps({"selection": selection}), flush=True)
        winners = selection["winners"]
        for number in range(1, 101):
            receipt = batch(
                f"round-{number:03}",
                f"round:{number}:{winners['expansion']}:{winners['contraction']}",
                selection_sha,
            )
            report["rounds"].append(
                {
                    "round": number,
                    "mode": receipt["mode"],
                    "status": receipt["status"],
                    "arms": receipt["arms"],
                    "counts": receipt["counts"],
                }
            )
        supervisor.check_pins()
        report.update(
            status="Completed",
            allowed_action="retain-finite-policy-comparison-and-100-round-evidence",
        )
    except TimeoutError as error:
        report.update(status="Unknown", reason=str(error))
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        StopIteration,
        subprocess.SubprocessError,
    ) as error:
        report.update(status="Blocked", reason=str(error))
    finally:
        report["aggregate"] = totals
        report["unreported_native_reservations"] = unreported_native_calls
        report["completed_rounds"] = len(report["rounds"])
        report["cost"] = {
            "wall_seconds_before_final_checkpoint": time.monotonic() - supervisor.started,
            "child_cpu_seconds": sum(c.get("cpu_seconds", 0) for c in supervisor.calls),
            "children": len(supervisor.calls),
            "pin_scans": supervisor.pin_scans,
            "pin_scan_seconds": supervisor.pin_seconds,
            "child_peak_rss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            "retained_bytes_before_final_checkpoint": supervisor.space(),
        }
        try:
            supervisor.save("report.json", report, final=True)
        finally:
            signal.signal(signal.SIGTERM, prior_handler)
    return report
