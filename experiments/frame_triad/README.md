# Frame, symmetry, and triadic continuation: external calibration

See [Research 0159](../../docs/research/0159-frame-symmetry-triadic-continuation.md)
for definitions, proofs, attribution, observed results, and Open boundaries.

The original invocation completed once under `contract.json`. `evidence.json`
contains all finite partition, update, and extension rows, continuation traces,
negative controls, and the source/contract SHA-256 values. `manifest.json`
covers the experiment files. Hashes bind bytes; they do not establish
authentication, native identity, or semantic authority.

To reproduce on Linux with Python 3.11 or later, from this directory:

```sh
timeout 20s python3 calibration.py --output evidence-new.json
```

Use a fresh path. Reproduction is a new invocation, not a replacement of the
archived run; the program refuses to overwrite evidence. It uses only Python's
standard library. It consumes a trusted local contract and is not a hardened
service for arbitrary untrusted contracts.

`Admissible` in an update row means nonempty model filtering. Actual answer
truth additionally needs a sound checker bound to the intended interpretation.
The continuation demonstration checks an explicitly supplied alternating
answer fixture. Its finite success is not autonomous discovery or proof of
the real world's future behavior.

The mathematical proof for arbitrary finite prefixes is in the report. The
exhaustive executable result has the frozen 0–3-question scope, plus one fresh
coordinate for each extension. No native operation or formal-proof-kernel
certificate is produced.
