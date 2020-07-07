#include "gtest/gtest.h"

#include <copentimelineio/clip.h>
#include <copentimelineio/deserialization.h>
#include <copentimelineio/errorStatus.h>
#include <copentimelineio/gap.h>
#include <copentimelineio/missingReference.h>
#include <copentimelineio/safely_typed_any.h>
#include <copentimelineio/serializableCollection.h>
#include <copentimelineio/serializableObject.h>
#include <copentimelineio/serializableObjectWithMetadata.h>
#include <copentimelineio/serialization.h>
#include <copentimelineio/stackAlgorithm.h>
#include <copentimelineio/timeline.h>
#include <copentimelineio/track.h>
#include <copentimelineio/transition.h>

#define xstr(s) str(s)
#define str(s) #s

class OTIOStackAlgoTests : public ::testing::Test
{
protected:
    void SetUp() override
    {
        OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

        /* trackZ */
        Any* decoded = /* allocate memory for destinantion */
            create_safely_typed_any_serializable_object(
                SerializableObject_create());
        bool decoded_successfully =
            deserialize_json_from_string(trackZStr, decoded, errorStatus);
        SerializableObject* decoded_object = safely_cast_retainer_any(decoded);
        trackZ                             = (Track*) decoded_object;

        /* trackABC */
        decoded = /* allocate memory for destinantion */
            create_safely_typed_any_serializable_object(
                SerializableObject_create());
        decoded_successfully =
            deserialize_json_from_string(trackABCStr, decoded, errorStatus);
        decoded_object = safely_cast_retainer_any(decoded);
        trackABC       = (Track*) decoded_object;

        /* trackDgE */
        decoded = /* allocate memory for destinantion */
            create_safely_typed_any_serializable_object(
                SerializableObject_create());
        decoded_successfully =
            deserialize_json_from_string(trackDgEStr, decoded, errorStatus);
        decoded_object = safely_cast_retainer_any(decoded);
        trackDgE       = (Track*) decoded_object;

        /* trackgFg */
        decoded = /* allocate memory for destinantion */
            create_safely_typed_any_serializable_object(
                SerializableObject_create());
        decoded_successfully =
            deserialize_json_from_string(trackgFgStr, decoded, errorStatus);
        decoded_object = safely_cast_retainer_any(decoded);
        trackgFg       = (Track*) decoded_object;

        OTIOErrorStatus_destroy(errorStatus);
        errorStatus = NULL;

        sample_data_dir = xstr(SAMPLE_DATA_DIR);
    }
    void TearDown() override
    {
        //        Track_possibly_delete(trackZ);
        //        Track_possibly_delete(trackABC);
        //        Track_possibly_delete(trackDgE);
        //        Track_possibly_delete(trackgFg);
        //        trackZ = trackABC = trackDgE = trackgFg = NULL;
    }

    const char* sample_data_dir;

    Track* trackZ   = NULL;
    Track* trackABC = NULL;
    Track* trackDgE = NULL;
    Track* trackgFg = NULL;

    const char* trackZStr =
        "{\n"
        "            \"OTIO_SCHEMA\": \"Track.1\",\n"
        "            \"children\": [\n"
        "                {\n"
        "                    \"OTIO_SCHEMA\": \"Clip.1\",\n"
        "                    \"effects\": [],\n"
        "                    \"markers\": [],\n"
        "                    \"media_reference\": null,\n"
        "                    \"metadata\": {},\n"
        "                    \"name\": \"Z\",\n"
        "                    \"source_range\": {\n"
        "                        \"OTIO_SCHEMA\": \"TimeRange.1\",\n"
        "                        \"duration\": {\n"
        "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n"
        "                            \"rate\": 24,\n"
        "                            \"value\": 150\n"
        "                        },\n"
        "                        \"start_time\": {\n"
        "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n"
        "                            \"rate\": 24,\n"
        "                            \"value\": 0.0\n"
        "                        }\n"
        "                    }\n"
        "                }\n"
        "            ],\n"
        "            \"effects\": [],\n"
        "            \"kind\": \"Video\",\n"
        "            \"markers\": [],\n"
        "            \"metadata\": {},\n"
        "            \"name\": \"Sequence1\",\n"
        "            \"source_range\": null\n"
        "        }";

