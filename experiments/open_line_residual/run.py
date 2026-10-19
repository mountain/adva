"""Finite research-only open-line proposal; no native identity or operation."""

import hashlib
import json
from pathlib import Path
import resource
import sys
import time
from dataclasses import asdict, dataclass, replace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests/python"))
from test_bootstrap_zero_line_coordination import _renamed_closed  # noqa: E402
from test_bootstrap_zero_syntax_coordination import _coordinate_am  # noqa: E402
from test_bootstrap_zero_whole_cut_grammar import (  # noqa: E402
    Alternative, AlternativeDecl, Atom, HistoryComposition, Hole, HoleDecl,
    OpenPort, Use, _fixture, _line_view, _validate_whole,
)


@dataclass(frozen=True)
class OpenLineProposal:
    """A local paired-record proposal, deliberately not the closed LineView."""

    whole: str
    ports: tuple
    channels: tuple
    open_ports: tuple
    holes: tuple
    residuals: tuple


def propose(form):
    return OpenLineProposal(
        form.name, form.ports, form.channels, form.open_ports,
        form.holes, form.residuals,
    )


def receive(term, expected, candidate):
    # Trusted finite dataclasses only; not an arbitrary-byte or hostile-object parser.
    if (len(expected.cells), len(expected.ports), len(expected.channels),
            len(expected.open_ports), len(expected.residuals)) != (3, 6, 2, 2, 2):
        raise ValueError("outside the fixed open-line domain")
    if any(channel.thread for channel in expected.channels):
        raise ValueError("this trial admits only empty thread words")
    _validate_whole(expected)
    if type(candidate) is not OpenLineProposal or candidate != propose(expected):
        raise ValueError("proposal differs from independently bound source")
    am = _coordinate_am(term, expected)
    bindings = tuple((item.port, item.hole, item.residual) for item in candidate.open_ports)
    if am.residuals != candidate.residuals:
        raise ValueError("AM and open-line residual ledgers differ")
    return {"status": "PairedResearchRecord", "am": asdict(am),
            "open_line": asdict(candidate), "open_bindings": bindings}


def term_for(form):
    hole, port = form.holes[0], form.ports[0]
    return HistoryComposition(Hole(hole.name, hole.value_type),
                              Use(port.source, port.occurrence, port.value_type))


def fresh_open():
    form = _renamed_closed("open-reuse-")
    removed = form.channels[-1]
    opened = tuple(OpenPort(p, "hole-" + p, "residual-" + p)
                   for p in (removed.source_port, removed.target_port))
    return replace(
        form, channels=form.channels[:-1], open_ports=opened,
        residuals=tuple(x.residual for x in opened),
        holes=tuple(HoleDecl(x.hole, "A", x.port) for x in opened),
        alternatives=tuple(AlternativeDecl(x.hole, (
            Alternative(x.hole + "-0", "A", Atom("body-0")),
            Alternative(x.hole + "-1", "A", Atom("body-1")),
        )) for x in opened),
    )


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      default=lambda x: x.value).encode()


