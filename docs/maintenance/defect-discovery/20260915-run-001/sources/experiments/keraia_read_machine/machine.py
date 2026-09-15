"""Explicit weak-head/read machine and checked, input-free segment reuse.

All terms are immutable external de Bruijn syntax. No native Adva identity,
cell, or source/occurrence contraction is constructed here.
"""
import copy
from dataclasses import dataclass, field, asdict, replace
import json

from syntax import PROFILE, COST, R, I, Limit, beta, compile_tree, shift, split_code


@dataclass(frozen=True)
class Frame:
    control: tuple
    stack: tuple
    cursor: int
    profile: str = PROFILE
    cost_convention: str = COST


@dataclass(frozen=True)
class Receipt:
    start: Frame
    end: Frame
    steps: int
    stop: str
    schema: str = "adva.external.keraia-pure-segment.v0"


def pure_segment(frame, allowance, budget, counts, category="execution_steps"):
    if frame.profile != PROFILE or frame.cost_convention != COST:
        raise ValueError("wrong segment profile")
    if type(allowance) is not int or allowance < 0:
        raise ValueError("invalid allowance")
    control, stack = frame.control, list(frame.stack)
    used = 0
    while True:
        budget.tick()
        if control == R and stack:
            return Receipt(frame, replace(frame, control=control, stack=tuple(stack)), used, "ReadReady")
        if used == allowance:
            return Receipt(frame, replace(frame, control=control, stack=tuple(stack)), used, "UnknownFuel")
        counts[category] += 1
        used += 1
        if control[0] == "a":
            stack.append(control[2])
            control = control[1]
            if len(stack) > budget.limits["max_stack"]:
                raise Limit("argument stack")
        elif control[0] == "l" and stack:
            control = beta(control[1], stack.pop(), budget)
        elif control[0] in ("l", "r"):
            return Receipt(frame, replace(frame, control=control, stack=tuple(stack)), used, "Halt")
        else:
            raise ValueError("free variable at machine head")


def check_receipt(receipt, expected, budget, counts):
    """Receiver supplies its own frame. Replay checks integrity, not a new kernel."""
    if type(receipt) is not Receipt or type(expected) is not Frame:
        return False
    if (receipt.schema != "adva.external.keraia-pure-segment.v0"
            or not typed_equal(asdict(receipt.start), asdict(expected), budget)
            or expected.profile != PROFILE or expected.cost_convention != COST
            or type(receipt.steps) is not int or not 0 <= receipt.steps <= budget.limits["max_semantic_steps"]
            or receipt.stop not in ("ReadReady", "Halt")):
        return False
    replay = pure_segment(expected, receipt.steps, budget, counts, "verification_steps")
    return typed_equal(asdict(replay), asdict(receipt), budget)


def typed_equal(left, right, budget):
    """Python's True == 1 and 0.0 == 0 are not evidence-field identities."""
    todo = [(left, right)]
    while todo:
        budget.tick()
        a, b = todo.pop()
        if type(a) is not type(b):
            return False
        if isinstance(a, dict):
            if a.keys() != b.keys():
                return False
            todo.extend((a[k], b[k]) for k in a)
        elif isinstance(a, (tuple, list)):
            if len(a) != len(b):
                return False
            todo.extend(zip(a, b))
        elif a != b:
            return False
    return True


class Engine:
    def __init__(self, budget, reuse=False):
        self.budget = budget
        self.reuse = reuse
        self.cache = {}
        self.counts = {"execution_steps": 0, "verification_steps": 0, "read_steps": 0,
                       "cache_hits": 0, "cache_misses": 0}

    def segment(self, frame, allowance):
        if self.reuse and frame in self.cache:
            receipt = self.cache[frame]
            if receipt.steps <= allowance:
                self.counts["cache_hits"] += 1
                return receipt
        self.counts["cache_misses"] += 1
        result = pure_segment(frame, allowance, self.budget, self.counts)
        if self.reuse and result.stop != "UnknownFuel":
            if not check_receipt(result, frame, self.budget, self.counts):
                raise AssertionError("generated segment failed its receiver")
            if frame not in self.cache and len(self.cache) >= self.budget.limits["max_cache_entries"]:
                raise Limit("segment cache")
            self.cache[frame] = result
        return result


