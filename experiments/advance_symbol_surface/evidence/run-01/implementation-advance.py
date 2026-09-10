"""One frozen research continuation; Rust retains all PSC0 semantic authority."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

if __package__:
    from .math_catalog import check_catalog
    from .quine_relay import Exhausted, Supervisor, canonical, digest
else:
    from math_catalog import check_catalog
    from quine_relay import Exhausted, Supervisor, canonical, digest

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "experiments/advance_byte_observer/contract.json"
PROFILES = ("copy-add", "scale-add", "repeated-literal", "reordered-copy")
OBSERVERS = ("byte-value", "node-count", "operation-histogram", "ordered-operation-names")


def read_bounded(path, limit=16_777_216):
    with Path(path).open("rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise Exhausted(f"input size: {path}")
    return raw


def save(path, value):
    raw = json.dumps(value, indent=2, allow_nan=False).encode() + b"\n"
    if len(raw) > 16_777_216:
        raise Exhausted("checkpoint byte limit")
    with Path(path).open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def require_pin(raw, expected):
    if digest(raw) != expected:
        raise ValueError("pinned input differs")


def source(profile, *, tamper=False, invalid=False):
    expressions = []
    for b in range(256):
        u = b % 8 + 1
        v = b - 2 * u + int(tamper and b == 0)
        choices = {
            "copy-add": f"(add (add (copy {u})) {v})",
            "scale-add": f"(add (scale 2 {u}) {v})",
            "repeated-literal": f"(add {u} (add {u} {v}))",
            "reordered-copy": f"(add {v} (add (copy {u})))",
        }
        expressions.append("256" if invalid and b == 0 else choices[profile])
    return (
        "(module relay (export main) (def main (fn () (outputs "
        + " ".join(["Real"] * 256)
        + ") (frontier "
        + " ".join(expressions)
        + "))))\n"
    ).encode()


def observe(report, raw_output):
    """External readout of one fresh Rust result, not semantic import of a saved graph."""
    if report["status"] != "ByteFrontierEvaluated":
        raise ValueError("native evaluation did not complete")
    compilation = report["compilation"]
    certificate = compilation["certificate"]
    if any(
        certificate.get(k) != "checked"
        for k in ("types", "linear_use", "diagram_integrity", "module_links", "call_history")
    ):
        raise ValueError("missing compilation certificate field")
    evaluation = report["evaluation"]
    ec = evaluation["certificate"]
    if (
        ec.get("diagram_integrity") != "checked"
        or ec.get("operation_rules_checked") is not True
        or ec.get("input_types_checked") is not True
    ):
        raise ValueError("missing evaluation certificate field")
    values = evaluation["values"]
    if len(values) != len(raw_output) or any(
        type(v) not in (int, float) or v != b for v, b in zip(values, raw_output, strict=True)
    ):
        raise ValueError("native value/output protocol mismatch")
    diagram = compilation["result"]
    ordered = diagram["nodes"]
    nodes = {n["id"]: n for n in ordered}
    if len(nodes) != len(ordered) or len(diagram["outputs"]) != len(values):
        raise ValueError("native graph coverage mismatch")
    if ec.get("executed_nodes") != [n["id"] for n in ordered]:
        raise ValueError("incomplete native execution coverage")
    rows = []
    for value, wire in zip(values, diagram["outputs"], strict=True):
        seen, pending = set(), [wire]
        while pending:
            producer = pending.pop()["producer"]
            if producer["kind"] != "node":
                raise ValueError("profile requires a closed constant graph")
            node_id = producer["node"]
            if node_id not in seen:
                seen.add(node_id)
                pending.extend(nodes[node_id]["inputs"])
        selected = [n for n in ordered if n["id"] in seen]
        names = []
        for node in selected:
            op = node["operation"]
            if op["namespace"] != "adva.builtin" or op["version"] != 1:
                raise ValueError("unexpected operation registry boundary")
            names.append(op["name"])
        rows.append(
            {
                "value": value,
                "node_count": len(selected),
                "operation_histogram": dict(sorted(Counter(names).items())),
                "ordered_operation_names": names,
                "retained_native_node_ids": [n["id"] for n in selected],
            }
        )
    return rows


def partitions(rows_by_profile):
    """Retain actual buckets; a class count alone is not a separating witness."""
    signatures = {name: [] for name in rows_by_profile}
    result = []
    fields = ("value", "node_count", "operation_histogram", "ordered_operation_names")
    for observer, field in zip(OBSERVERS, fields, strict=True):
        buckets = {}
        for name, row in rows_by_profile.items():
            signatures[name].append(row[field])
            key = canonical(signatures[name])
            buckets.setdefault(key, []).append(name)
        result.append({"observer": observer, "classes": list(buckets.values())})
    return result


def worker(output):
    """Called only as a resource-limited child in the pinned 0161 source directory."""
    spec = importlib.util.spec_from_file_location("signed_0161", "signed.py")
    signed = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(signed)
    fuel = 2_000_000
    rows = []
    for b in range(256):
        term, u, v = signed.encode_byte(b)
        rows.append(
            {
                "byte": b,
                "u": u,
                "v": v,
                "value": signed.signed_value(term, fuel),
                "term_sha256": digest(repr(term).encode()),
            }
        )
    roundtrips = {}
    for b in (0, 35, 100, 255):
        term, _, _ = signed.encode_byte(b)
        expanded, steps = signed.r.expand_iota(signed.r.to_iota(term), fuel)
        value = signed.signed_value(signed.r.normalize(expanded, fuel), fuel)
        roundtrips[str(b)] = {"value": value, "expand_steps": steps}
    passed = (
        all(r["byte"] == r["value"] for r in rows)
        and len({r["term_sha256"] for r in rows}) == 256
        and all(int(b) == r["value"] for b, r in roundtrips.items())
    )
    save(
        output / "ski.json",
        {
            "status": "Passed" if passed else "Rejected",
            "rows": rows,
            "iota_roundtrips": roundtrips,
            "authority": "external-model-only",
        },
    )
    if not passed:
        raise ValueError("SKI bridge control failed")


def run(args):
    output = Path(args.output).resolve()
    output.mkdir(parents=False, exist_ok=False)
    contract_raw = read_bounded(CONTRACT, 262_144)
    contract = json.loads(contract_raw)
    supervisor = Supervisor(output, contract["limits"])
    report = {
        "schema": "adva.advance-byte-observer.result.research",
        "version": 0,
        "status": "Rejected",
        "phase": "preflight",
        "controls": {},
        "native_admission": "not-granted",
        "new_knowledge_epoch": False,
        "native_free": "NotGranted",
        "profile": contract["profile"],
    }
    try:
        (output / "contract.json").write_bytes(contract_raw)
        for relative, expected in contract["pins"].items():
            require_pin(read_bounded(ROOT / relative), expected)
        predecessor_raw = read_bounded(ROOT / contract["predecessor"])
        (output / "predecessor.json").write_bytes(predecessor_raw)
        report["predecessor_sha256"] = digest(predecessor_raw)
        try:
            require_pin(predecessor_raw + b" ", report["predecessor_sha256"])
        except ValueError:
            report["controls"]["changed_predecessor_refused"] = True
        head = supervisor.git("source-head", ROOT, "rev-parse", "HEAD")
        report["source_head"] = head
        supervisor.call(
            "base-ancestor",
            ["git", "merge-base", "--is-ancestor", contract["base_commit"], "HEAD"],
            ROOT,
        )
        supervisor.call(
            "rust-source-boundary",
            [
                "git",
                "diff",
                "--exit-code",
                "--no-ext-diff",
                contract["base_commit"],
                "--",
                "Cargo.toml",
                "Cargo.lock",
                "crates",
                ".cargo",
                "rust-toolchain",
                "rust-toolchain.toml",
                "build.rs",
            ],
            ROOT,
        )
        library = ROOT / "adva-library"
        actual_library = supervisor.git("library-head", library, "rev-parse", "HEAD")
        if actual_library != contract["library_commit"]:
            raise ValueError("library version differs from this finite contract")
        catalog = check_catalog(ROOT)
        save(output / "catalog.json", catalog)
        if catalog["status"] != "CatalogConsistent":
            raise ValueError("catalog preflight failed")
        for name in ("advance.py", "adva.py", "quine_relay.py", "math_catalog.py"):
            (output / ("implementation-" + name)).write_bytes(
                read_bounded(ROOT / "python/adva" / name)
            )
        model_dir = output / "model"
        model_dir.mkdir()
        for name in ("signed.py", "reducer.py"):
            (model_dir / name).write_bytes(
                read_bounded(ROOT / "docs/research/0161-evidence" / name)
            )
        report["phase"] = "build-and-library-recheck"
        print("advance: preflight passed; rebuilding the pinned Rust observer", flush=True)
        supervisor.call(
            "build-observer",
            [
                "cargo",
                "rustc",
                "--locked",
                "--offline",
                "-j",
                "1",
                "-p",
                "adva-witness",
                "--example",
                "quine_relay",
                "--",
                "-C",
                "debuginfo=0",
                "-C",
                "strip=debuginfo",
            ],
            ROOT,
        )
        native = ROOT / "target/debug/examples/quine_relay"
        report["native_binary_sha256"] = digest(read_bounded(native))
        supervisor.call(
            "library-recheck",
            [native, "libraries", library, library, output / "library.json"],
            ROOT,
        )
        library_report = json.loads(read_bounded(output / "library.json"))
        if library_report["status"] != "BothSnapshotsRechecked":
            raise ValueError("library recheck failed")
        report["controls"]["library_nonzero_guard"] = all(
            bool(r["zero_refusal"]) for r in library_report["readings"]
        )
        report["library_fuel"] = library_report["fuel"]
        report["phase"] = "native-constructions"
        readings = {}

        def emit(name, raw, *, allow_failure=False):
            source_path = output / (name + ".lisp")
            source_path.write_bytes(raw)
            result_path = output / (name + "-native.json")
            bytes_path = output / (name + ".bin")
            code = supervisor.call(
                name,
                [native, "emit", source_path, bytes_path, result_path],
                ROOT,
                allow_failure=allow_failure,
            )
            native_report = json.loads(read_bounded(result_path))
            if code:
                return code, native_report, None
            return code, native_report, read_bounded(bytes_path, 256)

        for profile in PROFILES:
            supervisor.check()
            _, native_report, raw = emit(profile, source(profile))
            if raw != bytes(range(256)):
                raise ValueError("native output differs from the declared byte family")
            readings[profile] = observe(native_report, raw)
        print(
            "advance: four native constructions evaluated; checking replay and refusals", flush=True
        )
        _, repeated, raw = emit("unchanged-control", source("copy-add"))
        report["controls"]["unchanged_is_evidence_stutter"] = (
            observe(repeated, raw) == readings["copy-add"]
        )
        _, tampered, raw = emit("tampered-control", source("copy-add", tamper=True))
        observe(tampered, raw)
        report["controls"]["tampered_value_refused"] = raw == bytes(
            [1, *range(1, 256)]
        ) and raw != bytes(range(256))
        code, invalid, _ = emit(
            "out-of-range-control", source("copy-add", invalid=True), allow_failure=True
        )
        report["controls"]["out_of_range_refused_by_rust"] = (
            code != 0
            and invalid.get("status") == "Rejected"
            and "finite integers in 0..255" in invalid.get("error", "")
        )
        report["phase"] = "external-ski-bridge"
        ski_code = supervisor.call(
            "ski-bridge",
            [sys.executable, Path(__file__).resolve(), "--worker", output],
            model_dir,
            allow_failure=True,
        )
        if ski_code == 3:
            raise Exhausted("external SKI resource limit; see ski-bridge.stderr")
        if ski_code:
            raise ValueError("external SKI checker failed; see ski-bridge.stderr")
        ski = json.loads(read_bounded(output / "ski.json"))
        report["controls"]["fresh_ski_matches_native"] = (
            ski["status"] == "Passed"
            and len(ski["rows"]) == 256
            and [r["value"] for r in ski["rows"]] == list(range(256))
        )
        report["controls"]["iota_samples_match"] = set(ski["iota_roundtrips"]) == {
            "0",
            "35",
            "100",
            "255",
        } and all(int(b) == row["value"] for b, row in ski["iota_roundtrips"].items())
        report["phase"] = "observer-refinement"
        comparisons = []
        for b in range(256):
            supervisor.check()
            rows = {name: readings[name][b] for name in PROFILES}
            ladder = partitions(rows)
            first = next(
                (level["observer"] for level in ladder if len(level["classes"]) == 4), None
            )
            comparisons.append(
                {"byte": b, "readings": rows, "ladder": ladder, "first_separating_observer": first}
            )
        if any(r["first_separating_observer"] is None for r in comparisons):
            raise ValueError("frozen observer family does not separate all constructions")
        if len(report["controls"]) != 7 or not all(report["controls"].values()):
            raise ValueError("a frozen control failed")
        save(output / "comparisons.json", comparisons)
        report["finding"] = {
            "native_programs": 4,
            "byte_positions_per_program": 256,
            "checked_byte_constructions": 1024,
            "first_separator_counts": dict(
                Counter(r["first_separating_observer"] for r in comparisons)
            ),
            "class_count_patterns": dict(
                Counter(
                    "/".join(str(len(level["classes"])) for level in r["ladder"])
                    for r in comparisons
                )
            ),
            "interpretation": "First separating observation in the frozen list only; "
            "compilation-node order is not a canonical causal schedule.",
        }
        for relative, expected in contract["pins"].items():
            require_pin(read_bounded(ROOT / relative), expected)
        report["delta"] = {
            "kind": "observation",
            "checked": True,
            "scope": "external finite classifier over fresh Rust results",
            "description": "Read operation structure to resolve same-byte ambiguity; "
            "retain all original graphs and histories.",
        }
        report.update(status="VariationObserved", phase="complete")
    except (Exhausted, MemoryError, TimeoutError) as error:
        report.update(status="Unknown", error=str(error))
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        RecursionError,
        subprocess.SubprocessError,
    ) as error:
        report.update(status="Rejected", error=str(error))
    finally:
        try:
            report["files"], report["retained_bytes_before_report"] = supervisor.inventory()
        except Exhausted as error:
            report.update(status="Unknown", error=str(error))
        report["calls"] = supervisor.calls
        report["cost"] = {
            "wall_seconds_before_report": time.monotonic() - supervisor.started,
            "child_cpu_seconds": supervisor.child_cpu() - supervisor.child_cpu_start,
            "subprocess_invocations": len(supervisor.calls),
            "scope": "Includes preflight, build, controls, model, analysis and inventory; "
            "authoring and engineering tests are separate.",
        }
        save(output / "report.json", report)
        if time.monotonic() >= supervisor.deadline:
            report.update(status="Unknown", error="checkpoint crossed the run deadline")
            save(output / "checkpoint-limit.json", report)
    return report


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--worker":
        try:
            worker(Path(sys.argv[2]))
        except (MemoryError, RecursionError) as error:
            print(str(error), file=sys.stderr)
            raise SystemExit(3) from error
        except RuntimeError as error:
            if "fuel exceeded" not in str(error):
                raise
            print(str(error), file=sys.stderr)
            raise SystemExit(3) from error
    else:
        raise SystemExit("Use adva.py advance --output NEW-DIRECTORY")
