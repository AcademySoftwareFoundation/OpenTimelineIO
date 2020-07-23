package io.opentimeline;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.opentime.TimeTransform;
import io.opentimeline.opentimelineio.*;

import java.lang.ref.ReferenceQueue;
import java.util.LinkedList;
import java.util.List;

public class OTIOFactory {

    private ReferenceQueue<OTIONative> otioNativeReferenceQueue = new ReferenceQueue<>();
    private List<OTIOFinalizer> references = new LinkedList();

    private static final OTIOFactory instance = new OTIOFactory();

    private OTIOFactory() {
    }

    public static OTIOFactory getInstance() {
        return instance;
    }

    // Any ////////////////////////////////////////////////////////////////////

    public Any createAny(boolean v) {
        cleanUp();
        Any any = new Any(v);
        references.add(new OTIOFinalizer(any, otioNativeReferenceQueue));
        return any;
    }

    public Any createAny(int v) {
        cleanUp();
        Any any = new Any(v);
        references.add(new OTIOFinalizer(any, otioNativeReferenceQueue));
        return any;
    }

    public Any createAny(double v) {
        cleanUp();
        Any any = new Any(v);
        references.add(new OTIOFinalizer(any, otioNativeReferenceQueue));
        return any;
    }

    public Any createAny(String v) {
        cleanUp();
        Any any = new Any(v);
        references.add(new OTIOFinalizer(any, otioNativeReferenceQueue));
        return any;
    }

    public Any createAny(RationalTime v) {
        cleanUp();
        Any any = new Any(v);
        references.add(new OTIOFinalizer(any, otioNativeReferenceQueue));
        return any;
    }

    public Any createAny(TimeRange v) {
        cleanUp();
        Any any = new Any(v);
        references.add(new OTIOFinalizer(any, otioNativeReferenceQueue));
        return any;
    }

    public Any createAny(TimeTransform v) {
        cleanUp();
        Any any = new Any(v);
        references.add(new OTIOFinalizer(any, otioNativeReferenceQueue));
        return any;
    }

    public Any createAny(AnyDictionary v) {
        cleanUp();
        Any any = new Any(v);
        references.add(new OTIOFinalizer(any, otioNativeReferenceQueue));
        return any;
    }

    public Any createAny(AnyVector v) {
        cleanUp();
        Any any = new Any(v);
        references.add(new OTIOFinalizer(any, otioNativeReferenceQueue));
        return any;
    }

    public Any createAny(SerializableObject v) {
        cleanUp();
        Any any = new Any(v);
        references.add(new OTIOFinalizer(any, otioNativeReferenceQueue));
        return any;
    }
    ///////////////////////////////////////////////////////////////////////////

    // AnyDictionary //////////////////////////////////////////////////////////

    public AnyDictionary createAnyDictionary() {
        cleanUp();
        AnyDictionary anyDictionary = new AnyDictionary();
        references.add(new OTIOFinalizer(anyDictionary, otioNativeReferenceQueue));
        return anyDictionary;
    }

    public AnyDictionary.Iterator getAnyDictionaryIterator(AnyDictionary anyDictionary) {
        cleanUp();
        AnyDictionary.Iterator iterator = anyDictionary.iterator();
        references.add(new OTIOFinalizer(iterator, otioNativeReferenceQueue));
        return iterator;
    }

    ///////////////////////////////////////////////////////////////////////////

    // AnyVector //////////////////////////////////////////////////////////////

    public AnyVector createAnyVector() {
        cleanUp();
        AnyVector anyVector = new AnyVector();
        references.add(new OTIOFinalizer(anyVector, otioNativeReferenceQueue));
        return anyVector;
    }

    public AnyVector.Iterator getAnyVectorIterator(AnyVector anyVector) {
        cleanUp();
        AnyVector.Iterator iterator = anyVector.iterator();
        references.add(new OTIOFinalizer(iterator, otioNativeReferenceQueue));
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
        references.add(new OTIOFinalizer(clip, otioNativeReferenceQueue));
        return clip;
    }

    public Clip createClip(Clip.ClipBuilder builder) {
        cleanUp();
        Clip clip = builder.build();
        references.add(new OTIOFinalizer(clip, otioNativeReferenceQueue));
        return clip;
    }

    ///////////////////////////////////////////////////////////////////////////

    // Composable /////////////////////////////////////////////////////////////

