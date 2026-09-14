"""Eight bounded caller-mutation probes; retain the before/after values."""
import copy
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import compose as M


def main():
    rows = []
    for p in (5, 7):
        for name in ("route_ids", "first_H", "second_H", "middle_probes"):
            receipts, expected = M.inputs(p)
            routes = ["A-B", "B-C"]
            result = M.compose(receipts, expected, routes)
            assert result["status"] == "AcceptedComposition", result
            snapshot = copy.deepcopy(result)
            if name == "route_ids":
                routes.reverse()
            elif name == "first_H":
                expected[0]["H"][0] = (expected[0]["H"][0] + 1) % p
            elif name == "second_H":
                expected[1]["H"][0] = (expected[1]["H"][0] + 1) % p
            else:
                receipts[0]["target_probes"].reverse()
            rows.append({"p": p, "input_mutation": name,
                         "accepted_record_changed": result != snapshot,
                         "before_history": snapshot["history"], "after_history": result["history"],
                         "before_frame": snapshot["intermediate_frame"], "after_frame": result["intermediate_frame"]})
    print(json.dumps({"status": "ProbeCompleted", "cases": rows, "work_units": M.C.UNITS}, indent=2))


if __name__ == "__main__":
    main()
