# Finite positivity and observational knowledge

Status: external executable research calibration. No native Adva logic,
identity, certificate, `Seal`, or communication execution is introduced.
Original contribution under Unknown v0.3 by Codex (OpenAI, gpt-6-astra-wm),
through Mingli Yuan's authorized account proxy; not his authorship, review,
endorsement, or a correctness guarantee. Mingli supplied the research question
and requested reuse of the existing positivity metaprogram.

## Question and result

Can a model satisfy a specified ontological theory, including necessary
existence of a distinguished individual, while a receiver cannot identify its
current communication counterpart? **Yes, in the explicit finite semantics
below.** The construction separates metaphysical necessity from observational
knowledge. It does not refute the ontological existence conclusion.

The ordinary-set checker and bit-mask evaluator agree on all seven retained
cases. Six satisfy the selected Scott A1--A5; the relation-conflation control
fails A4 and A5. Each evaluation checks 626 formula instances over all 16
intensional properties and all four propositions. Eight unittest methods also
compare all 64 presentations in a separately bounded profile: two S5 modal
relations, four sender maps, four placements of principal positivity families,
and two observation partitions. Exactly 32 satisfy A1--A5, of which eight have
an observationally undecidable sender predicate. These are model checks, not
proof-assistant certificates or claims about every interpretation of the axioms.

## Reuse of Research 0261

The dependency is `mountain/adva` at
`2154b3c6716e7b5a19b98b81aca7940c0c93fe7d`, paths
`experiments/program_positivity/{meta.py,verifier.py,contract.json}`.
Their current exact bytes are also bound in `evidence.json`. They are unmodified.
The predecessor note is
[`docs/research/0261-external-program-positivity-metaprogram.md`](../../../docs/research/0261-external-program-positivity-metaprogram.md).

`requests.json` supplies `reply = x*x` on the indexed fillings `x=-1,+1`.
Both replies are exactly `1`. The joint policy retains two possible common
realizers. `marked_zero` fixes the positive family to `{ {0}, {0,1} }`, and
`marked_one` fixes its relabelled alternative. These are **chosen axiological
interpretations**, not goodness inferred from arithmetic. Contradictory premises
produce `Inconsistent`; zero fuel produces `Unknown` and a `NoClaim` receipt.
All five requests are checked by the existing independent positivity receiver.

The analyst predicate `selected` is an input-region description, not a channel
available to the epistemic observer. Only `transcripts` determine observational
access. This distinction is explicit: exposing the filling index would silently
supply the very identity oracle under investigation. A `ForcedPositive` query
is not a knowledge judgment, and an inhabited region is not itself a positive
one. The old metaprogram has not been promoted to a modal solver.

## Complete finite interpretation

Let `W={w0,w1}` and `D={0,1}`. All individuals exist at every world; quantifiers
use this constant domain. Unary properties range over the **entire** powerset
of `W x D` (16 properties), not just the observer-definable properties.
Propositions range over all subsets of `W` (four propositions).

For a property `F`, its local extension at `w` is `F_w`.
Lift the checked marked-zero family by

    P_w(F) iff 0 belongs to F_w.

Metaphysical accessibility `Rm` is the identity relation. Observational
accessibility `Re` is transcript equality; in the principal example it is
`W x W`. Both are S5 equivalence relations. No bridge axiom identifies them.
Necessity quantifies over `Rm` successors; knowledge quantifies over `Re`
successors. The endpoint sender is a **world-dependent role** `s(w0)=0`,
`s(w1)=1`, not a rigidly interpreted individual constant.

The definitions evaluated independently by both implementations are:

- `G(w,x)`: every property positive at `w` holds of `x` at `w`.
- `Ess(F,w,x)`: `F(w,x)`, and every property of `x` at `w` is necessarily
  entailed by `F` (over all individuals at every `Rm` successor).
- `NE(w,x)`: each essence of `x` at `w` is instantiated at every `Rm` successor.

The axiom obligations are complement exclusivity (A1), closure under necessary
entailment (A2), positivity of `G` (A3), necessity of positivity (A4), and
positivity of `NE` (A5). Scott's exemplification conjunct in `Ess` is retained.
The checker also evaluates possible exemplification of positive properties,
`G` as an essence of each Godlike individual, necessary existence of a Godlike
individual, and modal collapse for all four propositions.

