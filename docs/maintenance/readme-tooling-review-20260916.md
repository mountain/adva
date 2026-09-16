# README and tooling entry review, 2026-09-16

Direction: Mingli Yuan requested a fuller reading of Adva before rewriting its
entry point and considering a tooling workflow for people with stalled problems.
Reading, analysis and documentation: ChatGPT (OpenAI), submitted through Mingli
Yuan's GitHub account (`mountain`) as an authorized proxy. Account ownership is
not personal authorship, review or a correctness guarantee; this is not
institutional review by OpenAI.

## Reading boundary

The initial checkout was `4027933725c00ac81643e80e96dc59d5a2bb599a`, with
`adva-library` at `9928b11841f95235fbe4c17da431779f71eaa6b3`.
The reading inventory covered all **448 tracked Markdown documents** in that
checkout and submodule: 418 in the main repository and 30 in the library.
The reading included numbered and named research, nested evidence notes,
philosophy, ontology, ADRs, engineering, maintenance, experiments and trials.

Before integration, main advanced to
`6c01852c07250174e0ec0c3ad8b55d6a8cb5dcdc`. Its two new Markdown documents —
the Futamura research note and experiment README — were read in full, along
with the changes to the agenda and research index. This brings the source
document coverage to **450**, before this contribution's new documents.

This is document coverage, not a claim to have audited every line of code,
every generated artifact, every PDF, or every external reference. The claim
registry was parsed and inspected for the entry-point claims; it was not
independently proved. Source checks for the executable entry points included
the complete data-machine implementation and CLI boundary, the exchange and
chain checkers, and the new compilation experiment and its receiving tests.
Historical mathematical results remain attributed to their recorded runs.

## Editorial decisions

- Lead with the finite-observer question and a distinction a newcomer can
  understand: two explanations fit one observation, while another separates
  them. Follow it with the positive case in which a degree bound and a theorem
  make finite observations sufficient.
- Keep the connection to arithmetic, program construction, philosophy,
  geometry and language formation visible. A generic logging workflow would
  omit the project's central research question.
- Separate PSC0, the research data language, external experiments and open
  construction targets. In particular, arithmetic-universality vocabulary is
  proposed; an arithmetic interpreter is not full self interpretation.
- Use the current bounded interpreter and the five-round disclosed exchange
  as entry points. Preserve the engine details in `docs/DEVELOPMENT.md`.
- Include the newly arrived fully static compilation calibration with its
  compile cost, restricted observation and host-loading boundary. Do not
  describe it as a general specializer or a measured wall-clock speedup.
- Replace the old unqualified library quickstart with a link to the frozen
  receiver procedure. Old epoch profiles include their original lockfile;
  modifying their pins to make current admission pass would change the claim.
- Add an explicit current checkpoint above the exchange experiment's older
  waiting-for-reply narrative. Preserve the earlier account and the raw records.
- Invite readers to bring a failed attempt and remaining question. A star is
  an optional response to finding the work useful, not evidence of validity or
  a substitute for challenge eligibility and licensing requirements.

## Changes

| File | Purpose |
|---|---|
| [README](../../README.md) | English introduction, concrete examples, current entry points and reading routes. |
| [Chinese README](../../README.zh-CN.md) | Explain finite observation and arithmetic truth without assuming the full mathematical vocabulary. |
| [Development guide](../DEVELOPMENT.md) | Preserve PSC0 examples, stable/research boundaries, prerequisites and replay guidance. |
| [Tooling workflow](../TOOLING_WORKFLOW.md) | A proposed problem card, finite session, handoff and measured evaluation; existing tools are distinguished from future interfaces. |
| [Exchange README](../../experiments/bounded_observation_exchange/README.md) | Clarify the already retained fifth reply without rewriting its history. |

No semantic code, claim, license, budget, historical witness or submodule revision
is changed by this contribution. No challenge submission or external invitation
is sent.

## Checks and limits

- The existing exchange-chain command ran successfully:
  `DisclosedByteChainChecked`, five received replies, four stale-reply controls.
  All five retain unverified source binding and withheld semantic acceptance.
- `python -S python/adva/adva.py math-check --key-words` returned
  `CatalogConsistent` and `MatchedDeclaredKeys`; mathematical proofs are not
  rechecked and native admission is not granted by this command.
- The newly referenced compilation record's existing receiving tests passed:
  `python -m pytest -q tests/python/test_futamura_first_projection.py`,
  **7 passed**. These tests inspect records and reconstruct the compiler;
  they do not execute the native campaign.
- Relative file links, fenced shell syntax and diff whitespace were checked
  for the new entry documents. This is structural documentation validation,
  not a browser rendering test or a user comprehension study.
- Rust and Cargo are unavailable on this host. The native build, interpreter
  quickstart, suspension example and full Rust/Python suite were **not run**.
  Native example output is stated as expected, from the existing implementation
  and retained reports, rather than as a new execution by this contribution.

The tooling proposal has not been tested with new participants. Whether it
reduces repeated work or improves challenge construction remains an empirical
question; the proposed comparison includes record-keeping and checking costs.
