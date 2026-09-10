package iota.dual;

import java.util.List;

/**
 * The reduction rules: they exist for time frames only.
 *
 * Each rule fires on the pending head in the work stack and reads its arguments
 * from the space stack, first argument on top. That is the convention the
 * recorded rules already assume; the only thing that changes here is that the
 * arguments really are all present, because the spine was flattened when it was
 * read.
 *
 * A space frame has no rule: `[]` orders and collects, it never rewrites.
 */
final class Reductions {

    private Reductions() {
    }

    /**
     * Applies the rule for the pending head, if any.
     *
     * @return true when a rule fired
     */
    static boolean time(Symbol head, List<Symbol> work, List<Symbol> space) {
        if (head == Tokens.I) {
            if (space.size() < 1) {
                return false;
            }
            work.remove(work.size() - 1);
            work.add(space.remove(space.size() - 1));
            return true;
        }
        if (head == Tokens.K) {
            if (space.size() < 2) {
                return false;
            }
            work.remove(work.size() - 1);
            space.remove(space.size() - 1);
            work.add(space.remove(space.size() - 1));
            return true;
        }
        if (head == Tokens.S) {
            if (space.size() < 3) {
                return false;
            }
            work.remove(work.size() - 1);
            Symbol third = space.remove(space.size() - 1);
            Symbol second = space.remove(space.size() - 1);
            Symbol first = space.remove(space.size() - 1);
            // S x y z  =>  ((x z) (y z)). Both parts are pending applications,
            // so they are staged as terms for the enclosing frame to evaluate.
            space.add(new Syntax.App(second, third));
            space.add(new Syntax.App(first, third));
            work.add(first);
            return true;
        }
        if (head == Tokens.IOTA) {
            if (space.size() < 1) {
                return false;
            }
            // iota x  =>  x S K.
            work.remove(work.size() - 1);
            Symbol x = space.remove(space.size() - 1);
            space.add(Tokens.K);
            space.add(Tokens.S);
            work.add(x);
            return true;
        }
        return false;
    }
}
