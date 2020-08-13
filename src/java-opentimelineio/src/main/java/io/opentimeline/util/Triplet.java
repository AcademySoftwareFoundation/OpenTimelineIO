package io.opentimeline.util;

public class Triplet<T, U, V> {
    private T first;
    private U second;
    private V third;

    public Triplet(T first, U second, V third) {
        this.first = first;
        this.second = second;
        this.third = third;
    }

    public T getFirst() {
        return first;
    }

    public U getSecond() {
        return second;
    }

    public V getThird() {
        return third;
    }

    @Override
    public boolean equals(Object obj) {
        if (!(obj instanceof Triplet))
            return false;
        boolean firstEqual =
                (((Triplet<T, U, V>) obj).getFirst() == null && ((Triplet<T, U, V>) obj).getFirst() == null) ||
                        ((Pair<T, U>) obj).getFirst().equals(this.getFirst());
        boolean secondEqual =
                (((Triplet<T, U, V>) obj).getSecond() == null && ((Triplet<T, U, V>) obj).getSecond() == null) ||
                        ((Triplet<T, U, V>) obj).getSecond().equals(this.getSecond());
        boolean thirdEqual =
                (((Triplet<T, U, V>) obj).getThird() == null && ((Triplet<T, U, V>) obj).getThird() == null) ||
                        ((Triplet<T, U, V>) obj).getThird().equals(this.getThird());
        return firstEqual && secondEqual && thirdEqual;
    }

    @Override
    public String toString() {
        return this.getClass().getCanonicalName() +
                "(" +
                "first=" + this.getFirst().toString() +
                ", second=" + this.getSecond().toString() +
                ", third=" + this.getThird().toString() +
                ")";
    }
}
