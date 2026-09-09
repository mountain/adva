# Round 02: retained exclusions and joint finite observations

Status: external finite calibration and a second proposed communication request.
Mingli supplies the cross-workspace bridge. No automatic peer dispatch or merge.

## Receipt and next question

The actual published `response-01.json` at commit
`33518ad104f393f7c82b2a3203807fcbf6c47baf` answers request 01. Its byte-bound
acknowledgement is retained in `acknowledgement-01.json`; the live `status.json`
now records VariationObserved with source binding unverified and semantic
acceptance withheld. Calibration no longer overwrites live status.

There is no contradictory score to resolve: 0.2567 and 0.2092 belong to older
rules, while 0/25 belongs to the revised rule. The peer already recorded both.
Neither a zero intersection nor a matching acknowledgement proves that the
documents have no relation under every possible question.

**Request 02 asks which shared words the revised rule excluded and why.**
It fixes the same document pair, requests exact old/new rules and at most eight
authorized examples, and distinguishes mechanical exclusion from relevance.
Thirty seconds of source inspection is requested, not remotely enforced. Unknown
and partial disclosure are valid. No full documents or private paths are needed.
The request binds the exact prior response SHA-256 and its commit. These references
do not authenticate the sender or prove the original source records.

The peer may copy `response-template-02.json` to `response-02.json`. A separate
optional `word-witness-02.json` can disclose up to 25 head words per document,
normalization/tie rules, formulas and up to eight exclusion examples, within 16 KiB.
Its requested fields are in `request-02.json`. The current checker only validates
the ordinary three-string projection; it does not silently accept this attachment.
Do not manufacture missing word lists to satisfy the request.

```sh
python experiments/bounded_observation_exchange/check_exchange.py \
  experiments/bounded_observation_exchange/request-02.json response-02.json
```

Actual request-02 state: `Unknown/AwaitingReply` in `status-02.json`.
The original reply is rejected against the new request; the empty template yields
Unknown with all three fields incomplete. These checks were executed, but their
time and memory were not separately measured. Sending a link through Mingli is a
handoff, not evidence of delivery, acknowledgement, or semantic acceptance.

## Frozen arithmetic calibration

`round-02-contract.json` is written before execution. It specifies two integer
grids, interpreted as exact rational points, with fixed sum/difference observations.
They are external mathematical sets, not native Adva SourceIds or transformations.
This is a toy calibration for the agenda's observer-identifiability question;
it does not bypass the prerequisites for a native specialization or learning API.
The document experiment is not claimed to be an instance of this model yet.

For C = {(i/n,j/n): i,j >= 0, i+j <= n}, observer A bounds i+j and observer B
bounds i-j. All interval endpoints are inclusive. A shared record fixes the object,
coordinate frame, grid denominator, observation rules and assumptions. The exact
inverse i=(s+d)/2, j=(s-d)/2, including parity and domain guards, independently
checks the enumerated joint set.

| Instance | Initial | A alone | B alone | A and B | Repeat A |
| --- | ---: | ---: | ---: | ---: | ---: |
| n=16, truth=(6,4)/16 | 153 | 55 | 39 | 13 | 55 |
| n=12, truth=(5,2)/12 | 91 | 34 | 24 | 8 | 34 |

Both stipulated truths survive. Full finite point lists and inputs are retained in
`joint-evidence.json`. Each instance checks repeated A, repeated B after joining,
incomplete coverage, incompatible observations, and order-independent intersection.
An incomplete constraint returns UnknownCoverage without removing candidates.
An empty intersection returns Conflict, preserving inputs for investigation.
Repeated constraints produce EvidenceStutter, not another refinement.

The negative control matters: a **false** constraint i-j=0 also shrinks the set
and leaves it nonempty, but removes the stipulated true point in both instances.
Therefore shrinkage is not evidence of soundness. For sound constraints, truth
preservation follows directly from membership in both sets; the finite controls
calibrate the implementation rather than prove source soundness.

## Meaning of the result

The result supports a conditional mechanism: complementary, sound observations
can shrink a shared candidate set after repeated local observation has no effect.
Adding participants alone need not supply complementary information. Literal
intersection is order-independent, but the sequence of observations and its cost
history still differ and remain distinct. No native identity follows from equality.

This is not an implementation or convergence proof for Nelder-Mead. Being in one
observer's epsilon bin differs from small diameter in a jointly specified metric.
The retained non-singleton joint sets are concrete residuals. Repeated intersections
with the same two observations cannot refine them further. A further step needs
another justified observation, precision change, or problem change and a new finite
budget. No automatic continuation is installed.

No new vocabulary is registered. `receive`, `acknowledge`, `EvidenceStutter` and
scoped Unknown are reused. The descriptive phrase "joint refinement" names this
experiment only. No arithmetic normalization, native free/Seal, universal grammar
completeness, Calabi-Yau identification or real-world trust has been established.

## Reproduction and actual cost

```sh
python experiments/bounded_observation_exchange/joint_observation.py
python experiments/bounded_observation_exchange/check_exchange.py \
  experiments/bounded_observation_exchange/request.json \
  experiments/bounded_observation_exchange/response-01.json
```

The run enforces a 5-second wall alarm, 2-second CPU limit, 128-MiB address-space
limit, 10000 predicate visits and a 128-KiB main report limit. There were 976
predicate visits across both instances and their controls. Construction plus
verification took 0.417847 ms; serialization replay 0.134583 ms; evidence writing
0.177128 ms. Total measured run through evidence saving was 1.495010 ms, with
peak process RSS 9984 KiB (9.75 MiB) on Linux. The final cost-file write, research,
coding, network and publication are excluded. Source and contract hashes are
stored. One invocation, no correction replay and no remote CI claim.

The count comparison measures remaining ambiguity, not execution acceleration:
the joint route does additional work and communicates additional information.
Reusable tool-formation cost and real peer source-inspection cost are unmeasured.

This helps Mingli and subsequent operators ask which distinctions were discarded
and prevents an attractive smaller candidate set from being mistaken for a true
answer. Benefit for Jiamin's actual task remains unmeasured. The next minimal step
is the authorized word-exclusion reply; only then should we choose a finite checker
for the disclosed data and a question under which exclusions matter.
