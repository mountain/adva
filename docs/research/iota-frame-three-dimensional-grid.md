# One iota frame on a three-dimensional discrete grid

Status: **executed external finite correspondence**, 2026-09-20. This is one
research witness in `adva`, not a machine specification, native certificate,
content exchange or mathematical-library admission.

Authored and checked by Codex (OpenAI), contributed under Unknown v0.3 through
Mingli Yuan's authorized GitHub account proxy. Account use is not Mingli's
authorship, review, endorsement or correctness guarantee. The same assistant
wrote and checked this continuation; there is no independent reviewer.

## Question and fixed sources

Can the already received `chain-and-single` iota process be placed on a
three-dimensional nearest-neighbor integer grid while retaining its directed
events, causal cuts, source terms and declared `(e, i, iota)` observation?

The [contract](../../experiments/iota_grid_embedding/contract.json) fixes the
source at `a018b52d2af69a55e4b2e597f9319d293b173e97` and SHA-256 pins four
existing files: the [processes](../../knowledge/received/iota-frame-knowledge-2026-09-17-v1/materials/processes.json),
their [prefix-term checker](../../knowledge/received/iota-process-knowledge-2026-09-17-v1/materials/check.py),
the [frame interpretation](../../knowledge/received/iota-frame-knowledge-2026-09-17-v1/materials/frame.md)
and its [rational algebra](../../knowledge/received/iota-frame-knowledge-2026-09-17-v1/materials/algebra.py).
The source's historical spelling `i` means the iota combinator; the complex
structure below is the separately typed matrix `J`.

The machine's [existing interpretation profile](https://github.com/mountain/adva-machine/blob/d42ce284d725a13e1d6e1a75fd4e46eb432f6b17/spec/framework/iota-frame-v1.md)
is a fixed documentary reference. No consumer lock is upgraded. This continues
an existing finite interpretation rather than promoting the agenda's deferred
native process exponential or introducing a new semantic type.

## Exact grid correspondence

The three events have dependencies `0 -> 1`, with event `2` independent.
Coordinate `k` records whether event `k` has occurred. The legal vertices are

\[
V=\{(x,y,z)\in\{0,1\}^3:y\leq x\}.
\]

| Source cut mask | Grid position |
| --- | --- |
| 0 | (0,0,0) |
| 1 | (1,0,0) |
| 3 | (1,1,0) |
| 4 | (0,0,1) |
| 5 | (1,0,1) |
| 7 | (1,1,1) |

An edge increases exactly one coordinate from zero to one and retains that
event index. There are seven directed edges and three complete schedules.
The missing masks 2 and 6 would execute event 1 before event 0.

The checker first replays the source reductions with the pinned old checker.
It then independently enumerates the eight binary coordinate triples, filters
them by event dependencies, reconstructs grid adjacency, and compares every
cut term and labelled edge. Both directions are checked: no source edge is
lost and no grid edge is invented. A complete family digest, history digest,
entry/exit policies, event clocks, final apertures, ancestry reference and
explicit residual remain bound to the candidate. A digest does not supply the
still-external full constructor ancestry or native semantic identity.

This is an ambient three-dimensional presentation. The graph itself is
`P3 x P2`: mapping `(x,y,z)` to `(x+y,z)` flattens it onto a two-dimensional
rectangular grid. The witness therefore does **not** establish intrinsic
dimension three, three independent directions of concurrency, or that every
iota process admits this local embedding.

## Keeping the exponential observation

Use the combinatorial Laplacian `L` of the **legal induced subgraph**. Its
degrees in the sorted cut basis are `(2,3,2,2,3,2)`, so the old normalization is
`H0=L/6`. Set

\[
H=\begin{pmatrix}H_0&0\\0&H_0\end{pmatrix},\qquad
J=\begin{pmatrix}0&-I_6\\I_6&0\end{pmatrix},\qquad G=O=I_{12}.
\]

Exact rational comparison gives the same `H` and `J` as the source frame.
The checker verifies `J^2=-I`, `H^T=H`, `HJ=JH`, the absolute row-sum bound
one, and skew symmetry of `A=-JH`. It compares exponential coefficients
`A^k/k!` with the source through degree twelve and the Wick coefficients
`(-J)^k A^k/k! = (-H)^k/k!` through the same degree.

