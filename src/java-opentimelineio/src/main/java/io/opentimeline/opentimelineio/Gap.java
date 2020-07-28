package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;
import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;

import java.util.ArrayList;
import java.util.List;

public class Gap extends Item {

    protected Gap() {
    }

    Gap(OTIONative otioNative) {
        this.nativeManager = otioNative;
    }

    public Gap(
            TimeRange sourceRange,
            String name,
            List<Effect> effects,
            List<Marker> markers,
            AnyDictionary metadata) {
        this.initObject(
                sourceRange,
                name,
                effects,
                markers,
                metadata);
    }

    public Gap(
            RationalTime duration,
            String name,
            List<Effect> effects,
            List<Marker> markers,
            AnyDictionary metadata) {
        this.initObject(
                duration,
                name,
                effects,
                markers,
                metadata);
    }

    public Gap(Gap.GapBuilder builder) {
        if (builder.sourceRange == null) {
            this.initObject(
                    builder.duration,
                    builder.name,
                    builder.effects,
                    builder.markers,
                    builder.metadata);
        } else if (builder.duration == null) {
            this.initObject(
                    builder.sourceRange,
                    builder.name,
                    builder.effects,
                    builder.markers,
                    builder.metadata);
        }
    }

    private void initObject(TimeRange sourceRange,
                            String name,
                            List<Effect> effects,
                            List<Marker> markers,
                            AnyDictionary metadata) {
        this.nativeManager.className = this.getClass().getCanonicalName();
        Effect[] effectsArray = new Effect[effects.size()];
        effectsArray = effects.toArray(effectsArray);
        Marker[] markersArray = new Marker[markers.size()];
        markersArray = markers.toArray(markersArray);
        this.initializeSourceRange(
                sourceRange,
                name,
                effectsArray,
                markersArray,
                metadata);
    }

    private void initObject(RationalTime duration,
                            String name,
                            List<Effect> effects,
                            List<Marker> markers,
                            AnyDictionary metadata) {
        this.nativeManager.className = this.getClass().getCanonicalName();
        Effect[] effectsArray = new Effect[effects.size()];
        effectsArray = effects.toArray(effectsArray);
        Marker[] markersArray = new Marker[markers.size()];
        markersArray = markers.toArray(markersArray);
        this.initializeDuration(
                duration,
                name,
                effectsArray,
                markersArray,
                metadata);
    }

    private native void initializeSourceRange(TimeRange sourceRange,
                                              String name,
                                              Effect[] effects,
                                              Marker[] markers,
                                              AnyDictionary metadata);

    private native void initializeDuration(RationalTime durationRationalTime,
                                           String name,
                                           Effect[] effects,
                                           Marker[] markers,
                                           AnyDictionary metadata);

    public static class GapBuilder {
        private String name = "";
        private TimeRange sourceRange = null;
        private RationalTime duration = null;
        private AnyDictionary metadata = new AnyDictionary();
        private List<Effect> effects = new ArrayList<>();
        private List<Marker> markers = new ArrayList<>();

        public GapBuilder() {
        }

        public Gap.GapBuilder setName(String name) {
            this.name = name;
            return this;
        }

        public Gap.GapBuilder setSourceRange(TimeRange sourceRange) {
            this.sourceRange = sourceRange;
            this.duration = null;
            return this;
        }

        public Gap.GapBuilder setDuration(RationalTime duration) {
            this.duration = duration;
            this.sourceRange = null;
            return this;
        }

        public Gap.GapBuilder setMetadata(AnyDictionary metadata) {
            this.metadata = metadata;
            return this;
        }

        public Gap.GapBuilder setEffects(List<Effect> effects) {
            this.effects = effects;
            return this;
        }

        public Gap.GapBuilder setMarkers(List<Marker> markers) {
            this.markers = markers;
            return this;
        }

        public Gap build() {
            if (duration == null && sourceRange == null)
                sourceRange = new TimeRange();
            return new Gap(this);
        }
    }

    public native boolean isVisible();

}
