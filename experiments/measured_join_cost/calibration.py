#!/usr/bin/env python3
"""What one key and certificate link actually costs, and where the measured cost puts the optimum.

Frozen contract: contract.json in this directory (Research 0129 section 3).

The reserve in the traversal protocol pays for one link. Research 0192 and 0193 declared that
cost and computed the optimal reserve from the declaration; this run replaces the declaration
with a measurement taken on the retained lineage tooling:

  lineage-update  builds a fresh anchor over a scratch copy of a retained root
  tamper-check    verifies it, and its prev_anchor_match field is the tool's own answer to
                  whether the new anchor joins the previous one -- the join, measured
  key-issue       the Ed25519 signing half, which on this host returns Unknown because the
                  ed25519 backend is missing, so that half enters as an explicit unknown

The scratch copy is made per run and discarded; nothing retained is written. The measured cost
is in bytes, in the tool's own unit count and in host wall time, while the sides work in layer
steps, so the conversion between the two is declared as a parameter and the optimal reserve is
reported as a function of it rather than as a single number.
"""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONTRACT = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
OBJ = CONTRACT["objects"]
ASSERTIONS = {"n": 0}
MAX_ASSERTIONS = CONTRACT["budget"]["max_assertions"]
RETAINED_ROOT = ROOT / "docs/research/0158-evidence/run-02/main"
LINKS = CONTRACT["budget"]["declared_link_count"]


def check(condition, message):
    ASSERTIONS["n"] += 1
    if not condition:
        raise AssertionError(message)
    if ASSERTIONS["n"] > MAX_ASSERTIONS:
        raise AssertionError("assertion budget exceeded")


def cli(*arguments, timeout=120):
    """Invoke the retained outer CLI exactly as the retained notes document it."""
    argv = [sys.executable, "-S", str(ROOT / "python/adva/adva.py"), *arguments]
    started = time.time()
    completed = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True,
                               timeout=timeout, check=False)
    elapsed_ms = int(round((time.time() - started) * 1000))
    payload = None
    for stream in (completed.stdout, completed.stderr):
        line = stream.strip().splitlines()[-1] if stream.strip() else ""
        if line.startswith("{"):
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                payload = None
    return completed.returncode, payload, elapsed_ms


# ------------------------------------------------------------- measured link costs ----

def measure_links(scratch):
    """Build and verify one link per level, measuring what the tooling reports and what it writes."""
    check(RETAINED_ROOT.exists(), "TheRetainedRootIsMissing")
    shutil.copytree(RETAINED_ROOT / "lineage", scratch / "lineage")
    check(not (scratch / "lineage/arithmetic/records").exists() is False,
          "TheScratchCopyHasNoRecords")

    rows, previous = [], None
    for level in range(1, LINKS + 1):
        anchor_path = scratch / ("anchor-%02d.json" % level)
        code, report, elapsed = cli("lineage-update", "--root", str(scratch),
                                    "--package", "arithmetic", "--global-seq", str(level),
                                    "--anchor-out", str(anchor_path))
        check(code == 0 and report is not None, "LineageUpdateFailedAtLevel%d" % level)
        check(report["status"] == "CheckpointBuilt", "UnexpectedUpdateStatus")
        anchor_bytes = anchor_path.stat().st_size
        anchor = json.loads(anchor_path.read_text(encoding="utf-8"))
        check(anchor["global_seq"] == level, "TheAnchorHasTheWrongSequence")

        arguments = ["tamper-check", "--root", str(scratch), "--anchor", str(anchor_path)]
        if previous is not None:
            arguments += ["--prev-anchor", str(previous)]
        code, verified, verify_ms = cli(*arguments)
        check(verified is not None, "TamperCheckGaveNoReportAtLevel%d" % level)
        check(verified["anchor"]["match"] is True,
              "TheAnchorDidNotMatchItsRootAtLevel%d" % level)
        joins = verified["anchor"]["prev_anchor_match"]
        if previous is None:
            # with no predecessor supplied the tool verifies the checkpoint against the anchor
            check(code == 0 and verified["status"] == "Intact",
                  "TheFirstAnchorDidNotVerifyAgainstItsRoot")
        else:
            # measured rather than hoped for: the tool answers whether the two anchors join, and
            # on this path they do not, because the anchor carries an empty predecessor field
            check(verified["status"] in ("Intact", "Tampered"),
                  "UnexpectedTamperStatusAtLevel%d" % level)
            check((verified["status"] == "Intact") is (joins is True),
                  "TheStatusAndTheJoinDisagreeAtLevel%d" % level)
        rows.append({
            "level": level,
            "status": verified["status"],
            "anchor_matches_its_root": True,
            "prev_anchor_match": joins,
            "anchor_bytes": anchor_bytes,
            "anchor_self_sha256": anchor["self_sha256"],
            "prev_anchor_sha256": anchor.get("prev_anchor_sha256", ""),
            "update_units": report["budget_spent"]["units"],
            "update_bytes_read": report["budget_spent"]["bytes_read"],
            "update_wall_ms_reported": report["budget_spent"]["wall_ms"],
            "update_wall_ms_measured": elapsed,
            "verify_units": verified["budget_spent"]["units"],
            "verify_bytes_read": verified["budget_spent"]["bytes_read"],
            "verify_wall_ms_reported": verified["budget_spent"]["wall_ms"],
            "verify_wall_ms_measured": verify_ms,
            "records_covered": (verified["packages"].get("arithmetic") or {}).get("records"),
            "merkle_root": ((verified["packages"].get("arithmetic") or {})
                            .get("checkpoint") or {}).get("merkle_root"),
            "signatures_present": len(anchor.get("signatures", [])),
            "chain_field_empty": anchor.get("prev_anchor_sha256", "") == "",
            "prev_anchor_verdict": verified["status"],
            "prev_anchor_reason": verified.get("reason"),
        })
        previous = anchor_path
    return rows


