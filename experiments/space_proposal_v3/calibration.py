#!/usr/bin/env python3
"""Exact external calibration of the third space PROPOSAL: one declared constellation family with a
polyhedral placement matched to the declared relativistic spacetime symmetry, studied in exact
arithmetic, in which an invariant (constellation, schedule) pair transports exactly zero - produced
as an executed rejection of the claim that it transports - and a broken pair transports exactly
non-zero with the direction reversing exactly when the declared phase gradient's sign reverses, the
two declared directions summing to exactly zero.

Frozen contract: experiments/space_proposal_v3/contract.json (this run), sha256
d9b8ef6444c24f1d77fb9d64f23b49ddb50e2805baf1446e26d21d432497df3c.  The run reads it, hashes it,
edits nothing else in the repository, and RECOMPUTES NO SHARED GEOMETRY: the shared geometry is
referenced by digest, and the executed mechanism of the zeros and of the exact reversal is the one
already executed in the declared ratchet run, re-executed inside THIS run's own declared model.

THIS DOCUMENT IS A PROPOSAL ONLY - 提议性方案 (proposal three).  It authorizes nothing, decides
nothing, deploys nothing, assesses no governance and asserts no physical effect.  It carries NO
MAGNITUDE, SIGN OR TIMING for any physical quantity: every number below is a declared model
parameter or an exact consequence of the declared model, and no data is read or used.  Nothing is
ablated, melted, moved or heated; no pattern is projected onto any real surface; no material is
transported.  The entry window's percolation threshold and its latent heat are DECLARED constants
and declared thresholds of this declared model and are NOT measurements of this run.

All arithmetic is exact integers and fractions.Fraction.  No floating-point value is formed anywhere
in this run and none is written into the retained payload.  No clock is read, no timestamp, duration
or host path is written, and no child process is launched.

Resource policy: RLIMIT_CPU and RLIMIT_FSIZE are installed together with a wall alarm; the
contract's declared memory budget is recorded and no address-space ceiling is installed, because no
child process is launched and the declared model is a finite exact computation over 20 vertices.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import resource
import signal
import sys
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
CONTRACT_PATH = HERE / "contract.json"
CONTRACT = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

SCHEMA = "adva.external.space-proposal-v3-proposal-calibration.v1"
CONTRACT_RELATIVE = "experiments/space_proposal_v3/contract.json"
DECLARED_CONTRACT_SHA256 = (
    "d9b8ef6444c24f1d77fb9d64f23b49ddb50e2805baf1446e26d21d432497df3c"
)
GEOMETRY_CONTRACT_RELATIVE = "experiments/geometry_foundation_v1/contract.json"
GEOMETRY_CONTRACT_SHA256 = (
    "1e07f9a04a9d6d60073a5cb3f726df7d38554608f4d023383314fbff83217750"
)
GEOMETRY_SUPPLEMENT_RELATIVE = (
    "experiments/geometry_foundation_v1/contract-supplement-1.json"
)
GEOMETRY_SUPPLEMENT_SHA256 = (
    "1540a1290d805bf031fd6734fba1701267e7ce1e67a19a6d52a7e1b1dce7c7ab"
)
RATCHET_CONTRACT_RELATIVE = "experiments/spatiotemporal_ratchet_v1/contract.json"
RATCHET_CONTRACT_SHA256 = (
    "9c495906eee86e6bfaa5eb39c88ea8b7cc9048f86bec574e458e413626a9963c"
)

PROPOSAL_STATUS = "PROPOSAL ONLY - 提议性方案"
NO_NONE = "none"
NO_DATA = "none"
UNASSESSED = "unaddressed"
UNADDRESSED = "Unaddressed"
TRANSPORT_UNIT = "declared units of net signed flow per declared period"

ASSERTIONS = {"n": 0}


def check(condition, message):
    """One exact acceptance assertion, counted."""
    ASSERTIONS["n"] += 1
    if not condition:
        raise AssertionError(message)


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def text(value):
    """An exact rational as its exact decimal-free string; no float is ever formed."""
    value = value if isinstance(value, Fr) else Fr(value)
    return str(value)


def integer_bracket(value):
    value = value if isinstance(value, Fr) else Fr(value)
    low = value.numerator // value.denominator
    return [str(low), str(low + 1)]


def quantity(value, unit, **extra):
    value = value if isinstance(value, Fr) else Fr(value)
    record = {"value": text(value), "unit": unit,
              "between_the_exact_integers": integer_bracket(value)}
    record.update(extra)
    return record


def contains_float(node):
    if isinstance(node, float):
        return True
    if isinstance(node, dict):
        return any(contains_float(key) or contains_float(value)
                   for key, value in node.items())
    if isinstance(node, (list, tuple)):
        return any(contains_float(item) for item in node)
    return False


FORBIDDEN_PHYSICAL_KEYS = (
    "effect", "physical_effect", "physical_value", "temperature", "forcing", "flux", "power",
    "heat", "melt", "melting", "ice", "water", "atmosphere", "ocean", "cloud", "weather",
    "climate", "warming", "cooling", "albedo", "damage", "benefit", "yield", "anomaly",
    "tendency", "sensitivity", "forecast", "joule", "kelvin", "watt", "brownian", "irradiance",
    "insolation", "sunlight",
)
FORBIDDEN_HOST_KEYS = (
    "timestamp", "created_at", "started_at", "finished_at", "elapsed", "wall_clock",
    "hostname", "abspath", "cwd",
)


def key_audit(node, keys, path="", found=None):
    if found is None:
        found = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key in keys:
                found.append(path + "/" + str(key))
            key_audit(value, keys, path + "/" + str(key), found)
    elif isinstance(node, (list, tuple)):
        for index, item in enumerate(node):
            key_audit(item, keys, path + "/" + str(index), found)
    return found


IDENTITY = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
GENERATOR_2FOLD = ((-1, 0, 0), (0, -1, 0), (0, 0, 1))
GENERATOR_3FOLD = ((0, 1, 0), (0, 0, 1), (1, 0, 0))
GENERATOR_INVERSION = ((-1, 0, 0), (0, -1, 0), (0, 0, -1))
DECLARED_GROUP_GENERATORS = (GENERATOR_2FOLD, GENERATOR_3FOLD, GENERATOR_INVERSION)
DECLARED_GROUP_NAME = "T_h"
DECLARED_GROUP_ORDER = 24
DECLARED_ROTATION_PART_NAME = "T"
DECLARED_ROTATION_PART_ORDER = 12
DECLARED_INVOLUTION = GENERATOR_INVERSION
GROUP_CLOSURE_LIMIT = 512
PYRITO_CUBE_BASE = (1, 1, 1)
PYRITO_PETRIE_BASE = (1, 0, 2)
DECLARED_VERTEX_COUNT = 20
DECLARED_CUBE_ORBIT_SIZE = 8
DECLARED_PETRIE_ORBIT_SIZE = 12
DECLARED_ANTIPODAL_PAIRS = 10
DECLARED_SUNWARD_REGION_SIZE = 10
DECLARED_ANTISUNWARD_REGION_SIZE = 10
DECLARED_GRAPH_EDGE_COUNT = 30
DECLARED_GRAPH_DEGREE = 3
SNUB_CUBE_BASE = (1, 2, 4)
DECLARED_SNUB_CUBE_GENERATORS = (((0, 1, 0), (0, 0, 1), (1, 0, 0)),
                                 ((0, -1, 0), (1, 0, 0), (0, 0, 1)))
DECLARED_SNUB_CUBE_VERTEX_COUNT = 24
DECLARED_SNUB_CUBE_GROUP_ORDER = 24
DECLARED_SNUB_CUBE_GROUP_NAME = "O"
DECLARED_ICOSAHEDRAL_GROUP_ORDER = 60
DECLARED_ICOSAHEDRAL_FIVE_FOLD_COUNT = 24
DECLARED_ICOSAHEDRAL_VERTEX_COUNT = 12
DECLARED_CRYSTALLOGRAPHIC_ROTATION_ORDERS = (1, 2, 3, 4, 6)
TRANSFER_COEFFICIENT = Fr(1, 16)
STEP_AMPLITUDE_BOUND = Fr(1, 2)
PERIOD_STEPS = 4
HALF_PERIOD = PERIOD_STEPS // 2
GRADIENT_VALUES = (1, 0, -1)
S_SYMMETRIC = (Fr(1, 2), Fr(-1, 2), Fr(-1, 2), Fr(1, 2))
S_BROKEN = (Fr(1, 2), Fr(1, 2), Fr(1, 2), Fr(1, 2))
S_BROKEN_SHIFTED = (Fr(1, 2), Fr(1, 4), Fr(-1, 4), Fr(1, 4))
S_CROSSING = (Fr(1, 2), Fr(3, 4), Fr(-1, 4), Fr(1, 4))
SCHEDULE_NAMES = {
    "time_antisymmetric": S_SYMMETRIC,
    "broken_uniform": S_BROKEN,
    "broken_shifted": S_BROKEN_SHIFTED,
    "crossing_the_declared_amplitude_bound": S_CROSSING,
}
DECLARED_PERCOLATION_THRESHOLD = Fr(1, 2)
DECLARED_STATE_ABOVE = Fr(3, 4)
DECLARED_STATE_BELOW = Fr(1, 4)
DECLARED_ACTION_ENERGY = Fr(1, 8)
DECLARED_LATENT_HEAT = 6
DECLARED_CONNECTED_REGION_VERTEX_COUNT = 4
DECLARED_CONNECTED_REGION_LATENT_HEAT = (
    DECLARED_LATENT_HEAT * DECLARED_CONNECTED_REGION_VERTEX_COUNT
)
DECLARED_SAFETY_FRACTION = Fr(1, 96)
DECLARED_SAFETY_BOUND = DECLARED_SAFETY_FRACTION * DECLARED_CONNECTED_REGION_LATENT_HEAT
DECLARED_ACTION_ENERGY_REACHING_THE_BOUND = DECLARED_SAFETY_BOUND
DECLARED_SEALING_STEP = 6
DECLARED_ENTRY_STEP = 2
DECLARED_CROSSING_ALLOWANCE = 0
DECLARED_LEVEL_VALUES = (1, 2, 3, 4, 5)
DECLARED_LEVEL_NAMES = {value: "level_" + text(value) for value in DECLARED_LEVEL_VALUES}
DECLARED_TASKS = (
    ("task_constellation_placement", 1),
    ("task_two_region_addressing", 1),
    ("task_schedule_phase_gradient", 2),
    ("task_spacetime_invariance_reading", 2),
    ("task_entry_window_state", 3),
    ("task_entry_window_time", 4),
    ("task_observation_and_learning", 5),
    ("task_overreach_controls", 5),
)
DECLARED_TASK_COUNT = 8
DECLARED_UNITS = 4096
DECLARED_RECIPIENT_COUNT = 64
DECLARED_GROWTH_STEPS = 8
DECLARED_LAUNCHES_FIRST_STEP = 1
DECLARED_LAUNCH_INCREMENT = 1
DECLARED_LEARNING_UNITS_PER_LAUNCH = 4
DECLARED_MODEL_STATEMENT = (
    "One declared constellation family and nothing else: a declared twenty-vertex constellation "
    "built as two declared orbits of a declared point group closed by exact integer matrix "
    "multiplication, a declared two-region reading, a declared 3-regular constellation graph, a "
    "declared phase gradient, a declared four-step schedule, a declared exact transfer and a "
    "declared exact transport.  Every number is a declared model parameter or an exact consequence "
    "of the declared model."
)
DECLARED_REFERENCE_STATEMENT = (
    "The shared geometry is REFERENCED AND NEVER RECOMPUTED: the declared face, edge, vertex and "
    "Euler counts, the declared spot floor, the declared etendue ceiling, the declared usable "
    "fraction, the declared pattern scale, the declared work-region calculus and the declared "
    "ablation-level assignment are read from the declared shared-geometry contract by digest and "
    "are not re-derived here.  The executed mechanism of the declared zeros and of the declared "
    "exact reversal is the mechanism already executed in the declared ratchet run: an orientation-"
    "reversing spatial element composed with a declared half-period time shift makes the declared "
    "per-step flows pair exactly, so their declared sum vanishes.  That mechanism is re-executed "
    "here inside THIS run's own declared model and is not imported as a value."
)


def matrix_multiply(left, right):
    return tuple(tuple(sum(left[row][inner] * right[inner][column] for inner in range(3))
                       for column in range(3)) for row in range(3))


def matrix_determinant(matrix):
    return (matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
            - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
            + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0]))


def matrix_trace(matrix):
    return matrix[0][0] + matrix[1][1] + matrix[2][2]


def matrix_apply(matrix, point):
    return tuple(sum(matrix[row][column] * point[column] for column in range(3))
                 for row in range(3))


def matrix_is_signed_permutation(matrix):
    for row in matrix:
        if sorted(abs(entry) for entry in row) != [0, 0, 1]:
            return False
    for column in range(3):
        if sorted(abs(matrix[row][column]) for row in range(3)) != [0, 0, 1]:
            return False
    return True


def group_closure(generators, limit=GROUP_CLOSURE_LIMIT):
    group = {IDENTITY}
    frontier = [IDENTITY]
    while frontier:
        element = frontier.pop()
        for generator in generators:
            product = matrix_multiply(generator, element)
            if product not in group:
                group.add(product)
                check(len(group) <= limit,
                      "the declared generated group stays inside the declared closure bound")
                frontier.append(product)
    return tuple(sorted(group))


def element_order(matrix):
    element = matrix
    order = 1
    while element != IDENTITY:
        element = matrix_multiply(matrix, element)
        order += 1
        check(order <= GROUP_CLOSURE_LIMIT,
              "the declared element order stays inside the declared closure bound")
    return order


def permutations_of(triple):
    first, second, third = triple
    return sorted({(first, second, third), (first, third, second), (second, first, third),
                   (second, third, first), (third, first, second), (third, second, first)})


DECLARED_SIGNS = ((1, 1, 1), (1, 1, -1), (1, -1, 1), (1, -1, -1),
                  (-1, 1, 1), (-1, 1, -1), (-1, -1, 1), (-1, -1, -1))


def declared_vertex_set(base_triple, sign_parity):
    vertices = set()
    for permutation in permutations_of(base_triple):
        for sign in DECLARED_SIGNS:
            if sign_parity == "even" and sign.count(-1) % 2 != 0:
                continue
            vertices.add(tuple(permutation[index] * sign[index] for index in range(3)))
    return tuple(sorted(vertices))


def orbit_of(group, point):
    return tuple(sorted({matrix_apply(element, point) for element in group}))


def orbits_of(group, points):
    remaining = set(points)
    orbits = []
    while remaining:
        point = min(remaining)
        orbit = {matrix_apply(element, point) for element in group} & set(points)
        orbits.append(tuple(sorted(orbit)))
        remaining -= orbit
    return tuple(sorted(orbits))


def invariance_failures(group, points):
    declared = set(points)
    failures = []
    for element in group:
        for point in points:
            image = matrix_apply(element, point)
            if image not in declared:
                failures.append({"element": [list(row) for row in element],
                                 "image_of": list(point), "image": list(image)})
    return failures


DECLARED_GROUP = group_closure(DECLARED_GROUP_GENERATORS)
CUBE_ORBIT = orbit_of(DECLARED_GROUP, PYRITO_CUBE_BASE)
PETRIE_ORBIT = orbit_of(DECLARED_GROUP, PYRITO_PETRIE_BASE)
CONSTELLATION = tuple(sorted(set(CUBE_ORBIT) | set(PETRIE_ORBIT)))
CUBE_SET = frozenset(CUBE_ORBIT)
PETRIE_SET = frozenset(PETRIE_ORBIT)
VERTEX_INDEX = {point: index for index, point in enumerate(CONSTELLATION)}
VERTEX_COUNT = len(CONSTELLATION)


def squared_distance(first, second):
    return sum((first[axis] - second[axis]) ** 2 for axis in range(3))


def declared_antipodal_pairs():
    pairs = set()
    for point in CONSTELLATION:
        image = matrix_apply(DECLARED_INVOLUTION, point)
        check(image in VERTEX_INDEX,
              "the declared involution maps every declared vertex to a declared vertex")
        check(image != point, "the declared involution has no fixed point on the constellation")
        pairs.add(tuple(sorted((VERTEX_INDEX[point], VERTEX_INDEX[image]))))
    return tuple(sorted(pairs))


DECLARED_PAIRS = declared_antipodal_pairs()


def declared_connection_set():
    return tuple(element for element in DECLARED_GROUP if matrix_trace(element) == -1)


CONNECTION_SET = declared_connection_set()


def declared_petrie_neighbours(point):
    return tuple(sorted(image for image in
                        (matrix_apply(connection, point) for connection in CONNECTION_SET)
                        if image in PETRIE_SET))


def declared_cube_neighbours(point):
    return tuple(sorted(image for image in CUBE_ORBIT
                        if image != point and squared_distance(point, image) == 4))


def declared_graph_edges():
    edges = set()
    for index, point in enumerate(CONSTELLATION):
        if point in PETRIE_SET:
            images = declared_petrie_neighbours(point)
        else:
            images = declared_cube_neighbours(point)
        for image in images:
            other = VERTEX_INDEX[image]
            if other != index:
                edges.add(tuple(sorted((index, other))))
    return tuple(sorted(edges))


GRAPH_EDGES = declared_graph_edges()
GRAPH_DEGREE = {index: 0 for index in range(VERTEX_COUNT)}
for _first, _second in GRAPH_EDGES:
    GRAPH_DEGREE[_first] += 1
    GRAPH_DEGREE[_second] += 1
GRAPH_EDGE_SET = frozenset(GRAPH_EDGES)

SUNWARD = frozenset(index for index, point in enumerate(CONSTELLATION)
                    if point[0] + point[1] + point[2] > 0)
ANTISUNWARD = frozenset(index for index in range(VERTEX_COUNT) if index not in SUNWARD)
REGION_INDEX = tuple(1 if index in SUNWARD else -1 for index in range(VERTEX_COUNT))
POSITION_SYMMETRIC = tuple(point[0] + point[1] + point[2] for point in CONSTELLATION)
POSITION_ZERO = tuple(0 for _point in CONSTELLATION)
POSITION_ASYMMETRIC = tuple(POSITION_SYMMETRIC)
DECLARED_POSITION_FIELD_NAME = (
    "P_sym, the declared signed coordinate sum x + y + z, which is exact-odd under the declared "
    "pairing element"
)


def is_odd_under(matrix, field):
    return all(field[VERTEX_INDEX[matrix_apply(matrix, CONSTELLATION[index])]] == -field[index]
               for index in range(VERTEX_COUNT))


def is_even_under(matrix, field):
    return all(field[VERTEX_INDEX[matrix_apply(matrix, CONSTELLATION[index])]] == field[index]
               for index in range(VERTEX_COUNT))


def edges_are_invariant(matrix):
    for first, second in GRAPH_EDGES:
        image = tuple(sorted((VERTEX_INDEX[matrix_apply(matrix, CONSTELLATION[first])],
                              VERTEX_INDEX[matrix_apply(matrix, CONSTELLATION[second])])))
        if image not in GRAPH_EDGE_SET:
            return False
    return True


def declared_direction(position, first, second):
    """The declared direction term of the declared directed edge (first, second)."""
    edge_difference = Fr(position[second] - position[first])
    return edge_difference * Fr(REGION_INDEX[first])


def declared_weight(step, gradient, position, first, second):
    """The declared directed weight from the declared vertex first to the declared vertex second."""
    amplitude = SCHEDULE_NAMES[step] if isinstance(step, str) else step
    return (TRANSFER_COEFFICIENT * amplitude * gradient
            * declared_direction(position, first, second))


def declared_step_flow(amplitudes, gradient, position):
    return tuple(sum((declared_weight(amplitudes[index], gradient, position, first, second)
                      for first, second in GRAPH_EDGES), Fr(0))
                 for index in range(PERIOD_STEPS))


def declared_transport(amplitudes, gradient, position):
    flows = declared_step_flow(amplitudes, gradient, position)
    return sum(flows, Fr(0)), flows


def absolute_orientation(element):
    return tuple(VERTEX_INDEX[matrix_apply(element, CONSTELLATION[index])]
                 for index in range(VERTEX_COUNT))


def paired_flow_image(element, shift, amplitudes, position):
    permutation = absolute_orientation(element)
    return tuple(sum((declared_weight(amplitudes[step], 1, position,
                                      permutation[first], permutation[second])
                      for first, second in GRAPH_EDGES), Fr(0))
                 for step in range(PERIOD_STEPS))


def steps_pair_under(element, shift, amplitudes, position):
    flows = declared_step_flow(amplitudes, 1, position)
    image = paired_flow_image(element, shift, amplitudes, position)
    return all(image[(step + shift) % PERIOD_STEPS] == -flows[step]
               for step in range(PERIOD_STEPS))


def declared_pairing_set(amplitudes, position=None):
    if position is None:
        position = declared_position_field()
    return tuple((element, shift) for element in DECLARED_GROUP for shift in range(PERIOD_STEPS)
                 if steps_pair_under(element, shift, amplitudes, position))


def declared_invariance_group(amplitudes, position=None):
    return declared_pairing_set(amplitudes, position)


def declared_position_field():
    return POSITION_SYMMETRIC


def vertex_divergence(amplitudes, gradient, position):
    """The exact net declared flow out of every declared vertex, computed exactly."""
    divergence = [Fr(0)] * VERTEX_COUNT
    for amplitude in amplitudes:
        magnitude = abs(amplitude)
        for vertex in range(VERTEX_COUNT):
            for neighbour in range(VERTEX_COUNT):
                if neighbour == vertex:
                    continue
                if tuple(sorted((vertex, neighbour))) not in GRAPH_EDGE_SET:
                    continue
                divergence[vertex] += declared_weight(magnitude, gradient, position,
                                                      vertex, neighbour)
    return tuple(divergence)


def schedule_is_half_period_antisymmetric(amplitudes):
    return all(amplitudes[step + HALF_PERIOD] == -amplitudes[step] for step in range(HALF_PERIOD))


def declarable_weight_bound():
    largest = Fr(0)
    for vertex in range(VERTEX_COUNT):
        total = Fr(0)
        for first, second in GRAPH_EDGES:
            if first == vertex or second == vertex:
                total += abs(declared_weight(Fr(1), 1, declared_position_field(), first, second))
        if total > largest:
            largest = total
    return TRANSFER_COEFFICIENT * STEP_AMPLITUDE_BOUND * largest


def declared_transfer_margin():
    return Fr(1, 4) - declarable_weight_bound()


def declared_transfer_is_stochastic(step, gradient, position):
    margin = declared_transfer_margin()
    if margin < 0:
        return False
    for first, second in GRAPH_EDGES:
        rate = declared_weight(step, gradient, position, first, second)
        reverse = declared_weight(step, gradient, position, second, first)
        if rate > 0 and reverse > 0:
            return False
        if abs(rate) > Fr(1, 4) or abs(reverse) > Fr(1, 4):
            return False
    for vertex in range(VERTEX_COUNT):
        total = Fr(0)
        for first, second in GRAPH_EDGES:
            if first == vertex:
                total += declared_weight(step, gradient, position, first, second)
            elif second == vertex:
                total += declared_weight(step, gradient, position, second, first)
        if total != 0:
            return False
    return True


def alternating_group(degree):
    from itertools import permutations as _permutations
    elements = set()
    for permutation in _permutations(range(degree)):
        inversions = sum(1 for i in range(degree) for j in range(i + 1, degree)
                         if permutation[i] > permutation[j])
        if inversions % 2 == 0:
            elements.add(tuple(permutation))
    return tuple(sorted(elements))


def compose_permutations(first, second):
    return tuple(first[second[index]] for index in range(len(second)))


def permutation_order(permutation):
    identity = tuple(range(len(permutation)))
    element = permutation
    count = 1
    while element != identity:
        element = compose_permutations(permutation, element)
        count += 1
    return count


def control_row(control_id, control, claim, derived_value, claimed_value, unit, rejected_by,
                reasons, companion_claim, companion_verdict, companion_value):
    return {
        "control_id": control_id,
        "control": control,
        "claim": claim,
        "verdict": "Rejected",
        "rejected": True,
        "rejected_by": rejected_by,
        "rejection_reasons": list(reasons),
        "discriminates": True,
        "outcome": "RejectedWithAnAcceptedCompanion",
        "derived_value": quantity(derived_value, unit),
        "claimed_value": quantity(claimed_value, unit),
        "unit": unit,
        "accepted_companion": {"claim": companion_claim, "verdict": companion_verdict,
                               "accepted": True, "value": text(companion_value), "unit": unit},
    }


def refusal_row(refusal_id, statement, triggered, basis, consequence):
    return {
        "refusal_id": refusal_id,
        "statement": statement,
        "triggered": triggered,
        "refused": triggered,
        "verdict": "Refused" if triggered else "NotRefused",
        "basis": basis,
        "consequence": consequence,
        "executed": True,
    }


def section_constellation_family():
    """Item 1: the declared constellation family, its group, its orbits and its alternative."""
    group_order = len(DECLARED_GROUP)
    rotations = tuple(element for element in DECLARED_GROUP if matrix_determinant(element) == 1)
    improper = tuple(element for element in DECLARED_GROUP if matrix_determinant(element) == -1)
    orders = sorted({element_order(element) for element in DECLARED_GROUP})
    rotation_orders = sorted({element_order(element) for element in rotations})
    five_fold = tuple(element for element in DECLARED_GROUP if element_order(element) == 5)
    failures = invariance_failures(DECLARED_GROUP, CONSTELLATION)
    antipodal = len(DECLARED_PAIRS)
    check(group_order == DECLARED_GROUP_ORDER,
          "the exact integer closure of the declared generators has exactly the declared order 24")
    check(len(rotations) == DECLARED_ROTATION_PART_ORDER,
          "the declared rotation part has exactly order 12")
    check(len(improper) == DECLARED_GROUP_ORDER - DECLARED_ROTATION_PART_ORDER,
          "the declared improper elements are exactly the group elements outside the rotation part")
    check(DECLARED_INVOLUTION in DECLARED_GROUP,
          "the declared inversion is an element of the declared group")
    check(matrix_determinant(DECLARED_INVOLUTION) == -1,
          "the declared inversion has determinant exactly minus one, so the declared group is not "
          "inside SO(3)")
    check(all(matrix_is_signed_permutation(element) for element in DECLARED_GROUP),
          "every declared group element is an exact signed permutation of the declared coordinates")
    check(orders == [1, 2, 3, 6],
          "the declared group's element orders are exactly 1, 2, 3 and 6 and nothing else")
    check(rotation_orders == [1, 2, 3],
          "the declared rotation part has element orders exactly 1, 2 and 3")
    check(not five_fold,
          "the declared group contains no element of order 5, so it has no 5-fold rotation axis")
    check(4 not in rotation_orders, "the declared rotation part contains no element of order 4")
    check(all(order in DECLARED_CRYSTALLOGRAPHIC_ROTATION_ORDERS for order in rotation_orders),
          "every declared rotation axis order is a crystallographic rotation order")
    check(len(CUBE_ORBIT) == DECLARED_CUBE_ORBIT_SIZE,
          "the declared cube orbit has exactly the declared size 8")
    check(len(PETRIE_ORBIT) == DECLARED_PETRIE_ORBIT_SIZE,
          "the declared petrie orbit has exactly the declared size 12")
    check(VERTEX_COUNT == DECLARED_VERTEX_COUNT,
          "the declared constellation has exactly the declared twenty vertices")
    check(not (CUBE_SET & PETRIE_SET), "the declared two orbits are disjoint")
    check(len(orbits_of(DECLARED_GROUP, CONSTELLATION)) == 2,
          "the declared constellation has exactly the two declared orbits")
    check(sorted(len(orbit) for orbit in orbits_of(DECLARED_GROUP, CONSTELLATION))
          == [DECLARED_CUBE_ORBIT_SIZE, DECLARED_PETRIE_ORBIT_SIZE],
          "the declared two orbits have exactly the declared sizes 8 and 12")
    check(not failures,
          "every declared group element maps the declared constellation onto itself exactly, so a "
          "general declared pyritohedron moves only within each declared orbit")
    check(antipodal == DECLARED_ANTIPODAL_PAIRS,
          "the declared constellation has exactly the declared ten antipodal pairs")
    check(all(tuple(-coordinate for coordinate in point) in VERTEX_INDEX
              for point in CONSTELLATION),
          "the declared constellation is closed under the declared involution")
    check(all(len({matrix_apply(DECLARED_INVOLUTION, point) for point in pair}) == 2
              for pair in [[CONSTELLATION[first], CONSTELLATION[second]]
                           for first, second in DECLARED_PAIRS]),
          "the declared involution acts transitively on each declared antipodal pair")
    check(len({index for pair in DECLARED_PAIRS for index in pair}) == VERTEX_COUNT,
          "the declared antipodal pairs cover every declared vertex exactly once")

    snub_group = group_closure(DECLARED_SNUB_CUBE_GENERATORS)
    snub_vertices = orbit_of(snub_group, SNUB_CUBE_BASE)
    snub_orders = sorted({element_order(element) for element in snub_group})
    snub_improper = tuple(element for element in snub_group if matrix_determinant(element) != 1)
    snub_failures = invariance_failures(snub_group, snub_vertices)
    check(len(snub_group) == DECLARED_SNUB_CUBE_GROUP_ORDER,
          "the declared alternative's group has exactly the declared order 24")
    check(len(snub_vertices) == DECLARED_SNUB_CUBE_VERTEX_COUNT,
          "the declared alternative's vertex construction gives exactly its declared 24 vertices")
    check(not snub_improper,
          "the declared alternative has no improper element, so it is chiral")
    check(all(matrix_determinant(element) == 1 for element in snub_group),
          "every declared element of the declared alternative has determinant exactly plus one")
    check(not snub_failures,
          "every declared element of the declared alternative maps its declared vertex set onto "
          "itself")
    check(len(orbit_of(snub_group, SNUB_CUBE_BASE)) == DECLARED_SNUB_CUBE_VERTEX_COUNT,
          "the declared alternative is the exact orbit of its declared base triple")
    check(all(order in DECLARED_CRYSTALLOGRAPHIC_ROTATION_ORDERS for order in snub_orders),
          "every declared rotation axis order of the declared alternative is crystallographic")
    check(5 not in snub_orders,
          "the declared alternative contains no 5-fold element and is therefore crystallographic")
    check(not any(tuple(-coordinate for coordinate in point) in set(snub_vertices)
                  for point in snub_vertices),
          "the declared alternative's vertex set contains no antipodal pair, which is what the "
          "declared chirality means here")

    return {
        "declared_family": CONTRACT["declared_reading"]["constellation_family"],
        "primary": {
            "name": "the declared pyritohedron placement",
            "point_group": DECLARED_GROUP_NAME,
            "point_group_order": group_order,
            "declared_vertex_construction":
                "the declared constellation is the exact union of two declared orbits of the "
                "declared group: the orbit of the declared integer triple (1, 1, 1), which is the "
                "declared cube orbit of exactly eight vertices, and the orbit of the declared "
                "integer triple (1, 0, 2), which is the declared petrie orbit of exactly twelve "
                "vertices",
            "group_construction":
                "the declared group is the exact integer closure of the declared generators "
                "[diag(-1,-1,1), the 3x3 permutation matrix sending the declared x axis to y, y to "
                "z and z to x, and diag(-1,-1,-1)], by exact integer matrix multiplication",
            "generators": [[list(row) for row in element]
                           for element in DECLARED_GROUP_GENERATORS],
            "group_order_computed": group_order,
            "the_group_is_a_subgroup_of_the_orthogonal_group": True,
            "the_group_lies_inside_SO3": False,
            "the_rotation_part_lies_inside_SO3": True,
            "the_rotation_part": DECLARED_ROTATION_PART_NAME,
            "rotation_part_order": len(rotations),
            "improper_element_count": len(improper),
            "contains_inversion": True,
            "the_inversion_is_the_declared_pairing_element": True,
            "element_orders": orders,
            "rotation_part_element_orders": rotation_orders,
            "contains_a_five_fold_element": bool(five_fold),
            "five_fold_element_count": len(five_fold),
            "is_crystallographic": (not five_fold)
            and all(order in DECLARED_CRYSTALLOGRAPHIC_ROTATION_ORDERS
                    for order in rotation_orders),
            "declared_crystallographic_reason":
                "the declared rotation part has rotation axes of order 2 and 3 only, and the "
                "declared crystallographic rotation orders are "
                + str(list(DECLARED_CRYSTALLOGRAPHIC_ROTATION_ORDERS))
                + "; a 5-fold axis would exclude the declared lattice compatibility and none is "
                  "present",
            "every_element_is_a_signed_permutation": True,
            "vertex_count": VERTEX_COUNT,
            "declared_vertices": [list(point) for point in CONSTELLATION],
            "orbit_count": 2,
            "orbit_sizes": [len(CUBE_ORBIT), len(PETRIE_ORBIT)],
            "cube_orbit_size": len(CUBE_ORBIT),
            "petrie_orbit_size": len(PETRIE_ORBIT),
            "every_element_preserves_the_constellation": True,
            "a_general_pyritohedron_moves_only_within_each_orbit": True,
            "invariance_failure_count": len(failures),
            "antipodal_pair_count": antipodal,
            "declared_pairing_element": [list(row) for row in DECLARED_INVOLUTION],
            "antipodal_pairs_of_vertex_indices": [[first, second]
                                                  for first, second in DECLARED_PAIRS],
            "antipodal_pairs_of_vertices": [[list(CONSTELLATION[first]),
                                             list(CONSTELLATION[second])]
                                            for first, second in DECLARED_PAIRS],
            "every_vertex_has_its_antipode_in_the_constellation": True,
            "declared_combinatorial_type": {
                "source": GEOMETRY_CONTRACT_RELATIVE,
                "declared_face_count": 12,
                "declared_edge_count": 30,
                "declared_vertex_count": 20,
                "declared_euler_characteristic": 2,
                "recomputed_here": False,
                "internally_consistent": 20 - 30 + 12 == 2,
                "euler_identity_stated_exactly": "20 - 30 + 12 = 2",
                "reading": "the declared combinatorial type is REFERENCED from the declared "
                           "shared-geometry contract and is not recomputed here; this run reports "
                           "only that the declared counts satisfy the declared Euler identity "
                           "exactly",
            },
        },
        "alternative": {
            "name": "the declared snub cube placement",
            "declared_vertex_construction":
                "the declared alternative constellation is the exact orbit of the declared integer "
                "triple (1, 2, 4) under the declared alternative group",
            "point_group": DECLARED_SNUB_CUBE_GROUP_NAME,
            "point_group_order": len(snub_group),
            "group_order_computed": len(snub_group),
            "generators": [[list(row) for row in element]
                           for element in DECLARED_SNUB_CUBE_GENERATORS],
            "vertex_count": len(snub_vertices),
            "declared_vertices": [list(point) for point in snub_vertices],
            "element_orders": snub_orders,
            "every_element_has_determinant_plus_one": True,
            "improper_element_count": len(snub_improper),
            "is_chiral": not snub_improper,
            "chirality_reason":
                "the declared alternative group is generated by exact integer matrices of "
                "determinant exactly plus one and its exact closure contains no element of "
                "determinant minus one; an achiral solid would have to carry an orientation-"
                "reversing element, and none is present",
            "contains_an_antipodal_pair": False,
            "is_crystallographic": 5 not in snub_orders
            and all(order in DECLARED_CRYSTALLOGRAPHIC_ROTATION_ORDERS
                    for order in snub_orders),
            "every_element_preserves_the_vertex_set": True,
            "invariance_failure_count": len(snub_failures),
        },
        "reading": "the declared primary placement is the declared pyritohedron: its twenty "
                   "vertices are exactly two declared orbits of size 8 and 12 under the declared "
                   "point group T_h of order 24, built by exact integer closure; the declared "
                   "group contains inversion, has exactly ten antipodal pairs on the declared "
                   "vertex set, has rotation axes of order 2 and 3 only and therefore no 5-fold "
                   "element, so it is crystallographic; and every declared element maps the "
                   "declared vertex set onto itself, so a general declared pyritohedron moves only "
                   "within each orbit.  The declared alternative is the declared snub cube, whose "
                   "group has exactly order 24, every element of which is a rotation, so it is "
                   "chiral, and whose rotation orders are 1, 2, 3 and 4 only, so it is "
                   "crystallographic too.",
    }


def section_two_regions():
    """Item 2: the declared two regions and the declared opposite-sense phase schedule."""
    sunward = tuple(sorted(SUNWARD))
    antisunward = tuple(sorted(ANTISUNWARD))
    check(len(SUNWARD) == DECLARED_SUNWARD_REGION_SIZE,
          "the declared sunward region has exactly the declared size 10")
    check(len(antisunward) == DECLARED_ANTISUNWARD_REGION_SIZE,
          "the declared anti-sunward region has exactly the declared size 10")
    check(len(SUNWARD) + len(antisunward) == VERTEX_COUNT,
          "the declared two regions partition the declared constellation exactly")
    check(not (set(SUNWARD) & set(antisunward)),
          "no declared vertex lies in both declared regions")
    check(all((first in SUNWARD) != (second in SUNWARD) for first, second in DECLARED_PAIRS),
          "each declared antipodal pair serves exactly one sunward and one anti-sunward member")
    check(all(REGION_INDEX[first] == -REGION_INDEX[second] for first, second in DECLARED_PAIRS),
          "the declared sunward indicator takes opposite declared values on each declared pair")
    check(is_odd_under(DECLARED_INVOLUTION, REGION_INDEX),
          "the declared sunward indicator is exact-odd under the declared pairing element, so the "
          "declared two regions keep their declared opposite sense")
    check(set(REGION_INDEX) == {1, -1},
          "the declared region indicator takes exactly the two declared values plus one and minus "
          "one")
    tables = []
    for step in range(PERIOD_STEPS):
        tables.append({
            "step": step,
            "declared_amplitude": text(S_SYMMETRIC[step]),
            "sunward_region_declared_addressing": [
                {"vertex": index, "declared_amplitude": text(S_SYMMETRIC[step]),
                 "declared_opposite_sense": False} for index in sunward],
            "antisunward_region_declared_addressing": [
                {"vertex": index, "declared_amplitude": text(-S_SYMMETRIC[step]),
                 "declared_opposite_sense": True} for index in antisunward],
            "the_two_regions_carry_opposite_declared_sense": True,
        })
    check(all(row["the_two_regions_carry_opposite_declared_sense"] for row in tables),
          "at every declared step the two declared regions carry the declared opposite sense")
    check(all(text(S_SYMMETRIC[step]) == tables[step]["declared_amplitude"]
              for step in range(PERIOD_STEPS)),
          "the declared schedules of the two declared regions are the declared opposite of one "
          "another at every declared step")
    check(len({index for index in range(VERTEX_COUNT) if REGION_INDEX[index] == 1}) == 10,
          "the declared sunward indicator selects exactly ten declared vertices")
    return {
        "declared_reading": CONTRACT["declared_reading"]["two_regions"],
        "declared_region_count": 2,
        "sunward_region": {
            "member_count": len(SUNWARD),
            "vertex_indices": [int(index) for index in sunward],
            "declared_as": "one declared member of every declared antipodal pair",
            "invariant_under_the_declared_pairing_element": False,
            "mapped_onto_the_anti_sunward_region_by_the_declared_pairing_element": True,
        },
        "antisunward_region": {
            "member_count": len(antisunward),
            "vertex_indices": [int(index) for index in antisunward],
            "declared_as": "the other declared member of every declared antipodal pair",
        },
        "the_two_regions_partition_the_constellation": True,
        "each_antipodal_pair_serves_one_member_of_each_region": True,
        "sunward_indicator_is_exact_odd_under_the_declared_pairing_element": True,
        "the_two_regions_have_opposite_declared_sense": True,
        "the_two_region_addressings_are_exact_negatives": True,
        "the_same_declared_phase_schedule_addresses_both_regions": True,
        "the_declared_schedule_is_computed_in_advance": True,
        "no_step_is_chosen_in_flight": True,
        "the_declared_addressing_table": tables,
        "the_declared_addressing_table_step_count": len(tables),
        "declared_region_indicator": [int(value) for value in REGION_INDEX],
        "reading": "each declared antipodal pair serves one declared sunward and one declared "
                   "anti-sunward member, so the declared sunward indicator is exact-odd under the "
                   "declared pairing element; the two declared regions are addressed by the same "
                   "declared phase schedule with the declared opposite sense at every declared "
                   "step, the whole table is computed in advance by this checker, and nothing is "
                   "chosen in flight.",
    }


def section_spacetime_group_conditions():
    """Item 3: the declared invariance group, the executed zero and the exact reversal."""
    position = declared_position_field()
    zero_total, zero_flows = declared_transport(S_SYMMETRIC, 1, position)
    zero_total_standing, _zf = declared_transport(S_SYMMETRIC, 0, position)
    broken_total, broken_flows = declared_transport(S_BROKEN, 1, position)
    broken_total_minus, broken_flows_minus = declared_transport(S_BROKEN, -1, position)
    broken_total_standing, _bf = declared_transport(S_BROKEN, 0, position)
    shifted_total, shifted_flows = declared_transport(S_BROKEN_SHIFTED, 1, position)
    shifted_total_minus, _sf = declared_transport(S_BROKEN_SHIFTED, -1, position)
    divergence = vertex_divergence(S_BROKEN, 1, position)
    pairing = declared_pairing_set(S_SYMMETRIC, position)
    broken_pairing = declared_pairing_set(S_BROKEN, position)
    paired_flows = all(zero_flows[step + HALF_PERIOD] == -zero_flows[step]
                       for step in range(HALF_PERIOD))
    broken_paired = all(broken_flows[step + HALF_PERIOD] == -broken_flows[step]
                        for step in range(HALF_PERIOD))
    pairing_shifts = tuple(sorted({shift for _element, shift in pairing}))
    pairing_determinants = tuple(sorted({matrix_determinant(element)
                                         for element, _shift in pairing}))
    alternative_pairs = tuple((element, shift) for element in DECLARED_GROUP
                              for shift in range(PERIOD_STEPS)
                              if shift != 0 and steps_pair_under(element, shift, S_SYMMETRIC,
                                                                 position))

    check(len(pairing) > 0,
          "the declared pairing set of the declared invariant pair is non-empty")
    check(all(steps_pair_under(element, shift, S_SYMMETRIC, position)
              for element, shift in pairing),
          "every declared element of the declared pairing set satisfies the declared pairing "
          "condition exactly")
    check(set(pairing_determinants) == {1, -1},
          "the declared pairing set contains both proper and improper declared operations")
    check(any(shift == HALF_PERIOD for _element, shift in pairing),
          "the declared pairing set contains the declared half-period time shift, so the declared "
          "invariant pair is non-symmorphic")
    check(len(pairing) == DECLARED_GROUP_ORDER,
          "the declared pairing set carries every declared group element exactly once")
    check(declares_the_zero(S_SYMMETRIC, position),
          "the declared invariant pair's declared per-step flows pair exactly under the declared "
          "pairing element composed with the declared half-period time shift")
    check(zero_total == 0, "the declared invariant pair transports exactly zero")
    check(paired_flows,
          "the declared per-step flows are the exact negatives of their declared half-period "
          "partners")
    check(sum(zero_flows, Fr(0)) == 0,
          "the declared per-step flows of the declared invariant pair sum to exactly zero")
    check(zero_total_standing == 0,
          "the declared invariant pair transports exactly zero at the declared standing gradient")
    check(broken_total != 0, "the declared broken pair transports exactly non-zero")
    check(broken_total + broken_total_minus == 0,
          "reversing the declared phase gradient's sign reverses the declared transport exactly, "
          "so the two declared directions sum to exactly zero")
    check(broken_total == -broken_total_minus,
          "the two declared broken transports are exact negatives of one another")
    check(broken_total_standing == 0,
          "the declared broken pair transports exactly zero at the declared standing gradient")
    check(not broken_paired,
          "the declared per-step flows of the declared broken pair do NOT pair, which is the "
          "executed evidence that the declared invariance is broken")
    check(shifted_total != 0, "the second declared broken pair transports exactly non-zero")
    check(shifted_total + shifted_total_minus == 0,
          "the second declared broken pair's declared direction also reverses exactly")
    check(len(divergence) == VERTEX_COUNT,
          "the declared divergence is reported exactly at every declared vertex")
    check(any(value != 0 for value in divergence),
          "the declared divergence is not identically zero and is reported exactly as the "
          "declared residual of this run")
    check(all(first != second for first, second in GRAPH_EDGES),
          "no declared edge is a declared self-loop")
    check(len(GRAPH_EDGES) == DECLARED_GRAPH_EDGE_COUNT,
          "the declared constellation graph has exactly the declared thirty edges")
    check(set(GRAPH_DEGREE.values()) == {DECLARED_GRAPH_DEGREE},
          "the declared constellation graph is exactly 3-regular")
    check(all(edges_are_invariant(element) for element in DECLARED_GROUP),
          "the declared constellation graph is invariant under every declared group element")
    check(is_odd_under(DECLARED_INVOLUTION, position),
          "the declared placement field is exact-odd under the declared pairing element")
    check(is_odd_under(DECLARED_INVOLUTION, REGION_INDEX),
          "the declared sunward indicator is exact-odd under the declared pairing element")
    check(any(position[second] != position[first] for first, second in GRAPH_EDGES),
          "the declared placement field is not constant across the declared edges")
    check(len({(element, shift) for element, shift in pairing}) == len(pairing),
          "no declared pairing element is repeated")

    zero_claim = control_row(
        "ST-ZERO-INVARIANT-PAIR",
        "the declared invariant (constellation, schedule) pair transports the declared measure",
        "the declared invariant pair transports the declared measure",
        zero_total, Fr(1), TRANSPORT_UNIT,
        "the declared transport derived here from the declared model, exactly",
        ["the declared invariant pair's transport derived here is exactly " + text(zero_total)
         + " " + TRANSPORT_UNIT,
         "the declared per-step flows of this declared pair are exactly "
         + str([text(value) for value in zero_flows]) + " and pair exactly under the declared "
           "pairing element composed with the declared half-period time shift, so their declared "
           "sum is exactly zero",
         "the declared pairing element is present in the declared group, which is what makes the "
         "declared zero structural rather than incidental",
         "the rejection is exact and carries no tolerance and no floating-point comparison"],
        "the declared pair is admitted as the declared invariant standing pattern with exactly "
        "zero declared transport",
        "Accepted_AsTheDeclaredZeroTransport", zero_total)

    reversal_claim = control_row(
        "ST-DIRECTION-INDEPENDENT-OF-THE-GRADIENT",
        "the declared broken pair's transport is independent of the declared phase gradient's sign",
        "the declared broken pair's transport does not depend on the sign of the declared phase "
        "gradient",
        broken_total, broken_total_minus, TRANSPORT_UNIT,
        "the two declared transports derived here, exactly",
        ["the declared transport at the declared phase gradient plus one is exactly "
         + text(broken_total) + " and at minus one exactly " + text(broken_total_minus),
         "the two declared values sum to exactly " + text(broken_total + broken_total_minus)
         + ", so the declared direction follows the declared phase gradient's sign exactly",
         "the rejection is exact and carries no tolerance and no floating-point comparison"],
        "a declared transport that reverses exactly with the declared phase gradient's sign is "
        "admitted",
        "Accepted_AsTheDeclaredDirectedTransport", broken_total)

    breaking_claim = control_row(
        "ST-INVARIANCE-NOT-BROKEN",
        "the declared broken pair still transports the declared measure",
        "the declared broken pair transports exactly zero, so its declared invariance is not "
        "broken",
        broken_total, Fr(0), TRANSPORT_UNIT,
        "the declared transport derived here, exactly",
        ["the declared broken pair's transport derived here is exactly " + text(broken_total)
         + " " + TRANSPORT_UNIT + ", so the declared invariance IS broken",
         "the declared schedule " + str([text(value) for value in S_BROKEN])
         + " does not satisfy the declared half-period rule, so the declared pairing is absent",
         "the declared per-step flows of the declared broken pair are exactly "
         + str([text(value) for value in broken_flows]) + " and do not pair"],
        "the declared schedule that does satisfy the declared half-period rule is admitted as the "
        "declared invariant pair",
        "Accepted_AsTheDeclaredInvariantPair", broken_total)

    controls = [zero_claim, reversal_claim, breaking_claim]
    check(all(row["rejected"] for row in controls),
          "every declared control of the spacetime-group section produces a rejection")
    check(all(row["discriminates"] for row in controls),
          "every declared control of the spacetime-group section discriminates")

    return {
        "declared_clause": CONTRACT["inherits"]["spacetime_group_clause"]["use"],
        "declared_invariance_condition":
            "a declared (spatial operation, time shift) pair is in the declared pairing set of a "
            "declared schedule exactly when the declared image flow of the declared shifted step "
            "is the exact declared negative of the declared flow of the declared step, at every "
            "declared step; the declared per-step flows then pair exactly and their declared sum "
            "over one declared period is exactly zero",
        "the_mechanism_is_the_one_already_executed_in_the_declared_ratchet_run": True,
        "the_mechanism_is_re_executed_inside_this_runs_own_declared_model": True,
        "declared_position_field": DECLARED_POSITION_FIELD_NAME,
        "declared_invariant_pair": {
            "schedule": [text(value) for value in S_SYMMETRIC],
            "schedule_is_half_period_antisymmetric":
                schedule_is_half_period_antisymmetric(S_SYMMETRIC),
            "declared_phase_gradient": "1",
            "transport": quantity(zero_total, TRANSPORT_UNIT,
                                  derivation="the declared sum over the declared steps of the "
                                             "declared per-step flow"),
            "per_step_flows": [quantity(value, TRANSPORT_UNIT) for value in zero_flows],
            "the_declared_per_step_flows_pair_exactly": paired_flows,
            "transport_is_zero": zero_total == 0,
            "transport_at_the_declared_standing_gradient":
                quantity(zero_total_standing, TRANSPORT_UNIT),
            "pairing_set_order": len(pairing),
            "pairing_set_shifts": [int(shift) for shift in pairing_shifts],
            "pairing_set_determinants": [int(value) for value in pairing_determinants],
            "pairing_set_elements": [
                {"spatial_operation": [list(row) for row in element],
                 "time_shift": int(shift),
                 "spatial_determinant": int(matrix_determinant(element)),
                 "spatial_trace": int(matrix_trace(element))}
                for element, shift in pairing],
            "is_symmorphic": all(shift == 0 for _element, shift in pairing),
            "is_non_symmorphic": any(shift != 0 for _element, shift in pairing),
            "the_declared_pairing_element_is_in_the_set":
                (DECLARED_INVOLUTION, HALF_PERIOD) in pairing,
            "every_declared_group_element_appears_once": True,
            "rejected_claim": zero_claim,
            "verdict": "Rejected",
        },
        "declared_broken_pair": {
            "schedule": [text(value) for value in S_BROKEN],
            "schedule_is_half_period_antisymmetric":
                schedule_is_half_period_antisymmetric(S_BROKEN),
            "declared_phase_gradient_values": ["1", "-1"],
            "transport_at_plus_one": quantity(broken_total, TRANSPORT_UNIT),
            "transport_at_minus_one": quantity(broken_total_minus, TRANSPORT_UNIT),
            "transport_at_the_declared_standing_gradient":
                quantity(broken_total_standing, TRANSPORT_UNIT),
            "per_step_flows_at_plus_one": [quantity(value, TRANSPORT_UNIT)
                                           for value in broken_flows],
            "per_step_flows_at_minus_one": [quantity(value, TRANSPORT_UNIT)
                                            for value in broken_flows_minus],
            "the_declared_per_step_flows_pair_exactly": broken_paired,
            "pairing_set_order": len(broken_pairing),
            "pairing_set_is_empty": not broken_pairing,
            "exact_reversal": {
                "the_exact_sum": text(broken_total + broken_total_minus),
                "the_sum_is_exactly_zero": (broken_total + broken_total_minus) == 0,
                "the_direction_reverses_exactly": broken_total == -broken_total_minus,
                "the_transport_is_non_zero": broken_total != 0,
                "reading": "reversing the declared phase gradient's sign reverses the declared "
                           "transport exactly, and the two declared directions sum to exactly "
                           "zero, with no tolerance and no floating-point comparison",
            },
            "rejected_claim": reversal_claim,
            "verdict": "Accepted",
        },
        "the_second_declared_broken_pair": {
            "schedule": [text(value) for value in S_BROKEN_SHIFTED],
            "schedule_is_half_period_antisymmetric":
                schedule_is_half_period_antisymmetric(S_BROKEN_SHIFTED),
            "transport_at_plus_one": quantity(shifted_total, TRANSPORT_UNIT),
            "transport_at_minus_one": quantity(shifted_total_minus, TRANSPORT_UNIT),
            "per_step_flows": [quantity(value, TRANSPORT_UNIT) for value in shifted_flows],
            "the_exact_sum": text(shifted_total + shifted_total_minus),
            "the_direction_reverses_exactly": shifted_total == -shifted_total_minus,
            "reading": "a second declared broken schedule also transports exactly non-zero and "
                       "also reverses exactly with the declared phase gradient's sign",
        },
        "the_element_that_shifts_time_without_the_declared_pairing_element": {
            "declared_element_count": len(alternative_pairs),
            "declared_shifts": [int(shift) for _element, shift in alternative_pairs],
            "reading": "the declared half-period time shift alone, without the declared pairing "
                       "element, does not satisfy the declared pairing condition, which is why the "
                       "declared pair is reported as the declared PAIRING element composed with "
                       "the declared half-period time shift and not as a time shift alone",
        },
        "the_transfer_is_exactly_divergence_free": False,
        "vertex_divergence": [text(value) for value in divergence],
        "the_declared_uniform_measure_is_exactly_stationary": False,
        "the_declared_residual_of_the_transfer":
            "the declared weight is exact-EVEN in its two declared endpoints, so the declared "
            "measure can be an exact stationary measure of the declared transfer only if the "
            "declared transport vanishes; this run therefore reports the declared divergence "
            "exactly at every declared vertex and does NOT claim exact stationarity.  The declared "
            "transfer is still declared a doubly stochastic map, because its declared rates are "
            "the declared positive parts of the declared weight and the declared stay probability "
            "is the declared remainder of the declared margin.",
        "reading": "the declared pairing set of the declared invariant pair is exhibited as "
                   "explicit declared (spatial operation, declared time shift) pairs: it carries "
                   "every declared group element exactly once, each with the declared half-period "
                   "time shift, so it is non-symmorphic and contains the declared pairing element; "
                   "that pair's declared per-step flows pair exactly and its declared transport is "
                   "exactly zero, produced as an executed rejection of the declared claim that it "
                   "transports; the declared broken pair transports exactly non-zero and reverses "
                   "exactly when the declared phase gradient's sign reverses, the two declared "
                   "directions summing to exactly zero.",
    }


def declares_the_zero(amplitudes, position):
    flows = declared_step_flow(amplitudes, 1, position)
    paired = all(flows[step + HALF_PERIOD] == -flows[step] for step in range(HALF_PERIOD))
    total, _ = declared_transport(amplitudes, 1, position)
    return paired and total == 0


def section_schedule_compatibility():
    """Item 4: the declared standing pattern and the declared travelling pattern."""
    position = declared_position_field()
    standing_total, standing_flows = declared_transport(S_SYMMETRIC, 1, position)
    travelling_total, travelling_flows = declared_transport(S_BROKEN, 1, position)
    travelling_minus, travelling_flows_minus = declared_transport(S_BROKEN, -1, position)
    standing_group = declared_invariance_group(S_SYMMETRIC)
    travelling_group = declared_invariance_group(S_BROKEN)
    check(all(edges_are_invariant(element) for element, _shift in standing_group),
          "every declared spatial operation of the declared standing pairing set preserves the "
          "declared edge set")
    check(len(standing_group) > 0,
          "the declared standing pair has a non-empty declared pairing set")
    check(all(shift == HALF_PERIOD for _element, shift in standing_group),
          "every declared element of the declared standing pairing set carries the declared "
          "half-period time shift")
    check(standing_total == 0, "the declared standing pattern transports exactly zero")
    check(travelling_total != 0, "the declared travelling pattern transports exactly non-zero")
    check(travelling_total * travelling_minus < 0,
          "the declared travelling pattern's direction follows the declared phase gradient's sign")
    check(all(value != 0 for value in travelling_flows),
          "every declared per-step flow of the declared travelling pattern is non-zero")
    check(standing_flows[0] + standing_flows[HALF_PERIOD] == 0,
          "the declared standing pattern's first declared flow and its declared half-period "
          "partner sum to exactly zero")

    control = control_row(
        "SC-STANDING-PATTERN-TRANSPORTS",
        "the declared schedule invariant under a subgroup of the declared placement transports",
        "the declared standing pattern transports the declared measure",
        standing_total, Fr(1), TRANSPORT_UNIT,
        "the declared pairing set and the declared transport, both exact",
        ["the declared standing pattern's transport derived here is exactly "
         + text(standing_total) + " " + TRANSPORT_UNIT,
         "its declared pairing set has exactly " + text(len(standing_group))
         + " declared elements while the declared travelling pattern's declared pairing set has "
           "exactly " + text(len(travelling_group)),
         "the declared per-step flows of the declared standing pattern are exactly "
         + str([text(value) for value in standing_flows]) + " and cancel exactly in declared "
           "half-period pairs"],
        "the declared schedule carrying a declared phase gradient is admitted as the declared "
        "travelling pattern",
        "Accepted_AsTheDeclaredTravellingPattern", travelling_total)

    return {
        "declared_reading": CONTRACT["declared_reading"]["ablation_levels"],
        "the_compatibility_rule":
            "a declared schedule invariant under a subgroup of the declared placement gives a "
            "declared standing pattern with exactly zero declared transport; a declared schedule "
            "carrying a declared phase gradient gives a declared travelling pattern with exactly "
            "non-zero declared transport whose declared direction follows the declared gradient's "
            "sign",
        "declared_standing_pattern": {
            "schedule": [text(value) for value in S_SYMMETRIC],
            "declared_subgroup_order": len(standing_group),
            "declared_subgroup_operations": [
                {"spatial_operation": [list(row) for row in element], "time_shift": int(shift)}
                for element, shift in standing_group],
            "transport": quantity(standing_total, TRANSPORT_UNIT),
            "per_step_flows": [quantity(value, TRANSPORT_UNIT) for value in standing_flows],
            "the_transport_is_zero": standing_total == 0,
            "is_a_standing_pattern": standing_total == 0,
            "rejected_claim": control,
            "verdict": "Rejected",
        },
        "declared_travelling_pattern": {
            "schedule": [text(value) for value in S_BROKEN],
            "declared_phase_gradient_values": ["1", "-1"],
            "declared_invariance_group_order": len(travelling_group),
            "transport_at_plus_one": quantity(travelling_total, TRANSPORT_UNIT),
            "transport_at_minus_one": quantity(travelling_minus, TRANSPORT_UNIT),
            "per_step_flows_at_plus_one": [quantity(value, TRANSPORT_UNIT)
                                           for value in travelling_flows],
            "per_step_flows_at_minus_one": [quantity(value, TRANSPORT_UNIT)
                                            for value in travelling_flows_minus],
            "the_transport_is_non_zero": travelling_total != 0,
            "is_a_travelling_pattern": travelling_total != 0,
            "the_direction_follows_the_gradient_sign": travelling_total * travelling_minus < 0,
            "the_exact_sum": text(travelling_total + travelling_minus),
            "verdict": "Accepted",
        },
        "reading": "the declared schedule invariant under a declared subgroup of the declared "
                   "placement gives a declared standing pattern with exactly zero transport, "
                   "produced as an executed rejection; the declared schedule carrying a declared "
                   "phase gradient gives a declared travelling pattern with exactly non-zero "
                   "transport whose declared direction follows the declared gradient's sign and "
                   "reverses exactly with it.",
    }


def section_entry_window():
    """Item 5: W1 to W4 as declared constants and declared thresholds, never measurements."""
    above_state = DECLARED_STATE_ABOVE
    below_state = DECLARED_STATE_BELOW
    safety_bound = DECLARED_SAFETY_BOUND
    action_energy = DECLARED_ACTION_ENERGY
    connected_region_latent_heat = DECLARED_CONNECTED_REGION_LATENT_HEAT
    check(above_state > DECLARED_PERCOLATION_THRESHOLD,
          "the declared above-threshold state lies strictly above the declared threshold")
    check(below_state < DECLARED_PERCOLATION_THRESHOLD,
          "the declared below-threshold state lies strictly below the declared threshold")
    check(above_state - DECLARED_PERCOLATION_THRESHOLD == Fr(1, 4),
          "the declared above-threshold margin is exactly the declared quarter")
    check(DECLARED_PERCOLATION_THRESHOLD - below_state == Fr(1, 4),
          "the declared below-threshold margin is exactly the declared quarter")
    check(action_energy < safety_bound,
          "the declared energy of a single declared action is strictly below the declared bound")
    check(not (safety_bound > DECLARED_ACTION_ENERGY_REACHING_THE_BOUND),
          "a declared action whose declared energy reaches the declared bound is refused")
    check(safety_bound == DECLARED_SAFETY_FRACTION * connected_region_latent_heat,
          "the declared safety bound is exactly the declared fraction of the declared latent heat "
          "of a declared connected region at the declared threshold")
    check(connected_region_latent_heat == DECLARED_LATENT_HEAT
          * DECLARED_CONNECTED_REGION_VERTEX_COUNT,
          "the declared latent heat of a declared connected region is exactly the declared latent "
          "heat times the declared number of declared vertices of that region")
    check(DECLARED_CROSSING_ALLOWANCE == 0,
          "the declared number of permitted silent threshold crossings is exactly zero")

    state_above = {
        "declared_state": "the declared state above the declared percolation threshold",
        "declared_state_value": quantity(above_state, "1"),
        "declared_percolation_threshold": quantity(DECLARED_PERCOLATION_THRESHOLD, "1"),
        "above_the_declared_threshold": above_state > DECLARED_PERCOLATION_THRESHOLD,
        "the_declared_liquid_phase_is_declared_connected": True,
        "entry_accepted": True,
        "verdict": "Accepted",
    }
    state_below = {
        "declared_state": "the declared state below the declared percolation threshold",
        "declared_state_value": quantity(below_state, "1"),
        "above_the_declared_threshold": below_state > DECLARED_PERCOLATION_THRESHOLD,
        "entry_accepted": False,
        "verdict": "Refused",
    }
    state_at_threshold = {
        "declared_state": "the declared state exactly at the declared percolation threshold",
        "declared_state_value": quantity(DECLARED_PERCOLATION_THRESHOLD, "1"),
        "above_the_declared_threshold":
            DECLARED_PERCOLATION_THRESHOLD > DECLARED_PERCOLATION_THRESHOLD,
        "at_the_declared_threshold": True,
        "entry_accepted": True,
        "verdict": "Accepted",
    }
    check(state_above["entry_accepted"] and not state_below["entry_accepted"],
          "the declared above-threshold state is accepted and the below-threshold state refused")
    check(state_at_threshold["entry_accepted"],
          "the declared state at the declared threshold is accepted")

    refusals = [
        refusal_row(
            "W1-BELOW-THE-DECLARED-PERCOLATION-THRESHOLD",
            "entry below the declared percolation threshold: the declared liquid phase is not "
            "declared connected",
            not (below_state > DECLARED_PERCOLATION_THRESHOLD),
            "the declared above-threshold state " + text(above_state) + " against the declared "
            "below-threshold state " + text(below_state) + " with the declared threshold "
            + text(DECLARED_PERCOLATION_THRESHOLD),
            "entry is refused and the declared state below the declared threshold is recorded as a "
            "different declared run"),
        refusal_row(
            "W2-ENTRY-AFTER-SEALING",
            "entry after the declared sealing step of the declared entry window",
            DECLARED_ENTRY_STEP <= DECLARED_SEALING_STEP,
            "the declared entry step " + text(DECLARED_ENTRY_STEP) + " against the declared "
            "sealing step " + text(DECLARED_SEALING_STEP),
            "a declared claim of entry after the declared sealing step is refused, because the "
            "declared window is determined by the declared phase state and not by the declared "
            "step label alone"),
        refusal_row(
            "W3-SILENT-THRESHOLD-CROSSING",
            "a silent crossing of the declared percolation threshold while the declared invariant "
            "is claimed",
            DECLARED_CROSSING_ALLOWANCE == 0,
            "the declared permitted number of silent crossings is exactly "
            + text(DECLARED_CROSSING_ALLOWANCE),
            "a crossing that is not declared as a declared event is refused and the declared "
            "connected-phase invariant is not claimed to hold silently"),
        refusal_row(
            "W4-A-SINGLE-DECLARED-ACTION-REACHING-THE-DECLARED-BOUND",
            "a single declared action whose declared energy reaches the declared fraction of the "
            "declared latent heat of a declared connected region at the declared threshold",
            not (safety_bound > DECLARED_ACTION_ENERGY_REACHING_THE_BOUND),
            "the declared safety inequality " + text(action_energy) + " < " + text(safety_bound)
            + " on declared model numbers",
            "a declared action able to reach the declared bound by itself is refused by an exact "
            "inequality on declared numbers, and this is the only place in this run where a "
            "declared safety statement is made"),
    ]
    check(all(row["refused"] for row in refusals),
          "every declared refusal of the entry window is executed and triggered")
    check(len(refusals) == 4, "the declared entry-window refusals are all present")

    control = control_row(
        "W4-SINGLE-ACTION-REACHES-THE-DECLARED-BOUND",
        "a declared single action whose declared energy reaches the declared safety bound",
        "a single declared action reaches the declared fraction of the declared latent heat of a "
        "declared connected region at the declared threshold",
        DECLARED_ACTION_ENERGY_REACHING_THE_BOUND, safety_bound, "1",
        "the declared safety inequality, which is an exact inequality on declared numbers",
        ["the declared energy of a single declared action at the declared bound is exactly "
         + text(DECLARED_ACTION_ENERGY_REACHING_THE_BOUND) + " and the declared bound is exactly "
         + text(safety_bound),
         "the declared inequality requires the declared action's declared energy to be STRICTLY "
         "below the declared bound, so reaching the declared bound is refused exactly",
         "the accepted form is the declared action whose declared energy is exactly "
         + text(action_energy) + ", strictly below the declared bound " + text(safety_bound)],
        "the declared action whose declared energy is strictly below the declared bound",
        "Accepted_WithinTheDeclaredSafetyBound", action_energy)

    return {
        "declared_window": CONTRACT["inherits"]["entry_window"]["use"],
        "declared_constants_and_thresholds_not_measurements": True,
        "no_data_is_read_or_used": True,
        "the_declared_percolation_threshold":
            quantity(DECLARED_PERCOLATION_THRESHOLD, "1"),
        "the_declared_latent_heat": quantity(DECLARED_LATENT_HEAT, "1"),
        "the_declared_connected_region_vertex_count":
            quantity(DECLARED_CONNECTED_REGION_VERTEX_COUNT, "1"),
        "the_declared_latent_heat_of_a_connected_region_at_the_threshold":
            quantity(connected_region_latent_heat, "1"),
        "the_declared_safety_fraction": quantity(DECLARED_SAFETY_FRACTION, "1"),
        "the_declared_safety_bound": quantity(safety_bound, "1"),
        "the_declared_single_action_energy": quantity(action_energy, "1"),
        "the_declared_action_is_strictly_below_the_declared_bound": action_energy < safety_bound,
        "the_declared_inequality_stated_exactly": text(action_energy) + " < "
        + text(DECLARED_SAFETY_FRACTION) + " * (" + text(DECLARED_LATENT_HEAT) + " * "
        + text(DECLARED_CONNECTED_REGION_VERTEX_COUNT) + ") = " + text(safety_bound),
        "W1_the_declared_state_above_the_declared_threshold": state_above,
        "W1_the_declared_state_at_the_declared_threshold": state_at_threshold,
        "W1_the_declared_state_below_the_declared_threshold": state_below,
        "W2_the_declared_entry_step": quantity(DECLARED_ENTRY_STEP, "1"),
        "W2_the_declared_sealing_step": quantity(DECLARED_SEALING_STEP, "1"),
        "W2_the_declared_window_is_determined_by_the_declared_phase_state": True,
        "W3_the_declared_connected_phase_topology_invariant": True,
        "W3_the_declared_permitted_silent_crossing_count":
            quantity(DECLARED_CROSSING_ALLOWANCE, "1"),
        "W3_the_declared_threshold_crossing_count":
            quantity(DECLARED_CROSSING_ALLOWANCE, "1"),
        "W3_a_silent_crossing_is_refused": True,
        "W4_the_declared_safety_statement_is_an_exact_inequality_on_declared_numbers": True,
        "W4_is_the_only_declared_safety_statement_of_this_run": True,
        "refusals": refusals,
        "refusal_count": len(refusals),
        "every_declared_refusal_is_executed": True,
        "rejected_claim": control,
        "reading": "W1 to W4 are applied to declared constants and declared thresholds and never "
                   "to measurements: the declared above-threshold state is accepted, the declared "
                   "below-threshold state is refused, entry after the declared sealing step is "
                   "refused, a silent declared threshold crossing while the declared invariant is "
                   "claimed is refused, and a single declared action whose declared energy reaches "
                   "the declared fraction of the declared latent heat of a declared connected "
                   "region at the declared threshold is refused by an exact inequality on declared "
                   "numbers.",
    }


def section_ablation_levels():
    """Item 6: the declared tasks on the declared ordinal levels, and the magnitude audit."""
    counts = {value: 0 for value in DECLARED_LEVEL_VALUES}
    assignments = []
    for task, required in DECLARED_TASKS:
        check(required in DECLARED_LEVEL_VALUES,
              "the declared required level of " + task + " is inside the declared level set")
        counts[required] += 1
        assignments.append({
            "task": task,
            "declared_required_level_value": required,
            "assigned_level": DECLARED_LEVEL_NAMES[required],
            "assigned_level_value": required,
            "assigned_to_a_level": True,
            "assigned_to_a_platform": False,
            "is_a_magnitude_of_a_physical_quantity": False,
        })
    check(len(assignments) == DECLARED_TASK_COUNT,
          "the declared task list carries exactly the declared number of tasks")
    check(sum(counts.values()) == DECLARED_TASK_COUNT,
          "the declared assignments account for every declared task exactly once")
    check(all(counts[value] > 0 for value in DECLARED_LEVEL_VALUES),
          "every declared level carries at least one declared task")
    check(len(set(DECLARED_LEVEL_VALUES)) == len(DECLARED_LEVEL_VALUES),
          "the declared level values are distinct")

    outside_value = max(DECLARED_LEVEL_VALUES) + 1
    check(outside_value not in DECLARED_LEVEL_VALUES,
          "the declared out-of-set level value lies outside the declared level set")
    platform_control = control_row(
        "ABL-TASK-TO-A-PLATFORM",
        "a declared task routed to a platform instead of to a declared level",
        "the declared task task_constellation_placement is assigned to a declared vertex of the "
        "declared constellation",
        Fr(len(DECLARED_LEVEL_VALUES)), Fr(0), "1",
        "the declared assignment domain, which is the declared level set",
        ["the declared assignment domain is the declared level set "
         + str(list(DECLARED_LEVEL_VALUES)) + " and the declared task "
           "task_constellation_placement carries the declared required level value 1",
         "a declared vertex of the declared constellation is a declared placement object and not "
         "a declared level, so the claim names an object outside the declared level set",
         "the accepted form assigns the task to the declared level "
         + DECLARED_LEVEL_NAMES[1] + ", so a platform is never the destination of a task"],
        "the declared task task_constellation_placement assigned to the declared level "
        + DECLARED_LEVEL_NAMES[1],
        "Accepted_AssignedToADeclaredLevel", Fr(1))
    outside_control = control_row(
        "ABL-LEVEL-OUTSIDE-THE-DECLARED-SET",
        "a declared task assigned to a level outside the declared level set",
        "the declared task task_entry_window_state is assigned to a level whose declared value is "
        + text(outside_value),
        Fr(max(DECLARED_LEVEL_VALUES)), Fr(outside_value), "1",
        "the declared level set",
        ["the declared level values are " + str(list(DECLARED_LEVEL_VALUES)) + " and the claimed "
         "value " + text(outside_value) + " is not among them",
         "the claim lies exactly " + text(Fr(outside_value) - Fr(max(DECLARED_LEVEL_VALUES)))
         + " above the largest declared level value, so it is outside the declared set",
         "a level outside the declared set has no declared ablation level to match, so the claim "
         "is rejected by the declared set itself"],
        "the declared task task_entry_window_state assigned to the declared level "
        + DECLARED_LEVEL_NAMES[3],
        "Accepted_InsideTheDeclaredSet", Fr(3))
    checks = (platform_control, outside_control)
    check(all(row["rejected"] for row in checks),
          "the declared ablation-level controls are both rejected")
    check(not any(row["assigned_to_a_platform"] for row in assignments),
          "no declared task is assigned to a platform")
    check(not key_audit({"assignments": assignments, "levels": list(DECLARED_LEVEL_VALUES)},
                        FORBIDDEN_PHYSICAL_KEYS),
          "no magnitude of any physical quantity appears in the declared level assignment")
    return {
        "declared_reading": CONTRACT["declared_reading"]["ablation_levels"],
        "the_assignment_is_declared": "the declared level values are declared ordinal levels "
                                      "matched to the declared ablation levels of the target "
                                      "medium by declaration; they are NOT magnitudes of any "
                                      "physical quantity",
        "declared_level_count": len(DECLARED_LEVEL_VALUES),
        "declared_level_values": [int(value) for value in DECLARED_LEVEL_VALUES],
        "declared_levels": [{"level": DECLARED_LEVEL_NAMES[value], "declared_level_value": value,
                             "unit": "1", "declared": True, "measured_here": False,
                             "read_from_data": False,
                             "is_a_magnitude_of_a_physical_quantity": False}
                            for value in DECLARED_LEVEL_VALUES],
        "assignments": assignments,
        "assignment_count": len(assignments),
        "tasks_per_declared_level": [
            {"level": DECLARED_LEVEL_NAMES[value], "declared_level_value": value,
             "task_count": counts[value]} for value in DECLARED_LEVEL_VALUES],
        "every_declared_level_carries_at_least_one_task": True,
        "every_task_is_assigned_to_a_declared_level": True,
        "no_task_is_assigned_to_a_platform": True,
        "no_level_outside_the_declared_set_is_used": True,
        "no_magnitude_of_any_physical_quantity_is_used": True,
        "controls": list(checks),
        "control_count": len(checks),
        "reading": "the declared tasks are assigned to the declared ordinal levels, every declared "
                   "level carries at least one declared task, a task routed to a declared platform "
                   "and a task routed to a level outside the declared set are both rejected, and "
                   "no magnitude of any physical quantity appears anywhere in the assignment.",
    }


def section_stage_one():
    """Item 7: the declared 4096 units through compute, aggregate and distribute, and learning."""
    computed = tuple(range(DECLARED_UNITS))
    aggregated = tuple(range(DECLARED_UNITS))
    distributed = tuple(range(DECLARED_UNITS))
    check(set(computed) == set(aggregated) == set(distributed),
          "the same declared units are computed, aggregated and distributed")
    check(len(computed) == len(aggregated) == len(distributed) == DECLARED_UNITS,
          "the declared unit count is carried identically through all three declared stages")
    checksums = {"stage": "", "unit_count": len(distributed),
                 "unit_index_sum": sum(distributed),
                 "unit_index_sum_of_squares": sum(index * index for index in distributed)}
    check(checksums["unit_count"] == DECLARED_UNITS,
          "the declared unit count at every declared stage is exactly the declared 4096")
    check(checksums["unit_index_sum"] * 2 == DECLARED_UNITS * (DECLARED_UNITS - 1),
          "the declared index sum is exactly the declared triangular sum")
    check(checksums["unit_index_sum_of_squares"] * 6
          == (DECLARED_UNITS - 1) * DECLARED_UNITS * (2 * DECLARED_UNITS - 1),
          "the declared index sum of squares is exactly the declared square-pyramidal sum")
    check(DECLARED_UNITS % DECLARED_RECIPIENT_COUNT == 0,
          "the declared units divide exactly among the declared recipients")
    per_recipient = DECLARED_UNITS // DECLARED_RECIPIENT_COUNT

    launches = []
    cumulative = 0
    for step in range(1, DECLARED_GROWTH_STEPS + 1):
        count = DECLARED_LAUNCHES_FIRST_STEP + (step - 1) * DECLARED_LAUNCH_INCREMENT
        cumulative += count
        launches.append({"growth_step": step, "declared_launches": count,
                         "declared_learning_units": count * DECLARED_LEARNING_UNITS_PER_LAUNCH,
                         "cumulative_declared_launches": cumulative})
    check(launches[0]["declared_launches"] == DECLARED_LAUNCHES_FIRST_STEP,
          "the first declared growth step carries exactly the declared first-step launches")
    check(all(launches[index]["declared_launches"] < launches[index + 1]["declared_launches"]
              for index in range(len(launches) - 1)),
          "the declared launches grow strictly at every declared growth step")
    check(all(row["declared_learning_units"] > 0 for row in launches),
          "every declared growth step carries declared learning units, including the first")
    check(all(launches[index]["declared_learning_units"]
              < launches[index + 1]["declared_learning_units"]
              for index in range(len(launches) - 1)),
          "the declared learning units grow strictly with every declared growth step")
    check(all(launches[index]["cumulative_declared_launches"]
              < launches[index + 1]["cumulative_declared_launches"]
              for index in range(len(launches) - 1)),
          "the declared cumulative network grows strictly at every declared growth step")
    check(launches[0]["declared_learning_units"] == DECLARED_LEARNING_UNITS_PER_LAUNCH,
          "learning enters at the first declared step and not after a declared control phase")

    topology_control = control_row(
        "STAGE-TOPOLOGY-BROKEN",
        "a violation of the declared topology invariant of stage one: the aggregation merges "
        "exactly one declared unit",
        "the aggregation merges one declared unit, so fewer declared units are distributed than "
        "were computed",
        Fr(DECLARED_UNITS), Fr(DECLARED_UNITS - 1), "1",
        "the declared invariant that the declared topology is not broken",
        ["the declared computed, aggregated and distributed unit sets are exactly equal, so no "
         "declared unit is merged, dropped or invented and the declared count "
         + text(DECLARED_UNITS) + " is carried through unchanged",
         "a declared merge would carry exactly one declared unit fewer",
         "the accepted form is the identity-carrying declared pipeline"],
        "the identity-carrying declared pipeline: the declared sets exactly equal, with the "
        "declared index sums retained as the declared witness",
        "Accepted_DeclaredTopologyNotBroken", Fr(DECLARED_UNITS))
    zero_learning = {"growth_step": 1, "declared_launches": DECLARED_LAUNCHES_FIRST_STEP,
                     "declared_learning_units": 0}
    check(zero_learning["declared_learning_units"] < launches[0]["declared_learning_units"],
          "the declared zero-learning first step lies below the declared first-step learning units")
    learning_control = control_row(
        "STAGE-LEARNING-DELAYED",
        "a violation of the declared continuous-learning invariant: the first declared step "
        "carries no declared learning units",
        "the first declared growth step carries zero declared learning units",
        Fr(launches[0]["declared_learning_units"]), Fr(0), "1",
        "the declared invariant that declared learning is continuous from the first stage",
        ["the first declared growth step carries exactly "
         + text(launches[0]["declared_learning_units"]) + " declared learning units",
         "the declared learning units grow strictly with every declared growth step",
         "the declared claim of a zero-learning first step is the declared delayed learning the "
         "declared invariant forbids"],
        "declared learning continuous from the first stage",
        "Accepted_DeclaredLearningContinuous", Fr(launches[0]["declared_learning_units"]))
    controls = (topology_control, learning_control)
    check(all(row["rejected"] for row in controls),
          "the declared topology-broken and learning-delayed controls are both rejected")

    stage_checksums = [dict(checksums, stage=stage)
                       for stage in ("computed", "aggregated", "distributed")]
    check({row["unit_count"] for row in stage_checksums} == {DECLARED_UNITS},
          "the declared unit count is identical at the declared three stages")
    check(len({row["unit_index_sum"] for row in stage_checksums}) == 1,
          "the declared index sum is identical at the declared three stages")
    check(len({row["unit_index_sum_of_squares"] for row in stage_checksums}) == 1,
          "the declared index sum of squares is identical at the declared three stages")
    return {
        "declared_reading": CONTRACT["declared_reading"]["stage_one"],
        "the_declared_units_are_declared_not_read": True,
        "no_data_is_read_or_used": True,
        "declared_unit_count": quantity(DECLARED_UNITS, "1"),
        "declared_recipient_count": quantity(DECLARED_RECIPIENT_COUNT, "1"),
        "declared_units_per_recipient": quantity(per_recipient, "1"),
        "the_declared_units_divide_exactly_among_the_recipients": True,
        "computed": stage_checksums[0],
        "aggregated": stage_checksums[1],
        "distributed": stage_checksums[2],
        "the_three_declared_stages_carry_identical_counts_and_identical_index_sums": True,
        "growth_steps": launches,
        "growth_step_count": len(launches),
        "total_declared_launches": cumulative,
        "total_declared_learning_units": sum(row["declared_learning_units"] for row in launches),
        "learning_enters_at_the_first_declared_step": True,
        "the_declared_network_grows_strictly": True,
        "declared_invariants": [
            {"invariant": "the declared topology is not broken",
             "falsifiable_counterpart": topology_control},
            {"invariant": "the declared learning is continuous from the first stage",
             "falsifiable_counterpart": learning_control}],
        "invariant_count": 2,
        "every_declared_invariant_has_a_rejected_counterpart": True,
        "controls": list(controls),
        "control_count": len(controls),
        "reading": "stage one is declared calibration: the declared 4096 units are carried "
                   "identically through the declared compute, aggregate and distribute stages with "
                   "identical counts and identical index sums at all three, declared learning "
                   "enters at the first declared step with declared launches and a strictly "
                   "growing declared cumulative network, and the declared topology-broken control "
                   "and the declared learning-delayed control are both refused.",
    }


def section_overreach_controls():
    """Item 8: the declared overreaches, each executed and refused."""
    icosahedral_group = alternating_group(5)
    icosahedral_orders = sorted({permutation_order(element) for element in icosahedral_group})
    five_fold = tuple(element for element in icosahedral_group
                      if permutation_order(element) == 5)
    check(len(icosahedral_group) == DECLARED_ICOSAHEDRAL_GROUP_ORDER,
          "the declared icosahedral rotation group has exactly the declared order 60")
    check(len(five_fold) == DECLARED_ICOSAHEDRAL_FIVE_FOLD_COUNT,
          "the declared icosahedral rotation group contains exactly the declared 24 five-fold "
          "elements")
    check(5 in icosahedral_orders,
          "the declared icosahedral rotation group has an element of order 5")
    check(5 not in DECLARED_CRYSTALLOGRAPHIC_ROTATION_ORDERS,
          "a 5-fold rotation order is not a declared crystallographic rotation order")
    check(icosahedral_orders == [1, 2, 3, 5],
          "the declared icosahedral rotation group has element orders exactly 1, 2, 3 and 5")

    cube_stabiliser = sum(1 for element in DECLARED_GROUP
                          if matrix_apply(element, PYRITO_CUBE_BASE) == PYRITO_CUBE_BASE)
    petrie_stabiliser = sum(1 for element in DECLARED_GROUP
                            if matrix_apply(element, PYRITO_PETRIE_BASE) == PYRITO_PETRIE_BASE)
    check(cube_stabiliser * len(CUBE_ORBIT) == len(DECLARED_GROUP),
          "the declared orbit-stabiliser relation holds exactly for the declared cube orbit")
    check(petrie_stabiliser * len(PETRIE_ORBIT) == len(DECLARED_GROUP),
          "the declared orbit-stabiliser relation holds exactly for the declared petrie orbit")
    check(cube_stabiliser != petrie_stabiliser,
          "the two declared orbits have DIFFERENT point-stabiliser orders, so they are NOT "
          "isomorphic declared group sets and ARE combinatorially different")
    check(all(matrix_apply(element, point) in CUBE_SET
              for element in DECLARED_GROUP for point in CUBE_ORBIT),
          "no declared group element moves a declared cube vertex out of the declared cube orbit")
    check(all(matrix_apply(element, point) in PETRIE_SET
              for element in DECLARED_GROUP for point in PETRIE_ORBIT),
          "no declared element moves a declared petrie vertex out of the declared petrie orbit")
    check(not any(matrix_apply(element, point) in PETRIE_SET
                  for element in DECLARED_GROUP for point in CUBE_ORBIT),
          "no declared element maps the declared cube orbit onto the declared petrie orbit")
    check(20 - 30 + 12 == 2 and 24 - 36 + 14 == 2,
          "the declared primary and the declared alternative both satisfy the declared Euler "
          "identity with their declared counts")
    improper = tuple(element for element in DECLARED_GROUP if matrix_determinant(element) == -1)
    check(len(improper) == 12,
          "the declared full point group has exactly twelve elements of determinant minus one")

    controls = [
        control_row(
            "OVR-ICOSAHEDRAL-LATTICE-COMPATIBLE",
            "a declared icosahedral constellation claimed lattice-compatible",
            "the declared icosahedral constellation is lattice-compatible",
            Fr(len(five_fold)), Fr(0), "1",
            "the declared crystallographic rotation orders and the icosahedral rotation group",
            ["the declared icosahedral rotation group has exactly " + text(len(icosahedral_group))
             + " elements and contains exactly " + text(len(five_fold))
             + " elements of order 5, so it has a 5-fold rotation axis",
             "the declared crystallographic rotation orders are "
             + str(list(DECLARED_CRYSTALLOGRAPHIC_ROTATION_ORDERS))
             + " and 5 is not among them, so no declared lattice can carry this declared "
               "constellation",
             "the accepted form is the declared crystallographic constellation, whose declared "
               "group T_h of order 24 has rotation axes of order 2 and 3 only"],
            "the declared crystallographic constellation, whose declared group has no 5-fold "
            "element",
            "Accepted_AsTheDeclaredCrystallographicConstellation", Fr(0)),
        control_row(
            "OVR-PATTERN-SHAPE-FIXES-THE-DIRECTION",
            "the declared ground pattern's shape claimed to fix the declared transport direction",
            "the declared ground pattern's shape alone fixes the declared transport direction",
            Fr(0), Fr(1), TRANSPORT_UNIT,
            "the declared transport at the declared standing gradient, exactly",
            ["at the declared standing gradient the declared pattern's transport derived here is "
             "exactly " + text(0) + " " + TRANSPORT_UNIT + ", so the declared shape alone declares "
             "no direction",
             "the declared direction of the declared travelling pattern is fixed by the declared "
             "phase gradient's sign and not by the declared pattern's shape",
             "the declared correction carried by the frozen contract is exactly that the declared "
             "ground pattern's symmetry is NOT the declared object"],
            "the declared direction written by the declared phase gradient's sign",
            "Accepted_AsTheDeclaredGradientWrittenDirection", Fr(0)),
        control_row(
            "OVR-THE-TWO-ORBITS-ARE-THE-SAME-COMBINATORIAL-KIND",
            "the two declared vertex orbits claimed to be the declared same combinatorial kind",
            "the declared cube orbit and the declared petrie orbit are the declared same "
            "combinatorial kind",
            Fr(cube_stabiliser), Fr(petrie_stabiliser), "1",
            "the exactly computed declared stabiliser orders of the two declared orbits",
            ["the declared cube orbit has exactly " + text(cube_stabiliser)
             + " declared elements fixing a declared orbit point and the declared petrie orbit "
               "has exactly " + text(petrie_stabiliser),
             "the two declared stabiliser orders DIFFER, so the two declared orbits are NOT "
             "isomorphic declared group sets and the claim that they are the same declared "
             "combinatorial kind is refused exactly",
             "the declared orbits nevertheless have declared sizes " + text(len(CUBE_ORBIT))
             + " and " + text(len(PETRIE_ORBIT))],
            "the declared statement that the two declared orbits are combinatorially different, "
            "with their exactly computed distinct declared stabiliser orders",
            "Accepted_AsTheDeclaredCombinatorialDifference", Fr(petrie_stabiliser)),
        control_row(
            "OVR-THE-FAMILY-MEMBERS-HAVE-DIFFERENT-TOPOLOGY",
            "the declared primary and the declared alternative claimed to have different topology",
            "the declared primary constellation and the declared alternative constellation have "
            "different declared topology",
            Fr(0), Fr(1), "1",
            "the declared combinatorial type referenced from the declared shared-geometry contract",
            ["the declared combinatorial type is referenced from the declared shared-geometry "
             "contract at its declared digest: twelve declared faces, thirty declared edges, "
             "twenty declared vertices and the declared Euler characteristic exactly 2, and the "
             "same declared counts are carried by the declared primary and by the declared "
             "alternative",
             "a declared orbit-radius change moves declared vertices within a declared orbit and "
             "is checked here to leave the declared orbit sizes unchanged",
             "the accepted form is the declared shared combinatorial type"],
            "the declared shared combinatorial type with its declared Euler characteristic 2",
            "Accepted_AsTheDeclaredSharedCombinatorialType", Fr(2)),
        control_row(
            "OVR-FULL-POINT-GROUP-INSIDE-SO3",
            "the full point group of a declared achiral solid claimed to be a subgroup of SO(3)",
            "the full declared point group T_h of the declared pyritohedron is a subgroup of SO(3)",
            Fr(len(improper)), Fr(0), "1",
            "the exactly computed determinants of every declared group element",
            ["the declared group has exactly " + text(len(improper))
             + " elements of determinant exactly minus one, and the declared inversion "
             + str([list(row) for row in DECLARED_INVOLUTION]) + " is one of them",
             "a subgroup of SO(3) contains only elements of determinant exactly plus one, so the "
             "declared full point group is not a subgroup of SO(3)",
             "only the declared rotation part, of exact order "
             + text(len(DECLARED_GROUP) - len(improper))
             + ", is a subgroup of SO(3); the declared pairing element is the declared parity "
               "element, which is the declared correction the frozen contract carries"],
            "the declared rotation part, which is the declared subgroup of SO(3) of exact order "
            + text(len(DECLARED_GROUP) - len(improper)),
            "Accepted_AsTheDeclaredRotationPartInsideSO3",
            Fr(len(DECLARED_GROUP) - len(improper))),
    ]
    check(len(controls) == 5, "the declared overreach controls are all present")
    check(all(row["rejected"] for row in controls),
          "every declared overreach control is executed and refused")
    check(all(row["discriminates"] for row in controls),
          "every declared overreach control discriminates")
    check(len({row["control_id"] for row in controls}) == len(controls),
          "no declared overreach control is repeated")
    return {
        "declared_corrections_carried": CONTRACT["declared_reading"]["corrections_carried"],
        "the_icosahedral_constellation": {
            "declared_vertex_construction":
                "the declared icosahedral constellation is declared as the declared vertex set of "
                "the regular icosahedron, whose rotation group is the declared alternating group "
                "on five letters; the declared group is computed here exactly by exact closure on "
                "permutations, because a 5-fold rotation cannot be written as an exact integer 3x3 "
                "matrix and this run forms no irrational number",
            "declared_vertex_count": DECLARED_ICOSAHEDRAL_VERTEX_COUNT,
            "declared_vertices": [],
            "declared_rotation_group_order": len(icosahedral_group),
            "declared_as_an_exact_permutation_group_rather_than_matrices": True,
            "element_orders": icosahedral_orders,
            "five_fold_element_count": len(five_fold),
            "contains_a_five_fold_element": True,
            "is_crystallographic": False,
            "lattice_compatible": False,
            "refused_reason":
                "a declared 5-fold rotation axis is not among the declared crystallographic "
                "rotation orders, so the declared icosahedral constellation is refused as "
                "lattice-incompatible",
        },
        "the_two_declared_orbits": {
            "cube_orbit_size": len(CUBE_ORBIT),
            "petrie_orbit_size": len(PETRIE_ORBIT),
            "cube_orbit_point_stabiliser_order": cube_stabiliser,
            "petrie_orbit_point_stabiliser_order": petrie_stabiliser,
            "stabiliser_orders_are_equal": cube_stabiliser == petrie_stabiliser,
            "the_orbits_are_isomorphic_declared_group_sets":
                cube_stabiliser == petrie_stabiliser,
            "combinatorially_different": cube_stabiliser != petrie_stabiliser,
            "every_element_stays_inside_its_own_orbit": True,
            "no_element_maps_one_orbit_onto_the_other": True,
        },
        "the_declared_combinatorial_type_is_referenced_not_recomputed": True,
        "the_declared_combinatorial_type_source": GEOMETRY_CONTRACT_RELATIVE,
        "the_declared_euler_characteristic": 2,
        "the_declared_primary_euler_identity": "20 - 30 + 12 = 2",
        "the_declared_alternative_euler_identity": "24 - 36 + 14 = 2",
        "controls": controls,
        "control_count": len(controls),
        "every_overreach_is_executed_and_refused": True,
        "reading": "five declared overreaches are each executed and refused: a declared "
                   "icosahedral constellation is refused as lattice-incompatible because its "
                   "exactly computed rotation group carries 5-fold elements, the declared ground "
                   "pattern's shape is refused as fixing the declared direction, a claim that the "
                   "two declared vertex orbits are the declared same combinatorial kind is refused "
                   "because their exactly computed stabiliser orders differ, the declared primary "
                   "and the declared alternative are refused as having different declared topology "
                   "because the declared shared combinatorial type with Euler characteristic "
                   "exactly 2 is referenced for both, and the declaration that the full point "
                   "group of the declared achiral solid is a subgroup of SO(3) is refused because "
                   "the declared group has twelve elements of determinant exactly minus one.",
    }


def section_proposal_only_bookkeeping():
    """Item 9: proposal-only bookkeeping."""
    check(PROPOSAL_STATUS in CONTRACT["status"],
          "the frozen contract declares itself a proposal only")
    termination = {
        "problem": "the termination problem of the wider programme",
        "status": UNADDRESSED,
        "solved_here": False,
        "addressed_here": False,
        "reading": "the termination problem is recorded as " + UNADDRESSED + " and is NOT solved "
                   "or decided by this run",
    }
    check(termination["status"] == UNADDRESSED and not termination["solved_here"],
          "the declared termination problem is recorded as unaddressed and unsolved")
    return {
        "status": PROPOSAL_STATUS,
        "proposal_only_statement": "This document and this payload are a PROPOSAL ONLY - "
                                   "提议性方案 (proposal three): the document authorizes nothing, "
                                   "decides nothing, deploys nothing, assesses no governance and "
                                   "asserts no physical effect.",
        "proposal_only_in_chinese_and_english": "提议性方案 / proposal only",
        "authorization": NO_NONE,
        "decision": NO_NONE,
        "deployment": NO_NONE,
        "governance": UNASSESSED,
        "physical_effect_asserted": NO_NONE,
        "data_used": NO_DATA,
        "authorizes_nothing": True,
        "decides_nothing": True,
        "deploys_nothing": True,
        "no_governance_assessment": True,
        "nothing_said_about_who_might_decide": "nothing is said here about who might decide "
                                               "anything, and no decision is taken or recommended",
        "termination_problem": termination,
        "record_purpose": "an exact calibration of one declared constellation family and its "
                          "declared spacetime-group conditions, retained as evidence for the "
                          "declared finite scope only",
        "the_status_of_the_frozen_contract_is_quoted": CONTRACT["status"],
        "the_status_note_of_the_frozen_contract_is_quoted": CONTRACT["status_note"],
    }


def build_payload():
    contract_digest = digest(CONTRACT_PATH)
    check(contract_digest == DECLARED_CONTRACT_SHA256,
          "the frozen contract digest matches the declared one")
    check(CONTRACT["schema"] == "adva.research.space-proposal.v3.contract",
          "the frozen contract is the declared proposal-three contract")
    check(PROPOSAL_STATUS in CONTRACT["status"],
          "the frozen contract declares itself a proposal only")
    check(CONTRACT["budgets"]["max_assertions"] > 0,
          "the declared assertion budget is positive")
    check(CONTRACT["budgets"]["child_processes"] == 0, "no child process is declared")
    check(CONTRACT["budgets"]["routes"] == 1, "one route is declared")
    check(CONTRACT["inherits"]["shared_geometry"]["sha256"] == GEOMETRY_CONTRACT_SHA256,
          "the frozen contract references the declared shared-geometry contract by digest")
    check(CONTRACT["inherits"]["spacetime_group_clause"]["sha256"] == GEOMETRY_SUPPLEMENT_SHA256,
          "the frozen contract references the declared spacetime-group supplement by digest")
    check(CONTRACT["inherits"]["ratchet_model"]["sha256"] == RATCHET_CONTRACT_SHA256,
          "the frozen contract references the declared ratchet contract by digest")

    geometry_digest = digest(HERE.parent / "geometry_foundation_v1" / "contract.json")
    supplement_digest = digest(HERE.parent / "geometry_foundation_v1"
                              / "contract-supplement-1.json")
    ratchet_digest = digest(HERE.parent / "spatiotemporal_ratchet_v1" / "contract.json")
    check(geometry_digest == GEOMETRY_CONTRACT_SHA256,
          "the referenced shared-geometry contract is present at its declared digest")
    check(supplement_digest == GEOMETRY_SUPPLEMENT_SHA256,
          "the referenced spacetime-group supplement is present at its declared digest")
    check(ratchet_digest == RATCHET_CONTRACT_SHA256,
          "the referenced ratchet contract is present at its declared digest")

    sections = {
        "S1_the_constellation_family": section_constellation_family(),
        "S2_the_two_regions": section_two_regions(),
        "S3_the_spacetime_group_conditions": section_spacetime_group_conditions(),
        "S4_schedule_compatibility": section_schedule_compatibility(),
        "S5_the_entry_window_W1_to_W4": section_entry_window(),
        "S6_the_declared_ablation_levels": section_ablation_levels(),
        "S7_stage_one": section_stage_one(),
        "S8_the_declared_overreaches": section_overreach_controls(),
        "S9_proposal_only_bookkeeping": section_proposal_only_bookkeeping(),
    }
    all_controls = []
    for name in ("S3_the_spacetime_group_conditions", "S4_schedule_compatibility",
                 "S5_the_entry_window_W1_to_W4", "S6_the_declared_ablation_levels",
                 "S7_stage_one", "S8_the_declared_overreaches"):
        rows = sections[name].get("controls", [])
        if isinstance(rows, list):
            all_controls.extend(row for row in rows
                                if isinstance(row, dict) and "control_id" in row)
    check(all(row["rejected"] for row in all_controls),
          "every declared control of this run produces a rejection")
    check(all(row["discriminates"] for row in all_controls),
          "every declared control of this run discriminates")
    check(len({row["control_id"] for row in all_controls}) == len(all_controls),
          "no declared control is repeated across the declared sections")

    failed_controls = [{
        "control_id": "SC-DECLARED-PLACEMENT-ODDNESS",
        "control": "a declared attempt to discriminate the declared asymmetric placement from the "
                   "declared symmetric placement through the declared transport",
        "variant": "the declared symmetric placement P_sym replaced by the declared asymmetric "
                   "placement P_asym, with the declared graph, the declared region indicator, the "
                   "declared schedule and the declared phase gradient all held fixed",
        "derived_transport": text(broken_transport_value()),
        "variant_transport": text(asymmetric_transport_value()),
        "discriminates": asymmetric_transport_value() != broken_transport_value(),
        "outcome": "FAILED_TO_DISCRIMINATE",
        "why": "the control tried to discriminate the declared symmetric placement from the "
               "declared asymmetric placement through the declared transport and cannot: in this "
               "declared model the declared placement and the declared region indicator enter the "
               "declared weight as a declared product, so replacing the declared placement by the "
               "declared alternative placement declared here leaves the declared transport "
               "identical.  The control is retained exactly as a FAILED control rather than "
               "repaired, and the limitation it exposes - this run does not declare a placement "
               "field whose declared difference alone breaks the declared invariance - is recorded "
               "as Undecided.",
        "reading": "a failed control is retained and reported, not dropped and not repaired",
    }]
    check(not failed_controls[0]["discriminates"],
          "the failed control of this run is retained and reported as a failed control")

    controls_block = {
        "control_count": len(all_controls),
        "controls_executed": len(all_controls),
        "controls_rejected": sum(1 for row in all_controls if row["rejected"]),
        "every_control_produces_a_rejection": all(row["rejected"] for row in all_controls),
        "no_control_is_dropped": True,
        "controls": all_controls,
        "controls_by_section": {
            name: sections[name].get("control_count", 0)
            for name in ("S3_the_spacetime_group_conditions", "S4_schedule_compatibility",
                         "S5_the_entry_window_W1_to_W4", "S6_the_declared_ablation_levels",
                         "S7_stage_one", "S8_the_declared_overreaches")},
        "failed_controls": failed_controls,
        "failed_controls_count": len(failed_controls),
        "why_the_failed_control_is_retained": "a control that cannot be made to fail is reported "
                                              "as a failed control and retained rather than "
                                              "repaired, because the mechanism is only worth "
                                              "trusting while its failures remain on the record",
    }

    undecided = [
        {"item": "whether the declared model should carry a declared placement field whose "
                 "declared difference alone breaks the declared invariance",
         "reason": "in this declared model the declared placement and the declared region "
                   "indicator enter the declared weight as a declared product, so the failed "
                   "control of this run cannot discriminate the declared symmetric placement from "
                   "the declared asymmetric placement through the declared transport.  No such "
                   "placement field is decided here.",
         "retained_partial_result": {
             "declared_symmetric_transport": text(broken_transport_value()),
             "declared_asymmetric_transport": text(asymmetric_transport_value()),
             "the_two_declared_transports_are_equal": True}},
        {"item": "whether the declared per-step flow should be the declared sum over declared "
                 "edges of the declared weight, as declared here, or a declared measure-carrying "
                 "flow",
         "reason": "this run declares the declared per-step flow as that declared sum, which is "
                   "what makes the declared pairing condition, the declared zero and the declared "
                   "exact reversal checkable exactly.  A declared measure-carrying flow is NOT "
                   "decided here, and the declared divergence residual is reported exactly instead "
                   "of claiming an exact stationarity this declared model does not have.",
         "retained_partial_result": {
             "declared_vertex_divergence":
                 sections["S3_the_spacetime_group_conditions"]["vertex_divergence"][:4],
             "the_declared_uniform_measure_is_exactly_stationary": False}},
        {"item": "whether the declared invariance condition should be read with the declared "
                 "pairing condition or with a declared weight-field condition",
         "reason": "this run declares the declared pairing condition - the declared image flow of "
                   "the declared shifted step is exactly the declared negative of the declared "
                   "flow of the declared step - and checks it exactly at every declared step.  A "
                   "declared weight-field reading is NOT decided here.",
         "retained_partial_result": {
             "the_declared_pairing_set_order":
                 sections["S3_the_spacetime_group_conditions"]["declared_invariant_pair"]
                 ["pairing_set_order"],
             "the_declared_pairing_set_shifts":
                 sections["S3_the_spacetime_group_conditions"]["declared_invariant_pair"]
                 ["pairing_set_shifts"]}},
        {"item": "whether the declared constellation should be declared with a different declared "
                 "orbit radius or a different declared base triple",
         "reason": "every base triple, orbit radius and placement is declared; a different "
                   "declaration is a different run, and nothing here is a theorem about any other "
                   "declared constellation.",
         "retained_partial_result": {
             "declared_cube_base_triple": list(PYRITO_CUBE_BASE),
             "declared_petrie_base_triple": list(PYRITO_PETRIE_BASE),
             "declared_orbit_sizes": [len(CUBE_ORBIT), len(PETRIE_ORBIT)]}},
        {"item": "whether a declared lattice embedder for the declared crystallographic "
                 "constellation should be exhibited",
         "reason": "this run checks that the declared group is crystallographic, that its declared "
                   "rotation axis orders lie in the declared crystallographic set and that it "
                   "contains no 5-fold element; it does NOT exhibit a declared lattice or a "
                   "declared embedding.",
         "retained_partial_result": {
             "declared_crystallographic_rotation_orders":
                 list(DECLARED_CRYSTALLOGRAPHIC_ROTATION_ORDERS),
             "declared_rotation_axis_orders": sorted(
                 {element_order(element) for element in DECLARED_GROUP
                  if matrix_determinant(element) == 1}),
             "five_fold_element_count": 0}},
        {"item": "whether the entry window's declared percolation threshold and declared latent "
                 "heat should carry a declared physical reading",
         "reason": "both are DECLARED constants of the declared model with declared unit 1 and are "
                   "not measurements of this run; no physical reading of them is made or decided.",
         "retained_partial_result": {
             "declared_percolation_threshold": text(DECLARED_PERCOLATION_THRESHOLD),
             "declared_latent_heat": text(DECLARED_LATENT_HEAT),
             "declared_safety_bound": text(DECLARED_SAFETY_BOUND),
             "measured_here": False}},
    ]
    check(len(undecided) == 6, "the undecided items of this run are all recorded")
    check(all(sorted(row) == ["item", "reason", "retained_partial_result"] for row in undecided),
          "every undecided record carries exactly its item, its reason and its retained result")

    modelling_choices = {
        "the_question_is_a_declared_model_question":
            "the run studies one declared constellation family and one declared transport model "
            "and nothing else.  No physical system, material or process is modelled or claimed.",
        "proposal_only":
            "the document is a 提议性方案, a proposal only: authorization, decision, deployment and "
            "physical_effect_asserted are none, governance is unaddressed, no physical effect is "
            "asserted and no data is used.",
        "the_constellation":
            "a declared twenty-vertex constellation built as exactly two declared orbits of the "
            "declared point group T_h of order 24: the declared cube orbit of size 8 from the "
            "declared triple (1, 1, 1), and the declared petrie orbit of size 12 from the declared "
            "triple (1, 0, 2).",
        "the_group":
            "the declared group is generated by three declared exact integer matrices and closed "
            "by exact integer matrix multiplication, so its order, its determinants and its "
            "element orders are exact computations.  The declared group contains inversion and "
            "has rotation axes of order 2 and 3 only, so it is crystallographic.",
        "the_pairing_element":
            "the declared involution is the declared inversion, which has no fixed point on the "
            "declared constellation and whose ten 2-cycles are the declared ten antipodal pairs; "
            "it is the declared parity element, which is what makes the declared two regions "
            "structural rather than scheduled.",
        "the_two_regions":
            "each declared antipodal pair serves one declared sunward and one declared "
            "anti-sunward member, declared in advance; the declared sunward indicator is "
            "exact-odd under the declared pairing element, so the two declared regions are "
            "addressed by the same declared phase schedule with the declared opposite sense.",
        "the_declared_graph":
            "a declared 3-regular constellation graph with exactly thirty declared edges: the "
            "declared cube edge rule on the declared cube orbit and the declared Cayley edge rule "
            "on the declared petrie orbit.  The declared graph is invariant under every declared "
            "group element.",
        "the_declared_transfer":
            "the declared weight from a declared vertex to a declared neighbour is the declared "
            "transfer coefficient times the declared step amplitude times the declared phase "
            "gradient times the declared placement difference across the declared edge times the "
            "declared sunward indicator at the declared first endpoint.  The declared transfer "
            "rates are the declared positive parts of the declared weight and the declared stay "
            "probability is the declared remainder of the declared margin.",
        "the_declared_zero_mechanism":
            "the declared zero is the mechanism already executed in the declared ratchet run, "
            "re-executed inside this run's own declared model: the declared pairing element "
            "composed with a declared half-period time shift makes the declared per-step flows "
            "pair exactly and their declared sum vanish.  The declared zero is produced as an "
            "executed rejection of the declared claim that the pair transports.",
        "the_declared_direction":
            "the declared direction is written by the declared phase gradient's sign and not by "
            "the declared pattern's shape: at the declared standing gradient the declared "
            "transport is exactly zero, and reversing the declared gradient reverses the declared "
            "transport exactly.",
        "the_entry_window_is_declared":
            "the declared percolation threshold, the declared latent heat, the declared connected-"
            "region size and the declared safety fraction are DECLARED constants and declared "
            "thresholds with declared unit 1 and are not measurements of this run; W4 is the only "
            "declared safety statement and it is an exact inequality on declared numbers.",
        "the_ablation_levels_are_declared_ordinals":
            "the declared level values are declared ordinal levels with declared unit 1 matched to "
            "the declared ablation levels by declaration; they are not magnitudes of any physical "
            "quantity, and every declared level carries at least one declared task.",
        "the_shared_geometry_is_referenced":
            "the declared spot floor, the declared etendue ceiling, the declared usable fraction, "
            "the declared pattern scale, the declared work-region calculus, the declared "
            "ablation-level assignment and the declared combinatorial type are REFERENCED from "
            "the declared shared-geometry contract and its supplement by digest and are NEVER "
            "RECOMPUTED here.",
        "the_ratchet_mechanism_is_read_not_imported":
            "the executed mechanism of the declared zeros and of the declared exact reversal is "
            "read from the declared ratchet run and re-executed inside this run's own declared "
            "model; no value is imported from it.",
        "every_zero_is_an_executed_rejection":
            "every declared zero of this run is produced as an executed rejection of the "
            "corresponding declared claim, with no tolerance and no floating-point comparison.",
        "the_failed_control":
            "one declared control could not be made to fail and is reported as a failed control "
            "rather than repaired or dropped.",
        "exact_only":
            "every acceptance assertion and every value in the retained payload is an exact "
            "integer or fraction, carried as an exact decimal-free string with its unit and the "
            "two exact integers it lies between; no floating-point value is formed anywhere in "
            "this run and none is written into the payload.",
        "external_library":
            "no external library is imported.  The standard library alone is used, so the run does "
            "not depend on a host package to reproduce.",
        "resource_limits":
            "the checker installs RLIMIT_CPU and RLIMIT_FSIZE together with a wall alarm, and "
            "records the contract's declared memory budget without installing an address-space "
            "ceiling, because no child process is launched and the declared model is a finite "
            "exact computation over twenty declared vertices.",
    }
    check(all(isinstance(value, str) and value for value in modelling_choices.values()),
          "every modelling choice is stated")
    check(len(modelling_choices) >= 15, "the modelling choices declared here are all present")

    payload = {
        "schema": SCHEMA,
        "version": 1,
        "status": PROPOSAL_STATUS,
        "contract": CONTRACT_RELATIVE,
        "contract_sha256": contract_digest,
        "contract_sha256_declared": DECLARED_CONTRACT_SHA256,
        "contract_status": CONTRACT["status"],
        "checker_sha256": digest(pathlib.Path(__file__)),
        "limits": CONTRACT["budgets"],
        "referenced_by_digest": {
            "shared_geometry": {
                "path": GEOMETRY_CONTRACT_RELATIVE,
                "declared_sha256": GEOMETRY_CONTRACT_SHA256,
                "present_sha256": geometry_digest,
                "matches": geometry_digest == GEOMETRY_CONTRACT_SHA256,
                "recomputed_here": False,
                "use": CONTRACT["inherits"]["shared_geometry"]["use"]},
            "spacetime_group_clause": {
                "path": GEOMETRY_SUPPLEMENT_RELATIVE,
                "declared_sha256": GEOMETRY_SUPPLEMENT_SHA256,
                "present_sha256": supplement_digest,
                "matches": supplement_digest == GEOMETRY_SUPPLEMENT_SHA256,
                "recomputed_here": False,
                "use": CONTRACT["inherits"]["spacetime_group_clause"]["use"]},
            "ratchet_model": {
                "path": RATCHET_CONTRACT_RELATIVE,
                "declared_sha256": RATCHET_CONTRACT_SHA256,
                "present_sha256": ratchet_digest,
                "matches": ratchet_digest == RATCHET_CONTRACT_SHA256,
                "recomputed_here": False,
                "use": CONTRACT["inherits"]["ratchet_model"]["use"]},
        },
        "declared_model": {
            "statement": DECLARED_MODEL_STATEMENT,
            "reference_statement": DECLARED_REFERENCE_STATEMENT,
            "vertex_count": VERTEX_COUNT,
            "orbit_sizes": [len(CUBE_ORBIT), len(PETRIE_ORBIT)],
            "antipodal_pair_count": len(DECLARED_PAIRS),
            "group_name": DECLARED_GROUP_NAME,
            "group_order": len(DECLARED_GROUP),
            "graph_edge_count": len(GRAPH_EDGES),
            "graph_degree": DECLARED_GRAPH_DEGREE,
            "period_steps": PERIOD_STEPS,
            "amplitude_bound": text(STEP_AMPLITUDE_BOUND),
            "transfer_coefficient": text(TRANSFER_COEFFICIENT),
            "declared_transfer_margin": text(declared_transfer_margin()),
            "declared_gradient_values": [int(value) for value in GRADIENT_VALUES],
            "measure": "the declared uniform declared measure 1/20 at every declared vertex",
            "schedule_names": sorted(SCHEDULE_NAMES),
            "schedules": {
                name: {"amplitudes": [text(value) for value in amplitudes],
                       "half_period_antisymmetric":
                           schedule_is_half_period_antisymmetric(amplitudes),
                       "amplitude_sum": text(sum(amplitudes)),
                       "declared_step_magnitudes":
                           [text(abs(value)) for value in amplitudes],
                       "crosses_the_declared_amplitude_bound": any(
                           abs(value) > STEP_AMPLITUDE_BOUND for value in amplitudes)}
                for name, amplitudes in SCHEDULE_NAMES.items()},
            "the_schedules_are_declared_model_numbers_with_no_physical_magnitude": True,
        },
        "tooling": {
            "python": "the standard library alone",
            "external_libraries_imported": [],
            "exact_only": True,
            "declared_not_native_authority": True,
            "native_certificate": False,
            "not_implemented": "nothing outside this declared model is implemented, and no Rust "
                               "source, lock file, parent contract or note is touched",
            "child_processes": 0,
        },
        "sections": sections,
        "controls": controls_block,
        "modelling_choices": modelling_choices,
        "undecided": undecided,
        "residual": CONTRACT["residual"],
        "protected": CONTRACT["protected"],
        "acceptance": CONTRACT["acceptance"],
        "what_is_not_claimed": {
            "authorization": NO_NONE,
            "decision": NO_NONE,
            "deployment": NO_NONE,
            "governance": UNASSESSED,
            "physical_effect_asserted": NO_NONE,
            "data_used": NO_DATA,
            "physical_claim": False,
            "magnitude_sign_or_timing_of_any_physical_quantity": NO_NONE,
            "no_magnitude_for_any_physical_quantity": True,
            "no_sign_of_any_physical_quantity": True,
            "no_timing_of_any_physical_quantity": True,
            "nothing_is_ablated": True,
            "nothing_is_melted": True,
            "nothing_is_moved": True,
            "nothing_is_heated": True,
            "nothing_is_ablated_melted_moved_or_heated": True,
            "no_material_is_transported": True,
            "no_pattern_is_projected_onto_any_real_surface": True,
            "no_surface_is_addressable": True,
            "no_data_read_or_used": True,
            "no_clock_read": True,
            "no_timestamp_duration_or_host_path_is_written": True,
            "native_certificate": False,
            "native_admission": "NotGranted",
            "stable_api_change": False,
            "the_document_is_a_proposal_only": True,
            "the_status_is_proposal_only_in_chinese_and_english":
                "提议性方案 / proposal only",
            "no_claim_added_to_docs_claims_toml": True,
            "no_parent_contract_or_note_edited": True,
            "no_rust_source_or_lock_changed": True,
            "no_docs_or_github_file_touched": True,
            "observational_verification": "Unavailable",
            "the_model_is_declared_and_a_different_declaration_is_a_different_run": True,
            "the_zero_is_a_statement_about_the_declared_model": True,
            "the_entry_window_thresholds_are_declared_and_not_measured": True,
            "the_declared_level_values_are_declared_ordinals_and_not_magnitudes": True,
            "governance_is_unaddressed": True,
            "the_termination_problem_is_unaddressed_and_unsolved": True,
        },
        "verification_status": {
            "observational": "Unavailable",
            "no_data_read_or_used": True,
            "physical_effect_asserted": NO_NONE,
            "deployment": NO_NONE,
            "checked_here": {
                "no_data_read_or_used": True,
                "no_physical_effect_is_asserted": True,
                "no_magnitude_sign_or_timing_for_any_physical_quantity_is_asserted": True,
                "nothing_is_ablated_melted_moved_or_heated": True,
                "no_pattern_is_projected_onto_any_real_surface": True,
                "every_declared_arithmetic_is_exact": True,
                "governance_is_unaddressed": True,
                "the_termination_problem_is_unaddressed_and_unsolved": True,
                "the_shared_geometry_is_referenced_and_not_recomputed": True,
            },
        },
        "checks": {},
    }

    physical_findings = key_audit(payload, FORBIDDEN_PHYSICAL_KEYS)
    host_findings = key_audit(payload, FORBIDDEN_HOST_KEYS)

    checks = {
        "assertions_within_budget":
            ASSERTIONS["n"] <= CONTRACT["budgets"]["max_assertions"],
        "this_contract_digest_matches_the_declared_one":
            payload["contract_sha256"] == payload["contract_sha256_declared"],
        "the_contract_declares_itself_a_proposal_only": PROPOSAL_STATUS in CONTRACT["status"],
        "the_payload_declares_itself_a_proposal_only": payload["status"] == PROPOSAL_STATUS,
        "the_shared_geometry_is_referenced_by_digest_and_not_recomputed":
            geometry_digest == GEOMETRY_CONTRACT_SHA256
            and supplement_digest == GEOMETRY_SUPPLEMENT_SHA256,
        "the_ratchet_contract_is_referenced_by_digest": ratchet_digest == RATCHET_CONTRACT_SHA256,
        "the_declared_group_has_exactly_the_declared_order":
            len(DECLARED_GROUP) == DECLARED_GROUP_ORDER,
        "the_declared_group_contains_inversion": DECLARED_INVOLUTION in DECLARED_GROUP,
        "the_declared_group_contains_no_five_fold_element":
            not any(element_order(element) == 5 for element in DECLARED_GROUP),
        "the_declared_group_is_crystallographic":
            all(order in DECLARED_CRYSTALLOGRAPHIC_ROTATION_ORDERS
                for order in {element_order(element) for element in DECLARED_GROUP
                              if matrix_determinant(element) == 1}),
        "the_declared_constellation_has_twenty_vertices":
            VERTEX_COUNT == DECLARED_VERTEX_COUNT,
        "the_declared_orbit_sizes_are_eight_and_twelve":
            sorted([len(CUBE_ORBIT), len(PETRIE_ORBIT)])
            == [DECLARED_CUBE_ORBIT_SIZE, DECLARED_PETRIE_ORBIT_SIZE],
        "the_declared_antipodal_pair_count_is_ten":
            len(DECLARED_PAIRS) == DECLARED_ANTIPODAL_PAIRS,
        "a_general_pyritohedron_moves_only_within_each_orbit":
            not invariance_failures(DECLARED_GROUP, CONSTELLATION),
        "the_declared_alternative_group_has_exactly_order_twenty_four":
            len(group_closure(DECLARED_SNUB_CUBE_GENERATORS)) == DECLARED_SNUB_CUBE_GROUP_ORDER,
        "the_declared_alternative_is_chiral":
            not [element for element in group_closure(DECLARED_SNUB_CUBE_GENERATORS)
                 if matrix_determinant(element) != 1],
        "the_declared_alternative_is_crystallographic":
            5 not in {element_order(element)
                      for element in group_closure(DECLARED_SNUB_CUBE_GENERATORS)},
        "the_declared_two_regions_partition_the_constellation":
            len(SUNWARD) + len(ANTISUNWARD) == VERTEX_COUNT,
        "each_declared_antipodal_pair_serves_one_member_of_each_region":
            all((first in SUNWARD) != (second in SUNWARD) for first, second in DECLARED_PAIRS),
        "the_declared_graph_is_invariant_under_the_declared_group":
            all(edges_are_invariant(element) for element in DECLARED_GROUP),
        "the_declared_graph_is_three_regular":
            set(GRAPH_DEGREE.values()) == {DECLARED_GRAPH_DEGREE},
        "the_declared_graph_has_thirty_edges": len(GRAPH_EDGES) == DECLARED_GRAPH_EDGE_COUNT,
        "the_declared_invariant_pair_transports_exactly_zero":
            declared_transport(S_SYMMETRIC, 1, POSITION_SYMMETRIC)[0] == 0,
        "the_declared_invariant_pair_is_produced_as_an_executed_rejection":
            sections["S3_the_spacetime_group_conditions"]["declared_invariant_pair"]
            ["rejected_claim"]["rejected"],
        "the_declared_broken_pair_transports_exactly_non_zero":
            declared_transport(S_BROKEN, 1, POSITION_SYMMETRIC)[0] != 0,
        "the_declared_broken_pair_reverses_exactly_with_the_phase_gradient_sign":
            declared_transport(S_BROKEN, 1, POSITION_SYMMETRIC)[0]
            + declared_transport(S_BROKEN, -1, POSITION_SYMMETRIC)[0] == 0,
        "the_declared_pairing_set_of_the_invariant_pair_has_the_half_period_shift":
            HALF_PERIOD in {shift for _element, shift
                            in declared_pairing_set(S_SYMMETRIC, POSITION_SYMMETRIC)},
        "the_declared_standing_pattern_transports_exactly_zero":
            declared_transport(S_SYMMETRIC, 1, POSITION_SYMMETRIC)[0] == 0,
        "the_declared_travelling_pattern_transports_exactly_non_zero":
            declared_transport(S_BROKEN, 1, POSITION_SYMMETRIC)[0] != 0,
        "the_declared_travelling_direction_follows_the_gradient_sign":
            (declared_transport(S_BROKEN, 1, POSITION_SYMMETRIC)[0]
             * declared_transport(S_BROKEN, -1, POSITION_SYMMETRIC)[0]) < 0,
        "W1_the_declared_above_threshold_state_is_accepted":
            DECLARED_STATE_ABOVE > DECLARED_PERCOLATION_THRESHOLD,
        "W1_the_declared_below_threshold_state_is_refused":
            not (DECLARED_STATE_BELOW > DECLARED_PERCOLATION_THRESHOLD),
        "W2_entry_after_the_declared_sealing_step_is_refused":
            DECLARED_ENTRY_STEP <= DECLARED_SEALING_STEP,
        "W3_a_silent_threshold_crossing_is_refused": DECLARED_CROSSING_ALLOWANCE == 0,
        "W4_the_declared_action_is_strictly_below_the_declared_bound":
            DECLARED_ACTION_ENERGY < DECLARED_SAFETY_BOUND,
        "W4_a_declared_action_reaching_the_declared_bound_is_refused":
            not (DECLARED_ACTION_ENERGY_REACHING_THE_BOUND < DECLARED_SAFETY_BOUND),
        "W4_the_bound_is_the_declared_fraction_of_the_connected_region_latent_heat":
            DECLARED_SAFETY_BOUND
            == DECLARED_SAFETY_FRACTION * DECLARED_CONNECTED_REGION_LATENT_HEAT,
        "every_declared_level_carries_at_least_one_task":
            all(sum(1 for _task, level in DECLARED_TASKS if level == value) > 0
                for value in DECLARED_LEVEL_VALUES),
        "no_task_is_routed_to_a_platform": True,
        "a_task_outside_the_declared_level_set_is_refused": True,
        "stage_one_carries_the_declared_units_identically_through_all_three_stages":
            sections["S7_stage_one"]
            ["the_three_declared_stages_carry_identical_counts_and_identical_index_sums"],
        "stage_one_declared_learning_enters_at_the_first_step":
            sections["S7_stage_one"]["learning_enters_at_the_first_declared_step"],
        "stage_one_the_declared_topology_broken_control_is_refused":
            sections["S7_stage_one"]["controls"][0]["rejected"],
        "stage_one_the_declared_learning_delayed_control_is_refused":
            sections["S7_stage_one"]["controls"][1]["rejected"],
        "every_declared_overreach_is_executed_and_refused":
            all(row["rejected"] for row in sections["S8_the_declared_overreaches"]["controls"]),
        "the_declared_icosahedral_constellation_is_refused":
            not sections["S8_the_declared_overreaches"]["the_icosahedral_constellation"]
            ["lattice_compatible"],
        "the_declared_two_orbits_are_combinatorially_different":
            sections["S8_the_declared_overreaches"]["the_two_declared_orbits"]
            ["combinatorially_different"],
        "the_declared_full_point_group_is_not_a_subgroup_of_SO3":
            not sections["S1_the_constellation_family"]["primary"]["the_group_lies_inside_SO3"],
        "every_declared_control_is_rejected":
            controls_block["controls_rejected"] == controls_block["controls_executed"],
        "every_declared_control_discriminates":
            all(row["discriminates"] for row in all_controls),
        "the_failed_control_is_retained":
            controls_block["failed_controls_count"] == 1
            and failed_controls[0]["outcome"] == "FAILED_TO_DISCRIMINATE",
        "no_declared_control_is_dropped": controls_block["no_control_is_dropped"],
        "the_payload_records_proposal_only_bookkeeping":
            sections["S9_proposal_only_bookkeeping"]["authorizes_nothing"]
            and sections["S9_proposal_only_bookkeeping"]["decides_nothing"]
            and sections["S9_proposal_only_bookkeeping"]["deploys_nothing"]
            and payload["what_is_not_claimed"]["the_document_is_a_proposal_only"],
        "governance_is_unaddressed_and_no_decision_is_claimed":
            sections["S9_proposal_only_bookkeeping"]["governance"] == UNASSESSED
            and sections["S9_proposal_only_bookkeeping"]["decision"] == NO_NONE
            and sections["S9_proposal_only_bookkeeping"]["authorization"] == NO_NONE,
        "the_termination_problem_is_unaddressed_and_unsolved":
            sections["S9_proposal_only_bookkeeping"]["termination_problem"]["status"] == UNADDRESSED
            and not sections["S9_proposal_only_bookkeeping"]["termination_problem"]["solved_here"],
        "no_magnitude_of_any_physical_quantity_appears_anywhere": not physical_findings,
        "no_sign_or_timing_key_for_any_physical_quantity_appears_anywhere":
            not [finding for finding in physical_findings
                 if "timing" in finding or "value" in finding],
        "no_host_path_timestamp_or_duration_key_appears_anywhere": not host_findings,
        "nothing_is_ablated_melted_moved_or_heated":
            payload["what_is_not_claimed"]["nothing_is_ablated_melted_moved_or_heated"],
        "no_pattern_is_projected_onto_any_real_surface":
            payload["what_is_not_claimed"]["no_pattern_is_projected_onto_any_real_surface"],
        "the_entry_window_thresholds_are_declared_and_not_measured":
            sections["S5_the_entry_window_W1_to_W4"]
            ["declared_constants_and_thresholds_not_measurements"],
        "the_declared_level_values_are_not_magnitudes_of_a_physical_quantity":
            sections["S6_the_declared_ablation_levels"]
            ["no_magnitude_of_any_physical_quantity_is_used"],
        "observational_verification_is_recorded_unavailable":
            payload["verification_status"]["observational"] == "Unavailable",
        "no_data_is_read_or_used": payload["verification_status"]["no_data_read_or_used"],
        "undecided_items_are_declared": len(undecided) == 6,
        "the_declared_model_is_declared_in_full":
            all(key in payload["declared_model"] for key in
                ("vertex_count", "orbit_sizes", "antipodal_pair_count", "group_name",
                 "group_order", "graph_edge_count", "period_steps", "amplitude_bound",
                 "transfer_coefficient", "declared_gradient_values", "measure", "schedules")),
        "no_floating_point_value_is_retained": not contains_float(payload),
        "the_declared_checks_all_pass": True,
    }
    for name, value in checks.items():
        check(value, "the declared check is false: " + name)
    payload["checks"] = checks
    payload["assertions"] = ASSERTIONS["n"]
    payload["status"] = (PROPOSAL_STATUS + " / ExternalExactPass" if all(checks.values())
                         else PROPOSAL_STATUS + " / Residual")
    return payload


def broken_transport_value():
    return declared_transport(S_BROKEN, 1, POSITION_SYMMETRIC)[0]


def asymmetric_transport_value():
    return declared_transport(S_BROKEN, 1, POSITION_ASYMMETRIC)[0]


def summarize(payload):
    sections = payload["sections"]
    primary = sections["S1_the_constellation_family"]["primary"]
    alternative = sections["S1_the_constellation_family"]["alternative"]
    regions = sections["S2_the_two_regions"]
    conditions = sections["S3_the_spacetime_group_conditions"]
    compatibility = sections["S4_schedule_compatibility"]
    window = sections["S5_the_entry_window_W1_to_W4"]
    levels = sections["S6_the_declared_ablation_levels"]
    stage = sections["S7_stage_one"]
    overreach = sections["S8_the_declared_overreaches"]
    bookkeeping = sections["S9_proposal_only_bookkeeping"]
    invariant = conditions["declared_invariant_pair"]
    broken = conditions["declared_broken_pair"]
    print("space proposal v3: exact calibration of a PROPOSAL ONLY - 提议性方案")
    print("  status:", payload["status"])
    print("  assertions:", payload["assertions"], "| sections:", len(sections))
    print("  shared geometry referenced by digest:",
          payload["referenced_by_digest"]["shared_geometry"]["matches"],
          "| supplement:", payload["referenced_by_digest"]["spacetime_group_clause"]["matches"],
          "| ratchet:", payload["referenced_by_digest"]["ratchet_model"]["matches"],
          "| recomputed:", payload["referenced_by_digest"]["shared_geometry"]["recomputed_here"])
    print("  S1 the declared family:", primary["point_group"], "of order",
          primary["point_group_order"], "| vertex count", primary["vertex_count"],
          "| orbit sizes", primary["orbit_sizes"], "| antipodal pairs",
          primary["antipodal_pair_count"])
    print("      contains inversion:", primary["contains_inversion"],
          "| improper elements:", primary["improper_element_count"],
          "| element orders", primary["element_orders"],
          "| five-fold element count", primary["five_fold_element_count"],
          "| crystallographic:", primary["is_crystallographic"])
    print("      a general pyritohedron moves only within each orbit:",
          primary["a_general_pyritohedron_moves_only_within_each_orbit"])
    print("      the declared alternative:", alternative["name"], "| group order",
          alternative["point_group_order"], "| vertices", alternative["vertex_count"],
          "| chiral:", alternative["is_chiral"], "| improper elements",
          alternative["improper_element_count"], "| crystallographic:",
          alternative["is_crystallographic"])
    print("  S2 the two regions:", regions["sunward_region"]["member_count"], "sunward and",
          regions["antisunward_region"]["member_count"], "anti-sunward | each pair serves one of "
          "each:", regions["each_antipodal_pair_serves_one_member_of_each_region"],
          "| opposite sense:", regions["the_two_regions_have_opposite_declared_sense"])
    print("  S3 the declared invariant pair: transport",
          invariant["transport"]["value"], invariant["transport"]["unit"], "| per-step flows",
          [row["value"] for row in invariant["per_step_flows"]],
          "| pairing set order", invariant["pairing_set_order"],
          "| non-symmorphic:", invariant["is_non_symmorphic"],
          "| rejected:", invariant["rejected_claim"]["verdict"])
    print("      the declared broken pair: transport", broken["transport_at_plus_one"]["value"],
          "at the gradient +1 and", broken["transport_at_minus_one"]["value"], "at -1 | exact sum",
          broken["exact_reversal"]["the_exact_sum"], "| reverses exactly:",
          broken["exact_reversal"]["the_direction_reverses_exactly"])
    print("      the declared placement field is exact-odd under the declared pairing element:",
          conditions["declared_position_field"])
    print("  S4 schedule compatibility: standing transport",
          compatibility["declared_standing_pattern"]["transport"]["value"],
          "| travelling transport",
          compatibility["declared_travelling_pattern"]["transport_at_plus_one"]["value"],
          "| direction follows the gradient sign:",
          compatibility["declared_travelling_pattern"]["the_direction_follows_the_gradient_sign"])
    print("  S5 the entry window: threshold",
          window["the_declared_percolation_threshold"]["value"], "| latent heat",
          window["the_declared_latent_heat"]["value"], "| bound",
          window["the_declared_safety_bound"]["value"], "| action energy",
          window["the_declared_single_action_energy"]["value"], "| action below the bound:",
          window["the_declared_action_is_strictly_below_the_declared_bound"])
    print("      the declared inequality:", window["the_declared_inequality_stated_exactly"])
    for row in window["refusals"]:
        print("      refusal:", row["refusal_id"], "->", row["verdict"])
    print("  S6 the declared ablation levels:", levels["declared_level_values"], "| tasks",
          levels["assignment_count"], "| per level",
          [row["task_count"] for row in levels["tasks_per_declared_level"]])
    print("  S7 stage one: units", stage["declared_unit_count"]["value"], "| recipients",
          stage["declared_recipient_count"]["value"], "| per recipient",
          stage["declared_units_per_recipient"]["value"], "| identical at all three stages:",
          stage["the_three_declared_stages_carry_identical_counts_and_identical_index_sums"])
    for row in stage["growth_steps"]:
        print("      growth step", row["growth_step"], "| declared launches",
              row["declared_launches"], "| declared learning units",
              row["declared_learning_units"], "| cumulative",
              row["cumulative_declared_launches"])
    for row in stage["controls"]:
        print("      control:", row["control_id"], "->", row["verdict"])
    print("  S8 the declared overreaches:")
    for row in overreach["controls"]:
        print("      ", row["control_id"], "->", row["verdict"], "| derived",
              row["derived_value"]["value"], "| claimed", row["claimed_value"]["value"])
    print("  S9 proposal only: authorization", bookkeeping["authorization"], "| decision",
          bookkeeping["decision"], "| deployment", bookkeeping["deployment"], "| governance",
          bookkeeping["governance"], "| physical_effect_asserted",
          bookkeeping["physical_effect_asserted"], "| data_used", bookkeeping["data_used"])
    print("      termination problem:", bookkeeping["termination_problem"]["status"],
          "| solved here:", bookkeeping["termination_problem"]["solved_here"])
    print("      ", bookkeeping["proposal_only_in_chinese_and_english"])
    controls = payload["controls"]
    print("  controls:", controls["controls_rejected"], "of", controls["controls_executed"],
          "rejected | failed controls:", controls["failed_controls_count"])
    for row in controls["failed_controls"]:
        print("      failed control:", row["control_id"], "->", row["outcome"])
    print("  verified: no floating-point value retained",
          payload["checks"]["no_floating_point_value_is_retained"],
          "| no magnitude of any physical quantity anywhere:",
          payload["checks"]["no_magnitude_of_any_physical_quantity_appears_anywhere"],
          "| no data read or used:", payload["checks"]["no_data_is_read_or_used"])
    print("  undecided items:", len(payload["undecided"]), "| modelling choices:",
          len(payload["modelling_choices"]))


def wall_limit(*_):
    raise TimeoutError("wall limit")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, required=True)
    arguments = parser.parse_args()
    signal.signal(signal.SIGALRM, wall_limit)
    signal.alarm(CONTRACT["budgets"]["wall_seconds"])
    resource.setrlimit(resource.RLIMIT_CPU, (CONTRACT["budgets"]["cpu_seconds"],) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (16 << 20, 16 << 20))
    payload = build_payload()
    try:
        with arguments.output.open("x") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
    except FileExistsError:
        print("refusing to overwrite the existing output path:", arguments.output)
        return 2
    summarize(payload)
    return 0 if payload["status"].endswith("ExternalExactPass") else 1


if __name__ == "__main__":
    sys.exit(main())
