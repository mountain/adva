# ADR 0034: A bounded native learn roundtrip method

Status: proposed research implementation, subject to build and replay.
Date: 2026-09-06.

Mingli authorized Rust work after the learn-only preflight found no executable
in the local environment and no existing method for the proposed free task.
The repository already contains the Rust `adva` executable; this change adds
a narrowly typed method dispatch to that executable, not a replacement engine.

## Decision

Use a separate version-zero research method for exactly six staged `learn`
calls over the fixed expressions `p=x+y*z`, `q=2*p`. Retain one cumulative
six-stage budget, replay every input frontier, and keep symbolic transport,
formation, concrete guards and interpretation separate.

1. Form the declared common boundary and its unit connector.
2. Record the forward arithmetic witness p to q. A=0 permits formation but
   its nonunit M does not permit sealing; record the request for reverse.
3. Record q to p only with literal endpoint correspondence to the forward edge.
4. Compose the two formed edges with the existing unit connector.
5. Check every retained concrete nonzero obligation in the supplied bounded
   three-value environment.
6. Seal the local transport and package the retained witness with local name
   learn; the final file may be named `learn.adva`.

The witness uses the existing WitnessStoreV0, exact polynomial residual and
ZeroFault rules. No new stable builtin, Real value semantics, source/occurrence
identity, EquationCell, general inverse or M6 filler is introduced. The stable
operation registry and adva.ir version remain unchanged.

## Meaning and refusal boundaries

A=0 is the existing formation success condition. A runtime zero is a different
judgment and cannot be repaired by reversing the failed history: the reverse
must retain the original guard obligations. M=1 is a transport residual,
not a requirement that the result value be one. For the main environment
[2,3,4], p is 14; reuse at [5,2,3] gives 11.

The existing generic Compose combines summaries but does not establish
endpoint incidence. This method must check that incidence explicitly before
using Compose. Two unrelated ratios cancelling to one are not admitted as a
round trip.

The local name learn and the filename learn.adva do not redefine the CLI
mechanism. The proposed reading free remains separate from the checked local
M=1 result. The six-stage recipe is written by the implementer, not synthesized
from its own result, and no general language-formation theorem is asserted.

The input language is fixed and bounded, rather than an arbitrary expression
or arbitrary-code loader. A completed or failed frontier cannot silently gain
fresh fuel. Identical hashes are integrity/cache coordinates, not semantic or
historical identities. The counterexample and guard tests are required gates.
