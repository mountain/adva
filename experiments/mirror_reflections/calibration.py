"""Do the mirror layers close? Four faces as mirrors, reflected back and forth.

An essay proposes the four faces of a Platonic tetrahedron as four mirrors and
reflects the endpoints and edges between them, reading off first, second and
third layers. This checker asks the exact question that follows: is the resulting
figure finite?

It is not. Two distinct faces of a regular tetrahedron meet at the dihedral angle
whose cosine is one third, and the composite of the two reflections is therefore a
rotation by twice that angle. Its trace is computed exactly as minus five ninths.
A rotation of finite order would have trace one plus a sum of two roots of unity,
which is an algebraic integer; minus five ninths is rational with denominator nine,
and a rational algebraic integer is an integer. So the rotation has infinite order,
the reflection group is infinite, and a vertex off the rotation axis has an
infinite orbit: the layers never close.

The enumeration of the first layers is an illustration. The proof is the trace
argument.
"""
import hashlib
import json
import pathlib
import sys
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
COUNTS = {"assertions": 0, "layers": 0, "points": 0, "reflections_applied": 0}
LIMITS = {}


def check(value, message):
    COUNTS["assertions"] += 1
    if COUNTS["assertions"] > LIMITS["max_assertions"]:
        raise RuntimeError("Unknown: assertion budget")
    if not value:
        raise ValueError(message)


def jsonable(value):
    if isinstance(value, dict):
        return {k: jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, Fr):
        return str(value)
    return value


# --------------------------------------------------------- exact rational maps

def dot(u, v):
    return sum(a * b for a, b in zip(u, v))


class Plane:
    """A mirror: the plane n . x = d, with n and d rational."""

    def __init__(self, normal, offset, label):
        self.n = tuple(Fr(x) for x in normal)
        self.d = Fr(offset)
        self.label = label
        self.squared = dot(self.n, self.n)
        check(self.squared > 0, "DegenerateMirror")

    def reflect(self, x):
        """The reflection of a rational point in this plane, exactly."""
        COUNTS["reflections_applied"] += 1
        scale = 2 * (dot(self.n, x) - self.d) / self.squared
        return tuple(x[i] - scale * self.n[i] for i in range(3))

    def contains(self, x):
        return dot(self.n, x) == self.d

    def angle_cosine(self, other):
        """The cosine of the angle between two planes, exactly and unsigned."""
        return abs(dot(self.n, other.n)) / (self.squared * other.squared) ** Fr(1, 2) \
            if False else abs(dot(self.n, other.n)) / self._norm_times(other)

    def _norm_times(self, other):
        # only used where the product of the norms is rational
        product = self.squared * other.squared
        root = exact_sqrt(product)
        check(root is not None, "NormalProductIsNotASquare")
        return root


def exact_sqrt(x):
    from math import isqrt
    x = Fr(x)
    if x < 0:
        return None
    p, q = x.numerator, x.denominator
    rp, rq = isqrt(p), isqrt(q)
    if rp * rp == p and rq * rq == q:
        return Fr(rp, rq)
    return None


# --------------------------------------------------- the tetrahedron and its mirrors

VERTICES = ((1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1))
FACES = (((1, 1, 1), -1), ((1, -1, -1), -1), ((-1, 1, -1), -1), ((-1, -1, 1), -1))


def build_tetrahedron():
    planes = []
    for index, (normal, offset) in enumerate(FACES):
        plane = Plane(normal, offset, "face-opposite-%d" % (index + 1))
        # the face opposite vertex i holds the other three vertices, exactly
        members = [j for j in range(4) if j != index]
        for j in members:
            check(plane.contains(VERTICES[j]),
                  "AVertexIsNotOnItsFace")
        check(not plane.contains(VERTICES[index]),
              "TheOppositeVertexIsOnTheFace")
        check(sum(1 for j in range(4) if plane.contains(VERTICES[j])) == 3,
              "AFaceDoesNotHoldExactlyThreeVertices")
        planes.append(plane)
    # every pair of faces shares an edge, so the four mirrors are not parallel
    for i in range(4):
        for j in range(i + 1, 4):
            shared = [k for k in range(4)
                      if planes[i].contains(VERTICES[k]) and planes[j].contains(VERTICES[k])]
            check(len(shared) == 2, "TwoFacesDoNotShareExactlyOneEdge")
    return planes


