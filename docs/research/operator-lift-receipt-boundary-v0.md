# Operator-lift receipt boundary, version zero

Date: 2026-09-10. External research implementation, extending the Proposed
`operator-lift` word. No additional stable vocabulary or native judgment.

Main remains `60b37d8a4c155994acc7207f2feecc1da7cc6441`; PR #179 and the
parent PR #180 head `5f5168875cdb328822def9dfca3c26524a492fd4` were still
unmerged when checked. This continuation adds files to #180, preserving its
prior contract and evidence. It changes no Rust code or library content.

## Question and boundary

The previous checker constructed its own standard-basis observations. It did
not validate arbitrary external receipts. This step supplies a deliberately
bounded external JSON checker for dimensions two and three.

The [frozen contract](../../experiments/golden_ratio_operator_lift/receipt-contract.json)
specifies exact rational arithmetic, one fixed word, explicit inverse and
coverage obligations, hostile input controls, and resource limits. Research
0090 coverage, 0118 history preservation and 0129 finite execution rules remain
in force. The full 0090/0092 native obligations are not completed here.

The mathematical justification remains the earlier lemma:

    W(L,v)(x) = x - (L^2 - 3L + I)v,
    W = abbbaBAAB, a(x)=Lx, b(x)=x+v.

The rightmost map acts first and uppercase letters denote actual inverses.
If an explicitly checked basis spans V, zero residual on every basis vector
implies zero on all of V by linearity. Neither the number of submitted vectors
alone nor a submitted `closed` Boolean establishes this premise.

## Input, output and trust allocation

The receipt has exactly four top-level fields:

| Field | Role |
| --- | --- |
| schema | `adva.external.operator-lift-receipt.v0` |
| context | domain, dimension, operator, ordered basis, word and composition |
| context_sha256 | fingerprint of that canonical JSON context |
| observations | distinct basis indices, claimed rational residual vectors and Boolean results |

The receiver supplies **a separate expected context fingerprint**, selected
from an independently chosen local context. The CLI requires this parameter.
Reading it from the incoming receipt would defeat that boundary. The expected
context's suitability for a person's actual question remains the receiver's
responsibility. This is not author authentication, a signature scheme, a
historical identity, or native Adva authority. It is a context-comparison
mechanism using SHA-256; no new cryptographic security claim is made.

The checker rejects unknown fields, duplicate JSON keys, incorrect dimensions,
Boolean indices, floats and noncanonical or oversized rationals. It requires
an invertible operator and a full independent declared basis. Basis vectors
are listed in order as vectors, interpreted as columns for the rank check.
Observation indices refer to that order; observations themselves may arrive
in a different order.

It recomputes the nine affine steps, including the complete linear part, and
independently computes the polynomial residual. It compares both against the
submitted evidence before deciding coverage. Missing observations remain
explicit in the result. No source history is erased by equality of maps.

| Result | Meaning |
| --- | --- |
| ClosedForAllTranslationsByLinearity | all declared basis directions independently replay to zero |
| UnknownCoverage | available directions replay to zero but some are missing |
| Refuted | at least one correctly replayed direction has nonzero residual, even if others are missing |
| InvalidEvidence | the submitted residual or Boolean does not replay |
| InvalidContextBinding | the context differs from the receiver's selection |
| InvalidBasis / InvalidInverse | a necessary algebraic assumption fails |
| InvalidSchema | the bounded interchange format fails |
| UnknownResource | arithmetic work or intermediate-size budget is exhausted |

These names are external result tags, not stable Adva operations. All result
records explicitly deny native admission. A resource stop is not a theorem
about nonexistence. `InternalMismatch` separately signals disagreement between
the two calculations; no such mismatch occurred.

## Witnesses and adversarial controls

All 31 declared controls passed. The producer uses the **previous homogeneous
matrix implementation**, while the new verifier composes linear/shift pairs
from right to left and checks a polynomial oracle. Shared Python Fraction
arithmetic is a remaining common dependency, not independent formal kernels.

