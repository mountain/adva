# Triadic Halt Words and Circle Closure

Status: working semantic rule for the first circle-closing experiments.

## Relative halt words

Let the three machine domains be

\[
\mathbb D
=
\{K,X,t\}.
\]

For one shared typed run \(r\), define its relative halt set

\[
\mathsf{HaltSet}(r)
=
\{
d\in\mathbb D
\mid
\mathsf{Halt}_d(r)
\}.
\]

The seven nonempty relative halt words are indexed by

\[
H_7
=
\mathcal P(\mathbb D)
\setminus
\{\varnothing\}.
\]

Explicitly,

\[
H_7
=
\{
H_K,
H_X,
H_t,
H_{KX},
H_{Kt},
H_{Xt},
H_{KXt}
\}.
\]

These words must refer to the three domain projections of one shared run. Three
unrelated halting events do not form \(H_{KXt}\).

## Closure criterion

Adopt the working rule

\[
\boxed{
\mathsf{CircleClosed}(r)
\quad\Longleftrightarrow\quad
\mathsf{HaltSet}(r)
=
\{K,X,t\}.
}
\tag{TriHalt-Close}
\]

Thus only

\[
H_{KXt}
\]

is the closed-circle halt word.

For the one-hole-per-domain presentation, the remaining open-hole count is

\[
\#\mathsf{OpenDomainHoles}(r)
=
3-
\left|
\mathsf{HaltSet}(r)
\right|.
\]

Hence:

| relative halt word | halted domains | remaining domain holes | circle status |
|---|---:|---:|---|
| \(H_K,H_X,H_t\) | 1 | 2 | open |
| \(H_{KX},H_{Kt},H_{Xt}\) | 2 | 1 | open |
| \(H_{KXt}\) | 3 | 0 | closed |

The empty halt set is not one of the seven halt words. Its absence from \(H_7\)
does not prove global nontermination; it may also represent an unstarted,
unobserved, or bounded Unknown run.

## Typed terminality

The predicate \(\mathsf{Halt}_d(r)\) must mean that domain \(d\) reached a
declared typed terminal boundary in the shared run. Fuel exhaustion is not a
halt proof. A host function returning, three scalar values being available,
or three unrelated traces ending is not sufficient.

TriHalt-Close is the machine-level circle criterion. A semantic promotion may
require an additional compatibility certificate showing that the three local
terminal boundaries, connectors, sources, occurrences, and residuals form one
global closure.

## Universal introduction

The semantic rule for O1 is therefore refined to

\[
\frac{
\mathsf{HaltSet}(r)=\{K,X,t\}
\qquad
\operatorname{CloseCircle}(\mathrm{Null};r)
\Downarrow
\operatorname{Closed}(c,R)
}{
\Gamma
\vdash_{\mathsf{ND}}
\mathrm{Universal}[r,c,R]
:
\mathsf{OntologicalForm}
}
\quad
(\mathrm{Universal}\text{-I}_{3H}).
\]

No one-domain or two-domain halt word can introduce Universal.

## Residual boundary

Three-domain halt closes the three domain holes. It does not authorize
deletion of the answer residual, source and occurrence history, alternative
fillings, or closure certificate. Those remain in \(R\) or in an explicitly
typed answer boundary.

Accordingly,

\[
\#\mathsf{OpenDomainHoles}(r)=0
\]

does not mean that every residual in every finer observer view is empty.

## Experimental checks

The first bounded fixture should include:

1. all three one-domain halt words;
2. all three two-domain halt words;
3. the one three-domain halt word;
4. one fuel-exhausted run rejected as a halt word;
5. one attempted closure assembled from unrelated run identities and rejected;
6. one \(H_{KXt}\) run whose connector or residual incompatibility blocks
   semantic promotion; and
7. one \(H_{KXt}\) run with a replayable global closure certificate.

These are symbolic, finite, typed checks. Numerical equality of outputs cannot
replace them.
