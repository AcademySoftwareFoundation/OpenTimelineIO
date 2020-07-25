package io.opentimeline.opentimelineio;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;

import java.util.Arrays;
import java.util.List;

public class Timeline extends SerializableObjectWithMetadata {

    protected Timeline() {
    }

    public Timeline(long nativeHandle) {
        this.nativeHandle = nativeHandle;
    }

    public Timeline(SerializableObject serializableObject) {
        this.nativeHandle = serializableObject.nativeHandle;
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
        this.className = this.getClass().getCanonicalName();
        this.initialize(name, globalStartTime, metadata);
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

}
