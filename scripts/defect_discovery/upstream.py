#!/usr/bin/env python3
"""Prepare an agent-reviewed public upstream report; publish only with --publish."""
import argparse
import hashlib
import json
import pathlib
import re
import subprocess
from datetime import datetime, timezone

LIMIT = 128 * 1024


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    with path.open("rb") as f:
        data = f.read(LIMIT + 1)
    if len(data) > LIMIT:
        raise ValueError(f"artifact too large: {path.name}")
    return data


def dump(obj):
    return (json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def put(path, data):
    with path.open("xb") as f:
        f.write(data)


def prepare(candidate, out):
    c = json.loads(read(candidate))
    required = ("target", "title", "upstream_version", "invariant", "contract_url",
                "witness_key", "impact", "open_obligations", "policy_review",
                "dedup_review", "reviewed_by", "checked_at")
    if any(not isinstance(c.get(k), str) or not c[k].strip() for k in required):
        raise ValueError("missing nonempty candidate fields")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", c["target"]):
        raise ValueError("invalid target repository")
    if not c["contract_url"].startswith("https://"):
        raise ValueError("original upstream contract URL required")
    if c.get("classification") != "UpstreamContractViolation" or c.get("disclosure") != "PublicNonSecurity":
        raise ValueError("local/unknown/security findings are not eligible for this public transport")
    if c.get("public_payload_reviewed") is not True or c.get("target_allows_submission") is not True:
        raise ValueError("agent must review public payload and target contribution policy")
    existing = c.get("existing_issue_url")
    if existing and not re.fullmatch(r"https://github\.com/" + re.escape(c["target"]) + r"/issues/[1-9][0-9]*", existing):
        raise ValueError("existing issue must belong to target")
    files = {n: read(candidate.parent / n) for n in ("reproducer.py", "run-1.json", "run-2.json")}
    runs = [json.loads(files[f"run-{i}.json"]) for i in (1, 2)]
    for r in runs:
        if (r.get("evidence") != "ActualUpstreamReproduction" or r.get("violation") is not True
                or r.get("reproducer_sha256") != sha(files["reproducer.py"])
                or not r.get("command") or not r.get("environment")
                or not r.get("execution_id") or not r.get("executed_at")
                or "expected" not in r or "actual" not in r
                or dump(r["expected"]) == dump(r["actual"])):
            raise ValueError("two actual standalone reproduction records required")
    if runs[0]["execution_id"] == runs[1]["execution_id"]:
        raise ValueError("duplicate execution identity; two distinct runs required")
    if any(dump(runs[0][k]) != dump(runs[1][k]) for k in ("expected", "actual")):
        raise ValueError("replay observations differ; investigate before publishing")
    fingerprint = sha(dump({k: c[k] for k in ("target", "contract_url", "witness_key")}))
    marker = f"adva-defect:{fingerprint}"
    lines = [f"<!-- {marker} -->", "", "## Contract and observed behavior", "",
             c["invariant"], "", f"Contract: {c['contract_url']}",
             f"Version: {c['upstream_version']}; checked: {c['checked_at']}", "",
             "## Standalone reproduction", "", "````python", files["reproducer.py"].decode(), "````",
             "", "## Two retained runs", ""]
    for r in runs:
        lines += ["````json", json.dumps(r, indent=2), "````", ""]
    lines += ["## Impact and limits", "", c["impact"], "", c["open_obligations"], "",
              "## Prior-report and policy checks", "", c["dedup_review"], "", c["policy_review"], "",
              f"Report prepared by {c['reviewed_by']}, submitted through Mingli Yuan's GitHub account as an authorized proxy. Account use is not personal authorship, endorsement, review, or a correctness claim.", ""]
    body = "\n".join(lines)
    if len(body.encode()) > 60000:
        raise ValueError("public issue body exceeds bounded transport size")
    out.mkdir(parents=True, exist_ok=False)
    payload = dict(target=c["target"], title=c["title"], marker=marker,
                   existing_issue_url=existing, body=body)
    files.update({"candidate.json": dump(c), "issue.md": body.encode(), "payload.json": dump(payload)})
    for name, data in files.items():
        put(out / name, data)
    put(out / "COMPLETE.json", dump({"sha256": {n: sha(d) for n, d in files.items()}}))
    return dict(state="ReadyForAgentReview", package=str(out), marker=marker)


def verify(package):
    manifest = json.loads(read(package / "COMPLETE.json"))
    expected_names = {"candidate.json", "issue.md", "payload.json", "reproducer.py", "run-1.json", "run-2.json"}
    if set(manifest["sha256"]) != expected_names:
        raise ValueError("invalid package file set")
    for name, expected in manifest["sha256"].items():
        if sha(read(package / name)) != expected:
            raise ValueError(f"package changed after preparation: {name}")
    return json.loads(read(package / "payload.json"))


def gh(*args):
    r = subprocess.run(["gh", "api", *args], capture_output=True, text=True, timeout=30)
    if r.returncode:
        raise RuntimeError("GitHub request failed; inspect remote before retrying a publication")
    return json.loads(r.stdout)


def submit(package, publish):
    p = verify(package)
    if not publish:
        return dict(state="DryRun", target=p["target"], issue=str(package / "issue.md"))
    receipt_path = package / "SUBMISSION.json"
    if receipt_path.exists():
        return json.loads(read(receipt_path))
    if (package / "SUBMISSION_ATTEMPT.json").exists():
        raise RuntimeError("prior attempt exists without receipt; agent must inspect remote, no automatic retry")
    # Fail closed on failed/incomplete search. This is an exact-fingerprint check;
    # semantic open/closed-issue deduplication remains the agent's preceding work.
    gh(f"repos/{p['target']}")
    found = gh("--method", "GET", "search/issues", "-f",
               f"q=repo:{p['target']} is:issue \"{p['marker']}\"", "-f", "per_page=100")
    if found.get("incomplete_results") or found.get("total_count", 0) > 100:
        raise RuntimeError("dedup search incomplete")
    matches = [i for i in found.get("items", []) if p["marker"] in (i.get("body") or "")]
    if len(matches) > 1:
        raise RuntimeError("multiple existing fingerprint matches; reconcile manually")
    url = p.get("existing_issue_url") or (matches[0]["html_url"] if matches else None)
    if url:
        issue = gh(f"repos/{p['target']}/issues/{url.rsplit('/', 1)[-1]}")
        if "pull_request" in issue:
            raise ValueError("existing target is a PR, not an issue")
        state = "ExistingIssueNoNewContent"
    else:
        request = package / "request.json"
        put(request, dump({"title": p["title"], "body": p["body"]}))
        put(package / "SUBMISSION_ATTEMPT.json", dump(dict(target=p["target"], marker=p["marker"],
              attempted_at=datetime.now(timezone.utc).isoformat(), body_sha256=sha(p["body"].encode()))))
        issue = gh("--method", "POST", f"repos/{p['target']}/issues", "--input", str(request))
        url = issue["html_url"]
        state = "SubmittedNotUpstreamConfirmed"
    receipt = dict(state=state, url=url, target=p["target"], marker=p["marker"],
                   checked_at=datetime.now(timezone.utc).isoformat(),
                   prepared_body_sha256=sha(p["body"].encode()),
                   remote_body_sha256=sha((issue.get("body") or "").encode()))
    put(receipt_path, dump(receipt))
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("candidate", type=pathlib.Path)
    prep.add_argument("--out", type=pathlib.Path, required=True)
    pub = sub.add_parser("submit")
    pub.add_argument("package", type=pathlib.Path)
    pub.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    try:
        result = prepare(args.candidate, args.out) if args.action == "prepare" else submit(args.package, args.publish)
        print(json.dumps(result))
        return 0
    except (ValueError, KeyError, OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        parser.exit(2, f"Not submitted: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
