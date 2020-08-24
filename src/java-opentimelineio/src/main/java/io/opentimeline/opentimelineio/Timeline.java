package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;
import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;

import java.util.Arrays;
import java.util.List;
import java.util.stream.Stream;

/**
 * A class that contains a Stack.
 */
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

    /**
     * Get global starting time value and rate of the timeline.
     *
     * @return global starting time value and rate of the timeline.
     */
    public native RationalTime getGlobalStartTime();

    /**
     * Set global starting time value and rate of the timeline.
     *
     * @param globalStartTime global starting time value and rate of the timeline.
     */
    public native void setGlobalStartTime(RationalTime globalStartTime);

    /**
     * Get duration of this timeline.
     *
     * @param errorStatus errorStatus to report error while fetching duration
     * @return duration of the timeline.
     */
    public native RationalTime getDuration(ErrorStatus errorStatus);

    /**
     * Range of the child object contained in this timeline.
     *
     * @param child       child Composable whose range is to be found.
     * @param errorStatus errorStatus to report error while fetching range
     * @return range of the child object contained in this timeline.
     */
    public native TimeRange getRangeOfChild(Composable child, ErrorStatus errorStatus);

    /**
     * This convenience method returns a list of the top-level audio tracks in
     * this timeline.
     *
     * @return
     */
    public List<Track> getAudioTracks() {
        return Arrays.asList(getAudioTracksNative());
    }

    private native Track[] getAudioTracksNative();

    /**
     * This convenience method returns a list of the top-level video tracks in
     * this timeline.
     *
     * @return list of video tracks
     */
    public List<Track> getVideoTracks() {
        return Arrays.asList(getVideoTracksNative());
    }

    private native Track[] getVideoTracksNative();

    /**
     * Return a flat Stream of each child of specified type, limited to the search_range.
     * This recursively searches all compositions.
     *
     * @param searchRange   TimeRange to search in
     * @param descendedFrom only children who are a descendent of the descendedFrom type will be in the stream
     * @param errorStatus   errorStatus to report any error while iterating
     * @param <T>           type of children to fetch
     * @return a Stream consisting of all the children of specified type in the composition in the order in which it is found
     */
    public <T extends Composable> Stream<T> eachChild(
            TimeRange searchRange, Class<T> descendedFrom, ErrorStatus errorStatus) {
        return this.getTracks().eachChild(searchRange, descendedFrom, false, errorStatus);
    }

    /**
     * Return a flat Stream of each child, limited to the search_range.
     * This recursively searches all compositions.
     *
     * @param searchRange TimeRange to search in
     * @param errorStatus errorStatus to report any error while iterating
     * @return a Stream consisting of all the children in the composition (in the searchRange) in the order in which it is found
     */
    public Stream<Composable> eachChild(
            TimeRange searchRange, ErrorStatus errorStatus) {
        return this.eachChild(searchRange, Composable.class, errorStatus);
    }

    /**
     * Return a flat Stream of each child.
     * This recursively searches all compositions.
     *
     * @param errorStatus errorStatus to report any error while iterating
     * @return a Stream consisting of all the children in the composition in the order in which it is found
     */
    public Stream<Composable> eachChild(ErrorStatus errorStatus) {
        return this.eachChild((TimeRange) null, errorStatus);
    }

    /**
     * Return a flat Stream of each child of specified type.
     * This recursively searches all compositions.
     *
     * @param descendedFrom only children who are a descendent of the descendedFrom type will be in the stream
     * @param errorStatus   errorStatus to report any error while iterating
     * @param <T>           type of children to fetch
     * @return
     */
    public <T extends Composable> Stream<T> eachChild(Class<T> descendedFrom, ErrorStatus errorStatus) {
        return this.eachChild(null, descendedFrom, errorStatus);
    }

    /**
     * Return a flat Stream of each clip, limited to the search_range.
     *
     * @param searchRange TimeRange to search in
     * @param errorStatus errorStatus to report error while iterating
     * @return a Stream of all clips in the timeline (in the searchRange) in the order they are found
     */
    public Stream<Clip> eachClip(
            TimeRange searchRange, ErrorStatus errorStatus) {
        return this.getTracks().eachClip(searchRange, errorStatus);
    }

    /**
     * Return a flat Stream of each clip.
     *
     * @param errorStatus errorStatus to report error while iterating
     * @return a Stream of all clips in the timeline in the order they are found
     */
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
