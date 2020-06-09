#include "gtest/gtest.h"

#include <copentime/rationalTime.h>
#include <copentime/timeRange.h>
#include <copentimelineio/clip.h>
#include <copentimelineio/composable.h>
#include <copentimelineio/composition.h>
#include <copentimelineio/deserialization.h>
#include <copentimelineio/errorStatus.h>
#include <copentimelineio/generatorReference.h>
#include <copentimelineio/mediaReference.h>
#include <copentimelineio/safely_typed_any.h>
#include <copentimelineio/serializableObject.h>
#include <copentimelineio/serializableObjectWithMetadata.h>
#include <copentimelineio/serialization.h>
#include <copentimelineio/stack.h>
#include <copentimelineio/timeline.h>
#include <copentimelineio/track.h>

#define xstr(s) str(s)
#define str(s) #s

class OTIOGeneratorReferenceTests : public ::testing::Test
{
protected:
    void SetUp() override
    {
        RationalTime* start_time = RationalTime_create(0, 24);
        RationalTime* duration   = RationalTime_create(100, 24);
        TimeRange*    available_range =
            TimeRange_create_with_start_time_and_duration(start_time, duration);

        AnyDictionary* metadata  = AnyDictionary_create();
        Any*           value_any = create_safely_typed_any_string("bar");
        AnyDictionaryIterator* it =
            AnyDictionary_insert(metadata, "foo", value_any);

        AnyDictionaryIterator_destroy(it);
        it = NULL;
        Any_destroy(value_any);
        value_any = NULL;

        AnyDictionary* parameters = AnyDictionary_create();
        value_any                 = create_safely_typed_any_double(5.0);
        it = AnyDictionary_insert(parameters, "test_param", value_any);

        AnyDictionaryIterator_destroy(it);
        it = NULL;
        Any_destroy(value_any);
        value_any = NULL;

        gen = GeneratorReference_create(
            "SMPTEBars", "SMPTEBars", available_range, parameters, metadata);

        RationalTime_destroy(start_time);
        start_time = NULL;
        RationalTime_destroy(duration);
        duration = NULL;
        TimeRange_destroy(available_range);
        available_range = NULL;
        AnyDictionary_destroy(metadata);
        metadata = NULL;
        AnyDictionary_destroy(parameters);
        parameters = NULL;

        sample_data_dir = xstr(SAMPLE_DATA_DIR);
    }
    void TearDown() override
    {
        SerializableObject_possibly_delete((SerializableObject*) gen);
        gen = NULL;
    }

    GeneratorReference* gen;
    const char*         sample_data_dir;
};

TEST_F(OTIOGeneratorReferenceTests, ConstructorTest)
{
    EXPECT_STREQ(GeneratorReference_generator_kind(gen), "SMPTEBars");
    EXPECT_STREQ(
        SerializableObjectWithMetadata_name(
            (SerializableObjectWithMetadata*) gen),
        "SMPTEBars");

    AnyDictionary* metadata_compare = SerializableObjectWithMetadata_metadata(
        (SerializableObjectWithMetadata*) gen);
    AnyDictionaryIterator* it     = AnyDictionary_find(metadata_compare, "foo");
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
    Any_destroy(compare_any);
    compare_any = NULL;

    AnyDictionary* parameters_compare = GeneratorReference_parameters(gen);
    it     = AnyDictionary_find(parameters_compare, "test_param");
    it_end = AnyDictionary_end(parameters_compare);
    ASSERT_TRUE(AnyDictionaryIterator_not_equal(it, it_end));
    compare_any                 = AnyDictionaryIterator_value(it);
    double compare_value_double = safely_cast_double_any(compare_any);
    EXPECT_EQ(AnyDictionary_size(parameters_compare), 1);
    EXPECT_EQ(compare_value_double, 5.0);

    AnyDictionaryIterator_destroy(it);
    it = NULL;
    AnyDictionaryIterator_destroy(it_end);
    it_end = NULL;
    AnyDictionary_destroy(metadata_compare);
    metadata_compare = NULL;
    Any_destroy(compare_any);
    compare_any = NULL;
    AnyDictionary_destroy(metadata_compare);
    metadata_compare = NULL;
    AnyDictionary_destroy(parameters_compare);
    parameters_compare = NULL;

    TimeRange* gen_available_range =
        MediaReference_available_range((MediaReference*) gen);
    RationalTime* st = RationalTime_create(0, 24);
    RationalTime* d  = RationalTime_create(100, 24);
    TimeRange*    range_compare =
        TimeRange_create_with_start_time_and_duration(st, d);

    EXPECT_TRUE(TimeRange_equal(gen_available_range, range_compare));

    RationalTime_destroy(st);
    st = NULL;
    RationalTime_destroy(d);
    d = NULL;
    TimeRange_destroy(range_compare);
    range_compare = NULL;
}

TEST_F(OTIOGeneratorReferenceTests, SerializeTest)
{
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    Any* ref_any =
        create_safely_typed_any_serializable_object((SerializableObject*) gen);
    const char* encoded = serialize_json_to_string(ref_any, errorStatus, 4);
    Any*        decoded = /** allocate memory for destinantion */
        create_safely_typed_any_serializable_object((SerializableObject*) gen);
    bool decoded_successfully =
        deserialize_json_from_string(encoded, decoded, errorStatus);
    ASSERT_TRUE(decoded_successfully);

    SerializableObject* decoded_object = safely_cast_retainer_any(decoded);
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) gen, decoded_object));

    Any_destroy(decoded);
    decoded = NULL;
    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
}

TEST_F(OTIOGeneratorReferenceTests, ReadFileTest)
{
    const char* ref_file = "generator_reference_test.otio";
    char*       ref_path = (char*) calloc(
        strlen(sample_data_dir) + strlen(ref_file) + 1, sizeof(char));
    strcpy(ref_path, sample_data_dir);
    strcat(ref_path, ref_file);

    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    SerializableObject* so = SerializableObject_create();

    Any* ref_any = create_safely_typed_any_serializable_object(so);
    bool deserializeOK =
        deserialize_json_from_file(ref_path, ref_any, errorStatus);
    ASSERT_TRUE(deserializeOK);

    Timeline* timeline = (Timeline*) safely_cast_retainer_any(ref_any);

    Stack* stack = Timeline_tracks(timeline);

    ComposableRetainerVector* track_retainer_vector =
        Composition_children((Composition*) stack);
    RetainerComposable* track_0_retainer =
        ComposableRetainerVector_at(track_retainer_vector, 0);

    Track* track_0 = (Track*) RetainerComposable_value(track_0_retainer);

    ComposableRetainerVector* children_retainer_vector =
        Composition_children((Composition*) track_0);
    RetainerComposable* clip_0_retainer =
        ComposableRetainerVector_at(children_retainer_vector, 0);

    Clip* clip_0 = (Clip*) RetainerComposable_value(clip_0_retainer);

    MediaReference* media_reference = Clip_media_reference(clip_0);

    EXPECT_STREQ(
        GeneratorReference_generator_kind(
            (GeneratorReference*) media_reference),
        "SMPTEBars");

    ComposableRetainerVector_destroy(children_retainer_vector);
    children_retainer_vector = NULL;
    ComposableRetainerVector_destroy(track_retainer_vector);
    track_retainer_vector = NULL;
    SerializableObject_possibly_delete((SerializableObject*) timeline);
    timeline = NULL;
    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
}