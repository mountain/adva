#!/usr/bin/env python3
"""Read-only navigation over the recorded claims, evidence and corrections.

Item one of `docs/TOOLING_WORKFLOW.md` section 6: find claims, code, evidence,
versions and follow-up corrections by question, and keep three states apart —
**historical result**, **runnable here now**, and **not yet executed**.

Two disciplines are structural rather than stylistic:

- Every conclusion line is labelled `RECORDED` (a field of `docs/claims.toml`) or
  `OBSERVED HERE` (a filesystem check this command just made). Nothing is inferred
  from a title, a headline, a word count or a green check.
- The command is read-only. It executes no claim, no experiment and no checker; it
  reports whether a declared checker and its inputs are present, which is not the
  same as having run it.

Usage:

    python3 scripts/navigate.py                       # every recorded claim
    python3 scripts/navigate.py futamura self         # by question keywords
    python3 scripts/navigate.py --claim adva.bounded-experiment.futamura-first-projection.v0
    python3 scripts/navigate.py --corrections         # follow-up correction index
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import tomllib

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLAIMS = ROOT / "docs/claims.toml"
BINARY = ROOT / "target/debug/adva"

PATHISH = re.compile(r"[A-Za-z0-9_.\-]+(?:/[A-Za-z0-9_.\-]+)+")
NOTE = re.compile(r"[A-Za-z0-9_.\-]+\.md")
CORRECTION_MARKERS = ("supersede", "supersedes", "superseded", "withdraw",
                      "withdrawn", "corrects", "correction", "作废", "更正", "撤回")
EVIDENCE_PREFIXES = ("experiments/", "docs/", "programs/", "scripts/", "tests/", "crates/")


def load_claims() -> list[dict]:
    with CLAIMS.open("rb") as handle:
        return tomllib.load(handle)["claim"]


def tokens(text: str) -> list[str]:
    """Path-like tokens of a recorded text field, deduplicated in order."""
    found: list[str] = []
    for token in PATHISH.findall(text or "") + NOTE.findall(text or ""):
        token = token.rstrip(".,;:)`")
        if token.startswith(EVIDENCE_PREFIXES) and token not in found:
            found.append(token)
    return found


def classify(claim: dict) -> dict:
    """Report recorded fields and observed file presence; infer nothing else."""
    recorded = " ".join(str(claim.get(field, "")) for field in
                        ("code_symbol", "proof_or_certificate", "scope"))
    candidates = tokens(recorded)
    evidence = [t for t in candidates if t.startswith(("experiments/", "docs/"))]
    present = [t for t in evidence if (ROOT / t).exists()]
    checkers = [t for t in candidates if t.endswith(".py") and (ROOT / t).exists()]
    needs_binary = any(("data-run" in str(claim.get(field, "")) or "target/debug/adva" in str(claim.get(field, "")))
                       for field in ("code_symbol", "proof_or_certificate"))
    if not present and not checkers:
        state = "not-yet-executed"
        why = "no evidence path or checker is recorded, or none of the recorded paths exists here"
    elif checkers and (not needs_binary or BINARY.exists()):
        state = "runnable-here"
        why = "a recorded checker exists here and its declared prerequisite is present"
        if needs_binary and not BINARY.exists():
            why = "a recorded checker exists here but the native binary is missing"
    else:
        state = "historical"
        why = ("evidence is retained but no checker runs here without a missing "
               "prerequisite")
        if not BINARY.exists() and needs_binary:
            why = "evidence is retained; the native binary that its checker drives is missing here"
    return {
        "claim_id": claim.get("claim_id"),
        "recorded_status": claim.get("status"),
        "recorded_dimension": claim.get("dimension"),
        "recorded_code_symbol": claim.get("code_symbol"),
        "dependencies": claim.get("dependencies", []),
        "evidence_paths": evidence,
        "evidence_present": present,
        "checkers_present": checkers,
        "needs_native_binary": needs_binary,
        "state": state,
        "state_reason": why,
        "recorded_boundary": (claim.get("counterexample_boundary") or "")[:240],
        "recorded_forbidden": claim.get("forbidden_conflations", []),
    }


def corrections() -> list[dict]:
    """Find recorded notes that correct, supersede or withdraw an earlier one."""
    out = []
    for folder in ("docs/research", "docs/maintenance"):
        for path in sorted((ROOT / folder).glob("*.md")):
            head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:14])
            hits = [line for line in head.splitlines()
                    if any(marker in line.lower() for marker in CORRECTION_MARKERS)]
            if not hits:
                continue
            referenced = [name for name in NOTE.findall(head)
                          if name != path.name and not name.startswith("http")]
            if referenced:
                out.append({"note": str(path.relative_to(ROOT)),
                            "markers": [hit.strip("- *")[:160] for hit in hits],
                            "corrects": sorted(set(referenced))})
    return out


def matches(claim: dict, queries: list[str]) -> bool:
    if not queries:
        return True
    haystack = " ".join(str(claim.get(field, "")) for field in
                        ("claim_id", "canonical_name", "code_symbol", "dimension",
                         "scope", "status")).lower()
    return all(query.lower() in haystack for query in queries)


def report(rows: list[dict], as_json: bool) -> None:
    if as_json:
        print(json.dumps(rows, indent=2))
        return
    print("recorded fields and observed file presence only; no conclusion is inferred "
          "from titles, headlines or word counts.")
    print(f"binary present here: {BINARY.exists()}  (target/debug/adva)\n")
    for row in rows:
        print(f"{row['claim_id']}")
        print(f"  RECORDED      status={row['recorded_status']}")
        print(f"  RECORDED      dimension={row['recorded_dimension']}")
        print(f"  OBSERVED HERE state={row['state']}  ({row['state_reason']})")
        print(f"  OBSERVED HERE evidence {len(row['evidence_present'])}/{len(row['evidence_paths'])} present"
              f"; checkers={len(row['checkers_present'])}"
              f"; needs native binary={row['needs_native_binary']}")
        if row["dependencies"]:
            print(f"  RECORDED      depends on {', '.join(row['dependencies'])}")
        print(f"  RECORDED      boundary: {row['recorded_boundary']}")
        print()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("query", nargs="*", help="keywords matched against recorded fields")
    parser.add_argument("--claim", help="one exact claim id")
    parser.add_argument("--corrections", action="store_true",
                        help="print the follow-up correction index instead of claims")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    if args.corrections:
        rows = corrections()
        if args.json:
            print(json.dumps(rows, indent=2))
        else:
            print("follow-up corrections recorded in note headers (RECORDED text; "
                  "whether the correction is complete is not decided here):\n")
            for row in rows:
                print(f"{row['note']}  corrects {', '.join(row['corrects'])}")
                for marker in row["markers"]:
                    print(f"    {marker}")
        return 0

    claims = load_claims()
    if args.claim:
        claims = [claim for claim in claims if claim.get("claim_id") == args.claim]
        if not claims:
            print(f"no recorded claim with id {args.claim}", file=sys.stderr)
            return 1
    else:
        claims = [claim for claim in claims if matches(claim, args.query)]
    rows = [classify(claim) for claim in claims]
    if args.limit:
        rows = rows[: args.limit]
    if not rows:
        print("no recorded claim matched; this is not evidence that no such work exists",
              file=sys.stderr)
        return 1
    report(rows, args.json)
    summary: dict[str, int] = {}
    for row in rows:
        summary[row["state"]] = summary.get(row["state"], 0) + 1
    if not args.json:
        print("OBSERVED HERE summary:", ", ".join(f"{k}={v}" for k, v in sorted(summary.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
