"""Yau's Calabi journey as an arithmetic relation, read through our materials.
Five anchors, all exact Fractions; the mapping is proposed, not an identification."""
import json, pathlib
from fractions import Fraction as Q

I3 = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
I2 = ((1, 0), (0, 1))
A = ((1, 2), (0, 1))
B1 = ((1, 0), (-2, 1))
C = ((0, 1, 0), (0, 0, 1), (1, 0, 0))

def mm(a, b):
    n = len(a); m = len(b[0]); p = len(b)
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(p)) for j in range(m)) for i in range(n))

def mv(m, v):
    return tuple(sum(m[i][j] * v[j] for j in range(len(v))) for i in range(len(m)))

def det3(m):
    a, b, c = m
    return (a[0]*(b[1]*c[2]-b[2]*c[1]) - a[1]*(b[0]*c[2]-b[2]*c[0]) + a[2]*(b[0]*c[1]-b[1]*c[0]))

def scale(m, k):
    return tuple(tuple(Q(x) / k for x in row) for row in m)

def inv2(m):
    a, b = m[0]; c, d = m[1]
    det = a*d - b*c
    return ((Q(d)/det, Q(-b)/det), (Q(-c)/det, Q(a)/det))

def mat_pow2(m, w):
    out = I2
    base = m if w >= 0 else inv2(m)
    for _ in range(abs(w)):
        out = mm(out, base)
    return out

# Anchor 1: system -> scalar. L = (2I+C)/3; det(L) = 1/3.
L = scale(tuple(tuple(2*I3[i][j] + C[i][j] for j in range(3)) for i in range(3)), 3)
a1 = (det3(L) == Q(1, 3))
# and the recoverability identity (2I+C)(4I-2C+C^2) = 9I
C2 = mm(C, C)
nine_I = tuple(tuple(9*I3[i][j] for j in range(3)) for i in range(3))
lhs = mm(tuple(tuple(2*I3[i][j] + C[i][j] for j in range(3)) for i in range(3)),
         tuple(tuple(4*I3[i][j] - 2*C[i][j] + C2[i][j] for j in range(3)) for i in range(3)))
a1b = (lhs == nine_I)
print('A1 det(L) =', det3(L), '| (2I+C)(4I-2C+C^2) = 9I:', a1b)

# Anchor 2: winding as topological invariant (closed path, half-open convention)
# verified in receipt-13; here re-verify the diamond and its reverse.
def winding(path):
    total = 0
    for a, b in zip(path, path[1:]):
        det = a[0]*b[1] - a[1]*b[0]
        if a[1] <= 0 < b[1] and det > 0: total += 1
        elif b[1] <= 0 < a[1] and det < 0: total -= 1
    return total
def diamond(r):
    z = Q(0)
    return ((r, z), (z, r), (-r, z), (z, -r), (r, z))
w_plus = winding(diamond(Q(1, 8)))
w_minus = winding(tuple(reversed(diamond(Q(1, 8)))))
a2 = (w_plus == 1 and w_minus == -1)
print('A2 winding +1/-1:', w_plus, w_minus)

# Anchor 3: vanishing class -> local identity. A^0 = I; and A^w exact for w = +-1, +-2.
a3 = (mat_pow2(A, 0) == I2 and mat_pow2(A, 1) == A
      and mm(mat_pow2(A, 1), mat_pow2(A, -1)) == I2
      and mm(mat_pow2(A, 2), mat_pow2(A, -2)) == I2)
print('A3 A^0=I, A^w A^-w=I:', a3)

# Anchor 4: first nontrivial example. Diamond has closure yet transport != identity.
a4 = (mv(A, (0, 1)) == (2, 1) != (0, 1))
print('A4 A(0,1) =', mv(A, (0, 1)), '!= (0,1):', a4)

# Anchor 5: too good to be true -> scope guard. Commutator != I.
comm = mm(A, mm(B1, mm(inv2(A), inv2(B1))))
a5 = (comm == ((13, 8), (8, 5)) != I2)
print('A5 A B1 A^-1 B1^-1 =', comm, '!= I:', a5)

# Control: tampered matrix breaks anchor 4.
A_t = ((1, 3), (0, 1))
c_tamper = (mv(A_t, (0, 1)) != (2, 1))
# Control: promoting the local rule globally is refused by the commutator.
c_scope = (mv(comm, (1, 0)) != (1, 0))

status = 'MatchedFiniteScope' if (a1 and a1b and a2 and a3 and a4 and a5 and c_tamper and c_scope) else 'Rejected'
report = {
  "schema": "aeg.yau-calabi-narrative.result.research", "version": 0,
  "status": status,
  "mapping": {
    "narrative": ["system -> scalar equation", "curvature = topological invariant (first Chern class)",
                  "c1 = 0 vanishing condition", "first nontrivial example (K3)",
                  "too good to be true -> six-year verification"],
    "our_language": ["three cyclic expressions -> det(L) = 1/3",
                     "winding number as the path's topological invariant",
                     "local rule w=0 => identity action",
                     "diamond witness: closure != identity (A(0,1) = (2,1))",
                     "scope counterexample A B1 A^-1 B1^-1 = ((13,8),(8,5)) and the receipt chain 01-16"],
    "status": "proposed-mapping (human review pending)"
  },
  "evidence": {"A1_det_scalar": str(det3(L)), "A1_recoverability": a1b,
               "A2_winding": [w_plus, w_minus], "A3_zero_class": a3,
               "A4_first_nontrivial": a4, "A5_scope_guard": a5,
               "controls": {"tampered_matrix": c_tamper, "local_rule_not_global": c_scope}},
  "no_claims": ["this is a proposed correspondence, not an identification of our materials with Calabi-Yau geometry",
                "no native admission", "no catalog entry in this round"]
}
pathlib.Path('report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
print('status:', status)
