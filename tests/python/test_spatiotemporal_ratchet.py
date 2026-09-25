"""The paired test for the spatiotemporal-ratchet proposal v1 exact calibration.

The assertions here are about what the retained checker decided by exact arithmetic on a PROPOSAL
ONLY document - 提议性方案: one declared discrete model on a declared ring of six declared sites,
with a declared reflection, two declared potentials (one invariant under that reflection and one
not), a declared gate array read from the declared potential's slope signs, a declared phase
gradient in {-1, 0, +1}, a declared schedule of four declared signed amplitudes with a declared
step energy bound, a declared stochastic transfer per step, a declared periodic measure and a
declared transport computed as the accumulated declared flow.

They are not claims about any physical object.  Nothing is ablated, melted, moved or heated, no
magnitude, sign or timing is asserted for any physical quantity, no data is read or used, and the
wider programme's 'singular point' appears only as the declared pinning site of the declared
potential, that is as a declared spatial asymmetry.  The test checks that absence in the retained
payload.

The checker is invoked without `-S`; it imports nothing beyond the standard library, so the run is
an external exact calibration with no host package in the path.  Every declared transport value is
recomputed here from the payload's own declared parameters - the declared ring, the declared
reflection, the declared potentials, the declared gate value, the declared transfer step and the
declared schedules - by this test's own exact arithmetic, so the numbers are checked twice: once
by the checker and once here, independently.

The record carries no claim for this run: the parent session adds the claim to `docs/claims.toml`
with its note, so the last test asserts the claim is ABSENT rather than dropping the binding.
"""

import hashlib
import json
import shutil
import subprocess
import sys
import tomllib
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/spatiotemporal_ratchet_v1"
CHECKER = HERE / "calibration.py"
CONTRACT = HERE / "contract.json"
EVIDENCE = HERE / "evidence.json"

CLAIM_ID = "adva.bounded-experiment.spatiotemporal-ratchet.v0"
DECLARED_CONTRACT_SHA256 = "9c495906eee86e6bfaa5eb39c88ea8b7cc9048f86bec574e458e413626a9963c"

SCHEMA = "adva.external.spatiotemporal-ratchet-proposal-calibration.v1"
PROPOSAL_STATUS = "PROPOSAL ONLY - 提议性方案"
NO_NONE = "none"
UNASSESSED = "unaddressed"
NO_DATA = "none"
TRANSPORT_UNIT = "declared sites of net displacement per declared period"
FROZEN_ASSERTION_COUNT = 400
FROZEN_CHECK_COUNT = 43

N_SITES = 6
REFLECTION = (0, 5, 4, 3, 2, 1)
EPSILON = Fraction(1, 4)
DELTA_GATE = Fraction(1, 2)
PERIOD_STEPS = 4
DECLARED_ENERGY_UNIT = 4
DECLARED_ENERGY_BOUND = Fraction(2)
DECLARED_BIAS_COEFFICIENT = Fraction(3, 8)
U_INVARIANT = (2, 0, 1, 2, 1, 0)
U_ASYMMETRIC = (3, 0, 1, 2, 3, 2)
S_TIME_SYMMETRIC = (Fraction(1, 2), Fraction(0), Fraction(-1, 2), Fraction(0))
S_TIME_ASYMMETRIC = (Fraction(1, 2), Fraction(1, 4), Fraction(-1, 4), Fraction(-1, 2))
S_CROSSING_THE_BOUND = (Fraction(1, 2), Fraction(3, 4), Fraction(-1, 4), Fraction(-1, 2))
RING_EDGES = [(0, 1), (0, 5), (1, 2), (2, 3), (3, 4), (4, 5)]

R1_TRANSPORT = "0"
R1_FLOWS = ["3/16", "0", "-3/16", "0"]
R1_MEASURE = ["1/6", "1/6", "1/6", "1/6", "1/6", "1/6"]
R2_TRANSPORT = "0"
R2_FLOWS = ["935803/5613188", "0", "-935803/5613188", "0"]
R2_MEASURE = ["469939/2806594", "232612/1403297", "456117/2806594", "465365/2806594",
              "477241/2806594", "236354/1403297"]
R3_TRANSPORT = "0"
R3_FLOWS = ["3/16", "3/32", "-3/32", "-3/16"]
TRANSPORTING = "-2395373021828541/130893752065903472383"
R4_FLOWS = ["174609731747765250467/1047150016527227779064",
            "174479262821679451859/2094300033054455558128",
            "-174631454117461009859/2094300033054455558128",
            "-174552799084049099795/1047150016527227779064"]
R4_MEASURE = ["21959524069668552070/130893752065903472383",
              "21895605129088038625/130893752065903472383",
              "20337614820072238738/130893752065903472383",
              "21713511383313828403/130893752065903472383",
              "23175296404314213290/130893752065903472383",
              "21812200259446601257/130893752065903472383"]
R4_UNIFORM_TRANSPORT = "1/32768"
R5_STANDING_TRANSPORT = "0"

SECTION_NAMES = (
    "R1_spatially_and_temporally_symmetric", "R2_spatial_asymmetry_alone",
    "R3_temporal_asymmetry_alone", "R4_both_asymmetries",
    "R5_the_declared_phase_schedule", "R6_topology_and_step_bound",
    "R7_proposal_only_bookkeeping", "the_declared_model",
)

TOP_LEVEL_KEYS = (
    "assertions", "checker_sha256", "checks", "contract", "contract_sha256",
    "contract_sha256_declared", "contract_status", "controls", "declared_controls",
    "declared_obligations", "level", "limits", "modelling_choices", "question", "residual",
    "schema", "sections", "status", "tooling", "undecided", "verification_status", "version",
    "what_is_not_claimed",
)

FROZEN_SECTION_SHAPE = {
    "the_declared_model": [
        "gates", "measure", "phase", "potentials", "ring", "schedule", "statement", "transfer",
        "transport",
    ],
    "R1_spatially_and_temporally_symmetric": [
        "configuration", "declared_mechanism", "reading", "rejected_claim", "requirement",
        "transport", "verdict",
    ],
    "R2_spatial_asymmetry_alone": [
        "configuration", "declared_mechanism", "reading", "rejected_claim", "requirement",
        "the_declared_pair", "transport", "verdict",
    ],
    "R3_temporal_asymmetry_alone": [
        "configuration", "declared_mechanism", "reading", "rejected_claim", "requirement",
        "the_declared_contrast", "transport", "verdict",
    ],
    "R4_both_asymmetries": [
        "configuration", "declared_mechanism", "reading", "rejected_claim", "requirement",
        "the_declared_direction_reversal", "transport_at_the_declared_phase_gradient_minus_one",
        "transport_at_the_declared_phase_gradient_plus_one", "verdict",
    ],
    "R5_the_declared_phase_schedule": [
        "declared_phase_gradient", "reading", "requirement", "standing_wave", "verdict",
    ],
    "R6_topology_and_step_bound": [
        "connectivity_of_the_declared_transport", "declared_ring", "reading",
        "rejected_claim_changing_the_connectivity",
        "rejected_claim_crossing_the_declared_step_energy_bound", "requirement",
        "the_declared_step_energy_bound", "verdict",
    ],
    "R7_proposal_only_bookkeeping": [
        "authorization", "authorizes_nothing", "data_used", "decides_nothing", "decision",
        "deployment", "deploys_nothing", "governance", "no_governance_assessment",
        "nothing_said_about_who_might_decide", "physical_effect_asserted",
        "proposal_only_in_chinese_and_english", "proposal_only_statement", "record_purpose",
        "status", "the_question_is_declared_and_nothing_else",
    ],
}

