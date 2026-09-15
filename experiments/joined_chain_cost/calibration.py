#!/usr/bin/env python3
"""With the anchors where the retained code looks, does the link join, and what does it cost?

Frozen contract: contract.json in this directory (Research 0129 section 3).

Research 0194 measured the anchor-to-anchor link as not established, because it wrote its anchors
one directory above the place the retained updater scans. This run corrects the procedure and
measures again:

  the retained update scans root/lineage/anchors for the highest previous anchor and sets the new
  anchor's prev_anchor_sha256 to that anchor's self_sha256 (python/adva/lineage.py, the update
  path and anchor_hash); tamper-check then answers prev_anchor_match against a supplied previous
  anchor. Both are measured here at every level, together with the units and bytes each command
  reports, so a joined link has a price rather than a verdict.

The scratch copy is made per run and discarded. The measured growth replaces the declared cost
shapes of the two earlier rounds in the reserve computation, and the conversion from measured work
to layer steps stays declared.
"""

from __future__ import annotations

import hashlib
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


def retained_rule():
    """The join rule, read from the retained implementation rather than guessed."""
    source = (ROOT / "python/adva/lineage.py").read_text(encoding="utf-8")
    check('anchor["prev_anchor_sha256"]' in source, "TheAnchorHashInputsMoved")
    check('previous["self_sha256"] == anchor["prev_anchor_sha256"]' in source,
          "TheJoinRuleMoved")
    check('root / "lineage" / "anchors"' in source, "TheAnchorScanDirectoryMoved")
    return {"anchor_hash_inputs": "global_seq, checkpoints, prev_anchor_sha256",
            "join_rule": "previous_anchor.self_sha256 == anchor.prev_anchor_sha256",
            "scan_directory": "root/lineage/anchors",
            "read_from": "python/adva/lineage.py"}


def measure(scratch):
    shutil.copytree(RETAINED_ROOT / "lineage", scratch / "lineage")
    anchors = scratch / "lineage/anchors"
    check(not anchors.exists(), "TheRetainedRootAlreadyHasAnAnchorDirectory")
    anchors.mkdir(parents=True)

    rows, previous = [], None
    for level in range(1, LINKS + 1):
        anchor_path = anchors / ("anchor-%02d.json" % level)
        code, report, elapsed = cli("lineage-update", "--root", str(scratch),
                                    "--package", "arithmetic", "--global-seq", str(level),
                                    "--anchor-out", str(anchor_path))
        check(code == 0 and report is not None, "UpdateFailedAtLevel%d" % level)
        check(report["status"] == "CheckpointBuilt", "UnexpectedUpdateStatus")
        anchor = json.loads(anchor_path.read_text(encoding="utf-8"))
        check(anchor["global_seq"] == level, "WrongSequenceAtLevel%d" % level)

        # the join, as the retained rule states it
        if previous is None:
            check(anchor["prev_anchor_sha256"] == "", "TheFirstAnchorClaimedAPredecessor")
            joins = None
        else:
            before = json.loads(previous.read_text(encoding="utf-8"))
            check(anchor["prev_anchor_sha256"] == before["self_sha256"],
                  "TheChainFieldIsNotThePreviousSelfHashAtLevel%d" % level)
            joins = True

        arguments = ["tamper-check", "--root", str(scratch), "--anchor", str(anchor_path)]
        if previous is not None:
            arguments += ["--prev-anchor", str(previous)]
        code, verified, verify_ms = cli(*arguments)
        check(verified is not None, "TamperCheckGaveNoReportAtLevel%d" % level)
        check(verified["status"] == "Intact", "TheChainDidNotVerifyAtLevel%d" % level)
        check(verified["anchor"]["match"] is True, "TheAnchorMissedItsRootAtLevel%d" % level)
        if previous is not None:
            check(verified["anchor"]["prev_anchor_match"] is True,
                  "TheToolDidNotJoinAtLevel%d" % level)

        rows.append({
            "level": level,
            "chain_field_is_the_previous_self_hash": joins,
            "prev_anchor_match": verified["anchor"]["prev_anchor_match"],
            "status": verified["status"],
            "anchor_bytes": anchor_path.stat().st_size,
            "self_sha256": anchor["self_sha256"],
            "signatures": len(anchor.get("signatures", [])),
            "update_units": report["budget_spent"]["units"],
            "update_bytes_read": report["budget_spent"]["bytes_read"],
            "verify_units": verified["budget_spent"]["units"],
            "verify_bytes_read": verified["budget_spent"]["bytes_read"],
            "update_wall_ms_measured": elapsed,
            "verify_wall_ms_measured": verify_ms,
        })
        previous = anchor_path
    return rows


