"""Two-world external Scott/knowledge model; no native Adva authority.

Original contribution under Unknown v0.3 by Codex (OpenAI), through
Mingli Yuan's account proxy, not his authorship, review or endorsement.
"""

from itertools import product


def evaluate(model):
    """Exhaust every intensional property on exactly two worlds/two objects.

    Properties are four-bit masks, bit 2*w+x. Positivity is explicitly
    supplied on the four local extensions, then lifted world by world.
    Rm supplies metaphysical necessity; transcript equality supplies knowledge.
    The sender is a world-dependent role, NOT a rigid individual constant.
    """
    if set(model) != {"positive_extensions", "modal", "sender", "transcripts"}:
        raise ValueError("Unexpected model fields")
    positive, modal = model["positive_extensions"], model["modal"]
    sender, transcripts = model["sender"], model["transcripts"]
    if type(positive) is not list or len(positive) != 2:
        raise ValueError("Exactly two positivity rows required")
    for row in positive:
        if (type(row) is not list or any(type(x) is not int or x not in range(4) for x in row)
                or row != sorted(set(row))):
            raise ValueError("Invalid positive extensions")
    if (type(modal) is not list or len(modal) != 2 or any(
            type(row) is not list or len(row) != 2 or any(type(x) is not bool for x in row)
            for row in modal)):
        raise ValueError("Modal relation must be a 2x2 Boolean matrix")
    if type(sender) is not list or len(sender) != 2 or any(type(x) is not int or x not in (0, 1) for x in sender):
        raise ValueError("Invalid sender role")
    if (type(transcripts) is not list or len(transcripts) != 2 or any(
            type(row) is not list or not 1 <= len(row) <= 8 or any(
                type(x) is not str or len(x) > 32 for x in row) for row in transcripts)):
        raise ValueError("Invalid bounded transcripts")

    worlds, objects, properties = range(2), range(2), range(16)
    holds = lambda p, w, x: bool(p & (1 << (2*w+x)))
    pos = lambda p, w: ((p >> (2*w)) & 3) in positive[w]
    entails = lambda p, q, w: all(not modal[w][v] or all(
        not holds(p, v, x) or holds(q, v, x) for x in objects) for v in worlds)
    essence = lambda p, w, x: holds(p, w, x) and all(
        not holds(q, w, x) or entails(p, q, w) for q in properties)
    required_existence = lambda p, w: all(not modal[w][v] or any(
        holds(p, v, x) for x in objects) for v in worlds)
    g = sum(1 << (2*w+x) for w, x in product(worlds, objects)
            if all(not pos(p, w) or holds(p, w, x) for p in properties))
    ne = sum(1 << (2*w+x) for w, x in product(worlds, objects)
             if all(not essence(p, w, x) or required_existence(p, w) for p in properties))
    checks = {}

    def check(name, rows):
        rows = list(rows)
        failures = [list(coordinates) for coordinates, truth in rows if not truth]
        checks[name] = {"instances": len(rows), "holds": not failures,
                        "failure_count": len(failures), "first_failure": failures[0] if failures else None}

    check("A1", (((w, p), pos(15 ^ p, w) == (not pos(p, w))) for w, p in product(worlds, properties)))
    check("A2", (((w, p, q), not (pos(p, w) and entails(p, q, w)) or pos(q, w))
                 for w, p, q in product(worlds, properties, properties)))
    check("A3", (((w,), pos(g, w)) for w in worlds))
    check("A4", (((w, p), not pos(p, w) or all(not modal[w][v] or pos(p, v) for v in worlds))
                 for w, p in product(worlds, properties)))
    check("A5", (((w,), pos(ne, w)) for w in worlds))
    check("T1", (((w, p), not pos(p, w) or any(modal[w][v] and any(
        holds(p, v, x) for x in objects) for v in worlds)) for w, p in product(worlds, properties)))
    check("T2", (((w, x), not holds(g, w, x) or essence(g, w, x)) for w, x in product(worlds, objects)))
    check("T3", (((w,), required_existence(g, w)) for w in worlds))
    check("modal_collapse", (((w, p), not bool(p & (1 << w)) or all(
        not modal[w][v] or bool(p & (1 << v)) for v in worlds)) for w, p in product(worlds, range(4))))
    equivalence = lambda r: (all(r[w][w] for w in worlds)
                            and all(r[w][v] == r[v][w] for w, v in product(worlds, worlds))
                            and all(not (r[w][v] and r[v][u]) or r[w][u]
                                    for w, v, u in product(worlds, worlds, worlds)))
    epistemic = [[transcripts[w] == transcripts[v] for v in worlds] for w in worlds]
    truth = [holds(g, w, sender[w]) for w in worlds]
    exists = [any(holds(g, w, x) for x in objects) for w in worlds]
    knows = lambda values: [all(not epistemic[w][v] or values[v] for v in worlds) for w in worlds]
    known, known_not = knows(truth), knows([not value for value in truth])
    witness = next(([w, v] for w, v in product(worlds, worlds)
                    if epistemic[w][v] and truth[w] != truth[v]), None)
    return {
        "property_count": 16, "godlike": [[x for x in objects if holds(g, w, x)] for w in worlds],
        "necessary_existence": [[x for x in objects if holds(ne, w, x)] for w in worlds],
        "essences": [[[p for p in properties if essence(p, w, x)] for x in objects] for w in worlds],
        "checks": checks, "ontology_satisfied": equivalence(modal) and all(checks[k]["holds"] for k in ("A1", "A2", "A3", "A4", "A5")),
        "modal_s5": equivalence(modal), "epistemic_s5": equivalence(epistemic), "epistemic_relation": epistemic,
        "exists": exists, "necessarily_exists": [required_existence(g, w) for w in worlds],
        "knows_exists": knows(exists), "sender_godlike": truth,
        "knows_sender_godlike": known, "knows_sender_not_godlike": known_not,
        "identity_status": ["KnownTrue" if known[w] else "KnownFalse" if known_not[w] else "Underdetermined" for w in worlds],
        "identity_descends": witness is None, "non_saturation_witness": witness,
    }
