package io.opentimeline;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.opentime.TimeTransform;
import io.opentimeline.opentimelineio.*;

import java.lang.ref.ReferenceQueue;
import java.util.LinkedList;
import java.util.List;

/**
 * A singleton factory class that helps in creating all OTIO objects.
 * It is expected that the developers use this Factory to create objects and not the Classes' constructors.
 * After creation of each object the Factory adds a PhantomReference of the object to a ReferenceQueue.
 * Whenever the object is Garbage Collected it will be available for polling in the reference queue and
 * the native memory allocated for the object can be freed.
 * <p>
 * The factory does some minor cleanup everytime you interact with it, but the developers are expected to
 * setup a mechanism to call the cleanUp() method at regular intervals.
 */
public class OTIOFactory {

    private ReferenceQueue<OTIONative> otioNativeReferenceQueue = new ReferenceQueue<>();
    private List<OTIOFinalizer> references = new LinkedList();

    private static final OTIOFactory instance = new OTIOFactory();

    private OTIOFactory() {
    }

    public static OTIOFactory getInstance() {
        return instance;
    }

    void registerObject(OTIOObject otioObject) {
        references.add(new OTIOFinalizer(otioObject.getNativeManager(), otioNativeReferenceQueue));
    }

    // Any ////////////////////////////////////////////////////////////////////

    public <T> Any createAny(T value) {
        cleanUp();
        Any any = new Any(value);
        references.add(new OTIOFinalizer(any.getNativeManager(), otioNativeReferenceQueue));
        return any;
    }

    ///////////////////////////////////////////////////////////////////////////

    // AnyDictionary //////////////////////////////////////////////////////////

    public AnyDictionary createAnyDictionary() {
        cleanUp();
        AnyDictionary anyDictionary = new AnyDictionary();
        references.add(new OTIOFinalizer(anyDictionary.getNativeManager(), otioNativeReferenceQueue));
        return anyDictionary;
    }

    public AnyDictionary.Iterator getAnyDictionaryIterator(AnyDictionary anyDictionary) {
        cleanUp();
        AnyDictionary.Iterator iterator = anyDictionary.iterator();
        references.add(new OTIOFinalizer(iterator.getNativeManager(), otioNativeReferenceQueue));
        return iterator;
    }

    ///////////////////////////////////////////////////////////////////////////

    // AnyVector //////////////////////////////////////////////////////////////

    public AnyVector createAnyVector() {
        cleanUp();
        AnyVector anyVector = new AnyVector();
        references.add(new OTIOFinalizer(anyVector.getNativeManager(), otioNativeReferenceQueue));
        return anyVector;
    }

    public AnyVector.Iterator getAnyVectorIterator(AnyVector anyVector) {
        cleanUp();
        AnyVector.Iterator iterator = anyVector.iterator();
        references.add(new OTIOFinalizer(iterator.getNativeManager(), otioNativeReferenceQueue));
        return iterator;
    }

    ///////////////////////////////////////////////////////////////////////////

    // Clip ///////////////////////////////////////////////////////////////////

    public Clip createClip(
            String name,
            MediaReference mediaReference,
            TimeRange sourceRange,
            AnyDictionary metadata) {
        cleanUp();
        Clip clip = new Clip(name, mediaReference, sourceRange, metadata);
        references.add(new OTIOFinalizer(clip.getNativeManager(), otioNativeReferenceQueue));
        return clip;
    }

    public Clip createClip(Clip.ClipBuilder builder) {
        cleanUp();
        Clip clip = builder.build();
        references.add(new OTIOFinalizer(clip.getNativeManager(), otioNativeReferenceQueue));
        return clip;
    }

    ///////////////////////////////////////////////////////////////////////////

    // Composable /////////////////////////////////////////////////////////////

    public Composable createComposable(String name, AnyDictionary metadata) {
        cleanUp();
        Composable composable = new Composable(name, metadata);
        references.add(new OTIOFinalizer(composable.getNativeManager(), otioNativeReferenceQueue));
        return composable;
    }

