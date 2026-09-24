"""Exact external checker for what the involution route does to the frame's exponential reading.

This checker never constructs, reads or authorizes an Adva semantic identity and
makes no physical claim. It uses integers, tuples and Fractions only, imports
nothing outside the standard library, and opens no external corpus. Every input it
reads is a pinned byte sequence already received in this repository, and every
acceptance test compares integers or exact rationals. No eigenvalue is
approximated anywhere: the inertia of a symmetric rational form is computed by
exact congruence reduction.

The frame operators, the generator and the coefficient identity are QUOTED, not
restated, from a received material whose SHA-256 digest this file pins:

  frame   knowledge/received/iota-frame-knowledge-2026-09-17-v1/materials/frame.md
          "J = [[0, -I], [I, 0]],  J^2 = -I"  ;  "Set H0 = L/(2*d_max), with
           denominator one for the empty-edge case, and H = diag(H0,H0).
           Initially G=I and O=I."  ;  "Define the real-time and heat generators
           A = -J H,  B = -H.  The exponential readings are U(t)=exp(tA) and
           T(tau)=exp(tau B)."  ;  "Substituting t=-i*tau coefficient by
           coefficient gives (-J)^k A^k/k! = (-H)^k/k!."  ;  "The finite checker
           compares coefficients through order 12."

What this file computes, and what it does not, is stated in contract.json. In
particular it decides nothing about any physical process.
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

IOTA_INTERPRETATIONS = (
    "knowledge/received/iota-process-knowledge-2026-09-17-v1/materials/interpretations.json"
)
FRAME_MD = "knowledge/received/iota-frame-knowledge-2026-09-17-v1/materials/frame.md"
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


# ---------------------------------------------------------------------------
# exact rational matrices
# ---------------------------------------------------------------------------

def zeros(size):
    return [[F(0)] * size for _ in range(size)]


def identity(size):
    return [[F(1) if i == j else F(0) for j in range(size)] for i in range(size)]


def matmul(left, right):
    rows, inner, cols = len(left), len(right), len(right[0])
    out = [[F(0)] * cols for _ in range(rows)]
    for i in range(rows):
        for k in range(inner):
            factor = left[i][k]
            if factor == 0:
                continue
            for j in range(cols):
                out[i][j] += factor * right[k][j]
    return out


def transpose(matrix):
    return [list(row) for row in zip(*matrix, strict=True)]


def add(left, right):
    return [[left[i][j] + right[i][j] for j in range(len(left))] for i in range(len(left))]


def sub(left, right):
    return [[left[i][j] - right[i][j] for j in range(len(left))] for i in range(len(left))]


def negate(matrix):
    return [[-value for value in row] for row in matrix]


def is_zero(matrix):
    return all(value == 0 for row in matrix for value in row)


def scale(matrix, factor):
    return [[value * factor for value in row] for row in matrix]


def entries(matrix):
    return [value for row in matrix for value in row]


def power(matrix, exponent):
    result = identity(len(matrix))
    for _ in range(exponent):
        result = matmul(result, matrix)
    return result


def determinant(matrix):
    size = len(matrix)
    work = [row[:] for row in matrix]
    result = F(1)
    for column in range(size):
        pivot = next((r for r in range(column, size) if work[r][column] != 0), None)
        if pivot is None:
            return F(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        result *= work[column][column]
        for row in range(column + 1, size):
            if work[row][column] != 0:
                factor = work[row][column] / work[column][column]
                for c in range(column, size):
                    work[row][c] -= factor * work[column][c]
    return result


def inertia(matrix):
    """Exact positive and negative indices of a symmetric rational form."""
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
            left, right = work[row][i], work[row][j]
            for column in rest:
                work[row][column] -= (left * work[column][j] + right * work[column][i]) / off
        active.remove(i)
        active.remove(j)
    return positive, negative


# ---------------------------------------------------------------------------
# the frame's own instance, rebuilt from the received process
# ---------------------------------------------------------------------------

def frame_instance():
    families = {family["name"]: family for family in load(IOTA_INTERPRETATIONS)["families"]}
    family = families[RECEIVED_PROCESS]
    masks = sorted({cut["mask"] for cut in family["cuts"]})
    index = {mask: i for i, mask in enumerate(masks)}
    cuts = len(masks)
    lap = zeros(cuts)
    for left, right, _label in family["edges"]:
        i, j = index[left], index[right]
        lap[i][i] += 1
        lap[j][j] += 1
        lap[i][j] -= 1
        lap[j][i] -= 1
    d_max = max(lap[i][i] for i in range(cuts))
    divisor = F(1) if d_max == 0 else 2 * d_max
    h0 = [[value / divisor for value in row] for row in lap]
    size = 2 * cuts
    h = zeros(size)
    for i in range(cuts):
        for j in range(cuts):
            h[i][j] = h0[i][j]
            h[cuts + i][cuts + j] = h0[i][j]
    j_matrix = zeros(size)
    for i in range(cuts):
        j_matrix[i][cuts + i] = F(-1)
        j_matrix[cuts + i][i] = F(1)
    return {
        "source": family["source"],
        "cuts": cuts,
        "size": size,
        "d_max": d_max,
        "divisor": divisor,
        "h0": h0,
        "H": h,
        "J": j_matrix,
    }


def minimal_instance(cuts=2):
    """The smallest non-degenerate instance: two cuts joined by one edge."""
    lap = zeros(cuts)
    for i in range(cuts - 1):
        lap[i][i] += 1
        lap[i + 1][i + 1] += 1
        lap[i][i + 1] -= 1
        lap[i + 1][i] -= 1
    d_max = max(lap[i][i] for i in range(cuts))
    divisor = F(1) if d_max == 0 else 2 * d_max
    h0 = [[value / divisor for value in row] for row in lap]
    size = 2 * cuts
    h = zeros(size)
    for i in range(cuts):
        for j in range(cuts):
            h[i][j] = h0[i][j]
            h[cuts + i][cuts + j] = h0[i][j]
    return {"cuts": cuts, "size": size, "d_max": d_max, "divisor": divisor, "H": h}


def diagonal(values):
    size = len(values)
    matrix = zeros(size)
    for i, value in enumerate(values):
        matrix[i][i] = F(value)
    return matrix


def block_involution(cuts):
    size = 2 * cuts
    matrix = zeros(size)
    for i in range(cuts):
        matrix[i][i] = F(1)
        matrix[cuts + i][cuts + i] = F(-1)
    return matrix


# ---------------------------------------------------------------------------
# coefficient identities
# ---------------------------------------------------------------------------

def coefficient_identity_holds(H, S, sigma, degree):
    """(-S)^k (-S H)^k == sigma^k H^k for every k from zero to degree."""
    generator = negate(matmul(S, H))
    mismatches = []
    for k in range(degree + 1):
        left = matmul(power(negate(S), k), power(generator, k))
        right = scale(power(H, k), F(sigma) ** k)
        if left != right:
            mismatches.append(k)
    return generator, mismatches


def invariance_coefficients(H, S, metric, degree):
    """Coefficients of U(t)^T G U(t) through the declared degree, for A_S = -S H."""
    generator = negate(matmul(S, H))
    at = transpose(generator)
    remainder = []
    for total in range(1, degree + 1):
        coefficient = zeros(len(metric))
        for p in range(total + 1):
            q = total - p
            term = matmul(matmul(power(at, p), metric), power(generator, q))
            coefficient = add(coefficient, scale(term, F(1, _factorial(p) * _factorial(q))))
        if not is_zero(coefficient):
            remainder.append(total)
    zero_order = matmul(matmul(identity(len(metric)), metric), identity(len(metric)))
    return generator, remainder, zero_order == metric


def _factorial(n):
    out = 1
    for k in range(2, n + 1):
        out *= k
    return out


def generator_skewness_residual(generator, metric):
    return add(matmul(transpose(generator), metric), matmul(metric, generator))


# ---------------------------------------------------------------------------
# the declared linear system
# ---------------------------------------------------------------------------

def solve_metric_system(H, K):
    """All symmetric G with K^T G K = G and H (G K) + (G K) H = 0."""
    size = len(H)
    pairs = [(i, j) for i in range(size) for j in range(i, size)]
    column = {pair: c for c, pair in enumerate(pairs)}
    width = len(pairs)

    def linear_row(function, row_index):
        row = [F(0)] * width
        for pair in pairs:
            probe = zeros(size)
            probe[pair[0]][pair[1]] = F(1)
            probe[pair[1]][pair[0]] = F(1)
            image = function(probe)
            value = image[row_index[0]][row_index[1]]
            row[column[pair]] = value
        return row

    def compatible(G):
        return sub(matmul(matmul(transpose(K), G), K), G)

    def anticommuting(G):
        return add(matmul(H, matmul(G, K)), matmul(matmul(G, K), H))

    rows = []
    for function in (compatible, anticommuting):
        for i in range(size):
            for j in range(size):
                rows.append(linear_row(function, (i, j)))
    work = [row[:] for row in rows]
    pivots = []
    cursor = 0
    for c in range(width):
        target = next((r for r in range(cursor, len(work)) if work[r][c] != 0), None)
        if target is None:
            continue
        work[cursor], work[target] = work[target], work[cursor]
        lead = work[cursor][c]
        work[cursor] = [value / lead for value in work[cursor]]
        for r in range(len(work)):
            if r != cursor and work[r][c] != 0:
                factor = work[r][c]
                work[r] = [work[r][k] - factor * work[cursor][k] for k in range(width)]
        pivots.append(c)
        cursor += 1
        if cursor == len(work):
            break
    free = [c for c in range(width) if c not in pivots]
    basis = []
    for c in free:
        vector = [F(0)] * width
        vector[c] = F(1)
        for row_index, pivot in enumerate(pivots):
            vector[pivot] = -work[row_index][c]
        G = zeros(size)
        for pair, value in zip(pairs, vector, strict=True):
            G[pair[0]][pair[1]] = value
            G[pair[1]][pair[0]] = value
        basis.append(G)
    return {"basis": basis, "rank": len(pivots), "unknowns": width}


def every_element_is_degenerate(basis, samples):
    """A two-dimensional space: det(a + t b) at five values decides a degree-four polynomial."""
    if len(basis) != 2:
        return None, None
    values = [determinant(add(basis[0], scale(basis[1], F(t)))) for t in samples]
    return values, all(value == 0 for value in values)


# ---------------------------------------------------------------------------
# sections
# ---------------------------------------------------------------------------

def s0_frame_instance(declared):
    degree = declared["checked_degree"]
    frame = frame_instance()
    size, cuts = frame["size"], frame["cuts"]
    H, J = frame["H"], frame["J"]
    check(frame["cuts"] == 6 and size == 12, "the received instance changed")
    check(frame["d_max"] == 3 and frame["divisor"] == 6, "the frame normalization changed")
    check(matmul(J, J) == negate(identity(size)), "J squared is not minus the identity")
    check(matmul(H, J) == matmul(J, H), "H does not commute with J")
    A = negate(matmul(J, H))
    check(is_zero(generator_skewness_residual(A, identity(size))),
          "A is not skew for the identity metric")
    _generator, mismatches = coefficient_identity_holds(H, J, -1, degree)
    check(not mismatches, "the received Wick identity does not hold")
    _generator, remainder, zero_order_ok = invariance_coefficients(H, J, identity(size), degree)
    check(not remainder and zero_order_ok,
          "the received invariance identity does not hold through the declared degree")
    return {
        "process": RECEIVED_PROCESS,
        "source": frame["source"],
        "cuts": cuts,
        "carrier_dimension": size,
        "d_max": str(frame["d_max"]),
        "h0_scale": f"L/{frame['divisor']}",
        "checked_degree": degree,
        "J_squared_is_minus_identity": True,
        "H_commutes_with_J": True,
        "generator_A": "-J H",
        "A_is_skew_for_the_identity_metric": True,
        "wick_identity_(-J)^k_A^k_equals_(-H)^k_mismatched_degrees": mismatches,
        "invariance_identity_U_transpose_G_U_equals_G_degrees_with_nonzero_coefficient": remainder,
    }


def s1_sign_lemma(declared):
    degree = declared["checked_degree"]
    frame = frame_instance()
    size, cuts = frame["size"], frame["cuts"]
    H = frame["H"]
    J = frame["J"]
    K = block_involution(cuts)
    check(matmul(K, K) == identity(size), "the declared block involution does not square to one")
    check(matmul(H, K) == matmul(K, H), "the declared block involution does not commute with H")
    rows = []
    for name, S, sigma in (("the complex structure J", J, -1),
                           ("the declared block involution K", K, 1)):
        square = matmul(S, S)
        check(square == scale(identity(size), F(sigma)),
              f"the structure does not square to sigma: {name}")
        generator, mismatches = coefficient_identity_holds(H, S, sigma, degree)
        check(not mismatches, f"the coefficient identity fails for {name}")
        signs = []
        for k in range(4):
            left = matmul(power(negate(S), k), power(generator, k))
            signs.append({
                "k": k,
                "equals_plus_H_power_k": left == power(H, k),
                "equals_minus_one_power_k_times_H_power_k":
                    left == scale(power(H, k), F(-1) ** k),
            })
        rows.append({
            "structure": name,
            "sigma": sigma,
            "squares_to_sigma_identity": True,
            "commutes_with_H": True,
            "generator": "-S H",
            "identity": "(-S)^k A_S^k = sigma^k H^k",
            "mismatched_degrees": mismatches,
            "first_degrees": signs,
        })
    check(rows[0]["sigma"] == -1 and rows[1]["sigma"] == 1, "the declared sigmas changed")
    return {
        "instances": rows,
        "identity": (
            "(-S)^k A_S^k = sigma^k H^k for S squared equal to sigma times the identity "
            "with S commuting with H"
        ),
        "reading_at_sigma_minus_one": (
            "the coefficients alternate in sign, which is the exponential of minus H, the "
            "received heat reading"
        ),
        "reading_at_sigma_plus_one": (
            "every coefficient has the same sign, which is the exponential of plus H, the "
            "time reverse of the heat reading"
        ),
        "the_sign_in_the_exponent_is_the_sign_of_the_structure_square": True,
    }


def s2_lorentzian_carrier(declared):
    minimal = minimal_instance(declared["declared_minimal_instance"]["cuts"])
    size = minimal["size"]
    check(size == declared["declared_minimal_instance"]["carrier_dimension"],
          "the minimal instance dimension changed")
    metric = diagonal(declared["declared_lorentzian_metric"]["diagonal"])
    K = diagonal(declared["declared_involution"]["diagonal"])
    H = minimal["H"]
    j_matrix = zeros(size)
    for i in range(size // 2):
        j_matrix[i][size // 2 + i] = F(-1)
        j_matrix[size // 2 + i][i] = F(1)
    check(inertia(metric) == tuple(declared["declared_lorentzian_metric"]["signature"]),
          "the declared Lorentzian metric does not have its declared signature")
    check(matmul(K, K) == identity(size), "the declared involution does not square to one")
    check(matmul(matmul(transpose(K), metric), K) == metric,
          "the declared involution is not compatible with the Lorentzian metric")
    check(matmul(matmul(transpose(j_matrix), metric), j_matrix) != metric,
          "the complex structure is unexpectedly compatible with the Lorentzian metric")
    a_k = negate(matmul(K, H))
    residual = generator_skewness_residual(a_k, metric)
    check(not is_zero(residual), "the generator is unexpectedly skew for the metric")
    correction = zero_metric = None
    # the exact condition for skewness: H must anticommute with the product G K
    product = matmul(metric, K)
    correction = add(matmul(H, product), matmul(product, H))
    zero_metric = is_zero(correction)
    check(not zero_metric, "the skewness condition unexpectedly holds")
    return {
        "instance": {"cuts": minimal["cuts"], "carrier_dimension": size,
                     "d_max": str(minimal["d_max"]), "h0_scale": f"L/{minimal['divisor']}"},
        "lorentzian_metric_diagonal": declared["declared_lorentzian_metric"]["diagonal"],
        "lorentzian_signature": list(inertia(metric)),
        "involution_diagonal": declared["declared_involution"]["diagonal"],
        "involution_squares_to_identity": True,
        "involution_is_compatible_with_the_metric": True,
        "complex_structure_is_compatible_with_the_metric": False,
        "generator_A_K": "-K H",
        "A_K_is_skew": False,
        "residual_A_K_transpose_G_plus_G_A_K": [[str(v) for v in row] for row in residual],
        "residual_absolute_sum": str(sum(abs(v) for v in entries(residual))),
        "skewness_condition_is_H_anticommuting_with_G_K": True,
        "H_anticommutes_with_G_K": zero_metric,
    }


def s3_impossibility(declared):
    samples = declared["degeneracy_witness"]["sample_values"]
    instances = []
    for label, H, K, size in (
        ("the declared four-dimensional instance", minimal_instance(2)["H"],
         diagonal(declared["declared_involution"]["diagonal"]), 4),
        ("the frame's own twelve-dimensional instance", frame_instance()["H"],
         block_involution(6), 12),
    ):
        solution = solve_metric_system(H, K)
        check(len(solution["basis"]) == 2, f"the solution dimension changed for {label}")
        values, all_degenerate = every_element_is_degenerate(solution["basis"], samples)
        check(all_degenerate is True, f"a solution is not degenerate for {label}")
        determinants = [str(determinant(G)) for G in solution["basis"]]
        ranks = []
        for G in solution["basis"]:
            positive, negative = inertia(G)
            ranks.append(positive + negative)
        instances.append({
            "label": label,
            "carrier_dimension": size,
            "unknowns": solution["unknowns"],
            "rank": solution["rank"],
            "solution_dimension": len(solution["basis"]),
            "basis_determinants": determinants,
            "basis_inertia_ranks": ranks,
            "determinants_at_the_sample_values": [str(value) for value in values],
            "every_element_of_the_solution_space_is_degenerate": all_degenerate,
        })
    reason = ("the cut operator is a graph Laplacian, so its kernel on each connected component is "
              "the constants; the surviving compatible metrics are scalar multiples of a rank-one "
              "matrix in each block of the involution, and a block of rank one has zero "
              "determinant")
    return {
        "instances": instances,
        "system": (
            "K^T G K = G and H (G K) + (G K) H = 0, in the independent entries of a "
            "symmetric G"
        ),
        "no_nondegenerate_metric_satisfies_both": True,
        "structural_reason": reason,
        "bounded_to": (
            "the two declared instances; the general statement is an elementary argument and "
            "not an executed check over all graphs"
        ),
    }


def s4_refusals(declared):
    refusals = declared["refusals"]
    check(len(refusals) >= 5, "the declared refusal list is short")
    return {"refusals": refusals, "refusal_count": len(refusals)}


def run(output):
    started = time.perf_counter_ns()
    contract = load("experiments/lorentzian_frame_reading/contract.json")
    declared = contract["objects"]
    for relative, expected in PINS.items():
        check(digest(relative) == expected, f"pin mismatch: {relative}")
    recorded = load(FRAME_DEPENDENCIES)["previous_materials"]
    check(all(recorded[name] == value for name, value in declared["recorded_pins"].items()),
          "the pinned digests disagree with the received previous-materials record")
    delivered = {
        entry["destination"].split("/")[-1]: entry["sha256"]
        for entry in load(FRAME_RECEIPT)["files"]
    }
    check(all(delivered[name] == value for name, value in declared["receipt_pins"].items()),
          "the pinned digests disagree with the received delivery receipt")
    sections = {
        "S0_frame_instance": s0_frame_instance(declared),
        "S1_sign_lemma": s1_sign_lemma(declared),
        "S2_lorentzian_carrier": s2_lorentzian_carrier(declared),
        "S3_impossibility": s3_impossibility(declared),
        "S4_refusals": s4_refusals(declared),
    }
    report = {
        "schema": "adva.research.lorentzian-frame-reading-evidence.v0",
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
    an enforced limit; this file contains no address-space call.
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
    LIMITS.update(load("experiments/lorentzian_frame_reading/contract.json")["budget"])
    install_limits()
    report, _ = run(args.output)
    print(json.dumps({"status": report["status"], "assertions": report["assertions"]},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
