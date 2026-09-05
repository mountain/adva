# Research 0116: Reality meaning and custody continuation

## Question

Run the common inquiry interface a second time, asking:

1. What can “meaning on the reality side” mean for a finite observer?
2. How can the observation and its trace resist accidental or adversarial
   destruction?

The experiment must not answer either question by equating a digest, name,
signature, replica count, or majority vote with truth.

## Candidate

The second external resource contributes the word `custody`. Its working
hypothesis is:

> A formal claim has reality-facing meaning only relative to a versioned
> external coordinate and a protocol that independent observers can apply
> again. Its continued availability requires a separately auditable custody
> chain across independent failure domains.

Operationally, the meaning criterion is invariance under independent,
protocol-conforming remeasurement within a declared tolerance, with every
disagreement retained. This is stronger than naming and weaker than absolute
truth.

## Damage decomposition

| Destructive action | Required response | Remaining limit |
| --- | --- | --- |
| mutate bytes | content address and parent-chain mismatch | detects but does not restore |
| delete records | diverse replicas, erasure-coded cold export, repair | availability depends on the declared fault budget |
| equivocate | retain both signed branches and emit fork evidence | does not decide which branch is true |
| compromise keys | rotation, revocation, and successor receipts | cannot repair claims signed before a known compromise by itself |
| capture custodians | institutional, geographic, administrative, and media diversity | independence must be demonstrated, not asserted |
| drift semantics | versioned protocol plus independent remeasurement | observations may still genuinely disagree |

The recorded proposal uses five declared failure domains, a three-receipt
observation threshold, and a three-fragment recovery threshold. These numbers
make the plan locally checkable; they are not presented as a Byzantine
consensus theorem.

## Input and output

```console
cargo run -p adva-witness --bin adva -- \
  learn \
  programs/bootstrap-0/frontier-1.adva \
  programs/bootstrap-0/exploration.adva \
  programs/bootstrap-0/resource-2.adva \
  --output programs/bootstrap-0/hypothesis-2.adva \
  --frontier-output programs/bootstrap-0/frontier-2.adva
```

The input slots remain:

- `subject`: the sequence-one frontier;
- `method`: the unchanged exploration contract;
- `object`: the second recorded resource snapshot.

The output slots remain `history`, `result`, and `evidence`. The result must be
a proposed `custody` hypothesis. The evidence must contain a sequence-two
frontier with two consumed resources, two retained candidate identities, and
the original five open obligations.

## First recorded result

The CI run completed the second bounded transition:

| Artifact | BLAKE3 coordinate |
| --- | --- |
| second resource snapshot | `e68591b84f81dc9b1584619853943846685c50ef8922cd73234e93505ff907e6` |
| name-independent custody candidate | `65c139bcf849bae3a250a2a1f2f6fdec2d5edcd95f3bb1d4b5e853179926160a` |
| second hypothesis transition | `0f501b7c26e95b4f90ce3fb832027e0b73a5ad5af82a0681b59cd170aee0a52e` |
| sequence-two frontier | `ae23c007227cf0665fd2928dfb5adb41c2d23923649f867b128bdd6533deb39c` |

The history introduced exactly one word, `custody`; it did not introduce
`hypothesis` again. The output retained two distinct resource receipts and two
candidate identities. All five original obligations remained `open`. CI now
repeats both inquiry transitions and requires byte equality for every derived
artifact.

## Falsification boundary

The proposal fails if independent remeasurement is unavailable, if supposedly
independent receipts share one origin or control domain, if deletion within the
declared budget prevents recovery, if mutation or equivocation can be hidden,
or if protocol-conforming observations disagree beyond the declared tolerance.

A successful software run checks only the structure of this proposal and the
continuation chain. Actual reality grounding requires observation records;
actual resistance requires deployed custodians, cryptographic verification,
failure injection, recovery measurements, and governance outside this
repository.
