"""Check the five received exchanges and five requests; no source authentication.

The fifth reply was reviewed on 2026-09-12 and its receipt retained in review-05.json. The
gate that used to assert the fifth reply was still absent is now the terminal check:
there is no sixth request, so the chain ends here and nothing beyond round five is
asserted.
"""
import hashlib
import json
from pathlib import Path

from check_exchange import check, decode, read

ROOT = Path(__file__).resolve().parent


def main():
    request_paths = ["request.json"] + [f"request-{n:02d}.json" for n in range(2, 6)]
    requests = [read(ROOT / name) for name in request_paths]
    responses = [read(ROOT / f"response-{n:02d}.json") for n in range(1, 6)]
    attachment_paths = {2: "word-witness-02.json", 3: "use-witness-03.json",
                        4: "reuse-witness-04.json"}
    rows = []
    for n, response in enumerate(responses, 1):
        receipt = check(requests[n - 1], response)
        assert receipt["status"] == "VariationObserved"
        assert receipt["source_binding"] == "Unverified"
        assert receipt["semantic_acceptance"] == "Withheld"
        terminal = n == len(responses)
        if terminal:
            # no sixth request is declared; the chain ends at the fifth received reply
            assert len(request_paths) == 5 and not (ROOT / "request-06.json").exists()
            next_request = None
        else:
            next_request = decode(requests[n])
            assert next_request["parent_response_sha256"] == hashlib.sha256(response).hexdigest()
        row = {"round": n, "receipt": receipt,
               "next_request": request_paths[n] if not terminal else None,
               "parent_reply_bytes_match": True}
        if terminal:
            row["terminal_round"] = True
        if n in attachment_paths:
            raw = read(ROOT / attachment_paths[n])
            attachment = decode(raw)
            assert attachment["request_sha256"] == hashlib.sha256(requests[n - 1]).hexdigest()
            assert next_request["parent_attachment_sha256"] == hashlib.sha256(raw).hexdigest()
            row["parent_attachment_bytes_match"] = True
        if not terminal:
            rejected = check(requests[n], response)
            assert rejected["status"] == "Rejected" and rejected["acknowledge"] is None
            row["old_reply_cannot_answer_next_question"] = True
        rows.append(row)
    assert (ROOT / "review-05.json").exists(), "the fifth reply must be reviewed before this checkpoint"
    print(json.dumps({"status": "DisclosedByteChainChecked", "received_rounds": 5,
                      "question_count": 5, "rows": rows, "terminal_round": 5,
                      "limits": "Five bounded requests, five bounded responses, three bounded attachments, four stale-reply controls; no search or peer code execution.",
                      "residual": "Neither parent hashes nor local acknowledgements authenticate private sources, actual execution, historical event order or semantic faithfulness."}, indent=2))


if __name__ == "__main__":
    main()
