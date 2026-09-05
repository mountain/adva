# Research 0118: Local closure transport and adversarial naming

## Question

Can one realizable local closure contribute to a larger structure, be transported
more than once without aliasing occurrences, and survive a comparison between a
direct and a staged route? Can positive and negative observations be named
without turning a type error or an unresolved challenge into falsehood?

The experiment keeps the common interface:

\[
(\text{candidate},\text{verifier},\text{transport plan})
\longrightarrow
(\text{history},\text{result},\text{evidence}).
\]

The CLI command remains `verify`; method-schema dispatch changes the readings of
the three neutral files without adding a `join`, `transport`, or `close` primitive.

## Local closure

The subject is the distributivity identity

\[
a(x+y)=ax+ay.
\]

Both sides normalize to the same exact sparse polynomial. The method inserts an
arithmetic transition whose actual and declared additive boundaries are zero,
then seals its unit multiplicative residual. The resulting certificate contains
the two complete witness nodes and replays without trusting the stored summaries
or artifact keys.

This is a closure only in the exact commutative integer-polynomial fragment. It
does not establish an Adva scalar type, a general expression equivalence, an M6
filler, or a fact about an externally interpreted world.

## Transport square

Let the three scope/occurrence pairs be A, B, and C. The plan supplies the linear
one-slot contexts

\[
f(t)=z+t,\qquad g(t)=bt,\qquad h(t)=b(z+t).
\]

The checker requires syntactic composition `h = g o f` and performs:

\[
C_A \xrightarrow{f} C_B \xrightarrow{g} C_C,
\qquad
C_A \xrightarrow{h} C_C.
\]

The staged and direct `C_C` certificates are byte-identical. Their transport
receipts are not: one cites `C_B` and map B-to-C, while the other cites `C_A` and
map A-to-C. This is the desired finite result: endpoint agreement with preserved
path provenance.

The three occurrence coordinates remain distinct. They are research-local cache
coordinates, not newly allocated `adva.ir::OccurrenceId` values; the stronger
compiler-derived occurrence boundary remains the one in Research 0108.

## Adversarial names

The run records four different outcomes:

| Class | Experiment | Result |
| --- | --- | --- |
| `identity` | `a(x+y)` versus `ax+ay` | exact common normal form and sealed witness |
| `separation` | `a(x+y)` versus `ax+y` at `a=2,x=3,y=5` | `16` versus `11` |
| `incommensurate` | polynomial certificate offered to M6 ordered-holonomy and shared-truth units | two typed rejections; both target holes preserved |
| `challenge` | notice against scope A | A, B, and C reopened; falsity unchecked |

The word `absurdity` is reserved. A single counterexample only separates one
universal identity candidate. A type mismatch says that two claims cannot yet be
compared. A challenge says that review must resume. None is an internal
contradiction.

An incommensurate rejection preserves the target hole but creates no additional
semantic hole in version zero. A future constructive rejection may propose a
typed adapter obligation only under explicit deduplication and resource policy;
malformed or repeated submissions must not grow the semantic frontier.

This distinction also constrains natural-language reuse. For example, the
surface word "is" in identity, subset, and individual predication occupies three
different typed roles. A stable certificate may cross a renaming only when an
explicit interpretation map preserves type, scope, occurrence, dependency, and
method version.

## Counterevidence propagation

The retained dependency graph contains A-to-B, B-to-C, and A-to-C edges. Admitting
a challenge at A computes its finite reachable cone and reopens all three scopes.
The four certificate records (local, B, staged C, and direct C) remain append-only.
The experiment therefore distinguishes:

\[
\text{challenge admitted}\ne\text{certificate erased}
\quad\text{and}\quad
\text{challenge admitted}\ne\text{falsity proved}.
\]

## First run

```console
cargo run -p adva-witness --bin adva -- \
  verify \
  programs/bootstrap-0/local-closure.adva \
  programs/bootstrap-0/closure-verifier.adva \
  programs/bootstrap-0/closure-transport-plan.adva \
  --output programs/bootstrap-0/closure-transport-1.adva \
  --frontier-output programs/bootstrap-0/closure-transport-frontier-1.adva \
  --print
```

The recorded coordinates are:

| Artifact | BLAKE3 coordinate |
| --- | --- |
| subject candidate | `e1659ff6feb01703c70d8eb6035b3460604ba408d003c0b4b41760d084d4f7b3` |
| method contract | `ee6c99bb0be1e0d5f9cbe6c4a44920a0103c1ae64534a5f18212cef4389e2d7b` |
| transport plan | `c2a35b17930c3ecb04c9d549313667ece9a7e72bd7d7401af1f83559fc38e83c` |
| local certificate | `bd79a1c2052b8e50c0bfd02820f5ade0031f13d69cdc2ad555bfc593f86d77b0` |
| common C certificate | `aede178dae5ea22234910192fb1ea23bce4839c59904bfc98ada1ff17aab44ba` |
| challenge notice | `2da40775816aa2062dfca5df6451bdb989d8be77ca3dfa246ba303f991d6d3e2` |
| transition | `d77aa91b02a780051b9e2db97b1684a1ce46af674c3539d94032cd54c0fc735e` |
| reopened frontier | `7dfdb039d09a035ca11b74f1ec73ff33db5c04ecc2ec1a2d159521cf8a6702d8` |

CI regenerates both output files and requires byte equality.

## Growth and geometry boundary

Repeated closure transport can form a growing dependency complex: randomness
may propose names and candidate maps, exact methods select admissible edges, and
append-only certificates retain successful local structure. Version zero does
not yet measure whether reusable closures outpace new holes.

Nor does the experiment place programs in an actual surface moduli space. It is
an algebraic shadow whose vertices are typed polynomial scopes and whose edges
are one-slot contexts. A future geometric interpretation would need a typed map
to a total space over a chosen `M_(g,n)`, plus path, gluing, and holonomy checks.
