package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;

public class SerializableObjectWithMetadata extends SerializableObject {

    protected SerializableObjectWithMetadata() {
    }

    SerializableObjectWithMetadata(OTIONative otioNative) {
        this.nativeManager = otioNative;
    }

    public SerializableObjectWithMetadata(String name, AnyDictionary metadata) {
        this.initObject(name, metadata);
    }

    public SerializableObjectWithMetadata(String name) {
        this.initObject(name, new AnyDictionary());
    }

    public SerializableObjectWithMetadata(AnyDictionary metadata) {
        this.initObject("", metadata);
    }

    public SerializableObjectWithMetadata(SerializableObjectWithMetadataBuilder builder) {
        this.initObject(builder.name, builder.metadata);
    }

    private void initObject(String name, AnyDictionary metadata) {
        this.initialize(name, metadata);
        this.nativeManager.className = this.getClass().getCanonicalName();
    }

    private native void initialize(String name, AnyDictionary metadata);

    public static class SerializableObjectWithMetadataBuilder {
        private String name = "";
        private AnyDictionary metadata = new AnyDictionary();

        public SerializableObjectWithMetadataBuilder() {
        }

        public SerializableObjectWithMetadata.SerializableObjectWithMetadataBuilder setName(String name) {
            this.name = name;
            return this;
        }

        public SerializableObjectWithMetadata.SerializableObjectWithMetadataBuilder setMetadata(AnyDictionary metadata) {
            this.metadata = metadata;
            return this;
        }

        public SerializableObjectWithMetadata build() {
            return new SerializableObjectWithMetadata(this);
        }
    }

    public native String getName();

    public native void setName(String name);

    public native AnyDictionary getMetadata();

    public native void setMetadata(AnyDictionary metadata);

    @Override
    public String toString() {
        return this.getClass().getCanonicalName() +
                "(" +
                "name=" + this.getName() +
                ", metadata=" + this.getMetadata().toString() +
                ")";
    }
}
