# Li–Yorke "Period Three Implies Chaos" and Tien-Yien Li's Homotopy Continuation Program

*Quotations from the 1975 paper were read from a scanned JSTOR PDF ([1]); unverified items are flagged.*

## Topic A — The 1975 result

### A1. Bibliographic confirmation and verbatim theorem

Confirmed exactly as stated: **Tien-Yien Li and James A. Yorke, "Period Three Implies Chaos," *The American Mathematical Monthly* 82(10), Dec. 1975, 985–992** ([1], [2]).

**Verbatim ([1], p. 987):**

> **THEOREM 1.** *Let J be an interval and let F: J → J be continuous. Assume there is a point a ∈ J for which the points b = F(a), c = F²(a) and d = F³(a), satisfy*
> *d ≤ a < b < c (or d ≥ a > b > c).*
> *Then*
> **T1:** *for every k = 1, 2, … there is a periodic point in J having period k.*
> *Furthermore,*
> **T2:** *there is an uncountable set S ⊂ J (containing no periodic points), which satisfies the following conditions:*
> *(A) For every p, q ∈ S with p ≠ q,*
> *(2.1) lim sup_{n→∞} |Fⁿ(p) − Fⁿ(q)| > 0*
> *and*
> *(2.2) lim inf_{n→∞} |Fⁿ(p) − Fⁿ(q)| = 0.*
> *(B) For every p ∈ S and periodic point q ∈ J,*
> *lim sup_{n→∞} |Fⁿ(p) − Fⁿ(q)| > 0.*

Two commonly misreported points: **the hypothesis is *not* "a point of period 3"** but the inequality above (period 3 merely *satisfies* it), and **sensitivity is never claimed** — the paper says only that such a sequence *"might be called 'chaotic'"* (p. 986), undefined.

### A2. Scrambled sets; Li–Yorke vs Devaney chaos

**"Scrambled set" does not occur in the 1975 paper** (I grepped the full text); it says only "an uncountable set S ⊂ J"; first use of the term is **[UNVERIFIED]**.

Modern abstraction to (X, f, d): (x, y) is a **Li–Yorke (scrambled) pair** if lim inf_{n→∞} d(fⁿx, fⁿy) = 0 (**proximality**) and lim sup_{n→∞} d(fⁿx, fⁿy) > 0 (**separation**); a **scrambled set** has every two distinct points forming such a pair; f is **Li–Yorke chaotic** if an *uncountable* one exists.

The 1975 paper treats continuous interval maps only. Generalisation to compact metric spaces and comparison with **Devaney chaos** (transitivity + dense periodic points + sensitivity) came later; **Huang & Ye (2002)** proved *Devaney's chaos or 2-scattering implies Li–Yorke's chaos* ([6]), and the converse fails. The summary "period 3 ⟹ all periods" conflates T1 with the real hypothesis and ignores T2.

### A3. Sharkovsky's priority and the ordering

**Priority confirmed:** O. M. Sharkovsky, *"Co-existence of cycles of a continuous mapping of the line into itself"*, **Ukrainian Mathematical Journal 16 (1964) 61–71** (Russian; [4], [5]). Sharkovsky lived 1936–2022. The ordering ◁:

> 3 ◁ 5 ◁ 7 ◁ 9 ◁ ⋯ ◁ 2·3 ◁ 2·5 ◁ 2·7 ◁ ⋯ ◁ 2²·3 ◁ 2²·5 ◁ ⋯ ◁ 2ⁿ·3 ◁ 2ⁿ·5 ◁ ⋯ ◁ ⋯ ◁ 2⁵ ◁ 2⁴ ◁ 2³ ◁ 2² ◁ 2 ◁ 1

If continuous f : I → I has a point of period m, it has one of every period n with m ◁ n.

**Reverse direction, precisely.** Period 3 forces all periods, being the *first* element of ◁. "If all periods occur, is there period 3?" is trivially yes, with no content. The real converse content is **sharpness**: for each m there are continuous interval maps with period m and no period m′ whenever m′ ◁ m, m′ ≠ m. Li & Yorke gave the m = 5 case — **Appendix 1, "Period 5 does not imply period 3"** ([1]).

**Is T1 a special case of Sharkovsky?** Once a period-3 orbit exists, T1 follows — and the Li–Yorke hypothesis supplies one: with K = [a,b], L = [b,c], d ≤ a < b < c, F(K) = L and F(L) = [c,d] ⊇ K ∪ L, so K→L→L→K is a 3-loop, and a point following it has period exactly 3 (periods 1 and 2 are excluded by K ∩ L = {b}). So **T1 is exactly the period-3 corollary of Sharkovsky's theorem**. *Flag:* Jiu Ding argues the opposite ([4]) — likely a disagreement about applied breadth of the *hypothesis*, not logical strength. Unambiguous: **T2 has no Sharkovsky analogue**; there the novelty lies. The paper **never cites Sharkovsky** ([1], p. 992).

