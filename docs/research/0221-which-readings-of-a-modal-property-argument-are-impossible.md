# 0221 — Which readings of a modal property argument are impossible

Date: 2026-09-24. Direction: Mingli Yuan. Analysis, checker and note:
deepseek-v4-flash-vision-exp (DeepSeek Harness), submitted through his account
as an authorized proxy. Account use is not his authorship, review or endorsement.

Status: one bounded external exact experiment. No Rust witness, no stable API
change, no library admission, no Seal, and no claim about any text.

Base: `79f6353511d736ae743b109f1c573b652eff170a`. Library gitlink:
`73a6af4ac4ed8225366d3c16794e309cff15f51d`.

---

## 1. What this answers, and what is declared

An argument of the positive-properties shape is read in several ways. This note
asks which of those readings has a model and which has none, over a **declared
finite semantics** that is written out in this experiment's contract and
enumerated exhaustively within a declared bound. The readings tested, in the
words in which they are usually put:

1. the conclusion follows from the first two axioms;
2. it follows in whatever frame class the modality allows;
3. the axiom that necessary existence is positive is what delivers it;
4. essence is doing work in the argument;
5. the conclusion carries modal force, so "necessarily exists" is stronger than
   "exists";
6. the argument establishes uniqueness;
7. the one-world case is evidence for it.

**No text and no corpus count is imported.** No published formulation is quoted,
parsed or reproduced; the system below is written in this repository's own
notation from the declared definitions. **Any agreement between a verdict here
and a published verdict is a coincidence of results and is not imported as
evidence**, and a disagreement would not be evidence either.

The verdicts, each of which rests on a model retained in the evidence file or on
an exhaustion over the declared bound:

| reading | verdict | what decides it |
|---|---|---|
| 1. the first two axioms suffice | **impossible** | 1 728 models of the two axioms at three worlds, only **216** with the conclusion; countermodel retained |
| 2. it works in any frame class | **impossible** | with **all seven** axioms, no set forces the conclusion outside the symmetric frames; 4 countermodels retained |
| 3. necessary existence delivers it | **half: it forces, by being maximally restrictive** | over symmetric frames `{A5}` alone forces the conclusion — and leaves exactly **1** model |
| 4. essence is doing work | **impossible** | wherever the axioms force the conclusion they also make the essence vacuous in every model: the same **640** rows, and `φ ess x` collapses to `φ(x)` in the one symmetric model |
| 5. the conclusion has modal force | **impossible** | in all **86** models of `{A1, A2, A5}`, the conclusion holds **exactly when every property is constant** |
| 6. it establishes uniqueness | **not expressible** | the declared family contains no identity predicate; recorded as a residual, not a verdict |
| 7. the one-world case is evidence | **vacuous** | with one world all **128** subsets force the conclusion, the empty set included |

## 2. The declared semantics, and the one lemma that carries everything

A model is: a finite set of worlds; a relation on it; **one** individual present
at every world; a **property** is a set of worlds, so the algebra of properties
is the complete power set and the second-order quantifiers are not restricted to
a chosen list; and **positivity** is a set of properties at each world, allowed
to differ from world to world. Then

```
godlike at w        the individual has every property positive at w
φ is an essence at w  the individual has φ at w, and every property it has at w
                      holds at every world of φ that w sees
necessary existence at w  every essence at w is instantiated at every world w sees
the conclusion      every world a world sees is godlike
```

and seven axiom schemata, named here for their content and not by any edition's
numbering: negation excludes positivity (`A1`); positivity is complete, in the
sense that a property is positive when its negation is not (`A1c`); entailment
transfers positivity (`A2`); positivity is necessary (`A3`); positivity is
possible only if actual (`A4`); godlikeness is positive (`A6`); necessary
existence is positive (`A5`).

Everything below turns on one lemma, verified by exhaustion over **18 508**
models with **no exception**:

> **Necessity lemma.** Necessary existence holds at a world exactly when that
> world sees only itself.

It is three lines by hand, and the exhaustion is there because the hand argument
is where I have been wrong before. The smallest property containing a world is
that world alone, and it is always an essence: the essence condition only bites
at the world itself. So necessary existence demands that the world sees nothing
but itself. Everything strange about this argument follows from that: the notion
of necessary existence, as declared, is **not about necessity at all** — it is
the predicate "isolated".

