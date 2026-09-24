"""Exact external checker for four left-nested pure-iota frames.

This checker never constructs, reads or authorizes an Adva semantic identity. It
uses strings, tuples, integers and Fractions only, imports nothing outside the
standard library, and opens no external corpus. Every input it reads is a pinned
byte sequence already received in this repository, and every acceptance test
compares integers or exact rationals.

The three rewrite rules and the two frame operator definitions are QUOTED, not
restated, from received materials whose SHA-256 digests this file pins:

  rules   knowledge/received/iota-process-knowledge-2026-09-17-v1/materials/iota.md
          "The internal rules are iota x -> x S K, K x y -> x, and
           S x y z -> x z (y z). Iota remains the sole primitive source
           combinator.  I = iota iota, K = iota (iota (iota iota)), and
           S = iota K are the existing pure-iota encodings"

  frame   knowledge/received/iota-frame-knowledge-2026-09-17-v1/materials/frame.md
          "J = [[0, -I], [I, 0]],  J^2 = -I"  ;  "Set H0 = L/(2*d_max), with
           denominator one for the empty-edge case, and H = diag(H0,H0).
           Initially G=I and O=I."  ;  "The braces {}, brackets [] and
           parentheses () denote declared construction, space and time roles"

What this file computes, and what it does not, is stated in contract.json. In
particular it decides nothing about physical spacetime, and the four towers it
examines are not claimed to be well-formed received source terms.
"""
import argparse
import hashlib
import json
import resource
import signal
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COUNTS = {"assertions": 0}
LIMITS = {}
INSTALLED = {}

IOTA_MD = "knowledge/received/iota-process-knowledge-2026-09-17-v1/materials/iota.md"
IOTA_INTERPRETATIONS = (
    "knowledge/received/iota-process-knowledge-2026-09-17-v1/materials/interpretations.json"
)
IOTA_CONTRACT = "knowledge/received/iota-process-knowledge-2026-09-17-v1/materials/contract.json"
FRAME_MD = "knowledge/received/iota-frame-knowledge-2026-09-17-v1/materials/frame.md"
FRAME_DEPENDENCIES = (
    "knowledge/received/iota-frame-knowledge-2026-09-17-v1/materials/dependencies.json"
)
PINS = {
    IOTA_MD: "f2f13d6fefafb11d451dcc46166e0b77f35013a971460387ee5c0e9b6bf72454",
    IOTA_INTERPRETATIONS: "8009db7b8828ae76aa01b25684b9aa974fc91c4fcb64a439946701a49fe528b1",
    IOTA_CONTRACT: "c2656bf793d4175054cfc1822618233fe0bbb65a6f276578e77ba9749186bef6",
    FRAME_MD: "d8967cc3e6b953d547a22010f37d9997a023d1b55935928f88becba86862dae0",
}
RECEIVED_PROCESS = "chain-and-single"


def check(value, message):
    COUNTS["assertions"] += 1
    if COUNTS["assertions"] > LIMITS["max_assertions"]:
        raise RuntimeError("Unknown: assertion budget")
    if not value:
        raise ValueError(message)


def digest(relative):
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# prefix terms over @ i a b c : the alphabet check.py's parse() accepts
# ---------------------------------------------------------------------------

def parse(text):
    pos = 0

    def read():
        nonlocal pos
        if pos >= len(text):
            raise ValueError("incomplete prefix term")
        token = text[pos]
        pos += 1
        if token == "@":
            return (read(), read())
        if token not in "iksabc":
            raise ValueError("unknown term token")
        return token

    result = read()
    if pos != len(text):
        raise ValueError("trailing term tokens")
    return result


def show(term):
    return "@" + show(term[0]) + show(term[1]) if isinstance(term, tuple) else term


def tower(m):
    """The left-nested pure-iota tower with m iota leaves: C_1 = i, C_(m+1) = ((C_m) i)."""
    term = "i"
    for _ in range(m - 1):
        term = "@" + term + "i"
    return term


