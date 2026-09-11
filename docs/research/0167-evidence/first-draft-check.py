from fractions import Fraction as F
import math

# ---------- A. The Markov-graph core of the Li-Yorke 3-cycle argument ----------
# For a 3-cycle a<b<c with f(a)=b, f(b)=c, f(c)=a on an interval,
# set I1=[a,b], I2=[b,c]. Continuity + IVT give:
#   f(I1) >= I2          (via f(a)=b, f(b)=c)
#   f(I2) >= [a,c] >= I1 + I2  (via f(b)=c, f(c)=a)
A = [[0,1],[1,1]]     # rows = domain interval, cols = covered interval
def matmul(X,Y):
    return [[sum(X[i][k]*Y[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
def matpow(M,n):
    R=[[1,0],[0,1]]
    for _ in range(n): R=matmul(R,M)
    return R
def fib(n):
    a,b=0,1
    for _ in range(n): a,b=b,a+b
    return a
def lucas(n):
    a,b=2,1
    for _ in range(n): a,b=b,a+b
    return a

print("A. Markov graph of the period-3 forcing pattern")
print("   char poly of A:", "x^2 - x - 1", "-> Perron root phi =", (1+5**0.5)/2)
for n in range(1,9):
    tr = matpow(A,n)
    print(f"   n={n}: trace(A^n)={tr[0][0]+tr[1][1]:3d}  Lucas L_n={lucas(n):3d}  "
          f"  (closed walks = # fixed pts of f^n in the subshift)  phi^n={((1+5**0.5)/2)**n:8.3f}")

# ---------- B. Control 1: interval map with a genuine 3-cycle -> all periods ----------
# Tent map T(x)=1-|2x-1| has the exact 3-cycle 2/7 -> 4/7 -> 6/7 -> 2/7.
def T(x): return 1-abs(2*x-1)
x=F(2,7)
orb=[x]
for _ in range(3): x=T(x); orb.append(x)
print("\nB. Tent map T(x)=1-|2x-1|")
print("   exact 3-cycle (Fractions):", [str(o) for o in orb], "closed:", orb[0]==orb[3])

# count solutions of T^n(x)=x by fine root scanning (T^n is piecewise linear, 2^n pieces)
def Tn(x,n):
    for _ in range(n): x=T(x)
    return x
for n in (1,2,3,4,5,6):
    # sample sign changes of Tn(x)-x on a fine grid, then bisect
    N=2000000
    roots=[]
    prev=0-0
    xp=0.0; fp=Tn(0.0,n)-0.0
    for i in range(1,N+1):
        xc=i/N; fc=Tn(xc,n)-xc
        if fp==0.0 or fp*fc<0:
            lo,hi=xp,xc
            for _ in range(60):
                mid=(lo+hi)/2
                if (Tn(lo,n)-lo)*(Tn(mid,n)-mid)<=0: hi=mid
                else: lo=mid
            roots.append((lo+hi)/2)
        xp,fp=xc,fc
    print(f"   n={n}: #Fix(T^n)={len(roots):3d}   2^n={2**n:3d}   (all periods present)")

# ---------- C. Control 2: circle rotation by 1/3 -> period 3, zero chaos ----------
# R(x) = x + 1/3 mod 1 is a homeomorphism of the circle; every point has period 3.
# It is conjugate to the rigid rotation: equicontinuous, no scrambling, no growth.
def R(x): return (x + F(1,3)) % 1
print("\nC. Control: rigid rotation of the circle by 1/3")
p=F(1,7)
print("   exact orbit of 1/7:", [str(R(R(R(p))))==str(p)], "period exactly 3")
print("   #Fix(R^n) = 1 for every n (all points period 1 or 3); no exponential growth")
for n in (1,2,3,4,5,6):
    print(f"   n={n}: #Fix(R^n)=1 (trivially, since R^n is a rigid rotation by 0 or 1/3)")

# ---------- D. What differs: invertibility / folding ----------
print("\nD. Structural difference")
print("   Tent map with 3-cycle: non-invertible (folds), order structure of interval used")
print("   Circle rotation by 1/3: invertible homeomorphism -> torus/circle analogue fails")
print("   => '3 implies chaos' needs the folding (a collision/quotient), not the three alone.")
