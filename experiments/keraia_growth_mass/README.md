# Protected-stack growth certificates

External bounded Keraia experiment. Read the full question, proof, ablation and
limits in ../../docs/research/keraia-growth-invariants-and-mass-ablation.md.

At fuel 128, adding received stack-growth certificates changes no accepted-code
weights. Additional excluded mass is zero at depth 15 and 19/524288 at depth 19
(13 new cylinders). The depth-19 unresolved mass remains 95519/524288.

contract.json is the frozen run boundary. growth.py proposes finite traces and
checks their protected-bottom pumping condition using the previous independent
named-term receiver. calibrate.py measures the two arms over the same prefix
frontier. supervise.py freezes sources, runs one preflight, one primary and one
fresh replay, and stops at any failure. evidence/attempt-1 retains all three
outputs, full new certificates, compact terminal-source ledgers and original
sources. Host time/RSS differ; deterministic outputs and work counts agree.

Do not rerun into an existing evidence directory. No native semantics, general
halting algorithm, optimal-machine Omega or measured online speedup is claimed.