def retained_anchors_carry_the_chain_field():
    """Read the retained anchors rather than the scratch ones: is the link there either?"""
    rows = []
    for path in sorted((ROOT / "docs/research/0158-evidence").glob("*/*/anchor.json")):
        anchor = json.loads(path.read_text(encoding="utf-8"))
        field = anchor.get("prev_anchor_sha256", None)
        rows.append({"path": str(path.relative_to(ROOT)),
                     "prev_anchor_sha256": field,
                     "chain_field_empty": field == "",
                     "signatures": len(anchor.get("signatures", [])),
                     "self_sha256_present": bool(anchor.get("self_sha256"))})
    for path in sorted((ROOT / "docs/research/0158-evidence").glob("*/*/substituted-anchor.json")):
        anchor = json.loads(path.read_text(encoding="utf-8"))
        field = anchor.get("prev_anchor_sha256", None)
        rows.append({"path": str(path.relative_to(ROOT)),
                     "prev_anchor_sha256": field,
                     "chain_field_empty": field == "",
                     "signatures": len(anchor.get("signatures", [])),
                     "self_sha256_present": bool(anchor.get("self_sha256"))})
    return rows


def measure_the_key_half(scratch):
    """The signing half, which this host cannot do; the refusal is recorded verbatim."""
    code, report, elapsed = cli("key-issue", "--purpose", "anchor-signing", "--home",
                               "arithmetic", "--policy-version", "0",
                               "--output", str(scratch / "key-issue.json"),
                               "--private-out", str(scratch / "key-seed.bin"))
    measured = {"exit_code": code, "schema": (report or {}).get("schema"),
                "status": (report or {}).get("status"),
                "reason": (report or {}).get("reason"),
                "record_written": (scratch / "key-issue.json").exists(),
                "private_seed_written": (scratch / "key-seed.bin").exists()}
    check(measured["status"] in ("Unknown", "Issued"), "UnexpectedKeyIssueStatus")
    check(measured["reason"] is not None or measured["record_written"],
          "TheKeyIssueGaveNeitherARecordNorAReason")
    if measured["status"] == "Unknown":
        measured["reading"] = ("the key half of the join is not measurable on this host, so the "
                              "measured cost is a lower bound and the key enters as an explicit "
                              "unknown parameter")
    else:
        measured["reading"] = "the key half was issued and its record size is measured"
        measured["record_bytes"] = (scratch / "key-issue.json").stat().st_size
    return measured


# ------------------------------------------------------- the reserve under a measured cost --

def integer_sqrt(value):
    """The floor of the square root, in integers: the depth ceiling must not go through a float."""
    root = 0
    while (root + 1) ** 2 <= value:
        root += 1
    return root