FROZEN_TRANSPORT_BLOCK_KEYS = [
    "declared_measure", "final_minus_initial", "final_state_equals_initial_state",
    "per_step_flows", "periodic_measure", "periodic_measure_is_uniform",
    "the_two_declared_readings_agree_on_zero", "transport",
    "transport_from_the_declared_uniform_reference_measure", "transport_is_zero",
]

CONTROL_ROW_KEYS = (
    "accepted_companion", "claim", "claimed_value", "control", "derived_value", "discriminates",
    "executed", "rejected", "rejected_by", "rejection_reasons", "unit", "verdict",
)

FORBIDDEN_EFFECT_KEYS = (
    "effect", "physical_effect", "temperature", "forcing", "flux", "power", "heat", "melt",
    "melting", "ablation", "ice", "water", "atmosphere", "ocean", "cloud", "weather", "climate",
    "warming", "cooling", "albedo", "damage", "benefit", "yield", "anomaly", "tendency",
    "sensitivity", "forecast", "joule", "kelvin", "watt", "brownian",
)

FORBIDDEN_TIME_KEYS = ("timestamp", "created_at", "started_at", "finished_at", "elapsed",
                       "duration", "elapsed_seconds", "wall_clock")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    """Load JSON and refuse any floating-point literal in it."""
    def no_float(text):
        raise AssertionError(f"a floating-point literal is present: {text}")

    return json.loads(Path(path).read_text(encoding="utf-8"), parse_float=no_float)


