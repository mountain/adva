# Semantics

Status: active ontology research focus.

Semantics reads certified machine events as reusable semantic words. It does
not infer meaning from a printed symbol alone.

The first proposed bridge is

\[
\operatorname{CloseCircle}(\mathrm{Null})
\Downarrow
\operatorname{Closed}(c,R)
\quad\Longrightarrow\quad
\operatorname{Sem}
\bigl(
\operatorname{CloseCircle}(\mathrm{Null})
\bigr)
=
\mathrm{Universal}[c,R].
\]

Here the closure certificate \(c\) authorizes the reading and \(R\) retains
the residual and reopen history. Open or Unknown machine results introduce no
semantic word.

## Working rules

1. [Triadic Halt Words and Circle Closure](triadic-halt-circle-closure.md)

For one shared typed run \(r\), only the full three-domain halt word closes the
circle:

\[
\mathsf{CircleClosed}(r)
\quad\Longleftrightarrow\quad
\mathsf{HaltSet}(r)
=
\{K,X,t\}.
\]

The six one-domain and two-domain halt words retain one or two open domain
holes and cannot introduce Universal.

## Initial questions

1. Which machine results admit semantic readings?
2. Which closure proof seals a characteristic word?
3. How are scope, observer, source, occurrence, and residual retained?
4. Which substitutions and compositions preserve a certified reading?
5. When may an output residual become an input variable under polarity
   reversal?
6. How does a stronger observer reopen a sealed word without erasing its prior
   use?

The first registered requirement is
[O1: Null = Universal](../axioms/0001-null-equals-universal.md).
