# Periodic programs before Floquet observations

Status: proposed native-compatible expression profile, with an original external
exact-arithmetic calibration. This is not an implemented native Floquet calculus,
Rust transformation certificate, weather-model replacement, or new claim in the
stable registry. It follows the user's request to express Floquet inside Adva's
addition/multiplication framework before extending forecast interpretation.

## 1. What is primary

The primary carrier is a finite sequence of open programs, their ordered
boundaries, and their graft/source/occurrence histories. An annual coefficient
matrix is an observation of that carrier under additional assumptions.

Use the following as mathematical notation, not new Rust types:

\[
P_m:(\Gamma_m,\Xi_m)\longrightarrow\Gamma_{m+1},\qquad 0\leq m<12.
\]

Here \(\Gamma_m\) is an ordered state interface and \(\Xi_m\) the declared
parameter/forcing interface. Specify which ports are supplied constants, which
vary, which have memory, and which are observed. If a multiplier is produced by
another changing quantity, its input remains active or its producing process
must remain in the graft. Freezing it changes the question.

Supply a type-correct connection for every adjacent boundary, and a declared
same-season comparison between the final and initial boundary schemas. With
these connections included, an annual return program is the chronological graft

\[
\mathcal P_{[0]}=P_{11}\circ\cdots\circ P_1\circ P_0.
\]

This notation means that phase 0 executes first. It retains all internal
operations, explicit sharing, intermediate boundaries, and supplied inputs.
An input used twice requires an explicit copy; equal values never authorize
sharing or identification of occurrences. A repeated seasonal template has
fresh execution occurrences. Repeating a template is not identifying two years'
histories. Any finite multi-year run is unrolled; no cyclic Adva program or
unbounded recursion is being introduced.

A matrix, an eigenvalue, and an endpoint scalar cannot reconstruct this carrier.
In particular, Adva's linear/affine resource discipline is not a claim that
every numerical function expressed by its programs is linear/affine.

## 2. Finite change comes before a first-order reading

Declare a scalar arithmetic chart for the ports where addition and subtraction
are meaningful. Differences are not assumed for arbitrary typed frontiers.
Compare a base execution and a perturbed execution with a correspondence of
their input policies and construction histories. On their arithmetic values,

\[
\Delta(u+v)=\Delta u+\Delta v,
\qquad
\Delta(uv)=u\,\Delta v+v\,\Delta u+\Delta u\,\Delta v.
\]

The last term belongs to the exact finite change. Removing it defines a further
observation; it is not an equality of the full changes or programs. Likewise,
fixed \(c\) gives \(\Delta(cx)=c\Delta x\), while an active multiplier gives

\[
\Delta(cx)=c\Delta x+x\Delta c+\Delta c\Delta x.
\]

Paper 0's one-hole sections fix the other operand: \(z\mapsto z+c\) and
\(z\mapsto cz\) are affine in that selected hole. This is compatible with
nonlinear joint dependence, explicit branching, and richer process histories.
Neither “every multiplication is nonlinear in the selected state” nor “every
A/M process is just a matrix” is a sound reading of those materials.

Process Geometry's rank-transition calibration sharpens this point:
multiplication acts uniformly on an entire family of addition processes, rather
than merely naming one repeated sum. Lowering must preserve the mixed process
relation and its action, not only an endpoint value. The scalar chart below is
one declared external reading; it does not prove that variation commutes with
that rank lowering. The cited positive-integer rank calibration does not itself
admit this note's rational factors as a native extension.

After values/parameters and a phase reference \(\bar x_m\) are declared, write
\(F_m\) for the arithmetic reading of \(P_m\), and define

\[
E_m(h)=F_m(\bar x_m+h)-F_m(\bar x_m),\qquad
d_m=F_m(\bar x_m)-\bar x_{m+1}.
\]

The full, exact anomaly equation is

\[
\boxed{h_{m+1}=d_m+E_m(h_m).}
\]

