# murphy: a named Zot-derived Iota program

Status: bounded external reference experiment. No native Adva execution or new
native operation. The [research report](../../docs/research/murphy-iota-conjugation.md)
contains the construction, results, counterexamples and Futamura boundary.

Mingli Yuan named the program **murphy** after the `Kip Thorne` discussion.
The name binds the value produced by Zot `0001011011` before its stop/printer
wrapper. Its exact source is [`murphy.iota`](murphy.iota), 823 characters excluding
the final newline; [`murphy.json`](murphy.json) pins the bytes and interpretation.
`murphy murphy` means ordinary self-application, stored in
[`evidence/PP.iota`](evidence/PP.iota), 1,647 characters.

## Reproduce

From the repository root, with Python 3.10+, Node.js and POSIX resource limits:

```sh
python3 experiments/murphy/run.py --output /tmp/murphy-fresh-01
```

The output path must not exist. The runner executes each of six stages once,
with a 120-second total wall limit, at most 45 seconds per child, Python address
space limited to 1 GiB and Node old-space limited to 256 MiB. It stops on the
first failure or exhausted budget, retains outputs and performs no retry.
The original reducer's tighter limits remain active. This is a trusted fixed
fixture replay, not a sandbox for hostile arbitrary programs.

The Zot stage reads the already retained, separately licensed reference under
`../zot_prefix_machine/` at exact Git blob pins. No additional copy of that
reference source is included here. No Rust binary, native Adva process or old
frame receiving campaign is launched.

## Results and distinctions

| Observation | Retained result |
| --- | --- |
| Zot reading and finish wrapper | 125 CEK transitions, empty printer output |
| Pure Iota value | 823 characters, beta-normalization agrees with original value |
| `murphy murphy` | 1,808 Iota/S/K contractions, finite normal form distinct from murphy by beta equality |
| Coordinate conjugation / J | `C^2 = I`, `J^2 = -I`, `C J C = -J` on the explicit signed-coordinate domain |
| Coordinate / frame / carrier study | 400 checks, plus 16 table-adjoint checks |
| `murphy` on the declared `Kip Thorne` chain | 898 contractions, characters retained with an attached program value |
| `murphy murphy` on that chain | 1,813 contractions, characters retained with a different attached value |
| C twice on that chain | Does not restore the input; this is outside the coordinate domain |

The counts use different machines and cannot be interchanged. A symbolic normal
form is not a decoded string or a native Adva halt certificate. This experiment
does not implement the proposed end-leaf splice, general Adva `D*`, a general
conjugate of murphy, or a Futamura specializer.

The source grammar in all `.iota` files is `i` for the Iota combinator and
`*AB` for application. The letter `i` in the text probe is a separately tagged
opaque character, not an Iota token or imaginary unit.

## Evidence map

- `evidence/zot-trace.json`: all 125 original CEK transition records.
- `evidence/translation.json`: original translation and eager-evaluation checks.
- `evidence/result.json`, `evidence/PP-trace.json`: frozen base results and all
  1,808 combinator rewrite records.
- `adjoint_evidence/`: frozen table operations and 16 checks.
- `evidence/text-probe.json`: the four explicit character probes.
- `evidence/publication-replay/`: fresh-process publication validation and its
  source pins; exact matching payloads refer to their already retained copies.
- `attempts/adjoint-control-v0/`: the unsuccessful first reflection witness and
  its script; this attempted counterexample was corrected, not erased.
- `evidence/research-note-2026-09-19.zh-CN.md`: the original Chinese report,
  retained as written before naming and publication. Its "not pushed" statement
  refers to that earlier experiment stage.
- `inputs/source_manifest.json`, `source-review.json`: exact source/version pins.
- `SHA256SUMS`: publication-unit byte inventory, not semantic identity.

Authored by ChatGPT (OpenAI), submitted through Mingli Yuan's GitHub account as
an authorized proxy. Mingli supplied the research direction, left/right
intuition and name. Account use is not his technical review or endorsement.
New project-original contributions are dedicated under Unknown v0.3. The exact
copied frame/carrier synthetic inputs retain their declared project authorship
and source records. No book, film text, figure or other third-party expressive
material is incorporated. Publication admission is recorded under
`governance/publication/records/murphy-iota-2026-09-19.json`.
