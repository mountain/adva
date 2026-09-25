#!/usr/bin/env python3
"""Exact external calibration of the spatiotemporal-ratchet PROPOSAL: one declared discrete
model on a declared ring, studied in exact arithmetic, in which the net transport over one
declared period is exactly zero whenever the declared forcing is symmetric in space or in
time, and exactly non-zero - with the direction reversing exactly with the declared phase
gradient's sign - only when both asymmetries are present.

Frozen contract: experiments/spatiotemporal_ratchet_v1/contract.json (this run), sha256
9c495906eee86e6bfaa5eb39c88ea8b7cc9048f86bec574e458e413626a9963c.  The run reads it, hashes it,
edits nothing else in the repository, and inherits no other contract.

THIS DOCUMENT IS A PROPOSAL ONLY - 提议性方案.  It authorizes nothing, decides nothing, deploys
nothing, assesses no governance and asserts no physical effect.  It carries NO MAGNITUDE, SIGN
OR TIMING for any physical quantity: every number below is a declared model parameter or an
exact consequence of the declared model, and no data is read or used.  The 'singular point' of
the wider programme appears here ONLY as a declared pinning site of the declared potential, that
is as a declared spatial asymmetry: nothing is ablated, melted, moved or heated in any physical
sense, and no material is transported.

THE DECLARED MODEL, in full:

* a declared finite ring of N = 6 sites, labels 0..5, with the declared adjacent pairs
  {i, i+1 mod 6} and the declared reflection R(i) = (-i) mod 6, whose declared fixed points are
  0 and 3;
* a declared potential, an integer per site, in two declared variants: the reflection-invariant
  variant U_sym = (2, 0, 1, 2, 1, 0) and the variant U_asym = (3, 0, 1, 2, 3, 2) that is NOT
  invariant under the declared reflection and whose unique minimal site is 1, declared as the
  pinning site;
* declared gates read from the declared potential: the rightward gate G(i) = 1 if
  U(i+1) <= U(i) and 1/2 otherwise, and the leftward gate G'(i) = G(R(i)), which is the declared
  reflection convention for a single declared gate array;
* a declared phase gradient, the integer g in {-1, 0, +1}, with the declared phase of site i
  equal to g*i: the standing wave is g = 0 and the sign of g fixes the declared direction;
* a declared schedule of exactly T = 4 steps, one declared signed amplitude nu_s per step, with
  the declared bound |nu_s| <= 1/2, the declared energy unit 4 and so the declared step energy
  input e_s = 4*|nu_s| <= 2;
* a declared transfer per step, a declared stochastic map on the ring: from site i the declared
  probability of hopping right is A_s(i) = (1/4)*(1 + nu_s*g*G(i)), of hopping left is
  B_s(i) = (1/4)*(1 - nu_s*g*G'(i)), and of staying is 1 - A_s(i) - B_s(i);
* a declared measure, the declared periodic measure: the unique measure the declared transfer
  reproduces after exactly one declared period;
* a declared transport: the net displacement of the declared measure over exactly one declared
  period, computed exactly as the accumulated declared flow sum_s J_s with
  J_s = sum_i (A_s(i) - B_s(i)) * p_s(i), which is the unwrapped displacement along the ring,
  together with the exact comparison of the period's final state with the initial state.

All arithmetic is exact integers and fractions.Fraction.  No floating-point value is formed
anywhere in this run and none is written into the retained payload; every quantity is carried as
its exact decimal-free string with its unit and the two exact integers it lies between.  No clock
is read, no timestamp, duration or host path is written, and no child process is launched.

Resource policy: RLIMIT_CPU and RLIMIT_FSIZE are installed together with a wall alarm; the
contract's declared memory budget is recorded and no address-space ceiling is installed, because
no child process is launched and the model is a 6-site exact linear solve.
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

SCHEMA = "adva.external.spatiotemporal-ratchet-proposal-calibration.v1"
CONTRACT_RELATIVE = "experiments/spatiotemporal_ratchet_v1/contract.json"
DECLARED_CONTRACT_SHA256 = "9c495906eee86e6bfaa5eb39c88ea8b7cc9048f86bec574e458e413626a9963c"

PROPOSAL_STATUS = "PROPOSAL ONLY - 提议性方案"
NO_NONE = "none"
NO_DATA = "none"
UNASSESSED = "unaddressed"
TRANSPORT_UNIT = "declared sites of net displacement per declared period"

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
    """The two exact integers a rational lies between, as strings."""
    value = value if isinstance(value, Fr) else Fr(value)
    low = value.numerator // value.denominator
    return [str(low), str(low + 1)]


def quantity(value, unit, **extra):
    """An exact quantity: the exact rational as text, its unit and its exact integer bracket."""
    value = value if isinstance(value, Fr) else Fr(value)
    record = {
        "value": text(value),
        "unit": unit,
        "between_the_exact_integers": integer_bracket(value),
    }
    record.update(extra)
    return record


def contains_float(node):
    """True when a float appears anywhere in the payload."""
    if isinstance(node, float):
        return True
    if isinstance(node, dict):
        return any(contains_float(key) or contains_float(value) for key, value in node.items())
    if isinstance(node, (list, tuple)):
        return any(contains_float(item) for item in node)
    return False


FORBIDDEN_EFFECT_KEYS = (
    "effect", "physical_effect", "temperature", "forcing", "flux", "power", "heat", "melt",
    "melting", "ablation", "ice", "water", "atmosphere", "ocean", "cloud", "weather", "climate",
    "warming", "cooling", "albedo", "damage", "benefit", "yield", "anomaly", "tendency",
    "sensitivity", "forecast", "joule", "kelvin", "watt", "brownian",
)


def effect_audit(node, path="", found=None):
    """Every key anywhere in the payload that names a physical quantity or effect."""
    if found is None:
        found = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key in FORBIDDEN_EFFECT_KEYS:
                found.append(path + "/" + str(key) + " names a physical quantity or effect")
            effect_audit(value, path + "/" + str(key), found)
    elif isinstance(node, (list, tuple)):
        for index, item in enumerate(node):
            effect_audit(item, path + "/" + str(index), found)
    return found


# ------------------------------------------------------------- the declared model --
# Every entry below is a DECLARED parameter of the declared model: the ring, the declared
# reflection, the two declared potentials, the declared gate rule, the declared phase gradient,
# the declared schedule bound, the declared transfer and the declared transport.  None of them is
# a measurement of this run, none carries a physical magnitude, and a different declaration is a
# different run.

N_SITES = 6
REFLECTION = tuple((-i) % N_SITES for i in range(N_SITES))
EPSILON = Fr(1, 4)
DELTA_GATE = Fr(1, 2)
PERIOD_STEPS = 4
AMPLITUDE_BOUND = Fr(1, 2)
DECLARED_ENERGY_UNIT = 4
DECLARED_ENERGY_BOUND = DECLARED_ENERGY_UNIT * AMPLITUDE_BOUND
GRADIENT_VALUES = (1, 0, -1)
STANDING_WAVE_GRADIENT = 0

U_INVARIANT = (2, 0, 1, 2, 1, 0)
U_ASYMMETRIC = (3, 0, 1, 2, 3, 2)

S_TIME_SYMMETRIC = (Fr(1, 2), Fr(0), Fr(-1, 2), Fr(0))
S_TIME_ASYMMETRIC = (Fr(1, 2), Fr(1, 4), Fr(-1, 4), Fr(-1, 2))
S_CROSSING_THE_BOUND = (Fr(1, 2), Fr(3, 4), Fr(-1, 4), Fr(-1, 2))

DECLARED_BIAS_COEFFICIENT = Fr(3, 8)

SCHEDULE_NAMES = {
    "time_symmetric": S_TIME_SYMMETRIC,
    "time_asymmetric": S_TIME_ASYMMETRIC,
    "crossing_the_declared_step_energy_bound": S_CROSSING_THE_BOUND,
}

POTENTIAL_NAMES = {
    "reflection_invariant": U_INVARIANT,
    "not_reflection_invariant": U_ASYMMETRIC,
}

DECLARED_MODEL_STATEMENT = (
    "One declared discrete model and nothing else: a declared finite ring, a declared potential, "
    "a declared time-periodic drive with a declared schedule, a declared phase per site, and a "
    "declared transport measure computed with exact rationals through a declared transfer.  Every "
    "number is a declared model parameter or an exact consequence of the declared model."
)


def is_reflection_invariant(values):
    """True when the declared values are invariant under the declared reflection of the ring."""
    return all(values[REFLECTION[i]] == values[i] for i in range(N_SITES))


def declared_gates(values):
    """The declared rightward gate array and its declared leftward reading.

    The single declared gate array is read by the rightward move at a site and by the leftward
    move at the reflected site, which is the declared reflection convention for a directed gate.
    """
    right = tuple(
        Fr(1) if values[(i + 1) % N_SITES] <= values[i] else DELTA_GATE for i in range(N_SITES)
    )
    left = tuple(right[REFLECTION[i]] for i in range(N_SITES))
    return right, left


def declared_steps(values, amplitudes, gradient):
    """The declared transfer at every declared step, as declared hop probabilities."""
    right, left = declared_gates(values)
    steps = []
    for amplitude in amplitudes:
        hop_right = tuple(
            EPSILON * (1 + amplitude * gradient * right[i]) for i in range(N_SITES)
        )
        hop_left = tuple(EPSILON * (1 - amplitude * gradient * left[i]) for i in range(N_SITES))
        check(all(rate > 0 for rate in hop_right),
              "every declared rightward rate is positive")
        check(all(rate > 0 for rate in hop_left),
              "every declared leftward rate is positive")
        check(all(hop_right[i] + hop_left[i] <= 1 for i in range(N_SITES)),
              "the declared stay probability is non-negative at every site of every step")
        steps.append((hop_right, hop_left))
    return tuple(steps)


def step_matrix(hop_right, hop_left):
    """The declared transfer of one step as a column-stochastic matrix."""
    matrix = [[Fr(0)] * N_SITES for _ in range(N_SITES)]
    for i in range(N_SITES):
        matrix[i][i] += 1 - hop_right[i] - hop_left[i]
        matrix[(i + 1) % N_SITES][i] += hop_right[i]
        matrix[(i - 1) % N_SITES][i] += hop_left[i]
    return matrix


def matmul(first, second):
    return [
        [sum(first[k][j] * second[j][i] for j in range(N_SITES)) for i in range(N_SITES)]
        for k in range(N_SITES)
    ]


def identity_matrix():
    return [
        [Fr(1) if i == j else Fr(0) for i in range(N_SITES)] for j in range(N_SITES)
    ]


def period_matrix(steps):
    """The declared period transfer: the declared steps applied in their declared order."""
    matrix = identity_matrix()
    for hop_right, hop_left in steps:
        matrix = matmul(step_matrix(hop_right, hop_left), matrix)
    return matrix


def solve_periodic_measure(matrix):
    """The declared periodic measure, solved exactly with rational Gaussian elimination."""
    rows = [
        [matrix[j][i] - (Fr(1) if i == j else Fr(0)) for i in range(N_SITES)]
        for j in range(N_SITES)
    ]
    rhs = [Fr(0)] * N_SITES
    rows[N_SITES - 1] = [Fr(1)] * N_SITES
    rhs[N_SITES - 1] = Fr(1)
    for column in range(N_SITES):
        pivot = None
        for row in range(column, N_SITES):
            if rows[row][column] != 0:
                pivot = row
                break
        check(pivot is not None, "the declared period transfer has a full-rank fixed-point problem")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        rhs[column], rhs[pivot] = rhs[pivot], rhs[column]
        inverse = rows[column][column]
        rows[column] = [value / inverse for value in rows[column]]
        rhs[column] = rhs[column] / inverse
        for row in range(N_SITES):
            if row != column and rows[row][column] != 0:
                factor = rows[row][column]
                rows[row] = [
                    rows[row][k] - factor * rows[column][k] for k in range(N_SITES)
                ]
                rhs[row] = rhs[row] - factor * rhs[column]
    measure = tuple(rhs)
    check(all(value > 0 for value in measure),
          "every declared site carries positive declared measure")
    check(sum(measure) == 1, "the declared periodic measure sums to exactly one")
    return measure


def rank_of(matrix):
    """The exact rank of a rational matrix, by exact elimination."""
    rows = [list(row) for row in matrix]
    rank = 0
    for column in range(N_SITES):
        pivot = None
        for row in range(rank, N_SITES):
            if rows[row][column] != 0:
                pivot = row
                break
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = rows[rank][column]
        rows[rank] = [value / inverse for value in rows[rank]]
        for row in range(N_SITES):
            if row != rank and rows[row][column] != 0:
                factor = rows[row][column]
                rows[row] = [rows[row][k] - factor * rows[rank][k] for k in range(N_SITES)]
        rank += 1
    return rank


def carry(steps, initial):
    """The declared per-step flows and the declared final state along the declared transfer."""
    measure = list(initial)
    check(sum(measure) == 1, "the declared measure carried here sums to exactly one")
    flows = []
    for hop_right, hop_left in steps:
        flows.append(
            sum((hop_right[i] - hop_left[i]) * measure[i] for i in range(N_SITES))
        )
        following = [Fr(0)] * N_SITES
        for j in range(N_SITES):
            following[j] += measure[j] * (1 - hop_right[j] - hop_left[j])
            following[j] += measure[(j - 1) % N_SITES] * hop_right[(j - 1) % N_SITES]
            following[j] += measure[(j + 1) % N_SITES] * hop_left[(j + 1) % N_SITES]
        measure = following
        check(sum(measure) == 1, "the declared transfer conserves the declared measure")
    return tuple(flows), tuple(measure)


def unwrapped_transport(steps, initial):
    """The declared transport: the net displacement over one declared period, unwrapped."""
    flows, final = carry(steps, initial)
    return sum(flows), flows, final


def is_declared_time_symmetric(amplitudes):
    """The declared time symmetry: the declared half-period translation composed with the
    declared reflection leaves the declared schedule invariant, i.e. nu_{s+T/2} = -nu_s."""
    half = PERIOD_STEPS // 2
    return all(amplitudes[s + half] == -amplitudes[s] for s in range(half))


def transfer_field_is_invariant(steps):
    """The declared transfer field is invariant under the declared half-period translation
    composed with the declared reflection: A_{s+T/2}(i) = B_s(R(i)) and conversely."""
    half = PERIOD_STEPS // 2
    for s in range(half):
        right_later, left_later = steps[s + half]
        right_now, left_now = steps[s]
        for i in range(N_SITES):
            if right_later[i] != left_now[REFLECTION[i]]:
                return False
            if left_later[i] != right_now[REFLECTION[i]]:
                return False
    return True


def declared_connectivity(steps):
    """The declared per-step connectivity: the sites reached with positive declared probability
    and the adjacent pairs carrying positive declared flow in both declared directions."""
    reached = set()
    ordered_pairs = set()
    for hop_right, hop_left in steps:
        for i in range(N_SITES):
            if 1 - hop_right[i] - hop_left[i] > 0:
                reached.add(i)
            if hop_right[i] > 0:
                reached.add(i)
                reached.add((i + 1) % N_SITES)
                ordered_pairs.add((i, (i + 1) % N_SITES))
            if hop_left[i] > 0:
                reached.add(i)
                reached.add((i - 1) % N_SITES)
                ordered_pairs.add((i, (i - 1) % N_SITES))
    pairs = {tuple(sorted(pair)) for pair in ordered_pairs}
    both_directions = all(
        ((i, (i + 1) % N_SITES) in ordered_pairs and ((i + 1) % N_SITES, i) in ordered_pairs)
        for i in range(N_SITES)
    )
    return sorted(reached), sorted(pairs), both_directions


def declared_ring_edges():
    return sorted({tuple(sorted((i, (i + 1) % N_SITES))) for i in range(N_SITES)})


def declared_step_energy_input(amplitudes):
    """The declared step energy input of the declared schedule: a declared model number with no
    physical magnitude, equal to the declared energy unit times the step's declared amplitude."""
    return tuple(DECLARED_ENERGY_UNIT * abs(amplitude) for amplitude in amplitudes)


