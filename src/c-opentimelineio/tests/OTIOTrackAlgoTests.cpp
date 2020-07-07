#include "gtest/gtest.h"

#include <copentimelineio/clip.h>
#include <copentimelineio/deserialization.h>
#include <copentimelineio/errorStatus.h>
#include <copentimelineio/externalReference.h>
#include <copentimelineio/gap.h>
#include <copentimelineio/missingReference.h>
#include <copentimelineio/safely_typed_any.h>
#include <copentimelineio/serializableCollection.h>
#include <copentimelineio/serializableObject.h>
#include <copentimelineio/serializableObjectWithMetadata.h>
#include <copentimelineio/serialization.h>
#include <copentimelineio/timeline.h>
#include <copentimelineio/track.h>
#include <copentimelineio/trackAlgorithm.h>
#include <copentimelineio/transition.h>

class OTIOTrackAlgoTests : public ::testing::Test
{
protected:
    void SetUp() override
    {
        OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

        /* sample_track */
        Any* decoded = /* allocate memory for destinantion */
            create_safely_typed_any_serializable_object(
                SerializableObject_create());
        bool decoded_successfully = deserialize_json_from_string(
            sample_track_str, decoded, errorStatus);
        SerializableObject* decoded_object = safely_cast_retainer_any(decoded);
        sample_track                       = (Track*) decoded_object;

        OTIOErrorStatus_destroy(errorStatus);
        errorStatus = NULL;
    }
    void TearDown() override
    {
        Track_possibly_delete(sample_track);
        sample_track = NULL;
    }
    Track*      sample_track = NULL;
    const char* sample_track_str =
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
};

TEST_F(OTIOTrackAlgoTests, TrimToExistingRangeTest)
{
    RationalTime* start    = RationalTime_create(0, 24);
    RationalTime* duration = RationalTime_create(150, 24);
    TimeRange*    trimmed_range =
        TimeRange_create_with_start_time_and_duration(start, duration);

    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    TimeRange* sample_track_trimmed_range =
        Track_trimmed_range(sample_track, errorStatus);
    EXPECT_TRUE(TimeRange_equal(trimmed_range, sample_track_trimmed_range));

    Track* trimmed_track =
        track_trimmed_to_range(sample_track, trimmed_range, errorStatus);

    /* It shouldn't have changed at all */
    EXPECT_TRUE(Track_is_equivalent_to(
        sample_track, (SerializableObject*) trimmed_track));

    RationalTime_destroy(start);
    start = NULL;
    RationalTime_destroy(duration);
    duration = NULL;
    TimeRange_destroy(trimmed_range);
    trimmed_range = NULL;
    TimeRange_destroy(sample_track_trimmed_range);
    sample_track_trimmed_range = NULL;
    //    Track_possibly_delete(trimmed_track); // TODO: fix segfault
    //    trimmed_range = NULL;
}

TEST_F(OTIOTrackAlgoTests, TrimToLongerRangeTest)
{
    RationalTime* start    = RationalTime_create(-10, 24);
    RationalTime* duration = RationalTime_create(160, 24);
    TimeRange*    trimmed_range =
        TimeRange_create_with_start_time_and_duration(start, duration);

    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    Track* trimmed_track =
        track_trimmed_to_range(sample_track, trimmed_range, errorStatus);

    /* It shouldn't have changed at all */
    EXPECT_TRUE(Track_is_equivalent_to(
        sample_track, (SerializableObject*) trimmed_track));

    RationalTime_destroy(start);
    start = NULL;
    RationalTime_destroy(duration);
    duration = NULL;
    TimeRange_destroy(trimmed_range);
    trimmed_range = NULL;
    //    Track_possibly_delete(trimmed_track); // TODO: fix segfault
    //    trimmed_range = NULL;
}