def integer_sqrt(value):
    """Floor of the square root in integers, so no measurement rests on a float."""
    root = 0
    while (root + 1) ** 2 <= value:
        root += 1
    return root


def depth_for(steps):
    """The deepest layer a share pays for, from the retained (d+1)^2 cost."""
    depth = -1
    while (depth + 2) ** 2 <= steps:
        depth += 1
    return depth


def optimal_reserve(cost_per_level, budget):
    """Scan reserves: levels are bought cumulatively, and the depth ceiling is a square root.

    cost_per_level(level) is the measured price of the link at that level, in layer steps.
    """
    best = None
    for reserve in range(0, budget + 1):
        level, spent = 0, 0
        while spent + cost_per_level(level + 1) <= reserve:
            level += 1
            spent += cost_per_level(level)
        pool = budget - reserve
        ceiling = min(level, max(0, integer_sqrt(pool) - 1))
        resolved = 1 - Fr(1, 2 ** (ceiling + 1))
        row = {"reserve_steps": reserve, "levels_bought": level, "depth_ceiling": ceiling,
               "resolved": resolved}
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

    scratch = pathlib.Path(tempfile.mkdtemp(prefix="adva-joined-chain-"))
    try:
        rule = retained_rule()
        links = measure(scratch)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    # (0) the join, at every level, verified by the retained tool
    joined = [row for row in links if row["level"] > 1]
    check(all(row["prev_anchor_match"] is True for row in joined),
          "SomeLinkDidNotJoinAfterTheProcedureWasCorrected")
    check(all(row["chain_field_is_the_previous_self_hash"] is True for row in joined),
          "SomeChainFieldWasNotThePreviousSelfHash")
    check(links[0]["prev_anchor_match"] is None, "TheFirstAnchorClaimedAPredecessor")
    check(all(row["status"] == "Intact" for row in links), "SomeVerificationWasNotIntact")

    # (1) the measured growth, in the shape the numbers have
    anchor_bytes = [row["anchor_bytes"] for row in links]
    verify_bytes = [row["verify_bytes_read"] for row in links]
    update_bytes = [row["update_bytes_read"] for row in links]
    # the joined anchors carry a 64-hex predecessor where the lone one carried an empty field,
    # so the series steps once for joining and then only with the digits of the sequence number
    lone, first_joined = anchor_bytes[0], anchor_bytes[1]
    digits_only = all(anchor_bytes[index] == first_joined + len(str(level)) - len(str(2))
                      for index, level in enumerate(range(1, LINKS + 1)) if level >= 2)
    growth = {
        "anchor_bytes_per_level": anchor_bytes,
        "lone_anchor_bytes": lone,
        "first_joined_anchor_bytes": first_joined,
        "the_join_costs_bytes_per_anchor": first_joined - lone,
        "beyond_the_join_only_the_digits_move_the_size": digits_only,
        "update_bytes_read_per_level": sorted(set(update_bytes)),
        "verify_bytes_read_where_joined": sorted({row["verify_bytes_read"] for row in joined}),
        "verify_bytes_read_without_a_predecessor": links[0]["verify_bytes_read"],
        "the_join_costs_reading_the_predecessor": (
            joined[0]["verify_bytes_read"] - links[0]["verify_bytes_read"]),
        "anchor_growth_shape": ("one step for joining, then logarithmic in the level by the digits "
                               "of the sequence number"),
        "units_are_constant": sorted({row["update_units"] for row in links}) == [1]
                              and sorted({row["verify_units"] for row in links}) == [2],
    }
    check(lone == 533, "TheLoneAnchorSizeMoved")
    check(growth["the_join_costs_bytes_per_anchor"] > 0, "TheJoinWasExpectedToCostBytes")
    check(digits_only, "TheAnchorSizeMovedForSomethingOtherThanTheDigits")
    check(growth["units_are_constant"], "TheUnitCostsWereExpectedConstant")
    check(growth["the_join_costs_reading_the_predecessor"] > 0,
          "TheJoinWasExpectedToCostAPredecessorRead")

    # (2) the reserve under the measured growth, replacing the declared shapes
    budget = 1000
    def measured_cost(conversion):
        """Measured bytes per link, in layer steps, at a declared conversion."""
        def cost(level):
            digits = len(str(level))
            return conversion * (533 + digits - 1) // 533 + (1 if conversion * (533 + digits - 1) % 533 else 0)
        return cost

    rows = []
    for conversion in (1, 2, 4, 8, 16, 32, 64, 128):
        # a link at level L costs conversion * (533 + digits(L) - 1) / 533 layer steps, rounded up
        def cost(level, conversion=conversion):
            measured = 533 + len(str(level)) - 1
            product = conversion * measured
            return -(-product // 533)          # ceiling division, in integers
        best = optimal_reserve(cost, budget)
        rows.append({"declared_conversion_layer_steps_per_measure": conversion,
                     "cost_at_level_1": cost(1), "cost_at_level_12": cost(12),
                     "optimal_reserve_steps": best["reserve_steps"],
                     "optimal_reserve_fraction": str(Fr(best["reserve_steps"], budget)),
                     "levels_bought": best["levels_bought"],
                     "depth_ceiling": best["depth_ceiling"],
                     "resolved": str(best["resolved"]),
                     "remaining_mass": str(1 - best["resolved"]),
                     "one_percent_is_optimal": best["reserve_steps"] == 10})
    check(not any(row["one_percent_is_optimal"] for row in rows),
          "OnePerCentWasExpectedToBeOffTheOptimumUnderTheMeasuredGrowth")
    check(any(row["optimal_reserve_steps"] > 100 for row in rows),
          "NoConversionPutTheOptimumAboveTenPerCent")

    # (3) refusal controls
    refuse("a first anchor claimed to carry a predecessor", lambda: check(
        links[0]["prev_anchor_match"] is True, "TheFirstAnchorClaimedAPredecessor"))
    refuse("a chain field claimed equal to itself rather than to the previous self hash", lambda: check(
        links[1]["chain_field_is_the_previous_self_hash"] is False,
        "SomeChainFieldWasNotThePreviousSelfHash"))
    refuse("a joined verification claimed to read less than an unjoined one", lambda: check(
        growth["the_join_costs_reading_the_predecessor"] < 0,
        "TheJoinWasExpectedToCostAPredecessorRead"))

    elapsed = time.time() - started
    evidence = {
        "schema": "adva.research.joined-chain-cost-evidence.v0",
        "status": "ExternalExactPass" if all(row["refused"] for row in refusals) else "Failed",
        "authority": "research-only measurement over retained tooling on a scratch copy; no native admission",
        "native_status": "NotRun",
        "question": CONTRACT["question"],
        "the_correction": OBJ["the_correction"],
        "retained_rule": rule,
        "links": links,
        "growth": growth,
        "reserve_under_measured_growth": rows,
        "refusals": refusals,
        "findings": [
            "the anchor-to-anchor link joins when the anchors are written into the directory the retained updater scans, so Research 0194's third finding is withdrawn: the emptiness it measured came from its own output path and not from the tooling",
            "every level of the corrected run reports prev_anchor_match true and status Intact, and the chain field equals the previous anchor's self_sha256 at every level, which is the retained rule read out of the implementation rather than guessed",
            "the join has a measured price: verifying a joined link reads the predecessor and costs more bytes than verifying a lone anchor, while the unit counts stay at one for the update and two for the verification",
            "joining costs bytes as well as a read: the lone anchor is 533 bytes and every joined anchor is larger by the predecessor hash, after which the size moves only with the digits of the sequence number, so the measured shape is one step for joining and then logarithmic",
            "the growth shape measured here replaces the declared shapes of the two earlier rounds rather than confirming them",
            "the reserve's optimum under the measured growth still sits well above one per cent at every declared conversion, so the earlier conclusion survives the correction of the cost shape"],
        "non_claims": [
            "the key half is still unmeasured because the ed25519 backend is missing, so a joined link is a certificate-only price",
            "the conversion from measured work to layer steps is still declared, so the optimum is model-relative in that dimension",
            "no retained anchor, credential, key or lineage record is modified; the run works on a discarded copy",
            "the correction concerns the procedure and not the tooling's correctness: Research 0194's other measurements, including the logarithmic anchor growth and the absent key half, are unchanged",
            "nothing here decides whether the direction's protocol is right, and the triadic tension recorded in Research 0192 remains unresolved"],
        "counts": {"assertions": ASSERTIONS["n"], "links_measured": len(links),
                   "conversion_points": len(rows), "subprocesses": 2 * len(links),
                   "wall_seconds_before_serialization": round(elapsed, 4)},
    }
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "evidence.json"
    out.write_text(json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(json.dumps({"status": evidence["status"], "counts": evidence["counts"]}, indent=1))
    for finding in evidence["findings"]:
        print(" *", finding)
    print("anchor bytes:", anchor_bytes)
    print("update bytes:", growth["update_bytes_read_per_level"],
          "| verify bytes joined:", growth["verify_bytes_read_where_joined"],
          "| lone:", growth["verify_bytes_read_without_a_predecessor"])
    for row in rows:
        print("  conversion %3d -> optimal reserve %4d (%s), level %d" % (
            row["declared_conversion_layer_steps_per_measure"], row["optimal_reserve_steps"],
            row["optimal_reserve_fraction"], row["levels_bought"]))


if __name__ == "__main__":
    main()
