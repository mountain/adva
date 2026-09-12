package iota;

/**
 * Reconnection note (adva research 0167): the recorded `iota.Symbol` declares
 * only `symbolize`, while every rule of the machine reads `lpeek().value()`.
 * `value()` is the token's own identity carrier; `Symbols` keeps exactly one
 * instance per token so `==` is a stable identity comparison.
 */
public interface Symbol {

    Symbol value();

    static Symbol symbolize(String name) {
        return Symbols.symbolize(name);
    }
}
