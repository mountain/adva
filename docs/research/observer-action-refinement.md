# When does a finite observation carry the action?

*Research note · 21 November 2026 · v0.1*

Mingli Yuan (苑明理) provided the research direction. Codex (OpenAI) authored the analysis and checks, contributed under Unknown v0.3, and submitted this note through Mingli Yuan's GitHub account as an authorized proxy.

**Abstract.** A finite observation of a deterministic system may identify states with different observable futures. We construct the coarsest refinement that carries every declared transition, give a sharp bound on the observation horizon needed to compute it, and show that the resulting quotient system is invariant under surjective changes of presentation that preserve the observation and the action. An eight-state example exhibits a nontrivial quotient. A two-symbol observation of the integer shift shows that an infinite carrier can require infinitely many refined states.

**中文提要**

给定有限状态系统及其观察，本文构造使操作能够下降的最粗细化，给出达到稳定所需的最坏观察深度，并证明在保持观察与操作的满射换表示下，所得商系统一致。

## Agreement on the overlap

Let $X$ be a nonempty set of states, $q:X\twoheadrightarrow Y$ an observation, and $F_a:X\to X$ a deterministic transition for each $a$ in a finite alphabet $A$. A transition descends to $Y$ if it has a well-defined counterpart $\bar F_a$ satisfying $qF_a=\bar F_aq$. This holds exactly when

$$
q(x)=q(x')\quad\Longrightarrow\quad q(F_a x)=q(F_a x').
$$

Surjectivity then makes $\bar F_a$ unique. Equivalently, the two pullbacks of $qF_a$ to $X\times_Y X$ agree.

The fibre product is the point of contact with Peter Scholze's *Étale cohomology of diamonds*. Definition 9.1 describes descent data by comparing pullbacks to a double overlap and imposing a cocycle condition on the triple overlap. Proposition 9.7 proves $v$-descent for separated étale perfectoid spaces and for finite étale perfectoid spaces. The finite argument here takes place in sets. It asks how much observation must be added when the two pullbacks disagree. [Scholze, §9, Definition 9.1 and Proposition 9.7, 14 April 2026 revision](https://people.mpim-bonn.mpg.de/scholze/EtCohDiamonds.pdf)

## The canonical refinement

For a word $w=a_1\cdots a_r$, let $F_w=F_{a_r}\circ\cdots\circ F_{a_1}$, with $F_\varnothing=\mathrm{id}$. Define

$$
x\sim_j x'\quad\Longleftrightarrow\quad
q(F_w x)=q(F_w x')\ \ \text{for all } |w|\le j,
\qquad
\sim_\infty=\bigcap_{j\ge0}\sim_j .
$$

Write $Q=X/{\sim_\infty}$, $p:X\twoheadrightarrow Q$, and let $\pi:Q\to Y$ be the map with $q=\pi p$.

**Proposition.** Every transition descends to $Q$. If $r:X\twoheadrightarrow Z$ is any finer observation than $q$ on which every transition descends, there is a unique map $Z\to Q$ factoring $p$ through $r$. When $|X|=n$ and $|Y|=b$, one has $\sim_{n-b}=\sim_\infty$. For each $n\ge2$, the bound is attained for $b=2$ by a single transition that is a permutation.

**Proof.** If two states are $\sim_\infty$-equivalent, applying $F_a$ preserves the equality of all future observations, since the experiment $w$ after $a$ is the word $aw$. Thus $[x]\mapsto[F_a x]$ is well-defined. If $r(x)=r(x')$, every word produces equal $r$-observations by descent and hence equal $q$-observations because $q$ factors through $r$. Thus $r(x)=r(x')$ implies $p(x)=p(x')$, giving the unique factorization.

The depth-$(j+1)$ partition is obtained by grouping states by their present $q$-value and the depth-$j$ blocks of each immediate successor. If two successive partitions coincide, this update rule makes the partition stationary. Every strict refinement increases the number of blocks by at least one. The initial partition has $b$ blocks, and there are at most $n$. Hence depth $n-b$ suffices.

For sharpness, take a cycle of length $n$, with the mark at one vertex and a common unmarked observation at the others. For $0\le j\le n-2$, the vertices whose first forward visit to the mark takes $0,\ldots,j$ steps have distinct observations. The remaining vertices form one block. This yields $j+2$ blocks at depth $j$, so the partition stabilizes at depth $n-2$. $\square$

The construction uses the classical state-equivalence relation of a Moore machine. The formulation emphasizes how a given observation can be refined and how the result depends on the presentation. [E. F. Moore, *Gedanken-experiments on sequential machines*, 1956](https://www.cs.cmu.edu/~cdm/resources/Moore1956-gedanken-experiments.pdf) · [J. Hopcroft, *An n log n algorithm for minimizing states in a finite automaton*, 1971](https://www.cs.cmu.edu/~cdm/resources/Hopcroft1971.pdf)

## Change of presentation

Suppose $u:X'\twoheadrightarrow X$ is a surjection, $F'_a$ acts on $X'$, $uF'_a=F_au$, and $q'=qu$. For every word $w$, induction gives $q'F'_w=qF_wu$. Consequently

$$
x'\sim'_j y'\quad\Longleftrightarrow\quad u(x')\sim_j u(y')
$$

at every depth, and the same holds after intersecting over all depths. The resulting map

$$
X'/{\sim'_\infty}\longrightarrow X/{\sim_\infty},\qquad [x']\longmapsto[u(x')]
$$

is therefore an isomorphism respecting the transitions and the map to $Y$. This also identifies the quotient systems of any two carriers that admit a common surjective presentation preserving the observations and transitions.

For example, take $X=\mathbb Z/4\mathbb Z$, with transition $i\mapsto i+1$ and observation $q(i)=\mathbf 1_{i=0}$. At depth zero, $2$ and $3$ have the same reading, but their successors have different readings. The successive partitions are

$$
\{0\}\mid\{1,2,3\},\qquad
\{0\}\mid\{1,2\}\mid\{3\},\qquad
\{0\}\mid\{1\}\mid\{2\}\mid\{3\}.
$$

On the eight-state carrier $X'=X\times\{0,1\}$, let $F'(i,t)=(i+1,1-t)$ and $q'(i,t)=q(i)$. Projection $u(i,t)=i$ intertwines the transitions. The two presentations yield the same four-state quotient. Its transition is a four-cycle, so the square is distinct from both the transition and the identity.

The output alphabet alone gives no bound on the number of refined states. For the translations $i\mapsto i\pm1$ of $\mathbb Z$, take $q(i)=\mathbf 1_{i=0}$. Given $i\ne j$, translating $i$ to zero separates the two states. At depth $d$, each point of $[-d,d]$ is distinguished and all points outside this interval give the same readings. The number of classes is $2d+2$. The full quotient distinguishes every integer.

## Adva scope

Adva's earlier quotient note tested whether a declared reading descends. On its checked family, the role-set reading yielded the identity while the role-count reading failed. The universal refinement above starts with a failed reading and constructs an adequate observation on the supplied state space. A native application would require a repeatable family of total transitions on a declared reachable carrier. A Goldberg application would require constructing a map between levels and proving that it intertwines the chosen transitions. [Adva, *Independent reproduction of the quotient criterion*](https://github.com/mountain/adva/blob/8fc38427f2a479b4e8e84802e1873cff14d54566/docs/research/observer-quotient-descent-reproduction.md) · [Adva, *Lattice-polar admission*, §§2, 5](https://github.com/mountain/adva/blob/8fc38427f2a479b4e8e84802e1873cff14d54566/docs/research/lattice-polar-and-mirror-boundary.md)
