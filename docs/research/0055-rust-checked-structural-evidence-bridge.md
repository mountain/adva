# Rust-Checked Structural Evidence Bridge

Status: bounded research bridge following
[`0054-finite-linear-synchronized-evidence-tensor.md`](0054-finite-linear-synchronized-evidence-tensor.md).

The executable fixture is
[`tests/python/test_checked_lineage_evidence_bridge.py`](../../tests/python/test_checked_lineage_evidence_bridge.py).

Note 0054 introduced a synchronized evidence carrier with explicit resource
routing, but its resource identifiers were research-local Python strings.  The
present calibration removes that source of semantic authority.  Every tested
resource identity now comes from an existing Rust-certified causal cut or
program slice.

The central result is:

> The linear permutation-plus-continuation grammar survives as the
> arity-preserving fragment of checked program flow.  Copy and discard do not
> arise by weakening that grammar; they enter as separately recorded Rust
> events with exact source, occurrence, lineage, and history data.

This grounds the resource distinction used by the proposed evidence tensor.
It does not yet ground the finite \(T/X/K\) presentation semantics in one
shared Rust program model.

---

## 0. Executive construction

The fixture compiles four small Adva functions:

| fixture | checked resource form |
|---|---|
| `independent-sum` | two inputs with distinct sources and occurrences |
| `exchange-sum` | two resources explicitly permuted by `swap` |
| `shared-sum` | one occurrence explicitly branched by `copy` into two children |
| `drop-left` | one input explicitly consumed by `discard`, while the other passes through |

For every causal-cut wire \(w\), the Python research view reads only

\[
R(w)=\bigl(\operatorname{sources}(w),\operatorname{lineage}(w)\bigr)
\]

from the Rust result.  It allocates no `SourceId` or `OccurrenceId`, performs
no identity inference from values, and is never accepted back as semantic
input.

The four cases separate the structural rules exactly:

| operation | consumed | produced | occurrence law | retained history |
|---|---:|---:|---|---|
| independent boundary | — | 2 | two sources, two root occurrences | source events |
| `swap` | 2 | 2 | same occurrences, reversed routing | operation event |
| `copy` | 1 | 2 | one parent, two new children, one source | copy and operation events |
| `discard` | 1 | 0 | consumed occurrence has no output | operation event |

The whole `drop-left` frontier changes from two resources to one because the
unconsumed right input remains a through wire.

---

# Part I. What counts as a checked resource

## 1. Source and occurrence are different coordinates

`SourceId` answers which original program resource an occurrence descends
from.  `OccurrenceId` answers which concrete use or branch of that resource is
present at a boundary.

They must not be identified.  Before copying, a one-input function has one
source and one root occurrence.  After an explicit `copy`, the two output wires
have:

- the same source;
- distinct child occurrences;
- a recorded common parent occurrence; and
- a `HistoryEvent::Copy` naming the copy node, parent, and ordered children.

Thus source equality expresses descent, not permission to alias two ports.

## 2. A causal-cut wire is the boundary carrier

Rust supplies a `CutWire` containing:

- the exact `WireRef` and producer;
- its ordered occurrence lineage;
- its source set; and
- its unique future consumer.

The cut certificate checks the completed past and lineage preservation.  The
research adapter retains only the source and lineage fields required by this
calibration, but the complete checked wire remains available in the native
snapshot.

This is stronger than the string guard in note 0054.  Distinctness is no
longer a convention chosen by the evidence experiment; it is derived from the
validated program diagram.

## 3. Independent inputs

The initial cut of

\[
\operatorname{add}(\mathit{left},\mathit{right})
\]

contains two resources.  Each has one source and one occurrence, and the two
sources and occurrences are pairwise distinct.  Their identifiers agree
exactly with the Rust source partition.

This is the checked counterpart of introducing

\[
e\otimes_s f
\]

from two independently available evidence resources.  No host-language
object identity participates.

---

# Part II. The arity-preserving fragment

## 4. Explicit exchange

