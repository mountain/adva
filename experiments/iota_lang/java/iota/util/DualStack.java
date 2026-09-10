package iota.util;

import iota.Symbol;

/**
 * Reconnection note (adva research 0167). Two deltas against the recorded
 * `iota.util.DualStack`:
 *
 * 1. `lppeek()` — the second element from the top of the left stack — is used
 *    by the iota machine's two-argument rule but is not declared there;
 * 2. `toString()` is deterministic. The recorded version prints the two
 *    functional-interface fields, so its state strings depend on JVM lambda
 *    identities (`iota.util.Applicative$$Lambda$14/0x...`), which cannot be
 *    compared between runs.
 */
public class DualStack<T> {

    private final Stack<T> lstack = new Stack<T>() {
        @Override
        Node<T> build(T val) {
            return new LNode<>(val);
        }
    };

    private final Stack<T> rstack = new Stack<T>() {
        @Override
        Node<T> build(T val) {
            return new RNode<>(val);
        }
    };

    @Override
    public String toString() {
        return String.format("%s|%s", lstack, rstack);
    }

    public void clear() {
        lstack.clear();
        rstack.clear();
    }

    public int llen() {
        return lstack.len();
    }

    public int rlen() {
        return rstack.len();
    }

    public T lpeek() {
        return lstack.peek();
    }

    /** Second element from the top of the left stack. */
    public T lppeek() {
        return lstack.ppeek();
    }

    public T rpeek() {
        return rstack.peek();
    }

    public T lpop() {
        return lstack.pop();
    }

    public T rpop() {
        return rstack.pop();
    }

    public void lpush(T elem) {
        lstack.push(elem);
    }

    public void rpush(T elem) {
        rstack.push(elem);
    }
}
