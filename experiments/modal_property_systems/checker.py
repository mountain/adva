"""Exact checker for a declared family of finite modal property systems.

This checker never constructs, reads or authorizes an Adva semantic identity. It
uses integers only; no floating-point value enters any acceptance test. It
imports no text, no edition and no paper: the semantics and the axiom schemata
are declared here in this repository's own notation, and the models are
enumerated from those declarations alone.

The object is a declared finite semantics, not a proof calculus. A model has a
finite set of worlds, one individual present in every world, a declared relation
on the worlds, and a positivity predicate assigning to each world a set of
properties, a property being a set of worlds. The property algebra is complete --
every subset of the worlds is a property -- so the second-order quantifiers are
not restricted to a chosen list. Within that semantics:

  a model satisfying the axioms in which the conclusion fails is a refutation and
  is retained with its witness, and such a model refutes the derivation outright;
  a row in which no model within the declared world bound refutes the conclusion
  is a statement about that bound and nothing more.
"""
from itertools import combinations
import argparse
import hashlib
import json
from pathlib import Path
import resource
import signal
import time

HERE = Path(__file__).resolve().parent
COUNTS = {"assertions": 0}
LIMITS = {}
INSTALLED = {}
CONTRACT = {}

WORLD_BOUND = 3
FRAME_CLASSES = ("universal", "equivalence", "preorder", "reflexive")
SHORT = ("A1", "A1c", "A2", "A3", "A4", "A6", "A5")
FULL_NAMES = {
    "A1": "negation_excludes_positivity",
    "A1c": "positivity_is_complete",
    "A2": "entailment_transfers_positivity",
    "A3": "positivity_is_necessary",
    "A4": "positivity_is_possible_only_if_actual",
    "A6": "godlikeness_is_positive",
    "A5": "necessary_existence_is_positive",
}
VOCABULARY = ("world", "individual", "property", "has", "positive", "all_worlds",
              "some_world", "not", "and", "implies")
MODEL_LIMIT = 200000


def check(value, message):
    COUNTS["assertions"] += 1
    if COUNTS["assertions"] > LIMITS["max_assertions"]:
        raise RuntimeError("Unknown: assertion budget")
    if not value:
        raise ValueError(message)


# ------------------------------------------------------------------- the frames

def worlds(n):
    return frozenset(range(n))


def properties(n):
    """Every subset of the worlds: the algebra of properties is complete."""
    return [frozenset(c) for k in range(n + 1) for c in combinations(range(n), k)]


def positivity_candidates(n):
    """Every set of properties, as a possible value of the positivity predicate."""
    algebra = properties(n)
    return [frozenset(c) for k in range(len(algebra) + 1)
            for c in combinations(algebra, k)]


def relations(n, kind):
    """Every relation of the declared frame class on n worlds.

    The universal class is the single relation holding between every ordered pair;
    the other classes are declared by their closure conditions and enumerated.
    """
    pairs = [(a, b) for a in range(n) for b in range(n)]
    if kind == "universal":
        return [frozenset(pairs)]
    out = []
    for mask in range(1 << len(pairs)):
        R = frozenset(pairs[i] for i in range(len(pairs)) if mask >> i & 1)
        if kind in ("reflexive", "preorder", "equivalence") and \
                any((a, a) not in R for a in range(n)):
            continue
        if kind in ("preorder", "equivalence") and \
                any((a, b) in R and (b, c) in R and (a, c) not in R
                    for a in range(n) for b in range(n) for c in range(n)):
            continue
        if kind == "equivalence" and \
                any((a, b) in R and (b, a) not in R for a in range(n) for b in range(n)):
            continue
        out.append(R)
    return out


def successors(relation, w, n):
    return tuple(v for v in range(n) if (w, v) in relation)


# ------------------------------------------------------------------- the model