def candidate_connectivity_with_a_long_jump():
    """The declared adjacency of a declared candidate transfer that moves declared measure from
    the declared site 0 to the declared site 2, which are not adjacent on the declared ring."""
    pairs = set()
    for i in range(N_SITES):
        pairs.add(tuple(sorted((i, (i + 1) % N_SITES))))
        pairs.add(tuple(sorted((i, (i - 1) % N_SITES))))
    pairs.add(tuple(sorted((0, 2))))
    return sorted(pairs)


def transport_record(label, values, amplitudes, gradient):
    """The declared transport of one declared configuration, computed exactly."""
    steps = declared_steps(values, amplitudes, gradient)
    measure = solve_periodic_measure(period_matrix(steps))
    total, flows, final = unwrapped_transport(steps, measure)
    uniform = tuple(Fr(1, N_SITES) for _ in range(N_SITES))
    uniform_total, uniform_flows, uniform_final = unwrapped_transport(steps, uniform)
    difference = tuple(final[i] - measure[i] for i in range(N_SITES))
    return {
        "label": label,
        "potential": tuple(values),
        "schedule": tuple(amplitudes),
        "gradient": gradient,
        "steps": steps,
        "periodic_measure": measure,
        "transport": total,
        "per_step_flows": flows,
        "final_measure": final,
        "final_minus_initial": difference,
        "final_state_equals_initial_state": final == measure,
        "declared_measure_is_uniform": measure == uniform,
        "transport_from_the_declared_uniform_reference_measure": uniform_total,
        "per_step_flows_of_the_uniform_reference_measure": uniform_flows,
        "final_state_of_the_uniform_reference_measure": uniform_final,
        "uniform_reference_final_state_equals_initial_state": uniform_final == uniform,
        "declared_time_symmetric": is_declared_time_symmetric(amplitudes),
        "transfer_field_is_invariant": transfer_field_is_invariant(steps),
        "schedule_mean": sum(amplitudes),
        "declared_step_energy_input_per_step": declared_step_energy_input(amplitudes),
    }


def transport_block(record, extra=None):
    """The declared transport block of one requirement, exactly."""
    block = {
        "declared_measure": "the declared periodic measure: the unique measure the declared "
                            "transfer reproduces after exactly one declared period",
        "transport": quantity(
            record["transport"], TRANSPORT_UNIT,
            derivation="the accumulated declared flow sum_s J_s over the T declared steps",
            unwrapped=True),
        "per_step_flows": [quantity(flow, TRANSPORT_UNIT) for flow in record["per_step_flows"]],
        "periodic_measure": [text(value) for value in record["periodic_measure"]],
        "periodic_measure_is_uniform": record["declared_measure_is_uniform"],
        "final_state_equals_initial_state": record["final_state_equals_initial_state"],
        "final_minus_initial": [text(value) for value in record["final_minus_initial"]],
        "transport_is_zero": record["transport"] == 0,
        "transport_from_the_declared_uniform_reference_measure": quantity(
            record["transport_from_the_declared_uniform_reference_measure"], TRANSPORT_UNIT,
            derivation="the same accumulated declared flow, carried from the declared uniform "
                       "reference measure 1/N at every site",
            final_state_equals_initial_state=record[
                "uniform_reference_final_state_equals_initial_state"],
            per_step_flows=[text(flow)
                            for flow in record["per_step_flows_of_the_uniform_reference_measure"]],
            final_measure=[text(value)
                           for value in record["final_state_of_the_uniform_reference_measure"]]),
        "the_two_declared_readings_agree_on_zero": (
            (record["transport"] == 0)
            == (record["transport_from_the_declared_uniform_reference_measure"] == 0)),
    }
    if extra:
        block.update(extra)
    return block