For the `exchange-sum` function, the first event is `swap`.  Its checked causal
step consumes two resources and produces the same two source-lineage pairs in
reverse order:

\[
(r_0,r_1)
\xrightarrow{\mathrm{swap}}
(r_1,r_0).
\]

The corresponding program slice contains one `swap` node and one operation
history event.  It contains no copy event.

This realizes the exchange witness proposed in note 0054.  Exchange is not a
consequence of equal support or Python tuple reordering; it is a checked
program event whose lineage rule is part of the Rust operation registry.

## 5. Linear routing survives

The important point is not merely that `swap` works.  It is that the two
occurrences are neither duplicated nor removed.  The input-to-output relation
is a bijection.

Therefore the note-0054 rule

\[
\text{permutation}
+
\text{componentwise causal continuation}
\]

has a genuine checked program interpretation for arity-preserving structural
flow.  Its Python resource strings can be replaced by the occurrence
lineages returned by Rust.

This conclusion remains bounded: the fixture checks identity of the selected
finite wires and histories, not a general symmetric-monoidal coherence
theorem.

---

# Part III. Explicit arity change

## 6. Copy is occurrence branching

The first causal step of `shared-sum` is `copy`:

\[
p
\xrightarrow{\mathrm{copy}}
(c_0,c_1).
\]

The fixture checks exactly:

\[
c_0\ne c_1,
\qquad
p\notin\{c_0,c_1\},
\]

while all three occurrences belong to the same source partition.

The program slice also contains a copy history record satisfying

\[
\operatorname{parent}=p,
\qquad
\operatorname{children}=(c_0,c_1).
\]

This is not the diagonal map inferred from

\[
P\cap P=P.
\]

It is a constructive event that replaces one occurrence with two ordered new
occurrences while retaining their descent.

## 7. Discard is visible resource consumption

The `drop-left` function has two inputs.  Its first event explicitly discards
the left input and leaves the right input as a through wire.

Locally the step has shape

\[
r\xrightarrow{\mathrm{discard}}().
\]

Globally the frontier changes from two resources to one.  The discarded
resource is absent from the upper cut, but the slice still contains:

- the `discard` operation node;
- the consumed lower-boundary wire;
- the unchanged right through wire;
- the discard node among internal events; and
- the operation history event.

Therefore weakening cannot be represented by silently dropping a tuple
component.  The disappearing boundary resource leaves a checked temporal and
constructive trace.

## 8. Do not weaken the linear grammar

There are two possible responses to copy and discard:

1. relax the linear evidence map until arbitrary repeated or omitted indices
   are permitted; or
2. keep the linear grammar and add typed structural constructors whose
   certificates explain every arity change.

The finite evidence supports the second response.  The resulting grammar has
distinct generators:

\[
\begin{aligned}
\mathrm{exchange}&:(r_0,r_1)\to(r_1,r_0),\\
\mathrm{copy}&:p\to(c_0,c_1),\\
\mathrm{discard}&:r\to().
\end{aligned}
\]

Only exchange is a resource bijection.  Copy and discard are proof-relevant
program events, not ambient logical privileges.

---

# Part IV. Consequences for the 3-form proposal

## 9. A sharper three-coordinate reading

The checked fixture exposes the three coordinates without treating them as
three copies of the same data:

- **space:** the current cut frontier and its ordered open resources;
- **time:** the completed causal past and retained event history; and
- **construction:** the source-occurrence lineage change performed by each
  operation.

For `copy`, spatial multiplicity increases, temporal history grows, and the
constructive coordinate records one parent with two children.  For `discard`,
spatial multiplicity decreases, temporal history still grows, and the
constructive coordinate records explicit consumption.  For `swap`, spatial
order changes while resource multiplicity and occurrence identity are
preserved.

This is a more concrete candidate 3-form than support intersection alone.
It remains a finite program-process reading, not a finished 3-form logic.

## 10. Consequence for \(L/R\)

