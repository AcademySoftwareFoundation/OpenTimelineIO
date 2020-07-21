package io.opentimeline.opentimelineio;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;

import java.util.ArrayList;
import java.util.List;

public class Gap extends Item {

    protected Gap() {
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
        this.className = this.getClass().getCanonicalName();
        if (sourceRange == null) throw new NullPointerException();
        this.initializeSourceRange(
                TimeRange.timeRangeToArray(sourceRange),
                name,
                (Effect[]) effects.toArray(),
                (Marker[]) markers.toArray(),
                metadata);
    }

    private void initObject(RationalTime duration,
                            String name,
                            List<Effect> effects,
                            List<Marker> markers,
                            AnyDictionary metadata) {
        this.className = this.getClass().getCanonicalName();
        if (duration == null) throw new NullPointerException();
        this.initializeDuration(
                RationalTime.rationalTimeToArray(duration),
                name,
                (Effect[]) effects.toArray(),
                (Marker[]) markers.toArray(),
                metadata);
    }

    private native void initializeSourceRange(double[] sourceRange,
                                              String name,
                                              Effect[] effects,
                                              Marker[] markers,
                                              AnyDictionary metadata);

    private native void initializeDuration(double[] durationRationalTime,
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
