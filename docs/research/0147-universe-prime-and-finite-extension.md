# Research 0147: Universe(Prime) and finite prime extension

Status: expression feasibility audit, classical external proof, proposed
Adva question, and bounded Python calibration. The native theorem checker
and Rust prime-certificate adapter are not implemented by this study.

## The working word and the mathematical cut

Mingli Yuan proposes `Universe` to express the infinitude in the classical
prime-number question. In this note the typed working expression is

    Universe(Prime)

with the specific meaning

    for every finite list P of natural-number primes,
    there exists a natural-number prime q not in P.

This is a proposed interpretation of the user's name, not a new native
builtin or a definition of the physical universe. In the natural numbers
it is equivalent to `forall B : Nat, exists q : Nat, q > B and Prime(q)`.
The finite-list version avoids requiring a growing numerical maximum in
each local step: a prime outside a given list need not exceed its maximum.
For example, the construction on `[3]` can return 2.

An infinite assertion can have a finite formula and a finite proof. The
missing engineering boundary is therefore not infinite running time for
the theorem. It is the syntax, proof rules and checked interpretation of
the quantifiers and natural-number reasoning. One fixed fuel allowance
also cannot complete every concrete input of unbounded size.

## What the inspected repository can express

Main remains `24d7275971cfd61fabc3270ac2a71b79df377598`. Drafts #142--#146
remain unmerged. This proposal is stacked on #146 at
`67c1173295a2289a8973dd37134e48808dcace6c` and changes no stable API.

| Existing resource | Useful part | Present limit |
| --- | --- | --- |
| `crates/adva-witness/src/arithmetic.rs` | `BigInt`, `PolynomialV0`, `ExactExprV0`, exact sum/product/evaluation | These are not a general Nat/Prime theory or a quantified theorem checker |
| `crates/adva-lisp/src/operation.rs` and ADR 0035 | Bounded native compilation/evaluation and certificates | Current `adva run` profile uses `Real/f64`; the registry has no native Prime/divisibility/Nat-quantifier family |
| Research 0094 | Finite checked proof trees, right-linear-implication derivability and retained histories | Its formula grammar is atoms and right implication; it explicitly adds no quantifier rules or stable proof AST |
| ADR 0020 / Research 0110 | Neutral carrier references, compute/verify/learn transition frames, persistence | A well-formed stored frame does not execute an arbitrary method or verify the meaning of a new predicate |
| Research 0123 | Proposed arithmetic-universality and hypothesized-arithmetic-truth resources | Registering a word does not prove an arithmetic theorem |

The source audit supports a specific conclusion: the current admitted
native language/checker does not directly express and verify the whole
`Universe(Prime)` theorem. It can support pieces of the exact finite
construction and a versioned research declaration. This is not a proof
that Adva can never acquire an appropriate representation.

One existing guard matters here: `ExactExprV0::evaluate_guarded` rejects
zero at every node. The positive product-plus-one construction respects
that guard, including the empty product 1. Divisibility checks, however,
must allow a remainder of zero. They must not be routed through that
nonzero-expression guard or confused with multiplicative-unit admission.
The proposed adapter compares exact integers under its own declared
divisibility contract; it does not reinterpret the old guard.

The [question proposal](../../adva-library/prime-universe/question.adva)
retains the universal finite-list question and its finite witness interface.
Its `adva.prime-universe.question.proposed` schema is intentionally labelled
unsupported by the native dispatcher. The `.adva` suffix alone supplies no
execution or proof authority. It is not passed to `adva run` or `learn`.

A separate [fixed product program](../../adva-library/prime-universe/finite-product-program.adva)
uses the existing `adva.run.program.research` envelope and PSC0 add/multiply
surface to express `(2*3*5)+1`. Its four Real inputs are p1, p2, p3 and unit;
all are used once. This is an explicit finite program representation in the
existing language, not the proposed quantified question format. Native
execution is **NotRun** because the runtime is unavailable. These particular
small arithmetic values are exactly representable in binary64, but a
potential Real evaluation still does not check Prime or Universe(Prime).

## Classical proof and its explicit dependencies

Take any finite list P of primes. Define M as the product of its entries,
with empty product 1, and N = M + 1. Thus N >= 2.

The finite set of divisors d with `2 <= d <= N` is nonempty because it
contains N. Let q be its least member. If q were composite, a proper factor
a with `1 < a < q` would divide N, contradicting minimality. Hence q is
prime. If q appeared in P, it would divide M as well as M+1 and therefore
divide 1, which a prime cannot do. Consequently q is outside P.

This argument applies to an arbitrary finite prime list; if all primes
formed one finite list, it would produce a prime outside it. This proves
the classical infinitude statement. The argument needs natural-number
arithmetic, finite products, least-element reasoning and elementary
divisibility. It does not require unique factorization. To recover the
bounded-number formulation, take the finite list of primes at most B.

This is an external mathematical proof written in the research note.
The new Python run verifies concrete witnesses, not this universally
quantified argument in the current Adva logic. No new universality theorem
is inferred from the classical result.

The crucial witness relation is

    N = product(P) + 1
    N = q * k
    Prime(q)
    q not in P.

N itself need not be prime. The small counterexample is P=[3], N=4. The
consecutive-prime example is P=[2,3,5,7,11,13], N=30031=59*509. Both still
give a valid prime outside the original list.

Divisibility uses an exact natural-number witness k. Replacing it with the
field quotient N/q would make every nonzero q appear acceptable. The
remainder-one statement `N mod p = 1` for p in P is not native guarded M1
or an M6 filler. No inversion of zero or identification of histories is
performed here.

## Three representations and implementation order