class Store:
    """An identity-preserving term store.

    Every node keeps the index of the step that created it, so a redex can be
    traced to the contractions that made it available. A node reused by a rule
    keeps its identity; only new structure is stamped with the current step.
    """

    def __init__(self):
        self.node = {}
        self.made = {}
        self.count = 0
        self.step = -1

    def leaf(self, token):
        index = self.count
        self.count += 1
        self.node[index] = ("leaf", token)
        self.made[index] = self.step
        return index

    def app(self, left, right):
        index = self.count
        self.count += 1
        self.node[index] = ("app", left, right)
        self.made[index] = self.step
        return index

    def build(self, term):
        if isinstance(term, tuple):
            return self.app(self.build(term[0]), self.build(term[1]))
        return self.leaf(term)

    def text(self, index):
        kind = self.node[index]
        return kind[1] if kind[0] == "leaf" else "@" + self.text(kind[1]) + self.text(kind[2])

    def spine(self, index):
        args = []
        while self.node[index][0] == "app":
            _, left, right = self.node[index]
            args.append(right)
            index = left
        args.reverse()
        return index, args


def find_redex(store, node):
    """Leftmost-innermost redex of the subtree at node, or None.

    A redex is a spine head applied to exactly the declared number of arguments:
    iota takes one, K takes two, S takes three.
    """
    kind = store.node[node]
    if kind[0] == "leaf":
        return None
    found = find_redex(store, kind[1])
    if found:
        return found
    head, args = store.spine(node)
    head_kind = store.node[head]
    if head_kind[0] == "leaf":
        token = head_kind[1]
        if token == "i" and len(args) == 1:
            return (node, head, args, "i")
        if token == "k" and len(args) == 2:
            return (node, head, args, "k")
        if token == "s" and len(args) == 3:
            return (node, head, args, "s")
    return find_redex(store, kind[2])


def path_of(store, root, target):
    """The 0/1 path from root to the node target, or None."""
    if root == target:
        return ()
    kind = store.node[root]
    if kind[0] == "leaf":
        return None
    left = path_of(store, kind[1], target)
    if left is not None:
        return (0, *left)
    right = path_of(store, kind[2], target)
    if right is not None:
        return (1, *right)
    return None


def contract_once(store, node, head, args, rule):
    """One rule application, reusing argument nodes by identity."""
    if rule == "i":  # iota x -> x S K
        (x,) = args
        return store.app(store.app(x, store.leaf("s")), store.leaf("k"))
    if rule == "k":  # K x y -> x
        return args[0]
    x, y, z = args  # S x y z -> x z (y z)
    return store.app(store.app(x, z), store.app(y, z))


def graft(store, node, target, replacement):
    """Replace the subtree at target with replacement, rebuilding only the spine."""
    if node == target:
        return replacement
    kind = store.node[node]
    if kind[0] == "leaf":
        return node
    left = graft(store, kind[1], target, replacement)
    right = graft(store, kind[2], target, replacement)
    if left == kind[1] and right == kind[2]:
        return node
    return store.app(left, right)


def reduce_term(source, cap=10000):
    """Reduce to normal form, recording every local contraction as an event."""
    store = Store()
    root = store.build(parse(source))
    events = []
    for _ in range(cap):
        found = find_redex(store, root)
        if not found:
            break
        node, _head, args, rule = found
        spine_nodes = []
        cursor = node
        while store.node[cursor][0] == "app":
            spine_nodes.append(cursor)
            cursor = store.node[cursor][1]
        spine_nodes.append(cursor)
        store.step = len(events)
        before = store.text(node)
        after_node = contract_once(store, node, cursor, args, rule)
        events.append(
            {
                "index": store.step,
                "rule": rule,
                "path": list(path_of(store, root, node) or ()),
                "before": before,
                "after": store.text(after_node),
                "made_available_by": sorted(
                    {store.made[n] for n in spine_nodes if store.made[n] >= 0}
                ),
            }
        )
        root = graft(store, root, node, after_node)
    else:
        raise RuntimeError("Unknown: reduction did not reach a normal form")
    return {"store": store, "root": root, "events": events, "normal_form": store.text(root)}


# ---------------------------------------------------------------------------
# cut posets, cut graphs, exact linear algebra
# ---------------------------------------------------------------------------

