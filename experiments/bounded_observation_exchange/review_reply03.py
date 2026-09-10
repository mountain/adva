"""Fixture audit of the third peer reply; cannot authenticate its private sources."""
import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path

from check_exchange import check, decode, read

ROOT = Path(__file__).resolve().parent


def main():
    request = read(ROOT / "request-03.json")
    response = read(ROOT / "response-03.json")
    raw = read(ROOT / "use-witness-03.json")
    witness = decode(raw)
    protocol = check(request, response)
    assert protocol["status"] == "VariationObserved"
    assert witness["request_sha256"] == hashlib.sha256(request).hexdigest()
    assert witness["target"] == "use"
    rows = []
    for side, expected in (("left", (21, 61)), ("right", (234, 22))):
        item = witness[side]
        tokens = re.findall(r"[A-Za-z][A-Za-z'-]*|[0-9]+", item["excerpt"].lower())
        positions = [i for i, word in enumerate(tokens) if word == "use"]
        assert len(tokens) <= 25 and len(positions) == 1
        assert 2 <= positions[0] <= len(tokens) - 3
        assert type(item["frequency"]) is int and type(item["rank"]) is int
        assert (item["frequency"], item["rank"]) == expected
        rows.append({"side": side, "excerpt_token_count": len(tokens),
                     "frequency_rank_agrees_with_previous_claim": True})
    costs = witness["cost"]
    gap = (Decimal(str(costs["total_measured_seconds"]))
           - Decimal(str(costs["tokenize_and_rank_seconds"]))
           - Decimal(str(costs["context_seconds"])))
    assert gap >= 0
    print(json.dumps({"protocol": protocol,
                      "attachment_sha256": hashlib.sha256(raw).hexdigest(),
                      "excerpt_checks": rows,
                      "peer_reported_total_seconds": costs["total_measured_seconds"],
                      "peer_reported_content_tokens": sum(costs["input_content_tokens"].values()),
                      "time_not_separately_itemized_seconds": str(gap),
                      "history_clarification": witness["history_clarification"],
                      "scope": "Consistency of disclosed data, not independent source recomputation.",
                      "source_faithfulness": "Unverified", "semantic_acceptance": "Withheld",
                      "memory": "NotMeasured"}, indent=2))


if __name__ == "__main__":
    main()