Independent \(L\) and \(R\) need not be placed in a single temporal order in
order to coexist at a cut.  Their boundary resources remain distinct.  If
their roles are exchanged, a `swap` event records the routing.  If one is used
twice, `copy` creates two descendant occurrences.  If one disappears,
`discard` remains in the interval history.

The unresolved global reduction problem is therefore decomposed into:

- causal order of events;
- ordered coexistence at a frontier;
- explicit permutation of ports; and
- explicit change of resource multiplicity.

No unexplained \(L\mid R\) symbol needs to carry all four meanings.

## 11. Consequence for startup calibration

Three startup certificates can now have two fundamentally different origins:

- three independent sources; or
- three occurrences descended through an explicit share tree from one source.

These cases may produce equal coarse calibrated values but are not the same
construction.  A future three-computer startup certificate must retain which
case occurred, the ordered child occurrences, and every calibration event.

This is why moving directly from the binary experiment to an unlabelled
three-element tuple would have been premature.

---

# Part V. Verification and boundary

## 12. What the fixture establishes

Within four finite compiled functions, the fixture establishes:

1. two independent input resources have distinct checked sources and
   occurrences;
2. those identifiers agree with the Rust source partition;
3. `swap` is a checked two-to-two resource bijection;
4. the swapped output ordering is exactly the reversed input ordering;
5. `swap` does not create a copy history;
6. `copy` changes one occurrence into two distinct ordered children;
7. the parent and children belong to one checked source partition;
8. the copy slice retains both copy and operation history;
9. `discard` consumes one resource and produces none;
10. the unconsumed resource remains a through wire;
11. the discard node and history remain present despite the missing output;
12. the Python adapter rejects an accidentally duplicated occurrence; and
13. all semantic inputs and certificates originate in Rust.

## 13. What it does not establish

The fixture does not establish:

- a stable evidence, tensor, structural-rule, or 3-form API;
- that every evidence resource is one wire or one occurrence;
- a general categorical interpretation of `copy` or `discard`;
- contraction or weakening as unrestricted logical rules;
- proof normalization, cut elimination, or coherence;
- a checked relationship between \(T/X/K\) presentations and these four
  Adva programs;
- arity-three startup calibration;
- a universal three-computer language;
- a solution to the global \(L/R\) reduction problem; or
- validity beyond the checked finite diagrams.

The test-local `CheckedResource` is a frozen read-only projection of Rust data.
It is not passed back into the kernel and allocates no semantic identity.  The
change introduces no Rust API, IR schema change, `claims.toml` claim, or change
to the active implementation priority.

## 14. The remaining gap exposed by the bridge

The resource problem and the presentation problem are now each grounded, but
not yet joined:

- notes 0051--0054 compute \(T/X/K\) context presentations, causal suffixes,
  and synchronized evidence in a finite research machine;
- the present note obtains exact resource flow from Rust-checked Adva
  diagrams.

There is not yet a checked map saying which Adva program realizes each
\(T/X/K\) generator and transports its presentation evidence.  Treating the
two layers as already identical would reintroduce Python semantic authority.

## 15. Next gate

The next experiment should join the layers on one bounded fixture:

1. represent the finite \(T\), \(X\), and \(K\) actions by explicit Adva
   functions or a checked finite encoding;
2. derive their program histories and resource lineages from Rust;
3. compare Rust execution with the sixteen-element finite transformation
   monoid as an independent oracle;
4. lift one atomic suffix continuation to an exact checked program interval;
5. lift one synchronized exchange to checked `swap` lineage;
6. retain `copy` and `discard` as separate structural evidence constructors;
7. return a certificate or an explicit mismatch rather than identifying the
   two representations by convention.

Only after this joint calibration should an arity-three computation be called
a checked three-computer evidence form.

## 16. Conservative conclusion

The bridge result is:

> Linear evidence routing has a checked realization in Adva boundary lineage.
> Explicit copy and discard extend that fragment through certified occurrence
> branching and consumption; they do not follow from equal support or host
> aliasing.

This supports the resource intuition behind the synchronized tensor while
exposing the next nontrivial task: connect the finite context machine itself to
the Rust program-process carrier.