### A4. Publication history and the word "chaos"

The *Monthly* editor first returned the manuscript as too research-oriented, inviting an expository resubmission; it lay dormant nearly a year. In **May 1974 Robert M. May** lectured at Maryland on logistic-map iteration; Yorke showed him the manuscript en route to the airport, and May's reaction motivated a two-week rewrite. At the **7th International Conference on Nonlinear Oscillations, East Berlin, 1975**, Sharkovsky told Yorke of his earlier result through a Russian→Polish→French→English relay of translators; the reprint arrived about four months later ([4]).

"Period three implies chaos" is the paper's own title; "chaotic" appears in quotation marks as a suggestion, not a definition. Ding says the paper "first created the word chaos in mathematics" ([4]), though the term was already current (Lorenz 1963/64). **[UNVERIFIED: no primary quotation from Yorke or Li on the title phrase.]**

### A5. Biography ([3])

Born **1945**, died **25 June 2020**, aged 75. **B.S. mathematics, National Tsinghua University, Taiwan; Ph.D. 1974, University of Maryland, advisor James A. Yorke.** At **Michigan State University** 42 years, supervising **26 Ph.D. dissertations**, retiring **2018** as **University Distinguished Professor Emeritus**. He also proved **Ulam's conjecture** on the Frobenius–Perron operator, ref. 9 of the 1975 paper. Later program: "his greatest contribution was in his lifelong dedication to **homotopy continuation methods**, which started with his work on computing **Brouwer's fixed point**" ([3]).

## Topic B — The homotopy continuation program

### B6. Same person; key works

Sources: ([3], [7], [8]).

- *Solving polynomial systems*, Math. Intelligencer **9**(3) (1987) 33–39 ([10]); **Numerical solution of multivariate polynomial systems by homotopy continuation methods, *Acta Numerica* 6 (1997) 399–436** ([9]); and the survey in *Handbook of Numerical Analysis* **XI** (2003) 209–304 ([15]).
- Li, Sauer, Yorke: *Numerical solution of a class of deficient polynomial systems*, SIAM J. Numer. Anal. **24**(2) (1987) 435–451; **The random product homotopy and deficient polynomial systems**, Numer. Math. **51**(5) (1987) 481–500; **The cheater's homotopy**, SIAM J. Numer. Anal. **26**(5) (1989) 1241–1251 ([11]).
- Li & X. Wang: *The BKK root count in **C**ⁿ*, Math. Comp. **65**(216) (1996) 1477–1484, plus 1991–92 papers on deficient systems; with T. Wang, *Random product homotopy with minimal BKK bound*, Lectures in Appl. Math. **32**, AMS (1996) 503–512.
- *Solving polynomial systems by polyhedral homotopies*, Taiwanese J. Math. **3**(3) (1999) 251–279; *HOM4PS-2.0* (T. Lee, T. Y. Li, C. H. Tsai), Computing **83** (2008) 109–130 ([13]); and (Li & X. Li) *Finding mixed cells in the mixed volume computation*, Found. Comput. Math. **1**(2) (2001) 161–181.

**Corrections to the prompt.** (i) The 1997 survey is in ***Acta Numerica*** 6, **not** the *Bulletin of the AMS* ([7], [9]). (ii) **Polyhedral homotopy** is **Huber & Sturmfels**, Math. Comp. **64** (1995) 1541–1555 ([12]), resting on **Bernshtein's theorem**; the **BKK bound** honours Bernshtein–Kushnirenko–Khovananskii. (iii) **Coefficient-parameter polynomial continuation** is **Morgan & Sommese**, Appl. Math. Comput. **29**(2) (1989) 123–160, not Li's. (iv) **The Cauchy endgame is Li's**, in his 2003 Handbook chapter ([15]), implemented as `endGameCauchy` in Macaulay2 ([17]). **[UNVERIFIED: no standalone "Cauchy endgame" article by Li, Tsai or Zeng located. Classical endgames: Morgan–Sommese–Wampler (Numer. Math. 58 (1991) 669–684; Adv. Appl. Math. 13 (1992) 305–327; Numer. Math. 63 (1992) 391–409) and Sosonkina–Watson–Stewart ([18]).]**

### B7. Mathematical structure

Given **F**(x) = 0 on **C**ⁿ, choose a **start system G** with known nonsingular solutions and form **H**(x,t) = (1−t)**G**(x) + t**F**(x), t ∈ [0,1]. The parameter space is **C** (an interval, for real homotopies); the **solution paths** are the components of the zero fibre H⁻¹(0) lifted over t, from the roots of **G** to those of **F**, followed by **predictor–corrector**: an Euler predictor step in t, then Newton correction onto H = 0. Paths escaping to infinity are solutions at infinity, discarded — making the method complete up to the root count.

