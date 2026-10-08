# External program positivity metaprogram

`meta.py` receives a finite rational arithmetic program as JSON data, executes it
on supplied fillings, derives observation regions, and checks an explicitly
chosen positivity theory. Different programs can be supplied without changing
the analyzer. Everything here is external research tooling, not native Adva IR.

Run from the repository root using Python 3.12 and the standard library:

```sh
python experiments/program_positivity/meta.py \
  experiments/program_positivity/examples/mobius_joint.json \
  --output /tmp/adva-mobius-report.json
python experiments/program_positivity/verifier.py \
  experiments/program_positivity/examples/mobius_joint.json \
  /tmp/adva-mobius-report.json
```

The report path must be new. Existing output is refused before analysis. To
change a program, edit a copy of its request and choose a new report path. A
report binds the canonical request and exact producer/contract bytes by SHA-256.
The verifier must therefore use the matching source revision.

The request contains:

| Field | Meaning |
| --- | --- |
| `schema` | `adva.external-program-positivity-request.v0` |
| `program.holes` | Ordered external input labels, at most 8 |
| `program.steps` | At most 64 ordered `{name, op, args}` steps |
| `program.outputs` | At most 8 labels mapped to arithmetic tokens |
| `fillings` | 1–4 indexed dictionaries supplying every hole |
| `observations` | Named exact comparison or Boolean predicate trees |
| `properties` | Named Boolean region expressions, with acyclic references |
| `theory` | `policy`, `positive`, `negative`; `marked` for marked policy |
| `query` | Ordered names whose positivity is to be checked |
| `domain` | Optional guards that every declared filling must satisfy |
| `limits` | Optional `{ "fuel": N }`, with `0 <= N <= 200000` |

Arithmetic tokens are prior hole/step labels or canonical reduced rational
strings, such as `"-3/2"`. Predicates may also refer to `"out.result"`.
Operations are `const`, `neg`, `add`, `sub`, `mul`, and checked `div`.
Predicates use `{ "op": "gt", "args": ["out.result", "0"] }`, or
`and`, `or`, `not` over predicates. Regions refer to observation/property names,
`all`, `empty`, or use `and`, `or`, `not`, `xor`. Forward property references are
allowed; arithmetic forward references and property cycles are invalid.
No supplied token is executed as host-language source.

The positivity property domain is the full powerset of the supplied trial
indices, including unnamed regions. All policies impose static A1 (exactly one
of a region and its complement is positive) and static A2 (upward closure).
`basic` adds no common witness; `joint` requires one trial shared by every
positive region; `marked` fixes that trial to the declared index. Signed
premises restrict the surviving interpretations. These policies express chosen
meanings of positivity; arithmetic alone does not choose them.

| Query result | What the retained evidence establishes |
| --- | --- |
| `ForcedPositive` | Every surviving interpretation makes the region positive |
| `ForcedNegative` | Every surviving interpretation makes it negative |
| `Underdetermined` | Positive and negative interpretations both survive |
| `Inconsistent` | No interpretation satisfies the declared theory |
| `Unknown` | No complete positivity conclusion was obtained |

Program status is separately `Analyzed`, `UndefinedOnCarrier`, `InvalidInput`,
`Unsupported`, or `Unknown`. A zero divisor produces a concrete filling/step
failure. These incomplete statuses never emit a decisive positivity result.
`inhabited` records whether a region contains supplied trials; it is separate
from positivity. Witness indices refer to retained models or trial indices,
never native Adva semantic identities.

Reports retain exact step values, outputs, observer incidence, region masks,
every surviving positivity model, common realizers, query witnesses and fuel.
The independent verifier imports no producer code: it recursively evaluates
arithmetic dependencies and enumerates ordinary set families separately.
`Verified` checks a complete finite claim or an exact division failure;
`NoClaim` checks conservative withholding, without proving the producer's
diagnostic reason.

To reproduce the frozen campaign in a new directory:

```sh
python experiments/program_positivity/run_campaign.py /tmp/adva-meta-campaign
```

This makes at most five subprocess launches: ordinary and optimized batch
analysis, independent receiving, unit/mutation checks, and overwrite refusal.
The contract bounds wall time, aggregate CPU, memory, fuel and output; there is
no automatic retry. `cases.json`, `evidence.json` and `campaign.json` retain the
14-case experiment. See [Research 0261](../../docs/research/0261-external-program-positivity-metaprogram.md).

Conclusions concern the supplied finite trials. Unbounded loops, calls, arbitrary
programs, intrinsic positivity, all real fillings and full modal A1–A5 remain
outside this grammar. The tool does not evade Rice's theorem.

Authored by Codex (OpenAI), contributed under Unknown v0.3 through Mingli Yuan's
authorized account proxy; not his authorship, review or correctness endorsement.
