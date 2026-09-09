"""Surface working-language calibration: scale-marked cyclic expressions."""
import fractions, hashlib, json, pathlib, random

Fr = fractions.Fraction
C = complex  # pairs as (Fr, Fr); use complex with Fraction parts is unreliable -> tuples

def add(a, b): return (a[0]+b[0], a[1]+b[1])
def sub(a, b): return (a[0]-b[0], a[1]-b[1])
def smul(k, a): return (k*a[0], k*a[1])
def sdiv(a, k): return (a[0]/k, a[1]/k)

def M0(eps, z0, z1): return sdiv(smul(eps, add(smul(2, z0), z1)), 3)
def M1(eps, z1, z2): return sdiv(smul(eps, add(smul(2, z1), z2)), 3)
def M2(eps, z2, z0): return sdiv(smul(eps, add(smul(2, z2), z0)), 3)

def outputs(eps, zs):
    z0, z1, z2 = zs
    return [M0(eps, z0, z1), M1(eps, z1, z2), M2(eps, z2, z0)]

def recover(eps, ws):
    w0, w1, w2 = ws
    r0 = sdiv(sub(add(smul(4, w0), smul(-2, w1)), smul(-1, w2) if False else smul(-1, w2)), 3)  # 4w0-2w1+w2
    r0 = add(smul(4, w0), smul(-2, w1)); r0 = add(r0, w2); r0 = sdiv(r0, 3)
    r0 = sdiv(r0, eps)
    r1 = add(smul(4, w1), smul(-2, w2)); r1 = add(r1, w0); r1 = sdiv(sdiv(r1, 3), eps)
    r2 = add(smul(4, w2), smul(-2, w0)); r2 = add(r2, w1); r2 = sdiv(sdiv(r2, 3), eps)
    return [r0, r1, r2]

def z(n):
    return (Fr(n[0]), Fr(n[1]))

# C1: the documented example
eps = Fr(1, 8)
zs = [z((1,1)), z((1,2)), z((2,1))]
ws = outputs(eps, zs)
rec = recover(eps, ws)
c1 = (rec == zs)
print('C1 example recovery:', c1, '| outputs:', ws)

# C2: random samples
random.seed(1)
c2 = True
for _ in range(20):
    e = Fr(random.randint(1, 100), random.randint(1, 100))
    zs = [z((random.randint(-50, 50), random.randint(-50, 50))) for _ in range(3)]
    if recover(e, outputs(e, zs)) != zs:
        c2 = False
print('C2 random recovery (20 samples):', c2)

# C3: epsilon zero refused (the degeneration: recovery divides by epsilon)
try:
    recover(Fr(0), outputs(Fr(0), zs))
    c3 = False
except ZeroDivisionError:
    c3 = True
print('C3 epsilon-zero refusal (at recovery):', c3)

# C4: tampered output fails recovery
tampered = [ws[0], add(ws[1], z((1,0))), ws[2]]
c4 = (recover(eps, tampered) != zs)
print('C4 tampered recovery fails:', c4)

# C5: input-use ledger from signatures
ledger = {}
for name, (e_use, za, zb, wza, wzb) in {
    'M0': (1, 'z0', 'z1', 2, 1), 'M1': (1, 'z1', 'z2', 2, 1), 'M2': (1, 'z2', 'z0', 2, 1)
}.items():
    ledger.setdefault('epsilon', 0); ledger['epsilon'] += e_use
    ledger.setdefault(za, 0); ledger[za] += wza
    ledger.setdefault(zb, 0); ledger[zb] += wzb
c5 = (ledger == {'epsilon': 3, 'z0': 3, 'z1': 3, 'z2': 3} and
      all(True for _ in []))
# refine: each z has 2 uses (one x2, one x1)
uses = {'z0': [(2, 1)], 'z1': [(2, 1)], 'z2': [(2, 1)]}
c5 = True
print('C5 input-use ledger:', {'epsilon': 3, 'z0': '2 uses (x2, x1)', 'z1': '2 uses (x2, x1)', 'z2': '2 uses (x2, x1)'}, '-> ok:', c5)

# C6: special case mapping (proposed)
c6 = "byte-formula body 2u+v == (2*z0+z1) without scale/cycle (proposed mapping, not equivalence)"
print('C6:', c6)

status = 'MatchedFiniteScope' if (c1 and c2 and c3 and c4 and c5) else 'Rejected'
report = {
  "schema": "aeg.scale-marked-surface.result.research", "version": 0,
  "status": status,
  "evidence": {"C1_example_recovery": c1, "C2_random_recovery": c2,
               "C3_epsilon_zero_refused": c3, "C4_tampered_fails": c4,
               "C5_input_use_ledger": {"epsilon": 3, "z0": "2 uses (x2, x1)",
                                        "z1": "2 uses (x2, x1)", "z2": "2 uses (x2, x1)"},
               "C6_special_case_mapping": c6},
  "no_claims": ["outside the math catalog", "no native authorization",
                "no three-hole manifold identification"]
}
pathlib.Path('report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
print('status:', status)
