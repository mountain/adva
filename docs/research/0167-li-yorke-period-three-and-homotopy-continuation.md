# Period three, the 1975 statement, and the homotopy continuation programme

Date: 2026-09-11. Direction: Mingli Yuan. Literature reading and finite checks:
assistant (DeepSeek Harness), submitted through his account as an authorized
proxy. This note records a source audit and one bounded external check; it
registers no native semantics.

Status: external source audit plus one bounded external experiment. No Rust
witness, no stable API change, no library admission, no Seal.

Base: `59141a8af4d9a57ef192ded0b9354b0e93a34f51`.

---

## 1. Why this note exists

The programme's finite structures are threefold at several levels: the three
computers `T`, `X`, `K`; the three mechanism labels `subject/method/object`; the
six-port whole cut as `2 x 3`. The classical result that a one-dimensional map
carrying three forces unbounded periodic structure is therefore an obvious
comparison, and obvious comparisons are exactly where this repository asks for
the source to be read rather than recalled.

Reading the source changes the comparison. The paper's hypothesis is **not** a
point of period three; it never claims sensitivity; the phrase "scrambled set"
is not in it; and it does not cite Sharkovsky. Three of those four are the
standard popular rendering.

## 2. Provenance of the reading

The 1975 article was read from a scanned copy of the published pages. The
second conclusion's two-clause structure was recovered by rendering the theorem
page as an image, because text extraction dropped one of the two clauses. Two
of the four corrections below depend on that image reading and would not have
survived a text-only pass.

The paper is: **Tien-Yien Li and James A. Yorke, "Period Three Implies Chaos",
*The American Mathematical Monthly* 82(10), December 1975, 985-992.**

## 3. Theorem 1 as printed

> **THEOREM 1.** *Let J be an interval and let F: J -> J be continuous. Assume
> there is a point a in J for which the points b = F(a), c = F^2(a) and
> d = F^3(a), satisfy d <= a < b < c (or d >= a > b > c). Then*
>
> **T1:** *for every k = 1, 2, ... there is a periodic point in J having period
> k.*
>
> *Furthermore,*
>
> **T2:** *there is an uncountable set S contained in J (containing no periodic
> points), which satisfies the following conditions:*
> *(A) For every p, q in S with p != q,*
> *(2.1) lim sup |F^n(p) - F^n(q)| > 0 as n grows, and*
> *(2.2) lim inf |F^n(p) - F^n(q)| = 0 as n grows.*
> *(B) For every p in S and periodic point q in J,*
> *lim sup |F^n(p) - F^n(q)| > 0 as n grows.*

A point of period three satisfies the hypothesis with `d = a`, so T1 is a
corollary. It is not the hypothesis, and writing it as the hypothesis loses the
strict inequality `a < b < c`, which is what supplies the ordering the argument
uses.

## 4. Four corrections to the common rendering

1. **The hypothesis is the inequality, not a period-three orbit.** Period three
   merely satisfies it. Their own Remark (their word) draws the corollary.
2. **The paper never claims sensitivity.** "Sensitive dependence" does not
   appear. The word "chaotic" appears in quotation marks on p. 986 as a
   suggestion about what such a sequence "might be called"; it is not defined
   there and is not offered as a property proved.
3. **"Scrambled set" is not in the paper.** It says "an uncountable set S". The
   term is a later coinage; its first use was not located in this pass.
4. **T2 has two clauses, and (2.2) is the one usually dropped.** `(2.1)` says
   the pair never merges; `(2.2)` says it comes arbitrarily close infinitely
   often. Read together, T2 says there are uncountably many pairs whose
   provenances stay distinct while their *values* become indistinguishable
   infinitely often. This is the part of the 1975 paper with no analogue in the
   ordering theorem, and it is the part that bears on this repository's rule
   that value equality and observational equivalence authorize no contraction.

## 5. Sharkovsky's ordering, and what the converse actually says

**O. M. Sharkovsky, "Co-existence of cycles of a continuous mapping of the line
into itself", *Ukrainian Mathematical Journal* 16 (1964) 61-71** (Russian). The
ordering, read as forcing:

```
3 > 5 > 7 > 9 > ... > 2*3 > 2*5 > 2*7 > ... > 4*3 > 4*5 > ...
  > ... > 2^n*3 > 2^n*5 > ... > ... > ... > 8 > 4 > 2 > 1
```

If a continuous map of an interval has a point of period `m`, it has one of
every period `n` that comes after `m`. Period three is first, hence forces all
periods. The 1975 paper does not cite Sharkovsky; the result surfaced to Yorke
only later.

The real converse content is **sharpness**, not the vacuous reading "if all
periods occur then period three occurs". For every `m` there are continuous
interval maps whose set of periods is exactly those after `m`. Li and Yorke
supplied one such case themselves: their Appendix 1 is titled "Period 5 does not
imply period 3".