def main(output):
    if output.exists():
        raise ValueError("output already exists; preserve previous attempts")
    started = time.perf_counter()
    contract = json.loads((Path(__file__).parent / "contract.json").read_text())
    for path, digest in contract["input_sha256"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
    construction_start = time.perf_counter()
    first, fresh = _fixture(open_last=True), fresh_open()
    altered = replace(first,
        open_ports=tuple(replace(x, residual="changed-" + x.residual)
                         for x in first.open_ports),
        residuals=tuple("changed-" + x for x in first.residuals))
    candidates = (propose(first), propose(fresh))
    terms = (term_for(first), term_for(fresh))
    construction_seconds = time.perf_counter() - construction_start
    assertions = 0
    records = []

    def check(condition):
        nonlocal assertions
        assertions += 1
        if not condition:
            raise AssertionError(f"check {assertions} failed")

    receipt_times = []
    for label, form, candidate, term in zip(
            ("canonical", "fresh-reuse"), (first, fresh), candidates, terms):
        before = time.perf_counter()
        result = receive(term, form, candidate)
        receipt_times.append(time.perf_counter() - before)
        check(tuple(result["am"]["residuals"]) == form.residuals)
        check(len(result["open_bindings"]) == 2)
        check(result["am"]["holes"] == ((form.holes[0].name, "A"),))
        try:
            _line_view(form)
        except ValueError as error:
            legacy = str(error)
        else:
            legacy = "unexpected acceptance"
        check(legacy == "a closed line view needs a perfect through matching")
        records.append({"case": label, "input": {"source": asdict(form),
                        "term": asdict(term), "candidate": asdict(candidate)},
                        "output": result, "closed_view_refusal": legacy})
    check(first.name != fresh.name)
    check(first.residuals != fresh.residuals)
    check(tuple(p.occurrence for p in first.ports) != tuple(p.occurrence for p in fresh.ports))
    # A concrete failure of forgetting residual coordinates: both sources validate.
    _validate_whole(first)
    _validate_whole(altered)
    erase = lambda f: (f.name, f.ports, f.channels)
    check(first != altered)
    check(erase(first) == erase(altered))
    check(propose(first) != propose(altered))
    records.append({"case": "erasure-collision", "source_a": asdict(first),
                    "source_b": asdict(altered), "equal_erased_projection": True,
                    "distinct_open_proposals": True})
    c = candidates[0]
    mutations = {
        "foreign-whole": replace(c, whole=fresh.name),
        "reversed-ports": replace(c, ports=c.ports[::-1]),
        "omitted-channel": replace(c, channels=c.channels[:-1]),
        "reversed-open-ports": replace(c, open_ports=c.open_ports[::-1]),
        "omitted-residual": replace(c, residuals=c.residuals[:-1]),
        "renamed-residual": propose(altered),
        "rebound-hole": replace(c, holes=(replace(c.holes[0], port=c.holes[1].port), c.holes[1])),
    }
    negative_start = time.perf_counter()
    for name, candidate in mutations.items():
        try:
            receive(terms[0], first, candidate)
        except ValueError as error:
            reason = str(error)
        else:
            reason = "unexpected acceptance"
        check(reason == "proposal differs from independently bound source")
        records.append({"case": name, "expected_source_case": "canonical",
                        "candidate": asdict(candidate), "outcome": "Refused", "reason": reason})
    negative_seconds = time.perf_counter() - negative_start
    serial_start = time.perf_counter()
    payload = encode(records)
    check(json.loads(payload)[0]["output"]["open_bindings"] ==
          [[x.port, x.hole, x.residual] for x in first.open_ports])
    serialization_seconds = time.perf_counter() - serial_start
    check(len(payload) < contract["budgets"]["max_evidence_bytes"])
    check(time.perf_counter() - started < contract["budgets"]["trial_timeout_seconds"])
    output.mkdir(parents=True)
    (output / "cases.json").write_bytes(payload + b"\n")
    report = {"status": "Passed", "assertions": assertions,
        "positive_cases": 2, "refusal_cases": 7, "closed_view_refusals": 2,
        "erasure_collision_pairs": 1, "receiving_calls": 9, "search_nodes": 0,
        "new_words": 0, "construction_seconds": construction_seconds,
        "first_receiving_seconds": receipt_times[0], "reuse_receiving_seconds": receipt_times[1],
        "negative_receiving_seconds": negative_seconds,
        "serialization_and_decode_seconds": serialization_seconds,
        "total_seconds_before_summary": time.perf_counter() - started,
        "peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "cost_missing": ["primitive checker work units", "hard memory enforcement",
                         "human practical-use measurement", "implementation authoring time"],
        "base_commit": contract["base_commit"],
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (output / "execution.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
