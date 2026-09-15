#!/usr/bin/env python3
"""List where imprecision and host nondeterminism can enter each experiment.

Four classes are separated, because lumping them together is itself the mistake
this scan exists to find:

  binary64     real floating-point arithmetic: float(), math.sqrt/log/exp/...,
               cmath, numpy, round(), "%.Nf" formatting. These carry IEEE
               rounding, and equivalent expressions can differ.
  intmath      math.gcd / isqrt / comb / factorial / lcm, and Fraction and
               Decimal: exact. A scanner that greps for "math." reports these as
               floating point, which is a false positive this scan avoids.
  host         perf_counter, time.monotonic, time.time, getrusage, peak RSS.
               Not floating-point imprecision at all: these are run-to-run
               nondeterministic, and they break byte-identity for a different
               reason -- the same reason, in evidence terms.
  drift        random without a seed, set/dict iteration order that depends on
               hash randomisation, environment reads. Same class as host.

A construct is called acceptance-path when it appears on a line that also carries
an assertion or a comparison, so a value that can drift decides a verdict.

Usage: python3 scripts/float_aperture_scan.py [--json out.json]
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLASSES = {
    "binary64": re.compile(r"\bfloat\(|\bmath\.(?:sqrt|log|log2|log10|exp|pow|sin|cos|tan|"
                           r"asin|acos|atan|atan2|hypot|fabs|floor|ceil|trunc|fmod|degrees|"
                           r"radians|erf|gamma|lgamma|pi|e|tau|inf|nan)\b|\bcmath\b|"
                           r"\bnumpy\b|\bnp\.|round\(|%\.[0-9]*f|\.6f"),
    "intmath": re.compile(r"\bmath\.(?:gcd|isqrt|comb|factorial|lcm|prod|perm)\b|"
                          r"\bFraction\b|\bDecimal\b|\bFraction\(|\bfrom fractions\b|"
                          r"\bfrom decimal\b"),
    "host": re.compile(r"perf_counter|time\.monotonic|time\.time|getrusage|peak_rss|"
                       r"rss_|memory_info|resource\.RUSAGE"),
    "drift": re.compile(r"\brandom\.(?!seed)|hash\(|\bset\(\)|\bos\.environ"),
}
DECIDES = re.compile(r"\bassert\b|\bcheck\(|<=|>=|==|!=|isclose|<|>")


def classify(line):
    found = []
    for name, rx in CLASSES.items():
        if rx.search(line):
            found.append(name)
    return found


def scan_file(path):
    rows = []
    for i, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        classes = classify(line)
        if not classes:
            continue
        rows.append({"line": i, "classes": classes,
                     "acceptance_path": bool(DECIDES.search(line)),
                     "text": line.strip()[:90]})
    return rows


def main():
    experiments = []
    for d in sorted(p for p in (ROOT / "experiments").iterdir() if p.is_dir()):
        sources = sorted(list(d.glob("*.py")) + list(d.glob("*/calibration.py")))
        if not sources:
            continue
        rows, per_class = [], {k: 0 for k in CLASSES}
        for s in sources:
            for row in scan_file(s):
                row["file"] = s.name
                rows.append(row)
                for c in row["classes"]:
                    per_class[c] += 1
        deciding = [r for r in rows if r["acceptance_path"] and
                    ("binary64" in r["classes"] or "host" in r["classes"])]
        if not rows:
            verdict = "no-numeric-constructs"
        elif deciding:
            verdict = "imprecision-can-decide"
        elif per_class["binary64"] or per_class["host"]:
            verdict = "imprecision-in-illustration-only"
        else:
            verdict = "exact-only"
        experiments.append({"experiment": d.name, "sources": [s.name for s in sources],
                            "counts": per_class, "rows": len(rows),
                            "deciding_lines": [{"file": r["file"], "line": r["line"],
                                                "classes": r["classes"], "text": r["text"]}
                                               for r in deciding[:6]],
                            "verdict": verdict})

    # cross-check every claim that declares acceptance to be float-free
    import tomllib
    claims = tomllib.load(open(ROOT / "docs/claims.toml", "rb"))["claim"]
    declared = [c for c in claims
                if re.search(r"no floating-point value", c.get("scope", "") +
                             c.get("proof_or_certificate", ""), re.I)]
    checks = []
    for c in declared:
        files = [f.strip() for f in c["code_symbol"].split(";") if f.strip().endswith(".py")]
        offending = []
        for f in files:
            p = ROOT / f
            if not p.exists():
                offending.append({"file": f, "line": None, "note": "missing file"})
                continue
            for row in scan_file(p):
                if "binary64" in row["classes"] and row["acceptance_path"]:
                    offending.append({"file": f, "line": row["line"], "text": row["text"]})
                elif "host" in row["classes"] and row["acceptance_path"]:
                    offending.append({"file": f, "line": row["line"],
                                      "text": row["text"], "class": "host"})
        checks.append({"claim_id": c["claim_id"], "holds": not offending,
                       "offending": offending[:5]})

    summary = {}
    for e in experiments:
        summary[e["verdict"]] = summary.get(e["verdict"], 0) + 1
    report = {"experiments_scanned": len(experiments), "verdicts": summary,
              "claims_declaring_float_free_acceptance": {
                  "total": len(checks), "hold": sum(1 for c in checks if c["holds"]),
                  "details": checks},
              "experiments": experiments}
    if "--json" in sys.argv:
        out = pathlib.Path(sys.argv[sys.argv.index("--json") + 1])
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"experiments_scanned": len(experiments), "verdicts": summary,
                      "float_free_claims": report["claims_declaring_float_free_acceptance"]["total"],
                      "float_free_claims_that_hold":
                          report["claims_declaring_float_free_acceptance"]["hold"]}, indent=1))
    print("\nimprecision can decide a verdict:")
    for e in experiments:
        if e["verdict"] == "imprecision-can-decide":
            print("  %-38s %s" % (e["experiment"], e["counts"]))
            for r in e["deciding_lines"][:2]:
                print("      %s:%s %s" % (r["file"], r["line"], r["text"][:70]))
    print("\nclaims that declare float-free acceptance but do not hold:")
    for c in checks:
        if not c["holds"]:
            print("  %s" % c["claim_id"])
            for o in c["offending"][:3]:
                print("      %s:%s %s" % (o.get("file"), o.get("line"), (o.get("text") or o.get("note"))[:64]))


if __name__ == "__main__":
    main()