    public Composable createComposable(String name) {
        cleanUp();
        Composable composable = new Composable(name);
        references.add(new OTIOFinalizer(composable.getNativeManager(), otioNativeReferenceQueue));
        return composable;
    }

    public Composable createComposable(AnyDictionary metadata) {
        cleanUp();
        Composable composable = new Composable(metadata);
        references.add(new OTIOFinalizer(composable.getNativeManager(), otioNativeReferenceQueue));
        return composable;
    }

    public Composable createComposable(Composable.ComposableBuilder builder) {
        cleanUp();
        Composable composable = builder.build();
        references.add(new OTIOFinalizer(composable.getNativeManager(), otioNativeReferenceQueue));
        return composable;
    }
    ///////////////////////////////////////////////////////////////////////////

    // Composition ////////////////////////////////////////////////////////////

    public Composition createComposition(
            String name,
            TimeRange sourceRange,
            AnyDictionary metadata,
            List<Effect> effects,
            List<Marker> markers) {
        cleanUp();
        Composition composition = new Composition(
                name,
                sourceRange,
                metadata,
                effects,
                markers);
        references.add(new OTIOFinalizer(composition.getNativeManager(), otioNativeReferenceQueue));
        return composition;
    }

    public Composition createComposition(Composition.CompositionBuilder builder) {
        cleanUp();
        Composition composition = builder.build();
        references.add(new OTIOFinalizer(composition.getNativeManager(), otioNativeReferenceQueue));
        return composition;
    }

    ///////////////////////////////////////////////////////////////////////////

    // Effect /////////////////////////////////////////////////////////////////

    public Effect createEffect(
            String name,
            String effectName,
            AnyDictionary metadata) {
        cleanUp();
        Effect effect = new Effect(name, effectName, metadata);
        references.add(new OTIOFinalizer(effect.getNativeManager(), otioNativeReferenceQueue));
        return effect;
    }

    public Effect createEffect(Effect.EffectBuilder builder) {
        cleanUp();
        Effect effect = builder.build();
        references.add(new OTIOFinalizer(effect.getNativeManager(), otioNativeReferenceQueue));
        return effect;
    }

    ///////////////////////////////////////////////////////////////////////////

    // io.opentimeline.opentimelineio.ErrorStatus /////////////////////////////

    public io.opentimeline.opentimelineio.ErrorStatus createOpenTimelineIOErrorStatus() {
        cleanUp();
        ErrorStatus errorStatus = new ErrorStatus();
        references.add(new OTIOFinalizer(errorStatus.getNativeManager(), otioNativeReferenceQueue));
        return errorStatus;
    }

    ///////////////////////////////////////////////////////////////////////////

    // io.opentimeline.opentime.ErrorStatus ///////////////////////////////////

    public io.opentimeline.opentime.ErrorStatus createOpentimeIOErrorStatus() {
        cleanUp();
        io.opentimeline.opentime.ErrorStatus errorStatus = new io.opentimeline.opentime.ErrorStatus();
        references.add(new OTIOFinalizer(errorStatus.getNativeManager(), otioNativeReferenceQueue));
        return errorStatus;
    }

    ///////////////////////////////////////////////////////////////////////////

    // ExternalReference //////////////////////////////////////////////////////

    public ExternalReference createExternalReference(
            String targetURL,
            TimeRange availableRange,
            AnyDictionary metadata) {
        cleanUp();
        ExternalReference externalReference = new ExternalReference(targetURL, availableRange, metadata);
        references.add(new OTIOFinalizer(externalReference.getNativeManager(), otioNativeReferenceQueue));
        return externalReference;
    }

    public ExternalReference createExternalReference(ExternalReference.ExternalReferenceBuilder builder) {
        cleanUp();
        ExternalReference externalReference = builder.build();
        references.add(new OTIOFinalizer(externalReference.getNativeManager(), otioNativeReferenceQueue));
        return externalReference;
    }