    const char* trackABCStr =
        "{\n"
        "            \"OTIO_SCHEMA\": \"Track.1\",\n"
        "            \"children\": [\n"
        "                {\n"
        "                    \"OTIO_SCHEMA\": \"Clip.1\",\n"
        "                    \"effects\": [],\n"
        "                    \"markers\": [],\n"
        "                    \"media_reference\": null,\n"
        "                    \"metadata\": {},\n"
        "                    \"name\": \"A\",\n"
        "                    \"source_range\": {\n"
        "                        \"OTIO_SCHEMA\": \"TimeRange.1\",\n"
        "                        \"duration\": {\n"
        "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n"
        "                            \"rate\": 24,\n"
        "                            \"value\": 50\n"
        "                        },\n"
        "                        \"start_time\": {\n"
        "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n"
        "                            \"rate\": 24,\n"
        "                            \"value\": 0.0\n"
        "                        }\n"
        "                    }\n"
        "                },\n"
        "                {\n"
        "                    \"OTIO_SCHEMA\": \"Clip.1\",\n"
        "                    \"effects\": [],\n"
        "                    \"markers\": [],\n"
        "                    \"media_reference\": null,\n"
        "                    \"metadata\": {},\n"
        "                    \"name\": \"B\",\n"
        "                    \"source_range\": {\n"
        "                        \"OTIO_SCHEMA\": \"TimeRange.1\",\n"
        "                        \"duration\": {\n"
        "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n"
        "                            \"rate\": 24,\n"
        "                            \"value\": 50\n"
        "                        },\n"
        "                        \"start_time\": {\n"
        "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n"
        "                            \"rate\": 24,\n"
        "                            \"value\": 0.0\n"
        "                        }\n"
        "                    }\n"
        "                },\n"
        "                {\n"
        "                    \"OTIO_SCHEMA\": \"Clip.1\",\n"
        "                    \"effects\": [],\n"
        "                    \"markers\": [],\n"
        "                    \"media_reference\": null,\n"
        "                    \"metadata\": {},\n"
        "                    \"name\": \"C\",\n"
        "                    \"source_range\": {\n"
        "                        \"OTIO_SCHEMA\": \"TimeRange.1\",\n"
        "                        \"duration\": {\n"
        "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n"
        "                            \"rate\": 24,\n"
        "                            \"value\": 50\n"
        "                        },\n"
        "                        \"start_time\": {\n"
        "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n"
        "                            \"rate\": 24,\n"
        "                            \"value\": 0.0\n"
        "                        }\n"
        "                    }\n"
        "                }\n"
        "            ],\n"
        "            \"effects\": [],\n"
        "            \"kind\": \"Video\",\n"
        "            \"markers\": [],\n"
        "            \"metadata\": {},\n"
        "            \"name\": \"Sequence1\",\n"
        "            \"source_range\": null\n"
        "        }";

    const char* trackDgEStr =
        "{\n"
        "            \"OTIO_SCHEMA\": \"Track.1\",\n"
        "            \"children\": [\n"
        "                {\n"
        "                    \"OTIO_SCHEMA\": \"Clip.1\",\n"
        "                    \"effects\": [],\n"
        "                    \"markers\": [],\n"
        "                    \"media_reference\": null,\n"
        "                    \"metadata\": {},\n"
        "                    \"name\": \"D\",\n"
        "                    \"source_range\": {\n"
        "                        \"OTIO_SCHEMA\": \"TimeRange.1\",\n"
        "                        \"duration\": {\n"
        "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n"
        "                            \"rate\": 24,\n"
        "                            \"value\": 50\n"
        "                        },\n"
        "                        \"start_time\": {\n"
        "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n"
        "                            \"rate\": 24,\n"
        "                            \"value\": 0.0\n"
        "                        }\n"
        "                    }\n"
        "                },\n"
        "                {\n"
        "                    \"OTIO_SCHEMA\": \"Gap.1\",\n"
        "                    \"effects\": [],\n"
        "                    \"markers\": [],\n"
        "                    \"media_reference\": null,\n"
        "                    \"metadata\": {},\n"
        "                    \"name\": \"g\",\n"
        "                    \"source_range\": {\n"
        "                        \"OTIO_SCHEMA\": \"TimeRange.1\",\n"
        "                        \"duration\": {\n"
        "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n"
        "                            \"rate\": 24,\n"
        "                            \"value\": 50\n"
        "                        },\n"
        "                        \"start_time\": {\n"
        "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n"
        "                            \"rate\": 24,\n"
        "                            \"value\": 0.0\n"
        "                        }\n"
        "                    }\n"
        "                },\n"
        "                {\n"
        "                    \"OTIO_SCHEMA\": \"Clip.1\",\n"
        "                    \"effects\": [],\n"
        "                    \"markers\": [],\n"
        "                    \"media_reference\": null,\n"
        "                    \"metadata\": {},\n"
        "                    \"name\": \"E\",\n"
        "                    \"source_range\": {\n"
        "                        \"OTIO_SCHEMA\": \"TimeRange.1\",\n"
        "                        \"duration\": {\n"
        "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n"
        "                            \"rate\": 24,\n"
        "                            \"value\": 50\n"
        "                        },\n"
        "                        \"start_time\": {\n"
        "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n"
        "                            \"rate\": 24,\n"
        "                            \"value\": 0.0\n"
        "                        }\n"
        "                    }\n"
        "                }\n"
        "            ],\n"
        "            \"effects\": [],\n"
        "            \"kind\": \"Video\",\n"
        "            \"markers\": [],\n"
        "            \"metadata\": {},\n"
        "            \"name\": \"Sequence1\",\n"
        "            \"source_range\": null\n"
        "        }";

