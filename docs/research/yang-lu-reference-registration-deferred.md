# The Yang Lu reference registration is deferred at a declared bound

- Status: process record, no executable claim
- Date: 2026-09-13
- Related: `docs/research/0185-yang-difference-substitution-inequalities.md` (the readings),
  `adva-library/zhang-jingzhong-finite-example-point-elimination-external-reference-v0.md`
  (the registration that did succeed), `python/adva/math_catalog.py` (the bound)

## What was attempted

After the run of 0185, the readings behind it were registered in the catalog the same way
as the Zhang Jingzhong readings the round before: one new external-reference document
`adva-library/yang-lu-inequality-proving-external-reference-v0.md`, one manifest entry
with the document digest pinned, one key added to the geometry topic index, one key
words entry in both naming documents, the two digests that `logic-party-naming-layer`
declares re-pinned, and the counts in `adva-library/README.md` and
`adva-library/math/README.md` recomputed.

## What blocked it

The catalog then held **exactly 32 entries**, which is the declared bound
`LIMITS["entries"] = 32` in `python/adva/math_catalog.py`. The catalog check itself
returned `CatalogConsistent` at 32, so the registration was not invalid; what broke was
the growth fixture:
`tests/python/test_catalog_key_words.py::test_actual_catalog_growth_requires_thirty_first_name`
copies the real catalog, appends one more entry to the copy, and requires that the copy
be `CatalogConsistent` without a matching naming entry. With 32 real entries the copy
holds 33, the checker returns `Unknown` at the bound instead of `CatalogConsistent`, and
the test fails. In other words the bound had no headroom left for the check that keeps
growth and naming in step.

## Why it was not resolved by widening the bound

`python/adva/math_catalog.py` records that the previous widening — of `files`, from 96 to
120 — was "granted once for that admission and not a standing invitation: the next
increase needs its own reason". Widening a declared resource bound to make a test pass is
exactly the move that comment forbids, and it is not a decision an agent should take on
its own initiative. So the registration was **reverted**: the new document was removed,
the library was restored to its committed state, and the two test files were restored
with it. The catalog check then reports `CatalogConsistent` again at 31 entries with
topic counts 10 / 8 / 18 and 31 key words.

## What survives

The readings themselves are not lost. They are in 0185 section 2 with their quotations,
URLs, fetch dates, and an explicit record of how far each reading went and what could not
be retrieved (the Baidu entry named in the request, every full text, and the
successive-difference-substitution chapter of the 2016 book, of which only a title and a
DOI were obtained).

## Options for the direction

1. **Widen the entries bound** in `python/adva/math_catalog.py` with its own recorded
   reason, and register the document as a 33rd entry. The bound is a resource limit, not
   a correctness condition, but the file treats each widening as a decision to record.
2. **Fold the Yang Lu readings into the existing Zhang Jingzhong entry as a v1 layer**,
   which keeps the entry count unchanged. There is precedent: the Arakelov registration
   has a v0 and a v1 layer in one entry. It costs one document and two digest re-pins.
3. **Leave the readings in the note only**, as they are now, and admit no catalog entry.

Nothing in 0185 depends on this decision: the run's contract, checker, evidence and claim
are already committed and pushed, and the readings it cites are recorded in its own text.
