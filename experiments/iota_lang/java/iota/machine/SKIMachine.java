package iota.machine;

import iota.Symbol;
import iota.Symbols;
import iota.util.Cons;

/**
 * SKI reductions, reconnected to {@link Symbols} (adva research 0167).
 *
 * Every condition compares interned symbol identity through `value()`, and the
 * `Kr` rule reads the two public fields of {@link Cons} instead of the
 * Either-valued accessors of the recorded `iota.util.Cons` interface.
 */
public abstract class SKIMachine extends LISPMachine {

    public static final CondActn onI = new CondActn("I", state ->
            state.llen() >= 1 && state.rlen() >= 1 && state.lpeek().value() == Symbols.I,
            state -> {
                state.lpop();
                state.lpush(state.rpop());
                return state;
            });

    public static final CondActn onK = new CondActn("K", state ->
            state.llen() >= 1 && state.rlen() >= 2 && state.lpeek().value() == Symbols.K,
            state -> {
                state.lpop();
                state.lpush(state.rpop());
                state.rpop();
                return state;
            });

    public static final CondActn onKr = new CondActn("Kr", state -> {
        if (state.rlen() < 1) {
            return false;
        }
        if (!(state.rpeek() instanceof Cons)) {
            return false;
        }
        Symbol head = ((Cons) state.rpeek()).left;
        if (!(head instanceof Cons)) {
            return false;
        }
        return ((Cons) head).left == Symbols.K;
    }, state -> {
        Cons outer = (Cons) state.rpop();
        state.lpush(((Cons) outer.left).right);
        return state;
    });

    /**
     * Fix 2 of 2 (adva research 0167). The recorded action pushes `(y z)` and
     * then `z`, giving the right stack `(y z) z`; `wrap3` reads that stack as
     * `[third, second, first]`, which would rebuild `(x (y z))` and would also
     * leave the stack in a shape `wrap3`'s own condition requires. Pushing `z`
     * first and the application second is the same order this class's `onI`
     * and `onK` use when they return the head to the left stack.
     */
    public static final CondActn onS = new CondActn("S", state ->
            state.llen() >= 1 && state.rlen() >= 3 && state.lpeek().value() == Symbols.S,
            state -> {
                state.lpop();
                Symbol x = state.rpop();
                Symbol y = state.rpop();
                Symbol z = state.rpop();
                state.lpush(x);
                state.rpush(z);
                state.rpush(Symbols.cons(y, z));
                return state;
            });
}
