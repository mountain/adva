package iota.dual;

import java.util.ArrayList;
import java.util.List;

/**
 * DualMachine version 0.
 *
 * One work stack (time), one argument stack (space, the read-out), one frame
 * stack. Two regimes. See DUALMACHINE.md.
 *
 * - `(a b)` is a time frame: the head is applied to its arguments.
 * - `[a b c]` is a space frame: the elements form one ordered family. No rule
 *   consumes a space frame, so its elements are never dependent.
 * - `<L R>` is refused: it is a judgement over a typed middle object, not a
 *   term, so it has no normal form to reduce to.
 *
 * Reading. An application's spine is flattened when it is read: `(a b c)`
 * becomes the head `a` with arguments `b`, `c`. The head is the only pending
 * item; its arguments wait on the space stack, first argument on top, which is
 * the convention the recorded reduction rules already assume.
 *
 * Frames. A frame records the space-stack depth it opened at, so a closing
 * frame takes exactly the values produced above that depth and collapses them
 * into the single term it denotes. Ownership delimits a frame; a shared stack
 * alone cannot say whose argument is whose.
 */
public final class Machine {

    /** No rule applies and no head is pending. Reported, never a value. */
    public static final class Stall extends RuntimeException {
        public Stall(String message) {
            super(message);
        }
    }

    /** The step budget is exhausted. */
    public static final class Budget extends RuntimeException {
        public Budget(String message) {
            super(message);
        }
    }

    /** A recorded reason why a term was refused rather than evaluated. */
    public static final class Refusal extends RuntimeException {
        public Refusal(String message) {
            super(message);
        }
    }

    /** Time: pending heads. Top of stack is the head to reduce next. */
    private final List<Symbol> work = new ArrayList<>();
    /** Space: arguments, and the read-out. Top of stack is the first argument. */
    private final List<Symbol> space = new ArrayList<>();
    /** Frames, outermost first. */
    private final List<Frame> frames = new ArrayList<>();

    private boolean verbose = false;
    private long steps = 0L;
    private long budget = 100_000L;
    private String lastFired = "";

    public void setVerbose(boolean verbose) {
        this.verbose = verbose;
    }

    public long steps() {
        return steps;
    }

    public String state() {
        return show() + " frames:" + frames;
    }

    private String show() {
        StringBuilder sb = new StringBuilder();
        for (int i = work.size() - 1; i >= 0; i--) {
            sb.append(work.get(i));
        }
        sb.append('|');
        for (int i = 0; i < space.size(); i++) {
            sb.append(space.get(i));
        }
        return sb.toString();
    }

    public List<Symbol> results() {
        return List.copyOf(space);
    }

    /** Runs to a read-out and returns the ordered family. */
    public List<Symbol> run(Symbol program) {
        work.clear();
        space.clear();
        frames.clear();
        steps = 0L;
        work.add(program);
        while (!work.isEmpty()) {
            if (steps >= budget) {
                throw new Budget("step budget " + budget + " exhausted at " + state());
            }
            step();
            steps++;
            if (verbose) {
                System.out.println(steps + "  " + lastFired + "  " + state());
            }
        }
        return List.copyOf(space);
    }

    /** Runs exactly one round. */
    public void step() {
        lastFired = "";
        Symbol head = work.get(work.size() - 1);

        if (head instanceof Syntax.Angle) {
            throw new Refusal(refuseAngle((Syntax.Angle) head));
        }
        if (head instanceof Syntax.App) {
            work.remove(work.size() - 1);
            readApplication((Syntax.App) head);
            return;
        }
        if (head instanceof Syntax.Space) {
            work.remove(work.size() - 1);
            readSpace((Syntax.Space) head);
            return;
        }
        if (Reductions.time(head, work, space)) {
            lastFired = head + "-rule";
            // The reduced head is pending again; settle only when it is a value.
            if (!work.isEmpty() && !isRuleHead(work.get(work.size() - 1))) {
                Symbol value = work.remove(work.size() - 1);
                space.add(value);
                settle();
            }
            return;
        }
        // No rule applies, so this head is finished: it is a value.
        work.remove(work.size() - 1);
        space.add(head);
        lastFired = "value";
        settle();
    }

    /**
     * Flattens an application spine: `(a b c)` is the head `a` with arguments
     * `b` and `c`. The arguments are pushed in reverse so the first one sits on
     * top of the space stack, and the head becomes the only pending item.
     */
    private void readApplication(Syntax.App app) {
        List<Symbol> args = new ArrayList<>();
        Symbol head = app.head;
        args.add(app.operand);
        while (head instanceof Syntax.App) {
            Syntax.App inner = (Syntax.App) head;
            args.add(inner.operand);
            head = inner.head;
        }
        frames.add(new Frame(Frame.Then.APP, space.size(), args.size()));
        for (int i = args.size() - 1; i >= 0; i--) {
            space.add(args.get(i));
        }
        work.add(head);
        lastFired = "app";
        // A head that is already a value needs no reduction; it settles now.
        if (!(head instanceof Syntax.App) && !isRuleHead(head)) {
            work.remove(work.size() - 1);
            frames.get(frames.size() - 1).head = head;
            settle();
        }
    }

    /** A space frame: every element is pending; the frame collects them. */
    private void readSpace(Syntax.Space s) {
        frames.add(new Frame(Frame.Then.SPACE, space.size(), s.elements.size()));
        for (int i = s.elements.size() - 1; i >= 0; i--) {
            work.add(s.elements.get(i));
        }
        lastFired = "space";
    }

    /**
     * A value was produced. Every enclosing frame whose arguments are now all
     * present collapses, innermost first, and each collapse produces a value for
     * the frame above it.
     */
    private void settle() {
        while (!frames.isEmpty()) {
            Frame frame = frames.get(frames.size() - 1);
            if (space.size() < frame.base + frame.arity) {
                return;
            }
            frames.remove(frames.size() - 1);
            List<Symbol> parts = new ArrayList<>();
            while (space.size() > frame.base) {
                parts.add(0, space.remove(space.size() - 1));
            }
            if (frame.then == Frame.Then.SPACE) {
                space.add(Tokens.space(parts));
                lastFired = "frame-space";
            } else {
                if (frame.head == null) {
                    // The head is the bottom part; the rest are its arguments.
                    frame.head = parts.get(0);
                    parts = new ArrayList<>(parts.subList(1, parts.size()));
                }
                if (frame.head instanceof Syntax.Space) {
                    throw new Stall("space frame in head position: " + frame.head
                            + " applied to " + parts + " at " + state()
                            + "; giving [] a head-consuming behaviour would make it a third"
                            + " reduction mechanism (DUALMACHINE.md section 6)");
                }
                space.add(parts.isEmpty() ? frame.head
                        : Tokens.app(frame.head, parts.toArray(new Symbol[0])));
                lastFired = "frame-app";
            }
        }
    }

    private static boolean isRuleHead(Symbol term) {
        return term == Tokens.I || term == Tokens.K || term == Tokens.S || term == Tokens.IOTA;
    }

    private String refuseAngle(Syntax.Angle angle) {
        return "refused " + angle + ": the angle form is a judgement over a typed singular"
                + " middle object (research 0070), not a term; it needs a middle N_D, two pinch"
                + " maps, an observer policy Q, a version v and a resolution rho, none of which"
                + " DualMachine v0 has. It is not evaluated, not reduced and not a stuck term."
                + " See DUALMACHINE.md section 7";
    }
}
