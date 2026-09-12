package iota;

import iota.util.Cons;

/**
 * One interning site for symbol identity.
 *
 * The iota-lang sources compare tokens with `==`
 * (`state.lpeek().value() == $.Combinator.k`), so every token must be a single
 * stable object. In the recorded sources the combinators are lambdas in
 * `iota.combinators.Combinator`; those cannot carry a printable name, so the
 * rules of the machine could never match them. Here each symbol is one
 * `SymbolizeSymbol` with a fixed name and an identity-preserving `value()`.
 */
public final class Symbols {

    private Symbols() {
    }

    public static final Symbol S = new SymbolizeSymbol("s");
    public static final Symbol K = new SymbolizeSymbol("k");
    public static final Symbol I = new SymbolizeSymbol("i");
    public static final Symbol IOTA = new SymbolizeSymbol("ι");

    public static Symbol symbolize(String name) {
        return new SymbolizeSymbol(name);
    }

    public static Cons cons(Symbol left, Symbol right) {
        return new Cons(left, right);
    }

    /**
     * Right-nested application chain: chain(a, b, c) is ((a b) c).
     */
    public static Symbol apply(Symbol head, Symbol... args) {
        Symbol term = head;
        for (Symbol arg : args) {
            term = cons(term, arg);
        }
        return term;
    }

    public static final class SymbolizeSymbol implements Symbol {

        private final String name;

        SymbolizeSymbol(String name) {
            this.name = name;
        }

        @Override
        public Symbol value() {
            return this;
        }

        @Override
        public String toString() {
            return name;
        }
    }
}
