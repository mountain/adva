package iota.dual;

import java.util.ArrayList;
import java.util.List;

/**
 * A work item: either a term to evaluate, or a pending application whose head
 * and operand are still being evaluated.
 *
 * The pending application is the whole reason this type exists. When `S`
 * produces `((x z) (y z))` it does not produce two values: it produces one
 * application whose head is itself a term that still has to be evaluated. A
 * machine that pushes `(x z)` straight to the operand list gets
 * `S K K x y = ((k x) (k x))` handed back unevaluated, and the recorded tests
 * assert the reduced `x`. So a frame step is never "here is a value"; it is
 * always "here is a term, evaluate it, and then assemble."
 */
final class Item {

    enum Kind {
        /** Evaluate this term. */
        TERM,
        /** Evaluate the head, then the operand, then assemble `(head operand)`. */
        APPLY,
        /** Collect `arity` elements as one ordered family. */
        SPACE
    }

    final Kind kind;
    final Symbol term;
    final Symbol pendingHead;
    final Symbol pendingOperand;
    final int arity;

    private Item(Kind kind, Symbol term, Symbol pendingHead, Symbol pendingOperand, int arity) {
        this.kind = kind;
        this.term = term;
        this.pendingHead = pendingHead;
        this.pendingOperand = pendingOperand;
        this.arity = arity;
    }

    static Item term(Symbol term) {
        return new Item(Kind.TERM, term, null, null, 0);
    }

    static Item apply(Symbol head, Symbol operand) {
        return new Item(Kind.APPLY, null, head, operand, 0);
    }

    static Item space(int arity) {
        return new Item(Kind.SPACE, null, null, null, arity);
    }

    @Override
    public String toString() {
        switch (kind) {
            case APPLY:
                return "\u27e8" + pendingHead + " " + pendingOperand + "\u27e9";
            case SPACE:
                return "\u27e8[" + arity + "]\u27e9";
            default:
                return String.valueOf(term);
        }
    }
}
