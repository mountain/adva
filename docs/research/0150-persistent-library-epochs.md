# 0150 — Checked publication and reload of finite library epochs

Status: frozen continuation contract, written before execution. Research only;
the stable agenda and typed-aperture promotion gates remain unchanged.

## Question, current level and imported boundary

Research 0149 saved a checked finite candidate experiment, but no next run
loaded it as a library. The user requests that missing step and one more run.
Implement a Rust research snapshot store under `adva-library/stability/`,
publish only rechecked content, reload it, and compare the next epoch with its
predecessor. No stable Lisp operation, observer specialization, feedback or
hole calculus is authorized by this step.

The exact input is the unchanged 0149 `study.json`, SHA-256
`034910fbd171a8fa77e3bbc08f161d2b7c49162e2ecda8c1d9492efa8ac7ab98`.
Its `delayed-evidence` request supplies four expression candidates and five
rounds. Import those as proposals, retain the original artifact, and freshly
derive the snapshot with the current Rust checker. Do not promote or silently
reinterpret the old receipt or its checker revision.

The new epoch proposes `2*x*x` and adds exactly one supplied observation
`f(2)=4`. This is a calibration assumption, not world measurement, syntax
discovery, or a deduction from closure in the old catalogue. Candidate syntax
is the existing bounded `ExactExprV0` research language; observations use its
polynomial shadow, not guarded program execution. The old observations at
zero and one are retained and applied to the new candidate.

Use existing `WitnessStoreV0::insert` to derive and replay a two-node
ArithmeticTransition/Seal witness for `2*x` and `x+x`. Retain its nonzero
obligations. Reloaded reuse at `x=2` checks those guards and returns `4,4`;
zero-guard refusal remains separately tested. This is a guarded research
witness observation, not `ExecutedCell`, a PSC0 transformation, an M6 filler,
or a proof identifying programs.

## Protected obligations and publication

Each immutable snapshot embeds its ordered catalogue, entire observation/
revisit history, complete derived checkpoints, scoped witness artifacts and
origin reference. A successor additionally embeds an exact parent digest and
an append-only delta. Loading replays the complete bounded ancestry, validates
all shapes, rederives checkpoints and witness nodes, and compares full content.
Serde success, supplied status flags, paths and hashes alone authorize nothing.
Digests and ordinals are research storage coordinates, not semantic identities
or authentication. No source or occurrence identities are allocated.

Candidate insertion occurs at the new epoch boundary; its catalogue remains
fixed during that epoch's evidence steps. Old candidates, observations,
certificates and files are never deleted or overwritten. The added candidate
may remain in the catalogue while excluded from the active set. Publish only
a fully checked nonempty feature-closed terminal snapshot. `Open`, `ModelGap`
and `Unknown` attempts retain their proposed input and checks but cannot
publish a successor. A pending/failed write is not a committed snapshot.

Use complete same-directory staging followed by an atomic no-clobber hard-link
publication on the supported local filesystem. Flush file and directory;
readers consume only explicit final snapshot paths and revalidate them.
There is no mutable latest pointer, network service, concurrent branch merge,
global anti-fork ledger or automatic unbounded continuation. Leftover staging
files remain uncommitted and are reported rather than silently discarded.
This does not reinterpret existing Pascal files or the documentary index.

## Enforceable finite run budget

- One standalone workflow: bootstrap epoch 0 from the pinned old report;
  publish/reload it; perform exactly one new epoch; publish/reload epoch 1;
  save a comparison report. No automatic retry or second learning round.
- One shared 50000-unit account covers admission, node validation,
  normalization, evidence/feature checks, proof insertion/replay, bounded
  parsing, ancestry traversal, hashing, guard reuse and persistence. Reserve
  the final report charge in advance from this same account. Logical charges
  are not CPU instructions; the outer host limits cover all work and I/O.
- At most 8 catalogue expressions, 31 nodes/depth 8 each, constant integers
  in [-16,16], variable x only; at most 16 evidence/revisit steps per snapshot;
  point inputs in [-8,8], values in [-1000000,1000000].
- At most 4 snapshot epochs in any ancestry, each with at most 8 stored
  two-node witnesses. Input files and each output are at most 1 MiB; JSON
  decoding retains its recursion limit. The experiment reads one pinned
  165139-byte origin and writes at most two snapshots, their temporary files
  and one report; no search or arbitrary graph input.
- Standalone workflow: timeout 20 seconds, address space 512 MiB, output file
  limit 1 MiB. The directory must be new. Hard interruption may leave partial
  or complete committed prefixes; never claim unrecorded progress or reset
  the account. Save errors are surfaced explicitly.
- Engineering: at most three targeted test/build passes, each 180 seconds;
  at most two clippy passes, each 180 seconds; one full Rust regression pass,
  180 seconds. Unit tests use finite isolated ledgers and temporary directories,
  not production continuations. Record all failures and fixes. Stop at the
  declared outcome or bounds; any further trial requires a revised contract.

## Expected comparison and negative controls

Epoch 0: catalogue 4, active [1,2], polynomial 2x, five prior rounds, one
two-node retained witness. Before the new observation, the extended catalogue
has active [1,2,4] and is Open. After the supplied observation at two, the new
candidate predicts eight and is excluded, leaving the same two active syntax
candidates and polynomial 2x. Epoch 1 retains catalogue 5, six observations/
revisits, the same witness content, the refutation and its parent snapshot.

Tests must refuse stale parent linkage, altered catalogue/evidence/derived
features/proof summaries, method drift, unsafe path references, invalid input
sizes, duplicate publication and insufficient fuel. A loader must not admit
a partial file. A changed observation that empties the model cannot publish.
No-evidence extension remains Open and cannot publish. Guarded reuse at zero
must fail even though polynomial diagnostic values there are allowed.

Execution evidence will be written separately in `0150-evidence/`; the
original 0149 source, contract, output and prior library files remain unchanged.
