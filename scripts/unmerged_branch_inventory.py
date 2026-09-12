#!/usr/bin/env python3
"""Classify every remote branch that is not yet an ancestor of main.

Two independent signals are computed for each branch and shown rather than
summarised away:

  * patch equivalence -- `git cherry` marks a commit "-" when an equivalent patch
    is already in main, and "+" when it is not. This catches work that arrived by
    another route, including a rebase or a re-authoring.
  * file state -- for every path the branch changed relative to its merge base,
    whether main now has that path byte-identical, different, or not at all.

A branch is called absorbed when either signal says the content is already in
main, superseded when main has a different version of everything it touched, and
unmerged only when it would add a path main does not have. The verdict is a rule
over the two signals; the signals are printed so the rule can be checked.

Usage: python3 scripts/unmerged_branch_inventory.py [--json out.json]
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return out.stdout


def tree_map(rev):
    """path -> blob sha for every file in a revision."""
    result = {}
    for line in git("ls-tree", "-r", rev).splitlines():
        meta, path = line.split("\t", 1)
        result[path] = meta.split()[2]
    return result


def main():
    main_map = tree_map("main")
    branches = [b.strip() for b in git("branch", "-r").splitlines() if b.strip()]
    branches = [b for b in branches if "HEAD" not in b]
    rows = []
    for branch in branches:
        ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", branch, "main"],
                                  cwd=ROOT, capture_output=True)
        if ancestor.returncode == 0:
            continue
        base = git("merge-base", "main", branch).strip()
        cherry = git("cherry", "main", branch, base).splitlines()
        absorbed_commits = sum(1 for line in cherry if line.startswith("-"))
        pending_commits = sum(1 for line in cherry if line.startswith("+"))
        ahead = int(git("rev-list", "--count", f"{base}..{branch}").strip() or 0)
        branch_map = tree_map(branch)
        changed = []
        for line in git("diff", "--name-status", base, branch).splitlines():
            if not line.strip():
                continue
            parts = line.split("\t")
            status, path = parts[0][0], parts[-1]
            changed.append((status, path))
        identical = [p for s, p in changed if main_map.get(p) == branch_map.get(p)]
        different = [p for s, p in changed
                     if p in main_map and main_map.get(p) != branch_map.get(p)]
        absent = [p for s, p in changed if p not in main_map]
        if not changed:
            verdict = "empty"
        elif pending_commits == 0 or (identical and not different and not absent):
            verdict = "absorbed"
        elif absent:
            verdict = "unmerged"
        elif different:
            verdict = "superseded"
        else:
            verdict = "absorbed"
        rows.append({
            "branch": branch,
            "base": base[:8],
            "ahead": ahead,
            "patches_already_in_main": absorbed_commits,
            "patches_not_in_main": pending_commits,
            "changed_files": len(changed),
            "identical_on_main": len(identical),
            "different_on_main": len(different),
            "absent_from_main": len(absent),
            "would_add": absent[:8],
            "would_modify": different[:8],
            "last_commit": git("log", "-1", "--date=short",
                               "--pretty=%ad %s", branch).strip(),
            "verdict": verdict,
        })
    rows.sort(key=lambda r: (r["verdict"] != "unmerged", r["verdict"] != "superseded",
                             r["last_commit"]))
    summary = {}
    for row in rows:
        summary[row["verdict"]] = summary.get(row["verdict"], 0) + 1
    report = {"branches_not_in_main": len(rows), "summary": summary, "rows": rows}
    out = Path(sys.argv[sys.argv.index("--json") + 1]) if "--json" in sys.argv else None
    if out:
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                       encoding="utf-8")
    print(json.dumps({"branches_not_in_main": len(rows), "summary": summary}, indent=1))
    for row in rows:
        print("%-9s %-52s ahead=%-3d patches+=%-3d files=%-4d same=%-4d diff=%-3d absent=%-3d %s"
              % (row["verdict"], row["branch"][:52], row["ahead"], row["patches_not_in_main"],
                 row["changed_files"], row["identical_on_main"], row["different_on_main"],
                 row["absent_from_main"], row["last_commit"][:10]))


if __name__ == "__main__":
    main()
