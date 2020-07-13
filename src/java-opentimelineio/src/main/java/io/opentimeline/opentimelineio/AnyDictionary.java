package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;

import java.util.NoSuchElementException;

public class AnyDictionary extends OTIONative {

    public AnyDictionary() {
        this.initialize();
    }

    public AnyDictionary(long nativeHandle) {
        this.nativeHandle = nativeHandle;
    }

    private native void initialize();

    public class Iterator extends OTIONative {

        private Iterator(AnyDictionary anyDictionary) {
            this.initialize(anyDictionary);
        }

        public Iterator(long nativeHandle) {
            this.nativeHandle = nativeHandle;
        }

        private native void initialize(AnyDictionary anyDictionary);

        public boolean hasNext() {
            return hasNextNative(AnyDictionary.this);
        }

        public boolean hasPrevious() {
            return hasPreviousNative(AnyDictionary.this);
        }

        public AnyDictionary.Iterator next() {
            if (!hasNext()) {
                throw new NoSuchElementException();
            }
            return nextNative();
        }

        public AnyDictionary.Iterator previous() {
            if (!hasPrevious()) {
                throw new NoSuchElementException();
            }
            return previousNative();
        }

        public native AnyDictionary.Iterator nextNative();

        public native AnyDictionary.Iterator previousNative();

        private native boolean hasNextNative(AnyDictionary anyDictionary);

        public native boolean hasPreviousNative(AnyDictionary anyDictionary);

        public native String getKey();

        public native Any getValue();

        private native void dispose();

        @Override
        protected void finalize() throws Throwable {
            dispose();
        }
    }

    public AnyDictionary.Iterator iterator() {
        return new AnyDictionary.Iterator(this);
    }

    public boolean containsKey(String key) {
        if (key == null) throw new NullPointerException();
        return containsKeyNative(key);
    }

    public Any get(String key) {
        if (!containsKey(key)) throw new NoSuchElementException();
        return getNative(key);
    }

    /**
     * The previous value is returned, if an existing key is passed.
     * null is returned, if a new pair is passed.
     */
    public Any put(String key, Any value) {
        if (key == null || value == null) throw new NullPointerException();
        return putNative(key, value);
    }

    /**
     * The previous value associated with the key is returned.
     * null is returned if no such key is mapped.
     */
    public Any replace(String key, Any value) {
        if (key == null || value == null) throw new NullPointerException();
        return replaceNative(key, value);
    }

    public boolean isEmpty() {
        return size() == 0;
    }

    public native boolean containsKeyNative(String key);

    public native Any getNative(String key);

    public native int size();

    public native Any putNative(String key, Any value);

    public native Any replaceNative(String key, Any value);

    public native void clear();

    public native int remove(String key);

    private native void dispose();

    @Override
    protected void finalize() throws Throwable {
        dispose();
    }
}
