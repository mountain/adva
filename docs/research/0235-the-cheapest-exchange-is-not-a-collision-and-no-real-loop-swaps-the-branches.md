# 0235 — The two real-root branches are not exchanged by any real loop, and the cheapest exchange is not a collision

**Date**: 2026-09-25 · **Contract**: `experiments/exchange_amplitude_variation_v1/contract.json` ·
**Superseded contract**: `contract-initial.json` · **Checker**: `calibration.py` ·
**Evidence**: `evidence.json` · **Paired test**: `tests/python/test_exchange_amplitude_variation.py`

**Status**: one bounded external exact calibration in Python with declared `sympy`
for resultants and Groebner bases. No native certificate, no stable API, no
`ValueType`, no `OperationSpec`, no IR version, no Seal, no library admission, no
transport, no terminology home, no physical claim, no forecast and no
meteorological data. `mountain/process-geometry` and the repository's own note
0228 are cited as references; nothing is copied from either.

中文摘要：为 0233 十二相位周期程序的两条实根分支找一个"最省"的交换扰动 $(p,q)$。
第一版契约把 $(p,q)$ 实现成两实根的自由移动，**退化**（$p=-4,\ q=8\sqrt{17}-16$ 时
四次式在 $h=0$ 有二重根、$J_\infty=0$；分支取 $\pm\varepsilon$ 时 $J_\infty=\varepsilon$
精确成立），因此保留原契约、换版为**过程侧**主族（两个非线性相位的曲率取
$(q_0,q_1)=(1/8+p,1/8+q)$），分支恒由声明返回条件钉住。结果三条：**(1)**
判别式簇为 $-(8p+1)^6(8q+1)^2(64q+17)^2(2048p^2+608p-8q+43)$（12 次、52 项）；
**(2)** 各侧振幅的一致下界 $J_\infty\ge1$ 在 $(-2,17/10)$ 处**取到**且是内点、不在判别式簇上
——"最省的交换就是碰撞"这个猜想对极小点**为假**，二阶变分恒为 0、是一片平台；
**(3)** 任何声明的实闭环都**实现不了**两条实根分支的对换（L0 恒等对照通过，L2/L3/L4 记为
Undecided 并保留精确部分结果）。这条正是方案一必须走**复化**的原因，也是方案二
（四维时空 monotile、两侧互度、未来时间资源）要补的那一维。

## 1. What was asked, and the correction that had to come first

The question was to obtain the two branch perturbations $(p,q)$ of note
[0233](0233-periodic-programs-before-floquet-observations.md)'s twelve-phase program
by an exact variational computation that minimises the anomaly amplitude on every
side of the whole process, with the exchange of the two real-root branches as the
constraint, and to certify it with Wu's elimination, Yang Lu's real-root methods
and Zhang Jingzhong--Yang Lu positivity.

The first contract realised $(p,q)$ as a perturbation of the real-root quadratic
factor, i.e. as a free movement of the two branches. That family is degenerate and
the degeneracy was found before execution, not hidden: with
$P_{p,q}(y)=(y^2+py+(20-8\sqrt{17}+q))(y^2+20+8\sqrt{17})$ and $y=h+2$, the choice
$p=-4$, $q=8\sqrt{17}-16$ makes the first factor $(y-2)^2$, so the quartic has a
double root exactly at $h=0$ where every side amplitude vanishes and
$J_\infty=0$; with branches at $h=\pm\varepsilon$ the functional is exactly
$\varepsilon$ for rational $\varepsilon=1/2,1/4,1/10,1/100$. The infimum is
therefore $0$, approached with distinct branches and unattained. The initial
contract is retained byte for byte (`contract-initial.json`, sha256
`da49e395ad998dccbdf8794184043428023e06b9c6a22e6b74224b14d33eed01`) and the
correction is recorded in the active contract instead of rewriting it.

The amendment puts the perturbation on the process, so that the branches stay
defined by the declared return condition and the reference is never a branch:

$$E_{p,q}(h)=\tfrac34\Bigl(\tfrac12h+\bigl(\tfrac18+p\bigr)h^2\Bigr)
+\bigl(\tfrac18+q\bigr)\Bigl(\tfrac12h+\bigl(\tfrac18+p\bigr)h^2\Bigr)^2,
\qquad E_{p,q}(0)=0 .$$

