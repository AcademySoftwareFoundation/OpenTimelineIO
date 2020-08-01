package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;
import io.opentimeline.OTIOObject;

import java.util.*;

public class AnyVector extends OTIOObject implements Collection<Any> {

    public AnyVector() {
        this.initObject();
    }

    AnyVector(OTIONative otioNative) {
        this.nativeManager = otioNative;
    }

    private void initObject() {
        this.initialize();
        this.nativeManager.className = this.getClass().getCanonicalName();
    }

    private native void initialize();

    public class Iterator extends OTIOObject implements java.util.Iterator<Any> {
        private boolean startedIterating = false;

        private Iterator(AnyVector anyVector) {
            this.initObject(anyVector);
        }

        Iterator(OTIONative otioNative) {
            this.nativeManager = otioNative;
        }

        private void initObject(AnyVector anyVector) {
            this.initialize(anyVector);
            this.nativeManager.className = this.getClass().getCanonicalName();
        }

        private native void initialize(AnyVector anyVector);

        public boolean hasNext() {
            if (!startedIterating && size() > 0) return true;
            return hasNextNative(AnyVector.this);
        }

        public boolean hasPrevious() {
            return hasPreviousNative(AnyVector.this);
        }

        public Any next() {
            startedIterating = true;
            return nextNative(AnyVector.this);
        }

        public Any previous() {
            return previousNative(AnyVector.this);
        }

        private native Any nextNative(AnyVector anyVector);

        private native Any previousNative(AnyVector anyVector);

        private native boolean hasNextNative(AnyVector anyVector);

        private native boolean hasPreviousNative(AnyVector anyVector);
    }

    public AnyVector.Iterator iterator() {
        return new AnyVector.Iterator(this);
    }

    @Override
    public Object[] toArray() {
        return getArray();
    }

    @Override
    public <T> T[] toArray(T[] ts) {
        if (ts instanceof Any[])
            return (T[]) getArray();
        throw new ClassCastException();
    }

    private native Any[] getArray();

    public native Any get(int index);

    public native boolean add(Any any);

    @Override
    public boolean remove(Object o) {
        if (!(o instanceof Any))
            return false;
        int index = -1;
        for (int i = 0; i < size(); i++) {
            if (get(i).equals((Any) o)) {
                index = i;
                break;
            }
        }
        if (index >= 0) {
            remove(index);
            return true;
        }
        return false;
    }

    @Override
    public boolean containsAll(Collection<?> collection) {
        if (collection.size() > size())
            return false;
        for (Object o : collection) {
            if (!(o instanceof Any) || !contains(o))
                return false;
        }
        return true;
    }

    @Override
    public boolean addAll(Collection<? extends Any> collection) {
        for (Any any : collection) {
            add(any);
        }
        return true;
    }

    @Override
    public boolean removeAll(Collection<?> collection) {
        boolean vectorChanged = false;
        for (Object o : collection) {
            if (!(o instanceof Any))
                continue;
            vectorChanged = remove(o);
        }
        return vectorChanged;
    }

    @Override
    public boolean retainAll(Collection<?> collection) {
        TreeSet<Integer> indicesSet = new TreeSet<>(Collections.reverseOrder());

        for (int i = 0; i < size(); i++) {
            Any any = get(i);
            boolean removeIndex = true;
            for (Object o : collection) {
                if ((o instanceof Any) && ((Any) o).equals(any)) {
                    removeIndex = false;
                    break;
                }
            }
            if (removeIndex) indicesSet.add(i);
        }

        for (int index : indicesSet) {
            System.out.println(index);
            remove(index);
        }
        return indicesSet.size() > 0;
    }

    public native boolean add(int index, Any any);

    public native void clear();

    public native void ensureCapacity(int minCapacity);

    public native int size();

    public boolean isEmpty() {
        return size() == 0;
    }

    @Override
    public boolean contains(Object o) {
        if (!(o instanceof Any)) return false;

        for (int i = 0; i < size(); i++) {
            if (get(i).equals((Any) o))
                return true;
        }
        return false;

    }

    public native void remove(int index);

    public native void trimToSize();

    public boolean equals(AnyVector anyVector) {
        if (size() != anyVector.size()) return false;
        for (int i = 0; i < size(); i++) {
            Any thisAny = get(i);
            Any otherAny = anyVector.get(i);
            if (!thisAny.equals(otherAny))
                return false;
        }
        return true;
    }
}
