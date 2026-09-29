#!/usr/bin/env python3
"""Research 0244 successor: exact mass transport on the unchanged declared graph.

Project-original under Unknown v0.3. Authored by ChatGPT (OpenAI), submitted
through Mingli Yuan's account proxy; no independent review or native authority.
The frozen parent is imported read-only, never patched or monkeypatched.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import pathlib
import resource
import signal
from fractions import Fraction as F

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONTRACT_PATH = HERE / "contract.json"
CONTRACT_SHA256 = "2df59f3b50ff74f537fcabeb35e8b8e9adf2a98809bdc8cab05ea2fd52844e5a"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [encode(v) for v in value]
    require(not isinstance(value, float), "floating point is outside this contract")
    return value


def canonical(value):
    return json.dumps(encode(value), sort_keys=True, separators=(",", ":")).encode()


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def frozen_inputs():
    require(digest(CONTRACT_PATH) == CONTRACT_SHA256, "successor contract digest mismatch")
    contract = json.loads(CONTRACT_PATH.read_text())
    for path, expected in contract["protected_files"].items():
        require(digest(ROOT / path) == expected, f"protected source changed: {path}")
    old = load_module(ROOT / "experiments/space_proposal_v3/calibration.py", "frozen_v3")
    return contract, old


def transpose(matrix):
    return [list(row) for row in zip(*matrix, strict=True)]


def carry(matrix, measure):
    """Row-vector convention, with no normalization or resetting to uniform."""
    return [sum((measure[i] * matrix[i][j] for i in range(len(measure))), F(0))
            for j in range(len(measure))]


def audit(matrix):
    n = len(matrix)
    require(0 < n <= 20 and all(len(row) == n for row in matrix), "invalid matrix shape")
    require(all(type(x) in (int, F) for row in matrix for x in row), "non-exact matrix")
    rows = [sum(row, F(0)) - 1 for row in matrix]
    columns = [sum(row, F(0)) - 1 for row in transpose(matrix)]
    u = [F(1, n)] * n
    drift = [x - y for x, y in zip(carry(matrix, u), u, strict=True)]
    # Outgoing mass minus incoming mass, distinct from uniform drift off-contract.
    divergence = [(rows[i] - columns[i]) / n for i in range(n)]
    nonnegative = all(x >= 0 for row in matrix for x in row)
    return {
        "nonnegative": nonnegative,
        "row_sum_residual": rows,
        "column_sum_residual": columns,
        "uniform_drift": drift,
        "vertex_mass_divergence": divergence,
        "uniform_stationary": not any(drift),
        "doubly_stochastic": nonnegative and not any(rows) and not any(columns),
    }


def accept(matrix):
    result = audit(matrix)
    require(result["doubly_stochastic"] and result["uniform_stationary"],
            "candidate is not doubly stochastic and uniformly stationary")
    return result


def model(contract, old):
    n = old.VERTEX_COUNT
    require(n == 20, "vertex bound")
    reflection = old.absolute_orientation(old.DECLARED_INVOLUTION)
    cycle = [old.VERTEX_INDEX[tuple(p)] for p in contract["model"]["cycle"]]
    base = [[F(i == j, 4) for j in range(n)] for i in range(n)]
    for i, j in old.GRAPH_EDGES:
        base[i][j] = base[j][i] = F(1, 4)
    current = [[F(0) for _ in range(n)] for _ in range(n)]
    for i, j in zip(cycle, cycle[1:] + cycle[:1], strict=True):
        require(tuple(sorted((i, j))) in old.GRAPH_EDGE_SET, "cycle leaves old graph")
        current[i][j] += 1
        current[j][i] -= 1
        current[reflection[i]][reflection[j]] -= 1
        current[reflection[j]][reflection[i]] += 1
    for i in range(n):
        require(sum(current[i]) == 0, "current divergence")
        for j in range(n):
            require(current[i][j] == -current[j][i], "current must be skew")
            require(current[reflection[i]][reflection[j]] == -current[i][j],
                    "current must be antipodal-odd")
    require(sum(x * x for row in current for x in row) == 16, "cycle support")
    accept(base)
    return base, current, reflection, cycle


def transfer(base, current, amplitude, gradient):
    require(type(amplitude) in (int, F) and abs(amplitude) <= F(1, 2), "amplitude bound")
    require(type(gradient) is int and gradient in (-1, 0, 1), "undeclared gradient")
    return [[base[i][j] + amplitude * gradient * current[i][j] / 16
             for j in range(len(base))] for i in range(len(base))]


def flow(matrix, measure, observable):
    return sum((measure[i] * matrix[i][j] * observable[i][j]
                for i in range(len(measure)) for j in range(len(measure))), F(0))


def trajectory(matrices, initial, observable):
    measure = list(initial)
    states, flows = [measure], []
    for matrix in matrices:
        flows.append(flow(matrix, measure, observable))
        measure = carry(matrix, measure)
        states.append(measure)
    return {"states": states, "flows": flows, "transport": sum(flows, F(0))}


def field_invariant(matrices, reflection):
    return all(matrices[(s + 2) % 4][reflection[i]][reflection[j]] == matrices[s][i][j]
               for s in range(4) for i in range(len(reflection))
               for j in range(len(reflection)))


def components(base):
    remaining, found = set(range(len(base))), []
    while remaining:
        reached, pending = set(), [min(remaining)]
        while pending:
            i = pending.pop()
            if i in reached:
                continue
            reached.add(i)
            pending.extend(j for j in range(len(base)) if base[i][j] > 0 and j not in reached)
        found.append(sorted(reached))
        remaining -= reached
    return found


def reference_0242():
    """Use the frozen ring implementation, not the successor's current construction."""
    ref = load_module(ROOT / "experiments/spatiotemporal_ratchet_v1/calibration.py", "ratchet_ref")
    rows = {}
    for name, potential, schedule in (
        ("R1", ref.U_INVARIANT, ref.S_TIME_SYMMETRIC),
        ("R2", ref.U_ASYMMETRIC, ref.S_TIME_SYMMETRIC),
        ("R3", ref.U_INVARIANT, ref.S_TIME_ASYMMETRIC),
        ("R4", ref.U_ASYMMETRIC, ref.S_TIME_ASYMMETRIC),
    ):
        for gradient in (-1, 0, 1):
            record = ref.transport_record(name, potential, schedule, gradient)
            require(record["final_state_equals_initial_state"], "0242 periodic measure")
            rows[f"{name}/{gradient}"] = {
                "transport": record["transport"], "flows": record["per_step_flows"],
                "initial": record["periodic_measure"], "final": record["final_measure"],
                "uniform": record["declared_measure_is_uniform"],
            }
    expected = F(-2395373021828541, 130893752065903472383)
    require(rows["R4/1"]["transport"] == expected, "0242 retained nonzero reference")
    require(rows["R4/-1"]["transport"] == -expected, "0242 exact reversal")
    for key, row in rows.items():
        if not key.startswith("R4/") or key.endswith("/0"):
            require(row["transport"] == 0, f"0242 zero: {key}")
    hops = ref.declared_steps(ref.U_ASYMMETRIC, ref.S_TIME_ASYMMETRIC, 1)[0]
    # 0242 uses COLUMN stochastic matrices. Transpose explicitly at this boundary.
    candidate = transpose(ref.step_matrix(*hops))
    require(not audit(candidate)["uniform_stationary"], "reference must distinguish measures")
    return rows, candidate