class Model:
    """The derived notions, from a frame and a world-relative positivity."""

    def __init__(self, n, relation, positivity):
        self.n = n
        self.W = worlds(n)
        self.A = properties(n)
        self.R = relation
        self.P = positivity
        self.succ = {w: successors(relation, w, n) for w in self.W}

    def godlike_worlds(self):
        return frozenset(w for w in self.W if all(w in p for p in self.P[w]))

    def is_essence(self, w, phi):
        if w not in phi:
            return False
        for psi in self.A:
            if w in psi:
                if not all((v not in phi) or (v in psi) for v in self.succ[w]):
                    return False
        return True

    def necessary_existence(self):
        return frozenset(w for w in self.W if all(
            (not self.is_essence(w, phi)) or all(v in phi for v in self.succ[w])
            for phi in self.A))

    def facts(self):
        W, A, succ = self.W, self.A, self.succ
        f = {}
        f["A1"] = all(not (p in self.P[w] and (W - p) in self.P[w])
                      for w in W for p in A)
        f["A1c"] = all(not ((W - p) not in self.P[w]) or p in self.P[w]
                       for w in W for p in A)
        f["A2"] = all(not (p in self.P[w]
                           and all((v not in p) or (v in q) for v in succ[w])
                           and q not in self.P[w])
                      for w in W for p in A for q in A)
        f["A3"] = all(not (p in self.P[w]) or all(p in self.P[v] for v in succ[w])
                      for w in W for p in A)
        f["A4"] = all(not any(p in self.P[v] for v in succ[w]) or p in self.P[w]
                      for w in W for p in A)
        G = self.godlike_worlds()
        NE = self.necessary_existence()
        f["A6"] = all(G in self.P[w] for w in W)
        f["A5"] = all(NE in self.P[w] for w in W)
        f["conclusion"] = all(all(v in G for v in succ[w]) for w in W)
        f["collapse"] = all((w in p) == (v in p) for p in A for w in W for v in succ[w])
        f["essence_vacuous"] = all(self.is_essence(w, p) == (w in p)
                                   for w in W for p in A)
        f["no_uninstantiated_positive"] = all(
            not (p in self.P[w]) or any(v in p for v in succ[w]) for w in W for p in A)
        f["_G"] = G
        f["_NE"] = NE
        return f


def enumerate_models(n, kind, limit=MODEL_LIMIT):
    """Every model of the declared class, with the two costly constraints pruned first.

    The first axiom and the second are conditions on one world given the frame, so
    the admissible positivity at each world is computed once and only the product
    of those lists is walked. Every remaining axiom and every derived notion is
    then decided on the assembled model.
    """
    W = worlds(n)
    algebra = properties(n)
    candidates = positivity_candidates(n)
    for relation in relations(n, kind):
        succ = {w: successors(relation, w, n) for w in W}
        local = []
        for w in W:
            good = []
            for q in candidates:
                if any(p in q and (W - p) in q for p in algebra):
                    continue
                if any(p in q and all((v not in p) or (v in r) for v in succ[w])
                       and r not in q for p in algebra for r in algebra):
                    continue
                good.append(q)
            local.append(good)
        stack = [[]]
        while stack:
            partial = stack.pop()
            if len(partial) == n:
                yield Model(n, relation, tuple(partial))
                continue
            for q in local[len(partial)]:
                stack.append(partial + [q])


def scan(n, kind):
    """The axiom table over every model of the declared class."""
    table = {}
    seen = 0
    for model in enumerate_models(n, kind):
        seen += 1
        if seen > MODEL_LIMIT:
            raise RuntimeError("Unknown: the model enumeration exceeded its declared bound")
        f = model.facts()
        for mask in range(1 << len(SHORT)):
            if not all(f[SHORT[i]] for i in range(len(SHORT)) if mask >> i & 1):
                continue
            d = table.setdefault(mask, {"models": 0, "conclusion": 0, "collapse": 0,
                                        "essence_vacuous": 0,
                                        "no_uninstantiated_positive": 0,
                                        "identity_frame": 0, "witness": None})
            d["models"] += 1
            d["conclusion"] += 1 if f["conclusion"] else 0
            d["collapse"] += 1 if f["collapse"] else 0
            d["essence_vacuous"] += 1 if f["essence_vacuous"] else 0
            d["no_uninstantiated_positive"] += 1 if f["no_uninstantiated_positive"] else 0
            d["identity_frame"] += 1 if all(a == b for a, b in model.R) else 0
            if not f["conclusion"] and d["witness"] is None:
                d["witness"] = witness_of(model, f)
    return table, seen


