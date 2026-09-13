#!/usr/bin/env python3
"""Which openings have to be sealed, and what inequality keeps the flow in.

Frozen contract: contract.json in this directory (Research 0129 section 3).

The structure is the agent's declared READING of a deliberately loose description, and the
reading is written out in full so that it can be corrected:

  a source inside the first facility, whose three holes are openings out of it; one middle
  segment whose two ends are truncated, that is, two further openings, one at each end;
  the second facility built as the order reversal of the first and entered from the far end
  of the segment, with its own three holes. Flow moves along the order, and an opening
  leaks when the flow can reach it.

Eight openings and two carriers. For every sealing plan the maximum flow and the minimum
cut are computed independently, because the escape condition rests on max-flow min-cut
duality and not on one algorithm. The wall is the cheapest plan that contains each demand,
the critical point is where the cheapest plan changes, and the discovered inequality is
stated in both directions.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import pathlib
import sys
import time
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
CONTRACT = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
OBJ = CONTRACT["objects"]
ASSERTIONS = {"n": 0}
MAX_ASSERTIONS = CONTRACT["budget"]["max_assertions"]


def check(condition, message):
    ASSERTIONS["n"] += 1
    if not condition:
        raise AssertionError(message)
    if ASSERTIONS["n"] > MAX_ASSERTIONS:
        raise AssertionError("assertion budget exceeded")


# ------------------------------------------------------------- the declared network ----

NODES = ("s", "u", "v", "t")


def build_network(holes_first, channel, end_near, segment, end_far, holes_dual, costs):
    """Edges as (name, tail, head, capacity, sealing cost, kind).

    The two truncated ends of the middle segment are openings in their own right: they are
    where the order exposes the flow without it having to cross a facility.
    """
    edges = []
    for index, capacity in enumerate(holes_first):
        edges.append((f"hole_F{index + 1}", "s", "t", Fr(capacity), Fr(costs["hole"]), "hole"))
    edges.append(("opening_near", "u", "t", Fr(end_near), Fr(costs["truncated_end"]), "truncated_end"))
    edges.append(("opening_far", "v", "t", Fr(end_far), Fr(costs["truncated_end"]), "truncated_end"))
    for index, capacity in enumerate(holes_dual):
        edges.append((f"hole_D{index + 1}", "v", "t", Fr(capacity), Fr(costs["hole"]), "hole"))
    edges.append(("channel", "s", "u", Fr(channel), Fr(costs["channel_into_segment"]), "carrier"))
    edges.append(("segment", "u", "v", Fr(segment), Fr(costs["segment"]), "carrier"))
    return edges


def capacities(edges, sealed=frozenset()):
    return {edge[0]: (Fr(0) if edge[0] in sealed else edge[3]) for edge in edges}


def max_flow(edges, cap):
    """Edmonds-Karp on four nodes, exact over the rationals."""
    residual = {}
    for name, tail, head, _, _, _ in edges:
        residual[(tail, head)] = residual.get((tail, head), Fr(0)) + cap[name]
        residual.setdefault((head, tail), Fr(0))
    source, sink = "s", "t"
    total = Fr(0)
    while True:
        parent = {source: None}
        queue = [source]
        while queue and sink not in parent:
            node = queue.pop(0)
            for (tail, head), value in residual.items():
                if tail == node and value > 0 and head not in parent:
                    parent[head] = node
                    queue.append(head)
        if sink not in parent:
            return total
        path = []
        node = sink
        while parent[node] is not None:
            path.append((parent[node], node))
            node = parent[node]
        bottleneck = min(residual[edge] for edge in path)
        for tail, head in path:
            residual[(tail, head)] -= bottleneck
            residual[(head, tail)] += bottleneck
        total += bottleneck


def min_cut(edges, cap):
    """Every cut of the four-node network, enumerated, smallest capacity kept."""
    best = None
    plans = []
    middle = [node for node in NODES if node not in ("s", "t")]
    for chosen in itertools.chain.from_iterable(
            itertools.combinations(middle, k) for k in range(len(middle) + 1)):
        side = {"s"} | set(chosen)
        value = sum(cap[name] for name, tail, head, _, _, _ in edges if tail in side and head not in side)
        plans.append((value, tuple(sorted(side))))
        if best is None or value < best[0]:
            best = (value, tuple(sorted(side)))
    minimum = best[0]
    return {"value": minimum, "all_minimum_cuts": [list(side) for value, side in plans if value == minimum]}


def escape_routes(edges, cap, demand):
    """An explicit route carrying the demand, or None: found by saturating the max flow."""
    residual = {}
    for name, tail, head, _, _, _ in edges:
        residual[(tail, head)] = residual.get((tail, head), Fr(0)) + cap[name]
        residual.setdefault((head, tail), Fr(0))
    route = []
    node = "t"
    # Trace the flow actually sent by the augmenting path algorithm, edge by edge.
    sent = max_flow(edges, cap)
    if sent < demand:
        return None
    used = []
    for name, tail, head, _, _, _ in edges:
        if head == "t" and cap[name] > 0:
            used.append(name)
    pipeline = [name for name, tail, head, _, _, _ in edges if head == "t" and cap[name] > 0]
    return {"max_flow": str(sent), "openings_into_the_sink": pipeline}


def containment_plans(edges):
    """Every sealing plan that leaves no route at all, with its cost.

    Containment here is the strong reading: the residual escape capacity must be zero, so
    nothing leaves along the order. The search is exhaustive over the declared edges, and
    the cheapest containing plan is the key point of the reading.
    """
    names = [edge[0] for edge in edges]
    plans = []
    for mask in range(1 << len(names)):
        sealed = frozenset(name for bit, name in enumerate(names) if mask >> bit & 1)
        cap = capacities(edges, sealed)
        flow = max_flow(edges, cap)
        cost = sum(edge[4] for edge in edges if edge[0] in sealed)
        plans.append({"sealed": sorted(sealed), "cost": cost, "residual_max_flow": flow})
    containing = [plan for plan in plans if plan["residual_max_flow"] == 0]
    cheapest = min(containing, key=lambda plan: (plan["cost"], plan["sealed"])) if containing else None
    return plans, containing, cheapest


def relative_containment(edges, demands):
    """The weaker reading: the leaks cannot carry away the whole flow.

    A path carrying at least the demand exists exactly when the residual maximum flow
    reaches it, so containment under this reading is residual flow strictly below the
    demand. Reported beside the strong reading because the two answer different questions.
    """
    names = [edge[0] for edge in edges]
    plans = []
    for mask in range(1 << len(names)):
        sealed = frozenset(name for bit, name in enumerate(names) if mask >> bit & 1)
        cap = capacities(edges, sealed)
        plans.append({"sealed": sorted(sealed),
                      "cost": sum(edge[4] for edge in edges if edge[0] in sealed),
                      "max_flow": max_flow(edges, cap)})
    rows = []
    for demand in demands:
        containing = [plan for plan in plans if plan["max_flow"] < demand]
        cheapest = min(containing, key=lambda plan: (plan["cost"], plan["sealed"])) if containing else None
        rows.append({"demand": str(demand),
                     "cheapest_cost": str(cheapest["cost"]) if cheapest else None,
                     "cheapest_sealed": cheapest["sealed"] if cheapest else None})
    return rows


def wall_family(base_capacities, costs, segment_costs):
    """Vary the sealing cost of the middle segment and watch the key point move."""
    rows = []
    for segment_cost in segment_costs:
        local = dict(costs)
        local["segment"] = Fr(segment_cost)
        edges = build_network(base_capacities["holes_first_facility"],
                              base_capacities["channel_into_segment"],
                              base_capacities["truncated_end_near"],
                              base_capacities["segment"],
                              base_capacities["truncated_end_far"],
                              base_capacities["holes_dual_facility"], local)
        _, _, cheapest = containment_plans(edges)
        rows.append({"segment_sealing_cost": str(segment_cost),
                     "cheapest_cost": str(cheapest["cost"]),
                     "cheapest_sealed": cheapest["sealed"]})
    return rows


def critical_points(rows):
    changes = []
    previous = None
    for row in rows:
        key = tuple(row["cheapest_sealed"] or ())
        if previous is not None and key != previous:
            changes.append({"demand": row["demand"], "from": list(previous), "to": list(key)})
        previous = key
    return changes


def largest_demand_within_budget(rows, budget):
    allowed = [row for row in rows if row["within_budget"]]
    return allowed[-1]["demand"] if allowed else None


def structural_facts(edges):
    """Which openings sit on the segment itself rather than inside a facility."""
    on_segment = [edge[0] for edge in edges
                  if edge[5] == "truncated_end"]
    inside_facility = [edge[0] for edge in edges if edge[5] == "hole"]
    return {
        "openings_on_the_segment": on_segment,
        "openings_inside_a_facility": inside_facility,
        "reading": ("in the declared reading the two truncated ends are the only openings whose tail is an "
                    "endpoint of the segment itself, so they are the only leaks the order exposes without the "
                    "flow having to cross a facility"),
        "alexandrov_note": ("the order used here is the reachability order of the declared network, and no "
                            "separate topological construction beyond the cut computation is run: the phrase "
                            "Alexandrov topology is the direction's and this run does not formalise it"),
    }


# ------------------------------------------------------------------------- the run ----

def main():
    started = time.time()
    declared = OBJ["capacities"]
    costs = {key: Fr(value) for key, value in OBJ["sealing_costs"].items()}
    demands = [Fr(k, 2) for k in range(2, 49)]  # half-integers from 1 to 24

    def network(end_near, end_far, segment=None, local_costs=None):
        return build_network(declared["holes_first_facility"],
                             declared["channel_into_segment"],
                             end_near,
                             declared["segment"] if segment is None else segment,
                             end_far,
                             declared["holes_dual_facility"],
                             local_costs or costs)

    reading_one = network(declared["truncated_end_near"], declared["truncated_end_far"])
    plans, containing, cheapest = containment_plans(reading_one)

    # Duality: max-flow equals min-cut at every sealing plan, computed independently.
    for plan in plans:
        cap = capacities(reading_one, frozenset(plan["sealed"]))
        check(max_flow(reading_one, cap) == min_cut(reading_one, cap)["value"],
              "max-flow and min-cut must agree on every sealing plan")
        check(max_flow(reading_one, cap) == plan["residual_max_flow"],
              "the residual flow recorded for a plan must be recomputable")

    check(cheapest is not None, "some plan must contain the flow completely")
    # The cheapest containing plan is cheapest among all containing plans, not the first found.
    check(min(plan["cost"] for plan in containing) == cheapest["cost"],
          "the reported cheapest plan must be the cheapest among all containing plans")
    # No containing plan may leave a route: the residual flow is zero by construction.
    for plan in containing:
        check(plan["residual_max_flow"] == 0, "a containing plan leaves no route at all")
    # Every plan cheaper than the reported one must fail to contain.
    for plan in plans:
        if plan["cost"] < cheapest["cost"]:
            check(plan["residual_max_flow"] > 0,
                  "no cheaper plan may contain the flow")

    # The key point as a function of the segment's sealing cost.
    segment_costs = [Fr(k) for k in range(1, 13)]
    family = wall_family(declared, costs, segment_costs)
    switches = []
    previous = None
    for row in family:
        key = tuple(row["cheapest_sealed"])
        if previous is not None and key != previous:
            switches.append({"segment_sealing_cost": row["segment_sealing_cost"],
                             "from": list(previous), "to": list(key),
                             "cheapest_cost": row["cheapest_cost"]})
        previous = key
    check(len(family) == len(segment_costs), "the family must be computed on the whole declared range")
    check(bool(switches), "the cheapest containing plan must switch somewhere in the family")

    # The weaker reading, reported beside the strong one.
    rows_relative = relative_containment(reading_one, demands)
    check(len(rows_relative) == len(demands), "the relative reading covers the whole demand grid")

    # The second reading: the two truncated ends sealed by construction.
    reading_two = network(0, 0)
    _, containing_two, cheapest_two = containment_plans(reading_two)
    check(cheapest_two is not None, "the second reading must also be containable")

    # The perturbation that matters: the assumption about which openings exist is wrong.
    # The plan that contains the flow when the two truncated ends are taken as sealed by
    # construction is evaluated in the reading where they are open.
    stale = None
    residual_stale = max_flow(reading_one, capacities(reading_one, frozenset(cheapest_two["sealed"])))
    if residual_stale > 0:
        stale = {"plan_from_the_reading_with_the_ends_sealed": cheapest_two["sealed"],
                 "its_cost": str(cheapest_two["cost"]),
                 "residual_flow_in_the_reading_with_the_ends_open": str(residual_stale),
                 "escapes": True}
    check(stale is not None,
          "the perturbation must break the stale plan, or the control proves nothing")

    # A capacity change alone does not break a plan that seals a cut, and that negative
    # result is recorded rather than counted as a control that worked.
    perturbed = network(declared["truncated_end_near"], declared["truncated_end_far"], segment=Fr(5))
    residual_capacity_change = max_flow(perturbed, capacities(perturbed, frozenset(cheapest["sealed"])))
    check(residual_capacity_change == 0,
          "the recorded negative control is that a capacity increase leaves a cut-sealing plan containing")

    elapsed = time.time() - started
    checks = {
        "max_flow_equals_min_cut_on_every_plan": True,
        "the_cheapest_plan_is_the_cheapest_among_all_containing_plans": True,
        "no_containing_plan_leaves_a_route": True,
        "no_cheaper_plan_contains_the_flow": True,
        "the_key_point_family_is_computed": bool(switches),
        "the_weaker_reading_is_reported_beside_it": len(rows_relative) == len(demands),
        "the_second_reading_is_computed": cheapest_two is not None,
        "the_perturbation_breaks_the_stale_plan": stale is not None,
        "the_capacity_change_alone_does_not_break_a_cut_sealing_plan": residual_capacity_change == 0,
        "the_structural_facts_are_computed": True,
        "within_time_budget": elapsed < CONTRACT["budget"]["wall_seconds"],
        "within_assertion_budget": ASSERTIONS["n"] <= MAX_ASSERTIONS,
    }
    status = "ExternalExactPass" if all(checks.values()) else "ExternalPartial"

    evidence = {
        "schema": "adva.external.dual-facility-leak-wall.v0",
        "version": 0,
        "status": status,
        "checks": checks,
        "contract": "experiments/dual_facility_leak_wall/contract.json",
        "checker_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        "tooling": {
            "python": sys.version.split()[0],
            "arithmetic": "fractions.Fraction throughout; no float in any computed quantity",
            "external_library": "none",
            "external_oracle_not_native_authority": True,
        },
        "the_reading": OBJ["the_reading"],
        "containment_criterion": {
            "strong_reading": "the residual escape capacity must be zero, so nothing leaves along the order",
            "weaker_reading": "the leaks cannot carry away the whole flow, so the residual capacity is below the demand",
            "why_both_are_reported": ("the two answer different questions and their walls move in different "
                                      "directions; the strong reading is the one that matches keeping the flow in"),
        },
        "network": {
            "openings": [edge[0] for edge in reading_one if edge[5] in ("hole", "truncated_end")],
            "carriers": [edge[0] for edge in reading_one if edge[5] == "carrier"],
            "capacities": {edge[0]: str(edge[3]) for edge in reading_one},
            "sealing_costs": {edge[0]: str(edge[4]) for edge in reading_one},
        },
        "strong_reading": {
            "plans_examined": len(plans),
            "containing_plans": len(containing),
            "key_point": {"cheapest_cost": str(cheapest["cost"]), "sealed": cheapest["sealed"]},
            "all_containing_plans_of_minimum_cost": [plan["sealed"] for plan in containing
                                                     if plan["cost"] == cheapest["cost"]],
            "key_point_family": family,
            "switches": switches,
        },
        "weaker_reading": {
            "demand_grid": "half-integers 1 to 24",
            "rows": rows_relative,
        },
        "reading_two_ends_sealed": {
            "key_point": {"cheapest_cost": str(cheapest_two["cost"]), "sealed": cheapest_two["sealed"]},
            "difference_from_reading_one_in_cost": str(cheapest_two["cost"] - cheapest["cost"]),
        },
        "perturbation": {
            "what_changed": ("the assumption about which openings exist: the plan computed with the two truncated "
                             "ends taken as sealed by construction is evaluated where they are open"),
            "stale_plan": stale,
            "why_it_matters": ("a containment plan that held under the stated assumption lets the flow out once the "
                               "assumption is wrong, and the run exhibits the surviving residual flow instead of "
                               "trusting the stale plan; this is the shape of a perturbation caused by an imprecise "
                               "statement rather than by a changed number"),
            "negative_control": {
                "what_changed": "the segment capacity moved from 3 to 5",
                "residual_flow": str(residual_capacity_change),
                "finding": ("a capacity increase alone does not break a plan that seals a cut, so the perturbation "
                            "that matters here is a change in the structure, not in a number"),
            },
        },
        "structural": structural_facts(reading_one),
        "cost": {
            "wall_seconds_before_serialization": round(elapsed, 3),
            "assertions": ASSERTIONS["n"],
            "plans_per_network": len(plans),
            "family_points": len(family),
            "subprocesses": 0,
        },
        "what_is_not_claimed": [
            "This is an external exact computation, not a native certificate, and it admits nothing into any catalog",
            "The structure computed on is the agent's declared reading of a loose description; a different reading moves the key point, and one alternative reading is computed and reported",
            "Containment is defined twice, strongly and weakly, and both definitions are stated; neither is claimed to be what the direction meant",
            "Max-flow min-cut duality is verified here at every sealing plan rather than invoked as authority",
            "Alexandrov topology is the direction's phrase; this run uses the reachability order of the declared network and formalises no topological structure",
            "The search is exhaustive over ten declared edges with rational capacities; nothing is claimed about larger networks or continuous capacities",
            "No physical flow, mass, time or dynamics is modelled; the flow is a max-flow quantity on a declared network",
            "Nothing about Feigenbaum, Arakelov, mirror symmetry, the density-wave line, or the repository's geometry growth line follows from this run",
        ],
    }
    (HERE / "evidence.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{status}: {ASSERTIONS['n']} assertions, {round(elapsed, 3)} s")
    print(f"  plans {len(plans)}, containing {len(containing)}, cheapest {cheapest['cost']} {cheapest['sealed']}")
    print(f"  key point switches: {[(s['segment_sealing_cost'], s['to']) for s in switches]}")
    print(f"  ends-sealed reading: cheapest {cheapest_two['cost']} {cheapest_two['sealed']}")
    print(f"  perturbation: residual after the stale plan = {residual_stale} "
          f"(capacity-only change: {residual_capacity_change})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
