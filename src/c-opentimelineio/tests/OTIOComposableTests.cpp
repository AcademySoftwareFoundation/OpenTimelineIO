#include "gtest/gtest.h"

#include <copentimelineio/anyDictionary.h>
#include <copentimelineio/composable.h>
#include <copentimelineio/deserialization.h>
#include <copentimelineio/errorStatus.h>
#include <copentimelineio/safely_typed_any.h>
#include <copentimelineio/serializableObject.h>
#include <copentimelineio/serializableObjectWithMetadata.h>
#include <copentimelineio/serialization.h>

class OTIOComposableTests : public ::testing::Test
{
protected:
    void SetUp() override {}
    void TearDown() override {}
};

TEST_F(OTIOComposableTests, ConstructorTest)
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
    value = NULL;
    AnyDictionary_destroy(metadata);
    metadata = NULL;
    AnyDictionary_destroy(resultMetadata);
    resultMetadata = NULL;
    AnyDictionaryIterator_destroy(it);
    it = NULL;
    AnyDictionaryIterator_destroy(itMetadata);
    itMetadata = NULL;
    AnyDictionaryIterator_destroy(itMetadataEnd);
    itMetadataEnd = NULL;
    AnyDictionaryIterator_destroy(itMetadataResult);
    itMetadataResult = NULL;
}

TEST_F(OTIOComposableTests, SerializeTest)
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
    Any*        decoded = /* allocate memory for destinantion */
        create_safely_typed_any_serializable_object((SerializableObject*) seqi);

    bool decoded_successfully =
        deserialize_json_from_string(encoded, decoded, errorStatus);
    SerializableObject* decoded_object = safely_cast_retainer_any(decoded);

    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) seqi, decoded_object));

    Any_destroy(value);
    value = NULL;
    AnyDictionary_destroy(metadata);
    metadata = NULL;
    AnyDictionaryIterator_destroy(it);
    it = NULL;
    Any_destroy(seqi_any);
    seqi_any = NULL;
    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
    Any_destroy(decoded);
    decoded = NULL;
}