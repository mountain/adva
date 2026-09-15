"""Finite Gold-pair control for coverage-gated object closure."""
import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
import resource
import time

HERE = Path(__file__).resolve().parent
SCHEMA_OBS = "adva.external.finite-positive-observation.v0"
SCHEMA_COVER = "adva.external.finite-domain-coverage.v0"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


class Budget:
    def __init__(self, limit, wall):
        self.limit = limit
        self.wall = wall
        self.work = 0
        self.start = time.monotonic()

    def tick(self, amount=1):
        self.work += amount
        if self.work > self.limit or time.monotonic() - self.start > self.wall:
            raise RuntimeError("resource limit")


def universe(width, budget):
    if type(width) is not int or not 1 <= width <= 8:
        raise ValueError("invalid width")
    result = []
    for bits in itertools.product("01", repeat=width):
        budget.tick()
        result.append("".join(bits))
    return result


def validate_machine(width, schedule, budget):
    words = universe(width, budget)
    if type(schedule) is not dict or any(
        type(k) is not str or k not in words or type(v) is not int or v < 0
        for k, v in schedule.items()
    ):
        raise ValueError("invalid machine")
    return words


def observe(machine_name, width, schedule, stage, budget):
    words = validate_machine(width, schedule, budget)
    if type(machine_name) is not str or not machine_name or type(stage) is not int or stage < 0:
        raise ValueError("invalid observation context")
    events = [
        {"program": program, "first_stage": schedule[program]}
        for program in words if program in schedule and schedule[program] <= stage
    ]
    budget.tick(len(words))
    return {
        "schema": SCHEMA_OBS,
        "machine": machine_name,
        "width": width,
        "stage": stage,
        "events": events
    }


def receive_observation(receipt, expected_name, width, schedule, stage, budget):
    try:
        budget.tick()
        expected = observe(expected_name, width, schedule, stage, budget)
        return type(receipt) is dict and canonical(receipt) == canonical(expected)
    except (ValueError, TypeError):
        return False


def trace_only_guess(receipt, budget):
    budget.tick()
    return {
        "rule": "unsafe-positive-trace-is-complete",
        "guessed_domain": [event["program"] for event in receipt["events"]]
    }


def attempt_close(observation, expected_name, width, schedule, stage, coverage, budget):
    if not receive_observation(observation, expected_name, width, schedule, stage, budget):
        return {"outcome": "InvalidEvidence"}
    words = universe(width, budget)
    visible = [event["program"] for event in observation["events"]]
    if coverage is None:
        return {
            "outcome": "CertificateObstruction",
            "reason": "complete finite coverage is missing",
            "positive": visible,
            "unresolved": [word for word in words if word not in visible],
            "stage": stage,
            "history_sha256": digest(observation)
        }
    try:
        budget.tick()
        required = {"schema", "machine", "width", "universe", "accepted", "rejected",
                    "receiver_schedule_sha256", "proof_kind"}
        if type(coverage) is not dict or set(coverage) != required:
            return {"outcome": "InvalidCoverage"}
        if (coverage["schema"] != SCHEMA_COVER or coverage["machine"] != expected_name
                or type(coverage["width"]) is not int or coverage["width"] != width
                or coverage["universe"] != words
                or coverage["proof_kind"] != "receiver-enumerated-finite-syntax"
                or coverage["receiver_schedule_sha256"] != digest(schedule)):
            return {"outcome": "InvalidCoverage"}
        accepted, rejected = coverage["accepted"], coverage["rejected"]
        if (type(accepted) is not list or type(rejected) is not list
                or any(type(x) is not str for x in accepted + rejected)
                or len(set(accepted)) != len(accepted) or len(set(rejected)) != len(rejected)
                or set(accepted) & set(rejected)
                or set(accepted) | set(rejected) != set(words)
                or accepted != [word for word in words if word in schedule]
                or rejected != [word for word in words if word not in schedule]):
            return {"outcome": "InvalidCoverage"}
        return {
            "outcome": "ObjectClosed",
            "machine": expected_name,
            "width": width,
            "stage": stage,
            "positive_observed": visible,
            "accepted": accepted,
            "negative_certified": rejected,
            "universe": words,
            "history_sha256": digest(observation),
            "coverage_sha256": digest(coverage)
        }
    except (ValueError, TypeError, KeyError):
        return {"outcome": "InvalidCoverage"}


def coverage_for(name, width, schedule, budget):
    words = validate_machine(width, schedule, budget)
    return {
        "schema": SCHEMA_COVER,
        "machine": name,
        "width": width,
        "universe": words,
        "accepted": [word for word in words if word in schedule],
        "rejected": [word for word in words if word not in schedule],
        "receiver_schedule_sha256": digest(schedule),
        "proof_kind": "receiver-enumerated-finite-syntax"
    }


def mutate(value, path, replacement):
    result = copy.deepcopy(value)
    target = result
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = replacement
    return result


