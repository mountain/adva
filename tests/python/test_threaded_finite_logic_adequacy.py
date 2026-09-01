from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
from typing import Mapping, TypeAlias


Value: TypeAlias = int | str
Environment: TypeAlias = Mapping["Variable", Value]


class Term:
    pass


@dataclass(frozen=True)
class Variable(Term):
    name: str
    sort: str


@dataclass(frozen=True)
class Constant(Term):
    name: str
    sort: str


class Formula:
    pass


@dataclass(frozen=True)
class Top(Formula):
    pass


@dataclass(frozen=True)
class Bottom(Formula):
    pass


@dataclass(frozen=True)
class Atom(Formula):
    predicate: str
    arguments: tuple[Term, ...] = ()


@dataclass(frozen=True)
class Equality(Formula):
    left: Term
    right: Term


@dataclass(frozen=True)
class Not(Formula):
    body: Formula


@dataclass(frozen=True)
class And(Formula):
    left: Formula
    right: Formula


@dataclass(frozen=True)
class Or(Formula):
    left: Formula
    right: Formula


@dataclass(frozen=True)
class Implies(Formula):
    premise: Formula
    conclusion: Formula


@dataclass(frozen=True)
class Exists(Formula):
    variable: Variable
    body: Formula


@dataclass(frozen=True)
class Forall(Formula):
    variable: Variable
    body: Formula


@dataclass(frozen=True)
class PredicateInterpretation:
    argument_sorts: tuple[str, ...]
    extension: frozenset[tuple[Value, ...]]


@dataclass(frozen=True)
class FiniteStructure:
    domains: Mapping[str, tuple[Value, ...]]
    constants: Mapping[str, tuple[str, Value]]
    predicates: Mapping[str, PredicateInterpretation]


@dataclass(frozen=True)
class Line:
    rule: str
    payload: tuple[object, ...] = ()


def _term_value(
    term: Term,
    structure: FiniteStructure,
    environment: Environment,
) -> Value:
    if isinstance(term, Variable):
        value = environment[term]
        if value not in structure.domains[term.sort]:
            raise ValueError("variable value is outside its declared sort")
        return value
    if isinstance(term, Constant):
        declared_sort, value = structure.constants[term.name]
        if declared_sort != term.sort:
            raise ValueError("constant sort does not match the term")
        if value not in structure.domains[term.sort]:
            raise ValueError("constant value is outside its declared sort")
        return value
    raise TypeError(f"unsupported term: {term!r}")


def _satisfies(
    formula: Formula,
    structure: FiniteStructure,
    environment: Environment,
) -> bool:
    if isinstance(formula, Top):
        return True
    if isinstance(formula, Bottom):
        return False
    if isinstance(formula, Atom):
        interpretation = structure.predicates[formula.predicate]
        if len(interpretation.argument_sorts) != len(formula.arguments):
            raise ValueError("predicate arity mismatch")
        values = tuple(
            _term_value(term, structure, environment)
            for term in formula.arguments
        )
        for term, expected_sort in zip(
            formula.arguments,
            interpretation.argument_sorts,
            strict=True,
        ):
            if term.sort != expected_sort:
                raise ValueError("predicate argument sort mismatch")
        return values in interpretation.extension
    if isinstance(formula, Equality):
        if formula.left.sort != formula.right.sort:
            raise ValueError("equality requires terms of the same sort")
        return _term_value(
            formula.left,
            structure,
            environment,
        ) == _term_value(formula.right, structure, environment)
    if isinstance(formula, Not):
        return not _satisfies(formula.body, structure, environment)
    if isinstance(formula, And):
        return _satisfies(
            formula.left,
            structure,
            environment,
        ) and _satisfies(formula.right, structure, environment)
    if isinstance(formula, Or):
        return _satisfies(
            formula.left,
            structure,
            environment,
        ) or _satisfies(formula.right, structure, environment)
    if isinstance(formula, Implies):
        return not _satisfies(
            formula.premise,
            structure,
            environment,
        ) or _satisfies(formula.conclusion, structure, environment)
    if isinstance(formula, (Exists, Forall)):
        values = structure.domains[formula.variable.sort]
        results = []
        for value in values:
            extended = dict(environment)
            extended[formula.variable] = value
            results.append(_satisfies(formula.body, structure, extended))
        return any(results) if isinstance(formula, Exists) else all(results)
    raise TypeError(f"unsupported formula: {formula!r}")