    const char* trackgFgStr =
        "{\n"
        "            \"OTIO_SCHEMA\": \"Track.1\",\n"
        "            \"children\": [\n"
        "                {\n"
        "                    \"OTIO_SCHEMA\": \"Gap.1\",\n"
        "                    \"effects\": [],\n"
        "                    \"markers\": [],\n"
        "                    \"media_reference\": null,\n"
        "                    \"metadata\": {},\n"
        "                    \"name\": \"g1\",\n"
        "                    \"source_range\": {\n"
        "                        \"OTIO_SCHEMA\": \"TimeRange.1\",\n"
        "                        \"duration\": {\n"
        "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n"
        "                            \"rate\": 24,\n"
        "                            \"value\": 50\n"
        "                        },\n"
        "                        \"start_time\": {\n"
        "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n"
        "                            \"rate\": 24,\n"
        "                            \"value\": 0.0\n"
        "                        }\n"
        "                    }\n"
        "                },\n"
        "                {\n"
        "                    \"OTIO_SCHEMA\": \"Clip.1\",\n"
        "                    \"effects\": [],\n"
        "                    \"markers\": [],\n"
        "                    \"media_reference\": null,\n"
        "                    \"metadata\": {},\n"
        "                    \"name\": \"F\",\n"
        "                    \"source_range\": {\n"
        "                        \"OTIO_SCHEMA\": \"TimeRange.1\",\n"
        "                        \"duration\": {\n"
        "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n"
        "                            \"rate\": 24,\n"
        "                            \"value\": 50\n"
        "                        },\n"
        "                        \"start_time\": {\n"
        "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n"
        "                            \"rate\": 24,\n"
        "                            \"value\": 0.0\n"
        "                        }\n"
        "                    }\n"
        "                },\n"
        "                {\n"
        "                    \"OTIO_SCHEMA\": \"Gap.1\",\n"
        "                    \"effects\": [],\n"
        "                    \"markers\": [],\n"
        "                    \"media_reference\": null,\n"
        "                    \"metadata\": {},\n"
        "                    \"name\": \"g2\",\n"
        "                    \"source_range\": {\n"
        "                        \"OTIO_SCHEMA\": \"TimeRange.1\",\n"
        "                        \"duration\": {\n"
        "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n"
        "                            \"rate\": 24,\n"
        "                            \"value\": 50\n"
        "                        },\n"
        "                        \"start_time\": {\n"
        "                            \"OTIO_SCHEMA\": \"RationalTime.1\",\n"
        "                            \"rate\": 24,\n"
        "                            \"value\": 0.0\n"
        "                        }\n"
        "                    }\n"
        "                }\n"
        "            ],\n"
        "            \"effects\": [],\n"
        "            \"kind\": \"Video\",\n"
        "            \"markers\": [],\n"
        "            \"metadata\": {},\n"
        "            \"name\": \"Sequence1\",\n"
        "            \"source_range\": null\n"
        "        }";
};

TEST_F(OTIOStackAlgoTests, FlattenSingleTrackTest)
{
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();
    Stack*           stack       = Stack_create(NULL, NULL, NULL, NULL, NULL);
    ASSERT_TRUE(
        Stack_insert_child(stack, 0, (Composable*) trackABC, errorStatus));

    Track* flattenedStack = flatten_stack(stack, errorStatus);
    Track_set_name(flattenedStack, "Sequence1");
    Any* s_any = create_safely_typed_any_serializable_object(
        (SerializableObject*) flattenedStack);

    EXPECT_NE(flattenedStack, trackABC);

    EXPECT_TRUE(
        Track_is_equivalent_to(flattenedStack, (SerializableObject*) trackABC));

    Track_possibly_delete(flattenedStack);
    flattenedStack = NULL;
    OTIOErrorStatus_destroy(errorStatus);

    Stack_possibly_delete(stack);
    stack = NULL;

    Track_possibly_delete(trackZ);
    Track_possibly_delete(trackABC);
    Track_possibly_delete(trackDgE);
    Track_possibly_delete(trackgFg);
    trackZ = trackABC = trackDgE = trackgFg = NULL;
}

TEST_F(OTIOStackAlgoTests, FlattenObscuredTrackTest)
{
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();
    Stack*           stack       = Stack_create(NULL, NULL, NULL, NULL, NULL);
    ASSERT_TRUE(
        Stack_insert_child(stack, 0, (Composable*) trackABC, errorStatus));
    ASSERT_TRUE(
        Stack_insert_child(stack, 1, (Composable*) trackZ, errorStatus));

    Track* flattenedStack = flatten_stack(stack, errorStatus);
    Track_set_name(flattenedStack, "Sequence1");
    EXPECT_NE(flattenedStack, trackZ);
    EXPECT_TRUE(
        Track_is_equivalent_to(flattenedStack, (SerializableObject*) trackZ));

    //    Track_possibly_delete(flattenedStack); // TODO: Fix segafault
    //    flattenedStack = NULL;
    Stack_possibly_delete(stack);
    stack = NULL;

    stack = Stack_create(NULL, NULL, NULL, NULL, NULL);
    ASSERT_TRUE(
        Stack_insert_child(stack, 0, (Composable*) trackZ, errorStatus));
    ASSERT_TRUE(
        Stack_insert_child(stack, 1, (Composable*) trackABC, errorStatus));
    flattenedStack = flatten_stack(stack, errorStatus);
    Track_set_name(flattenedStack, "Sequence1");
    EXPECT_NE(flattenedStack, trackABC);
    EXPECT_TRUE(
        Track_is_equivalent_to(flattenedStack, (SerializableObject*) trackABC));

    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
    Track_possibly_delete(trackZ);
    Track_possibly_delete(trackABC);
    Track_possibly_delete(trackDgE);
    Track_possibly_delete(trackgFg);
    trackZ = trackABC = trackDgE = trackgFg = NULL;
}

