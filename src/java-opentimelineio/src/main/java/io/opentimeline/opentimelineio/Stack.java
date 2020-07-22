package io.opentimeline.opentimelineio;

import io.opentimeline.opentime.TimeRange;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

public class Stack extends Composition {

    protected Stack() {
    }

    public Stack(
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

    public Stack(Stack.StackBuilder builder) {
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
        this.initialize(
                name,
                sourceRange,
                metadata,
                (Effect[]) effects.toArray(),
                (Marker[]) markers.toArray());
    }

    private native void initialize(String name,
                                   TimeRange sourceRange,
                                   AnyDictionary metadata,
                                   Effect[] effects,
                                   Marker[] markers);

    public static class StackBuilder {
        private String name = "";
        private TimeRange sourceRange = null;
        private AnyDictionary metadata = new AnyDictionary();
        private List<Effect> effects = new ArrayList<>();
        private List<Marker> markers = new ArrayList<>();

        public StackBuilder() {
        }

        public Stack.StackBuilder setName(String name) {
            this.name = name;
            return this;
        }

        public Stack.StackBuilder setSourceRange(TimeRange sourceRange) {
            this.sourceRange = sourceRange;
            return this;
        }

        public Stack.StackBuilder setMetadata(AnyDictionary metadata) {
            this.metadata = metadata;
            return this;
        }

        public Stack.StackBuilder setEffects(List<Effect> effects) {
            this.effects = effects;
            return this;
        }

        public Stack.StackBuilder setMarkers(List<Marker> markers) {
            this.markers = markers;
            return this;
        }

        public Stack build() {
            return new Stack(this);
        }
    }

    public native TimeRange rangeOfChildAtIndex(int index, ErrorStatus errorStatus);

    public native TimeRange trimmedRangeOfChildAtIndex(int index, ErrorStatus errorStatus);

    public native TimeRange getAvailableRange(ErrorStatus errorStatus);

    public native HashMap<Composable, TimeRange> getRangeOfAllChildren(ErrorStatus errorStatus);
}