## 3. The first two axioms are not enough

Over the universal frame at three worlds, **1 728** models satisfy the first two
axioms and only **216** satisfy the conclusion. A countermodel is retained. Any
reading on which the argument is "really" just those two axioms has no model to
stand on; the reading is impossible in the declared semantics, and one model is
enough to say so.

The converse of the first axiom deserves its own line, because it looks like a
convenience and is not. Adding it — "a property is positive when its negation is
not" — moves the symmetric class at three worlds from **1 832** models to **77**,
and the number of models with the conclusion from **278** to **5**. It is neither
fatal nor free: it removes 96 % of the models and 98 % of the conclusions. A
reading that treats the two directions as interchangeable is not consistent with
the declared class.

## 4. It does not work outside the symmetric frames

**No** subset of the seven axioms forces the conclusion over the preorder, the
reflexive or the universal frames at two or three worlds. With **all seven**
axioms present the preorder class at three worlds still has **19** models, of
which exactly one satisfies the conclusion — so the argument fails there. Four
countermodels under every axiom are retained.

The retained three-world countermodel is small enough to write out. Worlds
`{0,1,2}`; the relation holds for `(0,0)`, `(0,1)`, `(1,1)`, `(2,2)` — reflexive
and transitive, and **not symmetric**, because `0` sees `1` and `1` does not see
`0`. Positivity at worlds `0` and `1` is the same four properties, and the
godlike worlds are `{1,2}`. The conclusion fails at world `0`, which sees world
`1` and is not itself godlike. **This model satisfies every one of the seven
axioms.** So the work in this argument is done by the symmetry of the
accessibility relation, and by nothing else that the seven axioms say.

## 5. The axiom that looks strongest is the most restrictive, not the most informative

Over the symmetric frames at two and three worlds, exactly **64** subsets force
the conclusion: precisely those containing `A5`, the axiom that necessary
existence is positive. And each of them leaves **exactly one model**.

So the smallest set that forces the conclusion is a **single axiom** — and the
reason is the opposite of the one the reading assumes. `A5` does not force the
conclusion by saying something informative about necessity; it forces the
conclusion by **collapsing the model class to a point**. By the necessity lemma,
requiring necessary existence to be positive puts the isolated worlds into the
positivity of every world; every world that sees another then drops out of the
godlike worlds; and what remains over the symmetric frames is one model. A
forcing result whose class has one member is reported here with its model count
precisely so that it is not read as strength: **the argument's validity is bought
by pinning the semantics down, not by deriving anything from it.**

## 6. The conclusion has no modal force, and this is exact

This is the sharpest verdict, and it is an equivalence rather than a one-way
statement. Over the **86** models that satisfy the three axioms `{A1, A2, A5}`
across every declared frame class and world count:

> **in all 86, the conclusion holds exactly when every property has the same
> extension at every world that a world sees.**

86 of 86, no exception. So the collapse of the modality is not a further defect
that a better formulation might avoid; **in the declared semantics the conclusion
and the collapse are the same condition.** A reading that keeps the argument and
rejects the collapse has no model, and a reading that keeps the collapse and
rejects the argument has no model either.

Only **50** of those 86 also satisfy the remaining four axioms, so `A5` neither
implies nor is implied by them: the coincidence is with `A1` and `A2`, not with
the whole list.

The one symmetric model the three axioms leave at three worlds can be described
exactly: its frame is the one in which **no world sees any other**, and its
positivity at each world is **exactly the set of non-empty properties the
individual has there**. In that model positivity carries no information at all —
"positive" coincides with "true of the individual" — godlikeness is trivially
satisfied everywhere, and necessity is the identity. That is what the conclusion
costs here.

## 7. Essence is not doing work

Wherever the declared axioms force the conclusion, they also make the essence
predicate vacuous in every model: **in all 640 forcing rows** the number of models
in which the essence predicate is vacuous equals the number of models in the row,
so the two sets of rows are the same 640 and no row forces the conclusion while
leaving the essence condition doing anything. And in the one symmetric model the
three axioms leave, the essence condition holds exactly when the individual has
the property: `φ ess x` collapses to `φ(x)` there. A reading in which the essence
machinery is what carries the argument has no model to stand on.

