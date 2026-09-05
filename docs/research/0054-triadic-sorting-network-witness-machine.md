# A Bounded Triadic Sorting-Network Witness Machine

Status: executable research calibration following
[`0049-triadic-universal-computation-form-plan.md`](0049-triadic-universal-computation-form-plan.md).

The executable machine is
[`experiments/verified_witness/sorting_network/`](../../experiments/verified_witness/sorting_network/).
Its regression tests are
[`tests/python/test_triadic_sorting_network_witness_machine.py`](../../tests/python/test_triadic_sorting_network_witness_machine.py),
and one emitted witness artifact is
[`examples/verified_witness/sorting-network-5ch-depth5.json`](../../examples/verified_witness/sorting-network-5ch-depth5.json).

This note asks one deliberately concrete question:

> Can three distinct bounded search programs cooperate to produce a finite
> mathematical witness whose correctness is much cheaper to check than to
> discover?

The selected calibration is a comparator sorting network. A candidate is a
finite sequence of pairwise-disjoint comparator layers. Correctness is exact:
by the zero-one principle it is enough to check every binary input. The
resulting witness is compact, deterministic, independently verifiable, and
suitable for later record-search experiments.

This is not yet the universal three-computer machine of note 0049. The three
programs are research-local Python search programs, not stable Adva
code-as-data values interpreted by three checked Rust interpreters. The
experiment introduces no stable sorting-network, search, scheduler, residual,
optimizer, or witness API. It does not modify `claims.toml` or the active
program-slice priority.

---

## 0. Executive result

The finite machine contains three distinct programs:

1. a **temporal program** that revises recent execution history by bounded
   replacement, exchange, and replay of layers;
2. a **spatial program** that sees the exact residual set of unsorted binary
   inputs and appends a layer chosen to contract that set;
3. a **constructive program** that grafts named reusable layer motifs such as
   odd-even, mirror, and block-stride matchings.

A deterministic level-synchronous scheduler combines their proposals, removes
identical networks, and retains a bounded beam under the exact score

\[
\bigl(
|R(N)|,
W(N),
\operatorname{size}(N),
\operatorname{hash}(N)
\bigr),
\]

where `R(N)` is the residual input set and `W(N)` is a distance-weighted
inversion count.

The checked small instances are:

| channels | depth bound | result size | inputs checked | result |
|---:|---:|---:|---:|---|
| 4 | 3 | 5 | 16 | exact sorting network found |
| 5 | 5 | 9 | 32 | exact sorting network found |
| 7 | 6 | 17 | 128 | exact sorting network found |

For the declared seven-channel fixture, construction-only search returns a
size-18 network at depth 6, while the full enabled program set returns a
size-17 network. This is only a bounded calibration. It does **not** establish
that all three programs are necessary, that the scheduler is generally
superior, or that the size-17 network is a new or globally optimal result.
The current improvement is principally attributable to the residual-sensitive
spatial program. The independent value of temporal replay remains an explicit
ablation question.

The five-channel sample artifact has network hash

```text
004181c05a2cb23e552d6c091dae32efeb4c6eecc76e585509a4b09cbc5d0b87
```

and passes both the bit-parallel verifier and the independent scalar verifier.

---

# Part I. The exact witness problem

## 1. Comparator networks

For `n` channels, a comparator is a pair

\[
(i,j),\qquad 0\leq i<j<n,
\]

which maps the two values to

\[
(\min(x_i,x_j),\max(x_i,x_j)).
\]

A layer is a matching: no channel may occur in two comparators in the same
layer. A sorting network is a finite ordered tuple of layers

\[
N=(L_0,L_1,\ldots,L_{d-1}).
\]

Its depth is `d`; its size is the total number of comparators.

The witness claim emitted by this experiment is narrow:

> the listed network sorts every binary input of the declared channel count.

No result artifact claims minimum depth or minimum size.

## 2. Exhaustive bit-parallel verification

There are

\[
2^n
\]

binary inputs. Bit position `p` of each Python integer represents one input
word. One integer is maintained for every channel. A comparator becomes the
exact simultaneous update

\[
B_i' = B_i\land B_j,
\qquad
B_j' = B_i\lor B_j.
\]

After executing all layers, the residual mask is

\[
R(N)
=
\bigvee_{i=0}^{n-2}
\left(B_i\land\neg B_{i+1}\right).
\]

The network sorts all binary inputs exactly when

\[
R(N)=0.
\]

The verifier also reports:

- `|R(N)|`, the number of failing inputs;
- one inversion count for every adjacent channel pair;
- a distance-weighted count over every pair of channels;
- a bounded list of concrete input/output counterexamples;
- a SHA-256 digest of the canonical network JSON.

