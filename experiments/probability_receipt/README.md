# Receiver-bound finite probability

Status: executed external finite receipt calibration. Base PR #187 commit
`0dbd2d8e048f2ad210eb40cf1834fdcda59604ad`. The native machine and library
dependency locks are unchanged. This is an initial finite probability interface,
not the completion of probability theory or its native Adva implementation.

Authored by ChatGPT (OpenAI), through Mingli Yuan's account as an authorized
submission proxy; not his endorsement, review or correctness guarantee. All new
code, prose, synthetic inputs and generated records are original contributions
under Unknown v0.3. No external materials or software dependencies are vendored.

## What changed

The previous finite-group calibration calculated density energy and exhibited
hidden variation. This continuation makes a sender's proposed calculation
answer an independently supplied receiver context. The receiver binds the
complete finite carrier, reference, probability, observation map, numerical
observable, unit label, history labels and scope before accepting any claim.

The mathematical foundation is a general finite probability space. A group
law is not required: the two group examples are inputs, not restrictions on
future probability questions. This receiver does not recheck their group laws.
Its strings and byte equality do not allocate or identify native Adva objects.

The numerical observable f is now explicit. In addition to density and its
fine/coarse energy residual, a receipt carries E[f], Var(f), the conditional
law on each observed event, and these two exact identities:

    E[f] = sum_B P(B) E[f | B]
    Var(f) = sum_B P(B) Var(f | B)
             + sum_B P(B) (E[f | B] - E[f])^2.

Conditional distributions use the problem's probability p, not its reference
lambda. If P(B)=0, the conditional distribution, conditional mean and
conditional variance are all null. The zero-mass event remains in the reference
and observation records. No arbitrary answer or division by zero is introduced.
Null here means this finite conditioning operation is undefined; it does not
assert that every regular conditional distribution in measure theory is absent.

The unit is a bound documentary label, not an implemented dimensional type.
This version cannot validate metre-to-centimetre conversion or dimensional
consistency. Similarly, provenance labels bind the selected question but do not
authenticate the historical sources or the human's intended meaning.

## One bounded campaign

The [contract](contract.json) was frozen before execution. A separate receiver
implementation runs in a fresh Python process for each candidate. The producer
is never imported by the receiver; both still share Python and Fraction. This
is implementation separation, not formal proof or institutional review.

| Fixture | E[f] | Var(f) | Hidden density-energy residual |
| --- | --- | --- | --- |
| S3, fixed-point count, cycle-type observation | 1 | 1 | 4/3 |
| C4, index, parity observation | 1/2 | 1/4 | 1 |
| C4, identity-only law, parity observation | 0 | 0 | 2 |

All three valid receipts were accepted. Each family also has eleven refused
controls: changed question, recomputed alternative reference, observation or
observable, changed history, erased residual, wrong variance, missing density
element, unsupported global-close claim, Boolean rational numerator and invented
conditional law. The last fixture explicitly tests a zero-probability event.
Every refusal retains the receiver's context and has an empty semantic delta.

The alternative-context candidates were constructed with the producer's
formulas, but their mathematical claims were not separately received under
those alternative contexts in this campaign. The established result is refusal
at the original question boundary, not an extra independently accepted model.

One campaign used **36 fresh receiver processes**, **1,266 counted receiver
work units**, **6.127441137 seconds**, and a highest child RSS of **10,240 KiB**
(10 MiB). Construction, serialization, process startup, checking and reuse share
that time; they were not separately timed. Final report encoding/writing,
archival, research and publication are excluded. There was no search and no
correction replay. The complete records are archived in `evidence/attempt-1.tar.gz`;
`evidence/manifest.json` identifies every member and the archive digest.

## Reproduce

```sh
timeout 30s python -B -S experiments/probability_receipt/run.py --output /tmp/adva-probability-receipt
```

An individual candidate can also be checked against the selected context:

```sh
python -B -S experiments/probability_receipt/receive.py \
  --expected /tmp/adva-probability-receipt/S3-observable-v0/expected.json \
  --candidate /tmp/adva-probability-receipt/S3-observable-v0/valid/candidate.json
```

This bounded local POSIX harness is not a hostile multi-user service. Each
receiver enforces finite schemas, canonical rational pairs, 32 KiB inputs,
10,000 counted work units and a three-second timer. The supervisor additionally
limits child address space, CPU, output and the 30-second/36-process campaign.
Unexpected process or implementation failures fail the campaign and preserve
partial files. An accepted receipt authorizes only the named finite check;
native probability import, Close and free are explicitly false.

## Integration correction

The previous PR's general Python CI failed its terminology-path test because
the newly added `mean-constraint-match` term used a string `origin` where the
existing checker expects an object. The fix wraps the unchanged attribution
in an `authorship` field; it does not weaken the test or change the mathematics.
The native mean-program CI had separately passed.

This host lacks pytest, so the targeted pytest command did not start. The five
unchanged, zero-argument test functions in `test_terminology_homes.py` were then
executed directly with Python's runpy and all passed. This is not a local run
of the full pytest suite; the repository CI remains its separate gate.

## Remaining work

This closes one finite receipt-construction obligation. It does not finish
the full probability framework: general finite transition kernels, dimensional
observables, verified source conversion, a native receiver, sampling assumptions,
statistical inference and decision utility still need their own contracts.
The next minimal combined application is a two-state observation kernel with
a labelled finite loss function and a checked comparison of expected losses.
See [the applied-mathematics roadmap](../../docs/research/applied-mathematics-contract-roadmap.md).
