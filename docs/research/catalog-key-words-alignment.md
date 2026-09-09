# Fifteen-entry naming alignment and retained coverage rejection

2026-09-09. Direction: Mingli Yuan. Integration and checking: ChatGPT.
Status: proposed documentary engineering; no native semantic admission.

## Remote change and bounded question

Adva main advanced from merged PR #167 to e62daacbca6ec33717326504d7ad5bede27ca680.
Its library gitlink is b3ff7ad6a87f6bc61c5122f7c699a528729870b0.
The library adds the rational-gap sixth anchor referencing external receipt 19
and aligns the naming documents with the v1 shape. Those narrative bytes are
preserved; the receipt is not retrieved, executed, or authenticated here.
The proposed narrative is not a proof of Calabi-Yau identification.

The catalog has fifteen entries, but both source and v1 naming lists have only
fourteen. The new logic-yau-calabi-mapping entry has no declared word row.
Main does not yet implement --key-words: its implementation is still in
unmerged PR #166. This continuation integrates the already proposed checker
with the newer library rather than widening the mathematical task.

The question, one route, zero search nodes and finite execution limits were
recorded before running in experiments/catalog_key_words/alignment/contract.json.
Each child has a 30-second timeout and a 512 MiB address-space limit; the
driver also caps its child schedule at 120 seconds. These are distinct from
the checker's existing five-second cooperative file-reading budget. No
automatic restart occurs.

## Paired result and minimal change

Using the original PR #166 checker at 06a085302cb00c9331e3b29c2295d6c8b2234880
with main's newer catalog:

| Stage | Default check | Opt-in naming check |
| --- | --- | --- |
| Before repair: 15 catalog / 14 name rows | CatalogConsistent | InvalidCatalog: missing complete key coverage |
| After repair: 15 catalog / 15 name rows | CatalogConsistent | MatchedDeclaredKeys within CatalogConsistent |

The repair explicitly appends the words [logic, yau, calabi, mapping] to
both naming documents and updates the source pin and two owner-material pins.
It preserves the fourteen preceding rows, seven historical exceptions, fixed
policy, all fifteen catalog entries, and the existing Yau-Calabi narrative.
README counts now match the catalog. No hash is automatically repaired by a
checker; these are reviewed source edits.

The original runtime implementations of math_catalog.py and adva.py are
byte-identical to PR #166. Only integration data, tests and handoff material
change in this continuation. Main's newer test_math_catalog.py, including
its Yau-Calabi case and three-material expectation, is retained.

This is the expected boundary: byte consistency did not imply naming
coverage. The existing v1 checker caught the omission without a semantic or
policy change. The source v0 prose is integrity-bound, not independently
interpreted by that checker. Title meaning remains explicitly unchecked.

## Verification and costs

648 targeted tests pass in 1.38 seconds of pytest time. New cases remove
the actual fifteenth word row and repin the document: the default check still
passes while the v1 coverage gate rejects it. A fresh synthetic sixteenth
entry is also refused until its word row is explicitly supplied, after which
the unchanged contract accepts it. The suite retains 516 finite codec cases,
repinned corruption controls, output protection, resource Unknown cases,
and earlier catalog/growth checks. Both CLI modes run with site packages
disabled. The changed naming test file passes Ruff; one preflight lint
finding on an old intentional delimiter-collision expression was clarified
before final tests, without changing that control's meaning.

| Measured scope | Baseline | Final |
| --- | ---: | ---: |
| Driver before serialization | 0.141903 s | 1.840813 s |
| Default CLI subprocess | 0.074935 s | 0.068598 s |
| Opt-in CLI subprocess | 0.066660 s | 0.071662 s |
| Test subprocess wall time | not run | 1.699873 s |
| Report serialization | 0.844530 ms | 0.598746 ms |
| JSON report replay | 0.096768 ms | 0.164320 ms |
| Parent process peak RSS | 10,752 KiB | 10,752 KiB |
| Largest child process peak RSS | 13,312 KiB | 33,500 KiB |

Memory figures are separate Linux process high-water marks, not aggregate
memory or file size. Authoring, network, and final file write were unmeasured.
These observations do not establish acceleration. Baseline rejection is an
expected control; there was no failing test run or correction replay.

Exact command outputs and source SHA-256 values are in alignment/baseline.json
and alignment/final.json. Both evidence records bind their driver and contract.
The original experiments/catalog_key_words/contract.json and evidence.json
remain unmodified historical records; this continuation does not relabel
their fourteen-entry results as fifteen-entry results.

## Reproduction and source boundary

After checking out the updated PR #166 and its pinned library, run:

```sh
python3 -S python/adva/adva.py math-check
python3 -S python/adva/adva.py math-check --key-words
python3 -m pytest -q tests/python/test_math_catalog.py tests/python/test_catalog_key_words.py
```

The standard-library driver refuses to overwrite an existing evidence file.
For a fresh full measurement, create a disposable git worktree of the PR,
initialize its pinned library submodule, remove only the copied
alignment/final.json, then run:

```sh
python3 experiments/catalog_key_words/alignment/run_evidence.py final
```

For the baseline, use another disposable copy of the same outer checkout,
set its library submodule to b3ff7ad6a87f6bc61c5122f7c699a528729870b0,
remove only that copy's alignment/baseline.json, then run the driver with
baseline. The gate must reject the missing row; this is not an instruction
to alter the submitted evidence. Core checker bytes match those originally
used. Local validation used Python 3.12.14 and a separately installed pytest.

The checked local snapshot was assembled from pinned remote files and the
original PR source; catalog references passed their full byte checks. Rust
and remote CI were not executed. Native histories, free, Seal, general
grammar, Calabi-Yau geometry and practical customer value remain unproved.

## Integration and next step

Update existing library PR #1 from current library main, preserving its old
commit as a parent. Then update existing Adva PR #166 from current main,
retaining its old head as a parent and pinning the new library commit.
This resolves the stale dependency without a force push or duplicate PR.
Review and merge library #1 before Adva #166; neither is merged in this run.

No new word is formed. This helps maintainers and subsequent agents keep
documentary growth explicit and prevents mistaking a passed byte check for
complete naming coverage. The next smallest step is to review the two
aligned PRs; the separate Pascal/Metamath proof-export plan remains pending.
