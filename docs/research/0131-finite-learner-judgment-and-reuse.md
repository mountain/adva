# Research 0131: Finite learner judgment, correction, and checked reuse

Status: external finite arithmetic calibration and proposed vocabulary organization.
No new native Adva operation, general learner, universality theorem, or automatic merge.

## Origin, authorization, and source boundary

On 2026-09-06 Mingli Yuan accepted the proposal to freeze the working vocabulary
and test success, counterexample, and fuel exhaustion as different learner updates,
including reuse on a fresh arithmetic instance. He proposed `syntax-formation`,
`word-formation`, and `propose`, and replaced the upper-level role of `switch`
with `judge`. The interpretations and implementation below are assistant proposals
within that authorization, not claims that Mingli's intended language is complete.

The inspected main was `57c1d04bcfe51b82f6e559a61ca02e668f630b5a`.
The only open PR was draft #130 at `f5357fff7fc1d93f1bfbaa184f26ac46b1f5da19`.
Its coverage experiment was read but not repeated or imported. Research 0121--0129
was already on main. The existing 0122 quorum learner is problem-specific and is
not repurposed as a general natural-language interpreter.

`AGENTS.md`, the research agenda, claims registry, and Research 0091, 0107,
0122, 0123 and 0129 constrain this work. The exact field arithmetic is an external
Python model, like the earlier independent finite calibrations. No native identities,
specializer, feedback, or exact-field primitives are installed. The paused
`unknown-syntax-building` inquiry stays paused. The arithmetic-universality and
hypothesized-arithmetic-truth candidates remain Proposed; M6 and 0092 promotion
obligations remain open.

The contract was written before execution:
[`0131-finite-learner-run-contract.json`](0131-finite-learner-run-contract.json),
SHA-256 `643ad235e4b2ad65e395fc705d33ffc7a42731e1f755f64b976693eca9b65474`.
No prior executable experiment for this exact F7 learner fixture was found in
the inspected tree. No claim is made about unseen conversation-only work.

## Organizing the vocabulary

A finite interpretation contract records interpreter, grammar, arithmetic domain,
interpretation, task/acceptance relation, interface assumptions, and budget.
Human interpretation supplies intended reference and real-world purpose; the
computer checks the declared model; an unspecified future interpreter leaves an
interface obligation. An unspecified interpreter and an `Unknown` result are
different types of incompleteness. Calling a person an OpenWorld computer is a
working analogy, not an axiom of this checker.

| Responsibility | Words and boundaries |
|---|---|
| Receive | `object`, observations, problem awareness, `history`; source and omissions remain explicit |
| Form and interpret | `problem-formation` identifies the question; `interpret-question-form` fixes type, quantifier, known/wanted positions |
| Propose and construct | `propose` offers a direction; `generate` builds an instance in a declared grammar |
| Check | `verify` checks a fixed obligation; `proof` is a proof object and `evidence` may be broader |
| Judge and schedule | `judge` uses evidence and resource limits; `action-plan` selects a finite next action |
| Update | `learn` revises constraints, methods or vocabulary; `word-formation` is only one possible outcome |
| Retain | `frontier`, `history`, `replay`, `resume` retain versions, failures, costs and cursors |

`syntax-formation` proposes/adopts formation and composition rules; it is needed
only when existing syntax is inadequate. `word-formation` records a named unit
within a language, with its interpretation and reuse contract. A word may denote
a hypothesis; forming the name does not prove it. `syntax-formation-propose`
is provisionally decomposed into a proposal concerning syntax, rather than a
fourth indivisible primitive. `start`, `originate`, and `arise` remain unassigned
documentary candidates and are excluded from this minimal executable fixture.

Syntax, semantics and pragmatics cross construction, space and time; they are
not assigned bijectively to those three domains. Likewise compute/verify/learn
are mechanism roles, not three new physical axes. The user's energy-level name
`reveal` is retained separately from the existing CLI command. Physical budgets
refer to the actual host; institutional acceptance belongs to the person who
defines the task or accepts its use. Arithmetic acceptance cannot supply consent
or prove customer utility.

`judge` is a proposed evidence-to-action policy, not an additional truth oracle.
Changing known/wanted positions (the earlier `switch` role) is one possible
action and requires a fresh difficulty check. A syntactically expressible inverse
problem need not be solvable, identifiable, or affordable.

The proposed finite sequence is:

```text
receive -> form/interpret -> judge(admissibility and budget)
        -> propose/generate -> verify -> judge(accepted/refuted/unknown)
        -> update -> retain
```

There is no automatic arrow from retain back to receive. A continuation is an
explicit bounded invocation. `breakthrough` remains a stronger composite research
process, not the name of this fixed-family calibration.

## Frozen arithmetic question and grammar

