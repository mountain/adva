# Restricted name formation and the opt-in catalog gate

Date: 2026-09-09. Direction: Mingli Yuan; implementation: ChatGPT/Codex.
Status: proposed documentary engineering, not native admission.
Adva base: ff8272102ce294e77ba1b4cf03ca6296721bfb39.
Library base: 695d6b4c26ebfd373ae696decfe82724f43b4c71.

## Problem and exact domain

All fourteen declared names previously linked and unlinked correctly. But
the general domain did not exclude separators inside words: ["a-b","c"] and
["a","b-c"] both join to "a-b-c". The source document was not a catalog
material, and math-check verified pins without checking the naming relation.

link_words now accepts nonempty ordered lists of at most sixteen distinct
tokens matching [a-z0-9]+, with joined length at most eighty characters.
No case conversion, trimming, Unicode normalization or repair occurs.
unlink_key splits and validates the recovered sequence. Every separator is
distinguishable from token characters, so unlink(link(w))=w on this domain;
injectivity follows by applying unlink to equal linked names. The finite
tests exercise the implementation; they are not the proof of the general
domain claim. No-repetition is an additional naming policy, not necessary
for mathematical reversibility. Catalog leading-letter/home rules still apply.

Invalid tokens, delimiter injection and noncanonical keys are refused.
Resource exhaustion raises CatalogLimitError and becomes Unknown at the
catalog boundary. Names are documentary coordinates, not semantic identities.

## Versioned integration

The original catalog-key-words.json bytes remain unchanged. A separate v1
document declares the fixed policy, original path/hash, entries and seven
historical prefix exceptions. Both files become explicit materials of the
existing logic-party-naming-layer entry. There remain fourteen entries; its
status stays proposed-document. The catalog schema still describes materials;
the new naming interpretation is explicitly versioned in the v1 layer.

```sh
python3 -S python/adva/adva.py math-check --key-words
```

Default math-check retains the documentary/hash guarantee. The new flag
first checks the catalog, references and immutable Open growth obligation,
then parses only the fixed registered v1 path with the existing bounded,
duplicate-key rejecting, no-symlink reader. Its digest is checked again after
metadata reading; the source pin must match the owner's registered source.
A file cannot select another parser, alter the fixed policy, extend the
historical exceptions or register itself by directory placement.

The check requires one-to-one complete catalog coverage, ordered word/key
agreement and the fixed historical home or topic prefix. Its versioned
subreport says MatchedDeclaredKeys, title_semantics_checked=false and
native_admission=not-granted. Seven exceptions derive from the already fixed
reserved-home table; candidate data cannot add exceptions. Referenced
evidence is not executed. The existing CI catalog step enables the flag.

No Wenyan implementation, native arithmetic operation, Pascal descendant,
title-meaning proof, authentication or universal grammar result is added.
The prior four Chinese path strings remain an experimental Python interface.

## Validation and cost

The frozen contract is experiments/catalog_key_words/contract.json. One
route covers all 516 length-one-through-four permutations of six tokens,
checks distinct images and round trips, and checks all fourteen real names.
A fresh synthetic logic-fresh-word entry reuses the checker and unchanged
exception policy. Thirteen repinned corrupt-document controls pass the old
byte check but fail the opt-in content check: coverage, duplicates, ordering,
separators, repeated words, foreign keys, exceptions, policy/version/authority
fields and source binding. This tests the difference between pins and meaning
of the stipulated finite naming relation.

Additional checks cover unsupported types, malformed names, Unknown for
budgets, unregistered files, CLI invocation without site packages, output
overwrite refusal and existing catalog/growth regressions. Changing a prose
title alone still passes: its meaning lies outside the checked relation.

Initially 645 tests passed in 1.26 s. Ruff then flagged fixture-import style
and an intentionally fullwidth negative-control literal; these were clarified
without changing their meanings, and the two files were formatted. Lint
passed. Final replay: 645 tests passed in 2.15 s, with 2.448 s child wall time.
There was no failing test execution or semantic correction. Reproduce with
pytest installed in the project test environment:

```sh
python3 experiments/catalog_key_words/run_evidence.py
```

Each child process is capped at thirty seconds. Measured construction was
0.054 ms; codec validation 2.751 ms; fresh codec reuse 0.005 ms; serialization
0.246 ms; replay 1.453 ms. Default and opt-in CLI calls took 75.837 and
73.421 ms; these single timings are not a speed comparison. Total before
report writing: 2.611 s. Python-process high-water RSS: 13,140 KiB; largest
child high-water RSS: 31,580 KiB (30.84 MiB), not simultaneous aggregate.
Research, authoring, network and final report writing were not measured.

Source hashes, full command outputs and costs are in
experiments/catalog_key_words/evidence.json. Results apply to the proposed
combined Adva/library snapshot. No full-workspace or remote CI success is
claimed. CI needs the pinned library contents, as existing catalog checks
already require; checkout permissions and credentials are not changed here.

## Integration order and remaining obligation

Two isolated PRs are needed: the library adds v1, registrations and docs;
Adva adds implementation, tests, CI, evidence and its exact library gitlink.
Review/merge the library dependency before the Adva integration. Neither is
automatically merged. Original source bytes, Pascal pins and the growth
obligation remain unchanged.

No new word is needed: link/unlink now have a restricted executable meaning.
How a human selects words from a title, and which meaning that choice must
preserve, still requires an independent interpretation contract. Reversible
spelling alone cannot discharge it.
