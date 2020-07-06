#include "gtest/gtest.h"

#include <copentimelineio/clip.h>
#include <copentimelineio/deserialization.h>
#include <copentimelineio/errorStatus.h>
#include <copentimelineio/gap.h>
#include <copentimelineio/missingReference.h>
#include <copentimelineio/safely_typed_any.h>
#include <copentimelineio/serializableCollection.h>
#include <copentimelineio/serializableObject.h>
#include <copentimelineio/serializableObjectWithMetadata.h>
#include <copentimelineio/serialization.h>
#include <copentimelineio/timeline.h>
#include <copentimelineio/track.h>
#include <copentimelineio/transition.h>

class OTIOGapTests : public ::testing::Test
{
protected:
    void SetUp() override {}
    void TearDown() override {}
};

class OTIOItemTests : public ::testing::Test
{
protected:
    void SetUp() override {}
    void TearDown() override {}
};

TEST_F(OTIOGapTests, SerializeTest)
{
    Gap* gap = Gap_create_with_duration(NULL, NULL, NULL, NULL, NULL);
    Any* gap_any =
        create_safely_typed_any_serializable_object((SerializableObject*) gap);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    const char* encoded = serialize_json_to_string(gap_any, errorStatus, 4);
    Any*        decoded = /* allocate memory for destinantion */
        create_safely_typed_any_serializable_object((SerializableObject*) gap);

    bool decoded_successfully =
        deserialize_json_from_string(encoded, decoded, errorStatus);
    ASSERT_TRUE(decoded_successfully);
    SerializableObject* decoded_object = safely_cast_retainer_any(decoded);

    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) gap, decoded_object));

    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
    Any_destroy(decoded);
    decoded = NULL;
    Gap_possibly_delete(gap);
    gap = NULL;
}

TEST_F(OTIOItemTests, ConstructorTest)
{
    RationalTime* start    = RationalTime_create(0, 1);
    RationalTime* duration = RationalTime_create(10, 1);
    TimeRange*    tr =
        TimeRange_create_with_start_time_and_duration(start, duration);

    Item* it = Item_create("foo", tr, NULL, NULL, NULL);

    EXPECT_STREQ(Item_name(it), "foo");

    TimeRange* it_source_range = Item_source_range(it);
    EXPECT_TRUE(TimeRange_equal(it_source_range, tr));
    TimeRange_destroy(it_source_range);
    it_source_range = NULL;
    RationalTime_destroy(start);
    start = NULL;
    RationalTime_destroy(duration);
    duration = NULL;

    Any* item_any =
        create_safely_typed_any_serializable_object((SerializableObject*) it);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    const char* encoded = serialize_json_to_string(item_any, errorStatus, 4);
    Any*        decoded = /* allocate memory for destinantion */
        create_safely_typed_any_serializable_object((SerializableObject*) it);

    bool decoded_successfully =
        deserialize_json_from_string(encoded, decoded, errorStatus);
    ASSERT_TRUE(decoded_successfully);
    SerializableObject* decoded_object = safely_cast_retainer_any(decoded);

    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) it, decoded_object));

    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
    Any_destroy(decoded);
    decoded = NULL;
    Item_possibly_delete(it);
    it = NULL;
}

TEST_F(OTIOItemTests, CopyArgumentsTest)
{
    RationalTime* start    = RationalTime_create(0, 24);
    RationalTime* duration = RationalTime_create(10, 24);
    TimeRange*    tr =
        TimeRange_create_with_start_time_and_duration(start, duration);

    const char*    it_name      = "foobar";
    MarkerVector*  markerVector = MarkerVector_create();
    AnyDictionary* metadata     = AnyDictionary_create();
    Item*          it = Item_create(it_name, tr, metadata, NULL, markerVector);

    it_name = "foobaz";
    EXPECT_STRNE(it_name, Item_name(it));

    RationalTime* start2 = RationalTime_create(1, RationalTime_rate(start));
    TimeRange_destroy(tr);
    tr = TimeRange_create_with_start_time_and_duration(start2, duration);

    TimeRange* it_source_range = Item_source_range(it);
    EXPECT_FALSE(TimeRange_equal(it_source_range, tr));
    RationalTime_destroy(start2);
    start2 = NULL;
    TimeRange_destroy(tr);
    tr = NULL;
    RationalTime_destroy(start);
    start = NULL;
    RationalTime_destroy(duration);
    duration = NULL;

    Marker* marker = Marker_create(NULL, NULL, NULL, NULL);
    MarkerVector_push_back(markerVector, marker);
    MarkerRetainerVector* markerRetainerVector = Item_markers(it);
    EXPECT_NE(
        MarkerRetainerVector_size(markerRetainerVector),
        MarkerVector_size(markerVector));
    MarkerRetainerVector_destroy(markerRetainerVector);
    markerRetainerVector = NULL;
    Marker_possibly_delete(marker);
    marker = NULL;

    Any* stringAny = create_safely_typed_any_string("bar");
    AnyDictionary_insert(metadata, "foo", stringAny);
    AnyDictionary* metadataResult = Item_metadata(it);
    EXPECT_NE(AnyDictionary_size(metadata), AnyDictionary_size(metadataResult));
    AnyDictionary_destroy(metadataResult);
    metadataResult = NULL;
    Any_destroy(stringAny);
    stringAny = NULL;

    MarkerVector_destroy(markerVector);
    markerVector = NULL;
    AnyDictionary_destroy(metadata);
    metadata = NULL;
    Item_possibly_delete(it);
    it = NULL;
}

