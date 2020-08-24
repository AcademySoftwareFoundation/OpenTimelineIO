package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;
import io.opentimeline.opentime.TimeRange;

import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * A kind of composition which can hold any serializable object.
 * This composition approximates the concept of a `bin` - a collection of
 * SerializableObjects that do not have any compositing meaning, but can
 * serialize to/from OTIO correctly, with metadata and a named collection.
 */
public class SerializableCollection extends SerializableObjectWithMetadata {

    protected SerializableCollection() {
    }

    SerializableCollection(OTIONative otioNative) {
        this.nativeManager = otioNative;
    }

    public SerializableCollection(
            String name,
            List<SerializableObject> children,
            AnyDictionary metadata) {
        this.initObject(name, children, metadata);
    }

    public SerializableCollection(SerializableCollectionBuilder serializableCollectionBuilder) {
        this.initObject(
                serializableCollectionBuilder.name,
                serializableCollectionBuilder.children,
                serializableCollectionBuilder.metadata);
    }

    private void initObject(String name, List<SerializableObject> children, AnyDictionary metadata) {
        SerializableObject[] serializableObjects = new SerializableObject[children.size()];
        serializableObjects = children.toArray(serializableObjects);
        this.initialize(name, serializableObjects, metadata);
        this.nativeManager.className = this.getClass().getCanonicalName();
    }

    private native void initialize(String name, SerializableObject[] children, AnyDictionary metadata);

    public static class SerializableCollectionBuilder {
        private String name = "";
        private List<SerializableObject> children = new ArrayList<>();
        private AnyDictionary metadata = new AnyDictionary();

        public SerializableCollectionBuilder() {
        }

        public SerializableCollection.SerializableCollectionBuilder setName(String name) {
            this.name = name;
            return this;
        }

        public SerializableCollection.SerializableCollectionBuilder setMetadata(AnyDictionary metadata) {
            this.metadata = metadata;
            return this;
        }

        public SerializableCollection.SerializableCollectionBuilder setChildren(
                List<SerializableObject> children) {
            this.children = children;
            return this;
        }

        public SerializableCollection build() {
            return new SerializableCollection(this);
        }
    }

    public List<SerializableObject> getChildren() {
        return Arrays.asList(getChildrenNative());
    }

    private native SerializableObject[] getChildrenNative();

    public void setChildren(List<SerializableObject> children) {
        setChildrenNative((SerializableObject[]) children.toArray());
    }

    private native void setChildrenNative(SerializableObject[] children);

    public native void clearChildren();

    public native boolean setChild(int index, SerializableObject child, ErrorStatus errorStatus);

    public native void insertChild(int index, SerializableObject child);

    public native boolean removeChild(int index, ErrorStatus errorStatus);

    public <T extends Composable> Stream<T> eachChild(
            TimeRange searchRange, Class<T> descendedFrom, ErrorStatus errorStatus) {
        List<SerializableObject> children = this.getChildren();
        return children.stream()
                .flatMap(element -> {
                            Stream<T> currentElementStream = Stream.empty();
                            if (descendedFrom.isAssignableFrom(element.getClass()))
                                currentElementStream = Stream.concat(Stream.of(descendedFrom.cast(element)), currentElementStream);
                            Stream<T> nestedStream = Stream.empty();
                            if (element instanceof Composition) {
                                nestedStream = ((Composition) element).eachChild(
                                        searchRange,
                                        descendedFrom,
                                        false,
                                        errorStatus);
                            }
                            return Stream.concat(currentElementStream, nestedStream);
                        }
                );
    }

    public Stream<Clip> eachClip(
            TimeRange searchRange, ErrorStatus errorStatus) {
        return this.eachChild(searchRange, Clip.class, errorStatus);
    }

    @Override
    public String toString() {
        return this.getClass().getCanonicalName() +
                "(" +
                "name=" + this.getName() +
                ", children=[" + this.getChildren()
                .stream().map(Objects::toString).collect(Collectors.joining(", ")) + "]" +
                ", metadata=" + this.getMetadata().toString() +
                ")";
    }
}
