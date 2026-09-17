# Reversible microscopic gates and a history-conditioned Markov boundary

Status: bounded external research, 2026-09-17. Requested by Mingli after the
Newton/Boltzmann time-reversal discussion. Baseline main is
`e4868eff9f46437a5e637ab7d4b713f351d2226b`. PR #197 at
`7c827a6d24640be139daa17a43c3083173305b0b` was an unmerged documentary
reference when the experiment was frozen. It merged during packaging as
`c91f6ec86a9b10d4443813039e853946614d52b8`; that main update is preserved
in this branch. The frozen contract, source and experimental evidence are
unchanged. This experiment imports no implementation from the earlier
supplied-kernel horizon check and preserves its original claims.

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy;
not his authorship, review, endorsement or correctness guarantee. This is an
original first-party contribution under Unknown v0.3. Another ChatGPT agent
implemented the separate receiver, and a third reviewed the mathematics,
protocol, code and retained results. That is not institutional or human review,
and does not replace a formal proof kernel. No external paper text, code,
figures, datasets or page images are incorporated. The authorship correction
from the discussion is **Xiao Ma / 马骁**, not 肖马; no review by him is implied.

## Frozen question and finite resources

Can the same symmetric flip kernel be used conditional on every positive
observed history, through a requested horizon of at most six steps, when the
underlying system-plus-environment dynamics is reversible?

The caller supplies one system bit, one through six named environment bits,
a complete rational joint initial law, a schedule of environment indices,
a flip probability q, ordered display labels, a question and history. Dense
probability entries include zeros. Their order, schedule and entire law are
bound to the receiving question, not inferred from observed trajectories.
The [contract](contract.json) was written before any campaign execution.

This is a finite probability space over Q, not a finite field. Encoding bounds
do not assert a universal physical resolution. The law is assumed exactly as
supplied; statistical inference of that law remains a separate problem.

## Microscopic invertibility and the observed path

For environment e=(e_0,...,e_(m-1)), let

    U_j(s,e) = (s XOR e_j,e).

Each gate is an involutive permutation of all 2^(m+1) microstates. Applying
the gates in the reversed schedule recovers every microstate, including those
with zero initial probability. The campaign checks this enumeratively, and
it also follows immediately from U_j squared being identity. These particular
gates commute; schedule retention here is not evidence of noncommutativity.

The environment is retained throughout. In a fresh-bit example, future bits
are part of a finite initial resource, independent of the system and the used
bits. No environment reset, deletion, or automatic resource renewal occurs.
Permuting the full joint law preserves its multiset of masses and hence its
Shannon entropy; no numerical logarithm calculation is needed for that fact.
The example has no physical Hamiltonian, temperature, work or heat assignment.
Its probability normalization must not be called energy normalization.

The observer sees S_0,...,S_t. The proposed row-stochastic kernel is

    K_q = [[1-q,q],[q,1-q]].

The receiver makes three separate checks at every step:

| Check | Exact object compared | What it does not establish alone |
| --- | --- | --- |
| Marginal recurrence | law(S_t) versus law(S_(t-1)) K_q | The joint law of paths |
| Adjacent-pair recurrence | law(S_(t-1),S_t) versus law(S_(t-1)) times K_q entrywise | Conditional independence from earlier observations |
| Full-history condition | Each positive predecessor history and its flip-extension mass | A different initial law, future horizon or physical preparation |

A failure of the specified K_q condition refutes that homogeneous-kernel
question. It need not rule out a different, time-dependent, or larger-state
Markov description. The stationary repeated-bit example below does also
exhibit genuine dependence on an earlier observed state.

## Exact finite criterion and proof

Write h=(s_0,...,s_(t-1)), M(h)=Pr(h), and F(h)=Pr(h and S_t differs from
S_(t-1)). The receiver requires

    F(h) = q M(h)   for every h with M(h)>0.

There is no division by a zero probability. Null histories are counted and
carry no asserted conditional distribution. Nonnegativity implies that both
extensions of a null history have zero mass.

This criterion at all steps is necessary and sufficient for the finite path
factorization

    Pr(s_0,...,s_H) = Pr(s_0) product_(t=1..H) K_q(s_(t-1),s_t).