If the reference is an actual periodic orbit, all \(d_m=0\) and the annual
finite change is \(E_{11}\circ\cdots\circ E_0\). This composition remains
nonlinear in general. If the reference is merely a repeating climatology,
retain the defects and compose \(h\mapsto d_m+E_m(h)\) instead. Periodic input
means do not prove that the process transports one mean into the next.

Here “homogeneous” means omission of an independent forcing/defect in the
selected perturbation equation. It must not be confused with homogeneous
polynomial degree, program resource linearity, or global linear dynamics.

These identities are arithmetic derivations. A native implementation must
certify the paired executions and any rewrite, retaining occurrence distinctions
even when the arithmetic differences vanish. That implementation is still open.

### An exact spectral question without discarding nonlinear terms

Before making a first-degree approximation, one can pose a separate question
directly about a complete annual program and a scalar-valued observer program
\(\psi\): does the declared observation satisfy

\[
\boxed{\psi\circ\mathcal P_{[0]}\;\simeq_Q\;
       D_\mu\circ\psi,\qquad D_\mu(y)=\mu y?}
\]

Here the composites are proposed finite grafts, and \(\simeq_Q\) is a
specified observational relation to be certified, not equality of histories.
The question asks whether a recurring observation of the full nonlinear return
is scaled by \(\mu\). It does not presume \(\mathcal P\) is linear. For a
centered perturbation observer require \(\psi(\bar x_0)=0\) and a nonconstant
observer, so a constant observation is not mistaken for a physical mode.

This route needs a declared observer language, allowed state domain, closure
under grafting, comparison checker, and retained residual when the equation
fails. Equality at a few sampled states is insufficient. No generic pullback
`D*`, eigenobserver type, or finite closure theorem is being installed. These
are prospective exact process-observation eigenrelations, not an assertion
that the classical Floquet theorem applies globally to nonlinear programs.

The quartic example below exhibits a precise closure obstruction. For any
nonconstant scalar polynomial \(\psi\) of degree \(d\),
\(\deg(\psi\circ E_{[0]})=4d\). It cannot equal \(\mu\psi\), whose degree
is \(d\) for nonzero \(\mu\), or which vanishes for zero \(\mu\).
Nor can a finite-dimensional polynomial observation space containing a
nonconstant polynomial be invariant under repeated composition: degrees grow
without bound. This is a degree argument in the external polynomial chart,
not an executed native impossibility certificate. A wider observer language,
local analytic construction, or explicit truncation residual would be needed.
Thus an exact nonlinear spectrum and the first-degree Floquet spectrum below
are distinct research questions.

## 3. How the Floquet observation can arise

For the finite polynomial A/M fragment, introduce a formal observer parameter
\(\epsilon\) and tag the chosen input change as \(\epsilon h\). This tag is
observer metadata, not a native source identity or a new wire type. Exact
expansion gives

\[
E_m(\epsilon h)=\epsilon L_m(h)+\sum_{k\geq2}\epsilon^k Q_{m,k}(h).
\]

At a multiplication node, the coefficient of \(\epsilon\) is
\(uL_v+vL_u\); higher coefficients include the cross terms. Addition merges
coefficients. Structural induction gives a first-degree expression linear in
the tagged perturbations, while its coefficients may be nonlinear expressions
in the base state and parameters. This is a coefficient-reading derivation;
it does not assume that the original program is linear. Keep the original
expression and higher-degree residual alongside this reading.

For nonpolynomial operations a separately justified variation rule, domain,
regularity assumption and remainder bound are required. Merely renaming an
ordinary derivative does not supply them. The existing symbolic-probe research
is a precedent for expression-valued linear observations, not a certificate for
this new construction.

Only after choosing a closed, finite port chart, a base path, frozen/active
inputs, units and a norm may \(L_m\) be recorded as \(J_m\). If these policies
and the coefficients repeat after twelve phases, define the column-coordinate
annual observation

\[
M_{[0]}=J_{11}\cdots J_1J_0.
\]