    public Composable createComposable(String name, AnyDictionary metadata) {
        cleanUp();
        Composable composable = new Composable(name, metadata);
        references.add(new OTIOFinalizer(composable, otioNativeReferenceQueue));
        return composable;
    }

    public Composable createComposable(String name) {
        cleanUp();
        Composable composable = new Composable(name);
        references.add(new OTIOFinalizer(composable, otioNativeReferenceQueue));
        return composable;
    }

    public Composable createComposable(AnyDictionary metadata) {
        cleanUp();
        Composable composable = new Composable(metadata);
        references.add(new OTIOFinalizer(composable, otioNativeReferenceQueue));
        return composable;
    }

    public Composable createComposable(Composable.ComposableBuilder builder) {
        cleanUp();
        Composable composable = builder.build();
        references.add(new OTIOFinalizer(composable, otioNativeReferenceQueue));
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
        references.add(new OTIOFinalizer(composition, otioNativeReferenceQueue));
        return composition;
    }

    public Composition createComposition(Composition.CompositionBuilder builder) {
        cleanUp();
        Composition composition = builder.build();
        references.add(new OTIOFinalizer(composition, otioNativeReferenceQueue));
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
        references.add(new OTIOFinalizer(effect, otioNativeReferenceQueue));
        return effect;
    }

    public Effect createEffect(Effect.EffectBuilder builder) {
        cleanUp();
        Effect effect = builder.build();
        references.add(new OTIOFinalizer(effect, otioNativeReferenceQueue));
        return effect;
    }

    ///////////////////////////////////////////////////////////////////////////

    // io.opentimeline.opentimelineio.ErrorStatus /////////////////////////////

    public io.opentimeline.opentimelineio.ErrorStatus createOpenTimelineIOErrorStatus() {
        cleanUp();
        ErrorStatus errorStatus = new ErrorStatus();
        references.add(new OTIOFinalizer(errorStatus, otioNativeReferenceQueue));
        return errorStatus;
    }

    ///////////////////////////////////////////////////////////////////////////

    // io.opentimeline.opentime.ErrorStatus ///////////////////////////////////

    public io.opentimeline.opentime.ErrorStatus createOpentimeIOErrorStatus() {
        cleanUp();
        io.opentimeline.opentime.ErrorStatus errorStatus = new io.opentimeline.opentime.ErrorStatus();
        references.add(new OTIOFinalizer(errorStatus, otioNativeReferenceQueue));
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
        references.add(new OTIOFinalizer(externalReference, otioNativeReferenceQueue));
        return externalReference;
    }

    public ExternalReference createExternalReference(ExternalReference.ExternalReferenceBuilder builder) {
        cleanUp();
        ExternalReference externalReference = builder.build();
        references.add(new OTIOFinalizer(externalReference, otioNativeReferenceQueue));
        return externalReference;
    }

    ///////////////////////////////////////////////////////////////////////////

    // FreezeFrame ////////////////////////////////////////////////////////////

    public FreezeFrame createFreezeFrame(String name, AnyDictionary metadata) {
        cleanUp();
        FreezeFrame freezeFrame = new FreezeFrame(name, metadata);
        references.add(new OTIOFinalizer(freezeFrame, otioNativeReferenceQueue));
        return freezeFrame;
    }

    public FreezeFrame createFreezeFrame(FreezeFrame.FreezeFrameBuilder builder) {
        cleanUp();
        FreezeFrame freezeFrame = builder.build();
        references.add(new OTIOFinalizer(freezeFrame, otioNativeReferenceQueue));
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
        references.add(new OTIOFinalizer(gap, otioNativeReferenceQueue));
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
        references.add(new OTIOFinalizer(gap, otioNativeReferenceQueue));
        return gap;
    }

    public Gap createGap(Gap.GapBuilder builder) {
        cleanUp();
        Gap gap = builder.build();
        references.add(new OTIOFinalizer(gap, otioNativeReferenceQueue));
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
        references.add(new OTIOFinalizer(generatorReference, otioNativeReferenceQueue));
        return generatorReference;
    }

    public GeneratorReference createGeneratorReference(GeneratorReference.GeneratorReferenceBuilder builder) {
        cleanUp();
        GeneratorReference generatorReference = builder.build();
        references.add(new OTIOFinalizer(generatorReference, otioNativeReferenceQueue));
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
        references.add(new OTIOFinalizer(imageSequenceReference, otioNativeReferenceQueue));
        return imageSequenceReference;
    }

