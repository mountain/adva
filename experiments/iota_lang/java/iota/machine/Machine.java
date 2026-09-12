package iota.machine;

import iota.Symbol;
import iota.util.DualStack;

import java.util.List;
import java.util.function.Function;

public interface Machine {

    @FunctionalInterface
    interface Condition extends Function<DualStack<Symbol>, Boolean> {
    }

    @FunctionalInterface
    interface Action extends Function<DualStack<Symbol>, DualStack<Symbol>> {
    }

    record CondActn(String name, Condition cond, Action actn) {
    }

    /** Exposed so a bounded run can observe each firing. */
    List<CondActn> rules();

    Symbol execute(Symbol program);

    Symbol execute(Symbol program, long stepCap) throws StepLimitExceeded;

    final class StepLimitExceeded extends RuntimeException {
        public StepLimitExceeded(String message) {
            super(message);
        }
    }
}