TEST_F(OTIOStackAlgoTests, FlattenGapsTest)
{
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();
    Stack*           stack       = Stack_create(NULL, NULL, NULL, NULL, NULL);
    ASSERT_TRUE(
        Stack_insert_child(stack, 0, (Composable*) trackABC, errorStatus));
    ASSERT_TRUE(
        Stack_insert_child(stack, 1, (Composable*) trackDgE, errorStatus));

    Track* flattenedStack = flatten_stack(stack, errorStatus);
    Track_set_name(flattenedStack, "Sequence1");

    ComposableRetainerVector* flattenedStackChildren =
        Track_children(flattenedStack);
    ComposableRetainerVectorIterator* flattenedStackIt =
        ComposableRetainerVector_begin(flattenedStackChildren);
    RetainerComposable* flattenedStack_0_retainer =
        ComposableRetainerVectorIterator_value(flattenedStackIt);
    Composable* flattenedStack_0 =
        RetainerComposable_value(flattenedStack_0_retainer);
    ComposableRetainerVectorIterator_advance(flattenedStackIt, 1);
    RetainerComposable* flattenedStack_1_retainer =
        ComposableRetainerVectorIterator_value(flattenedStackIt);
    Composable* flattenedStack_1 =
        RetainerComposable_value(flattenedStack_1_retainer);
    ComposableRetainerVectorIterator_advance(flattenedStackIt, 1);
    RetainerComposable* flattenedStack_2_retainer =
        ComposableRetainerVectorIterator_value(flattenedStackIt);
    Composable* flattenedStack_2 =
        RetainerComposable_value(flattenedStack_2_retainer);
    ComposableRetainerVector_destroy(flattenedStackChildren);
    flattenedStackChildren = NULL;
    ComposableRetainerVectorIterator_destroy(flattenedStackIt);
    flattenedStackIt = NULL;

    ComposableRetainerVector* trackDgEChildren = Track_children(trackDgE);
    ComposableRetainerVectorIterator* trackDgEIt =
        ComposableRetainerVector_begin(trackDgEChildren);
    RetainerComposable* trackDgE_0_retainer =
        ComposableRetainerVectorIterator_value(trackDgEIt);
    Composable* trackDgE_0 = RetainerComposable_value(trackDgE_0_retainer);
    ComposableRetainerVectorIterator_advance(trackDgEIt, 2);
    RetainerComposable* trackDgE_2_retainer =
        ComposableRetainerVectorIterator_value(trackDgEIt);
    Composable* trackDgE_2 = RetainerComposable_value(trackDgE_2_retainer);
    ComposableRetainerVector_destroy(trackDgEChildren);
    trackDgEChildren = NULL;
    ComposableRetainerVectorIterator_destroy(trackDgEIt);
    trackDgEIt = NULL;

    ComposableRetainerVector* trackABCChildren = Track_children(trackABC);
    ComposableRetainerVectorIterator* trackABCIt =
        ComposableRetainerVector_begin(trackABCChildren);
    RetainerComposable* trackABC_0_retainer =
        ComposableRetainerVectorIterator_value(trackABCIt);
    Composable* trackABC_0 = RetainerComposable_value(trackABC_0_retainer);
    ComposableRetainerVectorIterator_advance(trackABCIt, 1);
    RetainerComposable* trackABC_1_retainer =
        ComposableRetainerVectorIterator_value(trackABCIt);
    Composable* trackABC_1 = RetainerComposable_value(trackABC_1_retainer);
    ComposableRetainerVectorIterator_advance(trackABCIt, 1);
    RetainerComposable* trackABC_2_retainer =
        ComposableRetainerVectorIterator_value(trackABCIt);
    Composable* trackABC_2 = RetainerComposable_value(trackABC_2_retainer);
    ComposableRetainerVector_destroy(trackABCChildren);
    trackABCChildren = NULL;
    ComposableRetainerVectorIterator_destroy(trackABCIt);
    trackABCIt = NULL;

    EXPECT_NE(flattenedStack_0, trackDgE_0);
    EXPECT_NE(flattenedStack_1, trackABC_1);
    EXPECT_NE(flattenedStack_2, trackDgE_2);
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) flattenedStack_0,
        (SerializableObject*) trackDgE_0));
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) flattenedStack_1,
        (SerializableObject*) trackABC_1));
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) flattenedStack_2,
        (SerializableObject*) trackDgE_2));

    Stack_possibly_delete(stack);
    stack = Stack_create(NULL, NULL, NULL, NULL, NULL);
    ASSERT_TRUE(
        Stack_insert_child(stack, 0, (Composable*) trackABC, errorStatus));
    ASSERT_TRUE(
        Stack_insert_child(stack, 1, (Composable*) trackgFg, errorStatus));
    flattenedStack = flatten_stack(stack, errorStatus);
    Track_set_name(flattenedStack, "Sequence1");

    flattenedStackChildren = Track_children(flattenedStack);
    flattenedStackIt = ComposableRetainerVector_begin(flattenedStackChildren);
    flattenedStack_0_retainer =
        ComposableRetainerVectorIterator_value(flattenedStackIt);
    flattenedStack_0 = RetainerComposable_value(flattenedStack_0_retainer);
    ComposableRetainerVectorIterator_advance(flattenedStackIt, 1);
    flattenedStack_1_retainer =
        ComposableRetainerVectorIterator_value(flattenedStackIt);
    flattenedStack_1 = RetainerComposable_value(flattenedStack_1_retainer);
    ComposableRetainerVectorIterator_advance(flattenedStackIt, 1);
    flattenedStack_2_retainer =
        ComposableRetainerVectorIterator_value(flattenedStackIt);
    flattenedStack_2 = RetainerComposable_value(flattenedStack_2_retainer);
    ComposableRetainerVector_destroy(flattenedStackChildren);
    flattenedStackChildren = NULL;
    ComposableRetainerVectorIterator_destroy(flattenedStackIt);
    flattenedStackIt = NULL;

    ComposableRetainerVector* trackgFgChildren = Track_children(trackgFg);
    ComposableRetainerVectorIterator* trackgFgIt =
        ComposableRetainerVector_begin(trackgFgChildren);
    ComposableRetainerVectorIterator_advance(trackgFgIt, 1);
    RetainerComposable* trackgFg_1_retainer =
        ComposableRetainerVectorIterator_value(trackgFgIt);
    Composable* trackgFg_1 = RetainerComposable_value(trackgFg_1_retainer);
    ComposableRetainerVector_destroy(trackgFgChildren);
    trackgFgChildren = NULL;
    ComposableRetainerVectorIterator_destroy(trackgFgIt);
    trackgFgIt = NULL;

    EXPECT_NE(flattenedStack_0, trackABC_0);
    EXPECT_NE(flattenedStack_1, trackgFg_1);
    EXPECT_NE(flattenedStack_2, trackABC_2);
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) flattenedStack_0,
        (SerializableObject*) trackABC_0));
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) flattenedStack_1,
        (SerializableObject*) trackgFg_1));
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) flattenedStack_2,
        (SerializableObject*) trackABC_2));

    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
    Track_possibly_delete(trackZ);
    Track_possibly_delete(trackABC);
    Track_possibly_delete(trackDgE);
    Track_possibly_delete(trackgFg);
    trackZ = trackABC = trackDgE = trackgFg = NULL;
}

