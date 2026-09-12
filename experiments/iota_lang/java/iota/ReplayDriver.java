package iota;

import iota.machine.IotaMachine;
import iota.machine.Machine;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Replays the seventeen recorded cases of iota-lang
 * src/tests/java/iota/SKITest.java against the reconnected machine and emits
 * one JSON line per case plus one summary line per mode.
 *
 * Two modes:
 *
 * - `recorded` runs the recorded execution loop (`halted()` is "left stack
 *   empty") and is the only mode that can count as reproducing the contract;
 * - `strict-halt` is a bounded diagnostic that additionally requires an empty
 *   left stack AND a single right-stack term before reading a result, which
 *   separates "the rule algebra cannot reach the result" from "the loop stops
 *   one round too early".
 *
 * Every `expected` below is transcribed from that file; where the original
 * asserts a term (`"x"`, `"(x y)"`) the driver compares token strings.
 */
public final class ReplayDriver {

    private static final Symbol X = Symbols.symbolize("x");
    private static final Symbol Y = Symbols.symbolize("y");
    private static final Symbol Z = Symbols.symbolize("z");

    private static final Symbol IOTA = Symbols.IOTA;
    private static final Symbol I_ENC = Symbols.apply(IOTA, IOTA);
    private static final Symbol K_ENC = Symbols.apply(IOTA, Symbols.apply(IOTA, Symbols.apply(IOTA, IOTA)));
    private static final Symbol S_ENC = Symbols.apply(IOTA,
            Symbols.apply(IOTA, Symbols.apply(IOTA, Symbols.apply(IOTA, IOTA))));

    private static final long STEP_CAP = 100_000L;

    public static void main(String[] args) {
        List<Map<String, Object>> cases = new ArrayList<>();

        cases.add(run("testXY", Symbols.cons(X, Y), "(x y)"));
        cases.add(run("testI", Symbols.cons(Symbols.I, X), "x"));
        cases.add(run("testK", Symbols.cons(Symbols.cons(Symbols.K, X), Y), "x"));
        cases.add(run("testS", Symbols.cons(Symbols.cons(Symbols.cons(Symbols.S, X), Y), Z),
                "((x z) (y z))"));
        cases.add(run("testFalse", Symbols.cons(Symbols.cons(Symbols.cons(Symbols.S, Symbols.K), X), Y),
                "y"));
        Symbol reverse = Symbols.apply(Symbols.S,
                Symbols.cons(Symbols.K, Symbols.cons(Symbols.S, Symbols.I)), Symbols.K);
        cases.add(run("testReverse", Symbols.apply(reverse, X, Y), "(y x)"));
        cases.add(run("testKSKS",
                Symbols.cons(Symbols.cons(Symbols.cons(Symbols.K, Symbols.S), Symbols.K), Symbols.S),
                "(s s)"));
        cases.add(run("testKKKSKS",
                Symbols.apply(Symbols.apply(Symbols.cons(Symbols.cons(Symbols.K, Symbols.K), Symbols.K),
                        Symbols.S), Symbols.K, Symbols.S),
                "(s s)"));
        cases.add(run("testSKK",
                Symbols.cons(Symbols.apply(Symbols.cons(Symbols.cons(Symbols.S, Symbols.K), Symbols.K), X), Y),
                "(x y)"));

        // The (h h h) family. The recorded test builds `Symbol hi` from `hi`
        // and then writes `cons(cons(hi, hi), hi)`; the term is therefore
        // ((i i) (i i)) for every one of the five, and the five recorded
        // expect-strings differ from each other and from that term. The
        // transcribed terms and expect-strings are kept exactly as recorded.
        cases.add(run("testII", Symbols.apply(I_ENC, I_ENC), "(i i)"));
        cases.add(run("testIII", Symbols.apply(I_ENC, I_ENC), "((i i) i)"));
        cases.add(run("testIIII", Symbols.apply(I_ENC, I_ENC), "((i i) (i i))"));
        cases.add(run("testIIIII", Symbols.apply(I_ENC, I_ENC), "(((i i) (i i)) i)"));
        cases.add(run("testIIIIII", Symbols.apply(I_ENC, I_ENC), "(((i i) (i i)) (i i))"));

        cases.add(run("testIota2", Symbols.cons(I_ENC, X), "x"));
        cases.add(run("testIota4", Symbols.cons(K_ENC, Symbols.apply(X, Y)), "x"));
        cases.add(run("testIota5", Symbols.cons(S_ENC, Symbols.apply(X, Y, Z)), "((x z) (y z))"));

        for (Map<String, Object> c : cases) {
            System.out.println(json(c));
        }
        System.out.println(json(summary("recorded", cases)));
        System.out.println(json(summary("strict-halt", cases)));
        long reached = cases.stream()
                .filter(c -> asMap(c.get("recorded")).get("reached_result_at_step") != null)
                .count();
        System.exit(reached > 0 ? 0 : 1);
    }

    private static Map<String, Object> summary(String mode, List<Map<String, Object>> cases) {
        long verdict = 0;
        long halted = 0;
        long reached = 0;
        for (Map<String, Object> c : cases) {
            Map<String, Object> attempt = mode.equals("recorded")
                    ? asMap(c.get("recorded")) : asMap(c.get("strict"));
            if (attempt.containsKey("error")) {
                verdict++;
            } else {
                halted++;
            }
            if (attempt.get("reached_result_at_step") != null) {
                reached++;
            }
        }
        Map<String, Object> row = new LinkedHashMap<>();
        row.put("kind", "summary");
        row.put("mode", mode);
        row.put("cases", cases.size());
        row.put("expected_value_read", halted);
        row.put("errored", verdict);
        row.put("ever_reached_expected_value", reached);
        row.put("step_cap", STEP_CAP);
        return row;
    }

    @SuppressWarnings("unchecked")
    private static Map<String, Object> asMap(Object value) {
        return (Map<String, Object>) value;
    }

    private static boolean matches(Symbol term, String expected) {
        return term != null && expected.equals(term.toString());
    }

    private static Map<String, Object> run(String name, Symbol term, String expected) {
        Map<String, Object> row = new LinkedHashMap<>();
        row.put("kind", "case");
        row.put("name", name);
        row.put("term", term.toString());
        row.put("expected", expected);

        Map<String, Object> recorded = attempt(term, expected, false);
        Map<String, Object> strict = attempt(term, expected, true);
        Map<String, Object> modes = new LinkedHashMap<>();
        for (Map.Entry<String, Map<String, Object>> e : List.of(
                Map.entry("recorded", recorded), Map.entry("strict-halt", strict))) {
            String mode = e.getKey();
            Map<String, Object> attempt = e.getValue();
            modes.put(mode + ":verdict", attempt.get("result"));
            modes.put(mode + ":halted", attempt.get("halted"));
            modes.put(mode + ":reached_result_at_step", attempt.get("reached_result_at_step"));
        }
        row.put("modes", modes);
        row.put("recorded", recorded);
        row.put("strict", strict);
        return row;
    }

    private static Map<String, Object> attempt(Symbol term, String expected, boolean strict) {
        Map<String, Object> result = new LinkedHashMap<>();
        IotaMachine machine = new IotaMachine();

        String[] states = new String[1];
        Long[] resultStep = new Long[1];
        List<String> history = new ArrayList<>();
        machine.setObserver((step, state, leftTop, rightTop) -> {
            states[0] = state;
            history.add(step + ":" + state);
            if (resultStep[0] == null
                    && (matches(leftTop, expected) || matches(rightTop, expected))) {
                resultStep[0] = step;
                
            }
        });

        boolean halted = false;
        try {
            Symbol reduced = strict ? runStrict(machine, term) : machine.execute(term, STEP_CAP);
            result.put("result", reduced.toString());
            result.put("firings", machine.lastSteps());
            halted = true;
        } catch (Machine.StepLimitExceeded | IllegalStateException | IllegalArgumentException e) {
            if (Boolean.getBoolean("iota.debug")) {
                e.printStackTrace();
            }
            result.put("error", e.getClass().getSimpleName() + ": " + e.getMessage());
            result.put("firings", machine.lastSteps());
        }
        result.put("halted", halted);
        result.put("history", String.join(" ", history));
        result.put("last_state", states[0]);
        result.put("reached_result_at_step", resultStep[0]);
        return result;
    }

    private static Symbol runStrict(IotaMachine machine, Symbol term) {
        machine.reset(term);
        long steps = 0L;
        while (!machine.haltedStrict()) {
            machine.step();
            steps++;
            if (steps > STEP_CAP) {
                throw new Machine.StepLimitExceeded("strict step cap " + STEP_CAP
                        + " exhausted at state " + machine.stateString());
            }
            if (machine.lastFired().isEmpty()) {
                throw new IllegalStateException("no rule applies at state "
                        + machine.stateString() + " after " + steps + " rounds");
            }
        }
        return machine.result();
    }

    private static String json(Map<String, Object> row) {
        StringBuilder sb = new StringBuilder("{");
        boolean first = true;
        for (Map.Entry<String, Object> e : row.entrySet()) {
            if (!first) {
                sb.append(", ");
            }
            first = false;
            sb.append('"').append(e.getKey()).append("\": ");
            append(sb, e.getValue());
        }
        return sb.append('}').toString();
    }

    private static void append(StringBuilder sb, Object value) {
        if (value == null) {
            sb.append("null");
        } else if (value instanceof Number || value instanceof Boolean) {
            sb.append(value);
        } else if (value instanceof Map<?, ?> map) {
            StringBuilder inner = new StringBuilder("{");
            boolean first = true;
            for (Map.Entry<?, ?> e : map.entrySet()) {
                if (!first) {
                    inner.append(", ");
                }
                first = false;
                inner.append('"').append(e.getKey()).append("\": ");
                append(inner, e.getValue());
            }
            sb.append(inner).append('}');
        } else {
            sb.append('"').append(escape(String.valueOf(value))).append('"');
        }
    }

    private static String escape(String text) {
        return text.replace("\\", "\\\\").replace("\"", "\\\"");
    }
}
