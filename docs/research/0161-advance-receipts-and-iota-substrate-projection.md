# Research 0161: advance receipts and the iota/SKI substrate projection

Date: 2026-09-09. Status: local bounded trials; this note is a proposed
research record. No claim entry is registered in claims.toml; native
admission is not granted; no new knowledge epoch is produced.
Direction: Mingli Yuan. Implementation and local verification: assistant.
Numbering note: 0161 was an unused gap in the remote series; this note
fills it without colliding with any pushed research number.

## 1. Two sub-trials, one research line

The next research line combines 0163's prescribed next minimum step with
0164's bridge material. 0163 concluded that the 400 archived rounds of
Research 0162 stutter on the declared carrier and prescribed a versioned
`advance` receipt binding each round to its predecessor through an
admitted delta. 0164 constructed the byte formula
`(add (add (copy u)) v)` in PSC0 with u=(b mod 8)+1, v=b-2u.

**Sub-trial 1 (advance receipts)** measures the archive and the native
binary under that discipline: the 0162 archives and 100 native runs of one
pinned program are `EvidenceStutter` (the 100 outputs differ only in
`phase_seconds` instrumentation; classified `IncidentalVariation`), while
two distinct pinned programs both admitted by the same binary yield
`VariationObserved`.

**Sub-trial 2 (iota/SKI substrate projection)** implements a bounded pure
Python iota/SKI reducer using the iota-lang encodings (I=ιι, K=ι(ι(ιι)),
S=ι(ι(ι(ιι)))), brackets the 0164 formula to SKI, and evaluates it in the
finite integer model with sign-pair church arithmetic. The full 0..255
byte set passes: 256/256 values correct, 256/256 distinct terms, tampered
negative controls rejected, and ι expansion/round-trips agree on samples.

## 2. Findings worth retaining

- The ι encodings expand to **η-expanded SKI** (K → S S K K); equality with
  the compact bracket-abstraction form is by value, never by syntax.
- Fully reduced signed terms are **final pair values** and must be decoded
  through SND/FST behavioral tests, not the numeral wrapper.
- Engineering lessons: free-variable sets must be memoized with the term
  itself as key (id() reuse poisons the cache); bracket abstraction needs
  the free-variable shortcut; η-expanded terms need lazy normalization
  before strict evaluation.

## 3. Boundary

The substrate projection records a checkable finite mapping between the
Substrate language (iota/SKI) and the Knowledge carrier (PSC0): both
compute the same byte frontier for the 0164 formula. It is **not** a
language equivalence, a native admission, a claim registration, or a new
epoch. The stutter classification does not turn repetition counts into
learning evidence; native learning and `free` remain Open.

Evidence: byte copies under [0161-evidence](0161-evidence/README.md);
original trials retained in the local AEG repository.

## 4. Two-binary frontier connection (2026-09-09)

The machine-level embodiment of the substrate bridge: two compiled
artifacts from the same pinned Rust sources are bound by hash pins and
agree with the iota/SKI substrate on the full 256-byte frontier.

| Artifact | SHA-256 | Source pin |
| --- | --- | --- |
| main adva CLI (`target/debug/adva`) | `755cc1ecfc48…` | HEAD `ac2c173`; Rust inputs unchanged, rust-source-boundary holds |
| byte observer (`target/debug/examples/quine_relay`) | `dfc2de43e862…` | `a7b82a1` via the advance contract |

The main binary's run admission caps fuel at 1..=16, so a single
256-value module is rejected at source_preflight (attempt retained in the
evidence). The frontier is instead checked as 256 bounded single-byte
runs (fuel 8): values equal `range(256)` exactly and agree with the
substrate model 256/256. Receipt 07 binds the relation
(same-pinned-source artifacts agreeing on the shared frontier); the
per-run transient outputs are reproducible from the recorded procedure.
This is a value-level frontier relation, not bit-level isomorphism and
not a cross-machine reproducibility claim.

## 5. Amendment (2026-09-10): substrate-side continuation boundary

[Research 0167](0167-iota-lang-reconnection-audit.md) audited the iota-lang
checkout and found that it does not compile at any commit, that the recorded
rules never produce a readable result for any of the 17 recorded cases, and
that the recorded test contract contains inconsistent expectations.

By the direction of 2026-09-10, that line continues on the **iota-lang side
only**. Nothing in 0167 is connected into adva: no Rust type, operation,
certificate or `ProgramTerm`, no adapter, no comparison harness, and no change
to the projection recorded above or to its Python reducer. The "upgrade the
projection to two independent implementations" step named in section 1 is
therefore **blocked, not next**, and requires its own explicit decision and its
own bounded contract. Storing 0167's evidence in this repository is an archive
choice, not an admission.
