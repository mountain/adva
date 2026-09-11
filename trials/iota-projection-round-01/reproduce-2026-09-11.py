"""Re-run the iota/SKI substrate projection round and compare with its record.

Read-only with respect to this directory: every script runs in a fresh temporary
copy, and the committed artifacts are hashed before and after to show they were
not touched. The scripts load each other by relative path
(fullset.py -> signed.py -> reducer.py), so the whole directory must be copied
rather than a single file.

Usage:
    python3 reproduce-2026-09-11.py [--output report.json]

Exit status is 0 only if every check below passes.
"""
import argparse
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent
CHAIN = ("reducer.py", "signed.py", "fullset.py")
PRODUCED = ("results.json", "fullset-results.json")
PER_SCRIPT_TIMEOUT_S = 300
SIGNED_BYTES = (0, 7, 35, 100, 255)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_script(workdir, name):
    start = time.monotonic()
    completed = subprocess.run(
        [sys.executable, name],
        cwd=workdir,
        capture_output=True,
        text=True,
        timeout=PER_SCRIPT_TIMEOUT_S,
    )
    return {
        "script": name,
        "exit": completed.returncode,
        "seconds": round(time.monotonic() - start, 3),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def signed_rows(stdout):
    rows = {}
    for line in stdout.splitlines():
        m = re.fullmatch(r"b=(-?\d+) u=(-?\d+) v=(-?\d+) value=(-?\d+)", line)
        if m:
            b, u, v, value = (int(g) for g in m.groups())
            rows[b] = {"u": u, "v": v, "value": value}
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path)
    args = parser.parse_args()

    before = {name: digest(HERE / name) for name in (*CHAIN, *PRODUCED)}
    checks = []

    def check(name, ok, detail=""):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})
        return ok

    workdir = pathlib.Path(tempfile.mkdtemp(prefix="iota-projection-replay-"))
    try:
        # copytree, not a per-file loop: joining an absolute source name onto
        # workdir resolves back to the source and would copy files onto
        # themselves.
        shutil.copytree(HERE, workdir, dirs_exist_ok=True)
        check("copy has the import chain", all((workdir / n).is_file() for n in CHAIN))

        runs = [run_script(workdir, name) for name in CHAIN]
        for run in runs:
            check(f"{run['script']} exits 0", run["exit"] == 0,
                  run["stderr"].strip()[:200] if run["exit"] else "")

        reducer_stdout = runs[0]["stdout"]
        signed_stdout = runs[1]["stdout"]
        fullset_stdout = runs[2]["stdout"]

        check("reducer reports a status",
              '"status": "VariationObserved"' in reducer_stdout)
        check("reducer C1 combinator laws pass",
              all(f'"{k}": {{' in reducer_stdout for k in ("I", "K", "S")))
        check("signed primitive unit checks pass", "primitives ok" in signed_stdout)
        check("fullset covers every byte", "values correct: 256/256" in fullset_stdout)
        check("fullset terms stay distinct", "distinct terms: 256/256" in fullset_stdout)
        check("fullset tamper controls pass", "tamper controls: ok" in fullset_stdout)
        check("fullset round-trip passes",
              fullset_stdout.count("round-trip b=") == 4
              and all(f"round-trip b={b} -> {b} " in fullset_stdout for b in (0, 35, 100, 255)))
        check("round reaches VariationObserved", "status: VariationObserved" in fullset_stdout)

        for name in PRODUCED:
            same = (workdir / name).read_bytes() == (HERE / name).read_bytes()
            check(f"{name} reproduces byte for byte", same,
                  "" if same else f"produced {digest(workdir / name)[:16]} "
                                  f"vs committed {digest(HERE / name)[:16]}")

        rows = signed_rows(signed_stdout)
        record = json.loads((HERE / "fullset-results.json").read_text())
        sample = {r["b"]: r for r in record["sample_rows"]}
        check("signed.py printed all five sample bytes",
              sorted(rows) == list(SIGNED_BYTES), str(sorted(rows)))
        agree = [b for b in rows
                 if b in sample and all(sample[b][k] == rows[b][k] for k in ("u", "v", "value"))]
        check("signed rows agree with the retained sample_rows",
              len(agree) == len(rows) == len(SIGNED_BYTES))
        check("the signed path is exercised, not only the unsigned one",
              any(row["v"] < 0 for row in rows.values()))

        for name in (*CHAIN, *PRODUCED):
            check(f"{name} untouched by this replay", digest(HERE / name) == before[name])

        summary = {
            "schema": "aeg.iota-projection.reproduction.research",
            "version": 0,
            "date": "2026-09-11",
            "status": "Reproduced" if all(c["ok"] for c in checks) else "Mismatch",
            "authority": "external-model-only; reproduction of a retained record, "
                         "not an independent model",
            "runs": [{k: v for k, v in run.items() if k != "stdout"} for run in runs],
            "fullset_headline": {
                "values_correct": "256/256" in fullset_stdout,
                "distinct_terms": "256/256" in fullset_stdout,
                "tamper_controls_ok": "tamper controls: ok" in fullset_stdout,
            },
            "digests": {name: digest(HERE / name) for name in (*CHAIN, *PRODUCED)},
            "checks": checks,
        }

        width = max(len(c["check"]) for c in checks)
        for c in checks:
            print(f"{'PASS' if c['ok'] else 'FAIL'}  {c['check']:<{width}}  {c['detail']}")
        print()
        print("status:", summary["status"])
        for run in runs:
            print(f"  {run['script']:<14} exit={run['exit']} {run['seconds']}s")

        if args.output:
            text = json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
            args.output.open("x", encoding="utf-8").write(text)
            print("wrote", args.output)

        return 0 if summary["status"] == "Reproduced" else 1
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
