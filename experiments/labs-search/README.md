# Bounded triadic LABS search

Status: research-local executable calibration. This crate is not part of
Adva's stable semantic API.

The experiment searches for low-autocorrelation binary sequences (LABS). A
witness is a finite sequence

\[
s=(s_0,\ldots,s_{n-1}),\qquad s_i\in\{-1,+1\},
\]

with aperiodic autocorrelations

\[
C_k(s)=\sum_{i=0}^{n-k-1}s_i s_{i+k}
\]

and exact integer energy

\[
E(s)=\sum_{k=1}^{n-1}C_k(s)^2.
\]

Finding a low-energy sequence is difficult; checking a proposed sequence is
quadratic and exact. That makes LABS useful for the first Adva
"hard-to-find, cheap-to-verify" experiment.

## The three programs

The crate keeps observation and computation distinct. All three programs read
one checked candidate state, but they perform different computations.

- **Temporal program**: advances a search trajectory using exact incremental
  single-spin flips, a short recency memory, and bounded uphill escapes.
- **Spatial program**: reads the residual autocorrelation field, selects its
  dominant lags, and proposes a flip that reduces that restricted defect.
- **Constructive program**: splices blocks from archived witnesses and applies
  bounded mutations, producing nonlocal candidates.

An adaptive UCB-style scheduler chooses among enabled programs. Every proposal
is recomputed exactly before it can enter the archive or become a witness.
The scheduler, acceptance rule, and construction grammar are calibration
choices, not claimed universal laws.

## Build and test

From the repository root:

```bash
cargo test -p adva-labs-search
pytest tests/python/test_labs_witness_verifier.py
```

## Small exact calibration

```bash
cargo run --release -p adva-labs-search -- \
  exhaustive --length 13 --output labs-13-exact.json

python experiments/labs-search/verify.py labs-13-exact.json
```

The exhaustive command fixes the first spin to `+1`, removing only the global
sign symmetry. It is deliberately restricted to lengths `2..=25`.

## Three-program search

```bash
cargo run --release -p adva-labs-search -- search \
  --length 64 \
  --iterations 5000000 \
  --workers 16 \
  --seed 1 \
  --output labs-64.json

python experiments/labs-search/verify.py labs-64.json
```

`--iterations` is the number of scheduler steps per worker. Workers are
independent deterministic runs with derived SplitMix64 seeds. The output
contains the best witness, per-program use and reward statistics, restarts,
and a bounded trace.

## Checkpoint and resume

Periodic deterministic checkpoints currently require one worker:

```bash
cargo run --release -p adva-labs-search -- search \
  --length 128 \
  --iterations 10000000 \
  --workers 1 \
  --checkpoint labs-128.checkpoint.json \
  --checkpoint-every 100000 \
  --output labs-128-stage1.json

cargo run --release -p adva-labs-search -- search \
  --resume labs-128.checkpoint.json \
  --iterations 10000000 \
  --checkpoint-every 100000 \
  --output labs-128-stage2.json
```

A resumed run preserves the PRNG state, archive, scheduler statistics, current
trajectory, incumbent, and trace.

## Ablation

The same executable can isolate any subset of the three programs:

```bash
--programs temporal
--programs spatial
--programs constructive
--programs temporal,spatial
--programs temporal,constructive
--programs spatial,constructive
--programs temporal,spatial,constructive
```

Record equal evaluation budgets and multiple seeds. A public claim that the
triadic organization contributed to a result requires these comparisons; a
single good witness does not establish that claim.

## Independent verification

`verify.py` uses only the Python standard library and shares no search code
with Rust. It accepts a run report, exhaustive report, or bare witness,
recomputes every autocorrelation and the exact integer energy, checks the
derived merit factor, and emits a SHA-256 digest of the sign string.

## Scope and limitations

- This is a bounded heuristic, not a state-of-the-art LABS solver.
- The temporal, spatial, and constructive labels identify explicit program
  contracts; they do not establish three universal computers.
- UCB reward, acceptance temperature, archive policy, and splice grammar are
  provisional and must be ablated.
- Search failure means only that a budget was exhausted. It is never a proof
  that a better sequence does not exist.
- A new record must be checked against a date-stamped external baseline and by
  an independent implementation before publication.
