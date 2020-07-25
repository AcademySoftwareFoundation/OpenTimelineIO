package io.opentimeline.opentimelineio;

import io.opentimeline.opentime.TimeRange;

import java.util.ArrayList;
import java.util.List;

public class Clip extends Item {

    protected Clip() {
    }

    public Clip(long nativeHandle) {
        this.nativeHandle = nativeHandle;
    }

    public Clip(SerializableObject serializableObject) {
        this.nativeHandle = serializableObject.nativeHandle;
    }

    public Clip(
            String name,
            MediaReference mediaReference,
            TimeRange sourceRange,
            AnyDictionary metadata) {
        this.initObject(
                name,
                mediaReference,
                sourceRange,
                metadata);
    }

    public Clip(Clip.ClipBuilder builder) {
        this.initObject(
                builder.name,
                builder.mediaReference,
                builder.sourceRange,
                builder.metadata
        );
    }

    private void initObject(String name,
                            MediaReference mediaReference,
                            TimeRange sourceRange,
                            AnyDictionary metadata) {
        this.className = this.getClass().getCanonicalName();
        this.initialize(
                name,
                mediaReference,
                sourceRange,
                metadata);
    }

    private native void initialize(String name,
                                   MediaReference mediaReference,
                                   TimeRange sourceRange,
                                   AnyDictionary metadata);

    public static class ClipBuilder {
        private String name = "";
        private MediaReference mediaReference = null;
        private TimeRange sourceRange = null;
        private AnyDictionary metadata = new AnyDictionary();

        public ClipBuilder() {
        }

        public Clip.ClipBuilder setName(String name) {
            this.name = name;
            return this;
        }

        public Clip.ClipBuilder setMediaReference(MediaReference mediaReference) {
            this.mediaReference = mediaReference;
            return this;
        }

        public Clip.ClipBuilder setSourceRange(TimeRange sourceRange) {
            this.sourceRange = sourceRange;
            return this;
        }

        public Clip.ClipBuilder setMetadata(AnyDictionary metadata) {
            this.metadata = metadata;
            return this;
        }

        public Clip build() {
            return new Clip(this);
        }
    }

    public native void setMediaReference(MediaReference mediaReference);

    public native MediaReference getMediaReference();

    public native TimeRange getAvailableRange(ErrorStatus errorStatus);

}
