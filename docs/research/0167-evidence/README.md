# Research 0167 evidence

Byte copies of the two artifacts that produced
[Research 0167](../0167-li-yorke-period-three-and-homotopy-continuation.md),
taken on 2026-09-11 before either was moved or deleted. Both previously existed
only outside version control, in directories that are not repositories.

## 1. What is retained

| File | Origin before this copy | sha256 |
|---|---|---|
| `literature-report-raw.md` | `/Users/mingli/Adva/li-yorke-chaos-and-homotopy-report.md`, a workspace root that is not a git repository | `7228b402b689d05d6c356e20005225b0f791d8b66255c6ff51cd0630da272248` |
| `first-draft-check.py` | `/tmp/liyorke-check/check.py`, a scratch directory | `824eb54e250e266417282cad942e794c5fc4f80357dbb5d2c760ea05982673ca` |
| `first-draft-matrix-bridge.py` | `/tmp/liyorke-check/matrix_bridge.py` | `7c3f7f4cef09c25dab0a20d3a1ee5dee50dd7d81f9272379a059087627ea4da2` |
| `first-draft-one-hole.py` | `/tmp/liyorke-check/onehole.py` | `3127bc58aa5da2295d2b79e7b36ed3c6dbcdee542bbda6af8ffb3cd5e5d00eb7` |

Each copy was verified byte-identical to its origin with `cmp` before the origin
was left in place. Nothing was edited in transit, so the digests above pin the
originals, not a tidied version of them.

## 2. Precedence

**0167 is the authoritative reading, not `literature-report-raw.md`.** The raw
report is retained as the record of *what was actually read and how*, including
its own flagged items and the four corrections it makes to its brief. Where the
two differ in wording, 0167 governs; where 0167 records a correction, the raw
report is the earlier form and is not rewritten.

The raw report was produced by a delegated literature reading that was given a
brief containing four wrong premises. It corrected all four, and it twice
declined the framing the brief invited: it flagged rather than resolved a
disagreement with a secondary source over whether T1 is Sharkovsky's period-three
corollary, and it refused to write a paragraph about the "irony" of one career
holding both programmes because no source documents that link. Both refusals are
why 0167 section 7 records the observation as an outside reading.

## 3. Why the first drafts are retained rather than deleted

They are superseded, and one of them is partly wrong.

`first-draft-check.py` counts the fixed points of the tent-map iterate by
scanning two million floating-point samples and bisecting sign changes. That is
not a proof of anything: it is a numerical illustration whose result happens to
agree with the registered checker. The registered experiment replaces it with an
exact method — every one of the `2^n` linear branches is verified to map onto
`[0,1]` with slope `+/-2^n`, each fixed point is solved in closed form over
`Fraction`, and each solution is verified exactly. The float scan would have been
recorded as evidence for a claim it cannot support, which is precisely the
failure this repository's `bounded-experiment` discipline exists to refuse
("No numerical plot or sampled complex trajectory is sufficient evidence").

`first-draft-matrix-bridge.py` and `first-draft-one-hole.py` are sound but
unstructured: they compute the same identities without a contract, a budget, a
refusal control, or an evidence record. The registered checker
(`experiments/li_yorke_period_three/`) derives the interval graph from exact
interval images instead of stipulating it, adds the wrong-matrix control and the
rotation isometry control, and writes a pinned report.

They are kept because a superseded attempt and a rejected method are part of the
record. `AGENTS.md` requires that a reverted half-working attempt and a failed
control be written down rather than quietly repaired.

## 4. What this directory is not

- It is not the claim's evidence. The registered entry
  `adva.bounded-experiment.li-yorke-period-three-matrix.v0` names
  `experiments/li_yorke_period_three/` as its checker and evidence.
- It is not executable evidence of any mathematical statement. Nothing here runs
  in CI and nothing here is cited as a check.
- It is not a second home for the literature. The sources are read in 0167
  section 11; only the working report is retained here.
