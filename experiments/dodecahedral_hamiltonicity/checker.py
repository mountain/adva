#!/usr/bin/env python3
"""Bounded exact check: the dodecahedral graph's Hamiltonian cycles.

Frozen contract: contract.json in this directory (Research 0129 section 3).
Everything here is exact arithmetic in Z[phi], phi^2 = phi + 1. No floating
point is used on the mathematics; time.monotonic() is used for the wall-clock
bound only.

This program is an external oracle, not native Adva authority. It establishes
finite counts for the declared graphs and controls, and nothing else.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent

BUDGET_NODES = 2 * 10**7
BUDGET_SECONDS = 60.0

# ---------------------------------------------------------------- Z[phi] ----

def fadd(u, v):
    return (u[0] + v[0], u[1] + v[1])


def fsub(u, v):
    return (u[0] - v[0], u[1] - v[1])


def fmul(u, v):
    a, b = u
    c, d = v
    return (a * c + b * d, a * d + b * c + b * d)


def fzero(u):
    return u[0] == 0 and u[1] == 0


def fsign(u):
    """Exact sign of a + b*phi = (P + Q*sqrt5)/2, P = 2a+b, Q = b."""
    a, b = u
    P = 2 * a + b
    Q = b
    if Q == 0:
        return (P > 0) - (P < 0)
    if Q > 0:
        if P >= 0:
            return 1
        return 1 if 5 * Q * Q > P * P else -1
    if P <= 0:
        return -1
    return 1 if P * P > 5 * Q * Q else -1


ZERO = (0, 0)
ONE = (1, 0)
PHI = (0, 1)
INVPHI = (-1, 1)  # phi - 1


def vadd(u, v):
    return tuple(fadd(a, b) for a, b in zip(u, v))


def vsub(u, v):
    return tuple(fsub(a, b) for a, b in zip(u, v))


def vdot(u, v):
    acc = ZERO
    for a, b in zip(u, v):
        acc = fadd(acc, fmul(a, b))
    return acc


def vcross(u, v):
    return (
        fsub(fmul(u[1], v[2]), fmul(u[2], v[1])),
        fsub(fmul(u[2], v[0]), fmul(u[0], v[2])),
        fsub(fmul(u[0], v[1]), fmul(u[1], v[0])),
    )


def viszero(u):
    return all(fzero(x) for x in u)


def parallel_same_direction(u, v):
    """True when u and v are nonzero and u = t*v for a strictly positive t."""
    if viszero(u) or viszero(v):
        return False
    if not viszero(vcross(u, v)):
        return False
    return fsign(vdot(u, v)) > 0


# ---------------------------------------------------------------- graphs ----

def signed(values):
    out = []
    for v in values:
        out.append(v)
        out.append(tuple((-x[0], -x[1]) for x in v))
    return out


def icosahedron_vertices():
    verts = []
    for s1 in (ONE, (-1, 0)):
        for s2 in (PHI, (0, -1)):
            verts.append((ZERO, s1, s2))
    for s1 in (ONE, (-1, 0)):
        for s2 in (PHI, (0, -1)):
            verts.append((s1, s2, ZERO))
    for s1 in (ONE, (-1, 0)):
        for s2 in (PHI, (0, -1)):
            verts.append((s2, ZERO, s1))
    unique = []
    for v in verts:
        if v not in unique:
            unique.append(v)
    return unique


def dodecahedron_vertices():
    # the four orbits of the regular dodecahedron, in Z[phi]
    verts = []
    for x in (ONE, (-1, 0)):
        for y in (ONE, (-1, 0)):
            for z in (ONE, (-1, 0)):
                verts.append((x, y, z))
    for sy in (ONE, (-1, 0)):
        for sz in (PHI, (0, -1)):
            verts.append((ZERO, fmul(sy, INVPHI), sz))
    for sx in (ONE, (-1, 0)):
        for sy in (PHI, (0, -1)):
            verts.append((fmul(sx, INVPHI), sy, ZERO))
    for sx in (PHI, (0, -1)):
        for sz in (ONE, (-1, 0)):
            verts.append((sx, ZERO, fmul(sz, INVPHI)))
    return verts


def graph_from_metric(vertices):
    n = len(vertices)
    d2 = {}
    best = None
    for i in range(n):
        for j in range(i + 1, n):
            diff = vsub(vertices[i], vertices[j])
            val = vdot(diff, diff)
            d2[(i, j)] = val
            if best is None or fsign(fsub(val, best)) < 0:
                best = val
    adj = [[] for _ in range(n)]
    for (i, j), val in d2.items():
        if fzero(fsub(val, best)):
            adj[i].append(j)
            adj[j].append(i)
    for row in adj:
        row.sort()
    return adj, best


def edges_of(adj):
    return sorted((min(a, b), max(a, b)) for a, row in enumerate(adj) for b in row if a < b)


def components(adj):
    seen = [False] * len(adj)
    comps = []
    for s in range(len(adj)):
        if seen[s]:
            continue
        stack = [s]
        seen[s] = True
        group = []
        while stack:
            v = stack.pop()
            group.append(v)
            for w in adj[v]:
                if not seen[w]:
                    seen[w] = True
                    stack.append(w)
        comps.append(sorted(group))
    return comps


def girth(adj, cap=6):
    best = None
    n = len(adj)
    for s in range(n):
        dist = {s: 0}
        stack = [s]
        while stack:
            v = stack.pop()
            for w in adj[v]:
                if w not in dist:
                    dist[w] = dist[v] + 1
                    stack.append(w)
                elif dist[w] >= dist[v]:
                    cand = dist[v] + dist[w] + 1
                    if best is None or cand < best:
                        best = cand
    return best


# ------------------------------------------------- Hamiltonian enumeration ----

class Counter:
    def __init__(self):
        self.nodes = 0


def hamiltonian_rooted(adj, counter, start=0, cap=BUDGET_NODES):
    """Oriented cycles rooted at `start`, as tuples of vertex indices."""
    n = len(adj)
    cycles = []
    path = [start]
    visited = 1 << start

    def dfs(v):
        nonlocal visited
        counter.nodes += 1
        if counter.nodes > cap:
            raise BudgetExceeded("node budget exceeded")
        if len(path) == n:
            if start in adj[v]:
                cycles.append(tuple(path))
            return
        for w in adj[v]:
            if not (visited >> w) & 1:
                path.append(w)
                visited |= 1 << w
                dfs(w)
                visited ^= 1 << w
                path.pop()

    dfs(start)
    return cycles


def dp_cycle_count(adj, start=0):
    """Independent Held-Karp style count of oriented cycles rooted at start."""
    n = len(adj)
    if n > 16:
        raise ValueError("dp path used only for small graphs")
    adjmask = [0] * n
    for v, row in enumerate(adj):
        for w in row:
            adjmask[v] |= 1 << w
    full = (1 << n) - 1
    dp = [dict() for _ in range(n)]
    dp[start][1 << start] = 1
    for mask in range(1 << n):
        for v in range(n):
            cur = dp[v].get(mask)
            if not cur:
                continue
            if not (mask >> v) & 1:
                continue
            avail = adjmask[v] & ~mask
            w = 0
            rest = avail
            while rest:
                b = rest & -rest
                w = b.bit_length() - 1
                rest ^= b
                dp[w][mask | b] = dp[w].get(mask | b, 0) + cur
    total = 0
    for v in range(n):
        if (adjmask[start] >> v) & 1:
            total += dp[v].get(full, 0)
    return total


def canonical_cycle(seq):
    n = len(seq)
    rots = []
    for i in range(n):
        r = seq[i:] + seq[:i]
        rots.append(r)
        rots.append(tuple(reversed(r)))
    return min(rots)


def undirected_cycles(adj, counter, cap=BUDGET_NODES):
    rooted = hamiltonian_rooted(adj, counter, cap=cap)
    reps = {}
    for seq in rooted:
        reps.setdefault(canonical_cycle(seq), seq)
    return rooted, reps


class BudgetExceeded(Exception):
    pass


# ------------------------------------------------------------- faces -------

def cycle_order(nb, inner):
    """Order the members of a 5-cycle given each member's two inner neighbours."""
    if len(nb) != 5 or any(len(inner[a]) != 2 for a in nb):
        raise ValueError("not a 5-cycle")
    order = [nb[0]]
    prev = None
    while len(order) < len(nb):
        cur = order[-1]
        cands = sorted(x for x in inner[cur] if x != prev)
        if len(cands) != (2 if prev is None else 1):
            raise ValueError("ambiguous link step")
        nxt = cands[0]
        if nxt in order:
            raise ValueError("cycle closed early")
        prev = cur
        order.append(nxt)
    return order


