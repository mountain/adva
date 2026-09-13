# Pascal's normalized witness: an explicit commutation boundary

Status: **external exact algebraic certificate, independently replayed** for
one pinned coordinate presentation. No native Q4 filler, M6 coherence,
Pascal import, geometry successor or Seal is constructed. The geometry growth
obligation remains Open.

Authored by ChatGPT (OpenAI). Submitted through Mingli Yuan's GitHub account
as an authorized proxy. Mingli supplied the Pascal / Q4 / ACS research
question; ChatGPT supplied this algebraic derivation, implementation and
checks. Account use is not personal review or endorsement.

## Question and fixed input

The base is `60cb94780f6ac95aa6badcf6b74fa19172d957b2`, which adds
[Research 0181](0181-wu-elimination-on-plane-incidence.md). The Pascal task
and witness are the original two files in the `adva-library` submodule at
`9261194ba13a256fc1b761d7ffc25cd3d025224d`. Their byte hashes are in the
[run contract](../../experiments/pascal_commutator_certificate/contract.json).
No source byte, submodule pointer, catalog policy or growth obligation is
changed.

The question is which parameter commutations the **fixed normalized
polynomial presentation** needs. Work in the free associative algebra
`Z<d,e,f>`, with unity and central integer coefficients. Associativity,
distributivity and additive cancellation are imported algebraic laws.
Commutation of `d,e,f` is not silently imported.

The six supplied points are

\[
A=(1,0,0),\quad B=(0,0,1),\quad C=(1,1,1),\quad
D=(1,d,d^2),\quad E=(1,e,e^2),\quad F=(1,f,f^2).
\]

Read every supplied coordinate expression in its written multiplication
order. Incidence uses **line coefficients on the left**:
`l_0*p_0 + l_1*p_1 + l_2*p_2`. This is a declared algebraic lift of the
existing scalar presentation, not a proposed projective geometry over an
arbitrary noncommutative ring. In particular, no division, invertibility,
nondegeneracy, or general-conic coordinate transport is inferred.

## Exact result

There are 27 equations: six conic equations, twelve endpoint/line incidences,
six constructed-point/line incidences, and three Pascal-line incidences.
Twenty-three are already zero in the free associative algebra. The other
four have the following exact residuals, with `[a,b]=ab-ba`:

| Fixed equation | Residual before imposing commutativity |
| --- | --- |
| D lies on DE | `[d,e]` |
| E lies on EF | `[e,f]` |
| Z lies on FA | `[d,f]` |
| Z lies on the supplied Pascal line | `[d,e](1-f) + (1-e)[d,f]` |

Consequently, for every unital associative ring and every assignment of
`d,e,f` in it,

\[
\boxed{\text{all 27 fixed equations vanish}
\quad\Longleftrightarrow\quad
[d,e]=[d,f]=[e,f]=0.}
\]

Necessity is witnessed by the first three rows. For sufficiency, substitute
the three zero commutators into the fourth row; the remaining 23 residuals
are identities. The universal algebraic statement follows from these exact
identities, not from a finite sampling argument. Its scope is this fixed
system, not every formulation of Pascal's theorem.

There is a useful source-order correction. The witness also displays

\[
de(1+d-f)-d(de+e+f-ef)+df=d[e,d].
\]

That expression moves a line coefficient past `d` relative to the literal
left-coefficient incidence. Both vanish after commutativization, but they
are different free polynomials. The certificate keeps the display as a
28th, auxiliary equation; it never substitutes it for the actual `Z:Pascal`
residual. An explicit negative control rejects that substitution.

## What this says about Q4, M6 and ACS

[Research 0111](0111-group-neutral-operations-and-q4-m6-relation-profiles.md)
keeps Q4's interchange profile `ab => ba` distinct from M6's braid profile
`aba => bab`. The calculation above gives a concrete algebraic interface
for the former: under the left regular action `L_a(x)=ax`, the two length-two
paths have difference

\[
(L_aL_b-L_bL_a)(x)=[a,b]x.
\]

