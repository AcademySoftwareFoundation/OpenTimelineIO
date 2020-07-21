package io.opentimeline.util;

public class Triplet<T, U, V> {
    public T first;
    public U second;
    public V third;

    public Triplet(T first, U second, V third) {
        this.first = first;
        this.second = second;
        this.third = third;
    }
}
