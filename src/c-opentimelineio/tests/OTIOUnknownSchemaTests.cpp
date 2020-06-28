#include "gtest/gtest.h"

#include <copentime/rationalTime.h>
#include <copentime/timeRange.h>
#include <copentimelineio/clip.h>
#include <copentimelineio/deserialization.h>
#include <copentimelineio/errorStatus.h>
#include <copentimelineio/externalReference.h>
#include <copentimelineio/mediaReference.h>
#include <copentimelineio/missingReference.h>
#include <copentimelineio/safely_typed_any.h>
#include <copentimelineio/serializableObject.h>
#include <copentimelineio/serializableObjectWithMetadata.h>
#include <copentimelineio/serialization.h>
#include <copentimelineio/transition.h>

class OTIOUnknownSchemaTests : public ::testing::Test
{
protected:
    void SetUp() override
    {
        schema           = SerializableObject_create();
        Any* unknown_any = create_safely_typed_any_serializable_object(schema);
        OTIOErrorStatus* errorStatus          = OTIOErrorStatus_create();
        bool             decoded_successfully = deserialize_json_from_string(
            has_undefined_schema, unknown_any, errorStatus);
        schema = safely_cast_retainer_any(unknown_any);
        OTIOErrorStatus_destroy(errorStatus);
    }
    void TearDown() override { SerializableObject_possibly_delete(schema); }
    SerializableObject* schema = NULL;
    const char*         has_undefined_schema =
        "{\n"
        "    \"OTIO_SCHEMA\": \"Clip.1\",\n"
        "    \"effects\": [],\n"
        "    \"markers\": [],\n"
        "    \"media_reference\": {\n"
        "        \"OTIO_SCHEMA\": \"ExternalReference.1\",\n"
        "        \"available_range\": {\n"
        "            \"OTIO_SCHEMA\": \"TimeRange.1\",\n"
        "            \"duration\": {\n"
        "                \"OTIO_SCHEMA\": \"RationalTime.1\",\n"
        "                \"rate\": 24,\n"
        "                \"value\": 140\n"
        "            },\n"
        "            \"start_time\": {\n"
        "                \"OTIO_SCHEMA\": \"RationalTime.1\",\n"
        "                \"rate\": 24,\n"
        "                \"value\": 91\n"
        "            }\n"
        "        },\n"
        "        \"metadata\": {\n"
        "            \"stuff\": {\n"
        "                \"OTIO_SCHEMA\": \"MyOwnDangSchema.3\",\n"
        "                \"some_data\": 895,\n"
        "                \"howlongami\": {\n"
        "                     \"OTIO_SCHEMA\": \"RationalTime.1\",\n"
        "                      \"rate\": 30,\n"
        "                      \"value\": 100\n"
        "                   }\n"
        "            }\n"
        "        },\n"
        "        \"name\": null,\n"
        "        \"target_url\": \"/usr/tmp/some_media.mov\"\n"
        "    },\n"
        "    \"metadata\": {},\n"
        "    \"name\": null,\n"
        "    \"source_range\": null\n"
        "}";
};

TEST_F(OTIOUnknownSchemaTests, SerializeDeserializeTest)
{
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();
    Any* serialize_any = create_safely_typed_any_serializable_object(schema);
    const char* encoded =
        serialize_json_to_string(serialize_any, errorStatus, 4);
    Any* decoded = /** allocate memory for destinantion */
        create_safely_typed_any_serializable_object(schema);
    bool decoded_successfully =
        deserialize_json_from_string(encoded, decoded, errorStatus);
    SerializableObject* decoded_object = safely_cast_retainer_any(decoded);
    EXPECT_TRUE(SerializableObject_is_equivalent_to(schema, decoded_object));
    SerializableObject_possibly_delete(decoded_object);
    decoded_object = NULL;
}

TEST_F(OTIOUnknownSchemaTests, IsUnknownSchemaTest)
{
    EXPECT_FALSE(SerializableObject_is_unknown_schema(schema));

    Clip*                  clip           = (Clip*) schema;
    MediaReference*        mediaReference = Clip_media_reference(clip);
    AnyDictionary*         metadata = MediaReference_metadata(mediaReference);
    AnyDictionaryIterator* it       = AnyDictionary_find(metadata, "stuff");
    Any*                   any      = AnyDictionaryIterator_value(it);
    SerializableObject*    serializableObject = safely_cast_retainer_any(any);
    EXPECT_TRUE(SerializableObject_is_unknown_schema(serializableObject));
}