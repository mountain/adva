# Taixuan hierarchy and spectrum calibration

Original external finite research by Codex (OpenAI), under Unknown v0.3.
Mingli Yuan's account is an authorized submission proxy, not verification.

See [Research 0228](../../docs/research/0228-taixuan-hierarchy-observers-and-spectra.md)
for the definitions, proofs, findings, source boundaries and open geometric
obligations. This experiment is not a four-dimensional monotile, native Adva
calculus, physical space-time construction, or learned weather forecast.

The fixed family contains every point of `{0,...,8}^4`, equivalently every
ordered pair of four-place ternary addresses. The checker distinguishes block
coarsening from residue observation, retains an exact coarse/detail field
decomposition, and checks spectra for two different finite group laws.

Run from the repository root with standard-library Python on Linux/POSIX:

```sh
python3 experiments/taixuan_hierarchy_spectrum_v1/check.py \
  --repo-root . \
  --output /tmp/taixuan-spectrum-replay.json \
  --ledger /tmp/taixuan-spectrum-replay-ledger.json
```

Use a new output path without overwriting earlier evidence. Keep the same
ledger for all launches in one contracted attempt; changing its name is not
authorization to reset fuel. The script permits two launches, not two retries
after failures. A failed-checker repair or widened family needs a revised
contract. The parent supervisor enforces wall time and retains the worker
outcome; the worker imposes POSIX CPU/address-space/file-size limits and a
cooperative charged-case bound. The hidden worker entry is an implementation
detail, not a separate authorized unbounded entry point.

`evidence.json` retains the first run. Compare mathematical results when
replaying: elapsed time and peak RSS vary, and decimal Fourier values can vary
slightly across platforms. Exact cyclotomic tuples, multiplicities, partition
counts, rational energies, input hashes and the four rejected controls must
agree. No numerical tolerance applies to the exact results.
