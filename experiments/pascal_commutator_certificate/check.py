"""Independent external replay: expand signed words; never commute them.

No generator import, no SymPy, no evaluation of certificate-supplied code.
Shared trusted base: CPython integers, AST parsing, JSON and pinned input bytes.
Authored by ChatGPT (OpenAI), through Mingli Yuan's account as proxy.
"""
import ast
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PINS = {
    "pascal-task.adva": "60d3ca374486239afb82bbe31d821a4d0c02ef947ccf62557753e85137087a5d",
    "pascal-witness.adva": "f20338add39c292db6bac482a2c9265353d6a5a1a5189cc2823398ddc29fe448",
}
PAIRS = [("d", "e"), ("d", "f"), ("e", "f")]


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_json(path, limit):
    require(path.stat().st_size <= limit, "file exceeds bound")
    return json.loads(path.read_bytes(), object_pairs_hook=unique_object)


def collect(terms):
    """Cancel only identical ordered words; Counter's positive-only ops avoided."""
    counts = Counter()
    for coefficient, word in terms:
        counts[word] += coefficient
    return {word: coefficient for word, coefficient in counts.items() if coefficient}


def expand(text):
    """Uncollected distributive expansion, separately implemented from generator."""
    require(type(text) is str and len(text) <= 512, "expression bound")
    tree = ast.parse(text, mode="eval")
    require(sum(1 for _ in ast.walk(tree)) <= 256, "AST bound")
    def walk(node):
        if isinstance(node, ast.Constant):
            require(type(node.value) is int and abs(node.value) <= 1000000, "literal")
            return [(node.value, ())]
        if isinstance(node, ast.Name):
            require(node.id in ("d", "e", "f"), "variable")
            return [(1, (node.id,))]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return [(-c, w) for c, w in walk(node.operand)]
        require(isinstance(node, ast.BinOp), "grammar")
        left, right = walk(node.left), walk(node.right)
        if isinstance(node.op, ast.Add):
            output = left + right
        elif isinstance(node.op, ast.Sub):
            output = left + [(-c, w) for c, w in right]
        else:
            require(isinstance(node.op, ast.Mult), "operation")
            output = [(c * d, u + v) for c, u in left for d, v in right]
        require(len(output) <= 4096 and all(len(w) <= 16 for _, w in output), "expansion bound")
        return output
    return collect(walk(tree.body))


def source_equations():
    documents = []
    for name, expected in PINS.items():
        path = ROOT / "adva-library" / name
        require(path.stat().st_size <= 32768, "source bound")
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == expected, "source bytes changed")
        documents.append(json.loads(raw, object_pairs_hook=unique_object))
    task, witness = documents
    p = task["input"]["method"]["point_coordinates"]
    l = witness["proof"]["lines"]
    out = {}
    for name in "ABCDEF":
        u, v, w = p[name]
        out[name + ":conic"] = expand(f"({u})*({w})-({v})*({v})")
    def pairing(line, point):
        contributions = []
        for index in range(3):
            component = expand("(" + line[index] + ")*(" + point[index] + ")")
            contributions.extend((c, w) for w, c in component.items())
        return collect(contributions)
    for edge in ("AB", "BC", "CD", "DE", "EF", "FA"):
        for name in edge:
            out[name + ":" + edge] = pairing(l[edge], p[name])
    presentations = {item["construction"]: item for item in witness["presentations"]}
    for point, edges in (("X", ("AB", "DE")), ("Y", ("BC", "EF")), ("Z", ("CD", "FA"))):
        coords = presentations[point]["public_point"]
        require(presentations[point]["incidence_lines"] == list(edges), "incidence binding")
        for edge in edges:
            out[point + ":" + edge] = pairing(l[edge], coords)
        out[point + ":Pascal"] = pairing(witness["proof"]["pascal_line"], coords)
    out["auxiliary:displayed-residual"] = expand(witness["proof"]["third_point_residual"])
    require(len(out) == 28, "source obligation count")
    return out


def word(value):
    require(type(value) is list and len(value) <= 16, "word bound")
    require(all(type(v) is str and v in ("d", "e", "f") for v in value), "word alphabet")
    return tuple(value)


def integer(value):
    require(type(value) is int and 0 < abs(value) <= 1000000, "coefficient bound/type")
    return value


