package iota.dual;

import java.util.List;

/**
 * Reads the two construction forms and refuses the angle form.
 *
 *   (a b)      application, right-nested for more than two terms
 *   [a b c]    space frame, any arity including zero
 *   <a b>      refused at parse time with the reason recorded in DUALMACHINE.md
 */
public final class Reader {

    public static Symbol read(String text) {
        Cursor cursor = new Cursor(text);
        Symbol term = cursor.term();
        cursor.skipSpace();
        if (!cursor.done()) {
            throw new IllegalArgumentException("trailing input at " + cursor.pos() + " in " + text);
        }
        return term;
    }

    private static final class Cursor {

        private final String text;
        private int at = 0;

        Cursor(String text) {
            this.text = text;
        }

        int pos() {
            return at;
        }

        boolean done() {
            return at >= text.length();
        }

        void skipSpace() {
            while (at < text.length() && Character.isWhitespace(text.charAt(at))) {
                at++;
            }
        }

        private char peek() {
            if (done()) {
                throw new IllegalArgumentException("unexpected end of input");
            }
            return text.charAt(at);
        }

        private char next() {
            char c = peek();
            at++;
            return c;
        }

        Symbol term() {
            skipSpace();
            char c = peek();
            switch (c) {
                case '(':
                    next();
                    return application();
                case '[':
                    next();
                    return space();
                case '<':
                    next();
                    return angle();
                case ')':
                case ']':
                case '>':
                    throw new IllegalArgumentException("unexpected " + c + " at " + at);
                default:
                    return atom();
            }
        }

        private Symbol application() {
            Symbol head = term();
            Symbol operand = term();
            expect(')');
            return new Syntax.App(head, operand);
        }

        private Symbol space() {
            java.util.ArrayList<Symbol> elements = new java.util.ArrayList<>();
            skipSpace();
            if (peek() == ']') {
                next();
                return new Syntax.Space(elements);
            }
            while (true) {
                elements.add(term());
                skipSpace();
                if (peek() == ']') {
                    next();
                    return new Syntax.Space(List.copyOf(elements));
                }
            }
        }

        private Symbol angle() {
            Symbol left = term();
            Symbol right = term();
            expect('>');
            throw new Machine.Refusal("refused <" + left + " " + right + ">: the angle form is a"
                    + " judgement over a typed singular middle object (research 0070), not a term;"
                    + " DualMachine v0 has no middle N_D, pinch maps, observer policy or resolution,"
                    + " so the form is refused at parse time rather than evaluated."
                    + " See DUALMACHINE.md section 7");
        }

        private Symbol atom() {
            int start = at;
            while (at < text.length()) {
                char c = text.charAt(at);
                if (Character.isWhitespace(c) || c == '(' || c == ')' || c == '[' || c == ']'
                        || c == '<' || c == '>') {
                    break;
                }
                at++;
            }
            String name = text.substring(start, at);
            switch (name) {
                case "s":
                    return Tokens.S;
                case "k":
                    return Tokens.K;
                case "i":
                    return Tokens.I;
                case "\u03b9":
                    return Tokens.IOTA;
                default:
                    return Tokens.atom(name);
            }
        }

        private void expect(char c) {
            skipSpace();
            if (done() || peek() != c) {
                throw new IllegalArgumentException(
                        "expected " + c + " at " + at + " in " + text);
            }
            next();
        }
    }
}