A second declared realisation keeps the process frozen and perturbs the branch
levels — the positive branch solving $E(h)=1+p$ and the negative one $E(h)=1+q$,
which is the literal reading of "a perturbation at the positive and the negative
real root". Both are run; they agree at $p=q=0$ and disagree elsewhere, and every
disagreement is retained (at the witness below, the branch-level positive equation
has no real root at all).

One structural identity makes the problem finite and is asserted rather than
assumed: because phases 2..11 are pure translations, every branch has
$h_3=\dots=h_{11}=h_2=E_{p,q}(h)$, so on a branch the ten middle sides carry
exactly the declared level $1$ and

$$J_\infty(p,q)=\max_{\text{two branches}}\max\bigl(|h|,\ |E_0(h)|,\ 1\bigr).$$

## 2. The discriminant variety

Cleared of the denominator $2^{39}$,

$$D(p,q)=-(8p+1)^6(8q+1)^2(64q+17)^2\bigl(2048p^2+608p-8q+43\bigr),$$

of total degree twelve, degree eight in $p$ and five in $q$, with 52 terms and four
irreducible factors of multiplicity $6,2,2,1$. The four declared branches are

| Branch | Locus | Crossing type |
| --- | --- | --- |
| B1 | $q=256p^2+76p+43/8$ (a parabola) | two simple roots collide |
| B2 | $q=-17/64$ | a two-fold factor for every $p$; real double roots iff $p\ge-19/128$ |
| B3 | $q=-1/8$ | the degree drops |
| B4 | $p=-1/8$ | the degree drops |

The identity $\operatorname{Res}_h(G,G_h)=\operatorname{lc}(G)\operatorname{disc}_h(G)$
is verified symbolically, the sign rule $\operatorname{sign}(D)=-\operatorname{sign}(f(p)-q)$
is checked at the declared off-branch points, and the vertex structure is exact: at
$(-19/128,-17/64)$ the quartic is $(1/8+p)^2(1/8+q)(h-32/3)^4$, and at the triple
point $(-1/8,-1/8)$ it degenerates to $3h/8-1$ with the single finite root $8/3$.

## 3. Stationary cases, and what the minimum actually is

The maximum is piecewise algebraic, so the run works case by case in the variable
order $[h,p,q,\lambda]$, triangularises each system by pseudo-division into a
characteristic chain, reduces the conclusion modulo the chain, and cross-checks
every remainder by an independent Groebner membership test.

- The two cases with $|h|$ active are **empty**, with an exact certificate rather
  than a count: $G_q=h^2(8hp+h+4)^2/64=0$ together with $G(0)=-1$ forces
  $p=-(h+4)/(8h)$, after which $G\equiv-1$, contradicting $G=0$. Their nonzero
  pseudo-division remainders are retained, and the run records the chain
  limitation explicitly: a basic chain is not a zero-decomposition of an
  inconsistent system, so the Groebner agreement there is vacuous.
- The two cases with $|E_0(h)|$ active have **remainder 0** and an agreeing
  Groebner membership test. Their whole stationary locus,
  $p=-(h+2)/(8h)$, $q=-(h^2+24h-128)/(8h^2)$, satisfies $q=f(p)$ identically: every
  stationary candidate lies **on B1**, i.e. on the discriminant variety.

So the declared conjecture "the cheapest exchange is the collision configuration"
is **true for every stationary candidate and false for the minimiser**. The
minimiser is the floor: since the ten middle sides carry exactly $1$, $J_\infty\ge1$
always, and $J_\infty=1$ is **attained** at

$$(p,q)=(-2,\ 17/10),\qquad J_\infty=1,$$

in the interior with $D\neq0$ there; the two branch enclosures give
$|h|\le0.5995$ and $|E_0|\le0.9737$. The minimum is a non-isolated plateau: on the
declared rational box $p\in[-2001/1000,-1999/1000]$, $q\in[1699/1000,1701/1000]$
the run decides exactly that $J_\infty\equiv1$, so the second variation is
identically zero and the verdict is `SecondVariationZero_NonIsolatedMinimum`. The
declared control functional $J_2$ behaves quite differently — $J_2>20$ always, with
infimum exactly $20$, unattained, approached along the ray $p=-t,q=t$ and not on
$D=0$ — so the two functionals **disagree**, which is reported as a result.

## 4. The exchange, and its boundary

