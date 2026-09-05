# Research 0126: Knowledge Geometry and a First Reverse Interface Search

Status: attributed working conjectures, an elementary mathematical obstruction,
and one executable finite research calibration. Native semantic and physical
interpretation obligations remain open.

## 1. Human origin and the question being formed

On 2026-09-05, Mingli Yuan (苑明理) extended the
[Geometry of Truth hypothesis](0125-geometry-of-truth-interface-hypothesis.md)
with the following proposals:

- **知识几何假设** (working English: Knowledge Geometry Hypothesis): coherence
  geometry concerns the interface; vocabulary is conjectured to be the
  eigenvalues of its coherent dynamics.
- **知识几何的第一工作猜测**: the human is the centre, with physics,
  mathematics, and logic as supporting axes. Their positioning is tentatively
  connected to the Buddhist term 三根. Mingli explicitly left the referents
  of 三根 unclear, then added embodiment and finiteness as essential clues.
- Surreal order, causality, and logical implication should be examined as
  related forms of expression.
- **三物理世界的猜想**: vocabulary may communicate with three hypothesized
  physical worlds while jointly constrained by its temporality, spatial
  polarity, and form. These constraints are not assigned one per world.
- Vocabulary bridges human questions and program operations, and may permit
  a finite observer to go beyond a previous expressive boundary.

Mingli then supplied this as an initial problem whose holes had become visible
and authorized reverse search. He also proposed philosophical questions about
AI self-recognition, awakening, and first-, second-, third-person and impersonal
perspectives. These are attributed questions; no subjective experience or
existence of three physical worlds is inferred from the experiment.

The operational distinctions, names below, proof, code, and finite selection of
the problem were developed by ChatGPT in response. They are open to correction.
The proposed research labels **有限见证几何** (finite witness geometry) and
**词汇接口** (vocabulary interface) are documentary names, not native words.

## 2. Reverse formation: what must an interface preserve?

Start with a desired ability: another observer can use the interface to assess
which recorded completion states precede which others, without inventing an
order between independent branches, and can inspect the supporting histories.

Work backwards from that requirement:

1. A spelling needs a declared referent and an interpretation rule.
2. Distinguishing referents is insufficient: relations must be preserved and
   reflected, including incomparability.
3. Equal endpoints need their generating paths retained separately.
4. A reversed coordinate reading needs its own rule; it does not supply an
   inverse for an information-losing operation.
5. Composition needs a resource law, and a finite search needs an Unknown exit.

