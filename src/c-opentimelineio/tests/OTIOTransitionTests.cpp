#include "gtest/gtest.h"

#include <copentimelineio/deserialization.h>
#include <copentimelineio/errorStatus.h>
#include <copentimelineio/safely_typed_any.h>
#include <copentimelineio/serializableObject.h>
#include <copentimelineio/serializableObjectWithMetadata.h>
#include <copentimelineio/transition.h>

class OTIOTransitionTests : public ::testing::Test
{
protected:
    void SetUp() override {}
    void TearDown() override {}
};

TEST_F(OTIOTransitionTests, ConstructorTest)
{
    AnyDictionary*         metadata  = AnyDictionary_create();
    Any*                   value_any = create_safely_typed_any_string("bar");
    AnyDictionaryIterator* it =
        AnyDictionary_insert(metadata, "foo", value_any);

    Transition* trx =
        Transition_create("AtoB", "SMPTE.Dissolve", NULL, NULL, metadata);

    AnyDictionaryIterator_destroy(it);
    it = NULL;

    EXPECT_STREQ(Transition_transition_type(trx), "SMPTE.Dissolve");
    EXPECT_STREQ(Transition_name(trx), "AtoB");

    AnyDictionary* metadata_compare = Transition_metadata(trx);
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

    SerializableObject_possibly_delete((SerializableObject*) trx);
    trx = NULL;
    Any_destroy(value_any);
}