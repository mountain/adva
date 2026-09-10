package iota.dual;

import java.util.List;

/**
 * The machine language of DualMachine version 0: two construction forms, one
 * non-construction form.
 *
 * - {@link App}   `(a b)`    a time frame: head plus operand
 * - {@link Space} `[a ... b]` a space frame: ordered family, no head
 * - {@link Angle} `<L R>`    refused: it is a judgement, not a term
 */
public final class Syntax {

    private Syntax() {
    }

    /** `(head operand)` — the time frame. */
    public static final class App implements Symbol {

        public final Symbol head;
        public final Symbol operand;

        App(Symbol head, Symbol operand) {
            this.head = head;
            this.operand = operand;
        }

        @Override
        public Symbol value() {
            return this;
        }

        @Override
        public String toString() {
            return "(" + head + " " + operand + ")";
        }
    }

    /** `[e0 ... en]` — the space frame. May be empty. */
    public static final class Space implements Symbol {

        public final List<Symbol> elements;

        Space(List<Symbol> elements) {
            this.elements = List.copyOf(elements);
        }

        @Override
        public Symbol value() {
            return this;
        }

        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder("[");
            for (int i = 0; i < elements.size(); i++) {
                if (i > 0) {
                    sb.append(' ');
                }
                sb.append(elements.get(i));
            }
            return sb.append(']').toString();
        }
    }

    /** `<left right>` — parsed by the recorded sources, never a term here. */
    public static final class Angle implements Symbol {

        public final Symbol left;
        public final Symbol right;

        Angle(Symbol left, Symbol right) {
            this.left = left;
            this.right = right;
        }

        @Override
        public Symbol value() {
            return this;
        }

        @Override
        public String toString() {
            return "<" + left + " " + right + ">";
        }
    }
}
