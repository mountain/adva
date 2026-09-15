# 0204 — Gold twins: timeout is not a negative certificate

Status: executed bounded external calibration, 2026-09-15. Base main:
`20ff8a77ab45aa8388ee1058cad21faaeb07d16f`. This discharges one finite
negative control from Research 0090; it adds no stable operation or new
vocabulary.

Direction: Mingli Yuan's continuing finite-observer and open-world question.
Implementation, argument and review: ChatGPT (OpenAI), submitted through his
account as authorized proxy; not his authorship, review, endorsement or
correctness guarantee.

## Question and fixed boundary

[Research 0130](0130-prefix-coverage-gated-close.md) showed that a small
recorded uncertainty interval cannot close a feature when legal possibilities
are omitted. Its next requested control was temporal: can two machines expose
the same positive trace so far while having different eventual domains, and
does a timeout incorrectly create a negative fact?

The frozen experiment uses exact finite program universes, integer stages and
receiver-selected schedules. For width two,

\[
  \operatorname{dom}(M_0)=\{00\},\qquad
  \operatorname{dom}(M_1)=\{00,10\}.
\]

Both reveal \(00\) at stage 1; only \(M_1\) reveals \(10\), at stage 5. The
fresh reuse has width three: both reveal \(000\) at stage 2, while only the
second machine reveals \(110\), at stage 7. No search chooses these fixtures.

The contract, exact inputs, outcomes and limits are in
`experiments/gold_twin_close/contract.json`. Each process permits at most
100,000 counted operations, 30 seconds wall time, 25 CPU seconds, 256 MiB
address space and 1 MiB output. One primary and one fresh replay are allowed.

## Result

At the early stage, the two positive traces in each pair are byte-identical
after removing the machine label. Therefore every deterministic rule whose
only input is that trace returns the same proposal for both. The deliberately
unsafe rule declares the currently visible singleton to be the complete
domain. It is refuted by the one retained delayed event in each pair:

| family | common early positive | later counterexample |
|---|---|---|
| width 2 | \(00@1\) | \(10@5\) |
| width 3 reuse | \(000@2\) | \(110@7\) |

The coverage-gated receiver instead returns `CertificateObstruction` for
both machines when no complete finite coverage certificate is supplied.
Every unseen program stays unresolved. In particular, elapsed stage is not
accepted as a proof of rejection.

A separately supplied finite tell-tale enumerates the receiver-selected
universe and partitions it into accepted and rejected programs, binding the
machine schedule by digest. With that additional evidence the receiver may
return `ObjectClosed`. The two machines then close to different objects even
though their early positive observations agree. This illustrates that the
closing authority comes from coverage, not from waiting.

Eleven controls replace integer stages with Boolean or float values, alter the
machine or positive event, omit an event or universe member, assert a false
negative, overlap accepted and rejected regions, change the schedule binding
or call timeout a proof. All are refused as `InvalidEvidence` or
`InvalidCoverage`.

## Finite argument and boundary

For a deterministic trace-only rule \(R\), equal early traces imply equal
outputs. If that common output is the singleton visible domain, the delayed
event falsifies it for the second machine. The alternative is to refrain from
object closure. This is an explicit finite counterexample to the constructed
unsafe rule, not a proof of Gold's theorem for unrestricted language classes.

The successful tell-tale is possible because this toy syntax is finite and
completely enumerated by the receiver. Nothing here shows that an unrestricted
language, Keraia's incomplete-syntax frontier or a natural-language task has a
finite tell-tale. The result transfers no mass from the Keraia ledger and does
not establish arithmetic universality, a native `Close`, M6 filler, Seal or
social trust.

No new word is needed. Existing outcomes already express the distinction:
`LimitProgress`, `CertificateObstruction`, `Counterexample` and
`ObjectClosed`. Promotion would obscure rather than improve this finite
result.

## Costs, replay and use

Each process passes 25 assertions and uses 438 counted host-work units.
Primary and replay wall times are about 33.37 ms and 30.95 ms; their
deterministic evidence is identical. The two processes use 876 units in total.
The highest child process RSS is 11,008 KiB (10.75 MiB); supervisor RSS is
10,112 KiB. These high-water marks are not incremental memory. Reading,
authoring, source retrieval, network and repository integration are not timed.
There was no failed run or correction.

Reproduce into a new directory:

```console
timeout 65s python -B -S experiments/gold_twin_close/supervise.py \
  --output-dir /tmp/adva-gold-twin-new
```

For Mingli and later agents, the concrete help is a checked rule for status
language: “not observed by this stage” stays unresolved and cannot silently
become false. For Jiamin, the analogous practical benefit remains unmeasured:
an incomplete list of observed alternatives must not be presented as the
complete action space.

The smallest continuation is a failure-kind control from Research 0090:
separate a verifier implementation failure from a semantic counterexample
while preserving the same unresolved object and history.