TEST_F(OTIOTrackAlgoTests, TrimFrontTest)
{
    RationalTime* start    = RationalTime_create(60, 24);
    RationalTime* duration = RationalTime_create(90, 24);
    TimeRange*    trimmed_range =
        TimeRange_create_with_start_time_and_duration(start, duration);

    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    /* trim off the front (clip A and part of B) */
    Track* trimmed_track =
        track_trimmed_to_range(sample_track, trimmed_range, errorStatus);

    ComposableRetainerVector* trimmed_track_children =
        Track_children(trimmed_track);
    EXPECT_EQ(ComposableRetainerVector_size(trimmed_track_children), 2);

    TimeRange* trimmed_track_trimmed_range =
        Track_trimmed_range(trimmed_track, errorStatus);
    RationalTime_destroy(start);
    RationalTime_destroy(duration);
    start    = RationalTime_create(0, 24);
    duration = RationalTime_create(90, 24);
    TimeRange* trimmed_track_trimmed_range_compare =
        TimeRange_create_with_start_time_and_duration(start, duration);
    EXPECT_TRUE(TimeRange_equal(
        trimmed_track_trimmed_range, trimmed_track_trimmed_range_compare));
    TimeRange_destroy(trimmed_track_trimmed_range);
    trimmed_track_trimmed_range = NULL;
    TimeRange_destroy(trimmed_track_trimmed_range_compare);
    trimmed_track_trimmed_range_compare = NULL;
    RationalTime_destroy(start);
    RationalTime_destroy(duration);

    /* did clip B get trimmed? */
    ComposableRetainerVectorIterator* it =
        ComposableRetainerVector_begin(trimmed_track_children);
    RetainerComposable* clipB_retainer =
        ComposableRetainerVectorIterator_value(it);
    Clip* B = (Clip*) RetainerComposable_value(clipB_retainer);
    ComposableRetainerVectorIterator_advance(it, 1);
    RetainerComposable* clipC_retainer =
        ComposableRetainerVectorIterator_value(it);
    Clip* C = (Clip*) RetainerComposable_value(clipC_retainer);
    EXPECT_STREQ(Clip_name(B), "B");
    TimeRange* clipB_trimmed_range = Clip_trimmed_range(B, errorStatus);
    start                          = RationalTime_create(10, 24);
    duration                       = RationalTime_create(40, 24);
    TimeRange* clipB_trimmed_range_compare =
        TimeRange_create_with_start_time_and_duration(start, duration);
    EXPECT_TRUE(
        TimeRange_equal(clipB_trimmed_range, clipB_trimmed_range_compare));
    ComposableRetainerVectorIterator_destroy(it);
    it = NULL;
    TimeRange_destroy(clipB_trimmed_range_compare);
    clipB_trimmed_range_compare = NULL;
    TimeRange_destroy(clipB_trimmed_range);
    clipB_trimmed_range = NULL;

    ComposableRetainerVector* sample_track_children =
        Track_children(sample_track);
    ComposableRetainerVectorIterator* sample_track_it =
        ComposableRetainerVector_begin(sample_track_children);
    ComposableRetainerVectorIterator_advance(sample_track_it, 2);
    RetainerComposable* original_clipC_retainer =
        ComposableRetainerVectorIterator_value(sample_track_it);
    Clip* original_ClipC =
        (Clip*) RetainerComposable_value(original_clipC_retainer);

    /* clip C should have been left alone */
    EXPECT_TRUE(Clip_is_equivalent_to(C, (SerializableObject*) original_ClipC));

    ComposableRetainerVectorIterator_destroy(sample_track_it);
    sample_track_it = NULL;
    ComposableRetainerVector_destroy(sample_track_children);
    sample_track_children = NULL;

    EXPECT_FALSE(Track_is_equivalent_to(
        sample_track, (SerializableObject*) trimmed_track));

    RationalTime_destroy(start);
    start = NULL;
    RationalTime_destroy(duration);
    duration = NULL;
    TimeRange_destroy(trimmed_range);
    trimmed_range = NULL;
    ComposableRetainerVector_destroy(trimmed_track_children);
    trimmed_track_children = NULL;
    //    Track_possibly_delete(trimmed_track); // TODO: fix segfault
    //    trimmed_range = NULL;
}