"""Read-only replay of the received projection and finite disclosed word lists."""
import hashlib
import json
import re
from pathlib import Path

from check_exchange import check, decode, read

ROOT = Path(__file__).resolve().parent


def main():
    request = read(ROOT / "request-02.json")
    response = read(ROOT / "response-02.json")
    attachment_raw = read(ROOT / "word-witness-02.json")
    attachment = decode(attachment_raw)
    protocol = check(request, response)
    assert protocol["status"] == "VariationObserved"
    assert attachment["request_sha256"] == hashlib.sha256(request).hexdigest()
    left, right = attachment["head_left"], attachment["head_right"]
    assert len(left) == len(set(left)) == len(right) == len(set(right)) == 25
    assert not set(left) & set(right)
    examples = attachment["dropped_examples"]
    assert len(examples) == len({e["word"] for e in examples}) == 8
    checked = []
    for example in examples:
        match = re.fullmatch(
            r"naive-shared and content-shared; cookbook freq (\d+) rank (\d+); irs freq (\d+) rank (\d+)",
            example["old_membership_evidence"])
        assert match
        lf, lr, rf, rr = map(int, match.groups())
        assert min(lf, lr, rf, rr) > 0
        word = example["word"]
        for head, rank in ((left, lr), (right, rr)):
            assert ((rank <= 25 and head[rank - 1] == word)
                    or (rank > 25 and word not in head))
        checked.append({"word": word, "rank_claims": [lr, rr],
                        "consistent_with_disclosed_heads": True})
    print(json.dumps({"protocol": protocol,
                      "attachment_sha256": hashlib.sha256(attachment_raw).hexdigest(),
                      "head_lengths": [25, 25], "intersection": [], "examples": checked,
                      "scope": "Arithmetic and consistency of disclosed data; not source reconstruction.",
                      "unverified": ["source versions", "stoplist contents", "token extraction",
                                     "full frequencies/ranks", "semantic relevance"]}, indent=2))


if __name__ == "__main__":
    main()
