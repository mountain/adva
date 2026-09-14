# Keraia cycles and a certified mass upper bound

External bounded research in the existing
`keraia.appendix-b.cbn-whnf.read.v0` observation profile. The previous machine
and oracle in `../keraia_read_machine/` are imported unchanged and byte-pinned.
This experiment neither changes native Adva nor identifies this profile with
an optimal universal prefix machine.

`cycles.py` proposes finite exact-state recurrence traces using the previous
de Bruijn machine. Its receiver recompiles with the string/named compiler
and checks beta contractions using named substitution, rather than calling
the proposal kernel's beta or step functions. A positive-length cycle must
contain neither reading nor returning and must preserve the whole control,
ordered stack and absolute cursor. The complete supplied prefix must have
been consumed. These premises justify excluding every extension of that
prefix from the halting domain of the declared profile.

`calibrate.py` checks every binary word through length 15 at fuel 128 and
552 multi-read/delay cases. It retains exact accepted rows, unresolved
frontiers, positive cycle traces and negative controls. The exhaustive direct
and oracle ledgers are streamed into ordered digests rather than retained
as full per-word files. `support.py` constructs the fixed program family and
the source manifest. `supervise.py` saves exact source snapshots before one
primary run and its conditional fresh-process replay.

The fixed attempt in `evidence/attempt-1/` passed 264,671 assertions and used
5,004,990 counted host-work units per child. Both deterministic records agree;
there were no failed attempts or corrections. Fifteen deliberately invalid
cycle receipts were refused. A growing-stack loop deliberately remains
`UnknownFuel`, demonstrating the incompleteness of exact recurrence.

The global finite partition is:

| Class | Mass |
|---|---:|
| Accepted | `26078/32768` |
| Certified nonhalting | `1/32768` |
| Unresolved | `6689/32768` |

Thus the profile's eventual halting mass lies in
`[13039/16384, 32767/32768]`. A separate one-read selector has conditional
halting probability exactly `1/2`. The improvement in the global upper bound
is small and supplies no general convergence rate.

Replay from the repository root into a new directory, within a separately
finite continuation contract if another research run is intended:

```sh
timeout 100s prlimit --as=536870912 --cpu=95 --fsize=16777216 -- python3 -B -S experiments/keraia_cycle_mass/supervise.py --output-dir /tmp/keraia-cycle-new-attempt
```

The child budget includes both checkers and all fixture runs: 20 million work
units, 45 wall seconds, 40 CPU seconds, 512 MiB and 16 MiB per output file.
At most two children run, with no retry or automatic scope expansion. The
outer limits cover evidence loading and comparison. Earlier evidence must
not be overwritten.

See the [research note](../../docs/research/keraia-cycle-certificates-and-halting-mass-bounds.md)
for the extension argument, the exact-state boundary and implications for Q4.

Authored by ChatGPT (OpenAI), submitted through Mingli Yuan's GitHub account
as an authorized proxy. Account use is not human review or endorsement.
