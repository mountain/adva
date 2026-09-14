"""Exact finite lasso candidates with a separately implemented receiving kernel.

Candidates step the old de Bruijn machine. The receiver compiles with string
marking and checks beta contraction using named capture-avoiding substitution.
Only input-free recurrence of the complete frame supports a suffix cylinder.
"""
from dataclasses import asdict
import json

from support import canonical
import machine as M
import oracle as O
from syntax import I, R, shift

SCHEMA = "adva.external.keraia-input-free-cycle.v0"


def microstep(state, budget, counts):
    """One original semantic step, keeping return and pending input explicit."""
    if not state.fuel_left:
        state.status = "UnknownFuel"
        return None
    if state.control == R and state.stack:
        if state.cursor == len(state.source):
            state.status = "NeedInput"
            return None
        bit = state.source[state.cursor]
        argument = state.stack.pop()
        state.control = ("l", shift(argument, 1, budget)) if bit == "0" else I
        state.cursor += 1
        state.steps += 1
        state.fuel_left -= 1
        state.reads.append([state.steps, state.cursor - 1, bit])
        counts["read_steps"] += 1
        return "Read"
    receipt = M.pure_segment(state.frame(), 1, budget, counts)
    if receipt.steps != 1:
        raise AssertionError("unexpected zero-step pure transition")
    state.control, state.stack = receipt.end.control, list(receipt.end.stack)
    state.steps += 1
    state.fuel_left -= 1
    if receipt.stop == "Halt":
        state.status = "Halt" if state.cursor == len(state.source) else "Overflow"
    return "Pure"


def propose(source, fuel, budget):
    state = M.State.start(source, fuel, budget)
    counts = {"execution_steps": 0, "read_steps": 0}
    seen, heads, frames, actions = {}, {}, [], []
    head_only_repeat = None
    while state.status == "Running":
        budget.tick()
        frame = state.frame()
        frames.append(asdict(frame))
        if frame in seen:
            receipt = {"schema": SCHEMA, "source": source, "search_fuel": fuel,
                       "profile": M.PROFILE, "cost_convention": M.COST,
                       "cycle_entry": seen[frame], "frames": frames, "actions": actions}
            return {"status": "CycleCandidate", "certificate": json.loads(canonical(receipt)),
                    "counts": counts, "row": M.row(state)}
        if frame.control in heads and head_only_repeat is None:
            previous = heads[frame.control]
            head_only_repeat = {"earlier": asdict(previous), "later": asdict(frame)}
        heads[frame.control] = frame
        seen[frame] = len(frames) - 1
        action = microstep(state, budget, counts)
        if action:
            actions.append(action)
    return {"status": state.status, "row": M.row(state), "residual": state.record(),
            "head_only_repeat": head_only_repeat, "counts": counts}


def decode_term(data, budget, depth=0, remaining=None):
    budget.tick()
    if remaining is None:
        remaining = [budget.limits["max_term_nodes"]]
    remaining[0] -= 1
    if remaining[0] < 0:
        raise ValueError("term node limit")
    if type(data) is not list or not data or depth > 256:
        raise ValueError("term shape")
    if data == ["r"]:
        return R
    if data[0] == "v" and len(data) == 2 and type(data[1]) is int and 0 <= data[1] < depth:
        return ("v", data[1])
    if data[0] == "l" and len(data) == 2:
        return ("l", decode_term(data[1], budget, depth + 1, remaining))
    if data[0] == "a" and len(data) == 3:
        return ("a", decode_term(data[1], budget, depth, remaining), decode_term(data[2], budget, depth, remaining))
    raise ValueError("invalid or open term")


def decode_frame(data, source, budget):
    if type(data) is not dict or set(data) != {"control", "stack", "cursor", "profile", "cost_convention"}:
        raise ValueError("frame fields")
    if (type(data["cursor"]) is not int or not 0 <= data["cursor"] <= len(source)
            or data["profile"] != M.PROFILE or data["cost_convention"] != M.COST
            or type(data["stack"]) is not list or len(data["stack"]) > budget.limits["max_stack"]):
        raise ValueError("frame boundary")
    return M.Frame(decode_term(data["control"], budget),
                   tuple(decode_term(t, budget) for t in data["stack"]), data["cursor"])


def named(term, budget, env=()):
    budget.tick()
    if term[0] == "v":
        return ("var", env[term[1]])
    if term[0] == "l":
        variable = "bound_" + str(len(env))
        return ("lambda", variable, named(term[1], budget, (variable,) + env))
    if term[0] == "a":
        return ("apply", named(term[1], budget, env), named(term[2], budget, env))
    return ("read",)


def receiver_step(frame, source, budget):
    """Independent stack transition: no primary beta, shift or step function."""
    control, stack, cursor = frame.control, list(frame.stack), frame.cursor
    if control[0] == "a":
        return M.Frame(control[1], tuple(stack + [control[2]]), cursor), "Pure"
    if control[0] == "l" and stack:
        function = named(control, budget)
        reduced = O.substitute_named(function[2], function[1], named(stack.pop(), budget), budget)
        O.size(reduced, budget)
        return M.Frame(O.debruijn(reduced, budget), tuple(stack), cursor), "Pure"
    if control == R and stack and cursor < len(source):
        argument = named(stack.pop(), budget)
        # The frame is closed, so a fresh unused binder cannot capture anything.
        value = (("lambda", "read_result", argument) if source[cursor] == "0"
                 else ("lambda", "read_identity", ("var", "read_identity")))
        return M.Frame(O.debruijn(value, budget), tuple(stack), cursor + 1), "Read"
    raise ValueError("return or pending input is not a cycle edge")


def check(receipt, expected_source, expected_fuel, budget):
    """Receives JSON-shaped evidence; rejects malformed/type-coerced claims."""
    try:
        budget.tick()
        if (type(expected_source) is not str or len(expected_source) > budget.limits["max_code_bits"]
                or any(c not in "01" for c in expected_source)
                or type(expected_fuel) is not int or not 0 <= expected_fuel <= budget.limits["max_semantic_steps"]):
            return False
        if type(receipt) is not dict or set(receipt) != {"schema", "source", "search_fuel", "profile", "cost_convention", "cycle_entry", "frames", "actions"}:
            return False
        if (receipt["schema"] != SCHEMA or receipt["source"] != expected_source
                or type(receipt["search_fuel"]) is not int or receipt["search_fuel"] != expected_fuel
                or receipt["profile"] != M.PROFILE or receipt["cost_convention"] != M.COST):
            return False
        frames, actions, entry = receipt["frames"], receipt["actions"], receipt["cycle_entry"]
        if (type(frames) is not list or type(actions) is not list or type(entry) is not int
                or not 1 <= len(actions) <= expected_fuel or len(frames) != len(actions) + 1
                or not 0 <= entry < len(actions)):
            return False
        end = O.first_tree_end(expected_source, budget)
        if end is None:
            return False
        initial = O.debruijn(O.compile_string(expected_source[:end], budget), budget)
        actual = M.Frame(initial, (), end)
        decoded = [decode_frame(f, expected_source, budget) for f in frames]
        if decoded[0] != actual:
            return False
        for index, action in enumerate(actions):
            budget.tick()
            actual, actual_action = receiver_step(actual, expected_source, budget)
            if type(action) is not str or action != actual_action or decoded[index + 1] != actual:
                return False
        return (decoded[-1] == decoded[entry] and decoded[-1].cursor == len(expected_source)
                and all(action == "Pure" for action in actions[entry:]))
    except (ValueError, TypeError, KeyError, IndexError):
        return False
