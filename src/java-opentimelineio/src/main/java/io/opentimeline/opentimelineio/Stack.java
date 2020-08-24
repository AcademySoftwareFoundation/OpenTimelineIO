package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;
import io.opentimeline.opentime.TimeRange;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.stream.Stream;

/**
 * A stack represents a series of composables. Composables that are arranged such
 * that their start times are at the same point.
 * Most commonly, this would be a series of Track objects that then
 * contain clips.  The 0 time of those tracks would coincide with the 0-time of
 * the stack.
 * Stacks are in compositing order, with later children obscuring earlier
 * children. In other words, from bottom to top. If a stack has three children,
 * [A, B, C], C is above B which is above A.
 * A stack is the length of its longest child.  If a child ends before the other
 * children, then an earlier index child would be visible before it.
 */
public class Stack extends Composition {

    protected Stack() {
    }

    Stack(OTIONative otioNative) {
        this.nativeManager = otioNative;
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
        Effect[] effectsArray = new Effect[effects.size()];
        effectsArray = effects.toArray(effectsArray);
        Marker[] markersArray = new Marker[markers.size()];
        markersArray = markers.toArray(markersArray);
        this.initialize(
                name,
                sourceRange,
                metadata,
                effectsArray,
                markersArray);
        this.nativeManager.className = this.getClass().getCanonicalName();
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

    public Stream<Clip> eachClip(
            TimeRange searchRange, ErrorStatus errorStatus) {
        return this.eachChild(searchRange, Clip.class, false, errorStatus);
    }

    public Stream<Clip> eachClip(ErrorStatus errorStatus) {
        return this.eachChild(null, errorStatus);
    }
}