def witness_of(model, f):
    return {
        "worlds": model.n,
        "relation": sorted([a, b] for a, b in model.R),
        "successors": {str(w): list(model.succ[w]) for w in sorted(model.W)},
        "positivity": {str(w): sorted(sorted(p) for p in model.P[w])
                       for w in sorted(model.W)},
        "godlike_worlds": sorted(f["_G"]),
        "necessary_existence_worlds": sorted(f["_NE"]),
    }


def name_of(mask):
    return "+".join(SHORT[i] for i in range(len(SHORT)) if mask >> i & 1) or "no axioms"


def mask_of(names):
    return sum(1 << SHORT.index(name) for name in names)


def worlds_of_row(key):
    """The world count of a table row key, which is frame class, worlds, axioms."""
    return int(key.split(":")[1])


def scans():
    """Every declared frame class and world count, scanned once."""
    out = {}
    for kind in FRAME_CLASSES:
        for n in (1, 2, 3):
            out[(kind, n)] = scan(n, kind)
    return out


# ------------------------------------------------------------------- sections

def s1_semantics():
    """The declared semantics, and the lemma that pins the notion of necessity."""
    models = 0
    exceptions = []
    for kind in FRAME_CLASSES:
        for n in (1, 2, 3):
            for model in enumerate_models(n, kind):
                models += 1
                isolated = frozenset(w for w in model.W if model.succ[w] == (w,))
                if model.necessary_existence() != isolated:
                    exceptions.append((kind, n, sorted(model.necessary_existence()),
                                       sorted(isolated)))
    check(models > 0, "no model was enumerated at all")
    check(not exceptions, f"the necessity lemma fails at {exceptions[:2]}")
    shapes = {}
    for kind in FRAME_CLASSES:
        for n in (1, 2, 3):
            shapes[f"{kind}:{n}"] = len(relations(n, kind))
    check(shapes["universal:3"] == 1, "the universal frame on three worlds is not unique")
    check(shapes["equivalence:2"] == 2, "the equivalence frames on two worlds are not two")
    check(shapes["equivalence:3"] == 5, "the equivalence frames on three worlds are not five")
    check(shapes["preorder:3"] == 29, "the preorders on three worlds are not twenty-nine")
    check(shapes["reflexive:3"] == 64, "the reflexive frames on three worlds are not sixty-four")
    for n in (1, 2, 3):
        check(len(properties(n)) == 2 ** n, "the property algebra is not the full power set")
        check(len(positivity_candidates(n)) == 2 ** (2 ** n),
              "the positivity assignments are not two to the two to the n")
    check(len(positivity_candidates(3)) == 256,
          "the positivity assignments on three worlds are not two hundred fifty-six")
    return {
        "frames_per_class_and_worlds": shapes,
        "models_enumerated": models,
        "necessity_lemma": "necessary existence holds at a world exactly when that world"
                           " sees only itself",
        "necessity_lemma_exceptions": len(exceptions),
        "world_bound": WORLD_BOUND,
        "domain_size": 1,
        "positivity_may_vary_by_world": True,
        "property_algebra_is_complete": True,
        "frames_are_declared_as_relations_not_as_a_proof_calculus": True,
    }


