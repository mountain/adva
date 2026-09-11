"""Bounded breakthrough continuation runs 25-124 (length 44..143).

Discipline: Research 0129 sections 3 and 4.
- One frozen contract is written per run, immediately before that run.
- Every run: search -> independent verify -> one-field tampered negative control.
- Per-run wall bound is enforced with a subprocess timeout.
- The first failed acceptance stops the batch and records Unknown with its reason.
- No automatic fuel reset, no candidate-family enlargement, no retry, no
  overwriting of any existing artifact: every write is exclusive.

The series (runs 1-24, length 20..43) was closed by user instruction. This
driver implements the new explicit authorization: 100 continuation rounds.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BIN = Path("/Users/mingli/Adva/adva/target/debug/adva-labs-search")

FIRST_RUN = 25
LAST_RUN = 124
RUN_TO_LENGTH = 19          # run N covers length N + 19
ITERATIONS = 10_000
SEED = 1
WORKERS = 1
CHECKPOINT_EVERY = 5000
WALL_LIMIT_S = 120          # per-run enforced bound, as in runs 1-24
DATE = "2026-09-11"

SUMMARY = HERE / f"continuation-summary-{FIRST_RUN + RUN_TO_LENGTH}-{LAST_RUN + RUN_TO_LENGTH}.json"


def write_exclusive(path, text):
    """Refuse to overwrite an existing artifact."""
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path.name}")
    path.write_text(text, encoding="utf-8")


def make_contract(run, length, is_first):
    contract = {
        "schema": "adva.bounded-breakthrough.contract.v0",
        "version": 0,
        "date": DATE,
        "continuation_of": f"run {run - 1} (length {length - 1})",
        "revision": {
            "reason": (
                "series closed at length 43 by user instruction; reopened by a new "
                "explicit user authorization to advance 100 further rounds"
                if is_first else
                "adjacent family length; authorized 100-round extension"
            ),
            "changed": f"length {length - 1} -> {length}",
            "unchanged": "checker, seed 1, iterations 10000, workers 1, budgets",
        },
        "1_question_and_level": {
            "input_family": f"All length-{length} binary sequences over {{-1, +1}}",
            "requested_conclusion": (
                "Within the declared budget, find and independently verify one "
                "low-energy sequence with energy and merit factor"
            ),
            "level": "Computation-level finite search; no physical interpretation",
            "resolving_witness": "Independently rechecked run report; exhaustion yields Unknown",
        },
        "2_imported_knowledge": (
            "Same finite aperiodic autocorrelation arithmetic as run 1; no new imports"
        ),
        "3_interface": (
            "Candidate sequence -> (energy, merit) via exact correlation arithmetic; "
            "report.verify() must recompute identically"
        ),
        "4_protected_obligations": [
            "No exhaustive-optimality claim at any length from this sampled search; "
            "the separate exhaustive command covers N <= 25 only and was not run",
            "Resource exhaustion reports Unknown; no automatic fuel reset",
            "No new native word or vocabulary promotion",
            "Run 1-24 evidence remains unchanged and is not overwritten",
        ],
        "5_acceptance_and_verification": {
            "checker": "adva-labs-search verify <report>",
            "success": (
                "search completes within the wall bound + independent verify command "
                "exits 0 + one-field tampered copy is rejected"
            ),
            "negative_controls": ["one-field tampered copy rejected by verify"],
        },
        "6_resources_and_exit": {
            "length": length,
            "iterations": ITERATIONS,
            "workers": WORKERS,
            "seed": SEED,
            "checkpoint_every": CHECKPOINT_EVERY,
            "wall_clock_limit_s": WALL_LIMIT_S,
            "continuation_count": run,
        },
    }
    if is_first:
        contract["authorization"] = {
            "scope": f"runs {FIRST_RUN}-{LAST_RUN} (length {FIRST_RUN + RUN_TO_LENGTH}"
                     f"..{LAST_RUN + RUN_TO_LENGTH})",
            "rounds": LAST_RUN - FIRST_RUN + 1,
            "declared_total_wall_bound_s": (LAST_RUN - FIRST_RUN + 1) * WALL_LIMIT_S,
            "enforcement": "per-run subprocess timeout plus one outer supervisor bound",
            "prior_state": (
                "the length 20-43 series (runs 1-24) was closed by user instruction; "
                "continuation required a new explicit authorization, which this run records"
            ),
            "reason_to_expect_new_evidence": (
                "each round declares a strictly new adjacent finite family length, so the "
                "family differs from every previously searched family; the series also "
                "retains a per-length energy and merit record"
            ),
        }
    return contract


def run_one(run, length, is_first):
    contract_path = HERE / f"contract-run{run}.json"
    report_path = HERE / f"run{run}-report.json"
    tampered_path = HERE / f"run{run}-tampered.json"

    write_exclusive(contract_path,
                    json.dumps(make_contract(run, length, is_first), indent=2) + "\n")

    started = time.monotonic()
    search = subprocess.run(
        [str(BIN), "search", "--length", str(length), "--iterations", str(ITERATIONS),
         "--seed", str(SEED), "--workers", str(WORKERS), "--output", str(report_path)],
        capture_output=True, text=True, timeout=WALL_LIMIT_S)
    wall = round(time.monotonic() - started, 3)

    if search.returncode != 0 or not report_path.exists():
        return {"run": run, "length": length, "status": "SearchFailed",
                "exit_code": search.returncode, "wall_s": wall,
                "stderr": (search.stderr or "").strip()[:400]}

    report = json.loads(report_path.read_text(encoding="utf-8"))

    verify = subprocess.run([str(BIN), "verify", str(report_path)],
                            capture_output=True, text=True, timeout=WALL_LIMIT_S)

    tampered = dict(report)
    tampered["best"] = dict(report["best"], energy=report["best"]["energy"] + 1)
    write_exclusive(tampered_path, json.dumps(tampered))
    neg = subprocess.run([str(BIN), "verify", str(tampered_path)],
                         capture_output=True, text=True, timeout=WALL_LIMIT_S)
    neg_stderr = (neg.stderr or "").strip()[:200]

    row = {
        "run": run,
        "length": length,
        "energy": report["best"]["energy"],
        "merit": report["best"]["merit_factor"],
        "verify_exit": verify.returncode,
        "tamper_verify_exit": neg.returncode,
        "tamper_rejected": neg.returncode != 0 and "mismatch" in neg_stderr,
        "tamper_message": neg_stderr,
        "wall_s": wall,
        "status": "Checked",
    }
    return row


def main():
    rows = []
    status, reason = "Completed", None
    for run in range(FIRST_RUN, LAST_RUN + 1):
        length = run + RUN_TO_LENGTH
        try:
            row = run_one(run, length, is_first=(run == FIRST_RUN))
        except subprocess.TimeoutExpired:
            row = {"run": run, "length": length, "status": "WallBoundExhausted",
                   "wall_s": WALL_LIMIT_S}
        except Exception as exc:                       # recorded, not hidden
            row = {"run": run, "length": length, "status": "DriverError",
                   "error": f"{type(exc).__name__}: {exc}"}
        rows.append(row)
        print(f"  run{run} length={length} {row['status']} "
              f"energy={row.get('energy')} merit={row.get('merit')} "
              f"verify={row.get('verify_exit')} neg={row.get('tamper_rejected')} "
              f"{row.get('wall_s')}s", flush=True)

        if row["status"] != "Checked" or not row["tamper_rejected"] or row["verify_exit"] != 0:
            status = "Unknown"
            reason = (f"acceptance failed at run {run} (length {length}): "
                      f"status={row['status']} verify_exit={row.get('verify_exit')} "
                      f"tamper_rejected={row.get('tamper_rejected')}")
            break

    summary = {
        "schema": "adva.bounded-breakthrough.continuation-summary.v0",
        "version": 0,
        "date": DATE,
        "authorization": "new explicit user authorization: advance 100 rounds",
        "declared_scope": {
            "first_run": FIRST_RUN, "last_run": LAST_RUN,
            "first_length": FIRST_RUN + RUN_TO_LENGTH,
            "last_length": LAST_RUN + RUN_TO_LENGTH,
            "rounds_declared": LAST_RUN - FIRST_RUN + 1,
            "iterations": ITERATIONS, "seed": SEED, "workers": WORKERS,
            "wall_clock_limit_s_per_run": WALL_LIMIT_S,
            "declared_total_wall_bound_s": (LAST_RUN - FIRST_RUN + 1) * WALL_LIMIT_S,
        },
        "status": status,
        "reason": reason,
        "rounds_executed": len(rows),
        "verify_all_zero": all(r.get("verify_exit") == 0 for r in rows),
        "tamper_all_rejected": all(r.get("tamper_rejected") for r in rows),
        "total_wall_s": round(sum(r.get("wall_s", 0) for r in rows), 3),
        "max_wall_s": max((r.get("wall_s", 0) for r in rows), default=0),
        "budget_exhausted": any(r["status"] == "WallBoundExhausted" for r in rows),
        "rows": rows,
    }
    write_exclusive(SUMMARY, json.dumps(summary, indent=2) + "\n")
    print(f"\nstatus={status} executed={len(rows)} "
          f"total_wall={summary['total_wall_s']}s")
    return 0 if status == "Completed" else 1


if __name__ == "__main__":
    sys.exit(main())