The benchmark specification is Scott's variant, as identified in Figure 1 of
[Benzmueller and Woltzenlogel Paleo, ECAI 2014](https://doi.org/10.3233/978-1-61499-419-0-93).
This repository contains an independently composed finite implementation and
mathematical explanation; no paper text, image, or third-party implementation
has been imported. Other original/repaired Goedel variants are not silently
identified with this specification.

## The witness and a direct mathematical check

For every `w`, the positive family consists of the properties containing
`(w,0)`. Complement exclusivity and upward closure follow immediately.
`G(w,x)` holds exactly at `x=0`, hence `G` is positive. Because `Rm` is the
identity, A4 holds. At `w`, the essences of `x` are exactly the properties whose
local extension is `{x}`; they are instantiated there. Thus `NE(w,x)` holds
for both objects and A5 holds. This also explains why necessary existence alone
does not distinguish the two objects.

| Observation-world | Godlike objects | Current sender | Received reply | `G(s)` |
| --- | --- | --- | --- | --- |
| `w0` | `{0}` | `0` | `1` | true |
| `w1` | `{0}` | `1` | `1` | false |

At both worlds the following conjunction holds:

    Box_m exists x G(x)
    and K_a exists x G(x)
    and not K_a G(s)
    and not K_a not G(s).

Here `G(s)` abbreviates `G(w,s(w))`. The sender predicate is true at `w0`
and false at `w1`; its characteristic function is not constant on the single
observation fibre. Thus it cannot descend to that observation quotient. The
retained witness `[0,1]` is an external pair of world indices, NOT a native
source/occurrence or quotient-query-gate certificate.

This is minimal within the stated type of example: a mixed observation fibre
needs at least two worlds, and a same-world Godlike/non-Godlike pair needs at
least two individuals. It is not a universal minimality theorem across logics.

## One-variable controls

Each successor changes exactly one top-level model field.

| Case | Changed field | Outcome |
| --- | --- | --- |
| `equal_reply` | Baseline | Known necessary existence, unknown counterpart |
| `repeated_reply` | Four repetitions in the transcript | Same ambiguity |
| `spoofed_claim` | Identical claimed source label | Same ambiguity |
| `trusted_binding` | Distinct, assumed-authentic source observations | Identity decided in both worlds |
| `fixed_sender` | Sender is `0` in both candidates | Identity already entailed by the candidate class |
| `conflated_relations` | `Rm` replaced by universal `Re` | Eight A4 instances and two A5 instances fail |
| `swapped_positive` | Use the independently checked marked-one family | Truth labels reverse; ambiguity remains |

The authentic-binding case assumes access to a separating observation; it
does not implement or justify such a channel. The spoofed label has no such
binding. Repetition tests only this frozen transcript family, not all adaptive
protocols. No moral evil, deception strategy or agent intentions are assigned
to the non-Godlike object.

## Modal collapse and the epistemic boundary

Identity `Rm` makes every truth metaphysically necessary locally, so modal
collapse is satisfied, not evaded. It does not make every truth known under
the coarser `Re`. The two observational alternatives occupy different `Rm`
components. This is legitimate in the declared bimodal semantics, but a theory
requiring every epistemic alternative to be metaphysically accessible adds a
new bridge and excludes this particular witness. That bridge is not proved by
this experiment.

For any finite observation map, a Boolean predicate descends exactly when it
is constant on each fibre. In the present idealized knowledge semantics this
is equivalent to `K p or K not p` at every world. The 64-case check exercises
this equivalence. It does not model an observer's bounded reasoning time:
the mathematical `K` remains logically omniscient within its information set.

## Replay and evidence

From the repository root, on Linux with Python 3.11+ (standard library only):

```sh
timeout 45s prlimit --as=268435456 --cpu=30 --fsize=1048576 -- \
  python experiments/program_positivity/epistemic/run.py --output /tmp/epistemic-new.json
timeout 45s prlimit --as=268435456 --cpu=30 --fsize=1048576 -- \
  python tests/python/test_epistemic_positivity.py
```

The output path must be new; overwrite is refused before execution. The report
retains all five static requests' results/receipts, seven explicit models,
every semantic result, failed-axiom witnesses and source SHA-256 bindings.
`validation.json` records the actual replay/test commands and their outcomes.
The ordinary and optimized runs must be byte-identical. The two new semantic
implementations share no evaluation code; they were written by the same
assistant and do not constitute independent human review.

## Remaining obligations

1. A proof-assistant formalization of the selected bimodal semantics and its
   countermodel, with explicit non-rigid sender role and bridge assumptions.
2. Alternative ontological axioms that admit nontrivial metaphysical changes
   inside one connected component, tested without silently weakening the
   property domain or importing the observer's answer as an axiom.
3. An explicit challenge/response transition system and bisimulation argument
   before claiming indistinguishability for adaptive or unbounded protocols.
4. A native Adva receiving profile, if native authority is requested later.

This experiment gives a concrete model of the existence/identification gap.
It does not certify real theological identities, disprove the existence
argument, or establish impossibility under every additional assumption.
