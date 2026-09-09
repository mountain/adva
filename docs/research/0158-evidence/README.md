# External downward interpretation and drop-route records

See [Research 0158](../0158-downward-interpretation-and-drop-route.md) for
attribution, conclusions, assumptions, and the retained Open obligations.

These directories preserve the reports and three completed, separately bounded
external Python calibrations from 2026-09-08. Their hashes bind evidence to
source and contract bytes; they are not authentication or native certificates.
The reports' prepublication repository-status statements are historical.

| Directory | Files |
| --- | --- |
| `downward-interpretation-v0/` | Report, `calibration.py`, `contract.json`, `evidence.json`, and `manifest.json` |
| `mingli-drop-route-v0/` | Report, core `calibration.py` / `contract.json` / `evidence.json`, separate `retraction.py` / `retraction-contract.json` / `retraction-evidence.json`, and `manifest.json` |

The second manifest covers report version 0.2 and the retraction supplement.
The earlier source/contract/evidence bytes are unchanged.

## Reproduction

Use Linux and Python 3.11 or later, with a fresh output filename. Each command
is an optional new invocation, separate from the archived observed run.
The programs use finite process limits and refuse to overwrite evidence.

From `downward-interpretation-v0/`:

```sh
timeout 20s python3 calibration.py --contract contract.json --output evidence-new.json
```

From `mingli-drop-route-v0/`:

```sh
timeout 10s python3 calibration.py --output evidence-new.json
```

For the supplement, copy only `retraction.py` and `retraction-contract.json`
into a fresh directory and run from there:

```sh
timeout 5s python3 retraction.py
```

The supplement writes `retraction-evidence.json` beside its source. Never
delete or replace the archived evidence to make a command run. Timing and
memory measurements may vary; mathematical rows and declared case outcomes
are the meaningful comparisons.
