package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;
import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.util.Pair;

import java.util.HashMap;
import java.util.stream.Stream;

public class Track extends Composition {

    public static class Kind {
        public static String video = "Video";
        public static String audio = "Audio";
    }

    public enum NeighborGapPolicy {
        never,
        around_transitions,
    }

    protected Track() {
    }

    Track(OTIONative otioNative) {
        this.nativeManager = otioNative;
    }

    public Track(
            String name,
            TimeRange sourceRange,
            String kind,
            AnyDictionary metadata) {
        this.initObject(
                name,
                sourceRange,
                kind,
                metadata);
    }

    public Track(Track.TrackBuilder builder) {
        this.initObject(
                builder.name,
                builder.sourceRange,
                builder.kind,
                builder.metadata);
    }

    private void initObject(String name,
                            TimeRange sourceRange,
                            String kind,
                            AnyDictionary metadata) {
        this.initialize(
                name,
                sourceRange,
                kind,
                metadata);
        this.nativeManager.className = this.getClass().getCanonicalName();
    }

    private native void initialize(String name,
                                   TimeRange sourceRange,
                                   String kind,
                                   AnyDictionary metadata);

    public static class TrackBuilder {
        private String name = "";
        private TimeRange sourceRange = null;
        private String kind = Kind.video;
        private AnyDictionary metadata = new AnyDictionary();

        public TrackBuilder() {
        }

        public Track.TrackBuilder setName(String name) {
            this.name = name;
            return this;
        }

        public Track.TrackBuilder setSourceRange(TimeRange sourceRange) {
            this.sourceRange = sourceRange;
            return this;
        }

        public Track.TrackBuilder setKind(String kind) {
            this.kind = kind;
            return this;
        }

        public Track.TrackBuilder setMetadata(AnyDictionary metadata) {
            this.metadata = metadata;
            return this;
        }

        public Track build() {
            return new Track(this);
        }
    }

    public native String getKind();

    public native void setKind(String kind);

    public native TimeRange rangeOfChildAtIndex(int index, ErrorStatus errorStatus);

    public native TimeRange trimmedRangeOfChildAtIndex(int index, ErrorStatus errorStatus);

    public native TimeRange getAvailableRange(ErrorStatus errorStatus);

    public native Pair<RationalTime, RationalTime> getHandlesOfChild(
            Composable child, ErrorStatus errorStatus);

    public Pair<Composable, Composable> getNeighborsOf(
            Composable item,
            ErrorStatus errorStatus) {
        return getNeighborsOfNative(item, errorStatus, NeighborGapPolicy.never.ordinal());
    }

    public Pair<Composable, Composable> getNeighborsOf(
            Composable item,
            ErrorStatus errorStatus,
            NeighborGapPolicy neighborGapPolicy) {
        return getNeighborsOfNative(item, errorStatus, neighborGapPolicy.ordinal());
    }

    private native Pair<Composable, Composable> getNeighborsOfNative(
            Composable item,
            ErrorStatus errorStatus,
            int neighbourGapPolicyIndex);

    public native HashMap<Composable, TimeRange> getRangeOfAllChildren(ErrorStatus errorStatus);

    public Stream<Clip> eachClip(
            TimeRange searchRange, boolean shallowSearch, ErrorStatus errorStatus) {
        return this.eachChild(searchRange, Clip.class, shallowSearch, errorStatus);
    }

    public Stream<Clip> eachClip(
            TimeRange searchRange, ErrorStatus errorStatus) {
        return this.eachChild(searchRange, Clip.class, false, errorStatus);
    }
}
