"""Independent instruction reception; no Rust FFI or primary step function.

Generic v1 instruction oracle; source control is interpreted separately below.
BLAKE3 is an integrity primitive, not semantic or source identity.
"""
from copy import deepcopy
import json

import blake3


class Refusal(Exception):
    pass


class Budget:
    def __init__(self, maximum=2000000):
        self.steps = 0
        self.maximum = maximum

    def tick(self):
        self.steps += 1
        if self.steps > self.maximum:
            raise RuntimeError("independent receiving budget exhausted")


def encoded(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()


def integer(value):
    if type(value) is not int or not -(2**63) <= value < 2**63:
        raise Refusal("integer overflow")
    return {"kind": "integer", "value": value}


def node(tag, *fields):
    return {"kind": "node", "tag": tag, "fields": list(fields)}


def literal(value):
    return node(0, integer(value))


def size(data, depth=1):
    if depth > 48:
        raise Refusal("data capacity exceeded")
    if data["kind"] == "integer":
        integer(data["value"])
        return 1
    if data["kind"] != "node" or type(data["tag"]) is not int or not 0 <= data["tag"] <= 255:
        raise Refusal("invalid data")
    if len(data["fields"]) > 2048:
        raise Refusal("node arity exceeds 2048")
    n = 1 + sum(size(child, depth + 1) for child in data["fields"])
    if n > 16384:
        raise Refusal("data capacity exceeded")
    return n


def check_capacity(state):
    count = 0
    for value in state["registers"]:
        if value is None:
            continue
        if value["kind"] == "stack":
            if len(value["items"]) > 4096:
                raise Refusal("stack capacity exceeded")
            count += sum(size(item) for item in value["items"])
        elif value["kind"] == "data":
            count += size(value["value"])
        else:
            count += 1
    if state["phase"]["kind"] == "returned":
        count += size(state["phase"]["value"])
    if count > 131072:
        raise Refusal("state capacity exceeded")


def initial(program):
    return {"pc": 0, "registers": [None] * len(program["registers"]),
            "spent": 0, "phase": {"kind": "running"}}


def transition(program, data, before, budget):
    budget.tick()
    assert before["phase"] == {"kind": "running"}
    instruction = program["code"][before["pc"]]
    state = deepcopy(before)
    state["pc"] += 1
    registers = state["registers"]

    def get(r, kind=None):
        value = registers[r]
        if value is None:
            raise Refusal("uninitialized register")
        if kind is not None and value["kind"] != kind:
            raise Refusal("expected " + kind + " register")
        if kind == "stack":
            return value["items"]
        return value["value"] if kind is not None else value

    def put(r, value):
        assert value["kind"] == program["registers"][r]["kind"]
        registers[r] = deepcopy(value)

    def put_data(r, value):
        put(r, {"kind": "data", "value": value})

    op = instruction["op"]
    try:
        if op == "length":
            value = get(instruction["src"], "data")
            if value["kind"] != "node":
                raise Refusal("expected node data")
            put(instruction["dst"], integer(len(value["fields"])))
        elif op == "field_dynamic":
            index = get(instruction["index"], "integer")
            if index < 0:
                raise Refusal("negative field index")
            value = get(instruction["src"], "data")
            if value["kind"] != "node":
                raise Refusal("expected node data")
            if index >= len(value["fields"]):
                raise Refusal("field index outside node")
            put_data(instruction["dst"], value["fields"][index])
        elif op == "pack":
            value = node(instruction["tag"], *get(instruction["stack"], "stack"))
            size(value)
            put_data(instruction["dst"], value)
        elif op == "stack_length":
            put(instruction["dst"], integer(len(get(instruction["stack"], "stack"))))
        elif op == "input":
            put_data(instruction["dst"], data)
        elif op == "constant":
            put(instruction["dst"], integer(instruction["value"]))
        elif op == "copy":
            put(instruction["dst"], get(instruction["src"]))
        elif op == "clear":
            put(instruction["stack"], {"kind": "stack", "items": []})
        elif op == "push":
            items = list(get(instruction["stack"], "stack"))
            if len(items) >= 4096:
                raise Refusal("stack capacity exceeded")
            items.append(get(instruction["src"], "data"))
            put(instruction["stack"], {"kind": "stack", "items": items})
        elif op == "pop":
            items = list(get(instruction["stack"], "stack"))
            if not items:
                raise Refusal("empty stack")
            value = items.pop()
            put(instruction["stack"], {"kind": "stack", "items": items})
            put_data(instruction["dst"], value)
        elif op == "is_empty":
            put(instruction["dst"], {"kind": "boolean", "value": not get(instruction["stack"], "stack")})
        elif op == "tag":
            value = get(instruction["src"], "data")
            tag = -1 if value["kind"] == "integer" else value["tag"]
            put(instruction["dst"], integer(tag))
        elif op == "field":
            value = get(instruction["src"], "data")
            if value["kind"] != "node" or len(value["fields"]) != instruction["arity"]:
                raise Refusal("data shape mismatch")
            put_data(instruction["dst"], value["fields"][instruction["index"]])
        elif op == "as_integer":
            value = get(instruction["src"], "data")
            if value["kind"] != "integer":
                raise Refusal("expected integer data")
            put(instruction["dst"], integer(value["value"]))
        elif op == "box_integer":
            put_data(instruction["dst"], integer(get(instruction["src"], "integer")))
        elif op == "node":
            value = node(instruction["tag"], *(get(r, "data") for r in instruction["fields"]))
            size(value)
            put_data(instruction["dst"], value)
        elif op in ("add", "multiply", "equal"):
            a = get(instruction["left"], "integer")
            b = get(instruction["right"], "integer")
            if op == "equal":
                put(instruction["dst"], {"kind": "boolean", "value": a == b})
            else:
                put(instruction["dst"], integer(a + b if op == "add" else a * b))
        elif op == "jump":
            state["pc"] = instruction["target"]
        elif op == "branch":
            state["pc"] = instruction["yes"] if get(instruction["condition"], "boolean") else instruction["no"]
        elif op == "return":
            state["phase"] = {"kind": "returned", "value": deepcopy(get(instruction["src"], "data"))}
        elif op == "reject":
            raise Refusal(instruction["reason"])
        else:
            raise AssertionError("unknown instruction")
        check_capacity(state)
    except Refusal as exc:
        state = deepcopy(before)
        state["phase"] = {"kind": "rejected", "reason": str(exc)}
    state["spent"] += 1
    return state


def status(state, fuel):
    phase = state["phase"]["kind"]
    if phase == "returned":
        return "Returned"
    if phase == "rejected":
        return "Rejected"
    return "FuelExhausted" if state["spent"] == fuel else "Suspended"


def receive(report, program, data, fuel, profile, budget):
    assert report["schema"] == "adva.data-machine.run.research.v1"
    assert report["profile"] == profile
    assert encoded(report["program"]) == encoded(program)
    assert encoded(report["input"]) == encoded(data)
    assert type(report["fuel"]) is int and report["fuel"] == fuel
    assert 0 <= fuel <= 200000 and len(report["trace"]) <= fuel
    size(data)
    state = initial(program)
    for edge in report["trace"]:
        pc = state["pc"]
        state = transition(program, data, state, budget)
        expected = {"pc": pc, "next_pc": state["pc"], "state_digest": blake3.blake3(encoded(state)).hexdigest()}
        assert encoded(edge) == encoded(expected), (pc, edge, expected)
    assert encoded(state) == encoded(report["state"])
    assert report["status"] == status(state, fuel)
    assert 1 <= len(report["segments"]) <= 16
    end = 0
    for i, segment in enumerate(report["segments"]):
        assert all(type(segment[k]) is int for k in ("start", "end", "replayed"))
        assert segment["start"] == end <= segment["end"] <= state["spent"]
        assert segment["replayed"] == (end if i else 0)
        end = segment["end"]
    assert end == state["spent"]
    return state



def source_execute(source, data, budget):
    """Direct AST control, no lowering, addresses, seed or target execution.

    Generic primitive semantics are shared with the independently written v1
    receiver, not Rust. Source branch observations and primitive failures are
    explicit; only well-initialized boolean controls are in this finite family.
    """
    state = initial(source)
    events = []
    def visit(body, path):
        nonlocal state
        if state["phase"]["kind"] != "running":
            return
        budget.tick()  # Includes structural control and recursive checking.
        kind = body["kind"]
        if kind == "prim":
            state["pc"] = 0
            p = {"registers": source["registers"], "code": [body["instruction"]]}
            state = transition(p, data, state, budget)
            events.append({"path": path, "registers": deepcopy(state["registers"]),
                           "phase": deepcopy(state["phase"])})
        elif kind == "seq":
            for i, child in enumerate(body["items"]):
                visit(child, path + ["items", i])
        else:
            def condition():
                budget.tick()
                value = state["registers"][body["condition"]]
                if value is None:
                    state["phase"] = {"kind": "rejected", "reason": "uninitialized register"}
                    return False
                assert value["kind"] == "boolean"
                return value["value"]
            if kind == "if":
                yes = condition()
                visit(body["yes" if yes else "no"], path + ["yes" if yes else "no"])
            elif kind == "while":
                while state["phase"]["kind"] == "running" and condition():
                    visit(body["body"], path + ["body"])
            else:
                raise AssertionError("source constructor")
    visit(source["body"], [])
    return state["phase"], events