    ///////////////////////////////////////////////////////////////////////////

    // FreezeFrame ////////////////////////////////////////////////////////////

    public FreezeFrame createFreezeFrame(String name, AnyDictionary metadata) {
        cleanUp();
        FreezeFrame freezeFrame = new FreezeFrame(name, metadata);
        references.add(new OTIOFinalizer(freezeFrame.getNativeManager(), otioNativeReferenceQueue));
        return freezeFrame;
    }

    public FreezeFrame createFreezeFrame(FreezeFrame.FreezeFrameBuilder builder) {
        cleanUp();
        FreezeFrame freezeFrame = builder.build();
        references.add(new OTIOFinalizer(freezeFrame.getNativeManager(), otioNativeReferenceQueue));
        return freezeFrame;
    }

    ///////////////////////////////////////////////////////////////////////////

    // Gap ////////////////////////////////////////////////////////////////////

    public Gap createGap(
            TimeRange sourceRange,
            String name,
            List<Effect> effects,
            List<Marker> markers,
            AnyDictionary metadata) {
        cleanUp();
        Gap gap = new Gap(sourceRange, name, effects, markers, metadata);
        references.add(new OTIOFinalizer(gap.getNativeManager(), otioNativeReferenceQueue));
        return gap;
    }

    public Gap createGap(
            RationalTime duration,
            String name,
            List<Effect> effects,
            List<Marker> markers,
            AnyDictionary metadata) {
        cleanUp();
        Gap gap = new Gap(duration, name, effects, markers, metadata);
        references.add(new OTIOFinalizer(gap.getNativeManager(), otioNativeReferenceQueue));
        return gap;
    }

    public Gap createGap(Gap.GapBuilder builder) {
        cleanUp();
        Gap gap = builder.build();
        references.add(new OTIOFinalizer(gap.getNativeManager(), otioNativeReferenceQueue));
        return gap;
    }

    ///////////////////////////////////////////////////////////////////////////

    // GeneratorReference /////////////////////////////////////////////////////

    public GeneratorReference createGeneratorReference(
            String name,
            String generatorKind,
            TimeRange availableRange,
            AnyDictionary parameters,
            AnyDictionary metadata) {
        cleanUp();
        GeneratorReference generatorReference = new GeneratorReference(
                name,
                generatorKind,
                availableRange,
                parameters,
                metadata);
        references.add(new OTIOFinalizer(generatorReference.getNativeManager(), otioNativeReferenceQueue));
        return generatorReference;
    }

    public GeneratorReference createGeneratorReference(GeneratorReference.GeneratorReferenceBuilder builder) {
        cleanUp();
        GeneratorReference generatorReference = builder.build();
        references.add(new OTIOFinalizer(generatorReference.getNativeManager(), otioNativeReferenceQueue));
        return generatorReference;
    }

    ///////////////////////////////////////////////////////////////////////////

    // ImageSequenceReference /////////////////////////////////////////////////

    public ImageSequenceReference createImageSequenceReference(
            String targetURLBase,
            String namePrefix,
            String nameSuffix,
            int startFrame,
            int frameStep,
            double rate,
            int frameZeroPadding,
            ImageSequenceReference.MissingFramePolicy missingFramePolicy,
            TimeRange availableRange,
            AnyDictionary metadata) {
        cleanUp();
        ImageSequenceReference imageSequenceReference = new ImageSequenceReference(
                targetURLBase,
                namePrefix,
                nameSuffix,
                startFrame,
                frameStep,
                rate,
                frameZeroPadding,
                missingFramePolicy,
                availableRange,
                metadata);
        references.add(new OTIOFinalizer(imageSequenceReference.getNativeManager(), otioNativeReferenceQueue));
        return imageSequenceReference;
    }