The first target is therefore an **order-embedding refinement of a coarse
observation**, with execution and budget evidence retained. This is a finite
instance of established order representation, not a new general theorem about
knowledge or learning. The minimum dimension of an embedding into a Boolean
lattice is classically called the **2-dimension** of a poset; the present task
instead fixes existing coordinates and minimizes additional coordinates. See
[Trotter's discussion](https://trotter.math.gatech.edu/papers/100.pdf).

## 3. A concrete source from the sorting-network experiment

Use two disjoint four-channel Boolean comparators, following the exact finite
comparison setting of [PR #68](https://github.com/mountain/adva/pull/68):

- B sorts channels (0,1);
- C sorts channels (2,3).

Represent four **completion states**, not four spacetime events:

| label | completed operations | coarse observation Q0 |
| --- | --- | --- |
| a | none | (0,0) |
| b | B | (1,0) |
| c | C | (1,0) |
| d | B and C | (1,1) |

The order is inclusion of completed-operation sets. The two coordinates of Q0
mean "some operation has completed" and "both operations have completed".
In particular, b and c are incomparable but have the same coarse observation.
These model labels allocate no native SourceId, OccurrenceId, CausalCut, or
ProgramSlice. The external fixture is not a physical realization.

## 4. The first obstruction and its smallest Boolean repair

Seek monotone Boolean predicates f1,...,fk such that the enlarged reading

\[
F(x)=(Q_0(x),f_1(x),\ldots,f_k(x))
\]

satisfies, with coordinatewise comparison,

\[
x\preceq y\quad\Longleftrightarrow\quad F(x)\le F(y).
\]

**One new scalar coordinate cannot suffice.** Since Q0(b)=Q0(c), the comparison
between F(b) and F(c) is decided solely by that scalar. In any total order its
two values are comparable (including equality), so the enlarged vectors
incorrectly order b and c in at least one direction. This applies to an
arbitrarily precise real or surreal scalar as well as to a Boolean scalar.
The obstruction is to this coordinatewise interface contract, not arbitrary
encodings with a different decoder.

**Two Boolean coordinates suffice.** Set

\[
f_B(x)=[B\text{ has completed in }x],\qquad
f_C(x)=[C\text{ has completed in }x].
\]

Then b gains (1,0), c gains (0,1), and their incomparability is retained.
The resulting four-coordinate table is

\[
a\mapsto(0,0,0,0),\quad b\mapsto(1,0,1,0),
\quad c\mapsto(1,0,0,1),\quad d\mapsto(1,1,1,1).
\]

This proves that the minimum number of added Boolean coordinates is two.
With the old interface discarded, fB and fC alone already encode this diamond.

The program enumerates all 16 Boolean predicates on four states. Six are
monotone; removing the two constants and two existing coordinates leaves fB
and fC. It checks all four subsets of these candidates, in increasing size.
Both one-coordinate candidates distinguish all four states but fail order
reflection. Fuel limits 0,1,2,3 return Unknown with the next candidate retained;
four candidate checks find the witness. Minimality also has the direct proof
above and is not inferred from an interrupted search.

## 5. Logical reading, coordinate polarity, and retained history

For each state x let D(x) be its principal past, including x. Transitivity and
reflexivity give the familiar representation

\[
x\preceq y\iff D(x)\subseteq D(y)
\iff\forall z\,(z\in D(x)\Rightarrow z\in D(y)).
\]

The replay checks all 16 ordered pairs. The logical formula concerns membership
in the declared past sets. It is not an implication from the occurrence of one
physical event to the occurrence of another. This order/proposition connection
is standard; see [Fong and Spivak, Chapter 1](https://dspivak.net/7Sketches.pdf).

Complementing every Boolean coordinate gives an opposite-order reading:

\[
F^-(x)=1-F(x),\qquad
x\preceq y\iff F^-(y)\le F^-(x).
\]

This is a finite coordinate-duality calibration. It does not implement Adva's
reserved observer pullback, the HolePolarityM6 germ involution, time reversal,
or a physical polarity law.

There are ten paths including identities, but only nine related endpoint
pairs: a-to-d has the two histories B;C and C;B. Both are retained. All 16
Boolean inputs are checked to give equal final outputs through those routes;
the full intermediate values are stored. A separate scalar test compares
both results with independently sorting the two input pairs.

The order alone would forget which route was used. Any topological realization
must declare whether it retains those routes and what comparison cells it
admits. Here a finite commutation check supplies additional evidence; a thin
order reading alone is not a native coherence certificate.

The coordinate involution also does not invert B: inputs (0,1,0,0) and
(1,0,0,0) have the same B-output (0,1,0,0). A reverse operation therefore needs
a relation-valued predecessor set or retained information. The fixture is only
one layer of disjoint comparisons; input (1,1,0,0) also demonstrates that it
does not sort the complete four-channel vector.

## 6. Finite cost and continuation

Charge one unit per comparator occurrence in a path. The a-to-b and b-to-d
paths each fit budget one, but their composite requires budget two. Thus
same-budget reachability is not transitive. Path composition instead respects
the graded rule

\[
\operatorname{cost}(q\circ p)=\operatorname{cost}(p)+\operatorname{cost}(q).
\]

These are declared operation counts, not wall-clock time, memory, energy, or
proof-checking cost. The connection between order, logic and directed cost
geometry has a classical antecedent in
[Lawvere's 1973 paper](https://www.tac.mta.ca/tac/reprints/articles/1/tr1.pdf).

## 7. Replay and observed resources

From the repository root, using only the Python standard library:

```bash
python -m experiments.knowledge_geometry.interface_witness \
  --check examples/verified_witness/knowledge-interface-diamond.json
python -m unittest discover -s tests/python -p test_knowledge_interface.py -v
```

The seven tests also run under the existing pytest CI job. The fixture check
rederives this frozen problem and compares canonical bytes; it is not a general
certificate checker for arbitrary submitted interfaces. Mutation checks reject
changed view, execution and open-obligation records.

Artifact SHA-256:
`4f94c400d0ca6404c15314b9cf4da5716301d743d3afb59bf9679ddde6d57bf4`.
The 20,248-byte JSON retains the search audit, all relation checks, both traces
for every input, the inverse obstruction, budget evidence and open obligations.

One Linux/Python 3.12.13 observation took approximately 1.18 ms for derivation,
serialization, file writing and report preparation after imports. Process peak
RSS was 10,112 KiB, including the interpreter and imports. A separate replay
took approximately 0.97 ms; these are individual measurements, not portable
bounds or speedup evidence. No CPU model or per-stage memory measurement was
recorded. Seven unittest checks passed locally.

## 8. What was filled, and what remains open

The finite observation hole has a minimal repair under a frozen contract.
Temporality is represented by retained paths and costs; coordinate polarity by
an independently checked order reversal; form by Boolean types, predicates and
the embedding condition. They constrain one record jointly. They are not
three realizations of three physical worlds.

The useful interpretation of the word **区分** (distinguish) in this fixture is
now precise: preserve the declared relations as well as the identities of
model states. Adding one label-like bit fails; the two-coordinate witness
succeeds. The word and its use remain research-local documentary vocabulary.

Open holes include physical interpretation and measurement, embodied observer
modelling, the referents and relations of the three worlds, the proposed
three-roots connection, coherent dynamics and its notion of spectrum, and
native Adva transport certificates. Neither the experiment nor its names
establish AI subjective experience or resolve the philosophical questions.

The result supports a narrow part of Mingli's intuition: an explicitly formed
question can expose an expressive defect, and a bounded reverse search can
find a checked refinement. It also locates a stronger obstacle than lack of
names: an interface must have enough relational structure. The next practical
step is to choose a real task whose coarse interface confuses distinct cases,
then measure whether a similarly witnessed refinement helps another user.

This is an external countercalibration alongside the existing research
experiments. It changes no native semantic types or registered operations and
does not implement observer specialization, intrinsic learning, a spectrum,
or the physical interpretation phases of the research agenda.