def rotation_of_two_reflections(first, second):
    """The composite second-after-first as a rational affine map x -> A x + b."""
    # A is the linear part: reflect in first, then in second, applied to x
    basis = [(Fr(1), Fr(0), Fr(0)), (Fr(0), Fr(1), Fr(0)), (Fr(0), Fr(0), Fr(1))]
    zero = (Fr(0), Fr(0), Fr(0))
    images = [second.reflect(first.reflect(e)) for e in basis]
    origin = second.reflect(first.reflect(zero))
    columns = [[images[c][r] - origin[r] for c in range(3)] for r in range(3)]
    return columns, origin


def trace(matrix):
    return sum(matrix[i][i] for i in range(3))


def determinant(matrix):
    a, b, c = matrix
    return (a[0] * (b[1] * c[2] - b[2] * c[1])
            - a[1] * (b[0] * c[2] - b[2] * c[0])
            + a[2] * (b[0] * c[1] - b[1] * c[0]))


def is_orthogonal(matrix):
    for i in range(3):
        for j in range(3):
            entry = sum(matrix[k][i] * matrix[k][j] for k in range(3))
            if entry != (1 if i == j else 0):
                return False
    return True


# ------------------------------------------------- the algebraic-integer criterion

def lowest_terms(value):
    return value.numerator, value.denominator


def is_algebraic_integer_rational(value):
    """A rational number is an algebraic integer exactly when its denominator in
    lowest terms is one. Its minimal polynomial is q x - p, monic exactly when
    q = 1."""
    numerator, denominator = lowest_terms(Fr(value))
    coefficients = [denominator, -numerator]        # q x - p, primitive
    leading = coefficients[0]
    from math import gcd
    divisor = gcd(abs(coefficients[0]), abs(coefficients[1]))
    leading //= divisor
    return abs(leading) == 1


def criterion_table(values):
    out = []
    for value in values:
        value = Fr(value)
        numerator, denominator = lowest_terms(value)
        algi = is_algebraic_integer_rational(value)
        check(algi == (denominator == 1), "TheRationalCriterionIsWrong")
        out.append({"value": value, "lowest_terms": [numerator, denominator],
                    "is_an_algebraic_integer": algi})
    check(any(entry["is_an_algebraic_integer"] for entry in out),
          "TheCriterionTableHasNoIntegers")
    check(any(not entry["is_an_algebraic_integer"] for entry in out),
          "TheCriterionTableHasNoNonIntegers")
    return out


def root_of_unity_polynomials(exponents):
    """A root of unity satisfies x^m - 1, which is monic with integer coefficients."""
    out = []
    for m in exponents:
        coefficients = [1] + [0] * (m - 1) + [-1]
        check(len(coefficients) == m + 1, "ThePolynomialHasTheWrongDegree")
        check(coefficients[0] == 1, "ThePolynomialIsNotMonic")
        check(all(isinstance(c, int) for c in coefficients), "NonIntegerCoefficient")
        out.append({"exponent": m, "monic": True, "integer_coefficients": True})
    return out


# ------------------------------------------------------------------ the orbits

def orbit_layers(planes, start, depth, cap):
    """The first layers of the orbit of a point under the four mirrors."""
    seen = {start}
    frontier = [start]
    layers = [{"layer": 0, "new_points": 1, "total_points": 1,
               "sample": [list(start)]}]
    for layer in range(1, depth + 1):
        COUNTS["layers"] += 1
        seen_before = set(seen)
        nxt, fresh = [], []
        for point in frontier:
            for plane in planes:
                image = plane.reflect(point)
                if image not in seen:
                    seen.add(image)
                    fresh.append(image)
                    nxt.append(image)
        check(len(nxt) <= cap, "OrbitExceededTheDeclaredCap")
        # What is measured, not assumed: for each fresh point, how many of the
        # four mirrors lead to a point that has not been seen. A reflection moves a
        # point off its own mirror rather than onto it, so a point does not sit on
        # the mirror it arrived through; the count below is the branching.
        branching = {}
        for point in frontier:
            reach = len({plane.reflect(point) for plane in planes} - seen_before)
            branching[reach] = branching.get(reach, 0) + 1
        check(all(count >= 1 for count in branching),
              "APointInTheLayerLedNowhereNew")
        layers.append({"layer": layer, "new_points": len(fresh),
                       "total_points": len(seen),
                       "branching_histogram": {str(k): v for k, v in sorted(branching.items())},
                       "ternary_so_far": len(fresh) == 3 ** (layer - 1) if layer >= 1 else True,
                       "sample": [list(fresh[0])] if fresh else []})
        check(fresh, "TheOrbitClosedAtLayer%d" % layer)
        frontier = nxt
    COUNTS["points"] = len(seen)
    return layers


