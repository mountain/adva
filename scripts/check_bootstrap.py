"""Inspect bootstrap reports; this is protocol acceptance, not a proof kernel."""
import hashlib
import json
import sys
from pathlib import Path


def check(root):
    reports = root / "reports"
    data = {name: json.loads((reports / name).read_text()) for name in
            ("arithmetic.adva", "check.json", "reuse.json", "zero.json")}
    run = data["arithmetic.adva"]
    checked, reuse, zero = (data[name] for name in ("check.json", "reuse.json", "zero.json"))
    checks = {
        "arithmetic_14": run.get("state") == "Completed" and run.get("evaluation", {}).get("values") == [14],
        "snapshot_rechecked": checked.get("status") == "SnapshotChecked",
        "exact_reuse_4": reuse.get("status") == "ReuseChecked" and reuse.get("reuse", {}).get("guarded_values") == ["4", "4"],
        "same_checked_snapshot": checked.get("snapshot_digest") is not None and checked.get("snapshot_digest") == reuse.get("snapshot_digest") == zero.get("snapshot_digest"),
        "zero_guard_refused": zero.get("status") == "Rejected" and zero.get("reuse") is None and "zero" in (zero.get("error") or "").lower(),
        "zero_exit_2": (reports / "zero.exit").read_text().strip() == "2",
        "library_unchanged": True,
    }
    pins = dict(line.split(None, 1)[::-1] for line in (root / "source-inputs.sha256").read_text().splitlines())
    checks["library_unchanged"] = all(
        hashlib.sha256((root / "library/stability" / f"epoch-{i:04}.json").read_bytes()).hexdigest()
        == pins[f"adva-library/stability/epoch-{i:04}.json"] for i in (0, 1)
    )
    # Whole snapshot bytes, including guards and assumptions, stay in both reports.
    checks["same_retained_snapshot"] = checked.get("snapshot") is not None and checked.get("snapshot") == reuse.get("snapshot") == zero.get("snapshot")
    if not all(checks.values()):
        raise ValueError(checks)
    return {"status": "PassedBootstrapAcceptance", "checks": checks,
            "scope": "Saved-report protocol checks; no new native semantic judgment"}


if __name__ == "__main__":
    print(json.dumps(check(Path(sys.argv[1]).resolve()), indent=2))
