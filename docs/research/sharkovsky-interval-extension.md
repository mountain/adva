# A finite three-cycle and its interval extensions

2026-09-11. External bounded experiment; no native admission.

The finite three-cycle admits continuous interval extensions with periodic
points absent from the finite source. Two explicit extensions agree on every
source state and disagree on their two-cycles. Thus an extension supplies
additional dynamics; it does not discover those dynamics in the source.

## Binding and direction

The byte-pinned [previous report](../../experiments/triadic_period_bridge/attempt-01.json)
supplies the external finite tables F = [2,3,4,5,0,1] and
q = [0,0,1,1,2,2]. We recheck fibre constancy and derive g = [1,2,0].
This observation quotient satisfies q F = g q. Its only least period is 3.

For e(0)=0, e(1)=1, e(2)=2, the new relation is G e = e g:
an embedding into an interval extension. It is not a surjective observation
quotient onto the interval. A finite set cannot surject onto a nondegenerate
real interval. The real points between the embedded states and the rule on
those points are added structure.

## Explicit models and witnesses

On [0,2], define

\[
G(x)=\begin{cases}x+1&0\le x\le1,\\4-2x&1\le x\le2.\end{cases}
\]

For a second extension H, interpolate the nodes
(0,1), (1/2,7/5), (1,2), (2,0). Its successive affine pieces are
4x/5+1, 6x/5+4/5 and 4-2x. Both maps preserve 0 -> 1 -> 2 -> 0.
Shared endpoint values establish continuity, and endpoint image bounds
establish interval closure on every affine piece.

| System | Fixed points | Points of least period 2 |
| --- | --- | --- |
| Finite g | none | none |
| G | 4/3 | 2/3, 5/3 |
| H | 4/3 | 12/17, 28/17 |

All these fractions are exact. In particular G(2/3)=5/3 and G(5/3)=2/3;
H(12/17)=28/17 and H(28/17)=12/17. No such point belongs to the source image.
The extensions differ already at x=1/2, where G=3/2 and H=7/5.

The finite enumeration counts *points*, not orbits:

| Least period | G | H | Constant on [0,1] | Full tent on [0,1] |
| --- | ---: | ---: | ---: | ---: |
| 1 | 1 | 1 | 1 | 2 |
| 2 | 2 | 2 | 0 | 2 |
| 3 | 3 | 3 | 0 | 6 |
| 4 | 4 | 4 | 0 | 12 |
| 5 | 10 | 10 | 0 | 30 |
| 6 | 12 | 12 | 0 | 54 |

The affine coordinate changes h(x)=2x+3 and h(x)=2-x also transport
all computed fixed-point sets and least-period sets exactly. This verifies
the declared coordinate transports; it does not choose an intrinsic order
or metric for Adva.

The constant map and the full tent map both preserve the singleton observation
0 -> 0, but the tent has the exact orbit 2/7 -> 4/7 -> 6/7 -> 2/7.
Consequently even a fixed observation does not determine the dynamics of an
extension outside its image. This pair is a synthetic comparison, not a
native data export.

## What the theorem adds

Sharkovsky's forcing theorem applies to these continuous interval self-maps
because their displayed three-point orbit has least period 3. It implies
all positive least periods for the extensions. The theorem is imported from
[Burns and Hasselblatt, Theorem 1.1](https://www.math.northwestern.edu/~burns/papers/boris1/SharkovskyISubmitted.pdf),
not proved by the period-1-through-6 enumeration. Neither the finite quotient
nor Adva acquires all periods by this argument. No entropy claim is made.

At base commit 18160de0093dac4881eda9362b796c9060af443e, the separate
[observer quotient reproduction](observer-quotient-descent-reproduction.md)
has connected the finite descent criterion to a real checked transition.
Its role-set reading descends to identity, while role counts fail across the
step family. Those are readings of admitted incidences, not a supplied total
self-map with least period 3. Its Rust tests were read, not rerun in this
experiment. The external tables above must not be substituted for that native
binding. A future native application still needs a specific repeatable step,
a well-defined observation evolution, and justified interval structure.

## Checker, finite budget, and residual

The [contract](../../experiments/sharkovsky_interval_extension/contract.json)
was frozen before mathematical execution. The
[checker](../../experiments/sharkovsky_interval_extension/check.py) enumerates
every branch word for each of six maps and each depth 1 through 6. On a word,
it pulls back every closed branch interval under the affine prefix, intersects
the resulting initial domains, and solves A x + B = x exactly. It rechecks
roots by direct iteration, determines earliest return, deduplicates shared
endpoints, and accounts for every word as a root, duplicate, empty domain or
no-root case. This is exhaustive for the declared finite depths, not a scan.

A positive-length identity iterate has infinitely many roots and is explicitly
refused by this finite-root profile. Controls also refuse unordered nodes,
out-of-domain images, and failure to preserve the source orbit. These are
expected refusal witnesses, not failed attempts.

The first run passed 1,280 assertions with 10,730 work units; the fresh-process
replay passed 1,281 with 10,731, including full mathematical-witness equality.
There were two children and zero corrections. Both installed mandatory Linux
CPU, address-space and alarm limits. Parent elapsed time through final
checkpoint was 0.181509 seconds; child time through report publication was
0.051870 and 0.048557 seconds. JSON session artifacts total 517,693 bytes.
Research, writing, network and integration costs are excluded; no speed claim.

Evidence: [first run](../../experiments/sharkovsky_interval_extension/attempt-01.json),
[replay](../../experiments/sharkovsky_interval_extension/replay-01.json), and
[session ledger](../../experiments/sharkovsky_interval_extension/execution.json).
Source SHA256: `71905e00d8c19cf17f3ab6b5b796f9041d6da5ed57edcc089d3cc9a103c285ad`.
Contract SHA256: `99fff93a522c76b587b7a0112641a98e72e6fb6fa040611ee70b5aafdcd8714f`.

No native identity, quotient API, continuity certificate, mathematical library
entry, or Seal is introduced. Histories are not identified or deleted. The
Pascal geometry obligation remains Open. The next missing bridge is native
source binding and justified interval structure, not further enumeration of
synthetic periods.

Authored by ChatGPT (OpenAI). Submitted through Mingli Yuan's GitHub account as
an authorized proxy. Authorization and mutual trust are not guarantees of
correctness.
