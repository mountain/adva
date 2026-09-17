# Typed finite kernel composition and the dependence boundary

Status: bounded external experiment, 2026-09-17, following merged PR #192
(`32330dbcf22847eec9f2a4e81104470bf58e2af8`). This advances priority 2 of the
[applied-mathematics roadmap](../../docs/research/applied-mathematics-contract-roadmap.md).
It introduces no native vocabulary or authority.

Authored by ChatGPT (OpenAI), submitted through Mingli Yuan's authorized account
proxy; not his review, endorsement or correctness guarantee. Original code,
exposition and synthetic evidence under Unknown v0.3. A second ChatGPT agent
reviewed the finite mathematical boundary and statically inspected both scripts;
this is not independent institutional review.

## Question and exact calculation

Let A, B and C be distinct ordered two-state spaces. The receiver selects a
prior row vector p, row-stochastic kernels K:A→B and L:B→C, and the second
prior q. All arithmetic uses canonical rational pairs. Typed endpoints,
direction, labels, question, history and complete intermediate prior are bound.

The explicit **Markov extension** means the stipulated factorization

    J(a,b,c) = p(a) K(a,b) L(b,c).

Conditional-independence phrasing applies only when the conditioning event has
positive mass. The factorization itself includes zero-mass paths without division.
Define q=pK, M=KL and r=qL. Each entry is nonnegative. Row sums of M equal
sum_b K(a,b) sum_c L(b,c)=1; summing J over c, a, or b gives respectively
p(a)K(a,b), q(b)L(b,c), or p(a)M(a,c). These elementary finite identities justify
the three supplied interface tables under the premise. This exposition is not a
proof-kernel artifact, and the implementation is not exhaustive over all matrices.

Primary exact input and output:

    p = (1/3, 2/3)
    K = [[3/4, 1/4], [1/2, 1/2]]
    L = [[2/3, 1/3], [1/4, 3/4]]
    q = (7/12, 5/12)
    M = [[9/16, 7/16], [11/24, 13/24]]
    r = (71/144, 73/144)

A fresh asymmetric instance uses p=(2/5,3/5), K=[[1/2,1/2],[1/3,2/3]],
L=[[3/4,1/4],[1/4,3/4]]. It obtains M=[[1/2,1/2],[5/12,7/12]] and
r=(9/20,11/20). Its space IDs contain Chinese text to check the agreed carrier
serialization convention. Both fixtures have numerically noncommuting matrices;
reversing the product also fails the typed direction contract.

## Three checked interfaces, with no enlarged ancestor

The new receiver directly imports the unchanged
[`probability_receipt/receive.py`](../probability_receipt/receive.py). The producer
imports only that experiment's independent producer. No checkpoint, ledger,
unit-conversion or native runtime receiver is silently substituted.

| Interface | Four-atom probability | Observation | Conditional information |
| --- | --- | --- | --- |
| AB | p(a)K(a,b) | B | A given positive-mass B |
| BC | q(b)L(b,c) | B | C given positive-mass B |
| AC | p(a)M(a,c) | C | A given positive-mass C |

Each reference measure is uniform on four atoms, and each full carrier is retained.
The parent six-atom maximum, denominator bound 1024 and four-entry history limit
remain unchanged. The supervisor sums eight scalar path terms per accepted case
as an external independent calculation; it never sends an eight-atom context to
the parent. There is no claim to a new native three-object joint type.

The [frozen contract](contract.json) specifies exact field names, directions,
carrier encoding and resources. A candidate has `profile`, `request`,
`interfaces` (AB, BC, AC), and `claims` (middle prior, product, final prior).
After validating the expected request, the receiver checks all three receipts
against their own arithmetic, then checks their correspondence to that request.
All non-probability AC fields and both AC marginals must agree. With
`markov-extension`, the complete AC law must equal p(a)(KL)(a,c) before acceptance.
Without a selected premise it returns `UnknownDependence`, with empty semantic
delta and no accepted endpoint or kernel. This conservative branch is not an
identifiability solver: some deterministic adjacent laws can determine an endpoint.

## A small counterexample to silently choosing the premise

Let A and B be independent fair bits. On their four equiprobable latent states,
take either C=A or C=1−A. In both models AB and BC are exactly uniform on their
four atoms. Their endpoint laws differ:

| Model | AC table in order 00,01,10,11 | Probability A=C |
| --- | --- | --- |
| C=A | (1/2,0,0,1/2) | 1 |
| C=1−A | (0,1/2,1/2,0) | 0 |
| Declared Markov extension | (1/4,1/4,1/4,1/4) | 1/2 |

The first two satisfy the complete adjacent laws but not their Markov extension.
All three local receipt calculations pass. For each of the two countermodels the
new receiver returns `UnknownDependence` when the premise is unspecified, and
`InvalidEvidence` when a Markov extension was requested. It does not relabel a
valid non-Markov model as a mathematical impossibility.

This also sharpens the earlier energy discussion. With the declared uniform
pair references, AB and BC density energies are both 1 in all three models.
The endpoint energy is 2 for each dependent model, and 1 for the Markov extension.
Thus local energy 1 does not imply endpoint energy 1. This is an exact finite
density calculation, not physical energy conservation or a universal normalization.
The four-state witnesses and projections are in [coupling-models.json](evidence/coupling-models.json).

