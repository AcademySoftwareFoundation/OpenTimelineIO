package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;
import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.util.Pair;

import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * Base class for an OTIO Item that contains other Items.
 * Should be subclassed (for example by Track and Stack), not used directly.
 */
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

    /**
     * Returns a label specifying the kind of composition.
     *
     * @return the composition kind
     */
    public native String getCompositionKind();

    /**
     * @return all the chidlren held by this Composition.
     */
    public List<Composable> getChildren() {
        return Arrays.asList(getChildrenNative());
    }

    private native Composable[] getChildrenNative();

    /**
     * Remove all children from the composition and clear their parents.
     */
    public native void clearChildren();

    /**
     * Set children for this Composition.
     *
     * @param children    a list of Composables
     * @param errorStatus errorStatus to report an error if any child cannot be added.
     */
    public void setChildren(List<Composable> children, ErrorStatus errorStatus) {
        Composable[] childrenArray = new Composable[children.size()];
        childrenArray = children.toArray(childrenArray);
        setChildrenNative(childrenArray, errorStatus);
    }

    private native void setChildrenNative(Composable[] children, ErrorStatus errorStatus);

    /**
     * Insert a child Composable at an index.
     *
     * @param index       index at which child is to be inserted.
     * @param child       child Composable to be inserted.
     * @param errorStatus errorStatus to report an error if child cannot be inserted.
     * @return was the child inserted successfully?
     */
    public native boolean insertChild(int index, Composable child, ErrorStatus errorStatus);

    /**
     * Set the child at a particular index. The needs to exist for the child to be set.
     *
     * @param index       index to set the child
     * @param child       child Composable to be set
     * @param errorStatus errorStatus to report an error if child cannot be set.
     * @return was the child set successfully?
     */
    public native boolean setChild(int index, Composable child, ErrorStatus errorStatus);

    /**
     * Remove the child at any index.
     *
     * @param index       index from which the child needs to be removed.
     * @param errorStatus errorStatus to report an error if child cannot be removed.
     * @return was the child removed successfully?
     */
    public native boolean removeChild(int index, ErrorStatus errorStatus);

    /**
     * Append the child to the end of the Composition.
     *
     * @param child       child to be appended
     * @param errorStatus errorStatus to report an error if child cannot be appended.
     * @return was the child appended successfully?
     */
    public native boolean appendChild(Composable child, ErrorStatus errorStatus);

    /**
     * @param composable Composable to check ancestry of
     * @return true if this is a parent or ancestor of the composable.
     */
    public native boolean isParentOf(Composable composable);

    /**
     * If media beyond the ends of this child are visible due to adjacent
     * Transitions (only applicable in a Track) then this will return the
     * head and tail offsets as a Pair of RationalTime objects. If no handles
     * are present on either side, then null is returned instead of a
     * RationalTime.
     *
     * @param child       child Composable to get handles
     * @param errorStatus errorStatus to report error while fetching handles
     * @return head and tail offsets as a Pair of RationalTime objects
     */
    public native Pair<RationalTime, RationalTime> getHandlesOfChild(
            Composable child, ErrorStatus errorStatus);

    /**
     * Return the range of a child item in the time range of this composition.
     * For example, with a track:
     * [ClipA][ClipB][ClipC]
     * this.getRangeOfChildAtIndex(2, errorStatus) will return:
     * TimeRange(ClipA.duration + ClipB.duration, ClipC.duration)
     *
     * @param index       index of child whose range is to be fetched
     * @param errorStatus errorStatus to report error if range cannot be fetched
     * @return range of child at index
     */
    public native TimeRange getRangeOfChildAtIndex(int index, ErrorStatus errorStatus);

    /**
     * Return the trimmed range of the child item at index in the time
     * range of this composition.
     * <p>
     * For example, with a track:
     * [     ]
     * [ClipA][ClipB][ClipC]
     * The range of index 2 (ClipC) will be just like
     * getRangeOfChildAtIndex() but trimmed based on this Composition's
     * sourceRange.
     *
     * @param index       index of child whose trimmed range is to be fetched
     * @param errorStatus errorStatus to report error if trimmed range cannot be fetched
     * @return trimmed range of child at index
     */
    public native TimeRange getTrimmedRangeOfChildAtIndex(int index, ErrorStatus errorStatus);

    /**
     * The range of the child not trimmed based on this composition's sourceRange.
     * For example:
     * |     [-----]     | seq
     * [-----------------] Clip A
     * If ClipA has duration 17, and seq has sourceRange: 5, duration 15,
     * seq.getRangeOfChild(Clip A) will return (0, 17)
     * ignoring the sourceRange of seq.
     * <p>
     * To get the range of the child with the sourceRange applied, use the
     * getTrimmedRangeOfChild() method.
     *
     * @param child       child Composable whose range is to be fetched
     * @param errorStatus errorStatus to report error if range cannot be fetched
     * @return range of the child not trimmed based on this composition's sourceRange
     */
    public native TimeRange getRangeOfChild(Composable child, ErrorStatus errorStatus);

    /**
     * Get range of the child, after the sourceRange is applied.
     * Example
     * |     [-----]     | seq
     * [-----------------] Clip A
     * If ClipA has duration 17, and seq has sourceRange: 5, duration 10,
     * seq.getTrimmedRangeOfChild(Clip A) will return (5, 10)
     * Which is trimming the range according to the sourceRange of seq.
     * To get the range of the child without the sourceRange applied, use the
     * getRangeOfChild() method.
     * Another example
     * |  [-----]   | seq sourceRange starts on frame 4 and goes to frame 8
     * [ClipA][ClipB] (each 6 frames long)
     * <p>
     * seq.getRangeOfChild(ClipA) = 0, duration 6
     * seq.getTrimmedRangeOfChild(ClipB) = 4, duration 2
     *
     * @param child       child Composable whose trimmed range is to be fetched
     * @param errorStatus errorStatus to report error if range cannot be fetched
     * @return range of the child trimmed based on this composition's sourceRange
     */
    public native TimeRange getTrimmedRangeOfChild(Composable child, ErrorStatus errorStatus);

    /**
     * Trim childRange to this.sourceRange
     *
     * @param childRange range to be trimmed
     * @return null if childRange has no intersection with this.sourceRange, else trimmed range
     */
    public native TimeRange trimChildRange(TimeRange childRange);

    /**
     * @param child child to find
     * @return does the composition contain the child?
     */
    public native boolean hasChild(Composable child);

    /**
     * Return a HashMap mapping children to their range in this object.
     *
     * @param errorStatus errorStatus to report any error while fetching ranges
     * @return a HashMap mapping children to their range in this object
     */
    public native HashMap<Composable, TimeRange> getRangeOfAllChildren(ErrorStatus errorStatus);

    /**
     * Return the child that overlaps with time searchTime.
     * searchTime is in the space of self.
     * If shallowSearch is false, will recurse into compositions.
     *
     * @param searchTime    the time at which the child is to be fetched
     * @param shallowSearch should the algorithm recurse into compositions or not?
     * @param errorStatus   errorStatus to report any error while fetching the child
     * @return the child that overlaps with time searchTime
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

    /**
     * Return the child that overlaps with time searchTime.
     * searchTime is in the space of self.
     * This function will recurse into compositions.
     *
     * @param searchTime  the time at which the child is to be fetched
     * @param errorStatus errorStatus to report any error while fetching the child
     * @return the child that overlaps with time searchTime
     */
    public Composable getChildAtTime(RationalTime searchTime, ErrorStatus errorStatus) {
        return this.getChildAtTime(searchTime, false, errorStatus);
    }

    /**
     * Stream that returns each child of specified type contained in the composition in
     * the order in which it is found.
     *
     * @param searchRange   if not null, only children whose range overlaps with the search range will be in the stream.
     * @param descendedFrom only children who are a descendent of the descendedFrom type will be in the stream
     * @param shallowSearch should the algorithm recurse into compositions or not?
     * @param errorStatus   errorStatus to report any error while iterating
     * @param <T>           type of children to fetch
     * @return a Stream consisting of all the children of specified type in the composition in the order in which it is found
     */
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

    /**
     * Stream that returns each child contained in the composition in
     * the order in which it is found.
     *
     * @param searchRange   if not null, only children whose range overlaps with the search range will be in the stream.
     * @param shallowSearch should the algorithm recurse into compositions or not?
     * @param errorStatus   errorStatus to report any error while iterating
     * @return a Stream consisting of all the children in the composition (in the searchRange) in the order in which it is found
     */
    public Stream<Composable> eachChild(TimeRange searchRange, boolean shallowSearch, ErrorStatus errorStatus) {
        return eachChild(searchRange, Composable.class, shallowSearch, errorStatus);
    }

    /**
     * Stream that returns each child of specified type contained in the composition in
     * the order in which it is found. This stream will recurse into compositions.
     *
     * @param descendedFrom only children who are a descendent of the descendedFrom type will be in the stream
     * @param errorStatus   errorStatus to report any error while iterating
     * @param <T>           type of children to fetch
     * @return a Stream consisting of all the children of specified type in the composition in the order in which it is found
     */
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
