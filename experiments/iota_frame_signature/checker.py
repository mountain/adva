"""Exact external checker for the signatures the received {e, i, iota} frame can carry.

This checker never constructs, reads or authorizes an Adva semantic identity and
makes no physical claim. It uses integers, tuples and Fractions only, imports
nothing outside the standard library, and opens no external corpus. Every input
it reads is a pinned byte sequence already received in this repository, and every
acceptance test compares integers or exact rationals. No eigenvalue is
approximated anywhere: the inertia of a symmetric rational form is computed by
exact congruence reduction.

The frame operators are QUOTED, not restated, from received materials whose
SHA-256 digests this file pins:

  frame   knowledge/received/iota-frame-knowledge-2026-09-17-v1/materials/frame.md
          "J = [[0, -I], [I, 0]],  J^2 = -I"  ;  "Set H0 = L/(2*d_max), with
           denominator one for the empty-edge case, and H = diag(H0,H0).
           Initially G=I and O=I."  ;  "H commutes with J, is symmetric positive
           semidefinite and has operator norm at most one."  ;  "For y=T x, with
           an explicitly checked inverse, the target frame contains
           H' = T H T^-1, J' = T J T^-1, G' = T^-T G T^-1, O' = O T^-1.
           Thus J itself must be transported."

What this file computes, and what it does not, is stated in contract.json. In
particular it decides nothing about physical spacetime.
"""
import argparse
import hashlib
import itertools
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

