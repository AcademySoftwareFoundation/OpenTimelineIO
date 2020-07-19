package io.opentimeline.opentimelineio;

public class SerializableObjectWithMetadata extends SerializableObject {

    protected SerializableObjectWithMetadata() {
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
        this.className = this.getClass().getCanonicalName();
        this.initialize(name, metadata);
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
}
