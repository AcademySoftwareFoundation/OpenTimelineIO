package io.opentimeline.opentimelineio;

import io.opentimeline.opentime.TimeRange;

import java.util.List;

public class Algorithms {

    /**
     * Flatten a Stack, into a single Track.
     * Note that the 1st Track is the bottom one, and the last is the top.
     *
     * @param inStack     stack to flatten
     * @param errorStatus errorStatus to report error during flattening
     * @return flattened track
     */
    public native Track flattenStack(Stack inStack, ErrorStatus errorStatus);

    /**
     * Flatten a Stack, into a single Track.
     * Note that the 1st Track is the bottom one, and the last is the top.
     *
     * @param tracks      list of tracks to flatten
     * @param errorStatus errorStatus to report error during flattening
     * @return flattened track
     */
    public Track flattenStack(List<Track> tracks, ErrorStatus errorStatus) {
        Track[] trackArray = new Track[tracks.size()];
        trackArray = tracks.toArray(trackArray);
        return flattenStackNative(trackArray, errorStatus);
    }

    private native Track flattenStackNative(Track[] tracks, ErrorStatus errorStatus);

    /**
     * Returns a new track that is a copy of the inTrack, but with items
     * outside the trimRange removed and items on the ends trimmed to the
     * trimRange. Note that the track is never expanded, only shortened.
     * Please note that you could do nearly the same thing non-destructively by
     * just setting the Track's source_range but sometimes you want to really cut
     * away the stuff outside and that's what this function is meant for.
     *
     * @param inTrack     track to be trimmed
     * @param trimRange   this is the range, which the track will be trimmed to
     * @param errorStatus errorStatus to report error during trimming
     * @return trimmed track
     */
    public native Track trackTrimmedToRange(Track inTrack, TimeRange trimRange, ErrorStatus errorStatus);

    /**
     * Returns a new timeline that is a copy of the inTimeline, but with items
     * outside the trimRange removed and items on the ends trimmed to the
     * trimRange. Note that the timeline is never expanded, only shortened.
     * Please note that you could do nearly the same thing non-destructively by
     * just setting the Track's sourceRange but sometimes you want to really cut
     * away the stuff outside and that's what this function is meant for.
     *
     * @param inTimeline  timeline to be trimmed
     * @param trimRange   this is the range, which the timeline will be trimmed to
     * @param errorStatus errorStatus to report error during trimming
     * @return trimmed timeline
     */
    public Timeline timelineTrimmedToRange(Timeline inTimeline, TimeRange trimRange, ErrorStatus errorStatus) {
        Timeline newTimeline = (Timeline) inTimeline.clone(errorStatus);
        Stack stack = inTimeline.getTracks();
        Stack newStack = newTimeline.getTracks();
        List<Composable> tracks = stack.getChildren();
        for (int i = 0; i < tracks.size(); i++) {
            Track trimmedTrack = this.trackTrimmedToRange((Track) tracks.get(i), trimRange, errorStatus);
            if (errorStatus.getOutcome() != ErrorStatus.Outcome.OK) return null;
            newStack.setChild(i, trimmedTrack, errorStatus);
        }
        return newTimeline;
    }
}
