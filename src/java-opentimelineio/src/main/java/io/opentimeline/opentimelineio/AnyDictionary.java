package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;

import java.util.NoSuchElementException;

public class AnyDictionary extends OTIONative {

    public AnyDictionary() {
        this.initObject();
    }

    public AnyDictionary(long nativeHandle) {
        this.nativeHandle = nativeHandle;
    }

    private void initObject() {
        this.className = this.getClass().getCanonicalName();
        this.initialize();
    }

    private native void initialize();

    public class Element {
        public String key;
        public Any value;

        private Element(String key, Any value) {
            this.key = key;
            this.value = value;
        }
    }

    public class Iterator extends OTIONative {

        private Iterator(AnyDictionary anyDictionary) {
            this.initObject(anyDictionary);
        }

        public Iterator(long nativeHandle) {
            this.nativeHandle = nativeHandle;
        }

        private void initObject(AnyDictionary anyDictionary) {
            this.className = this.getClass().getCanonicalName();
            this.initialize(anyDictionary);
        }

        private native void initialize(AnyDictionary anyDictionary);

        public boolean hasNext() {
            return hasNextNative(AnyDictionary.this);
        }

        public boolean hasPrevious() {
            return hasPreviousNative(AnyDictionary.this);
        }

        public AnyDictionary.Element next() {
            if (!hasNext()) {
                throw new NoSuchElementException();
            }
            nextNative();
            return new Element(getKey(), getValue());
        }

        public AnyDictionary.Element previous() {
            if (!hasPrevious()) {
                throw new NoSuchElementException();
            }
            previousNative();
            return new Element(getKey(), getValue());
        }

        public native void nextNative();

        public native void previousNative();

        private native boolean hasNextNative(AnyDictionary anyDictionary);

        public native boolean hasPreviousNative(AnyDictionary anyDictionary);

        public native String getKey();

        public native Any getValue();

        private native void dispose();

        @Override
        public void close() throws Exception {
            dispose();
        }
    }

    public AnyDictionary.Iterator iterator() {
        return new AnyDictionary.Iterator(this);
    }

    public native boolean containsKey(String key);

    public native Any get(String key);

    /**
     * The previous value is returned, if an existing key is passed.
     * null is returned, if a new pair is passed.
     */
    public native Any put(String key, Any value);

    /**
     * The previous value associated with the key is returned.
     * null is returned if no such key is mapped.
     */
    public native Any replace(String key, Any value);

    public boolean isEmpty() {
        return size() == 0;
    }

    public native int size();

    public native void clear();

    public native int remove(String key);

    private native void dispose();

    @Override
    public void close() throws Exception {
        dispose();
    }
}
