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
