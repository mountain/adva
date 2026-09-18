# Bounded exact incidence duality diagnosis

Frozen before incidence construction and permutation enumeration. Source: /workspace/scratch/61565a2d9860/pascal-circle-study/formal-run/candidate.json. Read-only; do not alter the candidate or perform geometric optimization.

For each side construct exactly seven labelled affine points, the six tangent-limit hexagon side lines specified by its existing binding, and the Pascal line through its finite Pascal points. Red excludes the one Pascal point at infinity. All coordinates, lines, and incidence checks use Fraction arithmetic.

Red point order [1,3,5,7,9,11,13]; blue point order [2,4,8,12,0,6,10]. Line order l0..l5 (successive bound slots) then l6 (Pascal line). Derive row and column degree multisets first.

Enumerate at most 7! point-to-line bijections per side, at most 10,080 total. For each bijection f, test (a) existence of the reverse incidence bijection by matching the transformed incidence sets to point rows, and (b) involutivity directly via symmetry of M[i,f(k)]. Count the same f once regardless of the two tests. Wall and CPU <=10 seconds, address space <=2 GiB, zero automatic continuation. Exhaustion returns Unknown. No general projective polarity existence claim; combinatorial duality and closure under the known circle polarity are distinct.
