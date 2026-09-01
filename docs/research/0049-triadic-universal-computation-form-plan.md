# Research Plan for a Triadic Universal Computation Form

Status: research plan following
[`0046-proposal-for-logic-on-a-3-form.md`](0046-proposal-for-logic-on-a-3-form.md)
and
[`0048-directional-energy-of-a-learned-characteristic.md`](0048-directional-energy-of-a-learned-characteristic.md).

This plan records a correction to the current three-computer programme.

The existing finite calibrations have given a typed three-domain observation
form, opposite-pair sections, observer quotients, residuals, a first semantic
entailment order, and directional characteristic energies.  These are enough
to specify how the three domains observe one another.  They are not yet enough
to specify three programmable computers.

The missing distinction is:

> An opposite-pair section supplies one computer with a typed observation
> environment.  It is not the program executed by that computer.

Characteristic inference is one important injectable program family.  It
must not be identified with the universal computation form itself.  A
temporal, spatial, and constructive computer may receive three different
programs, maintain three different local states, and react differently to the
same three-domain observation form.

The target of this plan is therefore a research-level structure

\[
\mathbb U_Q
=
(\mathfrak F_Q;
U_t,U_X,U_K;
p_t,p_X,p_K;
\sigma;
\operatorname{Cal}_0),
\]

where \(\mathfrak F_Q\) is the observation form, \(U_D\) are typed
interpreters, \(p_D\) are independently injected programs, \(\sigma\) is an
explicit scheduler, and \(\operatorname{Cal}_0\) is the startup calibration.

“Universal” is a target and must be qualified.  The first deliverable is only
a **uniform programmable form** and one bounded interpreter calibration.  It
does not establish Turing universality, coupled universality, reflection, or a
new stable Adva machine model.

This plan introduces no stable code-as-data, interpreter, scheduler,
three-computer, logic, energy, observer, or reflection API.  It does not modify
`claims.toml`.  Rust remains the sole semantic authority, and the active
`ProgramSlice` priority remains unchanged.

---

## 0. Executive architecture

The proposed dependency chain is

\[
\boxed{
\text{injected program triple}
\longrightarrow
\text{scheduled run trace}
\longrightarrow
\text{3-form observation}
\longrightarrow
\text{characteristic, logic, and energy reports}.
}
\]

In a later learning system, the chain may feed back:

\[
\boxed{
\text{characteristic and residual}
\longrightarrow
\text{new observer, state, schedule, or program triple}.
}
\]

The first box is the immediate research target.  The feedback box requires an
explicit reflective extension and must not be smuggled into the baseline.

The minimum layers are:

| layer | role | current status |
|---|---|---|
| observation form | coordinates and typed compatibility | finite calibrations exist |
| opposite-pair section | raw environment supplied to one domain | finite algorithm exists |
| injected program | domain-specific computation over local state and environment | not represented as data |
| interpreter | evaluates one encoded program | not implemented |
| scheduler | chooses order and snapshot discipline | not formalized |
| startup calibration | aligns types, versions, scales, and initial state | open problem |
| run report | preserves result, trace, residual, and `Unknown` | only partial ingredients exist |
| learning feedback | changes observer or programs from prior runs | future reflective layer |

---

# Part I. Observation is not computation

## 1. The observation form

Retain a finite observer-indexed form

\[
\mathfrak F_Q
=
(T_Q,X_Q,K_Q;\operatorname{Obs}_Q).
\]

The observation judgment is typed:

\[
\operatorname{Obs}_Q:
T_Q\times X_Q\times K_Q
\longrightarrow
\operatorname{ObservationResult}_Q.
\]

The result must distinguish at least:

\[
\operatorname{Positive}(e),
\qquad
\operatorname{Refuted}(c),
\qquad
\operatorname{Unknown}(b),
\]

where `Positive` carries evidence, `Refuted` requires a finite exhaustive or
negative certificate, and `Unknown` retains the boundary that prevented a
decision.

The full product notation is mathematical shorthand.  An Adva
implementation must use explicit ordered typed ports and must not claim that
the current frontier representation implements a tensor product.

## 2. Raw opposite-pair environments

