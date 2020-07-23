package io.opentimeline.opentimelineio;

import io.opentimeline.opentime.TimeRange;

public class GeneratorReference extends MediaReference {
    protected GeneratorReference() {
    }

    public GeneratorReference(long nativeHandle) {
        this.nativeHandle = nativeHandle;
    }

    public GeneratorReference(String name,
                              String generatorKind,
                              TimeRange availableRange,
                              AnyDictionary parameters,
                              AnyDictionary metadata) {
        this.initObject(
                name,
                generatorKind,
                availableRange,
                parameters,
                metadata);
    }

    public GeneratorReference(GeneratorReference.GeneratorReferenceBuilder generatorReferenceBuilder) {
        this.initObject(
                generatorReferenceBuilder.name,
                generatorReferenceBuilder.generatorKind,
                generatorReferenceBuilder.availableRange,
                generatorReferenceBuilder.parameters,
                generatorReferenceBuilder.metadata);
    }

    private void initObject(String name,
                            String generatorKind,
                            TimeRange availableRange,
                            AnyDictionary parameters,
                            AnyDictionary metadata) {
        this.className = this.getClass().getCanonicalName();
        this.initialize(
                name,
                generatorKind,
                availableRange,
                parameters,
                metadata);

    }

    private native void initialize(String name,
                                   String generatorKind,
                                   TimeRange availableRange,
                                   AnyDictionary parameters,
                                   AnyDictionary metadata);

    public static class GeneratorReferenceBuilder {
        private String name = "";
        private String generatorKind = "";
        private TimeRange availableRange = null;
        private AnyDictionary parameters = new AnyDictionary();
        private AnyDictionary metadata = new AnyDictionary();

        public GeneratorReferenceBuilder() {
        }

        public GeneratorReference.GeneratorReferenceBuilder setName(String name) {
            this.name = name;
            return this;
        }

        public GeneratorReference.GeneratorReferenceBuilder setGeneratorKind(String generatorKind) {
            this.generatorKind = generatorKind;
            return this;
        }

        public GeneratorReference.GeneratorReferenceBuilder setAvailableRange(TimeRange availableRange) {
            this.availableRange = availableRange;
            return this;
        }

        public GeneratorReference.GeneratorReferenceBuilder setParameters(AnyDictionary parameters) {
            this.parameters = parameters;
            return this;
        }

        public GeneratorReference.GeneratorReferenceBuilder setMetadata(AnyDictionary metadata) {
            this.metadata = metadata;
            return this;
        }

        public GeneratorReference build() {
            return new GeneratorReference(this);
        }
    }

    public native String getGeneratorKind();

    public native void setGeneratorKind(String generatorKind);

    public native AnyDictionary getParameters();
}
