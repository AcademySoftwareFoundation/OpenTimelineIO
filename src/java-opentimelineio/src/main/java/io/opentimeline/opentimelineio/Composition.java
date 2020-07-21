package io.opentimeline.opentimelineio;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.util.Pair;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;

public class Composition extends Item {

    protected Composition() {
    }

    public Composition(
            String name,
            TimeRange sourceRange,
            AnyDictionary metadata,
            List<Effect> effects,
            List<Marker> markers) {
        this.initObject(
                name,
                sourceRange,
                metadata,
                effects,
                markers);
    }

    public Composition(Composition.CompositionBuilder builder) {
        this.initObject(
                builder.name,
                builder.sourceRange,
                builder.metadata,
                builder.effects,
                builder.markers);
    }

    private void initObject(String name,
                            TimeRange sourceRange,
                            AnyDictionary metadata,
                            List<Effect> effects,
                            List<Marker> markers) {
        this.className = this.getClass().getCanonicalName();
        double[] sourceRangeArray = new double[]{};
        if (sourceRange != null) {
            sourceRangeArray = TimeRange.timeRangeToArray(sourceRange);
        }
        this.initialize(
                name,
                sourceRangeArray,
                metadata,
                (Effect[]) effects.toArray(),
                (Marker[]) markers.toArray());
    }

    private native void initialize(String name,
                                   double[] sourceRange,
                                   AnyDictionary metadata,
                                   Effect[] effects,
                                   Marker[] markers);

    public static class CompositionBuilder {
        private String name = "";
        private TimeRange sourceRange = null;
        private AnyDictionary metadata = new AnyDictionary();
        private List<Effect> effects = new ArrayList<>();
        private List<Marker> markers = new ArrayList<>();

        public CompositionBuilder() {
        }

        public Composition.CompositionBuilder setName(String name) {
            this.name = name;
            return this;
        }

        public Composition.CompositionBuilder setSourceRange(TimeRange sourceRange) {
            this.sourceRange = sourceRange;
            return this;
        }

        public Composition.CompositionBuilder setMetadata(AnyDictionary metadata) {
            this.metadata = metadata;
            return this;
        }

        public Composition.CompositionBuilder setEffects(List<Effect> effects) {
            this.effects = effects;
            return this;
        }

        public Composition.CompositionBuilder setMarkers(List<Marker> markers) {
            this.markers = markers;
            return this;
        }

        public Composition build() {
            return new Composition(this);
        }
    }

    public native String getCompositionKind();

    public List<Retainer<Composable>> getChildren() {
        return Arrays.asList(getChildrenNative());
    }

    private native Retainer<Composable>[] getChildrenNative();

    public native void clearChildren();

    public void setChildren(List<Composable> children, ErrorStatus errorStatus) {
        setChildrenNative((Composable[]) children.toArray(), errorStatus);
    }

    private native void setChildrenNative(Composable[] children, ErrorStatus errorStatus);

    public native boolean insertChild(int index, Composable child, ErrorStatus errorStatus);

    public native boolean setChild(int index, Composable child, ErrorStatus errorStatus);

    public native boolean removeChild(int index, ErrorStatus errorStatus);

    public native boolean appendChild(Composable child, ErrorStatus errorStatus);

    public native boolean isParentOf(Composable composable);

    public native Pair<RationalTime, RationalTime> getHandlesOfChild(
            Composable child, ErrorStatus errorStatus);

    public TimeRange getRangeOfChildAtIndex(int index, ErrorStatus errorStatus) {
        return TimeRange.timeRangeFromArray(getRangeOfChildAtIndexNative(index, errorStatus));
    }

    private native double[] getRangeOfChildAtIndexNative(int index, ErrorStatus errorStatus);

    public TimeRange getTrimmedRangeOfChildAtIndex(int index, ErrorStatus errorStatus) {
        return TimeRange.timeRangeFromArray(getTrimmedRangeOfChildAtIndexNative(index, errorStatus));
    }

    private native double[] getTrimmedRangeOfChildAtIndexNative(int index, ErrorStatus errorStatus);

    public TimeRange getRangeOfChild(Composable child, ErrorStatus errorStatus) {
        return TimeRange.timeRangeFromArray(getRangeOfChildNative(child, errorStatus));
    }

    private native double[] getRangeOfChildNative(Composable child, ErrorStatus errorStatus);

    public TimeRange getTrimmedRangeOfChild(Composable child, ErrorStatus errorStatus) {
        double[] timeRangeArray = getTrimmedRangeOfChildNative(child, errorStatus);
        if (timeRangeArray.length == 0) return null;
        return TimeRange.timeRangeFromArray(timeRangeArray);
    }

    private native double[] getTrimmedRangeOfChildNative(Composable child, ErrorStatus errorStatus);

    public TimeRange trimChildRange(TimeRange childRange) {
        return TimeRange.timeRangeFromArray(
                trimChildRangeNative(
                        TimeRange.timeRangeToArray(childRange)));
    }

    private native double[] trimChildRangeNative(double[] childRange);

    public native boolean hasChild(Composable child);

    public native HashMap<Composable, TimeRange> getRangeOfAllChildren(ErrorStatus errorStatus);
}
