# Golden-ratio operator lift and basis coverage

Date: 2026-09-10. Status: external exact-arithmetic research, with an elementary
algebraic derivation and bounded execution evidence. No native admission.

## Source and dependency boundary

Main was `60b37d8a4c155994acc7207f2feecc1da7cc6441`. This experiment is based on
the **unmerged** PR #179 head `86c85632d78cccdf7b4febafc802e5f946a2d57b`.
Its scalar checker is pinned by SHA-256 in the input contract. Library PR #4
was merged; the consumer retains its reviewed library source commit
`c9fce90d13fe927614a3b9e9e81826b23692e0fe`.

Research 0123's `arithmetic-universality` and `hypothesized-arithmetic-truth`
remain Proposed hypotheses. Research 0090 requires coverage before closure;
its full prefix calibration and the dependent 0092 all-fillings transfer are
still unfinished. Research 0118 distinguishes endpoint equality from transport
history. We apply those disciplines to a different finite algebraic object,
without claiming to finish their native obligations.

The receiving review already compared scalar closure roots with a nonidentity
matrix's characteristic roots. The new question is stronger and precisely
typed: can the actual ordered affine word be interpreted on rational vectors,
and what evidence covers **all translation directions**?

## Frozen question and exact interpretation

The pre-execution [contract](../../experiments/golden_ratio_operator_lift/contract.json)
fixes one word, matrices of dimension two or three, standard basis probes,
exact rational arithmetic, refusal controls, and resource caps.

Let V be a finite-dimensional rational vector space, L an invertible linear
operator, and v a vector. Define a(x)=Lx and b(x)=x+v; capital letters are
their genuine inverses. Composition is conventional: the rightmost letter
acts first. Keep the complete source word

    W = abbbaBAAB.

Set p(t)=t^2-3t+1. The word has the exact interpretation

    W(L,v)(x) = x - p(L)v.

Here is a derivation independent of the execution checks. Applying the word
from right to left gives these successive values:

    x-v
    L^-1 x - L^-1 v
    L^-2 x - L^-2 v
    L^-2 x - L^-2 v - v
    L^-1 x - L^-1 v - Lv
    L^-1 x - L^-1 v - Lv + 3v  (the three b steps)
    x - v - L^2 v + 3Lv.

Consequently W(L,v) is the identity for every v if and only if p(L)=0.
Checking p(L)e_j=0 on every vector of a declared basis is sufficient by
linearity, rather than by extrapolating a finite sample. This is a general
elementary lemma under the stated assumptions; the Python runs are finite
checks of its implementation, not a formal proof assistant certificate.

Laurent polynomials act by substituting an invertible L, and translations
form their additive module. This is the specific interpretation that permits
the lift from the scalar checker. A shared polynomial alone would not do so.
Order still matters in the affine group: a b a^-1 translates by Lv. We do not
replace ordered noncommutative products by a scalar observation.

## Positive and separating witnesses

Take H=[[1,1],[1,2]]. Direct multiplication gives H^2-3H+I=0, so the word
closes on every rational translation vector. H itself is not the identity.
Its characteristic roots are phi^2 and phi^-2, with phi=(1+sqrt(5))/2;
this explains the exact connection with the delivered golden-ratio word.

The fresh-frame instance C H C^-1, C=diag(2,1), equals [[1,2],[1/2,2]] and
has the same annihilating polynomial. The same word is reused with both
standard basis translations and no new search.

| Input | Coverage | Exact outcome |
| --- | --- | --- |
| H | two of two basis directions | ClosedForAllTranslationsByLinearity |
| C H C^-1 | two of two | same result, fresh-frame reuse |
| diag(2,1/2) | two of two | Refuted; residuals (1,0) and (0,1/4) |
| diag(H,1) | first two of three | UnknownCoverage |
| diag(H,1) | all three | Refuted; third residual (0,0,1) |
| zero operator | inverse required | rejected as noninvertible |

For diag(H,1), the residual operator p(L) is diag(0,0,-1). The first two
directions genuinely close. They cannot justify a claim over the larger
space; e_3 supplies a replayable counterexample. Likewise v=0 closes even
for the non-root operator and cannot certify other directions. Duplicate
basis coordinates are rejected rather than counted twice.

