"""Corrected three-class depth ledger; v0 remains replayable as historical evidence."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RETAINED = ROOT / "experiments/keraia_cycle_mass/evidence/attempt-1/primary.json"


def mass(code):
    if type(code) is not str or any(bit not in "01" for bit in code):
        raise ValueError("invalid cylinder")
    return Fraction(1, 2 ** len(code))


def validate_row(row):
    """The invariant is about halting knowledge, not how many labels are present."""
    accepted = Fraction(row["accepted_mass"])
    excluded = Fraction(row["certified_nonhalting_mass"])
    unresolved = Fraction(row["unresolved_mass"])
    named = Fraction(row["named_unresolved_mass"])
    decided = Fraction(row["decided_mass"])
    if not (0 <= named <= unresolved <= 1 and 0 <= accepted <= 1 and 0 <= excluded <= 1):
        raise ValueError("invalid mass range")
    if accepted + excluded + unresolved != 1 or decided != accepted + excluded:
        raise ValueError("halting partition does not close")
    if (Fraction(row["lower"]) != accepted or Fraction(row["upper"]) != 1 - excluded
            or Fraction(row["upper"]) - Fraction(row["lower"]) != unresolved):
        raise ValueError("interval width must equal unresolved mass")


def build():
    contract = json.loads((HERE / "contract-v1.json").read_text())
    for name, digest in contract["inputs"].items():
        if hashlib.sha256((HERE / name).read_bytes()).hexdigest() != digest:
            raise ValueError("frozen v0 bytes changed: " + name)
    raw = RETAINED.read_bytes()
    if hashlib.sha256(raw).hexdigest() != contract["retained_sha256"]:
        raise ValueError("retained semantic evidence changed")
    source = json.loads(raw)
    if source["status"] != "Passed":
        raise ValueError("retained campaign did not pass")
    accepted = [row["code"] for row in source["accepted_ledger"]]
    excluded = [row["certificate"]["source"] for row in source["divergence_certificates"]]
    pending = [row["source"] for row in source["unresolved_frontiers"]]
    codes = sorted(accepted + excluded + pending)
    if any(b.startswith(a) for a, b in zip(codes, codes[1:])):
        raise ValueError("overlapping cylinders")
    for key, group in (("accepted", accepted), ("certified_nonhalting", excluded),
                       ("unresolved", pending)):
        if sum(map(mass, group), Fraction()) != Fraction(*source["mass_partition"][key]):
            raise ValueError("retained class mismatch: " + key)
    if sum(map(mass, codes), Fraction()) != 1:
        raise ValueError("incomplete terminal partition")
    historical = json.loads((HERE / "evidence.json").read_text())
    costs = {row["depth"]: row for row in historical["curve"]}
    rows = []
    for depth in range(max(map(len, codes)) + 1):
        halt = sum((mass(c) for c in accepted if len(c) <= depth), Fraction())
        nonhalt = sum((mass(c) for c in excluded if len(c) <= depth), Fraction())
        named = sum((mass(c) for c in pending if len(c) <= depth), Fraction())
        row = {
            "depth": depth, "accepted_mass": str(halt),
            "certified_nonhalting_mass": str(nonhalt),
            "named_unresolved_mass": str(named),
            "decided_mass": str(halt + nonhalt),
            "unresolved_mass": str(1 - halt - nonhalt),
            "lower": str(halt), "upper": str(1 - nonhalt),
            "declared_model_cost": {key: costs[depth][key]
                                    for key in ("reserve_steps", "side_steps", "total_steps")},
        }
        validate_row(row)
        rows.append(row)
    if Fraction(rows[-1]["unresolved_mass"]) != sum(map(mass, pending), Fraction()):
        raise ValueError("final residual mismatch")
    return {
        "schema": "adva.research.depth-curve-evidence.v1",
        "status": "ExternalExactPass", "native_status": "NotRun",
        "contract_sha256": hashlib.sha256((HERE / "contract-v1.json").read_bytes()).hexdigest(),
        "retained_sha256": contract["retained_sha256"],
        "frozen_v0": contract["inputs"],
        "curve": rows,
        "correction": "v0 called accepted plus named unresolved mass decided; v1 counts only accepted plus certified nonhalting. v0 evidence is historical and not a halting-uncertainty ledger.",
        "limits": [
            "Exact arithmetic over retained outcomes; interpreter semantics are not re-run.",
            "Costs are the historical declared model, not measured Keraia execution costs.",
            "Depth 15 is the last retained cut, not an asymptotic saturation claim.",
            "No optimal-machine Omega, Q4/M6, native import, or convergence-rate claim.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", nargs="?", type=Path, default=HERE / "evidence-v1.json")
    args = parser.parse_args()
    result = build()
    with args.output.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "last": result["curve"][-1]}))


if __name__ == "__main__":
    main()