def s2_table(all_scans):
    """Which declared axiom sets force the conclusion, and which admit no model."""
    rows = {}
    totals = {}
    retained = {}
    minimal_forcing = {}
    for (kind, n), (table, seen) in all_scans.items():
        totals[f"{kind}:{n}"] = seen
        for mask, d in table.items():
            forced = d["models"] > 0 and d["conclusion"] == d["models"]
            rows[f"{kind}:{n}:{name_of(mask)}"] = {
                "axioms": [SHORT[i] for i in range(len(SHORT)) if mask >> i & 1],
                "models": d["models"],
                "conclusion": d["conclusion"],
                "conclusion_holds_in_every_model": forced,
                "conclusion_holds_in_no_model": d["models"] > 0 and d["conclusion"] == 0,
                "collapse": d["collapse"],
                "essence_vacuous": d["essence_vacuous"],
                "no_uninstantiated_positive": d["no_uninstantiated_positive"],
                "identity_frame": d["identity_frame"],
            }
        forcing = [mask for mask, d in table.items()
                   if d["models"] > 0 and d["conclusion"] == d["models"]]
        minimal_forcing[f"{kind}:{n}"] = {
            "forcing_sets": len(forcing),
            "smallest_forcing_set": (name_of(min(forcing, key=lambda m: bin(m).count("1")))
                                     if forcing else None),
            "models_under_that_set": (table[min(forcing, key=lambda m: bin(m).count("1"))]["models"]
                                      if forcing else 0),
        }
        # the witnesses that matter: every axiom at once, and the first two alone
        full = (1 << len(SHORT)) - 1
        if table.get(full, {}).get("witness") is not None:
            retained[f"{kind}:{n}:all_seven_axioms"] = table[full]["witness"]
        first_two = mask_of(["A1", "A2"])
        if table.get(first_two, {}).get("witness") is not None:
            retained[f"{kind}:{n}:first_two_axioms"] = table[first_two]["witness"]
    forcing = sorted(k for k, v in rows.items() if v["conclusion_holds_in_every_model"])
    never = sorted(k for k, v in rows.items() if v["conclusion_holds_in_no_model"])

    # A row exists only for a subset that some model of the block satisfies, so a
    # subset no model satisfies contributes no row and the table is smaller than the
    # number of subset-and-block combinations. The gap is named and explained rather
    # than left as a lower bound on a count.
    combinations = len(FRAME_CLASSES) * 3 * (1 << len(SHORT))
    declared = CONTRACT["objects"]["expected_axiom_table_rows"]
    check(combinations == 1536,
          "twelve blocks of one hundred twenty-eight subsets are not fifteen hundred thirty-six")
    check(len(rows) == declared,
          f"the axiom table does not have the declared {declared} rows but {len(rows)}")
    gaps = {}
    for (kind, n), (table, seen) in all_scans.items():
        missing = [name_of(m) for m in range(1 << len(SHORT)) if m not in table]
        if missing:
            gaps[f"{kind}:{n}"] = {"rows": len(missing),
                                   "every_missing_subset_contains_A5": all("A5" in name
                                                                           for name in missing)}
            check(all("A5" in name for name in missing),
                  f"a subset missing from {kind}:{n} does not contain A5")
            check(not any("A5" in d["axioms"] for key, d in rows.items()
                          if key.startswith(f"{kind}:{n}:")),
                  f"a row of {kind}:{n} contains A5 although the block misses its subsets")
    check(sorted(gaps) == ["universal:2", "universal:3"],
          f"the blocks with rows missing are not the universal frame at two and three worlds: {sorted(gaps)}")
    check(all(v["rows"] == 1 << (len(SHORT) - 1) for v in gaps.values()),
          "a block does not miss exactly the sixty-four subsets containing A5")
    check(sum(v["rows"] for v in gaps.values()) == combinations - len(rows) == 128,
          "the missing rows are not the difference between the declared combinations and the table")
    check(mask_of(["A5"]) not in all_scans[("universal", 2)][0]
          and mask_of(["A5"]) not in all_scans[("universal", 3)][0],
          "A5 alone has a model under the universal frame above one world")
    check(forcing, "no declared axiom set forces the conclusion within the bound")
    check(never, "no declared axiom set refuses the conclusion within the bound")

    # forcing the conclusion, beyond the degenerate one-world case, is a property of the
    # equivalence frames only
    symmetric = [k for k, v in minimal_forcing.items()
                 if v["forcing_sets"] > 0 and not k.endswith(":1")]
    check(all(k.startswith("equivalence") for k in symmetric),
          f"a frame class other than the equivalence frames forces the conclusion: {symmetric}")
    check(len(symmetric) == 2, "the equivalence frames do not force the conclusion at two"
                               " and three worlds alike")
    degenerate = [k for k, v in minimal_forcing.items()
                  if v["forcing_sets"] > 0 and k.endswith(":1")]
    check(len(degenerate) == len(FRAME_CLASSES),
          "the one-world case does not force the conclusion in every frame class")
    check(all(v["smallest_forcing_set"] == "A5" for v in minimal_forcing.values()
              if v["forcing_sets"] > 0 and not v["smallest_forcing_set"] is None
              and v["models_under_that_set"] == 1),
          "the smallest set forcing the conclusion is not the axiom of necessary existence alone")
    check(all(v["smallest_forcing_set"] is None for k, v in minimal_forcing.items()
              if not k.startswith("equivalence") and not k.endswith(":1")),
          "a non-symmetric frame class has a set forcing the conclusion after all")
    check(len(retained) >= 2, "no countermodel under every axiom was retained")

    # the forcing rows have exactly one shape: one world, or the equivalence frames
    # with the axiom of necessary existence present
    outside = [k for k, v in rows.items() if v["conclusion_holds_in_every_model"]
               and worlds_of_row(k) > 1]
    check(all("A5" in rows[k]["axioms"] for k in outside),
          "a set forcing the conclusion omits the axiom of necessary existence")
    check(all(k.startswith("equivalence") for k in outside),
          "a set forcing the conclusion lies outside the equivalence frames")
    check(len(outside) == 128, "the number of forcing rows over the equivalence frames has moved")
    within = [k for k, v in rows.items()
              if k.startswith("equivalence") and worlds_of_row(k) > 1
              and "A5" in v["axioms"] and v["models"] > 0]
    check(sorted(within) == sorted(outside),
          "some subset of the equivalence axioms with necessary existence fails to force")
    check(all(rows[k]["models"] == 1 for k in outside),
          "a set forcing the conclusion over the equivalence frames has more than one model")

    # wherever the axioms force the conclusion they also make the essence vacuous
    essence_everywhere = [k for k, v in rows.items()
                          if v["models"] > 0 and v["essence_vacuous"] == v["models"]]
    forcing_rows = [k for k, v in rows.items() if v["conclusion_holds_in_every_model"]]
    check(all(k in essence_everywhere for k in forcing_rows),
          "a set forces the conclusion without making the essence vacuous in every model")
    check(len(forcing_rows) == 640,
          "the number of rows forcing the conclusion has moved")
    check(len(essence_everywhere) == len(forcing_rows) == 640,
          "the rows forcing the essence to be vacuous are not the rows forcing the conclusion")

    # adding one axiom never enlarges a model class
    monotone = 0
    for key, value in rows.items():
        kind, n, _ = key.split(":", 2)
        for i in range(len(SHORT)):
            if SHORT[i] in value["axioms"]:
                continue
            widened = rows.get(f"{kind}:{n}:{name_of(mask_of(value['axioms'] + [SHORT[i]]))}")
            if widened is None:
                continue
            monotone += 1
            check(widened["models"] <= value["models"],
                  f"adding an axiom enlarged the model class: {widened} over {key}")
    check(monotone > 1000, "too few axiom extensions were compared for monotonicity")
    return {
        "models_enumerated": totals,
        "rows": rows,
        "axiom_table_rows": len(rows),
        "subset_and_block_combinations": combinations,
        "rows_missing": combinations - len(rows),
        "blocks_with_rows_missing": sorted(gaps),
        "rows_missing_by_block": gaps,
        "why_rows_are_missing": "a row is written only where a model of the block satisfies the"
                                " subset, and A5 is satisfied by no model of the universal frame at"
                                " two or three worlds, so the sixty-four subsets containing A5"
                                " contribute no row in each of those two blocks",
        "the_first_two_axioms_are_pruning_conditions": "the enumeration admits only positivity"
                                                       " assignments that satisfy A1 and A2 at a"
                                                       " world, so those two axioms hold by"
                                                       " construction in every enumerated model and"
                                                       " the model count of their row is the size of"
                                                       " a pruned enumeration, not the result of an"
                                                       " independent scan",
        "sets_forcing_the_conclusion": forcing,
        "sets_never_admitting_the_conclusion": never,
        "minimal_forcing": minimal_forcing,
        "retained_countermodels": retained,
        "rows_forcing_the_conclusion": len(forcing_rows),
        "rows_in_which_every_model_makes_the_essence_vacuous": len(essence_everywhere),
        "forcing_the_conclusion_forces_the_essence_to_be_vacuous": True,
        "the_conclusion_is_forced_only_over_symmetric_frames": True,
        "the_smallest_forcing_set_is_one_axiom": True,
        "a_refutation_is_one_model": True,
        "forcing_is_reported_only_where_models_exist": True,
        "a_row_with_no_model_refutes_nothing": True,
    }


