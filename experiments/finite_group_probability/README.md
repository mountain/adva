# Finite probability at a word observation boundary

Status: proposed interpretation contract with a bounded external mathematical
calibration. This does not install a native Adva probability calculus.

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy;
account use is not his authorship, review or correctness guarantee. All prose,
code and synthetic fixtures here are project-original under Unknown v0.3.
No external text, images, source code or datasets are incorporated.

## The question and its limits

Can a finite observer use words with multiplicative actions while events retain
an additive probability measure? Yes, in the finite model below. This answers a
compatibility question, not whether groups are the final physical local theory.
An observer's inability to distinguish two states need not survive a later
action. An observation atom is relative to a fixed observation policy; it is
not thereby an indivisible physical object or a native word identity.

The minimum here is an engineering starting set, not a proof of axiom
independence or logical minimality. Probability itself does not require a group.

## A small proposed contract

| Obligation | Fixed data and exact condition |
| --- | --- |
| Finite scope | Nonempty explicitly complete carrier G, observation map q, and events formed from unions of observation fibres. Coverage is relative to this named carrier. |
| Positive normalization | Rational weights w(g)>=0, Z=sum w(g)>0. Set p(g)=w(g)/Z. Define P(A)=sum over g in A of p(g). Disjoint-event additivity and P(G)=1 follow by finite sums. |
| Reference binding | For density claims, pin a reference probability lambda(g)>0 on every element of G. Define rho(g)=p(g)/lambda(g). Do not change lambda or q to obtain a preferred answer. |
| Multiplication compatibility | If a group action is claimed, check its complete table, associativity, identity and inverses. If observed words are to multiply, require q(g)=q(g') and q(h)=q(h') to imply q(gh)=q(g'h'). Otherwise retain a probability observation without claiming a quotient group. |
| Joint-distribution binding | To compute a product of uncertain actions, supply their joint distribution. Multiplying marginal probabilities requires an explicit independence assumption or a check of the supplied joint table. |

For fixed finite events, finite additivity suffices: a disjoint countable family
can have only finitely many nonempty members. This does not license replacing
countable additivity when a later model introduces an infinite carrier.

Suggested representation fields are `carrier`, `composition_order`,
`multiplication_table`, `observation`, `reference_mass`, `probability_mass`,
`joint_mass`, `coverage_scope`, `budget` and `evidence`. These are proposed
contract fields, not new native syntax. Rational values use integer numerator
and positive-denominator pairs. A receiver must retain their source and history
bindings when eventually connecting this external model to native Adva objects.

## Several meanings of one

For a finite group of N elements, its uniform reference is lambda(g)=1/N.
Group translation is a permutation and therefore preserves this reference.
Conversely, invariance under all left translations forces every singleton to
have equal mass, so total mass one uniquely fixes that uniform distribution.
This is the finite normalized Haar construction, derived here by counting.

| Typed quantity | Value for the uniform model |
| --- | --- |
| Group identity | e_G, an element rather than a numerical mass |
| Unnormalized counting weight of one group element | 1 |
| Probability mass of one group element | 1/N |
| Total probability | 1 |
| Density relative to the uniform reference lambda | rho(g)=1 |

Thus density one is possible without making every word the same element. It
requires a fixed reference. With unnormalized counting measure instead, the
uniform probability density is 1/N. A common name, common scalar or equal
action does not erase the inputs, paths or histories that produced it.

Arbitrarily long words may represent the same group element. Counting words,
histories and group elements are three different sampling choices. Truncating
word length need not give a multiplication-closed set. Uniform measure on a
countably infinite discrete group cannot be normalized to a countably additive
probability: equal positive singleton masses sum to infinity, while zero masses
sum to zero. A finite observation alone does not remove this obligation.

## A precise energy-one condition, and its connection to std

With the reference fixed and strictly positive, define

    rho(g) = p(g)/lambda(g)
    E_lambda[rho] = sum lambda(g)*rho(g) = 1
    Q_lambda(p) = sum lambda(g)*rho(g)^2
                = sum p(g)^2/lambda(g).

Expanding the square gives the finite exact identity

    Q_lambda(p) - 1 = sum lambda(g)*(rho(g)-1)^2
                   = Var_lambda(rho) >= 0.

Consequently Q_lambda(p)=1 if and only if p=lambda, equivalently rho=1 at
every element of the complete named carrier. A suitable descriptive condition
is **reference-density uniformity**. It is a proposed research predicate, not
a new native primitive, physical energy law or semantic closure operation.

