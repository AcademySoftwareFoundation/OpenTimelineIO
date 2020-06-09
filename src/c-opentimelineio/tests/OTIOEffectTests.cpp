#include "gtest/gtest.h"

#include <copentimelineio/anyDictionary.h>
#include <copentimelineio/deserialization.h>
#include <copentimelineio/effect.h>
#include <copentimelineio/errorStatus.h>
#include <copentimelineio/freezeFrame.h>
#include <copentimelineio/item.h>
#include <copentimelineio/linearTimeWarp.h>
#include <copentimelineio/safely_typed_any.h>
#include <copentimelineio/serializableObject.h>
#include <copentimelineio/serializableObjectWithMetadata.h>
#include <copentimelineio/serialization.h>

class OTIOEffectTests : public ::testing::Test
{
protected:
    void SetUp() override {}
    void TearDown() override {}
};

class OTIOLinearTimeWarpTests : public ::testing::Test
{
protected:
    void SetUp() override {}
    void TearDown() override {}
};

class OTIOFreezeFrameTests : public ::testing::Test
{
protected:
    void SetUp() override {}
    void TearDown() override {}
};

TEST_F(OTIOEffectTests, ConstructorTest)
{
    AnyDictionary*         metadata  = AnyDictionary_create();
    Any*                   value_any = create_safely_typed_any_string("bar");
    AnyDictionaryIterator* it =
        AnyDictionary_insert(metadata, "foo", value_any);
    Effect* ef = Effect_create("blur it", "blur", metadata);

    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    Any* effect_any =
        create_safely_typed_any_serializable_object((SerializableObject*) ef);
    const char* encoded = serialize_json_to_string(effect_any, errorStatus, 4);
    Any*        decoded = /** allocate memory for destinantion */
        create_safely_typed_any_serializable_object((SerializableObject*) ef);
    bool decoded_successfully =
        deserialize_json_from_string(encoded, decoded, errorStatus);
    ASSERT_TRUE(decoded_successfully);

    SerializableObject* decoded_object = safely_cast_retainer_any(decoded);
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) ef, decoded_object));

    EXPECT_STREQ(
        SerializableObjectWithMetadata_name(
            (SerializableObjectWithMetadata*) decoded_object),
        "blur it");
    EXPECT_STREQ(Effect_effect_name((Effect*) decoded_object), "blur");

    AnyDictionaryIterator_destroy(it);
    it = NULL;

    AnyDictionary* metadata_compare = SerializableObjectWithMetadata_metadata(
        (SerializableObjectWithMetadata*) decoded_object);
    it                            = AnyDictionary_find(metadata_compare, "foo");
    AnyDictionaryIterator* it_end = AnyDictionary_end(metadata_compare);
    ASSERT_TRUE(AnyDictionaryIterator_not_equal(it, it_end));
    Any*        compare_any   = AnyDictionaryIterator_value(it);
    const char* compare_value = safely_cast_string_any(compare_any);
    EXPECT_STREQ(compare_value, "bar");
    AnyDictionaryIterator_destroy(it);
    it = NULL;
    AnyDictionaryIterator_destroy(it_end);
    it_end = NULL;
    AnyDictionary_destroy(metadata_compare);
    metadata_compare = NULL;

    AnyDictionary_destroy(metadata);
    metadata = NULL;
    Any_destroy(value_any);
    value_any = NULL;
    Any_destroy(compare_any);
    compare_any = NULL;

    SerializableObject_possibly_delete((SerializableObject*) ef);
    ef = NULL;
    SerializableObject_possibly_delete(decoded_object);
    decoded_object = NULL;
    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
}

TEST_F(OTIOEffectTests, EqTest)
{
    AnyDictionary*         metadata  = AnyDictionary_create();
    Any*                   value_any = create_safely_typed_any_string("bar");
    AnyDictionaryIterator* it =
        AnyDictionary_insert(metadata, "foo", value_any);
    Effect* ef  = Effect_create("blur it", "blur", metadata);
    Effect* ef2 = Effect_create("blur it", "blur", metadata);

    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) ef, (SerializableObject*) ef2));

    AnyDictionaryIterator_destroy(it);
    it = NULL;
    Any_destroy(value_any);
    value_any = NULL;
    AnyDictionary_destroy(metadata);
    metadata = NULL;
    //    SerializableObject_possibly_delete((SerializableObject*) ef);
    //    ef = NULL; //TODO fix segfault
    //    SerializableObject_possibly_delete((SerializableObject*) ef2);
    //    ef2 = NULL;
}