| Side | Proposed input and output | Admission boundary |
| --- | --- | --- |
| Adva | Typed question `Universe(Prime)`, one finite P, fuel, candidate/certificate references and residuals | A declaration, a successful finite instance and a checked universal proof are separate statuses |
| Python | Finite P and search budget -> exact N, candidate q, cofactor k, search trace or Unknown | It may propose and run external arithmetic; it allocates no native semantic identities |
| Rust | Versioned P/N/q/k and explicit prime/divisor evidence -> a checked finite certificate or refusal | Reuse existing exact integer infrastructure; add a scoped verifier before granting native authority |

These are responsibilities for this task, not intrinsic identities of three
subjects. An arbitrary Rust library is no more automatically admitted than
an arbitrary Python library. The existing Rust semantic boundary decides
which certificate-bearing operation can be admitted.

The implementation order is deliberately finite:

1. Retain the proposed question and run the bounded external construction.
2. Specify and implement a versioned Rust finite prime-certificate adapter
   over exact integers, with input size, checking fuel and overflow limits.
   The small profile could use bounded integers; later exact large integers
   require explicit bit-size and work budgets. Existing BigInt infrastructure
   is useful but does not remove those limits.
3. Connect that checked finite result to an admitted Adva task/result
   schema. Maintain old library versions and mark any new operation as a
   versioned extension; do not relabel the current Real entry as exact Nat.
4. Choose the proof boundary for the full theorem. Either introduce the
   justified Nat/list/quantifier/proof rules, or reference an independently
   verified external proof through an explicit import contract. An imported
   reference is not yet native verification; the chosen proof checker and
   its accepted statement must be accounted for.

Only the first step is executed here. The environment has Python and
`timeout` but no `adva`, `cargo` or `rustc`. No native run or Rust compilation
is claimed. The new question can guide work without pretending these gaps
are already solved.

## Frozen finite calibration

The [run contract](0147-prime-universe-contract.json) fixes eight cases
before execution. Input lists are sorted, unique, length at most six, with
entries from 2 through 13; the empty list is allowed. The product-plus-one
value is bounded by 65535 and all arithmetic is exact. The producer searches
for a divisor up to `isqrt(N)`, while the checker separately reconstructs
the product and checks possible divisors of q from 2 through q-1, stopping
at a refutation or its fuel limit. Input primality is checked too.

The fixed cases are the main list `[2,3,5]`, new list
`[2,3,5,7,11,13]`, composite successor `[3]`, empty list, zero search fuel,
forged q=1, falsely proposing the whole composite successor as prime, and
an invalid prime-list input `[4]`. There is one serialized main-witness
recheck. The generator and checker use different traversals but share the
Python runtime and integer arithmetic.

The budget is 2000 global logical units, at most 256 divisor trials and one
second per search, 1024 verification units per checker call, five seconds
for the invocation, 256 MiB address space and 262144 bytes per file. Search,
checking and saving are charged. A new execution does not refill any prior
task ledger. No scalability or speedup claim is made.

Reproduce from this branch into a new directory:

```sh
timeout 5s python3 experiments/prime_universe/finite_witness.py --contract docs/research/0147-prime-universe-contract.json --output /tmp/adva-0147-new
```

## Results and continuation

One bounded execution completed on 2026-09-06; all eight expected statuses
and the serialized main-witness recheck matched. There was no execution
repair replay. The retained cases are:

| Input/control | N | q, k | Result |
| --- | --- | --- | --- |
| `[2,3,5]` | 31 | 31, 1 | FiniteExtensionVerified |
| `[2,3,5,7,11,13]` | 30031 | 59, 509 | FiniteExtensionVerified; fresh instance |
| `[3]` | 4 | 2, 2 | FiniteExtensionVerified; N is composite and q is smaller than 3 |
| `[]` | 2 | 2, 1 | FiniteExtensionVerified; empty-product boundary |
| Main, zero search fuel | 31 | none | Unknown; divisor interval `[2,6)` remains unsearched |
| Main, forged q=1 | 31 | 1, 31 | Blocked |
| Fresh, falsely proposing q=N | 30031 | 30031, 1 | Blocked; divisor 59 refutes primality |
| `[4]` as a purported prime list | 5 | 5, 1 | Blocked; the input predicate fails |

Actual logical cost is **548 of 2000**: construction 39, search 126,
verification 371, serialization 12. The serialized main recheck is included
in these totals. Measured phases are construction 0.035 ms, search 0.082 ms,
verification 0.247 ms and serialization 0.513 ms. Reuse timing 0.291 ms
overlaps the fresh case and main recheck phases; it is not an additional
independent cost. The outer supervisor measures **32.419 ms** including
startup and all three output writes. Peak child RSS is **11,136 KiB
(10.875 MiB)**. Research, source authoring and network time are unmeasured
and excluded. File sizes are not RAM measurements.

The [report](0147-evidence/report.json), [phase costs](0147-evidence/costs.json),
[host costs](0147-evidence/host-cost.json) and
[manifest](0147-evidence/manifest.json) retain the exact contract, witness
traces, divisor coverage, outcomes and source digest. The only implementation
repair was a static type correction before execution: trace entries and
coverage endpoints reject Boolean values masquerading as integers. No
execution retry or scope expansion was performed.

The universal theorem and its proposed name remain separate from finite run
status. This study creates no new publication permission, social acceptance
or native `free` capability.

The next smallest engineering step is the exact Rust finite-certificate
verifier for the retained main and composite-successor examples. The next
logical decision is which quantifier and natural-number proof boundary
`Universe(Prime)` should inhabit. Neither requires changing every existing
library contract at once.
