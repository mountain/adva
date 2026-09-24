# Spectral memory, local constraints, and weather errors

Original external research by Codex (OpenAI), Unknown v0.3, submitted through
Mingli Yuan's authorized account proxy only. No native semantics, four-dimensional
monotile, independently authenticated weather data, or new live forecast.

Read [Research 0229](../../docs/research/0229-spectral-memory-local-constraints-and-weather-errors.md)
for the derivations, measured results, negative cases and source reservation.

## Executed order and retained files

| Step | Contract / instrument | Result |
| --- | --- | --- |
| 1. Coarse prediction and lost information | `contract.json`, `analyze.py --phase 1` | `phase1.json`: false AR1 damping, three-step repair, persistent hidden mode, fourth-alias stress failure |
| 2. Finite periods and small homometry search | same contract, `analyze.py --phase 2` | `phase2.json`: torus period counts; no non-dihedral pair in the two declared finite families |
| 2a. Single constructive continuation | `homometry-contract.json`, `homometry.py` | `homometry-evidence.json`: equal power, inequivalent arrangements, unequal three-point motif count |
| 3. Frozen xue error diagnosis | `xue-contract.json`, `xue_errors.py` | `xue-evidence.json`: all 24 declared aggregate rows and source-integrity checks |
| Presentation only | `render-contract.json`, `render.py` | `render-evidence.json`, two SVGs under `figures/` |

`bounded.py` supervises the latter three workers with fixed time, CPU, memory,
output and launch limits. The first instrument includes its own supervisor.
`replay.json` records unchanged fresh-process repetitions of all four numerical
runs; their result objects match exactly, excluding resource metadata. Full
replay envelopes and persistent launch ledgers remain in private staging.

The original contracts have exhausted their allowed numerical launches.
Further research requires a new bounded continuation contract; deleting a
ledger or automatically resetting the budget is not an authorized continuation.

## Reproduction interface

The external reference environment used Python 3.11.15, NumPy 2.4.6,
SciPy 1.17.1 and Matplotlib 3.11.2. Dependencies are installed separately;
none is vendored. Run with `OPENBLAS_NUM_THREADS=1` and without Python `-O`,
`-OO` or `PYTHONOPTIMIZE`. These research instruments use assertions; an
assertion of `__debug__` cannot itself enforce that requirement under `-O`.
The retained runs used ordinary unoptimized Python. Optimized executions
are outside this contract and must not be cited as checked results.

For an independently authorized reproduction, allocate an external output
directory and a persistent ledger for that reproduction, preserve the original
contracts and pins, and invoke from the repository root (replace placeholders):

```sh
OPENBLAS_NUM_THREADS=1 python experiments/taixuan_spectral_analysis_v1/analyze.py \
  --phase 1 --repo-root . --output /external/replay/phase1.json \
  --ledger /external/replay/synthetic-ledger.json

OPENBLAS_NUM_THREADS=1 python experiments/taixuan_spectral_analysis_v1/analyze.py \
  --phase 2 --repo-root . \
  --previous experiments/taixuan_spectral_analysis_v1/phase1.json \
  --output /external/replay/phase2.json \
  --ledger /external/replay/synthetic-ledger.json

python experiments/taixuan_spectral_analysis_v1/bounded.py \
  --contract experiments/taixuan_spectral_analysis_v1/homometry-contract.json \
  --input-root /external/private-inputs \
  --output /external/replay/homometry.json --ledger /external/replay/homometry-ledger.json

OPENBLAS_NUM_THREADS=1 python experiments/taixuan_spectral_analysis_v1/bounded.py \
  --contract experiments/taixuan_spectral_analysis_v1/xue-contract.json \
  --input-root /external/private-inputs \
  --output /external/replay/xue.json --ledger /external/replay/xue-ledger.json
```

The xue contract lists paths relative to `--input-root` and exact input byte
sizes/digests. The input root must supply `xue-study/...` and
`climatetensor-inputs/...` with those frozen bytes. These archives and the
separately pinned spherical evaluator are not distributed by this experiment.
Missing private files yield `Unavailable`; changed bytes yield `Failure`.
The original successful evidence must not be confused with a new local pass.

The rendering invocation uses `--contract .../render-contract.json`; its
`--input-root` denotes a new external figure-output directory. Rendering reads
the reviewed evidence beside its script and refuses to overwrite figures.
Only SVG text and original plot geometry are emitted; no external images or
font programs are embedded.

## Data and interpretation

Weather diagnostics compare frozen L6/L12 monthly 500 hPa vector backtests
against NCEP/NCAR Reanalysis 1, provided by
[NOAA PSL, Boulder, Colorado](https://psl.noaa.gov/data/gridded/data.ncep.reanalysis.html).
Raw weather arrays, spherical coefficients and external source code remain
outside Adva. Published results are original aggregates, not NOAA forecasts
or an endorsement. See the [PSL source statement](https://psl.noaa.gov/disclaimer/).

The user's concern about authenticity of the entire data chain remains
unresolved. Hash consistency does not prove physical truth. The 2020–2025
interval was already exposed during development; this is not a fresh holdout.
Patch Fourier bands, within-block detail and global spherical degree are
different decompositions. All interpretations are conditional on those limits.