Let the scalar domain be F7, represented by canonical integers 0 through 6.
The input variable also ranges over exactly these seven elements. Set

```text
f(x) = 2*x^2 + 3*x + 1
g(a,b,c,x) = (a*x+b)*x+c
```

The question is `exists (a,b,c) in F7^3, forall x in F7, g(a,b,c,x)=f(x)`.
The producer enumerates coefficient triples lexicographically. It knows the
declared target expression and uses the ordinary supplied Horner template.
No hidden-answer discovery, unknown-syntax construction or endogenous grammar
invention is claimed. The candidate grammar is fixed, with exactly 343 triples;
at most 2401 input comparisons suffice for one exhaustive search. A direct
coefficient-reading algorithm would already solve this deliberately elementary
problem: the search is a calibration baseline, not a competitive solver.

The producer evaluates nested Horner form. The checker independently evaluates
expanded powers modulo seven. An accepted record must contain every input in
order; a refutation retains the first checked mismatch. Every state transition
rechecks the record, binds the task digest, and retains a ledger entry. Digests
are content coordinates, not authentication or native semantic identities.

Under the stated integer/modular arithmetic assumptions, checker acceptance
implies equality at every element of the declared domain: each of the seven
entries is reconstructed by the specification. One unequal pair refutes that
candidate's universal claim. This is a direct finite argument, not a formal
proof of the Python interpreter or a theorem of universal grammar.

The formation check is narrow: exactly three canonical field coefficients,
the fixed domain, version and quantifier. There is no recursive parser, logical
binder, new hole type, or general syntax-formation operation.

## Three outcomes and their updates

| Event | Exact retained effect |
|---|---|
| Success | Candidate `[2,3,1]` is reached at zero-based ordinal 120, after 121 candidates; all seven inputs are checked and a scoped expression record is stored |
| Refutation | Candidate `[2,3,0]` fails at x=0: required 1, obtained 0; retain the task-bound constraint g(0)=1 |
| Zero fuel | `Unknown/fuel_exhausted`, cursor 0, unchanged constraints and word library; only the pause ledger grows |
| Three candidates, then one explicit continuation | Prefix ends at cursor 3; a separate 340-candidate allowance continues from 3 and reaches cursor 121; both ledger events and the witness remain |

The failure constraint leaves exactly 49 of the 343 triples and retains the
correct solution. The next proposal changes from `[0,0,0]` to `[0,0,1]` using
that constraint. This is an observable finite update, not a newly discovered
mathematical law. The complete enumeration in the test independently checks
the survivor count and that the solution was not removed.

The zero-fuel record proves nothing about the remaining candidates. The prefix
may retain counterexamples found before exhaustion, but exhaustion itself adds
no refutation. Search-family exhaustion is also returned as Unknown in this
implementation; there is no general no-solution certificate API.

## Zero and unit boundaries

The checked value vector is `[1,6,1,0,3,3,0]`. Pointwise differences g-f vanish
at all seven inputs. The ratio g/f is one at x=0,1,2,4,5 and is **undefined** at
x=3,6. Equality at those zeros is retained without evaluating 0/0.

These pointwise differences are not the native formation residual A from 0107.
These field ratios are not its symbolic execution transport M. In particular,
0107's concrete intermediate-zero fault discipline is not altered or bypassed
through a claimed native interface. Scalar agreement does not identify ordered
expression histories, sources, occurrences, or M6 fillings.

## Scoped word record and new-instance reuse

The external record is labelled `checked-quadratic-instance`, a descriptive
fixture label, not an additional user-approved language primitive.

- Function: retain one accepted Horner expression for later explicit substitution.
- Input/output: an accepted task-bound trial becomes a record containing its
  exact coefficients, definition, version, witness and residual.
- Scope: this expression over F7; no theorem about arbitrary future tasks.
- Refusal: missing verification points, noncanonical coefficients, stale task,
  changed definition or corrupted witness prevent admission/reuse.
- Replay: expand the coefficient triple and independently check all seven inputs.
- Residual: future targets require fresh checks; physical and native meanings
  remain unestablished.

The supplied reuse policy substitutes x+1 into the stored expression. Expansion
gives coefficients `[2,0,6]`, and fresh verification checks the new target
`2*x^2+6` on all seven inputs. The new record references the old word digest.
The old acceptance is not inherited: offering the expansion for target `[2,0,5]`
returns Refuted. Reuse is task-relative, with the substitution rule supplied
externally rather than learned from one instance.

| Route on the fresh task | Candidate trials | Qualification |
|---|---:|---|
| Lexicographic search | 105 | Elementary enumeration baseline |
| Checked expression reuse | 1 | Revalidates the source and checks the new target |
| Ordinary algebraic reuse | 1 | Same expansion and fresh target checker, without the word record machinery |