TEST_F(OTIOStackAlgoTests, FlattenGapsWithTrimsTest)
{
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();
    Stack*           stack       = Stack_create(NULL, NULL, NULL, NULL, NULL);
    ASSERT_TRUE(
        Stack_insert_child(stack, 0, (Composable*) trackZ, errorStatus));
    ASSERT_TRUE(
        Stack_insert_child(stack, 1, (Composable*) trackDgE, errorStatus));

    Track* flattenedStack = flatten_stack(stack, errorStatus);
    Track_set_name(flattenedStack, "Sequence1");

    ComposableRetainerVector* flattenedStackChildren =
        Track_children(flattenedStack);
    ComposableRetainerVectorIterator* flattenedStackIt =
        ComposableRetainerVector_begin(flattenedStackChildren);
    RetainerComposable* flattenedStack_0_retainer =
        ComposableRetainerVectorIterator_value(flattenedStackIt);
    Composable* flattenedStack_0 =
        RetainerComposable_value(flattenedStack_0_retainer);
    ComposableRetainerVectorIterator_advance(flattenedStackIt, 1);
    RetainerComposable* flattenedStack_1_retainer =
        ComposableRetainerVectorIterator_value(flattenedStackIt);
    Composable* flattenedStack_1 =
        RetainerComposable_value(flattenedStack_1_retainer);
    ComposableRetainerVectorIterator_advance(flattenedStackIt, 1);
    RetainerComposable* flattenedStack_2_retainer =
        ComposableRetainerVectorIterator_value(flattenedStackIt);
    Composable* flattenedStack_2 =
        RetainerComposable_value(flattenedStack_2_retainer);
    ComposableRetainerVector_destroy(flattenedStackChildren);
    flattenedStackChildren = NULL;
    ComposableRetainerVectorIterator_destroy(flattenedStackIt);
    flattenedStackIt = NULL;

    ComposableRetainerVector* trackDgEChildren = Track_children(trackDgE);
    ComposableRetainerVectorIterator* trackDgEIt =
        ComposableRetainerVector_begin(trackDgEChildren);
    RetainerComposable* trackDgE_0_retainer =
        ComposableRetainerVectorIterator_value(trackDgEIt);
    Composable* trackDgE_0 = RetainerComposable_value(trackDgE_0_retainer);
    ComposableRetainerVectorIterator_advance(trackDgEIt, 2);
    RetainerComposable* trackDgE_2_retainer =
        ComposableRetainerVectorIterator_value(trackDgEIt);
    Composable* trackDgE_2 = RetainerComposable_value(trackDgE_2_retainer);
    ComposableRetainerVector_destroy(trackDgEChildren);
    trackDgEChildren = NULL;
    ComposableRetainerVectorIterator_destroy(trackDgEIt);
    trackDgEIt = NULL;
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) flattenedStack_0,
        (SerializableObject*) trackDgE_0));
    EXPECT_STREQ(Composable_name(flattenedStack_1), "Z");
    RationalTime* start    = RationalTime_create(50, 24);
    RationalTime* duration = RationalTime_create(50, 24);
    TimeRange*    tr =
        TimeRange_create_with_start_time_and_duration(start, duration);
    TimeRange* flattenedStack_1_source_range =
        Clip_source_range((Clip*) flattenedStack_1);
    EXPECT_TRUE(TimeRange_equal(tr, flattenedStack_1_source_range));
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) flattenedStack_2,
        (SerializableObject*) trackDgE_2));
    TimeRange_destroy(tr);
    TimeRange_destroy(flattenedStack_1_source_range);
    RationalTime_destroy(start);
    RationalTime_destroy(duration);

    Stack_possibly_delete(stack);
    stack = NULL;
    Track_possibly_delete(flattenedStack);
    flattenedStack = NULL;

    stack = Stack_create(NULL, NULL, NULL, NULL, NULL);
    ASSERT_TRUE(
        Stack_insert_child(stack, 0, (Composable*) trackZ, errorStatus));
    ASSERT_TRUE(
        Stack_insert_child(stack, 1, (Composable*) trackgFg, errorStatus));
    flattenedStack = flatten_stack(stack, errorStatus);
    Track_set_name(flattenedStack, "Sequence1");

    flattenedStackChildren = Track_children(flattenedStack);
    flattenedStackIt = ComposableRetainerVector_begin(flattenedStackChildren);
    flattenedStack_0_retainer =
        ComposableRetainerVectorIterator_value(flattenedStackIt);
    flattenedStack_0 = RetainerComposable_value(flattenedStack_0_retainer);
    ComposableRetainerVectorIterator_advance(flattenedStackIt, 1);
    flattenedStack_1_retainer =
        ComposableRetainerVectorIterator_value(flattenedStackIt);
    flattenedStack_1 = RetainerComposable_value(flattenedStack_1_retainer);
    ComposableRetainerVectorIterator_advance(flattenedStackIt, 1);
    flattenedStack_2_retainer =
        ComposableRetainerVectorIterator_value(flattenedStackIt);
    flattenedStack_2 = RetainerComposable_value(flattenedStack_2_retainer);
    ComposableRetainerVector_destroy(flattenedStackChildren);
    flattenedStackChildren = NULL;
    ComposableRetainerVectorIterator_destroy(flattenedStackIt);
    flattenedStackIt = NULL;

    ComposableRetainerVector* trackgFgChildren = Track_children(trackgFg);
    ComposableRetainerVectorIterator* trackgFgIt =
        ComposableRetainerVector_begin(trackgFgChildren);
    ComposableRetainerVectorIterator_advance(trackgFgIt, 1);
    RetainerComposable* trackgFg_1_retainer =
        ComposableRetainerVectorIterator_value(trackgFgIt);
    Composable* trackgFg_1 = RetainerComposable_value(trackgFg_1_retainer);
    ComposableRetainerVector_destroy(trackDgEChildren);
    trackDgEChildren = NULL;
    ComposableRetainerVectorIterator_destroy(trackDgEIt);
    trackDgEIt = NULL;

    EXPECT_STREQ(Composable_name(flattenedStack_0), "Z");
    start    = RationalTime_create(0, 24);
    duration = RationalTime_create(50, 24);
    tr       = TimeRange_create_with_start_time_and_duration(start, duration);
    TimeRange* flattenedStack_0_source_range =
        Clip_source_range((Clip*) flattenedStack_0);
    EXPECT_TRUE(TimeRange_equal(tr, flattenedStack_0_source_range));
    TimeRange_destroy(tr);
    tr = NULL;
    TimeRange_destroy(flattenedStack_0_source_range);
    flattenedStack_0_source_range = NULL;
    RationalTime_destroy(start);
    start = NULL;

    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) flattenedStack_1,
        (SerializableObject*) trackgFg_1));
    EXPECT_STREQ(Composable_name(flattenedStack_2), "Z");
    start = RationalTime_create(100, 24);
    tr    = TimeRange_create_with_start_time_and_duration(start, duration);
    TimeRange* flattenedStack_2_source_range =
        Clip_source_range((Clip*) flattenedStack_2);
    EXPECT_TRUE(TimeRange_equal(tr, flattenedStack_2_source_range));
    TimeRange_destroy(tr);
    tr = NULL;
    TimeRange_destroy(flattenedStack_2_source_range);
    flattenedStack_2_source_range = NULL;
    RationalTime_destroy(start);
    start = NULL;
    RationalTime_destroy(duration);
    duration = NULL;

    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
    Stack_possibly_delete(stack);
    stack = NULL;
    Track_possibly_delete(flattenedStack);
    flattenedStack = NULL;
    Track_possibly_delete(trackZ);
    Track_possibly_delete(trackABC);
    Track_possibly_delete(trackDgE);
    Track_possibly_delete(trackgFg);
    trackZ = trackABC = trackDgE = trackgFg = NULL;
}