    public ImageSequenceReference createImageSequenceReference(
            ImageSequenceReference.ImageSequenceReferenceBuilder builder) {
        cleanUp();
        ImageSequenceReference imageSequenceReference = builder.build();
        references.add(new OTIOFinalizer(imageSequenceReference, otioNativeReferenceQueue));
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
        references.add(new OTIOFinalizer(item, otioNativeReferenceQueue));
        return item;
    }

    public Item createItem(Item.ItemBuilder builder) {
        cleanUp();
        Item item = builder.build();
        references.add(new OTIOFinalizer(item, otioNativeReferenceQueue));
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
        references.add(new OTIOFinalizer(linearTimeWarp, otioNativeReferenceQueue));
        return linearTimeWarp;
    }

    public LinearTimeWarp createLinearTimeWarp(LinearTimeWarp.LinearTimeWarpBuilder builder) {
        cleanUp();
        LinearTimeWarp linearTimeWarp = builder.build();
        references.add(new OTIOFinalizer(linearTimeWarp, otioNativeReferenceQueue));
        return linearTimeWarp;
    }

    ///////////////////////////////////////////////////////////////////////////

    // Marker /////////////////////////////////////////////////////////

    public Marker createMarker(String name, TimeRange markedRange, String color, AnyDictionary metadata) {
        cleanUp();
        Marker marker = new Marker(name, markedRange, color, metadata);
        references.add(new OTIOFinalizer(marker, otioNativeReferenceQueue));
        return marker;
    }

    public Marker createMarker(Marker.MarkerBuilder builder) {
        cleanUp();
        Marker marker = builder.build();
        references.add(new OTIOFinalizer(marker, otioNativeReferenceQueue));
        return marker;
    }

    ///////////////////////////////////////////////////////////////////

    // MediaReference /////////////////////////////////////////////////

    public MediaReference createMediaReference(String name, TimeRange availableRange, AnyDictionary metadata) {
        cleanUp();
        MediaReference mediaReference = new MediaReference(name, availableRange, metadata);
        references.add(new OTIOFinalizer(mediaReference, otioNativeReferenceQueue));
        return mediaReference;
    }

    public MediaReference createMediaReference(MediaReference.MediaReferenceBuilder builder) {
        cleanUp();
        MediaReference mediaReference = builder.build();
        references.add(new OTIOFinalizer(mediaReference, otioNativeReferenceQueue));
        return mediaReference;
    }

    ///////////////////////////////////////////////////////////////////

    // MediaReference /////////////////////////////////////////////////

    public MissingReference createMissingReference(String name, TimeRange availableRange, AnyDictionary metadata) {
        cleanUp();
        MissingReference mediaReference = new MissingReference(name, availableRange, metadata);
        references.add(new OTIOFinalizer(mediaReference, otioNativeReferenceQueue));
        return mediaReference;
    }

    public MissingReference createMediaReference(MissingReference.MissingReferenceBuilder builder) {
        cleanUp();
        MissingReference mediaReference = builder.build();
        references.add(new OTIOFinalizer(mediaReference, otioNativeReferenceQueue));
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
        references.add(new OTIOFinalizer(serializableCollection, otioNativeReferenceQueue));
        return serializableCollection;
    }

    public SerializableCollection createSerializableCollection(SerializableCollection.SerializableCollectionBuilder builder) {
        cleanUp();
        SerializableCollection serializableCollection = builder.build();
        references.add(new OTIOFinalizer(serializableCollection, otioNativeReferenceQueue));
        return serializableCollection;
    }

    ///////////////////////////////////////////////////////////////////

    // SerializableObject /////////////////////////////////////////

    public SerializableObject createSerializableObject() {
        cleanUp();
        SerializableObject serializableObject = new SerializableObject();
        references.add(new OTIOFinalizer(serializableObject, otioNativeReferenceQueue));
        return serializableObject;
    }

    ///////////////////////////////////////////////////////////////

    // SerializableObjectWithMetadata /////////////////////////////

    public SerializableObjectWithMetadata createSerializableObjectWithMetadata(String name, AnyDictionary metadata) {
        cleanUp();
        SerializableObjectWithMetadata serializableObjectWithMetadata = new SerializableObjectWithMetadata(name, metadata);
        references.add(new OTIOFinalizer(serializableObjectWithMetadata, otioNativeReferenceQueue));
        return serializableObjectWithMetadata;
    }

