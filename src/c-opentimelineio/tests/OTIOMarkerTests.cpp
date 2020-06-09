#include "gtest/gtest.h"

#include <copentime/rationalTime.h>
#include <copentime/timeRange.h>
#include <copentimelineio/deserialization.h>
#include <copentimelineio/errorStatus.h>
#include <copentimelineio/item.h>
#include <copentimelineio/marker.h>
#include <copentimelineio/safely_typed_any.h>
#include <copentimelineio/serializableObject.h>
#include <copentimelineio/serializableObjectWithMetadata.h>
#include <copentimelineio/serialization.h>

class OTIOMarkerTests : public ::testing::Test
{
protected:
    void SetUp() override {}
    void TearDown() override {}
};

TEST_F(OTIOMarkerTests, ConstructorTest)
{
    RationalTime* start_time = RationalTime_create(5, 24);
    RationalTime* duration   = RationalTime_create(10, 24);
    TimeRange*    tr =
        TimeRange_create_with_start_time_and_duration(start_time, duration);

    AnyDictionary*         metadata  = AnyDictionary_create();
    Any*                   value_any = create_safely_typed_any_string("bar");
    AnyDictionaryIterator* it =
        AnyDictionary_insert(metadata, "foo", value_any);

    Marker* m = Marker_create("marker_1", tr, MarkerColor_green, metadata);

    AnyDictionaryIterator_destroy(it);
    it = NULL;

    EXPECT_STREQ(
        SerializableObjectWithMetadata_name(
            (SerializableObjectWithMetadata*) m),
        "marker_1");

    AnyDictionary* metadata_compare = SerializableObjectWithMetadata_metadata(
        (SerializableObjectWithMetadata*) m);
    it                            = AnyDictionary_find(metadata_compare, "foo");
    AnyDictionaryIterator* it_end = AnyDictionary_end(metadata_compare);
    ASSERT_TRUE(AnyDictionaryIterator_not_equal(it, it_end));
    Any*        compare_any   = AnyDictionaryIterator_value(it);
    const char* compare_value = safely_cast_string_any(compare_any);
    EXPECT_STREQ(compare_value, "bar");
    EXPECT_EQ(AnyDictionary_size(metadata_compare), 1);
    AnyDictionaryIterator_destroy(it);
    it = NULL;
    AnyDictionaryIterator_destroy(it_end);
    it_end = NULL;
    AnyDictionary_destroy(metadata_compare);
    metadata_compare = NULL;

    TimeRange* marked_range = Marker_marked_range(m);
    EXPECT_TRUE(TimeRange_equal(marked_range, tr));
    TimeRange_destroy(marked_range);
    marked_range = NULL;

    const char* color = Marker_color(m);
    EXPECT_STREQ(color, MarkerColor_green);

    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    Any* marker_any =
        create_safely_typed_any_serializable_object((SerializableObject*) m);
    const char* encoded = serialize_json_to_string(marker_any, errorStatus, 4);
    Any*        decoded = /** allocate memory for destinantion */
        create_safely_typed_any_serializable_object((SerializableObject*) m);
    bool decoded_successfully =
        deserialize_json_from_string(encoded, decoded, errorStatus);
    ASSERT_TRUE(decoded_successfully);

    SerializableObject* decoded_object = safely_cast_retainer_any(decoded);
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) m, decoded_object));

    Any_destroy(marker_any);
    marker_any = NULL;
    SerializableObject_possibly_delete(decoded_object);
    decoded_object = NULL;

    AnyDictionary_destroy(metadata);
    metadata = NULL;
    Any_destroy(value_any);
    value_any = NULL;
    RationalTime_destroy(start_time);
    start_time = NULL;
    RationalTime_destroy(duration);
    duration = NULL;
    TimeRange_destroy(tr);
    tr = NULL;
}

TEST_F(OTIOMarkerTests, UpgradeTest)
{
    const char* src =
        " {\n"
        "            \"OTIO_SCHEMA\" : \"Marker.1\",\n"
        "            \"metadata\" : {},\n"
        "            \"name\" : null,\n"
        "            \"range\" : {\n"
        "                \"OTIO_SCHEMA\" : \"TimeRange.1\",\n"
        "                \"start_time\" : {\n"
        "                    \"OTIO_SCHEMA\" : \"RationalTime.1\",\n"
        "                    \"rate\" : 5,\n"
        "                    \"value\" : 0\n"
        "                },\n"
        "                \"duration\" : {\n"
        "                    \"OTIO_SCHEMA\" : \"RationalTime.1\",\n"
        "                    \"rate\" : 5,\n"
        "                    \"value\" : 0\n"
        "                }\n"
        "            }\n"
        "\n"
        "        } ";

    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    SerializableObject* so      = SerializableObject_create();
    Any*                decoded = /** allocate memory for destinantion */
        create_safely_typed_any_serializable_object((SerializableObject*) so);
    bool decoded_successfully =
        deserialize_json_from_string(src, decoded, errorStatus);
    ASSERT_TRUE(decoded_successfully);

    Marker* marker = (Marker*) safely_cast_retainer_any(decoded);

    RationalTime* start_time = RationalTime_create(0, 5);
    TimeRange*    range_compare =
        TimeRange_create_with_start_time_and_duration(start_time, start_time);
    TimeRange* marked_range = Marker_marked_range(marker);
    EXPECT_TRUE(TimeRange_equal(range_compare, marked_range));

    RationalTime_destroy(start_time);
    start_time = NULL;
    TimeRange_destroy(range_compare);
    range_compare = NULL;
    TimeRange_destroy(marked_range);
    marked_range = NULL;
    SerializableObject_possibly_delete((SerializableObject*) marker);
    marker = NULL;
}

TEST_F(OTIOMarkerTests, EqualityTest)
{
    Marker* m  = Marker_create(NULL, NULL, NULL, NULL);
    Item*   bo = Item_create(NULL, NULL, NULL, NULL, NULL);

    EXPECT_FALSE(SerializableObject_is_equivalent_to(
        (SerializableObject*) m, (SerializableObject*) bo));
    EXPECT_FALSE(SerializableObject_is_equivalent_to(
        (SerializableObject*) bo, (SerializableObject*) m));

    SerializableObject_possibly_delete((SerializableObject*) bo);
    bo = NULL;
    SerializableObject_possibly_delete((SerializableObject*) m);
    m = NULL;
}