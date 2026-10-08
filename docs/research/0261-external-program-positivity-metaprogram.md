# Research 0261 — An external program positivity metaprogram

## Question and implemented level

Research 0260 decided an explicit finite positivity problem after one arithmetic
example and its regions had already been frozen. The present question is whether
the arithmetic program itself can become input: can one tool execute distinct
program descriptions, derive their observed regions, and decide positivity
entailment under separately supplied premises and a policy?

The implementation is an external, bounded metaprogram:

\[
M(\mathrm{program},\mathrm{fillings},\mathrm{observers},\Gamma,
  \mathrm{policy},\mathrm{queries},\mathrm{fuel})
\longmapsto \mathrm{report}.
\]

It interprets a strict rational SSA data grammar, rather than a fixed region mask
table. The finite carrier and positivity theory are explicit inputs. It retains
evidence that can be challenged with a second implementation. Python provides
external arithmetic and set-theoretic calibration only: no native Adva term,
source, occurrence, history, cell, certificate, communication operation or Seal
is created. The host has no Rust toolchain or native extension; native execution
is recorded as unavailable.

The source lives in `experiments/program_positivity/`; the public entry points
are `meta.py`, `verifier.py`, and `run_campaign.py`. The contract was written
before semantic execution. The exact source/fixture hashes and aggregate costs
are retained by the campaign. This note is a research record, not a stable API.

## Input language and retained distinction

A request declares up to eight holes, 64 ordered arithmetic steps, eight outputs,
four fillings, eight observations, sixteen named Boolean properties and sixteen
queries. Each step is `{name, op, args}`. Operations are rational constant,
negation, addition, subtraction, multiplication and division. Arguments refer
only to prior steps, holes or canonical reduced rational literals. A divisor
must be nonzero on every supplied filling.

Comparisons `eq/ne/lt/le/gt/ge` and Boolean predicate trees produce observations.
Boolean region expressions can reference observations, other properties and
`all/empty`; forward references are allowed only in an acyclic property graph.
Optional domain guards must hold at every declared filling. A failed guard does
not quietly delete a point and change the question.

The carrier is the ordered set of supplied trial indices. Equal coordinate
dictionaries may remain distinct indexed trials. Arithmetic equality therefore
does not implement an observational quotient or authorize a native identity.
If the same observations cannot distinguish two trials, that limitation stays
visible in their incidence. The full powerset remains the declared positivity
property domain, including regions the observer vocabulary does not name.

The canonical JSON request digest binds the question. Step arrays, hole arrays,
trial ordering, query ordering, policy and signed premises are included. Source
and contract digests bind the producer implementation. There is no host `eval`,
arbitrary import, executable callback or native diagram decoding.

## The finite positivity decision

For a carrier \(C=\{0,\ldots,n-1\}\), a model is a family
\(\mathcal P\subseteq\mathcal P(C)\) satisfying:

\[
P(C\setminus S)\iff\neg P(S),\qquad
P(S)\land S\subseteq T\Rightarrow P(T).
\]

These are static finite A1 and A2. They do not implement the necessary modality,
God-likeness predicate, necessary existence, or full Gödel–Scott A1–A5.
Positive and negative premises constrain membership of named regions. The
`basic` policy adds no other requirement. `joint` requires
\(\bigcap\mathcal P\ne\varnothing\); `marked` requires a declared trial
\(c\in\bigcap\mathcal P\).

The producer chooses one element of every complementary region pair and checks
upward closure. There are \(2^{2^{n-1}}\le256\) such candidates. Every A1 model
appears exactly once in that census; the inclusion check removes exactly those
that violate A2. The policy and signed premises then filter the survivors.
This establishes a complete finite search when the report says `Analyzed`.

Under the common-witness policy, every surviving family is principal. If
\(c\in\bigcap\mathcal P\), then \(P(S)\Rightarrow c\in S\). Conversely, if
\(c\in S\) and \(\neg P(S)\), A1 makes \(C\setminus S\) positive, contradicting
the common-witness requirement. Thus \(P(S)\iff c\in S\). This is why choosing a
marked witness fixes positivity, and why demanding a witness is an additional
condition rather than a consequence of static A1/A2 alone.

