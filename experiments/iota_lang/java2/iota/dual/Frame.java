package iota.dual;

import java.util.List;

/**
 * An explicit continuation frame: one head, its argument buffer, and the
 * construction form its result is made of.
 *
 * A frame is created per flattened spine, not per written bracket. `(a b c)` is
 * right-nested application, so its spine is flattened once: the head plus its
 * three arguments. That is what lets the recorded rules work at all — `S` needs
 * three arguments in hand, and a machine that re-marshals one bracket at a time
 * can never present them together.
 *
 * The frame also records the right-stack depth it opened at, so its arguments
 * are exactly the values produced above that depth. Ownership, not counting, is
 * what delimits a frame; the recorded `wrap2`/`wrap3` rules could only count.
 */
final class Frame {

    enum Then {
        /** Application: the result is the head applied to its arguments. */
        APP,
        /** Space frame: the result is the ordered family of its elements. */
        SPACE
    }

    final Then then;
    final int base;
    final int arity;
    /** The head, once reduced. Null while it is still being evaluated. */
    Symbol head;

    Frame(Then then, int base, int arity) {
        this.then = then;
        this.base = base;
        this.arity = arity;
    }


    @Override
    public String toString() {
        return then + "/" + arity + "@" + base + (head == null ? "" : ":" + head);
    }
}
