package iota.dual;

import iota.dual.Machine.Budget;
import iota.dual.Machine.Refusal;
import iota.dual.Machine.Stall;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * The DualMachine v0 suite.
 *
 * Group A replays the cases recorded in iota-lang `src/tests/java/iota/SKITest.java`.
 * Group B checks the space frame. Group C checks mixed nesting. Group D checks
 * that the angle form is refused rather than evaluated.
 *
 * Assertions are made on the string form of the read-out family, which is the
 * canonical rendering of `(` `)` `[` `]` in the reader.
 */
public final class TestDriver {

    private static final Symbol S = Tokens.S;
    private static final Symbol K = Tokens.K;
    private static final Symbol I = Tokens.I;
    private static final Symbol IOTA = Tokens.IOTA;

    private static final Symbol X = Tokens.atom("x");
    private static final Symbol Y = Tokens.atom("y");
    private static final Symbol Z = Tokens.atom("z");

    private static final Symbol I_ENC = Tokens.app2(IOTA, IOTA);
    private static final Symbol K_ENC = Tokens.app2(IOTA, Tokens.app2(IOTA, Tokens.app2(IOTA, IOTA)));
    private static final Symbol S_ENC = Tokens.app2(IOTA,
            Tokens.app2(IOTA, Tokens.app2(IOTA, Tokens.app2(IOTA, IOTA))));

    private static final List<String[]> CASES = new ArrayList<>();
    private static final List<String> GROUPS = new ArrayList<>();

    static {
        // ---- Group A: the cases recorded in iota-lang SKITest, term and expectation.
        add("A", "testXY", Tokens.app2(X, Y), "(x y)");
        add("A", "testI", Tokens.app2(I, X), "x");
        add("A", "testK", Tokens.app(K, X, Y), "x");
        add("A", "testS", Tokens.app(S, X, Y, Z), "((x z) (y z))");
        add("A", "testFalse", Tokens.app(S, K, X, Y), "y");
        add("A", "testReverse", Tokens.app(Tokens.app2(S, Tokens.app2(K, Tokens.app2(S, I))), K, X, Y),
                "(y x)");
        add("A", "testKSKS", Tokens.app(K, S, K, S), "(s s)");
        add("A", "testKKKSKS", Tokens.app(Tokens.app2(K, K), K, S, K, S), "(s s)");
        add("A", "testSKK", Tokens.app(Tokens.app2(S, K), K, X, Y), "(x y)");
        add("A", "testIota2", Tokens.app2(I_ENC, X), "x");
        add("A", "testIota4", Tokens.app2(K_ENC, Tokens.app2(X, Y)), "x");
        add("A", "testIota5", Tokens.app2(S_ENC, Tokens.app(X, Y, Z)), "((x z) (y z))");
        // The five (h h h) cases share one term in the recorded file and assert
        // five different expect-strings; the term below is the recorded one.
        add("A", "testII", Tokens.app2(I_ENC, I_ENC), "(i i)");
        add("A", "testIII", Tokens.app2(I_ENC, I_ENC), "((i i) i)");
        add("A", "testIIII", Tokens.app2(I_ENC, I_ENC), "((i i) (i i))");
        add("A", "testIIIII", Tokens.app2(I_ENC, I_ENC), "(((i i) (i i)) i)");
        add("A", "testIIIIII", Tokens.app2(I_ENC, I_ENC), "(((i i) (i i)) (i i))");

        // ---- Group B: the space frame is ordered and headless.
        add("B", "spaceEmpty", Tokens.space(), "[]");
        add("B", "spaceAtom", Tokens.space(X), "[x]");
        add("B", "spaceOrder", Tokens.space(Z, Y, X), "[z y x]");
        add("B", "spaceEval", Tokens.space(Tokens.app2(I, X)), "[x]");
        add("B", "spaceNested", Tokens.space(X, Tokens.space(Y, Z)), "[x [y z]]");
        add("B", "spaceDoesNotReduce", Tokens.space(K, X, Y), "[k x y]");

        // ---- Group C: mixed nesting.
        add("C", "spaceOfTimes", Tokens.space(Tokens.app(K, X, Y), Tokens.app2(I, Z)), "[x z]");
        add("C", "timeOfSpaces", Tokens.app2(Tokens.space(X, Y), Z), null);
        add("C", "timeOfSpaceHead", Tokens.app(Tokens.space(X), Y, Z), null);

        // ---- Group D: the angle form is refused, never evaluated.
        addSource("D", "angleTop", "<a b>");
        addSource("D", "angleNested", "(i <a b>)");
        addSource("D", "angleInSpace", "[<a b>]");
    }

    private static void add(String group, String name, Symbol term, String expected) {
        CASES.add(new String[] { group, name, term.toString(), expected });
        GROUPS.add(group);
    }

    /** A case whose source text is the angle form, which cannot be constructed. */
    private static void addSource(String group, String name, String source) {
        CASES.add(new String[] { group, name, source, null });
        GROUPS.add(group);
    }

    public static void main(String[] args) {
        int passed = 0;
        int total = 0;
        for (String[] row : CASES) {
            String group = row[0];
            String name = row[1];
            String source = row[2];
            String expected = row[3];
            Map<String, Object> out = evaluate(group, name, source, expected);
            total++;
            if (Boolean.TRUE.equals(out.get("pass"))) {
                passed++;
            }
            System.out.println(json(out));
        }
        Map<String, Object> summary = new LinkedHashMap<>();
        summary.put("kind", "summary");
        summary.put("cases", total);
        summary.put("passed", passed);
        summary.put("failed", total - passed);
        System.out.println(json(summary));
        System.exit(passed == total ? 0 : 1);
    }

    private static Map<String, Object> evaluate(String group, String name, String source, String expected) {
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("kind", "case");
        out.put("group", group);
        out.put("name", name);
        out.put("term", source);
        out.put("expected", expected);

        try {
            Symbol term = Reader.read(source);
            Machine machine = new Machine();
            List<Symbol> results = machine.run(term);
            String value = render(results);
            out.put("results", value);
            out.put("arity", results.size());
            out.put("steps", machine.steps());
            out.put("pass", expected != null && expected.equals(value));
            return out;
        } catch (Refusal e) {
            out.put("refused", e.getMessage());
            return out;
        } catch (Stall | Budget e) {
            out.put("stopped", e.getMessage());
            return out;
        }
    }

    /** The canonical rendering of a read-out: a single term, or a space frame. */
    private static String render(List<Symbol> results) {
        if (results.size() == 1) {
            return results.get(0).toString();
        }
        return Tokens.space(results).toString();
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
            Object v = e.getValue();
            if (v == null) {
                sb.append("null");
            } else if (v instanceof Number || v instanceof Boolean) {
                sb.append(v);
            } else {
                sb.append('"').append(String.valueOf(v).replace("\\", "\\\\").replace("\"", "\\\""))
                        .append('"');
            }
        }
        return sb.append('}').toString();
    }
}
