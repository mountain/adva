# Zot baseline and prefix-Keraia boundary

External research only. The [research note](../../docs/research/zot-prefix-machine-weighted-sharing.md)
defines the machine, evidence, corrections and native boundary.

~~~sh
node experiments/zot_prefix_machine/run.cjs > /tmp/zot-keraia-replay.json
~~~

Use a fresh destination. The CLI writes to stdout and sets a nonzero exit
code on an incomplete campaign. Timings are not byte-stable. Machine/checker
bodies ran in V8; real Node/QuickJS was unavailable on the recorded host.

- machine.cjs: explicit CBV Zot, CEK steps, local checkpoints, strict framing,
  prefix and full-closure caches.
- verify.cjs: independent higher-order source oracle, weighted ledgers,
  cost-debit comparisons, controls and checkpoint verification.
- keraia-boundary.cjs: two parsers, exact Catalan/DP syntax mass, generic input
  controls. No Keraia evaluator.
- contract.json and keraia-contract.json: separate fixed budgets.
- evidence.json and keraia-evidence.json: accepted scoped records.
- evidence-attempt-1.json, evidence-regression-raw.json: retained earlier records.
- regression-contract.json: same-family checkpoint retention replay.
- compare.cjs, comparison-contract.json, comparison-evidence.json: structural
  comparison correcting an object-key-order false negative, without new search.
- reference-zot.js and LICENSE.reference: pinned source and MIT license,
  originally Chris Barker, modified Mingli Yuan.

Authored by ChatGPT (OpenAI); submitted through Mingli Yuan's GitHub account
as authorized proxy. Account use implies no human review or endorsement.