TEST_F(OTIOLinearTimeWarpTests, ConstructorTest)
{
    AnyDictionary*         metadata  = AnyDictionary_create();
    Any*                   value_any = create_safely_typed_any_string("bar");
    AnyDictionaryIterator* it =
        AnyDictionary_insert(metadata, "foo", value_any);

    LinearTimeWarp* ef = LinearTimeWarp_create("Foo", NULL, 2.5f, metadata);

    EXPECT_STREQ(Effect_effect_name((Effect*) ef), "LinearTimeWarp");
    EXPECT_STREQ(
        SerializableObjectWithMetadata_name(
            (SerializableObjectWithMetadata*) ef),
        "Foo");
    EXPECT_EQ(LinearTimeWarp_time_scalar(ef), 2.5);

    AnyDictionary* metadata_compare = SerializableObjectWithMetadata_metadata(
        (SerializableObjectWithMetadata*) ef);
    it                            = AnyDictionary_find(metadata_compare, "foo");
    AnyDictionaryIterator* it_end = AnyDictionary_end(metadata_compare);
    ASSERT_TRUE(AnyDictionaryIterator_not_equal(it, it_end));
    Any*        compare_any   = AnyDictionaryIterator_value(it);
    const char* compare_value = safely_cast_string_any(compare_any);
    EXPECT_STREQ(compare_value, "bar");

    AnyDictionaryIterator_destroy(it);
    it = NULL;
    AnyDictionaryIterator_destroy(it_end);
    it_end = NULL;
    AnyDictionary_destroy(metadata_compare);
    metadata_compare = NULL;
    Any_destroy(compare_any);
    compare_any = NULL;
    Any_destroy(value_any);
    value_any = NULL;
    AnyDictionary_destroy(metadata);
    metadata = NULL;

    SerializableObject_possibly_delete((SerializableObject*) ef);
    ef = NULL;
}

TEST_F(OTIOFreezeFrameTests, ConstructorTest)
{
    AnyDictionary*         metadata  = AnyDictionary_create();
    Any*                   value_any = create_safely_typed_any_string("bar");
    AnyDictionaryIterator* it =
        AnyDictionary_insert(metadata, "foo", value_any);

    FreezeFrame* ef = FreezeFrame_create("Foo", metadata);

    EXPECT_STREQ(Effect_effect_name((Effect*) ef), "FreezeFrame");
    EXPECT_STREQ(
        SerializableObjectWithMetadata_name(
            (SerializableObjectWithMetadata*) ef),
        "Foo");
    EXPECT_EQ(LinearTimeWarp_time_scalar((LinearTimeWarp*) ef), 0);

    AnyDictionary* metadata_compare = SerializableObjectWithMetadata_metadata(
        (SerializableObjectWithMetadata*) ef);
    it                            = AnyDictionary_find(metadata_compare, "foo");
    AnyDictionaryIterator* it_end = AnyDictionary_end(metadata_compare);
    ASSERT_TRUE(AnyDictionaryIterator_not_equal(it, it_end));
    Any*        compare_any   = AnyDictionaryIterator_value(it);
    const char* compare_value = safely_cast_string_any(compare_any);
    EXPECT_STREQ(compare_value, "bar");

    AnyDictionaryIterator_destroy(it);
    it = NULL;
    AnyDictionaryIterator_destroy(it_end);
    it_end = NULL;
    AnyDictionary_destroy(metadata_compare);
    metadata_compare = NULL;
    Any_destroy(compare_any);
    compare_any = NULL;
    Any_destroy(value_any);
    value_any = NULL;
    AnyDictionary_destroy(metadata);
    metadata = NULL;

    SerializableObject_possibly_delete((SerializableObject*) ef);
    ef = NULL;
}