TEST_F(OTIOStackAlgoTests, FlattenVectorOfTracksTest)
{
    TrackVector* tracks = TrackVector_create();
    TrackVector_push_back(tracks, trackABC);
    TrackVector_push_back(tracks, trackDgE);

    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    Track* flatTrack = flatten_stack_track_vector(tracks, errorStatus);

    ComposableRetainerVector* trackABCChildren = Track_children(trackABC);
    ComposableRetainerVectorIterator* trackABCIt =
        ComposableRetainerVector_begin(trackABCChildren);
    RetainerComposable* trackABC_0_retainer =
        ComposableRetainerVectorIterator_value(trackABCIt);
    Composable* trackABC_0 = RetainerComposable_value(trackABC_0_retainer);
    ComposableRetainerVectorIterator_advance(trackABCIt, 1);
    RetainerComposable* trackABC_1_retainer =
        ComposableRetainerVectorIterator_value(trackABCIt);
    Composable* trackABC_1 = RetainerComposable_value(trackABC_1_retainer);
    ComposableRetainerVectorIterator_advance(trackABCIt, 1);
    RetainerComposable* trackABC_2_retainer =
        ComposableRetainerVectorIterator_value(trackABCIt);
    Composable* trackABC_2 = RetainerComposable_value(trackABC_2_retainer);
    ComposableRetainerVector_destroy(trackABCChildren);
    trackABCChildren = NULL;
    ComposableRetainerVectorIterator_destroy(trackABCIt);
    trackABCIt = NULL;

    ComposableRetainerVector* trackDgEChildren = Track_children(trackDgE);
    ComposableRetainerVectorIterator* trackDgEIt =
        ComposableRetainerVector_begin(trackDgEChildren);
    RetainerComposable* trackDgE_0_retainer =
        ComposableRetainerVectorIterator_value(trackDgEIt);
    Composable* trackDgE_0 = RetainerComposable_value(trackDgE_0_retainer);
    ComposableRetainerVectorIterator_advance(trackDgEIt, 2);
    RetainerComposable* trackDgE_2_retainer =
        ComposableRetainerVectorIterator_value(trackDgEIt);
    Composable* trackDgE_2 = RetainerComposable_value(trackDgE_2_retainer);
    ComposableRetainerVector_destroy(trackDgEChildren);
    trackDgEChildren = NULL;
    ComposableRetainerVectorIterator_destroy(trackDgEIt);
    trackDgEIt = NULL;

    ComposableRetainerVector* trackgFgChildren = Track_children(trackgFg);
    ComposableRetainerVectorIterator* trackgFgIt =
        ComposableRetainerVector_begin(trackgFgChildren);
    ComposableRetainerVectorIterator_advance(trackgFgIt, 1);
    RetainerComposable* trackgFg_1_retainer =
        ComposableRetainerVectorIterator_value(trackgFgIt);
    Composable* trackgFg_1 = RetainerComposable_value(trackgFg_1_retainer);
    ComposableRetainerVector_destroy(trackDgEChildren);
    trackDgEChildren = NULL;
    ComposableRetainerVectorIterator_destroy(trackDgEIt);
    trackDgEIt = NULL;

    ComposableRetainerVector* flatTrackChildren = Track_children(flatTrack);
    ComposableRetainerVectorIterator* flatTrackIt =
        ComposableRetainerVector_begin(flatTrackChildren);
    RetainerComposable* flatTrack_0_retainer =
        ComposableRetainerVectorIterator_value(flatTrackIt);
    Composable* flatTrack_0 = RetainerComposable_value(flatTrack_0_retainer);
    ComposableRetainerVectorIterator_advance(flatTrackIt, 1);
    RetainerComposable* flatTrack_1_retainer =
        ComposableRetainerVectorIterator_value(flatTrackIt);
    Composable* flatTrack_1 = RetainerComposable_value(flatTrack_1_retainer);
    ComposableRetainerVectorIterator_advance(flatTrackIt, 1);
    RetainerComposable* flatTrack_2_retainer =
        ComposableRetainerVectorIterator_value(flatTrackIt);
    Composable* flatTrack_2 = RetainerComposable_value(flatTrack_2_retainer);
    ComposableRetainerVector_destroy(flatTrackChildren);
    flatTrackChildren = NULL;
    ComposableRetainerVectorIterator_destroy(flatTrackIt);
    flatTrackIt = NULL;

    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) flatTrack_0, (SerializableObject*) trackDgE_0));
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) flatTrack_1, (SerializableObject*) trackABC_1));
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) flatTrack_2, (SerializableObject*) trackDgE_2));

    TrackVector_destroy(tracks);
    tracks = NULL;
    Track_possibly_delete(flatTrack);
    flatTrack = NULL;

    tracks = TrackVector_create();
    TrackVector_push_back(tracks, trackABC);
    TrackVector_push_back(tracks, trackgFg);

    flatTrack = flatten_stack_track_vector(tracks, errorStatus);

    flatTrackChildren    = Track_children(flatTrack);
    flatTrackIt          = ComposableRetainerVector_begin(flatTrackChildren);
    flatTrack_0_retainer = ComposableRetainerVectorIterator_value(flatTrackIt);
    flatTrack_0          = RetainerComposable_value(flatTrack_0_retainer);
    ComposableRetainerVectorIterator_advance(flatTrackIt, 1);
    flatTrack_1_retainer = ComposableRetainerVectorIterator_value(flatTrackIt);
    flatTrack_1          = RetainerComposable_value(flatTrack_1_retainer);
    ComposableRetainerVectorIterator_advance(flatTrackIt, 1);
    flatTrack_2_retainer = ComposableRetainerVectorIterator_value(flatTrackIt);
    flatTrack_2          = RetainerComposable_value(flatTrack_2_retainer);
    ComposableRetainerVector_destroy(flatTrackChildren);
    flatTrackChildren = NULL;
    ComposableRetainerVectorIterator_destroy(flatTrackIt);
    flatTrackIt = NULL;

    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) flatTrack_0, (SerializableObject*) trackABC_0));
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) flatTrack_1, (SerializableObject*) trackgFg_1));
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) flatTrack_2, (SerializableObject*) trackABC_2));

    TrackVector_destroy(tracks);
    tracks = NULL;
    Track_possibly_delete(flatTrack);
    flatTrack = NULL;
    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
    Track_possibly_delete(trackZ);
    Track_possibly_delete(trackABC);
    Track_possibly_delete(trackDgE);
    Track_possibly_delete(trackgFg);
    trackZ = trackABC = trackDgE = trackgFg = NULL;
}

