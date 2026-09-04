# First Bounded Named `M6` Reveal Run

Status: executable research calibration; semantic filler remains open

This experiment is the first checked-in `.adva` program and the first CLI
command that emits a new `.adva` witness. It tests whether observer-local names
can be retained as presentation data while the relation judgment remains
coordinate- and mechanism-based.

## 1. Program

`programs/bootstrap-0/reveal.adva` is a validated neutral-carrier document. Its
initial input is read as:

```text
subject = first:observer:local-knowledge-snapshot
method  = first:program:reveal
object  = first:witness:bootstrap-zero-seed
```

This is one self-contained document graph. V0 does not yet compose three
independent `.adva` files at the command boundary.

The graph contains two complete three-frame paths with exact common endpoints:

```text
forward:   frame 0 compute -> frame 1 verify  -> frame 2 compute
conjugate: frame 3 verify  -> frame 4 compute -> frame 5 verify
```

Every adjacent frame reuses all three previous output carrier coordinates.

## 2. Injected naming

The first observer vocabulary is:

| side | name | proposed directed reading | frame mechanism |
|---|---|---|---|
| forward | `run` | construction to time | compute |
| forward | `reveal` | time to space | verify |
| forward | `name` | space to construction | compute |
| conjugate | `instantiate` | construction to space | verify |
| conjugate | `resume` | space to time | compute |
| conjugate | `compile` | time to construction | verify |

The two three-name sides are oppositely oriented domain cycles and together
cover all six off-diagonal directed pairs. This supplies a falsifiable naming
calibration; it does not prove that the mathematical `M6` boundary has these
real-world meanings.

Names are stored as entry-point selectors and resolved to frame IDs. They do
not enter the abstract relation word. The checked words remain:

```text
compute verify compute
verify compute verify
```

## 3. Reproducible command

```bash
cargo run -p adva-witness --bin adva -- \
  reveal programs/bootstrap-0/reveal.adva \
  --fuel 6 \
  --output target/first-reveal-witness.adva \
  --print
```

The CLI performs these bounded actions:

1. decode and validate the neutral source document;
2. validate the six-name domain plan;
3. resolve names to document-local frame coordinates;
4. consume at most six occurrence units of fuel;
5. derive and check the stored-frame `M6` relation after all six are observed;
6. atomically save a checked reveal-witness envelope.

With fuel less than six, the command emits a `suspended` witness containing
the observed prefix, remaining names, and one fuel-boundary question. It does
not call finite exhaustion an error or nontermination proof.

## 4. Expected first result

At fuel six, the finite run completes its observation and retains this order:

```text
run, reveal, name, instantiate, resume, compile
```

The result contains a formed `M6` boundary, both raw paths, exact three-port
handoffs, the source document digest, and the formation certificate. It also
contains exactly one unresolved question:

```text
kind: relation_filler
residual: experiment:first:m6-semantic-filler-required
```

Thus `completed` describes observation of all six stored occurrences. The
relation itself is still `open` and cannot be transported.

## 5. What the experiment does not establish

The recorded frame outputs still lack execution provenance. The runner does
not execute `compute`, `verify`, or `learn` semantics, replay a shared
knowledge-base witness, discover a cut, continue independent branches, compare
multiple observers, or show that the injected six-direction vocabulary is
canonical. Its first evidential content is narrower:

> one validated persistent graph supports two exact named paths whose
> mechanism words form the bounded `M6` profile, and a finite observer can
> publish that formation together with its unresolved semantic question.

The next calibration should vary snapshot time, visible carrier scope, and
naming plan independently. Exact matches, certified alignments, trust-policy
rejections, and merely unnamed results must remain distinct.