def _fill(
    formula: Formula,
    structure: FiniteStructure,
    environment: Environment,
) -> tuple[Line, ...]:
    if isinstance(formula, Top):
        return (Line("top-unit"),)
    if isinstance(formula, Bottom):
        return ()
    if isinstance(formula, Atom):
        if not _satisfies(formula, structure, environment):
            return ()
        values = tuple(
            _term_value(term, structure, environment)
            for term in formula.arguments
        )
        return (Line("atom", (formula.predicate, values)),)
    if isinstance(formula, Equality):
        if not _satisfies(formula, structure, environment):
            return ()
        value = _term_value(formula.left, structure, environment)
        return (Line("equality", (formula.left.sort, value)),)
    if isinstance(formula, Not):
        refuters = _fill(
            Implies(formula.body, Bottom()),
            structure,
            environment,
        )
        return tuple(Line("not", (refuter,)) for refuter in refuters)
    if isinstance(formula, And):
        return tuple(
            Line("and", (left, right))
            for left in _fill(formula.left, structure, environment)
            for right in _fill(formula.right, structure, environment)
        )
    if isinstance(formula, Or):
        left_lines = tuple(
            Line("or-left", (line,))
            for line in _fill(formula.left, structure, environment)
        )
        right_lines = tuple(
            Line("or-right", (line,))
            for line in _fill(formula.right, structure, environment)
        )
        return left_lines + right_lines
    if isinstance(formula, Implies):
        source = _fill(formula.premise, structure, environment)
        target = _fill(formula.conclusion, structure, environment)
        if not source:
            return (Line("implies-empty-source"),)
        if not target:
            return ()
        graph = tuple((line, target[0]) for line in source)
        return (Line("implies-total", graph),)
    if isinstance(formula, Exists):
        lines = []
        for value in structure.domains[formula.variable.sort]:
            extended = dict(environment)
            extended[formula.variable] = value
            lines.extend(
                Line("exists", (value, line))
                for line in _fill(formula.body, structure, extended)
            )
        return tuple(lines)
    if isinstance(formula, Forall):
        indexed_fibres = []
        values = structure.domains[formula.variable.sort]
        for value in values:
            extended = dict(environment)
            extended[formula.variable] = value
            indexed_fibres.append(
                tuple(
                    (value, line)
                    for line in _fill(formula.body, structure, extended)
                )
            )
        return tuple(
            Line("forall", tuple(family))
            for family in product(*indexed_fibres)
        )
    raise TypeError(f"unsupported formula: {formula!r}")


def _free_variables_term(term: Term) -> frozenset[Variable]:
    return frozenset({term}) if isinstance(term, Variable) else frozenset()


def _free_variables(formula: Formula) -> frozenset[Variable]:
    if isinstance(formula, (Top, Bottom)):
        return frozenset()
    if isinstance(formula, Atom):
        result: set[Variable] = set()
        for term in formula.arguments:
            result.update(_free_variables_term(term))
        return frozenset(result)
    if isinstance(formula, Equality):
        return _free_variables_term(formula.left) | _free_variables_term(
            formula.right
        )
    if isinstance(formula, Not):
        return _free_variables(formula.body)
    if isinstance(formula, (And, Or)):
        return _free_variables(formula.left) | _free_variables(formula.right)
    if isinstance(formula, Implies):
        return _free_variables(formula.premise) | _free_variables(
            formula.conclusion
        )
    if isinstance(formula, (Exists, Forall)):
        return _free_variables(formula.body) - {formula.variable}
    raise TypeError(f"unsupported formula: {formula!r}")


def _all_variables(formula: Formula) -> frozenset[Variable]:
    if isinstance(formula, (Top, Bottom)):
        return frozenset()
    if isinstance(formula, Atom):
        variables: set[Variable] = set()
        for term in formula.arguments:
            variables.update(_free_variables_term(term))
        return frozenset(variables)
    if isinstance(formula, Equality):
        return _free_variables_term(formula.left) | _free_variables_term(
            formula.right
        )
    if isinstance(formula, Not):
        return _all_variables(formula.body)
    if isinstance(formula, (And, Or)):
        return _all_variables(formula.left) | _all_variables(formula.right)
    if isinstance(formula, Implies):
        return _all_variables(formula.premise) | _all_variables(
            formula.conclusion
        )
    if isinstance(formula, (Exists, Forall)):
        return _all_variables(formula.body) | {formula.variable}
    raise TypeError(f"unsupported formula: {formula!r}")