TEST_F(OTIOStackAlgoTests, FlattenExampleCodeTest)
{
    const char* multitrack_file = "multitrack.otio";
    char*       multitrack_path = (char*) calloc(
        strlen(sample_data_dir) + strlen(multitrack_file) + 1, sizeof(char));
    strcpy(multitrack_path, sample_data_dir);
    strcat(multitrack_path, multitrack_file);

    const char* preflattened_file = "preflattened.otio";
    char*       preflattened_path = (char*) calloc(
        strlen(sample_data_dir) + strlen(multitrack_file) + 1, sizeof(char));
    strcpy(preflattened_path, sample_data_dir);
    strcat(preflattened_path, preflattened_file);

    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    Any* tlAny = create_safely_typed_any_serializable_object(
        SerializableObject_create());
    ASSERT_TRUE(
        deserialize_json_from_file(multitrack_path, tlAny, errorStatus));
    Timeline* timeline = (Timeline*) safely_cast_retainer_any(tlAny);

    Any* preflattenedAny = create_safely_typed_any_serializable_object(
        SerializableObject_create());
    ASSERT_TRUE(deserialize_json_from_file(
        preflattened_path, preflattenedAny, errorStatus));
    Timeline* preflattened =
        (Timeline*) safely_cast_retainer_any(preflattenedAny);

    Stack* preflattened_stack = Timeline_tracks(preflattened);
    ComposableRetainerVector* preflattened_tracks_vector =
        Stack_children(preflattened_stack);
    ComposableRetainerVectorIterator* preflattened_tracks_vector_it =
        ComposableRetainerVector_begin(preflattened_tracks_vector);
    RetainerComposable* preflattened_tracks_vector_0 =
        ComposableRetainerVectorIterator_value(preflattened_tracks_vector_it);
    Track* preflattened_track =
        (Track*) RetainerComposable_value(preflattened_tracks_vector_0);
    ComposableRetainerVector_destroy(preflattened_tracks_vector);
    preflattened_tracks_vector = NULL;
    ComposableRetainerVectorIterator_destroy(preflattened_tracks_vector_it);
    preflattened_tracks_vector_it = NULL;

    TrackVector* timeline_video_tracks = Timeline_video_tracks(timeline);
    Track*       flattened_track =
        flatten_stack_track_vector(timeline_video_tracks, errorStatus);

    Track_set_name(preflattened_track, "");
    Track_set_name(flattened_track, "");

    EXPECT_TRUE(Track_is_equivalent_to(
        preflattened_track, (SerializableObject*) flattened_track));

    TrackVector_destroy(timeline_video_tracks);
    timeline_video_tracks = NULL;
    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
    Track_possibly_delete(trackZ);
    Track_possibly_delete(trackABC);
    Track_possibly_delete(trackDgE);
    Track_possibly_delete(trackgFg);
    trackZ = trackABC = trackDgE = trackgFg = NULL;
}