For each query, all survivors are inspected. All-positive gives
`ForcedPositive`, all-negative `ForcedNegative`; two kinds of surviving model
give `Underdetermined` with both model indices. An empty model class gives
`Inconsistent`, rather than claiming both positive and negative by explosion.
The report separately records whether the region has trial inhabitants.
Neither inhabitation nor positive classification is silently substituted for
the other.

`Unknown` is a computational or coverage limitation. It differs from
`Underdetermined`, which requires a completed census with opposing witnesses.
Invalid input, an unsupported operation, an undefined divisor or budget
exhaustion cannot expose a partial census as complete and cannot produce a
decisive query result.

## Independent receiving and ways to challenge the tool

The receiver imports no producer functions. It reconstructs and validates the
request independently, evaluates expression dependencies recursively with exact
rationals, and derives region incidence with ordinary sets. For each carrier
size it enumerates all families of subsets, checks A1 and A2 directly, and caches
the resulting immutable families without resetting its cumulative fuel.
Across sizes one through four, there are at most 65,812 raw families to inspect.

For an `Analyzed` report it checks exact arithmetic traces, output values,
observations, guards, regions, the complete surviving model class, realizers,
query counts, classification and witness indices. Producer model ordering is
allowed to differ from receiver enumeration, but membership, uniqueness and
every referenced index must agree. A division failure is checked at its exact
filling and step. Conservative incomplete reports are classified `NoClaim`;
that outcome verifies withholding, not the diagnostic reason or a mathematical
negative result. The exact receiver results are retained by the campaign.

The tests vary actual programs and carrier sizes, transport the reversed chart,
and mutate an output, region, model, witness and request binding. The purpose is
to make the report an inspectable object that can fail independent receiving.
The receiver shares the declared mathematical assumptions, so agreement does
not independently justify a policy's philosophical meaning.

## Frozen experiment

The campaign uses fourteen predeclared requests. The Möbius source computes
\(p=ax+b\), \(q=ay\), \(d=p^2+q^2\),
\(r=-p/d\), \(s=q/d\). Its observers are

\[
B:\ r^2+(s-1/2)^2<1/4,\qquad H:\ s>1/4.
\]

The four source fillings are exactly those in Research 0260. The target request
receives \((a,b,p,q)\) directly in reversed order and computes the same inverse
chart. The program descriptions differ while the declared observer regions
transport by the exact permutation. The common-realizer index must transport
with the point, not stay attached to an old ordinal.

Other requests compute a square, negative identity and identity on carriers of
one and two trials. They also exercise zero division, zero fuel, an unsupported
loop operation, an invalid arithmetic forward reference and contradictory
signed premises. The loop is data outside the grammar; no loop is run.

The contract permits two producer launches (ordinary Python and `-O`), one
receiver launch, one unit-test launch and one overwrite-refusal launch. The
single supervisor enforces 60 seconds wall time, 45 seconds aggregate CPU,
256 MiB address space, twelve seconds per child, one MiB per output file and
sixteen MiB total retained output. Logical producer fuel is at most 200,000 per
request and receiver fuel at most ten million. All checking is included. A
failure ends the campaign; no automatic retry or scope widening occurs.

The one campaign **passed**, with five launches and no retries. Wall time was
1.082009 seconds; parent plus child CPU was 0.986970 seconds. Both producer
runs consumed 43,424 logical fuel across fourteen requests. Their output was
byte-identical, with SHA-256
`75f42628076452a734bc0265f52ecedaeafc62d560d623b6f8705e46ed0cab65`.
Only one copy is retained as `evidence.json`; `campaign.json` retains both
digests, source bindings, receiving outcomes and launch logs.

Ten requests were `Analyzed`, with fifty completely checked query results.
The independent receiver also verified the exact division-by-zero witness.
Zero fuel, the unsupported loop and the forward reference were respectively
`Unknown`, `Unsupported` and `InvalidInput`, received as `NoClaim` rather than
semantic theorems. Its census visited 65,556 raw families for carrier sizes
one, two and four, consuming 1,044,185 of ten million fuel. Size three is
supported by the grammar but was not exercised in this campaign.

