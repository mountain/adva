package iota.util;

import iota.Symbol;

/**
 * Reconnection note (adva research 0167): in iota-lang this type is an
 * interface with Either-valued accessors, while LISPMachine/SKIMachine read
 * the public fields `left`/`right` and require `instanceof Cons`. This is the
 * concrete `Symbol` pair the machine contract actually uses.
 */
public final class Cons implements Symbol {

    public final Symbol left;
    public final Symbol right;

    public Cons(Symbol left, Symbol right) {
        this.left = left;
        this.right = right;
    }

    @Override
    public Symbol value() {
        return this;
    }

    @Override
    public String toString() {
        return String.format("(%s %s)", left, right);
    }
}