def run(output):
    contract = json.loads((HERE / "contract.json").read_text())
    limits = contract["limits"]
    budget = Budget(limits["max_host_work"], limits["wall_seconds"])
    evidence = {
        "schema": "adva.external.gold-twin-close.evidence.v0",
        "status": "Running",
        "base": contract["base"],
        "families": [],
        "negative_controls": [],
        "checks": [],
        "failures": []
    }
    assertions = 0
    started = time.monotonic()

    def require(condition, label):
        nonlocal assertions
        budget.tick()
        assertions += 1
        if not condition:
            raise AssertionError(label)

    try:
        for family in contract["families"]:
            width = len(next(iter(family["M0"])))
            early, late = family["stage"], family["late_stage"]
            name0, name1 = family["name"] + "/M0", family["name"] + "/M1"
            early0 = observe(name0, width, family["M0"], early, budget)
            early1 = observe(name1, width, family["M1"], early, budget)
            trace0 = {"stage": early0["stage"], "events": early0["events"]}
            trace1 = {"stage": early1["stage"], "events": early1["events"]}
            require(canonical(trace0) == canonical(trace1), family["name"] + " equal early traces")
            guess0, guess1 = trace_only_guess(early0, budget), trace_only_guess(early1, budget)
            require(guess0 == guess1, family["name"] + " trace-only determinism")
            obstruction0 = attempt_close(early0, name0, width, family["M0"], early, None, budget)
            obstruction1 = attempt_close(early1, name1, width, family["M1"], early, None, budget)
            require(obstruction0["outcome"] == obstruction1["outcome"] == "CertificateObstruction",
                    family["name"] + " guarded early refusal")
            late0 = observe(name0, width, family["M0"], late, budget)
            late1 = observe(name1, width, family["M1"], late, budget)
            require(late0["events"] != late1["events"], family["name"] + " delayed separation")
            delayed = [x for x in late1["events"] if x not in early1["events"]]
            require(len(delayed) == 1 and delayed[0]["program"] not in guess1["guessed_domain"],
                    family["name"] + " unsafe close counterexample")
            cover0 = coverage_for(name0, width, family["M0"], budget)
            cover1 = coverage_for(name1, width, family["M1"], budget)
            closed0 = attempt_close(early0, name0, width, family["M0"], early, cover0, budget)
            closed1 = attempt_close(early1, name1, width, family["M1"], early, cover1, budget)
            require(closed0["outcome"] == closed1["outcome"] == "ObjectClosed",
                    family["name"] + " finite tell-tale close")
            require(closed1["accepted"] != closed0["accepted"], family["name"] + " certificate distinction")
            evidence["families"].append({
                "name": family["name"],
                "width": width,
                "early_stage": early,
                "late_stage": late,
                "common_positive_trace": trace0,
                "trace_only_guess": guess0,
                "guarded_M0": obstruction0,
                "guarded_M1": obstruction1,
                "late_M0": late0,
                "late_M1": late1,
                "counterexample": delayed[0],
                "closed_M0": closed0,
                "closed_M1": closed1
            })
        evidence["checks"].append("both Gold pairs share an early positive trace and separate at the declared later stage")
        evidence["checks"].append("missing coverage blocks object closure; complete finite tell-tales close the two distinct objects")
        evidence["checks"].append("the three-bit family reuses the same receiver without changing its implementation")

        base_family = contract["families"][0]
        width, stage = 2, base_family["stage"]
        name = base_family["name"] + "/M1"
        observation = observe(name, width, base_family["M1"], stage, budget)
        coverage = coverage_for(name, width, base_family["M1"], budget)
        tests = [
            ("boolean_stage", observation, coverage, True),
            ("float_stage", observation, coverage, 1.0),
            ("changed_machine", mutate(observation, ["machine"], "other"), coverage, stage),
            ("changed_event", mutate(observation, ["events", 0, "program"], "01"), coverage, stage),
            ("missing_event", mutate(observation, ["events"], []), coverage, stage),
            ("changed_coverage_machine", observation, mutate(coverage, ["machine"], "other"), stage),
            ("missing_universe_member", observation, mutate(coverage, ["universe"], coverage["universe"][:-1]), stage),
            ("false_negative", observation, mutate(coverage, ["accepted"], ["00"]), stage),
            ("overlap", observation, mutate(coverage, ["rejected"], coverage["rejected"] + ["00"]), stage),
            ("wrong_schedule_binding", observation, mutate(coverage, ["receiver_schedule_sha256"], "0" * 64), stage),
            ("wrong_proof_kind", observation, mutate(coverage, ["proof_kind"], "timeout"), stage)
        ]
        for label, candidate_observation, candidate_coverage, candidate_stage in tests:
            result = attempt_close(candidate_observation, name, width, base_family["M1"],
                                   candidate_stage, candidate_coverage, budget)
            refused = result["outcome"] in ("InvalidEvidence", "InvalidCoverage")
            require(refused, "negative " + label)
            evidence["negative_controls"].append({"name": label, "outcome": result["outcome"]})
        evidence["checks"].append("eleven typed, context, coverage and false-negative mutations are refused")
        evidence["result"] = {
            "verdict": "Passed",
            "unsafe_rule": "Counterexample",
            "guarded_without_coverage": "CertificateObstruction",
            "guarded_with_complete_finite_coverage": "ObjectClosed",
            "residual": "The experiment is finite and receiver-selected. It does not show that unrestricted language domains have finite tell-tales, and timeout remains unresolved."
        }
        evidence["status"] = "Passed"
    except Exception as exc:
        evidence["status"] = "Failed"
        evidence["failures"].append({"type": type(exc).__name__, "message": str(exc)})

    evidence["timings"] = {"inside_seconds": time.monotonic() - started}
    evidence["cost"] = {
        "assertions": assertions,
        "host_work_units": budget.work,
        "search_candidates": 0,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    }
    deterministic = {k: v for k, v in evidence.items() if k not in ("timings", "cost", "deterministic_sha256")}
    evidence["deterministic_sha256"] = digest(deterministic)
    output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    return evidence["status"] == "Passed"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("refusing to overwrite " + str(args.output))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    raise SystemExit(0 if run(args.output) else 1)