@dataclass
class State:
    source: str
    initial_fuel: int
    program_end: int | None
    control: tuple | None
    stack: list = field(default_factory=list)
    cursor: int = 0
    steps: int = 0
    fuel_left: int = 0
    reads: list = field(default_factory=list)
    status: str = "Running"

    @classmethod
    def start(cls, source, fuel, budget):
        if type(fuel) is not int or not 0 <= fuel <= budget.limits["max_semantic_steps"]:
            raise ValueError("invalid initial fuel")
        end = split_code(source, budget)
        return cls(source, fuel, end, compile_tree(source[:end], budget) if end is not None else None,
                   cursor=end or 0, fuel_left=fuel, status="Running" if end is not None else "NeedSyntax")

    def frame(self):
        return Frame(self.control, tuple(self.stack), self.cursor)

    def record(self):
        return {"schema": "adva.external.keraia-frontier.v0", "profile": PROFILE,
                "cost_convention": COST, **asdict(self)}

    def append_bit(self, bit, budget):
        if self.status != "NeedInput" or bit not in ("0", "1"):
            raise ValueError("only a requested input bit can be appended")
        if len(self.source) >= budget.limits["max_code_bits"]:
            raise Limit("source length")
        self.source += bit
        self.status = "Running"
        # The existing steps, reads and fuel_left deliberately remain unchanged.


def advance(state, engine):
    budget = engine.budget
    while state.status == "Running":
        receipt = engine.segment(state.frame(), state.fuel_left)
        state.control, state.stack = receipt.end.control, list(receipt.end.stack)
        state.steps += receipt.steps
        state.fuel_left -= receipt.steps
        if receipt.stop == "UnknownFuel":
            state.status = "UnknownFuel"
        elif receipt.stop == "Halt":
            state.status = "Halt" if state.cursor == len(state.source) else "Overflow"
        elif state.fuel_left == 0:
            state.status = "UnknownFuel"
        elif state.cursor == len(state.source):
            state.status = "NeedInput"
        else:
            budget.tick()
            argument = state.stack.pop()
            bit = state.source[state.cursor]
            state.steps += 1
            state.fuel_left -= 1
            state.reads.append([state.steps, state.cursor, bit])
            state.cursor += 1
            engine.counts["read_steps"] += 1
            state.control = ("l", shift(argument, 1, budget)) if bit == "0" else I
    return state


def row(state):
    result = {"code": state.source, "status": state.status, "cursor": state.cursor,
              "steps": state.steps, "fuel_left": state.fuel_left,
              "reads": copy.deepcopy(state.reads), "code_weight_exponent": len(state.source)}
    if state.status in ("Halt", "Overflow"):
        result["whnf"] = state.control
    return result


def restore_checkpoint(raw, expected_source, expected_fuel, engine):
    """Validate one event-frontier checkpoint by replay from receiver-selected inputs."""
    if type(raw) is not str or len(raw.encode()) > 262144:
        raise ValueError("checkpoint size")
    def unique_pairs(pairs):
        result = {}
        for k, v in pairs:
            if k in result:
                raise ValueError("duplicate checkpoint key")
            result[k] = v
        return result
    record = json.loads(raw, object_pairs_hook=unique_pairs)
    actual = advance(State.start(expected_source, expected_fuel, engine.budget), engine)
    if json.dumps(record, sort_keys=True, separators=(",", ":")) != json.dumps(actual.record(), sort_keys=True, separators=(",", ":")):
        raise ValueError("checkpoint does not match receiver-selected replay")
    return actual


def prefix_search(max_length, fuel, engine):
    """Branch only at incomplete syntax or a demanded input; never refund time."""
    todo = [("", None)]
    accepted, frontiers = [], []
    visited = 0
    while todo:
        engine.budget.tick()
        source, state = todo.pop()
        visited += 1
        if state is None:
            state = State.start(source, fuel, engine.budget)
        advance(state, engine)
        if state.status == "Halt":
            accepted.append(row(state))
        elif state.status == "UnknownFuel" or len(source) == max_length:
            frontiers.append(state.record())
        elif state.status in ("NeedInput", "NeedSyntax"):
            for bit in ("1", "0"):
                child = None
                if state.status == "NeedInput":
                    child = copy.deepcopy(state)
                    child.append_bit(bit, engine.budget)
                todo.append((source + bit, child))
        else:
            raise AssertionError("unexpected prefix-frontier outcome: " + state.status)
    return {"accepted": accepted, "frontiers": frontiers, "visited": visited}

