package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;
import io.opentimeline.opentime.TimeRange;

/**
 * Holds metadata over time on a timeline
 */
public class Marker extends SerializableObjectWithMetadata {

    public static class Color {
        public static String pink = "PINK";
        public static String red = "RED";
        public static String orange = "ORANGE";
        public static String yellow = "YELLOW";
        public static String green = "GREEN";
        public static String cyan = "CYAN";
        public static String blue = "BLUE";
        public static String purple = "PURPLE";
        public static String magenta = "MAGENTA";
        public static String black = "BLACK";
        public static String white = "WHITE";
    }

    protected Marker() {
    }

    Marker(OTIONative otioNative) {
        this.nativeManager = otioNative;
    }

    public Marker(String name, TimeRange markedRange, String color, AnyDictionary metadata) {
        this.initObject(name, markedRange, color, metadata);
    }

    public Marker(MarkerBuilder markerBuilder) {
        this.initObject(
                markerBuilder.name, markerBuilder.markedRange,
                markerBuilder.color, markerBuilder.metadata);
    }

    private void initObject(
            String name,
            TimeRange markedRange,
            String color,
            AnyDictionary metadata) {
        this.initialize(name, markedRange, color, metadata);
        this.nativeManager.className = this.getClass().getCanonicalName();
    }

    private native void initialize(
            String name,
            TimeRange markedRange,
            String color,
            AnyDictionary metadata);

    public static class MarkerBuilder {
        private String name = "";
        private TimeRange markedRange = new TimeRange();
        private String color = Color.green;
        private AnyDictionary metadata = new AnyDictionary();

        public MarkerBuilder() {
        }

        public Marker.MarkerBuilder setName(String name) {
            this.name = name;
            return this;
        }

        public Marker.MarkerBuilder setMarkedRange(TimeRange markedRange) {
            this.markedRange = markedRange;
            return this;
        }

        public Marker.MarkerBuilder setColor(String color) {
            this.color = color;
            return this;
        }

        public Marker.MarkerBuilder setMetadata(AnyDictionary metadata) {
            this.metadata = metadata;
            return this;
        }

        public Marker build() {
            return new Marker(this);
        }
    }

    /**
     * Get color string for this marker (for example: 'RED').
     *
     * @return
     */
    public native String getColor();

    /**
     * Set color string for this marker (for example: 'RED'), based on the
     * Color class.
     *
     * @param color String color
     */
    public native void setColor(String color);

    /**
     * Get range this marker applies to, relative to the Item this marker is
     * attached to (e.g. the Clip or Track that owns this marker).
     *
     * @return TimeRange this marker applies to.
     */
    public native TimeRange getMarkedRange();

    /**
     * Set range this marker applies to, relative to the Item this marker is
     * attached to (e.g. the Clip or Track that owns this marker).
     *
     * @param markedRange TimeRange this marker applies to.
     */
    public native void setMarkedRange(TimeRange markedRange);

    @Override
    public String toString() {
        return this.getClass().getCanonicalName() +
                "(" +
                "name=" + this.getName() +
                ", markedRange=" + this.getMarkedRange().toString() +
                ", metadata=" + this.getMetadata().toString() +
                ")";
    }
}
