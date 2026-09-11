# Reproduction of the iota/SKI substrate projection round

Date: 2026-09-11. Re-run by the assistant (DeepSeek Harness) in a second session,
submitted through Mingli Yuan's account as an authorized proxy. The round itself
was implemented and recorded earlier by the same project; this file only re-runs
it and records the outcome.

Status: reproduced. Every script and every retained artifact matches. No byte of
this round was modified by the replay.

## What was re-run

The three scripts of this round, in their own order, each from a **fresh
temporary copy** of this directory:

| Script | Exit | Wall | Role |
|---|---:|---:|---|
| `reducer.py` | 0 | 0.083 s | unsigned projection over bytes 35/100/255, C1–C5, writes `results.json` |
| `signed.py` | 0 | 0.126 s | sign-pair Church arithmetic, primitive unit checks, five sample bytes |
| `fullset.py` | 0 | 6.087 s | all 256 bytes, tamper controls, ι round-trip sample, writes `fullset-results.json` |

They are run in a copy rather than in place for a concrete reason: `reducer.py`
and `fullset.py` **write their result files into the current directory**, so
running them here would have overwritten the very records they are meant to be
compared against. The copy is removed afterwards.

The whole directory has to be copied, not a single script: the chain is
`fullset.py -> signed.py -> reducer.py`, and each link is loaded through
`importlib.util.spec_from_file_location` with a bare relative filename, so the
loader resolves against the working directory.

## Result

```
PASS  copy has the import chain
PASS  reducer.py exits 0
PASS  signed.py exits 0
PASS  fullset.py exits 0
PASS  reducer reports a status
PASS  reducer C1 combinator laws pass
PASS  signed primitive unit checks pass
PASS  fullset covers every byte                      256/256
PASS  fullset terms stay distinct                    256/256
PASS  fullset tamper controls pass
PASS  fullset round-trip passes
PASS  round reaches VariationObserved
PASS  results.json reproduces byte for byte
PASS  fullset-results.json reproduces byte for byte
PASS  signed.py printed all five sample bytes        [0, 7, 35, 100, 255]
PASS  signed rows agree with the retained sample_rows
PASS  the signed path is exercised, not only the unsigned one
PASS  reducer.py untouched by this replay
PASS  signed.py untouched by this replay
PASS  fullset.py untouched by this replay
PASS  results.json untouched by this replay
PASS  fullset-results.json untouched by this replay
```

22 checks, all passing. The two produced files are reproduced **byte for byte**,
not merely field by field, and that reproduction is exact in both senses: the
produced `results.json` is 1488 bytes and `fullset-results.json` compares equal
to the committed file under `cmp`.

### Digests

| File | sha256 |
|---|---|
| `reducer.py` | `ca2c23b42151ace07e2c0fa638b76612dc1408987a267f5c5d4aeda9139e9ce6` |
| `signed.py` | `af90ba2f583508f3517847c7cc70ef6019a036cef953ec6e36b4dbd6add3852f` |
| `fullset.py` | `9cdcd03a903fe41a2d40e94012878bb9ca51770f6c4e4b06fab7115d04095656` |
| `results.json` | `3eb9989ac479360376facab851e7369b9bcdd477a2f1e9045c85563cb4743c6e` |
| `fullset-results.json` | `0dadd116abbfe784cfae5dfa751b8f5c2b27f2ee353b55f9823c450314e1a5ff` |

The replay was run twice. Both runs passed the same 22 checks and both produced
artifacts equal to the committed ones, so the round is reproducible. The stdout
is **not** byte-identical between runs: it reports each script's wall time, and
those three numbers differ (for example `reducer.py` at 0.081 s and 0.079 s).
The check outcomes and every compared artifact are identical; only the reported
timings move.

## What this establishes, and what it does not

**It establishes** that the retained conclusions of this round — 256/256 byte
values, 256/256 distinct terms, term sizes 1811–5831, the tamper controls, the
four ι round-trips, and `VariationObserved` — are re-derivable from the retained
code, and that the retained artifacts are exactly what that code produces.

**It does not establish that the model is correct.** The scripts under test *are*
the implementation of the model, so their agreement is reproducibility, not
independent verification. `reducer.py` and `signed.py` each define their own
near-identical `model_eval`, so they do not verify each other either. Nothing
here is an independent kernel, and no term rewriting proof is involved.

**It does not change the round's own boundary**, which stands as written: this is
a finite projection between the ι/SKI substrate and the PSC0 carrier, **not** a
language equivalence, not native admission and not a new epoch. There is still no
`claims.toml` entry mentioning iota.

## One defect found in this file, recorded rather than smoothed over

The first version of the reproduction script copied files with
`shutil.copyfile(name, workdir / name)`. Because `name` is an absolute path,
joining it onto `workdir` resolves back to the source, so the script tried to
copy every file onto itself and stopped with `SameFileError` before running
anything. It was replaced by a single `copytree(..., dirs_exist_ok=True)`, and
the comment in the script records why. No artifact was affected: the failure
happened during the copy, before any script ran, and the record hashes are
identical before and after.

## Reproduce

```sh
python3 reproduce-2026-09-11.py
```

It prints the table above and exits 0 only if every check passes. With
`--output report.json` it also writes the full machine report, refusing to
overwrite an existing file. It requires only the Python standard library, and it
never writes inside this directory.
