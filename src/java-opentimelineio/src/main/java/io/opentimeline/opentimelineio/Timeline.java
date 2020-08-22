package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;
import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;

import java.util.Arrays;
import java.util.List;
import java.util.stream.Stream;

public class Timeline extends SerializableObjectWithMetadata {

    protected Timeline() {
    }

    Timeline(OTIONative otioNative) {
        this.nativeManager = otioNative;
    }

    public Timeline(
            String name,
            RationalTime globalStartTime,
            AnyDictionary metadata) {
        this.initObject(name, globalStartTime, metadata);
    }

    public Timeline(Timeline.TimelineBuilder builder) {
        this.initObject(
                builder.name,
                builder.globalStartTime,
                builder.metadata);
    }

    private void initObject(String name,
                            RationalTime globalStartTime,
                            AnyDictionary metadata) {
        this.initialize(name, globalStartTime, metadata);
        this.nativeManager.className = this.getClass().getCanonicalName();
    }

    private native void initialize(String name,
                                   RationalTime globalStartTime,
                                   AnyDictionary metadata);

    public static class TimelineBuilder {
        private String name = "";
        private RationalTime globalStartTime = null;
        private AnyDictionary metadata = new AnyDictionary();

        public TimelineBuilder() {
        }

        public Timeline.TimelineBuilder setName(String name) {
            this.name = name;
            return this;
        }

        public Timeline.TimelineBuilder setGlobalStartTime(RationalTime globalStartTime) {
            this.globalStartTime = globalStartTime;
            return this;
        }

        public Timeline.TimelineBuilder setMetadata(AnyDictionary metadata) {
            this.metadata = metadata;
            return this;
        }

        public Timeline build() {
            return new Timeline(this);
        }
    }

    public native Stack getTracks();

    public native void setTracks(Stack stack);

    public native RationalTime getGlobalStartTime();

    public native void setGlobalStartTime(RationalTime globalStartTime);

    public native RationalTime getDuration(ErrorStatus errorStatus);

    public native TimeRange getRangeOfChild(Composable child, ErrorStatus errorStatus);

    public List<Track> getAudioTracks() {
        return Arrays.asList(getAudioTracksNative());
    }

    private native Track[] getAudioTracksNative();

    public List<Track> getVideoTracks() {
        return Arrays.asList(getVideoTracksNative());
    }

    private native Track[] getVideoTracksNative();

    public <T extends Composable> Stream<T> eachChild(
            TimeRange searchRange, Class<T> descendedFrom, ErrorStatus errorStatus) {
        return this.getTracks().eachChild(searchRange, descendedFrom, false, errorStatus);
    }

    public Stream<Composable> eachChild(
            TimeRange searchRange, ErrorStatus errorStatus) {
        return this.eachChild(searchRange, Composable.class, errorStatus);
    }

    public Stream<Composable> eachChild(ErrorStatus errorStatus) {
        return this.eachChild((TimeRange) null, errorStatus);
    }

    public <T extends Composable> Stream<T> eachChild(Class<T> descendedFrom, ErrorStatus errorStatus) {
        return this.eachChild(null, descendedFrom, errorStatus);
    }

    public Stream<Clip> eachClip(
            TimeRange searchRange, ErrorStatus errorStatus) {
        return this.getTracks().eachClip(searchRange, errorStatus);
    }

    public Stream<Clip> eachClip(ErrorStatus errorStatus) {
        return this.eachClip(null, errorStatus);
    }

    @Override
    public String toString() {
        return this.getClass().getCanonicalName() +
                "(" +
                "name=" + this.getName() +
                ", tracks=" + this.getTracks().toString() +
                ")";
    }
}
