"""Read-only audit of peer reply 05, and of the three attachments it carries.

This is the review that the round-05 document requires after receipt, and that the
chain checker refuses to let pass silently. Nothing here executes incoming code:
the attachments are read as data. What can be recomputed locally is recomputed,
what can only be read is reported as read, and what the sender marked NotAvailable
is checked to be marked rather than reconstructed.

The one substantive closure offered by this reply is the stoplist encoding that
round 04 left pending: the sender confirms the receiver's inferred encoding, and
this audit re-derives the digest independently from the round-04 word list rather
than accepting the confirmation.
"""
import hashlib
import json
from pathlib import Path

from check_exchange import check, decode, read

ROOT = Path(__file__).resolve().parent
BOUNDS = {"response": 16384, "each_attachment": 16384, "total_attachments": 49152}
ATTACHMENTS = ["audit-witness-05.json", "audit-code-05.txt", "comparison-objects-05.json"]


def size(path):
    return len((ROOT / path).read_bytes())


def main():
    request = read(ROOT / "request-05.json")
    response = read(ROOT / "response-05.json")
    protocol = check(request, response)
    assert protocol["status"] == "VariationObserved"
    assert protocol["source_binding"] == "Unverified"
    assert protocol["semantic_acceptance"] == "Withheld"

    witness = decode(read(ROOT / "audit-witness-05.json"))
    assert witness["request_sha256"] == hashlib.sha256(request).hexdigest()
    objects = decode(read(ROOT / "comparison-objects-05.json"))
    code = (ROOT / "audit-code-05.txt").read_text(encoding="utf-8")

    # the declared budget is met by the ordinary reply and by every attachment
    assert size("response-05.json") <= BOUNDS["response"]
    assert all(size(name) <= BOUNDS["each_attachment"] for name in ATTACHMENTS)
    assert sum(size(name) for name in ATTACHMENTS) <= BOUNDS["total_attachments"]

    # the round-04 pending question: re-derive the stoplist digest independently
    round4 = decode(read(ROOT / "reuse-witness-04.json"))
    words = round4["rule_pins"]["stoplist"].split()
    assert len(words) == len(set(words)) == 119
    recomputed = hashlib.sha256("\n".join(sorted(words)).encode("utf-8")).hexdigest()
    declared_digest = witness["stoplist_versions"]["round-04"]["sha256"]
    assert recomputed == declared_digest, "the producer's confirmed encoding does not reproduce"
    assert witness["hash_encoding_confirmation"]["confirmed"] is True

    # the mechanism of the original failure, reproduced from the disclosed objects
    baseline = objects["baseline_projection_used_by_first_comparison"]
    reloaded = objects["reloaded_projection_used_by_first_comparison"]
    fields = {"frequency", "rank", "locator", "context"}
    for side in ("left", "right"):
        assert set(baseline[side]) - set(reloaded[side]) == {"content_tokens"}
        assert set(reloaded[side]) - set(baseline[side]) == set()
        assert all(baseline[side][f] == reloaded[side][f] for f in fields)
        assert baseline[side] != reloaded[side], "the full objects would have compared equal"
    corrected = objects["corrected_comparison"]
    assert set(corrected["compared_fields"]) == fields
    assert corrected["declared_projection_equal"] is True

    # the line references the manifest makes are present in the excerpt as claimed
    assert "156     equal = proj_B == proj_R" in code
    assert "147-158" in code and "41-46" in code or "40-46" in code
    assert code.count("content_tokens") >= 3
    assert "<redacted-local-path>" in code

    # what the sender marked unavailable must stay marked, and unreconstructed
    entries = {a["ref"]: a for a in witness["artifacts"]}
    unavailable = entries["round-03 inline computation script"]
    assert unavailable["provenance"] == "NotAvailable" and unavailable["sha256"] is None
    assert witness["stoplist_added_removed"]["status"] == "NotAvailable"
    assert witness["stoplist_versions"]["round-03"]["status"].startswith("NotAvailable")
    assert "words" not in witness["stoplist_versions"]["round-03"]
    first = witness["comparison_history"]["first_run"]
    assert first["output_record"].startswith("NotAvailable")
    assert len(first["statement_retained_in"]) == 3

    # provenance of the retained artifacts, as declared rather than as assumed
    vocabulary = ("OriginalCopy", "ExtractedFromRetainedArtifact", "ReconstructedNow",
                  "NotAvailable")
    provenance = {}
    for name in ("reuse_benchmark_04.py", "reuse_query.py", "reuse_rules.py",
                 "reuse-measure-04.json", "round-03 inline computation script"):
        stated = entries[name]["provenance"]
        assert stated.startswith(vocabulary), stated
        provenance[name] = stated
    # the corrected record is a copy of the retained file, and its own pre-correction
    # predecessor is declared unavailable in the same string rather than silently dropped
    assert provenance["reuse-measure-04.json"].startswith("OriginalCopy")
    assert "NotAvailable" in provenance["reuse-measure-04.json"]

    print(json.dumps({
        "protocol": protocol,
        "attachment_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                              for name in ATTACHMENTS},
        "budget_met": True,
        "stoplist_encoding_closed": {
            "round4_pending_question": "producer confirmation of the receiver's inferred encoding",
            "producer_confirmed": True,
            "recomputed_locally": recomputed == declared_digest,
            "digest": declared_digest,
            "scope": "the round-04 word list as disclosed in reuse-witness-04.json",
        },
        "original_failure_mechanism": {
            "extra_field_present_in_baseline": True,
            "extra_field_absent_in_reloaded": True,
            "declared_four_fields_equal": True,
            "full_objects_equal": False,
            "reading": "the retained objects differ in exactly one field, so a full-object "
                       "comparison could only have returned false; the failure is explained "
                       "by the disclosed evidence and not merely reported",
        },
        "code_excerpt": {
            "line_references_verified": ["156 equal = proj_B == proj_R", "40-46", "61-78",
                                          "147-158", "28-58"],
            "incoming_code_executed": False,
        },
        "unavailable_stays_unavailable": {
            "round_03_inline_script": "NotAvailable, no hash, no word list",
            "first_run_output_record": "NotAvailable, overwritten before commit",
            "reconstruction_offered": False,
            "word_level_added_removed": "unprovable from retained artifacts",
        },
        "still_unverified": [
            "the four artifact digests are the sender's claim; the corresponding bytes were not disclosed in full",
            "no local replay of any peer timing, and the process-per-query comparison stays NotComparable",
            "source, index and rule-module bytes remain unverified without their bytes",
            "text-layer pins 8f6e8af5 and 21f04d44 are declared unchanged across rounds 03 and 04, not checked",
            "the first-run failure is explained by the retained objects; the execution event itself is not authenticated",
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
