# The boundary of the $A_3$ permutohedron in two reduced-expression paths

*Research note · 21 November 2026 · v0.1*

Mingli Yuan (苑明理) provided the research direction. Codex (OpenAI) authored the analysis and checks, contributed under Unknown v0.3, and submitted this note through Mingli Yuan's GitHub account as an authorized proxy.

**中文提要**　最长元的两条改写路径合计恰好扫过截角八面体的六个方形面和八个六边形面。给每次改写对应的面定向，再取两条路径之差，所得是整个边界球面的基本链。

The $A_3$ Zamolodchikov relation compares two composites of local moves between reduced expressions of the longest element. Each such local move also sweeps a square or hexagon in the $A_3$ permutohedron. Using this correspondence, the difference of the two directed paths below is exactly the oriented boundary of the permutohedron, with multiplicity one on every face. The calculation gives a cellular description of the relation and a finite check for the proposed $Q_4/M_6$ coherence in Adva.

## Two kinds of graph

Write $s_1,s_2,s_3$ for the adjacent transpositions acting by swaps of positions in a one-line permutation. Let $P$ be the $A_3$ permutohedron, combinatorially a truncated octahedron. Its vertices are the 24 permutations. At the vertex $w$, the three incident edges lead to $ws_1,ws_2,ws_3$. For a coordinate realization we can label $(w^{-1}(1),\ldots,w^{-1}(4))$ by $w$. A two-face is a coset of a rank-two parabolic subgroup. The squares encode the relation $13\leftrightarrow31$ and the hexagons encode either $121\leftrightarrow212$ or $232\leftrightarrow323$. We call these types $Q_4$ and $M_6$, respectively, following Adva's terminology.

Let $\Gamma$ be the reduced-expression graph for $w_0=4321$. Here a vertex is a six-letter reduced expression, viewed as a shortest edge path in $P$ from $1234$ to $4321$. An edge of $\Gamma$ is a replacement of one consecutive block by the other side of one of the three displayed rank-two relations. Along this replacement the two shortest paths agree away from the rank-two face. Within that face they traverse its two boundary arcs from the same start to the same end. This gives a face of $P$ for each edge of $\Gamma$.

## The signed sweep

For a reduced expression $u$, let $G(u)$ be its oriented gallery chain in $C_1(\partial P;\mathbb Z)$. For a directed rewrite $u\to v$, orient the corresponding face $F(u,v)$ so that
$$
\partial F(u,v)=G(v)-G(u).
$$
For a path $\gamma$ in $\Gamma$, write $F(\gamma)$ for the sum of its directed faces.

Consider the following two paths. In the table $Q_{ab}$ is the square whose first two positions contain the unordered pair $\{a,b\}$. The hexagon $H_{12}(d)$ has $d$ in the last position and $H_{23}(d)$ has $d$ in the first position. These labels identify all six squares and eight hexagons. The face table was obtained by independent enumeration of the adjacent-swap galleries.

| Path $L$ | Face | Path $R$ | Face |
|---|---|---|---|
| $121321\to212321$ | $H_{12}(4)$ | $121321\to123121$ | $Q_{23}$ |
| $212321\to213231$ | $H_{23}(3)$ | $123121\to123212$ | $H_{12}(1)$ |
| $213231\to231231$ | $Q_{13}$ | $123212\to132312$ | $H_{23}(2)$ |
| $231231\to231213$ | $Q_{34}$ | $132312\to132132$ | $Q_{24}$ |
| $231213\to232123$ | $H_{12}(2)$ | $132132\to312132$ | $Q_{12}$ |
| $232123\to323123$ | $H_{23}(1)$ | $312132\to321232$ | $H_{12}(3)$ |
| $323123\to321323$ | $Q_{14}$ | $321232\to321323$ | $H_{23}(4)$ |

The labels can be read from the permutation after the prefix preceding the rewritten block. For example, $212321\to213231$ replaces $232$ by $323$ after the prefix $21$. The prefix reaches $3124$, so the block rearranges the last three positions with $3$ fixed in the first. The corresponding face is $H_{23}(3)$.

