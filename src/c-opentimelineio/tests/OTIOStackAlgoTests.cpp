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
    }
    void TearDown() override
    {
        //        Track_possibly_delete(trackZ);
        //        Track_possibly_delete(trackABC);
        //        Track_possibly_delete(trackDgE);
        //        Track_possibly_delete(trackgFg);
        //        trackZ = trackABC = trackDgE = trackgFg = NULL;
    }

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