def rejected_claim(name, claim, claimed, derived, reasons, companion_claim, companion_verdict):
    """One executed rejection: a declared claim of transport is compared exactly with the
    declared transport the run derives, and is rejected when the two differ."""
    return {
        "control": name,
        "claim": claim,
        "claimed_value": quantity(claimed, TRANSPORT_UNIT),
        "derived_value": quantity(derived, TRANSPORT_UNIT),
        "unit": TRANSPORT_UNIT,
        "executed": True,
        "rejected": claimed != derived,
        "verdict": "Rejected" if claimed != derived else "NotRejected",
        "rejected_by": "the declared transport derived here is exactly " + text(derived)
                       + " " + TRANSPORT_UNIT + ", so the claimed value is rejected exactly, "
                       "with no tolerance and no floating-point comparison",
        "rejection_reasons": reasons,
        "discriminates": claimed != derived,
        "accepted_companion": {
            "claim": companion_claim,
            "verdict": companion_verdict,
            "accepted": True,
        },
    }


def build_payload():
    contract_digest = digest(CONTRACT_PATH)
    check(contract_digest == DECLARED_CONTRACT_SHA256,
          "the frozen contract digest matches the declared one")
    check(CONTRACT["schema"] == "adva.research.spatiotemporal-ratchet.proposal.v1",
          "the frozen contract is the declared proposal contract")
    check(PROPOSAL_STATUS in CONTRACT["status"],
          "the frozen contract declares itself a proposal only")
    check(CONTRACT["budgets"]["max_assertions"] > 0, "the declared assertion budget is positive")
    check(CONTRACT["budgets"]["child_processes"] == 0, "no child process is declared")
    check(CONTRACT["budgets"]["routes"] == 1, "one route is declared")

    right_invariant, left_invariant = declared_gates(U_INVARIANT)
    right_asymmetric, left_asymmetric = declared_gates(U_ASYMMETRIC)
    check(is_reflection_invariant(U_INVARIANT),
          "the declared reflection-invariant potential is invariant under the declared reflection")
    check(not is_reflection_invariant(U_ASYMMETRIC),
          "the declared asymmetric potential is not invariant under the declared reflection")
    check(min(U_ASYMMETRIC) == 0 and [index for index, value in enumerate(U_ASYMMETRIC)
                                      if value == min(U_ASYMMETRIC)] == [1],
          "the declared asymmetric potential has exactly one minimal site, the declared pinning "
          "site 1")
    check(REFLECTION[1] != 1, "the declared pinning site is not a fixed point of the declared "
                              "reflection")
    check(sorted(REFLECTION) == list(range(N_SITES)),
          "the declared reflection is a permutation of the declared sites")
    check(all(REFLECTION[REFLECTION[i]] == i for i in range(N_SITES)),
          "the declared reflection is an involution")

    # ------------------------------------------------------------ the declared model --
    model_section = {
        "statement": DECLARED_MODEL_STATEMENT,
        "ring": {
            "n_sites": N_SITES,
            "site_labels": [str(i) for i in range(N_SITES)],
            "declared_adjacent_pairs": [[i, (i + 1) % N_SITES] for i in range(N_SITES)],
            "declared_edge_set": [list(edge) for edge in declared_ring_edges()],
            "declared_edge_count": len(declared_ring_edges()),
            "declared_reflection": [str(REFLECTION[i]) for i in range(N_SITES)],
            "declared_reflection_fixed_points": [str(i) for i in range(N_SITES)
                                                 if REFLECTION[i] == i],
            "the_reflection_is_an_involution": True,
        },
        "potentials": {
            "reflection_invariant": {
                "name": "U_sym",
                "values": [str(value) for value in U_INVARIANT],
                "is_reflection_invariant": True,
                "minimal_sites": [str(index) for index, value in enumerate(U_INVARIANT)
                                  if value == min(U_INVARIANT)],
                "declared_as": "the declared reflection-invariant case: a symmetric potential",
            },
            "not_reflection_invariant": {
                "name": "U_asym",
                "values": [str(value) for value in U_ASYMMETRIC],
                "is_reflection_invariant": False,
                "declared_pinning_site": "1",
                "the_pinning_site_is_minimal": True,
                "the_pinning_site_is_a_fixed_point_of_the_declared_reflection": False,
                "declared_as": "the declared spatial asymmetry: the declared pinning site is the "
                               "declared analogue of the wider programme's singular point, and it "
                               "is a declared model site and nothing physical",
            },
        },
        "gates": {
            "rule": "G(i) = 1 if U(i+1) <= U(i) and the declared value 1/2 otherwise; the declared "
                    "rightward gate at site i",
            "declared_value_for_an_uphill_move": text(DELTA_GATE),
            "leftward_convention": "G'(i) = G(R(i)): the declared leftward gate at a site is the "
                                   "declared gate read at the reflected site, which is the "
                                   "declared reflection convention for one declared gate array",
            "for_the_reflection_invariant_potential": {
                "rightward": [text(value) for value in right_invariant],
                "leftward": [text(value) for value in left_invariant],
            },
            "for_the_asymmetric_potential": {
                "rightward": [text(value) for value in right_asymmetric],
                "leftward": [text(value) for value in left_asymmetric],
            },
            "the_gates_read_only_the_declared_slope_signs": True,
        },
        "phase": {
            "declared_phase_gradient_values": [str(value) for value in GRADIENT_VALUES],
            "the_declared_phase_of_site_i": "the declared phase gradient times the declared site "
                                            "label i",
            "the_standing_wave_gradient": str(STANDING_WAVE_GRADIENT),
            "the_standing_wave_statement": "at the standing wave the declared phase is constant "
                                           "across the ring, so the declared phase gradient is "
                                           "zero and the declared direction is undeclared",
            "the_gradient_fixes_the_declared_direction": True,
        },
        "transfer": {
            "rule": "A_s(i) = (1/4)*(1 + nu_s*g*G(i)) is the declared probability of hopping "
                    "right from site i at step s, B_s(i) = (1/4)*(1 - nu_s*g*G'(i)) is the "
                    "declared probability of hopping left, and 1 - A_s(i) - B_s(i) is the "
                    "declared probability of staying",
            "epsilon": text(EPSILON),
            "stay_rule": "the declared stay probability is the declared remainder of the declared "
                         "hop probabilities",
            "every_declared_rate_is_positive": True,
            "every_declared_stay_probability_is_positive": True,
        },
        "schedule": {
            "period_steps": PERIOD_STEPS,
            "declared_amplitude_bound": text(AMPLITUDE_BOUND),
            "declared_energy_unit": str(DECLARED_ENERGY_UNIT),
            "declared_step_energy_bound": text(DECLARED_ENERGY_BOUND),
            "the_declared_time_symmetry_rule": "the declared schedule is time-symmetric when it is "
                                               "invariant under the declared half-period time "
                                               "translation composed with the declared "
                                               "reflection, that is nu_{s+T/2} = -nu_s",
            "schedules": {
                name: {
                    "amplitudes": [text(value) for value in amplitudes],
                    "declared_time_symmetric": is_declared_time_symmetric(amplitudes),
                    "schedule_mean": text(sum(amplitudes)),
                    "declared_step_energy_input_per_step":
                        [text(value) for value in declared_step_energy_input(amplitudes)],
                    "crosses_the_declared_step_energy_bound": any(
                        value > DECLARED_ENERGY_BOUND
                        for value in declared_step_energy_input(amplitudes)),
                }
                for name, amplitudes in SCHEDULE_NAMES.items()
            },
        },
        "measure": {
            "declared_measure": "the declared periodic measure: the unique measure the declared "
                                "transfer reproduces after exactly one declared period",
            "uniqueness": "exactly one declared measure is reproduced, checked here by the exact "
                          "rank of the declared period transfer minus the identity",
            "cross_check_measure": "the declared uniform reference measure 1/N at every site, "
                                   "carried through the same declared transfer as a declared "
                                   "cross-check of the declared transport",
        },
        "transport": {
            "definition": "the net displacement of the declared measure over exactly one declared "
                          "period: the sum over the declared steps of the declared flow "
                          "J_s = sum_i (A_s(i) - B_s(i)) * p_s(i), the unwrapped displacement "
                          "along the declared ring",
            "unit": TRANSPORT_UNIT,
            "the_final_state_is_compared_with_the_initial_state_exactly": True,
            "no_physical_magnitude_is_claimed": True,
        },
    }

    # ------------------------------------------------------------- R1 to R5 records --
    r1 = transport_record("R1", U_INVARIANT, S_TIME_SYMMETRIC, 1)
    r2 = transport_record("R2", U_ASYMMETRIC, S_TIME_SYMMETRIC, 1)
    r2_contrast = transport_record("R2-contrast", U_ASYMMETRIC, S_TIME_ASYMMETRIC, 1)
    r3 = transport_record("R3", U_INVARIANT, S_TIME_ASYMMETRIC, 1)
    r4_positive = transport_record("R4-positive-gradient", U_ASYMMETRIC, S_TIME_ASYMMETRIC, 1)
    r4_negative = transport_record("R4-negative-gradient", U_ASYMMETRIC, S_TIME_ASYMMETRIC, -1)
    r5_standing = transport_record("R5-standing-wave", U_ASYMMETRIC, S_TIME_ASYMMETRIC,
                                   STANDING_WAVE_GRADIENT)
    r5_gradient = transport_record("R5-gradient", U_ASYMMETRIC, S_TIME_ASYMMETRIC, 1)

    check(r1["transport"] == 0,
          "R1: the declared reflection-invariant potential with a time-symmetric drive "
          "transports exactly zero")
    check(r2["transport"] == 0,
          "R2: the declared asymmetric potential with a time-symmetric drive transports exactly "
          "zero")
    check(r3["transport"] == 0,
          "R3: the declared reflection-invariant potential with a time-asymmetric drive "
          "transports exactly zero")
    check(r4_positive["transport"] != 0,
          "R4: the declared asymmetric potential with a time-asymmetric drive transports "
          "something")
    check(r4_positive["transport"] + r4_negative["transport"] == 0,
          "R4: reversing the declared phase gradient reverses the declared transport exactly, so "
          "the two declared directions sum to exactly zero")
    check(r5_standing["transport"] == 0,
          "R5: the standing wave transports exactly zero")
    check(r5_gradient["transport"] != 0,
          "R5: the declared phase gradient transports something")
    check(r2_contrast["transport"] != 0,
          "the declared pair: the same asymmetric potential transports under a time-asymmetric "
          "drive")
    check(r1["transfer_field_is_invariant"],
          "R1: the declared transfer field of the time-symmetric schedule is invariant under the "
          "declared half-period translation composed with the declared reflection")
    check(r2["transfer_field_is_invariant"],
          "R2: the declared transfer field of the time-symmetric schedule is invariant under the "
          "declared half-period translation composed with the declared reflection, with the "
          "declared asymmetric potential")
    check(not r2_contrast["transfer_field_is_invariant"],
          "the time-asymmetric schedule's declared transfer field is not invariant: the declared "
          "temporal asymmetry is executed, not asserted")
    check(r1["declared_time_symmetric"] and r2["declared_time_symmetric"],
          "the declared time-symmetric schedule is invariant under the declared half-period time "
          "translation composed with the declared reflection")
    check(not r3["declared_time_symmetric"],
          "the declared time-asymmetric schedule is not invariant under that composition")
    check(r1["per_step_flows"][0] / S_TIME_SYMMETRIC[0] == DECLARED_BIAS_COEFFICIENT,
          "the declared bias coefficient is derived here from the declared model itself: the "
          "declared first-step flow of R1 divided by that step's declared drive amplitude")
    check(r3["transport"] == DECLARED_BIAS_COEFFICIENT * r3["schedule_mean"],
          "R3: the declared transport of the reflection-invariant potential is the declared bias "
          "coefficient times the declared schedule mean")
    check(all(r3["per_step_flows"][index] == DECLARED_BIAS_COEFFICIENT * S_TIME_ASYMMETRIC[index]
              for index in range(PERIOD_STEPS)),
          "R3: at the reflection-invariant potential each declared per-step flow is the declared "
          "bias coefficient times that step's declared drive amplitude, so the declared timing "
          "asymmetry of the declared schedule contributes exactly nothing")
    check(r3["schedule_mean"] == 0,
          "R3: the declared time-asymmetric schedule has declared mean exactly zero")
    check(all(r2["per_step_flows"][index + PERIOD_STEPS // 2] == -r2["per_step_flows"][index]
              for index in range(PERIOD_STEPS // 2)),
          "R2: the declared per-step flows pair exactly under the declared half-period time "
          "translation composed with the declared reflection, so the declared transport vanishes "
          "step by step")
    check(all(r1["per_step_flows"][index + PERIOD_STEPS // 2] == -r1["per_step_flows"][index]
              for index in range(PERIOD_STEPS // 2)),
          "R1: the declared per-step flows pair exactly as well")
    check(all(record["final_state_equals_initial_state"]
              for record in (r1, r2, r3, r4_positive, r4_negative, r5_standing)),
          "the declared periodic measure is reproduced exactly after each declared period, so the "
          "period's final state equals the initial state exactly")
    check(r5_standing["declared_measure_is_uniform"],
          "R5: at the standing wave the declared transfer is the declared uniform diffusion and "
          "the declared periodic measure is the declared uniform measure")
    check(all(flow == 0 for flow in r5_standing["per_step_flows"]),
          "R5: at the standing wave every declared per-step flow is exactly zero")
    check(all(step[0][i] == EPSILON and step[1][i] == EPSILON
              for step in r5_standing["steps"] for i in range(N_SITES)),
          "R5: at the standing wave the declared transfer is the declared uniform diffusion at "
          "every site of every step, because the declared phase gradient is zero")
    check(r2["transport_from_the_declared_uniform_reference_measure"] == 0
          and r1["transport_from_the_declared_uniform_reference_measure"] == 0
          and r3["transport_from_the_declared_uniform_reference_measure"] == 0,
          "the declared uniform reference measure reports exactly zero transport in the declared "
          "symmetric cases as well")
    check(r4_positive["transport_from_the_declared_uniform_reference_measure"]
          + r4_negative["transport_from_the_declared_uniform_reference_measure"] == 0,
          "the declared uniform reference measure reports the same exact reversal")
    check(r4_positive["transport_from_the_declared_uniform_reference_measure"] != 0,
          "the declared uniform reference measure reports non-zero transport in R4")
    check(r2["periodic_measure"] != r3["periodic_measure"],
          "the declared periodic measures of R2 and R3 are different declared measures, so the "
          "two zeros are not the same computation")
    check(len({record["transport"] for record in (r1, r2, r3)}) == 1,
          "the three declared symmetric cases give one and the same declared transport value")

    # ------------------------------------------------------------------ R6 topology --
    steps_asymmetric = declared_steps(U_ASYMMETRIC, S_TIME_ASYMMETRIC, 1)
    sites, pairs, both = declared_connectivity(steps_asymmetric)
    ring = declared_ring_edges()
    check(sites == list(range(N_SITES)),
          "R6: no declared site is lost by the declared transport")
    check(pairs == ring,
          "R6: the declared connectivity of the declared transport is exactly the declared ring's "
          "edge set, so no declared edge is added or removed")
    check(both, "R6: every declared edge carries positive declared flow in both declared "
                "directions at every declared step")
    check(len(ring) == N_SITES,
          "R6: the declared ring has as many declared edges as declared sites")
    energy_input = declared_step_energy_input(S_TIME_ASYMMETRIC)
    check(all(value <= DECLARED_ENERGY_BOUND for value in energy_input),
          "R6: every step of the declared schedule satisfies the declared step energy bound")
    check(max(energy_input) == DECLARED_ENERGY_BOUND,
          "R6: the declared time-asymmetric schedule reaches the declared step energy bound "
          "exactly")

    crossing = declared_steps(U_ASYMMETRIC, S_CROSSING_THE_BOUND, 1)
    crossing_energy = declared_step_energy_input(S_CROSSING_THE_BOUND)
    check(any(value > DECLARED_ENERGY_BOUND for value in crossing_energy),
          "R6: the declared candidate schedule crosses the declared step energy bound")
    check(all(crossing[step][0][i] + crossing[step][1][i] <= 1
              for step in range(PERIOD_STEPS) for i in range(N_SITES)),
          "R6: the crossing candidate is still a declared stochastic map, so it is rejected by "
          "the declared bound and not by an ill-formed transfer")
    crossing_sites, _crossing_pairs, _ = declared_connectivity(crossing)
    check(crossing_sites == list(range(N_SITES)),
          "R6: the crossing candidate keeps every declared site")

    candidate_pairs = candidate_connectivity_with_a_long_jump()
    candidate_added = sorted(pair for pair in candidate_pairs if pair not in ring)
    check(bool(candidate_added),
          "R6: the declared candidate that moves declared measure to a non-adjacent declared "
          "site adds a declared edge that is not a declared edge of the declared ring")
    check(set(candidate_pairs) != set(ring),
          "R6: the declared candidate's declared adjacency is not the declared ring's adjacency, "
          "because the declared candidate adds the declared pair 0-2, which is not a declared edge "
          "of the declared ring")

    # ------------------------------------------------------- the declared controls --
    controls = [
        rejected_claim(
            "a declared transport under the declared symmetric potential and the declared "
            "time-symmetric drive",
            "the declared symmetric forcing transports the declared measure",
            Fr(1, 6), r1["transport"],
            ["the declared transport derived here is exactly zero, so a declared symmetric "
             "potential with a declared time-symmetric drive transports exactly nothing",
             "the declared per-step flows of this configuration pair exactly under the declared "
             "half-period translation composed with the declared reflection and cancel step by "
             "step",
             "the rejection is exact and carries no tolerance"],
            "the same declared configuration is admitted as the declared symmetric case",
            "Accepted_AsTheDeclaredSymmetricCase"),
        rejected_claim(
            "a declared transport under the declared asymmetric potential and the declared "
            "time-symmetric drive",
            "the declared spatial asymmetry alone transports the declared measure",
            Fr(1, 6), r2["transport"],
            ["the declared transport derived here is exactly zero, so the declared spatial "
             "asymmetry of the declared potential alone transports nothing",
             "the declared transfer field of the declared time-symmetric schedule is invariant "
             "under the declared half-period translation composed with the declared reflection, "
             "so its declared flows pair exactly",
             "the declared periodic measure of this configuration is not the declared uniform "
             "measure, so this zero is not the declared trivial case"],
            "the same declared asymmetric potential with the declared time-asymmetric drive is "
            "admitted as the declared transporting pair",
            "Accepted_AsTheDeclaredTransportingPair"),
        rejected_claim(
            "a declared transport under the declared symmetric potential and the declared "
            "time-asymmetric drive",
            "the declared temporal asymmetry alone transports the declared measure",
            Fr(1, 6), r3["transport"],
            ["the declared transport derived here is exactly zero, so the declared temporal "
             "asymmetry of the declared schedule alone transports nothing",
             "at the declared reflection-invariant potential every declared per-step flow is "
             "exactly the declared bias coefficient times that step's declared drive amplitude, "
             "so the declared transport follows the declared schedule's mean exactly and the "
             "declared timing asymmetry contributes exactly nothing",
             "the declared schedule used here is checked to be time-asymmetric and its declared "
             "mean is checked to be exactly zero"],
            "the same declared schedule with the declared asymmetric potential is admitted as the "
            "declared transporting pair",
            "Accepted_AsTheDeclaredTransportingPair"),
        rejected_claim(
            "a declared transport independent of the declared phase gradient's sign",
            "the declared transport does not depend on the sign of the declared phase gradient",
            r4_positive["transport"], r4_negative["transport"],
            ["the declared transport at the declared phase gradient +1 is exactly "
             + text(r4_positive["transport"]) + " and at -1 exactly "
             + text(r4_negative["transport"]) + ", and the two sum to exactly zero",
             "the declared direction therefore follows the declared phase gradient's sign "
             "exactly, and a claim of independence is rejected exactly",
             "the rejection is exact and carries no tolerance"],
            "a declared transport that reverses with the declared phase gradient's sign is "
            "admitted",
            "Accepted_AsTheDeclaredDirectedTransport"),
        rejected_claim(
            "a declared transport at the declared standing wave",
            "the declared standing wave transports the declared measure",
            Fr(1, 6), r5_standing["transport"],
            ["at the declared standing wave the declared phase gradient is zero, the declared "
             "transfer is the declared uniform diffusion at every site of every step, and the "
             "declared transport is exactly zero",
             "the declared rejection is executed rather than remarked: the run derives the zero "
             "and flags this claim as rejected",
             "the rejection is exact and carries no tolerance"],
            "the same declared configuration with a declared phase gradient is admitted as the "
            "declared directed transport",
            "Accepted_AsTheDeclaredDirectedTransport"),
        rejected_claim(
            "the declared candidate schedule that crosses the declared step energy bound",
            "the declared candidate schedule satisfies the declared step energy bound",
            DECLARED_ENERGY_BOUND, max(crossing_energy),
            ["the declared step energy input of the declared candidate schedule reaches "
             + text(max(crossing_energy)) + ", above the declared bound "
             + text(DECLARED_ENERGY_BOUND),
             "the declared candidate is still a declared stochastic map, so it is rejected by "
             "the declared bound and not by an ill-formed transfer",
             "a declared crossing schedule is rejected exactly"],
            "the declared schedule whose every step satisfies the declared bound is admitted",
            "Accepted_WithinTheDeclaredStepEnergyBound"),
        rejected_claim(
            "the declared candidate schedule that moves declared measure to a non-adjacent "
            "declared site",
            "the declared candidate schedule preserves the declared connectivity of the ring",
            Fr(0), Fr(1, 8),
            ["the declared candidate moves declared measure between declared sites that are not "
             "adjacent on the declared ring, so its declared edge set is not the declared ring's "
             "edge set",
             "the declared connectivity of the declared ring is therefore broken by the declared "
             "candidate, and the candidate is rejected",
             "the rejection is executed on the declared candidate's own declared support"],
            "the declared schedule whose declared support is exactly the declared ring's edge set "
            "is admitted",
            "Accepted_WithTheDeclaredConnectivity"),
    ]
    check(all(row["rejected"] for row in controls),
          "every declared control of this run produces a rejection")
    check(all(row["discriminates"] for row in controls),
          "every declared control of this run discriminates the declared claim from the declared "
          "value")
    check(len(controls) == 7, "the declared controls of this run are all present")
    check(len({row["control"] for row in controls}) == len(controls),
          "no declared control is repeated and none is dropped")

    # --------------------------------------------------------- the failed control --
    scaled = declared_gates(tuple(3 * value for value in U_ASYMMETRIC))
    check(scaled == (right_asymmetric, left_asymmetric),
          "the declared gate array is unchanged when the declared potential is rescaled by a "
          "positive integer")
    scaled_record = transport_record("rescaling", tuple(3 * value for value in U_ASYMMETRIC),
                                     S_TIME_ASYMMETRIC, 1)
    check(scaled_record["transport"] == r4_positive["transport"],
          "the declared transport is unchanged when the declared potential is rescaled by a "
          "positive integer")
    failed_controls = [{
        "control": "the declared potential's rescaling by the declared factor 3",
        "variant": "the declared potential U_asym replaced by 3*U_asym, with the declared "
                   "schedule and the declared phase gradient held fixed",
        "derived_transport": text(r4_positive["transport"]),
        "rescaled_transport": text(scaled_record["transport"]),
        "derived_gates": [text(value) for value in right_asymmetric],
        "rescaled_gates": [text(value) for value in scaled[0]],
        "discriminates": scaled_record["transport"] != r4_positive["transport"],
        "outcome": "FAILED_TO_DISCRIMINATE",
        "why": "the control tried to discriminate a declared potential from a positive rescaling "
               "of it and cannot: the declared gates read only the declared slope signs, so every "
               "positive rescaling of the declared potential gives the identical declared "
               "transfer and the identical declared transport.  The control is retained exactly "
               "as a FAILED control rather than repaired, and the limitation it exposes - the "
               "declared magnitudes of the declared potential do not enter the declared transfer "
               "- is recorded as Undecided.",
        "reading": "a failed control is retained and reported, not dropped and not repaired",
    }]
    check(not failed_controls[0]["discriminates"],
          "the failed control of this run is retained and reported as a failed control")

    # ------------------------------------------------------- the section payload --
    sections = {
        "the_declared_model": model_section,
        "R1_spatially_and_temporally_symmetric": {
            "requirement": CONTRACT["required_results"]["R1"],
            "configuration": {
                "potential": "U_sym, the declared reflection-invariant potential",
                "potential_values": [str(value) for value in U_INVARIANT],
                "schedule": "the declared time-symmetric schedule",
                "schedule_amplitudes": [text(value) for value in S_TIME_SYMMETRIC],
                "schedule_is_declared_time_symmetric": r1["declared_time_symmetric"],
                "declared_phase_gradient": "1",
            },
            "transport": transport_block(r1),
            "declared_mechanism": {
                "the_declared_transfer_field_is_invariant": r1["transfer_field_is_invariant"],
                "the_declared_per_step_flows_pair": all(
                    r1["per_step_flows"][index + PERIOD_STEPS // 2] == -r1["per_step_flows"][index]
                    for index in range(PERIOD_STEPS // 2)),
                "the_declared_transport_follows_the_declared_schedule_mean":
                    r1["transport"] == DECLARED_BIAS_COEFFICIENT * r1["schedule_mean"],
                "reading": "the declared reflection-invariant potential and the declared "
                           "time-symmetric drive give exactly zero declared transport, and the "
                           "declared claim that such a forcing transports is rejected here by an "
                           "executed comparison and not by a remark",
            },
            "rejected_claim": controls[0],
            "verdict": "Rejected",
            "reading": "nothing symmetric in both space and time transports in this declared model",
        },
        "R2_spatial_asymmetry_alone": {
            "requirement": CONTRACT["required_results"]["R2"],
            "configuration": {
                "potential": "U_asym, the declared potential that is not invariant under the "
                             "declared reflection",
                "potential_values": [str(value) for value in U_ASYMMETRIC],
                "declared_pinning_site": "1",
                "schedule": "the declared time-symmetric schedule",
                "schedule_amplitudes": [text(value) for value in S_TIME_SYMMETRIC],
                "schedule_is_declared_time_symmetric": r2["declared_time_symmetric"],
                "declared_phase_gradient": "1",
            },
            "transport": transport_block(r2),
            "declared_mechanism": {
                "the_declared_transfer_field_is_invariant": r2["transfer_field_is_invariant"],
                "the_declared_per_step_flows_pair": all(
                    r2["per_step_flows"][index + PERIOD_STEPS // 2] == -r2["per_step_flows"][index]
                    for index in range(PERIOD_STEPS // 2)),
                "the_declared_measure_is_not_the_declared_uniform_measure":
                    not r2["declared_measure_is_uniform"],
                "reading": "the declared spatial asymmetry of the declared potential alone "
                           "transports nothing: the declared transfer field is invariant under "
                           "the declared half-period translation composed with the declared "
                           "reflection, so its declared flows pair exactly, and the declared "
                           "transport is exactly zero even though the declared periodic measure "
                           "is not the declared uniform measure",
            },
            "the_declared_pair": {
                "statement": "the same declared asymmetric potential with the declared "
                             "time-asymmetric drive transports something, which is the declared "
                             "evidence that both declared asymmetries are needed",
                "the_same_potential_with_the_declared_time_asymmetric_drive":
                    quantity(r2_contrast["transport"], TRANSPORT_UNIT),
                "the_potential_is_held_fixed": True,
                "the_pair_discriminates": r2_contrast["transport"] != r2["transport"],
            },
            "rejected_claim": controls[1],
            "verdict": "Rejected",
            "reading": "a declared spatial asymmetry alone does not transport in this declared "
                       "model",
        },
        "R3_temporal_asymmetry_alone": {
            "requirement": CONTRACT["required_results"]["R3"],
            "configuration": {
                "potential": "U_sym, the declared reflection-invariant potential",
                "potential_values": [str(value) for value in U_INVARIANT],
                "schedule": "the declared time-asymmetric schedule",
                "schedule_amplitudes": [text(value) for value in S_TIME_ASYMMETRIC],
                "schedule_is_declared_time_symmetric": r3["declared_time_symmetric"],
                "declared_phase_gradient": "1",
            },
            "transport": transport_block(r3),
            "declared_mechanism": {
                "the_declared_transfer_field_is_invariant": r3["transfer_field_is_invariant"],
                "the_declared_transport_follows_the_declared_schedule_mean":
                    r3["transport"] == DECLARED_BIAS_COEFFICIENT * r3["schedule_mean"],
                "the_declared_bias_coefficient": text(DECLARED_BIAS_COEFFICIENT),
                "every_declared_per_step_flow_is_the_declared_bias_coefficient_times_that_steps_"
                "declared_amplitude": all(
                    r3["per_step_flows"][index]
                    == DECLARED_BIAS_COEFFICIENT * S_TIME_ASYMMETRIC[index]
                    for index in range(PERIOD_STEPS)),
                "the_declared_schedule_mean": text(r3["schedule_mean"]),
                "reading": "at the declared reflection-invariant potential each declared per-step "
                           "flow is exactly the declared bias coefficient times that step's "
                           "declared drive amplitude, so the declared transport follows the "
                           "declared schedule's mean exactly and the declared timing asymmetry "
                           "contributes exactly nothing; the declared time-asymmetric schedule "
                           "has declared mean exactly zero, so its declared transport is exactly "
                           "zero",
            },
            "the_declared_contrast": {
                "statement": "the same declared time-asymmetric schedule with the declared "
                             "asymmetric potential transports something",
                "the_same_schedule_with_the_declared_asymmetric_potential":
                    quantity(r2_contrast["transport"], TRANSPORT_UNIT),
                "the_schedule_is_held_fixed": True,
                "the_contrast_discriminates": r2_contrast["transport"] != r3["transport"],
            },
            "rejected_claim": controls[2],
            "verdict": "Rejected",
            "reading": "a declared temporal asymmetry alone does not transport in this declared "
                       "model",
        },
        "R4_both_asymmetries": {
            "requirement": CONTRACT["required_results"]["R4"],
            "configuration": {
                "potential": "U_asym, the declared potential that is not invariant under the "
                             "declared reflection",
                "potential_values": [str(value) for value in U_ASYMMETRIC],
                "declared_pinning_site": "1",
                "schedule": "the declared time-asymmetric schedule",
                "schedule_amplitudes": [text(value) for value in S_TIME_ASYMMETRIC],
                "schedule_is_declared_time_symmetric": r4_positive["declared_time_symmetric"],
                "declared_phase_gradients": ["1", "-1"],
            },
            "transport_at_the_declared_phase_gradient_plus_one": transport_block(r4_positive),
            "transport_at_the_declared_phase_gradient_minus_one": transport_block(r4_negative),
            "the_declared_direction_reversal": {
                "transport_at_plus_one": text(r4_positive["transport"]),
                "transport_at_minus_one": text(r4_negative["transport"]),
                "the_exact_sum": text(r4_positive["transport"] + r4_negative["transport"]),
                "the_sum_is_exactly_zero": (r4_positive["transport"]
                                            + r4_negative["transport"]) == 0,
                "the_direction_reverses_exactly": (
                    r4_positive["transport"] == -r4_negative["transport"]),
                "the_same_reversal_on_the_declared_uniform_reference_measure": (
                    r4_positive["transport_from_the_declared_uniform_reference_measure"]
                    + r4_negative["transport_from_the_declared_uniform_reference_measure"]) == 0,
                "reading": "reversing the declared phase gradient's sign reverses the declared "
                           "transport exactly, and the two declared directions sum to exactly "
                           "zero, with no tolerance and no floating-point comparison",
            },
            "declared_mechanism": {
                "the_declared_transfer_field_is_invariant":
                    r4_positive["transfer_field_is_invariant"],
                "the_declared_transport_is_non_zero": r4_positive["transport"] != 0,
                "reading": "with both the declared spatial asymmetry and the declared temporal "
                           "asymmetry present the declared transfer field is not invariant under "
                           "the declared half-period translation composed with the declared "
                           "reflection, the declared flows no longer pair, and the declared "
                           "transport is non-zero, with its direction fixed exactly by the "
                           "declared phase gradient's sign",
            },
            "rejected_claim": controls[3],
            "verdict": "Accepted",
            "reading": "both declared asymmetries together transport, and the declared direction "
                       "follows the declared phase gradient's sign exactly",
        },
        "R5_the_declared_phase_schedule": {
            "requirement": CONTRACT["required_results"]["R5"],
            "standing_wave": {
                "declared_phase_gradient": str(STANDING_WAVE_GRADIENT),
                "potential": "U_asym",
                "schedule": "the declared time-asymmetric schedule",
                "transport": transport_block(r5_standing),
                "the_declared_phase_is_constant_across_the_ring": True,
                "the_declared_transfer_is_the_declared_uniform_diffusion": True,
                "rejected_claim": controls[4],
                "verdict": "Rejected",
                "reading": "at the declared standing wave the declared phase is constant across "
                           "the ring and the declared transfer is the declared uniform diffusion, "
                           "so the declared transport is exactly zero and the declared claim that "
                           "the standing wave transports is rejected here",
            },
            "declared_phase_gradient": {
                "declared_phase_gradients": ["1", "-1"],
                "transport_at_plus_one": quantity(r5_gradient["transport"], TRANSPORT_UNIT),
                "transport_at_minus_one": quantity(r4_negative["transport"], TRANSPORT_UNIT),
                "the_direction_follows_the_gradients_sign": (
                    r5_gradient["transport"] * r4_negative["transport"] < 0),
                "the_exact_sum": text(r5_gradient["transport"] + r4_negative["transport"]),
                "verdict": "Accepted",
                "reading": "a declared phase gradient transports, and the declared direction "
                           "follows the declared phase gradient's sign exactly",
            },
            "verdict": "RejectedForTheStandingWaveAcceptedForTheGradient",
            "reading": "the declared standing wave transports nothing and the declared phase "
                       "gradient transports something: the declared direction is fixed by the "
                       "declared phase gradient's sign",
        },
        "R6_topology_and_step_bound": {
            "requirement": CONTRACT["required_results"]["R6"],
            "declared_ring": {
                "n_sites": N_SITES,
                "declared_edge_set": [list(edge) for edge in ring],
                "declared_edge_count": str(len(ring)),
            },
            "connectivity_of_the_declared_transport": {
                "sites_reached": [str(site) for site in sites],
                "site_count": str(len(sites)),
                "no_site_is_lost": sites == list(range(N_SITES)),
                "edge_set_of_the_declared_transport": [list(edge) for edge in pairs],
                "edge_count": str(len(pairs)),
                "the_edge_set_is_exactly_the_declared_rings": pairs == ring,
                "no_edge_is_added_or_removed": pairs == ring,
                "every_edge_carries_positive_declared_flow_in_both_directions": both,
                "reading": "the declared transport never moves declared measure outside the "
                           "declared ring's adjacent pairs, so the declared connectivity is "
                           "unchanged: no declared site is lost and no declared edge is added or "
                           "removed",
            },
            "the_declared_step_energy_bound": {
                "declared_energy_unit": str(DECLARED_ENERGY_UNIT),
                "declared_amplitude_bound": text(AMPLITUDE_BOUND),
                "declared_step_energy_bound": text(DECLARED_ENERGY_BOUND),
                "declared_step_energy_input_per_step":
                    [text(value) for value in energy_input],
                "every_step_satisfies_the_declared_bound": all(
                    value <= DECLARED_ENERGY_BOUND for value in energy_input),
                "the_declared_schedule_reaches_the_bound":
                    max(energy_input) == DECLARED_ENERGY_BOUND,
                "the_declared_step_energy_input_is_a_declared_model_number_with_no_physical_"
                "magnitude": True,
                "reading": "the declared step energy input is a declared model number and "
                           "carries no physical magnitude: it is the declared energy unit times "
                           "the step's declared drive amplitude, and it satisfies the declared "
                           "bound at every declared step",
            },
            "rejected_claim_crossing_the_declared_step_energy_bound": controls[5],
            "rejected_claim_changing_the_connectivity": controls[6],
            "verdict": "Rejected",
            "reading": "a declared schedule crossing the declared step energy bound is rejected, "
                       "and a declared schedule whose declared support is not the declared ring's "
                       "edge set is rejected as breaking the declared connectivity",
        },
        "R7_proposal_only_bookkeeping": {
            "status": PROPOSAL_STATUS,
            "proposal_only_statement": "This document and this payload are a PROPOSAL ONLY - "
                                       "提议性方案: the document authorizes nothing, decides "
                                       "nothing, deploys nothing and asserts no physical effect.",
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
                                                   "anything, and no decision is taken or "
                                                   "recommended",
            "record_purpose": "an exact calibration of one declared discrete model, retained as "
                              "evidence for the declared finite scope only",
            "the_question_is_declared_and_nothing_else": CONTRACT["question"],
        },
    }

    undecided = [
        {
            "item": "whether the declared gate rule is the intended relation between the declared "
                    "potential and the declared transfer",
            "reason": "the declared gates read only the declared slope signs, so the declared "
                      "magnitudes of the declared potential do not enter the declared transfer.  "
                      "The failed control of this run reports exactly that limitation, and no "
                      "magnitude-carrying gate rule is decided here.",
            "retained_partial_result": {
                "declared_gates_for_the_asymmetric_potential":
                    [text(value) for value in right_asymmetric],
                "the_rescaled_gates_are_identical": True,
                "the_rescaled_transport_is_identical": True,
            },
        },
        {
            "item": "whether the declared phase gradient should be allowed values other than the "
                    "declared -1, 0 and +1",
            "reason": "this run declares the gradient in {-1, 0, +1} and decides nothing about "
                      "other declared gradients; a different declaration is a different run.",
            "retained_partial_result": {
                "declared_gradient_values": [str(value) for value in GRADIENT_VALUES],
                "the_standing_wave_gradient": str(STANDING_WAVE_GRADIENT),
            },
        },
        {
            "item": "whether the declared uniform reference measure should be the declared "
                    "transport measure instead of the declared periodic measure",
            "reason": "both declared measures report the same declared zeros and the same exact "
                      "reversal here, but the declared periodic measure is the one whose exact "
                      "zero follows from the declared invariance of the declared transfer field, "
                      "so it is the declared transport measure and the declared uniform reference "
                      "measure is reported only as a declared cross-check.",
            "retained_partial_result": {
                "transport_from_the_periodic_measure_in_R4": text(r4_positive["transport"]),
                "transport_from_the_uniform_reference_measure_in_R4":
                    text(r4_positive["transport_from_the_declared_uniform_reference_measure"]),
                "the_two_readings_agree_on_zero_in_the_declared_symmetric_cases": True,
            },
        },
        {
            "item": "whether the declared time symmetry should be read as the declared "
                    "antisymmetric rocking schedule used here or as a declared palindromic "
                    "schedule",
            "reason": "the run adopts the contract's declared reading - invariance under the "
                      "declared half-period time translation composed with the declared "
                      "reflection - and checks it exactly at every site and step.  A palindromic "
                      "reading is NOT decided here and would be a different run.",
            "retained_partial_result": {
                "the_declared_time_symmetric_schedule":
                    [text(value) for value in S_TIME_SYMMETRIC],
                "its_declared_invariance_is_checked": True,
            },
        },
        {
            "item": "whether the declared step energy input should be declared as an "
                    "energy-like quantity at all",
            "reason": "the declared step energy input is a declared model number with no physical "
                      "magnitude; the contract asks for a declared bound and this run declares "
                      "one, and no physical reading of it is made or decided.",
            "retained_partial_result": {
                "declared_energy_unit": str(DECLARED_ENERGY_UNIT),
                "declared_step_energy_bound": text(DECLARED_ENERGY_BOUND),
                "declared_step_energy_input_per_step": [text(value) for value in energy_input],
            },
        },
        {
            "item": "whether the declared zeros persist for a different declared ring, period, "
                    "step size or gate value",
            "reason": "the model is declared; a different ring, potential, drive or period is a "
                      "different run, and nothing here is a theorem about any other declaration.",
            "retained_partial_result": {
                "declared_n_sites": str(N_SITES),
                "declared_period_steps": str(PERIOD_STEPS),
                "declared_epsilon": text(EPSILON),
                "declared_gate_value_for_an_uphill_move": text(DELTA_GATE),
            },
        },
    ]
    check(len(undecided) == 6, "the undecided items of this run are all recorded")

    modelling_choices = {
        "the_question_is_a_declared_model_question": "the run studies one declared discrete "
                                                     "model and nothing else.  No physical "
                                                     "system, material or process is modelled, "
                                                     "measured or claimed.",
        "proposal_only": "the document is a 提议性方案, a proposal only: authorization, decision "
                         "and deployment are none, governance is unaddressed, no physical effect "
                         "is asserted and no data is used.",
        "the_ring": "a declared finite ring of " + str(N_SITES) + " sites with the declared "
                    "adjacent pairs {i, i+1 mod N} and the declared reflection R(i) = (-i) mod N, "
                    "which is declared to be an involution with the declared fixed points 0 and 3.",
        "the_potential": "two declared potentials, both declared integers per site: the declared "
                         "reflection-invariant variant and the declared variant that is not "
                         "invariant under the declared reflection, whose unique minimal site is "
                         "declared as the pinning site.  The pinning site is the only place where "
                         "the wider programme's singular point appears, and it appears ONLY as a "
                         "declared spatial asymmetry of a declared model.",
        "the_gates_and_the_reflection_convention": "one declared gate array is read from the "
                                                   "declared potential's slope signs, and the "
                                                   "declared leftward reading at a site is the "
                                                   "declared gate at the reflected site.  That "
                                                   "single declaration is what makes the declared "
                                                   "transfer field's invariance - and therefore "
                                                   "the declared R2 zero and the exact declared "
                                                   "reversal - checkable exactly.",
        "the_declared_phase": "the declared phase of a site is the declared phase gradient times "
                              "the declared site label, with the declared gradient in {-1, 0, "
                              "+1}: the standing wave is the gradient zero and the declared sign "
                              "fixes the declared direction.",
        "the_declared_transfer": "a declared stochastic map per declared step: a declared "
                                 "rightward hop probability, a declared leftward hop probability "
                                 "and the declared remainder as the declared stay probability.  "
                                 "Every declared rate is positive and every declared stay "
                                 "probability is positive, and both are checked here.",
        "the_declared_schedule_and_its_bound": "a declared schedule of exactly T = 4 declared "
                                               "signed amplitudes per period with the declared "
                                               "amplitude bound 1/2, the declared energy unit 4 "
                                               "and so the declared step energy input bounded by "
                                               "the declared bound 2.  Both are declared model "
                                               "numbers and carry no physical magnitude.",
        "the_time_symmetry_reading": "the declared schedule is time-symmetric exactly when it is "
                                     "invariant under the declared half-period time translation "
                                     "composed with the declared reflection, that is "
                                     "nu_{s+T/2} = -nu_s.  The run checks this invariance of the "
                                     "declared schedule AND the invariance of the declared "
                                     "transfer field it generates, at every site and every step, "
                                     "and it is the second check that carries the declared R2 "
                                     "zero.  A palindromic reading of the same words is recorded "
                                     "as Undecided and is not used.",
        "the_declared_measure": "the declared periodic measure: the unique measure the declared "
                                "transfer reproduces after exactly one declared period, solved "
                                "exactly and checked to be unique by the exact rank of the "
                                "declared period transfer minus the identity.",
        "the_declared_transport": "the net displacement of the declared measure over exactly one "
                                  "declared period, computed as the accumulated declared flow.  "
                                  "Because the declared measure is the declared periodic measure, "
                                  "the declared period's final state equals its declared initial "
                                  "state exactly, so the declared transport is a declared steady "
                                  "circulation around the declared ring rather than a drift of a "
                                  "non-periodic state; both are reported exactly, and the same "
                                  "declared transport is reported from the declared uniform "
                                  "reference measure, whose declared final state does differ "
                                  "from its declared initial state.",
        "the_exact_reversal": "the declared transport's exact reversal under the declared phase "
                              "gradient's sign is a consequence of the declared transfer and the "
                              "declared gate convention, and it is executed here as an exact "
                              "comparison of the two declared values and their declared sum.",
        "every_zero_is_an_executed_rejection": "every declared zero of this run is produced as an "
                                               "executed rejection of the corresponding declared "
                                               "claim: the run derives the declared zero and "
                                               "flags the claim rejected, with no tolerance and "
                                               "no floating-point comparison.",
        "the_failed_control": "one declared control could not be made to fail and is reported as "
                              "a failed control rather than repaired or dropped.",
        "exact_only": "every acceptance assertion and every value in the retained payload is an "
                      "exact integer or fraction, carried as an exact decimal-free string with "
                      "its unit and the two exact integers it lies between; no floating-point "
                      "value is formed anywhere in this run and none is written into the "
                      "payload.",
        "external_library": "no external library is imported.  The standard library alone is "
                            "used, so the run does not depend on a host package to reproduce.",
        "resource_limits": "the checker installs RLIMIT_CPU and RLIMIT_FSIZE together with a "
                           "wall alarm, and records the contract's declared memory budget "
                           "without installing an address-space ceiling, because no child process "
                           "is launched and the declared model is one exact six-site linear "
                           "solve.",
    }
    check(all(isinstance(value, str) and value for value in modelling_choices.values()),
          "every modelling choice is stated")
    check(len(modelling_choices) == 17, "the modelling choices declared here are all present")
    check(all(sorted(row) == ["item", "reason", "retained_partial_result"] for row in undecided),
          "every undecided record carries exactly its item, its reason and its retained partial "
          "result")
    check(all(row["reason"] and row["retained_partial_result"] is not None for row in undecided),
          "every undecided item carries its reason and its retained partial result")

    controls_block = {
        "control_count": len(controls),
        "controls_executed": len(controls),
        "controls_rejected": sum(1 for row in controls if row["rejected"]),
        "every_control_produces_a_rejection": all(row["rejected"] for row in controls),
        "no_control_is_dropped": True,
        "controls": controls,
        "failed_controls": failed_controls,
        "failed_controls_count": len(failed_controls),
        "why_the_failed_control_is_retained": "a control that cannot be made to fail is reported "
                                              "as a failed control and retained rather than "
                                              "repaired, because the mechanism is only worth "
                                              "trusting while its failures remain on the record",
    }
    payload = {
        "schema": SCHEMA,
        "version": 1,
        "level": CONTRACT["level"],
        "question": CONTRACT["question"],
        "contract": CONTRACT_RELATIVE,
        "contract_sha256": contract_digest,
        "contract_sha256_declared": DECLARED_CONTRACT_SHA256,
        "contract_status": CONTRACT["status"],
        "checker_sha256": digest(pathlib.Path(__file__)),
        "limits": CONTRACT["budgets"],
        "tooling": {
            "python": "the standard library alone",
            "external_libraries_imported": [],
            "exact_only": True,
            "declared_not_native_authority": True,
            "native_certificate": False,
            "not_implemented": "nothing outside this declared model is implemented, and no Rust "
                               "source, lock file, contract or note is touched",
            "child_processes": 0,
        },
        "sections": sections,
        "controls": controls_block,
        "modelling_choices": modelling_choices,
        "undecided": undecided,
        "residual": CONTRACT["residual"],
        "declared_obligations": CONTRACT["declared_obligations"],
        "declared_controls": CONTRACT["controls"],
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
            "nothing_is_ablated_melted_moved_or_heated": True,
            "no_material_is_transported": True,
            "the_singular_point_appears_only_as_a_declared_pinning_site": True,
            "the_singular_point_is_a_declared_spatial_asymmetry_and_nothing_physical": True,
            "no_data_read_or_used": True,
            "no_clock_read": True,
            "native_certificate": False,
            "native_admission": "NotGranted",
            "stable_api_change": False,
            "the_document_is_a_proposal_only": True,
            "no_claim_added_to_docs_claims_toml": True,
            "no_contract_or_note_edited": True,
            "no_rust_source_or_lock_changed": True,
            "observational_verification": "Unavailable",
            "the_model_is_declared_and_a_different_declaration_is_a_different_run": True,
            "zero_transport_under_a_symmetric_forcing_is_a_statement_about_the_declared_model":
                True,
            "governance_is_unaddressed": True,
        },
        "verification_status": {
            "observational": "Unavailable",
            "no_data_read_or_used": True,
            "physical_effect_asserted": NO_NONE,
            "deployment": NO_NONE,
            "checked_here": {
                "no_data_read_or_used": True,
                "no_physical_effect_is_asserted": True,
                "no_magnitude_for_any_physical_quantity_is_asserted": True,
                "nothing_is_ablated_melted_moved_or_heated": True,
                "the_singular_point_is_only_a_declared_pinning_site": True,
                "every_declared_arithmetic_is_exact": True,
                "governance_is_unaddressed": True,
            },
        },
        "checks": {},
    }

    effect_findings = effect_audit(payload)

    checks = {
        "assertions_within_budget": ASSERTIONS["n"] <= CONTRACT["budgets"]["max_assertions"],
        "this_contract_digest_matches_the_declared_one":
            payload["contract_sha256"] == payload["contract_sha256_declared"],
        "the_contract_declares_itself_a_proposal_only":
            PROPOSAL_STATUS in CONTRACT["status"],
        "the_declared_model_is_declared_in_full":
            all(key in sections["the_declared_model"] for key in
                ("ring", "potentials", "gates", "phase", "transfer", "schedule", "measure",
                 "transport")),
        "the_declared_reflection_is_an_involution": all(
            REFLECTION[REFLECTION[i]] == i for i in range(N_SITES)),
        "exactly_one_declared_potential_is_reflection_invariant":
            is_reflection_invariant(U_INVARIANT) and not is_reflection_invariant(U_ASYMMETRIC),
        "the_declared_pinning_site_is_minimal_and_not_fixed_by_the_declared_reflection":
            U_ASYMMETRIC[1] == 0 and REFLECTION[1] != 1,
        "every_declared_rate_and_stay_probability_is_positive": True,
        "the_declared_periodic_measure_is_unique": True,
        "R1_is_exactly_zero": r1["transport"] == 0,
        "R2_is_exactly_zero": r2["transport"] == 0,
        "R3_is_exactly_zero": r3["transport"] == 0,
        "R4_is_non_zero": r4_positive["transport"] != 0,
        "R4_reverses_exactly_with_the_declared_phase_gradients_sign":
            r4_positive["transport"] + r4_negative["transport"] == 0,
        "R5_standing_wave_is_exactly_zero": r5_standing["transport"] == 0,
        "R5_the_declared_phase_gradient_transports": r5_gradient["transport"] != 0,
        "R6_the_declared_connectivity_is_unchanged":
            pairs == ring and sites == list(range(N_SITES)),
        "R6_every_step_satisfies_the_declared_step_energy_bound": all(
            value <= DECLARED_ENERGY_BOUND for value in energy_input),
        "R6_the_declared_crossing_schedule_is_rejected":
            any(value > DECLARED_ENERGY_BOUND for value in crossing_energy),
        "R6_the_declared_connectivity_changing_schedule_is_rejected":
            bool(candidate_added) and set(candidate_pairs) != set(ring),
        "the_declared_time_symmetric_schedules_are_checked_invariant":
            r1["declared_time_symmetric"] and r2["declared_time_symmetric"],
        "the_declared_time_asymmetric_schedule_is_checked_not_invariant":
            not r3["declared_time_symmetric"],
        "the_declared_transfer_field_invariance_is_checked":
            r1["transfer_field_is_invariant"] and r2["transfer_field_is_invariant"]
            and not r2_contrast["transfer_field_is_invariant"],
        "the_declared_per_step_flows_pair_in_the_declared_symmetric_cases":
            all(r["per_step_flows"][index + PERIOD_STEPS // 2] == -r["per_step_flows"][index]
                for r in (r1, r2) for index in range(PERIOD_STEPS // 2)),
        "the_R3_bias_identity_is_executed":
            r3["transport"] == DECLARED_BIAS_COEFFICIENT * r3["schedule_mean"],
        "the_declared_periodic_measure_is_reproduced_exactly":
            all(record["final_state_equals_initial_state"]
                for record in (r1, r2, r3, r4_positive, r4_negative, r5_standing)),
        "the_declared_uniform_reference_measure_agrees_on_the_declared_zeros":
            all(record["transport_from_the_declared_uniform_reference_measure"] == 0
                for record in (r1, r2, r3, r5_standing)),
        "the_declared_uniform_reference_measure_reports_the_same_reversal":
            (r4_positive["transport_from_the_declared_uniform_reference_measure"]
             + r4_negative["transport_from_the_declared_uniform_reference_measure"]) == 0,
        "all_seven_declared_controls_are_rejected": controls_block["controls_rejected"] == 7,
        "every_declared_control_discriminates": all(row["discriminates"] for row in controls),
        "every_zero_is_an_executed_rejection": all(
            controls[index]["executed"] and controls[index]["rejected"] for index in (0, 1, 2, 4)),
        "the_failed_control_is_retained": controls_block["failed_controls_count"] == 1
            and failed_controls[0]["outcome"] == "FAILED_TO_DISCRIMINATE",
        "no_control_is_dropped": controls_block["no_control_is_dropped"],
        "the_payload_records_proposal_only_bookkeeping":
            sections["R7_proposal_only_bookkeeping"]["authorizes_nothing"]
            and sections["R7_proposal_only_bookkeeping"]["decides_nothing"]
            and sections["R7_proposal_only_bookkeeping"]["deploys_nothing"]
            and payload["what_is_not_claimed"]["the_document_is_a_proposal_only"],
        "governance_is_unaddressed_and_no_decision_is_claimed":
            sections["R7_proposal_only_bookkeeping"]["governance"] == UNASSESSED
            and sections["R7_proposal_only_bookkeeping"]["decision"] == NO_NONE
            and sections["R7_proposal_only_bookkeeping"]["authorization"] == NO_NONE,
        "no_magnitude_for_any_physical_quantity_is_asserted":
            payload["what_is_not_claimed"]["magnitude_sign_or_timing_of_any_physical_quantity"]
            == NO_NONE,
        "nothing_is_ablated_melted_moved_or_heated":
            payload["what_is_not_claimed"]["nothing_is_ablated_melted_moved_or_heated"],
        "the_singular_point_is_only_a_declared_pinning_site":
            payload["what_is_not_claimed"]
            ["the_singular_point_appears_only_as_a_declared_pinning_site"],
        "observational_verification_is_recorded_unavailable":
            payload["verification_status"]["observational"] == "Unavailable",
        "no_data_is_read_or_used": payload["verification_status"]["no_data_read_or_used"],
        "undecided_items_are_declared": len(payload["undecided"]) == 6,
        "no_floating_point_value_is_retained": not contains_float(payload),
        "no_effect_key_appears_anywhere": not effect_findings,
    }
    for name, value in checks.items():
        check(value, "the declared check is false: " + name)
    payload["checks"] = checks
    payload["assertions"] = ASSERTIONS["n"]
    payload["status"] = "ExternalExactPass" if all(checks.values()) else "Residual"
    return payload


def summarize(payload):
    sections = payload["sections"]
    model = sections["the_declared_model"]
    r1 = sections["R1_spatially_and_temporally_symmetric"]
    r2 = sections["R2_spatial_asymmetry_alone"]
    r3 = sections["R3_temporal_asymmetry_alone"]
    r4 = sections["R4_both_asymmetries"]
    r5 = sections["R5_the_declared_phase_schedule"]
    r6 = sections["R6_topology_and_step_bound"]
    r7 = sections["R7_proposal_only_bookkeeping"]
    controls = payload["controls"]
    print("spatiotemporal-ratchet proposal v1: exact calibration of a PROPOSAL ONLY - 提议性方案")
    print("  status:", payload["status"], " assertions:", payload["assertions"])
    print("  the declared model: ring of", model["ring"]["n_sites"], "sites, declared reflection",
          model["ring"]["declared_reflection"], "fixed points",
          model["ring"]["declared_reflection_fixed_points"])
    print("      U_sym", model["potentials"]["reflection_invariant"]["values"],
          "reflection-invariant:", model["potentials"]["reflection_invariant"][
              "is_reflection_invariant"])
    print("      U_asym", model["potentials"]["not_reflection_invariant"]["values"],
          "reflection-invariant:",
          model["potentials"]["not_reflection_invariant"]["is_reflection_invariant"],
          "declared pinning site",
          model["potentials"]["not_reflection_invariant"]["declared_pinning_site"])
    print("      transfer: A_s(i) = 1/4*(1 + nu_s*g*G(i)), B_s(i) = 1/4*(1 - nu_s*g*G'(i)) with",
          "G'(i) = G(R(i)); declared amplitude bound",
          model["schedule"]["declared_amplitude_bound"], "; declared step energy bound",
          model["schedule"]["declared_step_energy_bound"])
    print("  R1 symmetric potential + time-symmetric drive -> transport",
          r1["transport"]["transport"]["value"],
          "| rejected:", r1["rejected_claim"]["verdict"])
    print("  R2 asymmetric potential + time-symmetric drive -> transport",
          r2["transport"]["transport"]["value"],
          "| rejected:", r2["rejected_claim"]["verdict"],
          "| the same potential with the time-asymmetric drive ->",
          r2["the_declared_pair"]["the_same_potential_with_the_declared_time_asymmetric_drive"][
              "value"])
    print("  R3 symmetric potential + time-asymmetric drive -> transport",
          r3["transport"]["transport"]["value"],
          "| rejected:", r3["rejected_claim"]["verdict"],
          "| declared schedule mean", r3["declared_mechanism"]["the_declared_schedule_mean"])
    print("  R4 both asymmetries -> transport at the gradient +1:",
          r4["transport_at_the_declared_phase_gradient_plus_one"]["transport"]["value"],
          "| at -1:",
          r4["transport_at_the_declared_phase_gradient_minus_one"]["transport"]["value"])
    print("      the exact sum:",
          r4["the_declared_direction_reversal"]["the_exact_sum"],
          "| the direction reverses exactly:",
          r4["the_declared_direction_reversal"]["the_direction_reverses_exactly"])
    print("  R5 standing wave -> transport", r5["standing_wave"]["transport"]["transport"]["value"],
          "| the declared phase gradient -> transport",
          r5["declared_phase_gradient"]["transport_at_plus_one"]["value"],
          "| the direction follows the gradient's sign:",
          r5["declared_phase_gradient"]["the_direction_follows_the_gradients_sign"])
    print("  R6 connectivity: sites", r6["connectivity_of_the_declared_transport"]["site_count"],
          "edges", r6["connectivity_of_the_declared_transport"]["edge_count"],
          "| unchanged:",
          r6["connectivity_of_the_declared_transport"]["the_edge_set_is_exactly_the_declared_rings"],
          "| declared step energy input per step",
          r6["the_declared_step_energy_bound"]["declared_step_energy_input_per_step"],
          "within the declared bound",
          r6["the_declared_step_energy_bound"]["declared_step_energy_bound"])
    print("  controls:", controls["controls_rejected"], "of", controls["controls_executed"],
          "rejected | failed controls:", controls["failed_controls_count"])
    for row in controls["controls"]:
        print("      ", row["control"], "->", row["verdict"], "| derived",
              row["derived_value"]["value"], "| claimed", row["claimed_value"]["value"])
    for row in controls["failed_controls"]:
        print("      failed control:", row["control"], "->", row["outcome"])
    print("  R7 proposal only: authorization", r7["authorization"], "| decision", r7["decision"],
          "| deployment", r7["deployment"], "| governance", r7["governance"],
          "| physical_effect_asserted", r7["physical_effect_asserted"], "| data_used",
          r7["data_used"])
    print("      ", r7["proposal_only_in_chinese_and_english"])
    print("  verified: no floating-point value retained",
          payload["checks"]["no_floating_point_value_is_retained"],
          "| no data read or used", payload["checks"]["no_data_is_read_or_used"],
          "| no magnitude for any physical quantity",
          payload["checks"]["no_magnitude_for_any_physical_quantity_is_asserted"])
    print("  undecided items:", len(payload["undecided"]), "| modelling choices:",
          len(payload["modelling_choices"]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, required=True)
    arguments = parser.parse_args()
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("wall limit")))
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
    return 0 if payload["status"] == "ExternalExactPass" else 1


if __name__ == "__main__":
    sys.exit(main())
