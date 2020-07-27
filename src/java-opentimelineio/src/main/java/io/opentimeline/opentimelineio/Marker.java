package io.opentimeline.opentimelineio;

import io.opentimeline.opentime.TimeRange;

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

    public Marker(long nativeHandle) {
        this.nativeHandle = nativeHandle;
    }

    public Marker(SerializableObject serializableObject) {
        this.nativeHandle = serializableObject.nativeHandle;
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
        this.className = this.getClass().getCanonicalName();
        this.initialize(name, markedRange, color, metadata);
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

    public native String getColor();

    public native void setColor(String color);

    public native TimeRange getMarkedRange();

    public native void setMarkedRange(TimeRange markedRange);
}