def _replace_term(term: Term, old: Variable, new: Variable) -> Term:
    return new if term == old else term


def _rename_free_variable(
    formula: Formula,
    old: Variable,
    new: Variable,
) -> Formula:
    if isinstance(formula, (Top, Bottom)):
        return formula
    if isinstance(formula, Atom):
        return Atom(
            formula.predicate,
            tuple(_replace_term(term, old, new) for term in formula.arguments),
        )
    if isinstance(formula, Equality):
        return Equality(
            _replace_term(formula.left, old, new),
            _replace_term(formula.right, old, new),
        )
    if isinstance(formula, Not):
        return Not(_rename_free_variable(formula.body, old, new))
    if isinstance(formula, And):
        return And(
            _rename_free_variable(formula.left, old, new),
            _rename_free_variable(formula.right, old, new),
        )
    if isinstance(formula, Or):
        return Or(
            _rename_free_variable(formula.left, old, new),
            _rename_free_variable(formula.right, old, new),
        )
    if isinstance(formula, Implies):
        return Implies(
            _rename_free_variable(formula.premise, old, new),
            _rename_free_variable(formula.conclusion, old, new),
        )
    if isinstance(formula, (Exists, Forall)):
        if formula.variable == old:
            return formula
        renamed = _rename_free_variable(formula.body, old, new)
        return type(formula)(formula.variable, renamed)
    raise TypeError(f"unsupported formula: {formula!r}")


def _substitute_term(term: Term, variable: Variable, replacement: Term) -> Term:
    return replacement if term == variable else term


def _fresh_variable(
    variable: Variable,
    avoid: frozenset[Variable],
) -> Variable:
    suffix = 1
    while True:
        candidate = Variable(f"{variable.name}_{suffix}", variable.sort)
        if candidate not in avoid:
            return candidate
        suffix += 1


def _substitute(
    formula: Formula,
    variable: Variable,
    replacement: Term,
) -> Formula:
    if variable.sort != replacement.sort:
        raise ValueError("substitution must preserve the variable sort")
    if isinstance(formula, (Top, Bottom)):
        return formula
    if isinstance(formula, Atom):
        return Atom(
            formula.predicate,
            tuple(
                _substitute_term(term, variable, replacement)
                for term in formula.arguments
            ),
        )
    if isinstance(formula, Equality):
        return Equality(
            _substitute_term(formula.left, variable, replacement),
            _substitute_term(formula.right, variable, replacement),
        )
    if isinstance(formula, Not):
        return Not(_substitute(formula.body, variable, replacement))
    if isinstance(formula, And):
        return And(
            _substitute(formula.left, variable, replacement),
            _substitute(formula.right, variable, replacement),
        )
    if isinstance(formula, Or):
        return Or(
            _substitute(formula.left, variable, replacement),
            _substitute(formula.right, variable, replacement),
        )
    if isinstance(formula, Implies):
        return Implies(
            _substitute(formula.premise, variable, replacement),
            _substitute(formula.conclusion, variable, replacement),
        )
    if isinstance(formula, (Exists, Forall)):
        if formula.variable == variable:
            return formula
        body = formula.body
        binder = formula.variable
        if binder in _free_variables_term(replacement):
            avoid = (
                _all_variables(body)
                | _free_variables_term(replacement)
                | {variable}
            )
            fresh = _fresh_variable(binder, avoid)
            body = _rename_free_variable(body, binder, fresh)
            binder = fresh
        return type(formula)(
            binder,
            _substitute(body, variable, replacement),
        )
    raise TypeError(f"unsupported formula: {formula!r}")


def _and_all(formulas: tuple[Formula, ...]) -> Formula:
    result: Formula = Top()
    for formula in formulas:
        result = And(result, formula)
    return result


def _or_all(formulas: tuple[Formula, ...]) -> Formula:
    result: Formula = Bottom()
    for formula in formulas:
        result = Or(result, formula)
    return result


def _powerset(items: tuple[Value, ...]) -> tuple[frozenset[Value], ...]:
    return tuple(
        frozenset(selection)
        for size in range(len(items) + 1)
        for selection in combinations(items, size)
    )


HALT_WORLDS = tuple(
    frozenset(face)
    for size in range(1, 4)
    for face in combinations(("K", "X", "t"), size)
)


def _halt_structure(face: frozenset[str]) -> FiniteStructure:
    return FiniteStructure(
        domains={},
        constants={},
        predicates={
            name: PredicateInterpretation(
                (),
                frozenset({()}) if name in face else frozenset(),
            )
            for name in ("K", "X", "t")
        },
    )


