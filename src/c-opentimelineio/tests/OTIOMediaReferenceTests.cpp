#include "gtest/gtest.h"

#include <copentime/rationalTime.h>
#include <copentime/timeRange.h>
#include <copentimelineio/deserialization.h>
#include <copentimelineio/errorStatus.h>
#include <copentimelineio/externalReference.h>
#include <copentimelineio/mediaReference.h>
#include <copentimelineio/missingReference.h>
#include <copentimelineio/safely_typed_any.h>
#include <copentimelineio/serializableObject.h>
#include <copentimelineio/serializableObjectWithMetadata.h>
#include <copentimelineio/serialization.h>

class OTIOMediaReferenceTests : public ::testing::Test
{
protected:
    void SetUp() override {}
    void TearDown() override {}
};

TEST_F(OTIOMediaReferenceTests, ConstructorTest)
{
    RationalTime* start_time = RationalTime_create(5, 24);
    RationalTime* duration   = RationalTime_create(10, 24);
    TimeRange*    available_range =
        TimeRange_create_with_start_time_and_duration(start_time, duration);

    AnyDictionary* metadata  = AnyDictionary_create();
    Any*           value_any = create_safely_typed_any_string("OTIOTheMovie");
    AnyDictionaryIterator* it =
        AnyDictionary_insert(metadata, "show", value_any);

    MissingReference* mr =
        MissingReference_create(NULL, available_range, metadata);

    TimeRange* mr_available_range =
        MediaReference_available_range((MediaReference*) mr);
    EXPECT_TRUE(TimeRange_equal(mr_available_range, available_range));

    RationalTime_destroy(start_time);
    start_time = NULL;
    RationalTime_destroy(duration);
    duration = NULL;
    TimeRange_destroy(available_range);
    available_range = NULL;
    TimeRange_destroy(mr_available_range);
    mr_available_range = NULL;
    AnyDictionary_destroy(metadata);
    metadata = NULL;
    Any_destroy(value_any);
    value_any = NULL;
    AnyDictionaryIterator_destroy(it);
    it = NULL;
    SerializableObject_possibly_delete((SerializableObject*) mr);
    mr = NULL;

    mr                 = MissingReference_create(NULL, NULL, NULL);
    mr_available_range = MediaReference_available_range((MediaReference*) mr);
    EXPECT_EQ(mr_available_range, nullptr);
    SerializableObject_possibly_delete((SerializableObject*) mr);
    mr = NULL;
}

TEST_F(OTIOMediaReferenceTests, SerializationTest)
{
    MissingReference* mr = MissingReference_create(NULL, NULL, NULL);

    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    Any* mr_any =
        create_safely_typed_any_serializable_object((SerializableObject*) mr);
    const char* encoded = serialize_json_to_string(mr_any, errorStatus, 4);
    Any*        decoded = /** allocate memory for destinantion */
        create_safely_typed_any_serializable_object((SerializableObject*) mr);
    bool decoded_successfully =
        deserialize_json_from_string(encoded, decoded, errorStatus);
    ASSERT_TRUE(decoded_successfully);

    SerializableObject* decoded_object = safely_cast_retainer_any(decoded);
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) mr, decoded_object));

    Any_destroy(mr_any);
    mr_any = NULL;
    SerializableObject_possibly_delete(decoded_object);
    decoded_object = NULL;
    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
}

TEST_F(OTIOMediaReferenceTests, FilepathTest)
{
    ExternalReference* filepath =
        ExternalReference_create("var/tmp/foo.mov", NULL, NULL);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    Any* filepath_any = create_safely_typed_any_serializable_object(
        (SerializableObject*) filepath);
    const char* encoded =
        serialize_json_to_string(filepath_any, errorStatus, 4);
    Any* decoded = /** allocate memory for destinantion */
        create_safely_typed_any_serializable_object(
            (SerializableObject*) filepath);
    bool decoded_successfully =
        deserialize_json_from_string(encoded, decoded, errorStatus);
    ASSERT_TRUE(decoded_successfully);

    SerializableObject* decoded_object = safely_cast_retainer_any(decoded);
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) filepath, decoded_object));

    Any_destroy(filepath_any);
    filepath_any = NULL;
    SerializableObject_possibly_delete(decoded_object);
    decoded_object = NULL;
    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
}

TEST_F(OTIOMediaReferenceTests, EqualityTest)
{
    ExternalReference* filepath =
        ExternalReference_create("var/tmp/foo.mov", NULL, NULL);
    ExternalReference* filepath2 =
        ExternalReference_create("var/tmp/foo.mov", NULL, NULL);

    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) filepath, (SerializableObject*) filepath2));

    MissingReference* bl = MissingReference_create(NULL, NULL, NULL);

    EXPECT_FALSE(SerializableObject_is_equivalent_to(
        (SerializableObject*) filepath, (SerializableObject*) bl));

    filepath  = ExternalReference_create("var/tmp/foo.mov", NULL, NULL);
    filepath2 = ExternalReference_create("var/tmp/foo2.mov", NULL, NULL);

    EXPECT_FALSE(SerializableObject_is_equivalent_to(
        (SerializableObject*) filepath, (SerializableObject*) filepath2));
}

TEST_F(OTIOMediaReferenceTests, IsMissingTest)
{
    ExternalReference* filepath =
        ExternalReference_create("var/tmp/foo.mov", NULL, NULL);
    EXPECT_FALSE(
        MediaReference_is_missing_reference((MediaReference*) filepath));

    MissingReference* bl = MissingReference_create(NULL, NULL, NULL);
    EXPECT_TRUE(MediaReference_is_missing_reference((MediaReference*) bl));

    SerializableObject_possibly_delete((SerializableObject*) filepath);
    filepath = NULL;
    SerializableObject_possibly_delete((SerializableObject*) bl);
    bl = NULL;
}