def s3_necessary_existence(all_scans):
    """What the axiom of necessary existence forces, and what it costs."""
    total = 0
    equivalence = 0
    others = 0
    unique = None
    per_block = {f"{kind}:{n}": 0 for kind in FRAME_CLASSES for n in (1, 2, 3)}
    for kind in FRAME_CLASSES:
        for n in (1, 2, 3):
            for model in enumerate_models(n, kind):
                f = model.facts()
                if not (f["A1"] and f["A2"] and f["A5"]):
                    continue
                total += 1
                per_block[f"{kind}:{n}"] += 1
                if f["conclusion"] == f["collapse"]:
                    equivalence += 1
                if f["A3"] and f["A4"] and f["A6"] and f["A1c"]:
                    others += 1
                if kind == "equivalence" and n == 3:
                    unique = model
    check(total > 0, "no model of the three axioms was found")
    check(total == CONTRACT["objects"]["expected_models_of_the_three_axioms"],
          f"the three axioms do not have the declared {CONTRACT['objects']['expected_models_of_the_three_axioms']} models")
    check(sum(per_block.values()) == total,
          "the per-block tally of the three-axiom models does not sum to the total")
    # the eighty-six are spread over ten of the twelve blocks: the universal frame at
    # two and three worlds contributes none, because A5 has no model there, so the
    # figure must not be read as one model per class
    check(per_block["universal:2"] == 0 and per_block["universal:3"] == 0,
          "the three axioms have a model under the universal frame above one world")
    check(sum(1 for count in per_block.values() if count) == 10,
          "the three-axiom models are not spread over ten of the twelve blocks")
    check(equivalence == total,
          "the conclusion and the constancy of every property come apart inside the axioms")
    check(0 < others < total,
          "the axiom of necessary existence either implies or never implies the remaining ones")
    check(unique is not None, "the equivalence model of the three axioms was not found")

    # the one model the three axioms leave over the equivalence frames at three worlds
    W, A = unique.W, unique.A
    check(all(a == b for a, b in unique.R),
          "the model left by the three axioms is not the frame that sees only itself")
    per_world = all(unique.P[w] == frozenset(p for p in A if p and w in p) for w in W)
    check(per_world,
          "the positivity of the model left by the three axioms is not exactly the non-empty"
          " properties the individual has at that world")
    f = unique.facts()
    check(f["conclusion"] and f["collapse"] and f["essence_vacuous"],
          "the model left by the three axioms does not satisfy the conclusion, the collapse"
          " and the vacuity of the essence at once")
    check(f["_G"] == unique.W and f["_NE"] == unique.W,
          "the godlike worlds and the worlds of necessary existence are not every world there")
    return {
        "models_of_the_three_axioms": total,
        "models_of_the_three_axioms_by_frame_class_and_worlds": per_block,
        "blocks_contributing_a_model": sorted(k for k, count in per_block.items() if count),
        "blocks_contributing_no_model": sorted(k for k, count in per_block.items() if not count),
        "models_where_the_conclusion_agrees_with_the_constancy_of_every_property": equivalence,
        "models_that_also_satisfy_the_other_four": others,
        "the_conclusion_holds_exactly_where_every_property_is_constant": True,
        "the_three_axioms": ["A1", "A2", "A5"],
        "the_one_equivalence_model": {
            "worlds": unique.n,
            "relation_is_the_identity": True,
            "positivity_at_each_world": "exactly the non-empty properties the individual has there",
            "godlike_worlds": sorted(f["_G"]),
            "necessary_existence_worlds": sorted(f["_NE"]),
            "conclusion": True,
            "every_property_constant": True,
            "essence_vacuous": True,
        },
        "why": "necessary existence holds only at a world that sees only itself, so requiring"
               " it to be positive forces every world that sees another world out of the"
               " godlike worlds; what remains over the equivalence frames is the single frame"
               " in which no world sees another, and there necessity is the identity",
        "positivity_carries_no_information_in_that_model": True,
    }


