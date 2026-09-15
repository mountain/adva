"""External prefix-Keraia tree compiler; identifiers are research-local syntax."""
import time

PROFILE = "keraia.appendix-b.cbn-whnf.read.v0"
COST = "spine-beta-read-return.v0"
R = ("r",)
I = ("l", ("v", 0))


class Limit(Exception):
    pass


class Budget:
    def __init__(self, limits):
        self.limits = limits
        self.work = 0
        self.start = time.monotonic()

    def tick(self):
        self.work += 1
        if self.work > self.limits["max_host_work"] or time.monotonic() - self.start > self.limits["wall_seconds"]:
            raise Limit("host work or elapsed time")


def split_code(code, budget):
    if type(code) is not str or len(code) > budget.limits["max_code_bits"] or any(c not in "01" for c in code):
        raise ValueError("invalid code")
    slots = 1
    for i, c in enumerate(code):
        budget.tick()
        slots += 1 if c == "1" else -1
        if slots == 0:
            return i + 1
    return None


def tree_from_bits(bits, budget):
    position = 0
    def tree():
        nonlocal position
        budget.tick()
        c = bits[position]
        position += 1
        return (0,) if c == "0" else (1, tree(), tree())
    result = tree()
    if position != len(bits):
        raise ValueError("not exactly one tree")
    return result


def tree_word(tree, budget):
    budget.tick()
    return str(tree[0]) if len(tree) == 1 else str(tree[0]) + tree_word(tree[1], budget) + tree_word(tree[2], budget)


def marked(tree, budget):
    budget.tick()
    return (2,) if len(tree) == 1 else (3, marked(tree[1], budget), marked(tree[2], budget))


def replace_tree(tree, pattern, replacement, budget):
    budget.tick()
    if tree == pattern:
        return replacement
    if len(tree) == 1:
        return tree
    return (tree[0], replace_tree(tree[1], pattern, replacement, budget),
            replace_tree(tree[2], pattern, replacement, budget))


def compile_tree(bits, budget):
    def lower(tree, names):
        budget.tick()
        if tree[0] in (2, 3):
            # Marked subtrees are one variable symbol, not applications.
            name = tree_word(tree, budget)
            if name not in names:
                raise ValueError("free marked variable")
            return ("v", names.index(name))
        if tree == (0,):
            return R
        left, body = tree[1:]
        if left[0] == 1 and left[1] == (0,):
            pattern = left[2]
            replacement = marked(pattern, budget)
            name = tree_word(replacement, budget)
            return ("l", lower(replace_tree(body, pattern, replacement, budget), [name] + names))
        return ("a", lower(left, names), lower(body, names))
    term = lower(tree_from_bits(bits, budget), [])
    term_size(term, budget)
    return term


def term_size(term, budget):
    count = 0
    todo = [term]
    while todo:
        budget.tick()
        t = todo.pop()
        count += 1
        if count > budget.limits["max_term_nodes"]:
            raise Limit("term nodes")
        if t[0] == "l":
            todo.append(t[1])
        elif t[0] == "a":
            todo.extend(t[1:])
    return count


def shift(term, delta, budget, cutoff=0):
    budget.tick()
    tag = term[0]
    if tag == "v":
        return ("v", term[1] + delta if term[1] >= cutoff else term[1])
    if tag == "l":
        return ("l", shift(term[1], delta, budget, cutoff + 1))
    if tag == "a":
        return ("a", shift(term[1], delta, budget, cutoff), shift(term[2], delta, budget, cutoff))
    return term


def substitute(term, index, replacement, budget):
    budget.tick()
    tag = term[0]
    if tag == "v":
        return replacement if term[1] == index else term
    if tag == "l":
        return ("l", substitute(term[1], index + 1, shift(replacement, 1, budget), budget))
    if tag == "a":
        return ("a", substitute(term[1], index, replacement, budget), substitute(term[2], index, replacement, budget))
    return term


def beta(body, argument, budget):
    result = shift(substitute(body, 0, shift(argument, 1, budget), budget), -1, budget)
    term_size(result, budget)
    return result

