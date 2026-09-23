"""Single-writer, conservative reservation prototype; not a native Adva ledger.

Original Codex (OpenAI), Unknown v0.3, through Mingli Yuan's account proxy.
No refund, concurrency, authentication or power-loss guarantee.
"""
import json
import os
from pathlib import Path
import subprocess
import time


class BoundaryError(Exception):
    pass


def require(condition, reason):
    if not condition:
        raise BoundaryError(reason)


def integer(n, lower=0):
    return type(n) is int and lower <= n <= 100000


def wire(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode()


def strict(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "DuplicateKey")
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(BoundaryError("Number")))


def fields(value, keys):
    require(type(value) is dict and set(value) == set(keys), "Fields")


class Supervisor:
    def __init__(self, path, contract, initialize=False):
        self.path = Path(path)
        fields(contract, ("task", "work_cap", "call_cap", "correction_cap"))
        require(type(contract["task"]) is str and 0 < len(contract["task"]) <= 128, "Task")
        require(all(integer(contract[k], 1) for k in ("work_cap", "call_cap")), "Cap")
        require(integer(contract["correction_cap"]) and contract["correction_cap"] <= 1, "CorrectionCap")
        self.contract = contract.copy()
        self.serialization_seconds = 0.0
        if initialize:
            # Existing journals cannot silently become a new budget.
            with self.path.open("xb") as stream:
                stream.write(wire({"contract": self.contract, "events": []}))
        self.state()

    def read(self):
        require(self.path.stat().st_size <= 32768, "JournalSize")
        raw = self.path.read_bytes()
        data = strict(raw)
        require(raw == wire(data), "NoncanonicalJournal")
        fields(data, ("contract", "events"))
        require(wire(data["contract"]) == wire(self.contract), "ContextChanged")
        require(type(data["events"]) is list and len(data["events"]) <= 32, "EventCount")
        return data

    def fold(self, data):
        reserved = calls = corrections = observed = 0
        pending = None
        stopped = None
        for event in data["events"]:
            require(type(event) is dict, "Event")
            kind = event.get("kind")
            if kind == "reserve":
                fields(event, ("kind", "id", "units", "purpose"))
                require(pending is None and stopped is None, "AttemptBlocked")
                require(integer(event["id"], 1) and event["id"] == calls + 1, "Sequence")
                require(integer(event["units"], 1), "ReservationType")
                require(type(event["purpose"]) is str and 0 < len(event["purpose"]) <= 128, "Purpose")
                reserved += event["units"]
                calls += 1
                require(reserved <= self.contract["work_cap"], "WorkExhausted")
                require(calls <= self.contract["call_cap"], "CallsExhausted")
                pending = event
            elif kind == "settle":
                fields(event, ("kind", "id", "outcome", "reported_work"))
                require(pending is not None and type(event["id"]) is int and event["id"] == pending["id"], "Settlement")
                outcome, used = event["outcome"], event["reported_work"]
                require(outcome in ("Observed", "ImplementationFailure", "BudgetViolation"), "Outcome")
                if outcome == "Observed":
                    require(integer(used) and used <= pending["units"], "ReportedWork")
                    observed += used
                elif outcome == "BudgetViolation":
                    require(integer(used) and used > pending["units"], "ViolationWork")
                    stopped = "BudgetViolation"
                else:
                    require(used is None, "UnknownWork")
                    stopped = "CorrectionRequired"
                pending = None
            elif kind == "correct":
                fields(event, ("kind", "reason"))
                require(pending is None and stopped == "CorrectionRequired", "CorrectionBlocked")
                require(type(event["reason"]) is str and 0 < len(event["reason"]) <= 256, "CorrectionReason")
                corrections += 1
                require(corrections <= self.contract["correction_cap"], "CorrectionExhausted")
                stopped = None
            else:
                raise BoundaryError("EventKind")
        return {"reserved": reserved, "calls": calls, "corrections": corrections,
                "reported_work": observed, "pending": pending,
                "stop": "UnknownAttemptState" if pending else stopped,
                "remaining_work": self.contract["work_cap"] - reserved,
                "remaining_calls": self.contract["call_cap"] - calls}

    def state(self):
        return self.fold(self.read())

    def append(self, event):
        data = self.read()
        data["events"].append(event)
        require(len(data["events"]) <= 32, "EventCount")
        state = self.fold(data)  # refusal occurs before modifying any bytes
        raw = wire(data)
        require(len(raw) <= 32768, "JournalSize")
        started = time.perf_counter()
        temp = self.path.with_suffix(".next")
        with temp.open("xb") as stream:
            stream.write(raw)
        os.replace(temp, self.path)
        self.serialization_seconds += time.perf_counter() - started
        return state

    def reserve(self, units, purpose):
        state = self.state()
        return self.append({"kind": "reserve", "id": state["calls"] + 1,
                            "units": units, "purpose": purpose})

    def correct(self, reason):
        return self.append({"kind": "correct", "reason": reason})

    def run(self, command, units, purpose, trial, timeout=0.5):
        # A trusted trial-level account persists independently of task journals.
        # Charge before reservation/spawn; even a failed task reservation cannot
        # replenish this more conservative experimental allowance.
        trial.charge(units)
        state = self.reserve(units, purpose)
        started = time.perf_counter()
        raw, error, used = b"", None, None
        outcome = "ImplementationFailure"
        try:
            process = subprocess.run(command, capture_output=True, timeout=timeout)
            raw = process.stdout
            require(process.returncode == 0, "ChildExit")
            require(len(raw) <= 4096 and len(process.stderr) <= 4096, "FixtureOutput")
            report = strict(raw)
            fields(report, ("work_units", "value"))
            require(integer(report["work_units"]), "ReceiptWorkType")
            used = report["work_units"]
            outcome = "Observed" if used <= units else "BudgetViolation"
        except (OSError, subprocess.TimeoutExpired, ValueError, BoundaryError) as exc:
            error = type(exc).__name__ + ": " + str(exc)
            used = None
        final = self.append({"kind": "settle", "id": state["calls"],
                             "outcome": outcome, "reported_work": used})
        return {"outcome": outcome, "error": error, "stdout": raw.decode(errors="replace"),
                "wall_seconds": time.perf_counter() - started, "state": final}


if __name__ == "__main__":
    import sys
    path = Path(sys.argv[1])
    expected = strict(Path(sys.argv[2]).read_bytes())
    print(wire(Supervisor(path, expected).state()).decode(), end="")
