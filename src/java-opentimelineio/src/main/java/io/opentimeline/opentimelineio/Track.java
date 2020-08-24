package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;
import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.util.Pair;

import java.util.HashMap;
import java.util.stream.Stream;

/**
 * A class that holds a list of Composables.
 */
public class Track extends Composition {

    public static class Kind {
        public static String video = "Video";
        public static String audio = "Audio";
    }

    /**
     * enum for deciding how to add gap when asking for neighbors
     */
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

    /**
     * If media beyond the ends of this child are visible due to adjacent
     * Transitions (only applicable in a Track) then this will return the
     * head and tail offsets as a tuple of RationalTime objects. If no handles
     * are present on either side, then None is returned instead of a
     * RationalTime.
     *
     * @param child       child Composable to get handles
     * @param errorStatus errorStatus to report error while fetching handles
     * @return
     */
    public native Pair<RationalTime, RationalTime> getHandlesOfChild(
            Composable child, ErrorStatus errorStatus);

    public Pair<Composable, Composable> getNeighborsOf(
            Composable item,
            ErrorStatus errorStatus) {
        return getNeighborsOfNative(item, errorStatus, NeighborGapPolicy.never.ordinal());
    }

    /**
     * Returns the neighbors of the item as a Pair, (previous, next).
     * Can optionally fill in gaps when transitions have no gaps next to them.
     * with neighborGapPolicy == NeighborGapPolicy.never:
     * [A, B, C] :: getNeighborsOf(B) -> (A, C)
     * [A, B, C] :: getNeighborsOf(A) -> (null, B)
     * [A, B, C] :: getNeighborsOf(C) -> (B, null)
     * [A] :: getNeighborsOf(A) -> (null, null)
     * with neighborGapPolicy == NeighborGapPolicy.around_transitions:
     * (assuming A and C are transitions)
     * [A, B, C] :: getNeighborsOf(B) -> (A, C)
     * [A, B, C] :: getNeighborsOf(A) -> (Gap, B)
     * [A, B, C] :: getNeighborsOf(C) -> (B, Gap)
     * [A] :: getNeighborsOf(A) -> (Gap, Gap)
     *
     * @param item              Composable whose neighbors are to be fetched
     * @param errorStatus       errorStatus to report error while fetching neighbors
     * @param neighborGapPolicy optionally fill in gaps when transitions have no gaps next to them? [never, around_transitions]
     * @return neighbors of the item as a Pair
     */
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

    /**
     * Return a HashMap mapping children to their range in this track.
     *
     * @param errorStatus errorStatus to report any error while fetching ranges
     * @return a HashMap mapping children to their range in this track.
     */
    public native HashMap<Composable, TimeRange> getRangeOfAllChildren(ErrorStatus errorStatus);

    /**
     * Return a flat Stream of each clip, limited to the search_range.
     *
     * @param searchRange   TimeRange to search in
     * @param shallowSearch should the algorithm recurse into compositions or not?
     * @param errorStatus   errorStatus to report any error while iterating
     * @return a Stream of all clips in the timeline (in the searchRange) in the order they are found
     */
    public Stream<Clip> eachClip(
            TimeRange searchRange, boolean shallowSearch, ErrorStatus errorStatus) {
        return this.eachChild(searchRange, Clip.class, shallowSearch, errorStatus);
    }

    /**
     * Return a flat Stream of each clip, limited to the search_range.
     * This recurses into compositions.
     *
     * @param searchRange TimeRange to search in
     * @param errorStatus errorStatus to report any error while iterating
     * @return a Stream of all clips in the timeline (in the searchRange) in the order they are found
     */
    public Stream<Clip> eachClip(
            TimeRange searchRange, ErrorStatus errorStatus) {
        return this.eachChild(searchRange, Clip.class, false, errorStatus);
    }
}
