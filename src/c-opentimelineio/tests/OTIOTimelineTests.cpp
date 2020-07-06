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
#include <copentimelineio/transition.h>

class OTIOTimelineTests : public ::testing::Test
{
protected:
    void SetUp() override {}
    void TearDown() override {}
};

TEST_F(OTIOTimelineTests, InitTest)
{
    RationalTime* rt = RationalTime_create(12, 24);
    Timeline*     tl = Timeline_create("test_timeline", rt, NULL);

    EXPECT_STREQ(Timeline_name(tl), "test_timeline");

    RationalTime* tl_global_start_time = Timeline_global_start_time(tl);
    EXPECT_TRUE(RationalTime_equal(rt, tl_global_start_time));

    RationalTime_destroy(rt);
    rt = NULL;
    RationalTime_destroy(tl_global_start_time);
    tl_global_start_time = NULL;
    Timeline_possibly_delete(tl);
    tl = NULL;
}

TEST_F(OTIOTimelineTests, MetadataTest)
{
    RationalTime*          rt       = RationalTime_create(12, 24);
    AnyDictionary*         metadata = AnyDictionary_create();
    Any*                   barAny   = create_safely_typed_any_string("bar");
    AnyDictionaryIterator* it = AnyDictionary_insert(metadata, "foo", barAny);
    AnyDictionaryIterator_destroy(it);
    it = NULL;

    Timeline* tl = Timeline_create("test_timeline", rt, metadata);

    AnyDictionary* metadataResult = Timeline_metadata(tl);
    it                            = AnyDictionary_find(metadataResult, "foo");
    Any*        metadataResultValAny = AnyDictionaryIterator_value(it);
    const char* metadataResultValStr =
        safely_cast_string_any(metadataResultValAny);
    EXPECT_STREQ(metadataResultValStr, "bar");

    AnyDictionaryIterator_destroy(it);
    it = NULL;
    AnyDictionary_destroy(metadataResult);
    metadataResult = NULL;
    Any_destroy(metadataResultValAny);
    metadataResultValAny = NULL;

    Any* tl_any =
        create_safely_typed_any_serializable_object((SerializableObject*) tl);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    const char* encoded = serialize_json_to_string(tl_any, errorStatus, 4);
    Any*        decoded = /* allocate memory for destinantion */
        create_safely_typed_any_serializable_object((SerializableObject*) tl);

    bool decoded_successfully =
        deserialize_json_from_string(encoded, decoded, errorStatus);
    ASSERT_TRUE(decoded_successfully);
    SerializableObject* decoded_object = safely_cast_retainer_any(decoded);

    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) tl, decoded_object));

    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
    RationalTime_destroy(rt);
    rt = NULL;
    AnyDictionary_destroy(metadata);
    metadata = NULL;
    Any_destroy(barAny);
    barAny = NULL;
    Any_destroy(decoded);
    decoded = NULL;
    Timeline_possibly_delete(tl);
    tl = NULL;
}

TEST_F(OTIOTimelineTests, RangeTest)
{
    RationalTime* start    = RationalTime_create(5, 24);
    RationalTime* duration = RationalTime_create(15, 24);
    TimeRange*    tr =
        TimeRange_create_with_start_time_and_duration(start, duration);

    ExternalReference* mr =
        ExternalReference_create("/var/tmp/test.mov", tr, NULL);

    TimeRange* clip_tr =
        TimeRange_create_with_start_time_and_duration(NULL, start);

    RationalTime_destroy(start);
    RationalTime_destroy(duration);
    start = duration = NULL;

    Clip* cl  = Clip_create("test clip1", (MediaReference*) mr, clip_tr, NULL);
    Clip* cl2 = Clip_create("test clip2", (MediaReference*) mr, clip_tr, NULL);
    Clip* cl3 = Clip_create("test clip3", (MediaReference*) mr, clip_tr, NULL);

    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    Track* track = Track_create("test_track", NULL, NULL, NULL);

    ASSERT_TRUE(Track_insert_child(track, 0, (Composable*) cl, errorStatus));
    ASSERT_TRUE(Track_insert_child(track, 1, (Composable*) cl2, errorStatus));
    ASSERT_TRUE(Track_insert_child(track, 2, (Composable*) cl3, errorStatus));

    Stack* stack = Stack_create(NULL, NULL, NULL, NULL, NULL);
    ASSERT_TRUE(Stack_insert_child(stack, 0, (Composable*) track, errorStatus));

    Timeline* tl = Timeline_create("test_timeline", NULL, NULL);
    Timeline_set_tracks(tl, stack);

    RationalTime* rtx3        = RationalTime_create(15, 24);
    RationalTime* tl_duration = Timeline_duration(tl, errorStatus);
    EXPECT_TRUE(RationalTime_equal(rtx3, tl_duration));

    TimeRange* tl_range_of_child_cl =
        Timeline_range_of_child(tl, (Composable*) cl, errorStatus);
    TimeRange* track_range_of_child_0 =
        Track_range_of_child_at_index(track, 0, errorStatus);
    EXPECT_TRUE(TimeRange_equal(tl_range_of_child_cl, track_range_of_child_0));

    TimeRange_destroy(tl_range_of_child_cl);
    tl_range_of_child_cl = NULL;
    TimeRange_destroy(track_range_of_child_0);
    track_range_of_child_0 = NULL;
    TimeRange_destroy(clip_tr);
    clip_tr = NULL;
    TimeRange_destroy(tr);
    tr = NULL;
    RationalTime_destroy(tl_duration);
    tl_duration = NULL;
    RationalTime_destroy(rtx3);
    rtx3 = NULL;
    Timeline_possibly_delete(tl);
    tl = NULL;
}

