package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;
import io.opentimeline.opentime.TimeRange;

public class ExternalReference extends MediaReference {

    protected ExternalReference() {
    }

    ExternalReference(OTIONative otioNative) {
        this.nativeManager = otioNative;
    }

    public ExternalReference(String targetURL, TimeRange availableRange, AnyDictionary metadata) {
        this.initObject(targetURL, availableRange, metadata);
    }

    public ExternalReference(ExternalReference.ExternalReferenceBuilder mediaReferenceBuilder) {
        this.initObject(
                mediaReferenceBuilder.targetURL,
                mediaReferenceBuilder.availableRange,
                mediaReferenceBuilder.metadata);
    }

    private void initObject(String targetURL, TimeRange availableRange, AnyDictionary metadata) {
        this.nativeManager.className = this.getClass().getCanonicalName();
        this.initialize(targetURL, availableRange, metadata);
    }

    private native void initialize(String name, TimeRange availableRange, AnyDictionary metadata);

    public static class ExternalReferenceBuilder {
        private String targetURL = "";
        private TimeRange availableRange = null;
        private AnyDictionary metadata = new AnyDictionary();

        public ExternalReferenceBuilder() {
        }

        public ExternalReference.ExternalReferenceBuilder setTargetURL(String targetURL) {
            this.targetURL = targetURL;
            return this;
        }

        public ExternalReference.ExternalReferenceBuilder setAvailableRange(TimeRange availableRange) {
            this.availableRange = availableRange;
            return this;
        }


        public ExternalReference.ExternalReferenceBuilder setMetadata(AnyDictionary metadata) {
            this.metadata = metadata;
            return this;
        }

        public ExternalReference build() {
            return new ExternalReference(this);
        }
    }

    public native String getTargetURL();

    public native void setTargetURL(String targetURL);

}
