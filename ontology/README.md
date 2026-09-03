# Ontology

Status: experimental research path for ontology programming and requirements on
a future natural-deduction system.

This directory records proposed ontological axioms before they are promoted to
stable Adva syntax, semantics, or implementation. An entry here is a research
demand, not an executable builtin, a registered exact claim, or an
authorization to change the Rust semantic kernel.

## Programme

The working construction path is

\[
\text{open machine}
\longrightarrow
\text{closure proof}
\longrightarrow
\text{sealed characteristic word}
\longrightarrow
\text{certified semantic-symbol program}.
\]

A candidate symbol may be used as a reusable semantic word only after its open
boundaries, scope, residuals, and composition obligations have been closed by
a declared certificate. Reuse must retain a route back to the generating
machine and its proof history.

The first proposed machine-to-semantics bridge is:

\[
\operatorname{CloseCircle}(\mathrm{Null})
\longrightarrow
\mathrm{Universal}.
\]

Here CloseCircle is a future certified machine operation and Universal is its
semantic-side reading. A future natural-deduction system may introduce
Universal only from a checked Closed result; Open and Unknown authorize no such
judgement.

This path is intended to state requirements for a future natural-deduction
system. It does not yet define that calculus.

## Research paths

| path | role | present priority |
|---|---|---|
| [semantics](semantics/README.md) | read certified machine events as semantic words | active |
| [mathematics](mathematics/README.md) | form constructions and proofs over certified words | active |
| [physics](physics/README.md) | form physical quantities only from justified dimension words | active |
| [metaphysics](metaphysics/README.md) | provide the minimal category-type vocabulary | foundational only |

The metaphysical foundation currently introduces

\[
\mathrm{Quality},
\qquad
\mathrm{Quantity},
\qquad
\mathrm{Number}
:
\mathsf{OntologicalType},
\]

with

\[
0:\mathrm{Number},
\qquad
1:\mathrm{Number}.
\]

No arithmetic, truth-value, or physical interpretation is attached to those
two terms at this stage.

## Axiom index

1. [O1: Null = Universal](axioms/0001-null-equals-universal.md)

## Entry discipline

Each proposed axiom should record:

1. its exact surface statement;
2. the types required to make the statement well formed;
3. the judgement or proof rule requested from natural deduction;
4. its declared scope;
5. substitution, composition, and residual obligations;
6. nontriviality tests and counterexample boundaries; and
7. the gate for promotion from an open proposal to a certified semantic word.

No axiom may obtain stable implementation authority merely by being written in
this directory.