TEST_F(OTIOStackAlgoTests, FlattenWithTransitionTest)
{
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    RationalTime* in_offset  = RationalTime_create(10, 24);
    RationalTime* out_offset = RationalTime_create(15, 24);

    Transition* transition =
        Transition_create("test_transition", NULL, in_offset, out_offset, NULL);

    RationalTime_destroy(in_offset);
    RationalTime_destroy(out_offset);
    in_offset = out_offset = NULL;

    ASSERT_TRUE(
        Track_insert_child(trackDgE, 1, (Composable*) transition, errorStatus));

    Stack* stack = Stack_create(NULL, NULL, NULL, NULL, NULL);
    ASSERT_TRUE(
        Stack_insert_child(stack, 0, (Composable*) trackABC, errorStatus));
    ASSERT_TRUE(
        Stack_insert_child(stack, 2, (Composable*) trackDgE, errorStatus));

    Track* flat_track = flatten_stack(stack, errorStatus);

    ComposableRetainerVector* trackABC_childen = Track_children(trackABC);
    EXPECT_EQ(ComposableRetainerVector_size(trackABC_childen), 3);
    ComposableRetainerVector_destroy(trackABC_childen);
    trackABC_childen = NULL;

    ComposableRetainerVector* trackDgE_childen = Track_children(trackDgE);
    EXPECT_EQ(ComposableRetainerVector_size(trackDgE_childen), 4);
    ComposableRetainerVector_destroy(trackDgE_childen);
    trackDgE_childen = NULL;

    ComposableRetainerVector* flat_track_childen = Track_children(flat_track);
    EXPECT_EQ(ComposableRetainerVector_size(flat_track_childen), 4);

    ComposableRetainerVectorIterator* flat_track_it =
        ComposableRetainerVector_begin(flat_track_childen);
    ComposableRetainerVectorIterator_advance(flat_track_it, 1);
    RetainerComposable* flat_track_1_retainer =
        ComposableRetainerVectorIterator_value(flat_track_it);
    Composable* flat_track_1 = RetainerComposable_value(flat_track_1_retainer);
    EXPECT_STREQ(Composable_name(flat_track_1), "test_transition");

    ComposableRetainerVectorIterator_destroy(flat_track_it);
    flat_track_1 = NULL;
    ComposableRetainerVector_destroy(flat_track_childen);
    flat_track_childen = NULL;
    Transition_possibly_delete(transition);
    transition = NULL;
    Stack_possibly_delete(stack);
    stack = NULL;
    Track_possibly_delete(trackZ);
    Track_possibly_delete(trackABC);
    Track_possibly_delete(trackDgE);
    Track_possibly_delete(trackgFg);
    trackZ = trackABC = trackDgE = trackgFg = NULL;
}