For small channel counts, an independent scalar verifier enumerates binary
input tuples and executes ordinary `min`/`max` comparators. A disagreement
between the two implementations raises an error rather than selecting one
oracle silently.

## 3. Honest finite outcomes

A run returns one of two states:

```text
Found(network, verification, lineage)
Unknown(best_frontier, residual, lineage)
```

`Unknown` means that the declared depth, beam, branching, or resource budget
was exhausted. It is not evidence that no sorting network exists inside or
outside the bound.

---

# Part II. The three programs

## 4. Temporal program: bounded history revision

The temporal program does not append blindly. Given a newly proposed network,
it opens a bounded recent window and may:

- replace one recent layer using the residual visible at the corresponding
  prefix;
- replay the unchanged suffix after that replacement;
- exchange adjacent recent layers.

Its program shape is

\[
P_t:
(N,R(N),h)
\longmapsto
\{N'_1,\ldots,N'_k\},
\]

where `h` is the exact ordered layer history. The output preserves a lineage
step containing parent and candidate hashes, depths, residual counts, weighted
inversions, size, and the declared operation.

This is a small bounded backtracking program. It is not a proof that time is
identical to search history, and it does not yet use a learned characteristic
to choose its replay window.

## 5. Spatial program: residual contraction

The spatial program observes the current output state for all binary inputs.
For a candidate comparator `(i,j)`, it can count exactly how many residual
inputs currently satisfy

\[
x_i=1,
\qquad
x_j=0.
\]

For small channel counts it enumerates every non-empty matching. For larger
counts it builds a bounded pool from high-inversion pairs, greedy matchings,
and construction motifs. Every layer in the pool is then evaluated exactly,
and the best residual-contracting proposals are returned.

Its schematic form is

\[
P_X:
(N,R(N))
\longmapsto
\operatorname{Top}_k
\{N;L\mid L\text{ is an admitted layer}\}.
\]

The spatial program is currently the strongest component in the small
fixtures. Its success supports the narrower claim that the full residual
geometry carries more useful information than a single success/failure bit.
It does not yet establish a general spatial-computer semantics.

## 6. Constructive program: motif grafting

The constructive program proposes named layer families:

- even and odd adjacent matchings;
- a mirror matching;
- block-stride matchings at powers of two.

It has the form

\[
P_K:
(N,\mathcal M)
\longmapsto
\{N;L\mid L\in\mathcal M
given the current depth\}.
\]

Here `M` is a finite construction vocabulary. The program supplies reusable
structure and a meaningful baseline. It does not contain complete known
sorting networks as hidden answers.

## 7. Scheduler

The scheduler is explicit and deterministic:

1. call the enabled append programs on every beam member;
2. canonicalize and deduplicate proposed networks;
3. call temporal replay on a bounded prefix of the ranked appended proposals;
4. combine and deduplicate all candidates;
5. return immediately if a candidate has zero residual;
6. otherwise retain the best declared beam and advance one depth.

The deterministic final tie breaker is the candidate hash. Repeating a run
with the same configuration therefore produces the same artifact. The CLI
emits one flushed JSON progress record after every completed depth so long
runs remain observable without weakening checkpoint determinism.

---

# Part III. Running the experiment

## 8. Small exact run

From the repository root:

```bash
python -m experiments.verified_witness.sorting_network search \
  --channels 5 \
  --max-depth 5 \
  --beam-width 16 \
  --spatial-branching 12 \
  --construction-branching 8 \
  --temporal-branching 6 \
  --checkpoint .adva/sorting-5.checkpoint.json \
  --output .adva/sorting-5.result.json
```

Verify the resulting file independently:

```bash
python -m experiments.verified_witness.sorting_network verify \
  .adva/sorting-5.result.json
```

Continue a bounded run from its last completed depth:

```bash
python -m experiments.verified_witness.sorting_network resume \
  .adva/sorting-5.checkpoint.json \
  --max-depth 7 \
  --output .adva/sorting-5-resumed.result.json
```

## 9. Ablations

The enabled programs are explicit:

```bash
--programs construction
--programs spatial
--programs spatial,construction
--programs temporal,spatial,construction
```

A valid comparison must retain the same channel count, depth bound, beam
width, proposal limits, memory limit, and verifier. Search effort should also
be reported; witness quality alone does not identify which program caused an
improvement.

## 10. Resource behavior

The exact bit-parallel carrier scales exponentially. Its base storage is
estimated from approximately

\[
(3n+2)2^n
\]

bits before the bounded evaluation cache. The actual Python process has
additional integer, object, candidate, and lineage overhead.