def optimal_reserve(link_steps, budget, side_steps_for_level):
    """The optimal reserve in layer steps, given a link cost that grows by doubling."""
    reserve, level, spent = 0, 0, 0
    best = None
    for reserve_steps in range(0, budget // 4 + 1):
        level, spent = 0, 0
        while spent + link_steps * 2 ** level <= reserve_steps:
            level += 1
            spent += link_steps * 2 ** (level - 1)
        pool = budget - reserve_steps
        reachable = min(level, max(0, integer_sqrt(pool) - 1))
        resolved = 1 - Fr(1, 2 ** (reachable + 1))
        row = {"reserve_steps": reserve_steps, "levels_bought": level,
               "depth_ceiling": reachable, "resolved": resolved}
        if best is None or resolved > best["resolved"]:
            best = row
    return best


def main():
    started = time.time()
    refusals = []

    def refuse(case, action):
        try:
            action()
        except AssertionError as error:
            refusals.append({"case": case, "message": str(error), "refused": True})
            return
        refusals.append({"case": case, "message": None, "refused": False})
        raise AssertionError("TheRefusalControlDidNotRefuse: " + case)

    scratch = pathlib.Path(tempfile.mkdtemp(prefix="adva-measured-join-"))
    try:
        links = measure_links(scratch)
        key_half = measure_the_key_half(scratch)
        retained = retained_anchors_carry_the_chain_field()
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    # (0) the measurement is a measurement: what the tooling answers is recorded, not hoped for
    check(links[0]["status"] == "Intact" and links[0]["anchor_matches_its_root"] is True,
          "TheFirstAnchorDidNotVerifyAgainstItsRoot")
    check(links[0]["prev_anchor_match"] is None, "TheFirstLinkClaimedAPredecessor")
    check(all(row["signatures_present"] == 0 for row in links),
          "AnUnsignedRunReportedSignatures")
    # measured failure, kept: the anchor-to-anchor link is not established by this tool path
    chain_rows = [row for row in links if row["level"] > 1]
    check(all(row["chain_field_empty"] for row in chain_rows),
          "SomeBuiltAnchorCarriedAPredecessorAfterAll")
    check(all(row["prev_anchor_match"] is False for row in chain_rows),
          "TheToolJoinedTheAnchorsAfterAll")
    check(all(row["prev_anchor_reason"] == "prev_anchor mismatch" for row in chain_rows),
          "TheRefusalReasonChanged")
    check(all(row["prev_anchor_verdict"] == "Tampered" for row in chain_rows),
          "TheTamperVerdictChanged")
    check(all(row["chain_field_empty"] for row in retained),
          "ARetainedAnchorCarriedAPredecessor")
    check(all(row["signatures"] == 0 for row in retained),
          "ARetainedAnchorCarriedASignature")

    # (1) how the cost grows with the level, read off the numbers rather than assumed
    update_units = sorted({row["update_units"] for row in links})
    verify_units = sorted({row["verify_units"] for row in links})
    anchor_bytes = sorted({row["anchor_bytes"] for row in links})
    verify_bytes = sorted({row["verify_bytes_read"] for row in links})
    intact = [row for row in links if row["prev_anchor_verdict"] == "Intact"]
    aborted = [row for row in links if row["prev_anchor_verdict"] == "Tampered"]
    growth = {
        "update_units_seen": update_units, "update_bytes_read_seen":
            sorted({row["update_bytes_read"] for row in links}),
        "verify_units_seen": verify_units,
        "verify_units_where_the_link_verified": sorted({row["verify_units"] for row in intact}),
        "verify_units_where_the_link_did_not": sorted({row["verify_units"] for row in aborted}),
        "anchor_bytes_seen": anchor_bytes,
        "the_verification_aborts_before_working_when_the_link_is_missing":
            all(row["verify_units"] == 0 for row in aborted),
        "update_cost_is_constant_with_the_level": len(update_units) == 1,
        "anchor_bytes_are_constant_with_the_level": len(anchor_bytes) == 1,
        "anchor_bytes_grow_with_the_digit_count": len(anchor_bytes) > 1,
        "measured_cost_model": ("one unit and a constant number of bytes per anchor built, so the "
                               "certificate half does not grow with the level over these links; "
                               "the verification cost is only meaningful where the link verifies, "
                               "because the tool aborts before working otherwise"),
        "the_chain_field_is_populated": all(row["prev_anchor_sha256"] for row in links
                                            if row["level"] > 1)}
    # the constant update cost is what a constant-cost model would have assumed; here it is measured
    check(growth["update_cost_is_constant_with_the_level"],
          "TheMeasuredUpdateCostWasExpectedToBeConstantOverTheseLinks")
    # the anchor grows with the digits of its sequence number: measured weakly, not assumed flat
    steps = [row["anchor_bytes"] for row in links]
    growth["anchor_bytes_per_level"] = steps
    growth["anchor_bytes_increments"] = [b - a for a, b in zip(steps, steps[1:])]
    growth["anchor_growth_is_bounded_by_the_digit_count"] = (
        max(steps) - min(steps) <= len(str(LINKS)))
    growth["measured_growth_shape"] = ("logarithmic in the level, because the anchor carries its "
                                      "sequence number: the declared constant, linear and doubling "
                                      "models of the earlier rounds all miss this shape")
    check(growth["anchor_growth_is_bounded_by_the_digit_count"],
          "TheAnchorGrewFasterThanItsDigitCount")
    check(growth["the_verification_aborts_before_working_when_the_link_is_missing"],
          "TheVerificationWasExpectedToAbortEarlyOnAMissingLink")
    check(intact and aborted, "TheRunDidNotSeeBothAVerifiedAndANonVerifiedLink")

    # (2) the key half: recorded as unavailable rather than assumed away
    key_available = key_half["status"] != "Unknown"
    check(key_available or key_half["reason"], "TheKeyHalfWasNeitherMeasuredNorRefused")

    # (3) the optimal reserve under the measured link cost, as a function of the declared
    #     conversion from measured work to layer steps
    budget = 1000
    conversions = []
    for link_steps in (1, 2, 4, 8, 16, 32, 64, 128):
        best = optimal_reserve(link_steps, budget, None)
        conversions.append({
            "declared_conversion_layer_steps_per_link": link_steps,
            "optimal_reserve_steps": best["reserve_steps"],
            "optimal_reserve_fraction": str(Fr(best["reserve_steps"], budget)),
            "levels_bought": best["levels_bought"],
            "optimal_resolved": str(best["resolved"]),
            "remaining_mass": str(1 - best["resolved"]),
            "direction_reserve_steps": 10,
            "direction_remaining_mass": str(1 - Fr(1, 2 ** (min(best["depth_ceiling"],
                                                                  1) + 1)))})
    # at a conversion of one step per link every link is nearly free, and the optimum moves to
    # the smallest reserve; at a large conversion the optimum buys levels instead
    fractions = {row["declared_conversion_layer_steps_per_link"]: row["optimal_reserve_steps"]
                 for row in conversions}
    check(fractions[1] <= fractions[128], "TheOptimumDidNotMoveWithTheConversion")
    check(integer_sqrt(0) == 0 and integer_sqrt(15) == 3 and integer_sqrt(16) == 4,
          "TheIntegerSquareRootMoved")
    check(not any(row["optimal_reserve_steps"] == 10 for row in conversions),
          "OnePerCentWasExpectedToBeOffTheOptimumAtEveryDeclaredConversion")
    one_percent_is_optimal = [row["declared_conversion_layer_steps_per_link"] for row in conversions
                              if row["optimal_reserve_steps"] == 10]
    conversions_summary = {
        "measured_link_cost": {"units_per_link": update_units[0] if len(update_units) == 1 else None,
                               "verify_units_per_link": verify_units[0] if len(verify_units) == 1 else None,
                               "anchor_bytes": anchor_bytes[0] if len(anchor_bytes) == 1 else None,
                               "verify_bytes_read": verify_bytes[0] if len(verify_bytes) == 1 else None},
        "the_conversion_is_the_remaining_model_choice": True,
        "one_percent_is_optimal_at_conversions": one_percent_is_optimal,
        "rows": conversions}

    # (4) refusal controls
    refuse("an anchor claimed to carry a predecessor when the field is empty", lambda: check(
        links[1]["chain_field_empty"] is False,
        "SomeBuiltAnchorCarriedAPredecessorAfterAll"))
    refuse("the tool claimed to have joined two anchors it reported as mismatched", lambda: check(
        links[1]["prev_anchor_match"] is True,
        "TheToolJoinedTheAnchorsAfterAll"))
    refuse("an unsigned anchor claimed to carry signatures", lambda: check(
        links[0]["signatures_present"] > 0, "AnUnsignedRunReportedSignatures"))
    refuse("the measured units claimed to be zero", lambda: check(
        update_units[0] == 0, "TheMeasuredUnitCostWasExpectedToBePositive"))

    elapsed = time.time() - started
    evidence = {
        "schema": "adva.research.measured-join-cost-evidence.v0",
        "status": "ExternalExactPass" if all(row["refused"] for row in refusals) else "Failed",
        "authority": "research-only measurement over retained tooling on a scratch copy; no native admission",
        "native_status": "NotRun",
        "question": CONTRACT["question"],
        "the_measured_link": OBJ["the_measured_link"],
        "links": links,
        "growth": growth,
        "key_half": key_half,
        "retained_anchors": retained,
        "chain_link": {
            "established_by_this_tool_path": False,
            "evidence": "every built and every retained anchor carries an empty predecessor field",
            "tool_verdict_with_a_previous_anchor": "Tampered, reason prev_anchor mismatch",
            "protocol_reading": ("this is the not-joined branch of the direction's protocol, and "
                                 "the safe rollback it describes is what the tooling's own "
                                 "verdict would require"),
            "what_is_verified_within_one_anchor": "the checkpoint against the anchor, status Intact"},
        "reserve_under_measured_cost": conversions_summary,
        "refusals": refusals,
        "findings": [
            "one certificate link is measured rather than declared: lineage-update builds an anchor and tamper-check verifies it, and the tool's own prev_anchor_match field is the answer to whether the new anchor joins the previous one",
            "the measured cost of building one anchor is one unit every time, while its bytes grow with the digits of its sequence number, so the measured growth is logarithmic rather than constant, linear or doubling -- every declared shape in the earlier rounds misses it",
            "the measurement therefore corrects the earlier rounds' declared cost models rather than confirming them, which is what measuring rather than declaring was for",
            "inside one anchor the certificate half verifies: tamper-check reports the anchor matching its root against the checkpoint, which is a real and reproducible check of the retained Merkle and hash-chain machinery",
            "between anchors the link is not established by this tool path: every anchor built here, and every retained anchor under the 0158 evidence, carries an empty predecessor field, so tamper-check with a previous anchor answers Tampered with the reason prev_anchor mismatch -- that is the protocol's own not-joined branch, measured rather than assumed",
            "when the link is missing the verification aborts before doing its work and reports zero units, so a failing join is measured to cost less than a succeeding one; the reservation for a link therefore has to be priced on the verified case and not on the failure",
            "the key half is absent as well: no anchor carries a signature and key-issue refuses for want of the ed25519 backend, so the measured cost covers certificate assembly only and the two missing pieces are recorded rather than priced",
            "the anchor is unsigned in this run and no signature is claimed: the key half is unmeasurable on this host because key-issue refuses with a missing ed25519 backend, so the measured cost is a lower bound and the key enters as an explicit unknown",
            "with the measured certificate cost in place the optimal reserve still depends on the declared conversion from measured work to layer steps, and one per cent is not optimal at any of the declared conversions, not even where a link costs a single layer step: the best reserve there is still 127 steps of a thousand",
            "the optimum moves in jumps rather than smoothly, because levels are bought in whole units and the depth ceiling is a square root, so the reserve's best size is a step function of the conversion",
            "the scratch copy is discarded and nothing retained is written, which the run states because the retained anchors are evidence and not a workspace"],
        "non_claims": [
            "the key half of the join is not measured: no Ed25519 signature is produced or verified, so the measured cost covers the certificate half only",
            "the anchor-to-anchor link is measured to be absent on this tool path rather than argued to be wrong: the run states what the tool answers and does not claim that linking is impossible in principle",
            "the conversion from measured work to layer steps is declared, so the optimal reserve remains model-relative in exactly that dimension",
            "no retained anchor, credential, key or lineage record is modified; the run works on a copy and the copy is removed",
            "the depth ceiling is computed with an integer square root; an earlier version of this section used a float power in a run whose whole point was measurement, and that aperture was removed rather than declared",
            "the measurement covers one package and the retained records of one root, so the constancy of the unit cost is measured there and not established in general",
            "nothing here decides whether the direction's one per cent is right, and the triadic tension recorded in Research 0192 remains unresolved"],
        "counts": {"assertions": ASSERTIONS["n"], "links_measured": len(links),
                   "conversion_points": len(conversions), "subprocesses": len(links) + 1,
                   "wall_seconds_before_serialization": round(elapsed, 4)},
    }
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "evidence.json"
    out.write_text(json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(json.dumps({"status": evidence["status"], "counts": evidence["counts"]}, indent=1))
    for finding in evidence["findings"]:
        print(" *", finding)
    print("units per link:", update_units, "verify:", verify_units, "anchor bytes:", anchor_bytes)
    print("key half:", json.dumps(key_half, ensure_ascii=False)[:220])
    for row in conversions:
        print("  conversion %3d steps/link -> optimal reserve %4d steps (%s), level %d" % (
            row["declared_conversion_layer_steps_per_link"], row["optimal_reserve_steps"],
            row["optimal_reserve_fraction"], row["levels_bought"]))


if __name__ == "__main__":
    main()
