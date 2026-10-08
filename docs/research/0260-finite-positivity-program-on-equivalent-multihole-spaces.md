# Research 0260: A finite positivity program on equivalent multihole spaces

Date: 2026-10-08. Status: bounded external exact calibration. The frozen
five-launch campaign passed; 384 query results were independently checked.
No native equivalence or positivity operation is installed.

Research direction: **Mingli Yuan**. Formalization, mathematical review,
and this note: **Codex (OpenAI)**, submitted through Mingli Yuan's GitHub
account (`mountain`) as an authorized proxy. Account use is not his
authorship, review, endorsement, or a correctness guarantee. The original
contribution is offered under Unknown v0.3.

## 1. The precise question

Can a program decide positivity requirements on two equivalent arithmetic
coordinate spaces, while retaining the assumptions behind each answer?
The answer here concerns a fixed finite Boolean algebra and explicit
policies. A nonempty region is not inherently positive. A program decides
what is forced by the selected positivity theory and its finite carrier.

This continues [Research 0258](0258-henkin-completion-galois-closure-and-observer-separation.md)
and [Research 0259](0259-henkin-witness-completion-and-process-neighborhood-duality.md).
The experiment contract is `experiments/multihole_positivity/contract.json`.
It was frozen before execution. The example uses four real arithmetic
holes; these are not Adva's three native computation domains.

## 2. Two coordinate spaces and their programs

Let the source holes be `(a,b,x,y)`, with `a>0` and `y>0`, and put
`z=x+iy`. Let the target holes be `(a,b,p,q)`, with `a>0` and `q>0`.
Define

\[
\Phi(a,b,x,y)=(a,b,ax+b,ay),\qquad
\Phi^{-1}(a,b,p,q)=(a,b,(p-b)/a,q/a).
\]

These maps are mutually inverse on the declared domains. Write
`u=p+iq=az+b` and `d=p^2+q^2`. Since `q>0`, `d>0`.
The source program computes `p,q,d` and returns
`retain(a,b,-p/d,q/d)`; the target program computes `d` and returns the
same retained tuple. Thus their output charts obey the exact rational law

\[
E(a,b,z)=-\frac1{az+b}=K(a,b,az+b),\qquad K(a,b,u)=-\frac1u.
\]

Both programs retain `a,b`. The proof holds globally on the declared
real domains; the runnable calibration evaluates only rational fillings.
It proves a coordinate correspondence and observer incidence, not an
expression-word rewrite or an execution-history comparison cell. Treating
`u` as an independent new input without the coordinate relation would
change the problem. No native source or occurrence identity is invented.

The four frozen source fillings are as follows. All four holes vary.

| Source index | `(a,b,x,y)` | `u` | `w=r+is=-1/u` |
| --- | --- | --- | --- |
| 0 | `(1,0,1,1)` | `1+i` | `-1/2+i/2` |
| 1 | `(2,1,1/2,1/2)` | `2+i` | `-2/5+i/5` |
| 2 | `(3,-1,2/3,2/3)` | `1+2i` | `-1/5+2i/5` |
| 3 | `(4,-3,5/4,3/4)` | `2+3i` | `-2/13+3i/13` |

The target lists their images in reverse order `[3,2,1,0]`. Transport
must therefore relabel indices; comparing unchanged bit masks would be
incorrect. These indices are external finite labels, never native IDs.

## 3. Geometric requirements become exact regions

Use the two output observations

\[
B:\ r^2+(s-\tfrac12)^2<\tfrac14,\qquad H:\ s>\tfrac14.
\]

Substituting `r=-p/d`, `s=q/d` and using `d>0` gives

\[
B\iff q>1\iff ay>1,\qquad
H\iff p^2+(q-2)^2<4\iff(ax+b)^2+(ay-2)^2<4.
\]

Hence `B={2,3}` has source mask `12`, `H={0,2}` has mask `5`,
and their common witness is source index `2`, singleton mask `4`.
In reversed target order these masks are `3`, `10`, and `2`; the marked
point has target index `1`. The third region `B symmetric_difference H`
is `{0,3}`, mask `9`, and retains mask `9` after reversal.

