# Research 0250: Pending effect and bounded no-effect witnesses

Status: **bounded read-only receiving result**. This note adds no native
operation, general exactly-once guarantee, recovery permission or vocabulary
word.

## Question and frozen boundary

[Research 0248](0248-one-consumption-chain-and-the-pending-unknown.md) keeps a
single consumption slot at `pending` after a process disappears. Retrying is
unsafe because the effect may already have occurred. Merely leaving the slot
unknown is safe but gives no way to examine later evidence. This run asks the
next finite question: can a separate receiver distinguish evidence that one
effect was recorded, evidence that no matching effect was recorded in one
complete finite channel, and evidence that remains insufficient?

The [frozen contract](../../experiments/pending_effect_witness/contract.json)
fixes ten receiver processes, zero target processes, 20,000 total counted work
units, one second per receiver, fifteen outer seconds, zero search candidates
and at most one implementation-correction replay. It imports the exact pending
ledger digest and pair digest from Research 0248. The kernel/package boundary
is the canonical
`mountain/adva-machine/spec/framework/kernel-package-boundary-v0.1.md` at
`acfc9806fe18a36d0f7194dcc196a380b2834adf`; this remains an `adva` research
package and changes no kernel or executable profile.

The receiver is read-only. A witness binds an attempt, pair, channel and closed
sequence interval. One matching event is accepted only when the supplied
result bytes reproduce its SHA-256 coordinate. Zero matching events can be
accepted only when that exact finite channel declares its interval complete.
This is a bounded observation, not a statement that no effect happened outside
the selected channel or interval.

## Executed distinctions

Ten cases passed all checks:

| Case family | Result | Meaning in this experiment |
| --- | --- | --- |
| Exact alpha event plus result bytes | `EffectWitnessVerified` | one matching event and recomputed result digest |
| Byte-identical alpha replay | `EffectWitnessVerified` | verification repeats; no effect repeats |
| Complete empty gamma channel | `NoEffectWitnessVerified` | no matching event in this finite channel and interval only |
| Incomplete or missing material | `UnknownConsumptionState` | absence does not establish nonoccurrence |
| Two matching effect events | `UnknownConsumptionState` | conflict is retained rather than selected away |
| Attempt or pair substitution | `InvalidContext` | a well-formed witness answers another question |
| Wrong result bytes or duplicate sequence | `InvalidEvidence` | the proposed evidence fails its own finite rules |

Every receipt keeps effect, retry, refund, mutation, native and `free`
authority false. All ledgers and supplied witnesses remain byte-identical. No
target program starts and no pending state is changed.

The Gamma case is the required new-instance reuse. Its pair and attempt differ
from Alpha. The result is not inherited from Alpha and the two instances share
only the declared receiver grammar.

## Cost, failure record and replay

The [retained execution](../../experiments/pending_effect_witness/evidence/attempt-1/execution.json)
passes 145 assertions across ten receiver processes. It reports 6,194 counted
work units, 1.469044101999998 seconds of receiver-process wall time and
1.482247174999884 seconds for the whole supervisor interval. Maximum child and
supervisor RSS are each 11,648 KiB; these are category maxima, not a concurrent
total. There are zero search candidates, zero target processes and zero
implementation-correction replays. Reading, authoring and publication time are
not measured.

Before the experiment ran, a shell wrapper requested `/usr/bin/time`, which is
absent on this host. The command stopped with exit 127, created no output and
started no receiver. The
[retained wrapper failure](../../experiments/pending_effect_witness/evidence/prior-wrapper-failure.json)
is classified separately as `PreExecutionEnvironmentFailure`, not as a
mathematical result or an implementation-correction replay. The sole subsequent
execution used the unchanged Python sources and their already implemented wall
and RSS accounting.

Replay from the repository root with a new output path:

```sh
python experiments/pending_effect_witness/run.py \
  --output /tmp/adva-pending-effect-witness
```

## Meaning and remaining obligation

No new word is justified. Existing distinctions among effect evidence,
bounded observation, invalid context, invalid evidence and unknown state are
sufficient. `EffectWitnessVerified` and `NoEffectWitnessVerified` are local
receipt outcomes, not promoted framework vocabulary.

This helps Mingli and subsequent agents avoid two symmetric errors: treating a
claimed result digest as proof without checking its bytes, or treating an empty
or absent file as proof that nothing happened. It also preserves conflict
instead of selecting whichever event makes continuation convenient. Its value
for Jiamin's actual task remains unmeasured.

The finite event channel and its completeness declaration are trusted
project-original inputs. This run does not authenticate an observer, prove that
the channel is physically exclusive, survive power loss, contain a malicious
process, or establish distributed consistency. A no-effect receipt does not
authorize retry, and an effect receipt does not mutate the pending ledger. The
result establishes neither Research 0090 coverage, Research 0092 promotion,
native `free` or `Close`, M6 closure, hypothesized arithmetic truth nor
arithmetic universality.

The next minimum step is an atomic **application** receiver. It should accept
one exact recovery receipt and the unchanged pending ledger, produce either a
completed receipt or a separately versioned cancellation state, and refuse
replay or conflict without starting the target. Until that transition is
checked, the original ledger remains pending.

Authored by Codex (OpenAI), contributed under Unknown v0.3 through Mingli
Yuan's authorized GitHub account proxy. Account use is not his authorship,
review, endorsement or correctness guarantee.