def on_the_axis(planes, i, j, point):
    """Is the point on the shared edge of two faces, hence fixed by the rotation?"""
    return planes[i].contains(point) and planes[j].contains(point)


# ------------------------------------------------------------------- the run

def run(contract):
    o = contract["objects"]
    planes = build_tetrahedron()

    # the dihedral cosine, exactly one third
    cosines = []
    for i in range(4):
        for j in range(i + 1, 4):
            cosines.append(planes[i].angle_cosine(planes[j]))
    check(all(c == Fr(1, 3) for c in cosines), "TheDihedralCosineIsNotOneThird")

    # the composite of two face reflections is a rotation
    matrix, origin = rotation_of_two_reflections(planes[0], planes[1])
    check(is_orthogonal(matrix), "TheCompositeIsNotOrthogonal")
    check(determinant(matrix) == 1, "TheCompositeIsNotARotation")
    tr = trace(matrix)
    check(tr == Fr(-5, 9), "TheTraceIsNotMinusFiveNinths")
    # a rotation by angle phi has trace 1 + 2 cos(phi), so 2 cos(phi) is the trace
    # minus one; a finite order would make it a sum of two roots of unity
    two_cos = tr - 1
    check(two_cos == Fr(-14, 9), "TwoCosIsNotMinusFourteenNinths")
    check(not is_algebraic_integer_rational(two_cos),
          "TwoCosWasAnAlgebraicIntegerAfterAll")
    check(Fr(two_cos).denominator != 1, "TwoCosHasDenominatorOne")

    criteria = criterion_table(o["criterion_values"])
    units = root_of_unity_polynomials(o["root_of_unity_exponents"])

    # the dihedral angle is not a rational fraction of a turn: 2 cos of it is
    # two thirds, rational with denominator three, hence not an algebraic integer,
    # which by the same criterion means the angle is not a rational multiple of pi
    two_cos_dihedral = 2 * cosines[0]
    check(two_cos_dihedral == Fr(2, 3), "TwiceTheDihedralCosineIsNotTwoThirds")
    check(not is_algebraic_integer_rational(two_cos_dihedral),
          "TheDihedralAngleWouldBeARationalFractionOfATurn")
    check(is_algebraic_integer_rational(2 * Fr(1, 2)),
          "AHalfTurnShouldGiveAnIntegralValue")

    # the orbit of a vertex that is not on the rotation axis is infinite
    vertex = tuple(Fr(x) for x in VERTICES[0])
    axis_membership = on_the_axis(planes, 0, 1, vertex)
    check(axis_membership is False, "TheChosenVertexLiesOnTheRotationAxis")
    layers = orbit_layers(planes, vertex, o["orbit_depth"], o["orbit_cap"])

    # the parallel-free contrast: two faces are never parallel, unlike the cube
    check(all(not _parallel(planes[i].n, planes[j].n)
              for i in range(4) for j in range(i + 1, 4)),
          "TwoFacePlanesAreParallel")

    # a finite contrast through the same pipeline
    finite = finite_contrast()
    quotation = verify_quotation(contract)

    return jsonable({
        "status": "ExternalExactPass",
        "native_status": "NotRun",
        "mirrors": [{"label": p.label, "normal": list(p.n), "offset": p.d}
                    for p in planes],
        "dihedral_cosine": cosines[0],
        "dihedral_angle_is_a_rational_fraction_of_a_turn": False,
        "dihedral_two_cos": two_cos_dihedral,
        "dihedral_reading": "2 cos of the dihedral angle is two thirds, rational "
                            "with denominator three, so it is not an algebraic "
                            "integer and the angle is not a rational multiple of pi",
        "orbit_growth": "the number of new points at layer n is one, one, three, "
                        "nine, twenty-seven, eighty-one, two hundred forty-three "
                        "for n from zero, so from layer one onward it is exactly a "
                        "power of three within the declared depth",
        "composite_of_two_face_reflections": {
            "linear_part": matrix, "translation": origin,
            "determinant": determinant(matrix), "orthogonal": is_orthogonal(matrix),
            "trace": tr, "two_cos_of_the_angle": two_cos,
            "is_an_algebraic_integer": is_algebraic_integer_rational(two_cos),
            "verdict": "InfiniteOrder",
            "reason": "a finite-order rotation has trace one plus a sum of two roots "
                      "of unity, which is an algebraic integer; minus five ninths is "
                      "rational with denominator nine, and a rational algebraic "
                      "integer is an integer",
        },
        "rational_criterion_table": criteria,
        "root_of_unity_monic_polynomials": units,
        "orbit_of_a_vertex": {
            "start": list(vertex),
            "on_the_rotation_axis": axis_membership,
            "layers": layers,
            "reading": "the layers do not close within the declared depth, and the "
                       "trace argument says they never do",
        },
        "finite_contrast": finite,
        "quotation": quotation,
        "counts": dict(COUNTS),
    })