This is the discrete monodromy observation. Its eigenvalues are the Floquet
multipliers of this declared periodic linear reading. A genuine periodic base
orbit gives the usual local variational interpretation. If a non-solution
climatology merely supplies periodic coefficients, a linear periodic surrogate
can still be studied, but its multipliers alone are not stability evidence for
that climatology as an orbit. If coefficients do not repeat, retain a finite-time
product; do not relabel it periodic Floquet transport.

One eigenpair \(M_{[0]}v_0=\mu v_0\) induces phase readings
\(v_m=J_{m-1}\cdots J_0v_0\), with \(v_{12}=\mu v_0\). The “slowest decaying
mode” means the largest \(|\mu|<1\) among the declared stable modes: its
first-order same-season signal decays least rapidly per year. Multiplicity,
Jordan factors and norm-dependent transient amplification require separate
reporting. An unstable or neutral mode cannot be omitted when discussing the
whole system. Complex phase rotation is in this observed mode plane, not
automatically a geographical wind rotation.

The full return remains

\[
E_{[0]}(h)=M_{[0]}h+R_{[0]}(h)
\]

in this chart when the base is an orbit. Dropping \(R\) is an approximation at
finite amplitude. Local stability requires appropriate regularity and control
of \(R\); a multiplier by itself is not a global nonlinear error bound. This
note does not construct a continuous-time logarithm or a full Floquet normal
form, which would impose further conditions.

## 4. An exact twelve-phase A/M example

This original scalar fixture has a supplied seasonal reference

\[
(s_0,\ldots,s_{12})=(0,1,2,1,0,-1,-2,-1,0,1,0,-1,0).
\]

Define

\[
F_m(x)=s_{m+1}+a_m(x-s_m)+q_m(x-s_m)^2,
\]

with \((a_0,a_1)=(1/2,3/4)\), \((q_0,q_1)=(1/8,1/8)\), and
\(a_m=1,q_m=0\) for phases 2–11. Thus two phases are nonlinear and the
other ten are translations. This is a minimal seasonal example, not twelve
independently nonlinear months or a weather calibration.

A proposed program recipe is: add the fixed negative reference; explicitly
copy the resulting wire into the linear and quadratic branches; explicitly
copy within the quadratic branch; multiply; scale the two outputs; add them;
add the next reference. For translation-only phases use the direct translation
recipe. Do not eliminate branches of an existing program by numerical equality.
This recipe has not been compiled or issued a Rust certificate in this note.

The reference is an exact periodic orbit. Its full annual change is

\[
\boxed{E_{[0]}(h)=\frac38h+\frac18h^2+\frac1{64}h^3+\frac1{512}h^4.}
\]

The first-degree annual multiplier is \(3/8\), but the full return is quartic.
Reversing the two nonlinear anomaly steps retains the multiplier \(3/8\)
while changing the quadratic coefficient to \(17/128\) and the cubic one to
\(3/128\). Even the value dynamics differ despite identical first-order
annual spectra. Neither order nor its residual may be recovered from that one
multiplier.

The retained polynomial also supplies an actual finite-amplitude statement:
for \(|h|\leq1/2\),

\[
|R(h)|\leq\frac{273}{2048}|h|^2,\qquad
|E_{[0]}(h)|\leq\frac{1809}{4096}|h|<|h|\quad(h\ne0).
\]

The triangle inequality proves the bound for the whole interval; the checker
verifies its rational constants and five samples, rather than treating those
samples as a proof of the interval claim. The interval is invariant under
annual returns. This stronger conclusion uses the nonlinear residual explicitly.

In contrast, the equally periodic reference \(c_m=s_m+1/8\) has defects
\(d_0=-31/512\), \(d_1=-15/512\), and ten zero defects. Zero anomaly around
this reference is not preserved. The checker rejects the inference
“periodic reference implies a homogeneous anomaly equation.”

The standard-library checker uses exact fractions and retains the full quartic.
It compares composition with a separately written expansion and nested phase
evaluation, checks the finite product rule, and includes negative controls for
erased cross terms and erased order. See the
[contract and reproduction instructions](../../experiments/native_floquet_expression_v1/README.md).
Its successful output certifies only the declared external arithmetic checks;
it creates no native identities or proof objects.

