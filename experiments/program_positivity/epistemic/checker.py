"""Independent ordinary-set evaluation, with no producer import.

Same author as producer: implementation separation is not independent review.
Original contribution by Codex (OpenAI), Unknown v0.3, Mingli Yuan proxy.
"""

import itertools
import json


def recompute(model):
    # This receiver deliberately accepts only the finite 2-by-2 profile.
    if type(model) is not dict or set(model) != {"positive_extensions", "modal", "sender", "transcripts"}:
        raise ValueError("model shape")
    for field in model.values():
        if type(field) is not list or len(field) != 2:
            raise ValueError("two-world profile")
    for row in model["positive_extensions"]:
        if type(row) is not list or row != sorted(set(row)) or any(type(n) is not int or n not in range(4) for n in row):
            raise ValueError("local extension family")
    for row in model["modal"]:
        if type(row) is not list or len(row) != 2 or any(type(b) is not bool for b in row):
            raise ValueError("modal relation")
    if any(type(s) is not int or s not in (0, 1) for s in model["sender"]):
        raise ValueError("sender role")
    for row in model["transcripts"]:
        if type(row) is not list or not 1 <= len(row) <= 8 or any(type(s) is not str or len(s) > 32 for s in row):
            raise ValueError("transcript")
    states = (0, 1)
    points = tuple(itertools.product(states, states))
    universe = frozenset(points)
    props = [frozenset(c) for n in range(5) for c in itertools.combinations(points, n)]
    code = lambda p: sum(2 ** (2*w+x) for w, x in p)
    props.sort(key=code)
    modal_edges = {(w, v) for w in states for v in states if model["modal"][w][v]}
    visible_edges = {(w, v) for w in states for v in states if model["transcripts"][w] == model["transcripts"][v]}
    positive = {w: {p for p in props if sum(2**x for x in states if (w, x) in p)
                   in model["positive_extensions"][w]} for w in states}

    def entail(p, q, w):
        return not any((w, v) in modal_edges and (v, x) in p - q for v, x in points)

    essentials = {(w, x): {p for p in props if (w, x) in p and all(
        entail(p, q, w) for q in props if (w, x) in q)} for w, x in points}
    necessary = lambda p, w: all(any((v, x) in p for x in states) for u, v in modal_edges if u == w)
    g = frozenset((w, x) for w, x in points if all((w, x) in p for p in positive[w]))
    ne = frozenset((w, x) for w, x in points if all(necessary(p, w) for p in essentials[w, x]))
    checks = {}

    def record(name, evaluations):
        evaluations = list(evaluations)
        failures = [indices for indices, ok in evaluations if not ok]
        checks[name] = {"instances": len(evaluations), "holds": len(failures) == 0,
                        "failure_count": len(failures), "first_failure": failures[0] if failures else None}

    record("A1", (([w, code(p)], ((universe-p) in positive[w]) != (p in positive[w])) for w in states for p in props))
    record("A2", (([w, code(p), code(q)], p not in positive[w] or not entail(p, q, w) or q in positive[w])
                  for w in states for p in props for q in props))
    record("A3", (([w], g in positive[w]) for w in states))
    record("A4", (([w, code(p)], p not in positive[w] or all(p in positive[v] for u, v in modal_edges if u == w)) for w in states for p in props))
    record("A5", (([w], ne in positive[w]) for w in states))
    record("T1", (([w, code(p)], p not in positive[w] or any((w, v) in modal_edges and (v, x) in p for v, x in points))
                  for w in states for p in props))
    record("T2", (([w, x], (w, x) not in g or g in essentials[w, x]) for w, x in points))
    record("T3", (([w], necessary(g, w)) for w in states))
    propositions = [set(), {0}, {1}, {0, 1}]
    record("modal_collapse", (([w, i], w not in p or all(v in p for u, v in modal_edges if u == w))
                              for w in states for i, p in enumerate(propositions)))

    def s5(edges):
        return ({(0, 0), (1, 1)} <= edges and {(v, w) for w, v in edges} == edges
                and all((u, z) in edges for u, v in edges for y, z in edges if v == y))

    truths = {w for w in states if (w, model["sender"][w]) in g}
    exist = {w for w, x in g}
    know = lambda p: [all(v in p for u, v in visible_edges if u == w) for w in states]
    known, known_not = know(truths), know(set(states)-truths)
    mixed = sorted([w, v] for w, v in visible_edges if (w in truths) != (v in truths))
    return {
        "property_count": len(props), "godlike": [[x for x in states if (w, x) in g] for w in states],
        "necessary_existence": [[x for x in states if (w, x) in ne] for w in states],
        "essences": [[sorted(code(p) for p in essentials[w, x]) for x in states] for w in states],
        "checks": checks, "ontology_satisfied": s5(modal_edges) and all(checks[name]["holds"] for name in ("A1", "A2", "A3", "A4", "A5")),
        "modal_s5": s5(modal_edges), "epistemic_s5": s5(visible_edges),
        "epistemic_relation": [[(w, v) in visible_edges for v in states] for w in states],
        "exists": [w in exist for w in states], "necessarily_exists": [necessary(g, w) for w in states],
        "knows_exists": know(exist), "sender_godlike": [w in truths for w in states],
        "knows_sender_godlike": known, "knows_sender_not_godlike": known_not,
        "identity_status": ["KnownTrue" if a else "KnownFalse" if b else "Underdetermined" for a, b in zip(known, known_not)],
        "identity_descends": not mixed, "non_saturation_witness": mixed[0] if mixed else None,
    }


def verify(model, report):
    try:
        expected = recompute(model)
        # JSON distinguishes booleans from integers, unlike Python equality.
        if json.dumps(expected, sort_keys=True, allow_nan=False) != json.dumps(report, sort_keys=True, allow_nan=False):
            return {"status": "Rejected", "reason": "Finite set semantics disagree"}
        return {"status": "Verified", "reason": "All finite tables and formulas recomputed"}
    except (TypeError, ValueError, KeyError):
        return {"status": "Rejected", "reason": "Outside the fixed finite profile"}