Five closed loops are declared and computed in exact rational arithmetic. A
non-encircling control square returns the identity, as it must. A loop around a
smooth point of B1 crosses the branch twice at simple double roots and returns the
**identity** there as well, because the two transpositions cancel. The remaining
loops are recorded as **Undecided**, never faked: around B2 the crossings are
double-double (two pairs of roots collide at once) and around the triple point and
the wide loop the crossing parameters are irrational, so identifying which sheets
collide would need a certified complex or projective continuation that this run
does not implement. Their exact crossing counts, defining polynomials, edge
midpoint counts and per-crossing gcd data are retained.

The finding recorded is therefore: **no declared real loop realises the
transposition of the two real-root branches.** The stated reason is that a
transversal crossing of a smooth branch point contributes a transposition while a
closed real loop crosses each branch an even number of times; the run records this
as a finding with its justification, not as an exhaustive certificate, and the
Undecided loops are the honest boundary of that statement.

## 5. Controls, including the one that failed

1. The superseded contract's collapse witness is reproduced exactly.
2. **The deleted-side control failed to discriminate and is recorded as a failure
   rather than repaired**: deleting any single side (0, 1, 2 or 11) leaves the value
   at the witness at exactly 1, because at least nine frozen sides still carry 1, so
   the minimiser does not move. The discriminating variant — deleting all ten frozen
   sides — does move it, to the unattained infimum 0 approached along the escape ray.
   The payload states `single_side_deletion_moves_the_minimiser: False`.
3. The frozen unperturbed roots and the conjugate pair of note 0234 are reproduced.
4. The two realisations agree at $p=q=0$ and disagree elsewhere, retained.
5. The identity-loop control passes.
6. $E_{p,q}(0)=0$ is asserted at six declared perturbations.

## 6. What this means for the two schemes

The repository already carries two schemes for the same process. Scheme one reads
the exchange through a **spherical spectrum and its complexification**; scheme two
would read it through a **four-dimensional spacetime monotile**, using not only
spatial resources but also future time resources, with the first and second
addresses of note 0228 used simultaneously as two mutually measuring sides.

This run belongs to scheme one, and its result sharpens exactly why the
complexification is not optional there: in the declared real two-parameter family
the two real-root branches are **not exchanged by any real loop**, the cheapest
configuration is a plateau at the amplitude floor rather than a collision, and the
stationary candidates sit on the discriminant variety while the minimiser does not.
The complex pair is therefore where the exchange has to live, and a carrier whose
time direction supplies the missing dimension is precisely what scheme two
proposes. This run supplies scheme two's comparison baseline: $J_\infty=1$ attained
at $(-2,17/10)$, the resource account of a real-side protocol, and the three
falsifiable controls it must beat (the two-point block-address witness of 0228 §3,
the extrusion countermodel of 0228 §7, and the identity-loop control here).

The three time conditions proposed for scheme two — a factor-two condition at the
13 scale on the second address read as target state, a condition at the 25 scale
requiring the Later-Heaven Taixuan "three exits" clause, and the crossing point
introduced on the spatial side once the time factor enters, whose maximum
amplitude is to be computed — are **recorded as declared next-boundary items and
are not executed here**: the second and third need definitions that this note does
not invent, and the crossing-point reading already computed for the 0233 fixture
sits on side 0 with amplitude $2+\sqrt{8\sqrt{17}-20}=5.6034490429\ldots$.

## 7. Boundary

No physical claim is made anywhere: nothing here is a wind gap, a plateau, a
January circulation, a forecast or an observation. The meteorological
correspondence in the contract is declared and its data side is Unavailable in this
checkout. No Rust source, `Cargo.toml` or `Cargo.lock` changed, so the
advance-surface base commit does not move. Ruff is absent from the project virtual
environment and no workflow runs it; the host's ruff 0.15.7 reports nothing on the
two new Python files. Successive difference substitution is **not** implemented —
the interval-subdivision variant of exact rational interval arithmetic decides every
declared sign instead, and the run says so.

The undecided items are retained: the root permutations of three loops, and the
minimality certificate for a non-isolated plateau, which is exactly zero second
variation rather than a positive-definite one.

Authored and checked by deepseek-v4-flash-vision-exp (DeepSeek Harness), submitted
through Mingli Yuan's authorized account proxy. Account use is not his authorship,
review, endorsement or correctness guarantee. One agent wrote the contract, the
checker and this note; there is no independent reviewer.
