# Matrix-free Iota dual expansion: typed trees, failed process opposition, and actual apertures

Date: 2026-10-08. Status: external finite calibration, not a registered claim,
not a native identity, admission, Seal, or general theorem.

Authored by ChatGPT (OpenAI), contributed under Unknown v0.3 and submitted
through Mingli Yuan's authorized account proxy. Mingli supplied the signed
expansion question; ChatGPT supplied the external definitions, implementation,
checks and this report. Account use is not his authorship, technical review or
endorsement. The two reducer implementations are distinct code, not independent
participants or a proof of unrestricted correctness.

## Sources and boundary

The baseline is `mountain/adva@6d7ab990021f201d189c92be5d3729b3a9d4bf42`.
`mountain/aeg-paper@968c5c29557e8f7d70fe8baea2733726b852507d`,
`paper-0/sections/02-expansion.tex`, fixes chronological first-slot L and
second-slot R combs and opposition of operations. These are arithmetic trees,
not Iota applications. The exact file digest is in the contract; no external
source file is copied here.

The existing `mountain/adva` files
`docs/research/0224-four-left-nested-iota-frames.md`,
`experiments/four_iota_frames/checker.py`, and
`knowledge/received/iota-process-knowledge-2026-09-17-v1/materials/iota.md`
supply the retained comparison and Iota rules. Executed input pins are checked
before importing the reference reducer. Frozen files, claims and conclusions
are unchanged.

The experiment has its own [contract](../../experiments/iota_dual_expansion/contract.json),
[checker](../../experiments/iota_dual_expansion/checker.py),
[evidence](../../experiments/iota_dual_expansion/evidence.json), and
[test](../../tests/python/test_iota_dual_expansion.py).
Each CLI invocation enforces 20 wall seconds, 15 CPU seconds, 256 MiB address
space and 1 MiB output on Linux; non-Linux CLI execution refuses as Unknown.
The structural caps are 64 contractions per term and 4096 nodes per state.
There is no search or continuation. Missing pins stop execution; a digest mismatch fails; exhaustion is Unknown.
No matrix or numerical amplitude operation is used. The old checker calls its
strategy leftmost-innermost, but it checks a saturated root before its right
argument: (Iota (Iota a)) therefore contracts its outer Iota first. This new
contract records that actual priority rather than asserting full innermost
evaluation. Historical labels and evidence are unchanged.

## Three separate types and two counts

`Leaf` and `App` are external Iota syntax; `Comb` is a separate, tagged AEG
comb skeleton with chronological operation placeholders and constants. Cross
insertion raises TypeError. A skeleton comparison forgets operation semantics
and is not a functor between arithmetic evaluation and Iota reduction.
`history` is a third object: source, local rule/path/redex/replacement events,
normal form and every state of the declared retained spine schedule (left subtree, saturated root, then right
subtree).
The `i` prefix leaf means Iota; it never means the imaginary unit.

Write C^L_1=C^R_1=Iota and
C^L_(k+1)=App(C^L_k,Iota), C^R_(k+1)=App(Iota,C^R_k).
These pure trees have k leaves and k-1 applications. In contrast, open combs
O^L_0(a)=O^R_0(a)=a and
O^L_(k+1)(a)=App(O^L_k(a),Iota),
O^R_(k+1)(a)=App(Iota,O^R_k(a)) have k Iota leaves, one actual aperture
and k applications. They correspond to k-node comb skeletons.
A single Iota leaf is not a one-operation one-hole AEG expression.

The candidate positive signed spelling labels C^R_k or O^R_k; the negative
spelling labels C^L_k or O^L_k. A seed/type tag is required to distinguish them.
This is a notation proposal, not an exponential identity. No zero exponent,
addition law, inverse law or differential rule follows from this experiment.

| k Iota leaves | C^L_k | C^R_k | L/R normal forms | L/R events |
| ---: | --- | --- | --- | --- |
| 1 | Iota | Iota | Iota / Iota | 0 / 0 |
| 2 | (Iota Iota) | (Iota Iota) | ((S K) (K K)) / same | 3 / 3 |
| 3 | ((Iota Iota) Iota) | (Iota (Iota Iota)) | Iota / (S K) | 5 / 6 |

The two-leaf normal form is the intensional SK expression produced by these
rules; its identity behavior does not identify it with the primitive Iota.

