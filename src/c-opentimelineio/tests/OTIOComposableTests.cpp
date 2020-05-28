#include "gtest/gtest.h"

#include <copentimelineio/anyDictionary.h>
#include <copentimelineio/composable.h>
#include <copentimelineio/deserialization.h>
#include <copentimelineio/errorStatus.h>
#include <copentimelineio/safely_typed_any.h>
#include <copentimelineio/serializableObjectWithMetadata.h>
#include <copentimelineio/serialization.h>
#include <iostream>

class OTIOCOmposableTests : public ::testing::Test
{
protected:
    void SetUp() override {}
    void TearDown() override {}
};

TEST_F(OTIOCOmposableTests, ConstructorTest)
{
    Any*                   value    = create_safely_typed_any_string("bar");
    AnyDictionary*         metadata = AnyDictionary_create();
    AnyDictionaryIterator* it = AnyDictionary_insert(metadata, "foo", value);
    Composable*            seqi =
        Composable_create_with_name_and_metadata("test", metadata);
    const char* name = SerializableObjectWithMetadata_name(
        (SerializableObjectWithMetadata*) seqi);
    EXPECT_STREQ(name, "test");

    AnyDictionary* resultMetadata = SerializableObjectWithMetadata_metadata(
        (SerializableObjectWithMetadata*) seqi);
    ASSERT_EQ(AnyDictionary_size(metadata), AnyDictionary_size(resultMetadata));

    AnyDictionaryIterator* itMetadata    = AnyDictionary_begin(metadata);
    AnyDictionaryIterator* itMetadataEnd = AnyDictionary_end(metadata);
    AnyDictionaryIterator* itMetadataResult =
        AnyDictionary_begin(resultMetadata);

    for(; AnyDictionaryIterator_not_equal(itMetadata, itMetadataEnd);
        AnyDictionaryIterator_advance(itMetadata, 1),
        AnyDictionaryIterator_advance(itMetadataResult, 1))
    {
        ASSERT_STREQ(
            AnyDictionaryIterator_key(itMetadata),
            AnyDictionaryIterator_key(itMetadataResult));
        Any* x = AnyDictionaryIterator_value(itMetadata);
        Any* y = AnyDictionaryIterator_value(itMetadataResult);
        ASSERT_STREQ(safely_cast_string_any(x), safely_cast_string_any(y));
        Any_destroy(x);
        Any_destroy(y);
    }

    Any_destroy(value);
    AnyDictionary_destroy(metadata);
    AnyDictionary_destroy(resultMetadata);
    AnyDictionaryIterator_destroy(it);
    AnyDictionaryIterator_destroy(itMetadata);
    AnyDictionaryIterator_destroy(itMetadataEnd);
    AnyDictionaryIterator_destroy(itMetadataResult);
}

TEST_F(OTIOCOmposableTests, SerializeTest)
{
    Any*                   value    = create_safely_typed_any_string("bar");
    AnyDictionary*         metadata = AnyDictionary_create();
    AnyDictionaryIterator* it = AnyDictionary_insert(metadata, "foo", value);
    Composable*            seqi =
        Composable_create_with_name_and_metadata("test", metadata);
    Any* seqi_any =
        create_safely_typed_any_serializable_object((SerializableObject*) seqi);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();
    const char* encoded = serialize_json_to_string(seqi_any, errorStatus, 4);
    OTIO_ErrorStatus_Outcome outcome = OTIOErrorStatus_get_outcome(errorStatus);
    const char*              error = OTIOErrorStatus_outcome_to_string(outcome);
    printf("%s", error); /*type mismatch while decoding*/
    printf("\n");
}