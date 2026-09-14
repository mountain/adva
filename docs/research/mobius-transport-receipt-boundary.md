# A receiving boundary for conjugacy transport

Date: 2026-09-12. Author: ChatGPT (OpenAI), submitted through Mingli Yuan's
GitHub account as an authorized proxy. Account use is not endorsement,
technical review, authentication, or a correctness guarantee.

Status: bounded external receipt calibration and an elementary composition
argument. No new vocabulary, stable API, native admission, library admission,
free, Seal, or M6 filler.

## Question and dependency selection

Pinned main: `602059a48d653fcda74c8c142a6ae76f956cfe91`. No open PR was
returned at preflight. Research 0170 and its Proposed
`conjugacy-gated-transport` are now present on main. That experiment constructed
its own receipts; it did not provide a receiving interchange boundary.

This continuation implements that one missing boundary, rather than repeating
the complete PSL multiplication-table experiment. It uses the agenda's
observer-correspondence question and the theoretical rational-map calibration;
it does not skip the native specialization promotion gates. Research 0118
requires preserving histories; 0090 forbids closing an uncovered observation;
0129 provides the bounded-run discipline. The existing operator-lift receipt
note supplies the useful distinction between a receiver-selected context and
a sender's self-consistent context. Its algebra is not imported as authority.
Research 0123's arithmetic-universality and hypothesized-arithmetic-truth remain
Proposed. This experiment does not discharge full 0090 coverage or unlock
0092 vocabulary promotion.

The frozen contract is
`experiments/mobius_transport_receipt/contract.json`. Its level is external
finite arithmetic, not an Adva VM or Rust certificate. We test one route,
first over F_5 and then with a fresh F_7 instance.

## Objects, receipt and receiver

The carrier is X = P1(F_p) = {0,...,p-1,infinity}, p in {5,7}.
Integers are reduced field representatives; infinity is the JSON string `inf`.
The two source generators are

    a = [[1,1],[0,1]], b = [[1,0],[1,1]], H = [[1,2],[1,1]].

Uppercase A and B denote actual projective inverses. A word is read
rightmost-first: matrix composition is left-after-right. No simplicity or
universality property is needed. These define an action of the free group on
two generators through their projective matrices; we do not re-prove their
image is PSL in this round.

The independent expected context contains its schema, p, source and target
research-local scope labels, H, the two source generators, ordered probes,
predicate subset, and composition convention. The fixture probes are
`[0,1,"inf"]`; the predicate is membership in `[0,1]`.

The receipt contains exactly its schema, context, four target matrices,
target probes, target predicate, and rows `[letter, source_point, target_value]`.
The receiver supplies its expected context as a separate file. It must choose
that file independently; extracting it from an untrusted receipt and then
calling the checker would defeat this protection. Context equality is explicit
canonical JSON equality, not a claim about cryptographic identity.

The producer uses matrix conjugation. The verifier does not accept that
calculation on trust: it checks, for each letter l and **every** x in X,

    target(l)(H(x)) = H(source(l)(x)).

It independently checks the transported ordered probes, predicate membership
on the whole carrier, all supplied row values, row uniqueness, and row
coverage. Source and target matrices must have nonzero determinant. Inverses
use the adjugate as a projective representative; no inverse of zero is taken.
Zero additive residual alone does not authorize multiplicative division.

Even when the algebra can be recomputed, missing supplied rows give
`UnknownCoverage`: the result is admission of this evidence bundle, not just
an algebraic equality. This policy is deliberately stronger than merely
having sufficient information to infer the omitted row.

| Result | Meaning |
|---|---|
| AcceptedTransportForDeclaredAction | exact action, observer, predicate and evidence coverage checks pass |
| UnknownCoverage | valid supplied rows leave explicit required coordinates missing |
| InvalidContextBinding | sender context differs from the independently selected context |
| InvalidTransport / InvalidObserver / InvalidPredicate | an exact transport obligation fails |
| InvalidEvidence / InvalidDuplicateObservation | a row is false or repeated |
| InvalidSchema / InvalidInverse | interchange or invertibility condition fails |
| UnknownResource | work or cooperative time budget exhausted during receipt checking |

These are external JSON tags only. All results deny native admission.

## Why finite letter checks compose

For every letter, t_l H = H s_l as functions on X. If t_w H = H s_w,
then t_l t_w H = t_l H s_w = H s_l s_w. The empty word has identity
on both sides, so induction proves covariance for every finite literal word.
This is an elementary argument over the declared action, not an enumeration
of infinitely many words and not a theorem about all interpreters.