The **number of paths** follows from a root count for the start system: the **Bézout number** ∏deg Fᵢ for dense systems, or the **BKK/mixed-volume bound** for sparse ones (Bernshtein: for generic coefficients the number of isolated roots in (**C**\\{0})ⁿ equals the mixed volume of the Newton polytopes). The **γ-trick** — replacing the straight line by γ(1−t)G + tF, γ = e^{iθ} random on the unit circle — makes every path nonsingular for all t ∈ (0,1] except for finitely many θ. The **cheater's homotopy** starts from a system of the *same* structure when only one system's coefficients are wanted, cutting the path count — the ancestor of the **coefficient-parameter homotopy**, which moves inside the coefficient space of a fixed monomial support.

**Monodromy / path jumping.** Looping in parameter space around the **discriminant locus** permutes the solutions (the **monodromy group** action), so a tracked loop returns a generally *different* solution — the basis of the monodromy algorithm for decomposing non-generic or positive-dimensional solution sets.

### B8. Software lineage and Li's school

**HOMPACK** (Watson, Billups, Morgan; ACM TOMS 1987); **CONSOL** (Morgan, *Solving polynomial systems using continuation for engineering and scientific problems*, Prentice-Hall 1987; cf. ACM TOMS 9(1) (1983) 1–17); **PHCpack** (Verschelde, UIC — "PHC stands for Polynomial Homotopy Continuation", [8]); **Bertini** (Bates, Hauenstein, Sommese, Wampler; [14]).

Li's lineage includes **Birkett Huber**, **Tianran Chen**, **Xiaoshen Wang**, **Chun-Hua Tsai** (HOM4PS-2.0, [13]) and **Zhonggang Zeng**; his Michigan State group was a principal node, with UIC and Notre Dame, of the **numerical algebraic geometry** community ([16]).

### B9. Links between the two programs

**None found.** No statement by Li or others draws an ironic or conceptual circle between them; [3] presents two separate phases of one career, [4] narrates them as parallel activities. **The irony appears to be an external observation. [NOT VERIFIED.]**

## Bibliography

1. Li & Yorke, Amer. Math. Monthly 82(10) (1975) 985–992 — scanned PDF: https://www.its.caltech.edu/~matilde/LiYorke.pdf
2. MathWorld: https://sanweb.lib.msu.edu/crcmath/math/math/p/p253.htm
3. T. Chen, *Tien-Yien (TY) Li, 1945–2020*, NA Digest 20(26), 2020: https://na-digest.coecis.cornell.edu/na-digest-html/20/v20n26.html
4. 丁玖 (Jiu Ding), 《神奇的周期三》, 返朴, 2023: https://www.thepaper.cn/newsDetail_forward_23234632
5. Marcolli, *Sharkovsky's Ordering and Chaos*: http://www.its.caltech.edu/~matilde/FractalsUToronto4.pdf
6. Huang & Ye, Topology Appl. 117 (2002) 259–272: https://doi.org/10.1016/S0166-8641(01)00025-6
7. Sommese–Verschelde–Wampler bibliography: https://antonleykin.math.gatech.edu/math6122spr12/PROJECTS/
8. Verschelde, *Polynomial Homotopy Continuation*: http://homepages.math.uic.edu/~jan/tutorial.pdf
9. Li, Acta Numerica 6 (1997) 399–436: https://doi.org/10.1017/S0962492900002695
10. Li, Math. Intelligencer 9(3) (1987) 33–39: https://doi.org/10.1007/BF03023953
11. Li, Sauer, Yorke, *The Cheater's Homotopy*: https://doi.org/10.1137/0726080
12. Huber & Sturmfels, Math. Comp. 64 (1995) 1541–1555: https://doi.org/10.1090/S0025-5718-1995-1308452-6
13. Lee, Li, Tsai, *HOM4PS-2.0*, Computing 83 (2008): https://dlnext.acm.org/doi/10.1007/s00607-008-0015-6
14. Wampler, *Software*: https://academicweb.nd.edu/~cwample1/Software.htm
15. Li, Handbook of Numerical Analysis 11 (2003): https://doi.org/10.1016/S1570-8659(02)11004-0
16. Math Genealogy: https://www.genealogy.math.ndsu.nodak.edu/id.php?id=15593
17. Macaulay2, `endGameCauchy`: https://macaulay2.com/doc/Macaulay2/share/doc/Macaulay2/NumericalAlgebraicGeometry/html/_end__Game__Cauchy.html
18. Sosonkina, Watson, Stewart, ACM TOMS 22(3) (1996) 281–287.
