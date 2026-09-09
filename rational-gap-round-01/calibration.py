"""Rational-gap criterion and the simplex caveats from #167, exact Fractions."""
import json, math, pathlib
from fractions import Fraction as Q

# 1. rational gap criterion: R = N/D, N,D in Z, 0 < D <= B.
# |R| < 1/B  =>  N = 0. Exhaustive small check of the contrapositive.
B = 100
contrapositive = True
for N in range(-5, 6):
    if N == 0:
        continue
    for D in range(1, B + 1):
        R = Q(N, D)
        if abs(R) < Q(1, B):
            contrapositive = False
# positive instance
zero_ok = (abs(Q(0, 7)) < Q(1, B))
# scope counterexample: D > B breaks the bridge
scope_break = (abs(Q(1, 101)) < Q(1, 100))  # 1/101 < 1/100 with N != 0
print('1. gap criterion: contrapositive exhaustive:', contrapositive,
      '| zero certified:', zero_ok, '| D>B breaks bridge:', scope_break)

# 2. projective gauge: det(lambda X, lambda Y, lambda Z) = lambda^3 det(X,Y,Z)
def det3(a, b, c):
    return (a[0]*(b[1]*c[2]-b[2]*c[1]) - a[1]*(b[0]*c[2]-b[2]*c[0]) + a[2]*(b[0]*c[1]-b[1]*c[0]))
X, Y, Z = (1,0,0), (0,1,0), (0,0,1)
lam = Q(1, 1024)
det_orig = Q(det3(X, Y, Z))
det_scaled = Q(det3((lam,0,0),(0,lam,0),(0,0,lam)))
gauge = (det_orig == 1 and det_scaled == Q(1, 1073741824) and det_scaled == lam**3 * det_orig)
print('2. projective gauge: det=1 -> lam^3 =', det_scaled, '| exact:', gauge)

# 3. observer-relative: Q_eps(x) = floor(x/eps), eps=1, interval [3/4, 5/4]
eps = 1
obs = [math.floor(Q(3,4)/eps), math.floor(Q(5,4)/eps)]
observer = (obs == [0, 1] and Q(5,4) - Q(3,4) < eps)
print('3. observer-relative: width 1/2 < eps yet two observed values:', obs, '->', observer)

# 4. shrink count formula: D_m = sigma^m D_0; m >= ceil(log(D0/eps)/log(1/sigma))
sigma, D0 = Q(1, 2), Q(1)
eps_t = Q(1, 1024)
m_needed = math.ceil(math.log(float(D0/eps_t)) / math.log(1/float(sigma)))
m_exact = 10
shrink_ok = (sigma**m_exact * D0 <= eps_t and sigma**(m_exact-1) * D0 > eps_t and m_needed == m_exact)
print('4. shrink count: m =', m_needed, '| D_10 =', sigma**10, '<= eps | D_9 =', sigma**9, '> eps:', shrink_ok)

status = 'MatchedFiniteScope' if (contrapositive and zero_ok and scope_break
                                  and gauge and observer and shrink_ok) else 'Rejected'
report = {
  "schema": "aeg.rational-gap.result.research", "version": 0,
  "status": status,
  "evidence": {
    "gap_criterion": {"contrapositive_exhaustive_5x100": contrapositive,
                      "zero_certified": zero_ok, "D_gt_B_breaks_bridge": scope_break},
    "projective_gauge": {"lambda3_det": str(det_scaled), "exact": gauge},
    "observer_relative": {"observed_values": obs, "width_lt_cell": observer},
    "shrink_count": {"m": m_exact, "D10_le_eps": shrink_ok},
  },
  "documented_holes": [
    "McKinnon's nonstationary-convergence construction is not re-run here (documentary caveat: small diameter does not imply a root or proof)",
    "the whole-run shrink formula is invalidated by intervening reflection/expansion (declared in the source doc)",
  ],
  "no_claims": ["no promotion to geometric or native claims", "exact Fractions only"]
}
pathlib.Path('report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
print('status:', status)