def link_order(adj, v):
    nb = sorted(adj[v])
    inner = {a: sorted(set(adj[a]) & set(nb)) for a in nb}
    return cycle_order(nb, inner)


def icosahedron_faces(adj):
    faces = set()
    for v in range(len(adj)):
        order = link_order(adj, v)
        for i in range(5):
            faces.add(frozenset((v, order[i], order[(i + 1) % 5])))
    return sorted(faces, key=lambda s: sorted(s))


def dual_graph(faces, ico_adj):
    index = {f: i for i, f in enumerate(faces)}
    n = len(faces)
    adj = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if len(faces[i] & faces[j]) == 2:
                adj[i].append(j)
                adj[j].append(i)
    for row in adj:
        row.sort()
    return adj


def dual_faces(faces, ico_adj, tri_adj):
    """For each icosahedron vertex, the five triangles around it: a 5-cycle."""
    out = []
    index = {f: i for i, f in enumerate(faces)}
    for v in range(len(ico_adj)):
        around = [index[f] for f in faces if v in f]
        if len(around) != 5:
            raise ValueError("vertex does not carry five triangles")
        sub = {a: sorted(b for b in around if b != a and b in tri_adj[a]) for a in around}
        order = cycle_order(sorted(around), sub)
        out.append(tuple(order))
    return out