Thus the word record changes the route relative to enumeration but demonstrates
no computational advantage over ordinary algebraic reuse. No increased
expressiveness or general search acceleration is claimed.

## Costs, limits, and implementation correction

Standalone execution enforces five-second CPU and wall limits, 256 MiB address
space, at most 50,000 aggregate charged units, 343 candidates per search and a
512 KiB artifact bound. The outer command also has a five-second timeout.
There are three declared routes and one explicit continuation, with no resets
or unlimited nesting. Serialization and I/O are bounded by bytes and process
limits; work counters are abstract item counts, not CPU instructions or energy.

On Linux, Python 3.12.13, the initial construction, serialization, in-memory
parse/replay and witness-file save completed successfully:

| Observation | Result |
|---|---:|
| Build, including its nested phases | 9.215491 ms |
| Initial full search | 1.826381 ms |
| Success verification and word-record formation | 1.772011 ms |
| Fresh-task search baseline | 1.455525 ms |
| Checked reuse | 0.141449 ms |
| Ordinary reuse | 0.038727 ms |
| Serialization | 0.413580 ms |
| Parse | 0.424836 ms |
| Full artifact replay | 5.399567 ms |
| Witness-file save | 0.229408 ms |
| Total measured elapsed | 16.216859 ms |
| Aggregate charged units, including replay | 10,179 |
| Linux process peak RSS | 11,264 KiB (11 MiB) |
| Witness size | 54,445 bytes |

Build time nests the individual search/update/reuse phases; do not sum the
whole table. These are one-shot local observations, not a benchmark or a future
runtime bound. Imports, interpreter startup, research/design, source retrieval,
network persistence and cost-report writing are excluded. No physical energy,
customer effort or cost amortization has been established. Artifact size is
not memory usage. Raw counters and timings are saved separately.

Seven targeted tests passed in 0.024 seconds. Code review then found one
integration defect: applying process-wide RLIMIT_CPU/SIGALRM inside test setup
would constrain unrelated tests when collected by pytest. Those settings were
removed from test setup and remain in the standalone CLI. One correction replay
passed all seven tests in 0.024 seconds. No semantic search was enlarged, and
the deterministic artifact was unchanged. Test-process memory and aggregate
work were not measured. In-process tests have finite inputs and work charges;
process CPU/address limits apply only to the standalone CLI, not to the entire
repository pytest process. The suite was not rerun broadly and CI was not used
as a research loop.

The internal resource exception reports Unknown but does not guarantee a partial
checkpoint. Hard process termination may produce no JSON at all. Only the
observed candidate-fuel exits have verified saved continuation records. This is
an explicit remaining crash/checkpoint obligation, not a claim of perpetual
availability.

## Reproduction and evidence

From the repository root, Linux and Python 3.11 or later:

```console
timeout 5s python -m experiments.finite_learner.calibration --check examples/verified_witness/finite-learner-f7.json
timeout 5s python -m experiments.finite_learner.calibration --output /tmp/finite-learner-f7.json --cost-output /tmp/finite-learner-f7-cost.json
timeout 5s python -m unittest discover -s tests/python -p test_finite_learner.py -v
```

The committed witness SHA-256 is
`e2bff862aa78c432407c83848b7a90b202f7d281bf5f29348819eb97feef598b`.
The checker independently recomputes arithmetic entries, validates candidate
order, fuel exits, state updates, zero discipline and reuse. Transition rules
are shared with the producer, so this is not two independently implemented
state machines. Tests separately assert key expected transitions and mutations.
The existing Python CI can collect the seven tests without workflow changes;
the committed witness can be replayed by the explicit command above.

Artifacts:

- `experiments/finite_learner/calibration.py`
- `tests/python/test_finite_learner.py`
- `examples/verified_witness/finite-learner-f7.json`
- `examples/verified_witness/finite-learner-f7-cost.json`
- `examples/verified_witness/finite-learner-f7-validation.json`

## What this helps and what remains

Mingli and a subsequent agent can now inspect a concrete distinction between
forming a word, using evidence to revise a proposal, and merely running out of
fuel. They can replay the record without guessing what `judge` accepted. Jiamin
has not yet supplied a task whose practical value this fixture measures.

The intuition is supported only at this small procedural level. The central
result is evidence-bound update and fresh verification, with a negative result
against the ordinary-reuse control. It is not a completed grammar, an
irreducible vocabulary, native learning, a 0091 scope breakthrough, or a claim
that an open-world interpreter has been recovered.

The next smallest step is to specify and test a task/observer change that makes
an old constraint inapplicable, preserving its history while preventing its use
as evidence for the new task. The current stale-task rejection supplies a
starting boundary. A broader grammar or harder arithmetic problem is not needed
before that interface is explicit.
