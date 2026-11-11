"""Offline integrity and coverage checks. Never open a machine checkout."""
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import inventory_pinned_machine_reference_ledger as driver

CONTRACT_DIGEST = "3130a81a4933af62cc35b2c980fe2fdd3cbc2f197f055c58524891c495eafe47"
RECEIPT_DIGEST = "3a0b97db6ae274f03503fe583b901608a88d0bb4c8b95aa9086dbb328e86f421"
LEDGER_DIGEST = "f31bd194761e9bb3bd536f9a2e8ebf9ce7a8bc9e5fc4d107fcc9569e0a04ef2d"
REVIEW = driver.EXP / "machine-reference-ledger-review-20261106.json"


def check_review(review, raw_ledger):
    rows = [json.loads(line) for line in raw_ledger.splitlines()]
    wanted = Counter((row["path"], row["line"]) for row in rows)
    driver.require(driver.sha(raw_ledger) == review["ledger_sha256"] == LEDGER_DIGEST
                   and review["receipt_sha256"] == RECEIPT_DIGEST
                   and review["contract_sha256"] == CONTRACT_DIGEST
                   and review["revision"] == driver.prior.EXPECTED_REVISION, "review input pins differ")
    seen = Counter()
    for group in review["reference_groups"]:
        reason = review["basis"][group["basis"]]
        driver.require(group["lines"] and len(reason["ABCD"]) == 4
                       and all(code in review["grade_key"] for code in reason["ABCD"])
                       and reason["reason"], "incomplete four-obligation rationale")
        seen.update((group["path"], line) for line in group["lines"])
    driver.require(seen == wanted and len(seen) == len(rows) == review["rows_reviewed"] == 430
                   and len({p for p, _ in seen}) == review["candidate_files"] == 45,
                   "review coverage differs")


class ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review = driver.load_json(REVIEW)
        cls.ledger = (driver.RUN / "references.jsonl").read_bytes()

    def test_frozen_bundle_and_all_review_coordinates(self):
        anchor = driver.frozen_contract(CONTRACT_DIGEST)
        self.assertEqual(driver.verify(driver.RUN, anchor, CONTRACT_DIGEST), RECEIPT_DIGEST)
        check_review(self.review, self.ledger)

    def test_missing_review_reference_rejected(self):
        changed = deepcopy(self.review)
        changed["reference_groups"][0]["lines"].pop()
        with self.assertRaises(ValueError):
            check_review(changed, self.ledger)

    def test_duplicate_replacing_a_missing_row_rejected_even_with_same_count(self):
        changed = deepcopy(self.review)
        lines = changed["reference_groups"][0]["lines"]
        lines[-1] = lines[0]
        with self.assertRaises(ValueError):
            check_review(changed, self.ledger)

    def test_missing_fourth_judgment_rejected(self):
        changed = deepcopy(self.review)
        changed["basis"][changed["reference_groups"][0]["basis"]]["ABCD"].pop()
        with self.assertRaises(ValueError):
            check_review(changed, self.ledger)


if __name__ == "__main__":
    unittest.main()
