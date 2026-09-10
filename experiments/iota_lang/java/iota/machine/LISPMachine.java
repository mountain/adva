package iota.machine;

import iota.Symbol;
import iota.Symbols;
import iota.util.Cons;
import iota.util.DualStack;

import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.List;

/**
 * Reconnection note (adva research 0167). The recorded sources register rules
 * by reflecting over `getFields()` and reading `@rule` unconditionally, which
 * dereferences a null annotation on every non-rule field. Here rules are
 * collected from the class chain, superclass first, in declaration order, so
 * the firing order is deterministic and the deprecated `rule` annotation is
 * not required.
 */
public abstract class LISPMachine implements Machine {

    /**
     * Fix 1 of 2 (adva research 0167). The recorded action pushes the head
     * before the tail, which splits `(x y)` into the state `x|y`; every
     * collecting rule in this class (`swap`, `wrap2`, `wrap3`, `rvrt`) reads
     * the head from the left stack and the collected operands from the right,
     * and `rvrt` requires an empty left stack. Pushing tail-then-head is the
     * order those rules require, so the head lands on the left and the operand
     * goes to the right.
     */
    public static final CondActn onCons = new CondActn("cons", state ->
            state.llen() >= 1 && state.lpeek() instanceof Cons, state -> {
        Cons c = (Cons) state.lpop();
        state.rpush(c.right);
        state.lpush(c.left);
        return state;
    });

    public static final CondActn onSwap = new CondActn("swap", state ->
            state.llen() == 1 && state.rlen() == 0 && state.lpeek() instanceof Cons, state -> {
        Cons c = (Cons) state.lpop();
        state.lpush(c.left);
        state.lpush(c.right);
        return state;
    });

    public static final CondActn onMove = new CondActn("move", state ->
            state.llen() == 0 && state.rlen() == 2, state -> {
        state.lpush(state.rpop());
        state.lpush(state.rpop());
        return state;
    });

    public static final CondActn onVar = new CondActn("var", state ->
            state.llen() >= 1 && state.lpeek().value() == Symbols.symbolize("var"),
            state -> {
                state.rpush(state.lpop());
                return state;
            });

    public static final CondActn onWrap2 = new CondActn("wrap2", state ->
            state.llen() == 0 && state.rlen() == 2, state -> {
        state.rpush(Symbols.cons(state.rpop(), state.rpop()));
        return state;
    });

    public static final CondActn onWrap3 = new CondActn("wrap3", state ->
            state.llen() == 0 && state.rlen() == 3, state -> {
        Symbol third = state.rpop();
        Symbol second = state.rpop();
        Symbol first = state.rpop();
        state.rpush(Symbols.apply(first, second, third));
        return state;
    });

    public static final CondActn onLEmpty = new CondActn("lem", state ->
            state.llen() == 0 && state.rlen() > 0, state -> {
        state.lpush(state.rpop());
        return state;
    });

    public static final CondActn onDes = new CondActn("des", state ->
            state.llen() == 1 && state.rlen() == 1 && state.lpeek().value() == Symbols.S,
            state -> {
                state.lpush(Symbols.cons(state.lpop(), state.rpop()));
                return state;
            });

    public static final CondActn onREmpty = new CondActn("rem", state ->
            state.rlen() == 0 && state.llen() > 0, state -> {
        state.rpush(state.lpop());
        return state;
    });

    public static final CondActn onRvrt = new CondActn("rvrt", state ->
            state.llen() == 2 && state.rlen() == 0, state -> {
        Symbol second = state.lpop();
        Symbol first = state.lpop();
        state.lpush(Symbols.cons(first, second));
        return state;
    });

    private final List<CondActn> registry = new ArrayList<>();
    private final DualStack<Symbol> state = new DualStack<>();

