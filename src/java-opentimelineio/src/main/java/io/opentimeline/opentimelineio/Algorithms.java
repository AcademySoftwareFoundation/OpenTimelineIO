package io.opentimeline.opentimelineio;

import io.opentimeline.opentime.TimeRange;

import java.util.List;

public class Algorithms {

    public native Track flattenStack(Stack inStack, ErrorStatus errorStatus);

    public Track flattenStack(List<Track> tracks, ErrorStatus errorStatus) {
        Track[] trackArray = new Track[tracks.size()];
        trackArray = tracks.toArray(trackArray);
        return flattenStackNative(trackArray, errorStatus);
    }

    private native Track flattenStackNative(Track[] tracks, ErrorStatus errorStatus);

    public native Track trackTrimmedToRange(Track inTrack, TimeRange trimRange, ErrorStatus errorStatus);
}