The membership patterns of `B,H` distinguish all four points. Their
Boolean algebra is therefore all sixteen subsets. This supplies finite
observation separation, not reconstruction of arbitrary programs.

This is the executable incidence slice of the process-neighborhood pairing:
for a filling `t` and an output region `R`,
`rho(E(t),R) iff rho(t,E_inverse_image(R))`, where `rho` is membership.
The equations above compute that inverse image. Transporting all requested
regions together preserves their common filling fibre. Adding a Henkin-style
witness is justified only when that fibre is inhabited; a new witness name
does not make an empty fibre nonempty. This finite membership calculation
does not supply the proof-object equivalences proposed in Research 0259.

## 4. Three declared positivity policies

A positivity assignment is a Boolean function `P` on those sixteen
regions. The basic policy imposes the static conditions

\[
\text{A1: }P(S^c)\leftrightarrow\neg P(S),\qquad
\text{A2: }P(S)\land S\subseteq T\Longrightarrow P(T).
\]

Here A2 uses ordinary finite inclusion. It is not the modal necessary
entailment axiom from the Scott argument. The joint policy additionally
requires an actual carrier point in every positive region. The marked
policy fixes that realizing point to source index `2`.

**Finite realizer lemma.** Under A1, if a point `c` belongs to every
positive region, then `P(S)` holds exactly when `c in S`.
Indeed, positivity implies membership by assumption. If `c in S` but
`P(S)` fails, A1 makes `S^c` positive, contradicting the assumption.
Thus the joint policies are principal point evaluations; fixing the point
leaves one assignment. This is an extra realization requirement, not a
free choice that Henkin witness addition can justify without consistency.

There are twelve basic assignments: four have a positive singleton and
are principal. In the other eight, all singletons are negative, all
triples are positive, and one member of each of the three complementary
pairs of two-point regions is independently positive. Thus there are
four joint assignments and one marked assignment before extra requests.

Requiring both `B,H` positive leaves three basic assignments but only one
joint assignment. The singleton `{2}` is underdetermined in the basic
case and forced positive in the joint case. Requiring the third region
`{0,3}` positive leaves one basic assignment but no joint assignment:
all three regions are individually inhabited, yet their common
intersection is empty. This distinguishes consistency of A1+A2 from
the existence of the demanded common realizer.

| Requests | Basic models | Joint models | Marked models |
| --- | ---: | ---: | ---: |
| None | 12 | 4 | 1 |
| `B,H` positive | 3 | 1 | 1 |
| `B,H,B symmetric_difference H` positive | 1 | 0 | 0 |
| `H` positive and negative | 0 | 0 | 0 |

These counts follow from the finite argument above and agree with the
executed program census and independent verification.

## 5. Positivity itself becomes a Boolean polynomial geometry

Give each of the sixteen regions `R` a real variable `p_R` and impose

\[
p_R(p_R-1)=0,\qquad p_R+p_{R^c}=1,\qquad
p_R(1-p_S)=0\quad(R\subseteq S).
\]

These encode Boolean values, A1, and A2. Positive and negative premises
add `p_R=1` and `p_R=0`. Let `M` be the resulting real solution space.
For query `Q`, forced positivity means `M` is nonempty and its slice
`p_Q=0` is empty; forced negativity means `M` is nonempty and its slice
`p_Q=1` is empty. Both slices nonempty means underdetermination; `M`
empty means inconsistency. Thus the finite positivity problem is genuinely
an arithmetic constraint problem, with its assumptions inside the equations.

The joint policy adds four Boolean selector variables `s_i`, with

\[
s_i(s_i-1)=0,\qquad \sum_{i=0}^3s_i=1,\qquad
s_i p_R=0\quad(i\notin R).
\]

The selected point must lie in every positive region. The marked policy
adds `s_2=1`; after target relabeling it adds `s_1=1` instead. The checker
enumerates the finite assignments directly; it is not a general polynomial
solver. The original four-point carrier consists of filling configurations,
while `M` consists of positivity assignments, optionally with a selector.
Neither is the whole space of programs or execution histories. Classifying
a region does not decide the positivity or universality of the program
performing that classification. A future finite stock of programs would
need its own checked encoding and observer-incidence matrix.

