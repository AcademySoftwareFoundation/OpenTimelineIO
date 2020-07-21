package io.opentimeline.opentimelineio;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class SerializableCollection extends SerializableObjectWithMetadata {

    protected SerializableCollection() {
    }

    public SerializableCollection(String name, List<SerializableObject> children, AnyDictionary metadata) {
        this.initObject(name, children, metadata);
    }

    public SerializableCollection(SerializableCollectionBuilder serializableCollectionBuilder) {
        this.initObject(
                serializableCollectionBuilder.name,
                serializableCollectionBuilder.children,
                serializableCollectionBuilder.metadata);
    }

    private void initObject(String name, List<SerializableObject> children, AnyDictionary metadata) {
        this.className = this.getClass().getCanonicalName();
        this.initialize(name, (SerializableObject[]) children.toArray(), metadata);
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

        public SerializableCollection.SerializableCollectionBuilder setMetadata(List<SerializableObject> children) {
            this.children = children;
            return this;
        }

        public SerializableCollection build() {
            return new SerializableCollection(this);
        }
    }

    public List<Retainer<SerializableObject>> getChildren() {
        return Arrays.asList(getChildrenNative());
    }

    private native Retainer<SerializableObject>[] getChildrenNative();

    public void setChildren(List<SerializableObject> children) {
        setChildrenNative((SerializableObject[]) children.toArray());
    }

    private native void setChildrenNative(SerializableObject[] children);

    public native void clearChildren();

    public native boolean setChild(int index, SerializableObject child, ErrorStatus errorStatus);

    public native boolean removeChild(int index, ErrorStatus errorStatus);
}