FRAME_MD = "knowledge/received/iota-frame-knowledge-2026-09-17-v1/materials/frame.md"
IOTA_INTERPRETATIONS = (
    "knowledge/received/iota-process-knowledge-2026-09-17-v1/materials/interpretations.json"
)
FRAME_DEPENDENCIES = (
    "knowledge/received/iota-frame-knowledge-2026-09-17-v1/materials/dependencies.json"
)
FRAME_RECEIPT = "knowledge/received/iota-frame-knowledge-2026-09-17-v1/receipt.json"
PINS = {
    FRAME_MD: "d8967cc3e6b953d547a22010f37d9997a023d1b55935928f88becba86862dae0",
    IOTA_INTERPRETATIONS: "8009db7b8828ae76aa01b25684b9aa974fc91c4fcb64a439946701a49fe528b1",
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


def zeros(size):
    return [[F(0)] * size for _ in range(size)]


def matmul(left, right):
    size = len(left)
    inner = len(right)
    return [
        [sum(left[i][k] * right[k][j] for k in range(inner)) for j in range(len(right[0]))]
        for i in range(size)
    ]


def transpose(matrix):
    return [list(row) for row in zip(*matrix, strict=True)]


def identity(size):
    return [[F(1) if i == j else F(0) for j in range(size)] for i in range(size)]


def subtract(left, right):
    return [[left[i][j] - right[i][j] for j in range(len(left))] for i in range(len(left))]


def add(left, right):
    return [[left[i][j] + right[i][j] for j in range(len(left))] for i in range(len(left))]


def negate(matrix):
    return [[-value for value in row] for row in matrix]


def is_zero(matrix):
    return all(value == 0 for row in matrix for value in row)


def entry_sum(matrix):
    return sum(abs(value) for row in matrix for value in row)


def complex_structure(n):
    """J = [[0, -I], [I, 0]] on Q to the 2n, quoted from the received frame."""
    size = 2 * n
    matrix = zeros(size)
    for i in range(n):
        matrix[i][n + i] = F(-1)
        matrix[n + i][i] = F(1)
    return matrix


def laplacian(count, edges):
    matrix = zeros(count)
    for left, right, _label in edges:
        matrix[left][left] += 1
        matrix[right][right] += 1
        matrix[left][right] -= 1
        matrix[right][left] -= 1
    return matrix


def frame_operators(cut_graph_edges, cut_count, denominator=None):
    """H0 = L/(2 d_max), H = diag(H0, H0), J, and the generator A = -J H."""
    lap = laplacian(cut_count, cut_graph_edges)
    degrees = [lap[i][i] for i in range(cut_count)]
    d_max = max(degrees) if cut_count else F(0)
    divisor = F(denominator) if denominator is not None else (F(1) if d_max == 0 else 2 * d_max)
    h0 = [[value / divisor for value in row] for row in lap]
    size = 2 * cut_count
    h = zeros(size)
    for i in range(cut_count):
        for j in range(cut_count):
            h[i][j] = h0[i][j]
            h[cut_count + i][cut_count + j] = h0[i][j]
    n = cut_count
    return {
        "laplacian": lap,
        "degrees": degrees,
        "d_max": d_max,
        "divisor": divisor,
        "h0": h0,
        "H": h,
        "J": complex_structure(n) if size == 2 * n else None,
        "size": size,
    }


# ---------------------------------------------------------------------------
# exact inertia of a symmetric rational form, by congruence reduction
# ---------------------------------------------------------------------------

def inertia(matrix):
    """(positive, negative) indices of a symmetric rational matrix, exactly.

    One-by-one pivots on a nonzero diagonal entry; when no active diagonal entry
    is nonzero and the active block is not zero, a two-by-two block with zero
    diagonal and nonzero off-diagonal entry contributes exactly one positive and
    one negative direction and is eliminated by its block inverse. No eigenvalue
    is computed or approximated.
    """
    size = len(matrix)
    work = [row[:] for row in matrix]
    active = list(range(size))
    positive = negative = 0
    while active:
        pivot = next((i for i in active if work[i][i] != 0), None)
        if pivot is not None:
            value = work[pivot][pivot]
            positive += 1 if value > 0 else 0
            negative += 1 if value < 0 else 0
            for row in active:
                if row != pivot and work[row][pivot] != 0:
                    factor = work[row][pivot] / value
                    for column in active:
                        work[row][column] -= factor * work[pivot][column]
                    for column in active:
                        work[column][row] -= factor * work[column][pivot]
            active.remove(pivot)
            continue
        pair = None
        for i in active:
            for j in active:
                if j > i and work[i][j] != 0:
                    pair = (i, j)
                    break
            if pair:
                break
        if pair is None:
            break
        i, j = pair
        off = work[i][j]
        positive += 1
        negative += 1
        rest = [x for x in active if x not in (i, j)]
        for row in rest:
            left = work[row][i]
            right = work[row][j]
            for column in rest:
                work[row][column] -= (left * work[column][j] + right * work[column][i]) / off
        active.remove(i)
        active.remove(j)
    return positive, negative


def signature(matrix):
    positive, negative = inertia(matrix)
    return [positive, negative]


# ---------------------------------------------------------------------------
# exact solution of J-transpose G J = G
# ---------------------------------------------------------------------------

def rref(rows, columns):
    """Reduced row echelon form over Q; returns (matrix, pivot columns)."""
    work = [row[:] for row in rows]
    pivots = []
    row = 0
    for column in range(columns):
        target = next((r for r in range(row, len(work)) if work[r][column] != 0), None)
        if target is None:
            continue
        work[row], work[target] = work[target], work[row]
        lead = work[row][column]
        work[row] = [value / lead for value in work[row]]
        for r in range(len(work)):
            if r != row and work[r][column] != 0:
                factor = work[r][column]
                work[r] = [work[r][c] - factor * work[row][c] for c in range(columns)]
        pivots.append(column)
        row += 1
        if row == len(work):
            break
    return work, pivots


def solution_basis(rows, columns):
    """A basis of the null space of the given homogeneous system."""
    reduced, pivots = rref(rows, columns)
    free = [c for c in range(columns) if c not in pivots]
    basis = []
    for column in free:
        vector = [F(0)] * columns
        vector[column] = F(1)
        for index, pivot in enumerate(pivots):
            vector[pivot] = -reduced[index][column]
        basis.append(vector)
    return basis, len(pivots), free


def compatibility_system(n, symmetric):
    """The equations of J-transpose G J - G = 0, with optional symmetry equations."""
    size = 2 * n
    j = complex_structure(n)
    jt = transpose(j)
    columns = size * size
    rows = []
    for i in range(size):
        for k in range(size):
            row = [F(0)] * columns
            for a in range(size):
                for b in range(size):
                    coefficient = jt[i][a] * j[b][k]
                    if coefficient:
                        row[a * size + b] += coefficient
            row[i * size + k] -= 1
            rows.append(row)
    if symmetric:
        for i in range(size):
            for k in range(i + 1, size):
                row = [F(0)] * columns
                row[i * size + k] = F(1)
                row[k * size + i] = F(-1)
                rows.append(row)
    return rows, columns


def matrix_of(vector, size):
    return [[vector[i * size + j] for j in range(size)] for i in range(size)]


def symmetric_solution(n, values):
    """Build G = [[A, B], [-B, A]] from the free entries of A then B."""
    a_entries = [values.pop(0) for _ in range(n * (n + 1) // 2)]
    b_entries = [values.pop(0) for _ in range(n * (n - 1) // 2)]
    a = zeros(n)
    cursor = 0
    for i in range(n):
        for j in range(i, n):
            a[i][j] = a[j][i] = F(a_entries[cursor])
            cursor += 1
    b = zeros(n)
    cursor = 0
    for i in range(n):
        for j in range(i + 1, n):
            b[i][j] = F(b_entries[cursor])
            b[j][i] = -F(b_entries[cursor])
            cursor += 1
    size = 2 * n
    g = zeros(size)
    for i in range(n):
        for j in range(n):
            g[i][j] = a[i][j]
            g[i][n + j] = b[i][j]
            g[n + i][j] = -b[i][j]
            g[n + i][n + j] = a[i][j]
    return g


def free_entry_count(n):
    return n * (n + 1) // 2 + n * (n - 1) // 2


# ---------------------------------------------------------------------------
# sections
# ---------------------------------------------------------------------------

def s0_frame_instance(declared):
    """Rebuild the frame's own instance from the received process."""
    families = {family["name"]: family for family in load(IOTA_INTERPRETATIONS)["families"]}
    family = families[RECEIVED_PROCESS]
    masks = {cut["mask"] for cut in family["cuts"]}
    order = sorted(masks)
    index = {mask: i for i, mask in enumerate(order)}
    edges = []
    for left, right, label in family["edges"]:
        edges.append((index[left], index[right], label))
    count = len(order)
    frame = frame_operators(edges, count)
    j = frame["J"]
    h = frame["H"]
    size = frame["size"]
    check(matmul(j, j) == negate(identity(size)), "J squared is not minus the identity")
    check(h == transpose(h), "H is not symmetric")
    check(matmul(h, j) == matmul(j, h), "H does not commute with J")
    a = negate(matmul(j, h))
    check(transpose(a) == negate(a), "A = -J H is not skew")
    check(frame["degrees"] == [F(2), F(3), F(2), F(2), F(3), F(2)], "the degrees changed")
    check(frame["divisor"] == 6, "the frame denominator changed")
    metric = identity(size)
    jt = transpose(j)
    check(matmul(matmul(jt, metric), j) == metric, "the identity metric is not J compatible")
    return {
        "process": RECEIVED_PROCESS,
        "source": family["source"],
        "cuts": count,
        "carrier_dimension": size,
        "degrees": [str(value) for value in frame["degrees"]],
        "d_max": str(frame["d_max"]),
        "h0_scale": f"L/{frame['divisor']}",
        "checks": {
            "J_squared_is_minus_identity": True,
            "H_is_symmetric": True,
            "H_commutes_with_J": True,
            "A_is_skew": True,
            "G_equals_identity_is_J_compatible": True,
        },
        "metric_G": "I",
        "inertia_of_G": signature(metric),
        "signature_of_G": signature(metric),
    }


def s1_compatibility_system(declared):
    rows = []
    for n in declared["complex_structure_orders"]:
        size = 2 * n
        general_rows, columns = compatibility_system(n, symmetric=False)
        general_basis, general_rank, _ = solution_basis(general_rows, columns)
        symmetric_rows, _ = compatibility_system(n, symmetric=True)
        symmetric_basis, symmetric_rank, _ = solution_basis(symmetric_rows, columns)
        check(len(general_basis) == 2 * n * n, "the general solution dimension changed")
        check(len(symmetric_basis) == n * n, "the symmetric solution dimension changed")
        j = complex_structure(n)
        for vector in general_basis + symmetric_basis:
            matrix = matrix_of(vector, size)
            check(matmul(matrix, j) == matmul(j, matrix), "a solution does not commute with J")
        # the general solution has the declared block shape G = [[P, Q], [-Q, P]]
        shape_ok = True
        for vector in general_basis:
            matrix = matrix_of(vector, size)
            for i in range(n):
                for k in range(n):
                    if matrix[n + i][n + k] != matrix[i][k]:
                        shape_ok = False
                    if matrix[n + i][k] != -matrix[i][n + k]:
                        shape_ok = False
        check(shape_ok, "the general solution does not have the declared block shape")
        rows.append(
            {
                "n": n,
                "carrier_dimension": size,
                "unknowns": columns,
                "general_solution_dimension": len(general_basis),
                "general_rank": general_rank,
                "symmetric_solution_dimension": len(symmetric_basis),
                "symmetric_rank": symmetric_rank,
                "expected_general_dimension": 2 * n * n,
                "expected_symmetric_dimension": n * n,
                "every_basis_solution_commutes_with_J": True,
                "general_solutions_have_the_block_shape": True,
            }
        )
    return {
        "orders": rows,
        "general_dimension_is_two_n_squared": True,
        "symmetric_dimension_is_n_squared": True,
        "every_solution_commutes_with_J": True,
    }


def s2_exhaustive_inertia(declared):
    families = declared["exhaustive_families"]
    rows = []
    for key in ("n_equals_1", "n_equals_2", "n_equals_3"):
        entry = families[key]
        n = int(key.split("_")[-1])
        low, high = entry["range"]
        check(free_entry_count(n) == entry["free_entries"], "the free entry count changed")
        values = range(low, high + 1)
        examined = degenerate = 0
        signatures = {}
        odd = []
        for combination in itertools.product(values, repeat=entry["free_entries"]):
            examined += 1
            matrix = symmetric_solution(n, list(combination))
            positive, negative = inertia(matrix)
            if positive + negative != 2 * n:
                degenerate += 1
                continue
            signatures[(positive, negative)] = signatures.get((positive, negative), 0) + 1
            if positive % 2 or negative % 2:
                odd.append([list(combination), positive, negative])
        check(examined == entry["members"], "the family size changed")
        check(not odd, "a symmetric nondegenerate member has an odd inertia index")
        rows.append(
            {
                "n": n,
                "carrier_dimension": 2 * n,
                "range": [low, high],
                "free_entries": entry["free_entries"],
                "members_examined": examined,
                "degenerate_members": degenerate,
                "nondegenerate_members": examined - degenerate,
                "signatures_seen": {f"{p},{q}": c for (p, q), c in sorted(signatures.items())},
                "members_with_an_odd_index": odd,
                "every_index_is_even": True,
            }
        )
    return {
        "families": rows,
        "every_symmetric_nondegenerate_member_has_even_indices": True,
    }


def s3_four_dimensional_conclusion(declared):
    target = declared["four_dimensional_carrier"]
    reachable = []
    for positive in range(target + 1):
        for negative in range(target + 1):
            if positive + negative == target and positive % 2 == 0 and negative % 2 == 0:
                reachable.append([positive, negative])
    unreachable = []
    for positive in range(target + 1):
        for negative in range(target + 1):
            if positive + negative == target and [positive, negative] not in reachable:
                unreachable.append([positive, negative])
    check([3, 1] in unreachable, "one negative direction is not refused")
    check([1, 3] in unreachable, "three negative directions are not refused")
    check(reachable == [[0, 4], [2, 2], [4, 0]], "the reachable set changed")
    return {
        "carrier_dimension": target,
        "reachable_signatures": reachable,
        "unreachable_signatures": unreachable,
        "exactly_one_negative_direction_is_unreachable": True,
    }


def s4_lorentzian_cost(declared):
    """What a Lorentzian metric costs while the complex structure stays."""
    minimal = declared["minimal_four_dimensional_instance"]
    frame = frame_operators([(0, 1, 0)], minimal["cuts"])
    j = frame["J"]
    h = frame["H"]
    size = frame["size"]
    check(frame["divisor"] == minimal["denominator"], "the minimal instance denominator changed")
    check(matmul(h, j) == matmul(j, h), "the minimal instance does not commute")
    euclidean = identity(size)
    a = negate(matmul(j, h))
    residual_euclidean = add(transpose(a), a)
    check(is_zero(residual_euclidean), "A is not skew under the identity metric")
    lorentzian = zeros(size)
    for i, value in enumerate(declared["declared_lorentzian_metric"]["diagonal"]):
        lorentzian[i][i] = F(value)
    check(size == len(declared["declared_lorentzian_metric"]["diagonal"]),
          "the declared metric does not fit the minimal instance")
    jt = transpose(j)
    orthogonality_residual = subtract(matmul(matmul(jt, lorentzian), j), lorentzian)
    generator_residual = add(matmul(transpose(a), lorentzian), matmul(lorentzian, a))
    check(not is_zero(orthogonality_residual), "J is unexpectedly orthogonal for the metric")
    check(not is_zero(generator_residual), "the generator is unexpectedly skew for the metric")
    check(signature(lorentzian) == declared["declared_lorentzian_metric"]["signature"],
          "the declared metric does not have its declared signature")
    return {
        "instance": {
            "cuts": minimal["cuts"],
            "carrier_dimension": size,
            "degrees": [str(value) for value in frame["degrees"]],
            "d_max": str(frame["d_max"]),
            "h0_scale": f"L/{frame['divisor']}",
        },
        "identity_metric": {
            "signature": signature(euclidean),
            "A_is_skew": True,
            "residual_A_transpose_plus_A": [[str(v) for v in row] for row in residual_euclidean],
        },
        "lorentzian_metric": {
            "diagonal": declared["declared_lorentzian_metric"]["diagonal"],
            "signature": signature(lorentzian),
            "J_is_orthogonal": False,
            "residual_J_transpose_G_J_minus_G": [
                [str(v) for v in row] for row in orthogonality_residual
            ],
            "residual_J_transpose_G_J_minus_G_absolute_sum": str(entry_sum(orthogonality_residual)),
            "A_is_skew": False,
            "residual_A_transpose_G_plus_G_A": [
                [str(v) for v in row] for row in generator_residual
            ],
            "residual_A_transpose_G_plus_G_A_absolute_sum": str(entry_sum(generator_residual)),
        },
        "the_frame_identity_holds_for_one_metric_and_fails_for_the_other": True,
    }


def s5_involution_route(declared):
    """The same carrier and the same Lorentzian metric, with an involution instead."""
    size = len(declared["declared_involution"]["diagonal"])
    involution = zeros(size)
    for i, value in enumerate(declared["declared_involution"]["diagonal"]):
        involution[i][i] = F(value)
    lorentzian = zeros(size)
    for i, value in enumerate(declared["declared_lorentzian_metric"]["diagonal"]):
        lorentzian[i][i] = F(value)
    j = complex_structure(size // 2)
    it = transpose(involution)
    check(matmul(involution, involution) == identity(size), "the involution does not square to one")
    check(matmul(matmul(it, lorentzian), involution) == lorentzian,
          "the involution is not compatible with the Lorentzian metric")
    check(involution != j and involution != negate(j), "the involution coincides with J")
    check(matmul(j, j) != identity(size), "J unexpectedly squares to one")
    check(matmul(matmul(transpose(j), lorentzian), j) != lorentzian,
          "J is unexpectedly compatible with the Lorentzian metric")
    return {
        "involution_diagonal": declared["declared_involution"]["diagonal"],
        "involution_squares_to_identity": True,
        "involution_is_compatible_with_the_lorentzian_metric": True,
        "involution_equals_J": False,
        "complex_structure_is_compatible_with_the_lorentzian_metric": False,
        "lorentzian_signature": signature(lorentzian),
        "reading": (
            "a signature with exactly one negative direction is reachable on this carrier when "
            "the structure is an involution; what the frame's other obligations become under "
            "that structure is not decided here"
        ),
    }


def s6_refusals(declared):
    refusals = declared["refusals"]
    check(len(refusals) >= 5, "the declared refusal list is short")
    return {"refusals": refusals, "refusal_count": len(refusals)}


def run(output):
    started = time.perf_counter_ns()
    contract = load("experiments/iota_frame_signature/contract.json")
    declared = contract["objects"]
    for relative, expected in PINS.items():
        check(digest(relative) == expected, f"pin mismatch: {relative}")
    recorded = load(FRAME_DEPENDENCIES)["previous_materials"]
    check(all(recorded[name] == value for name, value in declared["recorded_pins"].items()),
          "the pinned digests disagree with the received previous-materials record")
    receipt = load(FRAME_RECEIPT)
    delivered = {
        entry["destination"].split("/")[-1]: entry["sha256"] for entry in receipt["files"]
    }
    check(all(delivered[name] == value
              for name, value in declared["receipt_pins"].items()),
          "the pinned digests disagree with the received delivery receipt")
    declared.setdefault("complex_structure_orders", [1, 2, 3])
    declared.setdefault("four_dimensional_carrier", 4)
    sections = {
        "S0_frame_instance": s0_frame_instance(declared),
        "S1_compatibility_system": s1_compatibility_system(declared),
        "S2_exhaustive_inertia": s2_exhaustive_inertia(declared),
        "S3_four_dimensional_conclusion": s3_four_dimensional_conclusion(declared),
        "S4_lorentzian_cost": s4_lorentzian_cost(declared),
        "S5_involution_route": s5_involution_route(declared),
        "S6_refusals": s6_refusals(declared),
    }
    report = {
        "schema": "adva.research.iota-frame-signature-evidence.v0",
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
    an enforced limit; this file deliberately contains no address-space call.
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
    LIMITS.update(load("experiments/iota_frame_signature/contract.json")["budget"])
    install_limits()
    report, _ = run(args.output)
    print(json.dumps({"status": report["status"], "assertions": report["assertions"]},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
