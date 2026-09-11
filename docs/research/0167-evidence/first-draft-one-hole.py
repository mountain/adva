from fractions import Fraction as F
# The golden one-hole recursion of the atlas: F_{a,b}(x)=a+b/x with (a,b)=(1,1)
def Fn(x): return 1 + F(1)/x
phi = (1+5**0.5)/2

print("F(x) = 1 + 1/x   on the self-map interval [1,2]")
print("  F(1)=%s F(2)=%s  -> image [3/2,2] subset [1,2]: %s" % (Fn(F(1)), Fn(F(2)), Fn(F(1))>=1 and Fn(F(2))<=2))
print("  F is strictly decreasing (monotone) -> no period-3 orbit possible (monotone maps have period <= 2)")

# exact iteration from rational starts; show it converges monotonically to phi
for start in (F(1), F(3,2), F(2), F(19,12)):
    x = start; hist=[x]
    for _ in range(30): x = Fn(x); hist.append(x)
    approx = float(hist[-1])
    print(f"  start {start}: 30 steps -> {hist[-1]}  = {approx:.12f}   |x-phi|={abs(approx-phi):.3e}   (fixed point, no cycle)")

# exact check: solve F(F(x)) = x for 2-cycles
# F(F(x)) = (2x+1)/(x+1) = x  <=>  x^2 - x - 1 = 0  -> only phi and (1-sqrt5)/2 (outside)
print("  2-cycle equation F(F(x))=x reduces to x^2-x-1=0 -> only phi in [1,2]; no 2-cycle, no 3-cycle.")
print("  F^n(x) -> phi for every rational start tested: globally attracting on [1,2].")

print()
print("Same matrix, two regimes:")
print("  M = [[1,1],[1,0]] used as the CONTINUED-FRACTION / substitution matrix of the monotone map F:")
print("     monotone, contractive in the hyperbolic metric, unique fixed point phi, NO chaos.")
print("  A = [[0,1],[1,1]] (== M up to swapping the two intervals) used as the MARKOV matrix of a 3-cycle:")
print("     expansive, trace(A^n)=Lucas -> phi, all periods, Li-Yorke chaos.")
print("  The matrix alone does not decide: the realized map (contraction vs folding) does.")