TEST_F(OTIOTimelineTests, SerializeTest)
{
    MissingReference* mr = MissingReference_create(NULL, NULL, NULL);
    Clip* clip = Clip_create("test_clip", (MediaReference*) mr, NULL, NULL);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    Track* track = Track_create("test_track", NULL, NULL, NULL);

    ASSERT_TRUE(Track_insert_child(track, 0, (Composable*) clip, errorStatus));

    Stack* stack = Stack_create(NULL, NULL, NULL, NULL, NULL);
    ASSERT_TRUE(Stack_insert_child(stack, 0, (Composable*) track, errorStatus));

    Timeline* tl = Timeline_create("test_timeline", NULL, NULL);
    Timeline_set_tracks(tl, stack);

    Any* tl_any =
        create_safely_typed_any_serializable_object((SerializableObject*) tl);

    const char* encoded = serialize_json_to_string(tl_any, errorStatus, 4);
    Any*        decoded = /* allocate memory for destinantion */
        create_safely_typed_any_serializable_object((SerializableObject*) tl);

    bool decoded_successfully =
        deserialize_json_from_string(encoded, decoded, errorStatus);
    ASSERT_TRUE(decoded_successfully);
    SerializableObject* decoded_object = safely_cast_retainer_any(decoded);

    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) tl, decoded_object));

    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
    Any_destroy(decoded);
    decoded = NULL;
    Timeline_possibly_delete(tl);
    tl = NULL;
}

TEST_F(OTIOTimelineTests, SerializationOfSubclassesTest)
{
    ExternalReference* mr =
        ExternalReference_create("/tmp/foo.mov", NULL, NULL);
    Clip* clip1 = Clip_create("Test Clip", (MediaReference*) mr, NULL, NULL);
    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    Track* track = Track_create("Test Track", NULL, NULL, NULL);

    ASSERT_TRUE(Track_insert_child(track, 0, (Composable*) clip1, errorStatus));

    Stack* stack = Stack_create(NULL, NULL, NULL, NULL, NULL);
    ASSERT_TRUE(Stack_insert_child(stack, 0, (Composable*) track, errorStatus));

    Timeline* tl = Timeline_create("Testing Serialization", NULL, NULL);
    Timeline_set_tracks(tl, stack);

    Any* tl_any =
        create_safely_typed_any_serializable_object((SerializableObject*) tl);

    const char* serialized = serialize_json_to_string(tl_any, errorStatus, 4);
    EXPECT_TRUE(serialized != NULL);

    Any* decoded = /* allocate memory for destinantion */
        create_safely_typed_any_serializable_object((SerializableObject*) tl);

    bool deserialized_successfully =
        deserialize_json_from_string(serialized, decoded, errorStatus);
    ASSERT_TRUE(deserialized_successfully);
    SerializableObject* deserialized_object = safely_cast_retainer_any(decoded);

    Timeline* tl2 = (Timeline*) deserialized_object;
    EXPECT_TRUE(tl2 != NULL);

    EXPECT_STREQ(Timeline_name(tl), Timeline_name(tl2));

    Stack* tl_tracks  = Timeline_tracks(tl);
    Stack* tl2_tracks = Timeline_tracks(tl2);

    ComposableRetainerVector* tl_tracks_vector  = Stack_children(tl_tracks);
    ComposableRetainerVector* tl2_tracks_vector = Stack_children(tl2_tracks);
    EXPECT_EQ(ComposableRetainerVector_size(tl_tracks_vector), 1);
    EXPECT_EQ(ComposableRetainerVector_size(tl2_tracks_vector), 1);

    ComposableRetainerVectorIterator* tl_tracks_vector_it =
        ComposableRetainerVector_begin(tl_tracks_vector);
    ComposableRetainerVectorIterator* tl2_tracks_vector_it =
        ComposableRetainerVector_begin(tl2_tracks_vector);

    RetainerComposable* tl_tracks_0_retainer_composable =
        ComposableRetainerVectorIterator_value(tl_tracks_vector_it);
    Composable* track1Composable =
        RetainerComposable_value(tl_tracks_0_retainer_composable);
    Track* track1 = (Track*) track1Composable;

    RetainerComposable* tl2_tracks_0_retainer_composable =
        ComposableRetainerVectorIterator_value(tl2_tracks_vector_it);
    Composable* track2Composable =
        RetainerComposable_value(tl2_tracks_0_retainer_composable);
    Track* track2 = (Track*) track2Composable;

    ComposableRetainerVector* track1_children = Track_children(track1);
    ComposableRetainerVector* track2_children = Track_children(track2);

    EXPECT_EQ(ComposableRetainerVector_size(track1_children), 1);
    EXPECT_EQ(ComposableRetainerVector_size(track2_children), 1);

    ComposableRetainerVectorIterator* clip2_it =
        ComposableRetainerVector_begin(track2_children);
    RetainerComposable* clip2_retainer_composable =
        ComposableRetainerVectorIterator_value(clip2_it);
    Composable* clip2_composable =
        RetainerComposable_value(clip2_retainer_composable);
    Clip* clip2 = (Clip*) clip2_composable;

    EXPECT_STREQ(Clip_name(clip1), Clip_name(clip2));

    MediaReference* clip1_mr = Clip_media_reference(clip1);
    MediaReference* clip2_mr = Clip_media_reference(clip2);
    EXPECT_TRUE(SerializableObject_is_equivalent_to(
        (SerializableObject*) clip1_mr, (SerializableObject*) clip2_mr));

    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;

    ComposableRetainerVector_destroy(tl_tracks_vector);
    tl_tracks_vector = NULL;
    ComposableRetainerVector_destroy(tl2_tracks_vector);
    tl2_tracks_vector = NULL;
    ComposableRetainerVector_destroy(track1_children);
    track1_children = NULL;
    ComposableRetainerVector_destroy(track2_children);
    track2_children = NULL;
    ComposableRetainerVectorIterator_destroy(tl_tracks_vector_it);
    tl_tracks_vector_it = NULL;
    ComposableRetainerVectorIterator_destroy(tl2_tracks_vector_it);
    tl2_tracks_vector_it = NULL;
    ComposableRetainerVectorIterator_destroy(clip2_it);
    clip2_it = NULL;
    Timeline_possibly_delete(tl);
    tl = NULL;
    Timeline_possibly_delete(tl2);
    tl2 = NULL;
}

