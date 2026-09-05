# Research 0115: Frontier-to-hypothesis interface experiment

## Question

Can the five open arithmetic questions cross a finite-observer/external-world
boundary in a form that another observer can continue after local time or
energy is exhausted?

The test is intentionally weaker than finding an answer. It asks whether the
questions, algorithm, external contribution, failed closure, and next input
can all survive interruption without relying on a prose name.

## Fixed boundary

The experiment uses the same positional interface for load and save:

| Mechanism | `subject` | `method` | `object` | `history` | `result` | `evidence` |
| --- | --- | --- | --- | --- | --- | --- |
| `learn` | `frontier.adva` | `exploration.adva` | `resource.adva` | selection receipt | proposed hypothesis | next `frontier.adva` |

The slot labels are stable. Artifact schemas provide the local reading. This
keeps the carrier boundary neutral while preventing a loader from guessing how
to unpack it.

## Inputs

1. `first-trace-arithmetic.adva` retains both ordered M6 paths and five exact
   question coordinates.
2. `exploration.adva` freezes the version-zero algorithm: take the first
   recorded candidate and treat every external claim as proposed only.
3. `resource.adva` is an unauthenticated external-session snapshot. It records
   a 32-byte entropy output and one falsifiable candidate named
   `representation`.

The candidate proposes an anchor-relative typed representation

\[
\rho_a : \mathrm{Trace}_{C,V,L} \longrightarrow \mathrm{End}(E_a).
\]

This is a search direction, not a constructed map. The missing anchor,
endomorphism images, three characteristic witnesses, holonomy identity, and
shared truth coordinate are listed as required observations. Concrete failure
conditions are stored beside them.

## Run

```console
cargo run -p adva-witness --bin adva -- \
  frontier programs/bootstrap-0/first-trace-arithmetic.adva \
  --output programs/bootstrap-0/frontier.adva

cargo run -p adva-witness --bin adva -- \
  learn \
  programs/bootstrap-0/frontier.adva \
  programs/bootstrap-0/exploration.adva \
  programs/bootstrap-0/resource.adva \
  --output programs/bootstrap-0/hypothesis.adva \
  --frontier-output programs/bootstrap-0/frontier-1.adva
```

The first command introduces `frontier`. The second introduces the structural
word `hypothesis`; the selected resource contributes the content word
`representation`.

## First recorded result

The CI-run experiment completed one bounded edge and retained these integrity
coordinates:

| Artifact | BLAKE3 coordinate |
| --- | --- |
| initial frontier | `fc9ab7afe284ac122e67bf6fa659318a8c264f5dbaed654fd2540fad6f3e1e1f` |
| exploration contract | `564d0f561d9c5e8974e7ef86ccc7cef781891a1e1f831607a7f0bdb2b78aeb7f` |
| resource snapshot | `41b2260753e4df9ee94918604bfead06b353390f41c6adf981c7bcbd12686858` |
| candidate content | `fe916162d4fa9b978dad63d97433b3ee8ea4369838c1f81bb2d406288e649f19` |
| hypothesis transition | `cd93301f498db9b118a820ef2f90522b85caadd676e25a8d387ca32222cc2cd0` |
| continued frontier | `2b0c3440a8dafda28880cea92d9d87d0158d49a08d2cd9a20d4406990d0786de` |

The continued frontier has sequence `1`, introduces `hypothesis` and
`representation`, records one consumed resource and one retained candidate,
and still has exactly five open obligations. CI regenerates all three derived
files and requires byte equality with the committed copies.

## Required observations

The generated transition must demonstrate all of the following:

- all three input and output labels equal the common interface;
- all five question coordinates and open states survive unchanged;
- the algorithm-contract digest is frozen in the next frontier;
- the entropy receipt and resource digest are retained in history;
- the candidate is copied exactly and remains `proposed`;
- its name-independent identity is stable under a local rename;
- the same resource cannot be consumed twice;
- editing embedded randomness or a question coordinate invalidates the
  transition or frontier;
- the next frontier contains everything needed except a fresh resource
  snapshot.

## Interpretation

The first new interface word is `hypothesis`, because the external side can
offer a candidate but cannot manufacture truth. The first content word is
`representation`, because it is the candidate selected from this particular
recorded resource snapshot. These words have different authority.

The experiment preserves a common interface across observers but does not
solve the social trust problem. Resource provenance is explicitly
unauthenticated. A future observation artifact would need an identity and trust
policy beyond BLAKE3 integrity coordinates. Continuing forever is permitted by
the format but neither guaranteed nor inferred from one successful step.