For sufficiency, induct on prefix length: the flip extension has mass q M(h),
and the stay extension has the remaining mass (1-q) M(h). The null case
follows from nonnegativity. Necessity follows by summing the factorized law
over later states. This elementary finite argument is distinct from the
executed examples; no samples are substituted for checking all positive
histories of the supplied finite law.

## Three routes and their witnesses

### Independent environment and reuse

With S_0=0, six independent bits of flip probability 1/4 give the first-state
probabilities

    1, 3/4, 5/8, 9/16, 17/32, 33/64, 65/128.

All six full-history steps pass. A new instance uses flip probability 1/3
and Pr(S_0=1)=1/3 with six independently prepared bits; it also passes.
This reuse changes both the environment law and initial system distribution.

Deterministic q=0 and q=1 controls are included. In particular q=1 can be
periodic while satisfying its kernel contract. The zero-horizon case is
vacuous and establishes no transition. Null histories stay undefined.

### Reusing one environment bit

Start with S_0=0 and one bit of probability 1/4, reused six times. The first
step matches K_(1/4), but the second returns S_2=S_0 exactly; the same-kernel
condition first fails at step two.

The stronger control starts S_0 and a single environment bit independently
and uniformly. Then S_2=S_0, S_3=S_1, and so on. All six single-time laws
are uniform and all six adjacent-pair laws have four equal masses. Both
weaker checks agree with K_(1/2) throughout. Nevertheless the observed
history (S_0,S_1)=(0,0) forces the next flip to be zero: its mass is 1/4,
its flip-extension mass is zero, but the proposed kernel requires 1/8.
Full-history checking first refuses the kernel at step two.

For this example the time-two conditional given S_1 alone is fair, while
the conditional given (S_0,S_1) is deterministic. The exact initial joint
law, rather than a finite sampling accident, supplies the distinction.

A separate schedule control repeats the first index of an otherwise independent
six-bit environment. Fresh storage alone does not justify using a bit twice
as independent noise; the first mismatch is again step two.

### A discrepancy delayed until step six

Take six fair bits conditioned on even total parity and S_0=0. Every set of
five environment coordinates has the independent uniform law: omitting any
one coordinate leaves exactly one completion for each five-bit assignment.
The campaign explicitly checks all six five-coordinate marginals, 32 values
each. The first five complete observed trace rows agree with the independent
fair-bit example. At step six, total parity forces S_6=0 rather than a fair
state, so the same kernel is refused.

This is higher-order dependence hidden from lower-order observations. It is
NOT a model of a vanishing-measure collision set: the parity restriction
excludes half the six-bit configurations. No Boltzmann-Grad or thermodynamic
limit is computed in this experiment.

## Receiving, missing coverage and retained negative evidence

The producer constructs tuple-valued paths and grouped masses. The receiver
independently applies dense-state bit permutations and packs history prefixes
into integers. It checks every gate's bijection, full-state roundtrips and
all positive history conditions, then compares each canonical trace row.
Neither imports the other. Python, Fraction and the operating system remain
shared trusted dependencies.

Only fully checked rows enter verified_prefix. A complete trace returns
VerifiedMarkovHorizon or Counterexample; the latter is valid negative evidence
about this exact question, not a receiver malfunction. An incomplete trace
returns UnknownCoverage for the whole requested horizon, with missing steps.
An already verified mismatch remains explicitly available as
verified_counterexample even when the remaining trace is missing or a later
claim is invalid. A whole-horizon Unknown does not erase a local refutation.

InvalidContext returns no validated expected_request. The raw supplied request
is retained separately in the evidence bundle. InvalidEvidence retains only
completed rows and their verified counterexample. Boolean/integer substitutions,
rebound laws or schedules, missing dense entries, malformed fractions, changed
labels, extra authority fields and false claims are refused. No outcome grants
native authority, Close, free, a library home, or automatic continuation fuel.

## Executed evidence and actual costs

One campaign completes 36 fresh receiving processes and 1,078 assertions:

- 6 VerifiedMarkovHorizon;
- 4 Counterexample;
- 3 UnknownCoverage, including one retaining a verified step-two counterexample;
- 13 InvalidEvidence;
- 10 InvalidContext.