They agree for all `x` iff `[a,b]=0`, by evaluation at unity. Thus this
Pascal presentation identifies **three explicit candidate square-filling
obligations**. Mapping them to native Q4 cells still requires typed
boundaries and source/occurrence/history-preserving derivation certificates.
An algebraic identity or a drawn square does not supply those certificates.

The generator chooses one deterministic adjacent-swap route. It does not
compare alternative swap histories or construct the coherence between
them, so it establishes no identification with the repository's M6 cell.
The number eight below counts commutator summands, not native cells or a
proved minimum.

The ACS comparison uses the distinction already visible in
[`aeg-paper`, Paper I, ACS section](https://github.com/mountain/aeg-paper/blob/609ac96b4df802a8a4a6c4079c43c2fae466bc3a/paper-1/sections/08-acs-torsion.tex),
and the older [flow](https://github.com/mountain/aeg-paper/blob/609ac96b4df802a8a4a6c4079c43c2fae466bc3a/notes/thermodynamics-and-renormalization/02-aeg-flow-and-renormalization-en.tex),
[iteration](https://github.com/mountain/aeg-paper/blob/609ac96b4df802a8a4a6c4079c43c2fae466bc3a/notes/thermodynamics-and-renormalization/04-renormalization-iteration-examples-zh.tex),
and [contact](https://github.com/mountain/aeg-paper/blob/609ac96b4df802a8a4a6c4079c43c2fae466bc3a/notes/thermodynamics-and-renormalization/07-contact-algorithmic-thermodynamics.tex)
notes: charge totals and ordered evaluation carry different information.
The current ACS evaluation includes the path term

\[
\nu_x(\gamma)=e^{M_\gamma}
\left(x+\int_{C_\gamma}e^{-M}\,dA\right).
\]

The checked negative control takes `A(x)=x+1`, `M(x)=2x`. Both orders have
the same totals `(A_total=1, exp(M_total)=2)`, but `M(A(x))=2x+2` and
`A(M(x))=2x+1`. Their exact affine matrix difference has translation one.
For general `A_p` and `M_q(x)=e^q x`, that defect is `p(e^q-1)`.

This supports a specific research direction: retain the residual discarded
by a commutative observation and prove when it vanishes. It does not prove
that ACS histories commute, that charge totals determine evaluation, or
that a renormalization equivalence has already been constructed. Comparing
different decompositions of the same renormalization map must likewise
retain their histories and chosen observer; the present run constructs no
renormalization operator or fixed-point result.

## Certificate, independent replay and controls

The [generator](../../experiments/pascal_commutator_certificate/generate.py)
retains words in their written order and emits identities

\[
P=\sum_i c_i u_i(a_i b_i-b_i a_i)v_i
\]

by telescoping adjacent inversions. It checks that the remaining commutative
normal form is zero. The separate
[checker](../../experiments/pascal_commutator_certificate/check.py) imports
neither the generator nor SymPy. It reconstructs all 28 expressions from
the pinned original bytes, distributes them into signed ordered words,
expands each certificate summand and compares coefficients. The checker
never reorders factors. Each used pair must be explicitly allowed.

This independence is implementation separation, not a second formal proof
kernel: both paths trust CPython integers, its AST parser, and JSON input
handling, and both implement the same stated incidence convention.

The retained [execution record](../../experiments/pascal_commutator_certificate/evidence/execution.json)
records 3 successful children, 0 retries, 0.131504 seconds through checking,
0.109141 child CPU seconds, and peak child RSS 11,392 KiB on Linux. The
9,506 retained bytes include the execution checkpoint. The timing field
stops before writing that checkpoint; it is not advertised as end-to-end
serialization time. Per-child CPU, address-space and output limits and
supervised wall deadlines are declared in the contract. Integration replay
also has an outer deadline covering the checkpoint.

The [check](../../experiments/pascal_commutator_certificate/evidence/check.json)
validates 8 summands across 28 expressions. The
[controls](../../experiments/pascal_commutator_certificate/evidence/controls.json)
reject all 12 altered certificates: deleted summand, changed sign, forged
variable, omitted equation, duplicate equation, wrong declared source hash,
Boolean coefficient, each of the three missing pair assumptions, forged
zero residual, and substitution of the distinct auxiliary lift. The affine
ACS counterexample is checked with exact integer matrices.

The [regression tests](../../tests/python/test_pascal_commutator_certificate.py)
bind retained bytes to the checked source code and claim, replay to a fresh
directory, compare deterministic outputs byte for byte, and reject an
actual source-byte change even when the certificate still declares the
correct hash. The separate
[regression contract](../../experiments/pascal_commutator_certificate/regression-contract.json)
bounds that one integration run. Tests do not overwrite frozen evidence.

From a checkout with the pinned `adva-library` submodule initialized:

```sh
python experiments/pascal_commutator_certificate/run.py /tmp/pascal-fresh-evidence
timeout 140s python -m unittest discover -s tests/python -p test_pascal_commutator_certificate.py -v
```

The output directory must be new. The experiment requires only Python's
standard library and POSIX process limits. If the submodule is absent,
the test suite explicitly skips the two source-dependent tests; the
experiment itself refuses missing inputs. No skip counts as proof replay.

## Correction to Research 0181's evidence interpretation

The new Wu experiment is relevant, but inspection of its pinned
[`calibration.py`](../../experiments/wu_elimination_geometry/calibration.py)
reveals limits stronger than its initial summary reports. This is a source
audit, not a new execution of that experiment. Its original code, numbered
note and evidence remain as the historical record; the live claim registry
is corrected to point here.

1. **The reported Groebner cross-check is not independent.** After reducing
   hypotheses and conclusion by the same chain, the empty-hypothesis branch
   merely retests that same pseudo-remainder. The nonempty branch constructs
   a Groebner basis with the target remainder itself included as a generator,
   making its membership tautological. The unused `in_ideal` helper has the
   same problem. Agreement is not an independent validation of Wu reduction.
2. **Ceva's initial is misreported.** The recorded pivot is
   `-2*e*f*t + e*f + e*t - e + f*t`, with main variable `t`. Its initial is
   `-2*e*f + e + f`. The code uses `Poly(pivot, *order).LC()` and reports `-2`,
   which is the coefficient of the multivariate leading monomial, not the
   required coefficient polynomial in the main variable. This correction
   concerns the pseudo-division side condition; it does not refute Ceva.
3. **The random checks do not have the stated coverage.** Ceva returns no
   substitution and is skipped. Pappus constructs names `p1x,...,q3x`, while
   its polynomial uses `p1,...,q3`; substitution therefore binds none of
   those parameters, hidden by the true polynomial already being zero.
4. **The determinant degree depends on the encoding.** The homogeneous
   conic determinant in Research 0128 has degree twelve in point coordinates
   and degree six in its quadratic Veronese entries. In the affine chart
   with columns `x^2,xy,y^2,x,y,1`, it has degree eight in the point
   coordinates. Calling it a sextic without naming the entries obscures
   that distinction.

These findings do not by themselves invalidate the observed Pascal
pseudo-remainder zero. They do withdraw the stronger claim that the old
run independently cross-validated its elimination and correctly recorded
every side condition and sample. A repaired Wu computation would need its
own finite contract, an independent check from the original hypotheses
without inserting the target, and preserved old evidence.

## Next precise obligation

The three integration tests passed in 0.191 seconds, with no skips; their
[log](../../experiments/pascal_commutator_certificate/regression.log) is
retained. The full Rust/Python repository suite was not run in this partial
checkout. No stable semantic code is changed.

The next native bridge is now explicit: represent one residual, for example
`D:DE = [d,e]`, with ordered source and occurrence data, and require an
actual checked interchange cell to discharge it. Refuse discharge when
that cell is missing, and retain the ACS affine counterexample as a case
where same-charge observation cannot authorize interchange. Promotion of
that interface remains a separate design and native-checker task.