A short interval-covering argument shows the 1975 hypothesis forces a
period-three orbit: with `K = [a,b]`, `L = [b,c]`, continuity gives `F(K)
containing L` and `F(L) containing K union L`, so `K -> L -> L -> K` is a
three-loop, and periods one and two are excluded by `K intersect L = {b}`. So
T1 is exactly the period-three corollary of Sharkovsky's theorem. **Flagged
disagreement:** Jiu Ding argues the opposite. The disagreement was not
reconciled in this pass and is recorded rather than settled; it appears to
concern the breadth of the hypothesis rather than logical strength.

## 6. Provenance and publication history

*Flagged: this section rests on a single secondary source ([D]).*

The *Monthly* first returned the manuscript as too research-oriented, inviting
an expository resubmission; it then lay dormant for about a year. In May 1974
Robert M. May lectured at Maryland on iteration of the logistic map; Yorke
showed May the manuscript, and May's reaction motivated a two-week rewrite. At
the 7th International Conference on Nonlinear Oscillations, East Berlin, 1975,
Sharkovsky told Yorke of the 1964 result through a Russian-Polish-French-English
relay of translators; the reprint arrived about four months later. Reference 17,
added in proof, is May's paper on stable cycles.

"Period three implies chaos" is the paper's own title, but the noun "chaos" was
already current (Lorenz, 1963/64). The claim that this paper "created the word
chaos in mathematics" is a secondary-source claim and is not adopted here.

## 7. Tien-Yien Li's later programme

Born 1945, died 25 June 2020. B.S. National Tsinghua University, Taiwan; Ph.D.
1974 University of Maryland under James A. Yorke; Michigan State University for
42 years, retiring in 2018 as University Distinguished Professor Emeritus. He
also proved Ulam's conjecture on finite approximation of the Frobenius-Perron
operator, reference 9 of the 1975 paper.

His later programme was **homotopy continuation for polynomial systems**. The
following attributions were corrected in this pass, against the common
rendering:

| Commonly attributed to Li | Actual |
|---|---|
| the 1997 survey in the *Bulletin of the AMS* | **Li, *Acta Numerica* 6 (1997) 399-436** |
| polyhedral homotopy | **Huber & Sturmfels, *Math. Comp.* 64 (1995) 1541-1555**, on Bernshtein's theorem; Li's own polyhedral work is 1996/1999/2001 plus HOM4PS |
| coefficient-parameter continuation | **Morgan & Sommese, *Appl. Math. Comput.* 29(2) (1989) 123-160** |
| a standalone "Cauchy endgame" article | none found; it is in **Li, *Handbook of Numerical Analysis* XI (2003) 209-304**, implemented as `endGameCauchy` in Macaulay2; the classical endgames are Morgan-Sommese-Wampler and Sosonkina-Watson-Stewart |

Li's own contributions include the cheater's homotopy and the random product
homotopy with deficient systems (with Sauer and Yorke, 1987-1989), the BKK root
count in `C^n` (with X. Wang, 1996), and HOM4PS-2.0 (with T. Lee and C. H.
Tsai, 2008).

**No source found in this pass links the chaos work to the homotopy work.** The
observation that one career contains both is an outside reading, not a
documented intention, and is recorded here as such.

## 8. Reader's record

Mingli Yuan states that he has read 丁玖, 《神奇的周期三》 (the popular piece on
Li listed as [D]) and 张筑生, 《微分动力系统原理》 (Science Press; he refers to
it as 《微分动力系统》). These are recorded as a **reading record under his
name**, not as verification of any claim in either source. The exact edition and
printing of the second title were not verified in this run.

## 9. The bounded check

One exact consequence is checkable and is registered as
`adva.bounded-experiment.li-yorke-period-three-matrix.v0`:
[`experiments/li_yorke_period_three/`](../../experiments/li_yorke_period_three/).

It is worth separating what the checker *derives* from what it *stipulates*.
From the concrete rational three-cycle `2/7 -> 4/7 -> 6/7 -> 2/7` of the tent
map, and from exact images of the two intervals under the tent map, the checker
**derives** the covering relation `I1 -> I2`, `I2 -> I1`, `I2 -> I2` and hence
the transition matrix

```
A = [[0, 1],
     [1, 1]]
```

It is not supplied with that matrix. It then checks exactly that `A` and the
golden one-hole matrix `M = [[1,1],[1,0]]` share the characteristic polynomial
`t^2 - t - 1`, that `P A P^-1 = M` for the basis swap `P`, that `M^2 =
[[2,1],[1,1]]` with trace 3 and characteristic polynomial `t^2 - 3t + 1`, that
`M^n` matches the Fibonacci-entry formula up to `n = 24`, and that `trace(A^n)`
is the Lucas number `L_n`.

Two controls refuse the reading that the matrix decides anything:

- **The golden one-hole map is tame.** `F(x) = 1 + 1/x` maps `[1,2]` onto
  `[3/2,2]`, is monotone, and `F(F(x)) - x = -(x^2 - x - 1)/(x + 1)` exactly, so
  its second iterate has exactly one fixed point in `[1,2]` and no two-cycle.
  The polynomial `x^2 - x - 1` is the golden matrix's own characteristic
  polynomial: **the same polynomial governs an attracting fixed point and a
  chaotic three-cycle.**