Independent controls check roundtrips for 660 microstates across ten supplied
contexts, including zero-mass states; these are context-specific checks, not
660 distinct bit strings. The q=1/4 matrix has inverse
[[3/2,-1/2],[-1/2,3/2]], checked by exact multiplication. The inverse is not a
stochastic kernel. Detailed balance at the uniform law also holds, so Markov
reversibility, algebraic invertibility and physical time reversal must stay
separate.

The campaign uses 45,747 receiver, 18,940 producer and 8,272 control work units
(total 72,959); search candidates are zero. Measured wall time is
6.245913490 seconds. Subtimes are: initial fixture-law construction
0.008786925 s, candidate construction 0.073306967 s, receiving processes
5.869143015 s, serialization 0.093529243 s and independent controls
0.005503938 s. These are not an exhaustive wall-time partition; remaining
orchestration and refusal-fixture assembly are included in total time.
New-instance candidate construction and receiving take 0.007879711 s and
0.131653235 s respectively; these are subsets of the above totals.

Highest child RSS is 10,112 KiB (9.875 MiB); supervisor RSS is 13,312 KiB
(13 MiB). These are measured per-process high-water marks, not simultaneous
aggregate memory and not file sizes. Child and supervisor address spaces have
128 MiB limits. Each child has a three-second ceiling, with an earlier soft
exit; the campaign has 30 seconds, 36 calls and 100,000 counted units. Counts
measure specified visits/checks, not machine instructions or bit complexity.
Explicit arithmetic has 512-bit guards; Fraction internal temporaries are not
separately bit-metered. Construction is finite and bounded by the fixed cases.

Static preflight caught and corrected a producer parenthesis, a partial-claim
schema mismatch and an invalid-context retention assertion before any campaign.
The first mathematical campaign passed; no failed campaign or corrective replay
occurred. Reading, coding, static review, network and final packaging time are
outside the campaign measurement. No speedup or learning claim follows.

Reproduce from repository root into a new directory:

```sh
python3 -B -S experiments/reversible_memory/run.py --output /tmp/adva-reversible-memory-new
```

[evidence/execution.json](evidence/execution.json) gives process-level results
and source digests. [evidence/manifest.json](evidence/manifest.json) inventories
all original requests, candidates, raw outputs, commands, controls and the
frozen contract inside [evidence/attempt-1.tar.gz](evidence/attempt-1.tar.gz).
The source scripts recompute evidence; reading a stored success flag does not.

## Relation to Newtonian and kinetic research

Deng, Hani and Xiao Ma (马骁), *Long time derivation of the Boltzmann equation
from hard sphere dynamics*, arXiv:2408.07818v3,
https://arxiv.org/abs/2408.07818v3, establish a conditional long-time kinetic
limit for rarefied hard spheres. Their follow-up arXiv:2503.01800,
https://arxiv.org/abs/2503.01800, connects kinetic and hydrodynamic limits.
These results are documentary context, not imported algorithms or premises
needed by this finite checker.

Bodineau, Gallagher, Saint-Raymond and Simonella, *One-sided convergence in the
Boltzmann-Grad limit*, https://arxiv.org/abs/1612.03722, explain the directional
collision-correlation boundary in that singular limit. Our comparison is an
inference about methodological discipline: low-order agreement alone does not
license deleting structure needed by another question. The finite bit model
does not reproduce their collision geometry, asymptotic estimates or proof.
No conclusion about the universe's low-entropy initial condition is obtained.

Aldous and Fill's distinction of reversible Markov chains is documented at
https://www.stat.berkeley.edu/~aldous/RWG/Book_Ralph/Ch3.S1.html . The concrete
inverse and detailed-balance identities above are independently recomputed.

## Continuation

No new word is needed: conditional probability, history, kernel, coverage and
counterexample already express this result. We have strengthened the condition
under which a supplied kernel may describe an observed finite path, not learned
a physical mechanism. The next small question is an approximate version:
can bounded errors in the history-conditional extension masses yield a checked
finite path-law error bound, with rare histories and reverse-direction use
kept explicit? It requires a new contract and budget. General gas kinetics,
entropy production, native interpretation and practical value for Jiamin's
actual task remain unverified. The roadmap's separate confidence-coverage and
ledger-holder-exit obligations remain open.

