package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;
import io.opentimeline.opentime.TimeRange;

public class GeneratorReference extends MediaReference {
    protected GeneratorReference() {
    }

    GeneratorReference(OTIONative otioNative) {
        this.nativeManager = otioNative;
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
        this.initialize(
                name,
                generatorKind,
                availableRange,
                parameters,
                metadata);
        this.nativeManager.className = this.getClass().getCanonicalName();
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

    @Override
    public String toString() {
        return this.getClass().getCanonicalName() +
                "(" +
                "name=" + this.getName() +
                ", generatorKind=" + this.getGeneratorKind() +
                ", parameters=" + this.getParameters().toString() +
                ", metadata=" + this.getMetadata().toString() +
                ")";
    }
}
