#!/usr/bin/env python3
"""Bounded execution adapter with separated result axes.

Item three of `docs/TOOLING_WORKFLOW.md` section 6, and the display rule of section 6
end: keep several facts apart and never fold them into one green success. The axes
this command prints are:

    material accepted   the declared inputs exist here
    execution           completed, stopped by a limit, or not started (with exit code)
    checker verdict     declared facts read from the checker's own output
    applies to          the declared scope, quoted from the plan
    unknown / residual  what the plan and the run leave open

Three properties are deliberate:

- A refusal is not hidden. A checker that refuses its input still reports both
  `execution=completed` and `checker verdict=<its refusal>`; the exit code is passed
  through unchanged.
- A tool that cannot run here reports `not-started` with the reason and the exact
  remediation command, instead of skipping the plan quietly (section 8).
- Resource limits are applied only where this host accepts them, and each one is
  reported as applied or refused with its reason. On macOS, `RLIMIT_AS` is refused by
  the kernel; that is recorded rather than assumed away.

Usage:

    python3 scripts/run_bounded.py --list
    python3 scripts/run_bounded.py --plan exchange-chain
    python3 scripts/run_bounded.py --plan data-machine-sample --output-dir /tmp/adva-bounded
"""

from __future__ import annotations

import argparse
import json
import pathlib
import resource
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]

PLANS: dict[str, dict] = {
    "exchange-chain": {
        "command": [sys.executable, "-B", "-S",
                    "experiments/bounded_observation_exchange/check_exchange_chain.py"],
        "scope": "the five already retained exchange rounds and their request/reply bytes; "
                 "literal equality of the three disclosed strings only",
        "requirements": [("file", "experiments/bounded_observation_exchange/check_exchange_chain.py")],
        "remediation": "run it inside a checkout that contains the retained exchange records",
        "verdict_keys": ["status", "received_rounds"],
        "separate_keys": ["source_binding", "semantic_acceptance", "native_admission"],
        "budget": {"wall_seconds": 60, "cpu_seconds": 30, "output_bytes": 262144},
        "unknown": "whether the counterpart's sources are authenticated (they are not), and "
                   "whether any semantic acceptance follows (it does not)",
    },
    "data-machine-sample": {
        "command": ["./target/debug/adva", "data-run",
                    "programs/bounded-interpreter/interpreter.adva",
                    "--input", "programs/bounded-interpreter/input.json",
                    "--fuel", "2048", "--quantum", "17", "--output", "<run-dir>/prefix.adva"],
        "scope": "one suspended sample of the declared research data machine at profile "
                 "v0; it is not PSC0 and allocates no native identity",
        "requirements": [("file", "target/debug/adva"),
                         ("file", "programs/bounded-interpreter/interpreter.adva"),
                         ("file", "programs/bounded-interpreter/input.json")],
        "remediation": "cargo build --locked -p adva-witness --bin adva",
        "verdict_keys": ["status"],
        "separate_keys": [],
        "budget": {"wall_seconds": 60, "cpu_seconds": 30, "output_bytes": 65536},
        "unknown": "the sample suspends by declaration; it establishes no speedup, no "
                   "termination and no self interpretation",
    },
}


def apply_limits(cpu_seconds: int, output_bytes: int) -> list[dict]:
    """Install only the limits this host accepts, and report each attempt."""
    attempts = [
        ("RLIMIT_CPU", resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds)),
        ("RLIMIT_FSIZE", resource.RLIMIT_FSIZE, (output_bytes, output_bytes)),
        ("RLIMIT_AS", resource.RLIMIT_AS, (768 * 1024 * 1024,) * 2),
    ]
    applied = []
    for name, which, value in attempts:
        try:
            resource.setrlimit(which, value)
            applied.append({"limit": name, "state": "applied", "value": value[0]})
        except (ValueError, OSError) as exc:
            applied.append({"limit": name, "state": "refused-by-host",
                            "reason": f"{type(exc).__name__}: {exc}"})
    return applied


def top_level(payload, keys: list[str]) -> dict[str, list]:
    """Facts recorded at the payload root, kept apart from nested per-row facts."""
    if not isinstance(payload, dict):
        return {}
    return {key: [payload[key]] for key in keys if key in payload}


def collect(payload, keys: list[str]) -> dict[str, list]:
    """Collect every value recorded under the given keys, wherever they appear."""
    found: dict[str, set] = {}

    def walk(node) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in keys and not isinstance(value, (dict, list)):
                    found.setdefault(key, set()).add(value)
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(payload)
    return {key: sorted(values, key=str) for key, values in sorted(found.items())}


