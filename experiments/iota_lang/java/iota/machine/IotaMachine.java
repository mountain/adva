package iota.machine;

import iota.Symbol;
import iota.Symbols;

/**
 * The iota machine: one symbol, one rule.
 *
 *     ι x  =>  x S K
 *
 * The recorded sources declare two iota rules that match the same token through
 * two different spellings (`Iota.toString()` and
 * `ski.lang.ski.$.Combinator.iota`). With one interning site those are the same
 * symbol, so the duplicate is dropped rather than kept as a dead rule; the
 * algebraic form is preserved exactly.
 */
public final class IotaMachine extends SKIMachine {

    public static final CondActn onIota = new CondActn("iota", state ->
            state.llen() > 0 && state.rlen() > 0 && state.lpeek().value() == Symbols.IOTA,
            state -> {
                state.lpop();
                state.lpush(state.rpop());
                state.rpush(Symbols.K);
                state.rpush(Symbols.S);
                return state;
            });

    public static final CondActn onIotaSwap = new CondActn("iota-swap", state ->
            state.llen() == 2 && state.rlen() == 0
                    && state.lppeek().value() == Symbols.IOTA, state -> {
        // l = [x, ι] with x on top. The dual stack already holds the argument,
        // so the consequent is staged directly: pop both, push x back, then
        // push K and S so that S sits on top.
        state.lpop();
        Symbol x = state.lpop();
        state.lpush(x);
        state.rpush(Symbols.K);
        state.rpush(Symbols.S);
        return state;
    });

    public static final CondActn onIotaCirc = new CondActn("iota-circ", state ->
            state.llen() < 2 && state.rlen() > 0
                    && state.lpeek().value() == Symbols.IOTA, state -> {
        state.lpush(state.rpop());
        return state;
    });

    public IotaMachine() {
        this(IotaMachine.class);
    }

    public IotaMachine(Class<?> from) {
        loadRules(from);
    }
}