- **The third-turn rotation is an isometry.** `R(x) = x + 1/3` on the circle has
  every point of period exactly three, no fixed point, no two-cycle, and
  preserves exact distances on the test grid, so it has no proximal pair at all.
  Three alone is not chaos outside the interval.

A wrong-matrix control (`[[0,1],[1,2]]`, characteristic polynomial `t^2 - 2t -
1`) is refused, so the equality test is not vacuous.

The checker additionally enumerates the `2^n` linear branches of the tent
iterate for every `n` up to 8, verifies each branch maps onto `[0,1]` with slope
`+/-2^n`, solves each branch's fixed point exactly, verifies it exactly, and
finds exactly `2^n` points fixed by `T^n` with `30` points of least period `5`
and `126` of least period `7`. The Lucas count is checked to be a lower bound
for it at every depth.

Contract `5010d8aea9a77ad7bc785365fcb7249d92a10920dfec7c4ecc68f0d06e189207`,
checker `c07258af5ecaae67d4af698ab00175793ccb452cb01be2429f15d92e5135fbf3`,
evidence `e557a20ab20e3775a0202bb09c8b73e2f16a2e8f3fdc6f66c7006f05be13a790`.
2,505 assertions, no floating-point value in any acceptance test, 30-second
contract. `RLIMIT_CPU` and `RLIMIT_FSIZE` were installed; **`RLIMIT_AS` was
refused by this platform** and is recorded as refused rather than as installed.

## 10. What this note does not establish

- It does not claim that any Adva program, three-computer cycle, observer or
  diagram is a Li-Yorke map, or that it has a periodic orbit of any period.
- It does not claim that an equal characteristic polynomial identifies two
  spaces, two semantics or one dynamics; section 9 exists to refuse that.
- It does not characterize the folding that separates the two regimes.
- Topological entropy, the sharpness of the Sharkovsky ordering, and the
  uncountable set are imported theorems. They are not reproved here.
- It does not promote anything to `claims.toml` beyond the bounded external
  entry named in section 9, and it changes no stable API, IR schema or
  `ProgramSlice` priority.

## 11. Sources

- [1] Li & Yorke, *Amer. Math. Monthly* 82(10) (1975) 985-992 —
  https://www.its.caltech.edu/~matilde/LiYorke.pdf
- [2] Sharkovsky, *Ukrainian Math. J.* 16 (1964) 61-71.
- [3] T. Chen, *Tien-Yien (TY) Li, 1945-2020*, NA Digest 20(26) (2020) —
  https://na-digest.coecis.cornell.edu/na-digest-html/20/v20n26.html
- [D] 丁玖, 《神奇的周期三》, 返朴/澎湃, 26 May 2023 —
  https://www.thepaper.cn/newsDetail_forward_23234632 (secondary)
- [4] Marcolli, *Sharkovsky's Ordering and Chaos* —
  http://www.its.caltech.edu/~matilde/FractalsUToronto4.pdf
- [5] Huang & Ye, *Topology Appl.* 117 (2002) 259-272 —
  https://doi.org/10.1016/S0166-8641(01)00025-6
- [6] Li, *Acta Numerica* 6 (1997) 399-436 —
  https://doi.org/10.1017/S0962492900002695
- [7] Li, Sauer, Yorke, *The Cheater's Homotopy*, *SIAM J. Numer. Anal.* 26(5)
  (1989) 1241-1251 — https://doi.org/10.1137/0726080
- [8] Huber & Sturmfels, *Math. Comp.* 64 (1995) 1541-1555 —
  https://doi.org/10.1090/S0025-5718-1995-1308452-6
- [9] Lee, Li, Tsai, *HOM4PS-2.0*, *Computing* 83 (2008) 109-130 —
  https://dlnext.acm.org/doi/10.1007/s00607-008-0015-6
- [10] Li, *Handbook of Numerical Analysis* XI (2003) 209-304 —
  https://doi.org/10.1016/S1570-8659(02)11004-0
- [11] Verschelde, *Polynomial Homotopy Continuation* —
  http://homepages.math.uic.edu/~jan/tutorial.pdf
- [12] Sommese-Verschelde-Wampler bibliography —
  https://antonleykin.math.gatech.edu/math6122spr12/PROJECTS/
- [13] 张筑生, 《微分动力系统原理》, 科学出版社 (edition and year not verified
  here) — https://www.ecsponline.com/goods.php?id=196490

### Flagged / unverified

No primary recollection by Li or Yorke on the title phrase. First use of
"scrambled set" not located. No standalone Cauchy-endgame article by Li, Tsai or
Zeng. No documented link between the chaos and homotopy programmes. The
rejection and rewrite history rests on [D] alone. The "26 doctoral dissertations"
figure comes from [3]. zhMATH, Wikipedia and the SIAM obituary page were
unreachable in this pass, so several bibliography entries rest on
primary-adjacent substitutes rather than on the publisher record.
