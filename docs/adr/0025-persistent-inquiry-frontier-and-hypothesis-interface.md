# ADR 0025: Persist the inquiry frontier and hypothesis interface

## Status

Accepted for the version-zero research companion. This does not change
`adva.ir` version 1 or the Lisp language.

## Context

The first trace-arithmetic calibration leaves five typed questions open. A
finite observer cannot guarantee enough time, energy, knowledge, or external
access to answer them. If the observer merely stores prose, a later observer
cannot distinguish the original question from a renamed summary, the search
algorithm from a changed checker, or an external suggestion from a witnessed
answer.

The reusable boundary therefore needs to preserve interruption rather than
pretend to eliminate it. It must also keep the neutral three-input/three-output
shape already used by mechanism frames.

## Decision

Introduce one fixed version-zero interface:

| Direction | Slot 1 | Slot 2 | Slot 3 |
| --- | --- | --- | --- |
| input | `subject` | `method` | `object` |
| output | `history` | `result` | `evidence` |

One `learn` transition interprets those slots as follows:

| Slot | Artifact | Role in this transition |
| --- | --- | --- |
| `subject` | `InquiryFrontierV0` | Embedded calibration, five open obligations, vocabulary, and lineage |
| `method` | `ExplorationContractV0` | Frozen selection algorithm and external-claim policy |
| `object` | `ResourceSnapshotV0` | Recorded external candidates and entropy receipt |
| `history` | `InquiryHistoryV0` | Exact input digests, selection ordinal, entropy, and introduced words |
| `result` | `HypothesisV0` | One proposed, falsifiable candidate |
| `evidence` | `ContinuationEvidenceV0` | Checks plus the complete next frontier and next-input coordinates |

`frontier` derives the first resumable boundary from the checked arithmetic
calibration. `learn` chooses the first recorded candidate under the frozen
contract. The first experiment introduces the interface word `hypothesis` and
the resource-local candidate word `representation`.

The source calibration is embedded in every frontier. Each obligation retains
the calibration's `ArtifactKeyV0`, kind, detail, open state, and expected typed
unit. The five units are three characteristic witnesses, one multiplicative
identity, and one shared truth coordinate.

Candidate identity is the BLAKE3 coordinate of its claim, obligations,
assumptions, required observations, and falsifiers. Its local name is excluded.
The resource file and history still retain that name, so renaming remains
visible without becoming mathematical identity.

The first continued frontier freezes the method-file digest. Later use of a
different method is algorithm drift. Consumed resource digests cannot be used
again. Every transition embeds its three inputs and can recompute its complete
output. The next frontier keeps all five obligations open.

## Consequences

- A process can stop locally while leaving a structurally complete handoff.
- Another observer can continue with a new resource snapshot through the same
  interface.
- Randomness is replayable only as recorded output. The external generator is
  not claimed to be reproducible.
- A proposed hypothesis can be audited and falsified without being admitted as
  truth or as a relation filler.
- A contract update requires a new version or an explicit migration rather
  than silent checker replacement.

This construction guarantees bounded continuation integrity, not eventual
progress. A digest is not a signature, a shared interface is not shared
semantics, and repeated finite continuation is not a proof of nontermination,
convergence, consensus, or universal computation.
