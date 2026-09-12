package iota.dual;

import iota.dual.Syntax.App;
import iota.dual.Syntax.Angle;
import iota.dual.Syntax.Space;

import java.util.Arrays;
import java.util.List;

/** One interning site. Every token exists exactly once, so `==` is identity. */
public final class Tokens {

    private Tokens() {
    }

    public static final Symbol S = new Atom("s");
    public static final Symbol K = new Atom("k");
    public static final Symbol I = new Atom("i");
    public static final Symbol IOTA = new Atom("\u03b9");

    public static Symbol atom(String name) {
        return new Atom(name);
    }

    /** `(head arg0 arg1 ...)`, right-nested. */
    public static Symbol app(Symbol head, Symbol... args) {
        Symbol term = head;
        for (Symbol arg : args) {
            term = new App(term, arg);
        }
        return term;
    }

    public static Symbol app2(Symbol head, Symbol operand) {
        return new App(head, operand);
    }

    public static Symbol space(Symbol... elements) {
        return new Space(Arrays.asList(elements));
    }

    public static Symbol space(List<Symbol> elements) {
        return new Space(elements);
    }

    public static Symbol angle(Symbol left, Symbol right) {
        return new Angle(left, right);
    }

    static final class Atom implements Symbol {

        private final String name;

        Atom(String name) {
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