The implementation's basis receipt is a helper over internally constructed
standard-basis observations. It is **not** a validator for arbitrary supplied
bases, Boolean claims, or untrusted serialized receipts. Such an interface
would need dimension, rank, provenance, arithmetic, and schema validation.

## Proposed working word: operator-lift

This is a descriptive research word, not a stable Adva vocabulary entry.

- **Action:** interpret the pinned scalar affine word as an action on a
  declared rational vector space and check its polynomial residual there.
- **Input:** word and composition convention, dimension, invertible L,
  translation vectors, and their complete standard-basis coverage.
- **Output:** full ordered word, exact affine matrices and residuals, plus a
  scoped closed/refuted/unknown result. Equality of the affine map does not
  erase its expression or computation history.
- **Applicability:** the specific affine/module interpretation above. With
  p(L)=0 the additive residual is zero and the ordered product is the affine
  group unit. Inverses require invertibility. This is not scalar division by
  zero and does not identify additive zero with a multiplicative unit.
- **Witness:** H and the changed frame; direct homogeneous composition and
  independently evaluated p(L)v agree.
- **Refusal:** singular L, duplicate coverage, or a missing direction.
  A witnessed nonzero residual refutes the universal translation claim.
- **Expansion/replay:** nine explicit affine steps, with the commands below.
- **Residual:** no Rust-owned importer, checked source identity, M6 filler,
  free, Seal, Pascal admission, holonomy, or universal-grammar completeness.

The vector-affine action is distinct from H's Mobius action on H^2. Indeed
H sends i to (3+i)/5. Closure of W on vectors does not make H an identity
hyperbolic isometry or provide a geometric transport connection.

## Execution and costs

One route, zero search candidates. The runner imposes 5 CPU seconds, 256 MiB
address-space limit, a cooperative 9-second cutoff and 20,000 arithmetic work
units; the command adds a 10-second outer timeout. Output is capped at 65,536
bytes. Underlying input dimension is at most three (homogeneous matrices have
one extra row). Bounds cover this fixed experiment, not arbitrary matrices.

The [first evidence](../../experiments/golden_ratio_operator_lift/evidence.json)
records 27 checks passed, 3,774 counted work units, construction/validation
12.214 ms and serialization plus JSON round-trip 0.622 ms. Peak process RSS
was 12,416 KiB (12.125 MiB), measured on Linux, not inferred from file size.
Fresh-frame construction/validation took 0.727 ms within that total.

A second fresh-process [replay](../../experiments/golden_ratio_operator_lift/replay-validation.json)
matched all semantic fields, excluding only timing and RSS measurements.
It took 50.188 ms including interpreter startup, with internal validation
14.886 ms and serialization/round-trip 0.586 ms, and the same peak RSS.
There were zero correction replays. No CI waiting was used for this experiment.
Final file-write time, separate algebra/word-formation time, and total research
and network time were not separately measured. These figures are not an
acceleration comparison or evidence of increased language expressivity.

## Reproduction

Use a checkout containing the pinned parent source and the five new files.
The external standard-library script needs Python on Linux; it does not need
pytest, Rust, or the unavailable source PDF.

```sh
timeout 10s python -S experiments/golden_ratio_operator_lift/replay.py \
  --output /tmp/golden-operator-lift-fresh.json
```

The output path must not exist. To compare the retained evidence with a fresh
output while preserving all mathematical fields:

```python
import json
from pathlib import Path
def semantic(path):
    result = json.loads(Path(path).read_text())
    result.pop('cost')
    for case in result['cases']:
        case.pop('construction_validation_seconds')
    return result
assert semantic('experiments/golden_ratio_operator_lift/evidence.json') == semantic('/tmp/golden-operator-lift-fresh.json')
```

## Practical next boundary

This helps Mingli and subsequent agents reuse a delivered scalar tool on
matrix objects without confusing action types or silently adding directions.
It does not establish Jiamin's real-task benefit or social trust. The next
minimal step is a versioned external receipt validator that binds the declared
dimension, basis and operator to the replayed word, with the missing-third-
direction instance as its rejection test. Native promotion is a later decision.

PR #179 remains unmerged. Its receiving validation improved to 656 selected
tests passing across two invocations (655 initially, then the one missing-
fixture test after fetching its pinned input). Two PDF-dependent tests remain
unrun, and CI's failed jobs still have no usable diagnostic steps. These are
separate integration obligations, not failures of the operator-lift lemma.