TEST_F(OTIOTimelineTests, TracksTest)
{
    Track* V1 = Track_create("V1", NULL, TrackKind_Video, NULL);
    Track* V2 = Track_create("V2", NULL, TrackKind_Video, NULL);
    Track* A1 = Track_create("A1", NULL, TrackKind_Audio, NULL);
    Track* A2 = Track_create("A2", NULL, TrackKind_Audio, NULL);

    Stack* stack = Stack_create(NULL, NULL, NULL, NULL, NULL);

    OTIOErrorStatus* errorStatus = OTIOErrorStatus_create();

    ASSERT_TRUE(Stack_insert_child(stack, 0, (Composable*) V1, errorStatus));
    ASSERT_TRUE(Stack_insert_child(stack, 1, (Composable*) V2, errorStatus));
    ASSERT_TRUE(Stack_insert_child(stack, 2, (Composable*) A1, errorStatus));
    ASSERT_TRUE(Stack_insert_child(stack, 3, (Composable*) A2, errorStatus));

    Timeline* tl = Timeline_create(NULL, NULL, NULL);
    Timeline_set_tracks(tl, stack);

    TrackVector* videoTrackVector = Timeline_video_tracks(tl);
    TrackVector* audioTrackVector = Timeline_audio_tracks(tl);

    const char* videoTrackNames[] = { "V1", "V2" };
    const char* audioTrackNames[] = { "A1", "A2" };

    TrackVectorIterator* vid_it     = TrackVector_begin(videoTrackVector);
    TrackVectorIterator* vid_it_end = TrackVector_end(videoTrackVector);
    TrackVectorIterator* aud_it     = TrackVector_begin(audioTrackVector);
    TrackVectorIterator* aud_it_end = TrackVector_end(audioTrackVector);

    for(int i = 0; TrackVectorIterator_not_equal(vid_it, vid_it_end);
        ++i, TrackVectorIterator_advance(vid_it, 1))
    {
        Track* track = TrackVectorIterator_value(vid_it);
        EXPECT_STREQ(Track_name(track), videoTrackNames[i]);
    }

    for(int i = 0; TrackVectorIterator_not_equal(aud_it, aud_it_end);
        ++i, TrackVectorIterator_advance(aud_it, 1))
    {
        Track* track = TrackVectorIterator_value(aud_it);
        EXPECT_STREQ(Track_name(track), audioTrackNames[i]);
    }

    OTIOErrorStatus_destroy(errorStatus);
    errorStatus = NULL;
    TrackVector_destroy(videoTrackVector);
    videoTrackVector = NULL;
    TrackVector_destroy(audioTrackVector);
    audioTrackVector = NULL;
    TrackVectorIterator_destroy(vid_it);
    vid_it = NULL;
    TrackVectorIterator_destroy(vid_it_end);
    vid_it_end = NULL;
    TrackVectorIterator_destroy(aud_it);
    aud_it = NULL;
    TrackVectorIterator_destroy(aud_it_end);
    aud_it_end = NULL;
    Timeline_possibly_delete(tl);
    tl = NULL;
}