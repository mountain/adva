package iota.util;

public class RNode<T> implements Node<T> {
    protected Node<T> parent;
    protected Node<T> left;
    protected T right;

    public RNode(T elem) {
        this.right = elem;
    }

    @Override
    public T value() {
        return right;
    }

    @Override
    public Node<T> previous() {
        return parent;
    }

    @Override
    public Node<T> next() {
        return left;
    }

    @Override
    public void value(T val) {
        right = val;
    }

    @Override
    public void previous(Node<T> node) {
        parent = node;
    }

    @Override
    public void next(Node<T> node) {
        left = node;
    }
}
