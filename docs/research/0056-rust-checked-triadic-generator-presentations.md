# Rust-Checked Triadic Generator Presentations

Status: bounded joint calibration following
[`0055-rust-checked-structural-evidence-bridge.md`](0055-rust-checked-structural-evidence-bridge.md).

The executable fixture is
[`tests/python/test_checked_triadic_generator_presentations.py`](../../tests/python/test_checked_triadic_generator_presentations.py).

Notes 0051--0054 used three Rust-checked scalar programs to justify the local
Boolean formulas for \(T\), \(X\), and \(K\), but Python still assembled the
three-coordinate state transformations.  Note 0055 separately grounded
resource identity in Rust causal cuts and program slices.

This note joins those two lines for the first time.  Each generator is now an
Adva function with the full boundary

\[
(t,x,k)\longrightarrow(t',x',k'),
\]

and the sixteen-element transformation monoid is generated from exact Rust
execution on all eight binary states.

The joint calibration passes extensionally and exposes an intensional no-go:

> The finite state transformation denoted by \(T\) does not select one checked
> program presentation.  Two Adva programs agree on every state while having
> different diagrams, histories, slices, and output lineage.

Therefore the sixteen transformations remain a useful finite decision
quotient, but they cannot by themselves index proof-relevant evidence.

---

## 0. Executive result

The declared checked generators realize

\[
T(t,x,k)=(1,x,k),
\]

\[
X(t,x,k)=(t,t k,k),
\]

and

\[
K(t,x,k)=(t,x,1-k).
\]

Rust evaluation agrees with the independent eight-state oracle for every
generator and state.  Closing the resulting three exact transformation tables
under composition gives:

| checked fact | result |
|---|---:|
| binary states | 8 |
| generator transformations | 3 |
| transformation monoid | 16 |
| maximum shortest-word length | 4 |

The selected full-state programs have the following operation content:

| presentation | checked operations |
|---|---|
| `temporal-preserve` | two constants, `mul`, `add` |
| `temporal-replace` | `discard`, constant |
| `spatial-update` | two `copy`, `discard`, `mul` |
| `construction-flip` | constant, `neg`, `add` |

Both temporal programs realize \(T\).  They are not the same evidence
presentation.

---

# Part I. Full-state checked generators

## 1. Why scalar calibration was insufficient

The earlier scalar functions established the formulas

\[
t\mapsto 1,
\qquad
(t,k)\mapsto tk,
\qquad
k\mapsto1-k.
\]

Python then inserted each result into the appropriate coordinate of a
three-tuple.  This was a sound external oracle calibration, but the tuple
update itself had no checked Adva boundary or lineage.

A full-state generator must account for all three inputs exactly once and
produce all three outputs exactly once.  In the finite linear core, preserving
a coordinate while also using it to compute another coordinate requires an
explicit `copy`; replacing a coordinate requires accounting for the old
resource, often through `discard`.

## 2. Temporal presentation with retained lineage

The first temporal program computes

\[
t'=1+0t
\]

and passes \(x\) and \(k\) through.  It has the required extensional value,
while the output temporal wire retains the source and occurrence lineage of
the input \(t\).

Its complete node set forms a Rust-certified program interval from the empty
causal past to the final cut.  This interval is the first checked realization
of the atomic evidence suffix

\[
\varepsilon\xRightarrow{T}T
\]

in the selected presentation.

The statement is deliberately narrow: the slice certifies execution of the
chosen \(T\) program.  It does not yet create a general morphism between the
research evidence fibres of note 0053.

## 3. Spatial update requires structural history

The spatial generator must return \(t\) and \(k\) unchanged while also using
them to calculate \(tk\).  Its declared implementation therefore:

1. copies the temporal resource;
2. copies the construction resource;
3. discards the old spatial resource;
4. multiplies one temporal child by one construction child; and
5. returns the other two children as the temporal and construction outputs.

The final output source pattern is exactly:

\[
\bigl(\{s_t\},\{s_t,s_k\},\{s_k\}\bigr).
\]

The old spatial source \(s_x\) is absent from the upper frontier, but its
discard node remains an internal event.  Both copy histories retain their
parent and ordered child occurrences.

Thus the apparently simple state action

\[
x\leftarrow tk
\]

contains nontrivial constructive evidence when realized in a linear program
language.

## 4. Construction flip

The construction program passes \(t\) and \(x\) through and computes

\[
k'=1-k.
\]

It needs no copy because the input construction resource is used once and is
not also preserved.  Its state action is involutive on the binary core:

\[
K^2=1.
\]

The two-step state return does not imply that the concatenated program history
is empty.  The distinction from proof inversion in note 0053 remains intact.

---

# Part II. Rust execution and the finite quotient

## 5. Generator tables come from Rust

For each exported full-state function and each of the eight binary inputs, the
fixture calls the checked native evaluator.  The returned triple determines
one entry of the generator transformation table.

Only after obtaining those tables does Python perform finite closure.  The
independent oracle implements the three equations directly and is compared
against the Rust-derived tables entry for entry.

The resulting equality is

\[
M_{\mathrm{Rust}}
=
M_{\mathrm{oracle}},
\qquad
|M|=16.
\]

This improves the authority boundary over notes 0052--0054: Python no longer
declares which complete state transition each generator performs.

## 6. What remains outside Rust

The closure queue, shortest-word table, and comparison with the oracle remain
finite research computations in Python.  They do not allocate semantic
program identities.

More importantly, executing a word such as \(XTK\) in the current fixture
means sequentially calling three separately checked functions from Python.
It does not yet produce one composed `SharedProgramDiagram` whose internal
cuts certify the whole word and its suffix decomposition.

The current result therefore establishes checked generators and a checked
atomic interval, not checked arbitrary context composition.

---

# Part III. Presentation no-go for the temporal action

## 7. A second temporal program

Consider the alternative program:

1. explicitly discard the old temporal input;
2. create the constant \(1\); and
3. pass the spatial and construction inputs through.

It realizes

\[
(t,x,k)\mapsto(1,x,k)
\]

on every binary state, just like `temporal-preserve`.

Its first output has no input source and no occurrence lineage.  By contrast,
the first program's temporal output retains the old temporal source through
the syntactic computation \(1+0t\).

## 8. Exact separation

The fixture establishes all of the following simultaneously:

\[
\llbracket T_{\mathrm{preserve}}\rrbracket
=
\llbracket T_{\mathrm{replace}}\rrbracket
\]

on the complete declared state space, while

\[
D_{\mathrm{preserve}}
\ne
D_{\mathrm{replace}},
\]

\[
H_{\mathrm{preserve}}
\ne
H_{\mathrm{replace}},
\]

and

\[
\operatorname{lineage}(t'_{\mathrm{preserve}})
\ne
\operatorname{lineage}(t'_{\mathrm{replace}}).
\]

Their exact full program slices are also unequal.  The replacement slice
retains the discard event even though its new temporal output is the same
constant value.

## 9. Correction to the finite evidence index

Notes 0053 and 0054 called the sixteen transformation indices “context
presentations.”  That terminology was adequate inside the fixed abstract
alphabet \(\{T,X,K\}\), where every letter already named one chosen action.

The checked-program bridge shows that a transformation alone is not a complete
presentation.  At minimum a proof-relevant index must distinguish:

- the extensional transformation \(m\in M\);
- the selected checked program or operation presentation;
- its typed boundary;
- its source and occurrence transport; and
- its retained history.

The sixteen-element monoid should therefore be understood as a finite
**extensional decision quotient** of richer checked presentations.

This is a strengthening, not a rejection, of the finite-representation idea:

- the quotient decides state action and finite reachability;
- the presentation retains constructive evidence; and
- the forgetting map between them must be explicit.

## 10. Why canonical shortest words do not repair the problem

Selecting the shortest abstract word `T` does not choose between the two Adva
programs, because both are implementations of that same letter.  A canonical
spelling in the transformation monoid solves redundancy among words only
after a generator presentation has already been selected.

Likewise, choosing the smaller node count would add a cost policy.  It would
not prove that the discarded-lineage presentation is semantically preferable.

A finite observer may adopt such a policy, but it must record the forgotten
alternatives or the criterion by which one was selected.

---

# Part IV. Consequences for the larger questions

## 11. Consequence for finite representation

The finite-expression/open-evidence form now has three distinct layers:

\[
\text{checked program presentation}
\longrightarrow
\text{finite transformation quotient}
\longrightarrow
\text{observed support}.

The first arrow forgets diagram, history, and lineage distinctions such as the
two temporal programs.  The second arrow forgets additional effects outside
the selected spatial observation.

The open evidence fibre should live over the first layer, while finite search
may use the middle quotient.  Returning a witness requires lifting the result
back to a concrete checked presentation rather than returning only a monoid
element.

## 12. Consequence for logic on a 3-form

The two temporal programs have the same truth-transforming effect but different
constructive and temporal content.  This supplies a particularly small
three-coordinate separation:

- their spatial/extensional state action agrees;
- their temporal event histories differ; and
- their constructive lineage transport differs.

A logic that quotients them immediately can express the coarse characteristic
but cannot explain how evidence was produced.  A logic that never quotients
them cannot use the compact sixteen-element decision procedure.

The desired 3-form logic therefore needs both the forgetting map and its
residual, not a choice between intensional and extensional semantics.

## 13. Consequence for \(L/R\) and calibration

Ordering the abstract letters of a context is still insufficient to determine
the checked computation.  One must also choose the presentation of each
letter.  Thus a word order such as

\[
L;R
\]

solves only temporal sequencing.  It does not settle source replacement,
occurrence branching, or which history realizes the same state action.

For startup calibration, reaching the same calibrated triple may mean either
that an old coordinate was retained through an algebraically null use or that
it was explicitly discarded and replaced.  These alternatives should not
share one certificate merely because the calibrated values agree.

---

# Part V. Verification and limits

## 14. What the fixture establishes

Within four finite full-state Adva functions and eight binary inputs, the
fixture establishes:

1. checked native execution of complete \(T\), \(X\), and \(K\) boundaries;
2. exact agreement with the independent generator oracle;
3. a sixteen-element Rust-derived transformation monoid;
4. closure under all ordered pairs of its elements;
5. maximum shortest context length four;
6. a complete checked program interval for the selected atomic \(T\) suffix;
7. two copies, one discard, and one multiplication in the selected \(X\)
   presentation;
8. exact temporal and construction source transport through \(X\);
9. disappearance of the old spatial source with its discard retained;
10. copy parents absent and copy children present at the final frontier;
11. two temporal programs agreeing on every declared state;
12. unequal diagrams, histories, intervals, and temporal output lineage for
    those programs; and
13. exact failure of extensional transformation to determine presentation.

## 15. What it does not establish

The fixture does not establish:

- a unique or canonical Adva realization of \(T\), \(X\), or \(K\);
- one checked diagram for an arbitrary context word;
- a general evidence-fibre or suffix-continuation API;
- a stable triadic machine, tensor, logic, or presentation API;
- completeness of the chosen generator set among all equivalent programs;
- a general quotient of checked programs by state action;
- that binary evaluation proves equality over all real inputs;
- normalization, proof equality, or coherence;
- a complete three-computer startup certificate;
- a universal computation result; or
- a solution to the global \(L/R\) problem.

Although the two temporal formulas in fact agree algebraically over real
inputs, this fixture claims only complete agreement on the declared eight-state
core.  The change adds no stable API, IR schema change, `claims.toml` entry, or
change to the active implementation priority.

## 16. Next gate

The next step should refine the word evidence itself:

1. define a finite research alphabet whose letters name exact checked program
   presentations rather than only \(T/X/K\) transformations;
2. compile one nontrivial context word into one `SharedProgramDiagram`;
3. use its graft trace and nested causal cuts to separate prefix and suffix
   intervals;
4. compare its extensional action with the sixteen-element quotient;
5. return both the quotient element and the exact checked word presentation;
6. verify sequential cut on two different suffix decompositions; and
7. preserve the alternative temporal presentation as a distinct witness over
   the same quotient element.

This would turn the present checked generator calibration into the first
program-level realization of open word evidence.

## 17. Conservative conclusion

The joint calibration gives both a positive and a negative result:

> Explicit Adva programs generate exactly the intended finite triadic monoid,
> and one atomic suffix already has an exact checked interval.  However, the
> monoid action does not determine the program presentation that produced it.

The finite quotient is therefore suitable for decision, while proof-relevant
evidence must remain presentation-indexed.  This is the missing distinction
needed before composing full checked context words.

