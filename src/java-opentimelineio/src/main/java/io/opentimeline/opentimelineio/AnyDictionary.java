package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;
import io.opentimeline.OTIOObject;

import java.util.*;
import java.util.function.BiConsumer;

public class AnyDictionary extends OTIOObject implements Map<String, Any> {

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

    public static class AnyEntry implements Entry<String, Any> {
        private String key = null;
        private Any value = null;

        private AnyEntry(String key, Any value) {
            this.key = key;
            this.value = value;
        }

        @Override
        public String getKey() {
            return key;
        }

        @Override
        public Any getValue() {
            return value;
        }

        @Override
        public Any setValue(Any any) {
            Any oldAny = value;
            value = any;
            return oldAny;
        }
    }

    public class Iterator extends OTIOObject implements java.util.Iterator<AnyEntry> {

        private boolean startedIterating = false;

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
            if (!startedIterating && size() > 0) return true;
            return hasNextNative(AnyDictionary.this);
        }

        public boolean hasPrevious() {
            return hasPreviousNative(AnyDictionary.this);
        }

        public AnyDictionary.AnyEntry next() {
            if (!startedIterating) {
                startedIterating = true;
                return new AnyEntry(getKey(), getValue());
            }
            if (!hasNext()) {
                throw new NoSuchElementException();
            }
            nextNative();
            return new AnyEntry(getKey(), getValue());
        }

        public AnyDictionary.AnyEntry previous() {
            if (!hasPrevious()) {
                throw new NoSuchElementException();
            }
            previousNative();
            return new AnyEntry(getKey(), getValue());
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

    @Override
    public Any remove(Object o) {
        return null;
    }

    @Override
    public void putAll(Map<? extends String, ? extends Any> map) {

    }

    /**
     * The previous value associated with the key is returned.
     * null is returned if no such key is mapped.
     */
    public native Any replace(String key, Any value);

    public boolean isEmpty() {
        return size() == 0;
    }

    @Override
    public boolean containsKey(Object o) {
        if (o instanceof String)
            return containsKey((String) o);
        return false;
    }

    @Override
    public boolean containsValue(Object o) {
        return false;
    }

    @Override
    public Any get(Object o) {
        if (o instanceof String)
            return get((String) o);
        return null;
    }

    public native int size();

    public native void clear();

    @Override
    public Set<String> keySet() {
        Set<String> keys = new HashSet<>();
        Iterator iterator = iterator();
        while (iterator.hasNext()) {
            AnyEntry element = iterator.next();
            keys.add(element.getKey());
        }
//        try {
//            iterator.getNativeManager().close();
//        } catch (Exception e) {
//            e.printStackTrace();
//        }
        return keys;
    }

    @Override
    public Collection<Any> values() {
        AnyVector anyVector = new AnyVector();
        Iterator iterator = iterator();
        while (iterator.hasNext()) {
            AnyEntry element = iterator.next();
            anyVector.add(element.getValue());
        }
//        try {
//            iterator.getNativeManager().close();
//        } catch (Exception e) {
//            e.printStackTrace();
//        }
        return anyVector;
    }

    @Override
    public Set<Entry<String, Any>> entrySet() {
        Set<Entry<String, Any>> elements = new HashSet<>();
        Iterator iterator = iterator();
        while (iterator.hasNext()) {
            elements.add(iterator.next());
        }
//        try {
//            iterator.getNativeManager().close();
//        } catch (Exception e) {
//            e.printStackTrace();
//        }
        return elements;
    }

    @Override
    public void forEach(BiConsumer<? super String, ? super Any> action) {
        Iterator iterator = iterator();
        while (iterator.hasNext()) {
            AnyEntry anyEntry = iterator.next();
            action.accept(anyEntry.getKey(), anyEntry.getValue());
        }
//        try {
//            iterator.getNativeManager().close();
//        } catch (Exception e) {
//            e.printStackTrace();
//        }
    }

    public native int remove(String key);

    public boolean equals(AnyDictionary anyDictionary) {
//        System.out.println(size() + " " + anyDictionary.size());
        if (size() != anyDictionary.size()) return false;

        Iterator thisIterator = iterator();
        Iterator otherIterator = anyDictionary.iterator();

        while (thisIterator.hasNext() && otherIterator.hasNext()) {
            AnyEntry thisElement = thisIterator.next();
            AnyEntry otherElement = otherIterator.next();
//            System.out.println(thisElement.key + " " + otherElement.key);
//            System.out.println(thisElement.getValue().getAnyTypeClass() + " " + otherElement.getValue().getAnyTypeClass());
            if (!(thisElement.key.equals(otherElement.key))
                    || !thisElement.value.equals(otherElement.value))
                return false;
        }
        return true;
    }

    @Override
    public boolean equals(Object obj) {
        if (!(obj instanceof AnyDictionary))
            return false;
        return this.equals((AnyDictionary) obj);
    }

    @Override
    public String toString() {
        StringBuilder values = new StringBuilder();
        String delimiterPrefix = "";
        Iterator thisIterator = iterator();
        while (thisIterator.hasNext()) {
            AnyEntry thisElement = thisIterator.next();
            values.append(delimiterPrefix).append(thisElement.getKey()).append("=").append(thisElement.getValue());
            delimiterPrefix = ", ";
        }
        return this.getClass().getCanonicalName() +
                "{" +
                values.toString() +
                "}";
    }
}
