"""Independent string-marking compiler and named-substitution weak-head oracle.

This implements the declared algorithm rather than executing copied PDF
JavaScript. It shares only resource accounting with the explicit machine.
"""
from syntax import Limit


def first_tree_end(text, budget):
    pending = [None]
    for i, c in enumerate(text):
        budget.tick()
        pending.pop()
        if c in "13":
            pending.extend((None, None))
        if not pending:
            return i + 1
    return None


def compile_string(bits, budget):
    def translate(text):
        budget.tick()
        if "1" not in text:
            return ("read",) if text == "0" else ("var", text)
        end = first_tree_end(text[1:], budget)
        left, right = text[1:1 + end], text[1 + end:]
        if left.startswith("10"):
            pattern = left[2:]
            name = pattern.translate(str.maketrans("01", "23"))
            return ("lambda", name, translate(right.replace(pattern, name)))
        return ("apply", translate(left), translate(right))
    return translate(bits)


def debruijn(term, budget, names=()):
    budget.tick()
    if term[0] == "var":
        return ("v", names.index(term[1]))
    if term[0] == "lambda":
        return ("l", debruijn(term[2], budget, (term[1],) + names))
    if term[0] == "apply":
        return ("a", debruijn(term[1], budget, names), debruijn(term[2], budget, names))
    return ("r",)


def names_in(term, budget, free=False):
    budget.tick()
    if term[0] == "var":
        return {term[1]}
    if term[0] == "lambda":
        names = names_in(term[2], budget, free)
        return names - {term[1]} if free else names | {term[1]}
    if term[0] == "apply":
        return names_in(term[1], budget, free) | names_in(term[2], budget, free)
    return set()


def substitute_named(term, variable, value, budget):
    budget.tick()
    if term[0] == "var":
        return value if term[1] == variable else term
    if term[0] == "lambda":
        name, body = term[1:]
        if name == variable:
            return term
        if name in names_in(value, budget, free=True):
            occupied = names_in(body, budget) | names_in(value, budget) | {variable, name}
            fresh = name + "_fresh"
            while fresh in occupied:
                budget.tick()
                fresh += "_"
            body = substitute_named(body, name, ("var", fresh), budget)
            name = fresh
        return ("lambda", name, substitute_named(body, variable, value, budget))
    if term[0] == "apply":
        return ("apply", substitute_named(term[1], variable, value, budget),
                substitute_named(term[2], variable, value, budget))
    return term


def size(term, budget):
    todo, count = [term], 0
    while todo:
        budget.tick()
        item = todo.pop()
        count += 1
        if count > budget.limits["max_term_nodes"]:
            raise Limit("oracle term nodes")
        if item[0] == "lambda":
            todo.append(item[2])
        elif item[0] == "apply":
            todo.extend(item[1:])


def run(code, budget):
    end = first_tree_end(code, budget)
    if end is None:
        return {"status": "NeedSyntax", "cursor": 0, "reads": []}
    term = compile_string(code[:end], budget)
    cursor, reads = end, []
    class NeedInput(Exception):
        pass

    def reduce_head(term):
        nonlocal cursor
        budget.tick()
        if term[0] != "apply":
            raise ValueError("unbound oracle head")
        function, argument = term[1:]
        if function[0] == "lambda":
            return substitute_named(function[2], function[1], argument, budget)
        if function[0] == "read":
            if cursor == len(code):
                raise NeedInput
            bit = code[cursor]
            reads.append([cursor, bit])
            cursor += 1
            if bit == "1":
                return ("lambda", "identity", ("var", "identity"))
            name = "ignored"
            occupied = names_in(argument, budget)
            while name in occupied:
                budget.tick()
                name += "_"
            return ("lambda", name, argument)
        return ("apply", reduce_head(function), argument)

    try:
        for _ in range(budget.limits["oracle_reductions"]):
            budget.tick()
            if term[0] in ("lambda", "read"):
                return {"status": "Halt" if cursor == len(code) else "Overflow", "cursor": cursor,
                        "reads": reads, "whnf": debruijn(term, budget)}
            term = reduce_head(term)
            size(term, budget)
    except NeedInput:
        return {"status": "NeedInput", "cursor": cursor, "reads": reads}
    return {"status": "UnknownFuel", "cursor": cursor, "reads": reads}
