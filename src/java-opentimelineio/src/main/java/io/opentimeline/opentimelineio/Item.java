package io.opentimeline.opentimelineio;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class Item extends Composable {

    protected Item() {
    }

    public Item(
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

    public Item(Item.ItemBuilder builder) {
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

    public static class ItemBuilder {
        private String name = "";
        private TimeRange sourceRange = null;
        private AnyDictionary metadata = new AnyDictionary();
        private List<Effect> effects = new ArrayList<>();
        private List<Marker> markers = new ArrayList<>();

        public ItemBuilder() {
        }

        public Item.ItemBuilder setName(String name) {
            this.name = name;
            return this;
        }

        public Item.ItemBuilder setSourceRange(TimeRange sourceRange) {
            this.sourceRange = sourceRange;
            return this;
        }

        public Item.ItemBuilder setMetadata(AnyDictionary metadata) {
            this.metadata = metadata;
            return this;
        }

        public Item.ItemBuilder setEffects(List<Effect> effects) {
            this.effects = effects;
            return this;
        }

        public Item.ItemBuilder setMarkers(List<Marker> markers) {
            this.markers = markers;
            return this;
        }

        public Item build() {
            return new Item(this);
        }
    }

    public native boolean isVisible();

    public native boolean isOverlapping();

    public TimeRange getSourceRange() {
        double[] timeRangeArray = getSourceRangeNative();
        if (timeRangeArray.length == 0) return null;
        return TimeRange.timeRangeFromArray(timeRangeArray);
    }

    private native double[] getSourceRangeNative();

    public void setSourceRange(TimeRange sourceRange) {
        double[] sourceRangeArray = new double[]{};
        if (sourceRange != null) {
            sourceRangeArray = TimeRange.timeRangeToArray(sourceRange);
        }
        setSourceRangeNative(sourceRangeArray);
    }

    private native void setSourceRangeNative(double[] sourceRange);

    public List<Retainer<Effect>> getEffects() {
        return Arrays.asList(getEffectsNative());
    }

    private native Retainer<Effect>[] getEffectsNative();

    public List<Retainer<Marker>> getMarkers() {
        return Arrays.asList(getMarkersNative());
    }

    private native Retainer<Marker>[] getMarkersNative();

    public RationalTime getDuration(ErrorStatus errorStatus) {
        return RationalTime.rationalTimeFromArray(getDurationNative(errorStatus));
    }

    private native double[] getDurationNative(ErrorStatus errorStatus);

    public TimeRange getAvailableRange(ErrorStatus errorStatus) {
        return TimeRange.timeRangeFromArray(getAvailableRangeNative(errorStatus));
    }

    private native double[] getAvailableRangeNative(ErrorStatus errorStatus);

    public TimeRange getTrimmedRange(ErrorStatus errorStatus) {
        return TimeRange.timeRangeFromArray(getTrimmedRangeNative(errorStatus));
    }

    private native double[] getTrimmedRangeNative(ErrorStatus errorStatus);

    public TimeRange getVisibleRange(ErrorStatus errorStatus) {
        return TimeRange.timeRangeFromArray(getVisibleRangeNative(errorStatus));
    }

    private native double[] getVisibleRangeNative(ErrorStatus errorStatus);

    public TimeRange getTrimmedRangeInParent(ErrorStatus errorStatus) {
        double[] trimmedRangeInParentArray = getTrimmedRangeInParentNative(errorStatus);
        if (trimmedRangeInParentArray.length == 0) return null;
        return TimeRange.timeRangeFromArray(getTrimmedRangeInParentNative(errorStatus));
    }

    private native double[] getTrimmedRangeInParentNative(ErrorStatus errorStatus);

    public TimeRange getRangeRangeInParent(ErrorStatus errorStatus) {
        return TimeRange.timeRangeFromArray(getRangeInParentNative(errorStatus));
    }

    private native double[] getRangeInParentNative(ErrorStatus errorStatus);

    public RationalTime getTransformedTime(
            RationalTime time,
            Item toItem,
            ErrorStatus errorStatus) {
        return RationalTime.rationalTimeFromArray(
                getTransformedTimeNative(
                        RationalTime.rationalTimeToArray(time),
                        toItem,
                        errorStatus));
    }

    private native double[] getTransformedTimeNative(
            double[] time,
            Item toItem,
            ErrorStatus errorStatus);

    public TimeRange getTransformedTimeRange(
            TimeRange timeRange,
            Item toItem,
            ErrorStatus errorStatus) {
        return TimeRange.timeRangeFromArray(
                getTransformedTimeRangeNative(
                        TimeRange.timeRangeToArray(timeRange),
                        toItem,
                        errorStatus));
    }

    private native double[] getTransformedTimeRangeNative(
            double[] timeRange,
            Item toItem,
            ErrorStatus errorStatus);
}
