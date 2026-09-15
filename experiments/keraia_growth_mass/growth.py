"""A finite stack-pumping witness, checked by the independent named-term kernel.

Stacks are bottom-first. The protected bottom must never be popped, even if
a later step would reconstruct identical bytes there. Positive stack growth
and a repeated control alone are insufficient.
"""
from dataclasses import asdict
import json

from common import C, M, O, canonical

SCHEMA = "adva.external.keraia-protected-stack-pump.v0"


def propose(source, fuel, budget):
    state = M.State.start(source, fuel, budget)
    frames, actions = [], []
    counts = {"execution_steps": 0, "read_steps": 0}
    while state.status == "Running":
        budget.tick()
        frame = state.frame()
        frames.append(frame)
        end = len(frames) - 1
        for entry, earlier in enumerate(frames[:-1]):
            budget.tick()
            base = earlier.stack
            if (frame.control != earlier.control or frame.cursor != earlier.cursor
                    or len(frame.stack) <= len(base) or frame.stack[:len(base)] != base
                    or frame.cursor != len(source)):
                continue
            safe = all(action == "Pure" for action in actions[entry:])
            for before, after in zip(frames[entry:end], frames[entry + 1:]):
                budget.tick()
                safe = safe and before.stack[:len(base)] == base and after.stack[:len(base)] == base
                if before.control[0] == "l" and len(before.stack) <= len(base):
                    safe = False
            if safe:
                receipt = {"schema": SCHEMA, "source": source, "search_fuel": fuel,
                           "profile": M.PROFILE, "cost_convention": M.COST,
                           "pump_entry": entry, "frames": [asdict(f) for f in frames],
                           "actions": actions}
                return {"status": "GrowthCandidate",
                        "certificate": json.loads(canonical(receipt)), "counts": counts}
        action = C.microstep(state, budget, counts)
        if action:
            actions.append(action)
    return {"status": state.status, "row": M.row(state), "counts": counts}


def check(receipt, expected_source, expected_fuel, budget):
    """Reconstruct every edge, then check stack-independence without the proposer."""
    try:
        budget.tick()
        if (type(expected_source) is not str
                or len(expected_source) > budget.limits["max_code_bits"]
                or any(c not in "01" for c in expected_source)
                or type(expected_fuel) is not int
                or not 0 <= expected_fuel <= budget.limits["max_semantic_steps"]):
            return False
        keys = {"schema", "source", "search_fuel", "profile", "cost_convention",
                "pump_entry", "frames", "actions"}
        if type(receipt) is not dict or set(receipt) != keys:
            return False
        if (receipt["schema"] != SCHEMA or receipt["source"] != expected_source
                or type(receipt["search_fuel"]) is not int
                or receipt["search_fuel"] != expected_fuel
                or receipt["profile"] != M.PROFILE or receipt["cost_convention"] != M.COST):
            return False
        frames, actions, entry = receipt["frames"], receipt["actions"], receipt["pump_entry"]
        if (type(frames) is not list or type(actions) is not list or type(entry) is not int
                or not 1 <= len(actions) <= expected_fuel
                or len(frames) != len(actions) + 1 or not 0 <= entry < len(actions)):
            return False
        tree_end = O.first_tree_end(expected_source, budget)
        if tree_end is None:
            return False
        control = O.debruijn(O.compile_string(expected_source[:tree_end], budget), budget)
        actual = M.Frame(control, (), tree_end)
        decoded = [C.decode_frame(f, expected_source, budget) for f in frames]
        if decoded[0] != actual:
            return False
        for i, action in enumerate(actions):
            budget.tick()
            actual, actual_action = C.receiver_step(actual, expected_source, budget)
            if type(action) is not str or action != actual_action or actual != decoded[i + 1]:
                return False
        first, last = decoded[entry], decoded[-1]
        bottom = first.stack
        if (first.control != last.control or first.cursor != last.cursor
                or last.cursor != len(expected_source) or len(last.stack) <= len(bottom)):
            return False
        for i in range(entry, len(actions)):
            budget.tick()
            before, after = decoded[i], decoded[i + 1]
            if actions[i] != "Pure":
                return False
            if before.stack[:len(bottom)] != bottom or after.stack[:len(bottom)] != bottom:
                return False
            # Push is harmless. A beta edge may consume only a newly pushed item.
            if before.control[0] == "l" and len(before.stack) <= len(bottom):
                return False
        return last.stack[:len(bottom)] == bottom
    except (ValueError, TypeError, KeyError, IndexError):
        return False