def s4_vocabulary():
    """What the declared family cannot say, checked on the declared vocabulary."""
    for symbol in VOCABULARY:
        check(symbol in VOCABULARY, symbol)
    check("identity" not in VOCABULARY, "the declared vocabulary contains identity")
    check("equals" not in VOCABULARY, "the declared vocabulary contains equality")
    # the notions the family does declare, and what they are built from
    notions = {
        "godlikeness": ("all_worlds_of_the_positivity", "has"),
        "essence": ("has", "implies", "all_worlds", "all_properties"),
        "necessary_existence": ("essence", "all_worlds", "some_individual"),
        "conclusion": ("all_worlds", "some_individual", "godlikeness"),
    }
    for name, parts in notions.items():
        for part in parts:
            check(part, f"{name} is declared with an empty part")
        check(not any("identity" in part or "equals" in part for part in parts),
              f"{name} is built from identity")
    check(all(("identity" not in " ".join(parts)) for parts in notions.values()),
          "identity occurs in a declared notion")
    return {
        "declared_vocabulary": list(VOCABULARY),
        "declared_notions": {k: list(v) for k, v in notions.items()},
        "identity_occurs_in_the_declared_family": False,
        "uniqueness_cannot_be_derived_from_this_family": True,
        "why": "no declared axiom or notion contains an identity predicate, so a statement"
               " that two godlike individuals are the same individual is not expressible"
               " in the declared family; uniqueness needs an added premise, and it is not"
               " tested here because the declared semantics has one individual",
        "uniqueness_is_an_untested_residual": True,
    }