def order_ideals(deps, count):
    """Every downward-closed subset of {0..count-1}, as a bit mask.

    deps[j] holds the declared predecessors of event j. The enumeration is a
    worklist from the empty ideal, so its cost is proportional to the number of
    ideals and not to two to the count.
    """
    start = 0
    seen = {start}
    stack = [start]
    while stack:
        mask = stack.pop()
        for j in range(count):
            if not (mask >> j) & 1 and all((mask >> d) & 1 for d in deps[j]):
                grown = mask | (1 << j)
                if grown not in seen:
                    seen.add(grown)
                    stack.append(grown)
    return seen


def cut_graph(masks):
    """Edges between ideals that differ in exactly one event, labelled by it."""
    ordered = sorted(masks)
    edges = []
    for i, left in enumerate(ordered):
        for right in ordered[i + 1:]:
            difference = left ^ right
            if difference and not (difference & (difference - 1)):
                edges.append((left, right, difference.bit_length() - 1))
    return ordered, edges


def laplacian(order, edges):
    index = {mask: i for i, mask in enumerate(order)}
    size = len(order)
    matrix = [[F(0)] * size for _ in range(size)]
    for left, right, _ in edges:
        a, b = index[left], index[right]
        matrix[a][a] += 1
        matrix[b][b] += 1
        matrix[a][b] -= 1
        matrix[b][a] -= 1
    return matrix


def matmul(left, right):
    size = len(left)
    return [
        [sum(left[i][k] * right[k][j] for k in range(size)) for j in range(size)]
        for i in range(size)
    ]


def charpoly(matrix):
    """det(x I - matrix) for an integer matrix, by Leverrier's method over Q."""
    size = len(matrix)
    power = [row[:] for row in matrix]
    traces = []
    for _ in range(size):
        traces.append(sum(power[i][i] for i in range(size)))
        power = matmul(power, matrix)
    coefficients = [F(1)]
    for k in range(1, size + 1):
        total = sum(coefficients[j] * traces[k - 1 - j] for j in range(k))
        coefficients.append(-total / k)
    return coefficients


