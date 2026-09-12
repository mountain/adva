package iota.dual;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * The dual stack of DualMachine v0.
 *
 * The left stack is the time coordinate: the single pending head, or a frame
 * marker. The right stack is the space coordinate: every subterm already
 * evaluated, bottom-to-top in production order, so the top of the right stack
 * is the operand produced most recently.
 */
public final class DualStack {

    private final List<Symbol> left = new ArrayList<>();
    private final List<Symbol> right = new ArrayList<>();

    public int llen() {
        return left.size();
    }

    public int rlen() {
        return right.size();
    }

    public Symbol lpeek() {
        if (left.isEmpty()) {
            throw new IllegalStateException("left stack is empty");
        }
        return left.get(left.size() - 1);
    }

    public Symbol rpeek() {
        if (right.isEmpty()) {
            throw new IllegalStateException("right stack is empty");
        }
        return right.get(right.size() - 1);
    }

    public Symbol lpop() {
        if (left.isEmpty()) {
            throw new IllegalStateException("left stack is empty");
        }
        return left.remove(left.size() - 1);
    }

    public Symbol rpop() {
        if (right.isEmpty()) {
            throw new IllegalStateException("right stack is empty");
        }
        return right.remove(right.size() - 1);
    }

    public void lpush(Symbol term) {
        left.add(term);
    }

    public void rpush(Symbol term) {
        right.add(term);
    }

    /** Pushes n operands, innermost first, so the last pushed is on top. */
    public void rpushAll(List<Symbol> terms) {
        right.addAll(terms);
    }

    /** The right stack, bottom-to-top. A copy. */
    public List<Symbol> rterms() {
        return List.copyOf(right);
    }

    public void clear() {
        left.clear();
        right.clear();
    }

    @Override
    public String toString() {
        StringBuilder l = new StringBuilder();
        for (Symbol t : left) {
            l.append(t);
        }
        StringBuilder r = new StringBuilder();
        for (int i = right.size() - 1; i >= 0; i--) {
            r.append(right.get(i));
        }
        return l + "|" + r;
    }

    /** Bottom-to-top read-out of one stack, for diagnostics. */
    public static String show(List<Symbol> terms) {
        List<Symbol> copy = new ArrayList<>(terms);
        Collections.reverse(copy);
        StringBuilder sb = new StringBuilder("top:");
        for (Symbol t : copy) {
            sb.append(' ').append(t);
        }
        return sb.toString();
    }
}