**Proposition.** $F(L)-F(R)$ is the fundamental cellular chain of $\partial P$, up to the overall choice of orientation.

**Proof.** The boundary telescopes along each path. Both paths go from $121321$ to $321323$, so $\partial(F(L)-F(R))=0$. The table shows that its coefficient on every face is $+1$ or $-1$. Since $\partial P$ is a sphere and has no three-cells, its cellular two-cycles are integral multiples of the fundamental cellular chain. The coefficients force the multiple to be $+1$ or $-1$. $\square$

## Which loops does the sweep detect?

Two rewrites on disjoint intervals of a word commute as changes of the gallery. Each rewrite sweeps the same signed face whichever of the two is performed first. For the later block, the group element reached by the preceding prefix is unchanged by the earlier rewrite. Consequently the boundary loop of a disjoint square maps to the zero two-chain.

In this case $\Gamma$ has 16 vertices and 18 edges. Its 10 commuting edges form eight connected components. There are four singleton components, two single edges, and two squares. All of the eight remaining edges are long braid moves. Contracting the commuting components gives a single octagon. One can check these counts by testing the $3^6$ words of length six for product $4321$, then applying each of the three block replacements at every consecutive position. For a direct check of the quotient, the eight components have the following representatives in cyclic order:
$$
121321,\ 212321,\ 213231,\ 232123,\ 321323,\ 321232,\ 132312,\ 123212.
$$
The two four-element components are the disjoint squares, with cyclic vertex lists
$$
(213231,231231,231213,213213)
\quad\text{and}\quad
(132312,132132,312132,312312).
$$

Writing $S_1,S_2$ for these square loops, the signed sweep therefore induces an isomorphism
$$
\frac{H_1(\Gamma;\mathbb Z)}{\langle [S_1],[S_2]\rangle}
\;\xrightarrow{\ \sim\ }\;
H_2(\partial P;\mathbb Z).
$$
Indeed, the domain is generated by the remaining octagon, and the proposition sends one lift of that generator to a fundamental class.

## Comparison with Soergel calculus

Elias and Williamson describe $\Gamma$ and its disjoint squares in §§1.4.3 and 4.2 of *Soergel calculus*. Their $A_3$ diagram has boundary words $121321$ and $321323$ and follows the two directed routes after commuting moves are contracted. In the diagrammatic Hecke category, equation (5.10) identifies the corresponding composites of the generating vertices. The sweep above computes the cellular boundary associated with the two routes. It works with oriented chains and does not require treating the six-valent Bott–Samelson morphisms as invertible. [Elias and Williamson, *Soergel calculus*](https://doi.org/10.1090/ert/481)

The existing Adva model supplies the finite $TO_{24}$ envelope and its $Q_4/M_6$ face occurrences. The signed sweep singles out two explicit sequences of face moves on that envelope and determines their full cellular boundary. The remaining question for Adva is whether those two pastings admit a common typed comparison while retaining the individual step occurrences. That requires a rule for composing the relation witnesses and checking the resulting boundary in the target category. [Adva Research 0103, fixed revision](https://github.com/mountain/adva/blob/8fc38427f2a479b4e8e84802e1873cff14d54566/docs/research/0103-cell-carrier-view-relation-machines.md)

## References

- Ben Elias and Geordie Williamson, *Soergel calculus*, Representation Theory **20** (2016), 295–374. See §§1.4.3 and 4.2, Example 4.13, and equation (5.10). [Journal DOI](https://doi.org/10.1090/ert/481) · [arXiv:1309.0865](https://arxiv.org/abs/1309.0865)
- Adva, *Cell–Carrier–View Relation Machines*, Research 0103, revision 8fc38427f2a479b4e8e84802e1873cff14d54566. [Research note](https://github.com/mountain/adva/blob/8fc38427f2a479b4e8e84802e1873cff14d54566/docs/research/0103-cell-carrier-view-relation-machines.md)
