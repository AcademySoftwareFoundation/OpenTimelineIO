package io.opentimeline.opentimelineio;

import io.opentimeline.opentime.TimeRange;

import java.util.List;

public class Algorithms {

    public static native Track flattenStack(Stack inStack, ErrorStatus errorStatus);

    public static Track flattenStack(List<Track> tracks, ErrorStatus errorStatus) {
        return flattenStackNative((Track[]) tracks.toArray(), errorStatus);
    }

    private static native Track flattenStackNative(Track[] tracks, ErrorStatus errorStatus);

    public static native Track trackTrimmedToRange(Track inTrack, TimeRange trimRange, ErrorStatus errorStatus);
}
