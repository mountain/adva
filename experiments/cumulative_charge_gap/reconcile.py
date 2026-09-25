#!/usr/bin/env python3
"""Read-only receiver for the charge-before-reservation interruption window.

Project-original ChatGPT (OpenAI), Unknown v0.3, submitted through Mingli
Yuan's authorized account proxy. Account use is not review or correctness.
"""
import argparse
import json
from pathlib import Path


class InvalidEvidence(Exception):
    pass


def require(condition, reason):
    if not condition:
        raise InvalidEvidence(reason)


def strict(raw):
    def pairs(items):
        value = {}
        for key, item in items:
            require(key not in value, "DuplicateKey")
            value[key] = item
        return value

    return json.loads(
        raw,
        object_pairs_hook=pairs,
        parse_constant=lambda _: (_ for _ in ()).throw(InvalidEvidence("Number")),
    )


def wire(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode()


def integer(value, lower=0):
    return type(value) is int and lower <= value <= 100000


def fields(value, names):
    require(type(value) is dict and set(value) == set(names), "Fields")


def nodes(value):
    if type(value) is dict:
        return 1 + sum(1 + nodes(item) for key, item in value.items())
    if type(value) is list:
        return 1 + sum(nodes(item) for item in value)
    return 1


def read_canonical(path, limit):
    raw = Path(path).read_bytes()
    require(len(raw) <= limit, "InputSize")
    value = strict(raw)
    require(raw == wire(value), "NoncanonicalInput")
    return value, nodes(value)


def receive(trial_path, journal_path):
    trial, trial_nodes = read_canonical(trial_path, 4096)
    journal, journal_nodes = read_canonical(journal_path, 32768)

    fields(trial, ("profile", "charges"))
    require(trial["profile"] == "cumulative-trial-v0", "TrialProfile")
    require(type(trial["charges"]) is list and len(trial["charges"]) <= 8,
            "TrialCharges")
    require(all(integer(item, 1) for item in trial["charges"]), "TrialCharge")

    fields(journal, ("contract", "events"))
    fields(journal["contract"], ("task", "work_cap", "call_cap", "correction_cap"))
    contract = journal["contract"]
    require(type(contract["task"]) is str and 0 < len(contract["task"]) <= 128,
            "Task")
    require(integer(contract["work_cap"], 1) and integer(contract["call_cap"], 1),
            "Cap")
    require(integer(contract["correction_cap"]) and contract["correction_cap"] <= 1,
            "CorrectionCap")
    require(type(journal["events"]) is list and len(journal["events"]) <= 16,
            "Events")

    reservations = []
    for index, event in enumerate(journal["events"], 1):
        fields(event, ("kind", "id", "units", "purpose"))
        require(event["kind"] == "reserve" and event["id"] == index,
                "ReservationSequence")
        require(integer(event["units"], 1), "ReservationUnits")
        require(type(event["purpose"]) is str and 0 < len(event["purpose"]) <= 128,
                "Purpose")
        reservations.append({"id": event["id"], "units": event["units"],
                             "purpose": event["purpose"]})

    charged = sum(trial["charges"])
    reserved = sum(event["units"] for event in reservations)
    reason = "TrialChargeLacksTaskBinding" if trial["charges"] else "TaskReservationLacksTrialCharge"
    require(trial["charges"] or reservations, "NoAttemptObserved")
    work_units = trial_nodes + journal_nodes + len(trial["charges"]) + len(reservations) + 12
    return {
        "profile": "adva.research.cumulative-charge-gap-receipt.v0",
        "outcome": "UnknownAttemptState",
        "reason": reason,
        "task": contract["task"],
        "trial_charge_count": len(trial["charges"]),
        "trial_charged_units": charged,
        "task_reservation_count": len(reservations),
        "task_reserved_units": reserved,
        "amounts_equal": charged == reserved,
        "binding_fields_present": False,
        "launch_authorized": False,
        "retry_authorized": False,
        "account_mutation_authorized": False,
        "native_authority": False,
        "free_authorized": False,
        "work_units": work_units,
    }


def main(trial, journal):
    try:
        result = receive(trial, journal)
    except (OSError, ValueError, InvalidEvidence) as error:
        result = {
            "profile": "adva.research.cumulative-charge-gap-receipt.v0",
            "outcome": "InvalidEvidence",
            "reason": type(error).__name__ + ": " + str(error),
            "launch_authorized": False,
            "retry_authorized": False,
            "account_mutation_authorized": False,
            "native_authority": False,
            "free_authorized": False,
            "work_units": 0,
        }
    print(wire(result).decode(), end="")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--trial", required=True, type=Path)
    parser.add_argument("--journal", required=True, type=Path)
    args = parser.parse_args()
    raise SystemExit(main(args.trial, args.journal))