    public SerializableObjectWithMetadata createSerializableObjectWithMetadata(String name) {
        cleanUp();
        SerializableObjectWithMetadata serializableObjectWithMetadata = new SerializableObjectWithMetadata(name);
        references.add(new OTIOFinalizer(serializableObjectWithMetadata, otioNativeReferenceQueue));
        return serializableObjectWithMetadata;
    }

    public SerializableObjectWithMetadata createSerializableObjectWithMetadata(AnyDictionary metadata) {
        cleanUp();
        SerializableObjectWithMetadata serializableObjectWithMetadata = new SerializableObjectWithMetadata(metadata);
        references.add(new OTIOFinalizer(serializableObjectWithMetadata, otioNativeReferenceQueue));
        return serializableObjectWithMetadata;
    }

    public SerializableObjectWithMetadata createSerializableObjectWithMetadata(
            SerializableObjectWithMetadata.SerializableObjectWithMetadataBuilder builder) {
        cleanUp();
        SerializableObjectWithMetadata serializableObjectWithMetadata = builder.build();
        references.add(new OTIOFinalizer(serializableObjectWithMetadata, otioNativeReferenceQueue));
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
        references.add(new OTIOFinalizer(stack, otioNativeReferenceQueue));
        return stack;
    }

    public Stack createStack(Stack.StackBuilder builder) {
        cleanUp();
        Stack stack = builder.build();
        references.add(new OTIOFinalizer(stack, otioNativeReferenceQueue));
        return stack;
    }

    ///////////////////////////////////////////////////////////////

    // TimeEffect /////////////////////////////////////////////////

    public TimeEffect createTimeEffect(String name, String effectName, AnyDictionary metadata) {
        cleanUp();
        TimeEffect timeEffect = new TimeEffect(name, effectName, metadata);
        references.add(new OTIOFinalizer(timeEffect, otioNativeReferenceQueue));
        return timeEffect;
    }

    public TimeEffect createTimeEffect(TimeEffect.TimeEffectBuilder builder) {
        cleanUp();
        TimeEffect timeEffect = builder.build();
        references.add(new OTIOFinalizer(timeEffect, otioNativeReferenceQueue));
        return timeEffect;
    }

    ///////////////////////////////////////////////////////////////

    // Timeline ///////////////////////////////////////////////////

    public Timeline createTimeline(String name, RationalTime globalStartTime, AnyDictionary metadata) {
        cleanUp();
        Timeline timeline = new Timeline(name, globalStartTime, metadata);
        references.add(new OTIOFinalizer(timeline, otioNativeReferenceQueue));
        return timeline;
    }

    public Timeline createTimeline(Timeline.TimelineBuilder builder) {
        cleanUp();
        Timeline timeline = builder.build();
        references.add(new OTIOFinalizer(timeline, otioNativeReferenceQueue));
        return timeline;
    }

    ///////////////////////////////////////////////////////////////

    // Track //////////////////////////////////////////////////////

    public Track createTrack(String name, TimeRange sourceRange, String kind, AnyDictionary metadata) {
        cleanUp();
        Track track = new Track(name, sourceRange, kind, metadata);
        references.add(new OTIOFinalizer(track, otioNativeReferenceQueue));
        return track;
    }

    public Track createTrack(Track.TrackBuilder builder) {
        cleanUp();
        Track track = builder.build();
        references.add(new OTIOFinalizer(track, otioNativeReferenceQueue));
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
        references.add(new OTIOFinalizer(transition, otioNativeReferenceQueue));
        return transition;
    }

    public Transition createTransition(Transition.TransitionBuilder builder) {
        cleanUp();
        Transition transition = builder.build();
        references.add(new OTIOFinalizer(transition, otioNativeReferenceQueue));
        return transition;
    }

    ///////////////////////////////////////////////////////////////

    // UnknownSchema //////////////////////////////////////////////

    public UnknownSchema createUnknownSchema(String originalSchemaName, int originalSchemaVersion) {
        cleanUp();
        UnknownSchema unknownSchema = new UnknownSchema(originalSchemaName, originalSchemaVersion);
        references.add(new OTIOFinalizer(unknownSchema, otioNativeReferenceQueue));
        return unknownSchema;
    }

    public UnknownSchema createUnknownSchema(UnknownSchema.UnknownSchemaBuilder builder) {
        cleanUp();
        UnknownSchema unknownSchema = builder.build();
        references.add(new OTIOFinalizer(unknownSchema, otioNativeReferenceQueue));
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
