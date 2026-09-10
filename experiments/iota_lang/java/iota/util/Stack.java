package iota.util;

public abstract class Stack<T> {

    protected int index = 0;
    protected Node<T> head = build(null);
    protected Node<T> tail = head;

    abstract Node<T> build(T val);

    public void push(T elem) {
        tail.next(build(elem));
        tail.next().previous(tail);
        tail = tail.next();
        index++;
    }

    public T pop() {
        if (index == 0) {
            throw new IllegalStateException("pop from empty stack");
        }
        T val = tail.value();
        tail = tail.previous();
        tail.next(null);
        index--;
        return val;
    }

    public T peek() {
        if (index == 0) {
            throw new IllegalStateException("peek on empty stack");
        }
        return tail.value();
    }

    public T ppeek() {
        if (index < 2) {
            throw new IllegalStateException("ppeek on stack of depth " + index);
        }
        return tail.previous().value();
    }

    public T pppeek() {
        if (index < 3) {
            throw new IllegalStateException("pppeek on stack of depth " + index);
        }
        return tail.previous().previous().value();
    }

    public int len() {
        return index;
    }

    public void clear() {
        while (this.len() != 0) {
            this.pop();
        }
    }

    /** Bottom-to-top token rendering, so a state string is comparable. */
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        for (Node<T> node = head.next(); node != null; node = node.next()) {
            sb.append(node.value());
        }
        return sb.toString();
    }
}