    public void loadRules(Class<?> from) {
        List<Class<?>> chain = new ArrayList<>();
        for (Class<?> c = from; c != null; c = c.getSuperclass()) {
            chain.add(0, c);
        }
        for (Class<?> c : chain) {
            for (Field field : c.getDeclaredFields()) {
                if (!CondActn.class.isAssignableFrom(field.getType())) {
                    continue;
                }
                try {
                    field.setAccessible(true);
                    CondActn rule = (CondActn) field.get(null);
                    if (rule != null) {
                        registry.add(rule);
                    }
                } catch (ReflectiveOperationException e) {
                    throw new IllegalStateException("rule field " + field.getName(), e);
                }
            }
        }
    }

    @Override
    public List<CondActn> rules() {
        return List.copyOf(registry);
    }

    /** Fires every rule whose condition holds; returns the rules that fired. */
    protected List<String> proceed() {
        List<String> fired = new ArrayList<>();
        for (CondActn rule : registry) {
            if (rule.cond().apply(state)) {
                rule.actn().apply(state);
                fired.add(rule.name());
                if (verbose) {
                    System.out.println(String.format("%s: %s", rule.name(), state));
                }
            }
        }
        return fired;
    }

    private boolean verbose = false;

    public void setVerbose(boolean verbose) {
        this.verbose = verbose;
    }

    /** The recorded halt condition: the left stack is empty. */
    public boolean halted() {
        return state.llen() == 0;
    }

    /**
     * Diagnostics only (adva research 0167). The recorded halt condition is
     * "left stack empty", which fires at states where no result exists yet:
     * after a K or I reduction the head often moves to the right stack and
     * leaves the left stack empty, and `rem` then pulls it back, so the
     * recorded loop treats an intermediate state as a normal form. A state is
     * a result only when the left stack is empty and the right stack holds
     * exactly one term.
     */
    public boolean haltedStrict() {
        return state.llen() == 0 && state.rlen() == 1;
    }

    /** Loads one program into a cleared machine. Diagnostics only. */
    public void reset(Symbol program) {
        state.clear();
        state.lpush(program);
        steps = 0L;
        lastFired = new ArrayList<>();
        notifyObserver(0L);
    }

    /** Runs exactly one round. Diagnostics only. */
    public void step() {
        lastFired = proceed();
        steps++;
        notifyObserver(steps);
    }

    /**
     * Called after every round with the current state string. Diagnostics only;
     * lets a driver record whether a documented result was ever reached, even
     * when the machine later fails.
     */
    @FunctionalInterface
    public interface Observer {
        void after(long step, String state, Symbol leftTop, Symbol rightTop);
    }

    private Observer observer = null;

    public void setObserver(Observer observer) {
        this.observer = observer;
    }

    protected void notifyObserver(long step) {
        if (observer != null) {
            observer.after(step, state.toString(),
                    state.llen() > 0 ? state.lpeek() : null,
                    state.rlen() > 0 ? state.rpeek() : null);
        }
    }

    public List<String> lastFired() {
        return List.copyOf(lastFired);
    }

    /** Reads the single term on the right stack. Diagnostics only. */
    public Symbol result() {
        if (state.llen() != 0 || state.rlen() != 1) {
            throw new IllegalStateException("no result at state " + state);
        }
        return state.rpeek();
    }

    private List<String> lastFired = new ArrayList<>();

    public String stateString() {
        return state.toString();
    }

    @Override
    public Symbol execute(Symbol program) {
        try {
            return execute(program, 100_000L);
        } catch (StepLimitExceeded e) {
            throw new IllegalStateException(e.getMessage(), e);
        }
    }

    @Override
    public Symbol execute(Symbol program, long stepCap) throws StepLimitExceeded {
        state.clear();
        state.lpush(program);
        long steps = 0L;
        while (!halted()) {
            List<String> fired = proceed();
            steps++;
            this.steps = steps;
            notifyObserver(steps);
            if (steps > stepCap) {
                throw new StepLimitExceeded(
                        "iota machine step cap " + stepCap + " exhausted at state " + state);
            }
            if (fired.isEmpty()) {
                throw new IllegalStateException(
                        "no rule applies at state " + state + " after " + steps + " rounds");
            }
        }
        return state.rpeek();
    }

    public long lastSteps() {
        return steps;
    }

    private long steps = 0L;
}
