# Historical Distributivity Character Calibration V0

Status: bounded research implementation following
[0078](0078-distributivity-characteristic-dual-read-v0.md) and
[0080](0080-finite-surface-universal-lift-imagination.md).

This note records the first engineering calibration of one reusable and
reopenable distributivity character. The implementation is
`adva.historical_character_research`; the executable pressure tests are in
`tests/python/test_historical_distributivity_character.py`.

The result is intentionally narrower than a logic rule, a Rust equation cell,
a specializer, or a universal-lift theorem.

## 1. Result

The previous checked span

\[
a(x+y)\xrightarrow{\chi_P} ax+ay
\xleftarrow{\chi_Q} ax+ay
\]

is packaged as the research-local record

\[
\sigma_{\mathrm{dist}}
=
(N,C,S,R_P,R_Q,H),
\]

where:

- \(N=ax+ay\) is the exact rational polynomial characteristic;
- \(C\) references the bounded distributivity witness and its checked cores;
- \(S\) restricts reuse to ordered Real inputs, the exact polynomial
  fragment, typed variable permutations, and finite multiplicative contexts;
- \(R_P,R_Q\) retain both complete process residuals; and
- \(H\) records refinement from the polynomial observer to the occurrence
  observer.

The record explicitly sets all of the following to false:

- Rust certificate authority;
- semantic identity;
- program identity;
- equation-cell authority;
- provenance erasure;
- deck transformation; and
- hyperbolic-axis authority.

Thus "character" here means a finite, marked, reusable research presentation,
not a new stable semantic object.

## 2. Typed finite reuse

One instantiation request contains

\[
(\sigma_{\mathrm{dist}},s,c_1,\ldots,c_k,n,\mathrm{fuel}),
\]

where \(s\) is a type-preserving permutation of the three linear variables and
the \(c_i\) are exact nonzero integer multiplicative contexts. For example,

\[
s=(a,x,y)\mapsto(x,a,y)
\]

generates

\[
x(a+y)\rightsquigarrow xa+xy.
\]

At finite depth \(d=k+1\), the generator emits two fresh Lisp programs: one
factored and one expanded. The expanded program performs an explicit
`copy` of the selected factor. Both programs are then compiled, linked,
validated, sliced, observed, and characterized through the existing
Rust-backed machinery.

The evidence records:

- the historical-character label and rule;
- the exact typed substitution and context;
- generated source and SHA-256 digest;
- original checked programs;
- new checked qualified program names;
- the rechecked common exact characteristic; and
- both fresh process residuals.

Every request is finite. The construction accepts an arbitrary finite tuple of
contexts rather than a pre-enumerated depth table, so the rule has no fixed
semantic depth. The tests check depths one through four; they do not infer an
infinite execution, termination theorem, confluence theorem, or universal
computation result from that range.

## 3. What is reused and what is rechecked

The original bounded certificate supplies the rule, scope, and retained
history. It is not rebuilt as a new distributivity theorem at every depth.
Each proposed instance is nevertheless checked again against the exact
polynomial feature. This is necessary because the current instantiator is
Python research code rather than a Rust-certified transformation.

The present factorization is therefore:

\[
\boxed{
\text{finite historical character}
+
\text{typed proposal}
+
\text{fresh Rust checks}
+
\text{instance feature check}.
}
\]

It is stronger than an unchecked host macro because the macro output has no
authority until the checked program and feature obligations pass. It is
weaker than a native certificate-bearing specializer because Python still
constructs the proposal. Moving the transformation rule and its
source-to-residual certificate into Rust remains a promotion gate.

## 4. Reopening under an occurrence observer

For every accepted instance, the polynomial observer sees one common feature.
Refinement to the occurrence observer returns a concrete witness containing:

- distinct checked qualified program names;
- no copy event on the factored side;
- at least one exact copy event on the expanded side;
- both complete occurrence-ID lists;
- the residual operation-profile differences; and
- the unchanged common characteristic.

Therefore reopening has the form

\[
\operatorname{Reopen}_{Q_{\mathrm{poly}}\to Q_{\mathrm{occ}}}
(\sigma_{\mathrm{dist}}[s,c])
=
(\omega_{\mathrm{copy}},R_L,R_R,N_{s,c}).
\]

It preserves two simultaneous judgments:

\[
\boxed{
\text{the polynomial law remains reusable},
\qquad
\text{the checked programs remain different}.
}
\]

Reopening is not inverse execution and does not reconstruct erased history:
the history was never erased.

## 5. Pressure-test matrix

| case | expected result | observed V0 result |
|---|---|---|
| original proved calibration with both residuals | create character | `Created` |
| fresh typed variable permutation | new checked instance | `Instantiated` |
| depths one through four | finite reuse with no semantic depth cap | `Instantiated` |
| occurrence-observer refinement | recover copy/history difference | `Reopened` |
| drop either residual | refuse sealing or reuse | `NotRepresentable` |
| source-quotient closure | refuse absent right to forget | `NotRepresentable` |
| wrong value type | refuse typed substitution | `NotRepresentable` |
| unsupported context operation | refuse fragment widening | `NotRepresentable` |
| degree budget below two | refuse characteristic | `NotRepresentable` |
| zero fuel | preserve search boundary | `FuelExhausted` |
| polynomial observer without refinement | do not fabricate reopening | `NotRepresentable` |

These outcomes deliberately do not use `Refuted` for malformed,
out-of-scope, or exhausted requests.

## 6. Red-team conclusions

### Supported

The finite distributivity observation can be retained as one historical
record, proposed in fresh typed contexts, rechecked on newly allocated Rust
program identities, and reopened under a stronger observer without losing its
original or instance residuals.

The experiment also gives a precise finite-to-potentially-unbounded form:

\[
\text{one finite marked rule}
+
\text{a constructor accepting every finite depth}
\neq
\text{a pre-enumerated finite table}.
\]

### Not supported

The experiment does not show that:

- the two feature maps are invertible;
- \(\chi_Q^{-1}\chi_P\) is defined;
- the character is a loop, braid, deck word, or hyperbolic translation;
- source equality authorizes occurrence contraction;
- the generated pair is one program;
- polynomial equality creates an equation cell;
- Python has semantic authority;
- arbitrary polynomial substitutions are covered;
- the instantiator is itself an Adva program;
- learning and proof are a strict self-duality; or
- the mechanism is a universal computer.

The `SOURCE_QUOTIENT` negative control is important. A coarse source
projection may close a relation in the earlier connector calibration, but it
still lacks a right-to-forget witness here and is rejected.

## 7. Remaining gap

The principal missing piece is no longer "can one feature be reused?" It is:

> Can typed instantiation itself become a Rust-owned,
> certificate-bearing residual transformation whose source-to-residual map
> composes, while keeping the historical character reopenable?

That is the proper bridge from this calibration to Phase 1 observer
specialization. A second gap is richer exact substitution: the current V0 uses
linear variable permutations and multiplicative integer contexts so that copy
remains explicit and the polynomial scope is decidable.

Only after those gaps are resolved should the geometric Stage D question from
0080 be reopened. The current noninvertible normalization span still supplies
no marked lift witness and therefore no deck transformation.
