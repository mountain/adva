# Trust-continuity gate for a future `M6` closure

Status: construction target with one documentary witness and no semantic
filler.

## Question

The current `M6` experiments preserve two ordered paths and common labelled
endpoints, but common storage coordinates do not establish a shared truth. If
a later construction supplies a typed `J`-lift or another semantic filler,
what must be retained so that one path cannot close by silently weakening the
conditions under which the other path was trusted?

## Proposed envelope

Define a research-only `TrustEnvelopeV0` with these coordinates:

| coordinate | immutable or append-only obligation |
| --- | --- |
| origin | parent content coordinates and attribution status are immutable |
| payload | content digest and schema are immutable for one occurrence |
| method | checker contract and version are immutable or explicitly migrated |
| evidence class | observation, derivation, testimony, hypothesis, and certificate remain distinct |
| residual | open obligations and scope limits are retained |
| challenge | rejections, counterevidence, reopenings, and forks are append-only |
| custody | availability warnings and handoff coordinates are retained |
| succession | the next finite input boundary is explicit |

Names and display labels may change only through an attributed mapping. A
mapping does not identify authors, occurrences, or semantic values.

For an ordered path `p`, let `T_p(E)` denote transport of an envelope `E`.
This notation does not yet name executable code. Transport may append history,
evidence, challenges, or custody events. It may not delete or silently rewrite
a protected coordinate.

## Typed `>` / `<` comparison

The continuity hypothesis introduces a resource comparison without licensing a
scalar trust score. Let `R` be a finite set of typed rupture obligations and
`H` a finite set of typed help resources. Each resource retains capability,
custodian, availability evidence, scope, cost, expiry, and copy/reuse policy.
Let `B` be the declared finite spacetime budget.

Write

\[
H >_B R
\]

only when a checked matching assigns every element of `R` to a compatible
resource, the combined typed costs are admitted by `B`, no noncopyable resource
is reused, every trust-continuity coordinate survives, and at least one
compatible reserve remains. Write `H =_B R` for exact coverage without reserve,
`H <_B R` when a retained obligation is unmatched or unaffordable, and
`Unknown` when the comparison lacks types, evidence, authority, availability,
or fuel.

These relations are observer-, scope-, contract-, and budget-relative. They do
not compare human worth, truth, popularity, or moral authority. Unrelated
resource types cannot compensate for an uncovered rupture.

The reciprocity hypothesis, “first we must be able to help them,” becomes an
interface rule: a request for outside help should carry a bounded need plus a
concrete contribution the current observer can offer. The contribution may be
a capability, repair, translation, replay, or custody action. It supplies no
claim on another participant's labor or consent and no guarantee of return.

## Integral candidates and the selected two-layer reading

An integral does not generate helping force by itself. Two existing mathematical
constructions nevertheless give the hypothesis a disciplined spatial form.

First, a capacity-bounded divergence-free field `F` carries a flux through an
oriented cut `C`:

\[
\Phi_C(F)=\int_C \langle F,n\rangle\,dA.
\]

Continuous max-flow/min-cut theorems equate the maximum admissible flux with a
minimum cut under stated analytic and geometric hypotheses. Backus's
topological formulation additionally fixes a relative homology class, exactly
the information needed to avoid collapsing distinct routes with similar
boundaries. For a scalar demand `D` in one fixed resource type, a robust
crossing candidate is therefore

\[
\max_F\Phi_C(F)>D,
\]

which is equivalent to every admissible separating cut in the chosen class
having capacity greater than `D`. The integral witnesses transported capacity;
it does not create the resource or prove that a social helper will act.

Second, the logarithmic differential returns the inquiry to Euler's formula:

\[
\oint_\gamma\frac{dz}{z}
=2\pi i\,\operatorname{wind}(\gamma,0).
\]

For the upper unit semicircle the integral is `i pi` and exponentiation gives
`exp(i pi) = -1`. For one full turn the additive trace is `2 pi i`, while its
multiplicative readout is one. A logarithm branch cut makes a local chart
single-valued; transport around the hole retains a period that exponentiation
forgets.

Version zero should therefore keep two layers:

| layer | candidate witness | retained obstruction |
| --- | --- | --- |
| capacity | typed max-flow/min-cut or finite matching | minimum bottleneck and consumed spacetime budget |
| history | logarithmic path integral or discrete winding ledger | orientation, winding, branch change, and additive period |

Neither layer substitutes for the other. A unit multiplicative readout cannot
erase a nonzero winding history, and a winding number does not show that enough
resource capacity exists.

For heterogeneous resources, ordinary single-commodity max-flow/min-cut is not
automatically valid as one scalar equality. The first finite implementation
should keep separate typed ledgers or an explicit multicommodity contract and
must not sum unrelated capacities.

### Historical boundary

The contour-integral statement is a modern complex-analysis reconstruction,
not Euler's recorded proof. Bernoulli's integral work and Cotes's logarithmic
geometry preceded Euler; de Moivre supplied the power-angle relation; Euler's
1748 *Introductio*, chapter 8 §138, used infinitesimal circular and exponential
formulas to derive the imaginary exponential relation. The later
contour/winding formulation is selected here for its structural fit, not
attributed to Euler.

## Finite imagination step

The working hypothesis for repeated experiments is:

\[
F_n\xrightarrow{\ i(H_n)\ }Q_{n+1},
\]