def invoke(checker, output, timeout=900):
    return subprocess.run(
        [sys.executable, str(checker), "--output", str(output)],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def section(name):
    return load(EVIDENCE)["sections"][name]


def declared_model():
    return section("the_declared_model")


def key_findings(node, keys, path="", found=None):
    """Every key anywhere under a record that is one of the declared forbidden keys."""
    if found is None:
        found = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key in keys:
                found.append(path + "/" + str(key))
            key_findings(value, keys, path + "/" + str(key), found)
    elif isinstance(node, (list, tuple)):
        for index, item in enumerate(node):
            key_findings(item, keys, path + "/" + str(index), found)
    return found


# ------------------------------------------------- this test's own model arithmetic --
# The functions below re-implement the declared model from the payload's own declared parameters
# and compute the declared transport independently of the checker.


def payload_parameters():
    """The declared parameters of the declared model, read from the retained payload."""
    model = declared_model()
    return {
        "n": model["ring"]["n_sites"],
        "reflection": [int(value) for value in model["ring"]["declared_reflection"]],
        "epsilon": Fraction(model["transfer"]["epsilon"]),
        "delta_gate": Fraction(model["gates"]["declared_value_for_an_uphill_move"]),
        "period_steps": model["schedule"]["period_steps"],
        "schedules": {
            name: [Fraction(value) for value in row["amplitudes"]]
            for name, row in model["schedule"]["schedules"].items()
        },
        "potentials": {
            name: tuple(int(value) for value in row["values"])
            for name, row in model["potentials"].items()
        },
    }


def recompute_transport(potential, amplitudes, gradient):
    """The declared transport of one declared configuration, computed here from the payload's own
    declared parameters with this test's own exact arithmetic."""
    parameters = payload_parameters()
    n = parameters["n"]
    reflection = parameters["reflection"]
    epsilon = parameters["epsilon"]
    delta = parameters["delta_gate"]
    right = [Fraction(1) if potential[(i + 1) % n] <= potential[i] else delta for i in range(n)]
    left = [right[reflection[i]] for i in range(n)]
    steps = []
    for amplitude in amplitudes:
        steps.append((
            [epsilon * (1 + amplitude * gradient * right[i]) for i in range(n)],
            [epsilon * (1 - amplitude * gradient * left[i]) for i in range(n)],
        ))
    for hop_right, hop_left in steps:
        assert all(rate > 0 for rate in hop_right + hop_left)
        assert all(hop_right[i] + hop_left[i] <= 1 for i in range(n))

    matrices = []
    for hop_right, hop_left in steps:
        matrix = [[Fraction(0)] * n for _ in range(n)]
        for i in range(n):
            matrix[i][i] += 1 - hop_right[i] - hop_left[i]
            matrix[(i + 1) % n][i] += hop_right[i]
            matrix[(i - 1) % n][i] += hop_left[i]
        matrices.append(matrix)
    period = [[Fraction(1) if i == j else Fraction(0) for i in range(n)] for j in range(n)]
    for matrix in matrices:
        period = [
            [sum(matrix[k][j] * period[j][i] for j in range(n)) for i in range(n)]
            for k in range(n)
        ]
    rows = [[period[j][i] - (Fraction(1) if i == j else Fraction(0)) for i in range(n)]
            for j in range(n)]
    rhs = [Fraction(0)] * n
    rows[n - 1] = [Fraction(1)] * n
    rhs[n - 1] = Fraction(1)
    for column in range(n):
        pivot = next(row for row in range(column, n) if rows[row][column] != 0)
        rows[column], rows[pivot] = rows[pivot], rows[column]
        rhs[column], rhs[pivot] = rhs[pivot], rhs[column]
        inverse = rows[column][column]
        rows[column] = [value / inverse for value in rows[column]]
        rhs[column] = rhs[column] / inverse
        for row in range(n):
            if row != column and rows[row][column] != 0:
                factor = rows[row][column]
                rows[row] = [rows[row][k] - factor * rows[column][k] for k in range(n)]
                rhs[row] = rhs[row] - factor * rhs[column]
    measure = list(rhs)
    assert sum(measure) == 1

    flows = []
    for hop_right, hop_left in steps:
        flows.append(sum((hop_right[i] - hop_left[i]) * measure[i] for i in range(n)))
        following = [Fraction(0)] * n
        for j in range(n):
            following[j] += measure[j] * (1 - hop_right[j] - hop_left[j])
            following[j] += measure[(j - 1) % n] * hop_right[(j - 1) % n]
            following[j] += measure[(j + 1) % n] * hop_left[(j + 1) % n]
        measure = following
    return sum(flows), flows


def payload_transport(name, sub="transport"):
    return Fraction(section(name)[sub]["transport"]["value"])


def payload_flows(name, sub="transport"):
    return [Fraction(row["value"]) for row in section(name)[sub]["per_step_flows"]]


def payload_measure(name, sub="transport"):
    return [Fraction(value) for value in section(name)[sub]["periodic_measure"]]


# ---------------------------------------------------------------------------- tests --


def test_retained_evidence_is_an_external_pass_inside_the_contract():
    report = load(EVIDENCE)
    contract = load(CONTRACT)
    assert report["status"] == "ExternalExactPass"
    assert report["schema"] == SCHEMA
    assert report["version"] == 1
    assert report["checker_sha256"] == digest(CHECKER)
    assert report["contract"] == "experiments/spatiotemporal_ratchet_v1/contract.json"
    assert report["contract_sha256"] == digest(CONTRACT) == DECLARED_CONTRACT_SHA256
    assert report["contract_sha256_declared"] == DECLARED_CONTRACT_SHA256
    assert PROPOSAL_STATUS in report["contract_status"]
    assert report["assertions"] == FROZEN_ASSERTION_COUNT
    assert report["assertions"] <= contract["budgets"]["max_assertions"]
    assert report["limits"] == contract["budgets"]
    assert contract["budgets"]["child_processes"] == 0
    assert contract["budgets"]["routes"] == 1
    assert all(report["checks"].values())
    assert len(report["checks"]) == FROZEN_CHECK_COUNT
    assert report["level"] == contract["level"]
    assert report["question"] == contract["question"]
    assert report["residual"] == contract["residual"]
    assert report["declared_obligations"] == contract["declared_obligations"]
    assert report["declared_controls"] == contract["controls"]
    assert report["tooling"]["declared_not_native_authority"] is True
    assert report["tooling"]["exact_only"] is True
    assert report["tooling"]["external_libraries_imported"] == []
    assert report["tooling"]["not_implemented"]
    assert report["tooling"]["child_processes"] == 0
    assert "RLIMIT_AS" not in CHECKER.read_text(encoding="utf-8")
    assert "RLIMIT_CPU" in CHECKER.read_text(encoding="utf-8")
    assert "RLIMIT_FSIZE" in CHECKER.read_text(encoding="utf-8")
    assert "signal.alarm" in CHECKER.read_text(encoding="utf-8")


def test_the_declared_model_is_declared_in_full():
    model = declared_model()
    assert model["ring"]["n_sites"] == N_SITES
    assert model["ring"]["site_labels"] == [str(i) for i in range(N_SITES)]
    assert model["ring"]["declared_edge_count"] == N_SITES
    assert model["ring"]["declared_edge_set"] == [list(edge) for edge in RING_EDGES]
    assert model["ring"]["declared_adjacent_pairs"] == [[i, (i + 1) % N_SITES]
                                                        for i in range(N_SITES)]
    assert model["ring"]["declared_reflection"] == [str(value) for value in REFLECTION]
    assert model["ring"]["declared_reflection_fixed_points"] == ["0", "3"]
    assert model["ring"]["the_reflection_is_an_involution"] is True
    assert all(REFLECTION[REFLECTION[i]] == i for i in range(N_SITES))

    invariant = model["potentials"]["reflection_invariant"]
    asymmetric = model["potentials"]["not_reflection_invariant"]
    assert invariant["values"] == [str(value) for value in U_INVARIANT]
    assert invariant["is_reflection_invariant"] is True
    assert all(U_INVARIANT[REFLECTION[i]] == U_INVARIANT[i] for i in range(N_SITES))
    assert asymmetric["values"] == [str(value) for value in U_ASYMMETRIC]
    assert asymmetric["is_reflection_invariant"] is False
    assert not all(U_ASYMMETRIC[REFLECTION[i]] == U_ASYMMETRIC[i] for i in range(N_SITES))
    assert asymmetric["declared_pinning_site"] == "1"
    assert asymmetric["the_pinning_site_is_minimal"] is True
    assert U_ASYMMETRIC[1] == min(U_ASYMMETRIC)
    assert asymmetric["the_pinning_site_is_a_fixed_point_of_the_declared_reflection"] is False
    assert REFLECTION[1] != 1

    gates = model["gates"]
    assert Fraction(gates["declared_value_for_an_uphill_move"]) == DELTA_GATE
    assert gates["the_gates_read_only_the_declared_slope_signs"] is True
    assert gates["for_the_asymmetric_potential"]["rightward"] == [
        "1", "1/2", "1/2", "1/2", "1", "1/2"]
    assert gates["for_the_asymmetric_potential"]["leftward"] == [
        "1", "1/2", "1", "1/2", "1/2", "1/2"]
    assert gates["for_the_reflection_invariant_potential"]["rightward"] == [
        "1", "1/2", "1/2", "1", "1", "1/2"]
    assert "G'(i) = G(R(i))" in gates["leftward_convention"]

    phase = model["phase"]
    assert phase["declared_phase_gradient_values"] == ["1", "0", "-1"]
    assert phase["the_standing_wave_gradient"] == "0"
    assert "constant across the ring" in phase["the_standing_wave_statement"]
    assert phase["the_gradient_fixes_the_declared_direction"] is True

    transfer = model["transfer"]
    assert Fraction(transfer["epsilon"]) == EPSILON
    assert "A_s(i)" in transfer["rule"] and "B_s(i)" in transfer["rule"]
    assert transfer["every_declared_rate_is_positive"] is True
    assert transfer["every_declared_stay_probability_is_positive"] is True

    schedule = model["schedule"]
    assert schedule["period_steps"] == PERIOD_STEPS
    assert Fraction(schedule["declared_amplitude_bound"]) == Fraction(1, 2)
    assert Fraction(schedule["declared_energy_unit"]) == DECLARED_ENERGY_UNIT
    assert Fraction(schedule["declared_step_energy_bound"]) == DECLARED_ENERGY_BOUND
    assert sorted(schedule["schedules"]) == [
        "crossing_the_declared_step_energy_bound", "time_asymmetric", "time_symmetric"]
    assert schedule["schedules"]["time_symmetric"]["amplitudes"] == [
        str(value) for value in S_TIME_SYMMETRIC]
    assert schedule["schedules"]["time_asymmetric"]["amplitudes"] == [
        str(value) for value in S_TIME_ASYMMETRIC]
    assert schedule["schedules"]["time_symmetric"]["declared_time_symmetric"] is True
    assert schedule["schedules"]["time_asymmetric"]["declared_time_symmetric"] is False
    assert schedule["schedules"]["time_asymmetric"]["schedule_mean"] == "0"
    assert "nu_{s+T/2} = -nu_s" in schedule["the_declared_time_symmetry_rule"]


def test_the_declared_gates_follow_the_declared_rule():
    """The declared gates are recomputed here from the payload's own declared potentials."""
    model = declared_model()
    delta = Fraction(model["gates"]["declared_value_for_an_uphill_move"])
    reflection = [int(value) for value in model["ring"]["declared_reflection"]]
    for key, potential in (("for_the_reflection_invariant_potential", U_INVARIANT),
                           ("for_the_asymmetric_potential", U_ASYMMETRIC)):
        right = [Fraction(1) if potential[(i + 1) % N_SITES] <= potential[i] else delta
                 for i in range(N_SITES)]
        left = [right[reflection[i]] for i in range(N_SITES)]
        assert model["gates"][key]["rightward"] == [str(value) for value in right]
        assert model["gates"][key]["leftward"] == [str(value) for value in left]


def test_the_declared_transport_values_are_recomputed_here():
    """Every declared R1 to R5 transport is recomputed independently from the payload's own
    declared model parameters, by this test's own exact arithmetic."""
    parameters = payload_parameters()
    assert parameters["n"] == N_SITES
    assert parameters["reflection"] == list(REFLECTION)
    assert parameters["epsilon"] == EPSILON
    assert parameters["delta_gate"] == DELTA_GATE
    assert parameters["period_steps"] == PERIOD_STEPS
    assert parameters["potentials"]["reflection_invariant"] == U_INVARIANT
    assert parameters["potentials"]["not_reflection_invariant"] == U_ASYMMETRIC
    schedules = parameters["schedules"]
    assert schedules["time_symmetric"] == list(S_TIME_SYMMETRIC)
    assert schedules["time_asymmetric"] == list(S_TIME_ASYMMETRIC)
    assert schedules["crossing_the_declared_step_energy_bound"] == list(S_CROSSING_THE_BOUND)

    for potential in (U_INVARIANT, U_ASYMMETRIC):
        for amplitudes in (S_TIME_SYMMETRIC, S_TIME_ASYMMETRIC):
            for gradient in (1, 0, -1):
                transport, flows = recompute_transport(potential, amplitudes, gradient)
                assert sum(flows) == transport

    r1_transport, r1_flows = recompute_transport(U_INVARIANT, S_TIME_SYMMETRIC, 1)
    assert r1_transport == payload_transport("R1_spatially_and_temporally_symmetric") == 0
    assert r1_flows == payload_flows("R1_spatially_and_temporally_symmetric")
    assert [str(value) for value in r1_flows] == R1_FLOWS

    r2_transport, r2_flows = recompute_transport(U_ASYMMETRIC, S_TIME_SYMMETRIC, 1)
    assert r2_transport == payload_transport("R2_spatial_asymmetry_alone") == 0
    assert r2_flows == payload_flows("R2_spatial_asymmetry_alone")
    assert [str(value) for value in r2_flows] == R2_FLOWS

    r3_transport, r3_flows = recompute_transport(U_INVARIANT, S_TIME_ASYMMETRIC, 1)
    assert r3_transport == payload_transport("R3_temporal_asymmetry_alone") == 0
    assert r3_flows == payload_flows("R3_temporal_asymmetry_alone")
    assert [str(value) for value in r3_flows] == R3_FLOWS

    r4_plus, r4_plus_flows = recompute_transport(U_ASYMMETRIC, S_TIME_ASYMMETRIC, 1)
    r4_minus, r4_minus_flows = recompute_transport(U_ASYMMETRIC, S_TIME_ASYMMETRIC, -1)
    assert r4_plus == payload_transport("R4_both_asymmetries",
                                        "transport_at_the_declared_phase_gradient_plus_one")
    assert r4_minus == payload_transport("R4_both_asymmetries",
                                         "transport_at_the_declared_phase_gradient_minus_one")
    assert r4_plus_flows == payload_flows("R4_both_asymmetries",
                                          "transport_at_the_declared_phase_gradient_plus_one")
    assert r4_minus_flows == payload_flows("R4_both_asymmetries",
                                           "transport_at_the_declared_phase_gradient_minus_one")
    assert r4_plus == Fraction(TRANSPORTING)
    assert r4_minus == -Fraction(TRANSPORTING)
    assert [str(value) for value in r4_plus_flows] == R4_FLOWS
    assert r4_plus + r4_minus == 0
    assert r4_plus != 0

    r5_standing, r5_standing_flows = recompute_transport(U_ASYMMETRIC, S_TIME_ASYMMETRIC, 0)
    standing_block = section("R5_the_declared_phase_schedule")["standing_wave"]["transport"]
    assert r5_standing == Fraction(standing_block["transport"]["value"]) == 0
    assert r5_standing_flows == [Fraction(row["value"])
                                 for row in standing_block["per_step_flows"]]
    assert all(value == 0 for value in r5_standing_flows)
    r5_gradient, _ = recompute_transport(U_ASYMMETRIC, S_TIME_ASYMMETRIC, 1)
    assert r5_gradient == Fraction(
        section("R5_the_declared_phase_schedule")["declared_phase_gradient"]
        ["transport_at_plus_one"]["value"]) == r4_plus


def test_the_declared_periodic_measures_are_recomputed_here():
    """The declared periodic measures are recomputed here as well, so the declared transport is
    checked against a measure this test derived itself."""
    parameters = payload_parameters()
    for name, potential, amplitudes, gradient in (
        ("R1_spatially_and_temporally_symmetric", U_INVARIANT, S_TIME_SYMMETRIC, 1),
        ("R2_spatial_asymmetry_alone", U_ASYMMETRIC, S_TIME_SYMMETRIC, 1),
        ("R3_temporal_asymmetry_alone", U_INVARIANT, S_TIME_ASYMMETRIC, 1),
        ("R4_both_asymmetries", U_ASYMMETRIC, S_TIME_ASYMMETRIC, 1),
    ):
        sub = ("transport_at_the_declared_phase_gradient_plus_one"
               if name == "R4_both_asymmetries" else "transport")
        transport, flows = recompute_transport(potential, amplitudes, gradient)
        assert transport == payload_transport(name, sub)
        assert flows == payload_flows(name, sub)
        assert parameters["n"] == len(payload_measure(name, sub))
        assert all(value > 0 for value in payload_measure(name, sub))
        assert sum(payload_measure(name, sub)) == 1


def test_R1_R2_and_R3_are_exactly_zero_and_each_claim_is_rejected():
    r1 = section("R1_spatially_and_temporally_symmetric")
    r2 = section("R2_spatial_asymmetry_alone")
    r3 = section("R3_temporal_asymmetry_alone")
    for row in (r1, r2, r3):
        assert row["transport"]["transport"]["value"] == "0"
        assert row["transport"]["transport_is_zero"] is True
        assert row["transport"]["transport"]["unit"] == TRANSPORT_UNIT
        assert row["transport"]["transport"]["between_the_exact_integers"] == ["0", "1"]
        assert row["transport"]["final_state_equals_initial_state"] is True
        assert row["transport"]["final_minus_initial"] == ["0"] * N_SITES
        assert row["transport"]["transport_from_the_declared_uniform_reference_measure"]["value"] \
            == "0"
        assert row["transport"]["the_two_declared_readings_agree_on_zero"] is True
        rejected = row["rejected_claim"]
        assert rejected["executed"] is True
        assert rejected["rejected"] is True
        assert rejected["verdict"] == "Rejected"
        assert rejected["discriminates"] is True
        assert Fraction(rejected["derived_value"]["value"]) == 0
        assert Fraction(rejected["claimed_value"]["value"]) != 0
        assert rejected["rejection_reasons"]
        assert rejected["accepted_companion"]["accepted"] is True
        assert row["verdict"] == "Rejected"

    assert r1["configuration"]["schedule_is_declared_time_symmetric"] is True
    assert r2["configuration"]["schedule_is_declared_time_symmetric"] is True
    assert r3["configuration"]["schedule_is_declared_time_symmetric"] is False
    assert r1["declared_mechanism"]["the_declared_transfer_field_is_invariant"] is True
    assert r2["declared_mechanism"]["the_declared_transfer_field_is_invariant"] is True
    assert r2["declared_mechanism"]["the_declared_per_step_flows_pair"] is True
    assert r2["declared_mechanism"]["the_declared_measure_is_not_the_declared_uniform_measure"] \
        is True
    assert r3["declared_mechanism"]["the_declared_schedule_mean"] == "0"
    assert Fraction(r3["declared_mechanism"]["the_declared_bias_coefficient"]) \
        == DECLARED_BIAS_COEFFICIENT
    assert Fraction(r3["declared_mechanism"]["the_declared_bias_coefficient"]) \
        == payload_flows("R1_spatially_and_temporally_symmetric")[0] / S_TIME_SYMMETRIC[0]
    assert r3["declared_mechanism"][
        "every_declared_per_step_flow_is_the_declared_bias_coefficient_times_that_steps_declared_"
        "amplitude"] is True
    assert r1["transport"]["periodic_measure"] == R1_MEASURE
    assert r1["transport"]["periodic_measure_is_uniform"] is True
    assert r2["transport"]["periodic_measure"] == R2_MEASURE
    assert r2["transport"]["periodic_measure_is_uniform"] is False
    assert [row["value"] for row in r2["transport"]["per_step_flows"]] == R2_FLOWS
    assert [row["value"] for row in r3["transport"]["per_step_flows"]] == R3_FLOWS
    for row in (r1, r2):
        flows = [Fraction(flow["value"]) for flow in row["transport"]["per_step_flows"]]
        assert flows[0] == -flows[PERIOD_STEPS // 2]
        assert flows[0] != 0

    pair = r2["the_declared_pair"]
    assert pair["the_potential_is_held_fixed"] is True
    assert pair["the_pair_discriminates"] is True
    assert Fraction(pair["the_same_potential_with_the_declared_time_asymmetric_drive"]["value"]) \
        == Fraction(TRANSPORTING)
    contrast = r3["the_declared_contrast"]
    assert contrast["the_schedule_is_held_fixed"] is True
    assert contrast["the_contrast_discriminates"] is True
    assert Fraction(
        contrast["the_same_schedule_with_the_declared_asymmetric_potential"]["value"]) != 0


def test_R4_is_non_zero_and_reverses_exactly_with_the_declared_phase_gradient():
    r4 = section("R4_both_asymmetries")
    plus = r4["transport_at_the_declared_phase_gradient_plus_one"]
    minus = r4["transport_at_the_declared_phase_gradient_minus_one"]
    assert sorted(plus) == sorted(FROZEN_TRANSPORT_BLOCK_KEYS)
    assert sorted(minus) == sorted(FROZEN_TRANSPORT_BLOCK_KEYS)
    assert Fraction(plus["transport"]["value"]) == Fraction(TRANSPORTING)
    assert Fraction(minus["transport"]["value"]) == -Fraction(TRANSPORTING)
    assert plus["transport_is_zero"] is False
    assert minus["transport_is_zero"] is False
    assert plus["periodic_measure"] == R4_MEASURE
    assert minus["periodic_measure"] == [plus["periodic_measure"][REFLECTION[i]]
                                        for i in range(N_SITES)]
    assert [row["value"] for row in plus["per_step_flows"]] == R4_FLOWS
    assert Fraction(plus["transport_from_the_declared_uniform_reference_measure"]["value"]) \
        == Fraction(R4_UNIFORM_TRANSPORT)
    assert Fraction(minus["transport_from_the_declared_uniform_reference_measure"]["value"]) \
        == -Fraction(R4_UNIFORM_TRANSPORT)
    assert plus["final_state_equals_initial_state"] is True
    assert minus["final_state_equals_initial_state"] is True

    reversal = r4["the_declared_direction_reversal"]
    assert reversal["the_exact_sum"] == "0"
    assert reversal["the_sum_is_exactly_zero"] is True
    assert reversal["the_direction_reverses_exactly"] is True
    assert reversal["the_same_reversal_on_the_declared_uniform_reference_measure"] is True
    assert Fraction(reversal["transport_at_plus_one"]) \
        + Fraction(reversal["transport_at_minus_one"]) == 0
    assert r4["declared_mechanism"]["the_declared_transport_is_non_zero"] is True
    assert r4["declared_mechanism"]["the_declared_transfer_field_is_invariant"] is False
    assert r4["configuration"]["schedule_is_declared_time_symmetric"] is False
    rejected = r4["rejected_claim"]
    assert rejected["rejected"] is True
    assert rejected["verdict"] == "Rejected"
    assert rejected["discriminates"] is True
    assert Fraction(rejected["claimed_value"]["value"]) \
        == Fraction(reversal["transport_at_plus_one"])
    assert Fraction(rejected["derived_value"]["value"]) \
        == Fraction(reversal["transport_at_minus_one"])
    assert "sum to exactly zero" in rejected["rejection_reasons"][0]
    assert r4["verdict"] == "Accepted"


def test_R5_standing_wave_is_zero_and_the_declared_gradient_transports():
    r5 = section("R5_the_declared_phase_schedule")
    standing = r5["standing_wave"]
    assert standing["declared_phase_gradient"] == "0"
    assert standing["transport"]["transport"]["value"] == R5_STANDING_TRANSPORT
    assert standing["transport"]["transport_is_zero"] is True
    assert [row["value"] for row in standing["transport"]["per_step_flows"]] == ["0"] * 4
    assert standing["transport"]["periodic_measure_is_uniform"] is True
    assert standing["transport"]["periodic_measure"] == R1_MEASURE
    assert standing["transport"]["transport_from_the_declared_uniform_reference_measure"]["value"]\
        == "0"
    assert standing["the_declared_phase_is_constant_across_the_ring"] is True
    assert standing["the_declared_transfer_is_the_declared_uniform_diffusion"] is True
    assert standing["rejected_claim"]["rejected"] is True
    assert standing["rejected_claim"]["verdict"] == "Rejected"
    assert Fraction(standing["rejected_claim"]["claimed_value"]["value"]) != 0
    assert standing["verdict"] == "Rejected"

    gradient = r5["declared_phase_gradient"]
    assert gradient["declared_phase_gradients"] == ["1", "-1"]
    assert Fraction(gradient["transport_at_plus_one"]["value"]) == Fraction(TRANSPORTING)
    assert Fraction(gradient["transport_at_minus_one"]["value"]) == -Fraction(TRANSPORTING)
    assert gradient["the_direction_follows_the_gradients_sign"] is True
    assert gradient["the_exact_sum"] == "0"
    assert gradient["verdict"] == "Accepted"
    assert r5["verdict"] == "RejectedForTheStandingWaveAcceptedForTheGradient"
    assert r5["standing_wave"]["transport"]["transport"]["value"] \
        != gradient["transport_at_plus_one"]["value"]


def test_R6_connectivity_and_the_declared_step_energy_bound():
    r6 = section("R6_topology_and_step_bound")
    ring = r6["declared_ring"]
    connectivity = r6["connectivity_of_the_declared_transport"]
    assert ring["n_sites"] == N_SITES
    assert ring["declared_edge_count"] == "6"
    assert ring["declared_edge_set"] == [list(edge) for edge in RING_EDGES]
    assert connectivity["sites_reached"] == [str(i) for i in range(N_SITES)]
    assert connectivity["site_count"] == "6"
    assert connectivity["no_site_is_lost"] is True
    assert connectivity["edge_set_of_the_declared_transport"] == [list(edge) for edge in RING_EDGES]
    assert connectivity["edge_count"] == "6"
    assert connectivity["the_edge_set_is_exactly_the_declared_rings"] is True
    assert connectivity["no_edge_is_added_or_removed"] is True
    assert connectivity["every_edge_carries_positive_declared_flow_in_both_directions"] is True

    bound = r6["the_declared_step_energy_bound"]
    assert Fraction(bound["declared_energy_unit"]) == DECLARED_ENERGY_UNIT
    assert Fraction(bound["declared_step_energy_bound"]) == DECLARED_ENERGY_BOUND
    assert bound["declared_step_energy_input_per_step"] == ["2", "1", "1", "2"]
    assert bound["every_step_satisfies_the_declared_bound"] is True
    assert bound["the_declared_schedule_reaches_the_bound"] is True
    assert bound["the_declared_step_energy_input_is_a_declared_model_number_with_no_physical_"
                 "magnitude"] is True
    for value, amplitude in zip(bound["declared_step_energy_input_per_step"], S_TIME_ASYMMETRIC,
                                strict=True):
        assert Fraction(value) == DECLARED_ENERGY_UNIT * abs(amplitude)
        assert Fraction(value) <= DECLARED_ENERGY_BOUND

    crossing = r6["rejected_claim_crossing_the_declared_step_energy_bound"]
    assert crossing["rejected"] is True
    assert crossing["verdict"] == "Rejected"
    assert Fraction(crossing["derived_value"]["value"]) > DECLARED_ENERGY_BOUND
    assert Fraction(crossing["claimed_value"]["value"]) == DECLARED_ENERGY_BOUND
    connectivity_claim = r6["rejected_claim_changing_the_connectivity"]
    assert connectivity_claim["rejected"] is True
    assert connectivity_claim["verdict"] == "Rejected"
    assert "not adjacent" in connectivity_claim["rejection_reasons"][0]
    assert r6["verdict"] == "Rejected"
    schedule = declared_model()["schedule"]["schedules"]["crossing_the_declared_step_energy_bound"]
    assert schedule["crosses_the_declared_step_energy_bound"] is True
    assert schedule["amplitudes"] == [str(value) for value in S_CROSSING_THE_BOUND]


def test_all_seven_controls_are_rejected_and_the_failed_control_is_retained():
    controls = load(EVIDENCE)["controls"]
    assert controls["control_count"] == 7
    assert controls["controls_executed"] == 7
    assert controls["controls_rejected"] == 7
    assert controls["every_control_produces_a_rejection"] is True
    assert controls["no_control_is_dropped"] is True
    assert len(controls["controls"]) == 7
    rows = controls["controls"]
    assert all(row["verdict"] == "Rejected" for row in rows)
    assert all(row["rejected"] is True for row in rows)
    assert all(row["executed"] is True for row in rows)
    assert all(row["discriminates"] is True for row in rows)
    assert all(sorted(row) == sorted(CONTROL_ROW_KEYS) for row in rows)
    assert all(row["rejection_reasons"] for row in rows)
    assert all(row["rejected_by"] for row in rows)
    assert all(row["unit"] == TRANSPORT_UNIT for row in rows)
    assert all(row["accepted_companion"]["accepted"] is True for row in rows)
    assert all(sorted(row["accepted_companion"]) == ["accepted", "claim", "verdict"]
               for row in rows)
    assert all(Fraction(row["derived_value"]["value"]) != Fraction(row["claimed_value"]["value"])
               for row in rows)
    assert all(row["derived_value"]["between_the_exact_integers"] for row in rows)
    zeroes = [row for row in rows if Fraction(row["derived_value"]["value"]) == 0]
    assert len(zeroes) == 4

    failed = controls["failed_controls"]
    assert controls["failed_controls_count"] == 1
    assert len(failed) == 1
    assert failed[0]["outcome"] == "FAILED_TO_DISCRIMINATE"
    assert failed[0]["discriminates"] is False
    assert Fraction(failed[0]["derived_transport"]) == Fraction(TRANSPORTING)
    assert failed[0]["derived_transport"] == failed[0]["rescaled_transport"]
    assert failed[0]["derived_gates"] == failed[0]["rescaled_gates"]
    assert "FAILED control" in failed[0]["why"]
    assert "rather than repaired" in failed[0]["why"]
    assert "retained" in controls["why_the_failed_control_is_retained"]


def test_the_payload_records_proposal_only_bookkeeping():
    bookkeeping = section("R7_proposal_only_bookkeeping")
    contract = load(CONTRACT)
    assert bookkeeping["authorization"] == NO_NONE
    assert bookkeeping["decision"] == NO_NONE
    assert bookkeeping["deployment"] == NO_NONE
    assert bookkeeping["governance"] == UNASSESSED
    assert bookkeeping["physical_effect_asserted"] == NO_NONE
    assert bookkeeping["data_used"] == NO_DATA
    assert bookkeeping["status"] == PROPOSAL_STATUS
    assert PROPOSAL_STATUS in contract["status"]
    assert bookkeeping["the_question_is_declared_and_nothing_else"] == contract["question"]
    assert "PROPOSAL ONLY" in bookkeeping["proposal_only_statement"]
    assert "authorizes nothing" in bookkeeping["proposal_only_statement"]
    assert bookkeeping["proposal_only_in_chinese_and_english"] == "提议性方案 / proposal only"
    assert bookkeeping["authorizes_nothing"] is True
    assert bookkeeping["decides_nothing"] is True
    assert bookkeeping["deploys_nothing"] is True
    assert bookkeeping["no_governance_assessment"] is True
    assert "who might decide" in bookkeeping["nothing_said_about_who_might_decide"]

    report = load(EVIDENCE)
    claimed = report["what_is_not_claimed"]
    assert claimed["authorization"] == NO_NONE
    assert claimed["decision"] == NO_NONE
    assert claimed["deployment"] == NO_NONE
    assert claimed["governance"] == UNASSESSED
    assert claimed["physical_effect_asserted"] == NO_NONE
    assert claimed["data_used"] == NO_DATA
    assert claimed["physical_claim"] is False
    assert claimed["magnitude_sign_or_timing_of_any_physical_quantity"] == NO_NONE
    assert claimed["no_magnitude_for_any_physical_quantity"] is True
    assert claimed["nothing_is_ablated_melted_moved_or_heated"] is True
    assert claimed["no_material_is_transported"] is True
    assert claimed["the_singular_point_appears_only_as_a_declared_pinning_site"] is True
    assert claimed["the_singular_point_is_a_declared_spatial_asymmetry_and_nothing_physical"] \
        is True
    assert claimed["no_data_read_or_used"] is True
    assert claimed["no_clock_read"] is True
    assert claimed["the_document_is_a_proposal_only"] is True
    assert claimed["no_claim_added_to_docs_claims_toml"] is True
    assert claimed["no_contract_or_note_edited"] is True
    assert claimed["native_certificate"] is False
    assert claimed["native_admission"] == "NotGranted"
    assert claimed["stable_api_change"] is False
    assert claimed["observational_verification"] == "Unavailable"

    status = report["verification_status"]
    assert status["observational"] == "Unavailable"
    assert status["no_data_read_or_used"] is True
    assert status["physical_effect_asserted"] == NO_NONE
    assert status["deployment"] == NO_NONE
    checked = status["checked_here"]
    assert checked["no_data_read_or_used"] is True
    assert checked["no_physical_effect_is_asserted"] is True
    assert checked["no_magnitude_for_any_physical_quantity_is_asserted"] is True
    assert checked["nothing_is_ablated_melted_moved_or_heated"] is True
    assert checked["the_singular_point_is_only_a_declared_pinning_site"] is True
    assert checked["every_declared_arithmetic_is_exact"] is True
    assert checked["governance_is_unaddressed"] is True


def test_the_payload_is_free_of_floating_point_literals_host_paths_and_timestamps():
    raw = EVIDENCE.read_text(encoding="utf-8")
    assert load(EVIDENCE)
    assert "NaN" not in raw and "Infinity" not in raw
    assert "/Users/" not in raw and "mingli" not in raw
    assert ".venv" not in raw and "tmp" not in raw
    report = load(EVIDENCE)
    assert report["checks"]["no_floating_point_value_is_retained"] is True
    assert report["checks"]["no_effect_key_appears_anywhere"] is True
    assert key_findings(report, FORBIDDEN_EFFECT_KEYS) == []
    assert key_findings(report, FORBIDDEN_TIME_KEYS) == []
    assert "T00:00" not in raw and "elapsed" not in raw


def test_the_frozen_shape_of_every_section():
    report = load(EVIDENCE)
    assert sorted(report) == sorted(TOP_LEVEL_KEYS)
    assert sorted(report["sections"]) == sorted(SECTION_NAMES)
    for name, keys in FROZEN_SECTION_SHAPE.items():
        assert sorted(report["sections"][name]) == sorted(keys), name
    for name in ("R1_spatially_and_temporally_symmetric", "R2_spatial_asymmetry_alone",
                 "R3_temporal_asymmetry_alone"):
        block = report["sections"][name]["transport"]
        assert sorted(block) == sorted(FROZEN_TRANSPORT_BLOCK_KEYS), name
    block = report["sections"]["R5_the_declared_phase_schedule"]["standing_wave"]["transport"]
    assert sorted(block) == sorted(FROZEN_TRANSPORT_BLOCK_KEYS), "R5"
    for sub in ("transport_at_the_declared_phase_gradient_plus_one",
                "transport_at_the_declared_phase_gradient_minus_one"):
        assert sorted(report["sections"]["R4_both_asymmetries"][sub]) \
            == sorted(FROZEN_TRANSPORT_BLOCK_KEYS), sub
    controls = report["controls"]
    assert controls["controls"][0]["unit"] == TRANSPORT_UNIT
    assert sorted(controls["failed_controls"][0]) == [
        "control", "derived_gates", "derived_transport", "discriminates", "outcome", "reading",
        "rescaled_gates", "rescaled_transport", "variant", "why"]
    model = report["sections"]["the_declared_model"]
    assert sorted(model["ring"]) == [
        "declared_adjacent_pairs", "declared_edge_count", "declared_edge_set",
        "declared_reflection", "declared_reflection_fixed_points", "n_sites", "site_labels",
        "the_reflection_is_an_involution"]
    assert sorted(model["schedule"]["schedules"]["time_symmetric"]) == [
        "amplitudes", "crosses_the_declared_step_energy_bound",
        "declared_step_energy_input_per_step", "declared_time_symmetric", "schedule_mean"]
    assert sorted(model["gates"]["for_the_asymmetric_potential"]) == ["leftward", "rightward"]


def test_the_undecided_items_and_modelling_choices_are_declared():
    report = load(EVIDENCE)
    undecided = report["undecided"]
    assert len(undecided) == 6
    assert report["checks"]["undecided_items_are_declared"] is True
    items = [row["item"] for row in undecided]
    assert any("gate rule" in item for item in items)
    assert any("phase gradient" in item for item in items)
    assert any("uniform reference measure" in item for item in items)
    assert any("time symmetry" in item for item in items)
    assert any("step energy input" in item for item in items)
    assert any("different declared ring" in item for item in items)
    for row in undecided:
        assert sorted(row) == ["item", "reason", "retained_partial_result"]
        assert row["reason"]
        assert row["retained_partial_result"] is not None
    gate = next(row for row in undecided if "gate rule" in row["item"])
    assert gate["retained_partial_result"]["the_rescaled_gates_are_identical"] is True
    assert gate["retained_partial_result"]["the_rescaled_transport_is_identical"] is True
    assert "Failed" not in gate["reason"] and "failed control" in gate["reason"]
    energy = next(row for row in undecided if "step energy input" in row["item"])
    assert energy["retained_partial_result"]["declared_step_energy_input_per_step"] \
        == ["2", "1", "1", "2"]
    reference = next(row for row in undecided if "uniform reference measure" in row["item"])
    assert reference["retained_partial_result"]["transport_from_the_periodic_measure_in_R4"] \
        == TRANSPORTING

    choices = report["modelling_choices"]
    assert len(choices) == 17
    for key in ("the_question_is_a_declared_model_question", "proposal_only", "the_ring",
                "the_potential", "the_gates_and_the_reflection_convention", "the_declared_phase",
                "the_declared_transfer", "the_declared_schedule_and_its_bound",
                "the_time_symmetry_reading", "the_declared_measure", "the_declared_transport",
                "the_exact_reversal", "every_zero_is_an_executed_rejection",
                "the_failed_control", "exact_only", "external_library", "resource_limits"):
        assert choices[key], key
    assert "提议性方案" in choices["proposal_only"]
    assert "No physical system" in choices["the_question_is_a_declared_model_question"]
    assert "pinning site" in choices["the_potential"]
    assert "nu_{s+T/2} = -nu_s" in choices["the_time_symmetry_reading"]
    assert "Undecided" in choices["the_time_symmetry_reading"]
    assert "executed rejection" in choices["every_zero_is_an_executed_rejection"]
    assert "failed control" in choices["the_failed_control"]
    assert "no floating-point value" in choices["exact_only"]
    assert "standard library alone" in choices["external_library"]
    assert "RLIMIT_CPU" in choices["resource_limits"]
    assert "RLIMIT_FSIZE" in choices["resource_limits"]
    assert "RLIMIT_AS" not in choices["resource_limits"]


def test_the_declared_checks_all_pass_and_name_their_conditions():
    checks = load(EVIDENCE)["checks"]
    assert all(checks.values())
    for name in ("assertions_within_budget",
                 "this_contract_digest_matches_the_declared_one",
                 "the_contract_declares_itself_a_proposal_only",
                 "the_declared_model_is_declared_in_full",
                 "the_declared_reflection_is_an_involution",
                 "exactly_one_declared_potential_is_reflection_invariant",
                 "the_declared_pinning_site_is_minimal_and_not_fixed_by_the_declared_reflection",
                 "every_declared_rate_and_stay_probability_is_positive",
                 "the_declared_periodic_measure_is_unique",
                 "R1_is_exactly_zero", "R2_is_exactly_zero", "R3_is_exactly_zero",
                 "R4_is_non_zero",
                 "R4_reverses_exactly_with_the_declared_phase_gradients_sign",
                 "R5_standing_wave_is_exactly_zero",
                 "R5_the_declared_phase_gradient_transports",
                 "R6_the_declared_connectivity_is_unchanged",
                 "R6_every_step_satisfies_the_declared_step_energy_bound",
                 "R6_the_declared_crossing_schedule_is_rejected",
                 "R6_the_declared_connectivity_changing_schedule_is_rejected",
                 "the_declared_time_symmetric_schedules_are_checked_invariant",
                 "the_declared_time_asymmetric_schedule_is_checked_not_invariant",
                 "the_declared_transfer_field_invariance_is_checked",
                 "the_declared_per_step_flows_pair_in_the_declared_symmetric_cases",
                 "the_R3_bias_identity_is_executed",
                 "the_declared_periodic_measure_is_reproduced_exactly",
                 "the_declared_uniform_reference_measure_agrees_on_the_declared_zeros",
                 "the_declared_uniform_reference_measure_reports_the_same_reversal",
                 "all_seven_declared_controls_are_rejected",
                 "every_declared_control_discriminates",
                 "every_zero_is_an_executed_rejection",
                 "the_failed_control_is_retained", "no_control_is_dropped",
                 "the_payload_records_proposal_only_bookkeeping",
                 "governance_is_unaddressed_and_no_decision_is_claimed",
                 "no_magnitude_for_any_physical_quantity_is_asserted",
                 "nothing_is_ablated_melted_moved_or_heated",
                 "the_singular_point_is_only_a_declared_pinning_site",
                 "observational_verification_is_recorded_unavailable",
                 "no_data_is_read_or_used", "undecided_items_are_declared",
                 "no_floating_point_value_is_retained", "no_effect_key_appears_anywhere"):
        assert checks[name] is True, name


def test_a_copied_checkout_reproduces_the_retained_payload(tmp_path):
    """The checker is re-run on a COPY: the payload must not depend on its location."""
    copied = tmp_path / "experiments" / "spatiotemporal_ratchet_v1"
    copied.mkdir(parents=True)
    shutil.copy(CHECKER, copied / "calibration.py")
    shutil.copy(CONTRACT, copied / "contract.json")
    output = tmp_path / "on-a-copy.json"
    completed = invoke(copied / "calibration.py", output)
    assert completed.returncode == 0, completed.stderr
    fresh = load(output)
    retained = load(EVIDENCE)
    assert fresh["status"] == retained["status"]
    assert fresh["assertions"] == retained["assertions"]
    assert fresh["sections"] == retained["sections"]
    assert fresh["checks"] == retained["checks"]
    assert fresh["controls"] == retained["controls"]
    assert fresh["undecided"] == retained["undecided"]
    assert fresh["what_is_not_claimed"] == retained["what_is_not_claimed"]
    assert fresh["modelling_choices"] == retained["modelling_choices"]
    assert digest(output) == digest(EVIDENCE)


def test_two_fresh_runs_are_byte_identical(tmp_path):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    assert invoke(CHECKER, first).returncode == 0
    assert invoke(CHECKER, second).returncode == 0
    assert digest(first) == digest(second) == digest(EVIDENCE)


def test_an_existing_output_is_never_overwritten(tmp_path):
    output = tmp_path / "keep.json"
    output.write_text("retained", encoding="utf-8")
    completed = invoke(CHECKER, output)
    assert completed.returncode != 0
    assert output.read_text(encoding="utf-8") == "retained"
    assert "refusing to overwrite" in completed.stdout


def test_the_claim_is_registered_once_and_binds_the_checker_and_the_note():
    """Exactly one claim for this run is registered, and it names the checker, the evidence and the note.

    The checker was written while this test asserted the claim's ABSENCE, because a claim lives in
    `docs/claims.toml` and is added by the parent session with its note.  The parent session has now
    added it; the assertion is inverted rather than dropped, so the binding stays checked.
    """
    claims = tomllib.loads((ROOT / "docs/claims.toml").read_text(encoding="utf-8"))["claim"]
    assert claims
    matches = [row for row in claims if row.get("claim_id") == CLAIM_ID]
    assert len(matches) == 1, "exactly one claim must be registered for this run"
    claim = matches[0]
    assert claim["status"] == "bounded-experiment"
    for symbol in ("spatiotemporal_ratchet_v1/calibration.py",
                   "spatiotemporal_ratchet_v1/contract.json",
                   "spatiotemporal_ratchet_v1/evidence.json",
                   "0242-a-spatiotemporal-ratchet"):
        assert symbol in claim["code_symbol"], symbol
    assert "failed to discriminate" in claim["counterexample_boundary"].lower(), \
        "the boundary must retain the failed control"
    assert "NotGranted" in claim["counterexample_boundary"], "the boundary must record native admission"
    assert claim["forbidden_conflations"], "the claim must name its conflations"