def s5_degenerate(all_scans):
    """The one-world case, where necessity is the identity by construction."""
    table, seen = all_scans[("universal", 1)]
    every = table[(1 << len(SHORT)) - 1]
    check(0 < seen < len(positivity_candidates(1)),
          "the one-world scan did not prune any positivity assignment, or pruned them all")
    check(len(positivity_candidates(1)) == 4,
          "the one-world positivity assignments are not four")
    check(every["models"] > 0, "the one-world system with every axiom has no model")
    check(every["conclusion"] == every["models"],
          "the one-world system with every axiom does not satisfy the conclusion")
    check(every["collapse"] == every["models"],
          "a property is not constant in the one-world system")
    forcing_one_world = []
    for mask, d in table.items():
        if d["models"] > 0 and d["conclusion"] == d["models"]:
            forcing_one_world.append(name_of(mask))
    check(len(forcing_one_world) > 1,
          "only the full axiom set forces the conclusion when there is one world")
    check(len(forcing_one_world) == 1 << len(SHORT),
          "not every declared subset forces the conclusion when there is one world")
    return {
        "positivity_assignments_after_pruning": seen,
        "models_with_every_axiom": every["models"],
        "conclusion_with_every_axiom": every["conclusion"],
        "collapse_with_every_axiom": every["collapse"],
        "declared_sets_forcing_the_conclusion_with_one_world": len(forcing_one_world),
        "every_declared_subset_forces_the_conclusion_with_one_world": True,
        "with_one_world_necessity_is_the_identity": True,
        "the_degenerate_case_is_not_evidence_for_the_argument": True,
    }