def verify(certificate):
    expected = source_equations()
    require(type(certificate) is dict and set(certificate) == {
        "schema", "source_sha256", "incidence_convention", "assumed_commuting_pairs", "equations"}, "certificate fields")
    require(certificate["schema"] == "adva.external.pascal-commutator-certificate.v0", "schema")
    require(certificate["source_sha256"] == PINS, "source pin declaration")
    require(certificate["incidence_convention"] == "line-coefficients-on-left", "convention")
    pairs = certificate["assumed_commuting_pairs"]
    require(type(pairs) is list and len(pairs) <= 3, "assumption bound")
    for pair in pairs:
        require(type(pair) is list and len(pair) == 2 and tuple(pair) in PAIRS, "pair declaration")
    allowed = {tuple(pair) for pair in pairs}
    require(len(allowed) == len(pairs), "duplicate assumption")
    rows = certificate["equations"]
    require(type(rows) is list and len(rows) == 28, "complete coverage")
    seen, used, summands_total = set(), set(), 0
    for row in rows:
        require(type(row) is dict and set(row) == {"id", "raw_residual", "commutator_summands"}, "row fields")
        name = row["id"]
        require(type(name) is str and name in expected and name not in seen, "equation identity")
        seen.add(name)
        raw = row["raw_residual"]
        require(type(raw) is list and len(raw) <= 128, "raw residual bound")
        raw_terms, raw_seen = [], set()
        for item in raw:
            require(type(item) is list and len(item) == 2, "raw term")
            w, c = word(item[0]), integer(item[1])
            require(w not in raw_seen, "duplicate raw term")
            raw_seen.add(w)
            raw_terms.append((c, w))
        require(collect(raw_terms) == expected[name], "source expression residual mismatch")
        summands = row["commutator_summands"]
        require(type(summands) is list and len(summands) <= 128, "summand bound")
        expansion = []
        for term in summands:
            require(type(term) is dict and set(term) == {"coefficient", "left", "a", "b", "right"}, "summand fields")
            c = integer(term["coefficient"])
            u, v = word(term["left"]), word(term["right"])
            a, b = word([term["a"]]), word([term["b"]])
            require(a != b and len(u + a + b + v) <= 16, "nontrivial bounded swap")
            pair = tuple(sorted((a[0], b[0])))
            require(pair in allowed, "missing commutation assumption")
            used.add(pair)
            expansion.extend([(c, u + a + b + v), (-c, u + b + a + v)])
        require(collect(expansion) == expected[name], "commutator identity mismatch")
        summands_total += len(summands)
    require(seen == set(expected), "coverage")
    # Exact necessity witnesses for this algebraic system, not ring geometry.
    require(expected["D:DE"] == expand("d*e-e*d"), "de necessity")
    require(expected["E:EF"] == expand("e*f-f*e"), "ef necessity")
    require(expected["Z:FA"] == expand("d*f-f*d"), "df necessity")
    require(expected["Z:Pascal"] == expand("(d*e-e*d)*(1-f)+(1-e)*(d*f-f*d)"), "literal incidence decomposition")
    require(expected["auxiliary:displayed-residual"] == expand("d*(e*d-d*e)"), "auxiliary decomposition")
    return {"status": "VerifiedConditionalAlgebraicCertificate", "geometric_equations": 27,
            "auxiliary_equations": 1, "nonzero_geometric_raw_residuals": [k for k, v in expected.items() if v and not k.startswith("auxiliary:")],
            "summands_checked": summands_total, "used_commuting_pairs": [list(p) for p in sorted(used)],
            "algebraic_equivalence": "All 27 equations hold iff d,e,f commute pairwise in a unital associative ring.",
            "native_admission": "NotGranted", "q4_native_fillers": 0,
            "literal_lift_differs_from_displayed_residual": expected["Z:Pascal"] != expected["auxiliary:displayed-residual"]}


def controls(certificate):
    results = []
    def reject(name, change):
        altered = copy.deepcopy(certificate)
        change(altered)
        try:
            verify(altered)
        except (ValueError, TypeError, KeyError, SyntaxError) as error:
            results.append({"name": name, "status": "Rejected", "reason": str(error)})
        else:
            raise ValueError("negative control accepted: " + name)
    def active(doc):
        return next(r for r in doc["equations"] if r["commutator_summands"])
    reject("deleted-summand", lambda d: active(d)["commutator_summands"].pop())
    reject("sign-change", lambda d: active(d)["commutator_summands"][0].__setitem__("coefficient", -active(d)["commutator_summands"][0]["coefficient"]))
    reject("forged-variable", lambda d: active(d)["commutator_summands"][0].__setitem__("a", "x"))
    reject("omitted-equation", lambda d: d["equations"].pop())
    reject("duplicate-equation", lambda d: d["equations"].__setitem__(0, copy.deepcopy(d["equations"][1])))
    reject("wrong-source-pin", lambda d: d["source_sha256"].__setitem__("pascal-task.adva", "0" * 64))
    reject("boolean-coefficient", lambda d: active(d)["commutator_summands"][0].__setitem__("coefficient", True))
    for pair in PAIRS:
        reject("missing-" + "".join(pair), lambda d, pair=pair: d["assumed_commuting_pairs"].remove(list(pair)))
    reject("forged-zero-raw-residual", lambda d: active(d).__setitem__("raw_residual", []))
    # Line-on-left incidence and the commutatively rewritten display are different lifts.
    def substitute_lift(doc):
        source = next(r for r in doc["equations"] if r["id"] == "auxiliary:displayed-residual")
        target = next(r for r in doc["equations"] if r["id"] == "Z:Pascal")
        target.update(copy.deepcopy(source))
        target["id"] = "Z:Pascal"
    reject("unannounced-lift-substitution", substitute_lift)
    def matmul(a, b):
        return [[sum(a[i][k] * b[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
    a, m = [[1, 1], [0, 1]], [[2, 0], [0, 1]]
    ma, am = matmul(m, a), matmul(a, m)
    require(ma != am and ma[0][1] - am[0][1] == 1, "ACS noncommutation control")
    return {"status": "Passed", "rejected_certificates": results,
            "acs_control": {"add_then_scale": ma, "scale_then_add": am, "same_charge": {"A": 1, "exp_M": 2}, "translation_defect": 1},
            "independent_implementation": "checker expands uncollected signed words; imports no generator algebra or sorting routine"}


def main():
    require(len(sys.argv) in (2, 3), "usage: check.py CERTIFICATE [--controls]")
    certificate = read_json(Path(sys.argv[1]), 262144)
    result = controls(certificate) if len(sys.argv) == 3 and sys.argv[2] == "--controls" else verify(certificate)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
