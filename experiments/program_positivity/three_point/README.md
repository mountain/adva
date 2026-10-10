# Three-point positivity successor calibration

Original first-party contribution under Unknown v0.3, authored by Codex
(OpenAI), submitted through Mingli Yuan's authorized account proxy. Account use
is not his authorship, review, endorsement or a correctness guarantee.

## Question, scope and reproduction

This is a separately contracted successor to
`mountain/adva/docs/research/0261-external-program-positivity-metaprogram.md`
at `cce73004c2b4fbfb87d9ba1ccc66820423273cf6`. The original fourteen requests,
contract, producer, receiver and frozen evidence are untouched. No native term,
identity, certificate, communication operation or Seal is introduced.

```sh
python experiments/program_positivity/three_point/run_campaign.py /tmp/adva-three-point-NEW
python tests/python/test_program_positivity_three_point.py
```

The destination must not exist. The supervisor reuses the existing producer
and independent receiver by exact paths, freezes source digests before execution
and enforces the successor contract: eight requests, five child launches,
60 seconds wall, 45 seconds aggregate CPU, 256 MiB address space, 12 seconds
per child, one MiB per file and sixteen MiB total output. There are no retries.
Producer and receiver logical limits remain their existing fixed bounds.
The standalone tests perform eight analyses and 23 receiver calls, including
15 deliberately corrupted reports. All checking is inside the campaign budget.
The fixtures, bounds and tests were fixed before the retained execution.

## Observer ambiguity does not identify trials

The program computes y=x*x on the indexed carrier x=(-1,1,2). Its only
observer is y>1. Outputs are (1,1,4), and observation equivalence classes are
{0,1} and {2}. Named regions are pair={0,1} (mask 3), large={2}
(mask 4), all (7) and empty (0). Both pair inhabitants are retained, although
the observer cannot distinguish them. Positivity is still declared on the full
powerset, including unnamed singleton regions; no observational quotient is
silently installed.

The complete basic census has exactly four positive families, written as masks:
(1,3,5,7), (2,3,6,7), (4,5,6,7), and (3,5,6,7). The first three have realizers
0, 1 and 2 respectively; the last has no common realizer. The receiver checks
these independently by enumerating all 256 families of subsets, rather than
the producer's sixteen complementary choices.

| Request | Surviving models | Query pair | Receiving outcome |
| --- | ---: | --- | --- |
| basic, no signed premises | 4 | Underdetermined (3 positive, 1 negative) | Verified |
| joint, no signed premises | 3 | Underdetermined (2 positive, 1 negative) | Verified |
| marked 0 | 1 | ForcedPositive | Verified |
| marked 1 | 1 | ForcedPositive | Verified |
| marked 2 | 1 | ForcedNegative | Verified |
| marked 0, negative pair | 0 | Inconsistent | Verified |
| joint, negative pair | 1 (realizer 2) | ForcedNegative | Verified |
| basic, fuel 200 | No exhaustive model claim | Unknown | NoClaim |

Marked 0 and marked 1 give identical answers to every named query, but distinct
full-powerset models and distinct realizers. This is the concrete observation
limitation. The basic and joint ambiguous answers both have a completed census
and checked opposing model witnesses: their theory does not determine pair's
positivity. The marked conflict has a completed empty census; it is inconsistent
because the selected policy and negative premise conflict, even though pair is
inhabited. Removing that marked restriction via joint restores a model.

The low-budget request stops after 8 of sixteen producer candidates,
with complete arithmetic traces and derived regions already present. Fuel use is
200/200. The incomplete model list is cleared, complete is false, and all
query classifications and witnesses are withheld. Its unrestricted counterpart
is the predeclared basic request above. NoClaim checks conservative withholding;
it does not independently certify the exhaustion diagnostic. The local test
checks the fuel code and the partial-census phase explicitly.

## Independent receiving and negative controls

Seven complete reports, covering 28 queries, are Verified; the budget-limited
report is NoClaim. The receiver visits 256 raw families once and caches immutable
models without resetting its cumulative budget; batch work is 4,109 logical
units. Ordinary and optimized producer outputs are byte-identical, SHA-256
`629caaa7c34612ba4ee36eb8178d1fa71ec94597a376418a4a49c817fec89b2c`. The bounded campaign passed in
0.531139 seconds with five launches and no retries; all six tests passed.
`campaign.json` retains source hashes, launch outputs, receiving outcomes and
resource accounting; `evidence.json` retains all eight reports.

Fifteen negative controls are rejected: omission with a repaired survivor count,
duplication, false common realizer, same positive/negative witness, ambiguity
misreported as Unknown or Inconsistent, wrong region, observation or arithmetic
output, a model violating marked policy, inconsistency misreported as Unknown,
and four Unknown leaks (decisive classification, model, witness, complete census).
These controls attack completeness and semantic consistency, rather than merely
checking a report's digest or shape. Their rejection does not prove the absence
of all producer or receiver bugs.

## Meaning for later metaprograms and strict boundaries

This closes size-three coverage for this finite profile and gives a small,
reproducible regression object for three distinct causes of missing a positive
answer: observers cannot separate trials; the completed theory permits opposing
models or has no models; computation cannot finish its census. They should retain
separate evidence obligations in future certificate profiles.

A later Diophantine profile could test an integer polynomial on a declared finite
integer box and check a concrete root independently. Failure to find a root in
that box establishes only bounded nonexistence. This calibration implements no
Diophantine encoding, unbounded integer search, quantifier elimination or proof
of global nonexistence. Encoding halting into an integer equation would require
a separate faithful encoding theorem and receiving contract; it would not make
global solvability decidable. Bounded simulation may certify a halt within its
budget, while exhaustion remains Unknown unless another proof establishes more.

The tool accepts only the existing terminating rational SSA grammar. Its chosen
static positivity theories are not arbitrary nontrivial extensional properties
of partial computable programs. Nothing here changes Rice's theorem, the halting
barrier, or the undecidability of unrestricted integer-polynomial solvability.
Henkin-style naming checks an available finite witness; it cannot manufacture
one for inconsistent premises. Observation incidence is only an external finite
calibration, not a proof of Projective Process–Neighborhood Duality, faithfulness
or native observer pullback. The useful next step is a separately bounded
certificate profile with explicit encoding and witness obligations.

## Publication review

All added code, fixtures and prose are project-original contributions under
Unknown v0.3; outputs derive only from those rational fixtures and existing
project tooling. No external text, dataset, software or theorem proof is copied
or vendored. This first-party origin record follows PUBLICATION_BOUNDARY.md.
Actual reviewer and author: Codex (OpenAI), 2026-10-09; no human review is implied.
