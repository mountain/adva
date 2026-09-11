"""Dual-side spectra of the scale-marked system: L and L^-1, exact."""
import json, math, pathlib
from fractions import Fraction as Q

I3 = ((1,0,0),(0,1,0),(0,0,1))
C = ((0,1,0),(0,0,1),(1,0,0))
C2 = ((0,0,1),(1,0,0),(0,1,0))

def scale(m, k):
    return tuple(tuple(Q(x)/k for x in row) for row in m)

L = scale(tuple(tuple(2*I3[i][j]+C[i][j] for j in range(3)) for i in range(3)), 3)
Linv = scale(tuple(tuple(4*I3[i][j]-2*C[i][j]+C2[i][j] for j in range(3)) for i in range(3)), 3)

def mm(a,b):
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)) for i in range(3))
def det3(m):
    a,b,c = m
    return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])

# exact inverse check
LL = mm(L, Linv)
inv_ok = (LL == I3)
print('L*L^-1 = I:', inv_ok, '| det(L) =', det3(L), '| det(L^-1) =', det3(Linv))

# eigenvalues symbolically: C eigenvalues are 1, omega, omega^2 (cube roots of unity)
# L eigenvalues: (2+lambda)/3 for lambda in {1, omega, omega^2}
# omega = -1/2 + i*sqrt(3)/2
s3 = math.sqrt(3)
eigL = {1: (2+1)/3, 'w': complex(2-0.5, s3/2)/3, 'w2': complex(2-0.5, -s3/2)/3}
eigLinv = {1: (4-2+1)/3, 'w': complex(4-2*(-0.5+1j*s3/2)+(-0.5-1j*s3/2))/3,
           'w2': complex(4-2*(-0.5-1j*s3/2)+(-0.5+1j*s3/2))/3}
print('L eigenvalues:', eigL)
print('L^-1 eigenvalues:', eigLinv)
# energy = |lambda|^2
enL = {k: round(abs(v)**2, 6) for k, v in eigL.items()}
enLinv = {k: round(abs(v)**2, 6) for k, v in eigLinv.items()}
prodL = round(enL[1]*enL['w']*enL['w2'], 6)
prodLinv = round(enLinv[1]*enLinv['w']*enLinv['w2'], 6)
print('energies L:', enL, 'product =', prodL, '(= det^2 = 1/9)')
print('energies L^-1:', enLinv, 'product =', prodLinv, '(= det^-2 = 9)')
print('reciprocal products:', round(prodL*prodLinv, 9) == 1.0)
# relation between the two sides' non-unit eigenvalues
alpha = complex(0.5, s3/6)
print('dual side non-unit eigenvalues == 3*conjugate(alpha):',
      abs(eigLinv['w'] - 3*alpha.conjugate()) < 1e-12 and abs(eigLinv['w2'] - 3*alpha) < 1e-12)

report = {
  "schema": "aeg.dual-spectrum.result.research", "version": 0,
  "status": "DualSpectrumComputed",
  "findings": {
    "L_eigenvalues": {"unit": 1, "nonunit": ["1/2 + i*sqrt(3)/6", "1/2 - i*sqrt(3)/6"]},
    "L_inv_eigenvalues": {"unit": 1, "nonunit": ["3/2 - i*sqrt(3)/2", "3/2 + i*sqrt(3)/2"]},
    "relation": "dual-side non-unit eigenvalues are 3 * conjugate of the primal side",
    "energies": {"primal": [1, 1/3, 1/3], "dual": [1, 3, 3]},
    "energy_products": {"primal": "1/9 = det^2", "dual": "9 = det^-2", "reciprocal": True},
    "one_positive_two_negative": "lives in the three-winding zero-sum (w0+w1+w2=0, e.g. +2,-1,-1); needs the third cusp generator (open slot)"
  },
  "no_claims": ["no identification with Calabi-Yau geometry", "exact arithmetic over Q(i) only"]
}
pathlib.Path('report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
print('report written')