TEST_F(OTIOItemTests, DurationTest)
{
    RationalTime* start    = RationalTime_create(0, 24);
    RationalTime* duration = RationalTime_create(10, 24);
    TimeRange*    tr =
        TimeRange_create_with_start_time_and_duration(start, duration);
    Item* it = Item_create(NULL, tr, NULL, NULL, NULL);

    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    RationalTime* it_duration = Item_duration(it, errorStatus);

    EXPECT_TRUE(RationalTime_equal(duration, it_duration));

    RationalTime_destroy(start);
    start = NULL;
    RationalTime_destroy(duration);
    duration = NULL;
    RationalTime_destroy(it_duration);
    it_duration = NULL;
    TimeRange_destroy(tr);
    tr = NULL;
    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
    Item_possibly_delete(it);
    it = NULL;
}

TEST_F(OTIOItemTests, AvailableRangeTest)
{
    Item* it = Item_create(NULL, NULL, NULL, NULL, NULL);

    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    TimeRange* available_range = Item_available_range(it, errorStatus);

    EXPECT_EQ(OTIOErrorStatus_get_outcome(errorStatus), 1);

    TimeRange_destroy(available_range);
    available_range = NULL;
    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
    Item_possibly_delete(it);
    it = NULL;
}

TEST_F(OTIOItemTests, DurationAndSourceRangeTest)
{
    Item* it = Item_create(NULL, NULL, NULL, NULL, NULL);

    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    RationalTime* it_duration = Item_duration(it, errorStatus);

    EXPECT_EQ(OTIOErrorStatus_get_outcome(errorStatus), 1);

    RationalTime* start    = RationalTime_create(1, 1);
    RationalTime* duration = RationalTime_create(10, 1);
    TimeRange*    tr =
        TimeRange_create_with_start_time_and_duration(start, duration);
    Item* it2 = Item_create(NULL, tr, NULL, NULL, NULL);

    TimeRange* it2_source_range = Item_source_range(it2);
    EXPECT_TRUE(TimeRange_equal(it2_source_range, tr));

    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = OTIOErrorStatus_create();

    RationalTime* it2_duration = Item_duration(it2, errorStatus);
    EXPECT_TRUE(RationalTime_equal(it2_duration, duration));
    EXPECT_NE(it2_duration, duration);

    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
    RationalTime_destroy(it_duration);
    it_duration = NULL;
    RationalTime_destroy(start);
    start = NULL;
    RationalTime_destroy(duration);
    duration = NULL;
    RationalTime_destroy(it2_duration);
    it2_duration = NULL;
    TimeRange_destroy(tr);
    tr = NULL;
    TimeRange_destroy(it2_source_range);
    it2_source_range = NULL;
    Item_possibly_delete(it);
    it = NULL;
    Item_possibly_delete(it2);
    it2 = NULL;
}

