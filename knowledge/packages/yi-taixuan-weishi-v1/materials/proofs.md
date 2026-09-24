# Original mathematical presentations for the intake

Codex (OpenAI), Unknown v0.3, through Mingli Yuan as an authorized account proxy.
These are external mathematical arguments. They are not native Adva proof
objects. The checker verifies selected finite instances and counterexamples;
the prose proofs retain their stated generality and assumptions separately.

## Observation fibres and information loss (O01, O02, O12)

Let X be finite, p:X->Y an observation, and b:X->{0,1} a question. A decoder
h:p(X)->{0,1} satisfying b=h composed with p exists exactly when
p(x)=p(x') implies b(x)=b(x'). Necessity follows by applying h to equal inputs.
For sufficiency, define h(y) using any x in the fibre over y. The implication
makes the choice immaterial. No definition off p(X) is required.

If q=f composed with p, then p(x)=p(x') implies q(x)=q(x'). Thus every
q-decidable question is p-decidable. With X={0,1,2,3}, p=(0,0,1,1) and constant
q, exactly four Boolean questions factor through p and only two through q.
The lost distinction is witnessed, not inferred from a vague notion of entropy.

An index can likewise be the same observation of either a complete two-row
source or a three-row source whose last row was omitted. A calculation taking
only that index as input cannot distinguish these cases. A second boundary to
the source inventory is necessary. This does not say that every index is wrong.

## Partial learning and finite categorical logic (O03, Y07, Y08)

