from fractions import Fraction as F
from itertools import product

# Li-Yorke period-3 interval graph (I1->I2 ; I2->I1,I2)
A = [[0,1],[1,1]]
# Golden one-hole continued-fraction matrix, atlas sec.5-6: F(x)=1+1/x  ->  [[1,1],[1,0]]
M = [[1,1],[1,0]]
# atlas sec.5: one-hole template F_{a,b}(x)=a+b/x -> [[a,b],[1,0]]
def M_ab(a,b): return [[a,b],[1,0]]

def mul(X,Y): return [[sum(X[i][k]*Y[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
def charpoly(X):
    # t^2 - tr t + det
    tr = X[0][0]+X[1][1]; det = X[0][0]*X[1][1]-X[0][1]*X[1][0]
    return (1, -tr, det)   # coefficients of t^2, t, 1
def eig(X):
    tr = X[0][0]+X[1][1]; det = X[0][0]*X[1][1]-X[0][1]*X[1][0]
    import cmath
    d = cmath.sqrt(tr*tr-4*det)
    return ((tr+d)/2, (tr-d)/2)

print("Li-Yorke 3-cycle Markov matrix A =", A, " charpoly t^2 - t - 1? ", charpoly(A)==(1,-1,-1))
print("Golden CF matrix          M =", M, " charpoly t^2 - t - 1? ", charpoly(M)==(1,-1,-1))
P=[[0,1],[1,0]]
print("P A P^-1 = M  (P = swap basis)?", mul(mul(P,A),P)==M, " -> A and M are the SAME linear map up to renaming the two intervals")
print()
print("A^2 =", mul(A,A), " trace =", mul(A,A)[0][0]+mul(A,A)[1][1])
print("M^2 =", mul(M,M), " trace =", mul(M,M)[0][0]+mul(M,M)[1][1], " charpoly:", charpoly(mul(M,M)))
print("atlas says M^2 = [[2,1],[1,1]], det(tI-M^2)=t^2-3t+1:",
      mul(M,M)==[[2,1],[1,1]], charpoly(mul(M,M))==(1,-3,1))
print("eigenvalues of M^2:", [f"{z.real:.6f}" for z in eig(mul(M,M))],
      " phi^2 =", ((1+5**0.5)/2)**2, " phi^-2 =", ((1+5**0.5)/2)**-2)
print()
# M^n = [[F_{n+1},F_n],[F_n,F_{n-1}]]  (atlas)
def fib(n):
    a,b=0,1
    for _ in range(n): a,b=b,a+b
    return a
for n in (1,2,3,4,5):
    R=[[1,0],[0,1]]
    for _ in range(n): R=mul(R,M)
    print(f"  M^{n} = {R}   atlas predicts [[F{n+1},F{n}],[F{n},F{n-1}]] = "
          f"[[{fib(n+1)},{fib(n)}],[{fib(n)},{fib(n-1)}]]  match:", R==[[fib(n+1),fib(n)],[fib(n),fib(n-1)]])
print()
print("Substitution A->AB, B->A counting matrix is M too: A,B counts after n steps -> Fibonacci.")
print("Li-Yorke closed walks trace(A^n) = Lucas, ratio -> phi;  CF convergents ratio -> phi. Same Perron root.")