TEST_F(OTIOItemTests, TrimmedRangeTest)
{
    Item* it = Item_create(NULL, NULL, NULL, NULL, NULL);

    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    TimeRange* it_trimmed_range = Item_trimmed_range(it, errorStatus);

    EXPECT_EQ(OTIOErrorStatus_get_outcome(errorStatus), 1);

    RationalTime* start    = RationalTime_create(1, 1);
    RationalTime* duration = RationalTime_create(10, 1);
    TimeRange*    tr =
        TimeRange_create_with_start_time_and_duration(start, duration);
    Item* it2 = Item_create(NULL, tr, NULL, NULL, NULL);

    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = OTIOErrorStatus_create();

    TimeRange* it2_trimmed_range = Item_trimmed_range(it2, errorStatus);

    EXPECT_TRUE(TimeRange_equal(it2_trimmed_range, tr));
    EXPECT_NE(it2_trimmed_range, tr);

    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
    RationalTime_destroy(start);
    start = NULL;
    RationalTime_destroy(duration);
    duration = NULL;
    TimeRange_destroy(tr);
    tr = NULL;
    TimeRange_destroy(it2_trimmed_range);
    it2_trimmed_range = NULL;
    TimeRange_destroy(it_trimmed_range);
    it_trimmed_range = NULL;
    Item_possibly_delete(it);
    it = NULL;
    Item_possibly_delete(it2);
    it2 = NULL;
}

TEST_F(OTIOItemTests, MetadataTest)
{
    RationalTime* start    = RationalTime_create(1, 1);
    RationalTime* duration = RationalTime_create(10, 1);
    TimeRange*    tr =
        TimeRange_create_with_start_time_and_duration(start, duration);

    AnyDictionary* metadata = AnyDictionary_create();

    Any* stringAny = create_safely_typed_any_string("bar");

    AnyDictionaryIterator* it =
        AnyDictionary_insert(metadata, "foo", stringAny);

    Item* item = Item_create(NULL, tr, metadata, NULL, NULL);

    Any* item_any =
        create_safely_typed_any_serializable_object((SerializableObject*) item);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    const char* encoded = serialize_json_to_string(item_any, errorStatus, 4);
    Any*        decoded = /* allocate memory for destinantion */
        create_safely_typed_any_serializable_object((SerializableObject*) item);

    bool decoded_successfully =
        deserialize_json_from_string(encoded, decoded, errorStatus);
    ASSERT_TRUE(decoded_successfully);
    SerializableObject* decoded_object = safely_cast_retainer_any(decoded);

    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) item, decoded_object));

    AnyDictionary* metadataResult = Item_metadata((Item*) decoded_object);
    AnyDictionaryIterator* metadataResultFooIt =
        AnyDictionary_find(metadataResult, "foo");
    Any* metadataFooValue = AnyDictionaryIterator_value(metadataResultFooIt);
    const char* metadataFooStr = safely_cast_string_any(metadataFooValue);

    EXPECT_STREQ(metadataFooStr, "bar");

    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
    Any_destroy(decoded);
    decoded = NULL;
    AnyDictionary_destroy(metadataResult);
    metadataResult = NULL;
    AnyDictionary_destroy(metadata);
    metadata = NULL;
    AnyDictionaryIterator_destroy(metadataResultFooIt);
    metadataResultFooIt = NULL;
    Any_destroy(metadataFooValue);
    metadataFooValue = NULL;
    AnyDictionaryIterator_destroy(it);
    it = NULL;
    Any_destroy(stringAny);
    stringAny = NULL;
    RationalTime_destroy(start);
    start = NULL;
    RationalTime_destroy(duration);
    duration = NULL;
    TimeRange_destroy(tr);
    tr = NULL;
    Item_possibly_delete(item);
    item = NULL;
}

TEST_F(OTIOItemTests, MarkersTest)
{
    RationalTime* start    = RationalTime_create(1, 1);
    RationalTime* duration = RationalTime_create(10, 1);
    TimeRange*    tr =
        TimeRange_create_with_start_time_and_duration(start, duration);

    Marker*       marker       = Marker_create("test_marker", tr, NULL, NULL);
    MarkerVector* markerVector = MarkerVector_create();
    MarkerVector_push_back(markerVector, marker);

    Item* item = Item_create(NULL, tr, NULL, NULL, markerVector);

    Any* item_any =
        create_safely_typed_any_serializable_object((SerializableObject*) item);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    const char* encoded = serialize_json_to_string(item_any, errorStatus, 4);
    Any*        decoded = /* allocate memory for destinantion */
        create_safely_typed_any_serializable_object((SerializableObject*) item);

    bool decoded_successfully =
        deserialize_json_from_string(encoded, decoded, errorStatus);
    ASSERT_TRUE(decoded_successfully);
    SerializableObject* decoded_object = safely_cast_retainer_any(decoded);

    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) item, decoded_object));

    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
    Any_destroy(decoded);
    decoded = NULL;
    RationalTime_destroy(start);
    start = NULL;
    RationalTime_destroy(duration);
    duration = NULL;
    TimeRange_destroy(tr);
    tr = NULL;
    Item_possibly_delete(item);
    item = NULL;
    MarkerVector_destroy(markerVector);
    markerVector = NULL;
}