For a fixed hypothesis family H and labeled observations E, define
V(E)={h in H: h agrees with every observation in E}. If E is contained in E',
then V(E') is contained in V(E), directly by conjunction of the constraints.
An empty version space means no member of the declared family fits; it does
not prove there is no explanation outside that family. Agreement on a new
question is conditional on H and the accepted examples. Partial functions also
need coverage; lack of coverage is not a negative answer. Contradictory labels
for the same complete context cannot be repaired by a majority vote while
preserving both labels as hard constraints.

For three unary predicates S,M,P, every individual belongs to one of eight
membership atoms. A/E/I/O formulas depend only on which atoms are empty:
universal inclusion excludes an atom region, exclusion excludes an intersection,
and particular statements require a region to be occupied. Replace each
occupied atom by one representative. All such formulas retain their truth.
Hence the 255 nonempty occupancy masks form a complete decision domain for
this fragment over a nonempty universe. Requiring S,M,P themselves to be
nonempty is an additional filter. Enumeration under both policies yields the
figure counts in Y08; it is not a decision procedure for arbitrary logic.

## Address projections and minimal coordinate count (T18--T23)

For X={0,1,2}^4 and a coordinate subset S of size k, projection fibres have
size 3^(4-k). Every observable subset is a union of those fibres, so its size
is divisible by 3^(4-k). Define mu(A) as the least k allowing such a union.
If 3 does not divide |A|, mu(A)=4. This applies to 47 and 34 independently of
where those sets sit. Divisibility is not sufficient: a three-element fibre
obtained by fixing three coordinates has mu=3, whereas the orbit of head 7
under displacement (1,2,1,1) has mu=4. Consequently a blanket claim that all
mu=4 results contain no positional information is false.

For fixed S there are 3^k fibres and 2^(3^k) possible unions. When varying S,
these families overlap; adding their sizes double-counts subsets. The packet
enumerates and deduplicates the union through k=2, obtaining 2,26,3014 at levels
0,1,2. The stored level-three upper bound is retained as an upper bound.

For the finite prefix 1..47, no modulus 2..80 separates it from 48..81. If
m<=34, the tail contains all residue classes, including the residue of 1. If
35<=m<=80, choose a=max(1,48-m) and b=a+m. Then 1<=a<=47, 48<=b<=81 and
both have the same residue. Modulus 81 makes every class a singleton; so do
larger moduli on this domain. A restricted observer's failure is not failure of
every possible address predicate.

## Carry arithmetic is a different operation (T03, T04, T06--T08)

In F3^4, three additions of v return to the starting point. If v is nonzero,
neither one nor two additions does, so its order is three. An involution is a
permutation with cycles of length one or two, so on 81 points it has at most
40 transpositions and an odd number of fixed points. This theorem excludes a
nonzero constant vector translation as that involution; it excludes neither
reflections nor variable-displacement permutations nor general relations.

For arbitrary distinct x,y, choose v=y-x. Then the cycle of x under v contains
y. The existentially chosen cycle discriminates no pair. Fixing v in advance
makes a different, testable relation.

Encoding four trits as a single residue modulo 81 gives a different addition.
The map i->i+40 mod 81 has order 81 because gcd(40,81)=1. Without wrapping,
the relation h->h+40 on 1<=h<=41 has 41 edges; head 41 belongs to both
(1,41) and (41,81). It is therefore not a disjoint pairing. Base-three carries
make its coordinate displacement vary. None of these facts establishes how
many historical pairs a particular extraction actually recovered.

## Magic arrays depend on the line family (T09--T17)

For the natural grid 9r+c+1, sum over c to get 81r+45, or over r to get
9c+333. Both diagonals sum to 369 by arithmetic progression. Only the middle
row and middle column join them at that value; the whole grid is not magic.

A square matrix over Z/nZ is invertible exactly when its determinant is a unit:
the adjugate gives an inverse in the forward construction, and determinants
of an inverse pair multiply to 1 in the necessary direction. Nonzero is enough
only when every nonzero element is a unit, such as in a field.

Over F3 let v(x)=1+sum_i 3^i*(Mx)_i, with digits represented by 0,1,2. Along
coordinate direction j, a nonzero M_ij makes digit i traverse all three values,
contributing 3*3^i to the line sum. A zero entry contributes
3*3^i*(Mx)_i instead. If there are no zero entries, every line sums to
3+3*(1+3+9+27)=123. Invertibility independently makes all 81 values distinct.

For necessity of constant sums in each direction, assume every row is nonzero.
If M_ij=0, choose x with (Mx)_i nonzero. The variable part of that direction's
line sum is zero at x=0 and positive at this x: it is a sum of nonnegative
weighted digits. It therefore cannot be constant. This proves the stated
no-zero-entry criterion without extending the finite binary-family exhaustion.
Diagonals vary several coordinates at once and require separate checks.

## Null models and provenance (T26, T27, T30, C01--C07)

Partition 729 positions into 81 blocks of nine. A uniform s-subset misses one
specified block with probability C(720,s)/C(729,s); linearity of expectation
gives the expected number of blocks hit. For m specified blocks,
inclusion-exclusion gives sum_j (-1)^j*C(m,j)*C(729-9j,s)/C(729,s).
This null is exchangeable over positions; an arithmetic progression does not
become exchangeable merely by having the same cardinality.

For any fixed 35-edge simple graph on 81 vertices, a uniform vertex permutation
sends each edge uniformly among C(81,2) unordered pairs. The expected number
that land in the original edge set is 35^2/C(81,2). No independence between
edges is required. Markov's inequality bounds the probability of at least one
overlap by this expectation. A zero overlap can therefore be ordinary.

Modulo 12, 4 is 1 modulo 3 and 0 modulo 4; 9 is 0 modulo 3 and 1 modulo 4.
Their products obey e_i^2=e_i, 4*9=0 and 4+9=1. Consequently
4*r3+9*r4 reconstructs each pair modulo 12. Uniqueness as an integer needs a
representative interval. Adding observations modulo 1 or 2 refines no fibre.
The distinct integers 9,21,33 remain aliases without a domain restriction.

Input fidelity is separate: source 5 gives (2,1), but the altered pair (0,1)
uniquely reconstructs 9. The library already retains this counterexample.
Checking x=q*m+r and 0<=r<m binds a residue to a disclosed x. Expected source
and policy pins must themselves arrive through an independently justified
boundary. This arithmetic does not verify a real-world measurement.

## Segmentation, alignment and doctrine (V01--V05)

A string of n>=1 tokens has n-1 interior gaps. Independently marking each gap
as a boundary gives 2^(n-1) segmentations, all erased to the same token string.
Thus a unit count requires a segmentation policy. Equal counts are likewise
consistent with different token strings; labels are yet another observation.

Character-set Jaccard uses only intersection and union cardinalities. Token
order and repetitions leave the character set unchanged. For example, the
original synthetic strings `ab` and `baaa` score 1 despite differing in both
order and multiplicity. This is a counterexample to recovery from that score,
not a theorem that no semantic method can distinguish texts.

For sequences a,b with additive match score s and gap penalty g, define the
optimal prefix score D(i,j). The final step consumes either both final tokens,
only a's final token or only b's. Therefore D(i,j) is the maximum of
D(i-1,j-1)+s(a_i,b_j), D(i-1,j)+g and D(i,j-1)+g, with boundary gap scores.
Induction on i+j proves optimality. Ties can produce multiple optima; an
optimum is relative to the score, not a proof of correspondence or ancestry.
The checker compares a fresh implementation against all paths on 36 small
synthetic sequence pairs. No external alignment implementation is copied.

Finally, 24+1+5=30 places the distinguished unit at 25 within the thirty; the
numerical center is 15.5. Calling a unit a conceptual pivot is an interpretation,
not an arithmetic midpoint or an extra item. No doctrinal conclusion follows
from this correction or from any other check in this packet.