    public ImageSequenceReference createImageSequenceReference(
            ImageSequenceReference.ImageSequenceReferenceBuilder builder) {
        cleanUp();
        ImageSequenceReference imageSequenceReference = builder.build();
        references.add(new OTIOFinalizer(imageSequenceReference.getNativeManager(), otioNativeReferenceQueue));
        return imageSequenceReference;
    }

    ///////////////////////////////////////////////////////////////////////////

    // Item ///////////////////////////////////////////////////////////////////

    public Item createItem(
            String name,
            TimeRange sourceRange,
            AnyDictionary metadata,
            List<Effect> effects,
            List<Marker> markers) {
        cleanUp();
        Item item = new Item(name, sourceRange, metadata, effects, markers);
        references.add(new OTIOFinalizer(item.getNativeManager(), otioNativeReferenceQueue));
        return item;
    }

    public Item createItem(Item.ItemBuilder builder) {
        cleanUp();
        Item item = builder.build();
        references.add(new OTIOFinalizer(item.getNativeManager(), otioNativeReferenceQueue));
        return item;
    }

    ///////////////////////////////////////////////////////////////////////////

    // LinearTimeWarp /////////////////////////////////////////////////////////

    public LinearTimeWarp createLinearTimeWarp(
            String name,
            String effectName,
            double timeScalar,
            AnyDictionary metadata) {
        cleanUp();
        LinearTimeWarp linearTimeWarp = new LinearTimeWarp(name, effectName, timeScalar, metadata);
        references.add(new OTIOFinalizer(linearTimeWarp.getNativeManager(), otioNativeReferenceQueue));
        return linearTimeWarp;
    }

    public LinearTimeWarp createLinearTimeWarp(LinearTimeWarp.LinearTimeWarpBuilder builder) {
        cleanUp();
        LinearTimeWarp linearTimeWarp = builder.build();
        references.add(new OTIOFinalizer(linearTimeWarp.getNativeManager(), otioNativeReferenceQueue));
        return linearTimeWarp;
    }

    ///////////////////////////////////////////////////////////////////////////

    // Marker /////////////////////////////////////////////////////////

    public Marker createMarker(String name, TimeRange markedRange, String color, AnyDictionary metadata) {
        cleanUp();
        Marker marker = new Marker(name, markedRange, color, metadata);
        references.add(new OTIOFinalizer(marker.getNativeManager(), otioNativeReferenceQueue));
        return marker;
    }

    public Marker createMarker(Marker.MarkerBuilder builder) {
        cleanUp();
        Marker marker = builder.build();
        references.add(new OTIOFinalizer(marker.getNativeManager(), otioNativeReferenceQueue));
        return marker;
    }

    ///////////////////////////////////////////////////////////////////

    // MediaReference /////////////////////////////////////////////////

    public MediaReference createMediaReference(String name, TimeRange availableRange, AnyDictionary metadata) {
        cleanUp();
        MediaReference mediaReference = new MediaReference(name, availableRange, metadata);
        references.add(new OTIOFinalizer(mediaReference.getNativeManager(), otioNativeReferenceQueue));
        return mediaReference;
    }

    public MediaReference createMediaReference(MediaReference.MediaReferenceBuilder builder) {
        cleanUp();
        MediaReference mediaReference = builder.build();
        references.add(new OTIOFinalizer(mediaReference.getNativeManager(), otioNativeReferenceQueue));
        return mediaReference;
    }

    ///////////////////////////////////////////////////////////////////

    // MediaReference /////////////////////////////////////////////////

    public MissingReference createMissingReference(String name, TimeRange availableRange, AnyDictionary metadata) {
        cleanUp();
        MissingReference mediaReference = new MissingReference(name, availableRange, metadata);
        references.add(new OTIOFinalizer(mediaReference.getNativeManager(), otioNativeReferenceQueue));
        return mediaReference;
    }

