#include "gtest/gtest.h"

#include <copentimelineio/clip.h>
#include <copentimelineio/deserialization.h>
#include <copentimelineio/errorStatus.h>
#include <copentimelineio/gap.h>
#include <copentimelineio/missingReference.h>
#include <copentimelineio/safely_typed_any.h>
#include <copentimelineio/serializableCollection.h>
#include <copentimelineio/serializableObject.h>
#include <copentimelineio/serializableObjectVector.h>
#include <copentimelineio/serializableObjectWithMetadata.h>
#include <copentimelineio/serialization.h>

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
    
}