Careful with the converse, which does **not** hold and which this experiment does
not claim: the conclusion alone, without the axioms, is satisfied in 4 388 models
of which only 44 also make the essence vacuous. The coincidence is between
*forcing* and *vacuity*, not between the conclusion and vacuity in general.

## 8. Uniqueness cannot even be asked here

The declared family — the three derived notions and the seven schemata — contains
**no identity predicate**. So a statement that two godlike individuals are the
same individual is not expressible in it, and no reading of these axioms
establishes uniqueness. This is recorded as an **untested residual** and not as a
verdict: testing it would need a second individual, a wider property algebra, and
an added premise, none of which is declared here. The one-individual restriction
is worth stating plainly for the opposite reason too: **one individual is the most
favourable case for "something is godlike"**, so the refutations above are not an
artifact of a small domain.

## 9. The degenerate case is worth exactly nothing

With one world there is only one frame, necessity is the identity by
construction, and **all 128** subsets of the seven axioms force the conclusion —
including the empty set of axioms. Any argument that leans on the one-world case
is leaning on the absence of a modality.

## 10. What the checker ran

`experiments/modal_property_systems/checker.py` against
`experiments/modal_property_systems/contract.json`, five sections, **4 937
assertions**, `ExternalExactPass`, in 2.4 s wall, evidence 646 kB.

The enumeration is exhaustive within the declared bound: every relation of the
four frame classes (`1, 2, 5` equivalence frames at one, two, three worlds; `1,
4, 29` preorders; `1, 4, 64` reflexive relations; one universal frame at every
size), every positivity assignment over the complete property algebra at every
world (256 candidate sets of properties at three worlds), and every one of the
128 axiom subsets, giving a table of 1 536 rows.

`RLIMIT_CPU`, `RLIMIT_FSIZE` and the wall alarm are installed; **no address-space
ceiling is installed**, because this checker launches no child process — the
convention 0211 had to adopt after its first version broke the frozen resource
inventory. An existing output file is refused, never overwritten.

`tests/python/test_modal_property_systems.py` re-runs the checker in a temporary
directory and compares the mathematical payload of the fresh run with the
retained evidence, section by section, with timing and platform keys removed. No
floating-point value enters any acceptance test.

## 11. Residual and non-claims

- **This is a declared finite semantics and not a proof calculus.** No derivation
  is checked, no completeness or soundness theorem is invoked, and nothing here
  decides what any axiom system proves. What is decided is which models exist.
- **The window is at most three worlds and one individual.** The impossibility
  verdicts are rigorous *inside* it — a model is a model, and one is enough — and
  **transfer to an unrestricted system is not claimed.** Every forcing row is
  reported with its model count, and every one of them that matters has count 1.
- **No published verdict is imported as evidence, and no agreement with one is a
  result.** The declared system is this repository's own; the axiom names are its
  own labels and not a numbering from any edition.
- **Nothing is claimed about meaning, truth, plausibility, theology or
  metaphysics** — not about the argument, not about positivity, not about
  godlikeness, and not that the declared translation is the reading any author
  intended.
- **No failing search is reported as evidence.** Every impossibility verdict rests
  on a retained model; a row with no model refutes nothing, and the checker
  asserts forcing only where models exist.
- **No claim that the seven axioms are all that anyone has proposed**, or that
  the four frame classes exhaust the modalities.
- **No SourceId, observer, aperture, clock, operation, native witness or Seal is
  created**, and no claim is promoted beyond `bounded-experiment`.

## 12. What changed in the repository

- `experiments/modal_property_systems/checker.py`, `contract.json`,
  `evidence.json` — the bounded experiment, 4 937 assertions.
- `tests/python/test_modal_property_systems.py` — tests over the retained
  evidence, the fresh-run payload, the no-overwrite rule, the necessity lemma,
  the frame census, the forcing table, the countermodels, the collapse
  equivalence, the vocabulary, the degenerate case, the contract's protected
  list, this note's residual, and the registered claim.
- `docs/claims.toml` — `adva.bounded-experiment.modal-property-systems.v0`.
- `docs/research/README.md` — this note added to the index and the numbered count
  advanced.