## 6. Decision outputs and coordinate transport

The interface is `decide(query_mask, positive_masks, negative_masks,
policy, fuel)`. Across the admitted models it returns `ForcedPositive`,
`ForcedNegative`, or `Underdetermined`, with model witnesses. An empty
model family returns `Inconsistent` before any entailment classification.
Fuel exhaustion returns `Unknown`; malformed input returns `InvalidInput`.
The last two outcomes cannot be interpreted as nonexistence. A joint
realization witness is returned separately from a positivity assignment.

Transport along the explicit bijection preserves complement, inclusion,
and common intersection. Define target positivity by inverse image.
Consequently the complete basic model family, requests, all sixteen
query classifications, and declared realizer policies transport. The
marked point must move from source index `2` to target index `1`.

This does not compute intrinsic goodness, interpret modal A3, A4, or A5,
or establish a general higher-order property domain. It does not encode
universality or assign a positive value to a universal mapping property.

## 7. Required countercontrols and execution status

Forgetting `a,b` is tested separately using the additional legal filling
`(2,1,0,1)`. It has the same `u=1+2i` and `w` as source index `2`, but
is a different full filling. On the enlarged carrier, principal positivity
at the original point distinguishes the two singleton regions. Their
`w`-only images coincide, so that positivity cannot descend unambiguously.
Retaining `(a,b,w)` keeps the two fillings distinct.

The receiver must also reject altered witnesses or coordinate evidence,
and test the missing denominator guard: cross-multiplication at zero
can admit the spurious equation `0*y=0`. The frozen campaign requires
ordinary and optimized producer bytes to agree, an independent receiver,
zero-fuel and conflicting-request controls, and output-overwrite refusal.
The producer enumerates complement choices; the receiver separately
derives upward families from all 65,536 subset families using ordinary
sets. Agreement is limited to this contract and its finite domain.

The retained [evidence](../../experiments/multihole_positivity/evidence.json)
and [campaign](../../experiments/multihole_positivity/campaign.json) record:

- Two producer runs, ordinary and optimized, produced identical bytes.
- Each producer spent 50,760 logical units of its 100,000-unit allowance.
- The independent receiver examined all 65,536 subset families, derived the
  twelve basic and four joint families, and checked 384 query results.
  Its charged work was 1,059,191 units against 10,000,000.
- Six unit tests passed, including three deliberately changed geometry,
  missing-model and altered-witness payloads rejected by the receiver.
- The fifth launch refused an existing output before computation. There
  were no retries. Total wall time was 1.334 seconds; aggregate parent and
  child CPU was about 1.201 seconds. POSIX limits enforced the declared
  process memory, CPU and per-file output bounds.

The exact evidence SHA-256 is
`c249c3ac8f9350ca1fe1c4350e5b3c26827115ec2d4f3a787795840b9d19f4f6`.
Source hashes are in the retained campaign. They bind bytes, not native
identities or authenticity. Before this single execution, review corrected
CLI argument mismatch, premise ordering, the division control, and parent
resource accounting; no failed semantic trial was silently restarted.

From the repository root, with fresh destinations:

```sh
python experiments/multihole_positivity/checker.py --output /tmp/multihole-evidence-new.json
python experiments/multihole_positivity/verifier.py /tmp/multihole-evidence-new.json
python experiments/multihole_positivity/run_campaign.py /tmp/multihole-campaign-new
```

The campaign is the bounded reproducibility route. The first two commands
show the individual interfaces; running them is a new local replay, not an
extension of the already consumed campaign budget.