## Proposed continuation: simultaneity, causal order and imaginary time

Mingli subsequently asked to consider Zhao Zheng's discussion of simultaneity
and whether imaginary time can connect this work to relativity. Indexed BNU
publications use the name Zhao Zheng / 赵峥. The indexed installment of
*Relativity, the Universe and Spacetime: The Nature of Time* has a section on
conditions for transitive simultaneity:
https://dxwl.bnu.edu.cn/CN/article/downloadArticleFile.do?attachType=PDF&id=5389 .
The full PDF could not be retrieved in this run. This identifies a source to
read, not a verified attribution of Mingli's imaginary-time proposal to Zhao.
The following is our original proposed organization, not his quoted argument.

Three operations require separate input and output contracts:

| Operation | Structure that must be fixed | Distinction to preserve |
| --- | --- | --- |
| Change inertial observer | Events, units, Lorentzian metric, time orientation, clock synchronization and observation policy | Spacelike simultaneity/order may change; future causal order is preserved by an orthochronous Lorentz map |
| Reverse microscopic dynamics | Full joint state, inverse gate sequence, retained environment and history | A reversed realization is not automatically represented by the same conditional observed kernel |
| Continue to imaginary time | Specified operator, analytic domain, real slice, boundary conditions and normalization | Analytic continuation is neither an observer boost nor automatic physical time reversal |

The existing bit gates have no positions, light cones or physical clock
calibration. Assigning their integer step labels to a spacetime diagram would
not prove locality, Lorentz covariance or compatibility of two observers.
Changing a simultaneity slice can change the selected event set and available
records. A merely relabeled record must not silently become a different
conditioning history. Even two same-time variables of this finite model are
not asserted to occupy causally separated physical sites.

A small future arithmetic question can precede any analytic continuation.
In 1+1 Minkowski coordinates ordered (t,x), use c=1 and v=3/5. The matrix

    L = [[5/4, -3/4], [-3/4, 5/4]]

has L^T diag(-1,1) L = diag(-1,1), determinant one, and inverse obtained by
changing the two off-diagonal signs. A simultaneous event difference (0,1)
maps to (-3/4,5/4); its squared interval remains one. A future timelike
difference (1,0) maps to (5/4,-3/4) and stays future timelike. These are
elementary exact identities, not a new receiver campaign. A next receiving
profile should bind both event identities and observers, check the complete
chosen finite event set and causal relations, and retain excluded observations
as a coverage gap. Reusing coordinates without moving the predicates should
be a negative control. No spacetime dynamics or continuum theorem follows.

Imaginary time supplies a separate connection to equilibrium statistical
mechanics. For a specified finite-dimensional self-adjoint Hamiltonian H,

    U(t) = exp(-i t H / hbar)
    t = -i tau_E  =>  exp(-tau_E H / hbar)
    tau_E = hbar beta, beta = 1/(k_B T), T > 0
    rho_beta = exp(-beta H) / Tr(exp(-beta H)).

In this finite setting the matrix exponential is entire; the last expression
is a definition of a Gibbs state, not a derivation of thermalization. At finite
tau_E the exponential still has an algebraic inverse. Nonunitarity does not
mean algebraic noninvertibility; nor does this operator automatically give a
stochastic Markov kernel or a trace-preserving quantum channel. Normalizing a
filtered state and taking infinite-time limits are additional operations.
Imaginary time also occurs in nonrelativistic quantum theory, so it does not
by itself establish relativity. No H or physical energy assignment is supplied
by our XOR gate experiment.

For fields and general spacetime the continuation/reconstruction conditions
require their own proof. Wick's original abstract explicitly conditions
analytic continuation on boundary information:
https://journals.aps.org/pr/abstract/10.1103/PhysRev.96.1124 .
Visser's discussion argues against an unrestricted time-coordinate substitution
on curved spacetime: https://arxiv.org/abs/1702.05572 . These are documentary
references, not incorporated derivations or source bytes.

This continuation is Proposed and unexecuted. It neither changes the frozen
six-step evidence nor adds a vocabulary word. Its practical question is how
two observers can compare the same causally available evidence before using
that evidence to license an effective evolution law.