def poly_mul(left, right):
    out = [F(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] += a * b
    return out


def poly_from_roots(roots):
    """The monic polynomial with the given roots, coefficients in descending order."""
    out = [F(1)]
    for root in roots:
        out = poly_mul(out, [F(1), -F(root)])
    return out


def exactly(coefficients):
    return [str(F(c)) for c in coefficients]


# ---------------------------------------------------------------------------
# sections
# ---------------------------------------------------------------------------

def s0_machinery_reproduces_received_cuts(declared):
    """The ideal enumeration must reproduce the received families' own cut masks."""
    families = load(IOTA_INTERPRETATIONS)["families"]
    check(len(families) == declared["received_families"],
          "the received family count changed")
    rows = []
    reproduced = 0
    for family in families:
        deps = [set(event["deps"]) for event in family["events"]]
        got = order_ideals(deps, len(family["events"]))
        want = {cut["mask"] for cut in family["cuts"]}
        rows.append(
            {
                "name": family["name"],
                "events": len(family["events"]),
                "declared_cuts": len(want),
                "recomputed_cuts": len(got),
                "masks_agree": got == want,
            }
        )
        reproduced += got == want
    check(reproduced == len(families), "the ideal machinery does not reproduce every family")
    dependencies = load(FRAME_DEPENDENCIES)
    recorded = dependencies["previous_materials"]
    pins_agree = all(recorded[name] == value for name, value in declared["recorded_pins"].items())
    check(pins_agree, "the pinned digests disagree with the received record")
    return {
        "families": rows,
        "families_reproduced": reproduced,
        "every_family_reproduced": reproduced == len(families),
        "pins_agree_with_the_received_dependencies_record": pins_agree,
    }


def s1_tower_reductions(declared):
    rows = []
    for k in range(len(declared["towers"])):
        source = tower(2 * k + 1)
        check(source == declared["towers"][k], "the generated tower differs from the declared one")
        run = reduce_term(source)
        rows.append(
            {
                "k": k,
                "iota_leaves": 2 * k + 1,
                "source": source,
                "events": run["events"],
                "event_count": len(run["events"]),
                "normal_form": run["normal_form"],
            }
        )
    counts = [row["event_count"] for row in rows]
    check(counts == declared["expected_event_counts"], "the event counts differ")
    check(all(row["normal_form"] == "i" for row in rows), "a tower does not reduce to iota")
    return {
        "towers": rows,
        "event_counts": counts,
        "every_normal_form_is_iota": True,
        "the_four_values_are_equal_and_the_four_ledgers_are_not": len(
            {tuple(json.dumps(e, sort_keys=True) for e in row["events"]) for row in rows}
        ) == len(rows),
    }


def is_path(degrees):
    if len(degrees) == 1:
        return degrees == [0]
    if len(degrees) == 2:
        return sorted(degrees) == [1, 1]
    return sorted(degrees) == sorted([1, 1] + [2] * (len(degrees) - 2))


def s2_cut_structure(declared):
    rows = []
    for index, entry in enumerate(declared["towers"]):
        run = reduce_term(entry)
        deps = [set(event["made_available_by"]) for event in run["events"]]
        count = len(run["events"])
        masks = order_ideals(deps, count) if count else {0}
        order, edges = cut_graph(masks)
        degrees = []
        for mask in order:
            degrees.append(sum(1 for left, right, _ in edges if mask in (left, right)))
        prefixes = {sum(1 << j for j in range(i)) for i in range(count + 1)}
        rows.append(
            {
                "k": index,
                "cuts": len(order),
                "masks": order,
                "cut_set_is_the_prefixes_of_a_total_order": masks == prefixes,
                "edges": [list(edge) for edge in edges],
                "degrees": degrees,
                "cut_graph_is_a_path": is_path(degrees),
                "carrier_dimension": 2 * len(order),
            }
        )
    check([row["cuts"] for row in rows] == declared["expected_cut_counts"], "cut counts differ")
    check([row["carrier_dimension"] for row in rows] == declared["expected_carrier_dimensions"],
          "carrier dimensions differ")
    check(all(row["cut_set_is_the_prefixes_of_a_total_order"] for row in rows),
          "a cut set is not the prefixes of a total order")
    check(all(row["cut_graph_is_a_path"] for row in rows), "a cut graph is not a path")
    return {
        "towers": rows,
        "cut_counts": [row["cuts"] for row in rows],
        "carrier_dimensions": [row["carrier_dimension"] for row in rows],
        "every_cut_graph_is_a_path": True,
        "intrinsic_causal_dimension_claimed": 1,
    }


def s3_frame_operators(declared):
    rows = []
    for index, entry in enumerate(declared["towers"]):
        run = reduce_term(entry)
        deps = [set(event["made_available_by"]) for event in run["events"]]
        count = len(run["events"])
        masks = order_ideals(deps, count) if count else {0}
        order, edges = cut_graph(masks)
        size = len(order)
        lap = laplacian(order, edges)
        degrees = [lap[i][i] for i in range(size)]
        d_max = max(degrees) if size else F(0)
        denominator = F(1) if d_max == 0 else 2 * d_max
        h0 = [[entry_ / denominator for entry_ in row] for row in lap]
        h = [[F(0)] * (2 * size) for _ in range(2 * size)]
        for i in range(size):
            for j in range(size):
                h[i][j] = h0[i][j]
                h[size + i][size + j] = h0[i][j]
        j_matrix = [[F(0)] * (2 * size) for _ in range(2 * size)]
        for i in range(size):
            j_matrix[i][size + i] = F(-1)
            j_matrix[size + i][i] = F(1)
        j_squared = matmul(j_matrix, j_matrix)
        negative_identity = [
            [F(-1) if i == j else F(0) for j in range(2 * size)] for i in range(2 * size)
        ]
        jh = matmul(j_matrix, h)
        hj = matmul(h, j_matrix)
        symmetric = all(h[i][j] == h[j][i] for i in range(2 * size) for j in range(2 * size))
        rows_max = max(sum(abs(value) for value in row) for row in h)
        negation = [[-value for value in row] for row in jh]
        skew = negation == [[jh[j][i] for j in range(2 * size)] for i in range(2 * size)]
        check(j_squared == negative_identity, "J squared is not minus the identity")
        check(hj == jh, "H and J do not commute")
        check(symmetric, "H is not symmetric")
        check(rows_max <= 1, "an absolute row sum of H exceeds one")
        check(skew, "A = -J H is not skew symmetric")
        rows.append(
            {
                "k": index,
                "cuts": size,
                "carrier_dimension": 2 * size,
                "degrees": [str(value) for value in degrees],
                "d_max": str(d_max),
                "denominator": str(denominator),
                "h0_scale": "L" if denominator == 1 else f"L/{denominator}",
                "laplacian_charpoly": exactly(charpoly(lap)) if size <= 16 else None,
                "checks": {
                    "J_squared_is_minus_identity": True,
                    "H_is_symmetric": True,
                    "H_commutes_with_J": True,
                    "absolute_row_sums_at_most_one": True,
                    "A_is_skew": True,
                },
            }
        )
    dimensions = [row["carrier_dimension"] for row in rows]
    check(len(set(dimensions)) == len(dimensions), "two towers share a carrier dimension")
    return {
        "towers": rows,
        "carrier_dimensions_are_pairwise_distinct": True,
        "no_carrier_dimension_is_four": 4 not in dimensions,
        "no_carrier_dimension_is_three_plus_one": 4 not in dimensions,
    }


def s4_unit_cell(declared):
    """Each tower for k >= 1 is the k = 1 ledger repeated k times, chained."""
    cell = reduce_term(declared["towers"][1])
    rows = []
    for k in range(1, len(declared["towers"])):
        run = reduce_term(declared["towers"][k])
        rules = [event["rule"] for event in run["events"]]
        expected_rules = [event["rule"] for event in cell["events"]] * k
        chained = all(
            any(d == 5 * block - 1 for d in run["events"][5 * block]["made_available_by"])
            for block in range(1, k)
        )
        rows.append(
            {
                "k": k,
                "rules": rules,
                "rules_are_the_cell_repeated": rules == expected_rules,
                "blocks_are_chained": chained,
                "events": len(run["events"]),
                "events_equal_five_k": len(run["events"]) == 5 * k,
                "cuts": len(run["events"]) + 1,
                "carrier_dimension": 2 * (len(run["events"]) + 1),
            }
        )
    check(all(row["rules_are_the_cell_repeated"] for row in rows),
          "a tower is not the cell repeated")
    check(all(row["blocks_are_chained"] for row in rows), "the cell blocks are not chained")
    check(all(row["events_equal_five_k"] for row in rows), "events are not five k")
    check([row["carrier_dimension"] for row in rows] == [10 * k + 2 for k in range(1, 4)],
          "the carrier dimension is not ten k plus two")
    return {
        "cell": {"rules": [event["rule"] for event in cell["events"]],
                 "events": len(cell["events"]),
                 "source": declared["towers"][1]},
        "towers": rows,
        "cell_is_the_k_equals_one_frame": True,
    }


def s5_same_dimension_different_operator(declared):
    """The received process and the k = 1 tower share a dimension and not an operator."""
    families = {family["name"]: family for family in load(IOTA_INTERPRETATIONS)["families"]}
    family = families[RECEIVED_PROCESS]
    masks = {cut["mask"] for cut in family["cuts"]}
    order, edges = cut_graph(masks)
    lap = laplacian(order, edges)
    size = len(order)
    received_charpoly = charpoly(lap)
    received_claimed = poly_from_roots([0, 1, 2, 3, 3, 5])
    check([str(value) for value in received_charpoly] == [str(value) for value in received_claimed],
          "the received process's Laplacian characteristic polynomial differs from the claimed one")
    tower_run = reduce_term(declared["towers"][1])
    tower_masks = order_ideals([set(e["made_available_by"]) for e in tower_run["events"]],
                               len(tower_run["events"]))
    tower_order, tower_edges = cut_graph(tower_masks)
    tower_lap = laplacian(tower_order, tower_edges)
    tower_charpoly = charpoly(tower_lap)
    tower_claimed = poly_mul(poly_from_roots([0, 1, 2, 3]), poly_mul([1, -4, 1], [1]))
    check([str(value) for value in tower_charpoly] == [str(value) for value in tower_claimed],
          "the k = 1 tower's Laplacian characteristic polynomial differs from the claimed one")
    discriminant = 16 - 4
    check(discriminant > 0 and int(discriminant ** 0.5) ** 2 != discriminant,
          "the quadratic factor is not irrational")
    check(received_charpoly != tower_charpoly, "the two operators coincide")
    check(size == len(tower_order), "the two cut counts differ")
    return {
        "received": {
            "name": RECEIVED_PROCESS,
            "source": family["source"],
            "events": len(family["events"]),
            "cuts": size,
            "degrees": [str(lap[i][i]) for i in range(size)],
            "h0_scale": "L/6",
            "laplacian_charpoly": exactly(received_charpoly),
            "charpoly_factorisation_claimed": "x (x-1) (x-2) (x-3)^2 (x-5)",
            "spectrum_is_integral": True,
        },
        "tower_k1": {
            "source": declared["towers"][1],
            "events": len(tower_run["events"]),
            "cuts": len(tower_order),
            "degrees": [str(tower_lap[i][i]) for i in range(len(tower_order))],
            "h0_scale": "L/4",
            "laplacian_charpoly": exactly(tower_charpoly),
            "charpoly_factorisation_claimed": "x (x-1) (x-2) (x-3) (x^2-4x+1)",
            "discriminant_of_the_quadratic_factor": discriminant,
            "quadratic_factor_is_irrational": True,
        },
        "same_cut_count": size == len(tower_order),
        "same_carrier_dimension": 2 * size == 2 * len(tower_order),
        "same_operator": False,
        "same_degrees": [str(lap[i][i]) for i in range(size)]
        == [str(tower_lap[i][i]) for i in range(len(tower_order))],
    }


def s6_role_obstruction_and_refusals(declared):
    families = load(IOTA_INTERPRETATIONS)["families"]
    apertures = {
        family["name"]: [letter for letter in "abc" if letter in family["source"]]
        for family in families
    }
    with_apertures = sum(1 for value in apertures.values() if value)
    check(with_apertures == len(families), "a received family carries no aperture leaf")
    tower_leaves = {
        entry: sorted({leaf for leaf in entry if leaf in "abc"}) for entry in declared["towers"]
    }
    check(all(not value for value in tower_leaves.values()),
          "a declared tower carries an aperture leaf")
    refusals = declared["refusals"]
    check(len(refusals) >= 5, "the declared refusal list is short")
    return {
        "received_families": len(families),
        "received_families_carrying_an_aperture": with_apertures,
        "received_aperture_leaves": apertures,
        "tower_aperture_leaves": tower_leaves,
        "towers_declare_no_port": True,
        "roles_bound": False,
        "role_reading": (
            "unbound: the received frame derives {} [] () from explicit entry and exit "
            "policies over declared apertures, and a tower carries none"
        ),
        "refusals": refusals,
        "refusal_count": len(refusals),
    }


def run(output):
    started = time.perf_counter_ns()
    contract = load("experiments/four_iota_frames/contract.json")
    declared = contract["objects"]
    for relative, expected in PINS.items():
        check(digest(relative) == expected, f"pin mismatch: {relative}")
    sections = {
        "S0_machinery_reproduces_received_cuts": s0_machinery_reproduces_received_cuts(declared),
        "S1_tower_reductions": s1_tower_reductions(declared),
        "S2_cut_structure": s2_cut_structure(declared),
        "S3_frame_operators": s3_frame_operators(declared),
        "S4_unit_cell": s4_unit_cell(declared),
        "S5_same_dimension_different_operator": s5_same_dimension_different_operator(declared),
        "S6_role_obstruction_and_refusals": s6_role_obstruction_and_refusals(declared),
    }
    report = {
        "schema": "adva.research.four-iota-frames-evidence.v0",
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
        ("RLIMIT_FSIZE", lambda: resource.setrlimit(
            resource.RLIMIT_FSIZE, (limit["output_bytes"], limit["output_bytes"]))),
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
    LIMITS.update(load("experiments/four_iota_frames/contract.json")["budget"])
    install_limits()
    report, _ = run(args.output)
    print(json.dumps({"status": report["status"], "assertions": report["assertions"]},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