    public MissingReference createMediaReference(MissingReference.MissingReferenceBuilder builder) {
        cleanUp();
        MissingReference mediaReference = builder.build();
        references.add(new OTIOFinalizer(mediaReference.getNativeManager(), otioNativeReferenceQueue));
        return mediaReference;
    }

    ///////////////////////////////////////////////////////////////////

    // SerializableCollection /////////////////////////////////////////

    public SerializableCollection createSerializableCollection(
            String name,
            List<SerializableObject> children,
            AnyDictionary metadata) {
        cleanUp();
        SerializableCollection serializableCollection = new SerializableCollection(name, children, metadata);
        references.add(new OTIOFinalizer(serializableCollection.getNativeManager(), otioNativeReferenceQueue));
        return serializableCollection;
    }

    public SerializableCollection createSerializableCollection(SerializableCollection.SerializableCollectionBuilder builder) {
        cleanUp();
        SerializableCollection serializableCollection = builder.build();
        references.add(new OTIOFinalizer(serializableCollection.getNativeManager(), otioNativeReferenceQueue));
        return serializableCollection;
    }

    ///////////////////////////////////////////////////////////////////

    // SerializableObject /////////////////////////////////////////

    public SerializableObject createSerializableObject() {
        cleanUp();
        SerializableObject serializableObject = new SerializableObject();
        references.add(new OTIOFinalizer(serializableObject.getNativeManager(), otioNativeReferenceQueue));
        return serializableObject;
    }

    ///////////////////////////////////////////////////////////////

    // SerializableObjectWithMetadata /////////////////////////////

    public SerializableObjectWithMetadata createSerializableObjectWithMetadata(String name, AnyDictionary metadata) {
        cleanUp();
        SerializableObjectWithMetadata serializableObjectWithMetadata = new SerializableObjectWithMetadata(name, metadata);
        references.add(new OTIOFinalizer(serializableObjectWithMetadata.getNativeManager(), otioNativeReferenceQueue));
        return serializableObjectWithMetadata;
    }

    public SerializableObjectWithMetadata createSerializableObjectWithMetadata(String name) {
        cleanUp();
        SerializableObjectWithMetadata serializableObjectWithMetadata = new SerializableObjectWithMetadata(name);
        references.add(new OTIOFinalizer(serializableObjectWithMetadata.getNativeManager(), otioNativeReferenceQueue));
        return serializableObjectWithMetadata;
    }

    public SerializableObjectWithMetadata createSerializableObjectWithMetadata(AnyDictionary metadata) {
        cleanUp();
        SerializableObjectWithMetadata serializableObjectWithMetadata = new SerializableObjectWithMetadata(metadata);
        references.add(new OTIOFinalizer(serializableObjectWithMetadata.getNativeManager(), otioNativeReferenceQueue));
        return serializableObjectWithMetadata;
    }

    public SerializableObjectWithMetadata createSerializableObjectWithMetadata(
            SerializableObjectWithMetadata.SerializableObjectWithMetadataBuilder builder) {
        cleanUp();
        SerializableObjectWithMetadata serializableObjectWithMetadata = builder.build();
        references.add(new OTIOFinalizer(serializableObjectWithMetadata.getNativeManager(), otioNativeReferenceQueue));
        return serializableObjectWithMetadata;
    }

    ///////////////////////////////////////////////////////////////

    // Stack //////////////////////////////////////////////////////

    public Stack createStack(
            String name,
            TimeRange sourceRange,
            AnyDictionary metadata,
            List<Effect> effects,
            List<Marker> markers) {
        cleanUp();
        Stack stack = new Stack(name, sourceRange, metadata, effects, markers);
        references.add(new OTIOFinalizer(stack.getNativeManager(), otioNativeReferenceQueue));
        return stack;
    }

    public Stack createStack(Stack.StackBuilder builder) {
        cleanUp();
        Stack stack = builder.build();
        references.add(new OTIOFinalizer(stack.getNativeManager(), otioNativeReferenceQueue));
        return stack;
    }

    ///////////////////////////////////////////////////////////////