## 5. What this changes for the first forecast

[The frozen operator audit](0232-floquet-checks-of-the-frozen-first-forecast.md)
remains a valid conditional observation: its approximately 0.09855 annual
spectral radius belongs to the fixed one-step homogeneous extension in the
declared normalized EOF chart. It is not the spectrum of Adva as a process,
not a bound on real atmospheric perturbations, and not a twelve-month accuracy
estimate. The six direct forecast maps failed composition; they have not been
reinterpreted as one annual program by this note.

For an actual native forecast analysis, the required next witness is the exact
forecast program and its parameter/source frontiers, chronological composition,
reference path and defects, observation policy, and retained nonlinear/forcing
residual. A learned multivariable multiplication must say whether both factors
remain active. Matrix conversion comes after those declarations and checks.

No forecast fields, training parameters, stable API, dependency lock, frozen
audit, mathematical catalog obligation, or published historical evidence is
changed here. In particular, source authenticity and independent forecast skill
remain separate unresolved questions.

## 6. Evidence and open implementation obligations

| Item | Evidence/status |
| --- | --- |
| Finite product-change identity and first-degree extraction | Arithmetic derivation in the stated polynomial chart; exact finite checks |
| Seasonal return, order counterexample, baseline defects | Original fixed rational example and retained checker report |
| Finite-amplitude return bound | Displayed triangle-inequality derivation; exact constants checked |
| Native program/source/occurrence/graft carrier | Existing Adva core supplies relevant machinery; this fixture has not been compiled |
| Paired execution correspondence and variation rewrite certificate | Open; host polynomial equality cannot supply it |
| First-degree observation composing over native slices | Open for this profile; prior symbolic-probe fixture is limited precedent |
| Generic nonlinear Floquet calculus or finite closed observable module | Not constructed or claimed |
| Application to the weather learner | Conditional existing numerical observation only; no new physical or predictive validation |

## References and provenance

- [Adva program/process core](../PROGRAM_PROCESS_CORE.md),
  [frontier before compiled presentations](../adr/0004-frontier-before-compiled-presentations.md),
  and [symbolic probe matrix observation](0019-symbolic-probe-matrix-shadow.md).
  These establish the retained-carrier and observation boundary, not a generic
  Floquet implementation.
- [AEG Paper 0: one-hole sections](https://github.com/mountain/aeg-paper/blob/609ac96b4df802a8a4a6c4079c43c2fae466bc3a/paper-0/sections/02-two-combs.tex)
  and [chronological paths](https://github.com/mountain/aeg-paper/blob/609ac96b4df802a8a4a6c4079c43c2fae466bc3a/paper-0/sections/03-paths.tex).
  Fixed-slot affine observations must not be generalized to all active-port
  dependencies.
- [Process Geometry A/M function theory](https://github.com/mountain/process-geometry/blob/c47c96fa79123c677172278be59d67ca1cc891b1/docs/06-addition-multiplication-function-theory.md),
  [addition-to-multiplication rank transition](https://github.com/mountain/process-geometry/blob/c47c96fa79123c677172278be59d67ca1cc891b1/docs/51-aeg-addition-multiplication-rank-transition.md)
  and [effective analysis principle](https://github.com/mountain/process-geometry/blob/c47c96fa79123c677172278be59d67ca1cc891b1/docs/65-effective-analysis-principle.md).
  These motivate finite process order before calculus and explicit evaluation,
  residual and cost obligations. No source text or software is imported.
- [DaCunha and Davis, unified Floquet theory](https://arxiv.org/abs/0901.3841)
  supplies the classical periodic linear comparison.
  [Huang's university lecture on periodic-orbit variations](https://personalpages.manchester.ac.uk/staff/yanghong.huang/ads/html/period-flo.html)
  distinguishes the nonlinear reference orbit from its linear variation.
  These are external mathematical references, not native certificates.

Authored by Codex (OpenAI), original contribution under Unknown v0.3.
Submitted through Mingli Yuan's authorized account proxy, without attributing
authorship, technical review, endorsement or a correctness guarantee to him.
