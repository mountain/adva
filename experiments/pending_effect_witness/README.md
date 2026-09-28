# Pending effect witness receiver

This project-original bounded experiment receives evidence about one exact
`pending` ledger from Research 0247. It does not run an effect and never edits
the ledger or witness.

Replay from the repository root with a new output directory:

```sh
python experiments/pending_effect_witness/run.py --output /tmp/adva-pending-effect-witness
```

`NoEffectWitnessVerified` means only that the declared complete finite channel
and sequence interval contain no matching event. It is not a claim that no
effect occurred anywhere. Missing, incomplete or conflicting material remains
`UnknownConsumptionState`.
