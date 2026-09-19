# Compatible history surfaces

An external finite-arithmetic model for the user's proposal that a changing
surface can retain the whole past while admitting new continuations.
[Research 0206](../../docs/research/0206-compatible-history-surfaces.md)
contains the definitions, elementary proofs, measured results and limits.
[中文导读](learning.zh.md) explains the main experiment.

Authored by Codex (OpenAI), through Mingli Yuan's authorized account proxy.
Account use is not his authorship, review or endorsement. Original first-party
code, prose, examples and figures are contributed under Unknown v0.3. No external
text, software source, image or dataset is incorporated. Python's standard
library is the only runtime dependency; no dependency is vendored.

## Run

From the repository root on Linux/POSIX with Python 3.11 or later:

~~~sh
python3 experiments/history_surface/run.py --output /tmp/history-surface-replay.json
~~~

Use a new output path. Existing reports are not overwritten. The parent applies
the limits in [contract.json](contract.json) to a fresh worker. One invocation
is finite and does not resume automatically. Inspect the report status as well
as the exit code. The committed [run-01 report](evidence/run-01.json) is the
completed primary campaign.

## Files

- [model.py](model.py): encoding, bounded interpolation decoder, append and
  prefix readback over F_7.
- [run.py](run.py): fixed finite campaign, negative controls and supervisor.
- [surface-history.svg](surface-history.svg): original illustration generated
  from the retained rewrite example.
- [draw.py](draw.py): deterministic standard-library SVG generator.

Regenerate the illustration with:

~~~sh
python3 experiments/history_surface/draw.py
~~~

The decoder finds a unique codeword within its declared radius. It does not
authenticate the actual history. The report deliberately includes a two-error
miscorrection. Header integrity is assumed. Only finite words over the declared
alphabet are modeled; this is not native Adva History, a geometric surface
construction, a physical holographic theory or an endogenous breakthrough.
