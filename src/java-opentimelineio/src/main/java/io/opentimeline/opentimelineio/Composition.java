package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;
import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.util.Pair;

import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class Composition extends Item {

    protected Composition() {
    }

    Composition(OTIONative otioNative) {
        this.nativeManager = otioNative;
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

    public List<Composable> getChildren() {
        return Arrays.asList(getChildrenNative());
    }

    private native Composable[] getChildrenNative();

    public native void clearChildren();

    public void setChildren(List<Composable> children, ErrorStatus errorStatus) {
        Composable[] childrenArray = new Composable[children.size()];
        childrenArray = children.toArray(childrenArray);
        setChildrenNative(childrenArray, errorStatus);
    }

    private native void setChildrenNative(Composable[] children, ErrorStatus errorStatus);

    public native boolean insertChild(int index, Composable child, ErrorStatus errorStatus);

    public native boolean setChild(int index, Composable child, ErrorStatus errorStatus);

    public native boolean removeChild(int index, ErrorStatus errorStatus);

    public native boolean appendChild(Composable child, ErrorStatus errorStatus);

    public native boolean isParentOf(Composable composable);

    public native Pair<RationalTime, RationalTime> getHandlesOfChild(
            Composable child, ErrorStatus errorStatus);

    public native TimeRange getRangeOfChildAtIndex(int index, ErrorStatus errorStatus);

    public native TimeRange getTrimmedRangeOfChildAtIndex(int index, ErrorStatus errorStatus);

    public native TimeRange getRangeOfChild(Composable child, ErrorStatus errorStatus);

    public native TimeRange getTrimmedRangeOfChild(Composable child, ErrorStatus errorStatus);

    public native TimeRange trimChildRange(TimeRange childRange);

    public native boolean hasChild(Composable child);

    public native HashMap<Composable, TimeRange> getRangeOfAllChildren(ErrorStatus errorStatus);

    /**
     * Return the child that overlaps with time search_time.
     * <p>
     * search_time is in the space of self.
     * <p>
     * If shallow_search is false, will recurse into compositions.
     */
    public Composable getChildAtTime(RationalTime searchTime, boolean shallowSearch, ErrorStatus errorStatus) {
        HashMap<Composable, TimeRange> rangeOfAllChildren = this.getRangeOfAllChildren(errorStatus);
        List<Composable> children = this.getChildren();
        // find the first item whose endTimeExclusive is after the target
        int firstInsideRange = bisectLeft(
                children,
                searchTime,
                child -> rangeOfAllChildren.get(child).endTimeExclusive(),
                0, null);
        // find the last item whose startTime is before the target
        int lastInRange = bisectRight(
                children,
                searchTime,
                child -> rangeOfAllChildren.get(child).getStartTime(),
                firstInsideRange, null);
        // limit the search to children who are in the searchRange
        children = children.subList(firstInsideRange, lastInRange);
        Composable result = null;
        for (Composable potentialMatch : children) {
            if (rangeOfAllChildren.get(potentialMatch).overlaps(searchTime)) {
                result = potentialMatch;
                break;
            }
        }
        // if the search cannot or should not continue
        if (shallowSearch || !(result instanceof Composition))
            return result;

        // before you recurse, you have to transform the time into the
        // space of the child
        RationalTime childSearchTime = this.getTransformedTime(searchTime, (Composition) result, errorStatus);
        if (errorStatus.getOutcome() != ErrorStatus.Outcome.OK) throw new RuntimeException();
        return ((Composition) result).getChildAtTime(childSearchTime, shallowSearch, errorStatus);
    }

    public Composable getChildAtTime(RationalTime searchTime, ErrorStatus errorStatus) {
        return this.getChildAtTime(searchTime, false, errorStatus);
    }

    public <T extends Composable> Stream<T> eachChild(
            TimeRange searchRange, Class<T> descendedFrom, boolean shallowSearch, ErrorStatus errorStatus) {
        List<Composable> children;
        if (searchRange != null) {
            HashMap<Composable, TimeRange> rangeOfAllChildren = this.getRangeOfAllChildren(errorStatus);
            children = this.getChildren();
            // find the first item whose endTimeInclusive is after the
            // startTime of the searchRange
            int firstInsideRange = bisectLeft(
                    children,
                    searchRange.getStartTime(),
                    child -> rangeOfAllChildren.get(child).endTimeInclusive(),
                    0, null);
            // find the last item whose startTime is before the
            // endTimeInclusive of the searchRange
            int lastInRange = bisectRight(
                    children,
                    searchRange.endTimeInclusive(),
                    child -> rangeOfAllChildren.get(child).getStartTime(),
                    firstInsideRange, null);
            children = children.subList(firstInsideRange, lastInRange);
        } else {
            children = this.getChildren();
        }

        return children.stream()
                .flatMap(element -> {
                            Stream<T> currentElementStream = Stream.empty();
                            if (descendedFrom.isAssignableFrom(element.getClass()))
                                currentElementStream = Stream.concat(Stream.of(descendedFrom.cast(element)), currentElementStream);
                            Stream<T> nestedStream = Stream.empty();
                            if (!shallowSearch && element instanceof Composition) {
                                nestedStream = ((Composition) element).eachChild(
                                        searchRange == null ? null : this.getTransformedTimeRange(searchRange, ((Composition) element), errorStatus),
                                        descendedFrom,
                                        shallowSearch,
                                        errorStatus);
                            }
                            return Stream.concat(currentElementStream, nestedStream);
                        }
                );
    }

    public Stream<Composable> eachChild(TimeRange searchRange, boolean shallowSearch, ErrorStatus errorStatus) {
        return eachChild(searchRange, Composable.class, shallowSearch, errorStatus);
    }

    public <T extends Composable> Stream<T> eachChild(Class<T> descendedFrom, ErrorStatus errorStatus) {
        return eachChild(null, descendedFrom, false, errorStatus);
    }

    /**
     * Return the index of the last item in seqChildren such that all e in seqChildren[:index]
     * have keyFunction(e) <= target, and all e in seq[index:] have keyFunction(e) > target.
     * <p>
     * Thus, seqChildren.insert(index, value) will insert value after the rightmost item
     * such that meets the above condition.
     * <p>
     * lowerSearchBound and upperSearchBound bound the range of elements to be searched.
     * <p>
     * Assumes that seqChildren is already sorted.
     */
    private int bisectRight(
            List<Composable> seqChildren,
            RationalTime target,
            Function<Composable, RationalTime> keyFunction,
            Integer lowerSearchBound,
            Integer upperSearchBound) {
        if (lowerSearchBound == null)
            lowerSearchBound = 0;
        if (lowerSearchBound < 0)
            throw new IndexOutOfBoundsException("lowerSearchBound must be non-negative");
        if (upperSearchBound == null)
            upperSearchBound = seqChildren.size();

        while (lowerSearchBound < upperSearchBound) {
            int midPointIndex = Math.floorDiv(lowerSearchBound + upperSearchBound, 2);

            if (target.compareTo(keyFunction.apply(seqChildren.get(midPointIndex))) < 0) {
                upperSearchBound = midPointIndex;
            } else {
                lowerSearchBound = midPointIndex + 1;
            }
        }
        return lowerSearchBound;
    }

    /**
     * Return the index of the last item in seqChildren such that all e in seqChildren[:index]
     * have keyFunction(e) < target, and all e in seqChildren[index:] have keyFunction(e) >= target.
     * <p>
     * Thus, seqChildren.insert(index, value) will insert value before the leftmost item
     * such that meets the above condition.
     * <p>
     * lowerSearchBound and upperSearchBound bound the range of elements to be searched.
     * <p>
     * Assumes that seqChildren is already sorted.
     */
    private int bisectLeft(
            List<Composable> seqChildren,
            RationalTime target,
            Function<Composable, RationalTime> keyFunction,
            Integer lowerSearchBound,
            Integer upperSearchBound) {
        if (lowerSearchBound == null)
            lowerSearchBound = 0;
        if (lowerSearchBound < 0)
            throw new IndexOutOfBoundsException("lowerSearchBound must be non-negative");
        if (upperSearchBound == null)
            upperSearchBound = seqChildren.size();

        while (lowerSearchBound < upperSearchBound) {
            int midPointIndex = Math.floorDiv(lowerSearchBound + upperSearchBound, 2);

            if (keyFunction.apply(seqChildren.get(midPointIndex)).compareTo(target) < 0) {
                lowerSearchBound = midPointIndex + 1;
            } else {
                upperSearchBound = midPointIndex;
            }
        }
        return lowerSearchBound;
    }

    @Override
    public String toString() {
        return this.getClass().getCanonicalName() +
                "(" +
                "name=" + this.getName() +
                ", children=[" + this.getChildren()
                .stream().map(Objects::toString).collect(Collectors.joining(", ")) + "]" +
                ", sourceRange=" + this.getSourceRange() +
                ", metadata=" + this.getMetadata() +
                ")";
    }
}