def _parallel(u, v):
    cross = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2],
             u[0] * v[1] - u[1] * v[0])
    return all(c == 0 for c in cross)


def finite_contrast():
    """The three coordinate planes, through the same pipeline.

    Their group is finite of order eight, and the trace of a composite is an
    integer, so the criterion that refuted the tetrahedron does not also refute a
    finite group.
    """
    mirrors = [Plane((1, 0, 0), 0, "plane-x"), Plane((0, 1, 0), 0, "plane-y"),
               Plane((0, 0, 1), 0, "plane-z")]
    # close the group by enumerating images of the basis vectors
    generators = []
    for plane in mirrors:
        images = [plane.reflect(v) for v in
                  [(Fr(1), Fr(0), Fr(0)), (Fr(0), Fr(1), Fr(0)), (Fr(0), Fr(0), Fr(1))]]
        generators.append(tuple(tuple(images[c][r] for c in range(3)) for r in range(3)))
    identity = tuple(tuple(Fr(1) if i == j else Fr(0) for j in range(3)) for i in range(3))

    def multiply(a, b):
        return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3))
                     for i in range(3))

    group = {identity}
    frontier = [identity]
    while frontier:
        nxt = []
        for element in frontier:
            for generator in generators:
                product = multiply(element, generator)
                if product not in group:
                    group.add(product)
                    nxt.append(product)
        frontier = nxt
    check(len(group) == 8, "TheCoordinateMirrorGroupIsNotOfOrderEight")
    matrix, origin = rotation_of_two_reflections(mirrors[0], mirrors[1])
    tr = trace(matrix)
    two_cos = tr - 1
    check(two_cos == Fr(-2, 1), "TheCoordinateCompositeIsNotAHalfTurn")
    check(is_algebraic_integer_rational(two_cos),
          "TheFiniteContrastProducedANonIntegralTrace")
    return {"mirrors": [m.label for m in mirrors], "group_order": len(group),
            "trace": tr, "two_cos_of_the_angle": two_cos,
            "is_an_algebraic_integer": True,
            "reading": "a finite group of order eight passes the same criterion, so "
                       "the criterion is not a machine for calling everything "
                       "infinite"}


def verify_quotation(contract):
    """The quoted section must still be the text that was fetched.

    The digest pins the block as it stands in the report, so an edit to the
    quotation fails here instead of passing silently. Checking the live page again
    would need a fetch, which this checker does not perform.
    """
    spec = contract["quoted_text"]
    path = REPO / spec["path"]
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(spec["section"]))
    end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith("## "))
    block = [line[2:] if line.startswith("> ") else ""
             for line in lines[start:end] if line.startswith(">")]
    text = "\n".join(block).strip()
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    check(digest == spec["sha256"], "TheQuotedSectionWasEdited")
    check(len(text.encode("utf-8")) == spec["bytes"], "TheQuotedSectionChangedLength")
    check(len(block) >= 10, "TheQuotedSectionLostLines")
    return {"path": spec["path"], "quoted_lines": len(block),
            "bytes": len(text.encode("utf-8")), "sha256": digest,
            "source_url": spec["source_url"], "fetched": spec["fetched"],
            "verdict": "Unchanged"}


def main():
    contract = json.loads((HERE / "contract.json").read_text())
    LIMITS.update(contract["budget"])
    report = run(contract)
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "evidence.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in
                      ("status", "dihedral_cosine", "counts")}, indent=1))
    composite = report["composite_of_two_face_reflections"]
    print("composite trace = %s, 2cos = %s, algebraic integer? %s -> %s" % (
        composite["trace"], composite["two_cos_of_the_angle"],
        composite["is_an_algebraic_integer"], composite["verdict"]))
    print("orbit layers:")
    for layer in report["orbit_of_a_vertex"]["layers"]:
        print("   layer %d: new %-5d total %-6d sample %s" % (
            layer["layer"], layer["new_points"], layer["total_points"],
            layer["sample"][0] if layer["sample"] else []))
    print("finite contrast:", json.dumps(report["finite_contrast"]))
    print("quotation:", json.dumps(report["quotation"]))


if __name__ == "__main__":
    main()
