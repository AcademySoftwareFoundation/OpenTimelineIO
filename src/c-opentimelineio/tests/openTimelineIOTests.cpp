#include "gtest/gtest.h"

#include <copentimelineio/anyDictionary.h>
#include <copentimelineio/composable.h>
#include <copentimelineio/safely_typed_any.h>
#include <copentimelineio/serializableObjectWithMetadata.h>
#include <iostream>

class OpenTimelineIOTests : public ::testing::Test
{
protected:
    void SetUp() override {}
    void TearDown() override {}
};

TEST_F(OpenTimelineIOTests, AnyDictionaryTest)
{
    Any*                   a      = create_safely_typed_any_int(1);
    Any*                   b      = create_safely_typed_any_int(2);
    Any*                   c      = create_safely_typed_any_int(3);
    AnyDictionary*         adict  = AnyDictionary_create();
    AnyDictionaryIterator* it1    = AnyDictionary_insert(adict, "any1", a);
    AnyDictionaryIterator* it2    = AnyDictionary_insert(adict, "any2", b);
    AnyDictionaryIterator* it3    = AnyDictionary_insert(adict, "any3", c);
    AnyDictionaryIterator* it     = AnyDictionary_begin(adict);
    AnyDictionaryIterator* it_end = AnyDictionary_end(adict);
    int                    count  = 0;
    for(; AnyDictionaryIterator_not_equal(it, it_end);
        AnyDictionaryIterator_advance(it, 1))
    {
        count++;
    }
    EXPECT_EQ(count, 3);
    Any_destroy(a);
    Any_destroy(b);
    Any_destroy(c);
    AnyDictionary_destroy(adict);
    AnyDictionaryIterator_destroy(it1);
    AnyDictionaryIterator_destroy(it2);
    AnyDictionaryIterator_destroy(it3);
    AnyDictionaryIterator_destroy(it);
    AnyDictionaryIterator_destroy(it_end);
    a = b = c = NULL;
    adict     = NULL;
    it1 = it2 = it3 = it = it_end = NULL;
}

TEST_F(OpenTimelineIOTests, ComposableTest)
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