The current host has neither `cargo` nor `rustc`; native checking is
unavailable. [Research 0087](0087-typed-three-domain-threaded-multihole-calculus.md)
supplies a future typed witness-stock direction, while
[Research 0129](0129-bounded-breakthrough-trusted-boundaries.md) retains
the trusted-boundary distinction. Python evidence cannot authorize a
native identity, rewrite, objectification, or higher filler. Mathematical
constraints remain referenced at
[`mountain/adva-library`, `math/constraints/growth-obligation-v0000.json`,
commit `73a6af4ac4ed8225366d3c16794e309cff15f51d`](https://github.com/mountain/adva-library/blob/73a6af4ac4ed8225366d3c16794e309cff15f51d/math/constraints/growth-obligation-v0000.json)
and its
[documentary checkpoint](https://github.com/mountain/adva-library/blob/73a6af4ac4ed8225366d3c16794e309cff15f51d/math/constraints/growth-obligation-seal-v0000.json).
No dependency lock, registry, catalog, stable operation, or Pascal
obligation is changed or discharged by this calibration.

## 8. The Wu and Yang Lu continuation

After the finite run, Mingli asked to reconnect the Wu and Yang Lu methods
previously used in this project. The completed computation took 1.334 seconds;
its finite census did not hit its resource limit. Larger carriers do introduce
a real scaling issue: the full property algebra has `2^n` regions, and the
complement-choice route has `2^(2^(n-1))` candidates. Symbolic structure should
be used before enlarging that census. No speedup theorem follows from choosing
an elimination method.

The concrete graph equations are

\[
p-ax-b=0,\quad q-ay=0,\quad g_3=d-p^2-q^2=0,
\quad g_4=dr+p=0,\quad g_5=ds-q=0.
\]

Keep `a>0`, `y>0`, `q>0`, `d>0`, and every nonzero initial used by a
triangular chain. Wu-style pseudo-division can remove graph auxiliaries and
give identities; real sign conditions and singular branches must still be
checked. For this example the following hand-derived multiplier identity
already exposes the circle-observation pullback:

\[
d^2\left[\tfrac14-r^2-(s-\tfrac12)^2\right]-d(q-1)
=g_3-(dr-p)g_4+(d-ds-q)g_5.
\]

Also `d(s-1/4)-(q-d/4)=g_5`. On the graph, positive `d` transfers the
strict signs exactly to `q>1` and `4q-d>0`. These identities are original
algebraic derivations, not the output of a new Wu implementation or replay.
A future receiver can check their coefficients against the original graph
equations, without treating the desired conclusion as an extra hypothesis.

The relevant existing records are
[Research 0185](0185-yang-difference-substitution-inequalities.md), which
implements a sound but incomplete single difference-substitution certificate,
and the [audit of Research 0181](pascal-commutator-certificate.md#correction-to-research-0181s-evidence-interpretation).
The latter corrects its original independence and initial-coefficient claims;
those historical claims cannot be reused as checked authority.

The published Yang--Hou--Xia route is broader than that limited substitution
experiment: the publisher abstract of *Automated Discovering and Proving for
Geometric Inequalities*, LNAI 1669, 30--46 (1999),
[DOI 10.1007/3-540-47997-X_3](https://doi.org/10.1007/3-540-47997-X_3),
identifies discriminant sequences, Wu elimination and partial cylindrical
algebraic decomposition as components. Only the publisher abstract and
bibliographic record were consulted here; no full algorithm, source code,
proof of completeness or implementation was imported.

For our next symbolic program, equality reduction and sign certification
have separate outputs. A finite difference-substitution search can return a
checked sufficient sign certificate on an explicitly covered cone. Its
failure remains `Unknown`; it does not exhaust real counterexamples. A
complete decision for the admitted real polynomial fragment would require
an implemented real-algebraic feasibility procedure with all branches covered.
None is supplied by this campaign. Strict boundary points and denominator
zeros stay explicit.

Finally, a sign certificate cannot select the free positivity predicate.
After fixing the theory, forced positivity can instead be asked as the
absence of real solutions to its Boolean-polynomial model equations plus
`p_Q=0`, with consistency of the theory checked separately. This connects
Wu/Yang-style algebra to the declared logical question while preserving the
distinction between a nonnegative polynomial and a positive property.
The continuation is a proposed checking route; it adds no trial, retry,
native authority, or new result to the frozen five-launch campaign.