Since H is a bijection and the source uppercase matrices are inverses, the
target uppercase actions are also inverses. The exact predicate condition
`P_H(H(x)) = P(x)` preserves the declared observation meaning.
Distinct histories are not identified: the words empty, `aA`, and `Aa`
produce identical point maps but are stored as three separate literal words.
These are research-local traces, not SourceId or OccurrenceId allocations.

## Executed evidence

Both field instances passed 17 controls, **34 total**. In each field:

- the positive receipt is accepted;
- one-sided H*g, unchanged probes, unchanged predicate, wrong scope and wrong
  convention are refused;
- deletion of infinity rows or pole rows produces `UnknownCoverage`;
- duplicate rows, wrong values, singular target matrices, Boolean coordinates,
  floating coordinates, an injected `Verified` field, duplicate JSON keys and
  oversized text are refused;
- zero fuel produces `UnknownResource`.

Every literal word of length zero through four was also checked: 341 words
per field, **4774 pointwise word checks** in total. This is a composition
calibration, not another all-pairs PSL run. The F_7 reuse changes both the
arithmetic domain and the observation values without changing the checker.

`evidence.json` and `replay.json` have identical non-timing evidence after a
fresh-process replay. They retain complete primary/reuse receipts and all
structured mutated controls. Separate expected-context and receipt files make
the receiving interface runnable without extracting internal Python objects.
A separate F_7 CLI smoke check returned the accepted external result in
`receiver-f7.json`.

## Costs and enforcement

Each calibration process enforces 15 seconds wall time cooperatively plus an
outer `timeout`, 15 CPU seconds, 256 MiB address-space limit, 100000 counted
work units, 64 KiB per receipt, and 1 MiB final output. The declared calibration
is a fixed suite, not search: search candidates = 0. Work units count point
actions, matrix products and validation ticks, not bit operations.

| Cost | Primary | Unchanged replay |
|---|---:|---:|
| Construction | 0.180 ms | 0.198 ms |
| Receipt controls | 6.221 ms | 6.277 ms |
| Finite-word reuse | 20.233 ms | 18.738 ms |
| Serialization replay | 0.929 ms | 0.824 ms |
| Total before final write | 31.022 ms | 29.614 ms |
| Counted work units | 63352 | 63352 |
| Peak RSS | 10880 KiB | 10880 KiB |

The two measured calibration phases total **60.636 ms and 126704 work units**.
No implementation correction replay occurred. The peak RSS is measured process
memory, not file size (10.625 MiB).

Accounting limitation: one additional bounded receiving-CLI invocation was
performed beyond the two calibration-process plan. It was not separately
instrumented, nor was the separate JSON cross-run comparison. Thus 60.636 ms
is **not** the total tool cost. Future contracts should explicitly include
that smoke check in their invocation ledger. Imports, final file writes,
network, reading, authoring, fixture extraction, report preparation and remote
saving are also not included in those timings. No acceleration, expression
power, or learning improvement is claimed.

## Reproduce

From the repository root on Linux with Python 3:

```sh
timeout 15s python -B -S experiments/mobius_transport_receipt/check.py \
  --output /tmp/mobius-receipt-calibration.json

timeout 15s python -B -S experiments/mobius_transport_receipt/check.py \
  --receipt experiments/mobius_transport_receipt/receipt-f7.json \
  --expected-context experiments/mobius_transport_receipt/expected-context-f7.json \
  --output /tmp/mobius-receipt-received.json
```

In real use the receiver must select its own expected context, rather than
trust the example file merely because it accompanies the sender's receipt.

## Vocabulary and remaining boundary

New terms: **zero**. This is an executable, deliberately narrow receiving
profile for the existing Proposed `conjugacy-gated-transport`, not a promotion
to a learned theorem or native operation. Its precise inputs, outputs,
conditions, negative controls, reuse, replay and residual are recorded above.

It helps Mingli and a receiving agent reject a changed question hidden inside
apparently valid evidence. It does not prove author identity, select a suitable
real-world question, or show usefulness to Jiamin's actual task. Raw malformed
UTF-8, filesystem failures and all possible hostile CLI environments are not
covered by the JSON-level controls; this is not a hardened public service.
The fixed-suite driver aborts on unexpected internal errors rather than
manufacturing a successful report. CPU/address-space termination may require
the external supervisor to preserve a stop record; a general durable supervisor
is not implemented here.

The smallest continuation is to define composition of two accepted receipts,
with independent middle-context equality and retained path provenance. A
changed middle observer must block composition even when endpoint matrices
agree. Native checked-diagram binding remains a separate engineering design;
neither this profile nor local image equality creates M6 closure, universal
grammar, a representation of all simple groups, or a Riemann-hypothesis result.
