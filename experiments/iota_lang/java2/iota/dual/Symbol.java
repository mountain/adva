package iota.dual;

/**
 * One token of the machine language.
 *
 * Identity is the token itself: the machine compares tokens with `==`, so every
 * token is created once by {@link Tokens}. The recorded sources compared a
 * lambda (from `iota.combinators.Combinator`) against `state.lpeek().value()`,
 * which can never hold; that is one of the defects 0167 section 3 records.
 */
public interface Symbol {

    /** The identity carrier used by rule conditions. */
    Symbol value();
}