Fixing two coordinates gives a raw section on the third:

\[
S_t(x,k)=\operatorname{Obs}_Q(-,x,k),
\]

\[
S_X(t,k)=\operatorname{Obs}_Q(t,-,k),
\]

and

\[
S_K(t,x)=\operatorname{Obs}_Q(t,x,-).
\]

These sections implement the triangle principle: the opposite pair supplies
the vocabulary with which one vertex can be read.

The important correction is that

\[
S_D
\ne
\text{computer }D.
\]

A section is an input environment, observation interface, or candidate
feature source.  A program may extract a characteristic from it, transform
the local state, ignore part of it, request more observation, or fail to
terminate.

## 3. Characteristic inference as one program family

A domain-relative characteristic program may have the schematic behavior

\[
p_D^{\mathrm{char}}:
(s_D,S_D(s_{-D}))
\rightharpoonup
(s_D',\chi_D,R_D).
\]

Here \(s_D\) is local state, \(S_D(s_{-D})\) is the opposite-pair environment,
\(\chi_D\) is a learned characteristic, and \(R_D\) is its residual.

Three characteristic programs may use different algorithms:

\[
p_t^{\mathrm{char}},
\qquad
p_X^{\mathrm{char}},
\qquad
p_K^{\mathrm{char}}.
\]

Nothing in the universal form requires all three to seek the same kind of
invariant.  Nothing requires the injected programs to be characteristic
programs at all.

---

# Part II. The programmable machine form

## 4. Local states and code

Each domain has a local state carrier

\[
S_t,
\qquad
S_X,
\qquad
S_K,
\]

and a typed code carrier

\[
\operatorname{Code}_t,
\qquad
\operatorname{Code}_X,
\qquad
\operatorname{Code}_K.
\]

The injected program triple is

\[
p=(p_t,p_X,p_K),
\qquad
p_D\in\operatorname{Code}_D.
\]

Code identity, program identity, value equality, and observational
equivalence must remain distinct.  An encoded program must retain its source,
occurrences, version, boundary, and provenance.  It cannot be represented by
an untracked Python callable.

The current Adva language does not yet have a stable code-as-data type.  The
first code carrier must therefore be a separately approved, finite, versioned
research representation rather than an accidental serialization of the
current AST.

## 5. Typed interpreters

Each domain has an interpreter

\[
U_D:
(\operatorname{Code}_D,S_D,\operatorname{Env}_D,\operatorname{Fuel})
\longrightarrow
\operatorname{RunResult}_D.
\]

The environment is derived from the opposite pair and the observation policy:

\[
\operatorname{Env}_t=S_t(s_X,s_K),
\]

\[
\operatorname{Env}_X=S_X(s_t,s_K),
\]

\[
\operatorname{Env}_K=S_K(s_t,s_X).
\]

The interpreters may share a checked instruction core while exposing
different typed operations.  Alternatively, the three code languages may be
distinct and connected by explicit translators.  The first calibration
should compare these designs rather than assume one prematurely.

An interpreter call is not ordinary Adva value application.  The current
core lowers calls through finite simultaneous grafting before evaluation.  A
future code interpreter requires a new, explicit code-as-data and machine-step
semantics.

## 6. Run results and partiality

The bounded result must distinguish:

```text
Halted(output, checked_trace)
Suspended(checkpoint, remaining_obligations)
Failed(error_certificate)
Unknown(boundary, partial_trace)
```

Fuel exhaustion returns `Unknown`, not a proof of divergence.  True divergence
is not a finite returned value unless an independent certificate proves a
specific nontermination pattern in a declared fragment.

Every run result must preserve:

- code and instruction version;
- source and occurrence identity;
- local input and output state;
- opposite-pair environment reference;
- exact finite machine steps;
- fuel consumed;
- observation policy;
- residual or unresolved obligations; and
- any directional energy or resource report requested by the experiment.

## 7. One local update

Let the complete state at step \(n\) be

\[
s_n=(s_{t,n},s_{X,n},s_{K,n}).
\]

If domain \(D\) is selected, first compute its environment from one declared
snapshot:

\[
e_{D,n}
=
S_D(s_{n,-D}).
\]

Then execute

\[
r_{D,n}
=
U_D(p_D,s_{D,n},e_{D,n},f_n).
\]

If the result halts with a new local state, update only that coordinate:

\[
s_{n+1}
=
s_n[D\leftarrow s_{D,n+1}].
\]

All other coordinates retain their identities.  Copy, discard, and shared
uses of opposite-domain observations must remain explicit.

---

# Part III. Scheduling and order

## 8. Why a scheduler is unavoidable

The three equations

\[
s_t^+=U_t(p_t;s_t,S_t(s_X,s_K)),
\]

\[
s_X^+=U_X(p_X;s_X,S_X(s_t,s_K)),
\]

and

\[
s_K^+=U_K(p_K;s_K,S_K(s_t,s_X))
\]

do not determine whether the right sides read old states or already updated
states.  They also do not decide what happens when one interpreter suspends or
returns `Unknown`.

The schedule is therefore semantic data, not an implementation detail.

## 9. Small-step schedule

Let

\[
D_n
=
\sigma(n,\operatorname{Trace}_{<n})
\in
\{t,X,K\}.
\]

The scheduler selects one domain and one snapshot discipline.  A run is a
partial transition sequence

\[
(p,s_0,Q,\sigma)
\rightsquigarrow
s_1
\rightsquigarrow
s_2
\rightsquigarrow
\cdots.
\]

The baseline scheduler must be finite and explicit.  Adaptive scheduling may
later read prior checked reports, but it must itself be represented as a
program or certified policy.

## 10. Synchronous execution as a derived macrostep

A synchronous round is not primitive.  It can be defined by:

1. freezing snapshot \(s_n\);
2. running all three programs against environments derived from that snapshot;
3. collecting three results; and
4. committing all successful updates at one declared barrier.

If one result is `Unknown`, the commit policy must say whether the entire round
remains unresolved or whether partial commits are allowed.  Different choices
produce different machines.

## 11. Relation to the L/R problem

The unresolved L/R order is not only a logical comparison problem.  It may
also be a scheduling problem.

Two program fragments may be incomparable as static propositions but become
ordered under a declared trace discipline.  Conversely, two locally valid
orders may produce incompatible global histories.

The universal computation form should therefore return:

\[
\operatorname{OrderReport}
=
(\text{schedule},
\text{trace comparison},
\text{observer},
\text{residual}).
\]

It must not manufacture a global `L | R` cut merely because one scheduler
chooses `L` first.

---

# Part IV. Startup calibration

## 12. Calibration inputs

Before the first step, \(\operatorname{Cal}_0\) must check at least:

1. the three code versions;
2. interpreter compatibility with each code carrier;
3. input and output port types;
4. initial local states;
5. coordinate and naming conventions;
6. observer policy and observation boundary;
7. snapshot and scheduling convention;
8. fuel and resource units;
9. directional energy scales, if scalar comparison is requested; and
10. source, occurrence, and certificate authority.

The result should be a calibration report, not an untracked initialization
side effect.

## 13. Calibration result

A minimal result is

```text
StartupCalibrationReport
  code_versions
  typed_ports
  initial_states
  observer_policy
  schedule_policy
  resource_scales
  directional_energy_scales
  accepted_correspondences
  residual_mismatches
  status
```

Calibration may succeed only on a restricted boundary.  It may also return a
residual mismatch or `Unknown`.  A coarse agreement must not be promoted to
identity of local coordinates or programs.

## 14. Relation to three-domain energy

The directional energy report is

\[
(E_t,E_X,E_K).
\]

A scalar total requires calibration coefficients

\[
(\alpha_t,\alpha_X,\alpha_K).
\]

Startup calibration may be responsible for declaring these conversions, but
it cannot derive physical units from the three-domain form alone.  The
interpreter also needs a separate operational cost model.  Graph energy,
execution cost, and physical energy remain different reports.

---

# Part V. Four levels of universality

## 15. Level U0: uniform programmability

The first attainable property is a common machine protocol:

- three independently chosen code values;
- three typed interpreters;
- one explicit scheduler;
- one startup calibration;
- one run-report schema; and
- exact `Unknown` behavior.

U0 does not say that any interpreter is universal.  It only says that the
three computers are genuinely programmable rather than hard-coded section
calculators.

## 16. Level U1: component universality

For a declared domain language \(\mathcal P_D\), component universality would
require:

\[
\forall P\in\mathcal P_D,
\ \exists\ulcorner P\urcorner\in\operatorname{Code}_D
\]

such that

\[
U_D(\ulcorner P\urcorner;s,e)
\simeq
P(s,e)
\]

under a stated result and trace relation.

This requires an encoding theorem and an interpreter correctness theorem.  A
few example programs do not establish U1.

## 17. Level U2: coupled universality

For a declared class of finite triadic machines, coupled universality would
require a program triple and scheduler whose run simulates the target machine:

\[
M
\simeq_Q
\operatorname{Run}
(U_t,U_X,U_K;p_t,p_X,p_K;\sigma).
\]

The comparison must specify:

- which states correspond;
- which steps correspond;
- what observation policy is used;
- which histories and sources survive;
- which residuals are permitted; and
- how divergence and `Unknown` are compared.

Observational agreement alone does not identify the source machines.

## 18. Level U3: reflective programmability

A reflective extension permits code to become a checked construction output.
The constructive computer may propose

\[
(p_t',p_X',p_K')
\]

from prior traces, characteristics, and residuals.

Applying the proposal must be a separate certified transition at an epoch
boundary:

\[
p_{n+1}
=
\operatorname{Install}
(p_n,\operatorname{Proposal}_K,\operatorname{Certificate}).
\]

The baseline U0 machine must not let an ordinary value masquerade as installed
code.  Reflection requires code typing, validation, capability boundaries,
and a source-to-new-code correspondence.

## 19. Universality is not reflection

A universal interpreter can execute encoded programs without allowing those
programs to rewrite the interpreter or install new code.  Conversely, a
finite self-modifying fixture is not automatically universal.

The hierarchy is therefore

\[
\text{U0 uniform form}
\;<\;
\text{U1 component universality}
\;<\;
\text{U2 coupled universality},
\]

with U3 reflection as an additional axis rather than an automatic final step.

---

# Part VI. Logic, energy, and other programs

## 20. Logic is an output regime, not the machine

A characteristic program may generate proposition-like supports.  Repeated
stable characteristics may generate an entailment order and a logical
calculus.  That path is

\[
\text{run trace}
\longrightarrow
\text{characteristics}
\longrightarrow
\text{entailment}
\longrightarrow
\text{logic}.
\]

The universal computation form must also admit programs that do not seek
stable characteristics:

- simulation and forward execution;
- search and exploration;
- construction and rewrite;
- counterexample generation;
- observer refinement;
- resource allocation;
- energy injection or dissipation; and
- program proposal.

Logic is therefore one institutionalized outcome of computation, not the
ontology of every computation.

## 21. Energy as a run report

For each finite step, the machine may report:

\[
\Delta\mathbf E_n
=
(\Delta E_{t,n},
\Delta E_{X,n},
\Delta E_{K,n}).
\]

This records directional feature variation relative to declared move systems.
Operational resource use must be recorded separately:

\[
\mathbf C_n
=
(\text{steps},\text{memory},\text{copies},\text{communication},\ldots).
\]

No default equation identifies \(\Delta\mathbf E_n\) with \(\mathbf C_n\).

## 22. Exploration need not minimize energy

A characteristic-learning program may seek a low-energy nonconstant mode.
Another program may deliberately:

- cross an energy barrier;
- increase variance;
- change the observation boundary;
- invalidate a coarse invariant;
- expose a hidden residual; or
- generate an entirely different code path.

The machine form must not hard-code monotone energy descent.  Energy descent
is one injectable strategy under one calibration.

---

# Part VII. The first bounded calibration

## 23. Exact question

The first executable question is:

> Can one finite, typed, fuel-bounded machine protocol execute three genuinely
> different injected programs against three opposite-pair environments while
> preserving schedule, source, occurrence, residual, and `Unknown`?

The experiment tests U0 only.

## 24. Candidate three-program fixture

Use three small programs with visibly different purposes.

### Temporal program

Read a bounded sequence of opposite-pair observations and return the first
certified change point.  If fuel expires before the declared finite boundary
is exhausted, return `Unknown` with the scanned prefix.

### Spatial program

Read a finite section on a small graph and mark its boundary edges.  Return the
exact boundary support and directional energy.

### Constructive program

Apply one declared tagged rewrite to a finite expression representation.
Return the rewritten code candidate, source-to-result correspondence, and an
explicit installation obligation.  Do not install the candidate in the U0
fixture.

The programs are not three labels on the same host function.  Their encoded
instructions, state transitions, outputs, and certificates must differ.

## 25. Minimal finite code

The first `ResearchCodeV0` should be:

- finite and versioned;
- typed by ordered input and output ports;
- independent of Python object identity;
- explicit about instruction position and source occurrence;
- incapable of hidden host callbacks;
- bounded by explicit fuel; and
- validated before execution.

The instruction set should be just large enough for the three fixtures.  It
must not be called a general Adva bytecode or stable AST.

## 26. Schedule variants

Run at least three schedules:

1. `t -> X -> K` sequential execution;
2. `K -> X -> t` sequential execution; and
3. one frozen-snapshot synchronous macrostep.

Require either:

- exact agreement with a schedule-independence certificate;
- an explicit difference in state or history; or
- `Unknown` when the bounded comparison is insufficient.

The test must not erase ordering differences merely because final scalar
values agree.

## 27. Required negative cases

The fixture must include:

1. one ill-typed program injection;
2. one code-version mismatch;
3. one fuel exhaustion;
4. one incompatible startup calibration;
5. one schedule-dependent history;
6. one coarse observer that merges distinct runs;
7. one residual that later refinement recovers; and
8. one attempted code installation rejected for lack of a certificate.

## 28. U0 success criteria

U0 succeeds only if:

- three distinct code values are validated;
- each runs under its declared typed interpreter;
- opposite-pair environments come from one explicit observation form;
- scheduling is present in the checked trace;
- local and global states remain typed;
- fuel exhaustion returns `Unknown`;
- no Python callable authorizes a semantic transition;
- source and occurrence identities survive serialization;
- observer forgetting retains exact run preimages; and
- energy and operational cost remain separate reports.

---

# Part VIII. Dependency-respecting implementation plan

## 29. Phase A: design now

This phase may proceed in parallel with the active engineering task.

Deliver:

- this research plan;
- a dedicated ADR for code-as-data versus current program terms;
- a versioned draft schema for U0 inputs and reports;
- exact success, failure, and `Unknown` criteria; and
- a comparison with the current finite call/graft semantics.

No stable implementation is authorized.

## 30. Phase B: exact process boundary

Wait for the current `ProgramSlice` phase to establish the exact finite process
carrier between cuts.  Then determine whether one interpreter step can be
reported as or linked to an exact slice without pretending that feedback is
already part of `ProgramSlice`.

Deliver:

- source-to-step correspondence;
- occurrence and lineage preservation;
- interpreter-step boundary design; and
- one counterexample if the current slice carrier is insufficient.

## 31. Phase C: finite code and bounded control

After finite tagged data and bounded control semantics are approved:

- define `ResearchCodeV0` in Rust;
- define validation and versioning;
- implement fuel-bounded instruction stepping;
- serialize code and checkpoints through the versioned IR boundary; and
- prohibit unchecked host callbacks.

This phase shares dependencies with the bounded arithmetic evaluator and
Metamath proof-step checker in the engineering agenda.

## 32. Phase D: three-program U0 calibration

Implement the temporal, spatial, and constructive fixtures.  Run the schedule
variants and negative cases.  Produce a single `TriadicRunReportV0` with all
typed subreports.

Success establishes uniform programmability for the bounded fragment, not
universality.

## 33. Phase E: U1 theorem or counterexample

Select one deliberately small finite instruction language and attempt an
encoding/interpreter correctness theorem.

The theorem must state:

- source language;
- code representation;
- interpreter;
- result relation;
- trace relation;
- resource bound; and
- treatment of failure and `Unknown`.

If the theorem fails, preserve the smallest counterexample and revise the code
or machine boundary.

## 34. Phase F: coupled and reflective experiments

Only after U1:

- define a class of finite triadic machines;
- test U2 coupled simulation;
- separate scheduling equivalence from state equivalence;
- let the constructive computer propose code;
- validate proposal and installation as separate steps; and
- test whether characteristic inference can change a later program without
  erasing the prior run history.

No self-modifying stable API is authorized by this phase plan.

---

# Part IX. Risks, falsifiers, and promotion gates

## 35. Main engineering risks

- Encoding current AST objects directly may freeze accidental parser details.
- A Python reference interpreter may silently become the semantic authority.
- A common untyped bytecode may erase the three domain boundaries.
- Three domain-specific languages may share no meaningful universal core.
- Fuel may be mistaken for a proof of nontermination.
- A scheduler may silently impose the L/R order under investigation.
- Code generation may be confused with code installation.
- Final-value equality may erase distinct schedules and histories.
- Energy reports may be confused with machine resource costs.
- Reflection may bypass source, occurrence, capability, or certificate checks.

## 36. Decisive falsifiers

The proposed form should be revised if:

1. the three programs can share a report only by erasing their typed outputs;
2. opposite-pair sections cannot be supplied without host-language special
   cases;
3. exact run history cannot preserve both program occurrence and observed
   environment occurrence;
4. schedule comparison produces no compositional residual;
5. every useful construction program requires unbounded hidden host behavior;
6. component interpreters cannot share any meaningful code or machine law;
7. the construction domain cannot distinguish a code proposal from an
   installed program; or
8. the observation form cannot be related to program execution without
   circularly defining accepted observations from desired outputs.

A negative result may show that the correct object is a network of typed
interpreters rather than one triadic universal machine.

## 37. Promotion gates

Do not add stable universal-machine or three-computer APIs until:

- U0 has one complete bounded Rust-authoritative fixture;
- code-as-data has a separately approved ADR;
- code, state, value, and program identities are distinct;
- interpreter steps preserve exact sources and occurrences;
- fuel exhaustion and `Unknown` are tested;
- at least two schedule variants have a certified comparison;
- observer quotient retains exact run residuals;
- logical and energy reports are derived rather than built into execution;
- one component encoding theorem or decisive counterexample exists; and
- the `ProgramSlice` dependency has been satisfied or explicitly revised.

## 38. Explicit nonclaims

This plan does not establish:

- a universal Turing machine in Adva;
- component, coupled, or reflective universality;
- a stable code representation;
- a general interpreter correctness theorem;
- a canonical scheduler;
- a solution to the L/R reduction problem;
- a complete startup calibration;
- a natural-deduction system;
- a physical energy law;
- a universal learning direction;
- that all three domains use one language; or
- that the world is exhausted by characteristic inference.

---

# Part X. Philosophical boundary

## 39. Characteristic inference is one path

Characteristic inference compresses many events into a stable distinction.
Logic may institutionalize the distinction.  Energy may describe its boundary
tension and the work hidden inside observer fibres.

The universal computation form must remain wider than that path.  It must
permit programs that stabilize, destabilize, explore, construct, revise the
observer, or propose a new program.  Otherwise the architecture would encode
one theory of learning as the only possible direction of computation.

The many paths between emptiness and universality are not represented merely
by adding more characteristics.  At the computational level, they first
appear as freedom to inject different programs, choose different schedules,
change observation boundaries, and retain the residual consequences of those
choices.

This statement sets an architectural boundary.  It is not yet a formal theory
of novelty, curiosity, adventure, or value.

---

## 40. Conservative conclusion

The research target can be stated compactly:

> Build a finite, typed, observer-aware protocol in which three independently
> injected programs execute under three interpreters, receive raw
> opposite-pair environments from one 3-form, advance under an explicit
> scheduler and startup calibration, and return checked traces, residuals,
> energy reports, and honest `Unknown`.

The first milestone is U0 uniform programmability.  Characteristic inference,
logic, and energy then become programs and reports over the machine rather
than substitutes for the machine itself.