TEST_F(OTIOItemTests, EffectsTest)
{
    RationalTime* start    = RationalTime_create(1, 1);
    RationalTime* duration = RationalTime_create(10, 1);
    TimeRange*    tr =
        TimeRange_create_with_start_time_and_duration(start, duration);

    Effect*       effect       = Effect_create(NULL, "blur", NULL);
    EffectVector* effectVector = EffectVector_create();
    EffectVector_push_back(effectVector, effect);

    Item* item = Item_create(NULL, tr, NULL, effectVector, NULL);

    Any* item_any =
        create_safely_typed_any_serializable_object((SerializableObject*) item);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    const char* encoded = serialize_json_to_string(item_any, errorStatus, 4);
    Any*        decoded = /* allocate memory for destinantion */
        create_safely_typed_any_serializable_object((SerializableObject*) item);

    bool decoded_successfully =
        deserialize_json_from_string(encoded, decoded, errorStatus);
    ASSERT_TRUE(decoded_successfully);
    SerializableObject* decoded_object = safely_cast_retainer_any(decoded);

    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) item, decoded_object));

    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
    Any_destroy(decoded);
    decoded = NULL;
    RationalTime_destroy(start);
    start = NULL;
    RationalTime_destroy(duration);
    duration = NULL;
    TimeRange_destroy(tr);
    tr = NULL;
    Item_possibly_delete(item);
    item = NULL;
    EffectVector_destroy(effectVector);
    effectVector = NULL;
}