| Request | Retained result |
| --- | --- |
| Möbius, basic A1/A2, positive B and H | Three models; positivity of B intersection H is underdetermined |
| Same program, joint policy | One model with realizer 2; the intersection is forced positive |
| Reversed target chart | Same classifications; realizer transports to index 1 |
| Basic, additionally positive B xor H | One nonprincipal model with no common realizer; the inhabited intersection is forced negative |
| Same three premises, joint policy | No model; every query is inconsistent |
| Square, marked trial x = 1 | Output-positive region forced positive; output greater than 1 forced negative |
| Negative identity, same marked trial | Output-positive region forced negative |
| Direct positive/negative conflict | No model; every query is inconsistent |
| Zero divisor, zero fuel, unsupported loop, forward arithmetic reference | Explicit distinct program statuses; no decisive positivity query |

All nine unit tests passed, within nineteen producer and twelve receiver calls.
They include changing multiplication to addition in actual program input:
the output-greater-than-one query changes from forced negative to forced
positive at the same marked trial. Four semantic mutations and one substituted
request were rejected. Existing output was refused with exit 2. These are
finite executable checks, not a claim of an unrestricted decision procedure.

## Relation to Henkin, projective duality and Rice

The report separates a region, its inhabitants, the choice of a witness and
transport of that witness. This is the useful Henkin connection: when the
declared model has a witness, it can be named and checked. The program does not
manufacture a witness for an empty region or inconsistent premises. In
particular, requiring a common positive witness can eliminate a basic model.

The process–neighborhood relation is represented here only by a finite
program-to-observation incidence map and a checked coordinate permutation.
That is an external calibration of a conditional transport question. It does
not establish the projective groupoid duality, higher coherence, faithfulness,
universality or native observer pullback \(D^*\). Those remain the obligations
described in Research 0259. Universality may be proposed as a named positive
property only after its meaning and finite observation are declared; the tool
does not infer normative positivity from a geometric encoding.

The metaprogram genuinely receives programs, but only a terminating rational
data fragment. A complete decision on that bounded fragment is compatible with
Rice's theorem. Extending it to all partial computable programs, with a fixed
nontrivial extensional property and an always-terminating correct binary
answer, is a different requirement. Changing representation to arithmetic or
geometry cannot by itself satisfy that requirement. More general inputs must
retain explicit unsupported, unknown or conditional outcomes unless a new
decidable fragment and checker are established.

Wu-style algebraic elimination and Yang-style sign decomposition could provide
future certificates beyond a supplied finite carrier. This implementation does
not claim either algorithm. A finite observation census does not prove a sign
condition over every real filling. The next useful extension is a separately
bounded certificate profile with explicit domain guards and an independent
receiver, rather than an unrestricted decision promise.

## Evidence and references

- `experiments/program_positivity/contract.json`: pre-execution question,
  assumptions, grammar, controls, budgets and protected obligations.
- `experiments/program_positivity/{meta.py,verifier.py,run_campaign.py}`:
  original implementation and supervisor.
- `experiments/program_positivity/{cases.json,examples/,evidence.json,campaign.json}`:
  original rational fixtures and retained external outcomes.
- `tests/python/test_program_positivity.py`: program, transport and mutation checks.
- `docs/research/0260-finite-positivity-program-on-equivalent-multihole-spaces.md`
  at Adva commit `16635439dcab19fded4abd0faaa5449745e4304b`: preceding fixed example.
- `docs/research/0259-henkin-witness-completion-and-process-neighborhood-duality.md`
  at the same commit: conditional witness transport and unresolved native obligations.
- `mountain/adva-machine`,
  `spec/framework/kernel-package-boundary-v0.1.md` at
  `acfc9806fe18a36d0f7194dcc196a380b2834adf`: explicit profile/receiving boundary.

Authored by Codex (OpenAI), contributed under Unknown v0.3 through Mingli Yuan's
authorized account proxy. Account use is not Mingli's authorship, review,
endorsement or a correctness guarantee. Claims above remain open to challenge
through their retained requests, checks, witnesses and residuals.