def _world_formula(face: frozenset[str]) -> Formula:
    return _and_all(
        tuple(
            Atom(name) if name in face else Not(Atom(name))
            for name in ("K", "X", "t")
        )
    )


def _support_formula(support: frozenset[frozenset[str]]) -> Formula:
    return _or_all(tuple(_world_formula(face) for face in support))


def _finite_structures() -> tuple[FiniteStructure, ...]:
    domain = (0, 1)
    unary_tuples = ((0,), (1,))
    binary_tuples = tuple(product(domain, repeat=2))
    structures = []
    for unary_values in _powerset(unary_tuples):
        for binary_values in _powerset(binary_tuples):
            for constant_value in domain:
                structures.append(
                    FiniteStructure(
                        domains={"Obj": domain},
                        constants={"c": ("Obj", constant_value)},
                        predicates={
                            "P": PredicateInterpretation(
                                ("Obj",),
                                frozenset(unary_values),
                            ),
                            "R": PredicateInterpretation(
                                ("Obj", "Obj"),
                                frozenset(binary_values),
                            ),
                        },
                    )
                )
    return tuple(structures)


def test_all_128_propositions_match_canonical_thread_inhabitation() -> None:
    for selected in _powerset(HALT_WORLDS):
        support = frozenset(selected)
        formula = _support_formula(support)
        for face in HALT_WORLDS:
            structure = _halt_structure(face)
            expected = face in support
            assert _satisfies(formula, structure, {}) is expected
            assert bool(_fill(formula, structure, {})) is expected


def test_finite_predicate_semantics_matches_thread_inhabitation() -> None:
    obj = "Obj"
    x = Variable("x", obj)
    y = Variable("y", obj)
    c = Constant("c", obj)
    p_x = Atom("P", (x,))
    p_y = Atom("P", (y,))
    r_xy = Atom("R", (x, y))

    formulas = (
        p_x,
        Equality(x, c),
        Exists(y, r_xy),
        Forall(y, Implies(r_xy, p_y)),
        Exists(x, And(p_x, Forall(y, Implies(r_xy, p_y)))),
        Forall(x, Or(p_x, Not(p_x))),
        Implies(Forall(x, p_x), Exists(x, p_x)),
    )

    for structure in _finite_structures():
        for x_value, y_value in product((0, 1), repeat=2):
            environment = {x: x_value, y: y_value}
            for formula in formulas:
                assert bool(_fill(formula, structure, environment)) is (
                    _satisfies(formula, structure, environment)
                )


def test_capture_avoiding_substitution_preserves_semantics_and_fibres() -> None:
    obj = "Obj"
    x = Variable("x", obj)
    y = Variable("y", obj)
    original = Exists(y, Atom("R", (x, y)))
    substituted = _substitute(original, x, y)

    assert isinstance(substituted, Exists)
    assert substituted.variable != y
    assert _free_variables(substituted) == frozenset({y})

    for structure in _finite_structures():
        for value in (0, 1):
            environment = {y: value}
            original_environment = {x: value}
            assert _satisfies(
                substituted,
                structure,
                environment,
            ) is _satisfies(original, structure, original_environment)
            assert len(_fill(substituted, structure, environment)) == len(
                _fill(original, structure, original_environment)
            )


def test_quantifiers_are_dependent_sum_and_product_with_empty_edges() -> None:
    obj = "Obj"
    x = Variable("x", obj)
    nonempty = FiniteStructure(
        domains={obj: (0, 1)},
        constants={},
        predicates={
            "P": PredicateInterpretation((obj,), frozenset({(0,)})),
        },
    )
    empty = FiniteStructure(
        domains={obj: ()},
        constants={},
        predicates={"P": PredicateInterpretation((obj,), frozenset())},
    )

    existential = _fill(Exists(x, Atom("P", (x,))), nonempty, {})
    universal_decision = _fill(
        Forall(x, Or(Atom("P", (x,)), Not(Atom("P", (x,))))),
        nonempty,
        {},
    )

    assert {line.payload[0] for line in existential} == {0}
    assert len(universal_decision) == 1
    assert {value for value, _line in universal_decision[0].payload} == {0, 1}
    assert _fill(Exists(x, Atom("P", (x,))), empty, {}) == ()
    assert _fill(Forall(x, Atom("P", (x,))), empty, {}) == (
        Line("forall"),
    )