def rejected_candidate(matrix):
    result = audit(matrix)
    try:
        accept(matrix)
    except ValueError:
        return {"rejected": True, "audit": result}
    raise ValueError("negative control was accepted")


def build_payload():
    contract, old = frozen_inputs()
    # Re-execute the parent without changing any of its inputs or historical claims.
    retained = json.loads((ROOT / "experiments/space_proposal_v3/evidence.json").read_text())
    fresh = old.build_payload()
    require(fresh == retained, "frozen parent replay differs")
    protected = {name: hashlib.sha256(canonical(fresh["sections"][name])).hexdigest()
                 for name in contract["protected_sections"]}
    base, current, reflection, cycle = model(contract, old)
    n, uniform = len(base), [F(1, 20)] * 20
    schedules = {name: tuple(F(x) for x in values)
                 for name, values in contract["model"]["schedules"].items()}
    require(tuple(schedules.values()) == (old.S_SYMMETRIC, old.S_BROKEN, old.S_BROKEN_SHIFTED),
            "schedules changed")
    cases, operators = {}, {}
    for name, schedule in schedules.items():
        for gradient in contract["model"]["gradients"]:
            matrices = [transfer(base, current, a, gradient) for a in schedule]
            for a, matrix in zip(schedule, matrices, strict=True):
                result = accept(matrix)
                require(not any(result["vertex_mass_divergence"]), "vertex mass imbalance")
                require(all((matrix[i][j] > 0) == (base[i][j] > 0)
                            for i in range(n) for j in range(n)), "support changed")
                require(matrix == transpose(transfer(base, current, a, -gradient)),
                        "gradient reversal must transpose actual transfer")
                operators[str(a * gradient)] = {"matrix": matrix, "audit": result}
            trace = trajectory(matrices, uniform, current)
            require(all(state == uniform for state in trace["states"]), "actual carry drift")
            require(trace["flows"] == [a * gradient / 20 for a in schedule], "derived current")
            invariant = field_invariant(matrices, reflection)
            require(invariant == (name == "invariant" or gradient == 0), "field symmetry")
            if invariant:
                require(trace["transport"] == 0, "invariant transport")
                require(all(trace["flows"][s + 2] == -trace["flows"][s] for s in range(2)),
                        "half-period current pairing")
            else:
                require(trace["transport"] != 0, "nonvacuous broken transport")
            # All single-valued endpoint gradients vanish; check a basis as well as coordinates.
            endpoint_flows = []
            for vertex in range(n):
                observable = [[F((j == vertex) - (i == vertex)) for j in range(n)]
                              for i in range(n)]
                values = [flow(matrix, uniform, observable) for matrix in matrices]
                require(not any(values), "stationary endpoint displacement")
                endpoint_flows.append(values)
            trace.update({"gradient": gradient, "schedule": schedule,
                          "operator_keys": [str(a * gradient) for a in schedule],
                          "antipodal_half_period_invariant": invariant,
                          "endpoint_indicator_flows": endpoint_flows})
            cases[f"{name}/{gradient}"] = trace
    for name in schedules:
        require(cases[f"{name}/1"]["transport"] == -cases[f"{name}/-1"]["transport"],
                "exact total reversal")

    reference, ring_candidate = reference_0242()
    good = transfer(base, current, F(1, 2), 1)
    i, j = cycle[:2]
    bad_row = [row[:] for row in good]
    bad_row[i][j] += F(1, 64)
    bad_row[i][i] -= F(1, 64)
    negative = [row[:] for row in base]
    negative[i][i] -= F(1, 2)
    negative[j][j] -= F(1, 2)
    negative[i][j] += F(1, 2)
    negative[j][i] += F(1, 2)
    raw = [row[:] for row in base]
    for i, j in old.GRAPH_EDGES:
        for source, target in ((i, j), (j, i)):
            raw[source][target] += old.declared_weight(F(1, 2), 1,
                                                      old.POSITION_SYMMETRIC, source, target)
    normalized = [row[:] for row in raw]
    for i in range(n):
        normalized[i][i] = 1 - sum(normalized[i][j] for j in range(n) if j != i)
    candidates = {
        "row_stochastic_but_not_stationary": bad_row,
        "uniform_stationary_but_not_row_stochastic": transpose(bad_row),
        "unit_marginals_but_negative_entry": negative,
        "raw_frozen_weight_candidate": raw,
        "row_normalized_frozen_weight_candidate": normalized,
        "0242_R4_wrong_uniform_measure": ring_candidate,
    }
    controls = {name: rejected_candidate(matrix) for name, matrix in candidates.items()}
    require(not any(audit(bad_row)["row_sum_residual"]), "row control isolation")
    require(audit(transpose(bad_row))["uniform_stationary"], "column control isolation")
    require(not any(audit(negative)["row_sum_residual"])
            and not any(audit(negative)["column_sum_residual"]), "positivity control isolation")
    require(audit(normalized)["nonnegative"]
            and not any(audit(normalized)["row_sum_residual"]), "normalization control isolation")
    broken = cases["broken_uniform/1"]
    controls["double_stochasticity_alone_implies_invariant_zero"] = {
        "rejected": broken["transport"] != 0 and not broken["antipodal_half_period_invariant"],
        "transport": broken["transport"], "companion": "invariant/1"}
    controls["gradient_sign_independent"] = {
        "rejected": broken["transport"] != cases["broken_uniform/-1"]["transport"],
        "companion": "broken_uniform/-1"}
    controls["nonzero_endpoint_displacement"] = {
        "rejected": all(not any(row) for row in broken["endpoint_indicator_flows"]),
        "companion": "nonzero cycle circulation in broken_uniform/1"}
    for name, amplitude, gradient in (("amplitude_bound", F(3, 4), 1),
                                      ("undeclared_gradient", F(1, 2), 2)):
        try:
            transfer(base, current, amplitude, gradient)
        except ValueError as error:
            controls[name] = {"rejected": True, "reason": str(error)}
        else:
            raise ValueError(f"control not rejected: {name}")
    for row in controls.values():
        row.setdefault("accepted_companion", "broken_uniform/1")
    require(all(row["rejected"] for row in controls.values()), "failed control")
    return encode({
        "schema": "adva.external.space-proposal-v3-transfer.v1",
        "status": "ExternalExactPass", "native_admission": "NotGranted",
        "contract_sha256": digest(CONTRACT_PATH), "checker_sha256": digest(HERE / "calibration.py"),
        "base": contract["base"], "protected_files": contract["protected_files"],
        "parent_replay_equal": True, "protected_section_sha256": protected,
        "vertices": old.CONSTELLATION, "edges": old.GRAPH_EDGES, "antipodal": reflection,
        "cycle": cycle, "current_and_observable": current, "components": components(base),
        "operators": operators, "cases": cases, "controls": controls,
        "independent_reference_0242": reference,
        "legacy_endpoint_even_edges": sum(
            old.declared_weight(F(1, 2), 1, old.POSITION_SYMMETRIC, i, j)
            == old.declared_weight(F(1, 2), 1, old.POSITION_SYMMETRIC, j, i)
            for i, j in old.GRAPH_EDGES),
        "residual": contract["residual"], "limits": contract["budgets"], "origin": contract["origin"],
    })


def wall_limit(*_):
    raise TimeoutError("finite wall budget exhausted; Unknown, no success evidence")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        print("refusing to overwrite existing output")
        return 2
    # Fixed ceilings also cover source validation and reference replay.
    signal.signal(signal.SIGALRM, wall_limit)
    signal.alarm(60)
    resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1048576, 1048576))
    try:
        payload = build_payload()
        output = json.dumps(payload, indent=2, sort_keys=True) + "\n"
        require(len(output.encode()) <= 1048576, "output budget exhausted")
        with args.output.open("x") as stream:
            stream.write(output)
    except (ValueError, TimeoutError, FileExistsError) as error:
        print(f"Refused/Unknown: {error}")
        return 1
    print("ExternalExactPass: 9 cases; 11 refused controls; exact mass stationarity")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
