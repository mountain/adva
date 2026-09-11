"""Independent verification of the finished 0129 continuation batch (runs 25-124).

Two independent routes, neither of which reuses the driver:
  A. the declared CLI check: adva-labs-search verify <report> and <tampered>
  B. my own recomputation of correlations, energy and merit factor from the
     stored sequence, in Python, compared exactly against the stored values,
     with a one-flip sensitivity control.
"""
import json, pathlib, subprocess, sys

BIN = "/Users/mingli/Adva/adva/target/debug/adva-labs-search"
D = pathlib.Path("/Users/mingli/Adva/adva/docs/research/0129-evidence")

def recompute(seq):
    n = len(seq)
    corr = [sum(seq[i] * seq[i + k] for i in range(n - k)) for k in range(1, n)]
    energy = sum(c * c for c in corr)
    merit = None if energy == 0 else n * n / (2 * energy)
    return corr, energy, merit

cli_report_ok = cli_tamper_rejected = 0
math_ok = 0
problems = []
insensitive = []

for run in range(25, 125):
    rep = D / f"run{run}-report.json"
    tam = D / f"run{run}-tampered.json"

    # --- A. the declared CLI check
    a = subprocess.run([BIN, "verify", str(rep)], capture_output=True)
    b = subprocess.run([BIN, "verify", str(tam)], capture_output=True)
    if a.returncode == 0:
        cli_report_ok += 1
    else:
        problems.append(f"run{run}: report verify exit {a.returncode}")
    if b.returncode != 0:
        cli_tamper_rejected += 1
    else:
        problems.append(f"run{run}: TAMPERED COPY ACCEPTED (exit 0)")

    # --- B. my own arithmetic
    doc = json.loads(rep.read_text())
    best = doc["best"]
    seq = best["sequence"]
    corr, energy, merit = recompute(seq)
    if best["length"] != len(seq):
        problems.append(f"run{run}: stored length {best['length']} != sequence length {len(seq)}")
    if best["correlations"] != corr:
        problems.append(f"run{run}: stored correlations differ from recomputation")
    elif best["energy"] != energy:
        problems.append(f"run{run}: stored energy {best['energy']} != {energy}")
    elif abs(best["merit_factor"] - merit) > 1e-12:
        problems.append(f"run{run}: stored merit {best['merit_factor']} != {merit}")
    else:
        math_ok += 1

    # sensitivity control: one flip must move the arithmetic
    if len(seq) > 1:
        flipped = list(seq)
        flipped[len(flipped) // 2] *= -1
        _, e2, m2 = recompute(flipped)
        if e2 == energy and m2 == merit:
            insensitive.append(run)

print(f"runs checked                  : 100")
print(f"A. CLI verify exit 0          : {cli_report_ok}/100")
print(f"A. CLI tampered rejected      : {cli_tamper_rejected}/100")
print(f"B. my arithmetic matches      : {math_ok}/100")
print(f"sensitivity controls passed   : {100 - len(insensitive)}/100")
print(f"problems                      : {len(problems)}")
for p in problems[:10]:
    print("   ", p)
if insensitive:
    print("   one-flip control did not move the arithmetic on runs:", insensitive[:10])