    // TimeEffect /////////////////////////////////////////////////

    public TimeEffect createTimeEffect(String name, String effectName, AnyDictionary metadata) {
        cleanUp();
        TimeEffect timeEffect = new TimeEffect(name, effectName, metadata);
        references.add(new OTIOFinalizer(timeEffect.getNativeManager(), otioNativeReferenceQueue));
        return timeEffect;
    }

    public TimeEffect createTimeEffect(TimeEffect.TimeEffectBuilder builder) {
        cleanUp();
        TimeEffect timeEffect = builder.build();
        references.add(new OTIOFinalizer(timeEffect.getNativeManager(), otioNativeReferenceQueue));
        return timeEffect;
    }

    ///////////////////////////////////////////////////////////////

    // Timeline ///////////////////////////////////////////////////

    public Timeline createTimeline(String name, RationalTime globalStartTime, AnyDictionary metadata) {
        cleanUp();
        Timeline timeline = new Timeline(name, globalStartTime, metadata);
        references.add(new OTIOFinalizer(timeline.getNativeManager(), otioNativeReferenceQueue));
        return timeline;
    }

    public Timeline createTimeline(Timeline.TimelineBuilder builder) {
        cleanUp();
        Timeline timeline = builder.build();
        references.add(new OTIOFinalizer(timeline.getNativeManager(), otioNativeReferenceQueue));
        return timeline;
    }

    ///////////////////////////////////////////////////////////////

    // Track //////////////////////////////////////////////////////

    public Track createTrack(String name, TimeRange sourceRange, String kind, AnyDictionary metadata) {
        cleanUp();
        Track track = new Track(name, sourceRange, kind, metadata);
        references.add(new OTIOFinalizer(track.getNativeManager(), otioNativeReferenceQueue));
        return track;
    }

    public Track createTrack(Track.TrackBuilder builder) {
        cleanUp();
        Track track = builder.build();
        references.add(new OTIOFinalizer(track.getNativeManager(), otioNativeReferenceQueue));
        return track;
    }

    ///////////////////////////////////////////////////////////////

    // Transition /////////////////////////////////////////////////

    public Transition createTransition(
            String name,
            String transitionType,
            RationalTime inOffset,
            RationalTime outOffset,
            AnyDictionary metadata) {
        cleanUp();
        Transition transition = new Transition(
                name,
                transitionType,
                inOffset,
                outOffset,
                metadata);
        references.add(new OTIOFinalizer(transition.getNativeManager(), otioNativeReferenceQueue));
        return transition;
    }

    public Transition createTransition(Transition.TransitionBuilder builder) {
        cleanUp();
        Transition transition = builder.build();
        references.add(new OTIOFinalizer(transition.getNativeManager(), otioNativeReferenceQueue));
        return transition;
    }

    ///////////////////////////////////////////////////////////////

    // UnknownSchema //////////////////////////////////////////////

    public UnknownSchema createUnknownSchema(String originalSchemaName, int originalSchemaVersion) {
        cleanUp();
        UnknownSchema unknownSchema = new UnknownSchema(originalSchemaName, originalSchemaVersion);
        references.add(new OTIOFinalizer(unknownSchema.getNativeManager(), otioNativeReferenceQueue));
        return unknownSchema;
    }

    public UnknownSchema createUnknownSchema(UnknownSchema.UnknownSchemaBuilder builder) {
        cleanUp();
        UnknownSchema unknownSchema = builder.build();
        references.add(new OTIOFinalizer(unknownSchema.getNativeManager(), otioNativeReferenceQueue));
        return unknownSchema;
    }

    ///////////////////////////////////////////////////////////////

    public void cleanUp() {
        OTIOFinalizer finalizer = (OTIOFinalizer) otioNativeReferenceQueue.poll();
        if (finalizer != null) {
            System.out.println("Here");
            finalizer.cleanUp();
            references.remove(finalizer);
        }
    }
}
