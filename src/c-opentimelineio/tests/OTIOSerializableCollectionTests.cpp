#include "gtest/gtest.h"

#include <copentimelineio/clip.h>
#include <copentimelineio/deserialization.h>
#include <copentimelineio/errorStatus.h>
#include <copentimelineio/mediaReference.h>
#include <copentimelineio/missingReference.h>
#include <copentimelineio/safely_typed_any.h>
#include <copentimelineio/serializableCollection.h>
#include <copentimelineio/serializableObject.h>
#include <copentimelineio/serializableObjectVector.h>
#include <copentimelineio/serializableObjectWithMetadata.h>
#include <copentimelineio/serialization.h>

class OTIOSerializableCollectionTests : public ::testing::Test
{
protected:
    void SetUp() override
    {
        testClip         = Clip_create("testClip", NULL, NULL, NULL);
        missingReference = MissingReference_create(NULL, NULL, NULL);
        children         = SerializableObjectVector_create();
        SerializableObjectVector_push_back(
            children, (SerializableObject*) testClip);
        SerializableObjectVector_push_back(
            children, (SerializableObject*) missingReference);
        md                        = AnyDictionary_create();
        stringAny                 = create_safely_typed_any_string("bar");
        AnyDictionaryIterator* it = AnyDictionary_insert(md, "foo", stringAny);

        sc = SerializableCollection_create("test", children, md);

        AnyDictionaryIterator_destroy(it);
        it = NULL;
        Any_destroy(stringAny);
        stringAny = NULL;
    }
    void TearDown() override
    {
        SerializableObjectVector_destroy(children);
        children = NULL;
        SerializableCollection_possibly_delete(sc);
        sc = NULL;
    }
    Clip*                     testClip;
    MissingReference*         missingReference;
    AnyDictionary*            md;
    Any*                      stringAny;
    SerializableObjectVector* children;
    SerializableCollection*   sc;
};

TEST_F(OTIOSerializableCollectionTests, ConstructorTest)
{
    EXPECT_STREQ(SerializableCollection_name(sc), "test");

    SerializableObjectRetainerVector* serializableObjectRetainerVector =
        SerializableCollection_children(sc);

    ASSERT_EQ(
        SerializableObjectRetainerVector_size(serializableObjectRetainerVector),
        SerializableObjectVector_size(children));

    SerializableObjectRetainerVectorIterator* it =
        SerializableObjectRetainerVector_begin(
            serializableObjectRetainerVector);
    SerializableObjectRetainerVectorIterator* endIt =
        SerializableObjectRetainerVector_end(serializableObjectRetainerVector);

    SerializableObjectVectorIterator* childIt =
        SerializableObjectVector_begin(children);

    for(; SerializableObjectRetainerVectorIterator_not_equal(it, endIt);
        SerializableObjectRetainerVectorIterator_advance(it, 1),
        SerializableObjectVectorIterator_advance(childIt, 1))
    {
        RetainerSerializableObject* retainerSerializableObject =
            SerializableObjectRetainerVectorIterator_value(it);
        SerializableObject* serializableObject =
            RetainerSerializableObject_value(retainerSerializableObject);
        SerializableObject* compareSerializableObject =
            SerializableObjectVectorIterator_value(childIt);
        EXPECT_EQ(serializableObject, compareSerializableObject);
    }

    SerializableObjectVectorIterator_destroy(childIt);
    childIt = NULL;
    SerializableObjectRetainerVectorIterator_destroy(it);
    it = NULL;
    SerializableObjectRetainerVectorIterator_destroy(endIt);
    endIt = NULL;

    AnyDictionary* resultMetadata = SerializableCollection_metadata(sc);
    ASSERT_EQ(AnyDictionary_size(md), AnyDictionary_size(resultMetadata));

    AnyDictionaryIterator* itMetadata    = AnyDictionary_begin(md);
    AnyDictionaryIterator* itMetadataEnd = AnyDictionary_end(md);
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

    AnyDictionaryIterator_destroy(itMetadata);
    itMetadata = NULL;
    AnyDictionaryIterator_destroy(itMetadataEnd);
    itMetadataEnd = NULL;
    AnyDictionaryIterator_destroy(itMetadataResult);
    itMetadataResult = NULL;
}

TEST_F(OTIOSerializableCollectionTests, SerializeTest)
{
    Any* sc_any =
        create_safely_typed_any_serializable_object((SerializableObject*) sc);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    const char* encoded = serialize_json_to_string(sc_any, errorStatus, 4);
    Any*        decoded = /* allocate memory for destinantion */
        create_safely_typed_any_serializable_object((SerializableObject*) sc);

    bool decoded_successfully =
        deserialize_json_from_string(encoded, decoded, errorStatus);
    ASSERT_TRUE(decoded_successfully);
    SerializableObject* decoded_object = safely_cast_retainer_any(decoded);

    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) sc, decoded_object));

    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
    Any_destroy(decoded);
    decoded = NULL;
}