package iota.util;

public interface Node<T> {

    @FunctionalInterface
    interface NodeHandler<T> {
        void handle(Node<T> x);
    }

    static <T> void iterate(Node<T> head, NodeHandler<T> handler) {
        Node<T> ptr = head;
        while (ptr != null) {
            if (ptr.value() != null) {
                handler.handle(ptr);
            }
            ptr = ptr.next();
        }
    }

    static <T> void reverse(Node<T> tail, NodeHandler<T> handler) {
        Node<T> ptr = tail;
        while (ptr != null) {
            if (ptr.value() != null) {
                handler.handle(ptr);
            }
            ptr = ptr.previous();
        }
    }

    T value();
    Node<T> previous();
    Node<T> next();
    void value(T val);
    void previous(Node<T> node);
    void next(Node<T> node);
}
