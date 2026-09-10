package iota.util;

public class LNode<T> implements Node<T> {
    protected Node<T> parent;
    protected Node<T> right;
    protected T left;

    public LNode(T left) {
        this.left = left;
    }

    @Override
    public T value() {
        return left;
    }

    @Override
    public Node<T> previous() {
        return parent;
    }

    @Override
    public Node<T> next() {
        return right;
    }

    @Override
    public void value(T val) {
        left = val;
    }

    @Override
    public void previous(Node<T> node) {
        parent = node;
    }

    @Override
    public void next(Node<T> node) {
        right = node;
    }
}