## Zero-mass rows and history

With p=(1/2,1/2), both K rows=(1,0), and
L=[(1/4,3/4),(1/3,2/3)], q=(1,0). Both M rows equal (1/4,3/4).
Changing only L's unused second row to (2/3,1/3) leaves every interface receipt,
every reported statistic and M identical. Nevertheless it changes the explicit
receiver-selected kernel request, so the altered candidate is refused. There is
no statistical distinction here. The unused row is **given, not learned**; its
label appears in `unobserved_middle`. Inventing a conditional distribution for
that zero-probability observation is independently refused by the old parent.

AB retains the first step and BC/AC retain both steps. Identity-first composition
retains that history even though its numerical product equals L. History erasure,
changed middle labels and alternate middle laws cannot be hidden by successful
local arithmetic checks.

## Executed result and costs

The first campaign passed: **40 fresh receiver processes, 397 supervisor assertions**.

| Outcome | Cases |
| --- | ---: |
| AcceptedMarkovKernelComposition | 5 |
| InvalidEvidence | 24 |
| UnknownDependence | 2 |
| InvalidContext | 9 |

Eighteen refused evidence candidates pass all three local arithmetic checks.
Controls include changed laws/claims/history, missing atoms, wrong direction or
middle type/prior, negative/nonstochastic rows, Boolean-as-integer input,
unsupported assumptions, excessive history and joint denominators outside the
unchanged ancestor boundary. Context refusal is a profile limit, not a theorem
of impossibility. The five accepted instances cover primary, asymmetric reuse,
identity, null-middle and fair Markov cases.

Measured campaign wall time was **7.940595629 seconds**, with **10,095 cumulative
receiver work units** across the 40 processes (each separately capped at 10,000),
48 supervisor path terms and zero search candidates. Instrumented construction
took 0.048237019 s, receiving 7.568227050 s, serialization 0.138490543 s and
independent path observation 0.004231336 s; some bookkeeping is included only
in the total wall time. The eleven reuse receiving calls account for
2.080882797 s of the receiving total. Highest child RSS was 11,904 KiB
(11.625 MiB), supervisor RSS 14,592 KiB (14.25 MiB), not a summed system peak.
Archive construction additionally took 0.092119339 s. Final report/manifest
writing, reading, design, static review, network and CI costs were not separately
measured. No acceleration or expression-power increase is claimed.

Static review corrected a Unicode carrier encoding mismatch and an overly broad
Unknown reason before execution. There was **no failed experiment and no corrective
replay**. Do not equate this with proof that the implementation has no defects.

## Replay and evidence

From repository root, using a fresh output path:

```sh
python3 -B -S experiments/kernel_composition/run.py --output /tmp/adva-kernel-fresh
```

Linux Python standard library suffices. The supervisor stops at 30 seconds or
40 processes, with each child capped at 3 wall/CPU seconds, 128 MiB address space,
32 KiB per input and 10,000 cumulative work units including parent calls.
No automatic retry or scope increase is implemented. The dedicated CI job has
an additional 35-second command timeout and retains evidence on failure.

[execution.json](evidence/execution.json) records all outcomes, timings and code
hashes. [manifest.json](evidence/manifest.json) inventories all **208 exact files**
inside [attempt-1.tar.gz](evidence/attempt-1.tar.gz), including every expected
request, candidate, command, stdout, stderr and independent projection.
The archive is 27,843 bytes, SHA-256
`d0ca0defb48c25955bab824f6a48efcaa2b3ec99084f2bb04f9ba164fc56f5b2`.
Byte size is not peak memory. Original command paths require substitution after
extraction. One stored case can be independently re-received with:

```sh
mkdir /tmp/adva-kernel-evidence
tar -xzf experiments/kernel_composition/evidence/attempt-1.tar.gz -C /tmp/adva-kernel-evidence
python3 -B -S experiments/kernel_composition/receive.py \
  --expected /tmp/adva-kernel-evidence/attempt-1/primary/valid/expected.json \
  --candidate /tmp/adva-kernel-evidence/attempt-1/primary/valid/candidate.json
```

## Residual and next bounded task

The Markov premise is supplied; no inference from physical data, causal claim,
hidden-dependence detection or general joint-law identifiability is established.
Python, Fraction, operating-system limits and the frozen probability checker
remain trusted dependencies. This finite protocol is not a hostile-input service,
native import, `free`, M6 filler, universal grammar proof or learned theorem.
No real decision benefit for Mingli or Jiamin has been measured.

The practical contribution is to help people and agents compose two uncertain
stages while exposing the middle-law and dependence assumptions they are using.
The next mathematical witness is roadmap priority 3: a small rational Ax=b,
with a complete solution claim, residual and direction/basis boundary. Separate
unique solution, inconsistency and an affine family; a zero residual alone does
not certify uniqueness. Ledger-holder termination remains a separate open
engineering obligation, and arbitrary kernel dimensions/compositions remain open.
