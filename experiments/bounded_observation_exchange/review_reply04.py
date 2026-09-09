"""Read-only arithmetic and disclosed-data audit of peer reply 04."""
import hashlib
import json
from decimal import Decimal, ROUND_FLOOR
from pathlib import Path

from check_exchange import check, decode, read

ROOT = Path(__file__).resolve().parent


def main():
    request = read(ROOT / "request-04.json")
    response = read(ROOT / "response-04.json")
    raw = read(ROOT / "reuse-witness-04.json")
    witness = decode(raw)
    protocol = check(request, response)
    assert protocol["status"] == "VariationObserved"
    assert witness["request_sha256"] == hashlib.sha256(request).hexdigest()
    assert witness["baseline_result"] == witness["reloaded_result"]
    expected = {"frequency", "rank", "locator", "context"}
    assert all(set(v) == expected for v in witness["baseline_result"].values())
    words = witness["rule_pins"]["stoplist"].split()
    assert len(words) == len(set(words)) == 119
    encoded = "\n".join(sorted(words)).encode("utf-8")
    assert hashlib.sha256(encoded).hexdigest() == witness["rule_pins"]["stoplist_sha256"]
    cost = witness["cost"]
    D = lambda value: Decimal(str(value))
    b, f, r = D(cost["B_seconds"]), D(cost["F_seconds"]), D(cost["R_seconds_in_process"])
    setup = D(cost["shared_setup_seconds"])
    assert b > r and f >= 0
    n = int((f / (b - r)).to_integral_value(rounding=ROUND_FLOOR)) + 1
    with_setup = int(((f + setup) / (b - r)).to_integral_value(rounding=ROUND_FLOOR)) + 1
    assert n == 4 and with_setup == 4
    balance = (D(cost["total_wall_seconds"]) - b - f
               - D(cost["R_subprocess_wall_seconds"]) - setup
               - D(witness["stale_rule_control"]["seconds"]))
    print(json.dumps({"protocol": protocol,
                      "attachment_sha256": hashlib.sha256(raw).hexdigest(),
                      "disclosed_four_field_results_equal": True,
                      "stoplist_distinct_words": 119,
                      "matching_stoplist_encoding": "UTF-8 lexicographically sorted words joined by newline, no final newline; producer confirmation pending",
                      "conditional_amortization_N": n,
                      "conditional_N_with_all_shared_setup_charged_to_F": with_setup,
                      "wall_balance_seconds": str(balance),
                      "process_per_query_comparison": "NotComparable: B excludes process startup, R_wall includes it",
                      "source_and_execution_verification": "Unverified",
                      "residuals": ["original wider comparison objects unavailable", "actual old stoplist unavailable",
                                    "source/index/rule-module bytes unavailable", "timings and stale-rule control reported by peer, not locally replayed"]}, indent=2))


if __name__ == "__main__":
    main()
