"""Original finite fixtures: each mode deliberately exercises one boundary."""
import json
import sys
import time

mode = sys.argv[1]
if mode == "exit":
    raise SystemExit(17)
if mode == "timeout":
    time.sleep(1)
elif mode == "malformed":
    print("not json")
else:
    units = {"success": 2, "reuse": 1, "probe": 0, "overreport": 5}[mode]
    print(json.dumps({"work_units": units, "value": mode}))
