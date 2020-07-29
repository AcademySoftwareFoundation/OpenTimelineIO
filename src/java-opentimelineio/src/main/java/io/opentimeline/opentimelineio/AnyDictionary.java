package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;
import io.opentimeline.OTIOObject;

import java.util.NoSuchElementException;

public class AnyDictionary extends OTIOObject {

    public AnyDictionary() {
        this.initObject();
    }

    AnyDictionary(OTIONative otioNative) {
        this.nativeManager = otioNative;
    }

    private void initObject() {
        this.initialize();
        this.nativeManager.className = this.getClass().getCanonicalName();
    }

    private native void initialize();

    public static class Element {
        public String key;
        public Any value;

        private Element(String key, Any value) {
            this.key = key;
            this.value = value;
        }
    }

    public class Iterator extends OTIOObject {

        private Iterator(AnyDictionary anyDictionary) {
            this.initObject(anyDictionary);
        }

        Iterator(OTIONative otioNative) {
            this.nativeManager = otioNative;
        }

        private void initObject(AnyDictionary anyDictionary) {
            this.initialize(anyDictionary);
            this.nativeManager.className = this.getClass().getCanonicalName();
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
}