| k | O^L_k(a) | O^R_k(a) | L/R events |
| ---: | --- | --- | ---: |
| 1 | (a Iota) | (Iota a) | 0 / 1 |
| 2 | ((a Iota) Iota) | (Iota (Iota a)) | 0 / 2 |
| 3 | (((a Iota) Iota) Iota) | (Iota (Iota (Iota a))) | 0 / 3 |

All left open sources are already normal. The right normals are a followed
by one, two or three successive S,K argument pairs. Full tagged trees,
chronological skeletons and local histories for all six rows are retained.

## What opposition preserves and what it fails to preserve

Recursive mirror M(App(u,v))=App(M(v),M(u)) is involutive and maps each declared
left source to its right partner. At the skeleton level it exchanges operand
slots and keeps chronological vertex marks and the abstract internal chain.
That is the structural correspondence.

It does not conjugate the ordinary Iota rewrite relation. The smallest open
counterexample has one application and one Iota: (Iota a) rewrites to ((a S) K),
whereas its mirror (a Iota) has no rewrite. A zero-application tree has no such
step, so this is minimal by application count in the declared syntax.
Even the self-mirror source (Iota Iota) has a first replacement whose mirror
is not its first replacement. Source symmetry is insufficient for local
history symmetry. The three-leaf pure pair is the first pure left/right pair
with different trees; its normal forms and event counts already disagree.

AEG opposition changes an operation to its opposite. Conjugating the entire
Iota rewrite system by M would likewise define a different, opposite evaluator.
We do not install that evaluator or claim ordinary application is its own
opposite. Keeping ordinary Iota rules while mirroring the source does not
preserve local histories. No alternative, non-mirror general correspondence
is ruled out by this finite experiment.

The smallest retained pure equal-endpoint control is Iota versus
((Iota Iota) Iota): 0 versus 5 events. With an aperture, a versus
((Iota Iota) a) both normalize to a, with 0 versus 5 events and 1 versus 6
sequential states. Among pure sources through two leaves there is no distinct
source with endpoint Iota; the declared aperture control ((Iota Iota) a) adds five contractions to the
zero-event source a. Minimality claims here are only for these declared comb
families, except the one-step mirror counterexample's node-count argument.
Sequential states are cuts of this total recorded schedule, not an enumeration
of all causal cuts, not native CausalCuts, and not full annotated ancestry.

## An actual aperture and three actual role ports

(Iota a) is the smallest source with an Iota event and an actual received
aperture leaf. A naked a is smaller but has no event. One port allows one
selected role policy; it does not silently provide three distinct ports.

For three separately assigned ports and at least one Iota event, use
((a (Iota b)) c), prefix `@@a@ibc`. It reduces once to
((a ((b S) K)) c), prefix `@@a@@bskc`.
Bind a,b,c to ports 0,1,2 and explicitly choose entry and exit policies
[0,1,2], read as construction {}, space [] and time (). Each aperture survives
once. The source has four leaves and three applications, meeting the binary
tree minimum for three distinct aperture leaves plus one Iota leaf.
These are explicit external source-policy bindings in the received vocabulary;
no stable Rust hole, native process admission, matrix frame admissibility or
full ancestry certificate is claimed. This addresses the missing-leaf obstacle
for this new source, without changing Research 0224's pure-tower obstruction.

## Verification and residual

All 19 declared source executions agree event by event and endpoint by endpoint
with the separately implemented retained reducer. This includes repeated
sources; it is 19 comparisons, not 19 distinct terms. Negative controls reject
cross-type operands, a mirrored rewrite, endpoint-only history identity,
modified source pins, and output overwrite. The evidence pins its checker,
contract and local rule dependencies. Fresh replay compares the entire payload. The targeted suite, including
Research 0224 and research-index consistency, passed 29 tests on Python 3.12.
The full repository suite was not run.

Reproduce on Linux with Python 3.11+ and a nonexistent output path:

    python3 -S experiments/iota_dual_expansion/checker.py --output /tmp/iota-dual-fresh.json
    python3 -m pytest -q tests/python/test_iota_dual_expansion.py tests/python/test_four_iota_frames.py

The finite result supports signed notation as a typed structural direction
marker and rejects the tested stronger ordinary-Iota process opposition.
Construction tree, endpoint and process history remain separate coordinates,
which is compatible with the three-computation question but does not prove a
three-computation equivalence. The next concrete prerequisite is an explicit
opposite application interpreter and a map on its local events and retained
boundaries; only then can a history correspondence be checked. Neither the
imaginary unit nor <> is defined here. In particular mirror squared is the
identity, so it cannot simply be declared an action whose square is minus one.
No existing exponential or derivative conclusion is modified or extended.