def check_face_system(adj, faces):
    edge_count = {}
    for face in faces:
        if len(face) != 5 or len(set(face)) != 5:
            return "a face is not a 5-set of distinct vertices"
        for i in range(5):
            a, b = face[i], face[(i + 1) % 5]
            if b not in adj[a]:
                return "a face edge is not an edge"
            key = (min(a, b), max(a, b))
            edge_count[key] = edge_count.get(key, 0) + 1
    if set(edge_count) != set(edges_of(adj)):
        return "faces do not cover exactly the edge set"
    if any(c != 2 for c in edge_count.values()):
        return "an edge is not in exactly two faces"
    return None


# ---------------------------------------------------------- isomorphism ----

def find_isomorphism(a_adj, b_adj):
    """Exact backtracking isomorphism witness; returns {a index: b index} or None."""
    n, m = len(a_adj), len(b_adj)
    if n != m or sorted(len(r) for r in a_adj) != sorted(len(r) for r in b_adj):
        return None
    order = [0]
    seen = {0}
    while len(order) < n:
        frontier = [w for v in order for w in a_adj[v] if w not in seen]
        if not frontier:
            nxt = next(i for i in range(n) if i not in seen)
            frontier = [nxt]
        for w in sorted(set(frontier)):
            if w not in seen:
                seen.add(w)
                order.append(w)
    mapping = {}
    used = set()

    def consistent(u, v):
        for w in a_adj[u]:
            if w in mapping and mapping[w] not in b_adj[v]:
                return False
        for x, y in mapping.items():
            if (y in b_adj[v]) != (x in a_adj[u]):
                return False
        return True

    def bt(i):
        if i == len(order):
            return True
        u = order[i]
        for v in range(m):
            if v in used or len(a_adj[u]) != len(b_adj[v]):
                continue
            if not consistent(u, v):
                continue
            mapping[u] = v
            used.add(v)
            if bt(i + 1):
                return True
            del mapping[u]
            used.discard(v)
        return False

    return dict(mapping) if bt(0) else None


def check_iso(adj_a, adj_b, mapping):
    a_edges = set(edges_of(adj_a))
    b_edges = set(edges_of(adj_b))
    if len(a_edges) != len(b_edges):
        return "edge counts differ"
    for (a, b) in a_edges:
        edge = tuple(sorted((mapping[a], mapping[b])))
        if edge not in b_edges:
            return "an edge does not map to an edge"
    return None


# ------------------------------------------------------------- controls ----

def cycle_graph(n):
    return [[(i - 1) % n, (i + 1) % n] for i in range(n)]


def complete_graph(n):
    return [[j for j in range(n) if j != i] for i in range(n)]


def cube_graph():
    adj = [[] for _ in range(8)]
    for i in range(8):
        for b in (1, 2, 4):
            j = i ^ b
            adj[i].append(j)
    return [sorted(r) for r in adj]


def petersen_graph():
    adj = [[] for _ in range(10)]
    outer = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
    star = [(5, 7), (7, 9), (9, 6), (6, 8), (8, 5)]
    for a, b in outer + star:
        adj[a].append(b)
        adj[b].append(a)
    for i in range(5):
        adj[i].append(i + 5)
        adj[i + 5].append(i)
    return [sorted(r) for r in adj]


def cut_vertex_graph():
    """Two triangles sharing vertex 0: no Hamiltonian cycle by the cut lemma."""
    adj = [[] for _ in range(5)]
    for a, b in ((0, 1), (1, 2), (2, 0), (0, 3), (3, 4), (4, 0)):
        adj[a].append(b)
        adj[b].append(a)
    return [sorted(r) for r in adj]


# ------------------------------------------------------------------ main ----

