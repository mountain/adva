# Symbol surface: representation before evaluation

Status: **Proposed external representation**, based on Adva main
`17fe19e283011f3c4361112f2fe25e4cdae9407e` and Research 0109/0110.
No Rust semantics, library catalog or native operations are changed.

## Question and boundary

Can the proposed symbols, construction history and mathematical application
obligations be written down using the existing research document envelope,
without evaluating the game or silently treating representation as proof?

`symbol-surface.adva` uses the existing
`adva.neutral-carrier-graph.research` version-0 envelope. Its three carrier
structure strings reference the exact SHA-256 bytes of `presentation.json`,
`contract.json` and `obligations.json`. They are documentary integrity references,
not authenticated provenance or a new native payload resolver. Native loading
does not interpret these external JSON payloads. The ready `verify` frame has
no discharges and no recorded outputs. The nine frontier coordinates index
document annotations; they are not native encodings of nine mathematical goals.

This is a proposal for representation in the existing container, not evidence
that Adva already executes this mathematical language. In particular, the
name `inspect` on the entrypoint does not introduce a native inspection command.

## What is represented

| Object | Representation | Boundary |
| --- | --- | --- |
| `i`, `pi`, `-1` | Named symbols with explicit types | Display width is not AST arity; `pi` may be one token |
| `H(a,b,c)=a-b*c` | Binary-constructor AST with three holes | Proposed external syntax, not new native primitives |
| Filling `H(0,1,1)` | Three occurrence IDs and a fill map | The two occurrences of one remain distinct; the equality to negative one is an unexecuted claim |
| Integer/real symbols in complex expressions | Declared canonical embedding boundary | No native coercion or type-proof installation |
| `S`, `S-bar`, `S-wedge` | Two symbolic value catalog declarations and a construction journal | The preceding catalogs are not fully migrated; the journal is not exterior algebra |
| The prior `r-pi` derivation | Five equation strings with origin and branch annotation | Not a replayable native proof; references do not create native copy |
| Codes `0`, `20`, `22` | Prefix-free finite words for the three symbols | Addresses, not the numbers denoted by the symbols |
| Cantor construction | Two affine-map strings and a finite-interval schema | No interval arithmetic, limit calculation or infinite branch chosen |
| Three named theorems | Preconditions, conclusions and missing instantiations | Application status stays Open |
| `game` block, `status: ProtocolProposal` — the prose label **"Reverse-Nim proposal" is withheld, not adopted** | History, exit and finite-fuel annotations | The block carries no game name and no rules: players, turns, legal moves and winner remain unspecified |

The last row's label is **withheld rather than adopted**. The payload carries no
game name and declares its four rules missing, so naming it now would grant by
location what the block does not contain (M2: location grants nothing), and
`game.continuation` says to attach an open question or `DirectionMissing` and
never invent progress. The former prose label is retained above as a comparison
column (M5). The name is deferred to the naming record in the
**protocol-engineering** repository, `naming-decision-symbol-surface-game-2026-09-11.md`
(cross-repository reference; no bytes copied).

The finite word `020` decodes syntactically to the names `i`, `pi`.
This does not place either mathematical value inside the Cantor set. A finite
word retains its length and terminator; zero padding is not an equality rule.
Cantor's two retained branches also do not establish a three-way correspondence
with the three collection declarations.

The recorded logarithm convention is branch index zero with the principal
argument value `Arg(-1)=+pi`. This does not assert a holomorphic logarithm on
a domain passing through its branch cut. All future divisions must first
justify their nonzero denominators. No equality of local values identifies
occurrences, closes an M6 obligation or grants native `free`.

## Result and reproduction

Run from the repository root with Python's standard library on Linux:

```sh
python experiments/symbol_surface/construct_records.py
timeout 5s python experiments/symbol_surface/inspect_representation.py
```

The first command writes the fixed records and updates their digest references.
The second reads at most 32,768 bytes per input, rejects duplicate JSON keys,
and checks the specified references, frontier annotations, ready frame,
symbol codes, hole bindings and unexecuted statuses. It writes
`inspection.json`. It is a fixed-record external check, not a general schema
validator or substitute for Rust authority. Do not treat its digest generation
as verification of the truth of an edited payload.

Observed result: `ExternalRepresentationConsistent`, with **nine open
obligations**. Static inspection took **0.367885 ms**; the Linux process peak
RSS was **9,984 KiB**. Arithmetic evaluations, game moves and search nodes were
all zero. Construction, serialization, research and network costs were not
measured. Timing and peak RSS can differ on replay. No performance improvement
or new mathematical expressiveness is claimed.

Native loading is **NotRun**: this environment had no available Rust compiler,
and the available CLI did not provide a read-only document-load command.
The native `verify` mechanism was not executed. No source changes or substitute
Python semantic implementation were introduced to bypass this boundary.

## Residual obligations

1. Supply or replay the negative-one derivation with typed embeddings.
2. Establish occurrence-preserving translation into actual native syntax.
3. Prove the intended prefix codec beyond this finite structural instance.
4. Specify the relation between finite addresses and Cantor-prefix intervals.
5. Supply both injections for a particular Schroeder-Bernstein application;
   an equal cardinality would still not prove structural faithfulness.
6. Fix a complete lattice and prove operator monotonicity for Knaster-Tarski;
   fixed-point existence does not promise finite iteration convergence.
7. Supply nested-interval premises and, for uniqueness, shrinking lengths;
   a finite prefix does not deliver an infinite-precision point.
8. Type and replay the prior pi derivation, including branch and division guards.
9. Define the game's legal turns and exit condition before allocating fuel, and
   decide the game's name only after those four rules exist.

The named theorems themselves are established mathematics. What remains open
here is their application to the proposed objects. Likewise, leaving the
elementary negative-one claim unexecuted does not suggest that it is an open
mathematical problem.

This record helps Mingli and subsequent collaborators distinguish a symbol,
its construction, its address and its verification obligations in one reviewable
place. It introduces no newly learned word and establishes no universality,
global completeness, infinite computation or real-user benefit.

The next smallest engineering step is a read-only load using the existing Rust
document loader once a compiler is available, retaining all outputs as absent.
Only after that boundary is checked should one separately authorize and
implement a typed translation or proof replay for a single obligation.
