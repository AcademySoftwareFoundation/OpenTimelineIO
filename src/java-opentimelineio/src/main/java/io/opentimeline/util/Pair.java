package io.opentimeline.util;

public class Pair<T, U> {
    private T first;
    private U second;

    public Pair(T first, U second) {
        this.first = first;
        this.second = second;
    }

    public T getFirst() {
        return first;
    }

    public U getSecond() {
        return second;
    }

    @Override
    public boolean equals(Object obj) {
        if (!(obj instanceof Pair))
            return false;
        boolean firstEqual =
                (((Pair<T, U>) obj).getFirst() == null && ((Pair<T, U>) obj).getFirst() == null) ||
                        ((Pair<T, U>) obj).getFirst().equals(this.getFirst());
        boolean secondEqual =
                (((Pair<T, U>) obj).getSecond() == null && ((Pair<T, U>) obj).getSecond() == null) ||
                        ((Pair<T, U>) obj).getSecond().equals(this.getSecond());
        return firstEqual && secondEqual;
    }
}