def main():
    started = time.monotonic()
    counter = Counter()
    evidence = {
        "schema": "adva.dodecahedral-hamiltonicity.evidence.research",
        "version": 0,
        "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "contract": "experiments/dodecahedral_hamiltonicity/contract.json",
        "exact_field": "Z[phi], phi^2 = phi + 1; no floating point on the mathematics",
        "budget": {"nodes": BUDGET_NODES, "seconds": BUDGET_SECONDS},
    }

    # --- construction G1: the standard dodecahedron
    dv = dodecahedron_vertices()
    g1, d2 = graph_from_metric(dv)
    evidence["G1"] = {
        "construction": "standard dodecahedron coordinates in Z[phi]",
        "vertices": len(dv),
        "edges": len(edges_of(g1)),
        "degrees": sorted({len(r) for r in g1}),
        "components": len(components(g1)),
        "girth": girth(g1),
        "min_squared_distance": list(d2),
    }

    # --- construction G2: the dual of the twelve-vertex icosahedron
    iv = icosahedron_vertices()
    ico_adj, ico_d2 = graph_from_metric(iv)
    ico_faces = icosahedron_faces(ico_adj)
    g2 = dual_graph(ico_faces, ico_adj)
    g2_faces = dual_faces(ico_faces, ico_adj, g2)
    evidence["G2"] = {
        "construction": "dual of the twelve-vertex icosahedron; the icosahedron vertex set and its 20 faces follow the golden-ratio calibration conventions",
        "icosahedron_vertices": len(iv),
        "icosahedron_edges": len(edges_of(ico_adj)),
        "icosahedron_faces": len(ico_faces),
        "icosahedron_girth": girth(ico_adj),
        "min_squared_distance_icosahedron": list(ico_d2),
        "vertices": len(g2),
        "edges": len(edges_of(g2)),
        "degrees": sorted({len(r) for r in g2}),
        "components": len(components(g2)),
        "girth": girth(g2),
    }
    mapping = find_isomorphism(g2, g1)

    # independent geometric check: the twenty triangle sums, with adjacency by
    # minimal distance, form a graph isomorphic to the two constructions
    sums = []
    for face in ico_faces:
        total = (ZERO, ZERO, ZERO)
        for v in face:
            total = vadd(total, iv[v])
        sums.append(total)
    sums_adj, sums_d2 = graph_from_metric(sums)
    sums_iso = find_isomorphism(sums_adj, g1)

    iso_error = check_iso(g2, g1, mapping)
    evidence["isomorphism"] = {
        "kind": "exact backtracking isomorphism witness between the two constructions",
        "bijection_G2_to_G1": mapping,
        "error": check_iso(g2, g1, mapping) if mapping else "no isomorphism found",
        "triangle_sums_graph": {
            "vertices": len(sums),
            "edges": len(edges_of(sums_adj)),
            "min_squared_distance": list(sums_d2),
            "isomorphic_to_G1": sums_iso is not None,
        },
    }
    iso_error = evidence["isomorphism"]["error"]
    if iso_error:
        evidence["status"] = "InterfaceFailure"
        evidence["reason"] = iso_error
        return finish(evidence, started, counter)

    # --- face systems
    # cyclic order must be preserved: the isomorphism carries face cycles to face cycles
    g1_faces = [tuple(mapping[i] for i in face) for face in g2_faces]
    face_errors = {
        "G1": check_face_system(g1, g1_faces),
        "G2": check_face_system(g2, [tuple(f) for f in g2_faces]),
    }
    evidence["face_systems"] = {
        "G1_faces": len(g1_faces),
        "G2_faces": len(g2_faces),
        "G1_faces_are_pentagons": all(len(f) == 5 for f in g1_faces),
        "errors": face_errors,
    }
    if any(face_errors.values()):
        evidence["status"] = "InterfaceFailure"
        evidence["reason"] = json.dumps(face_errors)
        return finish(evidence, started, counter)

    # --- Hamiltonian enumeration
    results = {}
    for name, adj, faces in (("G1", g1, g1_faces), ("G2", g2, [tuple(f) for f in g2_faces])):
        rooted, reps = undirected_cycles(adj, counter)
        face_hits = []
        per_face = [0] * len(faces)
        run_hist = {}
        facesets = [frozenset(f) for f in faces]
        for rep in reps.values():
            seq = list(rep)
            n = len(seq)
            runs = 0
            for i in range(n):
                window = frozenset(seq[i : i + 5] if i + 5 <= n else seq[i:] + seq[: (i + 5) - n])
                for fi, fs in enumerate(facesets):
                    if window == fs:
                        runs += 1
                        per_face[fi] += 1
            run_hist[runs] = run_hist.get(runs, 0) + 1
            if runs:
                face_hits.append(rep)
        results[name] = {
            "oriented_rooted_at_0": len(rooted),
            "undirected_unrooted": len(reps),
            "identity_oriented_is_twice_undirected": len(rooted) == 2 * len(reps),
            "face_consecutive_undirected": len(face_hits),
            "face_consecutive_oriented_rooted": 2 * len(face_hits),
            "per_face_counts": per_face,
            "per_face_counts_all_equal": len(set(per_face)) == 1,
            "total_face_run_incidences": sum(per_face),
            "face_runs_per_cycle_histogram": {str(k): v for k, v in sorted(run_hist.items())},
            "every_cycle_satisfies_declared_rule": len(face_hits) == len(reps),
            "cycles": sorted(list(r) for r in reps.values()),
        }
    evidence["hamiltonian"] = results

    # --- controls
    controls = []
    declared = [
        ("C3", cycle_graph(3), 1, "one-line: the only cyclic order"),
        ("C5", cycle_graph(5), 1, "one-line: the only cyclic order"),
        ("K4", complete_graph(4), 3, "one-line: (4-1)!/2 = 3"),
        ("Q3", cube_graph(), None, "computed; DFS and DP must agree"),
        ("Petersen", petersen_graph(), 0, "imported classical fact: Petersen is not Hamiltonian"),
        ("cut-vertex bowtie", cut_vertex_graph(), 0, "one-line cut-vertex lemma"),
    ]
    for name, adj, expected, why in declared:
        rooted = hamiltonian_rooted(adj, counter)
        und = len(rooted) // 2
        dp = dp_cycle_count(adj) if len(adj) <= 16 else None
        controls.append(
            {
                "name": name,
                "vertices": len(adj),
                "edges": len(edges_of(adj)),
                "oriented_rooted_at_0": len(rooted),
                "undirected_unrooted": und,
                "dp_oriented_rooted_at_0": dp,
                "dp_agrees": (dp is None) or (dp == len(rooted)),
                "expected_undirected": expected,
                "expectation_source": why,
                "matches": (expected is None) or (und == expected),
            }
        )
    evidence["controls"] = controls

    # --- verdicts
    checks = {
        "G1_shape_20_30_cubic": evidence["G1"]["vertices"] == 20
        and evidence["G1"]["edges"] == 30
        and evidence["G1"]["degrees"] == [3]
        and evidence["G1"]["components"] == 1,
        "G2_shape_20_30_cubic": evidence["G2"]["vertices"] == 20
        and evidence["G2"]["edges"] == 30
        and evidence["G2"]["degrees"] == [3]
        and evidence["G2"]["components"] == 1,
        "icosahedron_shape_12_30_20": evidence["G2"]["icosahedron_vertices"] == 12
        and evidence["G2"]["icosahedron_edges"] == 30
        and evidence["G2"]["icosahedron_faces"] == 20,
        "girth_five_both": evidence["G1"]["girth"] == 5 and evidence["G2"]["girth"] == 5,
        "isomorphic_counts": results["G1"]["undirected_unrooted"]
        == results["G2"]["undirected_unrooted"]
        and results["G1"]["oriented_rooted_at_0"] == results["G2"]["oriented_rooted_at_0"]
        and results["G1"]["face_consecutive_undirected"]
        == results["G2"]["face_consecutive_undirected"],
        "identity_holds_both": results["G1"]["identity_oriented_is_twice_undirected"]
        and results["G2"]["identity_oriented_is_twice_undirected"],
        "per_face_uniform_both": results["G1"]["per_face_counts_all_equal"]
        and results["G2"]["per_face_counts_all_equal"],
        "controls_match": all(c["matches"] and c["dp_agrees"] for c in controls),
        "within_node_budget": counter.nodes <= BUDGET_NODES,
        "within_time_budget": (time.monotonic() - started) <= BUDGET_SECONDS,
    }
    evidence["checks"] = checks
    evidence["status"] = "Checked" if all(checks.values()) else "Residual"
    return finish(evidence, started, counter)


def finish(evidence, started, counter):
    evidence["cost"] = {
        "nodes": counter.nodes,
        "wall_seconds_before_serialization": (
            (time.monotonic() - started) * 1000 // 1 / 1000
        ),
        "subprocesses": 0,
    }
    text = json.dumps(evidence, indent=2, sort_keys=True)
    (HERE / "evidence.json").write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if evidence["status"] == "Checked" else 1


if __name__ == "__main__":
    sys.exit(main())
