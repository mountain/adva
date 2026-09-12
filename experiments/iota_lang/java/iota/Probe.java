package iota;

import iota.machine.IotaMachine;
import iota.machine.LISPMachine;
import iota.machine.Machine;
import iota.machine.SKIMachine;

import java.util.ArrayList;
import java.util.List;

/**
 * Prints the first N state transitions of one term, per rule class, so the
 * stack effect of each rule can be read off directly.
 *
 *   java iota.Probe "(i x)" [maxRounds]
 */
public final class Probe {

    public static void main(String[] args) {
        String term = args.length > 0 ? args[0] : "(i x)";
        int maxRounds = args.length > 1 ? Integer.parseInt(args[1]) : 8;

        trace("LISPMachine", LISPMachine.class, term, maxRounds);
        trace("SKIMachine", SKIMachine.class, term, maxRounds);
        trace("IotaMachine", IotaMachine.class, term, maxRounds);
    }

    private static void trace(String label, Class<?> from, String term, int maxRounds) {
        IotaMachine machine = new IotaMachine(from);
        machine.setVerbose(true);
        System.out.println("--- " + label + " : " + term + " ---");
        System.out.println("rules: " + machine.rules().stream().map(Machine.CondActn::name).toList());
        try {
            machine.execute(Parse.of(term), maxRounds);
        } catch (RuntimeException e) {
            System.out.println("stop: " + e.getMessage());
        }
        System.out.println("halted: " + machine.halted() + " final: " + machine.stateString());
    }

    /** Minimal reader for the driver's own term syntax: atoms, (a b), "quoted". */
    static final class Parse {

        static Symbol of(String text) {
            List<String> tokens = tokenize(text);
            int[] pos = {0};
            Symbol term = atom(tokens, pos);
            if (pos[0] != tokens.size()) {
                throw new IllegalArgumentException("trailing tokens in " + text);
            }
            return term;
        }

        private static List<String> tokenize(String text) {
            List<String> tokens = new ArrayList<>();
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < text.length(); i++) {
                char c = text.charAt(i);
                if (c == '(' || c == ')') {
                    if (sb.length() > 0) {
                        tokens.add(sb.toString());
                        sb.setLength(0);
                    }
                    tokens.add(String.valueOf(c));
                } else if (Character.isWhitespace(c)) {
                    if (sb.length() > 0) {
                        tokens.add(sb.toString());
                        sb.setLength(0);
                    }
                } else {
                    sb.append(c);
                }
            }
            if (sb.length() > 0) {
                tokens.add(sb.toString());
            }
            return tokens;
        }

        private static Symbol atom(List<String> tokens, int[] pos) {
            if (pos[0] >= tokens.size()) {
                throw new IllegalArgumentException("unexpected end of input");
            }
            String token = tokens.get(pos[0]++);
            if (!token.equals("(")) {
                return switch (token) {
                    case "s" -> Symbols.S;
                    case "k" -> Symbols.K;
                    case "i" -> Symbols.I;
                    case "ι" -> Symbols.IOTA;
                    default -> Symbols.symbolize(token);
                };
            }
            Symbol left = atom(tokens, pos);
            Symbol right = atom(tokens, pos);
            if (pos[0] >= tokens.size() || !tokens.get(pos[0]++).equals(")")) {
                throw new IllegalArgumentException("expected )");
            }
            return Symbols.cons(left, right);
        }
    }
}