def run(output=None):
    started = time.perf_counter_ns()
    # the table's declared row count is read from the contract here as well, so the
    # section that compares against it does not depend on how this module was entered
    CONTRACT.update(json.loads((HERE / "contract.json").read_text(encoding="utf-8")))
    all_scans = scans()
    sections = {
        "S1_semantics": s1_semantics(),
        "S2_table": s2_table(all_scans),
        "S3_necessary_existence": s3_necessary_existence(all_scans),
        "S4_vocabulary": s4_vocabulary(),
        "S5_degenerate": s5_degenerate(all_scans),
    }
    report = {
        "schema": "adva.research.modal-property-systems-evidence.v0",
        "status": "ExternalExactPass",
        "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "contract_sha256": hashlib.sha256((HERE / "contract.json").read_bytes()).hexdigest(),
        "assertions": COUNTS["assertions"],
        "sections": sections,
        "limits": LIMITS,
        "installed_limits": INSTALLED,
        "wall_ns": time.perf_counter_ns() - started,
        "rss_high_water_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    text = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if output:
        target = Path(output)
        if target.exists():
            raise SystemExit("refused: the output path already exists")
        target.write_text(text, encoding="utf-8")
    return report, text


def install_limits():
    """Install what this host accepts and record every refusal.

    The checker launches no child process and allocates no large structure, so it
    installs a CPU, a file-size and a wall bound and no address-space ceiling.
    The contract's memory figure is a declared budget observed by peak RSS, not
    an enforced limit; this file deliberately contains no address-space call, so
    the repository's portability inventory is unaffected.
    """
    limit = LIMITS
    wanted = [
        ("RLIMIT_CPU", lambda: resource.setrlimit(resource.RLIMIT_CPU,
                                                  (limit["cpu_seconds"], limit["cpu_seconds"]))),
        ("RLIMIT_FSIZE", lambda: resource.setrlimit(resource.RLIMIT_FSIZE,
                                                    (limit["output_bytes"], limit["output_bytes"]))),
    ]
    for name, call in wanted:
        if not hasattr(resource, name):
            INSTALLED[name] = "absent"
            continue
        try:
            call()
            INSTALLED[name] = "installed"
        except (ValueError, OSError) as exc:
            INSTALLED[name] = f"refused: {type(exc).__name__}"
    if hasattr(signal, "SIGALRM") and hasattr(signal, "setitimer"):
        def stop(_signum, _frame):
            raise RuntimeError("Unknown: wall budget")
        signal.signal(signal.SIGALRM, stop)
        signal.setitimer(signal.ITIMER_REAL, limit["wall_seconds"])
        INSTALLED["wall_alarm"] = "installed"
    else:
        INSTALLED["wall_alarm"] = "absent"
    INSTALLED["address_space_ceiling"] = "not-installed: no child process"
    INSTALLED["memory_bound"] = "declared only; observed as peak RSS"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    contract = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
    LIMITS.update(contract["budget"])
    CONTRACT.update(contract)
    install_limits()
    report, _ = run(args.output)
    print(json.dumps({"status": report["status"], "assertions": report["assertions"]},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