Here a zero standard-deviation target has a concrete role: the density's mean
one is automatic normalization, while its standard deviation zero asserts
uniformity relative to lambda. Squared rational residuals suffice; no square
root or floating-point equality is needed. For arbitrary p, positivity of
lambda is essential. A reference with zero atoms would need a separate support
contract and cannot silently reuse this predicate.

This is NOT the previous program's random variable X=J/k. That program checks
E_p[X]=1, an actual constraint on a binomial weighted model, and returns
Var_p(X), which can be positive. Choosing the density rho as the observable
changes the question and must be recorded explicitly. Neither quadratic energy
nor native fuel is renamed into the other. No acceleration follows from this
identity without a specified algorithm and measured comparison.

## Multiplication does not replace probability addition

For a declared joint law gamma(g,h), the product law is

    r(x) = sum over gh=x of gamma(g,h).

For independent actions gamma(g,h)=p(g)*s(h), this is group convolution:

    (p*s)(x) = sum over g of p(g)*s(g^{-1}x).

This adds alternative ways of reaching the same result, while group
multiplication composes their actions in order. In the finite group algebra,
the equivalent calculation is (sum p(g)[g])*(sum s(h)[h]). Its multiplicative
unit is the point mass at e_G, not the uniform distribution. The uniform law
is idempotent under convolution; on a nontrivial group it is not the unit.

Uniform marginals do not imply independence. If X is uniform and Y=X^{-1},
then both marginals have density one, yet XY=e_G with probability one. The
independent joint law instead gives a uniform product. This distinction is
retained as an exact control in both examples.

## Observation can hide both algebraic and probabilistic distinctions

In S3, use right operand first, a=(12), b=(23). Then aa=e, ab=(123) and
ba=(132). Observing only cycle type makes q(a)=q(b), but q(aa)!=q(ab).
There is no representative-independent product of those three observation
labels. Probabilities still push forward correctly: the identity,
transposition and three-cycle classes have reference masses 1/6, 1/2, 1/3.
Giving those three classes equal counting weight would change the reference.
Parity, by contrast, gives a legitimate two-element quotient group.

More sharply, set p(e)=1/6, p(a)=1/2, p((123))=1/3, all other masses zero.
Its cycle-type probabilities equal the reference probabilities: observed
density is identically one and observed quadratic energy is one. On the
six-element carrier, however, Q_lambda(p)=7/3. A zero residual at the observation
boundary cannot certify invisible directions. The C4 reuse has p(0)=p(1)=1/2
and zero elsewhere: full energy two, parity-observed energy one.

In general the observed density is the reference-weighted average of the fine
densities within each fibre. Squaring and averaging shows Q_observed<=Q_fine.
More precisely, the gap is the retained within-fibre residual

    Q_fine - Q_observed = sum_g lambda(g)*(rho(g)-rho_observed(q(g)))^2.

This is loss of distinguishable variation, not proof that the lost variation
has physically vanished or that search has converged. Refinement and a
reference-preserving observation map must remain explicit.

## Reproduction and authority

The fixed [contract](contract.json) bounds one exact external calibration to
S3 and C4, at most 10,000 counted work units, 30 seconds and 256 MiB address
space. It uses no candidate search. Run once into a new directory:

```sh
timeout 30s python -B -S experiments/finite_group_probability/check.py --output /tmp/adva-finite-probability
```

The resulting complete tables, distributions, observation maps and exact
counterexamples are replayable mathematical inputs. Python does not create
native semantic identities. This proposal does not modify the machine lock,
catalogue, library growth obligation, native instruction registry, Close or
free. Coverage of all native words, an implementation of the receiver in Adva,
physical applicability and practical benefit remain open.

The first retained [result](evidence/attempt-1/result.json) passes 437 counted
assertions in one campaign, including all 216 S3 and 64 C4 associativity triples,
ten invalid-input controls, the observation counterexample and both joint-law
cases. It uses 928 defined work units, 0.011147157 seconds through verification
and peak process RSS 10,496 KiB (10.25 MiB). There was no search, correction or
extra replay. Final result encoding/writing and research/authoring costs were
not separately measured and are excluded. The bound is on this synthetic
calibration, not a hardened arbitrary-input receiver.

Separately, the preceding `mean-constraint-match` Adva program passed its
[native Rust CI](https://github.com/mountain/adva/actions/runs/35163926651)
at commit `0185e13c87d9877614b2db03e3f73865e3e543db`: all 16 fixtures passed
`RustDataRunWithIndependentReplay`. Its run records are attached to that CI
run. That native result does not upgrade this new probability calibration
from its explicitly external status.

For the established mathematical terminology, see the MIT course's
[group-convolution notes](https://symm4ml.mit.edu/symm4ml_s26/notes/group-convolution).
This is a bibliographic pointer; no content from that source is incorporated.
