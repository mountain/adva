"""Construct an external commutator certificate; never native Adva authority.

Authored by ChatGPT (OpenAI), through Mingli Yuan's account as proxy.
The checker deliberately does not import this module.
"""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PINS = {
    "pascal-task.adva": "60d3ca374486239afb82bbe31d821a4d0c02ef947ccf62557753e85137087a5d",
    "pascal-witness.adva": "f20338add39c292db6bac482a2c9265353d6a5a1a5189cc2823398ddc29fe448",
}


class FreePoly:
    def __init__(self, terms):
        self.terms = {w: c for w, c in terms.items() if c}

    def __add__(self, other):
        out = self.terms.copy()
        for w, c in other.terms.items():
            out[w] = out.get(w, 0) + c
        return FreePoly(out)

    def __neg__(self):
        return FreePoly({w: -c for w, c in self.terms.items()})

    def __sub__(self, other):
        return self + -other

    def __mul__(self, other):
        out = {}
        for u, c in self.terms.items():
            for v, d in other.terms.items():
                out[u + v] = out.get(u + v, 0) + c * d
        return FreePoly(out)


def polynomial(text):
    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return FreePoly({(): node.value})
        if isinstance(node, ast.Name) and node.id in ("d", "e", "f"):
            return FreePoly({(node.id,): 1})
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -visit(node.operand)
        if isinstance(node, ast.BinOp):
            a, b = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                return a + b
            if isinstance(node.op, ast.Sub):
                return a - b
            if isinstance(node.op, ast.Mult):
                return a * b
        raise ValueError("outside the fixed polynomial grammar")
    return visit(ast.parse(text, mode="eval").body)


def load_inputs():
    docs = {}
    for name, expected in PINS.items():
        path = ROOT / "adva-library" / name
        if path.stat().st_size > 32768:
            raise ValueError("input exceeds bound")
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError("input pin mismatch: " + name)
        docs[name] = json.loads(data)
    return docs["pascal-task.adva"], docs["pascal-witness.adva"]


def expressions(task, witness):
    points = task["input"]["method"]["point_coordinates"]
    lines = witness["proof"]["lines"]
    def dot(line, point):
        return "+".join("(" + a + ")*(" + b + ")" for a, b in zip(line, point))
    result = []
    for name, (u, v, w) in points.items():
        result.append((name + ":conic", f"({u})*({w})-({v})*({v})"))
    for name, line in lines.items():
        for point in name:
            result.append((point + ":" + name, dot(line, points[point])))
    for p in witness["presentations"]:
        for name in p["incidence_lines"]:
            result.append((p["construction"] + ":" + name, dot(lines[name], p["public_point"])))
        result.append((p["construction"] + ":Pascal", dot(witness["proof"]["pascal_line"], p["public_point"])))
    result.append(("auxiliary:displayed-residual", witness["proof"]["third_point_residual"]))
    return result


def decompose(poly):
    """P-NF(P) telescopes over adjacent inversions, retaining every context."""
    summands, normal = [], {}
    for word, coefficient in sorted(poly.terms.items()):
        current = list(word)
        while True:
            j = next((i for i in range(len(current) - 1) if current[i] > current[i + 1]), None)
            if j is None:
                break
            summands.append({"coefficient": coefficient, "left": current[:j],
                             "a": current[j], "b": current[j + 1], "right": current[j + 2:]})
            current[j], current[j + 1] = current[j + 1], current[j]
        key = tuple(current)
        normal[key] = normal.get(key, 0) + coefficient
    if any(normal.values()):
        raise ValueError("nonzero commutative residual")
    if len(summands) > 128:
        raise ValueError("certificate exceeds declared bound")
    return summands


def main():
    task, witness = load_inputs()
    equations = []
    for name, text in expressions(task, witness):
        poly = polynomial(text)
        equations.append({"id": name,
                          "raw_residual": [[list(w), c] for w, c in sorted(poly.terms.items())],
                          "commutator_summands": decompose(poly)})
    if len(equations) != 28:
        raise ValueError("wrong obligation count")
    certificate = {"schema": "adva.external.pascal-commutator-certificate.v0",
                   "source_sha256": PINS, "incidence_convention": "line-coefficients-on-left",
                   "assumed_commuting_pairs": [["d", "e"], ["d", "f"], ["e", "f"]],
                   "equations": equations}
    print(json.dumps(certificate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