1. H=[[1,1],[1,2]] closes both with the standard basis and with the new basis
   ((1,1),(0,1)). The latter is the fresh-instance reuse.
2. C H C^-1, C=diag(2,1), closes when explicitly selected as a new context.
   Offering that same valid, self-rehashed receipt under H's old context is
   rejected. Mathematical closure and answering the selected question are
   separate checks.
3. diag(H,1), observed on only its first two standard basis vectors, returns
   UnknownCoverage. Adding the third vector yields residual (0,0,1) and
   Refuted. Supplying that one negative direction alone already refutes the
   universal translation claim.
4. Forging that residual as zero, or forging only its Boolean, produces
   InvalidEvidence. Dependent bases, duplicate indices, singular operators,
   schema changes and unsupported operation conventions are rejected.
5. A zero-work budget produces UnknownResource. No scope expansion follows.

The full exact input strings, receiver selections, expected statuses and
actual results are retained in [receipt-evidence.json](../../experiments/golden_ratio_operator_lift/receipt-evidence.json).
Two separate CLI processes additionally replayed the fresh basis and the
forged-zero case, obtaining exit codes 0 and 2 respectively; see
[receipt-cli-evidence.json](../../experiments/golden_ratio_operator_lift/receipt-cli-evidence.json).

## Costs and reproducibility

The fixed suite used 7,840 counted arithmetic work units including its
homogeneous producer, zero search candidates, and no correction replay.
Fixture construction took 4.151 ms; suite validation 7.482 ms; fresh-basis
validation 0.407 ms within that total; serialization/round-trip 0.765 ms.
The suite reported its evidence write at 0.091 ms. Peak suite process RSS was
12,288 KiB (12 MiB), measured on Linux. The two CLI processes took 31.225 and
32.686 ms including startup. Their individual peak RSS was not measured.
Research/coding and network costs were not separately timed. No speedup or
expressivity increase is claimed.

Enforced limits: input 16 KiB; dimension 2 or 3; input rational components
32 bits; intermediate rational components 512 bits; 10,000 work units per
receipt; suite at most 40 cases and 100,000 total counted units; 256 MiB
address space; suite CPU 10 seconds and outer wall timeout 15 seconds.
Each CLI replay has CPU and outer timeout limits of 5 seconds. The accounting
units are a bounded implementation counter, not hardware operation counts.
The in-process function relies on its caller for process wall/memory limits;
the CLI installs its own CPU/address-space limits. Use an outer timeout for
file reads as well. JSON decoding and startup are covered by process limits.

Run the fixed suite, choosing an output path that does not already exist:

```sh
timeout 15s python -S experiments/golden_ratio_operator_lift/check_receipts.py \
  --output /tmp/operator-receipts-fresh.json
```

For a single stored test, export its `raw_json` exactly to a file, and use
its separately recorded `expected_context_sha256`:

```sh
timeout 5s python -S experiments/golden_ratio_operator_lift/receipt.py \
  /tmp/selected-receipt.json --expected-context-sha256 RECEIVER_SELECTED_DIGEST
```

The suite evidence pins all checker, producer and contract source files.
Timings vary; compare semantic results and input/context fingerprints rather
than timing bytes when replaying.

## Consequence and next step

This supports the intended direction: a change of representation can preserve
the arithmetic conclusion when its algebraic and question boundaries are
explicit. The important new distinction is between **a valid answer** and
**a valid answer to the receiver-selected question**.

Mingli and subsequent agents can now exchange this small kind of receipt
without trusting its submitted closure flag. No real-task benefit for Jiamin
has been measured. The next minimal integration step is a read-only Python
adapter that selects a local question context and calls this checker while
retaining the original bytes and external status. Any Rust-owned certificate
or native `free` remains a separate, versioned design and validation task.
