# Research 0168 evidence

Two things are retained here, and nothing else: the checker probe that
refuted my own first reading of the `M6` braid guard, and its raw output. No
iota-lang source or licence is copied into this repository — research 0168 §4
concludes that no iota-lang code should be imported, and the substrate-side-only
boundary of research 0167 §7 stands.

## 1. The claim under test

Before answering the direction question, the assessment in 0168 rests on "adva
already records the braid relation exactly". That claim is only as good as the
formation checker, so the checker was re-derived rather than trusted.

`crates/adva-witness/src/relation.rs:606` `check_braid` requires the left word to
be `a b a` with `a != b`, the right word to start `b a`, and the third right
label to equal `b`. My first reading judged the third conjunct absent from a
partial view of the condition:

```
if a != a_again || a == b || right_b != b || right_a != a || right_b_again != b {
```

The probe tested exactly that: a braid cell whose right word is `b a -b3`
instead of `b a b`.

## 2. Files

| File | sha256 |
| --- | --- |
| `m6-braid-guard-probe.rs` | `11546e07543d372cbd495b99d013016c05fc319357fcbbe9042f58088f2e2052` |
| `m6-braid-guard-output.txt` | `b32683fae4579e3394adf0ff47e7f4f8542f53cd73052d665110a36535a03ef6` |
| `m6-braid-guard-probe-Cargo.toml` | (path dependency only) |

## 3. Reproduction

The probe is deliberately **out of tree**: it depends on `adva-witness` by path
and is built in a temporary directory, so nothing is added to the workspace and
the checker is not modified.

```
mkdir -p <tmp>/src
cp m6-braid-guard-probe.rs <tmp>/src/main.rs
cp m6-braid-guard-probe-Cargo.toml <tmp>/Cargo.toml
# point the path dependency at the checkout under test
cd <tmp> && cargo run --quiet
```

Output, verbatim:

```
ACCEPTED  aba vs bab (the declared word): boundary_occurrences=6
REJECTED at new() aba vs ba-b3 (third label differs): InvalidBraidWord
REJECTED at new() aba vs ba-a (third label is a): InvalidBraidWord
```

`RelationCellV0::new` validates, so the rejection is raised at construction and
the third case never reaches `check()`.

## 4. Result

The `M6` braid formation checker is **sound for the word-shape obligation it
claims**: `aba` and `bab`, with a distinct generator, and a nonempty witness.
Both of my hand-built counterexamples were rejected with `InvalidBraidWord`.

The first reading and its refutation are both recorded in 0168 §7. An assessment
that reports only its conclusion cannot be checked, and this one was wrong on
the first pass.

What the checker still does not do, as its own documentation states: it checks
formation and explicit references only. It does not replay the witness, does not
prove path or program equality, and does not authorize reverse transport.
