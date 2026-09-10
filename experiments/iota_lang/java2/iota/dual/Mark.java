package iota.dual;

/** Frame markers on the work stack. Never produced by the reader. */
public final class Mark implements Symbol {

    public enum Kind {
        /** Push what the next head produces into the innermost continuation. */
        RETURN
    }

    public final Kind kind;

    Mark(Kind kind) {
        this.kind = kind;
    }

    static Mark ret() {
        return new Mark(Kind.RETURN);
    }

    @Override
    public Symbol value() {
        return this;
    }

    @Override
    public String toString() {
        return "\u21a9";
    }
}