The machine therefore:

- checks a declared oracle memory limit before search or standalone verification;
- bounds the evaluation cache with least-recently-used eviction;
- requires an explicit override when the base estimate exceeds the limit;
- writes atomic checkpoints at completed depth boundaries.

Example local enlargement:

```bash
python -m experiments.verified_witness.sorting_network search \
  --channels 10 \
  --max-depth 9 \
  --beam-width 512 \
  --spatial-branching 128 \
  --construction-branching 16 \
  --temporal-branching 64 \
  --temporal-backtrack 3 \
  --evaluation-cache-entries 1024 \
  --max-oracle-mib 4096 \
  --checkpoint .adva/sorting-10.checkpoint.json \
  --output .adva/sorting-10.result.json
```

The memory estimate is a guard, not a promise that the complete search fits
inside that amount. Process-level monitoring remains necessary for large
runs.

---

# Part IV. What this experiment does and does not show

## 11. Positive evidence

The experiment establishes, for the checked finite fixtures:

1. one exact witness format can carry candidate, verifier result, lineage,
   configuration, residuals, and hash;
2. three search programs with different access patterns can participate in
   one scheduler without being identified;
3. the residual set of failed inputs supplies a useful search signal;
4. construction-only and residual-guided search can be compared under one
   exact verifier;
5. a result is cheap to recheck without reproducing its search.

This is the required shape of a future public `Adva Verified Witness`: hard
search, compact witness, exact open verification, and an auditable account of
how the witness was generated.

## 12. Conservative conclusion

The current implementation should be described as:

> a bounded triadic search experiment in the Adva repository with an exact
> sorting-network witness verifier.

It should not yet be described as:

- a stable Adva three-computer runtime;
- a Turing-universal form;
- a record-setting sorting-network solver;
- proof that triadic search dominates SAT, local search, or known synthesis
  methods;
- proof that all three programs make an independent causal contribution.

The strongest current empirical result is that residual-sensitive search can
improve a fixed construction-motif baseline on the seven-channel fixture.

## 13. Red-team assessment

The principal weaknesses are:

1. **host-side status**: the scheduler and programs are Python research code,
   not checked code-as-data interpreted by Rust;
2. **exponential verifier**: full zero-one enumeration cannot reach the
   channel counts of current sorting-network records;
3. **weak temporal evidence**: temporal replay is present and exercised, but
   its independent advantage is not yet demonstrated;
4. **baseline weakness**: construction motifs are a calibration baseline, not
   a comparison with state-of-the-art SAT or evolutionary synthesis;
5. **cache and lineage cost**: exact output states and provenance can dominate
   memory before the raw input carrier does;
6. **no optimality certificate**: `Found` gives existence only.

These are not incidental engineering defects. They identify the next research
boundary.

---

# Part V. Next work

## 14. Immediate local experiments

The next useful run matrix is:

- channels `6` through `10`;
- several fixed depth bounds around known constructions;
- construction-only, spatial-only, spatial-plus-construction, and full
  three-program ablations;
- fixed evaluation budgets as well as fixed beam widths;
- repeated reporting of runtime, peak resident memory, generated proposal
  counts, residual trajectories, and witness size.

A temporal contribution should be claimed only when removing temporal replay
reliably worsens success rate, residual contraction, witness size, or required
search budget.

## 15. Route toward record-scale search

The exhaustive carrier should remain the final verifier for channel counts
where it is affordable. Record-scale search requires a different proposal
oracle, most plausibly:

1. counterexample-guided synthesis over a growing finite input set;
2. an incremental SAT/SMT backend that emits an independently checkable
   network witness and, when relevant, an unsatisfiability certificate;
3. a Rust bit-parallel and parallel candidate evaluator;
4. symmetry quotienting of channel permutations, reversal, and complement;
5. learned residual characteristics that predict useful layer families;
6. an exact final verification path independent of the proposal model.

The key discipline remains unchanged:

\[
\boxed{
\text{search may be heuristic or learned}
\quad\text{but the emitted witness must be exact and independently checkable.}
}

## 16. Brief assessment

The initial intuition survives in a restricted but operational form. Adva can
already host a finite witness-search protocol with three nonidentical programs
and exact artifacts. The decisive ingredient is not the name “three
computers”; it is the separation of ordered history revision, residual-space
contraction, and reusable construction syntax under one verifier.

The next bottleneck is no longer whether the idea can be made executable. It
is whether the temporal and constructive programs can acquire search signals
that are genuinely complementary to residual contraction, and whether the
same protocol can cross from exhaustive calibration to record-scale
counterexample-guided synthesis.