TEST_F(OTIOItemTests, VisibleRangeTest)
{
    RationalTime* start    = RationalTime_create(1, 30);
    RationalTime* duration = RationalTime_create(50, 30);
    TimeRange*    source_rangeA =
        TimeRange_create_with_start_time_and_duration(start, duration);
    Clip* A = Clip_create("A", NULL, source_rangeA, NULL);
    RationalTime_destroy(start);
    RationalTime_destroy(duration);

    start    = RationalTime_create(100, 30);
    duration = RationalTime_create(50, 30);
    TimeRange* source_rangeB =
        TimeRange_create_with_start_time_and_duration(start, duration);
    Clip* B = Clip_create("B", NULL, source_rangeB, NULL);
    RationalTime_destroy(start);
    RationalTime_destroy(duration);

    start    = RationalTime_create(50, 30);
    duration = RationalTime_create(50, 30);
    TimeRange* source_rangeC =
        TimeRange_create_with_start_time_and_duration(start, duration);
    Clip* C = Clip_create("C", NULL, source_rangeC, NULL);
    RationalTime_destroy(start);
    RationalTime_destroy(duration);

    start    = RationalTime_create(1, 30);
    duration = RationalTime_create(50, 30);
    TimeRange* source_rangeD =
        TimeRange_create_with_start_time_and_duration(start, duration);
    Clip* D = Clip_create("D", NULL, source_rangeD, NULL);
    RationalTime_destroy(start);
    RationalTime_destroy(duration);
    start = duration = NULL;

    RationalTime* in_offset  = RationalTime_create(7, 30);
    RationalTime* out_offset = RationalTime_create(10, 30);
    Transition*   transition1 =
        Transition_create(NULL, NULL, in_offset, out_offset, NULL);
    RationalTime_destroy(in_offset);
    RationalTime_destroy(out_offset);

    in_offset  = RationalTime_create(17, 30);
    out_offset = RationalTime_create(15, 30);
    Transition* transition2 =
        Transition_create(NULL, NULL, in_offset, out_offset, NULL);
    RationalTime_destroy(in_offset);
    RationalTime_destroy(out_offset);
    in_offset  = NULL;
    out_offset = NULL;

    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    Track* track = Track_create(NULL, NULL, NULL, NULL);
    ASSERT_TRUE(Track_insert_child(track, 0, (Composable*) A, errorStatus));
    ASSERT_TRUE(
        Track_insert_child(track, 1, (Composable*) transition1, errorStatus));
    ASSERT_TRUE(Track_insert_child(track, 2, (Composable*) B, errorStatus));
    ASSERT_TRUE(
        Track_insert_child(track, 3, (Composable*) transition2, errorStatus));
    ASSERT_TRUE(Track_insert_child(track, 4, (Composable*) C, errorStatus));
    ASSERT_TRUE(Track_insert_child(track, 5, (Composable*) D, errorStatus));

    Stack* stack = Stack_create(NULL, NULL, NULL, NULL, NULL);
    ASSERT_TRUE(Stack_insert_child(stack, 0, (Composable*) track, errorStatus));

    Timeline* timeline = Timeline_create(NULL, NULL, NULL);
    Timeline_set_tracks(timeline, stack);

    const char* name_list[]      = { "A", "B", "C", "D" };
    TimeRange*  trimmed_ranges[] = {
        source_rangeA, source_rangeB, source_rangeC, source_rangeD
    };

    start    = RationalTime_create(1, 30);
    duration = RationalTime_create(50 + 10, 30);
    TimeRange* visible_range_1 =
        TimeRange_create_with_start_time_and_duration(start, duration);
    RationalTime_destroy(start);
    RationalTime_destroy(duration);

    start    = RationalTime_create(100 - 7, 30);
    duration = RationalTime_create(50 + 15 + 7, 30);
    TimeRange* visible_range_2 =
        TimeRange_create_with_start_time_and_duration(start, duration);
    RationalTime_destroy(start);
    RationalTime_destroy(duration);

    start    = RationalTime_create(33, 30);
    duration = RationalTime_create(50 + 17, 30);
    TimeRange* visible_range_3 =
        TimeRange_create_with_start_time_and_duration(start, duration);
    RationalTime_destroy(start);
    RationalTime_destroy(duration);

    start    = RationalTime_create(1, 30);
    duration = RationalTime_create(50, 30);
    TimeRange* visible_range_4 =
        TimeRange_create_with_start_time_and_duration(start, duration);
    RationalTime_destroy(start);
    RationalTime_destroy(duration);
    TimeRange* visible_ranges[] = {
        visible_range_1, visible_range_2, visible_range_3, visible_range_4
    };

    ComposableVector*         clipVector = Track_each_clip(track);
    ComposableVectorIterator* it         = ComposableVector_begin(clipVector);
    ComposableVectorIterator* itEnd      = ComposableVector_end(clipVector);

    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;

    for(int i = 0; ComposableVectorIterator_not_equal(it, itEnd);
        ComposableVectorIterator_advance(it, 1), i++)
    {
        Composable* clipComposable = ComposableVectorIterator_value(it);
        Clip*       clipValue      = (Clip*) clipComposable;
        EXPECT_STREQ(name_list[i], Clip_name(clipValue));
        errorStatus = OTIOErrorStatus_create();

        TimeRange* clip_trimmed_range =
            Clip_trimmed_range(clipValue, errorStatus);
        EXPECT_TRUE(TimeRange_equal(clip_trimmed_range, trimmed_ranges[i]));
        TimeRange_destroy(clip_trimmed_range);

        TimeRange* clip_visible_range =
            Clip_visible_range(clipValue, errorStatus);
        EXPECT_TRUE(TimeRange_equal(clip_visible_range, visible_ranges[i]));
        TimeRange_destroy(clip_visible_range);

        clip_trimmed_range = NULL;
        clip_visible_range = NULL;
        OTIOErrorStatus_destroy(errorStatus);
    }

    TimeRange_destroy(source_rangeA);
    source_rangeA = NULL;
    TimeRange_destroy(source_rangeB);
    source_rangeB = NULL;
    TimeRange_destroy(source_rangeC);
    source_rangeC = NULL;
    TimeRange_destroy(source_rangeD);
    source_rangeD = NULL;
    TimeRange_destroy(visible_range_1);
    visible_range_1 = NULL;
    TimeRange_destroy(visible_range_2);
    visible_range_2 = NULL;
    TimeRange_destroy(visible_range_3);
    visible_range_3 = NULL;
    TimeRange_destroy(visible_range_4);
    visible_range_4 = NULL;
    ComposableVectorIterator_destroy(it);
    it = NULL;
    ComposableVectorIterator_destroy(itEnd);
    itEnd = NULL;
    ComposableVector_destroy(clipVector);
    clipVector = NULL;
    Timeline_possibly_delete(timeline);
    timeline = NULL;
}