Equality of the generators in the identical ordered basis implies equality
of their matrix exponentials by the defining series. This is an elementary
mathematical argument, not a proof-assistant certificate. As in the original
frame, for absolute parameter at most one the degree-twelve tail is bounded
by `3/13!` in the unchanged identity metric: `||A|| <= 1`, and
`sum_{k>=13} 1/k! <= e/13! < 3/13!`. A truncated polynomial is not asserted
to be exactly unitary. The continuous parameter is not the event clock.

The amplitude carrier has twelve real components, equivalently six complex
components, over six grid sites. Its dimension is distinct from the three
coordinates locating a site. Nothing requires or constructs a real 3-by-3
matrix whose square is `-I3`.

## Refusals and the boundary-condition obstruction

Seven altered candidates or receiving contexts are refused:

1. complete the cube by adding the two forbidden vertices;
2. replace a legal vertex by a forbidden one without changing the vertex count;
3. reverse a causal edge;
4. change an edge's event index;
5. replace the initial cut term by the normal form;
6. erase the separate event clock;
7. retain the same graph while changing the receiving role policy.

The existing `independent-iota` and `changed-roles` families are also freshly
replayed as controls. They have equal Laplacian operators and different frame
bindings. Operator equality is insufficient to identify processes.

The eighth control is an exact operator counterexample. Taking the principal
submatrix of the full cube's Laplacian keeps diagonal degree three, whereas
the induced-subgraph Laplacian uses the legal degrees above. Their difference
is

\[
L_{\mathrm{cube}}[V,V]-L_V=\operatorname{diag}(1,0,1,1,0,1).
\]

The former has nonzero row sums: it introduces boundary killing on four
vertices. That is a different observation and cannot replace the declared
source Laplacian. This is an algebraically checked counterexample, separate
from the seven candidate/context refusals.

## Executed result and reproduction

The first frozen run returned `GridCorrespondenceChecked`: **341 assertions,
30,472 counted host work units, eight controls**, six vertices, seven directed
edges and three schedules. It used 0.050328 seconds wall time, 0.049765 seconds
CPU and 14,464 KiB peak process RSS. There was no failed mathematical run or
corrective replay. Preparation and publication are outside these timings.
The [retained evidence](../../experiments/iota_grid_embedding/evidence.json)
contains the complete candidate, source summaries, matrices, coefficient
digest, refusals, dependency-bound contract/checker hashes and resource account.

From a checkout with Python 3.11+ on Linux, choose an output path that does not
already exist:

```sh
python3 -B experiments/iota_grid_embedding/check.py --output /tmp/iota-grid-fresh.json
```

The fixed contract enforces twenty wall seconds, fifteen CPU seconds, 256 MiB
address space, one MiB per output and twelve million counted work units, with
zero automatic retries. The alarm remains active through checkpoint writing.
Missing inputs or resource exhaustion yield `Unknown`; pin mismatches and
unexpected check failures yield `Failed`. An existing output is refused.
An inability to write a checkpoint is an execution error, not a positive result.
This checker receives only its frozen trusted inputs, not arbitrary user code.

## Repository scope and next boundary

This result belongs to research in `adva`. The existing received bytes,
historical transport receipts, `adva-machine` specifications and `adva-library`
catalog remain unchanged. All three native fields stay explicit: native
admission `NotGranted`, native execution `NotRun`, new transport `NotRun`.
The Python function named `receive` is a finite comparison, not the Adva
transport operation. This run does not repeat the full twelve-frame historical
campaign or claim independent validation of its shared checker and algebra.

The result supports the finite compatibility intuition and identifies the
choice of causal domain and boundary operator as essential. A subsequent
machine-side receiving design would have to bind this candidate, its exact
source, checks, authority and residuals explicitly. General grid execution,
larger process families, native identity admission and physical interpretation
remain separate questions. No M6 filler follows from six spatial directions.

Publication checks for this change ran over the exact staged payload and a
local audit snapshot of pinned source files. The known-withdrawal check's
`--history` flag covered that locally available snapshot only; the full remote
history and full Rust/CI suite were not replayed. This is not a whole-repository
rights or conformance certification.