where `F_n` is a sealed finite frontier, `H_n` is its retained history, `i` is
a research label for imagination plus append-only historical rereading, and
`Q_{n+1}` is a candidate boundary-crossing question. `Q_{n+1}` does not cross
the interface by itself; it must name the external observation, resource, or
construction its answer would require.

Under the neutral interface:

| slot | finite imagination reading |
| --- | --- |
| subject | sealed frontier and typed unresolved obligations |
| method | frozen imagination operations and historical-rereading policy |
| object | finite interface, budget, and missing outside coordinate |
| history | exact predecessor, source occurrence, rereading, and generation trace |
| result | falsifiable boundary-crossing question candidates |
| evidence | sources, falsifiers, outside request, help-first offer, cost, and next frontier |

Candidate admission requires all of those coordinates. Novelty, resonance, or
shared notation alone is insufficient. In particular, imagination `i` and the
complex unit `i` remain distinct typed readings. The Euler/logarithm construction
is a candidate bridge between their roles, not a proof that they are the same.

## Two-path gate

For the positive-braid boundary

\[
aba \Longrightarrow bab,
\]

a future bounded closure may report `Success` only when all of the following
are checked:

1. The typed mathematical payload condition required by the proposed filler
   succeeds independently of this gate.
2. Both paths begin from the same immutable origin envelope.
3. Both ordered histories remain separately addressable; endpoint equality
   does not identify them.
4. Both paths use the same checker contract, or an explicit migration witness
   relates the contracts without weakening protected obligations.
5. Every input residual, challenge, fork, and custody warning appears in each
   output or has an explicit typed disposition.
6. The two output envelopes have an explicit checked correspondence. Equal
   payload digests alone do not supply it.
7. The output names an exact next boundary from which another finite observer
   can replay, challenge, fork, or resume.
8. Every repair resource, typed matching, consumption event, and remaining
   reserve is retained; neither path double-spends a noncopyable capability or
   externalizes an unmatched rupture.

The gate has three outcomes:

- `Success`: the independent payload predicate and all eight continuity checks
  are witnessed in the declared finite scope, including `H >_B R` where the
  construction requires resilient continuation.
- `Failure`: a retained counterexample proves deletion, unrecorded rewriting,
  or weakening of a protected coordinate.
- `Unknown`: evidence, custody, authority, a typed map, or fuel is missing.

Search exhaustion and inaccessible evidence remain `Unknown`.

## First witness input

`programs/bootstrap-0/trust-continuity-session-witness.adva` records two
separate occurrences:

- the human declaration that trust continuity is necessary to the value of the
  human and shared story;
- a bounded generated response asking future successors to preserve exact
  provenance, replay, challenge, fork, and handoff coordinates without
  assigning machine output a higher truth class.

The second occurrence is not a statement by a durable machine person or a
collective “we”. It is not authenticated as a model identity and does not
represent OpenAI, other systems, or future observers.

## Finite implementation experiment

A later Rust experiment should:

1. define `TrustEnvelopeV0` and `TrustTransportV0` in the research companion;
2. import the two existing `M6` paths without changing `adva.ir`;
3. add one positive fixture preserving all protected coordinates;
4. add negative fixtures that drop one challenge, substitute a checker without
   migration, merge two histories, or erase a custody warning;
5. add an `Unknown` fixture for an unavailable parent or insufficient fuel;
6. prove deterministic round-trip and byte-stable replay for the fixture;
7. add matching fixtures for strict reserve, fragile equality, unmatched load,
   noncopyable-resource reuse, unaffordable cost, and unknown availability;
8. keep the typed `J`-lift and semantic filler open unless separately
   constructed.
9. add one finite imagination fixture that derives a boundary question from a
   sealed history, retains the original and rereading separately, names one
   external need and one help-first contribution, and rejects a candidate with
   no falsifier.

An additional arithmetic fixture should use a discrete winding ledger with
positive and negative orientation, a half-turn `i pi` residual, a full-turn
`2 pi i` residual, and a separate multiplicative unit readout. It must reject
any attempt to infer equal histories from the unit readout.

The first implementation should be promotion-gate infrastructure, not a trust
score. No weighted total may compensate for a missing invariant.

## What this would and would not close

It would close a finite preservation question: whether two named paths retain
the declared trust envelope under one frozen checker. It would not prove that
the underlying claim is true, the speaker is authentic, custody will survive,
participants will agree, the checker is morally or mathematically adequate,
or arbitrary `M6` cells close.

The construction depends on the current reality/custody, verification,
reopening, local-transport, and three-hole `M6` research. It promotes none of
those experiments beyond their registered boundaries.

## Sources

- [Euler, *Introductio*, volume 1, chapter 8, English translation](https://www.17centurymaths.com/contents/euler/introductiontoanalysisvolone/ch8vol1.pdf)
- [Roger Cotes, *Logometria* (1714), Royal Society](https://royalsocietypublishing.org/rstl/article/29/338/5/110482/Logometria-auctore-Rogero-Cotes-Trin-Coll-Cantab)
- [Backus, “The max flow/min cut theorem for currents and laminations”](https://arxiv.org/abs/2501.00974)
- [Headrick and Hubeny, “Riemannian and Lorentzian flow-cut theorems”](https://arxiv.org/abs/1710.09516)