def run_plan(name: str, plan: dict, output_dir: pathlib.Path, as_json: bool) -> int:
    budget = plan["budget"]
    output_dir.mkdir(parents=True, exist_ok=True)
    # A fresh directory per invocation: the machine refuses to overwrite an accepted
    # output, so reusing a path would report a no-clobber refusal instead of the plan.
    stamp = time.strftime("%Y%m%dT%H%M%S")
    run_dir = output_dir / f"{name}-{stamp}"
    attempt = 2
    while run_dir.exists():
        run_dir = output_dir / f"{name}-{stamp}-{attempt}"
        attempt += 1
    run_dir.mkdir(parents=True)
    missing = [path for _, path in plan["requirements"] if not (ROOT / path).exists()]
    command = [argument.replace("<output-dir>", str(output_dir)).replace("<run-dir>", str(run_dir))
               for argument in plan["command"]]

    axes: dict[str, object] = {
        "plan": name,
        "material accepted": "no" if missing else "yes",
        "missing": missing,
        "execution": "not-started",
        "applies to": plan["scope"],
        "unknown / residual": plan["unknown"],
    }
    if missing:
        axes["execution"] = f"not-started: missing {', '.join(missing)}"
        axes["remediation"] = plan["remediation"]
        write_record(output_dir, name, axes)
        emit(axes, as_json)
        return 3

    started = time.perf_counter()
    limits = apply_limits(budget["cpu_seconds"], budget["output_bytes"])
    try:
        done = subprocess.run(
            command, cwd=ROOT, check=False, capture_output=True, text=True,
            timeout=budget["wall_seconds"], preexec_fn=lambda: None,
        )
        exit_code = done.returncode
        stdout, stderr = done.stdout, done.stderr
        axes["execution"] = "completed"
    except subprocess.TimeoutExpired as expired:
        exit_code = None
        stdout = (expired.stdout or b"").decode() if isinstance(expired.stdout, bytes) else (expired.stdout or "")
        stderr = f"stopped by the declared wall limit of {budget['wall_seconds']}s"
        axes["execution"] = "stopped-by-wall-limit"
    wall = time.perf_counter() - started

    truncated = len(stdout) > budget["output_bytes"]
    stdout = stdout[: budget["output_bytes"]]
    verdict: dict[str, object] = {}
    try:
        payload = json.loads(stdout)
        verdict = {"top level": top_level(payload, plan["verdict_keys"]),
                   "repeated per row": collect(payload, plan["separate_keys"])}
    except json.JSONDecodeError:
        pairs = {key.strip(): value.strip()
                 for part in stdout.strip().splitlines()[0].split(";")
                 if "=" in part
                 for key, value in [part.split("=", 1)]}
        if pairs:
            verdict = {"top level": {key: [value] for key, value in pairs.items()}}
        else:
            verdict = {"note": "the plan declares no machine-readable verdict, and this "
                               "output carries neither JSON nor a key=value line"}

    axes.update({
        "exit code": exit_code,
        "wall seconds observed": round(wall, 3),
        "declared budget": budget,
        "limits": limits,
        "stdout truncated": truncated,
        "stderr head": stderr.strip()[:400],
    })
    axes["checker verdict"] = verdict
    write_record(output_dir, name, axes)
    emit(axes, as_json)
    return 0 if exit_code == 0 else 1


def write_record(output_dir: pathlib.Path, name: str, axes: dict) -> None:
    record = output_dir / f"bounded-run-{name}.json"
    record.write_text(json.dumps(axes, indent=2, default=str) + "\n")


def emit(axes: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(axes, indent=2, default=str))
        return
    print("these axes are reported separately on purpose; none of them is a green success "
          "by itself.\n")
    for key in ("material accepted", "execution", "checker verdict", "applies to",
                "unknown / residual", "exit code", "wall seconds observed",
                "stdout truncated", "stderr head", "remediation"):
        if key in axes:
            value = axes[key]
            if isinstance(value, dict):
                print(f"{key}:")
                for inner, items in value.items():
                    print(f"    {inner} = {items}")
            else:
                print(f"{key}: {value}")
    limits = axes.get("limits")
    if isinstance(limits, list):
        print("limits:")
        for entry in limits:
            state = entry["state"]
            detail = entry.get("reason", f"value {entry.get('value')}")
            print(f"    {entry['limit']} = {state} ({detail})")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--plan", choices=sorted(PLANS))
    parser.add_argument("--output-dir", default="/tmp/adva-bounded-run")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.list or not args.plan:
        for name, plan in PLANS.items():
            command = " ".join(plan["command"])
            print(f"{name}: {command}")
            print(f"    scope: {plan['scope']}")
            print(f"    budget: {plan['budget']}")
        return 0
    return run_plan(args.plan, PLANS[args.plan], pathlib.Path(args.output_dir), args.json)


if __name__ == "__main__":
    sys.exit(main())
