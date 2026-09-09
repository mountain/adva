"""Path-bound Surface phrase calibration: independent reimplementation of the
four-phrase / winding / monodromy checker (own code, same declared math)."""
import json, pathlib
from fractions import Fraction as Q

I = ((1, 0), (0, 1))
A = ((1, 2), (0, 1))
BASES = (I, ((0, -1), (1, 0)), ((1, 1), (0, 1)))
PHRASES = {"绕零孔 正行 1 周": 1, "绕零孔 逆行 1 周": -1,
           "绕零孔 正行 2 周": 2, "绕零孔 逆行 2 周": -2}

class Refusal(Exception):
    pass

def mm(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(2)) for j in range(2)) for i in range(2))

def mv(m, v):
    return tuple(sum(m[i][j] * v[j] for j in range(2)) for i in range(2))

def mat_pow(m, w):
    out = I
    base = m if w > 0 else inverse(m)
    for _ in range(abs(w)):
        out = mm(out, base)
    return out

def inverse(b):
    if b is None:
        raise Refusal("UnknownBasis")
    a, c = b[0]; d, e = b[1]
    if a * e - c * d != 1:
        raise Refusal("InvalidBasis")
    return ((e, -c), (-d, a))

def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]

def winding(path, base):
    if not 2 <= len(path) <= 32:
        raise Refusal("UnknownVertexBudget")
    if path[0] != base or path[-1] != base:
        raise Refusal("WrongBasepoint" if path[0] != base else "OpenPath")
    for p in path:
        norm = sum(v * v for v in p)
        if norm == 0:
            raise Refusal("OriginVertex")
        if norm >= Q(1, 4):
            raise Refusal("OutsideLocalDisk")
    total = 0
    for a, b in zip(path, path[1:]):
        det = cross(a, b)
        if det == 0 and sum(a[i] * b[i] for i in range(2)) <= 0:
            raise Refusal("OriginOnEdge")
        if a[1] <= 0 < b[1] and det > 0:
            total += 1
        elif b[1] <= 0 < a[1] and det < 0:
            total -= 1
    return total

def check(phrase, path, base, basis):
    if phrase not in PHRASES:
        raise Refusal("UnsupportedPhrase")
    w = winding(path, base)
    if w != PHRASES[phrase]:
        raise Refusal("DirectionOrTurnMismatch")
    standard = mat_pow(A, w)
    action = mm(mm(inverse(basis), standard), basis)
    q = (0, 1)
    if mv(basis, mv(action, mv(inverse(basis), q))) != mv(standard, q):
        raise Refusal("BasisTransportFailed")
    return {"status": "MatchedFiniteScope", "winding": w, "action": action}

def diamond(radius, turns):
    zero = Q(0)
    path = ((radius, zero), (zero, radius), (-radius, zero), (zero, -radius), (radius, zero))
    if turns < 0:
        path = path[::-1]
    return path + path[1:] * (abs(turns) - 1)

# positive set: 4 phrases x 3 radii x 3 bases
pos = []
for phrase, turns in PHRASES.items():
    for radius in (Q(1, 8), Q(1, 16), Q(1, 32)):
        for basis in BASES:
            pos.append(check(phrase, diamond(radius, turns), (radius, Q(0)), basis))
c_pos = all(r["status"] == "MatchedFiniteScope" for r in pos)
print('positive set:', len(pos), 'cases ->', c_pos)

# fresh six-vertex polygon, new basis
fresh = ((Q(1, 10), Q(0)), (Q(1, 10), Q(1, 7)), (Q(-1, 8), Q(1, 7)),
         (Q(-1, 8), Q(-1, 9)), (Q(1, 10), Q(-1, 9)), (Q(1, 10), Q(0)))
fresh_basis = ((1, 2), (1, 3))
c_fresh = check("绕零孔 正行 1 周", fresh, fresh[0], fresh_basis)["status"] == "MatchedFiniteScope"
print('fresh polygon + basis ((1,2),(1,3)):', c_fresh)

# diamond witness: endpoint closure != identity transport
path = diamond(Q(1, 8), 1)
w_plus = winding(path, path[0])
transport_plus = mv(A, (0, 1))
w_minus = winding(diamond(Q(1, 8), -1), (Q(1, 8), Q(0)))
transport_minus = mv(mat_pow(A, -1), (0, 1))
c_witness = (w_plus == 1 and transport_plus == (2, 1) != (0, 1)
             and w_minus == -1 and transport_minus == (-2, 1))
print('diamond witness (closure != identity):', c_witness)

# controls
controls = {}
def expect_refusal(name, fn):
    try:
        fn()
        controls[name] = False
    except Refusal as e:
        controls[name] = str(e)

expect_refusal('reversed-path', lambda: check("绕零孔 正行 1 周", diamond(Q(1, 8), -1), (Q(1, 8), Q(0)), I))
expect_refusal('closure-alone', lambda: check("闭合", path, path[0], I))
expect_refusal('missing-basis', lambda: check("绕零孔 正行 1 周", path, path[0], None))
c_ctrl = all(controls.values())
print('controls:', controls)

# scope counterexample: commutator != I on the three-punctured sphere
B1 = ((1, 0), (-2, 1))
comm = mm(A, mm(B1, mm(mat_pow(A, -1), inverse(B1))))
c_scope = (comm == ((13, 8), (8, 5)) != I)
print('scope counterexample A B1 A^-1 B1^-1 =', comm, '->', c_scope)

status = 'MatchedFiniteScope' if (c_pos and c_fresh and c_witness and c_ctrl and c_scope) else 'Rejected'
report = {
  "schema": "aeg.path-bound-surface.result.research", "version": 0,
  "status": status,
  "evidence": {"positive_cases": len(pos), "fresh_polygon": c_fresh,
               "diamond_witness": c_witness,
               "controls": controls, "scope_counterexample": c_scope},
  "notes": ["independent reimplementation of the declared math (own code)",
            "the other side's doc reports mountain/AEG as 404: our AEG repository remains local-only (recorded hole)"],
  "no_claims": ["no native admission", "no global monodromy promotion", "no phrase semantics beyond the four entries"]
}
pathlib.Path('report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
print('status:', status)
